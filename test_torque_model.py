import numpy as np
import pytest

import torque_model as m

H_VALUES = [25.0, m.H, 45.0]


@pytest.fixture(scope="module", params=H_VALUES)
def res(request):
    out = m.generate_graph_torque_theta_star_relation(500.0, h=request.param)
    return {**out, "h": request.param}


def test_closure_residuals_vanish(res):
    assert np.max(np.abs(res["f1"])) < 1e-9
    assert np.max(np.abs(res["f2"])) < 1e-9


def test_literal_closure_with_q_as_length_has_no_solution(res):
    # q (rad) as the span would need rho = sqrt(q^2 + R^2) ~ 23 mm
    gap = res["rho"] - np.hypot(res["q"], m.R)
    assert np.min(gap) > 200.0


def test_vaos_livres_is_rho_at_theta_plus_180():
    for h in H_VALUES:
        rho = m.calculate_rho(m.calculate_q(m.THETA + 180.0), h)
        np.testing.assert_allclose(m.calculate_array_vaos_livres(m.THETA, h),
                                   rho, rtol=1e-12)


def test_s_zero_matches_calibration():
    assert abs(m.s_zero(m.H_CALIBRADO) - 252.65) < 1e-3


def test_delta_is_zero_when_cable_slack():
    s = np.array([m.s_zero() - 5.0, m.s_zero(), m.s_zero() + 5.0])
    np.testing.assert_allclose(m.calculate_delta(s), [0.0, 0.0, 5.0])


def test_tau_equals_minus_force_times_perpendicular_arm(res):
    np.testing.assert_allclose(res["tau"]*1000, -res["force"]*res["m"],
                               rtol=1e-12, atol=1e-8)


def test_guards_raise():
    with pytest.raises(ValueError):
        m.calculate_tangent_span(m.R)
    with pytest.raises(ValueError):
        m.angulo_beta(np.array([10.0]))


def test_dead_point_closed_form_matches_root():
    for h in (m.H, m.H_CALIBRADO):
        assert abs(m.ponto_morto(h) - m.ponto_morto_numerico(h)) < 1e-8


def test_b_vector_is_the_tangent_point(res):
    bx, by = m.calculate_base_vector(res["h"])
    tangent = np.array([bx + res["s"]*np.cos(res["phi"]),
                        by + res["s"]*np.sin(res["phi"])])
    # beta from arccos is unsigned; this checks the side b_vector assumes
    np.testing.assert_allclose(res["b_vector"], tangent, atol=1e-9)
    pc = -m.C*np.array([np.cos(res["q"]), np.sin(res["q"])])
    np.testing.assert_allclose(np.hypot(*(tangent - pc)), m.R, rtol=1e-9)


def test_torque_equals_cross_product_and_scalar_forms(res):
    b, v, f = res["b_vector"], res["V_vector"], res["force"]
    tau = res["tau"]*1e3
    np.testing.assert_allclose(tau, b[0]*v[1] - b[1]*v[0], atol=1e-9)
    # antisymmetric part of the original outer product
    for i in (0, 150, 300):
        dyad = np.outer(b[:, i], v[:, i])
        assert np.isclose(dyad[0, 1] - dyad[1, 0], tau[i])
    b3 =np.vstack([b, np.zeros_like(tau)])
    v3 = np.vstack([v, np.zeros_like(tau)])
    np.testing.assert_allclose(np.cross(b3.T, v3.T)[:, 2], tau, atol=1e-6)
    # f * signed perpendicular arm c sin(phi - q) - R
    arm = m.C*np.sin(res["phi"] - res["q"]) - m.R
    np.testing.assert_allclose(tau, f*arm, atol=1e-6)


def test_h_changes_the_curve():
    taus = [m.generate_graph_torque_theta_star_relation(1.0, h=h)["tau"]
            for h in H_VALUES]
    assert not np.allclose(taus[0], taus[1])
    assert not np.allclose(taus[1], taus[2])


def test_scalar_and_array_theta():
    one = m.generate_graph_torque_theta_star_relation(1.0, theta=[m.THETA_POSE])
    assert one["tau"].shape == (1,)
