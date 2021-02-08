from graffan.cli.visualise import visualise_cli
from graffan.dashboard.app import DashboardApp
from graffan.library.models.analysis import AnalysedIteration


def test_visualize(isolated_runner, monkeypatch):

    monkeypatch.setattr(DashboardApp, "launch", lambda *args, **kwargs: None)

    with open("iteration_0000.json", "w") as file:

        file.write(
            AnalysedIteration(iteration=0, refit_parameters=[], targets=[]).json()
        )

    result = isolated_runner.invoke(visualise_cli, ["iteration_0000.json"])

    if result.exit_code != 0:
        raise result.exception
