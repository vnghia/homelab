import dataclasses
import importlib
import logging
import sys
import types
from pathlib import Path
from typing import ClassVar, Self

from hatchet_sdk import Hatchet, Worker

from .types import Workflow

logger = logging.getLogger("workflow")


@dataclasses.dataclass
class WorkflowModule:
    instances: ClassVar[dict[Path, Self]] = {}

    module: types.ModuleType
    workflows: dict[str, Workflow]

    @classmethod
    def load(
        cls, hatchet: Hatchet, worker: Worker, namespace: str | None, path: Path | str
    ) -> Self | None:
        path = Path(path).resolve(True)
        logger.info("Loading module from {}".format(path))

        if path in cls.instances:
            instance = cls.instances[path]
            module = importlib.reload(instance.module)
            old_workflows: dict[str, Workflow] = instance.workflows
        else:
            module = importlib.import_module(path.stem)
            old_workflows = {}

        if not hasattr(module, "build_workflows"):
            logger.warning(
                "Module `{}` does not have `build_workflows` method".format(path.stem)
            )
            return None

        workflows = Workflow.register_models(
            hatchet, worker, namespace, module.build_workflows(hatchet)
        )

        for old_workflow in old_workflows.values():
            if old_workflow.name not in workflows:
                logger.info(
                    "Deleting workflow {}:{}".format(old_workflow.name, old_workflow.id)
                )
                hatchet.workflows.delete(old_workflow.id)

        instance = cls(module=module, workflows=workflows)
        cls.instances[path] = instance
        return instance

    @classmethod
    def unload(cls, hatchet: Hatchet, path: Path | str) -> None:
        path = Path(path)
        logger.info("Unloading module from {}".format(path))

        instance = cls.instances.pop(path)
        for workflow in instance.workflows.values():
            logger.info("Deleting workflow {}:{}".format(workflow.name, workflow.id))
            hatchet.workflows.delete(workflow.id)
        del sys.modules[path.stem]
