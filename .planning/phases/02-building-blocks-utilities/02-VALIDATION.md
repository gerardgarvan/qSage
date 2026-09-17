---
phase: 2
slug: building-blocks-utilities
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-09-16
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `pyproject.toml` (existing) |
| **Quick run command** | `sage -python -m pytest tests/test_building_blocks.py tests/test_utilities.py -x -q` |
| **Full suite command** | `sage -python -m pytest tests/ -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `sage -python -m pytest tests/test_building_blocks.py tests/test_utilities.py -x -q`
- **After every plan wave:** Run `sage -python -m pytest tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | BUILD-01 | unit | `sage -python -m pytest tests/test_building_blocks.py::test_aqprod -xq` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | BUILD-02 | unit | `sage -python -m pytest tests/test_building_blocks.py::test_qbin -xq` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | BUILD-03 | unit | `sage -python -m pytest tests/test_building_blocks.py::test_etaq -xq` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 1 | BUILD-04 | unit | `sage -python -m pytest tests/test_building_blocks.py::test_jacprod -xq` | ❌ W0 | ⬜ pending |
| 02-01-05 | 01 | 1 | BUILD-05 | unit | `sage -python -m pytest tests/test_building_blocks.py::test_theta -xq` | ❌ W0 | ⬜ pending |
| 02-01-06 | 01 | 1 | BUILD-06 | unit | `sage -python -m pytest tests/test_building_blocks.py::test_theta2 -xq` | ❌ W0 | ⬜ pending |
| 02-01-07 | 01 | 1 | BUILD-07 | unit | `sage -python -m pytest tests/test_building_blocks.py::test_theta3 -xq` | ❌ W0 | ⬜ pending |
| 02-01-08 | 01 | 1 | BUILD-08 | unit | `sage -python -m pytest tests/test_building_blocks.py::test_theta4 -xq` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | BUILD-09 | unit | `sage -python -m pytest tests/test_building_blocks.py::test_tripleprod -xq` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 2 | BUILD-10 | unit | `sage -python -m pytest tests/test_building_blocks.py::test_quinprod -xq` | ❌ W0 | ⬜ pending |
| 02-02-03 | 02 | 2 | BUILD-11 | unit | `sage -python -m pytest tests/test_building_blocks.py::test_winquist -xq` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 3 | UTIL-01 | unit | `sage -python -m pytest tests/test_utilities.py::test_sift -xq` | ❌ W0 | ⬜ pending |
| 02-03-02 | 03 | 3 | UTIL-02/03/04 | unit | `sage -python -m pytest tests/test_utilities.py::test_qdegree -xq` | ❌ W0 | ⬜ pending |
| 02-03-03 | 03 | 3 | UTIL-05 | unit | `sage -python -m pytest tests/test_utilities.py::test_checkmult -xq` | ❌ W0 | ⬜ pending |
| 02-03-04 | 03 | 3 | UTIL-06 | unit | `sage -python -m pytest tests/test_utilities.py::test_checkprod -xq` | ❌ W0 | ⬜ pending |
| 02-03-05 | 03 | 3 | UTIL-07/08 | unit | `sage -python -m pytest tests/test_utilities.py::test_packageinfo -xq` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_building_blocks.py` — stubs/skeletons for BUILD-01 through BUILD-11
- [ ] `tests/test_utilities.py` — stubs/skeletons for UTIL-01 through UTIL-08
- [ ] `qseries/_building_blocks.py` — module file (may be empty initially)

*Existing `tests/` infrastructure and `pytest` configuration from Phase 1 covers the framework.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `quinprod` identity string format readability | BUILD-10 | Output format is human-readable; exact string not specifiable without doc page | Run `quinprod(z, q, 'prodid')` and `quinprod(z, q, 'seriesid')` in Sage; confirm strings are non-empty and mathematically recognizable |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
