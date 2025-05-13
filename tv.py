#!/usr/bin/env python3
import argparse, json, time, ssl, logging, base64
import socket
from contextlib import closing, contextmanager
import requests, websocket
from config import cfg
from st_manager import st

# ─── consts ────────────────────────────────────────────────────────────────────
APP = "PythonRemote"
APP_ENC_NAME = base64.b64encode(APP.encode()).decode()
URL_TMPL = ["wss://{ip}:8002/api/v2/channels/samsung.remote.control", "?name={name}&deviceId={dev}{tok}"]

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")


# ─── Wake-on-LAN ────────────────────────────────────────────────────────────────────
def is_tv_online(port=8002, timeout=1.0) -> bool:
    try:
        with socket.create_connection((cfg.TV_IP, port), timeout):
            return True
    except OSError:
        return False


def wait_service(timeout=60) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        if is_tv_online(8002):
            return True
        time.sleep(1)
    return False


# ── SmartThings Cloud — switch on/off ────────────────────────────
def st_switch(cmd: str):
    st.ensure_token()
    body = {"commands": [{"capability": "switch", "command": cmd}]}
    url = f"{cfg.ST_API_URL}/devices/{cfg.ST_TV_ID}/commands"
    r = requests.post(url, headers={"Authorization": f"Bearer {cfg.ST_TOKEN}", "Content-Type": "application/json"}, json=body, timeout=10)
    r.raise_for_status()
    logging.info("SmartThings %s → %s", cmd, r.status_code)


# ─── WebSocket helper ────────────────────────────────────────────────────────────────────
def ws_url(token: str, port: int) -> str:
    host = cfg.TV_IP.split(":", 1)[0]
    proto = "wss" if port == 8002 else "ws"
    tok = f"&token={token}" if token else ""
    logging.info(f"Connecting to {proto}://{host}:{port}")
    return f"{proto}://{host}:{port}/api/v2/channels/samsung.remote.control" f"?name={APP_ENC_NAME}&deviceId={cfg.TV_DEVICE_ID}{tok}"


def open_ws(port: int) -> websocket.WebSocket:
    tls = port == 8002
    url = ws_url(token=cfg.TOKEN, port=port)
    return websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE} if tls else {}, timeout=30)


def open_ws_with_retry(tries=4, delay=3.0) -> websocket.WebSocket:
    for n in range(1, tries + 1):
        try:
            return open_ws(8002)
        except (ConnectionResetError, ConnectionRefusedError, websocket.WebSocketException) as e:
            logging.warning("WebSocket connection attempt %d/%d port %d failed: %s", n, tries, 8002, e)
            time.sleep(delay)
    raise RuntimeError("Failed to connect to TV after multiple attempts via WebSocket")


@contextmanager
def tv_socket():
    with closing(open_ws_with_retry()) as ws:
        evt = json.loads(ws.recv())
        if evt["event"] != "ms.channel.connect":
            raise RuntimeError("Unauthorized: accept the connection on the TV")
        if not cfg.TOKEN:
            cfg.TOKEN = evt["data"]["token"]
            cfg.set_key(key="TV_TOKEN", value=cfg.TOKEN)
            logging.info("Set token value at .env file")
        ws.settimeout(None)
        yield ws


def send_cmd(ws: websocket.WebSocket, cmd: str, press="Click"):
    cmd = {"method": "ms.remote.control", "params": {"Cmd": press, "DataOfCmd": cmd, "TypeOfRemote": "SendRemoteKey"}}
    logging.info(f"Sending command: {cmd}")
    ws.send(json.dumps(cmd))


# ─── Energy actions ────────────────────────────────────────────────────────────────────
def power_on() -> None:
    if is_tv_online(8002):
        logging.info("TV is already on")
        return
    # Only with SmartThings Cloud, no WoL
    st_switch("on")
    port = wait_service()
    if not port:
        logging.error("SmartThings OK, but TV did not powered on")
        return
    logging.info("Power ON command sent")


def power_off() -> None:
    if not is_tv_online(8002):
        logging.info("TV is already off")
        return
    with tv_socket() as ws:
        send_cmd(ws, "KEY_POWER", "Press")
        time.sleep(2)
        send_cmd(ws, "KEY_POWER", "Release")
    logging.info("Power OFF command sent")


# ─── Volume actions ────────────────────────────────────────────────────────────────────
def volume(direc: str, steps: int):
    if not is_tv_online(8002):
        logging.info("TV is off")
        return
    with tv_socket() as ws:
        key = "KEY_VOLUP" if direc == "up" else "KEY_VOLDOWN"
        for _ in range(steps):
            send_cmd(ws, key)
            time.sleep(1.2)
        logging.info(f"Volume {direc.upper()} command sent")


# ─── CLI ────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("on")
    sub.add_parser("off")

    v = sub.add_parser("vol")
    v.add_argument("dir", choices=["up", "down"])
    v.add_argument("steps", type=int, nargs="?", default=1)

    tok = sub.add_parser("token", help="operações no SmartThings token")
    tok.add_argument("action", choices=["check", "renew"])

    args = ap.parse_args()

    try:
        if args.cmd == "on":
            power_on()
        elif args.cmd == "off":
            power_off()
        elif args.cmd == "vol":
            volume(args.dir, args.steps)
        elif args.cmd == "token":
            if args.action == "check":
                logging.info("Checking token...")
                st.ensure_token()
            elif args.action == "renew":
                st.TOKEN = ""
                st.ensure_token()
    except (RuntimeError, requests.exceptions.RequestException, websocket.WebSocketException, OSError) as e:
        logging.error(e)


if __name__ == "__main__":
    main()
