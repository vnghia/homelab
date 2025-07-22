import os
import shutil
import subprocess
from typing import ClassVar, cast

import pexpect
from homelab_pydantic import HomelabBaseModel


class KanidmClient(HomelabBaseModel):
    BINARY: ClassVar[str] = "kanidm"
    ACCOUNT: ClassVar[str] = "idm_admin"

    url: str

    @property
    def binary(self) -> str:
        binary = shutil.which(self.BINARY)
        if not binary:
            raise ValueError("{} is not installed".format(self.BINARY))
        return binary

    @property
    def env(self) -> dict[str, str]:
        return {
            "KANIDM_URL": self.url,
            "KANIDM_NAME": self.ACCOUNT,
            "KANIDM_SKIP_HOSTNAME_VERIFICATION": "true",
            "KANIDM_ACCEPT_INVALID_CERTS": "true",
        }

    def login(self, password: str) -> str:
        result = pexpect.run(
            "{} login".format(self.binary),
            events={"Enter password: ": password + "\n"},
            env=cast(os._Environ[str], self.env),
            encoding="utf-8",
        )
        if "Login Success for {}@".format(self.ACCOUNT) not in result:
            raise RuntimeError("Could not login to kanidm with log: {}".format(result))
        return self.ACCOUNT

    def extract_oauth_secret(self, system: str) -> str:
        return (
            subprocess.check_output(
                [
                    self.binary,
                    "system",
                    "oauth2",
                    "show-basic-secret",
                    system,
                ],
                env=self.env,
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .replace("\n", "")
        )
