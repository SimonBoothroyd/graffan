import os

from graffan.library.analysis.targets import analyze_targets, extract_target_gradients


def test_extract_target_gradients(dummy_fitting_target, force_balance_directory):

    gradient = extract_target_gradients(
        os.path.join(
            force_balance_directory,
            "optimize.tmp",
            dummy_fitting_target.name,
            "iter_0000",
        ),
        dummy_fitting_target,
    )

    assert gradient.shape == (1,)


def test_analyze_targets(force_balance_directory):

    analysed_targets = analyze_targets(force_balance_directory, 0)
    assert len(analysed_targets) == 1

    analysed_target = analysed_targets[0]

    assert analysed_target.type == "torsion"

    assert "b83" in analysed_target.gradients
    assert "k" in analysed_target.gradients["b83"]
    assert "[H][C:2]([H])([H:1])[O:3][H:4]" in analysed_target.gradients["b83"]["k"]
