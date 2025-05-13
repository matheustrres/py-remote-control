import logging, getpass, requests
from config import cfg


class SmartThingsTokenManager:
    def __init__(self) -> None:
        self.TOKEN = cfg.ST_TOKEN

    def _ping(self) -> tuple[bool, str]:
        if not self.TOKEN:
            return False, "Empty token"
        try:
            r = requests.get(f"{cfg.ST_API_URL}/devices?limit=1", headers={"Authorization": f"Bearer {self.TOKEN}"}, timeout=8)
            if r.status_code == 200:
                return True, "OK"
            return False, f"HTTP {r.status_code}"
        except requests.RequestException as e:
            return False, str(e)

    def ensure_token(self) -> None:
        ok, info = self._ping()
        if ok:
            logging.info("SmartThings token is valid: %s", info)
            return
        logging.warning("Invalid or expired token: %s", info)
        print("\nPlease insert a new SmartThings token with the following scopes: r:devices:* e x:devices:*")
        new_token = getpass.getpass("New SmartThings token: ").strip()
        if not new_token:
            raise RuntimeError("Empty token is not allowed")
        cfg.set_key("ST_TOKEN", new_token)
        self.TOKEN = new_token
        ok, info = self._ping()
        if not ok:
            raise RuntimeError(f"Invalid token: {info}")
        logging.info("SmartThings token successfully updated")


st = SmartThingsTokenManager()
