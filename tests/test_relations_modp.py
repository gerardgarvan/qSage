"""
tests/test_relations_modp.py
Tests for the Phase 6 mod-p relation finders: findhommodp, findhomcombomodp, findlincombomodp.

Oracles:
  - findlincombomodp doc page (qseries.org/fgarvan/qmaple/functions/findlincombomodp.html):
    findlincombomodp(F1, BB13, SBB13, 13, q, -8) prints 'nx = , 6' and '# of terms , 19'
    and returns -6 * _ETA1^11 _E6 _E4 (the j = 0 basis element).
  - Eisenstein congruences: E4 = 1 + 240 sum sigma_3(n) q^n and 240 = 2^4 * 3 * 5, so
    E4 = 1 (mod 5); E6 = 1 - 504 sum sigma_5(n) q^n and 504 = 2^3 * 3^2 * 7, so E6 = 1 (mod 7).
Expected values never come from this package's own output.
"""
import pytest
from sage.all import QQ, GF, LaurentSeriesRing, PolynomialRing, sigma

from qseries._series import QSeries
from qseries._building_blocks import etaq
from qseries._utilities import sift
from qseries._relations import (
    findhom, findhommodp, findhomcombomodp, findlincombomodp,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_q(T):
    R = LaurentSeriesRing(QQ, 'q', default_prec=T + 10)
    return R, R.gen()


def eisenstein(R, k, c, T):
    """1 + c * sum_{n<T} sigma_{k-1}(n) q^n  (E4: k=4, c=240; E6: k=6, c=-504)."""
    q = R.gen()
    return QSeries(R(1 + c * sum(sigma(n, k - 1) * q**n for n in range(1, T))).add_bigoh(T), T)


@pytest.fixture(scope="module")
def doc_example():
    """The findlincombomodp doc-page setup (T = 300)."""
    T = 300
    R, q = make_q(T)
    E4 = eisenstein(R, 4, 240, T)
    E6 = eisenstein(R, 6, -504, T)
    ETA1 = etaq(q, 1, T)
    P = QSeries(ETA1.series.__invert__(), T)
    F1 = sift(E4**16 * E6 * P, q, 13, 6, 299)
    BB13 = [ETA1**11 * E6 * E4**(3 * j + 1) for j in range(6)]
    return q, F1, BB13


@pytest.fixture(scope="module")
def e4_e6():
    T = 60
    R, q = make_q(T)
    one = QSeries(R(1).add_bigoh(T), T)
    return q, eisenstein(R, 4, 240, T), eisenstein(R, 6, -504, T), one


# ---------------------------------------------------------------------------
# REL-08: findlincombomodp
# ---------------------------------------------------------------------------

def test_findlincombomodp_doc_example(doc_example, capsys):
    """Doc page: F1 = -6 * BB13[1] (mod 13); prints 'nx = , 6' and '# of terms , 19'."""
    q, F1, BB13 = doc_example
    SBB13 = ['_ETA1^11*_E6*_E4^%d' % (3 * j + 1) for j in range(6)]
    result = findlincombomodp(F1, BB13, SBB13, 13, q, -8)
    out = capsys.readouterr().out
    assert "nx = , 6" in out
    assert "# of terms , 19" in out
    R = PolynomialRing(GF(13), ['X%d' % i for i in range(1, 7)])
    assert result == {-6 * R.gen(0)}, result


def test_findlincombomodp_not_a_combo(e4_e6, capsys):
    """E6 is not a multiple of E4 mod 13 (240 and 504 are units mod 13)."""
    q, E4, E6, one = e4_e6
    result = findlincombomodp(E6, [E4], ['E4'], 13, q, 0)
    assert result == set()
    assert "%NOT A LINEAR COMBO.%" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# REL-04: findhomcombomodp
# ---------------------------------------------------------------------------

def test_findhomcombomodp_degree1_matches_doc(doc_example, capsys):
    """Degree 1 homogeneous combo = linear combo: same -6*X1 mod 13, same 19 terms (7 rows, C=20, topshift -8)."""
    q, F1, BB13 = doc_example
    result = findhomcombomodp(F1, BB13, 13, q, 1, -8)
    assert "# of terms , 19" in capsys.readouterr().out
    R = PolynomialRing(GF(13), ['X%d' % i for i in range(1, 7)])
    assert result == {-6 * R.gen(0)}, result


def test_findhomcombomodp_uses_congruence(e4_e6):
    """E6 = E6 * 1 = E6 * E4 (mod 5) since E4 = 1 (mod 5): E6 is the degree-2 form X1*X2 in [E4, E6] mod 5."""
    q, E4, E6, one = e4_e6
    result = findhomcombomodp(E6, [E4, E6], 5, q, 2, 0)
    R = PolynomialRing(GF(5), ['X1', 'X2'])
    X1, X2 = R.gens()
    assert X1 * X2 in result, result


# ---------------------------------------------------------------------------
# REL-03: findhommodp
# ---------------------------------------------------------------------------

def test_findhommodp_e4_congruent_one_mod5(e4_e6):
    """E4 = 1 (mod 5): findhommodp([E4, E6, 1], 5, q, 1) = {X1 - X3}; no such relation over QQ."""
    q, E4, E6, one = e4_e6
    L = [E4, E6, one]
    R = PolynomialRing(GF(5), ['X1', 'X2', 'X3'])
    X1, X2, X3 = R.gens()
    result = findhommodp(L, 5, q, 1, 0)
    assert len(result) == 1 and all(p * (X1 - X3).lc() == (X1 - X3) * p.lc() for p in result), result
    assert findhom(L, q, 1, 0) == set()


def test_findhommodp_e6_congruent_one_mod7(e4_e6):
    """E6 = 1 (mod 7): the relation is X2 - X3."""
    q, E4, E6, one = e4_e6
    R = PolynomialRing(GF(7), ['X1', 'X2', 'X3'])
    X1, X2, X3 = R.gens()
    result = findhommodp([E4, E6, one], 7, q, 1)
    assert len(result) == 1 and all(p * (X2 - X3).lc() == (X2 - X3) * p.lc() for p in result), result


def test_findhommodp_none_mod13(e4_e6):
    """240 and 504 are units mod 13, so E4, E6, 1 stay independent mod 13."""
    q, E4, E6, one = e4_e6
    assert findhommodp([E4, E6, one], 13, q, 1, 0) == set()


def test_findhommodp_returns_gf_p_polynomials(e4_e6):
    q, E4, E6, one = e4_e6
    for poly in findhommodp([E4, one], 5, q, 1):
        assert poly.parent().base_ring() == GF(5)


# ---------------------------------------------------------------------------
# Non-prime p: ValueError before any computation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_p", [1, 12, 0, -7, 'x'])
def test_nonprime_p_raises(e4_e6, capsys, bad_p):
    q, E4, E6, one = e4_e6
    with pytest.raises(ValueError, match="prime"):
        findhommodp([E4, E6], bad_p, q, 1)
    with pytest.raises(ValueError, match="prime"):
        findhomcombomodp(E6, [E4], bad_p, q, 1)
    with pytest.raises(ValueError, match="prime"):
        findlincombomodp(E6, [E4], ['E4'], bad_p, q)
    assert "# of terms" not in capsys.readouterr().out, "computation started before the prime check"
