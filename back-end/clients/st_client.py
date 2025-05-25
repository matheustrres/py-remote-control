from dataclasses import dataclass
import logging, getpass, requests
from utils.config import cfg, ST_API_URL


@dataclass(frozen=True, slots=True)
class _Endpoints:
    devices = f"{ST_API_URL}/devices"
    commands = f"{ST_API_URL}/devices/{cfg.st_tv_id}/commands"


class SmartThingsClient:
    def __init__(self) -> None:
        # Personal Acess Token is mutable
        self._token = cfg.st_token
        self._eps = _Endpoints()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def _ping(self) -> tuple[bool, str]:
        try:
            r = requests.head(self._eps.devices, headers=self._headers(), timeout=5)
            return r.ok, f"HTTP {r.status_code}"
        except requests.RequestException as exc:
            return False, str(exc)

    def ensure_token(self) -> None:
        ok, info = self._ping()
        if ok:
            logging.info("SmartThings token is valid: %s", info)
            return
        logging.warning("Invalid or expired token: %s", info)
        print("\nInsert new SmartThings token with the following scopes: r:devices:* e x:devices:*")
        new_token = getpass.getpass("New SmartThings token: ").strip()
        if not new_token:
            raise RuntimeError("Empty token is not allowed")
        self._token = new_token
        cfg.set_key("ST_TOKEN", new_token)
        ok, info = self._ping()
        if not ok:
            raise RuntimeError(f"Token still invalid: {info}")
        logging.info("SmartThings token successfully updated")

    def set_tv_state_to_online(self) -> None:
        self.ensure_token()
        body = {"commands": [{"capability": "switch", "command": "on"}]}
        url = f"{ST_API_URL}/devices/{cfg.st_tv_id}/commands"
        r = requests.post(url, headers={"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}, json=body, timeout=10)
        r.raise_for_status()
        logging.info("SmartThings switch %s → %s", "on", r.status_code)


st_client = SmartThingsClient()
