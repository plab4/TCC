"""
Peso do apoio de braço do exoesqueleto 3 (US 9.737.374 B2), com as propriedades de massa
de cinco corpos do CAD do autor: capa, mola, polia interna, polia externa e came.

Os dados estão no referencial da peça, com z normal ao plano do mecanismo (massas em g,
comprimentos em mm e inércias em g·mm², com Ixy = −∫xy dm). O script:
1. confere a convenção do tensor pelo transporte do centro de massa até a origem;
2. acha os eixos: as duas polias são discos cheios (Ixx = Iyy e Ixy = 0 no centro de
   massa), e o centro de cada uma é o seu eixo. A externa (55 mm) fica no pino 572 (D),
   junto do came, e a interna (30 mm), no pino 632 (P);
3. confere o came com a flange da Figura 15A extrudada: R20 pela área, pela giração, pela
   excentricidade e pela caixa envolvente, e o giro do came em relação à reta de 572 a
   632, contra o da Figura 14D;
4. põe o pivô 584 (O), que o relatório não traz, a C2 do pino 572, com o ângulo entre C2 e
   a reta de 572 a 632 medido na Figura 14D (a pose do CAD). O came aparece sem
   espelhamento no desenho e no CAD, então o referencial da peça é o do desenho girado, e
   O fica do lado da mola, como no desenho;
5. dá o centro de massa de cada corpo em relação a O e ao eixo maior do apoio de braço
   (26,741° além de C2) e o momento do peso em torno de O,
       M(Θ) = −g Σ m d cos(Θ + a) / 10⁶     (N·m, positivo quando ergue o braço),
   com a positivo acima do eixo e o centro do came girando junto com as polias.

Rodar (na raiz do repositório):
    python exo3/massa_apoio.py
"""
import numpy as np
from PIL import Image
from scipy.optimize import least_squares

import poses_fig14 as pf

G = 9.81                                  # m/s²
C2, DEFASAGEM = 90.587, 26.741            # mm e graus, CAD do autor
GIRO_CAME_14D = 254.0                     # giro do referencial da 15B na Figura 14D (poses_fig14.py)
# material, massa (g), volume (mm³), caixa (mm), centro de massa (mm) e (Ixx, Iyy, Izz, Ixy)
# no centro de massa e na origem (g·mm²), como no relatório do CAD
CORPOS = {
    "capa": ("Náilon 6/6", 563.556, 4.987e5, (283.624, 136.626, 30.0), (8.38, 25.054),
             (5.498e5, 3.306e6, 3.771e6, -1.032e6), (9.036e5, 3.346e6, 4.165e6, -1.150e6)),
    "mola": ("Aço", 104.593, 13323.966, (207.351, 96.908, 18.0), (-11.578, 6.173),
             (63262.285, 3.677e5, 4.249e5, -1.438e5), (67247.319, 3.818e5, 4.430e5, -1.364e5)),
    "polia interna": ("Náilon 6/6", 15.975, 14137.167, (30.0, 30.0, 20.0), (129.754, 67.131),
                      (1431.093, 1431.094, 1797.187, 0.0),
                      (73423.961, 2.704e5, 3.427e5, -1.392e5)),
    "polia externa": ("Aço", 373.005, 47516.589, (55.0, 55.0, 20.0), (-32.681, 47.229),
                      (82954.794, 82954.812, 1.410e5, 0.0), (9.150e5, 4.813e5, 1.371e6, 5.757e5)),
    "came": ("Aço", 405.33, 51634.402, (44.585, 49.897, 30.0), (-39.51, 57.522),
             (98400.164, 79197.999, 1.168e5, -10821.072), (1.440e6, 7.119e5, 2.091e6, 9.104e5)),
}


def ang(v):
    return float(np.degrees(np.arctan2(v[1], v[0])))


def u(a):
    return np.array([np.cos(np.radians(a)), np.sin(np.radians(a))])


def meia_volta(a):
    return (a + 180.0) % 360.0 - 180.0


def confere_tensor():
    """Maior diferença relativa entre o tensor na origem e o transporte do do centro."""
    pior = 0.0
    for _, m, _, _, (x, y), ic, io in CORPOS.values():
        prev = np.array(ic) + m*np.array([y*y, x*x, x*x + y*y, -x*y])
        pior = max(pior, float(np.max(np.abs(prev - io)/np.abs(io).clip(1.0))))
    return pior


def disco(nome):
    """Desvio do volume de um cilindro cheio com o diâmetro e a altura da caixa, e Ixy."""
    _, m, vol, (a, b, h), _, ic, _ = CORPOS[nome]
    return vol/(np.pi*(a/2)**2*h) - 1, ic[3], ic[0]/ic[1] - 1


def secao(P):
    """Área, centróide e momentos de segunda ordem por área, no centróide, de um polígono."""
    x, y = P[:, 0], P[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    cr = x*y1 - x1*y
    A = cr.sum()/2
    c = np.array([((x + x1)*cr).sum(), ((y + y1)*cr).sum()])/(6*A)
    ixx = ((x*x + x*x1 + x1*x1)*cr).sum()/(12*A) - c[0]**2
    iyy = ((y*y + y*y1 + y1*y1)*cr).sum()/(12*A) - c[1]**2
    ixy = ((x*y1 + 2*x*y + 2*x1*y1 + x1*y)*cr).sum()/(24*A) - c[0]*c[1]
    return abs(A), c, np.array([[ixx, ixy], [ixy, iyy]])


def came_cad():
    """Área da seção, excentricidade e momentos por massa, no centro, do came do CAD."""
    _, m, vol, caixa, cg, (ixx, iyy, izz, ixy), _ = CORPOS["came"]
    e = np.array(cg) - np.array(CORPOS["polia externa"][4])
    M = np.array([[(iyy + izz - ixx)/2, -ixy], [-ixy, (ixx + izz - iyy)/2]])/m
    espessura = np.sqrt(6*(ixx + iyy - izz)/m)         # ∫z² dm = m h²/12
    return vol/caixa[2], e, M, espessura


def compara_came():
    T = pf.contorno_15a()                              # flange da 15A, em R20, ref. da 15B
    A, c, M = secao(T)
    A_cad, e, M_cad, h = came_cad()

    def caixa(p):
        R20, psi = p
        Q = (T @ np.array([[np.cos(np.radians(psi)), np.sin(np.radians(psi))],
                           [-np.sin(np.radians(psi)), np.cos(np.radians(psi))]]))*R20
        return np.ptp(Q, axis=0) - CORPOS["came"][3][:2]
    R20_cx, psi_cx = least_squares(caixa, [32.0, ang(e) - ang(c)]).x
    eixo = lambda S: 0.5*np.degrees(np.arctan2(2*S[0, 1], S[0, 0] - S[1, 1]))
    return {"R20_area": float(np.sqrt(A_cad/A)), "R20_giracao": float(np.sqrt(np.trace(M_cad)/np.trace(M))),
            "R20_excentricidade": float(np.hypot(*e)/np.hypot(*c)), "R20_caixa": float(R20_cx),
            "giro_caixa": float(meia_volta(psi_cx)), "giro_centroide": meia_volta(ang(e) - ang(c)),
            "giro_eixos": float(meia_volta(eixo(M_cad) - eixo(M))), "espessura": float(h),
            "excentricidade_mm": float(np.hypot(*e))}


def pontos_14d():
    """O, D e P na Figura 14D, em px, com y para cima, e a escala do desenho."""
    B = np.array(Image.open(pf.FIGURA).convert("L")) < 128
    a584, a572, a632 = pf.APROX["14D"]
    O, D, P = pf.furo_branco(B, a584), pf.anel(B, a572, 4, 12), pf.anel(B, a632, 4, 12)
    sobe = np.array([1.0, -1.0])
    return O*sobe, D*sobe, P*sobe, float(np.hypot(*(D - O))/C2)


def geometria():
    """Pivô, eixo maior e centros de massa no referencial da peça, contra a Figura 14D."""
    O14, D14, P14, esc = pontos_14d()
    D = np.array(CORPOS["polia externa"][4])
    P = np.array(CORPOS["polia interna"][4])
    chassi, chassi14 = ang(P - D), ang(P14 - D14)
    c2_chassi = meia_volta(ang(D14 - O14) - chassi14)  # de C2 à reta de 572 a 632 (21,8°)
    c2 = chassi + c2_chassi                           # direção de O para D, na peça
    O = D - C2*u(c2)
    eixo = c2 - DEFASAGEM                             # eixo maior: 26,741° além de C2
    def lado(p):                                      # distância com sinal à reta de 572 a 632
        w = u(chassi)
        return float(w[0]*(p - D)[1] - w[1]*(p - D)[0])
    corpos = {}
    for nome, (mat, m, _, _, cg, _, _) in CORPOS.items():
        r = np.array(cg) - O
        corpos[nome] = {"material": mat, "massa_g": m, "cg": list(cg), "d": float(np.hypot(*r)),
                        "a": meia_volta(ang(r) - eixo)}
    mt, cg, d, a = conjunto(corpos, O, eixo)
    came = compara_came()
    return {"O": O.tolist(), "D": D.tolist(), "P": P.tolist(), "L": float(np.hypot(*(P - D))),
            "L_14D": float(np.hypot(*(P14 - D14))/esc), "chassi_grau": chassi,
            "c2_chassi_14D": c2_chassi, "c2_grau": c2, "eixo_grau": eixo,
            "giro_peca_grau": meia_volta(chassi - chassi14),
            "lado_mola": lado(np.array(CORPOS["mola"][4])), "lado_O": lado(O),
            "corpos": corpos, "massa_g": mt, "cg": cg, "d": d, "a": a, "came": came,
            "nailon": variante_nailon(corpos, O, eixo),
            "came_chassi_peca": meia_volta(came["giro_caixa"] - chassi),
            "came_chassi_14D": meia_volta(GIRO_CAME_14D - chassi14)}


def conjunto(corpos, O, eixo):
    """Massa, centro de massa, distância a O e ângulo com o eixo maior do conjunto."""
    mt = sum(x["massa_g"] for x in corpos.values())
    cg = sum(x["massa_g"]*np.array(x["cg"]) for x in corpos.values())/mt
    r = cg - O
    return float(mt), cg.tolist(), float(np.hypot(*r)), meia_volta(ang(r) - eixo)


def variante_nailon(corpos, O, eixo):
    """O conjunto com a polia externa e o came em náilon 6/6, a aparência deles no CAD."""
    dens = CORPOS["capa"][1]/CORPOS["capa"][2]
    outro = {k: dict(v) for k, v in corpos.items()}
    for nome in ("polia externa", "came"):
        outro[nome]["massa_g"] = CORPOS[nome][2]*dens
    mt, cg, d, a = conjunto(outro, O, eixo)
    return {"densidade_g_mm3": dens, "massa_g": mt, "d": d, "a": a, "momento_max_N_m": G*mt*d/1e6}


def momento(geo, theta, dtp=0.0):
    """Momento do peso do apoio de braço em torno de O (N·m), para Θ em graus.

    dtp é o giro das polias em relação ao chassi desde a pose do CAD, em graus; ele só
    move o centro do came, que é excêntrico (as polias são discos centrados nos pinos)."""
    theta = np.atleast_1d(np.asarray(theta, float))
    dtp = np.broadcast_to(np.radians(dtp), theta.shape)
    O, D, eixo = np.array(geo["O"]), np.array(geo["D"]), geo["eixo_grau"]
    soma = np.zeros_like(theta)
    for nome, c in geo["corpos"].items():
        r = np.array(c["cg"]) - O
        if nome == "came":
            e = np.array(c["cg"]) - D
            ex = np.cos(dtp)*e[0] - np.sin(dtp)*e[1]
            ey = np.sin(dtp)*e[0] + np.cos(dtp)*e[1]
            rx, ry = (D - O)[0] + ex, (D - O)[1] + ey
        else:
            rx, ry = np.full_like(theta, r[0]), np.full_like(theta, r[1])
        # direção do vetor no referencial do mundo: ang(r) − eixo + Θ
        gira = np.radians(theta - eixo)
        soma += c["massa_g"]*(np.cos(gira)*rx - np.sin(gira)*ry)
    return -G*soma/1e6


def main():
    print(f"Tensor: Ixy = −∫xy dm; transporte do centro à origem confere com {confere_tensor():.1e} "
          "de diferença relativa")
    for nome in ("polia externa", "polia interna"):
        dv, ixy, dI = disco(nome)
        print(f"{nome}: volume {dv:+.1e} do cilindro cheio da caixa; Ixy = {ixy:g}; Ixx/Iyy − 1 = {dI:.1e}")
    geo = geometria()
    c = geo["came"]
    print(f"Came: espessura {c['espessura']:.2f} mm; R20 pela área {c['R20_area']:.2f} mm, pela giração "
          f"{c['R20_giracao']:.2f} mm, pela excentricidade ({c['excentricidade_mm']:.2f} mm) "
          f"{c['R20_excentricidade']:.2f} mm e pela caixa {c['R20_caixa']:.2f} mm")
    print(f"   giro do referencial da 15B na peça: {c['giro_caixa']:.1f}° pela caixa, {c['giro_centroide']:.1f}° "
          f"pelo centróide, {c['giro_eixos']:.1f}° pelos eixos principais")
    print(f"   em relação à reta de 572 a 632: {geo['came_chassi_peca']:.1f}° na peça, "
          f"{geo['came_chassi_14D']:.1f}° na Figura 14D")
    print(f"572 a 632: {geo['L']:.2f} mm na peça, {geo['L_14D']:.2f} mm na Figura 14D; a peça é o desenho "
          f"girado de {geo['giro_peca_grau']:.2f}°")
    print(f"C2 a {geo['c2_chassi_14D']:.2f}° da reta de 572 a 632; O = ({geo['O'][0]:.2f}; {geo['O'][1]:.2f}) mm; "
          f"eixo maior a {geo['eixo_grau']:.2f}° na peça; lado da mola {geo['lado_mola']:+.1f}, de O "
          f"{geo['lado_O']:+.1f} mm")
    print("corpo           massa (g)   x (mm)   y (mm)   d (mm)   a (graus)")
    for nome, x in geo["corpos"].items():
        print(f"{nome:15s} {x['massa_g']:9.3f} {x['cg'][0]:8.2f} {x['cg'][1]:8.2f} {x['d']:8.2f} {x['a']:9.2f}")
    print(f"{'conjunto':15s} {geo['massa_g']:9.3f} {geo['cg'][0]:8.2f} {geo['cg'][1]:8.2f} {geo['d']:8.2f} "
          f"{geo['a']:9.2f}")
    mmax = G*geo["massa_g"]*geo["d"]/1e6
    print(f"Momento máximo do peso: {mmax:.3f} N·m, em Θ = {-geo['a']:.1f}°; com o eixo na horizontal, "
          f"{momento(geo, 0.0)[0]:.3f} N·m; na pose do CAD (Θ = −88,465°), {momento(geo, -88.465)[0]:.3f} N·m")
    n = geo["nailon"]
    print(f"Com a polia externa e o came em náilon ({n['densidade_g_mm3']*1000:.3f} g/cm³): {n['massa_g']:.1f} g, "
          f"centro a {n['d']:.2f} mm e {n['a']:.2f}°, momento máximo {n['momento_max_N_m']:.3f} N·m")


if __name__ == "__main__":
    main()
