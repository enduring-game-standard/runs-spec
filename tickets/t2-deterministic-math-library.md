# T2: Deterministic Cross-Platform Math Library

A set of `runs-prim` Processor bodies implementing `sin`, `cos`, `sqrt`, `atan2`, `exp`, `log` using only integer arithmetic. Bit-exact across all platforms.

**Needs**: Numerical methods specialist who understands game requirements.
**Estimated effort**: 3–6 months of careful numerical work.

## Why This Is Hard

IEEE 754 does not mandate correctly rounded results for transcendental functions. Different hardware, compilers, and libm implementations produce different results for `sin(0.1)`. Any RUNS game using `float` types loses cross-platform determinism.

Games requiring determinism (demo playback, lockstep netcode, tournament verification) must use integer/fixed-point types. This library provides the math primitives to make that practical for modern game designs.

## Approach: CORDIC

CORDIC (COordinate Rotation DIgital Computer, 1956) computes trig functions using only shifts and adds — exactly the operations `runs-prim` supports. O(n) iterations where n = desired bits of precision. Invented for real-time navigation computers with no floating-point hardware.

## Acceptance Criteria

- All functions defined as `runs-prim` Processor bodies (no platform intrinsics)
- Accurate to ≥16 bits of fractional precision
- Performance: ≤100ns per call on modern hardware when compiled
- Test vectors verified against a reference math library (MPFR)
- Published in `runs-library` as `runs:math`
