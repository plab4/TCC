"""
Digitaliza as curvas AASM, RM e AWM da Figura 16 da US 9.737.374 B2.

A figura vem da imagem nativa da página (1 bit, 72 ppp declarados) da folha 23
de 48, girada para a leitura: patentes/US9737374B2_fig16.png. A grade foi
localizada na própria imagem: Theta de -80° a 40° entre x = 31 px e x = 1294 px
(linhas verticais a cada 10°) e momento de +100 a -100 entre y = 639 px e
y = 1279 px (linhas horizontais a cada 20). A patente não informa a unidade do
momento.

Cada curva é rastreada coluna a coluna, pelo trecho preto mais próximo da
posição anterior, depois de retirada a grade pontilhada (componentes pequenos).
O valor em cada grau é a mediana dos pontos a menos de 0,5° dele. A RM só é
mantida onde fecha com AASM + AWM a menos de 2 unidades: perto das pontas, a
linha de chamada do rótulo RM cruza a curva.

Rodar (na raiz do repositório):
    python exo3/digitalizar_fig16.py
Grava exo3/fig16_curvas.csv (separador ';', vírgula decimal) e
exo3/figuras/fig16_conferencia.png.
"""
import csv
from pathlib import Path

import numpy as np
import scipy.ndimage as nd
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
FIGURA = RAIZ / "patentes" / "US9737374B2_fig16.png"
SAIDA_CSV = RAIZ / "exo3" / "fig16_curvas.csv"
SAIDA_PNG = RAIZ / "exo3" / "figuras" / "fig16_conferencia.png"

X0, X1, T0, T1 = 31, 1294, -80.0, 40.0        # px e graus nas bordas da grade
Y0, Y1, M0, M1 = 639, 1279, 100.0, -100.0     # px e momento nas bordas da grade
INICIO = {"AASM": 18.0, "RM": -2.0, "AWM": -22.0}   # lidos na figura, perto de -75°
FAIXA = (-75.0, 30.0)                         # primeiro e último marcador das curvas


def theta(x):
    return T0 + (x - X0)*(T1 - T0)/(X1 - X0)


def momento(y):
    return M0 + (y - Y0)*(M1 - M0)/(Y1 - Y0)


def px_x(t):
    return X0 + (t - T0)*(X1 - X0)/(T1 - T0)


def px_y(m):
    return Y0 + (m - M0)*(Y1 - Y0)/(M1 - M0)


def trechos(coluna):
    """Trechos pretos de uma coluna; os longos são linhas verticais da figura."""
    idx = np.where(coluna)[0]
    if idx.size == 0:
        return []
    quebra = np.where(np.diff(idx) > 1)[0]
    ini, fim = np.r_[idx[0], idx[quebra + 1]], np.r_[idx[quebra], idx[-1]]
    return [(a + b)/2 for a, b in zip(ini, fim) if b - a < 25]


def rastrear(F):
    prev = {c: px_y(v) for c, v in INICIO.items()}
    pts = {c: [] for c in INICIO}
    margem = 40
    for x in range(int(round(px_x(FAIXA[0] - 0.5))), int(round(px_x(FAIXA[1] + 1.0))) + 1):
        cands = [y + Y0 - margem for y in trechos(F[Y0 - margem:Y1 + margem, x])]
        usados = set()
        for c in sorted(INICIO, key=lambda k: prev[k]):
            melhor = min(((abs(y - prev[c]), y) for y in cands if y not in usados), default=None)
            if melhor and melhor[0] <= 12:
                usados.add(melhor[1])
                prev[c] = melhor[1]
                pts[c].append((x, melhor[1]))
    return pts


def amostrar(pts):
    linhas = []
    for t in np.arange(FAIXA[0], FAIXA[1] + 1.0, 1.0):
        linha = {"theta_grau": float(t)}
        for c in INICIO:
            sel = [y for x, y in pts[c] if abs(theta(x) - t) <= 0.5]
            linha[c] = float(momento(np.median(sel))) if len(sel) >= 3 else None
        if None not in (linha["AASM"], linha["RM"], linha["AWM"]) and \
                abs(linha["AASM"] + linha["AWM"] - linha["RM"]) > 2.0:
            linha["RM"] = None
        linhas.append(linha)
    return linhas


def gravar(linhas):
    def num(v):
        return "" if v is None else f"{v:.2f}".replace(".", ",")
    with open(SAIDA_CSV, "w", newline="", encoding="utf-8") as fh:
        fh.write("# US 9.737.374 B2, Fig. 16: momentos em torno do pivo 584, em funcao do angulo de\n"
                 "# entrada Theta (eixo maior do apoio de braco 505 contra a horizontal). Unidade do\n"
                 "# momento nao informada na patente. AASM: momento de sustentacao do dispositivo;\n"
                 "# AWM: momento do peso do braco; RM = AASM + AWM. Digitalizado por\n"
                 "# exo3/digitalizar_fig16.py; RM em branco onde nao fecha com AASM + AWM.\n")
        w = csv.writer(fh, delimiter=";")
        w.writerow(["theta_grau", "AASM", "RM", "AWM"])
        for l in linhas:
            w.writerow([f"{l['theta_grau']:.0f}"] + [num(l[c]) for c in ("AASM", "RM", "AWM")])


def conferencia(pts):
    im = Image.open(FIGURA).convert("RGB")
    d = ImageDraw.Draw(im)
    cores = {"AASM": (220, 0, 0), "RM": (0, 140, 0), "AWM": (0, 0, 220)}
    for c, ps in pts.items():
        for x, y in ps[::3]:
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=cores[c])
    im.crop((0, 560, 1360, 1350)).save(SAIDA_PNG)


def main():
    B = np.array(Image.open(FIGURA).convert("L")) < 128
    lab, n = nd.label(B, structure=np.ones((3, 3)))
    tam = nd.sum(B, lab, range(1, n + 1))
    F = np.isin(lab, np.where(tam > 40)[0] + 1)       # sem a grade pontilhada
    pts = rastrear(F)
    linhas = amostrar(pts)
    gravar(linhas)
    conferencia(pts)

    t = np.array([l["theta_grau"] for l in linhas])
    a = np.array([l["AASM"] for l in linhas], dtype=float)
    w = np.array([l["AWM"] for l in linhas], dtype=float)
    ok = [l for l in linhas if None not in (l["AASM"], l["RM"], l["AWM"])]
    res = [l["AASM"] + l["AWM"] - l["RM"] for l in ok]
    X = np.c_[np.cos(np.radians(t)), np.sin(np.radians(t))]
    coef, *_ = np.linalg.lstsq(X, w, rcond=None)
    print(f"graus: {len(linhas)}; com as três curvas: {len(ok)}")
    print(f"RM − (AASM + AWM): máx |.| = {np.max(np.abs(res)):.2f}")
    print(f"AWM = {coef[0]:.2f} cos θ + {coef[1]:.2f} sin θ; "
          f"resíduo RMS {np.sqrt(np.mean((w - X @ coef)**2)):.2f}")
    i = int(np.nanargmax(a))
    print(f"AASM: máximo {a[i]:.2f} em θ = {t[i]:.0f}°; {a[0]:.2f} em {t[0]:.0f}°, "
          f"{a[-1]:.2f} em {t[-1]:.0f}°")


if __name__ == "__main__":
    main()
