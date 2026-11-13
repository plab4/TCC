"""
Marcadores das curvas AASM, RM e AWM da Figura 16 da US 9.737.374 B2.

Cada curva da figura tem 27 marcadores, de Θ = −74° a 30°, a cada 4°: são os
pontos de dados que a patente desenhou, e a linha entre eles é só a ligação do
gráfico. Este script lê o valor de cada curva nesses ângulos a partir do traçado
de exo3/digitalizar_fig16.py (um ponto por grau, calibrado pela grade da própria
figura: Θ de −80° a 40° e momento de +100 a −100) e confere:

1. o fechamento RM = AASM + AWM, que a figura obedece e que denuncia erro de
   calibração do eixo vertical (um deslocamento b no eixo aparece inteiro no
   resíduo, porque AASM + AWM − RM = b);
2. a posição dos marcadores na imagem, pelo centro de cada símbolo encontrado
   perto do traçado (abertura morfológica, que apaga as linhas e deixa os
   símbolos).

Com o argumento opcional --leitura arquivo.csv (pares Θ;M de uma leitura manual,
por curva, com linhas "# AASM", "# RM" e "# AWM"), estima a calibração afim
dessa leitura contra os marcadores, M_lido = a M + b e Θ_lido = c Θ + d, e
mostra o resíduo antes e depois de corrigi-la.

Rodar (na raiz do repositório):
    python exo3/marcadores_fig16.py [--leitura arquivo.csv]
Grava exo3/fig16_marcadores.csv e exo3/figuras/fig16_marcadores.png.
"""
import sys
from pathlib import Path

import numpy as np
import scipy.ndimage as nd
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from digitalizar_fig16 import FIGURA, px_x, px_y, theta, momento  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
TRACADO = RAIZ / "exo3" / "fig16_curvas.csv"
SAIDA_CSV = RAIZ / "exo3" / "fig16_marcadores.csv"
SAIDA_PNG = RAIZ / "exo3" / "figuras" / "fig16_marcadores.png"
CURVAS = ("AASM", "RM", "AWM")
MARCADORES = np.arange(-74, 31, 4)


def ler_tracado():
    dados = {}
    for linha in TRACADO.read_text(encoding="utf-8").splitlines():
        if linha.startswith("#") or linha.startswith("theta"):
            continue
        c = linha.split(";")
        dados[int(c[0])] = [float(v.replace(",", ".")) if v else np.nan for v in c[1:]]
    return dados


def simbolos():
    """Centros dos símbolos da figura, em (Θ, M), depois de apagadas as linhas."""
    B = np.array(Image.open(FIGURA).convert("L")) < 128
    lab, n = nd.label(B, structure=np.ones((3, 3)))
    tam = nd.sum(B, lab, range(1, n + 1))
    F = np.isin(lab, np.where(tam > 40)[0] + 1)
    yy, xx = np.ogrid[-3:4, -3:4]
    A = nd.binary_opening(F, structure=(xx**2 + yy**2) <= 9)
    l2, n2 = nd.label(A)
    return [(theta(cx), momento(cy)) for cy, cx in nd.center_of_mass(A, l2, range(1, n2 + 1))]


def ler_leitura(caminho):
    pts, atual = {}, None
    for linha in Path(caminho).read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha.startswith("#"):
            atual = linha[1:].strip()
            pts[atual] = []
        elif linha:
            t, m = (float(v) for v in linha.replace(";", ",").split(","))
            pts[atual].append((t, m))
    return pts


def main():
    dados = ler_tracado()
    tab = np.array([dados[int(t)] for t in MARCADORES])            # AASM, RM, AWM
    fecho = tab[:, 0] + tab[:, 2] - tab[:, 1]
    ok = ~np.isnan(fecho)

    # conferência com os símbolos encontrados na imagem
    simb = simbolos()
    desvios = []
    for j in range(3):
        for t, v in zip(MARCADORES, tab[:, j]):
            if np.isnan(v):
                continue
            perto = [(abs(m - v), m) for ts, m in simb if abs(ts - t) <= 0.6 and abs(m - v) <= 3]
            if perto:
                desvios.append(min(perto)[1] - v)
    desvios = np.array(desvios)

    with open(SAIDA_CSV, "w", encoding="utf-8") as fh:
        fh.write("# US 9.737.374 B2, Fig. 16: valores das curvas nos 27 marcadores (Theta de -74 a 30 graus,\n"
                 "# a cada 4 graus), lidos no tracado de exo3/digitalizar_fig16.py. Unidade do momento nao\n"
                 "# informada na patente. Fechamento = AASM + AWM - RM (RM em branco onde o tracado da RM foi\n"
                 "# descartado). Gerado por exo3/marcadores_fig16.py.\n")
        fh.write("theta_grau;AASM;RM;AWM;fechamento\n")
        for t, (a, r, w), f in zip(MARCADORES, tab, fecho):
            num = lambda v: "" if np.isnan(v) else f"{v:.2f}".replace(".", ",")   # noqa: E731
            fh.write(f"{t};{num(a)};{num(r)};{num(w)};{num(f)}\n")

    im = Image.open(FIGURA).convert("RGB")
    d = ImageDraw.Draw(im)
    for j, cor in zip(range(3), ((220, 0, 0), (0, 140, 0), (0, 0, 220))):
        for t, v in zip(MARCADORES, tab[:, j]):
            if not np.isnan(v):
                x, y = px_x(t), px_y(v)
                d.ellipse((x - 5, y - 5, x + 5, y + 5), outline=cor, width=2)

    print(f"marcadores: {len(MARCADORES)} por curva, de {MARCADORES[0]}° a {MARCADORES[-1]}°")
    print(f"fechamento RM = AASM + AWM: {ok.sum()} marcadores, máx |resíduo| = {np.max(np.abs(fecho[ok])):.2f}, "
          f"médio {np.mean(fecho[ok]):+.2f}")
    print(f"símbolos da imagem junto aos marcadores: {len(desvios)}; desvio mediano "
          f"{np.median(desvios):+.2f}, RMS {np.sqrt(np.mean(desvios**2)):.2f} unidade")

    if "--leitura" in sys.argv[1:]:
        pts = ler_leitura(sys.argv[sys.argv.index("--leitura") + 1])
        X, Y, TX, TY = [], [], [], []
        for nome, ps in pts.items():
            j = CURVAS.index(nome)
            for (x, y), t, v in zip(ps, MARCADORES, tab[:, j]):
                if not np.isnan(v):
                    X.append(x), Y.append(y), TX.append(t), TY.append(v)
        X, Y, TX, TY = map(np.array, (X, Y, TX, TY))
        c, dd = np.polyfit(TX, X, 1)
        a, b = np.polyfit(TY, Y, 1)
        Xc, Yc = (X - dd)/c, (Y - b)/a
        lidas = {n: np.array([m for _, m in ps]) for n, ps in pts.items()}
        f_lido = lidas["AASM"] + lidas["AWM"] - lidas["RM"]
        print(f"leitura: M_lido = {a:.4f} M {b:+.3f}; Θ_lido = {c:.4f} Θ {dd:+.3f}")
        print(f"  antes da correção: |ΔM| máx {np.max(np.abs(Y - TY)):.2f}, |ΔΘ| máx {np.max(np.abs(X - TX)):.2f}°; "
              f"fechamento médio {np.mean(f_lido):+.2f}")
        print(f"  depois: ΔM RMS {np.sqrt(np.mean((Yc - TY)**2)):.2f} (máx {np.max(np.abs(Yc - TY)):.2f}), "
              f"ΔΘ RMS {np.sqrt(np.mean((Xc - TX)**2)):.2f}° (máx {np.max(np.abs(Xc - TX)):.2f}°)")
        for nome, ps in pts.items():
            for x, y in ps:
                d.rectangle((px_x(x) - 5, px_y(y) - 5, px_x(x) + 5, px_y(y) + 5), outline=(255, 140, 0), width=2)
    im.crop((0, 560, 1360, 1320)).save(SAIDA_PNG)
    print(f"gravados {SAIDA_CSV.relative_to(RAIZ)} e {SAIDA_PNG.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
