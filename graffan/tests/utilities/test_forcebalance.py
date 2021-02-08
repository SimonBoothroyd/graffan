from graffan.library.models.targets import TorsionTarget
from graffan.utilities.forcebalance import (
    extract_target_parameters,
    extract_targets,
    load_fb_force_field,
)


def test_mvals_to_pvals_jacobian():
    # Not 100% clear what a good test for this will be.
    pass


def test_load_fb_force_field(force_balance_directory):

    fb_force_field = load_fb_force_field(force_balance_directory)
    assert fb_force_field is not None

    assert len(fb_force_field.plist) == 1


def test_extract_targets(force_balance_directory):

    targets = extract_targets(force_balance_directory)

    assert len(targets) == 1
    assert isinstance(targets[0], TorsionTarget)


def test_extract_target_parameters(force_balance_directory):

    fb_force_field = load_fb_force_field(force_balance_directory)
    parameters = extract_target_parameters(fb_force_field)

    assert len(parameters) == 1
    assert parameters[0].handler == "Bonds"
