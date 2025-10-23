from __future__ import annotations

import typing
from typing import Any

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic.tls import TraefikDynamicTlsModel

if typing.TYPE_CHECKING:
    from ... import TraefikService


class TraefikDynamicTlsModelBuilder(HomelabRootModel[TraefikDynamicTlsModel]):
    def to_data(
        self, traefik_service: TraefikService, extractor_args: ExtractorArgs
    ) -> dict[str, Any]:
        root = self.root
        traefik_extractor_args = traefik_service.extractor_args

        certs = [
            {
                "certFile": GlobalExtractor(cert.cert).extract_path(
                    traefik_extractor_args
                ),
                "keyFile": GlobalExtractor(cert.key).extract_path(
                    traefik_extractor_args
                ),
            }
            for cert in root.certs
        ]

        options = (
            {
                "clientAuth": {
                    "caFiles": [
                        GlobalExtractor(ca).extract_path(traefik_extractor_args)
                        for ca in root.mtls.cas
                    ],
                    "clientAuthType": "RequireAndVerifyClientCert",
                }
            }
            if root.mtls
            else {}
        )

        return {
            "tls": ({"certificates": certs} if certs else {})
            | (
                {
                    "options": {
                        extractor_args.service.add_service_name(root.name): options
                    }
                }
                if options
                else {}
            )
        }
