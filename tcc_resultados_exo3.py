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
   Figura 16, na escala do artigo de Okabe, Brittes e Brito (2026): 30 N·m no máximo;
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
from poses_fig14 import contorno_15a  # noqa: E402

PASTA = RAIZ/"results"
FIG14 = RAIZ/"patentes"/"US9737374B2_fig14cd.png"
FIG16 = RAIZ/"exo3"/"fig16_curvas.csv"

# medidos por exo3/poses_fig14.py
Q_14D = 61.19                       # q desenhado na Figura 14D (graus)
GIRO_CAME_14D = 254.0               # giro do referencial da Figura 15B na 14D (graus)
CABO_C2 = -21.80                    # direção de 572 para 632 em relação a C2, na 14D (graus)
R20 = (31.96 + 32.11)/2             # mm, média das Figuras 14C e 14D
O_14D, ESC_14D = np.array([1711.82, 965.50]), 1.6802      # px e px/mm
ESCALA_AASM = 30.0                  # N·m no máximo da curva AASM (artigo)
MARCAS_FIG16 = {"Z12": (-56.4, -40.3), "Z11": (-23.8, 4.0)}
# membro superior do artigo, com os centros de massa de de Leva (1996): kg e mm do ombro
MEMBRO = {"braço": (2.244, 162.6), "antebraço": (1.341, 281.7 + 123.4),
          "mão": (0.505, 281.7 + 269.8 + 68.1)}

SUPERFICIE, TINTA, TINTA_2, GRADE = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
AZUL, LARANJA, VERDE = "#2a78d6", "#eb6834", "#1baf7a"
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
             tp=tp, n_cam=n_cam, r=r_mm, rho=rho_mm, zona=zonas, transm=transm, dx=dx)
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


def ajuste_mola(v, th16, aasm, theta_max, peso=None):
    """Mola linear contra a AASM na escala do artigo; com peso (N·m em v["theta"]), o
    alvo é a AASM mais o que a mola gasta para sustentar o apoio de braço."""
    c = ESCALA_AASM/aasm.max()
    usar = th16 <= theta_max
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


def sensibilidade(th16, aasm, theta_max):
    """Ajuste da mola com o came girado de −120° a +40° em relação ao desenho da 14D."""
    linhas = []
    for d in np.arange(-120.0, 40.01, 1.0):
        v, _ = varredura(d)
        aj = ajuste_mola(v, th16, aasm, theta_max)
        z11 = intervalos(v, "Z11")
        linhas.append({"giro": float(d), "r2": aj["r2"], "rms": aj["rms"], "k": float(aj["k"]),
                       "x0": float(aj["x0"]), "z11": [list(map(float, z)) for z in z11]})
    fisicos = [x for x in linhas if x["k"] > 0 and x["x0"] > 0]
    melhor = max(fisicos, key=lambda x: x["r2"])
    return linhas, melhor


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
            label="AASM da Figura 16, na escala do artigo")
    ax.plot(th16[fora], aj["c"]*aasm[fora], "o", ms=3.0, color="#bdbcb7",
            label="acima do limite de subida desta ancoragem")
    tg = v["theta"][(v["theta"] >= -75) & (v["theta"] <= aj["theta"].max())]
    g = np.interp(tg, v["theta"], v["transm"])
    dx = np.interp(tg, v["theta"], v["dx"])
    ax.plot(tg, aj["k"]*(aj["x0"] + dx)*g/1000, color=LARANJA, lw=1.8,
            label="modelo com mola linear ajustada")
    ax.set_xlabel("Θ (graus)", color=TINTA_2)
    ax.set_ylabel("momento no pivô 584 (N·m)", color=TINTA_2)
    ax.set_ylim(0, 33)
    ax.text(0.0, 1.02, titulo, transform=ax.transAxes, fontsize=8.5, color=TINTA)


def figura_fig16(aj, th16, aasm, v, sens, melhor, aj_m, v_m):
    fig, axs = plt.subplots(2, 2, figsize=(10, 8.2), dpi=200, facecolor=SUPERFICIE)
    (a, b), (c, d) = axs
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
    eixos(c, 0, 2)
    gs = np.array([x["giro"] for x in sens])
    r2 = np.array([x["r2"] for x in sens])
    fis = np.array([x["k"] > 0 and x["x0"] > 0 for x in sens])
    c.plot(gs, np.where(fis, r2, np.nan), color=AZUL, lw=1.8, label="mola com k > 0 e x0 > 0")
    c.plot(gs, np.where(fis, np.nan, r2), color="#bdbcb7", lw=1.4, ls="--",
           label="sem solução física (k ou x0 negativo)")
    c.axvline(0, color=TINTA_2, lw=0.8, ls=":")
    c.axvline(melhor["giro"], color=LARANJA, lw=1.0)
    c.set_xlabel("giro do came em relação ao desenho da Figura 14D (graus)", color=TINTA_2)
    c.set_ylabel("R² do ajuste da mola", color=TINTA_2)
    c.set_ylim(0.5, 1.0)
    c.legend(loc="lower right", frameon=False, fontsize=7)
    c.text(0.0, 1.02, "(c) sensibilidade ao giro do came", transform=c.transAxes, fontsize=8.5,
           color=TINTA)
    painel_ajuste(d, aj_m, th16, aasm, v_m, f"(d) came girado de {num(melhor['giro'], 0)}°: "
                  f"R² = {num(aj_m['r2'], 3)}")
    fig.tight_layout()
    fig.savefig(PASTA/"exo3_tcc_fig_4_fig16.png", facecolor=SUPERFICIE)
    plt.close(fig)


# ---------------------------------------------------------------------- principal
def main():
    v, q_lim = varredura()
    th16, aasm = fig16()
    aj = ajuste_mola(v, th16, aasm, cc.theta_fig16(q_lim) - 0.05)
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
    sens, melhor = sensibilidade(th16, aasm, cc.theta_fig16(q_lim) - 0.05)
    v_m, _ = varredura(melhor["giro"])
    aj_m = ajuste_mola(v_m, th16, aasm, cc.theta_fig16(q_lim) - 0.05)
    N["sensibilidade_giro"] = sens
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
    membro = sum(m*d for m, d in MEMBRO.values())*ma.G/1000          # N·m na horizontal
    awm = amplitude_awm()
    aj_p = ajuste_mola(v, th16, aasm, cc.theta_fig16(q_lim) - 0.05, peso)
    i_max = int(np.argmin(peso))
    N["peso_apoio"] = {
        **{k: geo[k] for k in ("O", "D", "P", "L", "L_14D", "chassi_grau", "c2_chassi_14D", "c2_grau",
                               "eixo_grau", "giro_peca_grau", "corpos", "massa_g", "cg", "d", "a", "nailon",
                               "came", "came_chassi_peca", "came_chassi_14D")},
        "momento_max_N_m": float(-peso[i_max]), "theta_momento_max": float(v["theta"][i_max]),
        "momento_max_fixo_N_m": ma.G*geo["massa_g"]*geo["d"]/1e6, "theta_max_fixo": -geo["a"],
        "momento_pose_N_m": float(-np.interp(N["theta_pose"], v["theta"], peso)),
        "momento_zero_N_m": float(-np.interp(0.0, v["theta"], peso)),
        "came_variacao_max_N_m": float(np.max(np.abs(peso - peso_fixo))),
        "came_amplitude_N_m": ma.G*geo["corpos"]["came"]["massa_g"]*geo["came"]["excentricidade_mm"]/1e6,
        "mola_incerteza_N_m": ma.G*geo["corpos"]["mola"]["massa_g"]*abs(N["dx_total_ate_limite"])/2/1e6,
        "membro_horizontal_N_m": membro, "awm_amplitude": awm, "awm_escala_N_m": aj["c"]*awm,
        "carga_horizontal_N_m": membro + float(-np.interp(0.0, v["theta"], peso)),
        "ajuste_com_peso": {"k_N_por_mm": aj_p["k"], "x0_mm": aj_p["x0"], "r2": aj_p["r2"],
                            "rms_N_m": aj_p["rms"], "erro_max_N_m": aj_p["max"],
                            "forca_pose_N": aj_p["k"]*aj_p["x0"],
                            "forca_inicio_N": float(aj_p["k"]*(aj_p["x0"] + aj_p["dx"][0])),
                            "forca_fim_N": float(aj_p["k"]*(aj_p["x0"] + aj_p["dx"][-1]))},
    }
    PASTA.mkdir(exist_ok=True)
    with open(PASTA/"exo3_tcc_numeros.json", "w", encoding="utf-8") as fh:
        json.dump(N, fh, ensure_ascii=False, indent=1)
    figura_circuito(v)
    figura_came()
    figura_varredura(v, q_lim)
    figura_fig16(aj, th16, aasm, v, sens, melhor, aj_m, v_m)

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
    pa = N["peso_apoio"]
    print(f"apoio de braço: {pa['massa_g']:.1f} g, centro de massa a {pa['d']:.2f} mm de 584 e {pa['a']:.2f}° "
          f"acima do eixo; momento do peso até {pa['momento_max_N_m']:.3f} N·m (Θ = {pa['theta_momento_max']:.1f}°), "
          f"{pa['momento_zero_N_m']:.3f} N·m na horizontal e {pa['momento_pose_N_m']:.3f} N·m na pose; o came "
          f"muda até {pa['came_variacao_max_N_m']:.3f} N·m")
    print(f"membro superior na horizontal {pa['membro_horizontal_N_m']:.3f} N·m; carga total "
          f"{pa['carga_horizontal_N_m']:.3f} N·m; AWM = −{pa['awm_amplitude']:.2f} cos Θ, "
          f"{pa['awm_escala_N_m']:.2f} N·m na escala do artigo")
    ap = pa["ajuste_com_peso"]
    print(f"ajuste com o peso do apoio: k = {ap['k_N_por_mm']:.3f} N/mm, x0 = {ap['x0_mm']:.1f} mm, "
          f"F na pose = {ap['forca_pose_N']:.0f} N, R² = {ap['r2']:.3f}, RMS {ap['rms_N_m']:.2f} N·m")


if __name__ == "__main__":
    main()
