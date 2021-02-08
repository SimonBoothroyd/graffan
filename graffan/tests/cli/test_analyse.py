import os

from graffan.cli.analyse import analyse_cli
from graffan.utilities.utilities import temporary_cd


def test_analyze(force_balance_directory, runner):

    with temporary_cd(force_balance_directory):

        result = runner.invoke(analyse_cli)

        if result.exit_code != 0:
            raise result.exception

        assert os.path.isfile("iteration_0000.json")
