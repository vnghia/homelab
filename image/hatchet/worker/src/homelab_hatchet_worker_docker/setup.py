import logging
import sys

from hatchet_sdk import logger as hatchet_logger
from hatchet_sdk.opentelemetry.instrumentor import HatchetInstrumentor
from homelab_hatchet_tool.config import Config


def logger(config: Config) -> logging.Logger:
    hatchet_logger.logger.removeHandler(hatchet_logger.handler)

    logging.basicConfig(
        level=logging.getLevelNamesMapping()[config.log_level],
        stream=sys.stdout,
        format="[%(levelname)s] - %(message)s",
    )
    return logging.getLogger()


def otel() -> None:
    HatchetInstrumentor().instrument()
