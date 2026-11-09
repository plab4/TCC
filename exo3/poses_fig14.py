"""
Poses das Figuras 14C (braço erguido) e 14D (braço baixado) da US 9.737.374 B2 contra o
circuito do CAD do autor.

Na imagem da folha 21 (patentes/US9737374B2_fig14cd.png), mede:
- os centros do pivô 584 (disco cheio), do pino 572 e do pino 632 (anéis, por ajuste
  de círculo);
- q, o ângulo de C2 (de 584 a 572) com a horizontal, positivo para baixo, como no CAD;
- o ângulo da reta de 572 a 632, ao longo do chassi, e a diferença para C2;
- a escala do desenho, pela razão entre |584 572| e C2 = 90,587 mm;
- onde o CAD põe o ponto de ancoragem A (562), para comparar com o desenhado;
- a escala e o giro do came 570, ajustando a ele o contorno externo da Figura 15A, levado
  ao referencial da 15B (a 15A é a 15B espelhada), por distância aos traços pretos;
- o giro do came entre as duas figuras, contra o que a cinemática do cabo 560 prevê.

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
FIGURA15 = RAIZ / "patentes" / "US9737374B2_fig15.png"
R20_15B = 482.667                         # px da 15B (extrair_came570.py)
R_PRIMARIA = 26.443                       # mm, CAD do autor
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


def furo_branco(B, aprox, m=12):
    """Centro do furo branco no meio do anel preto do pivô 584."""
    cx, cy = aprox
    lab, _ = nd.label(~B[cy - m:cy + m, cx - m:cx + m])
    yy, xx = np.nonzero(lab == lab[m, m])
    return np.array([xx.mean() + cx - m, yy.mean() + cy - m])


def contorno_15a():
    """Contorno externo do came na Figura 15A, em R20 e no referencial da 15B."""
    import contourpy
    B = np.array(Image.open(FIGURA15).convert("L")) < 128
    x0, y0 = 150, 100
    reg = nd.binary_fill_holes(B[y0:1180, x0:960])
    lab, n = nd.label(reg)
    reg = nd.binary_opening(lab == np.argmax(nd.sum(reg, lab, range(1, n + 1))) + 1,
                            structure=np.ones((7, 7)))
    c = max(contourpy.contour_generator(z=reg.astype(float)).lines(0.5), key=len) + [x0, y0]
    o654, o573 = anel(B, (404, 850), 50, 75, m=80), anel(B, (350, 664), 12, 25)
    p654, p573 = anel(B, (2098, 1257), 50, 70, m=80), anel(B, (2153, 1085), 40, 55, m=70)
    da, db = o573 - o654, p573 - p654
    P = np.c_[-(c[:, 0] - o654[0]), -(c[:, 1] - o654[1])]          # espelha e põe y para cima
    eps = np.arctan2(-db[1], db[0]) - np.arctan2(-da[1], -da[0])
    Rm = np.array([[np.cos(eps), -np.sin(eps)], [np.sin(eps), np.cos(eps)]])
    return (P @ Rm.T)/(np.hypot(*da)/np.hypot(*db)*R20_15B)


def ajusta_came(B, centro, T):
    """Escala (px por R20) e giro (graus, anti-horário) do came desenhado em torno de centro."""
    cx, cy = centro
    m = 110
    x0, y0 = int(cx) - m, int(cy) - m
    D = nd.distance_transform_edt(~B[y0:y0 + 2*m, x0:x0 + 2*m])
    T = T[::6]

    def custo(psi, k):
        c, s = np.cos(np.radians(psi)), np.sin(np.radians(psi))
        Q = T @ np.array([[c, s], [-s, c]])
        xs, ys = cx + k*Q[:, 0] - x0, cy - k*Q[:, 1] - y0
        return np.minimum(nd.map_coordinates(D, [ys, xs], order=1, cval=50), 6).mean()

    melhor = min((custo(psi, k), psi, k) for psi in np.arange(0, 360, 1.0) for k in np.arange(35, 75, 0.5))
    _, p0, k0 = melhor
    melhor = min((custo(psi, k), psi, k) for psi in np.arange(p0 - 1.5, p0 + 1.51, 0.1)
                 for k in np.arange(k0 - 1, k0 + 1.01, 0.05))
    return melhor


def furos_came(B, centro, giro_came, janela=(95.0, 245.0)):
    """Furos pequenos em torno do pino 572, no lado do came oposto ao bolsão do 573.

    giro_came é o giro do referencial da Figura 15B na figura (graus), e janela, a faixa de
    ângulos desse referencial em que os furos são procurados (exclui o 573, a 72°).
    Raio: média das distâncias ao centro dos furos isolados (componentes pretos de 25 a 45 px,
    com caixa menor que 8 px). Ângulos: centros dos trechos em que a fração de pixels pretos
    num disco de 3,2 px, ao longo do círculo desse raio, passa de 0,8; assim entram também os
    furos tocados por linhas de chamada. Devolve os ângulos na figura (graus, anti-horários,
    y para cima) e o raio (px)."""
    cx, cy = centro
    m = 40
    x0, y0 = int(cx) - m, int(cy) - m
    lab, n = nd.label(B[y0:y0 + 2*m, x0:x0 + 2*m])
    dist = []
    for k in range(1, n + 1):
        yy, xx = np.nonzero(lab == k)
        if not (25 <= xx.size <= 45 and np.ptp(xx) < 8 and np.ptp(yy) < 8):
            continue
        gx, gy = xx.mean() + x0, yy.mean() + y0
        a = np.degrees(np.arctan2(-(gy - cy), gx - cx))
        if janela[0] <= (a - giro_came) % 360 <= janela[1]:
            dist.append(np.hypot(gx - cx, gy - cy))
    raio = float(np.mean(dist))
    yy, xx = np.mgrid[-4:5, -4:5]
    disco = (xx**2 + yy**2) <= 3.2**2
    angs = np.arange(janela[0], janela[1] + 1e-9, 0.5) + giro_came
    f = []
    for a in angs:
        xi = int(round(cx + raio*np.cos(np.radians(a))))
        yi = int(round(cy - raio*np.sin(np.radians(a))))
        f.append(B[yi - 4:yi + 5, xi - 4:xi + 5][disco].mean())
    acima = np.r_[False, np.array(f) >= 0.8, False]
    ini = np.flatnonzero(~acima[:-1] & acima[1:])
    fim = np.flatnonzero(acima[:-1] & ~acima[1:])
    centros = [float(np.mean(angs[a:b])) for a, b in zip(ini, fim)]
    return [((c + 180.0) % 360.0) - 180.0 for c in centros], raio


def ang(p, q):
    v = q - p
    return np.degrees(np.arctan2(-v[1], v[0]))          # y da imagem para baixo


def main():
    B = np.array(Image.open(FIGURA).convert("L")) < 128
    T = contorno_15a()
    giro = {}
    for nome, (a584, a572, a632) in APROX.items():
        O = furo_branco(B, a584)
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
        print(f"   escala {esc:.4f} px/mm; A pelo CAD em ({A_cad[0]:.1f}, {A_cad[1]:.1f}), 562 desenhado "
              f"em ({A_fig[0]:.1f}, {A_fig[1]:.1f}): {np.hypot(*(A_fig - A_cad))/esc:.1f} mm de diferença")
        dist, psi, k = ajusta_came(B, D, T)
        print(f"   came: {k:.2f} px por R20, isto é, R20 = {k/esc:.2f} mm; o referencial da 15B está girado "
              f"de {psi:.1f}° (sem espelhar); distância média ao desenho {dist:.2f} px; reta 572-632 a "
              f"{eixo - q:.2f}° de C2")
        # cinemática do cabo 560 pela geometria desenhada: φ e S a partir de A e D medidos
        d = (A_fig - D)*[1, -1]/esc
        S = np.sqrt(d @ d - R_PRIMARIA**2)
        fi = np.degrees(np.arctan2(d[1], d[0]) + np.arctan2(S, R_PRIMARIA))
        fu, rf = furos_came(B, D, psi)
        print(f"   furos em torno do 572: {len(fu)}, a {rf/esc:.2f} mm do centro; na figura em "
              + ", ".join(f"{x:.1f}°" for x in fu) + "; no referencial da 15B em "
              + ", ".join(f"{(x - psi) % 360:.1f}°" for x in fu)
              + f"; passo médio {(max(fu) - min(fu))/(len(fu) - 1):.2f}°")
        giro[nome] = (psi, fi, S)
    (pc, fc, sc), (pd, fd, sd) = giro["14C"], giro["14D"]
    previsto = (((fd - fc + 180) % 360) - 180) - np.degrees((sd - sc)/R_PRIMARIA)
    print(f"Giro absoluto do came da 14C para a 14D: medido {(pd - pc) % 360:.1f}°; previsto pelo cabo 560 "
          f"com A e D desenhados, {previsto % 360:.1f}° ({previsto:.1f}°)")


if __name__ == "__main__":
    main()
