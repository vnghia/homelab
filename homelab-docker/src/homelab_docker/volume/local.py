from pathlib import PosixPath

import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Local(BaseModel):
    model_config = ConfigDict(strict=True)

    bind: PosixPath | None = Field(None, strict=False)
    labels: dict[str, str] = {}

    @field_validator("bind", mode="after")
    @classmethod
    def check_bind_absolute_path(cls, bind: PosixPath | None) -> PosixPath | None:
        if bind and not bind.is_absolute():
            raise ValueError("`bind` path must be absolute")
        return bind

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions | None = None,
        name: str | None = None,
    ) -> docker.Volume:
        return docker.Volume(
            resource_name,
            opts=opts,
            name=name,
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
