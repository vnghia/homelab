import typing

from homelab_docker.resource.file.config import ConfigFileResource, YamlDumper
from pulumi import ResourceOptions

from homelab_dagu_service import DaguService

from ..model import DaguDagModel
from . import schema

if typing.TYPE_CHECKING:
    from .. import DaguService


class DaguDagResource(ConfigFileResource[schema.Model], module="dagu", name="DAG"):
    validator = schema.Model
    dumper = YamlDumper

    def __init__(
        self,
        resource_name: str,
        model: DaguDagModel,
        *,
        opts: ResourceOptions | None,
        dagu_service: "DaguService",
    ):
        super().__init__(
            resource_name,
            opts=opts,
            container_volume_path=dagu_service.get_dag_container_volume_path(
                model.path or resource_name
            ),
            data=model.to_data(dagu_service),
            volume_resource=dagu_service.docker_resource_args.volume,
        )
