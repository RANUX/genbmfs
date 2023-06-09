import logging 
import sys
from config import LOG_LEVEL

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(LOG_LEVEL)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(message)s'))
    logger.addHandler(handler)
    return logger