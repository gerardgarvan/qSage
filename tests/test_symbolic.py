"""Tests for qseries._symbolic — symbolic output classes.

All expected values are taken from the Maple qseries documentation and
the qseriesdoc.pdf tutorial (Garvan, 2016). Oracle = Maple docs.
"""
import pytest


# ---------------------------------------------------------------------------
# QProduct tests
# ---------------------------------------------------------------------------

def test_qproduct_empty():
    """Oracle: The empty product is 1; display format (Phase 1, FOUND-03/04)."""
    from qseries._symbolic import QProduct
    assert repr(QProduct({})) == "1"


def test_qproduct_single_exponent_one():
    """Oracle: Product notation (1-q^n) as printed on the prodmake doc page; exponent 1 suppressed (FOUND-04)."""
    from qseries._symbolic import QProduct
    assert repr(QProduct({1: 1})) == "(1-q)"


def test_qproduct_two_factors():
    """Oracle: Product notation (1-q^n) as on the prodmake doc page; factors joined by ' * ' (FOUND-04)."""
    from qseries._symbolic import QProduct
    assert repr(QProduct({1: 1, 2: 1})) == "(1-q) * (1-q^2)"


def test_qproduct_exponent_two():
    """Oracle: Product notation as on the prodmake doc page; exponent written ^e (FOUND-04)."""
    from qseries._symbolic import QProduct
    assert repr(QProduct({3: 2})) == "(1-q^3)^2"


def test_qproduct_negative_exponent():
    """Oracle: Product notation as on the prodmake doc page; negative exponent written ^-e (FOUND-04)."""
    from qseries._symbolic import QProduct
    assert repr(QProduct({1: -1})) == "(1-q)^-1"


def test_qproduct_mixed_negative():
    """Oracle: Product notation as on the prodmake doc page; negative exponents, ' * ' join (FOUND-04)."""
    from qseries._symbolic import QProduct
    assert repr(QProduct({1: -1, 2: -1})) == "(1-q)^-1 * (1-q^2)^-1"


def test_qproduct_to_series_empty():
    """Oracle: The empty product expands to 1."""
    from qseries._symbolic import QProduct
    qs = QProduct({}).to_series(5)
    # Constant 1 series: coefficient of q^0 is 1
    assert qs.series[0] == 1


def test_qproduct_to_series_coefficients():
    """Oracle: Direct expansion: (1-q)(1-q^2) = 1 - q - q^2 + q^3."""
    from qseries._symbolic import QProduct
    # (1-q)(1-q^2) = 1 - q - q^2 + q^3
    qs = QProduct({1: 1, 2: 1}).to_series(8)
    assert qs.series[1] == -1
    assert qs.series[2] == -1
    assert qs.series[3] == 1  # cross term


# ---------------------------------------------------------------------------
# EProduct tests
# ---------------------------------------------------------------------------

def test_eproduct_single():
    """Oracle: _E(q) = (q;q)_inf notation of the qetamake doc page."""
    from qseries._symbolic import EProduct
    assert repr(EProduct({1: 1})) == "_E(q)"


def test_eproduct_exponent_two():
    """Oracle: _E(q^m) notation of the qetamake doc page; exponent written ^e (FOUND-04)."""
    from qseries._symbolic import EProduct
    assert repr(EProduct({2: 2})) == "_E(q^2)^2"


def test_eproduct_mixed():
    """Oracle: _E(q^m) notation of the qetamake doc page; ' * ' join, ^-1 (FOUND-04)."""
    from qseries._symbolic import EProduct
    assert repr(EProduct({1: 1, 2: -1})) == "_E(q) * _E(q^2)^-1"


def test_eproduct_empty():
    """Oracle: The empty product is 1; display format (FOUND-04)."""
    from qseries._symbolic import EProduct
    assert repr(EProduct({})) == "1"


# ---------------------------------------------------------------------------
# EtaProduct tests
# ---------------------------------------------------------------------------

def test_etaproduct_two_factors():
    """Oracle: eta(m*tau) notation of the etamake doc page; exponents written ^e (FOUND-04)."""
    from qseries._symbolic import EtaProduct
    result = repr(EtaProduct(1, 0, [(1, 24), (2, -24)]))
    assert result == "eta(tau)^24 * eta(2*tau)^-24"


def test_etaproduct_single_exponent_one_suppressed():
    """Oracle: eta(tau) notation of the etamake doc page; exponent 1 suppressed (FOUND-04)."""
    from qseries._symbolic import EtaProduct
    result = repr(EtaProduct(1, 0, [(1, 1)]))
    assert result == "eta(tau)"


def test_etaproduct_with_constant_and_r():
    """Oracle: etamake doc page form: constant * q^r * eta-quotient (e.g. theta2 = 2 q^(1/4) eta(4 tau)^2 / eta(2 tau))."""
    from qseries._symbolic import EtaProduct
    from sage.all import QQ
    result = repr(EtaProduct(2, QQ(1) / 4, [(4, 2), (2, -1)]))
    assert result == "2 * q^(1/4) * eta(2*tau)^-1 * eta(4*tau)^2"


def test_etaproduct_sorted_by_level():
    """Oracle: eta(m*tau) notation of the etamake doc page, factors ordered by level m (FOUND-04)."""
    from qseries._symbolic import EtaProduct
    # Factors should appear sorted by level even if given out of order
    result = repr(EtaProduct(1, 0, [(2, 5), (4, -2), (1, -2)]))
    assert result == "eta(tau)^-2 * eta(2*tau)^5 * eta(4*tau)^-2"


# ---------------------------------------------------------------------------
# JacProduct tests
# ---------------------------------------------------------------------------

def test_jacproduct_single_exponent_one():
    """Oracle: JAC(a,b,infinity) notation of the jacprodmake doc page; exponent 1 suppressed (FOUND-04)."""
    from qseries._symbolic import JacProduct
    assert repr(JacProduct(factors=[(1, 2, 1)])) == "JAC(1,2,infinity)"


def test_jacproduct_exponent_two():
    """Oracle: JAC(a,b,infinity) notation of the jacprodmake doc page; exponent written ^e."""
    from qseries._symbolic import JacProduct
    assert repr(JacProduct(factors=[(1, 2, 2)])) == "JAC(1,2,infinity)^2"


def test_jacproduct_rational_exponent():
    """Oracle: JAC(a,b,infinity)^(1/2) as in the jacprodmake doc page / tutorial sqrt example (D-08)."""
    from qseries._symbolic import JacProduct
    from sage.all import QQ
    result = repr(JacProduct(factors=[(1, 2, QQ(1) / 2)]))
    assert result == "JAC(1,2,infinity)^(1/2)"


def test_jacproduct_multi_factor():
    """Oracle: JAC(a,b,infinity) notation of the jacprodmake doc page; ' * ' join, ^-1."""
    from qseries._symbolic import JacProduct
    result = repr(JacProduct(factors=[(1, 4, 1), (2, 4, -1)]))
    assert result == "JAC(1,4,infinity) * JAC(2,4,infinity)^-1"


def test_jacproduct_with_r_prefix():
    """Oracle: jacprodmake doc page form q^r * JAC(...) (lqdegree0 doc page examples use sqrt(q)*JAC)."""
    from qseries._symbolic import JacProduct
    from sage.all import QQ
    result = repr(JacProduct(constant=1, r=QQ(1) / 2, factors=[(0, 1, 1)]))
    assert result == "q^(1/2) * JAC(0,1,infinity)"


def test_jacproduct_jac0_to_series():
    """JAC(0,5,1).to_series should match (q^5;q^5)_inf (single Pochhammer).

    Oracle: jac2prod doc page: JAC(0,b,inf) = (q^b;q^b)_inf; Euler: coefficient of q^5 in (q^5;q^5)_inf is -1.
    """
    from qseries._symbolic import JacProduct
    T = 20
    qs = JacProduct(factors=[(0, 5, 1)]).to_series(T)
    # (q^5;q^5)_inf = prod_{n>=1}(1-q^{5n})
    # Coefficient of q^5 should be -1, q^10 should be -1+1=0... actually
    # (q^5;q^5)_inf = 1 - q^5 - q^10 + q^15 + ... (Euler's pentagonal)
    # Just verify coefficient of q^5 is -1 (first nontrivial)
    assert qs.series[5] == -1


# ---------------------------------------------------------------------------
# PochProduct tests
# ---------------------------------------------------------------------------

def test_pochproduct_single():
    """Oracle: (a;q)_infinity notation of the jac2prod doc page."""
    from qseries._symbolic import PochProduct
    assert repr(PochProduct([(1, 2, 1)])) == "(q;q^2)_infinity"


def test_pochproduct_exponent_two():
    """Oracle: (a;q)_infinity notation of the jac2prod doc page; exponent written ^e."""
    from qseries._symbolic import PochProduct
    assert repr(PochProduct([(1, 2, 2)])) == "(q;q^2)_infinity^2"


def test_pochproduct_empty():
    """Oracle: The empty product is 1; display format (FOUND-04)."""
    from qseries._symbolic import PochProduct
    assert repr(PochProduct([])) == "1"
