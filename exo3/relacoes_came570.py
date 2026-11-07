"""
Relações entre o came 570, o cabo da mola 634 e a polia de reversão 630 (exoesqueleto 3).

Três raios entram no par de polias:
- R: raio da polia primária 564, que é circular e fixo;
- ρ: raio do came no ponto em que o cabo 634 deixa o canal (os R20 a R25 da patente);
- r: raio efetivo, a distância do pino 572 à linha do cabo 634.

O equilíbrio do par de polias dá F_a R = F_s r. A patente trata o cabo como uma força
tangencial aplicada no raio, o que só vale onde ele sai perpendicular ao raio (r = ρ, na
zona Z10). Em geral, com β o ângulo entre o raio do ponto de saída e o cabo,

    r = ρ sin β,        ρ² = r² + (dr/dφ)²,

em que r(φ) é a função suporte da envoltória convexa do canal (o cabo tracionado passa
reto sobre concavidades) e φ é a direção normal ao cabo, no referencial do came.

Ângulo do cabo. O cabo sai do came tangente a ele e chega tangente à polia 630. No
referencial do chassi, com o pino 572 na origem, o centro 632 à distância L, na direção
λ, e a polia de raio r630, a normal ao cabo, φc = λ − 90° + δ, satisfaz

    r(φc − θp) − L cos(φc − λ) = r630   →   δ = asin((r − r630)/L),

em que θp é a rotação do came em relação ao chassi e δ é o ângulo entre o cabo e a linha que
vai de 572 a 632. O ângulo do cabo depende de θp por meio de r, e r depende do ângulo do cabo,
porque ele decide o ponto de saída. A equação é implícita e se resolve por ponto fixo; a
iteração contrai porque |dr/dφ| ≤ ρ é bem menor que L.

Alongamento da mola. O comprimento do cabo entre o ponto em que ele sai do bolsão e um
ponto fixo na polia 630 varia à taxa dℓ/dθp = −r (trabalho virtual: o momento do cabo
sobre o came é F_s r). A mola acompanha ℓ, então x(θp) = x(θp0) − ∫ r dθp. O script
confere essa taxa contra o comprimento calculado pela geometria: arco enrolado no came,
vão livre até a 630 e arco enrolado nela.

Convenção: o cabo se enrola no came no sentido anti-horário, a partir do chifre de cima
do bolsão (zona Z10, depois Z11 e Z12), e θp é anti-horário; θp crescente desenrola o
cabo. No mecanismo real, o lado e os sentidos saem do CAD.

L, λ e r630 vêm do CAD. Sem eles, o script só confere as contas numa geometria de teste,
que não é dado do mecanismo.

Rodar (na raiz do repositório):
    python exo3/relacoes_came570.py
"""
import csv
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull

RAIZ = Path(__file__).resolve().parent.parent
CONTORNO = RAIZ / "exo3" / "came570_contorno.csv"


def _num(s):
    return float(s.replace(",", "."))


def casco_came():
    """Vértices da envoltória convexa do canal, em R20 e em ordem anti-horária, começando
    no chifre de cima do bolsão, onde o cabo sai do bolsão para o canal."""
    with open(CONTORNO, encoding="utf-8") as fh:
        linhas = [linha for linha in fh if not linha.startswith("#")]
    P = np.array([[_num(r["x_R20"]), _num(r["y_R20"])]
                  for r in csv.DictReader(linhas, delimiter=";")])
    V = P[ConvexHull(P).vertices]                       # anti-horário
    lados = np.hypot(*(np.roll(V, -1, axis=0) - V).T)
    k = (int(np.argmax(lados)) + 1) % len(V)            # o lado mais longo é a ponte sobre o bolsão
    return np.roll(V, -k, axis=0)


def suporte(V, fi):
    """r(φ) = max V·u(φ) e o índice do vértice de saída, para φ (rad) no referencial do came."""
    fi = np.atleast_1d(np.asarray(fi, float))
    proj = V @ np.vstack([np.cos(fi), np.sin(fi)])      # (vértices, direções)
    k = np.argmax(proj, axis=0)
    return proj[k, np.arange(fi.size)], k


def cabo(V, tp, L, lam, r630, iteracoes=60):
    """Tangência do cabo 634 entre o came, girado de θp, e a polia 630.

    Devolve δ, φc, r, ρ e o índice do vértice de saída. Ângulos em rad e comprimentos em
    R20; L = inf dá a polia infinitamente longe (δ = 0)."""
    tp = np.atleast_1d(np.asarray(tp, float))
    d = np.zeros_like(tp)
    for _ in range(iteracoes):
        r, k = suporte(V, lam - np.pi/2 + d - tp)
        novo = np.arcsin(np.clip((r - r630)/L, -1.0, 1.0))
        pronto = np.max(np.abs(novo - d)) < 1e-13
        d = novo
        if pronto:
            break
    fc = lam - np.pi/2 + d
    r, k = suporte(V, fc - tp)
    return d, fc, r, np.hypot(V[k, 0], V[k, 1]), k


def comprimento(V, tp, L, lam, r630):
    """Comprimento do cabo 634 do chifre do bolsão até um ponto fixo da polia 630 (R20):
    arco enrolado no came, vão livre e arco enrolado na 630 (sentido anti-horário)."""
    d, fc, r, rho, k = cabo(V, tp, L, lam, r630)
    lados = np.hypot(*(np.roll(V, -1, axis=0) - V).T)
    arco_came = np.r_[0.0, np.cumsum(lados)[:-1]][k]
    c, s = np.cos(tp), np.sin(tp)
    E = np.c_[c*V[k, 0] - s*V[k, 1], s*V[k, 0] + c*V[k, 1]]
    F = L*np.array([np.cos(lam), np.sin(lam)]) + r630*np.c_[np.cos(fc), np.sin(fc)]
    arco_630 = r630*((lam + np.pi/2 - fc) % (2*np.pi))   # até o ponto em que o cabo volta à mola
    return arco_came + np.hypot(*(F - E).T) + arco_630


def main():
    V = casco_came()
    L, lam, r630 = 4.5, 0.0, 0.5            # geometria de teste, não é dado do mecanismo
    # θp tal que a normal ao cabo, no came, vá de 95° a 355°: saída do chifre de cima até
    # o arco de raio pequeno depois da Z12, sem passar pela ponte do bolsão
    fi_came = np.radians(np.arange(95.0, 355.0, 0.05))
    tp = lam - np.pi/2 - fi_came

    d, fc, r, rho, k = cabo(V, tp, L, lam, r630)
    _, _, r_inf, _, _ = cabo(V, tp, np.inf, lam, r630)
    l = comprimento(V, tp, L, lam, r630)
    dl = np.gradient(l, tp)
    resid = np.abs(dl + r)

    print("Geometria de teste, só para conferir as contas: L = 4,5 R20, r630 = 0,5 R20.")
    print(f"  ângulo do cabo com a linha 572-632: δ de {np.degrees(d.min()):.2f}° a "
          f"{np.degrees(d.max()):.2f}°")
    print(f"  r com a polia a distância finita, contra a polia no infinito: diferença de até "
          f"{np.abs(r - r_inf).max():.4f} R20 no mesmo θp")
    print(f"  δ = asin((r − r630)/L) na solução: resíduo máximo "
          f"{np.abs(np.sin(d) - (r - r630)/L).max():.1e}")
    print(f"  tangência r(φc − θp) − L cos(φc − λ) = r630: resíduo máximo "
          f"{np.abs(r - L*np.cos(fc - lam) - r630).max():.1e} R20")
    print(f"  dℓ/dθp = −r pelo comprimento geométrico: maior diferença {resid.max():.1e} R20 "
          f"(r de {r.min():.4f} a {r.max():.4f} R20)")
    print(f"  ρ ≥ r em todos os pontos: {bool(np.all(rho >= r - 1e-12))}; "
          f"r/ρ mínimo {np.min(r/rho):.4f}")


if __name__ == "__main__":
    main()
