import pytest
from click.testing import CliRunner


@pytest.yield_fixture(scope="module")
def runner() -> CliRunner:
    """Creates a new click CLI runner object."""
    click_runner = CliRunner()
    yield click_runner


@pytest.yield_fixture(scope="module")
def isolated_runner(runner) -> CliRunner:
    """Creates a new click CLI runner object and sets the temporarily moves
    the working directory to a temporary directory"""

    with runner.isolated_filesystem():
        yield runner
