from hatchet_sdk import DesiredWorkerLabel, WorkerLabelComparator

from ..config import Config

HOST_LABEL = "host"
DESIRED_HOST_LABEL = DesiredWorkerLabel(
    key=HOST_LABEL,
    value=Config.load().host,
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
