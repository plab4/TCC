import numpy as np
import pytest

import torque_model as m
from patent_data import load_patent_data

THETA = np.linspace(m.THETA_MIN, m.THETA_MAX, 1501)
PATENTE = load_patent_data()
PESO = m.torque_peso(THETA)


def avaliar(h):
    return m.vh_avaliar_h(h, THETA, PATENTE, PESO, 1e-6)


def test_enrolamento_nao_e_criterio():
    assert "enrolamento" not in m.VH_CRITERIOS
    assert set(m.VH_CRITERIOS) == {"tracao", "fechamento", "tv_ok"}


def test_h_calibrado_viavel_mesmo_com_troca_de_sinal_de_rel():
    linha = avaliar(m.H_CALIBRADO)
    assert linha["viavel"] and linha["enrol_troca"]
    assert linha["arco_pos_max"] < 1e-2   # mm: arco de micrômetros (7,4 µm)


def test_h_cad_falha_so_a_tracao():
    linha = avaliar(m.H_CAD)
    assert not linha["viavel"] and linha["motivo"] == "tracao"
    assert linha["delta_min"] == pytest.approx(-2.257, abs=1e-3)


def test_rmse_reproduz_modelo_congelado():
    tau = m.calculate_torque_curve(m.K, m.H_CALIBRADO, PATENTE["theta_star"])["tau"]
    rmse = np.sqrt(np.mean((-tau - PATENTE["torque"])**2))
    assert avaliar(m.H_CALIBRADO)["rmse"] == rmse


def test_vh_faixa_contigua():
    linhas = [{"h": h, "ok": ok} for h, ok in
              zip([1, 2, 3, 4, 5], [False, True, False, True, False])]
    f = m.vh_faixa(linhas, "ok")
    assert (f["min"], f["max"], f["n"], f["contigua"]) == (2, 4, 2, False)


def test_csv_pt_br(tmp_path):
    caminho = tmp_path / "x.csv"
    m.vh_salvar_csv(caminho, [{"h": 22.5, "viavel": True, "motivo": "a.b"}],
                    ["h", "viavel", "motivo"])
    assert caminho.read_text(encoding="utf-8").splitlines()[1] == "22,5;sim;a.b"
