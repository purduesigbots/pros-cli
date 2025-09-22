"""PROS CLI."""

import pathlib
import zipfile
import urllib.request
from urllib.parse import urlparse
import tempfile
import rich_click as click

from pros.cli.root import pros


@pros.group(
    short_help="Perform project management for PROS",
)
def conductor() -> None:
    """Command group for conductor."""

def is_url(string: str) -> bool:
    """Check if a string is a valid URL."""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
    
@conductor.command()
@click.argument(
    "template",
    type=str,
)
@click.option(
    "--project",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True, path_type=pathlib.Path
    ),
    default=pathlib.Path.cwd(),
)
def apply(template: str, project: pathlib.Path) -> None:
    """Install a PROS template."""
    if is_url(template):
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
            urllib.request.urlretrieve(template, temp_file.name)
            template_path = temp_file.name
    else:
        template_path = template
    with zipfile.ZipFile(template_path) as f:
        f.extractall(project)

    if is_url(template):
        pathlib.Path(template_path).unlink()
    click.echo(f"Applied template {template} to {project}")