"""Cable / drum / lever torque model as a function of the mechanism angle.

Mechanism (as implied by the closure equations; see DERIVATION.md):

    O  lever pivot (origin of the closure frame)
    A  fixed cable anchor / outlet,      O -> A = B (constant, depends on h, p, alpha)
    Pc centre of the drum of radius R,   Pc -> O = c*u(q)   (drum rides on the lever)
    T  point where the cable leaves the drum tangentially,
       A -> T = s*u(phi)  (free span),   T -> Pc = R*u_perp(phi)

    u(x) = (cos x, sin x),  u_perp(x) = (-sin x, cos x)

Closure  B + s*u(phi) + R*u_perp(phi) + c*u(q) = 0  is exactly the pair f1, f2.

Units: lengths in mm, forces in N, torques in N.mm internally (N.m where the
name says so). Angles are radians internally; the public "*_deg" inputs and
the module constants below are degrees, converted explicitly.
"""
from dataclasses import dataclass

import numpy as np

H, P, C, R = 34.785, 3.155, 283.438, 22.827  # mm

ALPHA = 20.428  # degrees

L_CARCACA = 131.37  # mm

TAU_PESO = 11.165  # N.m

T_MAX = 140  # N.m, desired peak cable torque

THETA = np.arange(10.0, 190.01, 0.5)  # degrees

THETA_REF = 10.0  # degrees, reference pose for the spring deflection

THETA_POSE = 115.017  # degrees, measured CAD pose

SPRING_POSE = 91.35  # mm, spring length at this pose


@dataclass(frozen=True)
class Geometry:
    h: float = H
    p: float = P
    c: float = C
    r: float = R
    alpha_deg: float = ALPHA

    @property
    def alpha(self):
        return np.radians(self.alpha_deg)

    @property
    def base_vector(self):
        """B = O -> A, the constant (h, p) term of the closure equations."""
        a = self.alpha
        return np.array([
            self.h*np.sin(a) - self.p*np.cos(a),
            self.h*np.cos(a) + self.p*np.sin(a),
        ])


GEOMETRY = Geometry()


# ---------------------------------------------------------------- kinematics

def calculate_q(theta_star, alpha):
    """q = theta* - pi/2 - alpha  (all radians)."""
    return theta_star - np.pi/2 - alpha


def calculate_center_distance(q, geom=GEOMETRY):
    """rho = |A -> Pc| = |B + c*u(q)|.

    With q = theta* - pi/2 - alpha this reduces to
    rho^2 = h^2 + p^2 + c^2 - 2c(h cos theta* + p sin theta*)  (alpha cancels).
    """
    bx, by = geom.base_vector
    return np.hypot(bx + geom.c*np.cos(q), by + geom.c*np.sin(q))


def calculate_free_span(rho, geom=GEOMETRY):
    """Tangent length s from A to the drum: rho^2 = s^2 + R^2."""
    if np.any(rho < geom.r):
        raise ValueError("anchor inside the drum: no tangent cable span")
    return np.sqrt(rho**2 - geom.r**2)


def calculate_phi(q, s, geom=GEOMETRY):
    """Closed-form cable direction phi from the closure equations.

    s*cos(phi) - R*sin(phi) = rho*cos(phi + gamma) = Wx
    s*sin(phi) + R*cos(phi) = rho*sin(phi + gamma) = Wy
    with W = -(B + c*u(q)), gamma = atan2(R, s)  =>  phi = atan2(Wy, Wx) - gamma.
    """
    bx, by = geom.base_vector
    wx = -(bx + geom.c*np.cos(q))
    wy = -(by + geom.c*np.sin(q))
    return np.arctan2(wy, wx) - np.arctan2(geom.r, s)


def closure_residuals(q, s, phi, geom=GEOMETRY):
    a = geom.alpha
    f1 = (geom.h*np.sin(a) - geom.p*np.cos(a)
          + s*np.cos(phi) - geom.r*np.sin(phi) + geom.c*np.cos(q))
    f2 = (geom.h*np.cos(a) + geom.p*np.sin(a)
          + s*np.sin(phi) + geom.r*np.cos(phi) + geom.c*np.sin(q))
    return f1, f2


def calculate_b(q, phi, geom=GEOMETRY):
    """b = |O -> T|, distance from the pivot to the force application point.

    T = -c*u(q) - R*u_perp(phi)  =>  b^2 = c^2 + R^2 + 2cR sin(q - phi).
    """
    return np.sqrt(geom.c**2 + geom.r**2
                   + 2*geom.c*geom.r*np.sin(q - phi))


def calculate_b_from_span(s, phi, geom=GEOMETRY):
    """Same b, through the anchor: |B + s*u(phi)| (law of cosines).

    This is the corrected form of the old measure_moment_arm(): its cosine
    argument is the angle between B and the cable, phi - atan2(By, Bx),
    not phi itself.
    """
    bx, by = geom.base_vector
    norm_b = np.hypot(bx, by)
    return np.sqrt(s**2 + norm_b**2
                   + 2*s*norm_b*np.cos(phi - np.arctan2(by, bx)))


def calculate_beta(q, phi, geom=GEOMETRY):
    """Signed angle beta such that O -> T = b*(-cos(beta - q), sin(beta - q)).

    The lever line O -> Pc points along q + pi; T sits at q + pi - beta.
    Its magnitude equals the old measure_moment_arm_deflection(b),
    acos((b^2 + c^2 - R^2) / (2bc)); atan2 also keeps the side.
    """
    return np.arctan2(-geom.r*np.cos(q - phi),
                      geom.c + geom.r*np.sin(q - phi))


def calculate_wrap_angle(q, phi):
    """Drum angle of the tangent point relative to the lever, in [0, 2pi).

    The cable wraps counter-clockwise from T, so the cable path from A to a
    point fixed on the drum is s + R*(q - phi) + const.
    """
    return np.mod(q - phi, 2*np.pi)


def calculate_cable_path(s, q, phi, geom=GEOMETRY):
    """Cable length from A to a fixed point on the drum, up to a constant."""
    return s + geom.r*calculate_wrap_angle(q, phi)


# -------------------------------------------------------------- force/torque

def moment_arm_vector(b, beta, q):
    """O -> T as a (2, N) array."""
    return np.array([-b*np.cos(beta - q), b*np.sin(beta - q)])


def cable_force_vector(force, phi):
    """Force of the cable on the drum at T, pulling towards A: -f*u(phi)."""
    return np.array([-force*np.cos(phi), -force*np.sin(phi)])


def cross_2d(a, b):
    """z component of a x b for (2, N) arrays: a_x*b_y - a_y*b_x.

    This is the antisymmetric part M[0, 1] - M[1, 0] of the dyad
    np.outer(a, b); the outer product itself is not a torque.
    """
    return a[0]*b[1] - a[1]*b[0]


def calculate_perpendicular_moment_arm(q, phi, geom=GEOMETRY):
    """Signed torque per unit tension, tau/f = c*sin(phi - q) - R (mm).

    Positive = counter-clockwise in the closure frame (theta* increasing).
    """
    return geom.c*np.sin(phi - q) - geom.r


def spring_tension(delta, stiffness, preload=0.0):
    """Linear spring, f = k*delta + f0, with f = 0 where the cable is slack."""
    return np.maximum(stiffness*delta + preload, 0.0)


@dataclass(frozen=True)
class MechanismState:
    theta_star: np.ndarray   # rad
    q: np.ndarray            # rad
    rho: np.ndarray          # mm, anchor to drum centre
    s: np.ndarray            # mm, free cable span
    phi: np.ndarray          # rad, cable direction A -> T
    beta: np.ndarray         # rad
    b: np.ndarray            # mm, |O -> T|
    moment_arm: np.ndarray   # mm, signed perpendicular arm (tau/f)
    cable_path: np.ndarray   # mm, up to a constant
    f1: np.ndarray           # mm, closure residual
    f2: np.ndarray           # mm, closure residual


def solve_mechanism(theta_star_deg, geom=GEOMETRY):
    """Geometry only (no force law): every quantity here is closed-form."""
    theta_star = np.radians(np.asarray(theta_star_deg, dtype=float))
    q = calculate_q(theta_star, geom.alpha)
    rho = calculate_center_distance(q, geom)
    s = calculate_free_span(rho, geom)
    phi = calculate_phi(q, s, geom)
    f1, f2 = closure_residuals(q, s, phi, geom)
    return MechanismState(
        theta_star=theta_star, q=q, rho=rho, s=s, phi=phi,
        beta=calculate_beta(q, phi, geom),
        b=calculate_b(q, phi, geom),
        moment_arm=calculate_perpendicular_moment_arm(q, phi, geom),
        cable_path=calculate_cable_path(s, q, phi, geom),
        f1=f1, f2=f2,
    )


def calculate_deflection(theta_star_deg, theta_ref_deg=THETA_REF,
                         geom=GEOMETRY):
    """Cable pulled out of the anchor since the reference pose (mm)."""
    path = solve_mechanism(theta_star_deg, geom).cable_path
    return path - solve_mechanism(theta_ref_deg, geom).cable_path


def stiffness_for_peak_torque(theta_star_deg, t_max_nm=T_MAX,
                              theta_ref_deg=THETA_REF, geom=GEOMETRY):
    """k (N/mm, zero preload) whose largest |tau| over the sweep is t_max."""
    state = solve_mechanism(theta_star_deg, geom)
    delta = calculate_deflection(theta_star_deg, theta_ref_deg, geom)
    torque_per_k = np.maximum(delta, 0.0)*state.moment_arm  # N.mm per N/mm
    return t_max_nm*1e3/np.max(np.abs(torque_per_k))


@dataclass(frozen=True)
class TorqueResult:
    state: MechanismState
    delta: np.ndarray            # mm, spring deflection
    force: np.ndarray            # N, cable tension
    b_vector: np.ndarray         # (2, N) mm
    force_vector: np.ndarray     # (2, N) N
    tau_nm: np.ndarray           # N.m, signed, CCW positive


def calculate_torque_theta_star(theta_star_deg, stiffness, preload=0.0,
                                theta_ref_deg=THETA_REF, geom=GEOMETRY):
    state = solve_mechanism(theta_star_deg, geom)
    delta = calculate_deflection(theta_star_deg, theta_ref_deg, geom)
    force = spring_tension(delta, stiffness, preload)
    b_vector = moment_arm_vector(state.b, state.beta, state.q)
    force_vector = cable_force_vector(force, state.phi)
    tau = cross_2d(b_vector, force_vector)
    return TorqueResult(state=state, delta=delta, force=force,
                        b_vector=b_vector, force_vector=force_vector,
                        tau_nm=tau/1e3)


# ---------------------------------------------------------------- reporting

def print_validation(theta_list, stiffness, geom=GEOMETRY):
    res = calculate_torque_theta_star(np.asarray(theta_list), stiffness,
                                      geom=geom)
    st = res.state
    alt = res.force*st.moment_arm/1e3
    for i, th in enumerate(theta_list):
        print(f"theta*={th:8.3f}  q={np.degrees(st.q[i]):9.3f}  "
              f"phi={np.degrees(st.phi[i]):9.3f}  "
              f"beta={np.degrees(st.beta[i]):7.4f}  b={st.b[i]:8.3f}  "
              f"s={st.s[i]:8.3f}  delta={res.delta[i]:7.3f}  "
              f"f={res.force[i]:8.1f}")
        print(f"    b_vec=({res.b_vector[0, i]:9.3f}, {res.b_vector[1, i]:9.3f})"
              f"  F_vec=({res.force_vector[0, i]:9.1f}, "
              f"{res.force_vector[1, i]:9.1f})  tau={res.tau_nm[i]:9.3f} N.m"
              f"  (f*d: {alt[i]:9.3f})  f1={st.f1[i]:.1e}  f2={st.f2[i]:.1e}")


def print_cad_pose_report(geom=GEOMETRY):
    pose = solve_mechanism(THETA_POSE, geom)
    ref = solve_mechanism(THETA_REF, geom)
    d_path = pose.cable_path - ref.cable_path
    print(f"CAD pose theta*={THETA_POSE}: s={pose.s:.3f} mm, "
          f"rho={pose.rho:.3f} mm, b={pose.b:.3f} mm, "
          f"d={pose.moment_arm:.3f} mm")
    print(f"  cable pulled out {THETA_REF}->{THETA_POSE} deg: "
          f"{d_path:.3f} mm (span only: {pose.s - ref.s:.3f} mm)")
    print(f"  spring at pose {SPRING_POSE} mm -> spring at {THETA_REF} deg "
          f"would be {SPRING_POSE + d_path:.3f} mm (compression spring) or "
          f"{SPRING_POSE - d_path:.3f} mm (extension spring); "
          f"L_CARCACA - SPRING_POSE = {L_CARCACA - SPRING_POSE:.3f} mm")


if __name__ == "__main__":
    k = stiffness_for_peak_torque(THETA)
    print(f"stiffness for |tau|max = {T_MAX} N.m with zero preload: "
          f"{k:.3f} N/mm (sizing assumption, not project data)\n")
    print_validation([10.0, 45.0, 90.0, THETA_POSE, 150.0, 190.0], k)
    print()
    print_cad_pose_report()
