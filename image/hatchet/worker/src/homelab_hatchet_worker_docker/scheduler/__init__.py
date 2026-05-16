import asyncio
import datetime
import logging
from typing import Any

import aiofiles
import croniter
from dateutil import tz
from hatchet_sdk import Context, EmptyModel, Hatchet
from hatchet_sdk.clients.rest.models.scheduled_run_status import ScheduledRunStatus
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_hatchet_tool import label
from homelab_hatchet_tool.config import Config, ConfigDependency
from homelab_hatchet_tool.schedule.model import ScheduleConfig
from homelab_pydantic import add_namespace

from ..workflow.loader import WorkflowLoader

logger = logging.getLogger("scheduler")


class Scheduler:
    NAME = "scheduler"
    LABEL_NAME = "{}-name".format(NAME)

    METADATA = label.build_labels(None)

    @classmethod
    def build_workflows(
        cls, hatchet: Hatchet, config: Config
    ) -> list[BaseWorkflow[Any]]:
        @hatchet.task(
            name=cls.NAME,
            on_crons=config.scheduler_cron,
            concurrency=1,
            desired_worker_labels=[label.DESIRED_HOST_LABEL],
            default_additional_metadata=label.build_labels(cls.NAME),
        )
        async def scheduler(
            input: EmptyModel, context: Context, config: ConfigDependency
        ) -> None:
            now = datetime.datetime.now(tz.tzlocal())
            workflow_loader = WorkflowLoader.instance()

            for path in await asyncio.to_thread(
                lambda: config.scheduler_dir.glob("*.json")
            ):
                logger.info("Running scheduler for {}".format(path))
                async with aiofiles.open(path) as file:
                    schedule = ScheduleConfig.model_validate_json(await file.read())

                for name, model in schedule.root.items():
                    namespaced_name = add_namespace(path.stem, name)
                    workflow = workflow_loader[model.workflow]
                    next_run = min(
                        [
                            croniter.croniter(
                                schedule,
                                start_time=now,
                                ret_type=datetime.datetime,
                                day_or=False,
                                max_years_between_matches=1,
                                second_at_beginning=True,
                                expand_from_start_time=False,
                            ).next()
                            for schedule in model.schedules
                        ]
                    )

                    metadata = cls.METADATA | {cls.LABEL_NAME: namespaced_name}

                    need_schedule = True
                    scheduled_workflows = (
                        await hatchet.scheduled.aio_list(
                            workflow_id=workflow.id,
                            statuses=[ScheduledRunStatus.SCHEDULED],
                            additional_metadata=metadata,
                        )
                    ).rows
                    if scheduled_workflows:
                        for scheduled_workflow in scheduled_workflows:
                            if scheduled_workflow.trigger_at != next_run:
                                await hatchet.scheduled.aio_delete(
                                    scheduled_id=scheduled_workflow.metadata.id
                                )
                            else:
                                logger.info(
                                    "Already scheduled workflow {} next run at {}".format(
                                        workflow.name, next_run
                                    )
                                )
                                need_schedule = False

                    if need_schedule:
                        logger.info(
                            "Scheduling workflow {} next run at {}".format(
                                workflow.name, next_run
                            )
                        )
                        await hatchet.scheduled.aio_create(
                            workflow_name=workflow.name,
                            trigger_at=next_run.astimezone(datetime.timezone.utc),
                            input=workflow.model.input_validator.validate_python(
                                model.input or {}
                            ).model_dump(mode="json"),
                            additional_metadata=metadata,
                        )

        return [scheduler]
