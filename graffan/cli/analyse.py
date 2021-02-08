import click

from graffan.library.analysis.targets import analyze_targets
from graffan.library.models.analysis import AnalysedIteration
from graffan.utilities.forcebalance import (
    extract_target_parameters,
    load_fb_force_field,
)


@click.command("analyse", help="Analyzes the output of a ForceBalance iteration.")
@click.option(
    "--iteration",
    default=0,
    type=int,
    help="The iteration to analyze.",
    show_default=True,
)
def analyse_cli(iteration):

    # Load in the definitions of the refit parameters.
    fb_force_field = load_fb_force_field("")
    parameters = extract_target_parameters(fb_force_field)

    # Perform the analysis
    output = AnalysedIteration(
        iteration=iteration,
        targets=analyze_targets("", iteration),
        refit_parameters=parameters,
    )

    with open(f"iteration_{str(iteration).zfill(4)}.json", "w") as file:

        file.write(output.json(sort_keys=True, indent=2, separators=(",", ": ")))
