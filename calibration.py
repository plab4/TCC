"""
Calibração do modelo original contra a curva da patente.

Fluxo (na ordem pedida, sem otimizar K e H juntos):

    1. dados da patente  →  curva de referência τ(θ*)
    2. K a partir da patente, com a geometria original (H = 34,785 mm)
    3. K congelado
    4. varredura grossa de H  →  tabela de erros
    5. varredura fina em torno do melhor H
    6. gráficos e verificação na pose do CAD

Rodar:  python calibration.py   (figuras e tabelas vão para results/)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import torque_model as model
from patent_data import estimate_peak, load_patent_data

RESULTS = Path(__file__).parent / "results"

# A patente dá o torque positivo no sentido em que o cabo puxa o braço
# (θ* decrescente). No referencial das equações de fechamento esse sentido é
# o horário, ou seja, negativo. Só a convenção muda; não é um abs().
TORQUE_SIGN_PATENT = -1.0

H_COARSE = np.arange(20.0, 50.01, 0.5)  # mm, ±15 mm em torno do H do CAD
FINE_HALF_WIDTH, FINE_STEP = 1.0, 0.01  # mm


def model_torque(k, h, theta):
    """τ(θ*) do modelo original [N·m], na convenção de sinal da patente."""
    return TORQUE_SIGN_PATENT*model.calculate_torque_curve(k, h, theta)["tau"]


# ---------------------------------------------------------------- passo 2: K

def calibrate_k(patent, h=model.H):
    """K por mínimos quadrados sobre todos os pontos da patente.

    O torque é linear em K: τ_modelo(θ) = K·g(θ), com g = torque para K = 1.
    Minimizar Σ(τ_patente − K·g)² dá K = Σ g·τ / Σ g², sem otimizador.
    """
    g = model_torque(1.0, h, patent["theta_star"])
    k = (g @ patent["torque"])/(g @ g)
    return k, g


def pointwise_k(patent, g, min_fraction=0.2):
    """K_i = τ_i / g_i em cada ponto, para ver se K é de fato constante.

    Pontos com torque abaixo de min_fraction do pico ficam de fora: lá a
    razão divide dois números pequenos e não diz nada sobre K.
    """
    mask = patent["torque"] >= min_fraction*patent["torque"].max()
    return patent["theta_star"][mask], patent["torque"][mask]/g[mask]


# ------------------------------------------------------- passos 4–5: erros

def compare_with_patent(k, h, patent, step=0.05):
    """Métricas de erro do modelo (K, H) contra a patente.

    O modelo é analítico, então é avaliado exatamente nos ângulos da patente
    (nada de interpolação). O pico do modelo vem de uma grade fina; o da
    patente, de uma parábola pelos 3 pontos em volta do máximo.
    """
    theta, torque = patent["theta_star"], patent["torque"]
    error = model_torque(k, h, theta) - torque

    grid = np.arange(theta.min(), theta.max() + step/2, step)
    curve = model_torque(k, h, grid)
    peak_theta_patent, peak_patent = estimate_peak(theta, torque)

    return {
        "H": h,
        "RMSE": np.sqrt(np.mean(error**2)),
        "MAE": np.mean(np.abs(error)),
        "max_abs": np.max(np.abs(error)),
        "peak_error": curve.max() - peak_patent,
        "peak_angle_error": grid[np.argmax(curve)] - peak_theta_patent,
    }


def sweep_h(k, h_values, patent):
    """Uma linha de métricas por H, com K fixo."""
    return [compare_with_patent(k, h, patent) for h in h_values]


def save_table(rows, path):
    keys = list(rows[0])
    lines = [",".join(keys)]
    lines += [",".join(f"{row[key]:.6g}" for key in keys) for row in rows]
    path.write_text("\n".join(lines) + "\n")


def print_table(rows, n=None):
    print(f"{'H (mm)':>8} {'RMSE':>8} {'MAE':>8} {'máx|e|':>8} "
          f"{'erro pico':>10} {'erro âng. pico':>15}")
    for row in rows[:n]:
        print(f"{row['H']:8.2f} {row['RMSE']:8.3f} {row['MAE']:8.3f} "
              f"{row['max_abs']:8.3f} {row['peak_error']:+10.3f} "
              f"{row['peak_angle_error']:+14.2f}°")


# --------------------------------------------------------------- gráficos

SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]  # azul, laranja, verde-água


def new_axes(title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.set_title(title, color=INK, loc="left", fontsize=12)
    ax.set_xlabel(xlabel, color=INK_2)
    ax.set_ylabel(ylabel, color=INK_2)
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK_2)
    ax.tick_params(colors=INK_2)
    return fig, ax


def plot_patent(ax, patent):
    ax.plot(patent["theta_star"], patent["torque"], "o", color=INK,
            markersize=5, label="Patente (pontos extraídos)", zorder=3)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(RESULTS/name, facecolor=SURFACE)
    plt.close(fig)


def make_plots(patent, k, h_low, h_nominal, h_high, coarse, fine, h_best):
    theta = np.linspace(patent["theta_star"].min(),
                        patent["theta_star"].max(), 600)
    torque_label = "Torque (N·m)"
    theta_label = "θ* (graus)"

    # 1 — referência da patente
    fig, ax = new_axes("Curva de referência da patente", theta_label,
                       torque_label)
    ax.plot(patent["theta_star"], patent["torque"], "-", color=INK_2,
            linewidth=1, zorder=2)
    plot_patent(ax, patent)
    ax.legend(frameon=False)
    save(fig, "1_patente.png")

    # 2 — vários H com K fixo
    fig, ax = new_axes(f"Efeito de H com K fixo = {k:.1f} N/mm", theta_label,
                       torque_label)
    for color, h in zip(SERIES, (h_low, h_nominal, h_high)):
        ax.plot(theta, model_torque(k, h, theta), color=color, linewidth=2,
                label=f"Modelo, H = {h:.3f} mm")
    plot_patent(ax, patent)
    ax.legend(frameon=False)
    save(fig, "2_comparacao_H.png")

    # 3 — sensibilidade H × RMSE
    fig, ax = new_axes("Erro em função de H (K fixo)", "H (mm)",
                       "RMSE (N·m)")
    ax.plot([r["H"] for r in coarse], [r["RMSE"] for r in coarse],
            color=SERIES[0], linewidth=2, label="Varredura grossa (0,5 mm)")
    ax.plot([r["H"] for r in fine], [r["RMSE"] for r in fine],
            color=SERIES[1], linewidth=2, label="Varredura fina (0,01 mm)")
    best = min(fine, key=lambda r: r["RMSE"])
    ax.plot(best["H"], best["RMSE"], "o", color=INK, markersize=6, zorder=3)
    ax.annotate(f"H = {h_best:.2f} mm\nRMSE = {best['RMSE']:.2f} N·m",
                (best["H"], best["RMSE"]), textcoords="offset points",
                xytext=(10, 25), color=INK)
    ax.legend(frameon=False)
    save(fig, "3_H_vs_RMSE.png")

    # 4 — melhor H
    fig, ax = new_axes(f"Melhor H = {h_best:.2f} mm (K = {k:.1f} N/mm)",
                       theta_label, torque_label)
    ax.plot(theta, model_torque(k, h_best, theta), color=SERIES[0],
            linewidth=2, label="Modelo original")
    plot_patent(ax, patent)
    ax.legend(frameon=False)
    save(fig, "4_melhor_H.png")


# ------------------------------------------------------------------- main

def main():
    RESULTS.mkdir(exist_ok=True)
    patent = load_patent_data()

    # Passo 1 — referência
    peak_theta, peak_torque = estimate_peak(patent["theta_star"],
                                            patent["torque"])
    print("1. Patente:", len(patent["theta_star"]), "pontos, θ* de "
          f"{patent['theta_star'].min():.1f}° a "
          f"{patent['theta_star'].max():.1f}°; pico estimado "
          f"{peak_torque:.2f} N·m em {peak_theta:.2f}°")

    # Passo 2 — K com a geometria original
    k, g = calibrate_k(patent, model.H)
    residual = patent["torque"] - k*g
    print(f"\n2. K = Σg·τ/Σg² com H = {model.H} mm, todos os "
          f"{len(g)} pontos:  K = {k:.2f} N/mm")
    print(f"   resíduo: RMSE = {np.sqrt(np.mean(residual**2)):.3f} N·m, "
          f"máx |e| = {np.max(np.abs(residual)):.3f} N·m")
    theta_k, k_i = pointwise_k(patent, g)
    print(f"   K ponto a ponto (torque ≥ 20% do pico, {len(k_i)} pontos): "
          f"{k_i.min():.1f} a {k_i.max():.1f} N/mm, média {k_i.mean():.1f}, "
          f"desvio {k_i.std():.1f}")
    for th, ki in zip(theta_k, k_i):
        print(f"     θ* = {th:7.2f}°   K_i = {ki:7.2f}")

    # Passo 3 — K congelado
    K = k
    print(f"\n3. K congelado em {K:.2f} N/mm")

    # Passo 4 — varredura grossa
    coarse = sweep_h(K, H_COARSE, patent)
    save_table(coarse, RESULTS/"varredura_H_grossa.csv")
    print("\n4. Varredura grossa de H (5 melhores, por RMSE):")
    print_table(sorted(coarse, key=lambda r: r["RMSE"]), 5)
    h_coarse = min(coarse, key=lambda r: r["RMSE"])["H"]

    # Passo 5 — varredura fina
    h_fine = np.arange(h_coarse - FINE_HALF_WIDTH,
                       h_coarse + FINE_HALF_WIDTH + FINE_STEP/2, FINE_STEP)
    fine = sweep_h(K, h_fine, patent)
    save_table(fine, RESULTS/"varredura_H_fina.csv")
    best = min(fine, key=lambda r: r["RMSE"])
    near = [r["H"] for r in fine if r["RMSE"] <= 1.05*best["RMSE"]]
    print(f"\n5. Varredura fina: melhor H = {best['H']:.2f} mm "
          f"(RMSE {best['RMSE']:.3f} N·m); RMSE até 5% acima do mínimo "
          f"para H de {min(near):.2f} a {max(near):.2f} mm")
    print_table([best])

    # Passo 6 — gráficos e pose do CAD
    make_plots(patent, K, 30.0, model.H, 40.0, coarse, fine, best["H"])
    pose = model.calculate_torque_curve(K, best["H"], [model.THETA_POSE])
    patent_at_pose = np.interp(model.THETA_POSE, patent["theta_star"],
                               patent["torque"])
    print(f"\n6. Pose do CAD (θ* = {model.THETA_POSE}°, H = {best['H']:.2f}):")
    print(f"   s = {pose['s'][0]:.2f} mm, b = {pose['b'][0]:.2f} mm, "
          f"δ = {pose['delta'][0]:.2f} mm, f = {pose['force'][0]:.0f} N")
    print(f"   τ modelo = {TORQUE_SIGN_PATENT*pose['tau'][0]:.2f} N·m, "
          f"patente (interpolada) = {patent_at_pose:.2f} N·m")
    print(f"   δ na pose = {pose['delta'][0]:.2f} mm;  L_CARCACA − "
          f"L_POSE = {model.L_CARCACA - model.L_POSE:.2f} mm")
    print(f"\nFiguras e tabelas em {RESULTS}/")


if __name__ == "__main__":
    main()
