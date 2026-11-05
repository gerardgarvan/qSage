# Deferred Items — Phase 04-product-conversion

## Pre-existing test failures (out of scope for Plan 04-02)

These failures exist in the WSL test suite but are NOT caused by Plan 04-02 changes:

1. **test_aqprod_zero_n** — AttributeError: 'int' object has no attribute. Pre-existing.
2. **test_theta_bivariate_type** — TypeError: bivariate theta type check. Pre-existing.
3. **test_theta2_shift** — `QQ(1, 4)` two-arg form fails in Sage 9.5 (same issue as the one we fixed in `_building_blocks.py`, but the test itself uses `QQ(1,4)` in the assertion). Pre-existing.
4. **test_tripleprod_bivariate_type** — AssertionError on bivariate tripleprod. Pre-existing.

These should be fixed in a future plan or hot-fix, not in Plan 04-02.
