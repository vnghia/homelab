import os
from pathlib import Path

import sqlite_backup
from loguru import logger
from tap import Tap


class ProfileParser(Tap):
    profiles: list[str]

    def configure(self) -> None:
        self.add_argument("profiles", nargs="*")


def main() -> None:
    args = ProfileParser().parse_args()
    source_dir = Path(os.environ["HOMELAB_SOURCE_DIR"])
    destination_dir = Path(os.environ["HOMELAB_DESTINATION_DIR"])

    for profile in args.profiles:
        paths = os.environ[
            "HOMELAB_{}".format(profile.upper().replace("-", "_"))
        ].split(",")
        for path in paths:
            source = source_dir / profile / path
            if source.exists():
                destination = destination_dir / profile / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                sqlite_backup.sqlite_backup(source, destination)
                logger.info("Backed up {} to {}".format(source, destination))
            else:
                logger.error("Source database {} not found".format(source))
