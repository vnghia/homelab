from hatchet_sdk import Context, EmptyModel, Hatchet
from homelab_hatchet_tool.config import ConfigDependency
from homelab_hatchet_tool.docker import Docker
from homelab_hatchet_tool.docker.model.exec import DockerContainerExecModel
from homelab_hatchet_tool.docker.model.run import DockerContainerRunModel
from homelab_hatchet_tool.worker import label

hatchet = Hatchet()


@hatchet.task(
    desired_worker_labels=[label.DESIRED_HOST_LABEL, label.DESIRED_DOCKER_LABEL]
)
async def run(_: EmptyModel, context: Context, config: ConfigDependency) -> None:
    service = "#service"
    container = "#container"
    name = "#name"
    return await Docker.load_and_run_model(
        context,
        DockerContainerRunModel(service=service, container=container, name=name),
        config,
    )


@hatchet.task(
    desired_worker_labels=[label.DESIRED_HOST_LABEL, label.DESIRED_DOCKER_LABEL]
)
async def exec(_: EmptyModel, context: Context, config: ConfigDependency) -> None:
    service = "#service"
    exec = "#exec"
    return await Docker.load_and_exec_model(
        context, DockerContainerExecModel(service=service, exec=exec), config
    )
