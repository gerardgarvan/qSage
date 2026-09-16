<!-- GSD:project-start source:PROJECT.md -->
## Project

**qseries-sage**

A function-for-function port of Frank Garvan's Maple **qseries** package (v1.3, 2016) to Python on SageMath. Same function names, argument order, and semantics, so tutorial and doc-page examples run unchanged apart from syntax. No Maple required.

**Core Value:** Do everything the Maple qseries package does — build q-series, convert to eta/theta/infinite products, find linear/homogeneous/polynomial relations, hunt congruences — in a free environment installable on HiPerGator, with results matching Maple's on the reference examples.

### Constraints

- **Runtime:** SageMath (Python 3) plus pure-Python PyPI packages only.
- **Interface fidelity:** Names and argument order match qseries 1.3; unavoidable divergences chosen once, documented, applied consistently.
- **Testing:** `pytest` under `sage -python`; every function has a test traceable to a documented example.
- **Licensing:** Garvan's source and docs are his copyright; porting approach and attribution settled before code is written.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Core Runtime
| Component | Choice | Version | Confidence |
|-----------|--------|---------|------------|
| Language | Python 3 (inside SageMath) | Python 3.10+ (Sage 10.x ships 3.10+) | High |
| Math engine | SageMath | 10.x (HiPerGator) / 10.3+ (stock) | High |
| Package manager | `sage -pip install .` | — | High |
| Build backend | `pyproject.toml` + `flit-core` or `setuptools` | setuptools ≥ 68 | High |
## Series Arithmetic Layer
## Existing Sage Primitives to Wrap
| Sage primitive | Wraps to qseries function | Notes |
|---|---|---|
| `sage.arith.misc.q_binomial(n, k, q)` | `qbin` | Check argument order — Sage uses (n,k,q), Maple uses (q,n,k) |
| `sage.functions.other.qexp_eta(q, prec)` | `etaq` | Sage returns series directly |
| `sage.modular.etaproducts` | Reference for eta arithmetic | Do NOT expose — different API surface |
| `sage.rings.finite_rings.GF(p)` | Coefficient ring for `*modp` functions | Use directly |
## Symbolic Output Layer
## Testing
| Tool | Role |
|---|---|
| `pytest` | Primary test runner, invoked as `sage -python -m pytest` |
| `sage.doctest` | Optional — for doctests in docstrings if desired |
| No `mock` | All Sage arithmetic is exact; no mocking needed |
## Packaging
## What NOT to Use
- **SymPy** — no exact power-series ring, no nullspace over QQ built in
- **NumPy/SciPy** — floating-point; relation finding requires exact arithmetic
- **Sage's `SR` (symbolic ring)** — wrong semantics for truncated series
- **Maple compatibility layer** — explicitly out of scope
- **Cython** — out of scope for v1.0
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
