"""
Modelo de torque do mecanismo cabo + tambor + braço, em função de θ*.

Cadeia de cálculo (cada etapa é uma função abaixo):

    θ*  →  q  →  ρ  →  s  →  φ  →  b, β  →  b_vector, V_vector  →  τ

Unidades: mm, N e N·m. Ângulos em graus na entrada (ALPHA, THETA, ...) e em
radianos dentro das contas; cada conversão é feita uma única vez.

Ainda depende da patente (não está no projeto):
  * a lei da força f (o que é K e qual δ ela usa);
  * a convenção de θ* (ver calculate_array_vaos_livres).
"""
import numpy as np

# ---------------------------------------------------------------- geometria
H = 34.785   # mm, componente h do vetor fixo pivô → ancoragem (a variar)
P = 3.155    # mm, componente p do vetor fixo pivô → ancoragem
C = 283.438  # mm, braço: pivô → centro do tambor
R = 22.827   # mm, raio do tambor
ALPHA = 20.428  # graus

# ------------------------------------------------------------- referências
L_CARCACA = 131.37  # mm
TAU_PESO = 11.165   # N·m (ainda não usado)
T_MAX = 140         # N·m, pico desejado do torque do cabo

THETA = np.arange(10.0, 190.01, 0.5)  # graus, de 10° a 190° (inclusive)
THETA_REF = 10.0      # graus, referência de δ = s − s10
THETA_POSE = 115.017  # graus, pose medida no CAD
SPRING_POSE = 91.35   # mm, comprimento da mola nessa pose


# ======================================================================
# 1. Cinemática: θ* → q → ρ → s → φ   (equações de fechamento)
# ======================================================================

def calculate_q(theta_star):
    """q = θ* − π/2 − α  [rad], com θ* em graus."""
    return np.radians(theta_star) - np.pi/2 - np.radians(ALPHA)


def calculate_base_vector(h=H):
    """B = (h sen α − p cos α,  h cos α + p sen α).

    São os termos constantes de f1 e f2: o vetor fixo pivô → ancoragem.
    """
    a = np.radians(ALPHA)
    return h*np.sin(a) - P*np.cos(a), h*np.cos(a) + P*np.sin(a)


def calculate_rho(q, h=H):
    """ρ: distância da ancoragem ao centro do tambor, |B + C·(cos q, sen q)|."""
    bx, by = calculate_base_vector(h)
    return np.hypot(bx + C*np.cos(q), by + C*np.sin(q))


def calculate_tangent_span(rho):
    """s: vão livre do cabo (ancoragem → ponto de tangência no tambor).

    O raio é perpendicular ao cabo na tangência, então s² + R² = ρ².
    """
    return np.sqrt(rho**2 - R**2)


def calculate_phi(q, s, h=H):
    """φ: direção do cabo, isolada analiticamente das equações de fechamento.

    Deixando de um lado só os termos com φ:
        s cos φ − R sen φ = Wx
        s sen φ + R cos φ = Wy,     com W = −(B + C·(cos q, sen q))
    O lado esquerdo é o vetor (s, R) girado de φ, logo
        ângulo de W = φ + atan2(R, s)   →   φ = atan2(Wy, Wx) − atan2(R, s)
    """
    bx, by = calculate_base_vector(h)
    wx = -(bx + C*np.cos(q))
    wy = -(by + C*np.sin(q))
    return np.arctan2(wy, wx) - np.arctan2(R, s)


def calculate_closure_residuals(q, s, phi, h=H):
    """f1 e f2 como escritos, para conferir a solução (devem dar ≈ 0).

    O comprimento que multiplica cos φ e sen φ é o vão s: com q (radianos)
    nessa posição o sistema não tem solução para nenhum θ*.
    """
    a = np.radians(ALPHA)
    f1 = (h*np.sin(a) - P*np.cos(a)
          + s*np.cos(phi) - R*np.sin(phi) + C*np.cos(q))
    f2 = (h*np.cos(a) + P*np.sin(a)
          + s*np.sin(phi) + R*np.cos(phi) + C*np.sin(q))
    return f1, f2


# ======================================================================
# 2. Fórmulas originais: deslocamento δ, b, β e torque
# ======================================================================

def calculate_array_vaos_livres(theta, h=H):
    """Fórmula original (agora com a raiz; antes devolvia s²).

    Atenção: o termo 2C(...) tem sinal oposto ao das equações de fechamento,
    então isto é igual a calculate_rho(calculate_q(theta + 180)). Mantida para
    comparação; a cadeia usa calculate_rho. A patente deve decidir.
    """
    t = np.radians(theta)
    return np.sqrt(h**2 + P**2 + C**2 + 2*C*(h*np.cos(t) + P*np.sin(t)))


def calculate_diff_s_s10(s, s10):
    """δ = s − s10, com s10 já calculado em θ* = 10° (sem converter 2 vezes)."""
    return s - s10


def measure_moment_arm(s, phi, h=H):
    """b: distância do pivô ao ponto onde o cabo toca o tambor.

    Lei dos cossenos original no triângulo pivô–ancoragem–tangência. O ângulo
    entre os lados é o ângulo entre B e o cabo, por isso desconta a direção
    de B. b varia com θ* porque s e φ variam.
    """
    bx, by = calculate_base_vector(h)
    angle = phi - np.arctan2(by, bx)
    return np.sqrt(s**2 + h**2 + P**2
                   + 2*s*np.sqrt(h**2 + P**2)*np.cos(angle))


def measure_moment_arm_deflection(b):
    """β: ângulo entre a linha do braço (pivô → centro do tambor) e b.

    Lei dos cossenos original no triângulo de lados b, C e R.
    """
    return np.arccos((b**2 + C**2 - R**2) / (2*b*C))


def torque_patent(b_vector, f_vector):
    """τ = componente z de b × F = bx·Fy − by·Fx.

    É a parte antissimétrica do produto externo original np.outer(b, F),
    M[0, 1] − M[1, 0]. Positivo = anti-horário (sentido de θ* crescente).
    """
    return b_vector[0]*f_vector[1] - b_vector[1]*f_vector[0]


# ======================================================================
# 3. Cadeia completa
# ======================================================================

def generate_graph_torque_theta_star_relation(force, h=H, theta=THETA):
    """Calcula todas as grandezas para cada θ*.

    force: tração do cabo f [N], número ou array do tamanho de theta.
           A lei f(K, δ) virá da patente; aqui ela é só uma entrada.
    h:     valor de H a testar [mm].
    theta: ângulos θ* [graus].
    """
    theta = np.asarray(theta, dtype=float)

    # cinemática
    q = calculate_q(theta)
    rho = calculate_rho(q, h)
    s = calculate_tangent_span(rho)
    phi = calculate_phi(q, s, h)
    f1, f2 = calculate_closure_residuals(q, s, phi, h)

    # deslocamento do cabo desde θ* = 10°
    s10 = calculate_tangent_span(calculate_rho(calculate_q(THETA_REF), h))
    delta = calculate_diff_s_s10(s, s10)

    # braço b e ângulo β (ambos variam com θ*)
    b = measure_moment_arm(s, phi, h)
    beta = measure_moment_arm_deflection(b)

    # vetores da formulação original e torque
    f = np.broadcast_to(np.asarray(force, dtype=float), theta.shape)
    b_vector = np.array([-b*np.cos(beta - q), b*np.sin(beta - q)])  # mm
    V_vector = np.array([-f*np.cos(phi), -f*np.sin(phi)])          # N
    tau = torque_patent(b_vector, V_vector) / 1000                  # N·m

    return dict(theta_star=theta, q=q, rho=rho, s=s, phi=phi, f1=f1, f2=f2,
                delta=delta, b=b, beta=beta, force=f,
                b_vector=b_vector, V_vector=V_vector, tau=tau)


if __name__ == "__main__":
    # Com f = 1 N, τ em N·mm é o braço efetivo de alavanca em mm.
    angles = [10.0, 45.0, 90.0, THETA_POSE, 150.0, 190.0]
    r = generate_graph_torque_theta_star_relation(1.0, theta=angles)

    print("   θ*(°)     φ(°)     s(mm)    b(mm)   β(°)   δ(mm)  τ/f(mm)")
    for i, th in enumerate(angles):
        print(f"{th:8.3f} {np.degrees(r['phi'][i]):8.2f} {r['s'][i]:9.3f} "
              f"{r['b'][i]:8.3f} {np.degrees(r['beta'][i]):6.3f} "
              f"{r['delta'][i]:7.3f} {r['tau'][i]*1000:8.3f}")
    print(f"resíduo máximo de f1, f2: {np.max(np.abs(r['f1'])):.1e}, "
          f"{np.max(np.abs(r['f2'])):.1e} mm")
