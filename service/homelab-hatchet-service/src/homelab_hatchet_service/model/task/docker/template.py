from hatchet_sdk import Context, EmptyModel, Hatchet
from homelab_hatchet_tool.docker import Docker
from homelab_hatchet_tool.worker import label

hatchet = Hatchet()


@hatchet.task(
    desired_worker_labels=[label.DESIRED_HOST_LABEL, label.DESIRED_DOCKER_LABEL]
)
async def run(_: EmptyModel, context: Context) -> None:
    service = "#service"
    name = "#name"
    return await Docker.load_and_run_model(context, service, name)


@hatchet.task(
    desired_worker_labels=[label.DESIRED_HOST_LABEL, label.DESIRED_DOCKER_LABEL]
)
async def exec(_: EmptyModel, context: Context) -> None:
    service = "#service"
    name = "#name"
    return await Docker.load_and_run_model(context, service, name)
