import dataclasses
from pathlib import PosixPath
from typing import Any, Sequence

from homelab_docker.model.file.config import ConfigFileModel
from homelab_docker.pydantic.path import RelativePath
from homelab_docker.resource.file.config import ConfigFileResource
from homelab_docker.resource.volume import VolumeResource
from pulumi import ResourceOptions
from pydantic import HttpUrl, PositiveInt

from homelab_dagu_service import DaguService

from .step import DaguDagStepConfig


@dataclasses.dataclass
class DaguDagConfig:
    steps: list[DaguDagStepConfig]

    path: RelativePath | None = None

    name: str | None = None
    group: str | None = None
    tags: list[str] | None = None
    schedule: str | None = None
    max_active_runs: PositiveInt | None = None

    params: dict[str, Any] | None = None

    # def build_resource(
    #     self,
    #     resource_name: str,
    #     *,
    #     opts: ResourceOptions | None,
    #     dagu_service: DaguService,
    #     volume_resource: VolumeResource,
    #     env_files: Sequence[ConfigFileResource] | None = None,
    # ) -> ConfigFileResource:
    #     return ConfigFileModel(
    #         container_volume_path=dagu_service.get_config_container_volume_path().join(
    #             self.path or PosixPath(resource_name), ".yaml"
    #         ),
    #         data={
    #             "steps": [step.dict() for step in self.steps],
    #         }
    #         | (
    #             {
    #                 "dotenv": [
    #                     env_file.to_container_path(
    #                         dagu_service.model.container.volumes
    #                     ).as_posix()
    #                     for env_file in env_files
    #                 ]
    #             }
    #             if env_files
    #             else {}
    #         )
    #         | ({"name": self.name} if self.name else {})
    #         | ({"group": self.group} if self.group else {})
    #         | ({"tags": ",".join(self.tags)} if self.tags else {})
    #         | ({"schedule": self.schedule} if self.schedule else {})
    #         | ({"maxActiveRuns": self.max_active_runs} if self.max_active_runs else {})
    #         | (
    #             {"params": [{key: param} for key, param in self.params.items()]}
    #             if self.params
    #             else {}
    #         ),
    #         schema_url=HttpUrl(
    #             "https://raw.githubusercontent.com/dagu-org/dagu/refs/heads/main/schemas/dag.schema.json"
    #         ),
    #     ).build_resource(
    #         resource_name,
    #         opts=ResourceOptions.merge(opts, ResourceOptions(depends_on=env_files)),
    #         volume_resource=volume_resource,
    #     )
