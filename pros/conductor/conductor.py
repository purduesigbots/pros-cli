"""PROS CLI."""

import pathlib
import zipfile
import requests
import os

import rich_click as click

from pros.cli.root import pros


@pros.group(
    short_help="Perform project management for PROS",
)
def conductor() -> None:
    """Command group for conductor."""


@conductor.command()
@click.argument(
    "template",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, path_type=pathlib.Path
    ),
)
@click.option(
    "--project",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True, path_type=pathlib.Path
    ),
    default=pathlib.Path.cwd(),
)
def apply(template: pathlib.Path, project: pathlib.Path) -> None:
    """Install a PROS template."""
    with zipfile.ZipFile(template) as f:
        f.extractall(project)
    
@conductor.command()
@click.option(
    "--project",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True, path_type=pathlib.Path
    ),
    default=pathlib.Path.cwd(),
)
def new_project(project: pathlib.Path) -> None:
    """Create a new PROS project."""
    url = "https://github.com/purduesigbots/pros-docs/raw/refs/heads/master/v5/_static/releases/kernel@4.2.1.zip"
    response = requests.get(url)

    with open("kernel.zip", "wb") as file:
        file.write(response.content)

    with zipfile.ZipFile("kernel.zip") as f:
        f.extractall(project)

    os.remove("kernel.zip")
