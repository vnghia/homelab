import os
import shutil
from pathlib import Path
from typing import Annotated

import sqlite_backup
import typer
from loguru import logger

app = typer.Typer()


@app.command()
def backup(
    source_dir: Annotated[Path, typer.Option(envvar="HOMELAB_SOURCE_DIR")],
    destination_dir: Annotated[Path, typer.Option(envvar="HOMELAB_DESTINATION_DIR")],
    profiles: list[str],
) -> None:
    for profile in profiles:
        paths = os.environ[
            "HOMELAB_{}".format(profile.upper().replace("-", "_"))
        ].split(",")
        for path in paths:
            source = (source_dir / profile / path).resolve(True)
            destination = destination_dir / profile / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            sqlite_backup.sqlite_backup(source, destination)
            logger.info("Backed up {} to {}".format(source, destination))


@app.command()
def restore(
    source_dir: Annotated[Path, typer.Option(envvar="HOMELAB_SOURCE_DIR")],
    destination_dir: Annotated[Path, typer.Option(envvar="HOMELAB_DESTINATION_DIR")],
    profiles: list[str],
) -> None:
    for profile in profiles:
        paths = os.environ[
            "HOMELAB_{}".format(profile.upper().replace("-", "_"))
        ].split(",")
        for path in paths:
            source = source_dir / profile / path
            source.parent.mkdir(parents=True, exist_ok=True)
            destination = (destination_dir / profile / path).resolve(True)
            shutil.copyfile(destination, source)
            logger.info("Restored {} to {}".format(destination, source))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
