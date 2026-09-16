"""Shared pytest fixtures for qseries-sage tests."""
import sys
import os
import pytest

# Insert project root so `qseries` package is importable without installing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sage.rings.rational_field import QQ
from sage.rings.laurent_series_ring import LaurentSeriesRing
from qseries._series import QSeries


@pytest.fixture
def q_ring():
    """Standard LaurentSeriesRing(QQ, 'q') for building test series."""
    return LaurentSeriesRing(QQ, 'q')


@pytest.fixture
def make_qs(q_ring):
    """Factory: make_qs(sage_series, T=20, r=0) -> QSeries."""
    def _make(series, T=20, r=0):
        return QSeries(series, T=T, r=r)
    return _make
