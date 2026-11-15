"""
Exoesqueleto 3 (US 9.737.374 B2): reprodução da Figura 16 pelos 27 marcadores e confronto
do torque da patente com o torque do peso, para as seções 4.7 e 4.8 do TCC.

A Figura 16 da patente desenha cada curva (AASM, RM e AWM) por 27 marcadores, de Θ = −74°
a 30°, a cada 4°: são os pontos de dado, e a linha entre eles é só a ligação do gráfico
(exo3/fig16_marcadores.csv, de exo3/marcadores_fig16.py). Este script usa só esses pontos:

1. reprodução: o ajuste da mola linear (o mesmo de tcc_resultados_exo3.py) feito só nos
   marcadores abaixo do limite de subida, com o came como na Figura 14D, com o melhor giro
   contínuo e com a montagem de dois furos no sentido horário; resíduo em cada marcador;
2. confronto: a AASM nos marcadores, na escala da AWM (a mesma do TCC), contra o torque do
   peso do membro de referência (que, nessa escala, é a própria AWM) e contra o do conjunto
   membro e apoio de braço (seção 4.8); razões, sobra RM em N·m e posição dos picos.

Não altera os números nem as figuras de tcc_resultados_exo3.py: importa as funções dele.
Grava results/exo3_marcadores.json (valores e, em "texto", os números como aparecem no TCC)
e as figuras results/exo3_tcc_fig_7_marcadores.png e results/exo3_tcc_fig_8_confronto.png.

Rodar (na raiz do repositório):
    python tcc_resultados_exo3_marcadores.py
"""
import json
import sys
from pathlib import Path

import numpy as np

import tcc_resultados_exo3 as t3
from tcc_resultados_exo3 import (AZUL, GRADE, LARANJA, SUPERFICIE, TINTA, TINTA_2, VERDE, eixos,
                                 plt)

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ/"exo3"))
import circuito_cabo560 as cc  # noqa: E402
import massa_apoio as ma  # noqa: E402

MARCADORES = RAIZ/"exo3"/"fig16_marcadores.csv"
PASTA = RAIZ/"results"
CINZA = "#9a9994"


def num(x, casas):
    s = f"{x:.{casas}f}".replace("-", "−").replace(".", ",")
    return "0" + s[1:] if s.startswith(",") else s


def ler_marcadores():
    th, aasm, rm, awm = [], [], [], []
    for linha in MARCADORES.read_text(encoding="utf-8").splitlines():
        if linha.startswith("#") or linha.startswith("theta"):
            continue
        c = [x.replace(",", ".") for x in linha.split(";")]
        th.append(float(c[0]))
        aasm.append(float(c[1]))
        rm.append(float(c[2]) if c[2] else np.nan)
        awm.append(float(c[3]))
    return np.array(th), np.array(aasm), np.array(rm), np.array(awm)


def zonas_de_sinal(res):
    """Trechos consecutivos de mesmo sinal do resíduo."""
    s = np.sign(res)
    return 1 + int(np.sum(s[1:] != s[:-1]))


def trechos_de_sinal(th, res):
    """(primeiro marcador, último marcador, sinal) de cada trecho de mesmo sinal."""
    s = np.sign(res)
    saida, ini = [], 0
    for k in range(1, len(s) + 1):
        if k == len(s) or s[k] != s[ini]:
            saida.append([float(th[ini]), float(th[k - 1]), int(s[ini])])
            ini = k
    return saida


def main():
    thM, aasmM, rmM, awmM = ler_marcadores()
    assert len(thM) == 27 and thM[0] == -74 and thM[-1] == 30
    # escala do TCC: a AWM (ajustada na curva digitalizada) igualada ao torque do peso do membro
    segs, hum = t3.membro_superior()
    awm_A = t3.amplitude_awm()
    c = hum["momento_horizontal_N_m"]/awm_A
    awm_A_marc = float(-np.sum(awmM*np.cos(np.radians(thM)))/np.sum(np.cos(np.radians(thM))**2))
    awm_res = awmM + awm_A_marc*np.cos(np.radians(thM))
    fecha = np.abs(aasmM + awmM - rmM)
    v, q_lim = t3.varredura()
    th_lim = cc.theta_fig16(q_lim)
    th16, aasm16 = t3.fig16()

    # ---------------------------------------------------------------- 1. reprodução nos marcadores
    sens, melhor = t3.sensibilidade(th16, aasm16, th_lim - 0.05, c)
    fu = t3.furos()
    casos = {"desenho": (0.0, None), "melhor_giro": (melhor["giro"], None),
             "dois_furos": (-2*fu["passo"], "furos")}
    rep, curvas = {}, {}
    for nome, (giro, tipo) in casos.items():
        vv, _ = t3.varredura(giro)
        lo, hi = t3.faixa_valida(vv)
        tmax = min(th_lim - 0.05, hi)
        tmin = lo if tipo else None
        aj_m = t3.ajuste_mola(vv, thM, aasmM, tmax, c, theta_min=tmin)        # só marcadores
        aj_c = t3.ajuste_mola(vv, th16, aasm16, tmax, c, theta_min=tmin)      # curva grau a grau
        res = aj_m["pred"] - aj_m["tau"]                                       # modelo − patente, N·m
        i = int(np.argmax(np.abs(res)))
        # modelo da curva grau a grau avaliado nos marcadores (conferência cruzada)
        gM = np.interp(aj_m["theta"], vv["theta"], vv["transm"])
        dxM = np.interp(aj_m["theta"], vv["theta"], vv["dx"])
        pred_c = aj_c["k"]*(aj_c["x0"] + dxM)*gM/1000
        res_c = pred_c - aj_m["tau"]
        r2_c = float(1 - np.sum(res_c**2)/np.sum((aj_m["tau"] - aj_m["tau"].mean())**2))
        rep[nome] = {"giro": float(giro), "n_marcadores": int(len(aj_m["theta"])),
                     "theta_marcadores": [float(aj_m["theta"][0]), float(aj_m["theta"][-1])],
                     "k": float(aj_m["k"]), "x0": float(aj_m["x0"]), "r2": aj_m["r2"],
                     "rms_N_m": aj_m["rms"], "erro_max_N_m": aj_m["max"],
                     "theta_erro_max": float(aj_m["theta"][i]),
                     "zonas_sinal": zonas_de_sinal(res),
                     "trechos_sinal": trechos_de_sinal(aj_m["theta"], res),
                     "forca_pose_N": float(aj_m["k"]*aj_m["x0"]),
                     "forca_pose_curva_N": float(aj_c["k"]*aj_c["x0"]),
                     "k_curva": float(aj_c["k"]), "x0_curva": float(aj_c["x0"]), "r2_curva": aj_c["r2"],
                     "r2_curva_nos_marcadores": r2_c,
                     "residuos": [[float(a), float(b)] for a, b in zip(aj_m["theta"], res)]}
        tg = vv["theta"][(vv["theta"] >= -76) & (vv["theta"] <= tmax)]
        curvas[nome] = (tg, aj_m["k"]*(aj_m["x0"] + np.interp(tg, vv["theta"], vv["dx"]))
                        * np.interp(tg, vv["theta"], vv["transm"])/1000, aj_m)

    # ---------------------------------------------------------------- 2. confronto nos marcadores
    geo = t3.ma.geometria()
    dtp = np.degrees(v["tp"]) - np.interp(cc.theta_fig16(cc.Q_CAD), v["theta"], np.degrees(v["tp"]))
    peso = ma.momento(geo, v["theta"], dtp)
    tau_hum = -ma.G*sum(s["massa"]*s["d"] for s in segs)/1000*np.cos(np.radians(v["theta"]))
    tau_g = -(tau_hum + peso)                                   # conjunto, N·m (módulo)
    membro_M = hum["momento_horizontal_N_m"]*np.cos(np.radians(thM))   # = c |AWM| ajustada
    dentro = thM <= th_lim - 0.05
    tgM = np.interp(thM[dentro], v["theta"], tau_g)
    aM = c*aasmM                                                 # AASM em N·m, todos os marcadores
    awmN = c*np.abs(awmM)                                        # AWM lida, em N·m
    r_awm = aasmM/np.abs(awmM)                                   # razão da própria patente
    r_conj = aM[dentro]/tgM
    sobra_conj = tgM - aM[dentro]
    rm_N = c*rmM                                                 # sobra da patente, N·m
    desenho = curvas["desenho"][2]
    mod_M = np.interp(thM[dentro], curvas["desenho"][0], curvas["desenho"][1])
    r_mod = mod_M/tgM

    def faixa(r, th):
        i, j = int(np.argmin(r)), int(np.argmax(r))
        return {"min": float(r[i]), "theta_min": float(th[i]), "max": float(r[j]), "theta_max": float(th[j])}

    acima90 = thM[dentro][r_conj >= 0.90]
    acima90_awm = thM[r_awm >= 0.90]
    # formas normalizadas pelos picos, na curva grau a grau (Θ de −75° ao limite de subida)
    g = (th16 >= -75) & (th16 <= th_lim - 0.05)
    tt = th16[g]
    a_n = aasm16[g]/aasm16[g].max()
    tg_c = np.interp(tt, v["theta"], tau_g)
    g_n = tg_c/tg_c.max()
    dif = a_n - g_n
    cruz = [float(tt[k] + (tt[k + 1] - tt[k])*dif[k]/(dif[k] - dif[k + 1]))
            for k in range(len(dif) - 1) if dif[k]*dif[k + 1] < 0]
    k_max, k_min = int(np.argmax(dif)), int(np.argmin(dif))
    tm = curvas["desenho"][0]
    m_n = curvas["desenho"][1]/curvas["desenho"][1].max()
    conf = {
        "c": c, "awm_amplitude_curva": awm_A, "awm_amplitude_marcadores": awm_A_marc,
        "awm_residuo_rms": float(np.sqrt(np.mean(awm_res**2))),
        "fechamento_max": float(np.nanmax(fecha)), "n_rm": int(np.sum(~np.isnan(rmM))),
        "n_dentro": int(dentro.sum()), "theta_limite": float(th_lim),
        "razao_awm": faixa(r_awm, thM), "razao_conjunto": faixa(r_conj, thM[dentro]),
        "razao_modelo": faixa(r_mod, thM[dentro]),
        "razao_awm_media": float(np.mean(r_awm[dentro])), "razao_conjunto_media": float(np.mean(r_conj)),
        "acima_90_conjunto": [float(acima90.min()), float(acima90.max())] if acima90.size else None,
        "n_acima_90_conjunto": int(acima90.size),
        "acima_90_awm": [float(acima90_awm.min()), float(acima90_awm.max())],
        "n_acima_90_awm": int(acima90_awm.size),
        "sobra_conjunto": faixa(sobra_conj, thM[dentro]),
        "rm_patente_N_m": faixa(-rm_N[~np.isnan(rmM)], thM[~np.isnan(rmM)]),
        "aasm_max_marcador_N_m": float(aM.max()), "theta_aasm_max_marcadores": [float(x) for x in thM[aasmM == aasmM.max()]],
        "tau_g_max_N_m": float(tau_g.max()), "theta_tau_g_max": float(v["theta"][np.argmax(tau_g)]),
        "theta_pico_aasm": float(th16[np.argmax(aasm16)]),
        "theta_pico_modelo": float(tm[np.argmax(curvas["desenho"][1])]),
        "pico_modelo_N_m": float(curvas["desenho"][1].max()),
        "normalizado": {"cruzamentos": cruz, "dif_max": float(dif[k_max]), "theta_dif_max": float(tt[k_max]),
                        "dif_min": float(dif[k_min]), "theta_dif_min": float(tt[k_min]),
                        # entre o primeiro e o último cruzamento, as formas quase coincidem
                        "meio_max_abs": float(np.max(np.abs(dif[(tt >= cruz[0]) & (tt <= cruz[-1])]))),
                        "abaixo_min": float(dif[tt < cruz[0]].min()),
                        "theta_abaixo_min": float(tt[tt < cruz[0]][np.argmin(dif[tt < cruz[0]])])},
        "linhas": [{"theta": float(a), "aasm_N_m": float(b), "awm_N_m": float(w), "razao_awm": float(r)}
                   for a, b, w, r in zip(thM, aM, awmN, r_awm)],
    }
    # ---------------------------------------------------------------- texto (números como no TCC)
    d, mg, df = rep["desenho"], rep["melhor_giro"], rep["dois_furos"]
    T = {
        "n_marc": str(d["n_marcadores"]), "marc_ini": num(d["theta_marcadores"][0], 0),
        "marc_fim": num(d["theta_marcadores"][1], 0),
        "fecha": num(conf["fechamento_max"], 2), "n_rm": str(conf["n_rm"]),
        "awm_marc": num(awm_A_marc, 2), "awm_curva": num(awm_A, 2), "awm_res": num(conf["awm_residuo_rms"], 2),
        "d_r2": num(d["r2"], 3), "d_k": num(d["k"], 3), "d_x0": num(d["x0"], 1), "d_rms": num(d["rms_N_m"], 2),
        "d_max": num(d["erro_max_N_m"], 2), "d_th_max": num(d["theta_erro_max"], 0), "d_zonas": str(d["zonas_sinal"]),
        "d_r2c": num(d["r2_curva"], 3), "d_r2cm": num(d["r2_curva_nos_marcadores"], 3),
        "d_kc": num(d["k_curva"], 3), "d_x0c": num(d["x0_curva"], 1),
        "d_fpose": num(d["forca_pose_N"], 0), "d_fpose_c": num(d["forca_pose_curva_N"], 0),
        "d_trechos": [[num(a, 0), num(b, 0), "+" if sg > 0 else "−"] for a, b, sg in d["trechos_sinal"]],
        "mg_giro": num(mg["giro"], 0), "mg_r2": num(mg["r2"], 3), "mg_k": num(mg["k"], 3), "mg_rms": num(mg["rms_N_m"], 2),
        "mg_max": num(mg["erro_max_N_m"], 2), "mg_n": str(mg["n_marcadores"]),
        "df_giro": num(df["giro"], 2), "df_r2": num(df["r2"], 3), "df_k": num(df["k"], 3), "df_x0": num(df["x0"], 1),
        "df_rms": num(df["rms_N_m"], 2), "df_max": num(df["erro_max_N_m"], 2), "df_th_max": num(df["theta_erro_max"], 0),
        "df_n": str(df["n_marcadores"]), "df_r2c": num(df["r2_curva"], 3),
        "c": num(c, 4),
        "ra_min": num(conf["razao_awm"]["min"], 2), "ra_th_min": num(conf["razao_awm"]["theta_min"], 0),
        "ra_max": num(conf["razao_awm"]["max"], 2), "ra_th_max": num(conf["razao_awm"]["theta_max"], 0),
        "rc_min": num(conf["razao_conjunto"]["min"], 2), "rc_th_min": num(conf["razao_conjunto"]["theta_min"], 0),
        "rc_max": num(conf["razao_conjunto"]["max"], 2), "rc_th_max": num(conf["razao_conjunto"]["theta_max"], 0),
        "rm_min": num(conf["razao_modelo"]["min"], 2), "rm_max": num(conf["razao_modelo"]["max"], 2),
        "ra_media": num(conf["razao_awm_media"], 2), "rc_media": num(conf["razao_conjunto_media"], 2),
        "a90_ini": num(conf["acima_90_awm"][0], 0), "a90_fim": num(conf["acima_90_awm"][1], 0),
        "a90_n": str(conf["n_acima_90_awm"]),
        "sobra_min": num(conf["sobra_conjunto"]["min"], 2), "sobra_th_min": num(conf["sobra_conjunto"]["theta_min"], 0),
        "sobra_max": num(conf["sobra_conjunto"]["max"], 2), "sobra_th_max": num(conf["sobra_conjunto"]["theta_max"], 0),
        "rmN_min": num(conf["rm_patente_N_m"]["min"], 2), "rmN_th_min": num(conf["rm_patente_N_m"]["theta_min"], 0),
        "rmN_max": num(conf["rm_patente_N_m"]["max"], 2), "rmN_th_max": num(conf["rm_patente_N_m"]["theta_max"], 0),
        "aasm_max_N": num(conf["aasm_max_marcador_N_m"], 2),
        "pico_aasm": num(conf["theta_pico_aasm"], 0), "pico_tg": num(conf["theta_tau_g_max"], 1),
        "pico_mod": num(conf["theta_pico_modelo"], 1), "pico_mod_N": num(conf["pico_modelo_N_m"], 2),
        "elev_aasm": num(conf["theta_pico_aasm"] + 90, 0), "elev_tg": num(conf["theta_tau_g_max"] + 90, 1),
        "elev_mod": num(conf["theta_pico_modelo"] + 90, 1),
        "defas_aasm": num(conf["theta_pico_aasm"] - conf["theta_tau_g_max"], 1),
        "defas_mod": num(conf["theta_tau_g_max"] - conf["theta_pico_modelo"], 1),
        "cruz": [num(x, 1) for x in cruz], "cruz_ini": num(cruz[0], 1), "cruz_fim": num(cruz[-1], 1),
        "meio_max": num(conf["normalizado"]["meio_max_abs"], 3),
        "abaixo_min": num(conf["normalizado"]["abaixo_min"], 3),
        "th_abaixo_min": num(conf["normalizado"]["theta_abaixo_min"], 0),
        "dif_max": num(conf["normalizado"]["dif_max"], 3),
        "th_dif_max": num(conf["normalizado"]["theta_dif_max"], 0), "dif_min": num(conf["normalizado"]["dif_min"], 3),
        "th_dif_min": num(conf["normalizado"]["theta_dif_min"], 0), "n_dentro": str(conf["n_dentro"]),
        "lim": num(th_lim, 1),
    }
    # as mesmas razões em porcentagem, como o texto as usa
    for chave, valor in (("ra_max", conf["razao_awm"]["max"]), ("ra_min", conf["razao_awm"]["min"]),
                         ("rc_min", conf["razao_conjunto"]["min"]), ("rc_max", conf["razao_conjunto"]["max"]),
                         ("rm_min", conf["razao_modelo"]["min"]), ("rm_max", conf["razao_modelo"]["max"]),
                         ("rc_media", conf["razao_conjunto_media"])):
        T[chave + "_pct"] = num(100*valor, 0)
    saida = {"reproducao": rep, "confronto": conf, "texto": T}
    with open(PASTA/"exo3_marcadores.json", "w", encoding="utf-8") as fh:
        json.dump(saida, fh, ensure_ascii=False, indent=1)

    # ---------------------------------------------------------------- figuras
    # 7: reprodução da Figura 16 pelos marcadores
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.4), dpi=200, facecolor=SUPERFICIE,
                               gridspec_kw={"width_ratios": [1.35, 1.0]})
    eixos(a, 0, 0)
    t3.sombrear_marcas(a)
    a.axhline(0, color=GRADE, lw=0.8)
    a.plot(thM, aasmM, "o-", ms=3.2, lw=0.8, color=TINTA, label="AASM, marcadores da patente")
    a.plot(thM, awmM, "s-", ms=2.8, lw=0.8, color=CINZA, label="AWM, marcadores da patente")
    ok = ~np.isnan(rmM)
    a.plot(thM[ok], rmM[ok], "^-", ms=3.0, lw=0.8, color=TINTA_2, label="RM, marcadores da patente")
    for nome, cor, rot in (("desenho", LARANJA, "came como na Figura 14D"),
                           ("dois_furos", AZUL, "came dois furos no sentido horário")):
        tg, tau, _ = curvas[nome]
        a.plot(tg, tau/c, color=cor, lw=1.6, label=f"AASM do modelo, {rot}")
        a.plot(tg, tau/c - awm_A*np.cos(np.radians(tg)), color=cor, lw=1.1, ls="--")
    a.plot([], [], color=TINTA_2, lw=1.1, ls="--", label="RM do modelo (AASM do modelo + AWM)")
    a.set_xlabel("Θ (graus)", color=TINTA_2)
    a.set_ylabel("momento, na unidade da figura", color=TINTA_2)
    a.set_xlim(-78, 33)
    a.legend(loc="lower left", frameon=False, fontsize=6.6)
    a.text(0.0, 1.02, "(a) Figura 16 da patente pelos marcadores e o modelo", transform=a.transAxes,
           fontsize=8.5, color=TINTA)
    eixos(b, 0, 1)
    t3.sombrear_marcas(b)
    b.axhline(0, color=TINTA_2, lw=0.8)
    for nome, cor, mk, rot in (("desenho", LARANJA, "o", f"came como na 14D, R² = {T['d_r2']}"),
                               ("dois_furos", AZUL, "s", f"dois furos, R² = {T['df_r2']}")):
        r = np.array(rep[nome]["residuos"])
        b.plot(r[:, 0], r[:, 1], mk + "-", ms=3.2, lw=0.9, color=cor, label=rot)
    b.set_xlabel("Θ (graus)", color=TINTA_2)
    b.set_ylabel("modelo − marcador (N·m)", color=TINTA_2)
    b.legend(loc="upper left", frameon=False, fontsize=7)
    b.text(0.0, 1.02, "(b) resíduo em cada marcador da AASM", transform=b.transAxes, fontsize=8.5,
           color=TINTA)
    fig.tight_layout()
    fig.savefig(PASTA/"exo3_tcc_fig_7_marcadores.png", facecolor=SUPERFICIE)
    plt.close(fig)

    # 8: confronto com o torque do peso
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.4), dpi=200, facecolor=SUPERFICIE)
    eixos(a, 0, 0)
    t3.sombrear_marcas(a)
    th_c = v["theta"][v["theta"] >= -76]
    a.plot(th_c, tau_g[v["theta"] >= -76], color=TINTA, lw=1.8, label="τ_g, membro e apoio de braço")
    a.plot(thM, awmN, "s", ms=2.8, color=CINZA, label="AWM da patente, na escala adotada")
    a.plot(thM, aM, "o", ms=3.2, color=TINTA_2, label="AASM da patente, na escala adotada")
    a.plot(curvas["desenho"][0], curvas["desenho"][1], color=LARANJA, lw=1.6,
           label="modelo com mola ajustada, came como na 14D")
    a.axvline(th_lim, color=TINTA_2, lw=0.8, ls=":")
    a.set_xlabel("Θ (graus)", color=TINTA_2)
    a.set_ylabel("momento no pivô 584 (N·m)", color=TINTA_2)
    a.set_ylim(0, 13)
    a.set_xlim(-78, 33)
    a.legend(loc="lower center", frameon=False, fontsize=6.8)
    a.text(0.0, 1.02, "(a) em N·m, na escala da AWM", transform=a.transAxes, fontsize=8.5, color=TINTA)
    eixos(b, 0, 1)
    t3.sombrear_marcas(b)
    b.plot(tt, g_n, color=TINTA, lw=1.8, label="τ_g")
    b.plot(tt, a_n, color=TINTA_2, lw=1.4, ls="--", label="AASM da patente")
    b.plot(tm, m_n, color=LARANJA, lw=1.6, label="modelo, came como na 14D")
    for x in (cruz[0], cruz[-1]):
        b.axvline(x, color=TINTA_2, lw=0.7, ls=":")
    b.set_xlabel("Θ (graus)", color=TINTA_2)
    b.set_ylabel("normalizado pelo pico", color=TINTA_2)
    b.set_ylim(0, 1.05)
    b.legend(loc="lower center", frameon=False, fontsize=7)
    b.text(0.0, 1.02, "(b) formas normalizadas pelos picos", transform=b.transAxes, fontsize=8.5,
           color=TINTA)
    fig.tight_layout()
    fig.savefig(PASTA/"exo3_tcc_fig_8_confronto.png", facecolor=SUPERFICIE)
    plt.close(fig)

    print(json.dumps(T, ensure_ascii=False, indent=0))
    for nome, x in rep.items():
        print(nome, f"giro {x['giro']:+.2f}: {x['n_marcadores']} marcadores, k {x['k']:.3f}, x0 {x['x0']:.1f}, "
              f"R² {x['r2']:.3f} (curva {x['r2_curva']:.3f}; modelo da curva nos marcadores {x['r2_curva_nos_marcadores']:.3f}), "
              f"RMS {x['rms_N_m']:.2f}, máx {x['erro_max_N_m']:.2f} em {x['theta_erro_max']:.0f}°, {x['zonas_sinal']} zonas")


if __name__ == "__main__":
    main()
