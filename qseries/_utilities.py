"""Degree utility functions for qseries-sage.

qdegree:   highest q-degree in a truncated q-series (QSeries input).
lqdegree:  lowest q-degree in a sum of q-monomials (QSeries input).
lqdegree0: q-degree of a single q-monomial (QSeries or symbolic type).

Clean reimplementation from Garvan's qseries documentation only.
Reference: https://qseries.org/fgarvan/qmaple/qseries/
No Maple source was consulted during implementation.
"""
from math import gcd
from sage.all import QQ
from qseries._series import QSeries
from qseries._prodmake import prodmake


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


# ---------------------------------------------------------------------------
# sift — UTIL-01
# ---------------------------------------------------------------------------

def sift(s, q, n, k, T):
    """Extract residue class from a q-series.

    Returns sum_{i=0}^{T//n} a[n*i + k] * q^i where a[j] = coefficient of q^j in s.

    s:  QSeries input
    q:  unused symbolic q variable (kept for Maple interface fidelity)
    n:  period (integer >= 1)
    k:  offset (0 <= k < n)
    T:  upper bound on source index (use s.T or explicit limit)

    Uses s.series.parent() as the output ring to preserve the coefficient ring
    (e.g. GF(p) input survives).

    Oracle: Garvan sift doc page; tutorial sec 6.2 (E0 = sift(etaq(q,1,500), q, 5, 0, 499)).
    """
    R = s.series.parent()  # preserves coefficient ring (GF(p), QQ, etc.)
    qvar = R.gen()
    result = R.zero()
    i = 0
    while True:
        idx = n * i + k
        if idx >= T:
            break
        # Guard against reading past precision (Pitfall 7)
        if idx >= s.series.prec():
            break
        coeff = s.series[idx]
        result += coeff * qvar**i
        i += 1
    T_out = i  # number of terms collected
    return QSeries(result.add_bigoh(T_out), T=T_out)


# ---------------------------------------------------------------------------
# checkmult — UTIL-05
# ---------------------------------------------------------------------------

def checkmult(QS, T, x=None):
    """Test whether the coefficients of QS satisfy multiplicativity.

    Checks a(m*n) == a(m) * a(n) for all coprime pairs (m, n) with m < n, m*n <= T.
    Returns True if multiplicative, False otherwise.

    QS:  QSeries (coefficients a[1], a[2], ..., a[T])
    T:   upper bound on product m*n to test
    x:   "yes" = verbose (print failing pairs); None = silent

    Return type: Python bool (not Maple's 1/0). See D-07.
    Oracle: Garvan checkmult doc page; RESEARCH.md Pattern 5.
    """
    verbose = (x == "yes")
    is_mult = True
    for m in range(1, T + 1):
        for n in range(m + 1, T + 1):
            mn = m * n
            if mn > T:
                break
            if gcd(m, n) != 1:
                continue
            # Skip pairs where any index is at or beyond precision (unknown coefficient)
            prec = QS.series.prec()
            if m >= prec or n >= prec or mn >= prec:
                continue
            am = QS.series[m]
            an = QS.series[n]
            amn = QS.series[mn]
            if amn != am * an:
                if verbose:
                    print(f"checkmult: a({mn}) = {amn} != a({m})*a({n}) = {am}*{an} = {am * an}")
                    is_mult = False
                else:
                    return False
    return bool(is_mult)


# ---------------------------------------------------------------------------
# checkprod — UTIL-06 (stub)
# ---------------------------------------------------------------------------

def checkprod(f, M, Q):
    """Check if a q-series has a 'nice' infinite product representation.

    Calls prodmake(f, None, Q) and checks whether all exponents |e_n| <= M.
    Returns [c, exps] where c is the constant prefactor (always 1 for prodmake input)
    and exps is the list of exponents e_1, ..., e_{Q-1}.
    Returns False if any |e_n| > M.

    f:  QSeries with constant term 1 and r=0
    M:  maximum allowed absolute value of any exponent e_n
    Q:  number of exponents to compute (= T argument to prodmake)

    Oracle: Garvan checkprod doc page (UTIL-06); verified in 02-RESEARCH.md.
    """
    p = prodmake(f, None, Q)
    # Check all exponents satisfy |e_n| <= M
    for n, e in p.exponents.items():
        if abs(QQ(e)) > M:
            return False
    # Return [constant, exponent_list] — constant is always 1 for prodmake input
    exp_list = [p.exponents.get(n, 0) for n in range(1, Q)]
    return [QQ(1), exp_list]


# ---------------------------------------------------------------------------
# packageversion — UTIL-07
# ---------------------------------------------------------------------------

def packageversion():
    """Return the qseries package version string.

    Reads __version__ from the qseries package.
    Oracle: Garvan packageversion doc page.
    """
    import qseries
    return qseries.__version__


# ---------------------------------------------------------------------------
# changes — UTIL-08
# ---------------------------------------------------------------------------

def changes():
    """Return a changelog string listing recent changes to qseries-sage.

    Oracle: Garvan changes doc page (returns a list of changes as a string).
    """
    return (
        "qseries-sage v1.3.0 (2026-11-05): milestone v1.0 - all 41 functions of qseries 1.3.\n"
        "  Phase 7: zqfactor implemented (ZQProduct); setup.cfg packaging; README; every test cites its oracle.\n"
        "  Phase 6: findhommodp, findhomcombomodp, findlincombomodp (GF(p)).\n"
        "  Phase 5: findhom, findhomcombo, findnonhom, findnonhomcombo, findlincombo, findmaxind, findpoly, findcong.\n"
        "  Phase 4: etamake, qetamake, jacprodmake, jac2prod, jac2series, mprodmake, qfactor, qs2jaccombo, findprod.\n"
        "  Phase 3: prodmake (Andrews' algorithm).\n"
        "  Phase 2: All 11 building-block functions and 8 utility functions implemented.\n"
        "  Phase 1: QSeries wrapper, five symbolic output types, degree conventions.\n"
        "  Clean reimplementation from Garvan qseries v1.3 documentation only.\n"
        "  Reference: https://qseries.org/fgarvan/qmaple/qseries/"
    )