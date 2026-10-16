import logging
import os
import sys


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def configure_logging() -> None:
    logging.basicConfig(
        level=LOG_LEVEL,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s"
        ),
        stream=sys.stdout,
        force=True,
    )
