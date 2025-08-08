from collections import defaultdict

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.service import ServiceExtractor
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_extra_service import ExtraService
from homelab_pydantic.path import AbsolutePath
from pulumi import ResourceOptions

from .config import DaguConfig
from .resource import DaguDagResource


class DaguService(ExtraService[DaguConfig]):
    DEBUG_DAG_NAME = "debug"

    def __init__(
        self,
        model: ServiceWithConfigModel[DaguConfig],
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)
        self.build()

        self.dags_dir_volume_path = ServiceExtractor(
            self.config.dags_dir
        ).extract_volume_path(self.extractor_args)
        self.log_dir_volume_path = ServiceExtractor(
            self.config.log_dir
        ).extract_volume_path(self.extractor_args)

        self.dotenvs: defaultdict[str, dict[str | None, DotenvFileResource]] = (
            defaultdict(dict)
        )
        self.dags: defaultdict[str, dict[str | None, DaguDagResource]] = defaultdict(
            dict
        )

    def get_dag_volume_path(self, name: str) -> ContainerVolumePath:
        return self.dags_dir_volume_path / name

    def get_dotenv_volume_path(self, name: str) -> ContainerVolumePath:
        return self.dags_dir_volume_path / name

    def get_log_dir_volume_path(self, name: str) -> ContainerVolumePath:
        return self.log_dir_volume_path / name

    def get_tmp_dir(self) -> AbsolutePath:
        tmpfs = self.model[None].tmpfs
        if not tmpfs:
            raise ValueError("tmpfs is not configured for {}".format(self.name()))
        return tmpfs[0].to_path()
