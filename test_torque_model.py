import numpy as np
import pytest

import torque_model as m


@pytest.fixture(scope="module")
def state():
    return m.solve_mechanism(m.THETA)


def test_closure_residuals_vanish(state):
    assert np.max(np.abs(state.f1)) < 1e-9
    assert np.max(np.abs(state.f2)) < 1e-9


def test_literal_closure_with_q_as_length_has_no_solution(state):
    # Taking the angle q (rad) as the span would need rho = sqrt(q^2 + R^2)
    # ~ 23 mm, while the anchor-to-drum distance is ~ 250-320 mm.
    gap = state.rho - np.hypot(state.q, m.R)
    assert np.min(gap) > 200.0


def test_rho_matches_law_of_cosines_without_alpha(state):
    th = state.theta_star
    rho2 = m.H**2 + m.P**2 + m.C**2 - 2*m.C*(m.H*np.cos(th) + m.P*np.sin(th))
    np.testing.assert_allclose(state.rho**2, rho2, rtol=1e-12)


def test_old_vaos_livres_formula_is_rho_squared_shifted_by_pi(state):
    th = state.theta_star + np.pi
    old = m.H**2 + m.P**2 + m.C**2 + 2*m.C*(m.H*np.cos(th) + m.P*np.sin(th))
    np.testing.assert_allclose(old, state.rho**2, rtol=1e-12)


def test_b_vector_is_the_tangent_point(state):
    bx, by = m.GEOMETRY.base_vector
    tangent = np.array([bx + state.s*np.cos(state.phi),
                        by + state.s*np.sin(state.phi)])
    b_vec = m.moment_arm_vector(state.b, state.beta, state.q)
    np.testing.assert_allclose(b_vec, tangent, atol=1e-9)
    # T is at distance R from the drum centre Pc = -c*u(q)
    pc = -m.C*np.array([np.cos(state.q), np.sin(state.q)])
    np.testing.assert_allclose(np.hypot(*(tangent - pc)), m.R, rtol=1e-12)


def test_b_from_span_and_old_deflection_formula_agree(state):
    np.testing.assert_allclose(m.calculate_b_from_span(state.s, state.phi),
                               state.b, rtol=1e-12)
    old_beta = np.arccos((-m.R**2 + state.b**2 + m.C**2)/(2*state.b*m.C))
    np.testing.assert_allclose(np.abs(state.beta), old_beta, atol=1e-9)
    assert np.all(state.beta > 0)  # side assumed by b_vector holds


def test_wrap_angle_stays_on_one_branch(state):
    wrap = m.calculate_wrap_angle(state.q, state.phi)
    assert np.all((wrap > np.pi/2) & (wrap < 3*np.pi/2))


def test_torque_formulations_agree():
    k = m.stiffness_for_peak_torque(m.THETA)
    res = m.calculate_torque_theta_star(m.THETA, k)
    st, f = res.state, res.force
    tau = res.tau_nm*1e3
    # f * signed perpendicular arm
    np.testing.assert_allclose(tau, f*st.moment_arm, atol=1e-6)
    # |b| |F| sin(angle from b to F)
    np.testing.assert_allclose(
        tau, st.b*f*np.sin(st.phi - st.q + st.beta), atol=1e-6)
    # moment about O of a force whose line passes through A
    bx, by = m.GEOMETRY.base_vector
    np.testing.assert_allclose(
        tau, -f*(bx*np.sin(st.phi) - by*np.cos(st.phi)), atol=1e-6)
    # antisymmetric part of the outer product
    for i in (10, 150, 300):
        dyad = np.outer(res.b_vector[:, i], res.force_vector[:, i])
        assert np.isclose(dyad[0, 1] - dyad[1, 0], tau[i])
    # 3D cross product with z = 0
    b3 = np.vstack([res.b_vector, np.zeros_like(tau)])
    f3 = np.vstack([res.force_vector, np.zeros_like(tau)])
    np.testing.assert_allclose(np.cross(b3.T, f3.T)[:, 2], tau, atol=1e-6)
    assert np.isclose(np.max(np.abs(res.tau_nm)), m.T_MAX)


def test_virtual_work_tau_equals_minus_f_dpath_dtheta():
    theta = np.linspace(10.0, 190.0, 20001)
    st = m.solve_mechanism(theta)
    dpath = np.gradient(st.cable_path, st.theta_star, edge_order=2)
    np.testing.assert_allclose(st.moment_arm, -dpath, atol=1e-6)
    # the free span alone is not the cable displacement
    dspan = np.gradient(st.s, st.theta_star, edge_order=2)
    assert np.max(np.abs(st.moment_arm + dspan)) > 1.0


def test_moment_arm_bounded_by_anchor_offset(state):
    assert np.max(np.abs(state.moment_arm)) <= np.hypot(m.H, m.P) + 1e-9


def test_scalar_input():
    res = m.calculate_torque_theta_star(m.THETA_POSE, stiffness=1.0)
    assert res.tau_nm.shape == ()
    assert res.b_vector.shape == (2,)
