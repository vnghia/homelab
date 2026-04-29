import operator
import shutil
from functools import reduce
from pathlib import Path

import sqlite_backup
import typer
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

app = typer.Typer()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BALITE_")

    source_dir: Path
    destination_dir: Path

    groups: dict[str, set[str]]
    profiles: dict[str, set[Path]]

    def get_paths(self, key: str) -> list[tuple[str, Path]]:
        if key in self.groups:
            return reduce(
                operator.add,
                [self.get_paths(profile) for profile in self.groups[key]],
                [],
            )
        return [(key, path) for path in self.profiles[key]]


@app.command()
def backup(profiles: list[str]) -> None:
    settings = Settings()  # pyright: ignore reportCallIssue

    for profile in profiles:
        for volume, path in settings.get_paths(profile):
            source = (settings.source_dir / volume / path).resolve(True)
            destination = settings.destination_dir / volume / "balite" / path
            destination.parent.mkdir(parents=True, exist_ok=True)

            sqlite_backup.sqlite_backup(source, destination)
            logger.info("Backed up {} to {}".format(source, destination))


@app.command()
def restore(profiles: list[str]) -> None:
    settings = Settings()  # pyright: ignore reportCallIssue

    for profile in profiles:
        for volume, path in settings.get_paths(profile):
            source = settings.source_dir / volume / path
            source.parent.mkdir(parents=True, exist_ok=True)
            destination = (settings.destination_dir / volume / "balite" / path).resolve(
                True
            )

            shutil.copyfile(destination, source)
            logger.info("Restored {} to {}".format(destination, source))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
