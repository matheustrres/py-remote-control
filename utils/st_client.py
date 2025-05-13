import logging, getpass, requests
from config import cfg


class SmartThingsClient:
    def __init__(self) -> None:
        # Personal Acess Token is mutable
        self.pat = cfg.ST_TOKEN

    def _ping(self) -> tuple[bool, str]:
        if not self.pat:
            return False, "Empty token"
        try:
            r = requests.get(f"{cfg.ST_API_URL}/devices?limit=1", headers={"Authorization": f"Bearer {self.pat}"}, timeout=8)
            if r.status_code == 200:
                return True, "OK"
            return False, f"HTTP {r.status_code}"
        except requests.RequestException as e:
            return False, str(e)

    def ensure_pat(self) -> None:
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
        self.pat = new_token
        ok, info = self._ping()
        if not ok:
            raise RuntimeError(f"Invalid token: {info}")
        logging.info("SmartThings token successfully updated")

    def switch_mode(self, state: str = 'on') -> None:
        self.ensure_pat()
        body = {"commands": [{"capability": "switch", "command": state}]}
        url = f"{cfg.ST_API_URL}/devices/{cfg.ST_TV_ID}/commands"
        r = requests.post(url, headers={"Authorization": f"Bearer {self.pat}", "Content-Type": "application/json"}, json=body, timeout=10)
        r.raise_for_status()
        logging.info("SmartThings %s → %s", state, r.status_code)


st_client = SmartThingsClient()
