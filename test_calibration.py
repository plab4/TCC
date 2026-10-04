import numpy as np

import calibration as cal
import torque_model as m
from patent_data import estimate_peak, load_patent_data

PATENT = load_patent_data()


def test_patent_data_sorted_and_complete():
    assert len(PATENT["theta_star"]) == len(PATENT["torque"]) == 29
    assert np.all(np.diff(PATENT["theta_star"]) > 0)


def test_peak_estimate_near_largest_sample():
    theta_peak, torque_peak = estimate_peak(PATENT["theta_star"],
                                            PATENT["torque"])
    assert 115.0 < theta_peak < 129.0
    assert torque_peak >= PATENT["torque"].max()


def test_k_is_the_least_squares_minimum():
    k, g = cal.calibrate_k(PATENT)
    def sse(kk):
        return np.sum((PATENT["torque"] - kk*g)**2)
    assert sse(k) < sse(k*1.001) and sse(k) < sse(k*0.999)


def test_torque_is_linear_in_k():
    theta = PATENT["theta_star"]
    np.testing.assert_allclose(cal.model_torque(2.0, m.H, theta),
                               2*cal.model_torque(1.0, m.H, theta))


def test_delta_never_negative_in_patent_range():
    res = m.calculate_torque_curve(1.0, m.H, PATENT["theta_star"])
    assert np.all(res["delta"] >= 0)


def test_sweep_keeps_k_fixed():
    k, _ = cal.calibrate_k(PATENT)
    rows = cal.sweep_h(k, [30.0, m.H, 40.0], PATENT)
    for row in rows:
        direct = cal.model_torque(k, row["H"], PATENT["theta_star"])
        rmse = np.sqrt(np.mean((direct - PATENT["torque"])**2))
        assert np.isclose(rmse, row["RMSE"])
