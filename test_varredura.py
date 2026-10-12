import numpy as np
import pytest

import torque_model as m
from patent_data import load_patent_data

THETA = np.linspace(m.THETA_MIN, m.THETA_MAX, 1501)
PATENTE = load_patent_data()


def avaliar(h):
    return m.vh_avaliar_h(h, THETA, PATENTE, 1e-6)


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


def test_k_nao_e_reidentificado_por_h():
    linha = avaliar(m.H_CALIBRADO)
    assert "k_estrela" not in linha and "rmse_k_estrela" not in linha
    assert m.VH_K == m.K == 174.68


def test_metricas_no_h_adotado():
    linha = avaliar(m.H_CALIBRADO)
    assert linha["mae"] == pytest.approx(1.5866, abs=1e-4)
    assert linha["r2"] == pytest.approx(0.99839, abs=1e-5)
    assert linha["theta_erro_max"] == pytest.approx(42.90947)


def test_fronteira_da_tracao():
    h = m.vh_fronteira_tracao(32.0, 34.0, THETA)
    assert h == pytest.approx(32.8863, abs=1e-4)
    assert m.vh_extensao(h, THETA).min() >= 0


def test_nos_da_familia():
    nos = m.vh_nos_da_familia(m.VH_FAMILIA, THETA)
    thetas = [t for t, _ in nos["nos"]]
    assert thetas == pytest.approx([68.03, 185.71], abs=0.15)
    assert nos["maximo"][0] == pytest.approx(130.38, abs=0.15)
