# qseries/_prodmake.py
#
# Clean reimplementation from Garvan's qseries documentation only.
# Reference: https://qseries.org/fgarvan/qmaple/qseries/
# Algorithm: Andrews' divisor-sum recurrence (tutorial §3, prodmake doc page)
# No Maple source was consulted.
#
# Licensing note:
# This file is a clean reimplementation derived solely from the documentation of
# Frank Garvan's Maple qseries package v1.3 (https://qseries.org/fgarvan/qmaple/qseries/)
# and the accompanying tutorial (qseriesdoc.pdf). No Maple source code was consulted
# or translated. All mathematical algorithms are derived from the documented function
# specifications and examples. The qseries package is copyright Frank Garvan; this
# Python reimplementation is an independent work for research use in SageMath environments.

from sage.all import QQ, divisors
from qseries._series import QSeries
from qseries._symbolic import QProduct


def prodmake(f, q, T):
    """Recover the exponent sequence of an infinite q-product from a truncated series.

    Given f = QSeries with f = 1 + b_1 q + b_2 q^2 + ... (constant term 1, r=0),
    returns a QProduct with exponents dict {n: e_n} such that
        f == prod_{n=1}^{T-1} (1 - q^n)^(e_n)  to O(q^T).

    Algorithm (Andrews' recurrence from Garvan tutorial §3):
      Step 1 — auxiliary sequence c_n (n = 1, ..., T-1):
        c_n = n * b_n - sum_{k=1}^{n-1} b_{n-k} * c_k

      Step 2 — exponents (divisor-sum inversion):
        a_n = (c_n - sum_{d | n, d < n} d * a_d) / n

    Sign convention:
      Maple defines f = prod(1-q^n)^(-a_n).
      QProduct stores e_n = -a_n (positive exponents for "nice" products).
      So if f = prod(1-q^n) (e.g. etaq), then a_n = -1 for all n, e_n = 1.

    Raises:
      ValueError: if f.r != 0 (fractional prefix — handle in etamake, not here)
      ValueError: if constant term of f is not 1

    Per decisions D-01, D-02, D-03 from 03-CONTEXT.md.

    Oracle: Garvan prodmake doc page; tutorial §3.1 Rogers-Ramanujan example.
    """
    # D-01: require r == 0 and constant term == 1
    if f.r != 0:
        raise ValueError(
            f"prodmake requires a series with no fractional q-power prefix (r=0), "
            f"got r={f.r}. Strip the prefix first (etamake handles this in Phase 4)."
        )
    b0 = f.series[0]
    if b0 != 1:
        raise ValueError(
            f"prodmake requires the constant term to be 1, got {b0}. "
            f"Divide by the leading coefficient before calling prodmake."
        )

    # Extract coefficients b_0, b_1, ..., b_{T-1} as QQ elements
    b = [QQ(f.series[n]) for n in range(T)]

    # Step 1: compute c_n for n = 1, ..., T-1
    c = [QQ(0)] * T          # c[0] unused; c[n] = c_n
    for n in range(1, T):
        c[n] = QQ(n) * b[n]
        for k in range(1, n):
            c[n] -= b[n - k] * c[k]

    # Step 2: recover Maple exponents a_n via divisor-sum inversion
    a = [QQ(0)] * T          # a[0] unused; a[n] = a_n (Maple convention)
    for n in range(1, T):
        inner = sum(QQ(d) * a[d] for d in divisors(n) if d < n)
        a[n] = (c[n] - inner) / QQ(n)

    # Convert to QProduct sign convention: e_n = -a_n
    # D-02: omit zero exponents
    exponents = {n: -a[n] for n in range(1, T) if a[n] != 0}
    return QProduct(exponents=exponents)
