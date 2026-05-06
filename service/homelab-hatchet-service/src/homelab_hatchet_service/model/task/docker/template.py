from hatchet_sdk import Context, EmptyModel, Hatchet
from homelab_hatchet_tool.config import Config
from homelab_hatchet_tool.docker import Docker

hatchet = Hatchet()


@hatchet.task(desired_worker_labels=[Config.get_worker_host_label()])
async def run(_: EmptyModel, context: Context) -> None:
    service = "#service"
    name = "#name"
    return await Docker.load_and_run_model(context, service, name)


@hatchet.task(desired_worker_labels=[Config.get_worker_host_label()])
async def exec(_: EmptyModel, context: Context) -> None:
    service = "#service"
    name = "#name"
    return await Docker.load_and_run_model(context, service, name)
