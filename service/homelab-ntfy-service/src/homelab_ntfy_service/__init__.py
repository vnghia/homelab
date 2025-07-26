from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
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
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)
        self.build()

        self.admin = NtfyUserResource(
            self.ADMIN_ROLE,
            opts=ResourceOptions.merge(
                self.child_opts, ResourceOptions(depends_on=[self.container])
            ),
            container=self.container.name,
            username=self.keepass[None].username,
            password=self.keepass[None].password,
            role=self.ADMIN_ROLE,
            acl=NtfyUserAclConfig(),
        )
        self.user = NtfyUserResource(
            self.USER_ROLE,
            opts=ResourceOptions.merge(
                self.child_opts, ResourceOptions(depends_on=[self.container])
            ),
            container=self.container.name,
            username=self.secret["{}-username".format(self.USER_ROLE)],
            password=self.secret["{}-password".format(self.USER_ROLE)],
            role=self.USER_ROLE,
            acl=NtfyUserAclConfig({"*": NtfyUserAclPermission.WRITE_ONLY}),
        )

        self.register_outputs({})
