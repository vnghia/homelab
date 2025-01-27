import homelab_docker as docker
from pydantic import BaseModel, ValidationInfo, field_validator

from homelab.config.docker.service import Service
from homelab.config.docker.volume import Volume


class Docker(BaseModel):
    platform: docker.image.Platform
    images: dict[str, docker.image.Remote]
    volumes: Volume
    services: dict[str, Service]

    @field_validator("images", mode="after")
    @classmethod
    def set_image_platform(
        cls, images: dict[str, docker.image.Remote], info: ValidationInfo
    ) -> dict[str, docker.image.Remote]:
        return {
            name: (
                model
                if model.platform
                else model.model_copy(update={"platform": info.data["platform"]})
            )
            for name, model in images.items()
        }
