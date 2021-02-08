import os
from typing import TYPE_CHECKING, Any, Dict, List

import numpy

from graffan.library.models.smirnoff import SMIRNOFFParameter
from graffan.library.models.targets import TYPE_TO_FITTING_TARGET, FittingTarget
from graffan.utilities.utilities import temporary_cd

TargetOptions = Dict[str, Any]

if TYPE_CHECKING:
    from forcebalance.forcefield import FF


def mvals_to_pvals_jacobian(
    force_field: "FF", perturbation_amount=1.0e-4
) -> numpy.ndarray:
    """Builds a matrix which maps the gradient w.r.t. mathematical parameters to
    a gradient w.r.t physical parameters.

    Parameters
    ----------
    force_field
        The force balance force field object containing the physical parameters.
    perturbation_amount: float
        The amount to perturb the physical parameters by when calculating the finite
        difference gradients.

    Returns
    -------
        The constructed mapping.
    """

    from forcebalance.nifty import col, flat, invert_svd

    jacobian_list = []

    inverse_tm_i = (invert_svd(force_field.tmI),)

    def create_mvals(pvals):
        return flat(numpy.dot(inverse_tm_i, col(pvals - force_field.pvals0)))

    for index in range(len(force_field.pvals0)):

        reverse_pvals = force_field.pvals0.copy()
        reverse_pvals[index] -= perturbation_amount
        reverse_mvals = numpy.array(create_mvals(reverse_pvals))

        forward_pvals = force_field.pvals0.copy()
        forward_pvals[index] += perturbation_amount
        forward_mvals = numpy.array(create_mvals(forward_pvals))

        gradients = (forward_mvals - reverse_mvals) / (2.0 * perturbation_amount)
        jacobian_list.append(gradients)

    jacobian = numpy.array(jacobian_list)
    return jacobian


def load_fb_force_field(root_directory: str) -> "FF":
    """Attempts to load the force field being refit from a force balance optimization
    directory.

    Parameters
    ----------
    root_directory
        The directory containing the force balance input files.

    Returns
    -------
        The loaded force balance force field object.
    """

    from forcebalance.forcefield import FF
    from forcebalance.parser import parse_inputs

    with temporary_cd(root_directory):
        fb_options, _ = parse_inputs("optimize.in")
        fb_force_field = FF(fb_options)

    return fb_force_field


def extract_targets(
    root_directory: str, input_file_name: str = "optimize.in"
) -> List[FittingTarget]:
    """Attempts to extract a list of targets from a set of force balance input files.

    Parameters
    ----------
    root_directory
        The path to the directory containing the force balance input files.
    input_file_name
        The file name of the input file in the input directory.

    Returns
    -------
        The extracted targets.
    """

    file_path = os.path.join(root_directory, input_file_name)

    with open(file_path) as file:
        lines = file.read().split("\n")

    # Go section by section finding the targets.
    i = -1

    targets = []

    while i + 1 < len(lines):

        i += 1

        if not lines[i].startswith("$target"):
            continue

        start_line = i

        while not lines[i].startswith("$end") and i < len(lines):
            i += 1

        if i == len(lines) or not lines[i].startswith("$end"):

            raise RuntimeError(
                f"The matching $end tag could not be found for the target defined on "
                f"line {start_line} of {file_path}"
            )

        target_options = {}

        for target_line in lines[start_line + 1 : i]:

            target_line_split = target_line.strip().split(" ")

            if len(target_line_split) == 0:
                continue

            target_options[target_line_split[0]] = (
                True if len(target_line_split) == 0 else " ".join(target_line_split[1:])
            )

        target_type = target_options.pop("type")
        target_name = target_options.pop("name")

        target_class = TYPE_TO_FITTING_TARGET[target_type]

        targets.append(
            target_class.from_directory(
                os.path.join(root_directory, "targets", target_name),
                target_name,
                target_options,
            )
        )

    return targets


def extract_target_parameters(force_field: "FF") -> List[SMIRNOFFParameter]:
    """Attempts to extract the list of parameters being refit from a force balance
    force field object.

    Parameters
    ----------
    force_field
        The force balance force field object.

    Returns
    -------
        The list of parameters being refit.
    """

    from openforcefield.typing.engines.smirnoff import ForceField

    openff_force_field: ForceField = force_field.openff_forcefield

    parameters = []

    for fb_parameter_id in force_field.plist:

        handler, _, attribute, smirks = fb_parameter_id.split("/")

        # Find the parameter ids
        openff_parameter = openff_force_field.get_parameter_handler(handler).parameters[
            smirks
        ]

        parameters.append(
            SMIRNOFFParameter(
                handler=handler,
                smirks=smirks,
                attribute=attribute,
                id=openff_parameter.id,
            )
        )

    return parameters
