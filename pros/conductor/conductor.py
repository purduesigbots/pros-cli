"""PROS CLI."""

import pathlib
import zipfile

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
