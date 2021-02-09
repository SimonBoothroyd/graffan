import functools
from typing import List, Optional

from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D


@functools.lru_cache(1024)
def smiles_to_svg(smiles: str, highlight_smirks: Optional[str]) -> str:
    """Renders a 2D representation of a molecule based on its SMILES representation as
    an SVG string.

    Parameters
    ----------
    smiles
        The SMILES pattern.
    highlight_smirks
        An optional SMIRK pattern to use to highlight a subset of atoms within
        the molecule.

    Returns
    -------
        The 2D SVG representation.
    """
    from openforcefield.topology import Molecule
    from openforcefield.utils import RDKitToolkitWrapper

    # Parse the SMILES into an RDKit molecule
    smiles_parser = Chem.rdmolfiles.SmilesParserParams()
    smiles_parser.removeHs = False

    rdkit_molecule = Chem.MolFromSmiles(smiles, smiles_parser)

    # Generate a set of 2D coordinates.
    if not rdkit_molecule.GetNumConformers():
        Chem.rdDepictor.Compute2DCoords(rdkit_molecule)

    # Find any atoms which should be highlighted.
    highlight_atoms = set()
    highlight_bonds = set()

    if highlight_smirks is not None:

        openff_molecule = Molecule.from_smiles(smiles, allow_undefined_stereo=True)

        matches = RDKitToolkitWrapper().find_smarts_matches(
            openff_molecule, highlight_smirks
        )

        for match in matches:

            matched_bonds = [
                rdkit_molecule.GetBondBetweenAtoms(match[i], match[i + 1])
                for i in range(len(match) - 1)
            ]

            highlight_atoms.update(match)

            highlight_bonds.update(
                bond.GetIdx() for bond in matched_bonds if bond is not None
            )

    drawer = rdMolDraw2D.MolDraw2DSVG(300, 300)

    rdMolDraw2D.PrepareAndDrawMolecule(
        drawer,
        rdkit_molecule,
        highlightAtoms=[*highlight_atoms],
        highlightBonds=[*highlight_bonds],
    )

    drawer.FinishDrawing()

    svg_content = drawer.GetDrawingText()
    return svg_content


def smiles_to_grid_svg(smiles: List[str]) -> str:
    """Renders a grid of 2D representations of a set of molecules based on their SMILES
    representation as an SVG string.

    Parameters
    ----------
    smiles
        The list of SMILES patterns.

    Returns
    -------
        The 2D SVG representation.
    """

    # Parse the SMILES into an RDKit molecule
    smiles_parser = Chem.rdmolfiles.SmilesParserParams()
    smiles_parser.removeHs = True

    rdkit_molecules = [
        Chem.MolFromSmiles(smiles_pattern, smiles_parser) for smiles_pattern in smiles
    ]

    return Draw.MolsToGridImage(rdkit_molecules, 5, useSVG=True, subImgSize=(200, 200))
