"""
Circuito do cabo de ancoragem 560 do exoesqueleto 3, na geometria do CAD do autor.

    S u(q) + R u(φ) + C2 u(α) + C1 u(γ) = 0,        q = φ − 90° (σ = −1)

O mecanismo tem um grau de liberdade: uma variável primária, o ângulo do apoio de braço,
que entra por α = Θ + α0, e duas secundárias, S e φ. A tangência liga q a φ e tira uma
incógnita, não uma equação; as duas equações do fechamento ficam para S e φ. A solução é
fechada:

    d = A − D = −(C1 u(γ) + C2 u(α)),   S = √(|d|² − R²),   φ = ang(d) + atan2(S, R)

Com q como primária, as secundárias passam a ser S e α, e também fecha:

    φ = q + 90°,   w = −(R u(φ) + C1 u(γ)),   α = φ ± acos(w·u(φ)/C2),
    S = (w − C2 u(α))·u(q)

com dois ramos; o do mecanismo é o que devolve a pose do CAD.

Braço: b = C2 u(α) + R u(φ), de O a T; β é o ângulo em O entre C2 e b, e

    (b × f)_z = b F_a sin(q − α + β) = F_a b⊥,   b⊥ = C1 sin(γ − q).

A segunda forma sai do fechamento (b = −S u(q) − C1 u(γ)): como a linha do cabo passa
por A, o braço em torno de O só depende de q. Ele zera quando q = γ + 180°, com o cabo
alinhado a C1 e passando por O.

Sem o Θ da pose do CAD (e, com ele, α0), a varredura é feita em ΔΘ = Δα a partir dela.

Rodar (na raiz do repositório):
    python exo3/circuito_cabo560.py
"""
import numpy as np
from scipy.optimize import brentq

C1, C2, R = 70.711, 90.587, 26.443        # mm, CAD do autor
GAMA, ALFA_CAD = 61.26, 118.276           # graus


def u(a):
    a = np.radians(a)
    return np.array([np.cos(a), np.sin(a)])


def ang(v):
    return np.degrees(np.arctan2(v[1], v[0])) % 360


def circuito(alfa):
    """S, φ, q, b, β e b⊥ (mm e graus) para o ângulo α de C2."""
    d = -(C1*u(GAMA) + C2*u(alfa))
    S = np.sqrt(d @ d - R**2)
    fi = (ang(d) + np.degrees(np.arctan2(S, R))) % 360
    q = (fi - 90) % 360
    bv = C2*u(alfa) + R*u(fi)
    b = float(np.hypot(*bv))
    beta = (alfa - ang(bv) + 180) % 360 - 180
    b_perp = b*np.sin(np.radians(q - alfa + beta))
    assert abs(b_perp - C1*np.sin(np.radians(GAMA - q))) < 1e-9
    return S, fi, q, b, beta, b_perp


def circuito_por_q(q):
    """Inverso: α e S para o ângulo q do cabo, nos dois ramos."""
    fi = q + 90
    w = -(R*u(fi) + C1*u(GAMA))
    c = np.degrees(np.arccos(np.clip(w @ u(fi)/C2, -1, 1)))
    ramos = []
    for alfa in ((fi + c) % 360, (fi - c) % 360):
        ramos.append((alfa, float((w - C2*u(alfa)) @ u(q))))
    return ramos


def main():
    print("Varredura a partir da pose do CAD (ΔΘ = Δα), comprimentos em mm e ângulos em graus:")
    print("   ΔΘ        α        S        φ        q        b       β       b⊥")
    for dT in range(-90, 91, 15):
        S, fi, q, b, beta, bp = circuito(ALFA_CAD + dT)
        print(f"{dT:5d} {ALFA_CAD + dT:8.3f} {S:8.3f} {fi:8.3f} {q:8.3f} {b:8.3f} {beta:7.3f} {bp:8.3f}")

    zero = brentq(lambda dT: circuito(ALFA_CAD + dT)[5], -60, -20)
    print(f"\nb⊥ = 0 (a linha do cabo passa por O) em ΔΘ = {zero:.2f}°, com q = "
          f"{circuito(ALFA_CAD + zero)[2]:.3f}°; abaixo disso o momento do cabo troca de sinal.")

    S, fi, q, b, beta, bp = circuito(ALFA_CAD)
    ramos = circuito_por_q(q)
    print(f"Pose do CAD: S = {S:.3f}, φ = {fi:.3f}, q = {q:.3f}, b = {b:.3f}, β = {beta:.3f}, "
          f"b⊥ = {bp:.3f}")
    print("Inverso com q como primária: " + "; ".join(f"α = {a:.3f}, S = {s:.3f}" for a, s in ramos))


if __name__ == "__main__":
    main()
