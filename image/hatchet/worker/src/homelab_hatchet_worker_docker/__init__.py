import dataclasses
import importlib
import sys
import threading
import types
from pathlib import Path
from typing import Any, ClassVar, Self

import watchfiles
from hatchet_sdk import ClientConfig, Hatchet, Worker
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_hatchet_tool.config import Config

from .logging import setup_logger

config = Config.load()
logger = setup_logger(config)

hatchet = Hatchet(
    config=ClientConfig(
        debug=config.log_level == "DEBUG", logger=logger, namespace=config.host
    )
)


@dataclasses.dataclass
class ModuleWorkflow:
    instances: ClassVar[dict[Path, Self]] = {}

    module: types.ModuleType
    workflows: dict[str, BaseWorkflow[Any]]

    @classmethod
    def delete_workflow(cls, hatchet: Hatchet, name: str) -> None:
        for workflow in hatchet.workflows.list(name).rows or []:
            id = workflow.metadata.id
            logger.info("Deleting workflow {}:{}".format(workflow.name, id))
            hatchet.workflows.delete(id)

    @classmethod
    def load(cls, hatchet: Hatchet, worker: Worker, path: Path | str) -> Self:
        path = Path(path).resolve(True)
        logger.info("Loading module from {}".format(path))

        if path in cls.instances:
            instance = cls.instances[path]
            module = importlib.reload(instance.module)
            old_workflows = instance.workflows
        else:
            module = importlib.import_module(path.stem)
            old_workflows = {}

        workflows = {}
        for workflow in module.build_workflows(hatchet):
            if not isinstance(workflow, BaseWorkflow):
                raise ValueError("Object {} is not a valid workflow".format(workflow))
            logger.info("Registering workflow {}:{}".format(path.stem, workflow.name))
            worker.register_workflow(workflow)
            workflows[workflow.name] = workflow

        for name in old_workflows:
            if name not in workflows:
                cls.delete_workflow(hatchet, name)

        instance = cls(module=module, workflows=workflows)
        cls.instances[path] = instance
        return instance

    @classmethod
    def unload(cls, hatchet: Hatchet, path: Path | str) -> None:
        path = Path(path)
        logger.info("Unloading module from {}".format(path))

        instance = cls.instances.pop(path)
        for name in instance.workflows:
            cls.delete_workflow(hatchet, name)

        importlib.invalidate_caches()


@dataclasses.dataclass
class WorkflowLoader:
    hatchet: Hatchet
    worker: Worker
    config: Config
    modules: dict[Path, ModuleWorkflow] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        sys.path.append(config.workflow_dir.as_posix())
        for path in config.workflow_dir.glob("*.py"):
            ModuleWorkflow.load(self.hatchet, self.worker, path)

    def watch(self) -> None:
        def _watch() -> None:
            workflow_dir = self.config.workflow_dir
            logger.info("Watching for modules in {}".format(workflow_dir))

            for changes in watchfiles.watch(
                workflow_dir,
                watch_filter=lambda _, path: path.endswith(".py"),
                raise_interrupt=False,
                recursive=False,
            ):
                for change, file in changes:
                    match change:
                        case watchfiles.Change.added | watchfiles.Change.modified:
                            ModuleWorkflow.load(self.hatchet, self.worker, file)
                        case watchfiles.Change.deleted:
                            path = Path(file)
                            if not path.exists():
                                ModuleWorkflow.unload(self.hatchet, path)

        threading.Thread(target=_watch, daemon=True).start()


def main() -> None:
    logger.info(config.model_dump_json())
    worker = hatchet.worker(
        config.name or "worker", labels={config.HOST_LABEL: config.host}
    )
    WorkflowLoader(hatchet, worker, config).watch()
    worker.start()
