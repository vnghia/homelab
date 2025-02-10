import pulumi_docker as docker
import pulumi_docker_build as docker_build
from pulumi import ResourceOptions
from pydantic import BaseModel

from homelab_docker.model.build.context import BuildContextModel


class BuildModel(BaseModel):
    context: BuildContextModel
    labels: dict[str, str] = {}

    @classmethod
    def get_name(cls, resource_name: str, project_prefix: str) -> str:
        return "{}-{}".format(project_prefix, resource_name)

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        remote_images: dict[str, docker.RemoteImage],
        project_prefix: str,
        project_labels: dict[str, str],
    ) -> docker_build.Image:
        return docker_build.Image(
            resource_name,
            opts=ResourceOptions.merge(
                opts, ResourceOptions(delete_before_replace=True)
            ),
            context=self.context.to_args(remote_images),
            load=True,
            labels=self.labels | project_labels,
            push=False,
            tags=[self.get_name(resource_name, project_prefix)],
        )
