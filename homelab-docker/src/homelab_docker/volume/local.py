from pathlib import PosixPath

import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict, field_validator


class Local(BaseModel):
    model_config = ConfigDict(strict=True)

    resource_name: str
    name: str | None = None

    bind: PosixPath | None = None
    labels: dict[str, str] = {}

    @field_validator("bind", mode="after")
    @classmethod
    def check_bind_absolute_path(cls, bind: PosixPath | None) -> PosixPath | None:
        if bind and not bind.is_absolute():
            raise ValueError("`bind` path must be absolute")
        return bind

    def build_resource(self, opts: ResourceOptions | None) -> docker.Volume:
        return docker.Volume(
            self.resource_name,
            opts=opts,
            name=self.name,
            driver="local",
            driver_opts={
                "type": "none",
                "o": "bind",
                "device": self.bind.as_posix(),
            }
            if self.bind
            else None,
            labels=[
                docker.VolumeLabelArgs(label=k, value=v) for k, v in self.labels.items()
            ],
        )
