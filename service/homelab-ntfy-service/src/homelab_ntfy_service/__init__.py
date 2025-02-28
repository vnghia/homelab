from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_traefik_service import TraefikService
from pulumi import ResourceOptions

from .config import NtfyConfig
from .resource.user import NtfyUserAclConfig, NtfyUserAclPermission, NtfyUserResource


class NtfyService(ServiceWithConfigResourceBase[NtfyConfig]):
    ADMIN_ROLE = "admin"
    USER_ROLE = "user"

    def __init__(
        self,
        model: ServiceWithConfigModel[NtfyConfig],
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.build_containers(options={})

        self.admin = NtfyUserResource(
            self.ADMIN_ROLE,
            opts=self.child_opts,
            container=self.container.name,
            username=self.secret["{}-username".format(self.ADMIN_ROLE)].result,
            password=self.secret["{}-password".format(self.ADMIN_ROLE)].result,
            role=self.ADMIN_ROLE,
            acl=NtfyUserAclConfig(),
        )
        self.user = NtfyUserResource(
            self.USER_ROLE,
            opts=self.child_opts,
            container=self.container.name,
            username=self.secret["{}-username".format(self.USER_ROLE)].result,
            password=self.secret["{}-password".format(self.USER_ROLE)].result,
            role=self.USER_ROLE,
            acl=NtfyUserAclConfig({"*": NtfyUserAclPermission.WRITE_ONLY}),
        )

        self.traefik = self.config.traefik.build_resources(
            opts=self.child_opts,
            main_service=self,
            traefik_service=traefik_service,
        )

        self.register_outputs({})
