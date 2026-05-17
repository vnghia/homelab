from hatchet_sdk import DesiredWorkerLabel, WorkerLabelComparator

from .config import Config

NAMESPACE_SEPARATOR = "."

HOST_LABEL = "host"
HOST_VALUE = Config.load().host
DESIRED_HOST_LABEL = DesiredWorkerLabel(
    key=HOST_LABEL,
    value=HOST_VALUE,
    comparator=WorkerLabelComparator.EQUAL,
    required=True,
)

DOCKER_LABEL = "docker"
DOCKER_VALUE = 1
DESIRED_DOCKER_LABEL = DesiredWorkerLabel(
    key=DOCKER_LABEL,
    value=DOCKER_VALUE,
    comparator=WorkerLabelComparator.EQUAL,
    required=True,
)

SOURCE_LABEL = "source"
SOURCE_VALUE = "provisioned"

SERVICE_LABEL = "service"

INPUT_ALL = "all"


def build_labels(service: str | None) -> dict[str, str]:
    return {HOST_LABEL: HOST_VALUE, SOURCE_LABEL: SOURCE_VALUE} | (
        {SERVICE_LABEL: service} if service else {}
    )
