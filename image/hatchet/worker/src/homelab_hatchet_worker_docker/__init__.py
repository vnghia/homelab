import logging
import sys

from hatchet_sdk import ClientConfig, Context, EmptyModel, Hatchet, Worker
from homelab_hatchet_tool.config import Config

config = Config.load()

logging.basicConfig(
    level=logging.INFO if not config.debug else logging.DEBUG, stream=sys.stdout
)
logger = logging.getLogger()

hatchet = Hatchet(config=ClientConfig(debug=config.debug, logger=logger))


@hatchet.task()
async def dummy(input: EmptyModel, ctx: Context) -> dict[str, str]:
    return {}


def load_workflows(hatchet: Hatchet, worker: Worker, config: Config) -> None:
    for path in config.workflow_dir.glob("*.py"):
        logger.info("Loading workflow from %s", path)


def main() -> None:
    logger.info(config)
    worker = hatchet.worker("worker", workflows=[dummy])
    load_workflows(hatchet, worker, config)
    worker.start()
