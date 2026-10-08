"""
Modelo de torque do mecanismo cabo + tambor + braço, em função de θ*.

Cadeia de cálculo (cada etapa é uma função abaixo):

    θ*  →  q  →  ρ  →  s  →  φ  →  T (b_vector)  →  V_vector  →  τ
                                      └→ b, β, m (relatório)

Unidades: comprimentos em mm. Ângulos em graus na entrada (ALPHA, THETA, ...)
e em radianos dentro das contas; cada conversão é feita uma única vez.
O torque do cabo sai na unidade da curva extraída da patente (u.p.), porque K
foi calibrado contra ela e a ordenada da patente não tem unidade declarada.
O torque do peso (torque_peso) sai em N·m. Não há conversão entre os dois.

Sinal: τ positivo = anti-horário = sentido de θ* crescente.
Parâmetros K, H_CALIBRADO e L_LIVRE são congelados: nada é ajustado aqui.
"""
import numpy as np

# ---------------------------------------------------------------- geometria
H = 34.785   # mm, componente h do vetor fixo pivô → ancoragem (a variar)
P = 3.155    # mm, componente p do vetor fixo pivô → ancoragem
C = 283.438  # mm, braço: pivô → centro do tambor
R = 22.827   # mm, raio do tambor
ALPHA = 20.428  # graus

# ------------------------------------------------------- CAD A CONFIRMAR
# Dois valores conflitam com o CAD usado antes. Nenhum foi escolhido em
# silêncio: os atuais ficam ativos até a confirmação.
L_CARCACA = 131.37  # mm, CAD anterior: 140,0. Não é usado na cadeia.
L_POSE = 91.35      # mm, comprimento da mola na pose THETA_POSE. CAD anterior:
                    # 90,13. Se for 90,13, L_LIVRE cai 1,22 mm para manter s_zero.

THETA_POSE = 115.017  # graus, pose medida no CAD

# ------------------------------------------------- faixa de operação (patente)
# Mapeamento congelado θ* = ANGLE_OFFSET − φ_pat. φ_pat é o ângulo da patente,
# diferente do φ deste modelo (direção do cabo); por isso o nome phi_pat.
ANGLE_OFFSET = 133.017              # graus
PHI_PAT_MIN, PHI_PAT_MAX = -60.0, 90.1   # graus, faixa da patente
THETA_MIN = ANGLE_OFFSET - PHI_PAT_MAX   # 42,917°
THETA_MAX = ANGLE_OFFSET - PHI_PAT_MIN   # 193,017°
THETA = np.append(np.arange(THETA_MIN, THETA_MAX, 0.5), THETA_MAX)  # graus

# ------------------------------------------- parâmetros calibrados (congelados)
# Calibrados fora deste arquivo contra a curva da patente; aqui só são usados.
K = 175.43          # rigidez da mola: K·δ·m/1000 sai em u.p. (seria N/mm se u.p. = N·m)
H_CALIBRADO = 22.701  # mm, H que reproduz a patente com K e L_LIVRE
L_LIVRE = 53.892    # mm, comprimento livre da mola: s_zero(H_CALIBRADO) = 252,65 mm


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
    Se ρ ≤ R a ancoragem está dentro do tambor e não há tangente.
    """
    if np.any(np.asarray(rho) <= R):
        raise ValueError(f"ρ ≤ R = {R} mm: ancoragem dentro do tambor, sem tangente")
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


def ponto_morto(h=H):
    """θ* do ponto morto em forma fechada [graus].

    No ponto morto a linha do cabo passa pelo pivô (m = 0, τ = 0):
    θ*_pm = 180 + atan2(P, h) + asen(R/C). Depois dele o torque troca de sinal.
    """
    return 180.0 + np.degrees(np.arctan2(P, h)) + np.degrees(np.arcsin(R/C))


def ponto_morto_numerico(h=H, tol=1e-10):
    """θ* do ponto morto pela raiz de m(θ*), por bissecção [graus].

    Só serve de autoteste para ponto_morto; não ajusta nenhum parâmetro.
    """
    def m_de(theta_star):
        q = calculate_q(theta_star)
        s = calculate_tangent_span(calculate_rho(q, h))
        return braco_perpendicular(calculate_phi(q, s, h), h)

    a, b = THETA_POSE, THETA_MAX + 10.0
    if np.sign(m_de(a)) == np.sign(m_de(b)):
        raise ValueError("m não troca de sinal no intervalo")
    while b - a > tol:
        meio = 0.5*(a + b)
        if np.sign(m_de(meio)) == np.sign(m_de(a)):
            a = meio
        else:
            b = meio
    return 0.5*(a + b)


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


def s_zero(h=H):
    """Valor de s em que a mola atinge o comprimento livre (força nula) [mm].

    A mola mede L_POSE na pose THETA_POSE e se alonga junto com s, então
    comprimento da mola = L_POSE + (s − s_pose). Ela relaxa quando esse
    comprimento vale L_LIVRE.
    """
    s_pose = calculate_tangent_span(calculate_rho(calculate_q(THETA_POSE), h))
    return s_pose - L_POSE + L_LIVRE


def calculate_delta(s, h=H):
    """δ = extensão elástica da mola [mm]. O cabo traciona, mas não empurra."""
    return np.maximum(s - s_zero(h), 0.0)


def ponto_tangencia(q, phi):
    """T: ponto onde o cabo deixa o tambor, em relação ao pivô [mm].

    T = centro da polia + R·(sen φ, −cos φ), com centro da polia = −C·(cos q,
    sen q). Não depende do sinal de β, então continua certo mesmo se o
    roteamento do cabo mudar de lado da polia.
    """
    centro_polia = np.array([-C*np.cos(q), -C*np.sin(q)])
    return centro_polia + R*np.array([np.sin(phi), -np.cos(phi)])


def distancia_ponto_tangencia(s, phi, h=H):
    """b: distância do pivô ao ponto onde o cabo toca o tambor [mm].

    NÃO é o braço de momento: o ponto de tangência está no círculo de raio R
    centrado a C do pivô, então b fica entre C − R e C + R (261 a 306 mm).
    O braço de momento é braco_perpendicular. τ = F·b erra por um fator ~9.

    Lei dos cossenos original no triângulo pivô–ancoragem–tangência. O ângulo
    entre os lados é o ângulo entre B e o cabo, por isso desconta a direção
    de B. b varia com θ* porque s e φ variam.
    """
    bx, by = calculate_base_vector(h)
    angle = phi - np.arctan2(by, bx)
    return np.sqrt(s**2 + h**2 + P**2
                   + 2*s*np.sqrt(h**2 + P**2)*np.cos(angle))


def angulo_beta(b):
    """β: ângulo entre a linha do braço (pivô → centro do tambor) e b.

    Lei dos cossenos original no triângulo de lados b, C e R. Um argumento
    fora de [−1, 1] indica geometria inconsistente: levanta erro em vez de
    truncar.
    """
    cos_beta = (b**2 + C**2 - R**2) / (2*b*C)
    if np.any(np.abs(cos_beta) > 1.0):
        raise ValueError("argumento do arccos de β fora de [−1, 1]")
    return np.arccos(cos_beta)


def braco_perpendicular(phi, h=H):
    """m: braço de momento do cabo, distância perpendicular do pivô à linha
    de ação do cabo [mm], com sinal: m = A_x·sen φ − A_y·cos φ.

    A = vetor base (pivô → ancoragem). A linha de ação passa por A, então
    |m| ≤ |A| = √(H² + P²) (34,93 mm com H = 34,785).

    Identidade verificada: τ = −F·m (τ positivo = anti-horário).
    """
    ax, ay = calculate_base_vector(h)
    return ax*np.sin(phi) - ay*np.cos(phi)


def torque_patent(b_vector, f_vector):
    """τ = componente z de b × F = bx·Fy − by·Fx.

    É a parte antissimétrica do produto externo original np.outer(b, F),
    M[0, 1] − M[1, 0]. Positivo = anti-horário (sentido de θ* crescente).
    """
    return b_vector[0]*f_vector[1] - b_vector[1]*f_vector[0]


# ======================================================================
# 3. Torque do peso (independente da cadeia do cabo)
# ======================================================================

MASS_KG = 4.034309       # kg, CAD
CG_DX_MM = -281.431845   # mm, CG na pose THETA_POSE, referencial do desenho
CG_DY_MM = -19.812358    # mm
GRAVITY = 9.80665        # m/s²


def torque_peso(theta_star):
    """Torque estático do peso em relação ao pivô [N·m], em módulo.

    O CG é dado na pose THETA_POSE, no referencial do desenho. Ele gira
    (θ* − THETA_POSE) com o elo, e o desenho ainda gira (ALPHA + 90 −
    ANGLE_OFFSET) = −22,589° para alinhar a vertical do desenho com a da
    configuração calibrada. Não usa K, L_LIVRE, H nem a cadeia do cabo.
    Inércia (Steiner) não entra: o torque é estático.
    """
    giro = np.radians(np.asarray(theta_star, dtype=float) - THETA_POSE
                      + ALPHA + 90.0 - ANGLE_OFFSET)
    x_cg = CG_DX_MM*np.cos(giro) - CG_DY_MM*np.sin(giro)
    return MASS_KG*GRAVITY*np.abs(x_cg)/1000.0


# ======================================================================
# 4. Cadeia completa
# ======================================================================

def generate_graph_torque_theta_star_relation(force, h=H, theta=THETA):
    """Calcula todas as grandezas para cada θ*.

    force: tração do cabo f, número ou array do tamanho de theta. Com
           força unitária, tau·1000 = −m. Para f = K·δ use calculate_torque_curve.
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

    # extensão da mola a partir do comprimento livre
    delta = calculate_delta(s, h)

    # ponto de tangência (cadeia) e, para relatório, b, β e o braço m
    b_vector = ponto_tangencia(q, phi)                               # mm
    b = distancia_ponto_tangencia(s, phi, h)
    beta = angulo_beta(b)
    m = braco_perpendicular(phi, h)

    # conferência: a via original por b e β tem que dar o mesmo ponto
    b_vector_beta = np.array([-b*np.cos(beta - q), b*np.sin(beta - q)])
    erro_T = np.max(np.abs(b_vector - b_vector_beta))
    assert erro_T < 1e-9, f"T por b, β difere da tangência em {erro_T:.1e} mm"

    # força do cabo e torque
    f = np.broadcast_to(np.asarray(force, dtype=float), theta.shape)
    V_vector = np.array([-f*np.cos(phi), -f*np.sin(phi)])          # N
    tau = torque_patent(b_vector, V_vector) / 1000

    return dict(theta_star=theta, q=q, rho=rho, s=s, phi=phi, f1=f1, f2=f2,
                delta=delta, b=b, beta=beta, m=m, force=f,
                b_vector=b_vector, b_vector_beta=b_vector_beta,
                erro_T=erro_T, V_vector=V_vector, tau=tau)


def spring_force(k, delta):
    """Lei da mola do modelo original: f = K·δ, com δ em mm."""
    return k*delta


def calculate_torque_curve(k, h=H, theta=THETA):
    """Cadeia completa com f = K·δ, para um K e um H dados (τ em u.p.)."""
    geometry = generate_graph_torque_theta_star_relation(0.0, h, theta)
    force = spring_force(k, geometry["delta"])
    return generate_graph_torque_theta_star_relation(force, h, theta)


# ======================================================================
# 5. Autotestes, relatório e gráfico
# ======================================================================

def autotestes(h=H_CALIBRADO):
    """Confere a cadeia com força unitária e devolve os números."""
    r = generate_graph_torque_theta_star_relation(1.0, h, THETA)
    numeros = {
        "residuo_f1": np.max(np.abs(r["f1"])),
        "residuo_f2": np.max(np.abs(r["f2"])),
        "tau_mais_F_m": np.max(np.abs(r["tau"]*1000 + r["m"])),
        "T_duas_vias": r["erro_T"],
        "ponto_morto_fechado": ponto_morto(h),
        "ponto_morto_numerico": ponto_morto_numerico(h),
    }
    assert numeros["residuo_f1"] < 1e-9 and numeros["residuo_f2"] < 1e-9
    assert numeros["tau_mais_F_m"] < 1e-9
    assert numeros["T_duas_vias"] < 1e-9
    assert abs(numeros["ponto_morto_fechado"]
               - numeros["ponto_morto_numerico"]) < 1e-8
    return numeros


def plot_torques(path, h=H_CALIBRADO):
    """Torque do cabo (eixo esquerdo, unidade da curva da patente), torque do
    peso (eixo direito, N·m) e pontos da patente, com os zeros alinhados."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from patent_data import load_patent_data

    patente = load_patent_data()
    cabo = -calculate_torque_curve(K, h, THETA)["tau"]   # convenção da patente
    peso = torque_peso(THETA)

    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=150, facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    ax.plot(patente["theta_star"], patente["torque"], "o", color="#0b0b0b",
            markersize=5, label="Patente, pontos extraídos (eixo esquerdo)")
    ax.plot(THETA, cabo, color="#2a78d6", linewidth=2,
            label=f"Cabo, −τ calculado, H = {h} mm (eixo esquerdo)")
    ax2 = ax.twinx()
    ax2.plot(THETA, peso, color="#eb6834", linewidth=2,
             label="Peso, |τ| (eixo direito)")

    hi1 = 1.08*max(cabo.max(), patente["torque"].max())
    lo1 = min(cabo.min(), 0.0) - 0.04*hi1
    hi2 = 1.15*peso.max()
    ax.set_ylim(lo1, hi1)
    ax2.set_ylim(hi2*lo1/hi1, hi2)            # zeros na mesma altura
    ax.axhline(0, color="#52514e", linewidth=0.8)
    ax.axvline(ponto_morto(h), color="#52514e", linewidth=0.8, linestyle="--")
    ax.annotate(f"ponto morto {ponto_morto(h):.2f}°", (ponto_morto(h), hi1),
                xytext=(-6, -14), textcoords="offset points", ha="right",
                color="#52514e", fontsize=8)

    ax.set_xlabel("θ* (graus)", color="#52514e")
    ax.set_ylabel("Torque do cabo (unidade da curva da patente)",
                  color="#52514e")
    ax2.set_ylabel("Torque do peso (N·m)", color="#52514e")
    ax.set_title("Torque do cabo e do peso em função de θ*", loc="left",
                 color="#0b0b0b", fontsize=12)
    for a in (ax, ax2):
        a.tick_params(colors="#52514e")
        for side in a.spines.values():
            side.set_color("#b9b8b2")
    ax.grid(color="#e6e5e1", linewidth=0.8)
    ax.set_axisbelow(True)
    linhas = ax.get_legend_handles_labels()
    linhas2 = ax2.get_legend_handles_labels()
    ax.legend(linhas[0] + linhas2[0], linhas[1] + linhas2[1], frameon=False,
              fontsize=8, loc="upper left")
    fig.text(0.01, 0.01, "Escalas independentes: a unidade da ordenada da "
             "patente não é declarada, então não há conversão para N·m.",
             fontsize=7.5, color="#52514e")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, facecolor="#fcfcfb")
    plt.close(fig)


if __name__ == "__main__":
    from pathlib import Path

    from patent_data import load_patent_data

    h = H_CALIBRADO
    print(f"Parâmetros congelados: K = {K}, H = {h} mm, L_LIVRE = {L_LIVRE} mm, "
          f"L_POSE = {L_POSE} mm → s_zero = {s_zero(h):.3f} mm")

    # autotestes (sempre impressos)
    a = autotestes(h)
    print("\nAutotestes (força unitária):")
    print(f"  resíduos de fechamento: max|f1| = {a['residuo_f1']:.1e} mm, "
          f"max|f2| = {a['residuo_f2']:.1e} mm")
    print(f"  τ = −F·m:               max|τ·1000 + m| = {a['tau_mais_F_m']:.1e} mm")
    print(f"  ponto de tangência:     direto × (b, β) = {a['T_duas_vias']:.1e} mm")
    print(f"  ponto morto:            forma fechada {a['ponto_morto_fechado']:.4f}°, "
          f"numérico {a['ponto_morto_numerico']:.4f}°")

    # tabela em ângulos representativos
    angulos = np.array([THETA_MIN, 60.0, 90.0, THETA_POSE, 133.58, 160.0,
                        ponto_morto(h), THETA_MAX])
    r = calculate_torque_curve(K, h, angulos)
    peso = torque_peso(angulos)
    print("\n   θ*(°)    φ(°)    q(°)   ρ(mm)   s(mm)   δ(mm)   b(mm)   β(°)"
          "   m(mm)   τ cabo(u.p.)  τ peso(N·m)")
    for i, th in enumerate(angulos):
        print(f"{th:8.3f} {np.degrees(r['phi'][i]):7.2f} "
              f"{np.degrees(r['q'][i]):7.2f} {r['rho'][i]:7.2f} "
              f"{r['s'][i]:7.2f} {r['delta'][i]:7.2f} {r['b'][i]:7.2f} "
              f"{np.degrees(r['beta'][i]):6.3f} {r['m'][i]:7.3f} "
              f"{r['tau'][i]:13.3f} {peso[i]:12.3f}")
    print("u.p. = unidade da curva da patente. τ positivo = anti-horário.")

    # troca de sinal e comparação com a patente
    curva = calculate_torque_curve(K, h, THETA)["tau"]
    positivo = THETA[curva > 0]
    print(f"\nPonto morto: θ* = {ponto_morto(h):.2f}° (φ_pat = "
          f"{ANGLE_OFFSET - ponto_morto(h):.2f}°). Com H do CAD ({H} mm): "
          f"{ponto_morto(H):.2f}° (φ_pat = {ANGLE_OFFSET - ponto_morto(H):.2f}°).")
    if positivo.size:
        print(f"τ do cabo troca de sinal (fica positivo) de θ* = "
              f"{positivo.min():.3f}° a {positivo.max():.3f}°.")
    patente = load_patent_data()
    tau_p = calculate_torque_curve(K, h, patente["theta_star"])["tau"]
    print(f"RMSE de −τ contra a patente: "
          f"{np.sqrt(np.mean((-tau_p - patente['torque'])**2)):.3f} u.p.")

    saida = Path(__file__).parent/"results"/"torque_cabo_peso.png"
    saida.parent.mkdir(exist_ok=True)
    plot_torques(saida, h)
    print(f"Gráfico: {saida}")
