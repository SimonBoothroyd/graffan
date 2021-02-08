"""Utilities for mocking ForceBalance input and output files."""
import json
import os
from collections import defaultdict
from typing import List

import numpy
from forcebalance.nifty import lp_dump
from openforcefield.topology import Molecule
from openforcefield.typing.engines.smirnoff import ForceField

from graffan.library.models.smirnoff import SMIRNOFFParameter
from graffan.library.models.targets import (
    FittingTarget,
    OptGeoTarget,
    SingleMoleculeTarget,
    TorsionTarget,
)
from graffan.utilities.utilities import temporary_cd


def mock_force_field(parameters: List[SMIRNOFFParameter]):
    """Mock a ForceBalance forcefield directory."""

    # Create the force field directory.
    force_field = ForceField("openff-1.2.0.offxml")

    parameters_to_fit = defaultdict(lambda: defaultdict(list))

    for parameter in parameters:
        parameters_to_fit[parameter.handler][parameter.smirks].append(
            parameter.attribute
        )

    for handler_name in parameters_to_fit:

        handler = force_field.get_parameter_handler(handler_name)

        for smirks in parameters_to_fit[handler_name]:
            openff_parameter = handler.parameters[smirks]
            attributes_string = ", ".join(parameters_to_fit[handler_name][smirks])

            openff_parameter.add_cosmetic_attribute("parameterize", attributes_string)

    os.makedirs("forcefield", exist_ok=True)
    force_field.to_file(os.path.join("forcefield", "forcefield.offxml"))


def mock_input(targets: List[FittingTarget]):

    options_lines = [
        "$options",
        "ffdir forcefield",
        "penalty_type L2",
        "jobtype optimize",
        "forcefield forcefield.offxml",
        "maxstep 50",
        "$end",
        "",
    ]

    for target in targets:

        options_lines.append("$target")
        options_lines.append(f"name {target.name}")
        options_lines.append(f"type {target.type}")

        for key, value in target.options.items():

            if isinstance(value, bool):
                options_lines.append(key)
            else:
                options_lines.append(f"{key} {value}")

        options_lines.append("$end")

    with open("optimize.in", "w") as file:
        file.write("\n".join(options_lines))


def mock_targets(targets: List[FittingTarget]):

    for target in targets:

        os.makedirs(os.path.join("targets", target.name), exist_ok=True)

        if isinstance(target, SingleMoleculeTarget):

            Molecule.from_smiles(target.molecule).to_file(
                os.path.join("targets", target.name, "input.sdf"), "SDF"
            )

        else:

            for i, smiles in enumerate(target.molecules):
                Molecule.from_smiles(smiles).to_file(
                    os.path.join("targets", target.name, f"MOL_{i}.sdf"), "SDF"
                )

        if isinstance(target, TorsionTarget):

            with open(
                os.path.join("targets", target.name, "metadata.json"), "w"
            ) as file:
                json.dump({"dihedrals": [[0, 1, 2, 3]]}, file)

        if isinstance(target, OptGeoTarget):

            with open(
                os.path.join("targets", target.name, "optgeo_options.txt"), "w"
            ) as file:

                lines = [
                    "$global",
                    "bond_denom 0.05",
                    "angle_denom 8",
                    "dihedral_denom 0",
                    "improper_denom 20",
                    "$end",
                    "",
                ]

                for i, smiles in enumerate(target.molecules):

                    lines.extend(
                        [
                            "$system",
                            f"name MOL_{i}",
                            f"geometry MOL_{i}.xyz",
                            f"topology MOL_{i}.pdb",
                            f"mol2 MOL_{i}.sdf",
                            "$end",
                        ]
                    )

                file.write("\n".join(lines))


def mock_target_outputs(
    targets: List[FittingTarget], parameters: List[SMIRNOFFParameter]
):

    for target in targets:

        target_directory = os.path.join("optimize.tmp", target.name, "iter_0000")
        os.makedirs(target_directory, exist_ok=True)

        lp_dump(
            {"G": numpy.random.randn(len(parameters))},
            os.path.join(target_directory, "objective.p"),
        )


def mock(
    directory: str, targets: List[FittingTarget], parameters: List[SMIRNOFFParameter]
):

    with temporary_cd(directory):

        # Mock a force field to refit
        mock_force_field(parameters)

        # Mock an input file.
        mock_input(targets)

        # Mock the target inputs
        mock_targets(targets)

        # Mock the target outputs
        mock_target_outputs(targets, parameters)
