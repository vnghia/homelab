import typing

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ...extract import ExtractorArgs


class DockerProcessCreationModel(HomelabBaseModel):
    model: str | None = None
    entrypoint: list[GlobalExtract] | None = None
    command: list[GlobalExtract] | None = None

    def build_entrypoint(
        self, extractor_args: ExtractorArgs
    ) -> list[Output[str]] | None:
        from ...extract.global_ import GlobalExtractor

        if self.entrypoint is not None:
            return [
                GlobalExtractor(entrypoint).extract_str(extractor_args)
                for entrypoint in self.entrypoint
            ]
        return None

    def build_command(self, extractor_args: ExtractorArgs) -> list[Output[str]] | None:
        from ...extract.global_ import GlobalExtractor

        if self.command is not None:
            return [
                GlobalExtractor(command).extract_str(extractor_args)
                for command in self.command
            ]
        return None


class DockerContainerCreationModel(DockerProcessCreationModel):
    pass
