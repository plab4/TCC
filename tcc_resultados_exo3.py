"""
Números e figuras do exoesqueleto 3 (US 9.737.374 B2) para o TCC.

Cadeia de cálculo, para cada ângulo Θ do apoio de braço (Figura 16 da patente):
1. q = −(Θ + 26,741°) e o circuito do cabo de ancoragem 560 (exo3/circuito_cabo560.py):
   S, φ, θ, b, β e o braço de momento do cabo em torno do pivô 584, C1 sin(γ − θ);
2. o giro absoluto do par de polias, φ − S/R (enrolamento do cabo 560), a partir do giro
   do came medido na Figura 14D (exo3/poses_fig14.py);
3. a direção do cabo da mola, fixa no chassi, de 572 para 632 (polia 630 no infinito);
4. o raio efetivo r e o raio do came no ponto de saída, ρ, pela função suporte da
   envoltória do canal (exo3/relacoes_came570.py), e a zona de saída;
5. a transmissão τ/F_s = (r/R)·C1 sin(γ − θ) e o alongamento da mola, dx/dθp = −r;
6. o ajuste de uma mola linear, τ = k (x0 + Δx)(r/R) C1 sin(γ − θ), à curva AASM da
   Figura 16, na escala da própria patente: a AWM, momento do peso do braço, é igualada ao
   torque do peso do membro de referência (de Leva, homem de 73,0 kg) na horizontal; a
   escala do artigo de Okabe, Brittes e Brito (2026), 30 N·m no máximo da AASM, fica como
   comparação;
7. a sensibilidade ao giro do came: o mesmo ajuste com o came girado em relação ao
   desenho da Figura 14D, para ver qual giro reproduz melhor a Figura 16;
8. o momento do peso do apoio de braço em torno de 584, com as massas do CAD
   (exo3/massa_apoio.py) e o centro do came girando com as polias, contra o do membro
   superior e o AWM da Figura 16, e o ajuste da mola com o peso do apoio somado à AASM.

Grava results/exo3_tcc_numeros.json e as figuras results/exo3_tcc_fig_*.png.

Rodar (na raiz do repositório):
    python tcc_resultados_exo3.py
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ/"exo3"))
import circuito_cabo560 as cc  # noqa: E402
import massa_apoio as ma  # noqa: E402
import relacoes_came570 as rc  # noqa: E402
from extrair_came570 import ZONAS, zona  # noqa: E402
import poses_fig14 as pf  # noqa: E402
from poses_fig14 import contorno_15a  # noqa: E402

PASTA = RAIZ/"results"
FIG14 = RAIZ/"patentes"/"US9737374B2_fig14cd.png"
FIG16 = RAIZ/"exo3"/"fig16_curvas.csv"

# medidos por exo3/poses_fig14.py
Q_14D = 61.19                       # q desenhado na Figura 14D (graus)
GIRO_CAME_14D = 254.0               # giro do referencial da Figura 15B na 14D (graus)
GIRO_CAME_14C = 192.7               # idem, na 14C
ESC_14C = 1.6850                    # px/mm na 14C (a da 14D está em ESC_14D)
N_FUROS = 5                         # furos em torno do 572 nas Figuras 14C e 14D
CABO_C2 = -21.80                    # direção de 572 para 632 em relação a C2, na 14D (graus)
R20 = (31.96 + 32.11)/2             # mm, média das Figuras 14C e 14D
O_14D, ESC_14D = np.array([1711.82, 965.50]), 1.6802      # px e px/mm
ESCALA_ARTIGO = 30.0                # N·m no máximo da curva AASM no artigo (comparação)
MARCAS_FIG16 = {"Z12": (-56.4, -40.3), "Z11": (-23.8, 4.0)}
# membro superior de referência, o das seções 3.1.2 e 3.2.2 (de Leva, 1996, Tab. 4: homem de
# 73,0 kg e 1,741 m, cotovelo estendido): massa (kg), comprimento (mm), centro de massa e raio
# de giração transversal em fração do comprimento. Em série a partir de 584, no eixo maior.
MEMBRO = (("braço", 0.0271*73.0, 281.7, 0.5772, 0.269),
          ("antebraço", 0.0162*73.0, 268.9, 0.4574, 0.265),
          ("mão", 0.0061*73.0, 86.2, 0.7900, 0.513))
# membro do artigo de Okabe, Brittes e Brito (2026), só para comparação (82,8 kg em de Leva)
MEMBRO_ARTIGO = (("braço", 2.244, 281.7, 0.5772, 0.269),
                 ("antebraço", 1.341, 269.8, 0.4574, 0.265),
                 ("mão", 0.505, 86.2, 0.7900, 0.513))

SUPERFICIE, TINTA, TINTA_2, GRADE = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
AZUL, LARANJA, VERDE = "#2a78d6", "#eb6834", "#1baf7a"
# rampas divergentes para as montagens do came (OKLab, L de 0,66 a 0,36 por passo de furo;
# contraste de 3,0 a 11,2 com a superfície): giro horário em azul, anti-horário em laranja
RAMPA_HORARIO = ("#4693f3", "#2573d1", "#0055af", "#003983")
RAMPA_ANTI = ("#e76530", "#c44400", "#a22000", "#770900")
COR_ZONA = {"Z10": AZUL, "Z11": LARANJA, "Z12": VERDE}


def virgula(casas):
    return FuncFormatter(lambda x, pos: f"{x:.{casas}f}".replace(".", ",").replace("-", "−"))


def eixos(ax, casas_x=0, casas_y=0):
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


def num(x, casas):
    return f"{x:.{casas}f}".replace(".", ",").replace("-", "−")


# ---------------------------------------------------------------------- varredura
def varredura(giro_extra=0.0):
    q_lim = cc.limite_subida()
    q = np.unique(np.r_[np.arange(q_lim + 0.02, 62.0, 0.02), Q_14D, cc.Q_CAD])
    est = np.array([cc.circuito(x) for x in q])                  # S, φ, θ, b, β, braço
    S, fi, teta, b, beta, braco = est.T
    psi_abs = np.degrees(np.unwrap(np.radians(fi))) - np.degrees(S/cc.R)
    psi_cam = GIRO_CAME_14D + giro_extra + psi_abs - np.interp(Q_14D, q, psi_abs)
    tp = np.radians(psi_cam + q)                                  # giro em relação ao chassi
    n_cam = (-q + CABO_C2 - 90.0 - psi_cam) % 360                 # normal ao cabo, no came
    V = rc.casco_came()
    r, k = rc.suporte(V, np.radians(n_cam))
    rho = np.hypot(V[k, 0], V[k, 1])
    saida = np.degrees(np.arctan2(V[k, 1], V[k, 0])) % 360
    zonas = np.array([zona(a) for a in saida])
    r_mm, rho_mm = R20*r, R20*rho
    transm = r_mm/cc.R*braco                                      # τ/F_s, em mm
    dx = -np.r_[0, np.cumsum(0.5*(r_mm[1:] + r_mm[:-1])*np.diff(tp))]
    dx -= np.interp(cc.Q_CAD, q, dx)                              # zero na pose do CAD
    theta_fig = cc.theta_fig16(q)
    o = np.argsort(theta_fig)
    v = dict(q=q, theta=theta_fig, S=S, fi=fi, teta=teta, b=b, beta=beta, braco=braco,
             tp=tp, n_cam=n_cam, r=r_mm, rho=rho_mm, zona=zonas, transm=transm, dx=dx, vert=k)
    return {c: x[o] for c, x in v.items()}, q_lim


def intervalos(v, z):
    """Faixas de Θ (graus) em que o cabo da mola sai na zona z."""
    dentro = v["zona"] == z
    faixas, ini = [], None
    for th, d in zip(v["theta"], dentro):
        if d and ini is None:
            ini = th
        if not d and ini is not None:
            faixas.append((ini, ant))
            ini = None
        ant = th
    if ini is not None:
        faixas.append((ini, ant))
    return [(a, c) for a, c in faixas if c - a > 0.5]


def fig16():
    with open(FIG16, encoding="utf-8") as fh:
        linhas = list(csv.DictReader([x for x in fh if not x.startswith("#")], delimiter=";"))
    th = np.array([float(x["theta_grau"].replace(",", ".")) for x in linhas])
    aasm = np.array([float(x["AASM"].replace(",", ".")) for x in linhas])
    return th, aasm


def amplitude_awm():
    """A em AWM = −A cos Θ, por mínimos quadrados na curva digitalizada."""
    with open(FIG16, encoding="utf-8") as fh:
        linhas = list(csv.DictReader([x for x in fh if not x.startswith("#")], delimiter=";"))
    th = np.radians([float(x["theta_grau"].replace(",", ".")) for x in linhas])
    awm = np.array([float(x["AWM"].replace(",", ".")) for x in linhas])
    return float(-np.sum(awm*np.cos(th))/np.sum(np.cos(th)**2))


def ajuste_mola(v, th16, aasm, theta_max, c, peso=None, theta_min=None):
    """Mola linear contra a AASM, com c em N·m por unidade da figura; com peso (N·m em
    v["theta"]), o alvo é a AASM mais o que a mola gasta para sustentar o apoio de braço.
    theta_min limita o ajuste por baixo (montagens em que o cabo sai do canal)."""
    usar = th16 <= theta_max
    if theta_min is not None:
        usar &= th16 >= theta_min
    th, tau = th16[usar], c*aasm[usar]
    if peso is not None:
        tau = tau - np.interp(th, v["theta"], peso)
    g = np.interp(th, v["theta"], v["transm"])
    dx = np.interp(th, v["theta"], v["dx"])
    A = np.c_[g, dx*g]/1000.0
    (a, k), *_ = np.linalg.lstsq(A, tau, rcond=None)
    pred = A @ [a, k]
    res = tau - pred
    return dict(c=c, k=k, x0=a/k, theta=th, tau=tau, pred=pred, g=g, dx=dx,
                rms=float(np.sqrt(np.mean(res**2))), max=float(np.abs(res).max()),
                r2=float(1 - np.sum(res**2)/np.sum((tau - tau.mean())**2)),
                f_req=1000*tau/g)


def sensibilidade(th16, aasm, theta_max, c):
    """Ajuste da mola com o came girado de −120° a +40° em relação ao desenho da 14D."""
    linhas = []
    for d in np.arange(-120.0, 40.01, 1.0):
        v, _ = varredura(d)
        aj = ajuste_mola(v, th16, aasm, theta_max, c)
        z11 = intervalos(v, "Z11")
        lo, hi = faixa_valida(v)
        linhas.append({"giro": float(d), "r2": aj["r2"], "rms": aj["rms"], "k": float(aj["k"]),
                       "x0": float(aj["x0"]), "z11": [list(map(float, z)) for z in z11],
                       "valido": bool(lo <= th16[0] and hi >= theta_max)})
    fisicos = [x for x in linhas if x["k"] > 0 and x["x0"] > 0 and x["valido"]]
    melhor = max(fisicos, key=lambda x: x["r2"])
    return linhas, melhor


def saida_valida(v, theta_ref=-30.0):
    """Pontos em que o cabo da mola sai do canal, entre os chifres do bolsão do 573.

    O cabo sai do bolsão pelo chifre de cima (vértice 0 do casco) e se enrola no canal, no
    sentido anti-horário do came, até o chifre de baixo (último vértice); a ponte do casco
    sobre o bolsão não é canal. w é o ângulo do ponto de saída a partir do chifre de cima,
    desdobrado ao longo de Θ a partir de theta_ref, onde a saída está no canal em todas as
    montagens; vale 0 < w < w_max, no trecho contínuo que contém theta_ref."""
    V = rc.casco_came()
    a = np.degrees(np.arctan2(V[:, 1], V[:, 0]))
    w = np.radians((a[v["vert"]] - a[0]) % 360.0)
    i0 = int(np.argmin(np.abs(v["theta"] - theta_ref)))
    wd = np.unwrap(w)
    wd += w[i0] - wd[i0]
    ok = (wd > 0) & (wd < np.radians((a[-1] - a[0]) % 360.0))
    assert ok[i0]
    lo = i0
    while lo > 0 and ok[lo - 1]:
        lo -= 1
    hi = i0
    while hi < ok.size - 1 and ok[hi + 1]:
        hi += 1
    dentro = np.zeros_like(ok)
    dentro[lo:hi + 1] = True
    return dentro


def faixa_valida(v):
    """Menor e maior Θ (graus) em que o cabo da mola sai do canal."""
    t = v["theta"][saida_valida(v)]
    return float(t.min()), float(t.max())


def furos():
    """Furos em torno do pino 572 nas Figuras 14C e 14D (exo3/poses_fig14.py)."""
    B = np.array(Image.open(FIG14).convert("L")) < 128
    saida = {}
    for nome, giro, esc in (("14C", GIRO_CAME_14C, ESC_14C), ("14D", GIRO_CAME_14D, ESC_14D)):
        centro = pf.anel(B, pf.APROX[nome][1], 4, 12)
        angs, raio = pf.furos_came(B, centro, giro)
        assert len(angs) == N_FUROS, (nome, angs)
        angs = sorted(angs)
        saida[nome] = {"angulos_figura": angs,
                       "angulos_came": [float((x - giro) % 360) for x in angs],
                       "raio_mm": raio/esc,
                       "passo": float((angs[-1] - angs[0])/(N_FUROS - 1)),
                       "espacamentos": [float(b - a) for a, b in zip(angs, angs[1:])]}
    passo = float(np.mean([x["passo"] for x in saida.values()]))
    meio = float(np.mean([np.mean(x["angulos_came"]) for x in saida.values()]))
    return {"figuras": saida, "passo": passo, "centro_came": meio,
            "raio_mm": float(np.mean([x["raio_mm"] for x in saida.values()]))}


def caminho_cabo(v):
    """Comprimento do cabo da mola do chifre de cima até um plano fixo no chassi, normal ao
    cabo (polia 630 no infinito), a menos de uma constante (mm): arco enrolado no canal
    menos a projeção do ponto de saída na direção do cabo. Vale o mesmo para qualquer
    montagem do came, porque a âncora 573 gira com ele."""
    V = rc.casco_came()
    lados = np.hypot(*(np.roll(V, -1, axis=0) - V).T)
    arco = np.r_[0.0, np.cumsum(lados)[:-1]]
    n = np.radians(v["n_cam"])
    t = np.c_[np.cos(n + np.pi/2), np.sin(n + np.pi/2)]
    return R20*(arco[v["vert"]] - np.sum(V[v["vert"]]*t, axis=1))


def montagens(aj, th16, aasm, passo, theta_max, c):
    """Came fixado na polia externa por furos de outro par: giro de j passos em relação ao
    desenho, j de −(N_FUROS − 1) a N_FUROS − 1 (com os mesmos furos na polia, 5 − |j| pares
    coincidem). Para cada montagem: trecho de Θ em que o cabo sai do canal; o torque com a
    mesma mola e o mesmo cabo da montagem desenhada (k e x0 do ajuste principal, com o
    alongamento contado do comprimento do cabo, que acompanha o came); e o ajuste de outra
    mola linear à Figura 16 (k e x0 livres), como na sensibilidade ao giro."""
    v0, _ = varredura(0.0)
    th_pose = cc.theta_fig16(cc.Q_CAD)
    L0 = caminho_cabo(v0)
    L_pose = float(np.interp(th_pose, v0["theta"], L0))
    conf = float(np.max(np.abs((L0 - L_pose) - v0["dx"])))
    linhas, curvas = [], {}
    for j in range(-(N_FUROS - 1), N_FUROS):
        d = j*passo
        v, _ = varredura(d)
        ok = saida_valida(v)
        lo, hi = faixa_valida(v)
        dx = caminho_cabo(v) - L_pose
        F = aj["k"]*(aj["x0"] + dx)
        tau = F*v["transm"]/1000.0
        fx = ok & (v["theta"] >= -75.0)
        th, tt = v["theta"][fx], tau[fx]
        i = int(np.argmax(tt))
        usar = (th16 <= theta_max) & (th16 >= lo) & (th16 <= hi)
        y = c*aasm[usar]
        pred = np.interp(th16[usar], th, tt)
        r2_m = float(1 - np.sum((y - pred)**2)/np.sum((y - y.mean())**2))
        ajj = ajuste_mola(v, th16, aasm, min(theta_max, hi), c, theta_min=lo)
        valores = {}
        for T in (-75.0, -60.0, -30.0, 0.0, 20.0):
            valores[f"{T:g}"] = (float(np.interp(T, th, tt)) if th[0] <= T <= th[-1] else None)
        linhas.append({
            "furos": j, "giro": d, "pares": N_FUROS - abs(j),
            "theta_valido": [max(lo, -75.0), hi], "toda_faixa": bool(lo <= -75.0 and hi >= theta_max),
            "forca_N": [float(F[fx].min()), float(F[fx].max())],
            "tau_max_N_m": float(tt[i]), "theta_tau_max": float(th[i]),
            "tau_N_m": valores, "r2_mesma_mola": r2_m,
            "ajuste": {"k": float(ajj["k"]), "x0": float(ajj["x0"]), "r2": ajj["r2"],
                       "rms_N_m": ajj["rms"], "n": int(len(ajj["theta"])),
                       "fisico": bool(ajj["k"] > 0 and ajj["x0"] > 0)}})
        curvas[j] = (th, tt)
    return {"linhas": linhas, "conferencia_comprimento_mm": conf}, curvas


def figura_montagens(mt, curvas, th16, aasm, c, sens, passo):
    """Curvas de torque das montagens do came (a) e R² do ajuste de outra mola (b)."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 5.0), dpi=200, facecolor=SUPERFICIE,
                               gridspec_kw={"width_ratios": [1.25, 1.0]})
    leg = {}
    eixos(a, 0, 0)
    sombrear_marcas(a)
    leg["aasm"], = a.plot(th16, c*aasm, "o", ms=2.6, color="#bdbcb7", zorder=1,
                          label="AASM da Figura 16, na escala da AWM")
    for x in mt["linhas"]:
        j = x["furos"]
        th, tt = curvas[j]
        if j == 0:
            cor, lw, ls = TINTA, 2.2, "-"
        else:
            cor = (RAMPA_HORARIO if j < 0 else RAMPA_ANTI)[abs(j) - 1]
            lw, ls = 1.5, ("-" if j < 0 else (0, (5, 2)))
        rot = ("0, como desenhado" if j == 0 else
               f"{j:+d} furo{'s' if abs(j) > 1 else ''}, {num(x['giro'], 1)}°")
        leg[j], = a.plot(th, tt, color=cor, lw=lw, ls=ls, label=rot.replace("-", "−"), zorder=3)
    a.set_xlim(-78, 24)
    a.set_ylim(0, None)
    a.set_xlabel("Θ, ângulo do apoio de braço com a horizontal (graus)", color=TINTA_2)
    a.set_ylabel("momento no pivô 584 (N·m)", color=TINTA_2)
    a.text(0.0, 1.02, "(a) mesma mola e mesmo cabo, came em cada par de furos",
           transform=a.transAxes, fontsize=8.5, color=TINTA)
    eixos(b, 0, 2)
    gs = np.array([x["giro"] for x in sens])
    r2 = np.array([x["r2"] for x in sens])
    fis = np.array([x["k"] > 0 and x["x0"] > 0 and x["valido"] for x in sens])
    val = np.array([x["valido"] for x in sens])
    b.plot(gs, np.where(fis, r2, np.nan), color=TINTA_2, lw=1.4, zorder=2,
           label="giro contínuo, mola com k > 0 e x0 > 0")
    b.plot(gs, np.where(val & ~fis, r2, np.nan), color="#bdbcb7", lw=1.2, ls="--", zorder=2,
           label="giro contínuo, sem mola física")
    for x in mt["linhas"]:
        j, aj_ = x["furos"], x["ajuste"]
        if not x["toda_faixa"]:
            continue
        cor = TINTA if j == 0 else (RAMPA_HORARIO if j < 0 else RAMPA_ANTI)[abs(j) - 1]
        b.plot(x["giro"], aj_["r2"], "o", ms=6.5, mew=1.2, zorder=4,
               color=cor if aj_["fisico"] else SUPERFICIE,
               mec=SUPERFICIE if aj_["fisico"] else cor)
        b.annotate(f"{j:+d}".replace("-", "−") if j else "0", (x["giro"], aj_["r2"]),
                   xytext=(0, 7), textcoords="offset points", ha="center", fontsize=7,
                   color=TINTA_2)
    b.set_xlabel("giro do came em relação ao desenho da Figura 14D (graus)", color=TINTA_2)
    b.set_ylabel("R² do ajuste de outra mola", color=TINTA_2)
    b.set_ylim(0.5, 1.02)
    b.set_xlim(-108, 58)
    b.legend(loc="lower left", frameon=False, fontsize=6.6, labelcolor=TINTA)
    b.text(0.0, 1.02, f"(b) montagens em passos de {num(passo, 1)}° (círculo vazio: k ou x0 ≤ 0)",
           transform=b.transAxes, fontsize=8.5, color=TINTA)
    # legenda comum embaixo: 1.ª linha, giros horários e o desenho; 2.ª, anti-horários e a AASM
    ordem = [-4, 1, -3, 2, -2, 3, -1, 4, 0, "aasm"]
    fig.legend([leg[k] for k in ordem], [leg[k].get_label() for k in ordem], loc="lower center",
               ncol=5, frameon=False, fontsize=7.2, labelcolor=TINTA, handlelength=2.6)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.savefig(PASTA/"exo3_tcc_fig_6_montagens.png", facecolor=SUPERFICIE)
    plt.close(fig)


def membro_superior(segmentos=MEMBRO):
    """Segmentos em série a partir de 584: massa, distância do centro a O (mm) e momentos de
    inércia no centro e em O (kg·m²), I_cm = m (k L)² e I_O = I_cm + m d² (Equação (1))."""
    corpos, inicio = [], 0.0
    for nome, m, L, fcm, fk in segmentos:
        d = inicio + fcm*L
        izz = m*(fk*L)**2/1e6
        corpos.append({"nome": nome, "massa": m, "L": L, "d": d, "izz_cg": izz,
                       "izz_o": izz + m*d**2/1e6})
        inicio += L
    M = sum(c["massa"] for c in corpos)
    d = sum(c["massa"]*c["d"] for c in corpos)/M
    izz_o = sum(c["izz_o"] for c in corpos)
    return corpos, {"massa": M, "d": d, "izz_o": izz_o, "izz_cg": izz_o - M*d**2/1e6,
                    "momento_horizontal_N_m": ma.G*M*d/1000}


def conjunto_total(hum, geo, izz_apoio):
    """Membro (no eixo) e apoio de braço (a d e a do eixo) como um corpo em torno de 584."""
    ma_kg = geo["massa_g"]/1000
    x = hum["massa"]*hum["d"] + ma_kg*geo["d"]*np.cos(np.radians(geo["a"]))
    y = ma_kg*geo["d"]*np.sin(np.radians(geo["a"]))
    M = hum["massa"] + ma_kg
    d = float(np.hypot(x, y))/M
    izz_o = hum["izz_o"] + izz_apoio
    return {"massa": M, "d": d, "a": float(np.degrees(np.arctan2(y, x))), "izz_o": izz_o,
            "izz_cg": izz_o - M*d**2/1e6, "amplitude_N_m": ma.G*M*d/1000}


def pontos_fig16():
    """AASM, AWM e RM da Figura 16 em ângulos de 15 em 15 graus e no máximo da AASM."""
    with open(FIG16, encoding="utf-8") as fh:
        linhas = list(csv.DictReader([x for x in fh if not x.startswith("#")], delimiter=";"))
    f = lambda t: float(t.replace(",", ".")) if t else None
    tab = {int(f(x["theta_grau"])): {k: f(x[k]) for k in ("AASM", "AWM", "RM")} for x in linhas}
    th_max = max(tab, key=lambda t: tab[t]["AASM"])
    usados = sorted(set(range(-75, 31, 15)) | {th_max})
    fecha = max(abs(x["RM"] - (x["AASM"] + x["AWM"])) for x in tab.values() if x["RM"] is not None)
    return [{"theta": t, **tab[t]} for t in usados], th_max, len(tab), \
        sum(1 for x in tab.values() if x["RM"] is not None), float(fecha)


def cabo634_teste():
    """dℓ/dθp = −r pelo comprimento geométrico do cabo 634, na geometria de teste de
    relacoes_came570.py (L = 4,5 R20 e r630 = 0,5 R20): maior diferença, em R20."""
    V = rc.casco_came()
    L, lam, r630 = 4.5, 0.0, 0.5
    tp = lam - np.pi/2 - np.radians(np.arange(95.0, 355.0, 0.05))
    _, _, r, _, _ = rc.cabo(V, tp, L, lam, r630)
    l = rc.comprimento(V, tp, L, lam, r630)
    return float(np.max(np.abs(np.gradient(l, tp) + r)))


def ancoragem_desenhada():
    """Distância (mm) entre o ponto A do CAD e o 562 desenhado, nas Figuras 14C e 14D."""
    import poses_fig14 as pf
    B = np.array(Image.open(FIG14).convert("L")) < 128
    saida = {}
    for nome, (a584, a572, _) in pf.APROX.items():
        O, D = pf.furo_branco(B, a584), pf.anel(B, a572, 4, 12)
        esc = np.hypot(*(D - O))/pf.C2
        w = pf.C1*np.array([np.cos(np.radians(pf.GAMA)), np.sin(np.radians(pf.GAMA))])
        A_cad = O + esc*np.array([w[0], -w[1]])
        saida[nome] = float(np.hypot(*(pf.disco(B, A_cad) - A_cad))/esc)
    return saida


def verificacoes(v, geo, conf):
    """Resíduos da cadeia de cálculo e das conferências com a patente."""
    S_c, fi_c, te_c = 139.575, 360 - 7.131, 360 - 97.131
    fech = (S_c*cc.u(te_c) + cc.R*cc.u(fi_c) + cc.C2*cc.u(180 - cc.Q_CAD) + cc.C1*cc.u(cc.GAMA))
    S, fi, teta, b, beta, braco = cc.circuito(cc.Q_CAD)
    duas = max(abs(-bb*np.sin(np.radians(t + q + be)) - cc.C1*np.sin(np.radians(cc.GAMA - t)))
               for q, t, bb, be in zip(v["q"], v["teta"], v["b"], v["beta"]))
    # caminho inverso: um dos dois ramos devolve q; perto do limite de subida, os dois têm S > 0
    inv, ambiguo, troca = 0.0, [], []
    for q, t in zip(v["q"][::5], v["teta"][::5]):
        ramos = cc.circuito_por_teta(t)
        inv = max(inv, min(abs(cc.meia_volta(qq - q)) for qq, ss in ramos if ss > 0))
        if all(ss > 0 for _, ss in ramos):
            ambiguo.append(cc.theta_fig16(q))
        if abs(cc.meia_volta(ramos[0][0] - q)) > 1e-6:
            troca.append(cc.theta_fig16(q))
    qs = np.linspace(-40, 75, 4601)
    tp = np.degrees(np.unwrap(np.radians([cc.circuito(q)[1] + q - np.degrees(cc.circuito(q)[0]/cc.R)
                                          for q in qs])))
    br = np.array([cc.circuito(q)[5] for q in qs])
    enrol = float(np.abs(-np.gradient(tp, qs) - br/cc.R)[2:-2].max())
    vol = max(abs(ma.disco(n)[0]) for n in ("polia externa", "polia interna"))
    return {"fechamento_cad_mm": float(np.hypot(*fech)), "S_cad_mm": abs(S - S_c),
            "fi_cad_grau": abs(fi - fi_c), "b_cad_mm": abs(b - 78.292), "beta_cad_grau": abs(beta - 15.979),
            "braco_duas_formas_mm": float(duas), "inverso_grau": float(inv),
            "inverso_dois_ramos_desde_theta": float(min(ambiguo)),
            "inverso_ramo_de_baixo_desde_theta": float(min(troca)),
            "trabalho_virtual_rel": conf, "enrolamento": enrol, "cabo634_R20": cabo634_teste(),
            "tensor_rel": ma.confere_tensor(), "polias_volume_rel": float(vol),
            "ancoragem_mm": ancoragem_desenhada()}


# ---------------------------------------------------------------------- figuras
def figura_circuito(v):
    """Circuito sobre a Figura 14D (pose do desenho) e o came ajustado ao desenho."""
    from matplotlib.transforms import Affine2D
    S, fi, teta, b, beta, braco = cc.circuito(Q_14D)
    gira = -1.0                                         # o CAD é a figura girada de 180°
    O = np.zeros(2)
    A = gira*(-cc.C1*cc.u(cc.GAMA))
    D = gira*(cc.C2*cc.u(180 - Q_14D))
    T = D + gira*(cc.R*cc.u(fi))
    pe = gira*np.dot(-cc.C1*cc.u(cc.GAMA), cc.u(teta + 90))*cc.u(teta + 90)
    img = np.array(Image.open(FIG14).convert("L"))/255.0
    fundo = 1.0 - 0.45*(1.0 - img)
    flange = contorno_15a()*R20
    c, s = np.cos(np.radians(GIRO_CAME_14D)), np.sin(np.radians(GIRO_CAME_14D))
    flange = flange @ np.array([[c, s], [-s, c]]) + D
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5.2), dpi=200, facecolor=SUPERFICIE,
                                   gridspec_kw={"width_ratios": [1.25, 1]})
    for ax in (ax1, ax2):
        eixos(ax)
        ax.grid(False)
        ax.set_facecolor("white")
        ax.set_aspect("equal")
        tr = (Affine2D().translate(-O_14D[0], -O_14D[1]).scale(1/ESC_14D, -1/ESC_14D)
              + ax.transData)
        ax.imshow(fundo, cmap="gray", vmin=0, vmax=1, interpolation="bilinear",
                  extent=(0, fundo.shape[1], fundo.shape[0], 0), transform=tr, zorder=1)
        ax.add_patch(plt.Circle(D, cc.R, fill=False, color=TINTA_2, lw=1.0, zorder=3))
        alcas = [
            ax.plot([0, D[0]], [0, D[1]], color=TINTA, lw=2.2, zorder=4,
                    label="C2: elo O → D, solidário ao chassi")[0],
            ax.plot([A[0], 0], [A[1], 0], color=LARANJA, lw=1.8, zorder=4,
                    label="C1: vetor fixo A → O")[0],
            ax.plot([D[0], T[0]], [D[1], T[1]], color=TINTA_2, lw=1.4, zorder=4,
                    label="R: raio da polia primária, D → T")[0],
            ax.plot([T[0], A[0]], [T[1], A[1]], color=AZUL, lw=1.8, zorder=4,
                    label="S: vão do cabo 560, T → A")[0],
            ax.plot([0, T[0]], [0, T[1]], color=TINTA_2, lw=1.0, ls=":", zorder=4,
                    label="b: O → T")[0],
            ax.plot([0, pe[0]], [0, pe[1]], color=VERDE, lw=1.4, ls="--", zorder=4,
                    label=f"braço do cabo: {num(abs(braco), 2)} mm")[0],
            ax.plot(*flange.T, color=VERDE, lw=1.0, zorder=5,
                    label="came 570: contorno da Figura 15A ajustado ao desenho")[0],
        ]
        for nome, p, d_ in (("O", O, (-9, 3)), ("A", A, (4, 3)), ("D", D, (5, -8)),
                            ("T", T, (-12, 2))):
            ax.annotate(nome, p, xytext=d_, textcoords="offset points", fontsize=8,
                        color=TINTA, zorder=6)
        ax.set_xlabel("x (mm)", color=TINTA_2)
    ax1.set_ylabel("y (mm)", color=TINTA_2)
    ax1.set_xlim(-60, 140)
    ax1.set_ylim(-260, 90)
    ax2.set_xlim(D[0] - 45, D[0] + 45)
    ax2.set_ylim(D[1] - 45, D[1] + 45)
    fig.legend(handles=alcas, loc="lower center", ncol=3, frameon=False, fontsize=7.5)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.98, bottom=0.23, wspace=0.12)
    fig.savefig(PASTA/"exo3_tcc_fig_1_circuito.png", facecolor=SUPERFICIE)
    plt.close(fig)


def figura_came():
    def ler(arq):
        with open(RAIZ/"exo3"/arq, encoding="utf-8") as fh:
            return list(csv.DictReader([x for x in fh if not x.startswith("#")], delimiter=";"))
    f = lambda s: float(s.replace(",", "."))
    cont = ler("came570_contorno.csv")
    P = np.array([[f(x["x_R20"]), f(x["y_R20"])] for x in cont])
    ang = np.array([f(x["angulo_grau"]) for x in cont])
    ef = ler("came570_raio_efetivo.csv")
    n = np.array([f(x["normal_grau"]) for x in ef])
    r = np.array([f(x["raio_efetivo_R20"]) for x in ef])
    rho = np.array([f(x["raio_saida_R20"]) for x in ef])
    zs = np.array([x["zona_da_saida"] for x in ef])
    V = rc.casco_came()
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.4), dpi=200, facecolor=SUPERFICIE,
                               gridspec_kw={"width_ratios": [1, 1.35]})
    eixos(a, 1, 1)
    eixos(b, 0, 1)
    a.plot(np.r_[V[:, 0], V[0, 0]], np.r_[V[:, 1], V[0, 1]], ls="--", lw=1.0, color="#9a9994",
           label="envoltória convexa (caminho do cabo)")
    a.plot(np.r_[P[:, 0], P[0, 0]], np.r_[P[:, 1], P[0, 1]], lw=1.3, color=TINTA_2,
           label="fundo do canal")
    for z, cor in COR_ZONA.items():
        s = np.array([zona(x) == z for x in ang])
        a.plot(np.where(s, P[:, 0], np.nan), np.where(s, P[:, 1], np.nan), lw=3.0, color=cor,
               solid_capstyle="round", label=f"zona {z}")
    a.plot([0], [0], "+", color=TINTA, ms=8)
    a.set_aspect("equal")
    a.set_xlabel("x / R20", color=TINTA_2)
    a.set_ylabel("y / R20", color=TINTA_2)
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False, fontsize=7)
    b.plot(n, rho, lw=1.0, ls="--", color=TINTA_2, label="ρ, raio do came no ponto de saída")
    b.plot(n, r, lw=1.3, color=TINTA_2, label="r, raio efetivo")
    for z, cor in COR_ZONA.items():
        s = zs == z
        b.plot(np.where(s, n, np.nan), np.where(s, r, np.nan), lw=3.0, color=cor,
               solid_capstyle="round", label=f"r com saída na zona {z}")
    b.set_xlim(0, 360)
    b.set_xticks(range(0, 361, 45))
    b.set_ylim(0, 1.15)
    b.set_xlabel("direção normal ao cabo, no referencial do came (graus)", color=TINTA_2)
    b.set_ylabel("raio / R20", color=TINTA_2)
    b.legend(loc="upper right", frameon=False, fontsize=7)
    a.text(0.0, 1.02, "(a)", transform=a.transAxes, fontsize=9, color=TINTA)
    b.text(0.0, 1.02, "(b)", transform=b.transAxes, fontsize=9, color=TINTA)
    fig.tight_layout()
    fig.savefig(PASTA/"exo3_tcc_fig_2_came.png", facecolor=SUPERFICIE)
    plt.close(fig)


def sombrear_marcas(ax):
    for z, (a0, a1) in MARCAS_FIG16.items():
        ax.axvspan(a0, a1, color=COR_ZONA[z], alpha=0.10, lw=0, zorder=0)


def figura_varredura(v, q_lim):
    th = v["theta"]
    fig, axs = plt.subplots(3, 1, figsize=(10, 9.0), dpi=200, facecolor=SUPERFICIE,
                            sharex=True)
    a, b, c = axs
    for ax in axs:
        eixos(ax, 0, 0)
        sombrear_marcas(ax)
        ax.axvline(cc.theta_fig16(cc.Q_CAD), color=TINTA_2, lw=0.8, ls=":")
    a.plot(th, v["S"], color=AZUL, lw=1.6, label="S, vão do cabo 560")
    a.plot(th, v["braco"], color=VERDE, lw=1.6, label="C1 sin(γ − θ), braço do cabo em torno de O")
    a.set_ylabel("mm", color=TINTA_2)
    a.legend(loc="upper right", frameon=False, fontsize=7.5)
    b.plot(th, v["rho"], color=TINTA_2, lw=1.0, ls="--", label="ρ, raio do came no ponto de saída")
    b.plot(th, v["r"], color=TINTA_2, lw=1.2, label="r, raio efetivo")
    for z, cor in COR_ZONA.items():
        s = v["zona"] == z
        b.plot(np.where(s, th, np.nan), np.where(s, v["r"], np.nan), color=cor, lw=3.0,
               solid_capstyle="round", label=f"saída na zona {z}")
    b.set_ylabel("mm", color=TINTA_2)
    b.set_ylim(0, 36)
    b.legend(loc="lower right", frameon=False, fontsize=7.5, ncol=2)
    c.plot(th, v["transm"], color=LARANJA, lw=1.6, label="τ/F_s = (r/R) C1 sin(γ − θ)")
    c.plot(th, v["dx"], color=AZUL, lw=1.6, ls="--", label="Δx, alongamento da mola desde a pose")
    c.set_ylabel("mm", color=TINTA_2)
    c.legend(loc="lower left", frameon=False, fontsize=7.5)
    c.set_xlabel("Θ, ângulo do apoio de braço com a horizontal (graus)", color=TINTA_2)
    c.set_xlim(-90, 25)
    for ax, rot in zip(axs, "abc"):
        ax.text(0.0, 1.02, f"({rot})", transform=ax.transAxes, fontsize=9, color=TINTA)
    fig.tight_layout()
    fig.savefig(PASTA/"exo3_tcc_fig_3_varredura.png", facecolor=SUPERFICIE)
    plt.close(fig)


def painel_ajuste(ax, aj, th16, aasm, v, titulo):
    eixos(ax, 0, 0)
    sombrear_marcas(ax)
    fora = th16 > aj["theta"].max()
    ax.plot(th16[~fora], aj["c"]*aasm[~fora], "o", ms=3.0, color=TINTA_2,
            label="AASM da Figura 16, na escala da AWM")
    ax.plot(th16[fora], aj["c"]*aasm[fora], "o", ms=3.0, color="#bdbcb7",
            label="acima do limite de subida desta ancoragem")
    tg = v["theta"][(v["theta"] >= -75) & (v["theta"] <= aj["theta"].max())]
    g = np.interp(tg, v["theta"], v["transm"])
    dx = np.interp(tg, v["theta"], v["dx"])
    ax.plot(tg, aj["k"]*(aj["x0"] + dx)*g/1000, color=LARANJA, lw=1.8,
            label="modelo com mola linear ajustada")
    ax.set_xlabel("Θ (graus)", color=TINTA_2)
    ax.set_ylabel("momento no pivô 584 (N·m)", color=TINTA_2)
    ax.yaxis.set_major_formatter(virgula(0 if aj["c"]*aasm.max() > 15 else 1))
    ax.set_ylim(0, 1.1*aj["c"]*aasm.max())
    ax.text(0.0, 1.02, titulo, transform=ax.transAxes, fontsize=8.5, color=TINTA)


def figura_fig16(aj, th16, aasm, v, sens, melhor, aj_m, v_m):
    """Ajuste da mola com o came como na Figura 14D (exo3_tcc_fig_4_fig16.png) e
    sensibilidade ao giro do came (exo3_tcc_fig_5_giro.png)."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.3), dpi=200, facecolor=SUPERFICIE)
    painel_ajuste(a, aj, th16, aasm, v, "(a) came girado como na Figura 14D: "
                  f"R² = {num(aj['r2'], 3)}")
    a.legend(loc="lower center", frameon=False, fontsize=7)
    eixos(b, 0, 0)
    b.plot(aj["dx"], aj["f_req"], "o", ms=3.0, color=TINTA_2,
           label="força da mola que reproduz a Figura 16")
    xx = np.linspace(aj["dx"].min(), aj["dx"].max(), 50)
    b.plot(xx, aj["k"]*(aj["x0"] + xx), color=LARANJA, lw=1.8, label="mola linear ajustada")
    b.set_xlabel("Δx, alongamento da mola desde a pose (mm)", color=TINTA_2)
    b.set_ylabel("força da mola (N)", color=TINTA_2)
    b.legend(loc="upper left", frameon=False, fontsize=7)
    b.text(0.0, 1.02, "(b) força necessária, came como na Figura 14D", transform=b.transAxes,
           fontsize=8.5, color=TINTA)
    fig.tight_layout()
    fig.savefig(PASTA/"exo3_tcc_fig_4_fig16.png", facecolor=SUPERFICIE)
    plt.close(fig)
    fig, (c, d) = plt.subplots(1, 2, figsize=(10, 4.3), dpi=200, facecolor=SUPERFICIE)
    eixos(c, 0, 2)
    gs = np.array([x["giro"] for x in sens])
    r2 = np.array([x["r2"] for x in sens])
    val = np.array([x["valido"] for x in sens])
    fis = np.array([x["k"] > 0 and x["x0"] > 0 for x in sens]) & val
    c.plot(gs, np.where(fis, r2, np.nan), color=AZUL, lw=1.8, label="mola com k > 0 e x0 > 0")
    c.plot(gs, np.where(val & ~fis, r2, np.nan), color="#bdbcb7", lw=1.4, ls="--",
           label="sem solução física (k ou x0 negativo)")
    c.axvspan(gs[0], gs[val][0] - 0.5, color=GRADE, alpha=0.6, lw=0, zorder=0)
    c.text(0.5*(gs[0] + gs[val][0]), 0.52, "cabo da mola\nfora do canal", ha="center",
           va="bottom", fontsize=6.5, color=TINTA_2)
    c.axvline(0, color=TINTA_2, lw=0.8, ls=":")
    c.axvline(melhor["giro"], color=LARANJA, lw=1.0)
    c.set_xlabel("giro do came em relação ao desenho da Figura 14D (graus)", color=TINTA_2)
    c.set_ylabel("R² do ajuste da mola", color=TINTA_2)
    c.set_ylim(0.5, 1.0)
    c.legend(loc="lower right", frameon=False, fontsize=7)
    c.text(0.0, 1.02, "(a) R² do ajuste em função do giro do came", transform=c.transAxes,
           fontsize=8.5, color=TINTA)
    painel_ajuste(d, aj_m, th16, aasm, v_m, f"(b) came girado de {num(melhor['giro'], 0)}°: "
                  f"R² = {num(aj_m['r2'], 3)}")
    fig.tight_layout()
    fig.savefig(PASTA/"exo3_tcc_fig_5_giro.png", facecolor=SUPERFICIE)
    plt.close(fig)


# ---------------------------------------------------------------------- principal
def main():
    v, q_lim = varredura()
    th16, aasm = fig16()
    # escala da própria patente: a AWM, momento do peso do braço, igualada ao torque do peso
    # do membro de referência na horizontal
    segs, hum = membro_superior()
    awm = amplitude_awm()
    c = hum["momento_horizontal_N_m"]/awm
    aj = ajuste_mola(v, th16, aasm, cc.theta_fig16(q_lim) - 0.05, c)
    # conferência: τ/F_s contra −dx/dΘ (por radiano)
    dxdth = -np.gradient(v["dx"], np.radians(v["theta"]))
    ok = (v["theta"] > -88) & (v["theta"] < cc.theta_fig16(q_lim) - 1)
    conf = float(np.max(np.abs(dxdth[ok] - v["transm"][ok])/np.max(v["transm"][ok])))

    def em(campo, T):
        return float(np.interp(T, v["theta"], v[campo]))

    pontos = {}
    for nome, T in (("pose", cc.theta_fig16(cc.Q_CAD)), ("inicio_fig16", -75.0),
                    ("base_Z12", -56.4), ("topo_Z12", -40.3), ("base_Z11", -23.8),
                    ("zero", 0.0), ("topo_Z11", 4.0)):
        i = int(np.argmin(np.abs(v["theta"] - T)))
        pontos[nome] = {"theta": T, "q": em("q", T), "S": em("S", T), "teta": em("teta", T),
                        "braco": em("braco", T), "r": em("r", T), "rho": em("rho", T),
                        "zona": str(v["zona"][i]), "transm": em("transm", T), "dx": em("dx", T),
                        "dtp_dtheta": em("braco", T)/cc.R}
    N = {
        "R20_mm": R20, "R20_sobre_R": R20/cc.R, "q_limite": q_lim,
        "theta_limite": cc.theta_fig16(q_lim), "theta_pose": cc.theta_fig16(cc.Q_CAD),
        "zonas": {z: intervalos(v, z) for z in ZONAS},
        "pontos": pontos,
        "transm_max": float(v["transm"].max()),
        "theta_transm_max": float(v["theta"][np.argmax(v["transm"])]),
        "dx_total_ate_limite": float(v["dx"][-1]),
        "conferencia_trabalho_virtual": conf,
        "ajuste": {"escala_N_m_por_unidade": aj["c"], "k_N_por_mm": aj["k"], "x0_mm": aj["x0"],
                   "rms_N_m": aj["rms"], "erro_max_N_m": aj["max"], "r2": aj["r2"],
                   "theta_max_ajuste": float(aj["theta"].max()), "n_pontos": int(len(aj["theta"])),
                   "forca_pose_N": aj["k"]*aj["x0"],
                   "forca_inicio_N": float(aj["k"]*(aj["x0"] + aj["dx"][0])),
                   "forca_fim_N": float(aj["k"]*(aj["x0"] + aj["dx"][-1]))},
    }
    sens, melhor = sensibilidade(th16, aasm, cc.theta_fig16(q_lim) - 0.05, c)
    v_m, _ = varredura(melhor["giro"])
    aj_m = ajuste_mola(v_m, th16, aasm, cc.theta_fig16(q_lim) - 0.05, c)
    N["sensibilidade_giro"] = sens
    gv = [x["giro"] for x in sens if x["valido"]]
    N["giro_valido"] = [min(gv), max(gv)]
    assert all(x["valido"] for x in sens if min(gv) <= x["giro"] <= max(gv))
    # montagens do came pelos furos em torno do 572 (Figuras 14C e 14D)
    fu = furos()
    mt, curvas_mt = montagens(aj, th16, aasm, fu["passo"], cc.theta_fig16(q_lim) - 0.05, c)
    N["furos"] = fu
    N["montagens"] = mt
    N["melhor_giro"] = {**melhor, "zonas": {z: intervalos(v_m, z) for z in ZONAS},
                        "rms_N_m": aj_m["rms"], "erro_max_N_m": aj_m["max"],
                        "forca_pose_N": aj_m["k"]*aj_m["x0"],
                        "forca_inicio_N": float(aj_m["k"]*(aj_m["x0"] + aj_m["dx"][0])),
                        "forca_fim_N": float(aj_m["k"]*(aj_m["x0"] + aj_m["dx"][-1])),
                        "transm_max": float(v_m["transm"].max()),
                        "dx_total_ate_limite": float(v_m["dx"][-1])}
    # peso do apoio de braço (massas do CAD), com o came girando com as polias
    geo = ma.geometria()
    dtp = np.degrees(v["tp"]) - np.interp(N["theta_pose"], v["theta"], np.degrees(v["tp"]))
    peso = ma.momento(geo, v["theta"], dtp)
    peso_fixo = ma.momento(geo, v["theta"])
    _, hum_art = membro_superior(MEMBRO_ARTIGO)
    iner, izz_apoio = ma.inercia_o(geo)
    tot = conjunto_total(hum, geo, izz_apoio)
    tau_hum = -ma.G*sum(c["massa"]*c["d"] for c in segs)/1000*np.cos(np.radians(v["theta"]))
    tau_g = -(tau_hum + peso)                                       # módulo, N·m
    aj_p = ajuste_mola(v, th16, aasm, cc.theta_fig16(q_lim) - 0.05, c, peso)
    i_max = int(np.argmin(peso))
    N["peso_apoio"] = {
        **{k: geo[k] for k in ("O", "D", "P", "L", "L_14D", "chassi_grau", "c2_chassi_14D", "c2_grau",
                               "eixo_grau", "giro_peca_grau", "corpos", "massa_g", "cg", "d", "a",
                               "came", "came_chassi_peca", "came_chassi_14D", "espelhamento")},
        "inercia": iner, "izz_o_kgm2": izz_apoio,
        "mola_desenho": ma.mola_no_desenho(geo), "pivo": ma.sensibilidade_pivo(geo),
        "momento_max_N_m": float(-peso[i_max]), "theta_momento_max": float(v["theta"][i_max]),
        "momento_max_fixo_N_m": ma.G*geo["massa_g"]*geo["d"]/1e6, "theta_max_fixo": -geo["a"],
        "momento_pose_N_m": float(-np.interp(N["theta_pose"], v["theta"], peso)),
        "momento_zero_N_m": float(-np.interp(0.0, v["theta"], peso)),
        "came_variacao_max_N_m": float(np.max(np.abs(peso - peso_fixo))),
        "mola_incerteza_N_m": ma.G*geo["corpos"]["mola"]["massa_g"]*abs(N["dx_total_ate_limite"])/2/1e6,
        "mola_10mm_N_m": ma.G*geo["corpos"]["mola"]["massa_g"]*10/1e6,
        "ajuste_com_peso": {"k_N_por_mm": aj_p["k"], "x0_mm": aj_p["x0"], "r2": aj_p["r2"],
                            "rms_N_m": aj_p["rms"], "erro_max_N_m": aj_p["max"],
                            "forca_pose_N": aj_p["k"]*aj_p["x0"],
                            "forca_inicio_N": float(aj_p["k"]*(aj_p["x0"] + aj_p["dx"][0])),
                            "forca_fim_N": float(aj_p["k"]*(aj_p["x0"] + aj_p["dx"][-1]))},
    }
    N["membro"] = {"segmentos": segs, **hum,
                   "artigo_momento_horizontal_N_m": hum_art["momento_horizontal_N_m"],
                   "artigo_massa": hum_art["massa"]}
    N["conjunto"] = {**tot, "tau_g_max_N_m": float(tau_g.max()),
                     "theta_tau_g_max": float(v["theta"][np.argmax(tau_g)]),
                     "tau_g_zero_N_m": float(np.interp(0.0, v["theta"], tau_g)),
                     "awm_amplitude": awm, "awm_escala_N_m": aj["c"]*awm}
    # confronto com o torque gravitacional, nos ângulos marcados e no limite de subida
    tau_mod = aj["k"]*(aj["x0"] + v["dx"])*v["transm"]/1000
    confr = []
    for T in (-75.0, -56.4, -40.3, -23.8, 0.0, 4.0, 21.0):
        tg = float(np.interp(T, v["theta"], tau_g))
        aa = float(aj["c"]*np.interp(T, th16, aasm))
        tm = float(np.interp(T, v["theta"], tau_mod))
        confr.append({"theta": T, "aasm_N_m": aa, "modelo_N_m": tm, "tau_g_N_m": tg,
                      "razao_aasm": aa/tg, "razao_modelo": tm/tg})
    N["confronto"] = {"linhas": confr, "theta_pico_aasm": float(th16[np.argmax(aasm)]),
                      "theta_pico_modelo": float(v["theta"][np.argmax(tau_mod)]),
                      "pico_modelo_N_m": float(tau_mod.max())}
    pts, th_max, n16, n_rm, fecha = pontos_fig16()
    N["fig16"] = {"pontos": pts, "theta_max_aasm": th_max, "n_pontos": n16, "n_rm": n_rm,
                  "fechamento_max": fecha, "aasm_max": float(aasm.max())}
    N["verificacoes"] = verificacoes(v, geo, conf)
    # Figura 16: faixa acima de 95% do máximo, razão AASM/|AWM| na horizontal e escala alternativa
    i0 = int(np.argmax(aasm))
    lo = hi = i0
    while lo > 0 and aasm[lo - 1] >= 0.95*aasm[i0]:
        lo -= 1
    while hi < len(aasm) - 1 and aasm[hi + 1] >= 0.95*aasm[i0]:
        hi += 1
    awm_zero = -awm*np.cos(0.0)
    N["fig16"].update({"faixa_95": [float(th16[lo]), float(th16[hi])],
                       "aasm_inicio": float(aasm[0]), "aasm_fim": float(aasm[-1]),
                       "aasm_awm_zero": float(np.interp(0.0, th16, aasm)/abs(awm_zero))})
    # escala do artigo, para comparação: k e as forças crescem na razão das escalas, e x0 e
    # R² não mudam no ajuste sem o peso do apoio
    c_art = ESCALA_ARTIGO/float(aasm.max())
    f_art = c_art/c
    N["escala"] = {"c": c, "aasm_max_N_m": c*float(aasm.max()), "awm_N_m": c*awm,
                   "membro_N_m": hum["momento_horizontal_N_m"]}
    N["escala_artigo"] = {"c": c_art, "razao": f_art, "aasm_max_N_m": ESCALA_ARTIGO,
                          "awm_N_m": c_art*awm,
                          "awm_sobre_membro": c_art*awm/hum["momento_horizontal_N_m"],
                          "awm_sobre_membro_artigo": c_art*awm/hum_art["momento_horizontal_N_m"],
                          "awm_sobre_conjunto": c_art*awm/N["conjunto"]["tau_g_zero_N_m"],
                          "k_N_por_mm": aj["k"]*f_art, "x0_mm": aj["x0"],
                          "forca_pose_N": aj["k"]*aj["x0"]*f_art, "r2": aj["r2"],
                          "rms_N_m": aj["rms"]*f_art, "erro_max_N_m": aj["max"]*f_art,
                          "forca_inicio_N": float(aj["k"]*(aj["x0"] + aj["dx"][0]))*f_art,
                          "forca_fim_N": float(aj["k"]*(aj["x0"] + aj["dx"][-1]))*f_art}
    q0, s0_ = cc.circuito_por_teta(cc.GAMA + 180)[0]
    assert s0_ > 0
    N["ponto_morto"] = {"q": float(q0), "theta": cc.theta_fig16(q0)}
    S_, fi_, *_ = cc.circuito(cc.Q_CAD)
    Dp = cc.C2*cc.u(180 - cc.Q_CAD)
    N["pontos_cad"] = {"A": (-cc.C1*cc.u(cc.GAMA)).tolist(), "D": Dp.tolist(),
                       "T": (Dp + cc.R*cc.u(fi_)).tolist()}
    N["confronto"]["theta_pico_tau_g"] = N["conjunto"]["theta_tau_g_max"]
    PASTA.mkdir(exist_ok=True)
    with open(PASTA/"exo3_tcc_numeros.json", "w", encoding="utf-8") as fh:
        json.dump(N, fh, ensure_ascii=False, indent=1)
    figura_circuito(v)
    figura_came()
    figura_varredura(v, q_lim)
    figura_fig16(aj, th16, aasm, v, sens, melhor, aj_m, v_m)
    figura_montagens(mt, curvas_mt, th16, aasm, c, sens, fu["passo"])

    print(f"R20 = {R20:.2f} mm (R20/R = {R20/cc.R:.3f}); limite de subida Θ = {N['theta_limite']:.2f}°")
    for z, fx in N["zonas"].items():
        print(f"  saída na {z}: " + "; ".join(f"Θ de {a:.1f}° a {c:.1f}°" for a, c in fx))
    for nome, p in pontos.items():
        print(f"  {nome:13s} Θ {p['theta']:7.2f}  q {p['q']:7.2f}  braço {p['braco']:6.2f}  r {p['r']:6.2f}  "
              f"ρ {p['rho']:6.2f}  {p['zona'] or '-':3s}  τ/Fs {p['transm']:6.2f} mm  Δx {p['dx']:7.2f} mm")
    print(f"τ/F_s máximo {N['transm_max']:.2f} mm em Θ = {N['theta_transm_max']:.1f}°; Δx até o limite "
          f"{N['dx_total_ate_limite']:.1f} mm")
    print(f"conferência τ/F_s = −dx/dΘ: diferença máxima relativa {conf:.1e}")
    a = N["ajuste"]
    print(f"ajuste à Figura 16 ({a['n_pontos']} pontos, Θ até {a['theta_max_ajuste']:.0f}°): k = {a['k_N_por_mm']:.3f} N/mm, "
          f"x0 = {a['x0_mm']:.1f} mm, F na pose = {a['forca_pose_N']:.0f} N; RMS {a['rms_N_m']:.2f} N·m, "
          f"erro máximo {a['erro_max_N_m']:.2f} N·m, R² = {a['r2']:.3f}")
    m = N["melhor_giro"]
    print(f"melhor giro físico: {m['giro']:+.0f}°: R² = {m['r2']:.3f}, RMS {m['rms_N_m']:.2f} N·m, "
          f"k = {m['k']:.3f} N/mm, x0 = {m['x0']:.1f} mm; " +
          "; ".join(f"{z} de {a_:.1f}° a {c_:.1f}°" for z, fx in m["zonas"].items() for a_, c_ in fx))
    print(f"giros com o cabo da mola no canal em toda a faixa: de {N['giro_valido'][0]:+.0f}° a "
          f"{N['giro_valido'][1]:+.0f}°")
    print(f"furos em torno do 572: passo {fu['passo']:.2f}°, raio {fu['raio_mm']:.2f} mm, centro do arco a "
          f"{fu['centro_came']:.1f}° no referencial da 15B; conferência do comprimento do cabo "
          f"{mt['conferencia_comprimento_mm']:.1e} mm")
    for x in mt["linhas"]:
        aj_ = x["ajuste"]
        print(f"  {x['furos']:+d} furos ({x['giro']:+7.2f}°, {x['pares']} pares): Θ válido de "
              f"{x['theta_valido'][0]:6.1f}° a {x['theta_valido'][1]:5.1f}°; F de {x['forca_N'][0]:5.1f} a "
              f"{x['forca_N'][1]:5.1f} N; τ máx {x['tau_max_N_m']:5.2f} N·m em {x['theta_tau_max']:6.1f}°; "
              f"R² mesma mola {x['r2_mesma_mola']:6.3f}; outra mola k {aj_['k']:6.3f} x0 {aj_['x0']:8.1f} "
              f"R² {aj_['r2']:.3f}{'' if aj_['fisico'] else ' (sem mola física)'}")
    pa, cj, mb = N["peso_apoio"], N["conjunto"], N["membro"]
    print(f"membro: {mb['massa']:.3f} kg a {mb['d']:.2f} mm, I_O = {mb['izz_o']:.6f} kg·m², "
          f"{mb['momento_horizontal_N_m']:.3f} N·m na horizontal (membro do artigo: {mb['artigo_momento_horizontal_N_m']:.3f})")
    print(f"apoio: {pa['massa_g']:.1f} g a {pa['d']:.2f} mm e {pa['a']:.2f}°, I_O = {pa['izz_o_kgm2']:.6f} kg·m²; "
          f"momento até {pa['momento_max_N_m']:.3f} N·m (Θ = {pa['theta_momento_max']:.1f}°), {pa['momento_zero_N_m']:.3f} "
          f"na horizontal, {pa['momento_pose_N_m']:.3f} na pose; came até {pa['came_variacao_max_N_m']:.3f}")
    print(f"conjunto: {cj['massa']:.3f} kg a {cj['d']:.2f} mm e {cj['a']:.2f}°, I_O = {cj['izz_o']:.6f} kg·m², "
          f"M g d = {cj['amplitude_N_m']:.3f} N·m; τ_g máximo {cj['tau_g_max_N_m']:.3f} em Θ = {cj['theta_tau_g_max']:.1f}°, "
          f"{cj['tau_g_zero_N_m']:.3f} na horizontal; AWM {cj['awm_escala_N_m']:.2f} N·m na escala adotada")
    ap = pa["ajuste_com_peso"]
    print(f"ajuste com o peso do apoio: k = {ap['k_N_por_mm']:.3f} N/mm, x0 = {ap['x0_mm']:.1f} mm, "
          f"R² = {ap['r2']:.3f}, RMS {ap['rms_N_m']:.2f} N·m")
    for x in N["confronto"]["linhas"]:
        print(f"  Θ {x['theta']:6.1f}: AASM {x['aasm_N_m']:6.2f}  modelo {x['modelo_N_m']:6.2f}  τ_g {x['tau_g_N_m']:6.2f}  "
              f"razões {x['razao_aasm']:.2f} e {x['razao_modelo']:.2f}")
    print("verificações:", json.dumps(N["verificacoes"], ensure_ascii=False))


if __name__ == "__main__":
    main()
