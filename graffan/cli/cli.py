import click

from graffan.cli.analyse import analyse_cli
from graffan.cli.visualise import visualise_cli


@click.group()
def cli():
    """The root group for all CLI commands."""


cli.add_command(analyse_cli)
cli.add_command(visualise_cli)
