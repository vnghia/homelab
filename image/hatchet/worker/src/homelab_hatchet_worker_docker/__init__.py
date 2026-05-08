from hatchet_sdk import ClientConfig, Hatchet
from homelab_hatchet_tool.config import Config
from homelab_hatchet_tool.docker import Docker
from homelab_hatchet_tool.worker import NAMESPACE_SEPARATOR, label

from . import setup
from .schedule.loader import ScheduleLoader
from .workflow.loader import WorkflowLoader
from .workflow.types import Workflow

config = Config.load()
setup.otel()
logger = setup.logger(config)

hatchet = Hatchet(config=ClientConfig(debug=config.log_level == "DEBUG", logger=logger))


def main() -> None:
    logger.info(config.model_dump_json())
    worker = hatchet.worker(
        label.HOST_VALUE + ((NAMESPACE_SEPARATOR + config.name) if config.name else ""),
        labels={
            label.HOST_LABEL: label.HOST_VALUE,
            label.DOCKER_LABEL: label.DOCKER_VALUE,
        },
    )

    namespace = label.HOST_VALUE
    static_workflows = Workflow.register_models(
        hatchet, worker, namespace, Docker.build_workflows(hatchet)
    )

    workflow_loader = WorkflowLoader(
        hatchet, worker, config, namespace, static_workflows
    )
    workflow_loader.watch()

    schedule_loader = ScheduleLoader(workflow_loader)
    schedule_loader.watch()

    worker.start()
