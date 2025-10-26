import dataclasses

import pulumi_tls as tls
from homelab_extract.service.mtls import MTlsInfoSourceModel
from pulumi import Output


@dataclasses.dataclass
class SecretMTlsResource:
    ca_cert: tls.SelfSignedCert
    server_key: tls.PrivateKey
    server_cert: tls.LocallySignedCert
    client_key: tls.PrivateKey
    client_cert: tls.LocallySignedCert

    def get_info(self, info: MTlsInfoSourceModel) -> Output[str]:
        match info:
            case MTlsInfoSourceModel.CA_CERT:
                return self.ca_cert.cert_pem
            case MTlsInfoSourceModel.SERVER_KEY:
                return self.server_key.private_key_pem
            case MTlsInfoSourceModel.SERVER_CERT:
                return self.server_cert.cert_pem
            case MTlsInfoSourceModel.CLIENT_KEY:
                return self.client_key.private_key_pem
            case MTlsInfoSourceModel.CLIENT_CERT:
                return self.client_cert.cert_pem

    def to_dict(self) -> dict[str, Output[str]]:
        return {info: self.get_info(info) for info in MTlsInfoSourceModel}
