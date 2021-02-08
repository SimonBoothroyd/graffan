from datetime import datetime
from typing import Dict, List, Literal

from pydantic import BaseModel, Field

from graffan.library.models.smirnoff import SMIRNOFFParameter
from graffan.utilities.provenance import default_analysis_provenance

GradientDictionary = Dict[str, Dict[str, Dict[str, float]]]


class AnalysisProvenance(BaseModel):
    """A model which stores provenance information about an analysed result."""

    time_created: datetime = Field(
        default_factory=datetime.now,
        description="The time and date that the analysis was performed.",
    )
    software_provenance: Dict[str, str] = Field(
        default_factory=default_analysis_provenance,
        description="A dictionary storing the versions of the software used in the "
        "analysis.",
    )


class AnalysedTarget(BaseModel):
    """A model which stores the analysed output of a fitting target. Currently this
    only contains information about per-molecule gradients."""

    type: Literal["torsion", "vibration", "optgeo"] = Field(
        ..., description="The type of target the gradients were computed for."
    )
    gradients: GradientDictionary = Field(
        ...,
        description="The gradients stored in a dictionary of the form: "
        "``gradients[param_id][param_attr][smiles] = value``.",
    )


class AnalysedIteration(BaseModel):
    """A model for storing analysis performed on the output of an iteration of a
    ForceBalance optimization."""

    provenance: AnalysisProvenance = Field(
        AnalysisProvenance(), description="Provenance about this model."
    )
    iteration: int = Field(
        ..., description="The optimization iteration which was analysed."
    )

    refit_parameters: List[SMIRNOFFParameter] = Field(
        ..., description="The parameters which were refit during the optimization."
    )

    targets: List[AnalysedTarget] = Field(
        ..., description="The analysed outputs of each target type."
    )
