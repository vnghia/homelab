from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.file.docker import DockerContainerRunModel
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pulumi import Output

from .base import HatchetTaskBaseModel


class HatchetTaskDockerExecInnerModel(HomelabBaseModel):
    container: str | None = None
    command: list[GlobalExtract]

    def build_command(self, extractor_args: ExtractorArgs) -> list[Output[str]]:
        return [
            GlobalExtractor(command).extract_str(extractor_args)
            for command in self.command
        ]


class HatchetTaskDockerExecModel(HomelabBaseModel):
    exec: HatchetTaskDockerExecInnerModel


class HatchetTaskDockerRunModel(HomelabBaseModel):
    run: DockerContainerRunModel = DockerContainerRunModel()


class HatchetTaskDockerModel(HatchetTaskBaseModel):
    docker: HatchetTaskDockerExecModel | HatchetTaskDockerRunModel = (
        HatchetTaskDockerRunModel()
    )
