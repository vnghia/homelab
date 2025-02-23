from ...model.container.volume_path import ContainerVolumePath


class ServiceContainerVolumePath(ContainerVolumePath):
    service: str | None = None
