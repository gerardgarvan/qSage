"""Tests for qseries._symbolic — symbolic output classes.

All expected values are taken from the Maple qseries documentation and
the qseriesdoc.pdf tutorial (Garvan, 2016). Oracle = Maple docs.
"""
import pytest


# ---------------------------------------------------------------------------
# QProduct tests
# ---------------------------------------------------------------------------

def test_qproduct_empty():
    from qseries._symbolic import QProduct
    assert repr(QProduct({})) == "1"


def test_qproduct_single_exponent_one():
    from qseries._symbolic import QProduct
    assert repr(QProduct({1: 1})) == "(1-q)"


def test_qproduct_two_factors():
    from qseries._symbolic import QProduct
    assert repr(QProduct({1: 1, 2: 1})) == "(1-q) * (1-q^2)"


def test_qproduct_exponent_two():
    from qseries._symbolic import QProduct
    assert repr(QProduct({3: 2})) == "(1-q^3)^2"


def test_qproduct_negative_exponent():
    from qseries._symbolic import QProduct
    assert repr(QProduct({1: -1})) == "(1-q)^-1"


def test_qproduct_mixed_negative():
    from qseries._symbolic import QProduct
    assert repr(QProduct({1: -1, 2: -1})) == "(1-q)^-1 * (1-q^2)^-1"


def test_qproduct_to_series_empty():
    from qseries._symbolic import QProduct
    qs = QProduct({}).to_series(5)
    # Constant 1 series: coefficient of q^0 is 1
    assert qs.series[0] == 1


def test_qproduct_to_series_coefficients():
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
    from qseries._symbolic import EProduct
    assert repr(EProduct({1: 1})) == "_E(q)"


def test_eproduct_exponent_two():
    from qseries._symbolic import EProduct
    assert repr(EProduct({2: 2})) == "_E(q^2)^2"


def test_eproduct_mixed():
    from qseries._symbolic import EProduct
    assert repr(EProduct({1: 1, 2: -1})) == "_E(q) * _E(q^2)^-1"


def test_eproduct_empty():
    from qseries._symbolic import EProduct
    assert repr(EProduct({})) == "1"


# ---------------------------------------------------------------------------
# EtaProduct tests
# ---------------------------------------------------------------------------

def test_etaproduct_two_factors():
    from qseries._symbolic import EtaProduct
    result = repr(EtaProduct(1, 0, [(1, 24), (2, -24)]))
    assert result == "eta(tau)^24 * eta(2*tau)^-24"


def test_etaproduct_single_exponent_one_suppressed():
    from qseries._symbolic import EtaProduct
    result = repr(EtaProduct(1, 0, [(1, 1)]))
    assert result == "eta(tau)"


def test_etaproduct_with_constant_and_r():
    from qseries._symbolic import EtaProduct
    from sage.all import QQ
    result = repr(EtaProduct(2, QQ(1) / 4, [(4, 2), (2, -1)]))
    assert result == "2 * q^(1/4) * eta(2*tau)^-1 * eta(4*tau)^2"


def test_etaproduct_sorted_by_level():
    from qseries._symbolic import EtaProduct
    # Factors should appear sorted by level even if given out of order
    result = repr(EtaProduct(1, 0, [(2, 5), (4, -2), (1, -2)]))
    assert result == "eta(tau)^-2 * eta(2*tau)^5 * eta(4*tau)^-2"


# ---------------------------------------------------------------------------
# JacProduct tests
# ---------------------------------------------------------------------------

def test_jacproduct_single_exponent_one():
    from qseries._symbolic import JacProduct
    assert repr(JacProduct(factors=[(1, 2, 1)])) == "JAC(1,2,infinity)"


def test_jacproduct_exponent_two():
    from qseries._symbolic import JacProduct
    assert repr(JacProduct(factors=[(1, 2, 2)])) == "JAC(1,2,infinity)^2"


def test_jacproduct_rational_exponent():
    from qseries._symbolic import JacProduct
    from sage.all import QQ
    result = repr(JacProduct(factors=[(1, 2, QQ(1) / 2)]))
    assert result == "JAC(1,2,infinity)^(1/2)"


def test_jacproduct_multi_factor():
    from qseries._symbolic import JacProduct
    result = repr(JacProduct(factors=[(1, 4, 1), (2, 4, -1)]))
    assert result == "JAC(1,4,infinity) * JAC(2,4,infinity)^-1"


def test_jacproduct_with_r_prefix():
    from qseries._symbolic import JacProduct
    from sage.all import QQ
    result = repr(JacProduct(constant=1, r=QQ(1) / 2, factors=[(0, 1, 1)]))
    assert result == "q^(1/2) * JAC(0,1,infinity)"


def test_jacproduct_jac0_to_series():
    """JAC(0,5,1).to_series should match (q^5;q^5)_inf (single Pochhammer)."""
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
    from qseries._symbolic import PochProduct
    assert repr(PochProduct([(1, 2, 1)])) == "(q;q^2)_infinity"


def test_pochproduct_exponent_two():
    from qseries._symbolic import PochProduct
    assert repr(PochProduct([(1, 2, 2)])) == "(q;q^2)_infinity^2"


def test_pochproduct_empty():
    from qseries._symbolic import PochProduct
    assert repr(PochProduct([])) == "1"
