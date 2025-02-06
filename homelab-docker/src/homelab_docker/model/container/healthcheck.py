import pulumi_docker as docker
from pydantic import BaseModel, PositiveInt


class ContainerHealthCheckConfig(BaseModel):
    tests: list[str]
    interval: str | None = None
    retries: PositiveInt | None = None
    start_period: str | None = None
    timeout: str | None = None

    def to_args(self) -> docker.ContainerHealthcheckArgs:
        return docker.ContainerHealthcheckArgs(
            tests=self.tests,
            interval=self.interval,
            retries=self.retries,
            start_period=self.start_period,
            timeout=self.timeout,
        )
