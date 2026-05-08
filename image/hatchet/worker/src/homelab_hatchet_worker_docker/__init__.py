from hatchet_sdk import ClientConfig, Hatchet
from homelab_hatchet_tool.config import Config
from homelab_hatchet_tool.docker import Docker
from homelab_hatchet_tool.worker import NAMESPACE_SEPARATOR, label

from . import setup
from .workflow.loader import WorkflowLoader
from .workflow.types import Workflow

config = Config.load()
setup.otel()
logger = setup.logger(config)

hatchet = Hatchet(config=ClientConfig(debug=config.log_level == "DEBUG", logger=logger))


def main() -> None:
    logger.info(config.model_dump_json())
    worker = hatchet.worker(
        config.host + ((NAMESPACE_SEPARATOR + config.name) if config.name else ""),
        labels={label.HOST_LABEL: config.host, label.DOCKER_LABEL: label.DOCKER_VALUE},
    )

    namespace = config.host
    static_workflows = Workflow.register_models(
        hatchet, worker, namespace, Docker.build_workflows(hatchet)
    )

    workflow_loader = WorkflowLoader(
        hatchet, worker, config, namespace, static_workflows
    )
    workflow_loader.watch()

    worker.start()
