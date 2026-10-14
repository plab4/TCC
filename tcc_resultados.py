"""
Números e figuras citados no TCC, gerados a partir do modelo vigente.

Não altera torque_model.py nem os parâmetros congelados: importa o modelo,
chama as funções com h explícito e grava

    results/tcc_numeros.json          todos os números citados no texto
    results/tcc_tabela_patente.csv     rastreabilidade dos 29 pontos extraídos
    results/tcc_fig1_geometria.png     laço vetorial na pose de referência
    results/tcc_fig2_ajuste.png        torque do cabo × pontos extraídos
    results/tcc_fig3_familia.png       família de curvas, K congelado
    results/tcc_fig4_efeito_h.png      efeito de h sobre o torque entregue
    results/tcc_fig_folga.png          torque com folga de cabo, h > fronteira de tração
    results/tcc_fig5_normalizado.png   perfis normalizados do cabo e do peso

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
    """Torque do cabo na convenção da patente (−τ do modelo), em u.p."""
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
    ax1.set_ylabel("Torque do cabo (u.p.)", color=TINTA_2)
    ax1.legend(loc="upper left", frameon=False, fontsize=8)
    ax2.axhline(0, color=TINTA_2, lw=0.8)
    ax2.vlines(patente["theta_star"], 0, met["res"], color=AZUL, lw=1.6)
    ax2.plot(patente["theta_star"], met["res"], "o", color=AZUL, ms=3.5)
    ax2.set_ylabel("Resíduo (u.p.)", color=TINTA_2)
    ax2.set_xlabel("θ* (graus)", color=TINTA_2)
    for ax in (ax1, ax2):
        ax.xaxis.set_major_formatter(virgula(0))
        ax.yaxis.set_major_formatter(virgula(0))
    fig.tight_layout()
    fig.savefig(PASTA/"tcc_fig2_ajuste.png", facecolor=SUPERFICIE)
    plt.close(fig)


EH_FAIXA = (90.0, 150.0)        # elevação: trabalho acima da linha dos ombros
EH_TABELA = (8.0, 12.0, 16.0, 20.0, H, 25.0, 28.0, 30.0)
EH_MARGENS = (10.0, 5.0, 2.0)   # extensão mínima exigida da mola (mm)


def _retorno(h, th, el):
    """Torque devolvido com K e X_POSE congelados: pico, média na faixa de
    trabalho, trabalho devolvido na faixa toda e restrições físicas."""
    c = cabo(th, h)
    ordem = np.argsort(el)
    e_o, c_o = el[ordem], c[ordem]
    faixa = (e_o >= EH_FAIXA[0]) & (e_o <= EH_FAIXA[1])
    ext = tm.vh_extensao(h, th)
    return {
        "h": float(h), "pico": float(c.max()), "elev_pico": float(el[np.argmax(c)]),
        "media_trabalho": float(np.trapezoid(c_o[faixa], e_o[faixa])/(EH_FAIXA[1] - EH_FAIXA[0])),
        "trabalho": float(np.trapezoid(c_o, np.radians(e_o))),
        "tau_90": float(np.interp(90.0, e_o, c_o)),
        "tau_150": float(np.interp(150.0, e_o, c_o)),
        "elev_pm": float(elevacao(tm.ponto_morto(h))),
        "delta_min": float(ext.min()), "delta_max": float(ext.max()),
        "mola_max": float(tm.L_LIVRE + ext.max()),
        "razao_ext_livre": float(ext.max()/tm.L_LIVRE),
        "forca_max": float(K*ext.max()),
    }


H_MAX_CAD = 76.846              # mm, maior h que o CAD admite (posição física da ancoragem)


def limites_h():
    """Validade física de h de 8 mm até o limite geométrico do CAD, em passo de
    0,005 mm, com K e X_POSE congelados: fechamento, trabalho virtual, tração
    e comprimento máximo da mola contra o alojamento (L_CARCACA)."""
    grade = np.unique(np.append(np.arange(8.0, H_MAX_CAD, 0.005), [H, tm.H_CAD, H_MAX_CAD]))
    th = tm.VH_THETA
    fech, tv, tracao, mola = [], [], [], []
    for h in grade:
        q = tm.calculate_q(th)
        rho = tm.calculate_rho(q, h)
        fech.append(bool(np.all(rho > tm.R)))
        tv.append(float(tm.residuo_trabalho_virtual(h)))
        ext = tm.vh_extensao(h, th)
        tracao.append(bool(np.all(ext >= 0)))
        mola.append(float(tm.L_LIVRE + ext.max()))
    tracao, mola = np.array(tracao), np.array(mola)
    viaveis = grade[tracao]
    i = int(np.argmax(mola > tm.L_CARCACA))
    a, b = grade[i - 1], grade[i]
    for _ in range(60):
        c = 0.5*(a + b)
        if tm.L_LIVRE + tm.vh_extensao(c, th).max() > tm.L_CARCACA:
            b = c
        else:
            a = c
    th_f = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 1501)
    return {
        "n": int(len(grade)), "h_max_cad": H_MAX_CAD,
        "fechamento_todos": bool(all(fech)), "tv_max": float(max(tv)),
        "tracao_n": int(tracao.sum()), "tracao_max": float(viaveis.max()),
        "tracao_contigua": bool(np.all(tracao[:tracao.sum()])),
        "h_alojamento": float(0.5*(a + b)),
        "no_cad": {"delta_min": float(tm.vh_extensao(H_MAX_CAD, th).min()),
                   "mola_max": float(mola[-1] if grade[-1] == H_MAX_CAD else
                                     tm.L_LIVRE + tm.vh_extensao(H_MAX_CAD, th).max()),
                   "curso": float(np.ptp(tm.caminho_cabo(th_f, H_MAX_CAD))),
                   "rho_min": float(tm.calculate_rho(tm.calculate_q(th), H_MAX_CAD).min())},
    }


FOLGA_H = (32.88631833613309, 35.0, 40.0, 45.0, 50.0, 60.0, 70.0, H_MAX_CAD)


def cenario_folga():
    """h acima da fronteira de tração, com a mola e a montagem atuais: o cabo
    afrouxa no início da faixa (braço alto) e ali o torque é nulo, pela
    saturação de calculate_delta. Ignora o alojamento da mola."""
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 15011)
    el = elevacao(th)
    ordem = np.argsort(el)
    e_o = el[ordem]
    faixa = (e_o >= EH_FAIXA[0]) & (e_o <= EH_FAIXA[1])
    peso = tm.torque_peso(th)
    linhas = []
    for h in FOLGA_H:
        c = cabo(th, h)
        ext = tm.vh_extensao(h, th)
        frouxo = el[ext < 0]
        c_o = c[ordem]
        inicio = float(frouxo.min()) if frouxo.size else None
        linhas.append({
            "h": float(h), "folga_de": inicio,
            "peso_no_inicio": float(np.interp(inicio, e_o, peso[ordem])) if inicio else None,
            "pico": float(c.max()), "elev_pico": float(el[np.argmax(c)]),
            "media_trabalho": float(np.trapezoid(c_o[faixa], e_o[faixa])/(EH_FAIXA[1] - EH_FAIXA[0])),
            "trabalho": float(np.trapezoid(c_o, np.radians(e_o))),
            "tau_150": float(np.interp(150.0, e_o, c_o)),
            "elev_pm": float(elevacao(tm.ponto_morto(h))),
            "delta_min": float(ext.min()), "forca_max": float(K*max(ext.max(), 0.0)),
        })
    grade = np.arange(32.89, H_MAX_CAD, 0.01)
    medias = []
    for h in grade:
        c_o = cabo(th, h)[ordem]
        medias.append(np.trapezoid(c_o[faixa], e_o[faixa]))
    return {"linhas": linhas, "media_monotona": bool(np.all(np.diff(medias) > 0)),
            "peso_pico": float(peso.max())}


def figura_folga():
    """Torque devolvido ao longo da elevação para h acima da fronteira de
    tração (cabo frouxo no braço alto) e início da zona sem assistência."""
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 3001)
    el = elevacao(th)
    hs = (40.0, 50.0, 60.0, 70.0, H_MAX_CAD)
    rampa = ["#86b6ef", "#5598e7", "#2a78d6", "#184f95", "#0d366b"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.4), dpi=200, facecolor=SUPERFICIE,
                               gridspec_kw={"width_ratios": [1.6, 1]})
    for ax in (a, b):
        eixos(ax)
    a.axhline(0, color=TINTA_2, lw=0.8)
    a.plot(el, cabo(th, H), color=LARANJA, lw=2.4, label="h = 22,701 mm (adotado)")
    a.plot(el, cabo(th, 32.88631833613309), color=TINTA_2, lw=1.4, ls="--",
           label="h = 32,886 mm (fronteira de tração)")
    for h, cor in zip(hs, rampa):
        ext = tm.vh_extensao(h, th)
        a.plot(el, cabo(th, h), color=cor, lw=1.6, label=f"h = {h:g} mm".replace(".", ","))
        if np.any(ext < 0):
            a.plot(el[ext < 0].min(), 0, "o", color=cor, ms=4, zorder=5)
    a.set_xlabel("Elevação anatômica do braço (graus)", color=TINTA_2)
    a.set_ylabel("Torque do cabo (u.p.)", color=TINTA_2)
    a.legend(loc="upper right", frameon=False, fontsize=7)
    grade = np.arange(33.0, H_MAX_CAD + 1e-9, 0.25)
    inicio = []
    for h in grade:
        ext = tm.vh_extensao(h, th)
        inicio.append(el[ext < 0].min())
    b.plot(grade, inicio, color=AZUL, lw=2)
    b.fill_between(grade, inicio, 180.1, color=AZUL, alpha=0.12, label="cabo frouxo, sem assistência")
    b.axhline(90.0, color=TINTA_2, lw=0.8, ls=":")
    b.set_ylim(80, 182)
    b.set_xlabel("h (mm)", color=TINTA_2)
    b.set_ylabel("Elevação em que a assistência cessa (graus)", color=TINTA_2)
    b.legend(loc="lower left", frameon=False, fontsize=7)
    for ax in (a, b):
        ax.xaxis.set_major_formatter(virgula(0))
        ax.yaxis.set_major_formatter(virgula(0))
    fig.tight_layout()
    fig.savefig(PASTA/"tcc_fig_folga.png", facecolor=SUPERFICIE)
    plt.close(fig)


TODOS_H = (8.0, 12.0, 16.0, 20.0, H, 25.0, 28.0, 30.0, 32.88631833613309, 35.0, 40.0, 50.0,
           60.0, 70.0, H_MAX_CAD)


def h_todos():
    """Torque devolvido para h de 8 mm ao limite do CAD, com a mola e a montagem
    atuais. Acima da fronteira de tração o cabo afrouxa no braço alto; ali o
    torque é nulo. Registra também a descontinuidade da derivada no início da
    folga: o torque vai a zero de forma contínua, mas com inclinação finita."""
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 150001)
    el = elevacao(th)
    th_r = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 15011)   # mesma malha de efeito_h
    el_r = elevacao(th_r)
    linhas = []
    for h in TODOS_H:
        l = _retorno(h, th_r, el_r)
        ext = tm.vh_extensao(h, th)
        frouxo = np.where(ext < 0)[0]
        l["folga_de"] = None
        if frouxo.size:
            j = frouxo.max() + 1                       # primeiro ponto tracionado
            c = cabo(th[j:j + 101], h)
            inclin = (c[100] - c[0])/abs(el[j + 100] - el[j])
            l.update(folga_de=float(el[j]), contigua=bool(frouxo.min() == 0 and
                     np.all(np.diff(frouxo) == 1)), torque_no_limiar=float(cabo(th[[j]], h)[0]),
                     inclinacao_limiar=float(inclin))
        linhas.append(l)
    grade = np.arange(8.0, H_MAX_CAD + 1e-9, 0.05)
    media = [_retorno(h, th_r, el_r)["media_trabalho"] for h in grade]
    return {"linhas": linhas, "media_monotona_ate_cad": bool(np.all(np.diff(media) > 0))}


def figura_familia_h(patente):
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 1501)
    hs = np.arange(8.0, H_MAX_CAD, 4.0).tolist() + [H_MAX_CAD]
    import matplotlib.colors as mcolors
    cmap = mcolors.LinearSegmentedColormap.from_list("h", ["#b9d4f5", "#2a78d6", "#0b2a52"])
    norma = mcolors.Normalize(vmin=8.0, vmax=H_MAX_CAD)
    fig, ax = plt.subplots(figsize=(9.6, 5.0), dpi=200, facecolor=SUPERFICIE)
    eixos(ax)
    ax.axhline(0, color=TINTA_2, lw=0.8)
    for h in hs:
        ax.plot(th, cabo(th, h), color=cmap(norma(h)), lw=1.1)
    ax.plot(th, cabo(th, 32.88631833613309), color=TINTA_2, lw=1.3, ls="--",
            label="h = 32,886 mm, fronteira de tração")
    ax.plot(th, cabo(th, H), color=LARANJA, lw=2.6, label="h = 22,701 mm, identificado")
    ax.plot(patente["theta_star"], patente["torque"], "o", color=TINTA, ms=4, zorder=6,
            label="pontos extraídos da patente")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norma)
    barra = fig.colorbar(sm, ax=ax, pad=0.02)
    barra.set_label("h (mm)", color=TINTA_2)
    barra.ax.yaxis.set_major_formatter(virgula(0))
    ax.set_xlabel("θ* (graus)", color=TINTA_2)
    ax.set_ylabel("Torque do cabo (u.p.)", color=TINTA_2)
    topo = ax.secondary_xaxis("top", functions=(lambda t: tm.ANGLE_OFFSET + 90.0 - t,
                                                lambda e: tm.ANGLE_OFFSET + 90.0 - e))
    topo.set_xlabel("Elevação anatômica do braço (graus)", color=TINTA_2)
    topo.tick_params(colors=TINTA_2)
    topo.xaxis.set_major_formatter(virgula(0))
    ax.xaxis.set_major_formatter(virgula(0))
    ax.yaxis.set_major_formatter(virgula(0))
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(PASTA/"tcc_fig3_familia_h.png", facecolor=SUPERFICIE)
    plt.close(fig)


def figura_indicadores_h():
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 3001)
    el = elevacao(th)
    grade = np.arange(8.0, H_MAX_CAD + 1e-9, 0.1)
    L = [_retorno(h, th, el) for h in grade]
    col = lambda k: np.array([l[k] for l in L])
    folga = []
    for h in grade:
        ext = tm.vh_extensao(h, th)
        folga.append(el[ext < 0].min() if np.any(ext < 0) else np.nan)
    hf = 32.88631833613309
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.4), dpi=200, facecolor=SUPERFICIE, sharex=True)
    (a, b), (c, d) = axs
    for ax in axs.flat:
        eixos(ax)
        ax.axvspan(hf, H_MAX_CAD, color=TINTA_2, alpha=0.07)
        ax.axvline(H, color=LARANJA, lw=1.4)
        ax.axvline(hf, color=TINTA_2, lw=1.1, ls="--")
    a.plot(grade, col("pico"), color=AZUL, lw=2, label="pico")
    a.plot(grade, col("media_trabalho"), color=TINTA_2, lw=1.6, ls=":", label="média de 90° a 150°")
    a.set_ylabel("Torque devolvido (u.p.)", color=TINTA_2)
    a.legend(loc="upper left", frameon=False, fontsize=7.5)
    b.plot(grade, folga, color=AZUL, lw=2)
    b.set_ylim(130, 182)
    b.set_ylabel("Elevação do início da folga (graus)", color=TINTA_2)
    c.plot(grade, col("delta_min"), color=AZUL, lw=2)
    c.axhline(0, color=TINTA_2, lw=0.8)
    c.set_ylabel("Extensão mínima da mola (mm)", color=TINTA_2)
    d.plot(grade, col("elev_pm"), color=AZUL, lw=2)
    d.set_ylabel("Elevação do ponto morto (graus)", color=TINTA_2)
    for ax in (c, d):
        ax.set_xlabel("h (mm)", color=TINTA_2)
    for ax in axs.flat:
        ax.xaxis.set_major_formatter(virgula(0))
        ax.yaxis.set_major_formatter(virgula(0))
    from matplotlib.ticker import MultipleLocator
    d.yaxis.set_major_locator(MultipleLocator(4))
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    fig.legend(handles=[Line2D([], [], color=LARANJA, lw=1.4), Line2D([], [], color=TINTA_2, lw=1.1, ls="--"),
                        Patch(color=TINTA_2, alpha=0.15)],
               labels=["h identificado (22,701 mm)", "fronteira de tração (32,886 mm)",
                       "cabo frouxo em parte da faixa"],
               loc="lower center", ncol=3, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(PASTA/"tcc_fig4_indicadores_h.png", facecolor=SUPERFICIE)
    plt.close(fig)


def efeito_h():
    """Otimização de h para o maior torque devolvido, com K e X_POSE
    congelados, sujeita às restrições físicas (tração, fechamento, trabalho
    virtual) e, opcionalmente, a uma margem mínima de extensão da mola."""
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 15011)
    el = elevacao(th)
    h_lim = 32.88631833613309
    grade = np.append(np.arange(8.0, h_lim, 0.01), h_lim)
    linhas = [_retorno(h, th, el) for h in grade]
    monotono = {k: bool(np.all(np.diff([l[k] for l in linhas]) > 0))
                for k in ("pico", "media_trabalho", "trabalho")}
    otimo = _retorno(h_lim, th, el)
    hs = np.array([l["h"] for l in linhas])
    dm = np.array([l["delta_min"] for l in linhas])
    margens = []
    for mg in EH_MARGENS:
        h_mg = float(np.interp(mg, dm[::-1], hs[::-1]))
        margens.append({"margem": mg, **_retorno(h_mg, th, el)})
    ref = _retorno(H, th, el)
    tabela = sorted([_retorno(h, th, el) for h in EH_TABELA] + [otimo], key=lambda l: l["h"])
    return {"linhas": linhas, "tabela": tabela, "otimo": otimo, "margens": margens,
            "adotado": ref, "monotono": monotono, "faixa": list(EH_FAIXA)}

def figura_efeito_h(ef):
    L = ef["linhas"]
    hs = np.array([l["h"] for l in L])
    def col(k):
        return np.array([l[k] for l in L])
    hx = ef["otimo"]["h"]
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.4), dpi=200, facecolor=SUPERFICIE, sharex=True)
    (a, b), (c, d) = axs
    for ax in axs.flat:
        eixos(ax)
        ax.axvline(H, color=LARANJA, lw=1.4)
        ax.axvline(hx, color=VERDE, lw=1.2, ls="--")
    a.plot(hs, col("pico"), color=AZUL, lw=2, label="pico")
    a.plot(hs, col("media_trabalho"), color=TINTA_2, lw=1.6, ls=":", label="média de 90° a 150°")
    a.set_ylabel("Torque devolvido (u.p.)", color=TINTA_2)
    a.legend(loc="upper left", frameon=False, fontsize=7.5)
    b.plot(hs, col("trabalho"), color=AZUL, lw=2)
    b.set_ylabel("Trabalho devolvido na faixa (u.p.·rad)", color=TINTA_2)
    c.plot(hs, col("delta_min"), color=AZUL, lw=2)
    c.axhline(0.0, color=TINTA_2, lw=0.8)
    for m in ef["margens"]:
        c.plot(m["h"], m["margem"], "o", color=TINTA, ms=3.5, zorder=5)
    c.set_ylabel("Extensão mínima da mola (mm)", color=TINTA_2)
    d.plot(hs, col("elev_pm"), color=AZUL, lw=2)
    d.axhline(30.0, color=TINTA_2, lw=0.8, ls=":")
    d.set_ylabel("Elevação do ponto morto (graus)", color=TINTA_2)
    for ax in (c, d):
        ax.set_xlabel("h (mm)", color=TINTA_2)
    for ax in axs.flat:
        ax.xaxis.set_major_formatter(virgula(0))
        ax.yaxis.set_major_formatter(virgula(0))
    from matplotlib.lines import Line2D
    fig.legend(handles=[Line2D([], [], color=LARANJA, lw=1.4),
                        Line2D([], [], color=VERDE, lw=1.2, ls="--")],
               labels=["h adotado (22,701 mm)",
                       f"maior torque devolvido, fronteira de tração ({hx:.3f} mm)".replace(".", ",")],
               loc="lower center", ncol=2, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(PASTA/"tcc_fig4_efeito_h.png", facecolor=SUPERFICIE)
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
    ax.set_ylabel("Torque do cabo (u.p.)", color=TINTA_2)
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


def figura_normalizada(cruzamentos):
    th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 1501)
    c = cabo(th)
    p = tm.torque_peso(th)
    elev = elevacao(th)
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200, facecolor=SUPERFICIE)
    eixos(ax)
    ax.axhline(0, color=TINTA_2, lw=0.8)
    ax.plot(elev, c/c.max(), color=AZUL, lw=2,
            label="torque do cabo / pico (u.p./u.p.)")
    ax.plot(elev, p/p.max(), color=LARANJA, lw=2,
            label="torque do peso / pico (N·m/N·m)")
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
    efeito = efeito_h()
    figura_efeito_h(efeito)
    figura_folga()
    figura_familia_h(patente)
    figura_indicadores_h()
    figura_normalizada(norm["cruzamentos_elev"])
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
        "efeito_h": {k: v for k, v in efeito.items() if k != "linhas"},
        "limites_h": limites_h(),
        "cenario_folga": cenario_folga(),
        "h_todos": h_todos(),
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
