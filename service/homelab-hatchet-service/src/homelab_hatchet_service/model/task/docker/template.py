from hatchet_sdk import Context, EmptyModel, Hatchet
from homelab_hatchet_tool import label
from homelab_hatchet_tool.config import ConfigDependency
from homelab_hatchet_tool.docker import Docker
from homelab_hatchet_tool.docker.model.exec import DockerContainerExecConfig
from homelab_hatchet_tool.docker.model.run import DockerContainerRunConfig

hatchet = Hatchet()


@hatchet.task(
    desired_worker_labels=[label.DESIRED_HOST_LABEL, label.DESIRED_DOCKER_LABEL]
)
async def run(_: EmptyModel, context: Context, config: ConfigDependency) -> None:
    service = "#service"
    container = "#container"
    name = "#name"
    await Docker.run_container(
        context,
        await DockerContainerRunConfig(
            service=service, container=container, name=name
        ).load(config),
    )


@hatchet.task(
    desired_worker_labels=[label.DESIRED_HOST_LABEL, label.DESIRED_DOCKER_LABEL]
)
async def exec(_: EmptyModel, context: Context, config: ConfigDependency) -> None:
    service = "#service"
    exec = "#exec"
    await Docker.exec_container(
        context,
        await DockerContainerExecConfig(service=service, exec=exec).load(config),
    )
