# Phase 1: Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-16
**Phase:** 01-foundation
**Areas discussed:** Licensing approach, QSeries ring selection, EtaProduct repr format, Degree function edge cases

---

## Licensing approach

| Option | Description | Selected |
|--------|-------------|----------|
| Proceed as clean reimplementation from docs only | No source translation — read only the qseries documentation and write all code from scratch. Garvan's docs are publicly available. Cite them in comments. Fast path, no waiting. | ✓ |
| Email Garvan for permission first | Contact Garvan before writing any code. Courteous, but adds unknown delay. | |
| Translate source but request permission in parallel | Start translating the Maple source while emailing Garvan. Risky if permission is denied. | |

**User's choice:** Clean reimplementation from docs only.

**Follow-up — where to record the decision:**

| Option | Description | Selected |
|--------|-------------|----------|
| Comment in _series.py | A block comment at the top of _series.py explaining the approach and citing the docs URL. | ✓ |
| Standalone LICENSING.md | A separate file in the repo root. | |
| Both | Brief note in _series.py pointing to a fuller LICENSING.md. | |

**User's choice:** Comment in `_series.py`.

---

## QSeries ring selection

| Option | Description | Selected |
|--------|-------------|----------|
| Always LaurentSeriesRing | Laurent series subsumes power series. One class, one ring. | ✓ |
| PowerSeries by default, Laurent on demand | Switches to Laurent ring when negative-degree operation requested. | |
| Two separate classes | QSeries and QLaurentSeries. More boilerplate, user must choose. | |

**User's choice:** Always LaurentSeriesRing.

**Follow-up — internal access pattern:**

| Option | Description | Selected |
|--------|-------------|----------|
| `.series` attribute | Internal modules access `self.series` for raw Sage operations. | ✓ |
| Delegate all arithmetic via dunder methods | No `.series` exposed; everything through operators. | |
| Claude's discretion | Let planner decide. | |

**User's choice:** `.series` attribute.

---

## EtaProduct repr format

| Option | Description | Selected |
|--------|-------------|----------|
| Suppress trivial parts | `e=1` → omit `^1`; `r=0` → omit `q^0` entirely. | ✓ |
| Always show all parts explicitly | `eta(k*tau)^1`, `q^0` always printed. | |
| Match Maple exactly from qseriesdoc.pdf | Character-for-character match. | |

**User's choice:** Suppress trivial parts.

**Follow-up — multi-factor separator:**

| Option | Description | Selected |
|--------|-------------|----------|
| ` * ` (space-star-space) | `eta(tau)^24 * eta(2*tau)^-24`. | ✓ |
| No separator (implicit multiplication) | `eta(tau)^24 eta(2*tau)^-24`. | |
| Claude's discretion | Match Maple's qseriesdoc.pdf output. | |

**User's choice:** ` * ` separator.

---

## Degree function edge cases

| Option | Description | Selected |
|--------|-------------|----------|
| Raise ValueError | `qdegree(0)` and `lqdegree(0)` raise `ValueError('zero series has no degree')`. | ✓ |
| Return -Infinity / +Infinity | Mathematical convention. | |
| Return None | Pythonic sentinel. | |

**User's choice:** Raise `ValueError`.

**Follow-up — lqdegree0 behavior:**

| Option | Description | Selected |
|--------|-------------|----------|
| lqdegree0 returns 0 for zero series | Safe variant; returns 0 instead of raising. Used inside relation finders. | ✓ |
| lqdegree0 returns +Infinity for zero | Mathematical total function. | |
| Same as lqdegree, just an alias | Collapse to one function. | |

**User's choice:** `lqdegree0` returns `0` for the zero series.

---

## Claude's Discretion

- Exact internal field names on EtaProduct/JacProduct dataclasses.
- Whether QSeries.__repr__ delegates to Sage's repr or custom-formats.
- Exact wording of the licensing comment in _series.py.

## Deferred Ideas

None.
