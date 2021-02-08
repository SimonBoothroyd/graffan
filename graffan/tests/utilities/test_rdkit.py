import pytest

from graffan.utilities.rdkit import smiles_to_grid_svg, smiles_to_svg


@pytest.mark.parametrize("highlight_smirks", [None, "CO"])
def test_smiles_to_svg(highlight_smirks):
    # It's difficult to test this as it's a graphical function. For now make sure
    # it doesn't error and something is produced.
    output = smiles_to_svg("CO", highlight_smirks)
    assert len(output) > 0


def test_smiles_to_grid_svg():
    # It's difficult to test this as it's a graphical function. For now make sure
    # it doesn't error and something is produced.
    output = smiles_to_grid_svg(["CO", "CCO"])
    assert len(output) > 0
