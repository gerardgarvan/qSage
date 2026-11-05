# qseries/_series.py
#
# Licensing note:
# This file is a clean reimplementation derived solely from the documentation of
# Frank Garvan's Maple qseries package v1.3 (https://qseries.org/fgarvan/qmaple/qseries/)
# and the accompanying tutorial (qseriesdoc.pdf). No Maple source code was consulted
# or translated. All mathematical algorithms are derived from the documented function
# specifications and examples. The qseries package is copyright Frank Garvan; this
# Python reimplementation is an independent work for research use in SageMath environments.

from sage.all import QQ
from sage.all import LaurentSeriesRing


class QSeries:
    """Wrapper around a Sage LaurentSeries with explicit truncation order and rational shift.

    Attributes:
        series: The underlying Sage LaurentSeries object.
        T:      Truncation order (integer). Arithmetic propagates Sage's actual precision.
        r:      Rational exponent shift. The represented object is q^r * series.
        R:      Coefficient ring (QQ by default; GF(p) for mod-p; polynomial ring in z
                for bivariate functions).
    """

    def __init__(self, series, T=20, r=None, R=None):
        from sage.all import Infinity
        self.series = series
        self.T = T if T is Infinity else int(T)
        # Infer R from the series parent's base ring if not supplied
        parent = series.parent()
        if R is None:
            self.R = parent.base_ring()
        else:
            self.R = R
        if r is None:
            self.r = QQ(0)
        else:
            self.r = QQ(r)

    def _wrap(self, result, r, R=None):
        """Wrap a raw Sage LaurentSeries into QSeries; T = Sage's actual precision."""
        from sage.all import Infinity, infinity
        T = int(result.prec()) if result.prec() != infinity else self.T
        return QSeries(result, T=T, r=r, R=R or self.R)

    def _align_shifts(self, other):
        """Return (s1, s2, r_out, T) with shifts aligned for addition/subtraction.

        Rules (from D-12):
          - r1 == r2: use common shift, no series adjustment needed.
          - r1 - r2 is an integer k: multiply the series with the larger r by q^k
            to bring both to the smaller r; r_out = min(r1, r2).
          - otherwise: raise ValueError (Maple would return a symbolic sum — out of scope).
        """
        T = min(self.T, other.T)
        delta = self.r - other.r
        if delta == 0:
            return self.series.add_bigoh(T), other.series.add_bigoh(T), self.r, T
        from sage.all import ZZ
        if delta in ZZ:
            k = int(delta)
            q = self.series.parent().gen()
            if k > 0:
                # self.r > other.r: multiply self's series by q^k, use other.r
                return (self.series * q**k).add_bigoh(T), other.series.add_bigoh(T), other.r, T
            else:
                # other.r > self.r: multiply other's series by q^(-k), use self.r
                return self.series.add_bigoh(T), (other.series * q**(-k)).add_bigoh(T), self.r, T
        raise ValueError(
            f"Cannot add/subtract QSeries with incommensurable shifts r={self.r} and r={other.r}; "
            "shifts must agree or differ by an integer."
        )

    def __add__(self, other):
        if isinstance(other, QSeries):
            s1, s2, r_out, T = self._align_shifts(other)
            return self._wrap((s1 + s2).add_bigoh(T), r_out)
        return self._wrap((self.series + other).add_bigoh(self.T), self.r)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, QSeries):
            s1, s2, r_out, T = self._align_shifts(other)
            return self._wrap((s1 - s2).add_bigoh(T), r_out)
        return self._wrap((self.series - other).add_bigoh(self.T), self.r)

    def __rsub__(self, other):
        return self._wrap((other - self.series).add_bigoh(self.T), self.r)

    def __mul__(self, other):
        if isinstance(other, QSeries):
            T = min(self.T, other.T)
            result = (self.series.add_bigoh(T) * other.series.add_bigoh(T)).add_bigoh(T)
            return self._wrap(result, self.r + other.r)
        return self._wrap((self.series * other).add_bigoh(self.T), self.r)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __pow__(self, n):
        """Raise QSeries to an integer power (negative exponents use series inversion)."""
        if not isinstance(n, int):
            raise TypeError(f"QSeries ** n requires an integer exponent, got {n!r}")
        if n == 0:
            one = self.series.parent().one()
            return self._wrap(one.add_bigoh(self.T), QQ(0))
        if n > 0:
            result = self
            for _ in range(n - 1):
                result = result * self
            return result
        else:
            # Negative exponent: invert then raise to positive power
            inv_series = self.series.__invert__().add_bigoh(self.T)
            inv = self._wrap(inv_series, -self.r)
            result = inv
            for _ in range(-n - 1):
                result = result * inv
            return result

    def __truediv__(self, other):
        if isinstance(other, QSeries):
            T = min(self.T, other.T)
            result = (self.series.add_bigoh(T) / other.series.add_bigoh(T)).add_bigoh(T)
            return self._wrap(result, self.r - other.r)
        return self._wrap((self.series / other).add_bigoh(self.T), self.r)

    def __neg__(self):
        return QSeries(-self.series, T=self.T, r=self.r, R=self.R)

    def __repr__(self):
        if self.r != 0:
            return f"q^({self.r}) * {self.series}"
        return repr(self.series)

    def __eq__(self, other):
        if isinstance(other, QSeries):
            return self.series == other.series and self.T == other.T and self.r == other.r
        return self.series == other

    __hash__ = None  # unhashable by design: __eq__ defined without natural hash
