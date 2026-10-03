# Torque model: derivation and verification

Code: `torque_model.py`. Checks: `test_torque_model.py` (`python -m pytest`).
Validation printout: `python torque_model.py`.

Notation: `u(x) = (cos x, sin x)`, `u⊥(x) = (−sin x, cos x)`, and
`a × b = a_x b_y − a_y b_x`.

## 1. The closure equations as written are inconsistent

```
f1 = h sinα − p cosα + q cosφ − R sinφ + c cos q = 0
f2 = h cosα + p sinα + q sinφ + R cosφ + c sin q = 0
q  = θ* − π/2 − α
```

`q` is used two ways:

- In `cos q` and `sin q` it is an angle in radians.
- In `q cosφ` and `q sinφ` it is a length that sits next to `R` and `c` in mm.

Taking it literally does not work. For a given θ* the only unknown is φ, but there
are two equations. The pair has a solution only when
`|B + c u(q)| = √(q² + R²) ≈ 23 mm`. Over the whole range that distance is
248–318 mm, so the literal system has **no solution for any θ\***. The test
`test_literal_closure_with_q_as_length_has_no_solution` checks this.

The length in that term is the free cable span: the "vão livre" `s` that
`calculate_array_vaos_livres` was meant to compute. The model uses:

```
f1 = h sinα − p cosα + s cosφ − R sinφ + c cos q = 0
f2 = h cosα + p sinα + s sinφ + R cosφ + c sin q = 0
```

In vector form this is `B + s u(φ) + R u⊥(φ) + c u(q) = 0`, where
`B = (h sinα − p cosα, h cosα + p sinα)` is constant.

## 2. Geometry implied by the loop

| point | definition |
|---|---|
| O | lever pivot (origin) |
| A | fixed cable anchor/outlet, `O→A = B`, `|B| = √(h²+p²) = 34.93 mm` |
| T | point where the cable leaves the drum tangentially, `A→T = s u(φ)` |
| Pc | drum centre (radius R, on the lever), `T→Pc = R u⊥(φ)`, `Pc→O = c u(q)` |

`R u⊥(φ)` is perpendicular to the span, so the cable is tangent to the drum at T.
The lever line `O→Pc` points along `q + π`.

Three things in the existing code support this reading:

- **`measure_moment_arm_deflection(b)`.** This is the law of cosines in the
  triangle O–Pc–T, with sides `b`, `c` and `R`.
- **`b_vector = b(−cos(β−q), sin(β−q))`.** This equals `b u(q + π − β)`: the
  lever line rotated by −β.
- **`V = −f u(φ)`.** This is the cable pulling the drum at T back towards A.

## 3. φ in closed form (no numerical solver needed)

Move the φ terms to one side. Let `W = −(B + c u(q))`, which is the vector A→Pc:

```
s cosφ − R sinφ = W_x
s sinφ + R cosφ = W_y
```

The left side is the vector `(s, R)` rotated by φ. Its length is
`ρ = √(s² + R²)` and its phase is `γ = atan2(R, s)`:

```
ρ cos(φ + γ) = W_x ,  ρ sin(φ + γ) = W_y
```

Both equations together give:

- **Distance:** `ρ = |W|`, and α drops out:
  `ρ² = h² + p² + c² − 2c(h cosθ* + p sinθ*)`.
- **Span:** `s = √(ρ² − R²)`. This needs `ρ > R`, and it always holds
  (ρ ≥ 248 mm, R = 22.8 mm).
- **Direction:** `φ = atan2(W_y, W_x) − atan2(R, s)`.

`s > 0` is the physical tangent. A negative root would be the crossed tangent on
the other side of the drum. Both residuals stay ≤ 1e‑13 mm over 10°–190°.

**Note on the old `calculate_array_vaos_livres`.**

- It returned **ρ²**, not `s`: there is no square root and no `−R²` term.
- Its cross term has the **opposite sign**: it equals the closure ρ² at θ* + π.
  Either θ in that formula is measured from the opposite direction, or `(h, p)`
  has the opposite sign in f1/f2. The closure equations were used as the
  authority; the CAD sketch has to decide this.
- `calculate_diff_s_s10` applied `np.radians` twice.

## 4. b, β and the old `measure_moment_arm`

`T = −c u(q) − R u⊥(φ)`, so

```
b² = c² + R² + 2cR sin(q − φ)
β  = atan2(−R cos(q − φ), c + R sin(q − φ))     (signed)
```

This β is the signed form of the old `acos((b² + c² − R²)/(2bc))`. Its sign is
positive over the whole range (β ≈ 4.6°), so `b_vector` has the right side.

`measure_moment_arm(φ)` is the same `b` measured through the anchor:
`b = |B + s u(φ)|`. The correct cosine argument is the angle between B and the
cable, `φ − atan2(B_y, B_x)`, not φ. So the old function and `b` are the same
quantity once that argument is fixed. Neither one is the perpendicular moment arm.

## 5. Torque: a 2D cross product, not an outer product

`τ_z = b_x F_y − b_y F_x`. `np.outer(b, F)` gives the dyad `b_i F_j`; the torque
is only its antisymmetric part `M₀₁ − M₁₀`. A 3D cross product with z = 0 gives
`(0, 0, τ_z)`, so a scalar is enough. The following forms are checked to agree:

```
τ = b × F
  = f (c sin(φ − q) − R)          signed perpendicular arm d
  = b f sin(φ − q + β)
  = −f (B × u(φ))                 the cable line passes through A
  = −f dℓ/dθ*                     virtual work
```

`ℓ = s + R·wrap(q − φ)` is the cable path from A to a point fixed on the drum.
`|d| ≤ |B| = 34.93 mm` always holds, because the line of action passes through A.

Sign: positive is counter-clockwise in the closure frame, which is the direction
of increasing θ*. With tension `f ≥ 0`, `d < 0` from 10° to about 189.5°. So the
cable torque is **restoring** (negative), and it is not passed through `abs()`.

## 6. What is determined and what is not

| quantity | status |
|---|---|
| q, ρ, s, φ, b, β, d, ℓ (up to a constant) | analytic, closed form |
| f1, f2 | ≈ 1e‑13 mm residual |
| spring deflection δ = ℓ(θ*) − ℓ(θ_ref) | analytic. It includes the drum wrap `R Δ(q−φ)`; the span alone (`s − s10`) is off by up to 3.2 mm/rad in dℓ/dθ* |
| spring stiffness k, preload, free length | **missing project data.** `stiffness_for_peak_torque` sizes k so that `max|τ| = T_MAX` with zero preload, as an explicit design assumption (k ≈ 91.1 N/mm, θ_ref = 10°) |
| TAU_PESO | unused: its dependence on θ* is not given |
| numerical solver | not needed |

## 7. CAD pose (θ* = 115.017°, spring 91.35 mm)

- **Tangent point.** O→T = (−285.126, 0.002) mm. T lies on the x axis to within
  0.002 mm, which looks like the CAD reference dimension. It agrees with the
  closure frame.
- **Cable pulled out from 10° to 115.017°.** 46.03 mm (48.63 mm from the span alone).
- **The single spring length is not enough on its own.** The model gives only
  length *changes*, so one spring length is not comparable without the spring
  length at another pose. Under the unverified hypothesis that the spring sits at
  `L_CARCACA` at θ* = 10°, the CAD implies 131.37 − 91.35 = 40.02 mm. The model
  gives 46.03 mm, which is 6.0 mm off. With the old sign convention it gives
  42.02 mm.

Possible causes, which were not corrected:

- the sign convention in §3;
- the spring reference pose: the cable may be slack until θ* ≈ 41.9°;
- the spring not acting in line with the cable.
