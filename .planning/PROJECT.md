# qseries-sage

## What This Is

A function-for-function port of Frank Garvan's Maple **qseries** package (v1.3, 2016) to Python on SageMath. Same function names, argument order, and semantics, so tutorial and doc-page examples run unchanged apart from syntax. No Maple required.

## Core Value

Do everything the Maple qseries package does — build q-series, convert to eta/theta/infinite products, find linear/homogeneous/polynomial relations, hunt congruences — in a free environment installable on HiPerGator, with results matching Maple's on the reference examples.

## Requirements

### Validated

**Series foundation** — Validated in Phase 01: foundation
- [x] One internal truncated q-series representation on Sage `PowerSeriesRing`/`LaurentSeriesRing` over `QQ` (and `GF(p)` for mod-p functions), truncation order propagated through arithmetic.
- [x] Printable, series-convertible output types for eta-products (`eta(k*tau)` factors with rational q-power prefactor) and Jacobi products (`JAC(a,b,infinity)`).
- [x] Degree/lowest-degree/coefficient conventions matching Maple on Laurent polynomials in q.

### Active

**Function parity — all 41 public functions of qseries 1.3**

*Validated in Phase 02: building-blocks-utilities* — all building-block and series-utility functions implemented, exported, and tested:
- Building blocks: `aqprod`, `qbin`, `etaq`, `jacprod`, `theta`, `theta2`, `theta3`, `theta4`, `tripleprod`, `quinprod`, `winquist` ✓
- Series utilities: `sift`, `qdegree`, `lqdegree`, `lqdegree0`, `checkmult`, `checkprod`, `packageversion`, `changes` ✓
- Product conversion: `prodmake`, `etamake`, `qetamake`, `jacprodmake`, `mprodmake`, `qfactor`, `zqfactor`, `jac2prod`, `jac2series`, `qs2jaccombo`, `findprod`
- Relation finding: `findhom`, `findhomcombo`, `findhommodp`, `findhomcombomodp`, `findnonhom`, `findnonhomcombo`, `findlincombo`, `findlincombomodp`, `findmaxind`, `findpoly`, `findcong`
- [ ] Each signature, optional argument, and return shape documented against its Maple doc page; divergences listed.
- [ ] Each function has ≥1 test reproducing a documented example, expected value taken from the Maple docs.

**Packaging**
- [ ] `sage -pip install .`; `from qseries import *`.
- [ ] Runs on HiPerGator's Sage (no root) and a current stock SageMath release.
- [ ] Sage-kernel Jupyter tutorial mirroring the Maple tutorial's sections.

### Out of Scope

- Related packages (ETA, thetaids, ramarobinsids, rank, crank, sptcrank, tcore) — later milestones.
- Identity proving (thetaids territory).
- Maple-syntax compatibility layer or worksheet importer.
- Performance work (Cython, parallelism) beyond interactive-speed tutorial examples.
- Pure-SymPy fallback — rejected (see Key Decisions).

## Context

- Reference: `https://qseries.org/fgarvan/qmaple/qseries/` (function index, per-function docs, `qseriesdoc.pdf` tutorial, Maple source). v1.3 dated 2016-08-12.
- No Maple available: documented outputs are the test oracle; undocumented cases are cross-checked by identity verification to high order.
- Relation finders are exact linear algebra over `QQ` (nullspace of a monomial coefficient matrix). Maple's ordering of returned relations may differ — test up to equivalence.
- `prodmake`/`etamake`/`jacprodmake` implement Andrews' algorithm; highest value and risk. Build `prodmake` first, layer the rest on it.
- Sage already has `q_binomial`, `q_pochhammer`, `qexp_eta`, `sage.modular.etaproducts` — wrap or reimplement, but keep qseries' public names and argument order.

## Constraints

- **Runtime:** SageMath (Python 3) plus pure-Python PyPI packages only.
- **Interface fidelity:** Names and argument order match qseries 1.3; unavoidable divergences chosen once, documented, applied consistently.
- **Testing:** `pytest` under `sage -python`; every function has a test traceable to a documented example.
- **Licensing:** Garvan's source and docs are his copyright; porting approach and attribution settled before code is written.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python on SageMath, not SymPy | Exact series rings, exact linear algebra, eta/theta primitives built in. | ✓ Decided |
| Full 41-function port in v1.0 | Partial ports leave the tutorial only partly runnable. | ✓ Decided |
| Oracle = Maple doc examples + identity checks | No Maple available. | ✓ Decided |
| Explicit `T` truncation argument, mirroring Maple `(f, q, T)` | Keeps call sites identical; no hidden global precision. | ✓ Decided |
| Lightweight `EtaProduct`/`JacProduct` classes, not Sage symbolic ring | Printable like Maple, convertible, cheap to test. | ✓ Decided |
| Porting method: source translation vs. clean reimplementation | Depends on licensing check. Blocks Phase 1. | — Pending |
| Package name: `qseries` vs. `qseries_sage` | Decide before packaging phase. | — Pending |

## Evolution

Updated at phase transitions (`/gsd:transition`): move validated/invalidated requirements, log decisions, check "What This Is". Full review at `/gsd:complete-milestone`.

---
## Current State

Phase 01 (foundation) complete — package scaffold, QSeries wrapper, five symbolic output classes, three degree functions, and pytest scaffold are in place. Next: Phase 02 (building-blocks-&-utilities).

---
*Last updated: 2026-09-17 after Phase 01 completion*
