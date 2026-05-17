from hatchet_sdk import ClientConfig, Hatchet
from homelab_hatchet_tool import constant
from homelab_hatchet_tool.config import Config
from homelab_hatchet_tool.docker import Docker

from . import setup
from .scheduler import Scheduler
from .workflow.loader import WorkflowLoader
from .workflow.types import Workflow

config = Config.load()
setup.otel()
logger = setup.logger(config)

hatchet = Hatchet(config=ClientConfig(debug=config.log_level == "DEBUG", logger=logger))


def main() -> None:
    logger.info(config.model_dump_json())
    worker = hatchet.worker(
        constant.HOST_VALUE
        + ((constant.NAMESPACE_SEPARATOR + config.name) if config.name else ""),
        slots=config.slots,
        durable_slots=config.durable_slots,
        labels={
            constant.HOST_LABEL: constant.HOST_VALUE,
            constant.DOCKER_LABEL: constant.DOCKER_VALUE,
        },
    )

    namespace = constant.HOST_VALUE
    static_workflows = Workflow.register_models(
        hatchet, worker, namespace, Docker.build_workflows(hatchet)
    ) | Workflow.register_models(
        hatchet, worker, namespace, Scheduler.build_workflows(hatchet, config)
    )
    logger.info("Staic workflows: {}".format(static_workflows))

    workflow_loader = WorkflowLoader(
        hatchet, worker, config, namespace, static_workflows
    )
    workflow_loader.watch()

    worker.start()
