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

__all__ = [
    # Core wrapper
    "QSeries",
    # Symbolic output types (FOUND-03)
    "QProduct",
    "EtaProduct",
    "EProduct",
    "JacProduct",
    "PochProduct",
    # Degree utilities (FOUND-05)
    "qdegree",
    "lqdegree",
    "lqdegree0",
]
__version__ = "1.3.0"
