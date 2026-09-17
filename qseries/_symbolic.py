"""Symbolic output types for qseries-sage.

Five classes matching the return types of prodmake, etamake, qetamake,
jacprodmake, and jac2prod respectively.

Clean reimplementation from Garvan's qseries documentation only.
Reference: https://qseries.org/fgarvan/qmaple/qseries/
No Maple source was consulted during implementation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any

from sage.all import QQ
from sage.all import LaurentSeriesRing


def _get_QSeries():
    """Lazy import of QSeries to avoid circular/missing import at module load."""
    from qseries._series import QSeries  # noqa: PLC0415
    return QSeries


def _exp_str(base: str, e) -> str:
    """Format 'base^e' suppressing '^1'."""
    if e == 1:
        return base
    return f"{base}^{e}"


# ---------------------------------------------------------------------------
# QProduct
# ---------------------------------------------------------------------------

@dataclass
class QProduct:
    """Return type of prodmake: product of (1-q^n)^e_n factors.

    exponents: dict mapping n -> e_n; zero exponents omitted.
    """
    exponents: Dict[int, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        if not self.exponents:
            return "1"
        parts = []
        for n in sorted(self.exponents):
            e = self.exponents[n]
            if e == 0:
                continue
            base = "(1-q)" if n == 1 else f"(1-q^{n})"
            parts.append(_exp_str(base, e))
        return " * ".join(parts) if parts else "1"

    def to_series(self, T: int):
        """Expand the product to a QSeries truncated at T."""
        QSeries = _get_QSeries()
        R = LaurentSeriesRing(QQ, 'q')
        q = R.gen()
        result = R(1).add_bigoh(T)
        for n, e in self.exponents.items():
            factor = (1 - q**n).add_bigoh(T)
            result = (result * factor**e).add_bigoh(T)
        return QSeries(result, T=T)


# ---------------------------------------------------------------------------
# EProduct
# ---------------------------------------------------------------------------

@dataclass
class EProduct:
    """Return type of qetamake: product of _E(q^k)^e_k factors.

    _E(q^k) = prod_{n>=1}(1 - q^{kn})  (the eta function without q^(k/24) prefactor)
    exponents: dict mapping k -> e_k.
    """
    exponents: Dict[int, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        if not self.exponents:
            return "1"
        parts = []
        for k in sorted(self.exponents):
            e = self.exponents[k]
            if e == 0:
                continue
            base = "_E(q)" if k == 1 else f"_E(q^{k})"
            parts.append(_exp_str(base, e))
        return " * ".join(parts) if parts else "1"

    def to_series(self, T: int):
        """Expand to a QSeries truncated at T using etaq-style product."""
        QSeries = _get_QSeries()
        R = LaurentSeriesRing(QQ, 'q')
        q = R.gen()
        result = R(1).add_bigoh(T)
        for k, e in self.exponents.items():
            # _E(q^k) = prod_{n>=1}(1-q^{kn}); build by direct product up to T
            factor = R(1).add_bigoh(T)
            for n in range(1, (T - 1) // k + 1):
                factor = (factor * (1 - q**(k * n))).add_bigoh(T)
            result = (result * factor**e).add_bigoh(T)
        return QSeries(result, T=T)


# ---------------------------------------------------------------------------
# EtaProduct
# ---------------------------------------------------------------------------

@dataclass
class EtaProduct:
    """Return type of etamake: c * q^r * prod_k eta(k*tau)^e_k.

    constant: scalar coefficient (QQ element or integer); omitted in repr if 1
    r:        rational q-power shift; omitted in repr if 0
    factors:  list of (level, exponent) pairs; level=1 prints as eta(tau)
    """
    constant: Any = 1
    r: Any = 0          # rational, stored as QQ
    factors: List[Tuple] = field(default_factory=list)

    def __repr__(self) -> str:
        parts = []
        if self.constant != 1:
            parts.append(str(self.constant))
        r = QQ(self.r)
        if r != 0:
            parts.append(f"q^({r})")
        for level, e in sorted(self.factors, key=lambda x: x[0]):
            base = "eta(tau)" if level == 1 else f"eta({level}*tau)"
            parts.append(_exp_str(base, e))
        return " * ".join(parts) if parts else "1"

    def to_series(self, T: int):
        """Convert to QSeries by expanding each eta factor.

        eta(k*tau) = q^(k/24) * prod_{n>=1}(1-q^{kn}). The EtaProduct
        represents c * q^r * prod_k eta(k*tau)^e_k, so the total q-power
        shift is r + sum_k(k * e_k / 24). We track this as the QSeries shift.
        """
        QSeries = _get_QSeries()
        R = LaurentSeriesRing(QQ, 'q')
        q = R.gen()
        result = R(self.constant).add_bigoh(T)
        total_shift = QQ(self.r)
        for level, e in self.factors:
            # Accumulate q^(level/24)^e contribution to the total shift
            total_shift += QQ(level) * QQ(e) / QQ(24)
            # Expand prod_{n>=1}(1-q^{level*n}) up to T
            eta_k = R(1).add_bigoh(T)
            for n in range(1, (T - 1) // level + 1):
                eta_k = (eta_k * (1 - q**(level * n))).add_bigoh(T)
            result = (result * eta_k**e).add_bigoh(T)
        return QSeries(result, T=T, r=total_shift)


# ---------------------------------------------------------------------------
# JacProduct
# ---------------------------------------------------------------------------

@dataclass
class JacProduct:
    """Return type of jacprodmake: c * q^r * product of JAC(a,b,infinity)^e factors.

    JAC(a,b,infinity) = (q^a;q^b)_inf * (q^{b-a};q^b)_inf * (q^b;q^b)_inf
    Special case: JAC(0,b,infinity) = (q^b;q^b)_inf only (tutorial §3.4).

    constant: scalar coefficient; omitted in repr if 1
    r:        rational q-power shift; omitted in repr if 0
    factors:  list of (a, b, e) triples; e may be rational
    """
    constant: Any = 1
    r: Any = 0
    factors: List[Tuple] = field(default_factory=list)

    def __repr__(self) -> str:
        parts = []
        if self.constant != 1:
            parts.append(str(self.constant))
        r = QQ(self.r)
        if r != 0:
            parts.append(f"q^({r})")
        for a, b, e in self.factors:
            base = f"JAC({a},{b},infinity)"
            e_q = QQ(e)
            if e_q.denominator() != 1:
                parts.append(f"{base}^({e_q})")
            else:
                parts.append(_exp_str(base, int(e_q)))
        return " * ".join(parts) if parts else "1"

    def to_series(self, T: int):
        """Expand JAC factors to a QSeries truncated at T.

        Handles:
        - a == 0: JAC(0,b,inf) = (q^b;q^b)_inf only (not three factors)
        - rational e: use jac.nth_root(den) ** num (constant term is 1, so root exists)
        """
        QSeries = _get_QSeries()
        R = LaurentSeriesRing(QQ, 'q')
        q = R.gen()
        result = R(self.constant).add_bigoh(T)

        def poch(start, step, prec):
            """(q^start; q^step)_inf up to prec."""
            s = R(1).add_bigoh(prec)
            n = 0
            while start + n * step < prec:
                s = (s * (1 - q**(start + n * step))).add_bigoh(prec)
                n += 1
            return s

        for a, b, e in self.factors:
            if a == 0:
                # JAC(0,b,inf) = (q^b;q^b)_inf only
                jac = poch(b, b, T)
            else:
                jac = (poch(a, b, T) * poch(b - a, b, T) * poch(b, b, T)).add_bigoh(T)
            # Handle rational exponents: e = num/den -> jac.nth_root(den) ** num
            e_q = QQ(e)
            if e_q.denominator() != 1:
                num, den = int(e_q.numerator()), int(e_q.denominator())
                jac_e = jac.nth_root(den) ** num
            else:
                jac_e = jac ** int(e_q)
            result = (result * jac_e).add_bigoh(T)
        return QSeries(result, T=T, r=QQ(self.r))


# ---------------------------------------------------------------------------
# PochProduct
# ---------------------------------------------------------------------------

@dataclass
class PochProduct:
    """Return type of jac2prod: product of (q^a;q^b)_infinity^e factors.

    factors: list of (a, b, e) triples
    """
    factors: List[Tuple] = field(default_factory=list)

    def __repr__(self) -> str:
        if not self.factors:
            return "1"
        parts = []
        for a, b, e in self.factors:
            if a == 1 and b == 1:
                base = "(q;q)_infinity"
            elif a == 1:
                base = f"(q;q^{b})_infinity"
            else:
                base = f"(q^{a};q^{b})_infinity"
            parts.append(_exp_str(base, e))
        return " * ".join(parts)

    def to_series(self, T: int):
        """Expand Pochhammer factors to a QSeries truncated at T."""
        QSeries = _get_QSeries()
        R = LaurentSeriesRing(QQ, 'q')
        q = R.gen()
        result = R(1).add_bigoh(T)
        for a, b, e in self.factors:
            factor = R(1).add_bigoh(T)
            n = 0
            while a + n * b < T:
                factor = (factor * (1 - q**(a + n * b))).add_bigoh(T)
                n += 1
            result = (result * factor**e).add_bigoh(T)
        return QSeries(result, T=T)
