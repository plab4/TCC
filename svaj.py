"""
Diagrama SVAJ a partir das equações de circuito (formulação simbólica).

    variável primária:      q
    variáveis secundárias:  s, ψ
    f1 =  C1 cos α + C2 cos γ + e cos q − s cos ψ = 0
    f2 = −C1 sen α + C2 sen γ + e sen q − s sen ψ = 0

Coeficientes cinemáticos (derivadas em relação a q):
    K = ds/dq = −[J]⁻¹ ∂f/∂q        (velocidade)
    L = dK/dq                       (aceleração)
    M = dL/dq                       (jerk)

Com ω = dq/dt constante: V = K·ω, A = L·ω², J = M·ω³. Como dq = dθ*, os
coeficientes em relação a q são os mesmos em relação a θ*.

Valores numéricos: a mesma geometria de torque_model. Com C1 = −P, C2 = H,
γ = π/2 − α e e = C, o termo fixo do circuito é exatamente o vetor (h, p)
das equações de fechamento (verificado simbolicamente). Assim s é a
distância da ancoragem ao centro do tambor (ρ em torque_model).

Rodar:  python svaj.py   (figuras em results/)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sympy as sy
from sympy import Function, Matrix, cos, sin, symbols

import torque_model as model

# ------------------------------------------------------------ simbólico
q = symbols('q')                                  # primária
s, psi = symbols('s psi')                         # secundárias
C1, C2, e, alpha, gamma = symbols('C1 C2 e alpha gamma')   # constantes
Ks, Kpsi, Ls, Lpsi = symbols('K_s K_psi L_s L_psi')

f1 = C1*cos(alpha) + C2*cos(gamma) + e*cos(q) - s*cos(psi)
f2 = -C1*sin(alpha) + C2*sin(gamma) + e*sin(q) - s*sin(psi)
f = Matrix([f1, f2])

Jacobian = f.jacobian([s, psi])      # ∂f/∂(s, ψ)  (2×2)
df_dq = f.jacobian([q])              # ∂f/∂q       (2×1)
MatK = sy.simplify(-Jacobian.inv() @ df_dq)

# d/dq de cada variável que depende de q
CADEIA = {s: Ks, psi: Kpsi, Ks: Ls, Kpsi: Lpsi}


def derivada_em_q(M):
    """dM/dq pela mesma técnica do código original: troca cada variável
    por uma função de q, deriva e troca as derivadas pelos símbolos K, L."""
    funcoes = {v: Function(v.name)(q) for v in CADEIA}
    dM = sy.diff(M.subs(funcoes, simultaneous=True), q)
    dM = dM.subs({sy.Derivative(funcoes[v], q): d for v, d in CADEIA.items()})
    return dM.subs({fn: v for v, fn in funcoes.items()})


MatL = sy.simplify(derivada_em_q(MatK))   # depende de K_s, K_ψ
MatM = derivada_em_q(MatL)                # depende de K e de L (só numérico)

ARGS = (q, s, psi, Ks, Kpsi, Ls, Lpsi, C1, C2, e, alpha, gamma)
_K = sy.lambdify(ARGS, MatK, "numpy")
_L = sy.lambdify(ARGS, MatL, "numpy")
_M = sy.lambdify(ARGS, MatM, "numpy")


# ------------------------------------------------------------- numérico
def constants(h=model.H):
    """C1, C2, e, α, γ a partir da geometria de torque_model."""
    a = np.radians(model.ALPHA)
    return -model.P, h, model.C, a, np.pi/2 - a


def position(q_val, consts):
    """Posição em forma fechada: s·(cos ψ, sen ψ) = termo fixo + e·(cos q, sen q)."""
    c1, c2, ee, a, g = consts
    x = c1*np.cos(a) + c2*np.cos(g) + ee*np.cos(q_val)
    y = -c1*np.sin(a) + c2*np.sin(g) + ee*np.sin(q_val)
    return np.hypot(x, y), np.arctan2(y, x)


def calculate_svaj(theta_star, h=model.H, omega=None):
    """S, V, A, J de s e de ψ para cada θ* (graus).

    Sem omega: coeficientes por radiano (V = ds/dq, A = d²s/dq², J = d³s/dq³).
    Com omega [rad/s] constante: valores no tempo (V·ω, A·ω², J·ω³).
    """
    theta_star = np.asarray(theta_star, dtype=float)
    consts = constants(h)
    q_val = model.calculate_q(theta_star)
    s_val, psi_val = position(q_val, consts)
    zero = np.zeros_like(q_val)

    k = _K(q_val, s_val, psi_val, zero, zero, zero, zero, *consts)
    k_s, k_psi = (np.broadcast_to(v, q_val.shape) for v in k[:, 0])
    l = _L(q_val, s_val, psi_val, k_s, k_psi, zero, zero, *consts)
    l_s, l_psi = (np.broadcast_to(v, q_val.shape) for v in l[:, 0])
    m = _M(q_val, s_val, psi_val, k_s, k_psi, l_s, l_psi, *consts)
    m_s, m_psi = (np.broadcast_to(v, q_val.shape) for v in m[:, 0])

    w = 1.0 if omega is None else omega
    return {
        "theta_star": theta_star, "q": q_val,
        "S": s_val, "V": k_s*w, "A": l_s*w**2, "J": m_s*w**3,
        "psi": psi_val, "V_psi": k_psi*w, "A_psi": l_psi*w**2,
        "J_psi": m_psi*w**3,
    }


# -------------------------------------------------------------- gráfico
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
COLOR = "#2a78d6"


def plot_svaj(res, rows, title, path):
    fig, axes = plt.subplots(4, 1, figsize=(8, 9), dpi=150, sharex=True,
                             facecolor=SURFACE)
    for ax, (key, label, scale) in zip(axes, rows):
        ax.set_facecolor(SURFACE)
        ax.plot(res["theta_star"], res[key]*scale, color=COLOR, linewidth=2)
        ax.axhline(0, color=INK_2, linewidth=0.8)
        ax.axvline(model.THETA_POSE, color=INK_2, linewidth=0.8,
                   linestyle="--")
        ax.set_ylabel(label, color=INK_2)
        ax.grid(color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(INK_2)
        ax.tick_params(colors=INK_2)
    axes[0].set_title(title, color=INK, loc="left", fontsize=12)
    axes[0].annotate(f"pose CAD {model.THETA_POSE}°",
                     (model.THETA_POSE, 0), xycoords=("data", "axes fraction"),
                     xytext=(4, 4), textcoords="offset points",
                     color=INK_2, fontsize=8)
    axes[-1].set_xlabel("θ* (graus)", color=INK_2)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def main():
    results = Path(__file__).parent / "results"
    results.mkdir(exist_ok=True)

    print("det[J] =", sy.simplify(Jacobian.det()))
    print("K = ds/dq =")
    sy.pprint(MatK)
    print("L = dK/dq =")
    sy.pprint(MatL)

    res = calculate_svaj(model.THETA)
    plot_svaj(res, [("S", "S = s (mm)", 1),
                    ("V", "V = ds/dq\n(mm/rad)", 1),
                    ("A", "A = d²s/dq²\n(mm/rad²)", 1),
                    ("J", "J = d³s/dq³\n(mm/rad³)", 1)],
              f"Diagrama SVAJ de s (H = {model.H} mm, por unidade de ω)",
              results/"5_svaj_s.png")
    plot_svaj(res, [("psi", "ψ (graus)", 180/np.pi),
                    ("V_psi", "dψ/dq\n(rad/rad)", 1),
                    ("A_psi", "d²ψ/dq²\n(1/rad)", 1),
                    ("J_psi", "d³ψ/dq³\n(1/rad²)", 1)],
              f"Diagrama SVAJ de ψ (H = {model.H} mm, por unidade de ω)",
              results/"6_svaj_psi.png")

    pose = calculate_svaj([model.THETA_POSE])
    print(f"\nPose CAD θ* = {model.THETA_POSE}°: S = {pose['S'][0]:.3f} mm, "
          f"V = {pose['V'][0]:.3f} mm/rad, A = {pose['A'][0]:.3f} mm/rad², "
          f"J = {pose['J'][0]:.3f} mm/rad³")
    print(f"Figuras em {results}/")


if __name__ == "__main__":
    main()
