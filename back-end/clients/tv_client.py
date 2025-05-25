import time, logging, socket, functools
from websocket import WebSocket
from clients.ws_client import ws_client
from clients.st_client import st_client
from utils.config import cfg

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")


# ─── Wake-on-LAN ────────────────────────────────────────────────────────────────────
def is_tv_online(port=8002, timeout=1.0) -> bool:
    try:
        with socket.create_connection((cfg.tv_ip, port), timeout):
            return True
    except OSError:
        return False


def wait_for_tv_is_online(timeout=60) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        if is_tv_online(8002):
            return True
        time.sleep(1)
    return False


# ─── TV ────────────────────────────────────────────────────────────────────
def require_tv_online(fn):
    @functools.wraps(fn)
    def wrapper(self, *args, **kw):
        if not is_tv_online(8002):
            logging.info("TV is off")
            return
        with ws_client.authorize_connection_to_tv() as ws:
            return fn(self, ws, *args, **kw)

    return wrapper


class TVClient:
    def turn_tv_on(self) -> None:
        if is_tv_online(8002):
            logging.info("TV is already on")
            return
        # Only with SmartThings Cloud, no WoL
        st_client.set_tv_state_to_online()
        if not wait_for_tv_is_online():
            logging.error("SmartThings OK, but TV did not powered on")
            return
        logging.info("Power ON command sent")

    @require_tv_online
    def turn_tv_off(self, ws: WebSocket) -> None:
        self._send_cmd(ws, "KEY_POWER", press="Press")
        time.sleep(1)
        self._send_cmd(ws, "KEY_POWER", press="Release")
        logging.info("Power OFF command sent")

    @require_tv_online
    def volume(self, ws: WebSocket, direction: str, steps: int) -> None:
        key = "KEY_VOLUP" if direction == "up" else "KEY_VOLDOWN"
        for _ in range(steps):
            self._send_cmd(ws, key)
            time.sleep(1.2)
        logging.info(f"Volume {direction.upper()} command sent")

    @require_tv_online
    def toggle_mute(self, ws: WebSocket) -> None:
        self._send_cmd(ws, "KEY_MUTE", log="Mute toggled")

    def _send_cmd(self, ws: WebSocket, cmd: str, *, press: str = "Click", log: str | None = None) -> None:
        ws_client.send_cmd(ws, cmd, press)
        if log:
            logging.info(log)


tv_client = TVClient()
