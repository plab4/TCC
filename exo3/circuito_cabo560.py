"""
Circuito do cabo de ancoragem 560 do exoesqueleto 3, na geometria do CAD do autor.

Ângulos no referencial do CAD, anti-horários a partir da horizontal: γ (C1, de A a O),
φ (R, de D a T) e θ (S, de T a A). A variável primária q é o ângulo entre C2 (de O a D)
e a horizontal, 61,724° na pose do CAD; nesse referencial, a direção de C2 é 180° − q:

    S u(θ) + R u(φ) + C2 u(180° − q) + C1 u(γ) = 0
    f1 = S cos θ + R cos φ − C2 cos q + C1 cos γ = 0
    f2 = S sin θ + R sin φ + C2 sin q + C1 sin γ = 0

O mecanismo tem um grau de liberdade: a primária q e duas secundárias, S e φ. O cabo é
tangente à polia, então θ = φ − 90° (σ = −1, como na pose do CAD); a tangência tira uma
incógnita, não uma equação. A solução é fechada:

    d = A − D = −(C1 u(γ) + C2 u(180° − q)),   S = √(|d|² − R²),
    φ = ang(d) + atan2(S, R)

O caminho inverso, com θ dado, também fecha: φ = θ + 90°, w = −(R u(φ) + C1 u(γ)),
q = 180° − φ ∓ acos(w·u(φ)/C2) e S = (w − C2 u(180° − q))·u(θ). Dos dois ramos, o do
sinal de cima devolve a pose do CAD; o outro dá S negativo.

Braço: b = C2 u(180° − q) + R u(φ), de O a T; β é o ângulo em O entre C2 e b, e a
direção de b é 180° − q − β. Então

    (b × f)_z = −b F_a sin(θ + q + β) = F_a C1 sin(γ − θ).

A segunda forma sai do fechamento (b = −S u(θ) − C1 u(γ)): como a linha do cabo passa
por A, o braço em torno de O só depende de θ. Ele zera em θ = γ + 180°, com o cabo
alinhado a C1 e passando por O.

Rodar (na raiz do repositório):
    python exo3/circuito_cabo560.py
"""
import numpy as np

C1, C2, R = 70.711, 90.587, 26.443        # mm, CAD do autor
GAMA = 61.26                              # graus, referencial do CAD
Q_CAD = 61.724                            # graus, ângulo entre C2 e a horizontal na pose


def u(a):
    a = np.radians(a)
    return np.array([np.cos(a), np.sin(a)])


def ang(v):
    return np.degrees(np.arctan2(v[1], v[0])) % 360


def meia_volta(a):
    return (a + 180) % 360 - 180


def circuito(q):
    """S, φ, θ, b, β e o braço do cabo em torno de O (mm e graus), para q dado."""
    c2 = C2*u(180 - q)
    d = -(C1*u(GAMA) + c2)
    S = float(np.sqrt(d @ d - R**2))
    fi = (ang(d) + np.degrees(np.arctan2(S, R))) % 360
    teta = (fi - 90) % 360
    bv = c2 + R*u(fi)
    b = float(np.hypot(*bv))
    beta = meia_volta((180 - q) - ang(bv))
    braco = -b*np.sin(np.radians(teta + q + beta))
    assert abs(braco - C1*np.sin(np.radians(GAMA - teta))) < 1e-9
    return S, fi, teta, b, beta, braco


def circuito_por_teta(teta):
    """Inverso: q e S para o ângulo θ do cabo, nos dois ramos."""
    fi = teta + 90
    w = -(R*u(fi) + C1*u(GAMA))
    c = np.degrees(np.arccos(np.clip(w @ u(fi)/C2, -1, 1)))
    ramos = []
    for q in (meia_volta(180 - fi - c), meia_volta(180 - fi + c)):
        ramos.append((q, float((w - C2*u(180 - q)) @ u(teta))))
    return ramos


def main():
    q_zero = circuito_por_teta(GAMA + 180)[0][0]
    print("q como primária (mm e graus):")
    print("       q        S        φ        θ        b       β   C1 sin(γ−θ)")
    for q in sorted(set(range(-30, 121, 15)) | {Q_CAD, round(q_zero, 3)}):
        S, fi, teta, b, beta, braco = circuito(q)
        print(f"{q:8.3f} {S:8.3f} {fi:8.3f} {teta:8.3f} {b:8.3f} {beta:7.3f} {braco:10.3f}")
    S, fi, teta, b, beta, braco = circuito(Q_CAD)
    print(f"\nPose do CAD: S = {S:.3f}, φ = {fi:.3f}, θ = {teta:.3f}, b = {b:.3f}, β = {beta:.3f}, "
          f"braço = {braco:.3f}")
    print("Inverso com θ = " + f"{teta:.3f}: " +
          "; ".join(f"q = {qq:.3f}, S = {s:.3f}" for qq, s in circuito_por_teta(teta)))
    print(f"O braço zera em θ = γ + 180° = {GAMA + 180:.2f}°, isto é, em q = {q_zero:.3f}°.")


if __name__ == "__main__":
    main()
