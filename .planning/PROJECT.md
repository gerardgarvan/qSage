# qseries-sage

## What This Is

A function-for-function port of Frank Garvan's Maple **qseries** package (version 1.3, 2016) to Python running on SageMath. Every public function in the Maple package gets a Sage counterpart with the same name, argument order, and semantics, so that worked examples from the qseries tutorial and per-function documentation pages run unchanged apart from syntax. The package lives as an importable Python module inside a Sage session; no Maple installation or license is needed at any point.

## Core Value

A researcher who knows the Maple qseries package can do the same work — build q-series, convert them to eta/theta/infinite products, find linear, homogeneous, and polynomial relations, and hunt congruences — in a free, scriptable, HiPerGator-installable environment, with results that agree with Maple's on the reference examples.

## Requirements

### Validated

(None yet — v1.0 not started)

### Active

**Series foundation**
- [ ] A single internal representation for truncated q-series with a declared truncation order, built on Sage's `PowerSeriesRing` / `LaurentSeriesRing` over `QQ` (and `GF(p)` for mod-p functions), with arithmetic that propagates truncation order correctly.
- [ ] Symbolic-output types for the "make" functions: eta-products written as `eta(k*tau)` factors with a rational power of q in front, and Jacobi-type products written as `JAC(a,b,infinity)`, both printable and convertible back to series.
- [ ] Conventions (lowest-degree, degree, coefficient extraction) that match Maple's on Laurent polynomials in q.

**Function parity — all 41 public functions of qseries 1.3**

*Building blocks:* `aqprod`, `qbin`, `etaq`, `jacprod`, `theta`, `theta2`, `theta3`, `theta4`, `tripleprod`, `quinprod`, `winquist`

*Series utilities:* `sift`, `qdegree`, `lqdegree`, `lqdegree0`, `checkmult`, `checkprod`, `packageversion`, `changes`

*Product conversion:* `prodmake`, `etamake`, `qetamake`, `jacprodmake`, `mprodmake`, `qfactor`, `zqfactor`, `jac2prod`, `jac2series`, `qs2jaccombo`, `findprod`

*Relation finding:* `findhom`, `findhomcombo`, `findhommodp`, `findhomcombomodp`, `findnonhom`, `findnonhomcombo`, `findlincombo`, `findlincombomodp`, `findmaxind`, `findpoly`, `findcong`

- [ ] Each function's argument signature, optional arguments (e.g. `topshift`, `etaoption`), and return shape documented against its Maple doc page, with divergences listed explicitly.
- [ ] Every function has at least one test reproducing an example from the tutorial or its doc page, with expected output taken from the Maple documentation.

**Packaging**
- [ ] Installable with `sage -pip install .` (and plain `pip` inside a Sage venv); importable as `from qseries import *`.
- [ ] Works on the Sage version available on UF HiPerGator and on a current stock SageMath release.
- [ ] Tutorial notebook (Jupyter, Sage kernel) walking through the same sections as the Maple tutorial.

### Out of Scope

- The related Maple packages (ETA, thetaids, ramarobinsids, rank, crank, sptcrank, tcore) — natural follow-on milestones, not v1.0.
- Proving identities (valence-formula machinery lives in thetaids, not qseries).
- A Maple-syntax compatibility layer or Maple worksheet importer.
- Performance beyond "tutorial examples finish in reasonable interactive time"; no Cython or parallelism in v1.0.
- Pure-SymPy fallback for non-Sage Python — decided against (see Key Decisions).

## Context

- Reference material: package index and per-function docs at `https://qseries.org/fgarvan/qmaple/qseries/`, the updated q-product tutorial (`qseriesdoc.pdf`), and the Maple source distributed from the same site. Version 1.3 is dated 2016-08-12; the function list was last updated 2016-08-13.
- Maple is unavailable, so Maple documentation output is the oracle for tests. Where a doc page shows no output for a case, the Sage result must be cross-checked another way (numerical check of a product identity to high order, or an independent implementation of the same identity).
- The relation-finding functions are linear algebra over `QQ` (nullspace of a coefficient matrix built from monomials in the input series); Sage's exact linear algebra is a strength here. Maple's ordering of returned relations may not be reproducible — tests should check the relation set up to equivalence, not verbatim ordering.
- `etamake` / `jacprodmake` / `prodmake` are implementations of Andrews' algorithm (recover exponents from log-derivative / Möbius-style recursion). These are the highest-value and highest-risk functions; get `prodmake` right first and build the others on it.
- Sage already ships some overlapping primitives (`q_binomial`, `q_pochhammer`, `qexp_eta`, `theta` in `sage.modular.etaproducts`). The port wraps or reimplements as needed but keeps qseries' names and argument conventions at the public surface.
- Deployment target is UF HiPerGator (no root access); must build with `sage -pip install .`.

## Constraints

- **Runtime:** SageMath (Python 3). No Maple, no proprietary dependencies. Only Sage, its bundled libraries, and pure-Python packages from PyPI.
- **Interface fidelity:** Function names and argument order match qseries 1.3. Where Maple semantics cannot be matched, the divergence is chosen once, documented, and applied consistently.
- **Testing:** `pytest` under `sage -python`; every function has a test with an expected value traceable to a documented example.
- **Licensing:** Frank Garvan's Maple source and documentation are his copyright. The porting approach (source translation vs. reimplementation from documented behavior) and any attribution/permission requirements must be settled before code is written.
- **Deployment:** Must build and run on HiPerGator without root.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Target platform: Python on SageMath, not SymPy | Exact power-series rings, exact linear algebra, number-theoretic primitives, and eta/theta infrastructure are all built in; SymPy would mean rewriting truncated-series arithmetic and nullspace routines from scratch. | — Pending |
| Scope: Full 41-function port in v1.0 | User request; partial ports leave the tutorial only partly runnable. | — Pending |
| Oracle for correctness: Maple documentation examples + independent identity checks | No Maple available; documented outputs are the only Maple-produced ground truth. | — Pending |
| Series truncation: Explicit `T` argument everywhere, mirroring Maple's `(f, q, T)` signatures | Keeps call sites identical to the tutorial; avoids hidden global precision. | — Pending |
| Symbolic outputs: Lightweight Python classes (`EtaProduct`, `JacProduct`) rather than Sage symbolic expressions | Printable like Maple's output, convertible back to series, and trivially testable. | — Pending |
| Porting method: source translation vs. clean reimplementation from docs | **Pending** — depends on licensing check. Blocks Phase 1. | — Pending |
| Package name: `qseries` vs. `qseries_sage` | **Pending** — decide before packaging phase. | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-16 after initialization*
