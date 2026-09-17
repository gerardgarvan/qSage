# qseries/_conversion.py
#
# Licensing note:
# This file is a clean reimplementation derived solely from the documentation of
# Frank Garvan's Maple qseries package v1.3 (https://qseries.org/fgarvan/qmaple/qseries/)
# and the accompanying tutorial (qseriesdoc.pdf). No Maple source code was consulted
# or translated. All mathematical algorithms are derived from the documented function
# specifications and examples. The qseries package is copyright Frank Garvan; this
# Python reimplementation is an independent work for research use in SageMath environments.

"""Product-conversion functions for qseries-sage (Phase 4).

Implements CONV-02 through CONV-11: etamake, qetamake, jacprodmake, jac2prod,
jac2series, mprodmake, qfactor, zqfactor, qs2jaccombo, findprod.

All 10 names are exported so that import lines in Plans 04-02 and 04-03 never
raise ImportError. Functions not yet implemented raise NotImplementedError.
"""

from sage.all import QQ
from collections import defaultdict

from qseries._series import QSeries
from qseries._symbolic import EtaProduct, EProduct, QProduct
from qseries._building_blocks import etaq


# ---------------------------------------------------------------------------
# CONV-02: etamake
# ---------------------------------------------------------------------------

def etamake(f, q, T):
    """Greedy eta-product identification (CONV-02).

    Given a QSeries f, returns an EtaProduct c * q^r * prod_k eta(k*tau)^{e_k}
    such that to_series(T) matches f to O(q^T).

    Algorithm (D-04):
      1. Strip fractional q-shift r_input and leading constant c.
      2. Greedy loop: find lowest non-unit coefficient c_k at q^k;
         multiply residual by etaq(q,k,T)^(c_k) to cancel; record eta(k*tau)^(-c_k).
      3. EtaProduct.r = r_input - sum(k * e_k / 24) over recorded factors.

    Oracle (D-05):
      etamake(theta3(q,100), q, 100) -> eta(2tau)^5 / (eta(4tau)^2 * eta(tau)^2)
      etamake(theta4(q,100), q, 100) -> eta(tau)^2 / eta(2tau)
      etamake(theta2(q,100), q, 100) -> 2 * eta(4tau)^2 / eta(2tau)  (r=0)
    """
    r_input = QQ(f.r)

    # Step 1: strip leading constant so residual has constant term 1
    c = QQ(f.series[0])
    if c == 0:
        raise ValueError("etamake: leading coefficient is zero; cannot normalize")

    R = f.series.parent()
    residual_series = (f.series / c).add_bigoh(T)
    residual = QSeries(residual_series, T=T)  # r=0

    factors = []  # list of (level, exponent) pairs

    # Step 2: greedy cancellation loop
    for _ in range(T - 1):
        # Find lowest k >= 1 where coefficient != 0
        k = None
        for n in range(1, T):
            coeff = QQ(residual.series[n])
            if coeff != 0:
                k = n
                c_k = coeff
                break
        if k is None:
            break  # residual == 1 + O(q^T): done

        c_k_q = QQ(c_k)
        if c_k_q.denominator() != 1:
            raise ValueError(
                f"etamake: non-integer coefficient {c_k} at q^{k}; "
                "series is not an exact eta-product to this precision"
            )
        c_k_int = int(c_k_q)

        # Multiply residual by etaq(q,k,T)^(c_k_int) to cancel +c_k q^k term.
        # etaq = 1 - q^k + ..., so (etaq)^(c_k_int) contributes -c_k_int * q^k,
        # cancelling the positive c_k_int coefficient.
        eta_k = etaq(q, k, T)
        if c_k_int >= 0:
            multiplier = eta_k ** c_k_int
        else:
            # Negative exponent: multiply by etaq^(c_k_int) = 1/(etaq^|c_k_int|)
            # Use series inversion
            abs_exp = -c_k_int
            inv_series = (eta_k.series ** abs_exp).__invert__().add_bigoh(T)
            multiplier = QSeries(inv_series, T=T)

        residual = residual * multiplier
        # Record eta(k*tau)^(-c_k_int) in the EtaProduct
        factors.append((k, -c_k_int))

    # Step 3: compute EtaProduct.r
    # eta(k*tau) = q^(k/24) * prod_{n>=1}(1-q^{kn}), so accumulated q-shift
    # from the recorded factors (k, e_k) is sum(k * e_k / 24).
    eta_shift = sum(QQ(k) * QQ(e) / QQ(24) for k, e in factors)
    r_out = r_input - eta_shift

    # Merge duplicate levels
    merged = defaultdict(lambda: QQ(0))
    for k, e in factors:
        merged[k] += QQ(e)
    factors_merged = [(k, int(merged[k])) for k in sorted(merged) if merged[k] != 0]

    return EtaProduct(constant=c, r=r_out, factors=factors_merged)


# ---------------------------------------------------------------------------
# CONV-03: qetamake
# ---------------------------------------------------------------------------

def qetamake(f, q, T):
    """Greedy _E-product identification (CONV-03).

    Returns an EProduct with exponents dict {k: e_k} such that
    to_series(T) matches f to O(q^T).

    Requires f.r == 0 (no fractional q-shift). Same greedy algorithm as etamake
    but factors are _E(q^k) = prod_{n>=1}(1-q^{kn}) (no q^(k/24) shift tracked).

    Oracle: qetamake(triangular_series, q, 30) -> EProduct({1:-1, 2:2})
    """
    if QQ(f.r) != 0:
        raise ValueError(
            f"qetamake requires r=0 (no fractional q-shift), got r={f.r}"
        )

    c = QQ(f.series[0])
    if c == 0:
        raise ValueError("qetamake: leading coefficient is zero")
    if c != 1:
        # qetamake strips constant silently (consistent with etamake)
        residual_series = (f.series / c).add_bigoh(T)
    else:
        residual_series = f.series.add_bigoh(T)
    residual = QSeries(residual_series, T=T)

    factors = []

    for _ in range(T - 1):
        k = None
        for n in range(1, T):
            coeff = QQ(residual.series[n])
            if coeff != 0:
                k = n
                c_k = coeff
                break
        if k is None:
            break

        c_k_q = QQ(c_k)
        if c_k_q.denominator() != 1:
            raise ValueError(
                f"qetamake: non-integer coefficient {c_k} at q^{k}"
            )
        c_k_int = int(c_k_q)

        eta_k = etaq(q, k, T)
        if c_k_int >= 0:
            multiplier = eta_k ** c_k_int
        else:
            abs_exp = -c_k_int
            inv_series = (eta_k.series ** abs_exp).__invert__().add_bigoh(T)
            multiplier = QSeries(inv_series, T=T)

        residual = residual * multiplier
        factors.append((k, -c_k_int))

    merged = defaultdict(lambda: QQ(0))
    for k, e in factors:
        merged[k] += QQ(e)
    exponents = {k: int(merged[k]) for k in sorted(merged) if merged[k] != 0}
    return EProduct(exponents=exponents)


# ---------------------------------------------------------------------------
# CONV-04: jacprodmake (Plan 04-02)
# ---------------------------------------------------------------------------

def jacprodmake(f, q, T, base=None):
    """Jacobi product identification (CONV-04). Implemented in Plan 04-02."""
    raise NotImplementedError("jacprodmake: implemented in Plan 04-02")


# ---------------------------------------------------------------------------
# CONV-08: jac2prod (Plan 04-02)
# ---------------------------------------------------------------------------

def jac2prod(jacexpr):
    """Convert JacProduct to PochProduct (CONV-08). Implemented in Plan 04-02."""
    raise NotImplementedError("jac2prod: implemented in Plan 04-02")


# ---------------------------------------------------------------------------
# CONV-09: jac2series (Plan 04-02)
# ---------------------------------------------------------------------------

def jac2series(jacexpr, T):
    """Expand JacProduct to QSeries (CONV-09). Implemented in Plan 04-02."""
    raise NotImplementedError("jac2series: implemented in Plan 04-02")


# ---------------------------------------------------------------------------
# CONV-05: mprodmake (Plan 04-03)
# ---------------------------------------------------------------------------

def mprodmake(f, q, T):
    """Write f as a product of (1+q^n) factors (CONV-05). Implemented in Plan 04-03."""
    raise NotImplementedError("mprodmake: implemented in Plan 04-03")


# ---------------------------------------------------------------------------
# CONV-06: qfactor (Plan 04-03)
# ---------------------------------------------------------------------------

def qfactor(f, T=None):
    """Factor a polynomial/rational function in q (CONV-06). Implemented in Plan 04-03."""
    raise NotImplementedError("qfactor: implemented in Plan 04-03")


# ---------------------------------------------------------------------------
# CONV-07: zqfactor (Plan 04-03)
# ---------------------------------------------------------------------------

def zqfactor(F, z, q, N=1000):
    """Factor a bivariate (z,q)-series (CONV-07). Implemented in Plan 04-03."""
    raise NotImplementedError("zqfactor: implemented in Plan 04-03")


# ---------------------------------------------------------------------------
# CONV-10: qs2jaccombo (Plan 04-03)
# ---------------------------------------------------------------------------

def qs2jaccombo(f, q, T, P=None):
    """Convert each term in a sum to a JacProduct (CONV-10). Implemented in Plan 04-03."""
    raise NotImplementedError("qs2jaccombo: implemented in Plan 04-03")


# ---------------------------------------------------------------------------
# CONV-11: findprod (Plan 04-03)
# ---------------------------------------------------------------------------

def findprod(FL, T, M, Q):
    """Exhaustive search for q-products (CONV-11). Implemented in Plan 04-03."""
    raise NotImplementedError("findprod: implemented in Plan 04-03")
