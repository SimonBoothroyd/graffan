from typing import Dict


def default_analysis_provenance() -> Dict[str, str]:
    """Returns a dictionary containing the versions of key software packages used as
    part of any analysis."""

    import forcebalance

    import graffan

    return {"graffan": graffan.__version__, "forcebalance": forcebalance.__version__}
