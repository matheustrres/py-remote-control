import uuid, logging, os, sys
from dotenv import load_dotenv, set_key

load_dotenv()


class Config:
    def __init__(self) -> None:
        self.ST_API_URL = "https://api.smartthings.com/v1"
        self.TV_IP = os.getenv("TV_IP") or sys.exit("Missing TV_IP in .env")
        self.TV_MACRAW = os.getenv("TV_MAC") or sys.exit("Missing TV_MAC in .env")
        self.TV_MAC = self.TV_MACRAW.replace(":", "").replace("-", "")
        self.ST_TOKEN = os.getenv("ST_TOKEN") or sys.exit("Missing ST_TOKEN in .env")
        self.ST_TV_ID = os.getenv("ST_TV_ID") or sys.exit("Missing ST_TV_ID in .env")
        self.TOKEN = os.getenv("TV_TOKEN", "")

        self.TV_DEVICE_ID = os.getenv("TV_DEVICE_ID")
        if not self.TV_DEVICE_ID:
            self.TV_DEVICE_ID = f"uuid-{uuid.uuid4()}"
            self.set_key("TV_DEVICE_ID", self.TV_DEVICE_ID)
            logging.info("Set TV_DEVICE_ID in .env")

    @staticmethod
    def set_key(key: str, value: str) -> None:
        set_key(".env", key, value)
        logging.info("Set key %s in .env", key.upper())


cfg = Config()
