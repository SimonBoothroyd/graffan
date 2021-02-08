import abc
import json
import os
from typing import Any, Dict, List, Literal, Type, TypeVar, Union

from pydantic import BaseModel, Field
from rdkit import Chem

T = TypeVar("T")


class _FittingTarget(BaseModel, abc.ABC):
    """The base class for models which store information about ForceBalance fitting
    targets."""

    name: str = Field(..., description="The name of the fitting target.")

    options: Dict[str, Any] = Field(
        ..., description="The set of options associated with the target."
    )

    @classmethod
    @abc.abstractmethod
    def from_directory(cls, directory: str, name: str, options: Dict[str, Any]):
        """Creates a target object based on the targets input files and specified
        options.

        Parameters
        ----------
        directory
            The path to the directory containing the targets input files.
        name
            The name of the target.
        options
            The options dictionary associated with the target, parsed from the main
            options input file.

        Returns
        -------
            The created target.
        """
        raise NotImplementedError()


class SingleMoleculeTarget(_FittingTarget, abc.ABC):
    """The base class for models which store information about ForceBalance fitting
    targets which operate on a single molecule."""

    molecule: str = Field(
        ...,
        description="A SMILES patterns describing the molecule included in the "
        "fitting target.",
    )

    @classmethod
    def from_directory(
        cls: Type[T], directory: str, name: str, options: Dict[str, Any]
    ) -> T:
        from openforcefield.topology import Molecule

        input_molecule_path = os.path.join(directory, options["mol2"])

        input_molecule = Molecule.from_file(
            input_molecule_path, allow_undefined_stereo=True
        )

        return cls(
            name=name,
            molecule=input_molecule.to_smiles(explicit_hydrogens=False),
            options=options,
        )


class MultiMoleculeTarget(_FittingTarget, abc.ABC):
    """The base class for models which store information about ForceBalance fitting
    targets which operate on multiple molecules."""

    molecules: List[str] = Field(
        ...,
        description="A list SMILES patterns describing the molecules included in the "
        "fitting target.",
    )


class TorsionTarget(SingleMoleculeTarget):
    """A model which stores information about a ``TorsionProfile_SMIRNOFF`` ForceBalance
    fitting target."""

    type: Literal["TorsionProfile_SMIRNOFF"] = "TorsionProfile_SMIRNOFF"

    @classmethod
    def from_directory(
        cls: Type["TorsionTarget"], directory: str, name: str, options: Dict[str, Any]
    ) -> "TorsionTarget":

        from openforcefield.topology import Molecule

        input_molecule_path = os.path.join(directory, options["mol2"])

        input_molecule = Molecule.from_file(
            input_molecule_path, allow_undefined_stereo=True
        )

        # Store a SMILES pattern with the driven torsion tagged with map indices.
        with open(os.path.join(directory, "metadata.json")) as file:
            metadata = json.load(file)

        dihedrals = metadata["dihedrals"]

        if len(dihedrals) != 1:
            raise NotImplementedError()

        atom_indices = dihedrals[0]

        rd_molecule = input_molecule.to_rdkit()

        for i, index in enumerate(atom_indices):

            rd_atom = rd_molecule.GetAtomWithIdx(index)
            rd_atom.SetAtomMapNum(i + 1)

        return cls(
            name=name,
            molecule=Chem.MolToSmiles(rd_molecule),
            options=options,
        )


class VibrationTarget(SingleMoleculeTarget):
    """A model which stores information about a ``VIBRATION_SMIRNOFF`` ForceBalance
    fitting target."""

    type: Literal["VIBRATION_SMIRNOFF"] = "VIBRATION_SMIRNOFF"


class OptGeoTarget(MultiMoleculeTarget):
    """A model which stores information about an ``OptGeoTarget_SMIRNOFF`` ForceBalance
    fitting target."""

    type: Literal["OptGeoTarget_SMIRNOFF"] = "OptGeoTarget_SMIRNOFF"

    @classmethod
    def from_directory(
        cls, directory: str, name: str, options: Dict[str, Any]
    ) -> "OptGeoTarget":
        from forcebalance.smirnoffio import OptGeoTarget_SMIRNOFF
        from openforcefield.topology import Molecule

        inner_options_path = os.path.join(directory, "optgeo_options.txt")
        inner_options = OptGeoTarget_SMIRNOFF.parse_optgeo_options(inner_options_path)

        molecules = [
            Molecule.from_file(
                os.path.join(directory, file_name), allow_undefined_stereo=True
            ).to_smiles(explicit_hydrogens=False)
            for inner_option_dict in inner_options.values()
            for file_name in inner_option_dict["mol2"]
        ]

        return cls(name=name, molecules=molecules, options=options)


FittingTarget = Union[TorsionTarget, VibrationTarget, OptGeoTarget]

TYPE_TO_FITTING_TARGET = {
    "TorsionProfile_SMIRNOFF": TorsionTarget,
    "VIBRATION_SMIRNOFF": VibrationTarget,
    "OptGeoTarget_SMIRNOFF": OptGeoTarget,
}
