"""
Números e figuras do apêndice da Ottobock (EP 3 504 033 B1) no TCC, gerados
a partir do modelo vigente torque_model_ottobock.py.

Não altera o modelo nem seus parâmetros: importa as funções, chama-as com e
explícito e grava

    results/ottobock_tcc_numeros.json            todos os números citados no apêndice
    results/ottobock_tcc_fig_a1_geometria.png    circuito na pose do CAD e no regime II
    results/ottobock_tcc_fig_a2_fig16.png        pontos da Fig. 16 e ajustes de s0
    results/ottobock_tcc_fig_a3_projeto.png      projeto padrão contra o torque do peso
    results/ottobock_tcc_fig_a4_normalizado.png  formas normalizadas na faixa de s0
    results/ottobock_tcc_fig_a5_familia.png      família em e (τ/K e razão exo/peso)

Além do ajuste por curva de torque_model_ottobock.ajustar_fig16, calcula duas
verificações que o modelo não faz: o ajuste conjunto das três curvas com uma
só escala c (mesmo atuador e mesmo eixo y, como descreve [0093] da patente) e
o ajuste com força constante (forma limite de s0 → −∞).

Convenção angular: θ_el é a anteversão do braço (0° pendente, 90° horizontal
à frente), chamada theta_star no código; λ é o ângulo do trecho e da
alavanca, chamado q no código.

Rodar:  python tcc_resultados_ottobock.py
"""
import contextlib
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

import torque_model_ottobock as tmo

PASTA = Path(__file__).parent/"results"
E = tmo.E_CAD
FAIXA = tmo.FIG16_FAIXA_AJUSTE
THETA = tmo.VE_THETA                      # 0° a 180°, passo 0,1°
SUPERFICIE, TINTA, TINTA_2, GRADE = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
AZUL, LARANJA, VERDE = "#2a78d6", "#eb6834", "#1baf7a"
COR = {"pontilhada": AZUL, "tracejada": LARANJA, "continua": VERDE}
ESTILO = {"pontilhada": ":", "tracejada": "--", "continua": "-"}
NOME = {"pontilhada": "pontilhada", "tracejada": "tracejada", "continua": "contínua"}
ORDEM = ("pontilhada", "tracejada", "continua")   # pré-tensão crescente, [0093]


def virgula(casas):
    return FuncFormatter(lambda x, pos: f"{x:.{casas}f}".replace(".", ","))


def eixos(ax, casas_x=0, casas_y=1):
    ax.set_facecolor(SUPERFICIE)
    ax.grid(color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(TINTA_2)
    ax.tick_params(colors=TINTA_2)
    ax.xaxis.set_major_formatter(virgula(casas_x))
    ax.yaxis.set_major_formatter(virgula(casas_y))


def montar(braco_pose=None):
    """Geometria do CAD, com a opção de trocar só o sinal de BRACO_POSE."""
    par = dict(tmo.PARAMETROS_CAD)
    if braco_pose is not None:
        par["BRACO_POSE"] = braco_pose
    alpha = tmo.derivar_alpha(par["GAMMA"])
    phi = tmo.derivar_phi(par["PHI_ABS_POSE"], par["Q_POSE"])
    delta = tmo.derivar_delta(par["Q_POSE"], par["BRACO_POSE"])
    theta_pose = tmo.derivar_theta_pose(par["BRACO_POSE"])
    geo = tmo.montar_geometria(par["C1"], par["C2"], alpha, par["GAMMA"],
                               par["C3"], par["BETA"], par["P"], phi, delta)
    return par, geo, {"alpha": alpha, "phi": phi, "delta": delta,
                      "theta_pose": theta_pose}


def conjunto_humano(par):
    return tmo.montar_conjunto_braco(
        tmo.ESTATURA, tmo.MASSA_CORPORAL, tmo.DE_LEVA_TAB4,
        (tmo.MASSA_BRACO_EXO, tmo.CG_BRACO_EXO_FUSION, tmo.IZZ_CG_BRACO_EXO),
        tmo.O_FUSION, par["BRACO_POSE"])


def circuito(theta, e, geo):
    """λ, regime, ℓ, φ e braço m em θ_el (graus)."""
    q = tmo.calculate_q(theta, geo)
    contato, s, psi = tmo.resolver_circuito(q, e, geo)
    return q, contato, s, psi, tmo.braco_momento(q, psi, e, geo, contato)


def theta_transicao(e, geo):
    q = tmo.q_estrela_numerico(e, geo, tmo.calculate_q(THETA, geo))
    return None if q is None else float(tmo.theta_star_de_q(q, geo)), q


def dados_ajuste(fig16, e, geo, peso):
    """Pontos usados (faixa estrita) e grandezas do circuito por curva."""
    saida = {}
    for nome in ORDEM:
        th, r = fig16[nome]["theta"], fig16[nome]["razao"]
        usar = (th > FAIXA[0]) & (th < FAIXA[1])
        q, contato, s, psi, b = circuito(th[usar], e, geo)
        saida[nome] = {"th": th[usar], "r": r[usar], "s": s, "b": b,
                       "tp": np.abs(tmo.torque_peso(th[usar], *peso)),
                       "contato": contato}
    return saida


def metricas(c, mu, r):
    res = c*mu - r
    i = int(np.argmax(np.abs(res)))
    return {"rms": float(np.sqrt(np.mean(res**2))),
            "rms_max": float(np.sqrt(np.mean(res**2))/np.max(r)),
            "mae": float(np.mean(np.abs(res))),
            "erro_max": float(abs(res[i])), "i_erro_max": i,
            "r2": float(1 - np.sum(res**2)/np.sum((r - r.mean())**2)),
            "zonas_sinal": int(1 + np.count_nonzero(np.diff(np.sign(res)))),
            "residuo_medio": float(np.mean(res))}


def ajuste_conjunto(d, grade):
    """Uma escala c comum às três curvas e um s0 por curva.

    Com c ótimo em forma fechada, SSE = Σr² − (Σμr)²/(Σμ²); a busca maximiza
    (Σμr)²/(Σμ²) por descida coordenada na grade de s0 (0,01 mm), a partir de
    vários pontos iniciais, e refina cada s0 por Brent limitado.
    """
    from scipy.optimize import minimize_scalar
    nomes = list(d)
    M = {n: tmo.calculate_x(d[n]["s"][None, :], grade[:, None])*d[n]["b"]
         / (1000.0*d[n]["tp"]) for n in nomes}
    num = {n: M[n] @ d[n]["r"] for n in nomes}
    den = {n: np.einsum("ij,ij->i", M[n], M[n]) for n in nomes}
    rr = sum(float(d[n]["r"] @ d[n]["r"]) for n in nomes)

    def sse_indices(idx):
        nu = sum(num[n][i] for n, i in zip(nomes, idx))
        de = sum(den[n][i] for n, i in zip(nomes, idx))
        return np.inf if de == 0 else rr - nu**2/de

    melhor = (np.inf, None)
    partidas = [0, 10000, 20000, 30000, 38000]
    for i0 in partidas:
        for j0 in partidas:
            for k0 in partidas:
                idx = [i0, j0, k0]
                for _ in range(60):
                    antigo = list(idx)
                    for a, n in enumerate(nomes):
                        nu_o = sum(num[m][i] for m, i in zip(nomes, idx) if m != n)
                        de_o = sum(den[m][i] for m, i in zip(nomes, idx) if m != n)
                        with np.errstate(divide="ignore", invalid="ignore"):
                            sse = rr - (nu_o + num[n])**2/(de_o + den[n])
                        sse[(de_o + den[n]) == 0] = np.inf
                        idx[a] = int(np.argmin(sse))
                    if idx == antigo:
                        break
                v = sse_indices(idx)
                if v < melhor[0]:
                    melhor = (v, list(idx))
    s0 = [float(grade[i]) for i in melhor[1]]

    def sse_de(vals):
        mus = [tmo.modelo_fig16(d[n]["s"], d[n]["b"], d[n]["tp"], v)
               for n, v in zip(nomes, vals)]
        nu = sum(float(m @ d[n]["r"]) for m, n in zip(mus, nomes))
        de = sum(float(m @ m) for m in mus)
        return rr - nu**2/de, nu/de, mus

    passo = grade[1] - grade[0]
    for _ in range(3):
        for a in range(len(nomes)):
            if s0[a] <= grade[0] or s0[a] >= grade[-1]:
                continue

            def f(v, a=a):
                vals = list(s0)
                vals[a] = v
                return sse_de(vals)[0]
            busca = minimize_scalar(f, bounds=(s0[a] - passo, s0[a] + passo),
                                    method="bounded", options={"xatol": 1e-10})
            if busca.fun <= f(s0[a]):
                s0[a] = float(busca.x)
    sse, c, mus = sse_de(s0)
    por_curva = {n: {"s0": v, "limite": (v <= grade[0]) or (v >= grade[-1]),
                     **metricas(c, mu, d[n]["r"])}
                 for n, v, mu in zip(nomes, s0, mus)}
    ntot = sum(len(d[n]["r"]) for n in nomes)
    return {"c": c, "sse": sse, "rms_total": float(np.sqrt(sse/ntot)),
            "por_curva": por_curva}


def ajuste_forca_constante(d):
    """Força constante: μ_F = m/(1000·|τ_g|); só a escala c é ajustada."""
    saida = {}
    for n, v in d.items():
        mu = v["b"]/(1000.0*v["tp"])
        c = float(mu @ v["r"])/float(mu @ mu)
        saida[n] = {"c": c, **metricas(c, mu, v["r"])}
    return saida


def inicio_curva(th, r):
    """θ em que a curva digitalizada cruza zero (interpolação linear entre os
    dois primeiros pontos, se houver troca de sinal)."""
    if r[0] <= 0 < r[1]:
        return float(th[0] - r[0]*(th[1] - th[0])/(r[1] - r[0]))
    return None


def cruzamentos(theta, y):
    i = np.where(y[:-1]*y[1:] < 0)[0]
    return [float(theta[k] - y[k]*(theta[k + 1] - theta[k])/(y[k + 1] - y[k]))
            for k in i]


def main():
    PASTA.mkdir(exist_ok=True)
    par, geo, der = montar()
    bx, by = tmo.calculate_base_vector(geo)
    conj = conjunto_humano(par)
    tmo.autoteste_conjunto(conj)
    peso = tmo.argumentos_peso(conj)
    fig16 = tmo.load_fig16(tmo.FIG16_CSV)
    N = {}

    # ---------------------------------------------------------- geometria
    q_pose = tmo.calculate_q(der["theta_pose"], geo)
    th_t, q_t = theta_transicao(E, geo)
    s_I, psi_I = tmo.resolver_regime_I(q_t, E, geo)
    b_t = float(tmo.braco_momento(q_t, psi_I, E, geo, False))
    geo0 = geo._replace(p=0.0)
    th_t0, q_t0 = theta_transicao(E, geo0)
    P_pose, C_pose = tmo.ponto_P(q_pose, E, geo), tmo.ponto_78(q_pose, geo)
    _, s_pose, _ = tmo.resolver_circuito(q_pose, E, geo)
    N["geometria"] = {
        "parametros_cad": par, "E_CAD": E, "derivados": der,
        "B": [float(bx), float(by)], "modulo_B": float(np.hypot(bx, by)),
        "direcao_B": float(np.degrees(np.arctan2(by, bx))),
        "d78": tmo.calculate_d(E, geo), "x78": float(tmo.calculate_x78(E, geo)),
        "raio_OP": float(tmo.raio_OP(E, geo)),
        "angulo_OP": float(np.degrees(tmo.angulo_OP(E, geo))),
        "P_pose": P_pose.tolist(), "C78_pose": C_pose.tolist(),
        "s_pose_modelo": float(s_pose),
        "erro_s_pose": abs(float(s_pose) - par["S_POSE"]),
        "lambda_t": float(np.degrees(q_t)), "theta_t": th_t,
        "s_t": float(s_I), "b_t": b_t,
        "lambda_t_p0": float(np.degrees(q_t0)), "theta_t_p0": th_t0,
        "lambda_t_p0_fechado": float(np.degrees(tmo.q_estrela_fechado(E, geo0))),
        "lambda_faixa": [float(np.degrees(tmo.calculate_q(0.0, geo))),
                         float(np.degrees(tmo.calculate_q(180.0, geo)))],
    }
    qg, cg, sg, pg, bg = circuito(THETA, E, geo)
    N["geometria"].update(
        m_max=float(bg.max()), theta_m_max=float(THETA[np.argmax(bg)]),
        m_min=float(bg.min()), theta_m_min=float(THETA[np.argmin(bg)]),
        l_0=float(sg[0]), l_180=float(sg[-1]), curso=float(sg[0] - sg[-1]),
        regime_II=[float(THETA[cg].min()), float(THETA[cg].max())])
    angs = [0.0, 10.0, th_t, 30.0, 60.0, 90.0, der["theta_pose"], 120.0, 150.0,
            180.0]
    q, contato, s, psi, b = circuito(np.array(angs), E, geo)
    N["tabela_geometria"] = [
        {"theta": float(t), "lambda": float(np.degrees(qq)),
         "regime": "II" if c else "I", "l": float(ss), "phi": float(np.degrees(pp)),
         "l_menos_d": float(ss - tmo.calculate_d(E, geo)) if c else None,
         "m": float(bb)}
        for t, qq, c, ss, pp, bb in zip(angs, q, contato, s, psi, b)]

    # ---------------------------------------------------------- massa
    corpos = []
    for c in conj["corpos"]:
        d_o = float(np.hypot(*c["pos"]))
        corpos.append({"nome": c["nome"], "massa": c["massa"],
                       "d": d_o, "izz_cg": c["izz_cg"]/1e6,
                       "izz_o": (c["izz_cg"] + c["massa"]*d_o**2)/1e6})
    seg = [{"nome": nome, "massa_pct": mp, "L": L, "cm_pct": cm, "r_pct": rp}
           for nome, mp, L, cm, rp in tmo.DE_LEVA_TAB4]
    N["massa"] = {"humano": conj["humano"], "total": conj["total"],
                  "exo_incluido": conj["exo_incluido"], "corpos": corpos,
                  "segmentos_de_leva": seg,
                  "tau_g_pico": abs(float(tmo.torque_peso(90.0, *peso))),
                  "braco_exo": {"massa_g": tmo.MASSA_BRACO_EXO,
                                "cg_fusion": list(tmo.CG_BRACO_EXO_FUSION),
                                "izz_cg_gmm2": tmo.IZZ_CG_BRACO_EXO}}

    # ---------------------------------------------------------- Fig. 16
    desc = {}
    for n in ORDEM:
        th, r = fig16[n]["theta"], fig16[n]["razao"]
        usar = (th > FAIXA[0]) & (th < FAIXA[1])
        desc[n] = {"n_total": int(th.size), "n_usado": int(usar.sum()),
                   "theta_min": float(th.min()), "theta_max": float(th.max()),
                   "r_max": float(r.max()), "theta_r_max": float(th[np.argmax(r)]),
                   "inicio": inicio_curva(th, r)}
    N["fig16"] = {"curvas": desc, "pixels_por_divisao": 21.1311,
                  "erro_mediano_px": 0.5,
                  "erro_mediano_div": 0.5/21.1311}

    ajustes = {n: tmo.ajustar_fig16(fig16[n]["theta"], fig16[n]["razao"], E,
                                    geo, peso, FAIXA, tmo.FIG16_GRADE_S0,
                                    tmo.FIG16_FOLGA_FAIXA, tmo.ALVO_FRACAO,
                                    tmo.THETA_ALVO) for n in ORDEM}
    d = dados_ajuste(fig16, E, geo, peso)
    ind = {}
    for n in ORDEM:
        aj = ajustes[n]
        mu = tmo.modelo_fig16(d[n]["s"], d[n]["b"], d[n]["tp"], aj["s0"])
        ind[n] = {k: aj[k] for k in ("s0", "limite", "c", "n", "rms", "rms_max",
                                     "faixa_s0", "faixa_contigua", "faixa_na_borda",
                                     "todos_regime_I", "x_alvo", "b_alvo",
                                     "tau_peso_alvo", "k_alvo", "forca_alvo")}
        ind[n].update(metricas(aj["c"], mu, d[n]["r"]))
        ind[n]["theta_erro_max"] = float(d[n]["th"][ind[n]["i_erro_max"]])
        ind[n]["escala_div"] = aj["k_alvo"]/aj["c"]
    grade = (tmo.FIG16_GRADE_S0[0] + tmo.FIG16_GRADE_S0[2]
             * np.arange(int(round((tmo.FIG16_GRADE_S0[1] - tmo.FIG16_GRADE_S0[0])
                                   / tmo.FIG16_GRADE_S0[2])) + 1))
    conjunto = ajuste_conjunto(d, grade)
    constante = ajuste_forca_constante(d)
    N["ajuste"] = {"individual": ind, "conjunto": conjunto,
                   "forca_constante": constante}

    # ------------------------------------------------- projeto padrão
    aj = ajustes[tmo.CURVA_PROJETO]
    K = aj["k_alvo"]
    defs0 = tmo.definir_s0("c", s0_fixo=aj["s0"], origem="tracejada")
    r = tmo.calculate_torque_curve(K, E, geo, defs0, THETA)
    tp = np.abs(tmo.torque_peso(THETA, *peso))
    i_pico = int(np.argmax(r["tau"]))
    with np.errstate(divide="ignore", invalid="ignore"):
        razao = r["tau"]/tp
    angs = np.array(tmo.THETA_TABELA_PROJETO)
    rt = tmo.calculate_torque_curve(K, E, geo, defs0, angs)
    tpt = np.abs(tmo.torque_peso(angs, *peso))
    N["projeto"] = {
        "s0": aj["s0"], "K": K, "tau_pico": float(r["tau"][i_pico]),
        "theta_pico": float(THETA[i_pico]),
        "x_max": float(r["x"].max()), "theta_x_max": float(THETA[np.argmax(r["x"])]),
        "x_min": float(r["x"].min()), "theta_x_min": float(THETA[np.argmin(r["x"])]),
        "frouxo": tmo.trechos_frouxos(THETA, r["extensao"]),
        "tau_min": float(r["tau"].min()), "theta_tau_min": float(THETA[np.argmin(r["tau"])]),
        "razao_pico": float(razao[i_pico]),
        "F_max": float(r["force"].max()), "F_min": float(r["force"].min()),
        "tabela": [{"theta": float(t), "lambda": float(np.degrees(qq)),
                    "regime": "II" if c else "I", "l": float(ss), "x": float(xx),
                    "m": float(bb), "F": float(ff), "tau": float(tt),
                    "tau_g": float(g), "razao": float(tt/g)}
                   for t, qq, c, ss, xx, bb, ff, tt, g in zip(
                       angs, rt["q"], rt["contato"], rt["s"], rt["x"],
                       rt["braco"], rt["force"], rt["tau"], tpt)],
    }

    # sensibilidade dentro da faixa de identificação (tracejada)
    sens = []
    for rot, s0 in (("faixa_min", aj["faixa_s0"][0]), ("s0", aj["s0"]),
                    ("faixa_max", aj["faixa_s0"][1])):
        qa, ca, sa, pa, ba = circuito(np.array([90.0]), E, geo)
        xa = float(tmo.calculate_x(sa, s0)[0])
        Ks = tmo.ALVO_FRACAO*float(tp[np.argmin(np.abs(THETA - 90))])/(xa*float(ba[0])/1000)
        ds = tmo.definir_s0("c", s0_fixo=s0)
        rs = tmo.calculate_torque_curve(Ks, E, geo, ds, THETA)
        ip = int(np.argmax(rs["tau"]))
        with np.errstate(divide="ignore", invalid="ignore"):
            rz = rs["tau"]/tp
        sens.append({"caso": rot, "s0": s0, "K": Ks,
                     "tau_pico": float(rs["tau"][ip]), "theta_pico": float(THETA[ip]),
                     "x_0": float(rs["x"][0]), "x_180": float(rs["x"][-1]),
                     "razao": {str(int(a)): float(rz[np.argmin(np.abs(THETA - a))])
                               for a in (30, 60, 120, 150)}})
    N["sensibilidade_s0"] = sens

    # formas normalizadas (independem de K)
    sel = (THETA >= FAIXA[0]) & (THETA <= FAIXA[1])
    norm = {}
    for caso in sens:
        ds = tmo.definir_s0("c", s0_fixo=caso["s0"])
        t1 = tmo.calculate_torque_curve(1.0, E, geo, ds, THETA)["tau"]
        dif = t1/t1.max() - tp/tp.max()
        norm[caso["caso"]] = {
            "theta_pico_exo": float(THETA[np.argmax(t1)]),
            "cruzamentos": cruzamentos(THETA, dif),
            "dif_max": float(dif[sel].max()), "theta_dif_max": float(THETA[sel][np.argmax(dif[sel])]),
            "dif_min": float(dif[sel].min()), "theta_dif_min": float(THETA[sel][np.argmin(dif[sel])]),
            "dif_10": float(dif[np.argmin(np.abs(THETA - 10))])}
    N["normalizado"] = {"theta_pico_peso": float(THETA[np.argmax(tp)]), "casos": norm}

    # ---------------------------------------------------------- família em e
    fam = []
    curvas = {}
    for ee in tmo.VE_FAMILIA:
        re_ = tmo.calculate_torque_curve(K, ee, geo, defs0, THETA)
        ip = int(np.argmax(re_["tau"]))
        tt, _ = theta_transicao(ee, geo)
        with np.errstate(divide="ignore", invalid="ignore"):
            rz = re_["tau"]/tp
        curvas[ee] = (re_["tau"], rz)
        fam.append({"e": ee, "d78": tmo.calculate_d(ee, geo), "theta_t": tt,
                    "tau_pico": float(re_["tau"][ip]), "theta_pico": float(THETA[ip]),
                    "tau_90": float(re_["tau"][np.argmin(np.abs(THETA - 90))]),
                    "razao_90": float(rz[np.argmin(np.abs(THETA - 90))]),
                    "x_min": float(re_["extensao"].min()),
                    "x_max": float(re_["extensao"].max())})
    e_lo, e_hi = min(tmo.VE_FAMILIA), max(tmo.VE_FAMILIA)
    cruz = cruzamentos(THETA[1:-1], (curvas[e_hi][0] - curvas[e_lo][0])[1:-1])
    N["familia"] = {"linhas": fam, "cruzamentos_e_extremos": cruz}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        v = tmo.varredura_e(geo, K, defs0, THETA, tmo.VE_GRID, tmo.VE_FAMILIA,
                            tmo.EXTRACAO_EP, tmo.SINAL_PATENTE, peso,
                            tmo.ALVO_FRACAO, PASTA, plot_familia=False,
                            rotulo_projeto="projeto padrão", sufixo="_tcc")
    for arq in ("ve_varredura_e_tcc.csv", "ve_e_notaveis_tcc.csv"):
        (PASTA/arq).unlink(missing_ok=True)
    N["varredura"] = {
        "n": len(v["linhas"]), "faixas": v["faixas"],
        "nos": [list(x) for x in v["familia"]["nos"]],
        "abertura_max": list(v["familia"]["maximo"]),
        "tv_max": max(l["trabalho_virtual"] for l in v["linhas"] if l["fechamento"]),
        "theta_t": [min(l["theta_estrela"] for l in v["linhas"]),
                    max(l["theta_estrela"] for l in v["linhas"])]}

    # ------------------------------------------------- sinal de BRACO_POSE
    par_b, geo_b, der_b = montar(-par["BRACO_POSE"])
    peso_b = tmo.argumentos_peso(conjunto_humano(par_b))
    aj_b = tmo.ajustar_fig16(fig16[tmo.CURVA_PROJETO]["theta"],
                             fig16[tmo.CURVA_PROJETO]["razao"], E, geo_b, peso_b,
                             FAIXA, tmo.FIG16_GRADE_S0, tmo.FIG16_FOLGA_FAIXA,
                             tmo.ALVO_FRACAO, tmo.THETA_ALVO)
    N["braco_pose_invertido"] = {
        "BRACO_POSE": par_b["BRACO_POSE"], "delta": der_b["delta"],
        "theta_pose": der_b["theta_pose"], "theta_t": theta_transicao(E, geo_b)[0],
        "s0": aj_b["s0"], "c": aj_b["c"], "rms_max": aj_b["rms_max"],
        "faixa_s0": aj_b["faixa_s0"], "k_alvo": aj_b["k_alvo"],
        "n_regime_II": aj_b["n_regime_II"]}

    # ---------------------------------------------------------- verificações
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        a = tmo.autotestes(E, geo, K, defs0, THETA, e_extra=(E + 10.0, 0.5*E, 2.0*E),
                           theta_pose_cad=der["theta_pose"], s_pose_cad=par["S_POSE"])
    N["verificacoes"] = {k: (v if not isinstance(v, (np.floating,)) else float(v))
                         for k, v in a.items() if k not in ("p_zero", "frouxo")}
    N["verificacoes"]["p_zero"] = {k: v for k, v in a["p_zero"].items()
                                   if k != "q_fechado"}
    N["verificacoes"]["q_estrela"] = float(np.degrees(a["q_estrela"]))

    figuras(N, fig16, ajustes, conjunto, d, geo, peso, der, K, defs0, r, tp,
            curvas, sens)
    with open(PASTA/"ottobock_tcc_numeros.json", "w", encoding="utf-8") as f:
        json.dump(N, f, ensure_ascii=False, indent=1, default=float)
    print(f"números: {PASTA/'ottobock_tcc_numeros.json'}")


def figuras(N, fig16, ajustes, conjunto, d, geo, peso, der, K, defs0, r, tp,
            curvas, sens):
    # ------------------------------------------- A.1 geometria
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.6), dpi=200,
                                 facecolor=SUPERFICIE,
                                 gridspec_kw={"width_ratios": [1, 1.5]})
    A = tmo.ponto_A(geo)
    poses = ((der["theta_pose"], LARANJA, "pose do CAD, regime I"),
             (10.0, AZUL, r"$\theta_{el}$ = 10°, regime II"))
    for ax in (a1, a2):
        eixos(ax, 0, 0)
        ax.set_aspect("equal")
        for th, cor, rot in poses:
            q = tmo.calculate_q(th, geo)
            cot = E*tmo.versor(q)
            P = tmo.ponto_P(q, E, geo)
            C = tmo.ponto_78(q, geo)
            contato = tmo.em_contato(q, E, geo)
            braco = 300*tmo.versor(tmo.direcao_braco(th))
            ax.plot([0, braco[0]], [0, braco[1]], color=cor, lw=1.0, ls=":",
                    label=f"eixo do braço, {rot}" if ax is a2 else None)
            ax.plot([0, cot[0], P[0]], [0, cot[1], P[1]], color=TINTA, lw=2.0)
            via = [A, C, P] if contato else [A, P]
            ax.plot([p[0] for p in via], [p[1] for p in via], color=cor, lw=1.6,
                    label=f"elástico, {rot}" if ax is a2 else None)
            ax.plot(*C, "s", color=cor, ms=4.5, zorder=5)
            ax.plot(*P, "o", color=cor, ms=4.5, zorder=5)
        ax.plot(0, 0, "o", color=TINTA, ms=5, zorder=6)
    a1.plot(*A, "o", color=TINTA, ms=5)
    a1.annotate("A", A, xytext=(6, 0), textcoords="offset points", fontsize=8)
    a1.annotate("O", (0, 0), xytext=(6, -10), textcoords="offset points", fontsize=8)
    a1.set_xlim(-150, 250)
    a1.set_ylim(-360, 70)
    a2.set_xlim(-75, 60)
    a2.set_ylim(-45, 45)
    a2.annotate("O", (0, 0), xytext=(5, -11), textcoords="offset points", fontsize=8)
    for ax in (a1, a2):
        ax.set_xlabel("x (mm)", color=TINTA_2)
    a1.set_ylabel("y (mm)", color=TINTA_2)
    a2.plot([], [], "o", color=TINTA_2, ms=4.5, label="P (fim do cotovelo C3)")
    a2.plot([], [], "s", color=TINTA_2, ms=4.5, label="centro do elemento 78")
    a2.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False,
              fontsize=7)
    fig.tight_layout()
    fig.savefig(PASTA/"ottobock_tcc_fig_a1_geometria.png", facecolor=SUPERFICIE)
    plt.close(fig)

    # ------------------------------------------- A.2 Fig. 16 e ajustes
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.4), dpi=200, facecolor=SUPERFICIE,
                            sharey=True)
    for k, ax in enumerate(axs):
        eixos(ax, 0, 1)
        ax.axvspan(*FAIXA, color=GRADE, alpha=0.6, lw=0)
        ax.axhline(0, color=TINTA_2, lw=0.8)
        for n in ORDEM:
            th, rr = fig16[n]["theta"], fig16[n]["razao"]
            usar = (th > FAIXA[0]) & (th < FAIXA[1])
            ax.plot(th[~usar], rr[~usar], "o", color="#9a9994", ms=3)
            ax.plot(th[usar], rr[usar], "o", color=COR[n], ms=3.5,
                    markeredgecolor=SUPERFICIE, markeredgewidth=0.6)
            tg = np.linspace(th.min(), th.max(), 500)
            q, ct, ss, ps, bb = circuito(tg, E, geo)
            tpg = np.abs(tmo.torque_peso(tg, *peso))
            if k == 0:
                c, s0 = ajustes[n]["c"], ajustes[n]["s0"]
            else:
                c, s0 = conjunto["c"], conjunto["por_curva"][n]["s0"]
            ax.plot(tg, c*tmo.modelo_fig16(ss, bb, tpg, s0), color=COR[n], lw=1.8,
                    ls=ESTILO[n], label=f"{NOME[n]}")
        ax.set_xlim(0, 180)
        ax.set_ylim(-0.2, 5.0)
        ax.set_xlabel(r"Anteversão do braço, $\theta_{el}$ (graus)", color=TINTA_2)
    axs[0].set_ylabel("Razão de torques (divisões da grade)", color=TINTA_2)
    axs[0].text(0.02, 0.97, "(a) escala c por curva", transform=axs[0].transAxes,
                va="top", fontsize=8, color=TINTA)
    axs[1].text(0.02, 0.97, "(b) escala c comum", transform=axs[1].transAxes,
                va="top", fontsize=8, color=TINTA)
    axs[1].plot([], [], "o", color="#9a9994", ms=3, label="fora da faixa do ajuste")
    axs[1].legend(loc="center left", bbox_to_anchor=(0.02, 0.7), frameon=False,
                  fontsize=7.5)
    fig.tight_layout()
    fig.savefig(PASTA/"ottobock_tcc_fig_a2_fig16.png", facecolor=SUPERFICIE)
    plt.close(fig)

    # ------------------------------------------- A.3 projeto padrão
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200, facecolor=SUPERFICIE)
    eixos(ax, 0, 1)
    ax.axhline(0, color=TINTA_2, lw=0.8)
    ax.plot(THETA, tp, color=LARANJA, lw=2, label=r"$|\tau_g|$, membro humano")
    ax.plot(THETA, tmo.ALVO_FRACAO*tp, color=LARANJA, lw=1.6, ls="--",
            label=r"0,4 $|\tau_g|$ (alvo, hipótese)")
    ax.plot(THETA, r["tau"], color=AZUL, lw=2, label="τ do elástico, projeto padrão")
    th_t = N["geometria"]["theta_t"]
    ax.axvline(th_t, color=TINTA_2, lw=0.8, ls=":")
    ax.annotate(("transição de regime, $\\theta_{el}$ = " + f"{th_t:.2f}°").replace(".", ","),
                (th_t, 9.6), xytext=(4, 0), textcoords="offset points",
                fontsize=7.5, color=TINTA)
    for t in (30, 60, 90, 120, 150):
        j = int(np.argmin(np.abs(THETA - t)))
        ax.plot(THETA[j], r["tau"][j], "o", color=AZUL, ms=4.5,
                markeredgecolor=SUPERFICIE)
        ax.annotate(f"{r['tau'][j]/tp[j]:.2f}".replace(".", ","),
                    (THETA[j], r["tau"][j]), xytext=(0, -13),
                    textcoords="offset points", ha="center", fontsize=7.5,
                    color=TINTA)
    ax.set_xlim(0, 180)
    ax.set_xlabel(r"Anteversão do braço, $\theta_{el}$ (graus)", color=TINTA_2)
    ax.set_ylabel("Torque (N·m)", color=TINTA_2)
    ax.legend(loc="upper right", frameon=False, fontsize=7.5)
    fig.tight_layout()
    fig.savefig(PASTA/"ottobock_tcc_fig_a3_projeto.png", facecolor=SUPERFICIE)
    plt.close(fig)

    # ------------------------------------------- A.4 formas normalizadas
    fig, ax = plt.subplots(figsize=(8, 4.0), dpi=200, facecolor=SUPERFICIE)
    eixos(ax, 0, 1)
    formas = {}
    for caso in sens:
        ds = tmo.definir_s0("c", s0_fixo=caso["s0"])
        t1 = tmo.calculate_torque_curve(1.0, E, geo, ds, THETA)["tau"]
        formas[caso["caso"]] = t1/t1.max()
    ax.fill_between(THETA, np.minimum(formas["faixa_min"], formas["faixa_max"]),
                    np.maximum(formas["faixa_min"], formas["faixa_max"]),
                    color=AZUL, alpha=0.18, lw=0,
                    label="elástico, s0 na faixa de identificação")
    ax.plot(THETA, formas["s0"], color=AZUL, lw=2, label="elástico, s0 ajustado")
    ax.plot(THETA, tp/tp.max(), color=LARANJA, lw=2, label="peso do membro humano")
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel(r"Anteversão do braço, $\theta_{el}$ (graus)", color=TINTA_2)
    ax.set_ylabel("Torque normalizado pelo pico", color=TINTA_2)
    ax.legend(loc="lower center", frameon=False, fontsize=7.5)
    fig.tight_layout()
    fig.savefig(PASTA/"ottobock_tcc_fig_a4_normalizado.png", facecolor=SUPERFICIE)
    plt.close(fig)

    # ------------------------------------------- A.5 família em e
    rampa = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=200,
                                 facecolor=SUPERFICIE)
    eixos(a1, 0, 1)
    eixos(a2, 0, 1)
    for i, ee in enumerate(sorted(curvas)):
        cad = abs(ee - E) < 1e-9
        rot = (f"e = {ee:g} mm" + (" (CAD)" if cad else "")).replace(".", ",")
        a1.plot(THETA, curvas[ee][0]/K, color=rampa[i], lw=2.6 if cad else 1.6,
                label=rot)
        a2.plot(THETA, curvas[ee][1], color=rampa[i], lw=2.6 if cad else 1.6)
    for ax in (a1, a2):
        ax.set_xlim(0, 180)
        ax.set_xlabel(r"Anteversão do braço, $\theta_{el}$ (graus)", color=TINTA_2)
    a1.set_ylabel(r"$\tau/K$ (N·m por N/mm)", color=TINTA_2)
    a1.set_ylim(0, 11)
    a2.set_ylabel(r"$\tau/|\tau_g|$ com $K = K_{40}$", color=TINTA_2)
    a2.set_ylim(0, 1.5)
    a1.legend(loc="upper left", frameon=False, fontsize=7.5)
    fig.tight_layout()
    fig.savefig(PASTA/"ottobock_tcc_fig_a5_familia.png", facecolor=SUPERFICIE)
    plt.close(fig)


if __name__ == "__main__":
    main()
