from __future__ import annotations

import pulumi
from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import Output, ResourceOptions

from .client import KanidmClient
from .config import KandimConfig
from .resource.password import KanidmPasswordResource
from .resource.state import KanidmStateResource


class KanidmService(ServiceWithConfigResourceBase[KandimConfig]):
    OPENID_GROUP = "openid"
    ADMIN_GROUP = "role_admin"
    USER_GROUP = "role_user"

    def __init__(
        self,
        model: ServiceWithConfigModel[KandimConfig],
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        self.build_containers()

        self.config_path = GlobalExtractor(self.config.path).extract_path(
            self.extractor_args
        )
        self.admin = KanidmPasswordResource(
            opts=self.child_opts,
            container=self.container.id,
            account="admin",
            config_path=self.config_path,
            extractor_args=self.extractor_args,
        )
        self.idm_admin = KanidmPasswordResource(
            opts=self.child_opts,
            container=self.container.id,
            account="idm_admin",
            config_path=self.config_path,
            extractor_args=self.extractor_args,
        )
        pulumi.export("kanidm.admin", self.admin.password)
        pulumi.export("kanidm.idm_admin", self.idm_admin.password)

        self.url = Output.format(
            "https://{}:{}",
            GlobalExtractor(self.config.address).extract_str(self.extractor_args),
            GlobalExtractor(self.config.port)
            .extract_str(self.extractor_args)
            .apply(int),
        )

        self.state = KanidmStateResource(
            opts=self.child_opts.merge(
                ResourceOptions(depends_on=[self.container.resource])
            ),
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
            for system, model in self.config.state.systems.oauth2.root.items()
            if not model.public
        }
        for system, secret in self.exports.items():
            pulumi.export("kanidm.{}.oauth".format(system), secret)

        self.register_outputs({})
