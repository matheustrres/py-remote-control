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
    tv_mac_raw: str = field(default_factory=lambda: _env("TV_MAC"))
    st_token: str = field(default_factory=lambda: _env("ST_TOKEN"))
    st_tv_id: str = field(default_factory=lambda: _env("ST_TV_ID"))
    tv_token: str = field(default_factory=lambda: os.getenv("TV_TOKEN", ""))  # pode faltar
    tv_device_id: str = field(default_factory=lambda: os.getenv("TV_DEVICE_ID", ""))

    tv_mac: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "tv_mac", self.tv_mac_raw.replace(":", "").replace("-", ""))

        if not self.tv_device_id:
            new_tv_device_id = f"uuid-{uuid.uuid4()}"
            self._persist(".env", "TV_DEVICE_ID", new_tv_device_id)
            object.__setattr__(self, "tv_device_id", new_tv_device_id)

    @staticmethod
    def _persist(env_file: str | Path, key: str, value: str) -> None:
        set_key(str(env_file), key, value, quote_mode="never")
        logging.debug("Set key %s in %s", key.upper(), env_file)

    @staticmethod
    def set_key(key: str, value: str) -> None:
        set_key(".env", key, value)
        logging.info("Set key %s in .env", key.upper())


cfg = Config()
