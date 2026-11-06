"""
tests/test_zqfactor.py — CONV-07: zqfactor (Phase 7).

Oracles:
  - zqfactor doc page (qseries.org/fgarvan/qmaple/qseries/functions/zqfactor.html):
    g = tripleprod(-z^2 q^3, q^4, 20) - tripleprod(-z^2 q, q^4, 20)/z;  zqfactor(g, z, q, 10) =
    (1-1/z)(1-zq)(1-q)(1-q/z)(1-zq^2)(1-q^2)(1-q^2/z)(1-zq^3)(1-q^3).
  - Mathematical identities (stated per test): Jacobi triple product, Euler's product
    (q;q)_inf, the product (-zq;q)_inf, and Phi_3(z) = (1 - z^3)/(1 - z).
"""
import warnings
import pytest
from sage.all import QQ, LaurentPolynomialRing, LaurentSeriesRing

from qseries._series import QSeries
from qseries._building_blocks import tripleprod, etaq
from qseries._zqfactor import zqfactor, ZQProduct


@pytest.fixture
def zq():
    Lz = LaurentPolynomialRing(QQ, 'z')
    z = Lz.gen()
    R = LaurentSeriesRing(Lz, 'q', default_prec=60)
    return z, R.gen()


def _doc_g(z, q):
    return tripleprod(-z**2 * q**3, q**4, 20) - tripleprod(-z**2 * q, q**4, 20) / z


def test_zqfactor_doc_example(zq):
    """Oracle: zqfactor doc page example, zqfactor(g, z, q, 10) -> nine factors in Maple's order."""
    z, q = zq
    result = zqfactor(_doc_g(z, q), z, q, 10)
    assert isinstance(result, ZQProduct)
    assert result.factors == [
        (1, -1, 0, 1),
        (1, 1, 1, 1), (1, 0, 1, 1), (1, -1, 1, 1),
        (1, 1, 2, 1), (1, 0, 2, 1), (1, -1, 2, 1),
        (1, 1, 3, 1), (1, 0, 3, 1),
    ]
    assert result.constant == 1 and result.zpow == 0 and result.qpow == 0
    assert repr(result) == ("(1 - 1/z) * (1 - z*q) * (1 - q) * (1 - q/z) * (1 - z*q^2) * "
                            "(1 - q^2) * (1 - q^2/z) * (1 - z*q^3) * (1 - q^3)")


def test_zqfactor_doc_example_round_trip(zq):
    """Oracle: Jacobi triple product -- g = (1/z;q)_inf (zq;q)_inf (q;q)_inf, so expanding the
    returned product reproduces g to O(q^40)."""
    z, q = zq
    g = _doc_g(z, q)
    result = zqfactor(g, z, q, 200)
    assert all(e == 1 and a == 1 for a, i, j, e in result.factors)
    expanded = result.to_series(40, z)
    assert expanded.series == g.series.add_bigoh(40)


def test_zqfactor_euler_product(zq):
    """Oracle: Euler -- etaq(q,1,T) = prod (1 - q^n); with no z the factors are (1 - q^n)."""
    z, q = zq
    f = etaq(q, 1, 30)
    result = zqfactor(f, z, q)
    assert result.factors == [(1, 0, n, 1) for n in range(1, 30)]


def test_zqfactor_plus_factors(zq):
    """Oracle: (-zq;q)_inf = prod (1 + z q^n) -- returned as (1 + z q^n), not as (1 - z q^n)^-1 (1 - z^2 q^2n)."""
    z, q = zq
    T = 20
    s = q.parent()(1).add_bigoh(T)
    for n in range(1, T):
        s = (s * (1 + z * q**n)).add_bigoh(T)
    result = zqfactor(QSeries(s, T), z, q, 9)
    assert result.factors[:8] == [(-1, 1, n, 1) for n in range(1, 9)]
    assert "(1 + z*q)" in repr(result)


def test_zqfactor_cyclotomic_q0(zq):
    """Oracle: Phi_3(z) = 1 + z + z^2 = (1 - z^3)/(1 - z); times (1 - q)."""
    z, q = zq
    f = QSeries(((1 + z + z**2) * (1 - q)).add_bigoh(20), 20)
    result = zqfactor(f, z, q)
    assert (1, 3, 0, 1) in result.factors and (1, 1, 0, -1) in result.factors
    assert (1, 0, 1, 1) in result.factors


def test_zqfactor_monomial_prefactor(zq):
    """Oracle: q^2 * z * (1 - q) -> prefactor z * q^2 and the single factor (1 - q)."""
    z, q = zq
    f = QSeries((z * q**2 * (1 - q)).add_bigoh(20), 20)
    result = zqfactor(f, z, q)
    assert (result.zpow, result.qpow, result.constant) == (1, 2, 1)
    assert result.factors == [(1, 0, 1, 1)]


def test_zqfactor_fails_gracefully(zq):
    """Oracle: doc page -- 'at times it will fail'. 1 + z + 2z^2 is irreducible and not cyclotomic,
    so no (1 - a z^i) factorisation exists: warn and return None (design decision)."""
    z, q = zq
    f = QSeries(((1 + z + 2 * z**2) * (1 - q)).add_bigoh(20), 20)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert zqfactor(f, z, q) is None
    assert any(issubclass(w.category, UserWarning) for w in caught)


def test_zqfactor_type_error():
    """Design decision: input must be a QSeries.

    Oracle: Design decision (Phase 7): input must be a QSeries.
    """
    with pytest.raises(TypeError):
        zqfactor(None, None, None, 10)
