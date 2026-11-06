---
phase: 07-packaging-test-suite
plan: 01
status: complete
completed: 2026-11-05
requirements: [PKG-01, PKG-02, CONV-07]
files_modified: [setup.cfg, setup.py, pyproject.toml, README.md, .gitignore, qseries/_zqfactor.py, qseries/_conversion.py, qseries/__init__.py, qseries/_utilities.py, tests/test_zqfactor.py, tests/test_conversion.py, tests/*.py (oracle labels)]
---

# 07-01 Summary: packaging, zqfactor, oracle labels — milestone v1.0

## PKG-01: install

- `sage -pip install` on Ubuntu 22.04 (system pip 22.0.2) produced `UNKNOWN-0.0.0` with no files:
  that setup reads metadata with setuptools 59, which ignores the `[project]` table.
- Fix: metadata moved to `setup.cfg` (`version = attr: qseries.__version__`), a three-line
  `setup.py` shim, `pyproject.toml` keeps `[build-system]` and the pytest settings. Verified with
  Python 3.10 + pip 22.0.2 + setuptools 59.6 and with setuptools 80, and on the WSL Sage 9.5 box:
  `qseries_sage-1.3.0` installs, `from qseries import *` works, `packageversion()` = 1.3.0.
- Distribution `qseries-sage`, import name `qseries` (pending package-name question resolved).
- README.md added; `.gitignore` added (caches, build artefacts); 36 tracked `.pyc` files and an
  accidentally nested stale repo copy (`qSage/`, Phase 1 era) removed from git.
- No license chosen (owner's decision; Garvan's qseries is his copyrighted work).

## CONV-07: zqfactor (was a stub)

- `qseries/_zqfactor.py`: two-variable Andrews algorithm. The q^0 coefficient is factored over ZZ
  into binomials (orientation chosen so the left-over monomial is simplest) and cyclotomic
  polynomials; it is divided out exactly; factors (1 - z^i q^j)^e are read off order by order
  in q; (1 - x)^-1 (1 - x^2) is rewritten as (1 + x). Returns `ZQProduct` (Maple-style repr,
  `to_series`), or warns and returns None when no such product is found (the doc page notes
  Maple's version can fail too). `N` caps the result at N - 1 factors, which reproduces the
  doc-page example exactly.
- `_conversion.zqfactor` now re-exports it; the old stub test was replaced by
  `tests/test_zqfactor.py` (8 tests: doc example, triple-product round trip to O(q^40), Euler
  product, (-zq;q)_inf as (1 + z q^n), cyclotomic q^0, monomial prefactor, failure, type error).

## PKG-02: tests

- Audit: all 41 public functions have tests (144 tests).
- 81 tests had no stated source; each now has an `Oracle:` line naming the Maple doc page,
  tutorial section, identity, construction, or design decision its expected value rests on.

## Follow-ups (not blocking v1.0)

- `C:\qSage` and `~/qSage` have separate git histories; pick one as the source of truth
  (ideally with a GitHub remote).
