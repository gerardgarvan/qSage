---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 01
current_plan: 1
status: verifying
last_updated: "2026-09-16T23:58:08.038Z"
progress:
  total_phases: 7
  completed_phases: 1
  total_plans: 3
  completed_plans: 3
  percent: 0
---

# State: qseries-sage

## Project Reference

- **Project:** qseries-sage
- **Core value:** A researcher who knows the Maple qseries package can do the same work in a free, scriptable, HiPerGator-installable environment, with results that agree with Maple's on the reference examples.
- **PROJECT.md:** `.planning/PROJECT.md`
- **ROADMAP.md:** `.planning/ROADMAP.md`
- **REQUIREMENTS.md:** `.planning/REQUIREMENTS.md`

---

## Current Position

Phase: 01 (foundation) — EXECUTING
Plan: 3 of 3

- **Current phase:** 01
- **Current plan:** 1
- **Status:** Phase complete — ready for verification
- **Last updated:** 2026-09-16

```
Progress: [░░░░░░░░░░░░░░░░░░░░] 0% (0/7 phases complete)
```

---

## Phase Map

| Phase | Name | Status |
|-------|------|--------|
| 1 | Foundation | Not started |
| 2 | Building Blocks & Utilities | Not started |
| 3 | prodmake (Andrews' Algorithm) | Not started |
| 4 | Product Conversion | Not started |
| 5 | Relation Finding (Exact) | Not started |
| 6 | Relation Finding (Mod-p) | Not started |
| 7 | Packaging & Test Suite | Not started |

---

## Performance Metrics

- **Phases complete:** 0/7
- **Requirements addressed:** 0/28
- **Tests passing:** 0 (test suite not yet created)

---

## Accumulated Context

### Decisions Made

- Python on SageMath (not SymPy) — exact series rings and linear algebra built in.
- Full 41-function port in v1.0 — partial port leaves tutorial only partly runnable.
- Oracle = Maple doc examples + identity checks — no Maple available.
- Explicit `T` truncation argument, mirroring Maple `(f, q, T)` call sites.
- Lightweight `EtaProduct`/`JacProduct` dataclasses, not Sage symbolic ring.
- Granularity: standard (7 phases), overriding config.json coarse setting per roadmap instructions.
- [Phase 01]: QSeries uses LaurentSeriesRing with T=result.prec(), r as QQ rational shift, R inferred from series.parent().base_ring()
- [Phase 01-foundation]: D-06/D-07/D-08 applied: trivial exponent suppression and space-star-space join in all five symbolic class reprs
- [Phase 01-foundation]: Lazy import pattern in _symbolic.py to avoid parallel-wave import-order coupling
- [Phase 01-03]: qdegree uses .degree() not .dict() on LaurentSeries — .dict() is not guaranteed API
- [Phase 01-03]: lqdegree0 v1.0 scope: single monomials only; symbolic sums out of scope (D-15)

### Pending Decisions

- Licensing: contact Garvan before writing code; reimplement from docs or translate source. **Blocks Phase 1.**
- Package name: `qseries` vs. `qseries_sage`. Decide before Phase 7.

### Key Risks

- Andrews' algorithm (prodmake) is the highest-complexity item; Phase 3 is isolated for this reason.
- Fractional q-power prefixes in prodmake require careful handling.
- Test oracle discipline: expected values must come from Maple docs only, never from our own code.
- Relation ordering: test relation *sets*, not ordered lists — Sage's kernel basis differs from Maple's.
- GF(p) functions must assert prime p; use `GF(p)`, not `ZZ/pZZ`.

### Architecture Notes

```
_series.py          → QSeries wrapper (Phase 1)
_symbolic.py        → EtaProduct, JacProduct (Phase 1)
_building_blocks.py → 11 core functions (Phase 2)
_utilities.py       → 8 utility functions (Phase 2)
_prodmake.py        → Andrews' algorithm (Phase 3)
_conversion.py      → 10 product conversion functions (Phase 4)
_relations.py       → 11 relation finders: 9 exact (Phase 5) + 3 mod-p (Phase 6)
```

### Todos

- [ ] Resolve licensing before any code is written (Phase 1, plan 1)
- [ ] Test `sage -pip install --user .` early on target environment

### Blockers

- Licensing decision pending (not a code blocker yet — roadmap phase, no code written)

---

## Session Continuity

To resume: read `.planning/STATE.md` (this file), `.planning/ROADMAP.md`, and the current phase's plan file (`.planning/phases/phase-N.md` when created).
