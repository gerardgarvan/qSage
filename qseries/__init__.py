"""qseries-sage: SageMath port of Garvan's Maple qseries package v1.3.

Clean reimplementation from documentation only.
Reference: https://qseries.org/fgarvan/qmaple/qseries/
"""

from qseries._series import QSeries
from qseries._symbolic import (
    QProduct,
    EtaProduct,
    EProduct,
    JacProduct,
    PochProduct,
)
from qseries._utilities import qdegree, lqdegree, lqdegree0
from qseries._building_blocks import (
    aqprod,
    qbin,
    etaq,
    jacprod,
    theta,
    theta2,
    theta3,
    theta4,
    tripleprod,
    quinprod,
    winquist,
)
from qseries._utilities import sift, checkmult, checkprod, packageversion, changes
from qseries._prodmake import prodmake
from qseries._conversion import (
    etamake,
    qetamake,
    jacprodmake,
    jac2prod,
    jac2series,
    mprodmake,
    qfactor,
    zqfactor,
    qs2jaccombo,
    findprod,
)

__all__ = [
    # Core wrapper
    "QSeries",
    # Symbolic output types (FOUND-03)
    "QProduct",
    "EtaProduct",
    "EProduct",
    "JacProduct",
    "PochProduct",
    # Degree utilities (FOUND-05) — UTIL-02, UTIL-03, UTIL-04
    "qdegree",
    "lqdegree",
    "lqdegree0",
    # Building blocks (BUILD-01 through BUILD-11)
    "aqprod",
    "qbin",
    "etaq",
    "jacprod",
    "theta",
    "theta2",
    "theta3",
    "theta4",
    "tripleprod",
    "quinprod",
    "winquist",
    # Series utilities (UTIL-01 through UTIL-08)
    "sift",
    "checkmult",
    "checkprod",
    "packageversion",
    "changes",
    # Product conversion (CONV-01)
    "prodmake",
    # Product conversion — eta-family (CONV-02, CONV-03)
    "etamake",
    "qetamake",
    # Product conversion — jac-family (CONV-04, CONV-08, CONV-09) — stubs
    "jacprodmake",
    "jac2prod",
    "jac2series",
    # Product conversion — misc (CONV-05 through CONV-07, CONV-10, CONV-11) — stubs
    "mprodmake",
    "qfactor",
    "zqfactor",
    "qs2jaccombo",
    "findprod",
]
__version__ = "1.3.0"
