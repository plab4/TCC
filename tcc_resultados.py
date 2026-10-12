"""
Números e figuras citados no TCC, gerados a partir do modelo vigente.

Não altera torque_model.py nem os parâmetros congelados: importa o modelo,
chama as funções com h explícito e grava

    results/tcc_numeros.json          todos os números citados no texto
    results/tcc_tabela_patente.csv     rastreabilidade dos 29 pontos extraídos
    results/tcc_fig1_geometria.png     laço vetorial na pose de referência
    results/tcc_fig2_ajuste.png        torque do cabo × pontos extraídos
    results/tcc_fig3_familia.png       família de curvas, K congelado
    results/tcc_fig4_rmse_h.png        RMSE em função de h, K congelado
    results/tcc_fig5_normalizado.png   perfis normalizados do cabo e do peso
    results/tcc_fig6_compensacao.png   cabo × peso em N·m e razão cabo/peso

A Figura 3 refaz, no estilo das demais, a família de curvas que a passada de
varredura de torque_model.py grava em results/vh_familia_curvas.png (mesmos h,
mesmo K congelado, mesmos nós).

Convenções angulares usadas no TCC:
    θ*        ângulo interno do mecanismo (variável do modelo), em graus
    φ_pat     ângulo da patente, medido a partir da horizontal: θ* = 133,017 − φ_pat
    elevação  elevação anatômica do braço: elevação = φ_pat + 90 = 223,017 − θ*

Rodar:  python tcc_resultados.py
"""
import contextlib
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import torque_model as tm
from patent_data import load_patent_data

PASTA = Path(__file__).parent/"results"
H = tm.H_CALIBRADO
K = tm.K

SUPERFICIE, TINTA, TINTA_2, GRADE = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
AZUL, LARANJA, VERDE = "#2a78d6", "#eb6834", "#1baf7a"


def elevacao(theta_star):
    return tm.ANGLE_OFFSET + 90.0 - np.asarray(theta_star, dtype=float)


def phi_pat(theta_star):
    return tm.ANGLE_OFFSET - np.asarray(theta_star, dtype=float)


def virgula(casas):
    from matplotlib.ticker import FuncFormatter
    return FuncFormatter(lambda x, pos: f"{x:.{casas}f}".replace(".", ","))


def eixos(ax):
    ax.set_facecolor(SUPERFICIE)
    ax.grid(color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(TINTA_2)
    ax.tick_params(colors=TINTA_2)


def cabo(theta, h=H, k=K):
    """Torque do cabo na convenção da patente (−τ do modelo). O TCC adota a
    ordenada da patente em N·m (decisão do autor), então sai em N·m."""
    return -tm.calculate_torque_curve(k, h, np.asarray(theta, dtype=float))["tau"]


# ------------------------------------------------------------ resultados

def metricas_ajuste(patente):
    y = patente["torque"]
    calc = cabo(patente["theta_star"])
    res = calc - y
    ordem = np.argsort(patente["theta_star"])
    zonas, atual = [], None
    for i in ordem:
        sinal = int(np.sign(res[i]))
        if sinal == 0:
            continue
        if atual is None or atual["sinal"] != sinal:
            atual = {"sinal": sinal, "theta": [], "res": []}
            zonas.append(atual)
        atual["theta"].append(float(patente["theta_star"][i]))
        atual["res"].append(float(res[i]))
    i_max = int(np.argmax(np.abs(res)))
    g = -tm.calculate_torque_curve(1.0, H, patente["theta_star"])["tau"]
    return {
        "rmse": float(np.sqrt(np.mean(res**2))),
        "mae": float(np.mean(np.abs(res))),
        "erro_max": float(abs(res[i_max])),
        "theta_erro_max": float(patente["theta_star"][i_max]),
        "elev_erro_max": float(elevacao(patente["theta_star"][i_max])),
        "r2": float(1 - np.sum(res**2)/np.sum((y - y.mean())**2)),
        "mae_sobre_media": float(np.mean(np.abs(res))/np.mean(y)),
        "rmse_sobre_pico": float(np.sqrt(np.mean(res**2))/y.max()),
        "residuo_medio": float(np.mean(res)),
        "k_forma_fechada": float((g @ y)/(g @ g)),
        "erro_linear_k": float(np.max(np.abs(calc - K*g))),
        "zonas": [{"sinal": z["sinal"], "n": len(z["res"]),
                   "theta_de": min(z["theta"]), "theta_ate": max(z["theta"]),
                   "media": float(np.mean(z["res"]))} for z in zonas],
        "calc": calc, "res": res,
    }


def grandezas_mecanismo():
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 150101)
    r = tm.calculate_torque_curve(K, H, th)
    torque = -r["tau"]
    ext = r["caminho"] - tm.s_zero(H)
    i_m, i_t = int(np.argmax(r["m"])), int(np.argmax(torque))
    i_pico_grade = int(np.argmax(cabo(tm.THETA)))
    arco = r["arco"]
    arco_pose = tm.R*tm.angulo_cabo_elo(
        tm.calculate_q(tm.THETA_POSE),
        tm.calculate_phi(tm.calculate_q(tm.THETA_POSE),
                         tm.calculate_tangent_span(tm.calculate_rho(
                             tm.calculate_q(tm.THETA_POSE), H)), H))
    dif_delta = -(arco - arco_pose)          # δ(caminho) − δ(vão), mesma ancoragem
    peso = tm.torque_peso(th)
    i_p = int(np.argmax(peso))
    return {
        "delta_min": float(ext.min()), "delta_max": float(ext.max()),
        "theta_delta_min": float(th[np.argmin(ext)]),
        "theta_delta_max": float(th[np.argmax(ext)]),
        "curso": float(ext.max() - ext.min()),
        "mola_min": float(tm.L_LIVRE + ext.min()),
        "mola_max": float(tm.L_LIVRE + ext.max()),
        "razao_ext_livre": float(ext.max()/tm.L_LIVRE),
        "forca_max": float(K*ext.max()),
        "m_min": float(r["m"].min()), "m_max": float(r["m"].max()),
        "theta_m_max": float(th[i_m]),
        "oa": float(np.hypot(H, tm.P)),
        "b_min": float(r["b"].min()), "b_max": float(r["b"].max()),
        "beta_min_grau": float(np.degrees(r["beta"].min())),
        "beta_max_grau": float(np.degrees(r["beta"].max())),
        "pico": float(torque[i_t]), "theta_pico": float(th[i_t]),
        "elev_pico": float(elevacao(th[i_t])),
        "pico_grade_05": float(cabo(tm.THETA)[i_pico_grade]),
        "theta_pico_grade_05": float(tm.THETA[i_pico_grade]),
        "arco_variacao": float(np.ptp(arco)),
        "caminho_variacao": float(np.ptp(r["caminho"])),
        "vao_variacao": float(np.ptp(r["s"])),
        "dif_delta_max": float(np.max(np.abs(dif_delta))),
        "theta_dif_delta_max": float(th[np.argmax(np.abs(dif_delta))]),
        "dif_delta_rel_max": float(np.max(np.abs(dif_delta)/ext)),
        "theta_dif_delta_rel_max": float(th[np.argmax(np.abs(dif_delta)/ext)]),
        "ponto_morto": float(tm.ponto_morto(H)),
        "elev_ponto_morto": float(elevacao(tm.ponto_morto(H))),
        "peso_pico": float(peso[i_p]), "theta_peso_pico": float(th[i_p]),
        "elev_peso_pico": float(elevacao(th[i_p])),
        "peso_no_ponto_morto": float(tm.torque_peso(tm.ponto_morto(H))),
        "peso_theta_max": float(tm.torque_peso(tm.THETA_MAX)),
        "peso_theta_min": float(tm.torque_peso(tm.THETA_MIN)),
        "tau_theta_max": float(cabo([tm.THETA_MAX])[0]),
        "caminho_pose": float(tm.caminho_cabo(tm.THETA_POSE, H)),
        "s_zero": float(tm.s_zero(H)),
    }


def comparacao_normalizada():
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 150101)
    c = cabo(th)
    p = tm.torque_peso(th)
    cn, pn = c/c.max(), p/p.max()
    d = cn - pn
    elev = elevacao(th)
    cruz = tm.vh_cruzamentos(elev[::-1], d[::-1])

    def faixa(e0, e1):
        sel = (elev >= e0) & (elev <= e1)
        return float(d[sel].min()), float(d[sel].max())

    i_min = int(np.argmin(d))
    return {
        "cruzamentos_elev": cruz,
        "dif_min": float(d.min()), "elev_dif_min": float(elev[i_min]),
        "dif_max": float(d.max()), "elev_dif_max": float(elev[np.argmax(d)]),
        "faixa_105_150": faixa(105.0, 150.0),
        "faixa_94_160": faixa(94.0, 160.0),
        "faixa_160_180": faixa(160.0, 180.2),
        "dif_elev_30": float(np.interp(30.0, elev[::-1], d[::-1])),
    }


def perfil_alternativo(patente, l_pose=tm.L_POSE):
    """ANÁLISE ALTERNATIVA, não o procedimento principal: para cada h,
    reidentifica X_POSE (varredura fina) e K (forma fechada). Serve só para
    auditar a afirmação da seção 4.3 sobre a identificação de H."""
    th, y = patente["theta_star"], patente["torque"]
    xs = np.arange(0.0, 90.0 + 1e-9, 0.01)
    saida = []
    for h in np.arange(8.0, 60.0 + 1e-9, 0.25):
        q = tm.calculate_q(th)
        s = tm.calculate_tangent_span(tm.calculate_rho(q, h))
        phi = tm.calculate_phi(q, s, h)
        caminho = tm.comprimento_caminho(q, s, phi)
        m = tm.braco_perpendicular(phi, h)
        cam_pose = tm.caminho_cabo(tm.THETA_POSE, h)
        ext = caminho[None, :] - (cam_pose - xs[:, None])
        g = np.where(ext > 0, ext, 0.0)*m[None, :]/1000
        k = (g @ y)/np.einsum("ij,ij->i", g, g)
        rmse = np.sqrt(np.mean((k[:, None]*g - y[None, :])**2, axis=1))
        j = int(np.argmin(rmse))
        thf = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 1501)
        ext_f = tm.caminho_cabo(thf, h) - (cam_pose - xs[j])
        saida.append({"h": float(h), "x_pose": float(xs[j]), "k": float(k[j]),
                      "rmse": float(rmse[j]),
                      "razao_ext_livre": float(ext_f.max()/(l_pose - xs[j]))})
    return saida


def identificacao_no_h_adotado(patente):
    """Reproduz a parte verificável da identificação: com h = H_CALIBRADO,
    X_POSE por varredura fina e K por mínimos quadrados em forma fechada."""
    th, y = patente["theta_star"], patente["torque"]
    q = tm.calculate_q(th)
    s = tm.calculate_tangent_span(tm.calculate_rho(q, H))
    phi = tm.calculate_phi(q, s, H)
    caminho = tm.comprimento_caminho(q, s, phi)
    m = tm.braco_perpendicular(phi, H)
    cam_pose = tm.caminho_cabo(tm.THETA_POSE, H)
    xs = np.arange(30.0, 45.0 + 1e-9, 0.001)
    ext = caminho[None, :] - (cam_pose - xs[:, None])
    g = np.where(ext > 0, ext, 0.0)*m[None, :]/1000
    k = (g @ y)/np.einsum("ij,ij->i", g, g)
    rmse = np.sqrt(np.mean((k[:, None]*g - y[None, :])**2, axis=1))
    j = int(np.argmin(rmse))
    return {"x_pose": float(xs[j]), "k": float(k[j]), "rmse": float(rmse[j])}


def h_restricao_extensao(patente, l_pose=tm.L_POSE):
    """h em que, com X_POSE e K reidentificados, δ_max = L_LIVRE (análise
    alternativa; a restrição de projeto exata não está registrada no código)."""
    th, y = patente["theta_star"], patente["torque"]
    xs = np.arange(30.0, 45.0 + 1e-9, 0.001)
    thf = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 1501)
    anterior = None
    for h in np.arange(22.0, 23.5 + 1e-9, 0.005):
        q = tm.calculate_q(th)
        s = tm.calculate_tangent_span(tm.calculate_rho(q, h))
        phi = tm.calculate_phi(q, s, h)
        caminho = tm.comprimento_caminho(q, s, phi)
        m = tm.braco_perpendicular(phi, h)
        cam_pose = tm.caminho_cabo(tm.THETA_POSE, h)
        ext = caminho[None, :] - (cam_pose - xs[:, None])
        g = np.where(ext > 0, ext, 0.0)*m[None, :]/1000
        k = (g @ y)/np.einsum("ij,ij->i", g, g)
        j = int(np.argmin(np.mean((k[:, None]*g - y[None, :])**2, axis=1)))
        razao = (tm.caminho_cabo(thf, h) - (cam_pose - xs[j])).max()/(l_pose - xs[j])
        if anterior is not None and anterior[1] < 1.0 <= razao:
            return float(h)
        anterior = (h, razao)
    return None


def tabela_patente(patente, calc, res):
    linhas = ["indice;theta_star_grau;phi_pat_grau;elevacao_grau;"
              "torque_extraido_up;torque_modelo_up;residuo_up"]
    for i, (t, y) in enumerate(zip(patente["theta_star"], patente["torque"]), 1):
        linhas.append(";".join([str(i)] + [
            f"{v:.6f}".replace(".", ",") for v in
            (t, phi_pat(t), elevacao(t), y, calc[i - 1], res[i - 1])]))
    (PASTA/"tcc_tabela_patente.csv").write_text("\n".join(linhas) + "\n",
                                                encoding="utf-8")


# ---------------------------------------------------------------- figuras

def figura_geometria():
    th = tm.THETA_POSE
    q = tm.calculate_q(th)
    s = tm.calculate_tangent_span(tm.calculate_rho(q, H))
    phi = tm.calculate_phi(q, s, H)
    A = np.array(tm.calculate_base_vector(H))
    Pc = -tm.C*np.array([np.cos(q), np.sin(q)])
    T = tm.ponto_tangencia(q, phi)
    u = np.array([np.cos(phi), np.sin(phi)])
    m = tm.braco_perpendicular(phi, H)
    pe = A + (-A @ u)*u                       # pé da perpendicular de O à linha do cabo

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.9), dpi=200,
                                   facecolor=SUPERFICIE,
                                   gridspec_kw={"width_ratios": [1.9, 1]})
    alcas = []
    for ax in (ax1, ax2):
        eixos(ax)
        ax.set_aspect("equal")
        ax.add_patch(plt.Circle(Pc, tm.R, fill=False, color=TINTA_2, lw=1.2))
        alcas = [
            ax.plot([0, Pc[0]], [0, Pc[1]], color=TINTA, lw=2.2,
                    label="elo O → D (comprimento C)")[0],
            ax.plot([A[0], T[0]], [A[1], T[1]], color=AZUL, lw=1.8,
                    label="vão reto s (A → T), linha de ação do cabo")[0],
            ax.plot([0, A[0]], [0, A[1]], color=LARANJA, lw=1.8,
                    label="vetor fixo B (O → A)")[0],
            ax.plot([0, pe[0]], [0, pe[1]], color=VERDE, lw=1.6, ls="--",
                    label=f"braço perpendicular m = {m:.2f} mm".replace(".", ","))[0],
            ax.plot([0, T[0]], [0, T[1]], color=TINTA_2, lw=1.0, ls=":",
                    label="distância b (O → T), não é braço de momento")[0],
        ]
        ax.xaxis.set_major_formatter(virgula(0))
        ax.yaxis.set_major_formatter(virgula(0))
        ax.set_xlabel("x (mm)", color=TINTA_2)
    pontos = {"O": (np.zeros(2), (6, -12)), "A": (A, (6, 2)),
              "D": (Pc, (6, -12)), "T": (T, (-4, 6))}
    for nome, (p, desloc) in pontos.items():
        for ax in (ax1, ax2):
            ax.plot(*p, "o", color=TINTA, ms=4, zorder=5)
        ax1.annotate(nome, p, xytext=desloc, textcoords="offset points",
                     fontsize=8, color=TINTA)
    for nome in ("O", "A"):
        p, desloc = pontos[nome]
        ax2.annotate(nome, p, xytext=desloc, textcoords="offset points",
                     fontsize=8, color=TINTA)
    ax1.set_ylabel("y (mm)", color=TINTA_2)
    ax1.set_ylim(-50, 35)
    ax2.set_xlim(-40, 30)
    ax2.set_ylim(-15, 35)
    fig.legend(handles=alcas, loc="lower center", ncol=3, frameon=False,
               fontsize=7.5)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.98, bottom=0.30, wspace=0.15)
    fig.savefig(PASTA/"tcc_fig1_geometria.png", facecolor=SUPERFICIE)
    plt.close(fig)
    return {"A": A.tolist(), "Pc": Pc.tolist(), "T": T.tolist(), "m": float(m),
            "phi_grau": float(np.degrees(phi)), "q_grau": float(np.degrees(q)),
            "s": float(s)}


def figura_ajuste(patente, met):
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 1501)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5.6), dpi=200,
                                   facecolor=SUPERFICIE, sharex=True,
                                   gridspec_kw={"height_ratios": [2.4, 1]})
    for ax in (ax1, ax2):
        eixos(ax)
    ax1.axhline(0, color=TINTA_2, lw=0.8)
    ax1.plot(th, cabo(th), color=AZUL, lw=2, label="modelo congelado (−τ)")
    ax1.plot(patente["theta_star"], patente["torque"], "o", color=TINTA, ms=4,
             label="pontos extraídos da patente", zorder=5)
    ax1.set_ylabel("Torque do cabo (N·m)", color=TINTA_2)
    ax1.legend(loc="upper left", frameon=False, fontsize=8)
    ax2.axhline(0, color=TINTA_2, lw=0.8)
    ax2.vlines(patente["theta_star"], 0, met["res"], color=AZUL, lw=1.6)
    ax2.plot(patente["theta_star"], met["res"], "o", color=AZUL, ms=3.5)
    ax2.set_ylabel("Resíduo (N·m)", color=TINTA_2)
    ax2.set_xlabel("θ* (graus)", color=TINTA_2)
    for ax in (ax1, ax2):
        ax.xaxis.set_major_formatter(virgula(0))
        ax.yaxis.set_major_formatter(virgula(0))
    fig.tight_layout()
    fig.savefig(PASTA/"tcc_fig2_ajuste.png", facecolor=SUPERFICIE)
    plt.close(fig)


def figura_rmse(varredura):
    linhas = [l for l in varredura["linhas"] if l["fechamento"]]
    hs = np.array([l["h"] for l in linhas])
    rm = np.array([l["rmse"] for l in linhas])
    viavel = varredura["faixas"]["viavel"]
    platos = varredura["platos"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=200,
                                   facecolor=SUPERFICIE,
                                   gridspec_kw={"width_ratios": [1.5, 1]})
    for ax in (ax1, ax2):
        eixos(ax)
    ax1.axvspan(viavel["min"], viavel["max"], color=VERDE, alpha=0.12,
                label="h fisicamente viáveis")
    ax1.plot(hs, rm, color=AZUL, lw=2, label="RMSE(h), K congelado")
    ax1.axvline(H, color=LARANJA, lw=1.4, label="H_CALIBRADO")
    ax1.axvline(tm.H_CAD, color=TINTA_2, lw=1.2, ls="--", label="H_CAD")
    ax1.set_yscale("log")
    ax1.set_xlabel("h (mm)", color=TINTA_2)
    ax1.set_ylabel("RMSE (N·m), escala log", color=TINTA_2)
    ax1.xaxis.set_major_formatter(virgula(0))
    ax1.legend(loc="upper right", frameon=False, fontsize=7)
    sel = (hs >= 21.6) & (hs <= 23.9)
    cores = {1.01: "#86b6ef", 1.05: "#5598e7", 1.10: "#2a78d6", 2.00: "#184f95"}
    for f in (2.00, 1.10, 1.05, 1.01):
        p = platos[f]
        ax2.axvspan(p["min"], p["max"], color=cores[f], alpha=0.18,
                    label=f"RMSE ≤ {f:.2f}·mín".replace(".", ","))
    ax2.plot(hs[sel], rm[sel], color=AZUL, lw=2)
    ax2.axvline(H, color=LARANJA, lw=1.4)
    ax2.set_xlabel("h (mm)", color=TINTA_2)
    ax2.set_ylabel("RMSE (N·m)", color=TINTA_2)
    ax2.xaxis.set_major_formatter(virgula(1))
    ax2.yaxis.set_major_formatter(virgula(1))
    ax2.legend(loc="upper center", frameon=False, fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(PASTA/"tcc_fig4_rmse_h.png", facecolor=SUPERFICIE)
    plt.close(fig)


def figura_familia(patente):
    """Família torque × θ* para os h de tm.VH_FAMILIA, com K congelado; nós da
    família pela mesma função da passada de varredura."""
    familia = tm.VH_FAMILIA
    nos = tm.vh_nos_da_familia(familia, tm.VH_THETA)
    rampa = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#184f95", "#0d366b"]
    outros = sorted(h for h in familia if h != H)
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=200, facecolor=SUPERFICIE)
    eixos(ax)
    ax.axhline(0, color=TINTA_2, lw=0.8)
    for j, (theta_no, _) in enumerate(nos["nos"]):
        ax.axvline(theta_no, color=TINTA_2, lw=0.8, ls=":",
                   label="nós da família" if j == 0 else None)
    for i, h in enumerate(outros):
        cor = rampa[round(i*(len(rampa) - 1)/max(len(outros) - 1, 1))]
        ax.plot(tm.VH_THETA, nos["curvas"][list(familia).index(h)], color=cor,
                lw=1.5, label=f"h = {h:g} mm".replace(".", ","))
    ax.plot(tm.VH_THETA, nos["curvas"][list(familia).index(H)], color=LARANJA,
            lw=2.6, label=f"h = {H:g} mm (adotado)".replace(".", ","))
    ax.plot(patente["theta_star"], patente["torque"], "o", color=TINTA, ms=4,
            label="pontos extraídos da patente", zorder=5)
    ax.set_xlabel("θ* (graus)", color=TINTA_2)
    ax.set_ylabel("Torque do cabo (N·m)", color=TINTA_2)
    ax.xaxis.set_major_formatter(virgula(0))
    ax.yaxis.set_major_formatter(virgula(0))
    alcas, nomes = ax.get_legend_handles_labels()
    ordem = sorted(range(len(nomes)), key=lambda k: (
        0 if nomes[k].startswith("h =") else 1,
        float(nomes[k].split()[2].replace(",", ".")) if nomes[k].startswith("h =")
        else 0))
    ax.legend([alcas[k] for k in ordem], [nomes[k] for k in ordem],
              loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False,
              fontsize=8)
    fig.subplots_adjust(left=0.08, right=0.74, bottom=0.12, top=0.97)
    fig.savefig(PASTA/"tcc_fig3_familia.png", facecolor=SUPERFICIE)
    plt.close(fig)


def verificacoes_complementares(patente, varredura):
    """Números citados no TCC que não saem das funções acima."""
    th, y = patente["theta_star"], patente["torque"]
    thf = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 1501)

    def lei_antiga(h, x_pose):
        """Lei anterior (δ pelo vão reto s, sem o arco), ancorada na pose."""
        q = tm.calculate_q(th)
        s = tm.calculate_tangent_span(tm.calculate_rho(q, h))
        m = tm.braco_perpendicular(tm.calculate_phi(q, s, h), h)
        qp = tm.calculate_q(tm.THETA_POSE)
        ext = s - (tm.calculate_tangent_span(tm.calculate_rho(qp, h)) - x_pose)
        g = np.where(ext > 0, ext, 0.0)*m/1000
        k = (g @ y)/(g @ g)
        return float(k), float(np.sqrt(np.mean((k*g - y)**2)))

    xs = np.arange(30.0, 45.0 + 1e-9, 0.01)
    antiga = min((lei_antiga(H, x)[1], x, lei_antiga(H, x)[0]) for x in xs)
    giro = np.radians(np.linspace(tm.THETA_MIN, tm.THETA_MAX, 150101)
                      - tm.THETA_POSE + tm.ALPHA + 90.0 - tm.ANGLE_OFFSET)
    x_cg = tm.CG_DX_MM*np.cos(giro) - tm.CG_DY_MM*np.sin(giro)
    troca = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 150101)[
        np.where(np.diff(np.sign(x_cg)))[0]]
    linhas = varredura["linhas"]
    r_cad = tm.calculate_torque_curve(K, tm.H_CAD, thf)
    pico_peso = float(tm.torque_peso(thf).max())
    oa = float(np.hypot(H, tm.P))
    calc_pontos = cabo(th)
    return {
        "m_theta_min": float(tm.calculate_torque_curve(K, H, [tm.THETA_MIN])["m"][0]),
        "curso_h": {str(h): float(np.ptp(tm.caminho_cabo(thf, h)))
                    for h in (15.0, H, 60.0)},
        "lei_antiga_x_pose_congelado": lei_antiga(H, tm.X_POSE),
        "lei_antiga_x_pose_reidentificado": {"rmse": antiga[0], "x_pose": antiga[1],
                                             "k": antiga[2]},
        "tv_max_grade": max(l["trabalho_virtual"] for l in linhas),
        "tv_max_viaveis": max(l["trabalho_virtual"] for l in linhas if l["viavel"]),
        "linearidade_k_max_grade": max(l["erro_linear_K"] for l in linhas),
        "theta_troca_sinal_x_cg": troca.tolist(),
        "b_h_cad": [float(r_cad["b"].min()), float(r_cad["b"].max())],
        "pico_modelo_nos_pontos": float(calc_pontos.max()),
        "theta_pico_modelo_nos_pontos": float(th[np.argmax(calc_pontos)]),
        "forca_para_pico_peso_n": pico_peso/(oa/1000),
        "razao_pico_cabo_pico_peso": float(cabo(thf).max())/pico_peso,
        "razao_b_min_m_max": float(tm.calculate_torque_curve(K, H, thf)["b"].min())/oa,
    }


COMP_ELEVACOES = (35.0, 45.0, 60.0, 75.0, 90.0, 105.0, 120.0, 135.0, 150.0, 165.0)


def compensacao():
    """Torque do cabo (N·m, escala adotada no TCC) contra o torque do peso, em
    função da elevação: razão cabo/peso e excedente cabo − peso."""
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 150101)
    elev = elevacao(th)
    c, p = cabo(th), tm.torque_peso(th)
    ordem = np.argsort(elev)
    e_o, c_o, p_o = elev[ordem], c[ordem], p[ordem]
    pontos = [{"elev": e, "theta": float(tm.ANGLE_OFFSET + 90.0 - e),
               "cabo": float(np.interp(e, e_o, c_o)), "peso": float(np.interp(e, e_o, p_o)),
               "razao": float(np.interp(e, e_o, c_o)/np.interp(e, e_o, p_o))}
              for e in COMP_ELEVACOES]
    razao = c_o/p_o
    sel = (e_o >= 30.0) & (e_o <= 170.0) & (p_o > 0)
    i_um = np.where(np.diff(np.sign(razao[sel] - 1.0)))[0]
    i_pp = int(np.argmax(p))
    faixa = (e_o >= 60.0) & (e_o <= 150.0)
    return {
        "pontos": pontos,
        "elev_razao_1": [float(e_o[sel][i]) for i in i_um],
        "cabo_no_pico_peso": float(c[i_pp]), "razao_no_pico_peso": float(c[i_pp]/p[i_pp]),
        "razao_60_150": [float(razao[faixa].min()), float(razao[faixa].max())],
        "media_razao_60_150": float(np.mean(razao[faixa])),
        "excedente_max": float(np.max(c - p)), "elev_excedente_max": float(elev[np.argmax(c - p)]),
    }


def figura_compensacao():
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 1501)
    elev = elevacao(th)
    c, p = cabo(th), tm.torque_peso(th)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=200, facecolor=SUPERFICIE)
    for ax in (ax1, ax2):
        eixos(ax)
    ax1.axhline(0, color=TINTA_2, lw=0.8)
    ax1.plot(elev, c, color=AZUL, lw=2, label="torque do cabo")
    ax1.plot(elev, p, color=LARANJA, lw=2, label="torque do peso")
    ax1.set_xlabel("Elevação anatômica do braço (graus)", color=TINTA_2)
    ax1.set_ylabel("Torque (N·m)", color=TINTA_2)
    ax1.legend(loc="upper right", frameon=False, fontsize=8)
    sel = (elev >= 32.0) & (elev <= 170.0)
    ax2.plot(elev[sel], c[sel]/p[sel], color=AZUL, lw=2)
    ax2.axhline(1.0, color=TINTA_2, lw=0.8, ls=":")
    ax2.set_xlabel("Elevação anatômica do braço (graus)", color=TINTA_2)
    ax2.set_ylabel("Torque do cabo / torque do peso", color=TINTA_2)
    for ax in (ax1, ax2):
        ax.xaxis.set_major_formatter(virgula(0))
        ax.yaxis.set_major_formatter(virgula(0))
    fig.tight_layout()
    fig.savefig(PASTA/"tcc_fig6_compensacao.png", facecolor=SUPERFICIE)
    plt.close(fig)


def figura_normalizada(cruzamentos):
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 1501)
    c = cabo(th)
    p = tm.torque_peso(th)
    elev = elevacao(th)
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200, facecolor=SUPERFICIE)
    eixos(ax)
    ax.axhline(0, color=TINTA_2, lw=0.8)
    ax.plot(elev, c/c.max(), color=AZUL, lw=2,
            label="torque do cabo / pico")
    ax.plot(elev, p/p.max(), color=LARANJA, lw=2,
            label="torque do peso / pico")
    for e in cruzamentos:
        ax.axvline(e, color=TINTA_2, lw=0.8, ls=":")
    ax.set_xlabel("Elevação anatômica do braço (graus)", color=TINTA_2)
    ax.set_ylabel("Torque normalizado (adimensional)", color=TINTA_2)
    ax.xaxis.set_major_formatter(virgula(0))
    ax.yaxis.set_major_formatter(virgula(2))
    ax.legend(loc="upper right", frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(PASTA/"tcc_fig5_normalizado.png", facecolor=SUPERFICIE)
    plt.close(fig)


def main():
    PASTA.mkdir(exist_ok=True)
    patente = load_patent_data()
    met = metricas_ajuste(patente)
    mec = grandezas_mecanismo()
    norm = comparacao_normalizada()
    auto = tm.autotestes(H)
    with contextlib.redirect_stdout(io.StringIO()):
        varredura = tm.varredura_h(plot_familia=True, plot_perfil=False,
                                   plot_curvas=False)
    alternativo = perfil_alternativo(patente)
    ident = identificacao_no_h_adotado(patente)
    h_restricao = h_restricao_extensao(patente)
    geo = figura_geometria()
    figura_ajuste(patente, met)
    figura_familia(patente)
    figura_rmse(varredura)
    figura_normalizada(norm["cruzamentos_elev"])
    figura_compensacao()
    tabela_patente(patente, met["calc"], met["res"])

    linha = {round(l["h"], 9): l for l in varredura["linhas"]}
    lcad, lcal = linha[round(tm.H_CAD, 9)], linha[round(H, 9)]
    calc = [l for l in varredura["linhas"] if l["fechamento"]]
    otimo = min(calc, key=lambda l: l["rmse"])
    alt_min = min(alternativo, key=lambda l: l["rmse"])
    numeros = {
        "parametros": {"K": K, "H_CALIBRADO": H, "H_CAD": tm.H_CAD,
                       "X_POSE": tm.X_POSE, "L_POSE": tm.L_POSE,
                       "L_LIVRE": tm.L_LIVRE, "ALPHA": tm.ALPHA, "P": tm.P,
                       "C": tm.C, "R": tm.R, "THETA_POSE": tm.THETA_POSE,
                       "ANGLE_OFFSET": tm.ANGLE_OFFSET, "THETA_MIN": tm.THETA_MIN,
                       "THETA_MAX": tm.THETA_MAX, "MASS_KG": tm.MASS_KG,
                       "CG": [tm.CG_DX_MM, tm.CG_DY_MM],
                       "d_cg": float(np.hypot(tm.CG_DX_MM, tm.CG_DY_MM))},
        "patente": {"n": int(len(patente["theta_star"])),
                    "theta_min": float(patente["theta_star"].min()),
                    "theta_max": float(patente["theta_star"].max()),
                    "torque_max": float(patente["torque"].max()),
                    "theta_torque_max": float(patente["theta_star"][np.argmax(patente["torque"])]),
                    "media": float(patente["torque"].mean())},
        "ajuste": {k: v for k, v in met.items() if k not in ("calc", "res")},
        "autotestes": {k: float(v) for k, v in auto.items()},
        "mecanismo": mec,
        "normalizada": norm,
        "compensacao": compensacao(),
        "geometria_pose": geo,
        "varredura": {
            "n": len(varredura["linhas"]),
            "h_menor_rmse": otimo["h"], "rmse_min": otimo["rmse"],
            "r2_min": otimo["r2"],
            "platos": {str(f): {"min": p["min"], "max": p["max"],
                                "largura": p["largura"], "n": p["n"]}
                       for f, p in varredura["platos"].items()},
            "degradacao": {str(f): v for f, v in
                           varredura["degradacao"]["fatores"].items()},
            "fronteira_tracao": varredura["fronteira_tracao"],
            "viavel": varredura["faixas"]["viavel"],
            "h_dc_entra": varredura["h_dc_entra"],
            "h_dc_sai_formula": varredura["h_dc_sai_formula"],
            "nos": varredura["familia"]["nos"],
            "abertura_maxima": varredura["familia"]["maximo"],
            "erro_ancora": varredura["erro_ancora"],
            "posto_h_cal": lcal["posto_rmse"],
            "h_cad": {k: lcad[k] for k in ("rmse", "r2", "delta_min",
                                           "theta_delta_min", "posto_rmse",
                                           "motivo", "mola_max", "delta_max")},
        },
        "identificacao_no_h_adotado": ident,
        "complementares": verificacoes_complementares(patente, varredura),
        "h_delta_max_igual_l_livre": h_restricao,
        "alternativo_x_pose_livre": {
            "h_min": alt_min["h"], "rmse_min": alt_min["rmse"],
            "x_pose_min": alt_min["x_pose"], "k_min": alt_min["k"],
            "razao_ext_livre_min": alt_min["razao_ext_livre"],
            "perfil": alternativo,
        },
    }
    (PASTA/"tcc_numeros.json").write_text(
        json.dumps(numeros, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in numeros.items()
                      if k not in ("alternativo_x_pose_livre",)},
                     indent=1, ensure_ascii=False)[:6000])
    print("perfil alternativo (h, X_POSE, K, RMSE, δmax/L_LIVRE):")
    for l in alternativo[::8]:
        print(f"  {l['h']:6.2f} {l['x_pose']:7.2f} {l['k']:9.2f} {l['rmse']:8.4f} "
              f"{l['razao_ext_livre']:7.3f}")
    print("mínimo alternativo:", {k: round(v, 4) for k, v in alt_min.items()})


if __name__ == "__main__":
    main()
