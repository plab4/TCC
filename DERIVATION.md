# Original formulation: cleanup notes and calibration status

Code: `torque_model.py`, which keeps the original function names and formulas.
Checks: `python -m pytest`.

## Calibration workflow status

| step | status |
|---|---|
| 1. Original formulation, cleaned up | done (this file) |
| 2. Patent consolidated data | **blocked: no patent material in the project** |
| 3. Reference torque(θ*) curve | waiting on step 2 |
| 4. K from the patent | waiting on step 2. What K means is not assumed |
| 5–9. Freeze K, sweep H, compare, refine | waiting on step 4. H is already an explicit parameter (`h=`) |

To continue, step 2 needs one of the following:

- the patent document itself (PDF, or its number);
- the torque × θ* figure(s);
- any table of torque, force or spring displacement values.

The patent's parameter definitions should also cover:

- what K is and the force law it enters (e.g. f = K·δ, a preload, a torsional K);
- what δ is (span change, cable path change, spring deflection);
- the θ* zero and its positive direction;
- the torque sign convention;
- whether the torque includes the weight term (TAU_PESO).

## Fixes applied to the original code

| original | problem | fix |
|---|---|---|
| `from math import ...` | scalar functions, fail on arrays | NumPy throughout |
| `calculate_array_vaos_livres` | returned `s²`, which `measure_moment_arm` then squared again (mm⁴) | `np.sqrt` added |
| `calculate_diff_s_s10` | `np.radians(10)` passed into a function that converts again | `s10` is computed at 10° by the caller and passed in |
| `calculate_diff_s_s10(s, THETA)` call | one-argument function | signature `(s, s10)` |
| `measure_moment_arm(phi)` | `s` and `H` were globals | `(s, phi, h)` |
| `generate_graph_...(braco, force)` | `b, beta, q, f, phi` undefined | each one computed in order (below) |
| `torque_patent` | `np.outer` returns a 2×2 tensor, not a torque | outer product kept; the torque is its antisymmetric part `M₀₁ − M₁₀ = b_x F_y − b_y F_x` |
| `H` global | not controllable | `h=` argument, defaults to `H = 34.785` |

## Where each variable comes from

```
θ* (deg) ── q = θ* − π/2 − α  (rad, converted once)
         ├─ ρ   = |B + C u(q)|                 anchor → drum centre
         ├─ s   = √(ρ² − R²)                   free (tangent) span
         ├─ φ   = atan2(W_y, W_x) − atan2(R, s),   W = −(B + C u(q))
         ├─ δ   = s − s(10°)                   calculate_diff_s_s10
         ├─ b   = measure_moment_arm(s, φ − ∠B, h)
         ├─ β   = measure_moment_arm_deflection(b)
         ├─ f   = input (force law pending the patent)
         ├─ b_vector = (−b cos(β−q),  b sin(β−q))
         ├─ V_vector = (−f cos φ,    −f sin φ)
         └─ τ   = torque_patent(b_vector, V_vector)
```

`B = (h sinα − p cosα, h cosα + p sinα)` is the constant term of f1 and f2.

**φ.** The closure equations reduce to closed form, so no numerical solver is
needed. The φ terms are the vector (s, R) rotated by φ:

```
s cosφ − R sinφ = ρ cos(φ + γ) = W_x,   γ = atan2(R, s)
s sinφ + R cosφ = ρ sin(φ + γ) = W_y
```

The residuals of f1 and f2 are ≈ 1e‑13 mm for every θ* and every H tested.

**The length multiplying cos φ.** The equations as written use `q` there. Taken
literally (q in rad), the pair has no solution for any θ*. It would need ρ ≈ 23 mm,
but ρ is 248–318 mm. That length has to be the free span `s`.

**measure_moment_arm.** Its `phi` is the angle *between* the (H, P) offset and
the cable, so the closure φ is passed as `φ − atan2(B_y, B_x)`. It then gives
`b = |pivot → tangent point|`.

**β.** `b_vector` places the tangent point at the lever direction rotated by −β.
`measure_moment_arm_deflection` gives |β|, and the side is checked in the tests.
β ≈ 4.6° over the whole range.

**Torque.** Several forms agree to machine precision:

- the antisymmetric part of the outer product;
- the 2D cross product;
- the z component of the 3D cross product;
- `f·(C sin(φ − q) − R)`.

Sign: positive is counter-clockwise in the closure frame, which is the direction
of increasing θ*.

## Open conflict inside the original formulation

`calculate_array_vaos_livres(θ)` uses `+2C(H cosθ + P sinθ)`. The closure
equations with `q = θ* − π/2 − α` give `−2C(...)`. So the original formula equals
the closure ρ at θ* + 180° (this is tested).

The torque chain uses the closure geometry, so that φ satisfies f1 and f2.
`calculate_array_vaos_livres` is kept unchanged (apart from the square root) for
comparison. The patent's angle convention should decide between them.

## Other things that depend on the patent

- **δ.** δ = s − s10 is kept as in the original. The physical cable displacement
  at the drum also includes the wrapped arc R·Δ(q − φ). Which one K multiplies
  must come from the patent.
- **CAD pose (115.017°).** It can't be compared to one spring length alone,
  because the model gives only changes. From 10° to the pose:
  - s changes by 48.63 mm;
  - the cable path including the wrap changes by 46.03 mm;
  - L_CARCACA − SPRING_POSE = 40.02 mm, if the spring sits at L_CARCACA at 10°
    (unverified).

  At the pose, b_vector = (−285.126, 0.002) mm, so the tangent point lies on the
  x axis.
