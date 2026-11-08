"""
Poses das Figuras 14C (braço erguido) e 14D (braço baixado) da US 9.737.374 B2 contra o
circuito do CAD do autor.

Na imagem da folha 21 (patentes/US9737374B2_fig14cd.png), mede:
- os centros do pivô 584 (disco cheio), do pino 572 e do pino 632 (anéis, por ajuste
  de círculo);
- q, o ângulo de C2 (de 584 a 572) com a horizontal, positivo para baixo, como no CAD;
- o ângulo da reta de 572 a 632, ao longo do chassi, e a diferença para C2;
- a escala do desenho, pela razão entre |584 572| e C2 = 90,587 mm;
- onde o CAD põe o ponto de ancoragem A (562), para comparar com o desenhado.

O referencial do CAD é o da figura girado de 180°, então A − O na figura vale C1 u(γ).
O ângulo do apoio de braço da Figura 16 sai de Θ = −(q + 26,741°), com a defasagem
entre C2 e o eixo maior medida no CAD.

Rodar (na raiz do repositório):
    python exo3/poses_fig14.py
"""
from pathlib import Path

import numpy as np
import scipy.ndimage as nd
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
FIGURA = RAIZ / "patentes" / "US9737374B2_fig14cd.png"
C1, C2, GAMA = 70.711, 90.587, 61.26          # mm e graus, CAD do autor
DEFASAGEM = 26.741                            # graus entre C2 e o eixo maior, CAD do autor
APROX = {"14C": ((461, 762), (582, 671), (850, 601)),
         "14D": ((1711, 964), (1785, 1098), (1820, 1374))}   # 584, 572 e 632, a olho


def anel(B, aprox, rmin, rmax, m=25):
    cx, cy = aprox
    ys, xs = np.nonzero(B[cy - m:cy + m, cx - m:cx + m])
    x, y = (xs + cx - m).astype(float), (ys + cy - m).astype(float)
    for _ in range(6):
        d = np.hypot(x - cx, y - cy)
        k = (d > rmin) & (d < rmax)
        A = np.c_[2*x[k], 2*y[k], np.ones(k.sum())]
        s, *_ = np.linalg.lstsq(A, x[k]**2 + y[k]**2, rcond=None)
        cx, cy, r = s[0], s[1], np.sqrt(s[2] + s[0]**2 + s[1]**2)
        rmin, rmax = r - 1.5, r + 1.5
    return np.array([cx, cy])


def disco(B, aprox, m=12):
    """Centro do disco cheio mais próximo de aprox, depois de tirar as linhas finas."""
    cx, cy = int(aprox[0]), int(aprox[1])
    sub = nd.binary_opening(B[cy - m:cy + m, cx - m:cx + m], structure=np.ones((3, 3)))
    lab, n = nd.label(sub)
    cs = nd.center_of_mass(sub, lab, range(1, n + 1))
    c = min(cs, key=lambda c: np.hypot(c[1] + cx - m - aprox[0], c[0] + cy - m - aprox[1]))
    return np.array([c[1] + cx - m, c[0] + cy - m])


def ang(p, q):
    v = q - p
    return np.degrees(np.arctan2(-v[1], v[0]))          # y da imagem para baixo


def main():
    B = np.array(Image.open(FIGURA).convert("L")) < 128
    for nome, (a584, a572, a632) in APROX.items():
        O = disco(B, a584, m=8)
        D = anel(B, a572, 4, 12)
        P = anel(B, a632, 4, 12)
        q = -ang(O, D)
        eixo = -ang(D, P)
        esc = np.hypot(*(D - O))/C2
        v = C1*np.array([np.cos(np.radians(GAMA)), np.sin(np.radians(GAMA))])
        A_cad = O + esc*np.array([v[0], -v[1]])
        A_fig = disco(B, A_cad)
        print(f"Fig. {nome}: q = {q:+.2f}°; reta 572-632 a {eixo:+.2f}° da horizontal (positivo para "
              f"baixo), {eixo - q:.2f}° além de C2; Θ = −(q + {DEFASAGEM}°) = {-(q + DEFASAGEM):+.2f}°")
        print(f"   escala {esc:.3f} px/mm; A pelo CAD em ({A_cad[0]:.1f}, {A_cad[1]:.1f}), 562 desenhado "
              f"em ({A_fig[0]:.1f}, {A_fig[1]:.1f}): {np.hypot(*(A_fig - A_cad))/esc:.1f} mm de diferença")


if __name__ == "__main__":
    main()
