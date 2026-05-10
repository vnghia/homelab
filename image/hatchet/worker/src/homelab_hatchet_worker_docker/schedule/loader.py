import dataclasses
import logging
import threading
from collections import defaultdict
from pathlib import Path
from typing import ClassVar

import watchfiles
from hatchet_sdk import Hatchet, Worker
from homelab_hatchet_tool.config import Config
from homelab_hatchet_tool.schedule.model import ScheduleConfig
from homelab_hatchet_tool.worker import NAMESPACE_SEPARATOR, label
from homelab_pydantic import add_namespace
from pydantic import ValidationError

from ..workflow.loader import WorkflowLoader
from .types import NamespacedExpressionScheduleWorkflows, ScheduleWorkflow

logger = logging.getLogger("schedule")


@dataclasses.dataclass
class ScheduleLoader:
    SOURCE_LABEL: ClassVar[str] = "schedule-source"
    SOURCE_VALUE: ClassVar[str] = "provisioned"

    NAMESPACE_LABEL: ClassVar[str] = "schedule-namespace"

    METADATA: ClassVar[dict[str, str]] = {
        SOURCE_LABEL: SOURCE_VALUE,
        label.HOST_LABEL: label.HOST_VALUE,
    }

    workflow_loader: WorkflowLoader

    schedules: dict[str, NamespacedExpressionScheduleWorkflows] = dataclasses.field(
        default_factory=lambda: defaultdict(
            lambda: NamespacedExpressionScheduleWorkflows(root=defaultdict(dict))
        )
    )

    @property
    def hatchet(self) -> Hatchet:
        return self.workflow_loader.hatchet

    @property
    def worker(self) -> Worker:
        return self.workflow_loader.worker

    @property
    def config(self) -> Config:
        return self.workflow_loader.config

    @property
    def namespace(self) -> str | None:
        return self.workflow_loader.namespace

    def __post_init__(self) -> None:
        for schedule in (
            self.hatchet.cron.list(additional_metadata=self.METADATA).rows or []
        ):
            if not schedule.name:
                logger.warning("Expecting a named schedule, got {}".format(schedule))
                continue

            namespace = str((schedule.additional_metadata or {})[self.NAMESPACE_LABEL])
            self.schedules[namespace].root[schedule.name][schedule.cron] = (
                ScheduleWorkflow(
                    id=schedule.metadata.id,
                    workflow=self.workflow_loader[schedule.workflow_name].name,
                    input=schedule.input,
                )
            )

        new_namespaces = [
            new_namespace
            for path in self.config.schedule_dir.glob("*.json")
            if (new_namespace := self.load(path))
        ]

        for old_namespace in self.schedules:
            if old_namespace not in new_namespaces:
                self.delete_old_schedule(self.schedules.pop(old_namespace))

    def delete_old_schedule(
        self, schedules: NamespacedExpressionScheduleWorkflows
    ) -> None:
        for full_name, expression_schedules in schedules.root.items():
            for expression, schedule in expression_schedules.items():
                logger.info(
                    "Deleting schedule {}:{}:{}".format(
                        full_name, expression, schedule.id
                    )
                )
                self.hatchet.cron.delete(schedule.id)

    def load(self, path: Path | str) -> str | None:
        path = Path(path).resolve(True)
        logger.info("Loading schedule from {}".format(path))

        namespace = path.stem
        old_schedules = self.schedules.pop(namespace, None)
        logger.info("Old {} schedule: {}".format(namespace, old_schedules))
        new_schedules = NamespacedExpressionScheduleWorkflows(root=defaultdict(dict))

        with open(path) as file:
            try:
                schedule_config = ScheduleConfig.model_validate_json(file.read())
            except ValidationError as exception:
                logger.exception(exception)
                return None

            for name, config in schedule_config.root.items():
                full_name = add_namespace(
                    self.namespace,
                    add_namespace(namespace, name),
                    separator=NAMESPACE_SEPARATOR,
                )

                workflow = self.workflow_loader[config.workflow]

                try:
                    input = workflow.model.input_validator.validate_python(
                        config.input or {}
                    )
                except ValidationError as exception:
                    logger.exception(exception)
                    continue

                expression_schedules = {}
                for expression in config.schedules:
                    new_schedule = None
                    old_schedule = (
                        old_schedules.root.get(full_name, {}).pop(expression, None)
                        if old_schedules
                        else None
                    )

                    if old_schedule:
                        try:
                            old_input = workflow.model.input_validator.validate_python(
                                old_schedule.input or {}
                            )
                        except ValidationError:
                            old_input = None

                        if input != old_input or workflow.name != old_schedule.workflow:
                            logger.info(
                                "Deleting schedule {}:{}:{}".format(
                                    full_name, expression, old_schedule.id
                                )
                            )
                            self.hatchet.cron.delete(old_schedule.id)
                        else:
                            new_schedule = old_schedule

                    if not new_schedule:
                        logger.info(
                            "Creating schedule {}:{}:{}".format(
                                full_name, workflow.name, expression
                            )
                        )
                        schedule_id = workflow.model.create_cron(
                            full_name,
                            expression,
                            input=input,
                            additional_metadata=self.METADATA
                            | {self.NAMESPACE_LABEL: namespace},
                        ).metadata.id
                        new_schedule = ScheduleWorkflow(
                            id=schedule_id, workflow=workflow.name, input=config.input
                        )

                    expression_schedules[expression] = new_schedule
                new_schedules.root[full_name] = expression_schedules

        if old_schedules:
            self.delete_old_schedule(old_schedules)

        logger.info("New {} schedule: {}".format(namespace, new_schedules))
        self.schedules[namespace] = new_schedules
        return namespace

    def unload(self, path: Path | str) -> None:
        path = Path(path)
        logger.info("Unloading schedule from {}".format(path))

        schedules = self.schedules.pop(path.stem)
        for full_name, expression_schedules in schedules.root.items():
            for expression, expression_schedule in expression_schedules.items():
                logger.info(
                    "Deleting schedule {}:{}:{}".format(
                        full_name, expression, expression_schedule.id
                    )
                )
                self.hatchet.cron.delete(expression_schedule.id)

    def watch(self) -> None:
        def _watch() -> None:
            schedule_dir = self.config.schedule_dir
            logger.info("Watching for schedules in {}".format(schedule_dir))

            for changes in watchfiles.watch(
                schedule_dir,
                watch_filter=lambda _, path: path.endswith(".json"),
                raise_interrupt=False,
                recursive=False,
            ):
                for change, file in changes:
                    match change:
                        case watchfiles.Change.added | watchfiles.Change.modified:
                            self.load(file)
                        case watchfiles.Change.deleted:
                            path = Path(file)
                            if not path.exists():
                                self.unload(path)

        threading.Thread(target=_watch, daemon=True).start()
