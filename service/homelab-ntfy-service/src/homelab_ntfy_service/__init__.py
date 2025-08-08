from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from pulumi import ResourceOptions

from .resource.user import NtfyUserAclConfig, NtfyUserAclPermission, NtfyUserResource


class NtfyService(ExtraService[ExtraConfig]):
    REGISTER_OUTPUT = False

    ADMIN_ROLE = "admin"
    USER_ROLE = "user"

    def __init__(
        self,
        model: ServiceWithConfigModel[ExtraConfig],
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)
        self.build()

        self.admin = NtfyUserResource(
            self.ADMIN_ROLE,
            opts=ResourceOptions.merge(
                self.child_opts, ResourceOptions(depends_on=[self.container.resource])
            ),
            container=self.container.name,
            username=self.keepass[None].username,
            password=self.keepass[None].password,
            role=self.ADMIN_ROLE,
            acl=NtfyUserAclConfig(),
            docker_resource_args=self.docker_resource_args,
        )
        self.user = NtfyUserResource(
            self.USER_ROLE,
            opts=ResourceOptions.merge(
                self.child_opts, ResourceOptions(depends_on=[self.container.resource])
            ),
            container=self.container.name,
            username=self.secret["{}-username".format(self.USER_ROLE)],
            password=self.secret["{}-password".format(self.USER_ROLE)],
            role=self.USER_ROLE,
            acl=NtfyUserAclConfig({"*": NtfyUserAclPermission.WRITE_ONLY}),
            docker_resource_args=self.docker_resource_args,
        )

        self.register_outputs({})
