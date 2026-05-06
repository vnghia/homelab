import typing

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ...extract import ExtractorArgs


class DockerContainerOverwriteModel(HomelabBaseModel):
    service: str | None = None
    model: str | None = None
    entrypoint: list[GlobalExtract] | None = None
    command: list[GlobalExtract] | None = None

    def build_entrypoint(
        self, extractor_args: ExtractorArgs
    ) -> list[Output[str]] | None:
        from ...extract.global_ import GlobalExtractor

        if self.entrypoint is not None:
            extractor_args = extractor_args.get_service_resource(
                self.service
            ).extractor_args
            return [
                GlobalExtractor(entrypoint).extract_str(extractor_args)
                for entrypoint in self.entrypoint
            ]
        return None

    def build_command(self, extractor_args: ExtractorArgs) -> list[Output[str]] | None:
        from ...extract.global_ import GlobalExtractor

        if self.command is not None:
            extractor_args = extractor_args.get_service_resource(
                self.service
            ).extractor_args
            return [
                GlobalExtractor(command).extract_str(extractor_args)
                for command in self.command
            ]
        return None
