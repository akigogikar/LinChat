import logging
import os


def setup_logging():
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE")
    fmt = "%(asctime)s %(levelname)s %(name)s - %(message)s"
    if log_file:
        logging.basicConfig(filename=log_file, level=level, format=fmt)
    else:
        logging.basicConfig(level=level, format=fmt)
