"""
Contorno do fundo do canal do came 570 (Figura 15B da US 9.737.374 B2) e raio
efetivo do cabo da mola.

A Figura 15B é um corte pelo plano do canal: a área hachurada é o fundo do
canal, onde o cabo 634 assenta. O contorno sai em quatro passos:

1. Faixas da hachura. Os vãos brancos entre as linhas de hachura são faixas
   retas e paralelas, a cerca de -45° na imagem, com a largura do passo da
   hachura. Para separá-las do branco do canal nos pontos em que a borda tem
   falhas (onde passam cotas e chamadas), o branco é erodido antes de rotular.
   Ficam só as faixas com a inclinação, a largura e a forma retangular da
   hachura; o canal, mais largo e curvo, sai.
2. Região hachurada: as faixas, mais as linhas de hachura entre elas.
3. Lascas, cunhas e entalhes. Dentro da envoltória convexa da região, cada
   pedaço branco é preenchido se nenhum ponto dele fica a mais de 26 px da
   região (largura de uma faixa mais a linha), repetindo até estabilizar. O
   bolsão do 573, os chifres dele e o canal têm partes bem mais longe e ficam
   de fora. O furo 654 é preenchido.
4. Contorno fechado da região (contourpy), centrado no furo 654.

O raio efetivo é o que entra na relação F_cabo_560 = F_mola * r_e / R: a
distância do pino 572 à linha do cabo da mola onde ele deixa o canal. O cabo
tracionado passa reto sobre concavidades, então o raio efetivo é a função
suporte da envoltória convexa do canal: para cada direção normal ao cabo, a
maior projeção dos pontos do canal.

Ângulos em graus, anti-horários a partir da horizontal à direita, na Figura 15B
girada para a leitura. Comprimentos divididos por R20, o raio médio da zona Z10
(R20 = R21 na patente). As zonas vão das linhas de chamada das cotas Z10, Z11 e
Z12, que são radiais e foram localizadas na própria imagem.

Rodar (na raiz do repositório):
    python exo3/extrair_came570.py
"""
import csv
from pathlib import Path

import contourpy
import matplotlib
import numpy as np
import scipy.ndimage as nd
from matplotlib.path import Path as Caminho
from PIL import Image, ImageDraw
from scipy.spatial import ConvexHull

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FIGURA = RAIZ / "patentes" / "US9737374B2_fig15.png"
SAIDA = RAIZ / "exo3"
CORTE_X = 1350                     # px: a Figura 15B fica à direita da folha
FURO_654 = (2094.0, 1252.0)        # px, posição aproximada lida na figura
FURO_573 = (2156.0, 1085.0)
ZONAS = {"Z10": (89.6, 140.4), "Z11": (152.4, 218.8), "Z12": (242.6, 292.6)}
DIST_MAX = 26.0                    # px: largura de uma faixa (21) mais a linha


def disco(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x*x + y*y <= r*r


def circunferencia(B, aprox, rmin, rmax):
    """Circunferência ajustada aos pixels pretos de um contorno de furo."""
    cx, cy = aprox
    m = 90
    ys, xs = np.where(B[int(cy) - m:int(cy) + m, int(cx) - m:int(cx) + m])
    x, y = (xs + int(cx) - m).astype(float), (ys + int(cy) - m).astype(float)
    d = np.hypot(x - cx, y - cy)
    x, y = x[(d > rmin) & (d < rmax)], y[(d > rmin) & (d < rmax)]
    for _ in range(8):
        A = np.c_[2*x, 2*y, np.ones_like(x)]
        sol, *_ = np.linalg.lstsq(A, x*x + y*y, rcond=None)
        xc, yc = sol[0], sol[1]
        r = np.sqrt(sol[2] + xc*xc + yc*yc)
        res = np.abs(np.hypot(x - xc, y - yc) - r)
        manter = res < max(1.5, np.percentile(res, 60))
        x, y = x[manter], y[manter]
    return xc, yc, r


def estatisticas(lab, n, mask):
    idx = np.arange(1, n + 1)
    yy, xx = np.indices(mask.shape)
    area = nd.sum(mask, lab, idx)
    mx, my = nd.sum(xx, lab, idx)/area, nd.sum(yy, lab, idx)/area
    cxx = nd.sum(xx*xx, lab, idx)/area - mx*mx
    cyy = nd.sum(yy*yy, lab, idx)/area - my*my
    cxy = nd.sum(xx*yy, lab, idx)/area - mx*my
    tr, det = cxx + cyy, cxx*cyy - cxy*cxy
    disc = np.sqrt(np.maximum(tr*tr/4 - det, 0))
    larg = np.sqrt(12*np.maximum(tr/2 - disc, 0))
    comp = np.sqrt(12*np.maximum(tr/2 + disc, 0))
    ang = np.degrees(0.5*np.arctan2(2*cxy, cxx - cyy))
    return area, mx, my, larg, comp, ang


def regiao_hachurada(Bc, xc, yc):
    W = ~Bc
    # 1. faixas da hachura
    We = nd.binary_erosion(W, structure=disco(4))
    lab, n = nd.label(We)
    area, mx, my, larg, comp, ang = estatisticas(lab, n, We)
    borda = np.zeros(n + 1, bool)
    for fatia in (lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]):
        borda[np.unique(fatia)] = True
    faixa = ((np.abs(ang + 45) < 8) & (larg > 6) & (larg < 18) & (comp > 1.3*larg)
             & (area/np.maximum(comp*larg, 1) > 0.75) & ~borda[1:]
             & (np.hypot(mx - xc, my - yc) < 900) & (area > 40))
    # 2. faixas + linhas de hachura entre elas
    M = nd.binary_dilation(np.isin(lab, np.where(faixa)[0] + 1), structure=disco(4)) & W
    M = nd.binary_fill_holes(nd.binary_closing(M, structure=np.ones((9, 9))))
    lb, nb = nd.label(M)
    M = lb == (np.argmax(nd.sum(M, lb, range(1, nb + 1))) + 1)
    # 3. lascas, cunhas e entalhes dentro da envoltória convexa
    ys, xs = np.nonzero(M ^ nd.binary_erosion(M))
    casco = Caminho(np.c_[xs, ys][ConvexHull(np.c_[xs, ys]).vertices])
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    gy, gx = np.mgrid[y0:y1, x0:x1]
    dentro = np.zeros_like(M)
    dentro[y0:y1, x0:x1] = casco.contains_points(np.c_[gx.ravel(), gy.ravel()]).reshape(gy.shape)
    D = dentro & ~M & W
    ld, nd_ = nd.label(D)
    tam = nd.sum(D, ld, range(1, nd_ + 1))
    Mi = M.copy()
    for _ in range(8):
        dmax = nd.maximum(nd.distance_transform_edt(~Mi), ld, range(1, nd_ + 1))
        sel = (tam < 6000) & (dmax <= DIST_MAX)
        novo = M | np.isin(ld, np.where(sel)[0] + 1)
        novo = nd.binary_closing(novo, structure=np.ones((5, 5))) & (novo | ~W)
        if (novo == Mi).all():
            break
        Mi = novo
    M = nd.binary_closing(M | np.isin(ld, np.where(sel)[0] + 1), structure=np.ones((7, 7)))
    yy, xx = np.indices(M.shape)
    M |= (xx - xc)**2 + (yy - yc)**2 <= 63.0**2          # furo 654
    M = nd.binary_fill_holes(M)
    lb, nb = nd.label(M)
    M = lb == (np.argmax(nd.sum(M, lb, range(1, nb + 1))) + 1)
    return M, int(faixa.sum()), int(sel.sum()), sorted(int(t) for t in tam[~sel])[-3:]


def zona(a):
    for z, (a0, a1) in ZONAS.items():
        if a0 <= a % 360 <= a1:
            return z
    return ""


def main():
    B = np.array(Image.open(FIGURA).convert("L")) < 128
    X654, Y654, r654 = circunferencia(B, FURO_654, 30, 70)
    X573, Y573, r573 = circunferencia(B, FURO_573, 25, 55)
    Bc = B[:, CORTE_X:]
    xc, yc = X654 - CORTE_X, Y654
    M, n_faixas, n_lascas, mantidos = regiao_hachurada(Bc, xc, yc)
    cont = max(contourpy.contour_generator(z=M.astype(float)).lines(0.5), key=len)

    # coordenadas centradas no furo 654, com y para cima
    P = np.c_[cont[:, 0] - xc, -(cont[:, 1] - yc)]
    ang = np.degrees(np.arctan2(P[:, 1], P[:, 0])) % 360
    rad = np.hypot(P[:, 0], P[:, 1])
    z10 = (ang >= ZONAS["Z10"][0]) & (ang <= ZONAS["Z10"][1])
    R20 = float(np.mean(rad[z10]))

    # envoltória radial: maior raio do contorno em cada direção (o bolsão fica por baixo)
    grade = np.arange(0.0, 360.0, 0.5)
    env = np.array([rad[np.abs(((ang - a + 180) % 360) - 180) <= 0.5].max() for a in grade])

    def r_em(a):
        return float(np.interp(a % 360, grade, env, period=360))

    # raio efetivo: função suporte da envoltória convexa
    casco = P[ConvexHull(P).vertices]
    h, saida = [], []
    for fi in grade:
        n_ = np.array([np.cos(np.radians(fi)), np.sin(np.radians(fi))])
        proj = casco @ n_
        k = int(np.argmax(proj))
        h.append(proj[k]/R20)
        saida.append(np.degrees(np.arctan2(casco[k, 1], casco[k, 0])) % 360)
    h, saida = np.array(h), np.array(saida)

    # reta da zona Z12: desvio dos pontos do contorno em relação à reta ajustada
    z12 = (ang >= ZONAS["Z12"][0] + 2) & (ang <= ZONAS["Z12"][1] - 2)
    q = P[z12]
    c0 = q.mean(axis=0)
    _, _, vt = np.linalg.svd(q - c0)
    desvio_z12 = np.abs((q - c0) @ vt[1])

    with open(SAIDA / "came570_contorno.csv", "w", newline="", encoding="utf-8") as fh:
        fh.write("# Fundo do canal do came 570 (US 9.737.374 B2, Figura 15B), centrado no furo 654.\n"
                 "# Coordenadas e raio divididos por R20 (raio medio da zona Z10); angulo em graus,\n"
                 "# anti-horario a partir da horizontal a direita, figura girada para a leitura.\n"
                 "# Pontos na ordem do contorno fechado. Gerado por exo3/extrair_came570.py.\n")
        w = csv.writer(fh, delimiter=";")
        w.writerow(["x_R20", "y_R20", "angulo_grau", "raio_R20", "zona"])
        for (x, y), a, r in zip(P[::2], ang[::2], rad[::2]):
            w.writerow([f"{x/R20:.4f}".replace(".", ","), f"{y/R20:.4f}".replace(".", ","),
                        f"{a:.2f}".replace(".", ","), f"{r/R20:.4f}".replace(".", ","), zona(a)])
    with open(SAIDA / "came570_raio_efetivo.csv", "w", newline="", encoding="utf-8") as fh:
        fh.write("# Raio efetivo do came 570 para o cabo da mola: distancia do pino 572 a linha do cabo,\n"
                 "# dividida por R20, em funcao da direcao normal ao cabo (no referencial do came).\n"
                 "# saida_grau: direcao, a partir do centro, do ponto em que o cabo deixa o canal.\n")
        w = csv.writer(fh, delimiter=";")
        w.writerow(["normal_grau", "raio_efetivo_R20", "saida_grau", "zona_da_saida"])
        for fi, hh, s in zip(grade, h, saida):
            w.writerow([f"{fi:.1f}".replace(".", ","), f"{hh:.4f}".replace(".", ","),
                        f"{s:.1f}".replace(".", ","), zona(s)])

    conferencia(Bc, M, cont, xc, yc)
    grafico(P/R20, ang, rad/R20, grade, env/R20, h, saida, casco/R20,
            (X573 - X654)/R20, -(Y573 - Y654)/R20, r573/R20, r654/R20)

    print(f"faixas da hachura: {n_faixas}; lascas e entalhes preenchidos: {n_lascas}; "
          f"maiores brancos mantidos (px²): {mantidos}")
    print(f"furo 654: centro ({X654:.1f}, {Y654:.1f}) px, raio {r654:.1f} px = {r654/R20:.4f} R20")
    print(f"R20 = {R20:.1f} px; zona Z10: raio de {rad[z10].min()/R20:.4f} a {rad[z10].max()/R20:.4f} R20")
    for z, (a0, a1) in ZONAS.items():
        print(f"{z}: {a0:.1f}° a {a1:.1f}°; raio nas pontas {r_em(a0)/R20:.4f} e {r_em(a1)/R20:.4f} R20")
    print(f"reta da zona Z12: desvio máximo {desvio_z12.max():.2f} px ({desvio_z12.max()/R20:.4f} R20)")
    d573 = np.hypot(X573 - X654, Y573 - Y654)
    a573 = np.degrees(np.arctan2(-(Y573 - Y654), X573 - X654)) % 360
    print(f"furo 573: a {d573/R20:.4f} R20 do centro, a {a573:.1f}°, raio {r573/R20:.4f} R20")
    print(f"raio efetivo: de {h.min():.4f} a {h.max():.4f} R20")
    for z in ZONAS:
        s = np.array([zona(a) == z for a in saida])
        print(f"  cabo saindo na {z}: {h[s].min():.4f} a {h[s].max():.4f} R20, "
              f"em {s.sum()*0.5:.1f}° de direção do cabo")


def conferencia(Bc, M, cont, xc, yc):
    img = Image.fromarray(np.where(Bc, 0, 255).astype(np.uint8)).convert("RGB")
    img = Image.composite(Image.new("RGB", img.size, (255, 175, 175)), img,
                          Image.fromarray((M*85).astype(np.uint8)))
    d = ImageDraw.Draw(img)
    d.line([tuple(p) for p in cont] + [tuple(cont[0])], fill=(200, 0, 0), width=2)
    d.ellipse((xc - 6, yc - 6, xc + 6, yc + 6), fill=(0, 0, 230))
    ox, oy = int(xc - 760), int(yc - 760)
    img.crop((ox, oy, ox + 1140, oy + 1140)).save(SAIDA / "figuras" / "came570_conferencia.png")
    janelas = [(380, 420), (330, 520), (760, 440), (760, 560), (790, 840), (520, 900), (630, 900)]
    det = Image.new("RGB", (len(janelas)*330, 330), (255, 255, 255))
    for k, (wx, wy) in enumerate(janelas):
        c = img.crop((ox + wx - 55, oy + wy - 55, ox + wx + 110, oy + wy + 110))
        det.paste(c.resize((330, 330), Image.NEAREST), (k*330, 0))
    det.save(SAIDA / "figuras" / "came570_conferencia_detalhes.png")


def grafico(Pn, ang, radn, grade, envn, h, saida, cascon, x573, y573, r573, r654):
    cores = {"Z10": "#2a78d6", "Z11": "#eb6834", "Z12": "#1baf7a"}   # paleta categórica validada
    tinta, tinta2, neutro, grade_cor = "#0b0b0b", "#5f5e5a", "#9a9a94", "#e6e5e0"
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": tinta2, "axes.labelcolor": tinta,
                         "xtick.color": tinta2, "ytick.color": tinta2})
    fig, ax = plt.subplots(1, 3, figsize=(15, 5.4), dpi=150,
                           gridspec_kw={"width_ratios": [1.0, 1.25, 1.25]})
    fig.patch.set_facecolor("#fcfcfb")

    a = ax[0]
    a.plot(np.r_[cascon[:, 0], cascon[0, 0]], np.r_[cascon[:, 1], cascon[0, 1]], ls="--",
           lw=1.0, color=neutro, label="envoltória convexa (caminho do cabo)")
    a.plot(np.r_[Pn[:, 0], Pn[0, 0]], np.r_[Pn[:, 1], Pn[0, 1]], lw=1.4, color=tinta2,
           label="fundo do canal")
    for z, cor in cores.items():
        s = np.array([zona(v) == z for v in ang])
        a.plot(np.where(s, Pn[:, 0], np.nan), np.where(s, Pn[:, 1], np.nan), lw=3.0, color=cor,
               solid_capstyle="round", label=f"zona {z}")
        k = np.where(s)[0][len(np.where(s)[0])//2]
        a.annotate(z, (Pn[k, 0], Pn[k, 1]), xytext=(Pn[k, 0]*1.18, Pn[k, 1]*1.18),
                   ha="center", va="center", color=tinta, fontsize=10)
    t = np.linspace(0, 2*np.pi, 100)
    a.plot(r654*np.cos(t), r654*np.sin(t), lw=1.0, color=tinta2)
    a.plot(x573 + r573*np.cos(t), y573 + r573*np.sin(t), lw=1.0, color=tinta2)
    a.annotate("654", (0, 0), xytext=(0.0, -0.25), ha="center", color=tinta2, fontsize=9)
    a.annotate("573", (x573, y573), xytext=(x573, y573 + r573 + 0.05), ha="center", color=tinta2,
               fontsize=9)
    a.plot([0], [0], "+", color=tinta, ms=8)
    a.set_aspect("equal")
    a.set_xlabel("x / R20")
    a.set_ylabel("y / R20")
    a.set_title("(a) Fundo do canal, centrado no pino 572", loc="left", fontsize=10, color=tinta)
    a.grid(color=grade_cor, lw=0.6)
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=3, fontsize=7.5, frameon=False)

    a = ax[1]
    a.plot(grade, envn, lw=1.4, color=tinta2)
    for z, (a0, a1) in ZONAS.items():
        s = (grade >= a0) & (grade <= a1)
        a.plot(grade[s], envn[s], lw=3.0, color=cores[z], solid_capstyle="round")
        a.annotate(z, ((a0 + a1)/2, envn[s].max() + 0.05), ha="center", color=tinta, fontsize=10)
    a.annotate("bolsão\ndo 573\n(sem canal)", (38, envn[(grade > 10) & (grade < 60)].max() + 0.05),
               ha="center", color=tinta2, fontsize=8.5)
    a.set_xlim(0, 360)
    a.set_xticks(range(0, 361, 45))
    a.set_ylim(0, 1.15)
    a.set_xlabel("direção a partir do centro (°)")
    a.set_ylabel("raio do canal / R20")
    a.set_title("(b) Raio do canal (envoltória radial)", loc="left", fontsize=10, color=tinta)
    a.grid(color=grade_cor, lw=0.6)

    a = ax[2]
    a.plot(grade, h, lw=1.4, color=tinta2, label="saída fora das zonas")
    for z, cor in cores.items():
        s = np.array([zona(v) == z for v in saida])
        a.plot(np.where(s, grade, np.nan), np.where(s, h, np.nan), lw=3.0, color=cor,
               solid_capstyle="round", label=f"saída na zona {z}")
    a.set_xlim(0, 360)
    a.set_xticks(range(0, 361, 45))
    a.set_ylim(0, 1.15)
    a.set_xlabel("direção normal ao cabo, no referencial do came (°)")
    a.set_ylabel("raio efetivo / R20")
    a.set_title("(c) Raio efetivo para o cabo da mola", loc="left", fontsize=10, color=tinta)
    a.grid(color=grade_cor, lw=0.6)
    a.legend(loc="lower right", fontsize=7.5, frameon=False)

    for a in ax:
        a.set_facecolor("#fcfcfb")
        for lado in ("top", "right"):
            a.spines[lado].set_visible(False)
    fig.tight_layout()
    fig.savefig(SAIDA / "figuras" / "came570_raios.png", facecolor=fig.get_facecolor(),
                bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


if __name__ == "__main__":
    main()
