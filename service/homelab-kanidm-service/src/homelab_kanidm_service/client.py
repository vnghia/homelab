import re
from contextlib import contextmanager
from pathlib import PosixPath
from typing import ClassVar, Iterator

from homelab_docker.client import DockerClient
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pydantic import PositiveInt


class KanidmClient(HomelabBaseModel):
    ACCOUNT: ClassVar[str] = "idm_admin"

    BINARY_PATH: ClassVar[AbsolutePath] = AbsolutePath(PosixPath("/sbin/kanidm"))
    CACHE_PATH: ClassVar[AbsolutePath] = AbsolutePath(PosixPath("/root/.cache"))

    ID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r".*uuid: ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*"
    )

    host: str
    port: PositiveInt
    network: str
    image: str
    cache: str

    @contextmanager
    def run(
        self, command: list[str] | str, environment: dict[str, str] | None = None
    ) -> Iterator[str]:
        container = DockerClient().containers.run(
            image=self.image,
            command=command,
            entrypoint=[],
            detach=True,
            environment={
                "KANIDM_URL": "https://{}:{}".format(self.host, self.port),
                "KANIDM_NAME": self.ACCOUNT,
                "KANIDM_SKIP_HOSTNAME_VERIFICATION": "true",
                "KANIDM_ACCEPT_INVALID_CERTS": "true",
            }
            | (environment or {}),
            network=self.network,
            remove=False,
            volumes={self.cache: {"bind": self.CACHE_PATH.as_posix(), "mode": "rw"}},
        )
        try:
            response = container.wait()
            if response["StatusCode"] != 0:
                raise RuntimeError(
                    response,
                    container.logs(stdout=True, stderr=True, stream=False).decode(),
                )
            yield container.logs(stdout=True, stderr=False, stream=False).decode()
        finally:
            container.remove(force=True)

    def login(self, password: str) -> str:
        with self.run(
            "/bin/sh -c 'echo \"${{KANIDM_PASSWORD}}\\n\" | {} login'".format(
                self.BINARY_PATH.as_posix()
            ),
            environment={"KANIDM_PASSWORD": password},
        ) as result:
            if "Login Success for {}@".format(self.ACCOUNT) not in result:
                raise RuntimeError(
                    "Could not login to kanidm with log: {}".format(result)
                )
            return self.ACCOUNT

    def extract_oauth_secret(self, system: str) -> str:
        with self.run(
            [
                self.BINARY_PATH.as_posix(),
                "system",
                "oauth2",
                "show-basic-secret",
                system,
            ]
        ) as result:
            return result.replace("\n", "")
