from hatchet_sdk import DesiredWorkerLabel, WorkerLabelComparator

from .. import IS_INSIDE_WORKER_ENVIRONMENT
from ..config import Config

HOST_LABEL = "host"
HOST_VALUE = "" if not IS_INSIDE_WORKER_ENVIRONMENT else Config.load().host
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
