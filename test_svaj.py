import numpy as np

import svaj
import torque_model as m

THETA = np.linspace(10.0, 190.0, 20001)
RES = svaj.calculate_svaj(THETA)


def grad(y):
    return np.gradient(y, np.radians(THETA), edge_order=2)


def test_position_is_rho_of_torque_model():
    np.testing.assert_allclose(RES["S"], m.calculate_rho(m.calculate_q(THETA)),
                               rtol=1e-12)


def test_circuit_equations_vanish():
    c1, c2, e, a, g = svaj.constants()
    q, s, psi = RES["q"], RES["S"], RES["psi"]
    f1 = c1*np.cos(a) + c2*np.cos(g) + e*np.cos(q) - s*np.cos(psi)
    f2 = -c1*np.sin(a) + c2*np.sin(g) + e*np.sin(q) - s*np.sin(psi)
    assert np.max(np.abs(f1)) < 1e-9 and np.max(np.abs(f2)) < 1e-9


def test_v_a_j_are_successive_derivatives_of_s():
    inner = slice(5, -5)
    np.testing.assert_allclose(RES["V"][inner], grad(RES["S"])[inner], atol=1e-5)
    np.testing.assert_allclose(RES["A"][inner], grad(RES["V"])[inner], atol=1e-5)
    np.testing.assert_allclose(RES["J"][inner], grad(RES["A"])[inner], atol=1e-4)


def test_psi_coefficients_are_derivatives_of_psi():
    inner = slice(5, -5)
    psi = np.unwrap(RES["psi"])
    np.testing.assert_allclose(RES["V_psi"][inner], grad(psi)[inner], atol=1e-7)
    np.testing.assert_allclose(RES["A_psi"][inner], grad(RES["V_psi"])[inner], atol=1e-7)
    np.testing.assert_allclose(RES["J_psi"][inner], grad(RES["A_psi"])[inner], atol=1e-6)


def test_omega_scales_time_derivatives():
    w = 2.0
    r = svaj.calculate_svaj(THETA[:50], omega=w)
    np.testing.assert_allclose(r["V"], RES["V"][:50]*w)
    np.testing.assert_allclose(r["A"], RES["A"][:50]*w**2)
    np.testing.assert_allclose(r["J"], RES["J"][:50]*w**3)
