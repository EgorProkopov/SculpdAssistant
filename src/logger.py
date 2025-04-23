import logging
from logging import Logger
from typing import Optional


def get_logger(name: Optional[str] = None, level: int = logging.INFO) -> Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.propagate = False

    return logger