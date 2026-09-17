"""Degree utility functions for qseries-sage.

qdegree:   highest q-degree in a truncated q-series (QSeries input).
lqdegree:  lowest q-degree in a sum of q-monomials (QSeries input).
lqdegree0: q-degree of a single q-monomial (QSeries or symbolic type).

Clean reimplementation from Garvan's qseries documentation only.
Reference: https://qseries.org/fgarvan/qmaple/qseries/
No Maple source was consulted during implementation.
"""
from sage.all import QQ
from qseries._series import QSeries


def qdegree(f: QSeries):
    """Return the highest q-degree in f, including the rational shift r.

    Raises TypeError if f is not a QSeries.
    Raises ValueError if f is the zero series.

    Example (matches Maple docs):
      P = q^(-5) - q^(-4) - q^(-3) + 1 + q^2 - q^7 - q^10 + O(q^17)
      qdegree(P) -> 10  (with r=0; shift is included when r != 0)
    """
    if not isinstance(f, QSeries):
        raise TypeError(f"qdegree expects a QSeries, got {type(f)}")
    s = f.series
    if s.is_zero():
        raise ValueError("qdegree undefined for zero series")
    return QQ(f.r) + QQ(s.degree())


def lqdegree(f: QSeries):
    """Return the lowest q-degree in f, including rational shift.

    Degrees may be negative or fractional. Raises ValueError for zero series.

    Example (matches Maple docs):
      lqdegree(QSeries with r=0, series=q^(-5)+...) -> -5
    """
    if not isinstance(f, QSeries):
        raise TypeError(f"lqdegree expects a QSeries, got {type(f)}")
    s = f.series
    if s.is_zero():
        raise ValueError("lqdegree undefined for zero series")
    return QQ(f.r) + QQ(s.valuation())


def lqdegree0(f):
    """Return the q-degree of a single q-monomial f.

    f may be a QSeries (reads r + valuation) or a symbolic type with .r attribute
    (EtaProduct, JacProduct, etc., reads .r directly).

    Handles fractional and negative degrees. Does NOT raise for zero series
    (behaviour on zero input is unspecified by the doc page; callers should
    guard against zero before calling lqdegree0).

    Note (D-15): symbolic sums of JAC terms (e.g. (1/2)*JAC(1,2,inf) + q*JAC(3,4,inf))
    are out of scope for v1.0. Call lqdegree0 on individual monomial terms only.

    Examples (from Garvan doc page):
      lqdegree0(sqrt(q)*JAC(...))   -> 1/2
      lqdegree0(q*JAC(...))         -> 1
      lqdegree0(JAC(...))           -> 0
      lqdegree0(JAC(...)/q^3)       -> -3
      lqdegree0(JAC(...)/q^(1/3))   -> -1/3
    """
    if isinstance(f, QSeries):
        return QQ(f.r) + QQ(f.series.valuation())
    if hasattr(f, 'r'):
        return QQ(f.r)
    raise TypeError(f"lqdegree0: cannot extract q-degree from {type(f)}")
