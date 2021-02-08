import os

import pytest

from graffan.library.models.targets import OptGeoTarget, TorsionTarget, VibrationTarget
from graffan.tests.mock.mock import mock_targets
from graffan.utilities.utilities import temporary_cd


@pytest.mark.parametrize(
    "expected",
    [
        TorsionTarget(
            name="dummy-target-1",
            molecule="[H][C:2]([H])([H:1])[O:3][H:4]",
            options={"mol2": "input.sdf"},
        ),
        VibrationTarget(
            name="dummy-target-1",
            molecule="CO",
            options={"mol2": "input.sdf"},
        ),
        OptGeoTarget(
            name="dummy-target-1",
            molecules=["CO", "CCO"],
            options={"mol2": "input.sdf"},
        ),
    ],
)
def test_target_from_directory(expected, tmpdir):

    with temporary_cd(str(tmpdir)):

        mock_targets([expected])

        target = expected.__class__.from_directory(
            os.path.join("targets", expected.name), expected.name, expected.options
        )

    assert expected.name == target.name
    assert expected.options == target.options

    if isinstance(expected, VibrationTarget):
        assert expected.molecule == target.molecule

    if isinstance(expected, OptGeoTarget):
        assert expected.molecules == target.molecules
