"""
Exoesqueleto 1 (US 9.889.554 B2): ajuste do modelo congelado e melhor aproximação da curva
da patente com a pré-tensão e a rigidez reidentificadas em cada h (análise alternativa de
tcc_resultados.perfil_alternativo), na mesma figura, para a seção 4.5 do TCC.

A melhor aproximação usa o h de menor RMSE dessa análise (h ≈ 24,0 mm, em malha de 0,25 mm) e
o X_pose e o K reidentificados nele, lidos de results/tcc_numeros.json
("alternativo_x_pose_livre"). Não altera nenhum parâmetro do modelo nem os números de
tcc_resultados.py.

Grava results/tcc_fig2_ajuste_melhor_h.png e results/tcc_melhor_h.json.

Rodar (na raiz do repositório):
    python tcc_resultados_melhor_h.py
"""
import json

import numpy as np

import tcc_resultados as tr
import torque_model as tm
from patent_data import load_patent_data
from tcc_resultados import AZUL, LARANJA, PASTA, SUPERFICIE, TINTA, TINTA_2, eixos, plt, virgula


def torque_reidentificado(theta, h, x_pose, k):
    """−τ (u.p.) com a ancoragem em h e a extensão na pose x_pose, como em perfil_alternativo."""
    theta = np.asarray(theta, dtype=float)
    q = tm.calculate_q(theta)
    s = tm.calculate_tangent_span(tm.calculate_rho(q, h))
    phi = tm.calculate_phi(q, s, h)
    caminho = tm.comprimento_caminho(q, s, phi)
    m = tm.braco_perpendicular(phi, h)
    ext = caminho - (tm.caminho_cabo(tm.THETA_POSE, h) - x_pose)
    return k*np.where(ext > 0, ext, 0.0)*m/1000


def main():
    pat = load_patent_data()
    th, y = pat["theta_star"], pat["torque"]
    alt = json.loads((PASTA/"tcc_numeros.json").read_text(encoding="utf-8"))["alternativo_x_pose_livre"]
    h, xp, k = alt["h_min"], alt["x_pose_min"], alt["k_min"]
    congelado = tr.cabo(th)
    melhor = torque_reidentificado(th, h, xp, k)
    res_c, res_m = congelado - y, melhor - y

    def ind(res):
        return {"rmse": float(np.sqrt(np.mean(res**2))), "erro_max": float(np.abs(res).max()),
                "r2": float(1 - np.sum(res**2)/np.sum((y - y.mean())**2))}
    saida = {"congelado": {"h": tr.H, "x_pose": tm.X_POSE, "k": tr.K, **ind(res_c)},
             "melhor": {"h": h, "x_pose": xp, "k": k, **ind(res_m)}}
    assert abs(saida["melhor"]["rmse"] - alt["rmse_min"]) < 1e-6, "RMSE diferente da análise alternativa"
    (PASTA/"tcc_melhor_h.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")

    tf = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 1501)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5.6), dpi=200, facecolor=SUPERFICIE, sharex=True,
                                   gridspec_kw={"height_ratios": [2.4, 1]})
    for ax in (ax1, ax2):
        eixos(ax)
    f = lambda x, c: f"{x:.{c}f}".replace(".", ",")   # noqa: E731
    ax1.axhline(0, color=TINTA_2, lw=0.8)
    ax1.plot(tf, tr.cabo(tf), color=AZUL, lw=2,
             label=f"modelo congelado: h = {f(tr.H, 3)} mm (RMSE {f(saida['congelado']['rmse'], 3)} u.p.)")
    ax1.plot(tf, torque_reidentificado(tf, h, xp, k), color=LARANJA, lw=1.6, ls="--",
             label=f"melhor aproximação: h = {f(h, 1)} mm, $X_\\mathrm{{pose}}$ e K reidentificados "
                   f"(RMSE {f(saida['melhor']['rmse'], 3)} u.p.)")
    ax1.plot(th, y, "o", color=TINTA, ms=4, label="pontos extraídos da patente", zorder=5)
    ax1.set_ylabel("Torque do cabo (u.p.)", color=TINTA_2)
    ax1.legend(loc="lower center", frameon=False, fontsize=7.5)
    ax2.axhline(0, color=TINTA_2, lw=0.8)
    ax2.vlines(th, 0, res_c, color=AZUL, lw=1.6)
    ax2.plot(th, res_c, "o", color=AZUL, ms=3.5, label="modelo congelado")
    ax2.plot(th + 0.6, res_m, "s", color=LARANJA, ms=3.2, label="melhor aproximação")
    ax2.set_ylabel("Resíduo (u.p.)", color=TINTA_2)
    ax2.set_xlabel("θ* (graus)", color=TINTA_2)
    ax2.legend(loc="lower left", frameon=False, fontsize=7, ncol=2)
    for ax in (ax1, ax2):
        ax.xaxis.set_major_formatter(virgula(0))
        ax.yaxis.set_major_formatter(virgula(0))
    fig.tight_layout()
    fig.savefig(PASTA/"tcc_fig2_ajuste_melhor_h.png", facecolor=SUPERFICIE)
    plt.close(fig)
    print(json.dumps(saida, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
