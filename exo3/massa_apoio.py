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
   com a positivo acima do eixo e o centro do came girando junto com as polias;
6. confere o referencial de forma independente: o came espelhado não fecha (centróide
   e eixos principais discordam), e o eixo da mola do CAD, levado ao desenho, cai sobre
   a mola 636 da Figura 14D, que não entrou em nenhuma das etapas anteriores;
7. mede a sensibilidade à posição do pivô: com o q do CAD no lugar do ângulo da 14D, ou
   com o eixo x da peça tomado como eixo maior.

Rodar (na raiz do repositório):
    python exo3/massa_apoio.py
"""
import numpy as np
from PIL import Image
from scipy.optimize import least_squares

import poses_fig14 as pf

G = 9.80665                               # m/s², como em torque_model_ottobock.py
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
    "polia externa": ("Náilon 6/6", 53.694, 47516.589, (55.0, 55.0, 20.0), (-32.681, 47.229),
                      (11941.263, 11941.266, 20302.946, 0.0),
                      (1.317e5, 69288.57, 1.974e5, 82876.103)),
    "came": ("Náilon 6/6", 58.347, 51634.402, (44.585, 49.897, 30.0), (-39.51, 57.522),
             (14164.61, 11400.476, 16813.055, -1557.683), (2.072e5, 1.025e5, 3.010e5, 1.310e5)),
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
    eixo = eixo_principal
    return {"R20_area": float(np.sqrt(A_cad/A)), "R20_giracao": float(np.sqrt(np.trace(M_cad)/np.trace(M))),
            "R20_excentricidade": float(np.hypot(*e)/np.hypot(*c)), "R20_caixa": float(R20_cx),
            "giro_caixa": float(meia_volta(psi_cx)), "giro_centroide": meia_volta(ang(e) - ang(c)),
            "giro_eixos": float(meia_volta(eixo(M_cad) - eixo(M))), "espessura": float(h),
            "excentricidade_mm": float(np.hypot(*e))}


def eixo_principal(S):
    """Direção do maior momento de segunda ordem, em graus (período de 180°)."""
    return 0.5*np.degrees(np.arctan2(2*S[0, 1], S[0, 0] - S[1, 1]))


def espelhamento():
    """Diferença entre o giro do came pelo centróide e pelos eixos principais, com a flange
    como está e espelhada: só a hipótese certa dá giros parecidos."""
    T = pf.contorno_15a()
    _, e, M_cad, _ = came_cad()
    saida = {}
    for nome, TT in (("sem_espelhar", T), ("espelhado", T*[1.0, -1.0])):
        _, c, M = secao(TT)
        pc = meia_volta(ang(e) - ang(c))
        pe = meia_volta(eixo_principal(M_cad) - eixo_principal(M))
        saida[nome] = min(abs(meia_volta(pc - pe)), abs(meia_volta(pc - pe - 180.0)))
    return saida


def mola_no_desenho(geo, B=None):
    """Eixo da mola do CAD levado à Figura 14D, contra os traços da mola 636 desenhada:
    diferença de direção (graus) e afastamento do centro dos traços (mm)."""
    O14, D14, P14, esc = pontos_14d()
    D = np.array(geo["D"])
    g = -np.radians(geo["giro_peca_grau"])
    Rm = np.array([[np.cos(g), -np.sin(g)], [np.sin(g), np.cos(g)]])

    def px(p):                                         # mm na peça -> px, y para baixo
        q = D14 + esc*(Rm @ (np.asarray(p) - D))
        return np.array([q[0], -q[1]])
    _, m, _, _, cg, (ixx, iyy, izz, ixy), _ = CORPOS["mola"]
    eixo_m = eixo_principal(np.array([[(iyy + izz - ixx)/2, -ixy], [-ixy, (ixx + izz - iyy)/2]]))
    p0, p1 = px(np.array(cg) - 75*u(eixo_m)), px(np.array(cg) + 75*u(eixo_m))
    if B is None:
        B = np.array(Image.open(pf.FIGURA).convert("L")) < 128
    ys, xs = np.nonzero(B)
    v = (p1 - p0)/np.hypot(*(p1 - p0))
    n = np.array([-v[1], v[0]])
    rel = np.c_[xs - p0[0], ys - p0[1]]
    t, s = rel @ v, rel @ n
    sel = (t > 0) & (t < np.hypot(*(p1 - p0))) & (np.abs(s) < 22)   # faixa de ±13 mm
    P = np.c_[xs[sel], ys[sel]].astype(float)
    c = P.mean(axis=0)
    _, _, Vt = np.linalg.svd(P - c, full_matrices=False)
    dif = meia_volta(np.degrees(np.arctan2(-Vt[0, 1], Vt[0, 0]) - np.arctan2(-v[1], v[0])))
    dif = min(abs(dif), abs(meia_volta(dif - 180.0)))
    return {"eixo_peca_grau": float(eixo_m), "dif_direcao_grau": float(dif),
            "afastamento_mm": float(abs((c - p0) @ n)/esc), "pixels": int(sel.sum())}


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
            "came_chassi_peca": meia_volta(came["giro_caixa"] - chassi),
            "came_chassi_14D": meia_volta(GIRO_CAME_14D - chassi14),
            "espelhamento": espelhamento()}


def conjunto(corpos, O, eixo):
    """Massa, centro de massa, distância a O e ângulo com o eixo maior do conjunto."""
    mt = sum(x["massa_g"] for x in corpos.values())
    cg = sum(x["massa_g"]*np.array(x["cg"]) for x in corpos.values())/mt
    r = cg - O
    return float(mt), cg.tolist(), float(np.hypot(*r)), meia_volta(ang(r) - eixo)


def sensibilidade_pivo(geo):
    """O e o conjunto com outras direções de C2 na peça: a do q do CAD com a peça girada de
    90° em relação ao desenho, e a do eixo x da peça tomado como eixo maior."""
    D = np.array(geo["D"])
    saida = {}
    for nome, c2 in (("q_do_CAD", -61.724 + 90.0), ("eixo_x", DEFASAGEM)):
        O = D - C2*u(c2)
        mt, cg, d, a = conjunto(geo["corpos"], O, c2 - DEFASAGEM)
        saida[nome] = {"c2_grau": c2, "desvio_O_mm": float(np.hypot(*(O - np.array(geo["O"])))),
                       "d": d, "a": a, "momento_max_N_m": G*mt*d/1e6}
    return saida


def inercia_o(geo):
    """Momento de inércia de cada corpo em torno do eixo de 584 (kg·m²), pelo teorema dos
    eixos paralelos com o Izz do centro de massa do CAD, e o do apoio inteiro."""
    saida = {}
    for nome, c in geo["corpos"].items():
        izz_cg = CORPOS[nome][5][2]
        saida[nome] = {"izz_cg": izz_cg*1e-9, "izz_o": (izz_cg + c["massa_g"]*c["d"]**2)*1e-9}
    return saida, sum(x["izz_o"] for x in saida.values())


def momento(geo, theta, dtp=0.0, corpos=None):
    """Momento do peso do apoio de braço em torno de O (N·m), para Θ em graus.

    dtp é o giro das polias em relação ao chassi desde a pose do CAD, em graus; ele só
    move o centro do came, que é excêntrico (as polias são discos centrados nos pinos).
    corpos substitui as massas (por exemplo, as da variante em náilon)."""
    theta = np.atleast_1d(np.asarray(theta, float))
    dtp = np.broadcast_to(np.radians(dtp), theta.shape)
    O, D, eixo = np.array(geo["O"]), np.array(geo["D"]), geo["eixo_grau"]
    soma = np.zeros_like(theta)
    for nome, c in (corpos or geo["corpos"]).items():
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
    esp = geo["espelhamento"]
    print(f"Espelhamento: giro do came pelo centróide e pelos eixos principais difere {esp['sem_espelhar']:.1f}° "
          f"sem espelhar e {esp['espelhado']:.1f}° espelhado")
    mo = mola_no_desenho(geo)
    print(f"Mola do CAD na Figura 14D: eixo a {mo['eixo_peca_grau']:.2f}° na peça; difere {mo['dif_direcao_grau']:.1f}° "
          f"dos traços da mola 636 e passa a {mo['afastamento_mm']:.1f} mm do centro deles ({mo['pixels']} px)")
    for nome, x in sensibilidade_pivo(geo).items():
        print(f"Pivô com {nome}: C2 a {x['c2_grau']:.2f}°, O desloca {x['desvio_O_mm']:.2f} mm, d = {x['d']:.2f} mm, "
              f"a = {x['a']:.2f}°, momento máximo {x['momento_max_N_m']:.3f} N·m")


if __name__ == "__main__":
    main()
