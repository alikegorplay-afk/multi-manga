__all__ = [
    "config"
]

from dataclasses import dataclass
from dotenv import load_dotenv

import logging

import os

load_dotenv()
_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

@dataclass
class Config:
    DEBUG = os.getenv("DEBUG") == "True"
    MAX_TRY = int(os.getenv("MAX_TRY")) if os.getenv("MAX_TRY") and os.getenv("MAX_TRY").isdigit() else 3
    BASE_URL = os.getenv("BASE_URL") if os.getenv("BASE_URL") else "https://multi-manga.today"
    MAX_WORKERS = int(os.getenv("MAX_WORKERS")) if os.getenv("MAX_WORKERS") and os.getenv("MAX_WORKERS").isdigit() else 5
    def logger(self, name: str):
        return LoggerFactory(name)

config = Config()

class LoggerFactory:
    def __new__(
        cls,
        name: str
    ):
        lvl = logging.DEBUG if config.DEBUG else logging.INFO
        logger = logging.getLogger(name)
        logger.setLevel(lvl)
        
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(_log_format))
        
        logger.addHandler(
            stream_handler
        )
        return logger
