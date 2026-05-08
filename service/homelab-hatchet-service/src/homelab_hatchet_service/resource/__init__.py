import typing

from homelab_docker.extract import ExtractorArgs
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.file.config import ConfigFileResource, JsonDumper
from homelab_hatchet_config.model.task.schedule import HatchetTaskScheduleArgs
from homelab_hatchet_tool.schedule.model import ScheduleConfig
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from .. import HatchetService


class HatchetWorkflowResource(FileResource, module="hatchet", name="Workflow"):
    def __init__(
        self,
        resource_name: str | None,
        content: str,
        *,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> None:
        resource_name = resource_name or extractor_args.service.name()
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=hatchet_service.get_workflow_volume_path(resource_name),
            content=content,
            permission=hatchet_service.user,
            extractor_args=hatchet_service.extractor_args,
        )


class HatchetScheduleResource(
    ConfigFileResource[ScheduleConfig], module="hatchet", name="Schedule"
):
    validator = ScheduleConfig
    dumper = JsonDumper[ScheduleConfig]

    def __init__(
        self,
        resource_name: str | None,
        schedules: dict[str | None, HatchetTaskScheduleArgs],
        *,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> None:
        resource_name = resource_name or extractor_args.service.name()
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=hatchet_service.get_schedule_volume_path(resource_name),
            data={
                (key or ScheduleConfig.NONE_KEY): {
                    "workflow": value.workflow,
                    "schedules": value.schedules,
                    "input": value.input,
                }
                for key, value in schedules.items()
            },
            permission=hatchet_service.user,
            extractor_args=hatchet_service.extractor_args,
        )
