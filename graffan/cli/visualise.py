import click

from graffan.dashboard.app import DashboardApp
from graffan.library.models.analysis import AnalysedIteration


@click.command(
    "visualise", help="Launch an interactive dashboard to visualise an analyzed output."
)
@click.option(
    "--debug",
    default=False,
    type=bool,
    is_flag=True,
    help="Launch the dashboard in debug mode.",
)
@click.argument("filename", type=click.Path(exists=True))
def visualise_cli(filename, debug):

    analyzed_output = AnalysedIteration.parse_file(filename)

    # Launch the dashboard.
    DashboardApp.launch(analyzed_output, debug=debug)
