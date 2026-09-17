# Deferred Items — Phase 02 Building Blocks & Utilities

## Pre-existing failures from 02-02 (out of scope for 02-03)

**test_tripleprod_bivariate_type** — `TypeError: unsupported operand parent(s) for *`
when calling `tripleprod(z, q, 5)` with a `LaurentPolynomialRing` z generator.
The bivariate path in `_building_blocks.py` cannot multiply across mismatched parent rings.
Requires fixing `tripleprod` (and possibly `quinprod`) in `_building_blocks.py`.

**test_quinprod_series** — same root cause: `quinprod(z, q, 5)` fails with bivariate z.

These tests were unskipped in 02-02 but the implementation is incomplete for bivariate inputs.
Deferred to a future patch of `_building_blocks.py`.
