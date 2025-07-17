import json
from typing_extensions import Annotated, Optional
from pathlib import Path
import typer

from .sensor import Module

cli = typer.Typer(add_completion=False, rich_markup_mode="rich", no_args_is_help=True)

input_file_argument = Annotated[
    Path,
    typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        show_default=False,
        help="Path to the input file.",
    ),
]


@cli.command("get", no_args_is_help=True)
def cli_get(file: input_file_argument) -> None:
    with open(file) as f:
        config = json.loads(f.read())
        module = Module(config)
        print(module.print(), end="", flush=True)


@cli.command("debug", no_args_is_help=True)
def cli_debug(file: input_file_argument) -> None:
    with open(file) as f:
        config = json.loads(f.read())
        module = Module(config)
        print(module.debug())


if __name__ == "__main__":
    cli()  # pragma: no cover
