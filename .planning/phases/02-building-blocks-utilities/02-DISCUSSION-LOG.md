# Phase 2: Building Blocks & Utilities - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-16
**Phase:** 02-building-blocks-utilities
**Areas discussed:** Sage primitive wrapping, Bivariate z-variable interface, quinprod identity modes, checkmult/checkprod semantics

---

## Sage Primitive Wrapping

| Option | Description | Selected |
|--------|-------------|----------|
| Wrap Sage builtins | etaq → qexp_eta; qbin → q_binomial. Less code, Sage's tested math. | ✓ (for etaq, qbin) |
| Reimplement from math | Write product formulas directly from docs. | ✓ (for everything else) |
| Hybrid: wrap where exact, reimplement where divergence risk | Case-by-case decision. | |

**User's choice (Q1 — etaq/qbin):** Wrap Sage builtins  
**User's choice (Q2 — rest):** Reimplement from math  
**Notes:** `sage.modular.etaproducts` remains off-limits (CLAUDE.md constraint).

---

## Bivariate z-Variable Interface

| Option | Description | Selected |
|--------|-------------|----------|
| z is a Sage symbolic variable the caller creates | theta(z, q, T) — caller does z = var('z'). Matches Maple. | ✓ |
| z is always created internally | Function returns polynomial in an internal z. Simpler but wrong signature. | |

**User's choice (Q1 — caller interface):** Caller-created symbolic variable  

| Option | Description | Selected |
|--------|-------------|----------|
| QSeries with R = LaurentPolynomialRing(QQ, 'z') | Consistent with Phase 1 FOUND-01. | ✓ |
| Raw Sage LaurentSeries | No QSeries wrapper. Breaks downstream consistency. | |

**User's choice (Q2 — return type):** QSeries with LaurentPolynomialRing  
**Notes:** Consistent with Phase 1 decision and FOUND-01.

---

## quinprod Identity Modes

| Option | Description | Selected |
|--------|-------------|----------|
| Plain string | Returns formatted "LHS = RHS" string. No new class. | ✓ |
| IdentityEquation dataclass | New class with .lhs/.rhs and .to_series(). | |
| Claude's discretion | Any type that prints clearly. | |

**User's choice:** Plain string  
**Notes:** Applies when T == 'prodid' or T == 'seriesid'. Normal integer T returns QSeries.

---

## checkmult / checkprod Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| bool (True/False) | Returns True if all tested coprime pairs satisfy a(mn)=a(m)a(n). | ✓ |
| bool + first counterexample | Returns (True, None) or (False, (m, n, ...)). | |
| Claude's discretion after doc page | Match whatever Maple returns. | |

**User's choice (checkmult):** bool  

| Option | Description | Selected |
|--------|-------------|----------|
| bool; 'nice' = prodmake exponents bounded | Depends on Phase 3 prodmake. | ✓ |
| bool; 'nice' = slow coefficient growth | Prodmake-free heuristic. | |
| Claude's discretion after doc page | Planner reads doc page. | |

**User's choice (checkprod):** bool with prodmake-based criterion  

| Option | Description | Selected |
|--------|-------------|----------|
| Stub with NotImplementedError in Phase 2 | Clean forward dependency; Phase 3 fills in. | ✓ |
| Implement prodmake-free approximation now | Two implementations, divergence risk. | |
| Skip checkprod until Phase 3 | Leave name out of __init__.py. | |

**User's choice (checkprod Phase 2 handling):** Stub with NotImplementedError  
**Notes:** checkprod IS exported in Phase 2 with the stub so the name is available.

---

## Claude's Discretion

- Exact coprime pairs checked in `checkmult`
- Internal variable naming in bivariate functions
- String format for quinprod identity modes
- Whether `packageversion()` reads from `__version__` or a constant

## Deferred Ideas

None

