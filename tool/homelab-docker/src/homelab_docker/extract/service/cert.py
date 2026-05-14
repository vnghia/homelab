import typing

from homelab_extract.service.cert import ServiceExtractCertSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ServiceCertSourceExtractor(ExtractorBase[ServiceExtractCertSource]):
    @typing.override
    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        return extractor_args.service.secret.get_cert(self.root.cert).cert_pem
