import dataclasses
import logging
import sys
import threading
from pathlib import Path

import watchfiles
from hatchet_sdk import Hatchet, Worker
from homelab_hatchet_tool.config import Config

from .module import WorkflowModule

config = Config.load()
logger = logging.getLogger("workflow")


@dataclasses.dataclass
class WorkflowLoader:
    hatchet: Hatchet
    worker: Worker
    config: Config
    namespace: str | None

    def __post_init__(self) -> None:
        sys.path.append(config.workflow_dir.as_posix())
        for path in config.workflow_dir.glob("*.py"):
            WorkflowModule.load(self.hatchet, self.worker, self.namespace, path)

        for workflow_data in self.hatchet.workflows.list(self.namespace).rows or []:
            if self.namespace and not workflow_data.name.startswith(self.namespace):
                continue

            should_delete = True
            for module in WorkflowModule.instances.values():
                if workflow_data.name in module.workflows:
                    should_delete = False
                    break

            if should_delete:
                logger.info(
                    "Deleting stale workflow {}:{}".format(
                        workflow_data.name, workflow_data.metadata.id
                    )
                )
                self.hatchet.workflows.delete(workflow_data.metadata.id)

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
                            WorkflowModule.load(
                                self.hatchet, self.worker, self.namespace, file
                            )
                        case watchfiles.Change.deleted:
                            path = Path(file)
                            if not path.exists():
                                WorkflowModule.unload(self.hatchet, path)

        threading.Thread(target=_watch, daemon=True).start()
