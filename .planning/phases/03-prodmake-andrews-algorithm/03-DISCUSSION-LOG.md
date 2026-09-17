# Phase 3: prodmake (Andrews' Algorithm) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-16
**Phase:** 03-prodmake-andrews-algorithm
**Areas discussed:** Normalization & leading-term contract, Recurrence edge cases & stopping rule, Return type detail, checkprod integration

---

## Normalization & Leading-Term Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Raise ValueError | Require caller to normalize; matches Maple behavior | |
| Divide through silently | Normalize internally, prepend constant as prefactor | |
| Claude's discretion | Decide based on Maple doc page | ✓ |

**User's choice:** Claude's discretion — read the CONV-01 doc page and match Maple exactly.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Strip r, compute product, return QProduct with r | QProduct already has r field | |
| Raise ValueError | Simpler but violates CONV-01 SC-3 | |
| Claude's discretion | Decide based on doc page + SC-3 requirement | ✓ |

**User's choice:** Claude's discretion — but CONV-01 SC-3 requires fractional prefix support.

---

## Recurrence Edge Cases & Stopping Rule

| Option | Description | Selected |
|--------|-------------|----------|
| All n from 1 to T-1 | Most complete, matches Maple | |
| Only nonzero exponents up to T-1 | Same computation, saves memory | |
| Claude's discretion | Choose what makes to_series() cleanest | ✓ |

**User's choice:** Claude's discretion — optimize for to_series() round-trip correctness.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Return QProduct with empty exponents | Mathematically correct empty product | |
| Raise ValueError | Overly strict | |
| Claude's discretion | Decide | ✓ |

**User's choice:** Claude's discretion — must be mathematically correct.

---

## Return Type Detail — QProduct Exponent Storage

| Option | Description | Selected |
|--------|-------------|----------|
| Sage Integers | Natural from recurrence arithmetic | |
| Python ints | More portable | |
| Claude's discretion | Choose for fewest downstream surprises | ✓ |

**User's choice:** Claude's discretion.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Deferred to Phase 4 | Rational exponents not needed for prodmake proper | |
| In scope — support rational e_n now | Adds complexity | ✓ (initially) |

**Follow-up:** User reconsidered — rational exponents deferred to Phase 4. Integer only for Phase 3.

**User's final choice:** Integer exponents only in Phase 3.

---

## checkprod Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Bounded exponents criterion | |e_n| ≤ K | |
| Finite support criterion | Finitely many nonzero exponents | |
| Claude's discretion — read doc page | UTIL-06 marked [?] in REQUIREMENTS.md | ✓ |

**User's choice:** Claude's discretion — planner must fetch checkprod doc page.

---

| Option | Description | Selected |
|--------|-------------|----------|
| QSeries input only | Matches Maple calling convention | |
| QProduct input only | Direct exponent inspection | |
| Both — accept either type | isinstance dispatch | ✓ |

**User's choice:** Accept both QSeries and QProduct input.

---

## Claude's Discretion

- Normalization strategy (raise vs divide) — derive from doc page
- Fractional-prefix handling — required per CONV-01 SC-3
- Stopping rule and degenerate-input handling
- Exponent type (int vs Sage Integer)
- "Nice product" criterion — derive from checkprod doc page

## Deferred Ideas

- Rational exponents in QProduct — moved to Phase 4 (jacprodmake)
