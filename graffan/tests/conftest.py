import pytest

from graffan.library.models.smirnoff import SMIRNOFFParameter
from graffan.library.models.targets import TorsionTarget
from graffan.tests.mock.mock import mock


@pytest.fixture()
def dummy_fitting_target() -> TorsionTarget:

    return TorsionTarget(
        name="dummy-target",
        molecule="[H][C:1]([O:2][H])([H:3])[H:4]",
        options={"mol2": "input.sdf"},
    )


@pytest.fixture()
def force_balance_directory(tmpdir, dummy_fitting_target):

    mock(
        str(tmpdir),
        [dummy_fitting_target],
        [
            SMIRNOFFParameter(
                handler="Bonds", smirks="[#6X4:1]-[#1:2]", attribute="k", id="b83"
            )
        ],
    )

    return str(tmpdir)
