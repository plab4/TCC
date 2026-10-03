"""Original cable / lever torque formulation, cleaned up and vectorized.

Function names and formulas follow the original script. Changes are limited
to Python/interface fixes and to tracing the previously undefined variables
(s, q, phi, b, beta, f) to explicit calculations. See DERIVATION.md.

Units: mm, N, N.m for torque. Angles: degrees at the interface (ALPHA,
THETA, THETA_POSE), radians internally; each conversion happens once.

Pending on the patent (not available in the project):
  * the force law, i.e. what K is and how f depends on delta;
  * confirmation of the torque operation (implemented as the z component
    of b x V, extracted from the original outer product);
  * the theta* convention (see calculate_array_vaos_livres).
"""
import numpy as np

H, P, C, R = 34.785, 3.155, 283.438, 22.827  # mm

ALPHA = 20.428  # degrees

L_CARCACA = 131.37  # mm

TAU_PESO = 11.165  # N.m

T_MAX = 140  # N.m, desired peak cable torque

THETA = np.arange(10.0, 190.01, 0.5)  # degrees

THETA_REF = 10.0  # degrees, reference of delta (s - s10)

THETA_POSE = 115.017  # degrees, measured CAD pose

SPRING_POSE = 91.35  # mm, spring length at this pose


def calculate_array_vaos_livres(theta, h=H):
    """Original formula, now with the square root (it returned s**2).

    Note: with q = theta* - pi/2 - alpha the closure equations give
    rho^2 = h^2 + p^2 + c^2 - 2c(h cos theta* + p sin theta*): the sign of the
    cross term is opposite, i.e. this function equals calculate_rho(theta+180).
    Which convention the patent uses is still open; the torque chain below
    uses calculate_rho so that phi satisfies the closure equations.
    """
    t = np.radians(theta)
    return np.sqrt(h**2 + P**2 + C**2 + 2*C*(h*np.cos(t) + P*np.sin(t)))


def calculate_diff_s_s10(s, s10):
    """delta = s - s(theta = 10 deg). s10 is passed in, already evaluated with
    the same function and H as s (the original applied np.radians twice)."""
    return s - s10


def calculate_q(theta_star):
    """q = theta* - pi/2 - alpha, radians, from theta* in degrees."""
    return np.radians(theta_star) - np.pi/2 - np.radians(ALPHA)


def calculate_base_vector(h=H):
    """Constant (h, p) term of the closure equations."""
    a = np.radians(ALPHA)
    return h*np.sin(a) - P*np.cos(a), h*np.cos(a) + P*np.sin(a)


def calculate_rho(q, h=H):
    """Distance from the cable anchor to the drum centre, from the closure."""
    bx, by = calculate_base_vector(h)
    return np.hypot(bx + C*np.cos(q), by + C*np.sin(q))


def calculate_tangent_span(rho):
    """Free span used in the closure equations: s^2 + R^2 = rho^2."""
    return np.sqrt(rho**2 - R**2)


def calculate_phi(q, s, h=H):
    """phi from the closure equations, closed form.

    f1, f2 rearranged: s cos(phi) - R sin(phi) = Wx, s sin(phi) + R cos(phi) = Wy
    with W = -(B + C u(q)). The left side is (s, R) rotated by phi, so
    phi = atan2(Wy, Wx) - atan2(R, s).
    """
    bx, by = calculate_base_vector(h)
    wx = -(bx + C*np.cos(q))
    wy = -(by + C*np.sin(q))
    return np.arctan2(wy, wx) - np.arctan2(R, s)


def calculate_closure_residuals(q, s, phi, h=H):
    """f1, f2 as given, with the free span s as the length multiplying
    cos(phi) and sin(phi) (q there would be radians times mm)."""
    a = np.radians(ALPHA)
    f1 = (h*np.sin(a) - P*np.cos(a)
          + s*np.cos(phi) - R*np.sin(phi) + C*np.cos(q))
    f2 = (h*np.cos(a) + P*np.sin(a)
          + s*np.sin(phi) + R*np.cos(phi) + C*np.sin(q))
    return f1, f2


def measure_moment_arm(s, phi, h=H):
    """Original law of cosines: b = |pivot -> cable tangent point|.

    phi here is the angle between the (H, P) offset and the cable, i.e. the
    closure phi minus the direction of the base vector.
    """
    return np.sqrt(
        s**2 + h**2 + P**2
        + 2*s*np.sqrt(h**2 + P**2)*np.cos(phi)
    )


def measure_moment_arm_deflection(b):
    """Original: angle beta between the lever line and b (triangle b, C, R)."""
    return np.arccos((-R**2 + b**2 + C**2) / (2*b*C))


def torque_patent(b_vector, f_vector):
    """Torque from the original outer product M_ij = b_i F_j.

    M itself is a 2x2 tensor, not a torque; the moment about the pivot is its
    antisymmetric part M_01 - M_10 = b_x F_y - b_y F_x (z of b x F).
    Positive = counter-clockwise in the closure frame. Vectorized over the
    trailing axis.
    """
    m = np.einsum('i...,j...->ij...', b_vector, f_vector)
    return m[0, 1] - m[1, 0]


def generate_graph_torque_theta_star_relation(force, h=H, theta=THETA):
    """Original chain with every variable explicit.

    force: cable tension f in N, scalar or array matching theta. Its law
    (K, delta) must come from the patent and is not assumed here.
    """
    theta = np.asarray(theta, dtype=float)
    q = calculate_q(theta)
    rho = calculate_rho(q, h)
    s = calculate_tangent_span(rho)
    phi = calculate_phi(q, s, h)

    s10 = calculate_tangent_span(calculate_rho(calculate_q(THETA_REF), h))
    delta = calculate_diff_s_s10(s, s10)

    bx, by = calculate_base_vector(h)
    b = measure_moment_arm(s, phi - np.arctan2(by, bx), h)
    beta = measure_moment_arm_deflection(b)

    f = np.broadcast_to(np.asarray(force, dtype=float), theta.shape)
    b_vector = np.array([-b*np.cos(beta - q), b*np.sin(beta - q)])
    V_vector = np.array([-f*np.cos(phi), -f*np.sin(phi)])

    tau = torque_patent(b_vector, V_vector) / 1e3  # N.mm -> N.m
    f1, f2 = calculate_closure_residuals(q, s, phi, h)
    return {
        "theta_star": theta, "q": q, "rho": rho, "s": s, "delta": delta,
        "phi": phi, "b": b, "beta": beta, "force": f,
        "b_vector": b_vector, "V_vector": V_vector, "tau": tau,
        "f1": f1, "f2": f2,
    }


if __name__ == "__main__":
    # Geometry check with a unit tension: tau is then the moment arm in m.
    res = generate_graph_torque_theta_star_relation(1.0)
    print(f"max |f1|, |f2| = {np.max(np.abs(res['f1'])):.1e}, "
          f"{np.max(np.abs(res['f2'])):.1e} mm")
    pose = generate_graph_torque_theta_star_relation(1.0, theta=[THETA_POSE])
    print(f"theta*={THETA_POSE}: s={pose['s'][0]:.3f} mm, "
          f"b={pose['b'][0]:.3f} mm, beta={np.degrees(pose['beta'][0]):.4f} deg, "
          f"b_vector=({pose['b_vector'][0, 0]:.3f}, "
          f"{pose['b_vector'][1, 0]:.3f}) mm, "
          f"tau/f={pose['tau'][0]*1e3:.3f} mm, "
          f"delta={pose['delta'][0]:.3f} mm")
