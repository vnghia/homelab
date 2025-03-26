import pulumi_tls as tls
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import KandimConfig


class KanidmService(ServiceWithConfigResourceBase[KandimConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[KandimConfig],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

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
            volume_path=self.config.tls_key.extract_volume_path(self, None),
            content=self.key.private_key_pem,
            mode=0o440,
            volume_resource=self.docker_resource_args.volume,
        )
        self.chain_file = FileResource(
            "chain",
            opts=self.child_opts,
            volume_path=self.config.tls_chain.extract_volume_path(self, None),
            content=self.chain.cert_pem,
            mode=0o440,
            volume_resource=self.docker_resource_args.volume,
        )

        self.options[None].files = [self.key_file, self.chain_file]
        self.build_containers()

        self.register_outputs({})
