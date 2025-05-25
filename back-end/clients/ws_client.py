import logging, ssl, time, json
from contextlib import closing, contextmanager
import websocket
from utils.config import cfg, APP_ENC_NAME


class WebSocketClient:
    @contextmanager
    def authorize_connection_to_tv(self):
        with closing(self._open_connection_with_retry()) as ws:
            evt = json.loads(ws.recv())
            if evt["event"] != "ms.channel.connect":
                raise RuntimeError("Unauthorized: accept the connection on the TV")
            if not cfg.tv_token:
                cfg.tv_token = evt["data"]["token"]
                cfg.set_key(key="TV_TOKEN", value=cfg.tv_token)
                logging.info("Set token value at .env file")
            ws.settimeout(None)
            yield ws

    def _build_url(self, token: str, app_enc_name: str, port: int) -> str:
        host = cfg.tv_ip.split(":", 1)[0]
        proto = "wss" if port == 8002 else "ws"
        tok = f"&token={token}" if token else ""
        logging.info(f"Connecting to {proto}://{host}:{port}")
        return f"{proto}://{host}:{port}/api/v2/channels/samsung.remote.control" f"?name={app_enc_name}&deviceId={cfg.tv_device_id}{tok}"

    def _open_connection(self, port: int) -> websocket.WebSocket:
        tls = port == 8002
        url = self._build_url(token=cfg.tv_token, app_enc_name=APP_ENC_NAME, port=port)
        return websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE} if tls else {}, timeout=30)

    def _open_connection_with_retry(self, tries=4, delay=3.0) -> websocket.WebSocket:
        for n in range(1, tries + 1):
            try:
                return self._open_connection(8002)
            except (ConnectionResetError, ConnectionRefusedError, websocket.WebSocketException) as e:
                logging.warning("WebSocket connection attempt %d/%d port %d failed: %s", n, tries, 8002, e)
                time.sleep(delay)
        raise RuntimeError("Failed to connect to TV after multiple attempts via WebSocket")

    def send_cmd(self, ws: websocket.WebSocket, cmd: str, press="Click"):
        cmd = {"method": "ms.remote.control", "params": {"Cmd": press, "DataOfCmd": cmd, "TypeOfRemote": "SendRemoteKey"}}
        logging.info(f"Sending command: {cmd}")
        ws.send(json.dumps(cmd))


ws_client = WebSocketClient()
