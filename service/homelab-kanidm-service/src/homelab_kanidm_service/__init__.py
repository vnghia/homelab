from __future__ import annotations

import pulumi
import pulumi_tls as tls
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.file.config import (
    ConfigFileResource,
    JsonDefaultModel,
    TomlDumper,
)
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import Output, ResourceOptions

from .client import KanidmClient
from .config import KandimConfig
from .resource.password import KanidmPasswordResource
from .resource.state import KanidmStateResource


class KanidmServerConfigResource(
    ConfigFileResource[JsonDefaultModel], module="kanidm", name="ServerConfig"
):
    validator = JsonDefaultModel
    dumper = TomlDumper[JsonDefaultModel]

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        kanidm_service: KanidmService,
    ) -> None:
        config = kanidm_service.config
        path = GlobalExtractor(kanidm_service.config.path.config)
        self.path = path.extract_path(kanidm_service, None)

        super().__init__(
            resource_name,
            opts=opts,
            volume_path=path.extract_volume_path(kanidm_service, None),
            data={
                "version": "2",
                "bindaddress": Output.format("[::]:{}", kanidm_service.port),
                "db_path": GlobalExtractor(config.path.db).extract_path(
                    kanidm_service, None
                ),
                "tls_key": GlobalExtractor(config.path.tls_key).extract_path(
                    kanidm_service, None
                ),
                "tls_chain": GlobalExtractor(config.path.tls_chain).extract_path(
                    kanidm_service, None
                ),
                "domain": GlobalExtractor(config.domain).extract_str(
                    kanidm_service, None
                ),
                "origin": GlobalExtractor(config.origin).extract_str(
                    kanidm_service, None
                ),
            },
            docker_resource_args=kanidm_service.docker_resource_args,
        )


class KanidmService(ServiceWithConfigResourceBase[KandimConfig]):
    OPENID_GROUP = "openid"
    ADMIN_GROUP = "role_admin"
    USER_GROUP = "role_user"

    def __init__(
        self,
        model: ServiceWithConfigModel[KandimConfig],
        *,
        opts: ResourceOptions,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.port = GlobalExtractor(self.config.port).extract_str(self, None).apply(int)

        self.key = tls.PrivateKey(
            "key", opts=self.child_opts, algorithm="ECDSA", ecdsa_curve="P256"
        )
        self.chain = tls.SelfSignedCert(
            "chain",
            opts=self.child_opts,
            allowed_uses=["any_extended"],
            private_key_pem=self.key.private_key_pem,
            validity_period_hours=100 * 365 * 60,
        )

        self.key_file = FileResource(
            "key",
            opts=self.child_opts,
            volume_path=GlobalExtractor(self.config.path.tls_key).extract_volume_path(
                self, None
            ),
            content=self.key.private_key_pem,
            mode=0o440,
            docker_resources_args=self.docker_resource_args,
        )
        self.chain_file = FileResource(
            "chain",
            opts=self.child_opts,
            volume_path=GlobalExtractor(self.config.path.tls_chain).extract_volume_path(
                self, None
            ),
            content=self.chain.cert_pem,
            mode=0o440,
            docker_resources_args=self.docker_resource_args,
        )

        self.config_file = KanidmServerConfigResource(
            "server", opts=self.child_opts, kanidm_service=self
        )

        self.options[None].files = [self.key_file, self.chain_file, self.config_file]
        self.build_containers()

        self.admin = KanidmPasswordResource(
            opts=self.child_opts,
            container=self.container.id,
            account="admin",
            config_path=self.config_file.path,
        )
        self.idm_admin = KanidmPasswordResource(
            opts=self.child_opts,
            container=self.container.id,
            account="idm_admin",
            config_path=self.config_file.path,
        )
        pulumi.export("kanidm.admin", self.admin.password)
        pulumi.export("kanidm.idm_admin", self.idm_admin.password)

        self.url = Output.format(
            "https://{}:{}",
            GlobalExtractor(self.config.address).extract_str(self, None),
            GlobalExtractor(self.config.port).extract_str(self, None),
        )

        self.state = KanidmStateResource(
            opts=self.child_opts.merge(ResourceOptions(depends_on=[self.container])),
            kanidm_service=self,
        )

        self.client_data = Output.json_dumps({"url": self.url})

        self.login_account = Output.all(
            self.client_data, self.idm_admin.password
        ).apply(lambda x: KanidmClient.model_validate_json(x[0]).login(password=x[1]))

        self.exports |= {
            system: Output.all(
                self.client_data, system, self.state.hash, self.login_account
            ).apply(
                lambda x: KanidmClient.model_validate_json(x[0]).extract_oauth_secret(
                    x[1]
                )
            )
            for system in self.config.state.systems.oauth2.root
        }
        for system, secret in self.exports.items():
            pulumi.export("kanidm.{}.oauth".format(system), secret)

        self.register_outputs({})
