# Phase 5: Relation Finding (Exact) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-17
**Phase:** 05-relation-finding-exact
**Areas discussed:** Phase merge, Argument signatures, Matrix/nullspace strategy, topshift semantics, findcong implementation

---

## Phase Merge (Phase 6 → Phase 5)

| Option | Description | Selected |
|--------|-------------|----------|
| Merge — implement all 11 functions in Phase 5 | Mod-p variants are same algorithm with GF(p) ring | ✓ |
| Keep separate — Phase 5 = QQ, Phase 6 = GF(p) | Cleaner phase boundaries | |

**User's choice:** Merge
**Notes:** Mod-p variants share the same matrix/nullspace code path. Merging eliminates Phase 6 entirely.

---

## Argument Signatures for Unknowns (REL-07/09/11)

| Option | Description | Selected |
|--------|-------------|----------|
| Researcher reads Garvan doc pages | WebFetch the qseries doc pages for the three [?] functions | ✓ |
| Describe signatures now | Lock signatures from tutorial PDF knowledge | |

**User's choice:** Researcher reads Garvan doc pages
**Notes:** findcong's optional 3rd argument is also unknown — researcher resolves both.

---

## Matrix/Nullspace Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| matrix(QQ, rows).right_kernel() | Sage exact rational nullspace | ✓ |
| matrix.LLL() / lattice reduction | For large-integer coefficients | |
| Claude's discretion | Researcher/planner decides | |

**Nullspace primitive:** `matrix(QQ, rows).right_kernel()` (GF(p) for mod-p variants)

| Matrix orientation | Description | Selected |
|---|---|---|
| Monomials as columns, series as rows | Standard Macaulay matrix | ✓ |
| Series coefficients as columns, monomials as rows | Transpose | |
| Claude's discretion | Researcher picks | |

**Empty result:** Return `[]` (empty list), not `None`.

---

## topshift Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Trim top topshift rows from coefficient matrix | Suppresses leading-term truncation artefacts | ✓ |
| Describe exact semantics | User provides | |
| Researcher reads doc + finds example | Open question | |

**User's choice:** Trim top rows (recommended)
**Notes:** Tutorial §5 uses topshift=0. Researcher must find a topshift>0 example to validate direction.

---

## findcong Implementation

| Option | Description | Selected |
|--------|-------------|----------|
| Sift-and-check over (A,B,M) triples | Direct translation of tutorial §7 | ✓ |
| Algebraic approach in graded ring | More sophisticated | |
| Claude's discretion | Researcher reads algorithm | |

**Search bounds:** A ≤ T, B < A, M prime — exact upper bounds from doc page + oracle.
**Oracle:** `findcong(1/etaq(q,1,1001), 1000)` → `{[4,5,5],[5,7,7],[6,11,11],[24,25,25]}`

---

## Claude's Discretion

- Monomial ordering within matrix (grlex vs lex) — match Maple output ordering
- findhomcombo `etaoption='yes'` return format — match tutorial §5 output
- Implementation file structure — planner's call

## Deferred Ideas

None.
