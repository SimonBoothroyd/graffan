from typing import Literal

from pydantic import BaseModel, Field

SMIRNOFFHandler = Literal[
    "Constraints",
    "Bonds",
    "Angles",
    "ProperTorsions",
    "ImproperTorsions",
    "vdW",
    "LibraryCharges",
    "ChargeIncrements",
]


class SMIRNOFFParameter(BaseModel):
    """A model which tracks a particular SMIRNOFF force field parameter."""

    handler: SMIRNOFFHandler = Field(
        ..., description="The name of the handler associated with the parameter."
    )
    smirks: str = Field(
        ...,
        description="The SMIRKS pattern describing the chemical environment that this "
        "parameter is applied to.",
    )
    attribute: str = Field(
        ...,
        description="The specific attribute of the parameter being referenced (e.g. "
        "`k1`, `epsilon`).",
    )

    id: str = Field(..., description="The unique ID associated with the parameter.")
