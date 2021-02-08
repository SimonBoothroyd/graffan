import errno
import logging
import os
from collections import defaultdict
from typing import List

import numpy

from graffan.library.models.analysis import AnalysedTarget
from graffan.library.models.targets import FittingTarget, MultiMoleculeTarget
from graffan.utilities.forcebalance import (
    extract_target_parameters,
    extract_targets,
    load_fb_force_field,
    mvals_to_pvals_jacobian,
)

logger = logging.getLogger(__name__)


def extract_target_gradients(
    target_directory: str, target: FittingTarget
) -> numpy.ndarray:
    """Attempts to extract the gradient of a particular fitting target.

    Parameters
    ----------
    target_directory
        A file path to the output directory of the target of interest.
    target
        The options associated with the target.

    Returns
    -------
        The extracted gradients.
    """
    from forcebalance.nifty import lp_load

    output_path = os.path.join(target_directory, "objective.p")

    if not (os.path.isfile(output_path)):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), output_path)

    if target.type in ["TorsionProfile_SMIRNOFF", "VIBRATION_SMIRNOFF"]:
        pass

    else:
        raise NotImplementedError()

    output_dictionary = lp_load(output_path)
    return output_dictionary["G"]


def analyze_targets(root_directory: str, iteration: int) -> List[AnalysedTarget]:
    """Analyses the outputs of a set of fitting targets found within a ForceBalance
    fitting directory at a particular iteration.

    Parameters
    ----------
    root_directory
        The directory containing the fitting inputs and outputs.
    iteration
        The iteration to analyze.

    Returns
    -------
        A set of analyzed results for each type of fitting target.
    """

    iteration_string = "iter_" + str(iteration).zfill(4)

    # Load in the definitions of the refit parameters.
    fb_force_field = load_fb_force_field(root_directory)

    parameters = extract_target_parameters(fb_force_field)
    jacobian = mvals_to_pvals_jacobian(fb_force_field)

    # Determine which targets are present.
    targets: List[FittingTarget] = extract_targets(root_directory)

    targets_by_type = defaultdict(list)

    for target in targets:
        targets_by_type[target.type].append(target)

    # Extract the gradients from each target.
    analyzed_targets: List[AnalysedTarget] = []

    target_types = {
        "TorsionProfile_SMIRNOFF": "torsion",
        "VIBRATION_SMIRNOFF": "vibration",
        "OptGeoTarget_SMIRNOFF": "optgeo",
    }

    for target_type in targets_by_type:

        target_gradients = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

        if target_type not in ["TorsionProfile_SMIRNOFF", "VIBRATION_SMIRNOFF"]:

            logger.warning(
                f"{target_type} targets are not yet supported and will be skipped."
            )
            continue

        for target in targets_by_type[target_type]:

            if isinstance(target, MultiMoleculeTarget):

                if len(target.molecules) != 1:
                    raise NotImplementedError()

                smiles = target.molecules[0]

            else:
                smiles = target.molecule

            # Extract the raw mathematical gradients.
            target_directory = os.path.join(
                root_directory, "optimize.tmp", target.name, iteration_string
            )
            target_mval_gradients = extract_target_gradients(target_directory, target)

            # Map the FB mathematical gradients to physical gradients.
            target_pval_gradients = jacobian @ target_mval_gradients

            # Store the gradients.
            for parameter, gradient in zip(parameters, target_pval_gradients):

                if not numpy.isclose(gradient, 0.0):
                    target_gradients[parameter.id][parameter.attribute][
                        smiles
                    ] += gradient

        analyzed_targets.append(
            AnalysedTarget(type=target_types[target_type], gradients=target_gradients)
        )

    return analyzed_targets
