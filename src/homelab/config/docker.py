import homelab_docker as docker
from pydantic import BaseModel, ValidationInfo, field_validator


class Docker(BaseModel):
    platform: docker.image.Platform
    image: dict[str, docker.image.Remote]

    @field_validator("image", mode="after")
    @classmethod
    def set_image_platform(
        cls, image: dict[str, docker.image.Remote], info: ValidationInfo
    ) -> dict[str, docker.image.Remote]:
        return {
            name: (
                model
                if model.platform
                else docker.image.Remote.model_copy(
                    model, update={"platform": info.data["platform"]}
                )
            )
            for name, model in image.items()
        }
