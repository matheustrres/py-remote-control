import uuid, logging, os, sys, base64
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv, set_key

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

APP_NAME = "PyRemote"
APP_ENC_NAME = base64.b64encode(APP_NAME.encode()).decode()
ST_API_URL = "https://api.smartthings.com/v1"
WS_PORT_TLS = 8002


def _env(key: str, *, required: bool = True, default: str | None = None) -> str:
    val = os.getenv(key, default)
    if required and not val:
        sys.exit(f"✖  Missing key {key} in .env")
    return val


@dataclass(frozen=True, slots=True)
class Config:
    tv_ip: str = field(default_factory=lambda: _env("TV_IP"))
    tv_mac_raw: str = field(default_factory=lambda: _env("TV_MAC").replace(":", "").replace("-", ""))
    st_token: str = field(default_factory=lambda: _env("ST_TOKEN"))
    st_tv_id: str = field(default_factory=lambda: _env("ST_TV_ID"))
    tv_token: str = field(default_factory=lambda: os.getenv("TV_TOKEN", ""))
    tv_device_id: str = field(default_factory=lambda: os.getenv("TV_DEVICE_ID", ""))

    tv_mac: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "tv_mac", self.tv_mac_raw)

        if not self.tv_device_id:
            new_tv_device_id = f"uuid-{uuid.uuid4()}"
            self.set_key("TV_DEVICE_ID", new_tv_device_id)
            object.__setattr__(self, "tv_device_id", new_tv_device_id)

    @staticmethod
    def set_key(key: str, value: str) -> None:
        set_key(ENV_FILE, key, value, quote_mode="never")
        logging.warning("Set key %s in %s", key.upper(), ENV_FILE)


cfg = Config()
