import pulumi_docker as docker
from pydantic import BaseModel, ConfigDict, PositiveInt


class Healthcheck(BaseModel):
    model_config = ConfigDict(strict=True)

    tests: list[str]
    interval: str | None = None
    retries: PositiveInt | None = None
    start_period: str | None = None
    timeout: str | None = None

    def to_container_healthcheck(self) -> docker.ContainerHealthcheckArgs:
        return docker.ContainerHealthcheckArgs(
            tests=self.tests,
            interval=self.interval,
            retries=self.retries,
            start_period=self.start_period,
            timeout=self.timeout,
        )
