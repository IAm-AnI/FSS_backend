import logging
import sys

logger = logging.getLogger("API Logger")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(name)s - [%(message)s]"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.propagate = False