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
    qs2jaccombo,
    findprod,
    MProduct,
    QFactorResult,
)
from qseries._zqfactor import zqfactor, ZQProduct
from qseries._relations import (
    findhom,
    findhomcombo,
    findnonhom,
    findnonhomcombo,
    findlincombo,
    findmaxind,
    findpoly,
    findcong,
    findhommodp,
    findhomcombomodp,
    findlincombomodp,
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
    # Product conversion — jac-family (CONV-04, CONV-08, CONV-09)
    "jacprodmake",
    "jac2prod",
    "jac2series",
    # Product conversion — misc (CONV-05 through CONV-07, CONV-10, CONV-11)
    "mprodmake",
    "qfactor",
    "zqfactor",
    "qs2jaccombo",
    "findprod",
    # Return types for mprodmake and qfactor
    "MProduct",
    "QFactorResult",
    # Return type for zqfactor (CONV-07)
    "ZQProduct",
    # Relation finding — exact (REL-01, 02, 05, 06, 07, 09, 10, 11)
    "findhom",
    "findhomcombo",
    "findnonhom",
    "findnonhomcombo",
    "findlincombo",
    "findmaxind",
    "findpoly",
    "findcong",
    # Relation finding — mod p (REL-03, REL-04, REL-08)
    "findhommodp",
    "findhomcombomodp",
    "findlincombomodp",
]
__version__ = "1.3.0"
