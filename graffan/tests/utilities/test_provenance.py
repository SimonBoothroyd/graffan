from graffan.utilities.provenance import default_analysis_provenance


def test_default_analysis_provenance():

    provenance = default_analysis_provenance()

    assert "graffan" in provenance
    assert "forcebalance" in provenance
