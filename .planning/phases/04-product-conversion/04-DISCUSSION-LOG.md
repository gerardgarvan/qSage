# Phase 4: Product Conversion - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-16
**Phase:** 04-product-conversion
**Areas discussed:** Module layout, Unknown signatures (CONV-05/10/11), etamake termination, qfactor input type

---

## Module Layout

| Option | Description | Selected |
|--------|-------------|----------|
| One file: _conversion.py | All 10 functions in one module, pattern of _building_blocks.py | ✓ |
| Two files: _etamake.py + _jacprod.py | Split into eta-family and jac-family | |
| Three files by subgroup | Eta-family, jac-family, misc — most granular | |

**User's choice:** One file (`_conversion.py`)
**Notes:** None

---

## Plan Splitting

| Option | Description | Selected |
|--------|-------------|----------|
| Split by subgroup (~3 plans) | 04-01: etamake+qetamake; 04-02: jac-family; 04-03: misc | ✓ |
| One big plan | Single PLAN.md for all 10 functions | |

**User's choice:** Split into ~3 plans
**Notes:** Matches prior phases' pattern

---

## Unknown Signatures (CONV-05, CONV-10, CONV-11)

| Option | Description | Selected |
|--------|-------------|----------|
| Researcher reads doc pages and resolves | Standard [?] handling | ✓ |
| Deprioritize — stub with NotImplementedError | If underdocumented | |
| User knows the signatures | Lock in now | |

**User's choice:** Researcher reads doc pages
**Notes:** Same approach used for prior [?] requirements in Phase 2

---

## etamake Greedy Termination

| Option | Description | Selected |
|--------|-------------|----------|
| Convergence check: stop when series == 1 | Mathematically correct; raises ValueError if no convergence | ✓ |
| Fixed iteration bound: at most T passes | Pragmatic but may silently fail | |
| Let researcher decide from doc page | | |

**User's choice:** Convergence check
**Notes:** ValueError raised if convergence not reached within T steps

---

## etamake Non-convergence Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Raise ValueError('not an eta product') | Fail loudly | ✓ |
| Return partial result with warning | More Maple-like | |

**User's choice:** Raise ValueError
**Notes:** Consistent with no-silent-failures principle

---

## qfactor Input Type

| Option | Description | Selected |
|--------|-------------|----------|
| Sage polynomial/rational in q | PolynomialRing(QQ,'q') or fraction field element | ✓ |
| QSeries input | Truncated series treated as polynomial | |
| Let researcher decide from doc page | | |

**User's choice:** Sage polynomial/rational
**Notes:** Most natural Sage representation; enables use of Sage's factor()

---

## qfactor Return Type

| Option | Description | Selected |
|--------|-------------|----------|
| Rich return: (num QProduct, denom QProduct, q^r) | Preserves rational product structure | ✓ |
| Single QProduct with negative exponents | Simpler but less readable | |
| Let researcher decide from doc page | | |

**User's choice:** Rich structured return
**Notes:** Exact container type (namedtuple/dataclass/tuple) left to Claude's discretion

---

## Claude's Discretion

- Exact return type container for qfactor result
- Whether qs2jaccombo/findprod go in Plan 04-02 or 04-03 after researcher resolves signatures

## Deferred Ideas

None
