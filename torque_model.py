"""
Modelo de torque do mecanismo cabo + tambor + braço, em função de θ*.

Cadeia de cálculo (cada etapa é uma função abaixo):

    θ*  →  q  →  ρ  →  s  →  φ  →  T (b_vector)  →  V_vector  →  τ
                            └→ caminho = s − R·rel  →  δ  →  f = K·δ
                                      └→ b, β, m (relatório)

Unidades: comprimentos em mm. Ângulos em graus na entrada (ALPHA, THETA, ...)
e em radianos dentro das contas; cada conversão é feita uma única vez.
O torque do cabo sai na unidade da curva extraída da patente (u.p.), porque K
foi calibrado contra ela e a ordenada da patente não tem unidade declarada.
O torque do peso (torque_peso) sai em N·m. Não há conversão entre os dois.

Sinal: τ positivo = anti-horário = sentido de θ* crescente.
Parâmetros K, H_CALIBRADO e X_POSE são congelados: nada é ajustado aqui.
h é argumento obrigatório em toda a cadeia; H_CAD é só valor documental.
"""
import numpy as np

# ---------------------------------------------------------------- geometria
H_CAD = 34.785  # mm, componente h do vetor pivô → ancoragem no CAD. Valor
                # documental: NÃO é o parâmetro do modelo (ver H_CALIBRADO).
P = 3.155    # mm, componente p do vetor fixo pivô → ancoragem
C = 283.438  # mm, braço: pivô → centro do tambor
R = 22.827   # mm, raio do tambor
ALPHA = 20.428  # graus

# ------------------------------------------------------- CAD A CONFIRMAR
# Dois valores conflitam com o CAD usado antes. Nenhum foi escolhido em
# silêncio: os atuais ficam ativos até a confirmação.
L_CARCACA = 131.37  # mm, CAD anterior: 140,0. Não é usado na cadeia.
# Par documental da mola: a curva depende só de X_POSE = L_POSE − L_LIVRE,
# então o conflito 91,35 × 90,13 não muda o ajuste, só a mola a comprar.
# Pares coerentes: (91,35; 53,967) ou (90,13; 52,747).
L_POSE = 91.35      # mm, comprimento da mola na pose THETA_POSE. CAD anterior: 90,13.
L_LIVRE = 53.967    # mm, comprimento livre da mola, coerente com L_POSE = 91,35.

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
K = 174.68          # rigidez da mola: K·δ·m/1000 sai em u.p. (seria N/mm se u.p. = N·m)
H_CALIBRADO = 22.701  # mm, H que reproduz a patente com K e X_POSE
X_POSE = 37.383     # mm, extensão elástica da mola na pose THETA_POSE. É a única
                    # combinação de L_POSE e L_LIVRE que o ajuste identifica.

H = H_CAD  # apelido só para calibration.py e svaj.py (defasados, intocados
           # nesta rodada). Nenhuma função deste arquivo usa H.


# ======================================================================
# 1. Cinemática: θ* → q → ρ → s → φ   (equações de fechamento)
# ======================================================================

def calculate_q(theta_star):
    """q = θ* − π/2 − α  [rad], com θ* em graus."""
    return np.radians(theta_star) - np.pi/2 - np.radians(ALPHA)


def calculate_base_vector(h):
    """B = (h sen α − p cos α,  h cos α + p sen α).

    São os termos constantes de f1 e f2: o vetor fixo pivô → ancoragem.
    """
    a = np.radians(ALPHA)
    return h*np.sin(a) - P*np.cos(a), h*np.cos(a) + P*np.sin(a)


def calculate_rho(q, h):
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


def calculate_phi(q, s, h):
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


def ponto_morto(h):
    """θ* do ponto morto em forma fechada [graus].

    No ponto morto a linha do cabo passa pelo pivô (m = 0, τ = 0):
    θ*_pm = 180 + atan2(P, h) + asen(R/C). Depois dele o torque troca de sinal.
    """
    return 180.0 + np.degrees(np.arctan2(P, h)) + np.degrees(np.arcsin(R/C))


def ponto_morto_numerico(h, tol=1e-10):
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


def calculate_closure_residuals(q, s, phi, h):
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

def calculate_array_vaos_livres(theta, h):
    """Fórmula original (agora com a raiz; antes devolvia s²).

    O termo 2C(...) tem sinal oposto ao das equações de fechamento. Equivale a
    calculate_rho(calculate_q(θ* + 180)), verificado numericamente (diferença
    5,7e-14 mm). Não é a formulação usada: a cadeia usa calculate_rho, que vem
    das equações de fechamento. Mantida apenas como referência histórica.
    """
    t = np.radians(theta)
    return np.sqrt(h**2 + P**2 + C**2 + 2*C*(h*np.cos(t) + P*np.sin(t)))


def angulo_cabo_elo(q, phi):
    """rel: ângulo entre a direção do cabo e a direção do elo (pivô → centro do
    tambor), contínuo em (−π, π]. Vai de −4,656° a 0,019° na faixa de operação."""
    return np.angle(np.exp(1j*(phi - (q + np.pi))))


def comprimento_caminho(q, s, phi):
    """Caminho variável do cabo [mm], a partir das grandezas já obtidas na cadeia:
    vão reto menos o arco enrolado no tambor.

    O sinal vem do trabalho virtual: d(caminho)/dθ* = m só com s − R·rel
    (ver residuo_trabalho_virtual).
    """
    return s - R*angulo_cabo_elo(q, phi)


def caminho_cabo(theta_star, h):
    """Mesmo caminho, a partir de θ*. Usado por s_zero e pelo teste de trabalho
    virtual, que precisam dele fora da cadeia."""
    q = calculate_q(theta_star)
    s = calculate_tangent_span(calculate_rho(q, h))
    return comprimento_caminho(q, s, calculate_phi(q, s, h))


def s_zero(h):
    """Valor do caminho em que a mola atinge o comprimento livre (força nula) [mm]."""
    return caminho_cabo(THETA_POSE, h) - X_POSE


def calculate_delta(caminho, h):
    """δ = extensão elástica da mola [mm]. O cabo traciona, mas não empurra."""
    return np.maximum(caminho - s_zero(h), 0.0)


def ponto_tangencia(q, phi):
    """T: ponto onde o cabo deixa o tambor, em relação ao pivô [mm].

    T = centro da polia + R·(sen φ, −cos φ), com centro da polia = −C·(cos q,
    sen q). Não depende do sinal de β, então continua certo mesmo se o
    roteamento do cabo mudar de lado da polia.
    """
    centro_polia = np.array([-C*np.cos(q), -C*np.sin(q)])
    return centro_polia + R*np.array([np.sin(phi), -np.cos(phi)])


def distancia_ponto_tangencia(s, phi, h):
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


def braco_perpendicular(phi, h):
    """m: braço de momento do cabo, distância perpendicular do pivô à linha
    de ação do cabo [mm], com sinal: m = A_x·sen φ − A_y·cos φ.

    A = vetor base (pivô → ancoragem). A linha de ação passa por A, então
    |m| ≤ |A| = √(h² + P²) (34,93 mm com H_CAD; 22,92 mm com H_CALIBRADO).

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
    configuração calibrada. Não usa K, X_POSE, h nem a cadeia do cabo.
    Inércia (Steiner) não entra: o torque é estático.
    """
    giro = np.radians(np.asarray(theta_star, dtype=float) - THETA_POSE
                      + ALPHA + 90.0 - ANGLE_OFFSET)
    x_cg = CG_DX_MM*np.cos(giro) - CG_DY_MM*np.sin(giro)
    return MASS_KG*GRAVITY*np.abs(x_cg)/1000.0


# ======================================================================
# 4. Cadeia completa
# ======================================================================

def generate_graph_torque_theta_star_relation(force, h, theta=THETA):
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

    # caminho do cabo (vão reto menos arco no tambor) e extensão da mola
    arco = R*angulo_cabo_elo(q, phi)
    caminho = comprimento_caminho(q, s, phi)
    delta = calculate_delta(caminho, h)

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
                arco=arco, caminho=caminho, delta=delta,
                b=b, beta=beta, m=m, force=f,
                b_vector=b_vector, b_vector_beta=b_vector_beta,
                erro_T=erro_T, V_vector=V_vector, tau=tau)


def spring_force(k, delta):
    """Lei da mola do modelo original: f = K·δ, com δ em mm."""
    return k*delta


def calculate_torque_curve(k, h, theta=THETA):
    """Cadeia completa com f = K·δ, para um K e um H dados (τ em u.p.)."""
    geometry = generate_graph_torque_theta_star_relation(0.0, h, theta)
    force = spring_force(k, geometry["delta"])
    return generate_graph_torque_theta_star_relation(force, h, theta)


# ======================================================================
# 5. Autotestes, relatório e gráfico
# ======================================================================

def residuo_trabalho_virtual(h, passo=1e-4):
    """max|d(caminho)/dθ* − m| [mm]. ~0 num mecanismo conservativo."""
    th = np.linspace(THETA_MIN, THETA_MAX, 2001)
    d = (caminho_cabo(th + passo, h) - caminho_cabo(th - passo, h))/np.radians(2*passo)
    q = calculate_q(th)
    s = calculate_tangent_span(calculate_rho(q, h))
    return np.max(np.abs(d - braco_perpendicular(calculate_phi(q, s, h), h)))


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
        "trabalho_virtual": residuo_trabalho_virtual(h),
        "par_mola": abs((L_POSE - L_LIVRE) - X_POSE),
    }
    assert numeros["residuo_f1"] < 1e-9 and numeros["residuo_f2"] < 1e-9
    assert numeros["tau_mais_F_m"] < 1e-9
    assert numeros["T_duas_vias"] < 1e-9
    assert abs(numeros["ponto_morto_fechado"]
               - numeros["ponto_morto_numerico"]) < 1e-8
    assert numeros["trabalho_virtual"] < 1e-3
    assert numeros["par_mola"] < 1e-9
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
    print(f"Parâmetros congelados: K = {K}, H = {h} mm, X_POSE = {X_POSE} mm "
          f"→ s_zero = {s_zero(h):.4f} mm (caminho na pose "
          f"{caminho_cabo(THETA_POSE, h):.4f} mm)")

    # autotestes (sempre impressos)
    a = autotestes(h)
    print("\nAutotestes (força unitária):")
    print(f"  resíduos de fechamento: max|f1| = {a['residuo_f1']:.1e} mm, "
          f"max|f2| = {a['residuo_f2']:.1e} mm")
    print(f"  τ = −F·m:               max|τ·1000 + m| = {a['tau_mais_F_m']:.1e} mm")
    print(f"  ponto de tangência:     direto × (b, β) = {a['T_duas_vias']:.1e} mm")
    print(f"  ponto morto:            forma fechada {a['ponto_morto_fechado']:.4f}°, "
          f"numérico {a['ponto_morto_numerico']:.4f}°")
    print(f"  trabalho virtual:       max|d(caminho)/dθ* − m| = {a['trabalho_virtual']:.1e} mm")
    print(f"  par da mola:            |(L_POSE − L_LIVRE) − X_POSE| = {a['par_mola']:.1e} mm")

    # tabela em ângulos representativos
    angulos = np.array([THETA_MIN, 60.0, 90.0, THETA_POSE, 133.58, 160.0,
                        ponto_morto(h), THETA_MAX])
    r = calculate_torque_curve(K, h, angulos)
    peso = torque_peso(angulos)
    print("\n   θ*(°)    φ(°)    q(°)   ρ(mm)   s(mm) arco(mm) caminho   δ(mm)"
          "   b(mm)   β(°)   m(mm)   τ cabo(u.p.)  τ peso(N·m)")
    for i, th in enumerate(angulos):
        print(f"{th:8.3f} {np.degrees(r['phi'][i]):7.2f} "
              f"{np.degrees(r['q'][i]):7.2f} {r['rho'][i]:7.2f} "
              f"{r['s'][i]:7.2f} {r['arco'][i]:8.3f} {r['caminho'][i]:7.2f} "
              f"{r['delta'][i]:7.2f} {r['b'][i]:7.2f} "
              f"{np.degrees(r['beta'][i]):6.3f} {r['m'][i]:7.3f} "
              f"{r['tau'][i]:13.3f} {peso[i]:12.3f}")
    print("u.p. = unidade da curva da patente. τ positivo = anti-horário.")

    # troca de sinal e comparação com a patente
    curva = calculate_torque_curve(K, h, THETA)["tau"]
    positivo = THETA[curva > 0]
    print(f"\nPonto morto: θ* = {ponto_morto(h):.2f}° (φ_pat = "
          f"{ANGLE_OFFSET - ponto_morto(h):.3f}°). Com H_CAD ({H_CAD} mm): "
          f"{ponto_morto(H_CAD):.2f}° (φ_pat = {ANGLE_OFFSET - ponto_morto(H_CAD):.2f}°).")
    if positivo.size:
        print(f"τ do cabo troca de sinal (fica positivo) de θ* = "
              f"{positivo.min():.3f}° a {positivo.max():.3f}°.")
    patente = load_patent_data()
    tau_p = calculate_torque_curve(K, h, patente["theta_star"])["tau"]
    print(f"RMSE de −τ contra a patente: "
          f"{np.sqrt(np.mean((-tau_p - patente['torque'])**2)):.3f} u.p.; pico nos "
          f"pontos da patente {np.max(-tau_p):.3f} (alvo "
          f"{patente['torque'].max():.3f}), na grade THETA {np.max(-curva):.3f}")

    saida = Path(__file__).parent/"results"/"torque_cabo_peso.png"
    saida.parent.mkdir(exist_ok=True)
    plot_torques(saida, h)
    print(f"Gráfico: {saida}")


# ==========================================================================
# PASSADA ADICIONAL - VARREDURA PARAMÉTRICA DE h  (diagnóstico)
# Nada acima desta linha foi alterado.
# ==========================================================================
#
# Regras desta seção: nenhum nome global existente é religado; toda conta
# vive dentro de funções; h é passado explicitamente em toda chamada; nada
# aqui substitui K, H_CALIBRADO ou X_POSE. Globais novos: só as funções vh_* e
# varredura_h, e as constantes VH_*.
#
# Viabilidade = (a) tração + (c) fechamento + (d) trabalho virtual
# (VH_CRITERIOS). O ENROLAMENTO NÃO É CRITÉRIO: rel = 0 em angulo_cabo_elo
# significa arco de enrolamento nulo, não cabo fora da polia. Quem garante o
# cabo no tambor é a tangência, o critério (c) ρ > R. Usar a troca de sinal de
# rel como critério reprovava o próprio H_CALIBRADO (arco de micrômetros). Não
# reintroduzir; o enrolamento continua só como diagnóstico.

VH_CRITERIOS = ("tracao", "fechamento", "tv_ok")
VH_FOLGAS = (1.01, 1.05, 1.10, 2.00)
VH_FOLGA_REFERENCIA = 1.05


def vh_trapezio(y, x):
    """Integral pela regra do trapézio (sem depender da versão do NumPy)."""
    return float(np.sum(0.5*(y[1:] + y[:-1])*np.diff(x)))


def vh_zonas_de_sinal(residuo):
    """Número de trechos de sinal constante do resíduo, ignorando zeros exatos."""
    sinais = np.sign(residuo[residuo != 0])
    return int(1 + np.count_nonzero(np.diff(sinais))) if sinais.size else 0


def vh_cruzamentos(theta, d):
    """θ* onde d troca de sinal, por interpolação linear entre nós."""
    saida = list(theta[d == 0])
    i = np.where(d[:-1]*d[1:] < 0)[0]
    saida += list(theta[i] - d[i]*(theta[i + 1] - theta[i])/(d[i + 1] - d[i]))
    return sorted(float(t) for t in saida)


def vh_h_de_theta_dc(theta_dc):
    """Inversão analítica de θ*_pm(h) = 180 + atan2(P, h) + asen(R/C)."""
    return P/np.tan(np.radians(theta_dc - 180.0 - np.degrees(np.arcsin(R/C))))


def vh_bissecao_theta_dc(theta_alvo, h_a=1e-3, h_b=1e3, tol=1e-13):
    """Raiz de ponto_morto(h) − θ_alvo por bissecção própria, ou None se o
    intervalo não tiver troca de sinal (o alvo não é atingível)."""
    fa = ponto_morto(h_a) - theta_alvo
    fb = ponto_morto(h_b) - theta_alvo
    if np.sign(fa) == np.sign(fb):
        return None
    while h_b - h_a > tol:
        meio = 0.5*(h_a + h_b)
        fm = ponto_morto(meio) - theta_alvo
        if np.sign(fm) == np.sign(fa):
            h_a, fa = meio, fm
        else:
            h_b = meio
    return 0.5*(h_a + h_b)


def vh_avaliar_h(h, theta, patente, peso, tol_tv):
    """Validade (a), (c), (d), diagnóstico de enrolamento e métricas de um h.

    Nada é saturado nem corrigido. Torque do cabo na convenção da patente
    (−τ do modelo), K congelado.
    """
    linha = {"h": float(h), "motivo": "", "viavel": False}
    q = calculate_q(theta)
    rho = calculate_rho(q, h)
    linha["fechamento"] = bool(np.all(rho > R))
    if not linha["fechamento"]:
        linha["motivo"] = "fechamento: ρ ≤ R em parte da faixa"
        return linha
    try:
        s = calculate_tangent_span(rho)
        phi = calculate_phi(q, s, h)
        rel = angulo_cabo_elo(q, phi)
        extensao = comprimento_caminho(q, s, phi) - s_zero(h)   # sem saturação
        cabo = -calculate_torque_curve(K, h, theta)["tau"]
        g_theta = -calculate_torque_curve(1.0, h, theta)["tau"]
        cabo_pat = -calculate_torque_curve(K, h, patente["theta_star"])["tau"]
        g = -calculate_torque_curve(1.0, h, patente["theta_star"])["tau"]
        tv = residuo_trabalho_virtual(h)
    except (ValueError, AssertionError) as erro:
        linha["fechamento"] = False
        linha["motivo"] = f"fechamento: {erro}"
        return linha

    # τ é linear em K (δ não depende de K): τ(K) = K·g com g = τ(h, K = 1)
    erro_linear = float(max(np.max(np.abs(cabo - K*g_theta)),
                            np.max(np.abs(cabo_pat - K*g))))
    assert erro_linear < 1e-9, f"τ não é linear em K: {erro_linear:.1e}"

    i_min = int(np.argmin(extensao))
    linha.update(
        tracao=bool(np.all(extensao >= 0)),
        trabalho_virtual=float(tv),
        tv_ok=bool(tv < tol_tv),
        delta_min=float(extensao[i_min]),
        theta_delta_min=float(theta[i_min]),
        delta_max=float(extensao.max()),
        mola_max=float(L_LIVRE + extensao.max()),
        rel_min_grau=float(np.degrees(rel.min())),
        rel_max_grau=float(np.degrees(rel.max())),
        enrol_troca=bool(rel.min() < 0 < rel.max()),
        arco_pos_max=max(0.0, float(R*rel.max())),
        erro_linear_K=erro_linear,
    )
    linha["viavel"] = all(linha[c] for c in VH_CRITERIOS)
    linha["motivo"] = ", ".join(c for c in VH_CRITERIOS if not linha[c])

    residuo = cabo_pat - patente["torque"]
    k_estrela = float((g @ patente["torque"])/(g @ g))   # forma fechada
    linha.update(
        rmse=float(np.sqrt(np.mean(residuo**2))),
        k_estrela=k_estrela,
        rmse_k_estrela=float(np.sqrt(np.mean((k_estrela*g
                                               - patente["torque"])**2))),
        tau_max=float(cabo.max()),
        deficit_max=float(np.max(peso - cabo)),
    )
    return linha


def vh_valores_notaveis(h, theta, patente, peso, tol_tv):
    """Valores notáveis da curva torque × θ* de um h. Sem fechamento, devolve
    só a avaliação básica (com o motivo)."""
    v = vh_avaliar_h(h, theta, patente, peso, tol_tv)
    if not v["fechamento"]:
        return v
    q = calculate_q(theta)
    s = calculate_tangent_span(calculate_rho(q, h))
    m = braco_perpendicular(calculate_phi(q, s, h), h)
    cabo = -calculate_torque_curve(K, h, theta)["tau"]
    pontos = np.array([THETA_MIN, THETA_POSE, THETA_MAX])
    cabo_pontos = -calculate_torque_curve(K, h, pontos)["tau"]
    passo = 1e-4
    lados = -calculate_torque_curve(
        K, h, np.array([THETA_POSE - passo, THETA_POSE + passo]))["tau"]
    dif = cabo - peso
    residuo = (-calculate_torque_curve(K, h, patente["theta_star"])["tau"]
               - patente["torque"])
    integral_cabo = vh_trapezio(cabo, np.radians(theta))
    integral_peso = vh_trapezio(peso, np.radians(theta))
    v.update(
        theta_dc=float(ponto_morto(h)),
        theta_dc_na_faixa=bool(THETA_MIN - 1e-9 <= ponto_morto(h)
                               <= THETA_MAX + 1e-9),
        s_zero=float(s_zero(h)),
        braco_max=float(m.max()), theta_braco_max=float(theta[np.argmax(m)]),
        theta_tau_max=float(theta[np.argmax(cabo)]),
        tau_theta_min=float(cabo_pontos[0]),
        tau_pose=float(cabo_pontos[1]),
        tau_theta_max=float(cabo_pontos[2]),
        dtau_dtheta_pose=float((lados[1] - lados[0])/np.radians(2*passo)),
        dif_min=float(dif.min()), theta_dif_min=float(theta[np.argmin(dif)]),
        dif_max=float(dif.max()), theta_dif_max=float(theta[np.argmax(dif)]),
        cruzamentos=vh_cruzamentos(theta, dif),
        integral_cabo=integral_cabo, integral_peso=integral_peso,
        razao_integrais=integral_cabo/integral_peso,
        residuo_max_abs=float(np.max(np.abs(residuo))),
        residuo_medio=float(np.mean(residuo)),
        zonas_de_sinal=vh_zonas_de_sinal(residuo),
    )
    return v


def vh_faixa(linhas, chave):
    """Menor e maior h com linhas[chave] verdadeiro, quantos são e se o
    conjunto é contíguo na grade (linhas ordenadas por h)."""
    hs = np.array([l["h"] for l in linhas])
    ok = np.array([bool(l.get(chave, False)) for l in linhas])
    if not ok.any():
        return None
    indices = np.flatnonzero(ok)
    primeiro, ultimo = int(indices[0]), int(indices[-1])
    return {"min": float(hs[primeiro]), "max": float(hs[ultimo]),
            "n": int(ok.sum()),
            "contigua": bool(ok[primeiro:ultimo + 1].all()),
            "borda_min": primeiro == 0, "borda_max": ultimo == len(ok) - 1}


def vh_plato(linhas, chave_rmse, folga):
    """h com chave_rmse ≤ folga·mínimo (entre os h com fechamento)."""
    minimo = min(l[chave_rmse] for l in linhas if l["fechamento"])
    marcas = [{"h": l["h"], "ok": bool(l["fechamento"]
                                       and l[chave_rmse] <= folga*minimo)}
              for l in linhas]
    faixa = vh_faixa(marcas, "ok")
    faixa.update(folga=folga, minimo=minimo,
                 largura=faixa["max"] - faixa["min"])
    return faixa


def vh_degradacao(linhas, chave_rmse, fatores=(2.0, 10.0)):
    """A partir do h de menor erro, o primeiro h de cada lado em que o erro
    passa de fator × mínimo (None se não passa dentro da grade)."""
    calc = [l for l in linhas if l["fechamento"]]
    i0 = min(range(len(calc)), key=lambda i: calc[i][chave_rmse])
    minimo = calc[i0][chave_rmse]
    saida = {}
    for fator in fatores:
        limite = fator*minimo
        esq = next((calc[i]["h"] for i in range(i0, -1, -1)
                    if calc[i][chave_rmse] > limite), None)
        dir_ = next((calc[i]["h"] for i in range(i0, len(calc))
                     if calc[i][chave_rmse] > limite), None)
        saida[fator] = {"esq": esq, "dir": dir_}
    return {"h_min": calc[i0]["h"], "minimo": minimo, "fatores": saida}


def vh_salvar_csv(caminho, linhas, colunas, colunas_texto=("papeis", "motivo")):
    """CSV para Excel pt-BR: separador ';', decimal vírgula, sim/nao."""
    texto = [";".join(colunas)]
    for l in linhas:
        celulas = []
        for c in colunas:
            valor = l.get(c, "")
            if c in colunas_texto:
                celula = str(valor)
            elif isinstance(valor, (bool, np.bool_)):
                celula = "sim" if valor else "nao"
            elif isinstance(valor, (list, tuple)):
                celula = " ".join(f"{x:.4f}".replace(".", ",") for x in valor)
            elif isinstance(valor, (float, np.floating)):
                celula = f"{valor:.6g}".replace(".", ",")
            else:
                celula = str(valor)
            celulas.append(celula)
        texto.append(";".join(celulas))
    caminho.write_text("\n".join(texto) + "\n", encoding="utf-8")


def vh_formatador_virgula(casas):
    from matplotlib.ticker import FuncFormatter
    return FuncFormatter(lambda x, pos: f"{x:.{casas}f}".replace(".", ","))


def vh_plot_perfil_rmse(linhas, notaveis, faixas, caminho_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ok = [l for l in linhas if l["fechamento"]]
    hs = np.array([l["h"] for l in ok])
    fig, ax = plt.subplots(figsize=(9.5, 5), dpi=200, facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    viaveis = faixas.get("viavel")
    if viaveis:
        ax.axvspan(viaveis["min"], viaveis["max"], color="#1baf7a", alpha=0.12,
                   label="h viáveis: (a), (c), (d)")
    ax.plot(hs, [l["rmse"] for l in ok], color="#2a78d6", linewidth=2,
            label="RMSE(h), K congelado")
    ax.plot(hs, [l["rmse_k_estrela"] for l in ok], color="#eb6834",
            linewidth=2, label="RMSE*(h), K reidentificado (perfil)")
    for nome, h in notaveis:
        ax.axvline(h, color="#52514e", linewidth=0.7, linestyle=":")
    ax.plot([], [], color="#52514e", linewidth=0.7, linestyle=":",
            label="h notáveis")
    ax.set_yscale("log")
    ax.set_xlabel("h (mm)")
    ax.set_ylabel("RMSE (unidade da curva extraída), escala log")
    ax.xaxis.set_major_formatter(vh_formatador_virgula(0))
    ax.grid(color="#e6e5e1", linewidth=0.8, which="both")
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False,
              fontsize=8)
    fig.tight_layout()
    fig.savefig(caminho_png, facecolor="#fcfcfb")
    plt.close(fig)


def vh_plot_curvas_notaveis(notaveis, theta, patente, peso, caminho_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cores = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4",
             "#008300", "#4a3aa7", "#e34948"]
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=200, facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    ax.axhline(0, color="#52514e", linewidth=0.8)
    ax.plot(patente["theta_star"], patente["torque"], "o", color="#0b0b0b",
            markersize=4, label="Extração da patente (cabo)")
    for i, (nome, h) in enumerate(notaveis):
        cabo = -calculate_torque_curve(K, h, theta)["tau"]
        papel = nome.split("+")[0].split(" [")[0]
        if "+" in nome:
            papel += " e outros"
        ax.plot(theta, cabo, color=cores[i % len(cores)], linewidth=1.6,
                linestyle="-" if i < len(cores) else "--",
                label=f"h = {h:.3f} mm ({papel})".replace(".", ","))
    ax2 = ax.twinx()
    ax2.plot(theta, peso, color="#7a7974", linewidth=1.4, linestyle="--",
             label="Peso (N·m, eixo direito)")
    baixo, alto = ax.get_ylim()
    ax2.set_ylim(ax2.get_ylim()[1]*baixo/alto, ax2.get_ylim()[1])  # zeros alinhados
    ax.set_xlabel("θ* (graus)")
    ax.set_ylabel("Torque do cabo (unidade da curva extraída)")
    ax2.set_ylabel("Torque do peso (N·m)")
    for eixo, casas in ((ax.xaxis, 0), (ax.yaxis, 0), (ax2.yaxis, 1)):
        eixo.set_major_formatter(vh_formatador_virgula(casas))
    ax.grid(color="#e6e5e1", linewidth=0.8)
    ax.set_axisbelow(True)
    linhas_a, nomes_a = ax.get_legend_handles_labels()
    linhas_b, nomes_b = ax2.get_legend_handles_labels()
    ax.legend(linhas_a + linhas_b, nomes_a + nomes_b, loc="upper left",
              bbox_to_anchor=(1.14, 1.0), frameon=False, fontsize=7)
    fig.subplots_adjust(left=0.08, right=0.60, bottom=0.11, top=0.95)
    fig.savefig(caminho_png, facecolor="#fcfcfb")
    plt.close(fig)


def varredura_h(plot_perfil=None, plot_curvas=None):
    """Varre h, classifica validade física e reporta os h notáveis.

    Diagnóstico: não altera K, H_CALIBRADO nem X_POSE. Devolve um dicionário
    com as linhas da varredura, as faixas e os valores notáveis.
    """
    from pathlib import Path

    from patent_data import load_patent_data

    VH_GRID = np.arange(8.0, 60.0 + 1e-9, 0.05)            # mm, h VARRIDO
    VH_THETA = np.linspace(THETA_MIN, THETA_MAX, 1501)      # graus
    VH_TOL_TV = 1e-6                                        # mm/rad
    if plot_perfil is None:
        plot_perfil = VH_PLOT_PERFIL_RMSE
    if plot_curvas is None:
        plot_curvas = VH_PLOT_CURVAS_NOTAVEIS

    patente = load_patent_data()
    peso = torque_peso(VH_THETA)

    # guarda do h implícito: dois h distintos têm de dar curvas distintas
    curva_a = calculate_torque_curve(K, 15.0, VH_THETA)["tau"]
    curva_b = calculate_torque_curve(K, 30.0, VH_THETA)["tau"]
    if np.array_equal(curva_a, curva_b):
        raise RuntimeError("h não está chegando à cadeia: curvas iguais para "
                           "h = 15 e h = 30. Varredura abortada.")

    grade = np.unique(np.concatenate([VH_GRID, [H_CALIBRADO, H_CAD]]))
    linhas = [vh_avaliar_h(h, VH_THETA, patente, peso, VH_TOL_TV)
              for h in grade]
    linha_de = {round(l["h"], 9): l for l in linhas}

    # ancoragem: extensão na pose = X_POSE para todo h
    erro_ancora = max(abs(caminho_cabo(THETA_POSE, h) - s_zero(h) - X_POSE)
                      for h in grade)
    assert erro_ancora < 1e-9, f"ancoragem violada: {erro_ancora:.1e} mm"

    # reprodução exata do RMSE do modelo congelado
    tau_congelado = calculate_torque_curve(K, H_CALIBRADO,
                                           patente["theta_star"])["tau"]
    rmse_congelado = np.sqrt(np.mean((-tau_congelado - patente["torque"])**2))
    linha_cal = linha_de[round(H_CALIBRADO, 9)]
    assert linha_cal["rmse"] == rmse_congelado

    calculaveis = [l for l in linhas if l["fechamento"]]
    viaveis = [l for l in calculaveis if l["viavel"]]
    for posto, l in enumerate(sorted(calculaveis, key=lambda l: l["rmse"]),
                              start=1):
        l["posto_rmse"] = posto
    n_calc = len(calculaveis)
    faixas = {nome: vh_faixa(linhas, nome)
              for nome in ("tracao", "tv_ok", "viavel")}

    def contexto(linha):
        marcas = []
        if linha["h"] in (grade[0], grade[-1]):
            marcas.append("[borda da grade]")
        if faixas["viavel"] and linha["h"] in (faixas["viavel"]["min"],
                                                faixas["viavel"]["max"]):
            marcas.append("[borda da faixa viável]")
        return (" " + " ".join(marcas)) if marcas else ""

    # grupo A
    otimo = min(calculaveis, key=lambda l: l["rmse"])
    otimo_viavel = min(viaveis, key=lambda l: l["rmse"]) if viaveis else None
    pior = max(viaveis, key=lambda l: l["rmse"]) if viaveis else None
    platos = {f: vh_plato(linhas, "rmse", f) for f in VH_FOLGAS}
    degr = vh_degradacao(linhas, "rmse")
    # grupo B
    otimo_k = min(calculaveis, key=lambda l: l["rmse_k_estrela"])
    platos_k = {f: vh_plato(linhas, "rmse_k_estrela", f) for f in VH_FOLGAS}
    degr_k = vh_degradacao(linhas, "rmse_k_estrela")
    plato_ref = platos[VH_FOLGA_REFERENCIA]
    # grupo D
    h_dc_entra = float(vh_h_de_theta_dc(THETA_MAX))
    h_dc_entra_bis = vh_bissecao_theta_dc(THETA_MAX)
    assert abs(h_dc_entra - h_dc_entra_bis) < 1e-12
    h_dc_sai_formula = float(vh_h_de_theta_dc(THETA_MIN))
    h_dc_sai_bis = vh_bissecao_theta_dc(THETA_MIN)
    # grupo F (descritivo, só entre viáveis)
    h_tau_max = max(viaveis, key=lambda l: l["tau_max"]) if viaveis else None
    h_deficit = min(viaveis, key=lambda l: l["deficit_max"]) if viaveis else None

    # ---------------------------------------------------------- relatório
    print("\n" + "=" * 78)
    print("PASSADA ADICIONAL - VARREDURA PARAMÉTRICA DE h (diagnóstico)")
    print("=" * 78)
    print("Critério de ótimo: menor RMSE contra a curva extraída da patente, que")
    print("representa EXCLUSIVAMENTE o torque do cabo. A gravidade não entra no")
    print("critério, na normalização nem na ponderação.")
    print("h_otimo é ACHADO DIAGNÓSTICO, não adoção. O modelo congelado continua")
    print(f"com H_CALIBRADO = {H_CALIBRADO}; esta seção não religa H_CALIBRADO nem K.")
    print("\nUNIDADES: a ordenada da curva extraída não tem unidade declarada. A")
    print("unidade do torque do cabo é herdada de K, identificado contra essa")
    print("curva sem unidade; 'N·m' só vale se K estiver em N/mm. O torque do")
    print("peso está em N·m por construção. Não há conversão nem reescala; as")
    print("diferenças cabo − peso abaixo só têm sentido físico se K estiver em N/mm.")
    print(f"\nAncoragem: s_zero(h) = caminho_cabo(THETA_POSE, h) − X_POSE, "
          f"extensão na pose fixa em X_POSE = {X_POSE} mm para todo h "
          f"(escolha de modelagem; erro máx. {erro_ancora:.1e} mm).")
    print(f"Classificação: h VARRIDO ({grade.size} valores, 8,00 a 60,00 mm em "
          f"0,05 mm + {H_CALIBRADO} e {H_CAD} exatos); h_otimo, h_pior e "
          f"demais h notáveis DERIVADOS (diagnóstico).")
    print(f"Viabilidade = {' + '.join(VH_CRITERIOS)} (critérios (a), (c), (d)). "
          f"Enrolamento só como diagnóstico.")
    print(f"Guarda do h implícito: curvas com h = 15 e h = 30 diferem "
          f"(máx. {np.max(np.abs(curva_a - curva_b)):.3f} u.p.). OK.")
    print(f"Linearidade em K: max|τ(K) − K·g| na grade = "
          f"{max(l['erro_linear_K'] for l in calculaveis):.1e} (< 1e-9), o que "
          f"justifica o K* em forma fechada.")
    print(f"RMSE em H_CALIBRADO pela varredura = {linha_cal['rmse']:.6f} "
          f"(modelo congelado: {rmse_congelado:.6f}, idêntico).")

    print(f"\nGrupo A - concordância com a extração (K congelado em {K}):")
    print(f"  h_otimo        = {otimo['h']:.3f} mm{contexto(otimo)}  RMSE "
          f"{otimo['rmse']:.4f}  viável: {otimo['viavel']}"
          + (f" (falha: {otimo['motivo']})" if not otimo["viavel"] else ""))
    if viaveis:
        coincide = otimo_viavel["h"] == otimo["h"]
        print(f"  h_otimo_viavel = {otimo_viavel['h']:.3f} mm"
              f"{contexto(otimo_viavel)}  RMSE {otimo_viavel['rmse']:.4f}  "
              + ("(coincide com h_otimo)" if coincide
                 else "(DIFERE de h_otimo: o mínimo irrestrito não é viável)"))
        print(f"  h_pior         = {pior['h']:.3f} mm{contexto(pior)}  RMSE "
              f"{pior['rmse']:.4f} (entre os viáveis)")
        if contexto(pior):
            print("    ↳ h_pior cai numa borda: ali o 'pior' mede o intervalo "
                  "varrido, não o mecanismo. Ver a degradação abaixo.")
    else:
        print("  nenhum h viável: h_otimo_viavel e h_pior não existem")
    for f in VH_FOLGAS:
        p = platos[f]
        print(f"  platô RMSE ≤ {f:.2f}·mín: h de {p['min']:.3f} a {p['max']:.3f} "
              f"mm, largura {p['largura']:.3f} mm, {p['n']} h"
              f"{'' if p['contigua'] else ', NÃO contíguo'}"
              f"{' (encosta na borda da grade)' if p['borda_min'] or p['borda_max'] else ''}"
              f"{'   ← referência' if f == VH_FOLGA_REFERENCIA else ''}")
    for fator, lados in degr["fatores"].items():
        esq = "não atinge na grade" if lados["esq"] is None else f"{lados['esq']:.3f} mm"
        dir_ = "não atinge na grade" if lados["dir"] is None else f"{lados['dir']:.3f} mm"
        print(f"  degradação RMSE > {fator:g}×mín a partir de h = "
              f"{degr['h_min']:.3f}: esquerda {esq}, direita {dir_}")

    print("\nPERFIL DE IDENTIFICABILIDADE - não altera parâmetros congelados")
    print("  (K reidentificado por h, mínimos quadrados lineares em forma fechada)")
    print(f"  h_otimo_K = {otimo_k['h']:.3f} mm{contexto(otimo_k)}, K*(h_otimo_K) "
          f"= {otimo_k['k_estrela']:.3f}, RMSE* = {otimo_k['rmse_k_estrela']:.4f}")
    for nome in ("min", "max"):
        l = linha_de[round(plato_ref[nome], 9)]
        print(f"  borda {nome} do platô RMSE ({VH_FOLGA_REFERENCIA:.2f}, h = "
              f"{l['h']:.3f}): K*/{K} = {l['k_estrela']/K:.4f}")
    for f in VH_FOLGAS:
        p = platos_k[f]
        print(f"  platô RMSE* ≤ {f:.2f}·mín: h de {p['min']:.3f} a {p['max']:.3f} "
              f"mm, largura {p['largura']:.3f} mm, {p['n']} h"
              f"{'' if p['contigua'] else ', NÃO contíguo'}"
              f"{' (encosta na borda da grade)' if p['borda_min'] or p['borda_max'] else ''}")
    for fator, lados in degr_k["fatores"].items():
        esq = "não atinge na grade" if lados["esq"] is None else f"{lados['esq']:.3f} mm"
        dir_ = "não atinge na grade" if lados["dir"] is None else f"{lados['dir']:.3f} mm"
        print(f"  degradação RMSE* > {fator:g}×mín a partir de h = "
              f"{degr_k['h_min']:.3f}: esquerda {esq}, direita {dir_}")

    print("\nGrupo C - fronteiras de validade física (na grade):")
    rotulos = {"tracao": "(a) tração", "tv_ok": "(d) trabalho virtual",
               "viavel": "viável (a), (c), (d)"}
    for nome, rotulo in rotulos.items():
        f = faixas[nome]
        if f is None:
            print(f"  {rotulo:22s} nenhum h atende")
            continue
        print(f"  {rotulo:22s} h de {f['min']:.3f}"
              f"{' (borda da grade)' if f['borda_min'] else ''} a "
              f"{f['max']:.3f}{' (borda da grade)' if f['borda_max'] else ''}"
              f", {f['n']} h{'' if f['contigua'] else ', NÃO contíguo'}")
    print(f"  (c) fechamento         {sum(l['fechamento'] for l in linhas)} de "
          f"{len(linhas)} h com solução real em toda a faixa")
    if faixas["viavel"]:
        for lado, borda in (("inferior", "min"), ("superior", "max")):
            if faixas["viavel"][f"borda_{borda}"]:
                print(f"  limite {lado} da faixa viável: borda da grade")
                continue
            vizinho = linhas[[l["h"] for l in linhas].index(faixas["viavel"][borda])
                             + (1 if borda == "max" else -1)]
            print(f"  limite {lado} da faixa viável: imposto por "
                  f"{vizinho['motivo']} (primeiro h fora: {vizinho['h']:.3f} mm)")
    tv_max = max(l["trabalho_virtual"] for l in calculaveis)
    print(f"  trabalho virtual máximo na grade: {tv_max:.1e} mm/rad")

    troca = [l for l in calculaveis if l["enrol_troca"]]
    arco_max = max(calculaveis, key=lambda l: l["arco_pos_max"])
    print("\n  Enrolamento - DIAGNÓSTICO, não critério de validade")
    if troca:
        primeiro = min(l["h"] for l in troca)
        seguidos = all(l["enrol_troca"] for l in calculaveis
                       if l["h"] >= primeiro)
        print(f"    rel troca de sinal em {len(troca)} de {n_calc} h, a partir "
              f"de h = {primeiro:.3f} mm"
              f"{' (e em todos os h acima)' if seguidos else ' (não contíguo)'}")
    else:
        print("    rel não troca de sinal em nenhum h da grade")
    print(f"    maior arco positivo R·rel: {arco_max['arco_pos_max']*1000:.2f} µm "
          f"em h = {arco_max['h']:.3f} mm")
    print("    rel = 0 é arco de enrolamento nulo, não cabo fora da polia; quem")
    print("    garante o cabo no tambor é a tangência, o critério (c) ρ > R.")

    print("\nGrupo D - marcos de mecanismo (forma fechada):")
    print(f"  h_dc_entra = {h_dc_entra:.12f} mm (θ*_pm cruza THETA_MAX = "
          f"{THETA_MAX:.3f}°); bissecção {h_dc_entra_bis:.12f}, diferença "
          f"{abs(h_dc_entra - h_dc_entra_bis):.1e}")
    print(f"  h_dc_sai: NÃO EXISTE. Para h > 0, θ*_pm fica entre "
          f"{180 + np.degrees(np.arcsin(R/C)):.3f}° e "
          f"{270 + np.degrees(np.arcsin(R/C)):.3f}° e nunca chega a THETA_MIN = "
          f"{THETA_MIN:.3f}°. A inversão por tangente devolve h = "
          f"{h_dc_sai_formula:.4f} mm, ramo espúrio: θ*_pm({h_dc_sai_formula:.4f})"
          f" = {ponto_morto(h_dc_sai_formula):.3f}°. Bissecção: "
          f"{'sem troca de sinal' if h_dc_sai_bis is None else h_dc_sai_bis}.")

    print("\nGrupo E - referências, não ótimos:")
    for nome, h in (("H_CALIBRADO", H_CALIBRADO), ("H_CAD", H_CAD)):
        l = linha_de[round(h, 9)]
        print(f"  {nome:12s} = {h:.3f} mm  RMSE {l['rmse']:.4f}  posto "
              f"{l['posto_rmse']} de {n_calc} (percentil "
              f"{100*l['posto_rmse']/n_calc:.1f}%)  viável: {l['viavel']}"
              + (f" (falha: {l['motivo']})" if not l["viavel"] else ""))
    l_cad = linha_de[round(H_CAD, 9)]
    if not l_cad["tracao"]:
        print(f"    ↳ H_CAD falha a tração: δ_min = {l_cad['delta_min']:.3f} mm em "
              f"θ* = {l_cad['theta_delta_min']:.2f}°. Com a ancoragem por X_POSE, "
              f"no h documental o cabo afrouxaria dentro da faixa de operação.")
    print(f"  delta = h_otimo − H_CALIBRADO = {otimo['h'] - H_CALIBRADO:+.3f} mm")

    print("\nDESCRITIVO - a gravidade não define otimalidade neste trabalho")
    if viaveis:
        print(f"  h que maximiza τ_max (entre viáveis): {h_tau_max['h']:.3f} mm"
              f"{contexto(h_tau_max)}, τ_max = {h_tau_max['tau_max']:.3f}")
        print(f"  h que minimiza o pior déficit max(τ_peso − τ_cabo) (entre "
              f"viáveis): {h_deficit['h']:.3f} mm{contexto(h_deficit)}, déficit = "
              f"{h_deficit['deficit_max']:.3f} (negativo = cabo acima do peso "
              f"em toda a faixa)")

    # ------------------------------------------------- valores notáveis
    papeis = [("h_otimo", otimo["h"]), ("h_otimo_K", otimo_k["h"]),
              ("h_plato_min", plato_ref["min"]), ("h_plato_max", plato_ref["max"]),
              ("h_dc_entra", h_dc_entra), ("H_CALIBRADO", H_CALIBRADO),
              ("H_CAD", H_CAD)]
    if viaveis:
        papeis += [("h_otimo_viavel", otimo_viavel["h"]), ("h_pior", pior["h"]),
                   ("h_tau_max", h_tau_max["h"]),
                   ("h_min_deficit", h_deficit["h"])]
    for nome in ("tracao", "viavel"):
        if faixas[nome]:
            papeis += [(f"h_{nome}_min", faixas[nome]["min"]),
                       (f"h_{nome}_max", faixas[nome]["max"])]
    for fator, lados in degr["fatores"].items():
        for lado in ("esq", "dir"):
            if lados[lado] is not None:
                papeis.append((f"h_rmse_{fator:g}x_{lado}", lados[lado]))
    agrupados, valor_exato = {}, {}
    for nome, h in papeis:
        chave = round(float(h), 9)
        agrupados.setdefault(chave, []).append(nome)
        valor_exato.setdefault(chave, float(h))
    notaveis, sem_fechamento = [], []
    for chave in sorted(agrupados):
        v = vh_valores_notaveis(valor_exato[chave], VH_THETA, patente, peso,
                                VH_TOL_TV)
        v["papeis"] = "+".join(agrupados[chave])
        if valor_exato[chave] in (grade[0], grade[-1]):
            v["papeis"] += " [borda da grade]"
        if not v["fechamento"]:
            v["papeis"] += " [SEM FECHAMENTO]"
            sem_fechamento.append(v)
            continue
        l = linha_de.get(chave)
        v["posto_rmse"] = l.get("posto_rmse", "") if l else "fora da grade"
        notaveis.append(v)

    print("\nValores notáveis por h (ordenado por h; torque do cabo na convenção")
    print("da patente, em u.p.; peso em N·m; flags a=tração c=fechamento "
          "d=trab. virtual; ~ = rel troca de sinal, só diagnóstico)")
    print("Papéis de cada h:")
    for v in notaveis + sem_fechamento:
        print(f"  {v['h']:10.4f}  {v['papeis']}")
    if sem_fechamento:
        print("Sem fechamento (fora das tabelas de curva):")
        for v in sem_fechamento:
            print(f"  {v['h']:10.4f}  {v['motivo']}")
    print(f"\n{'h (mm)':>10} {'posto RMSE':>13} {'θ*_pm':>8} {'na faixa':>8}"
          f" {'s_zero':>8} {'δ_min':>7} {'δ_max':>7} {'mola_max':>9} {'flags':>6}"
          f" {'enrol':>5}")
    for v in notaveis:
        flags = "".join(c if v.get(k) else "-" for c, k in
                        (("a", "tracao"), ("c", "fechamento"), ("d", "tv_ok")))
        print(f"{v['h']:10.4f} {str(v['posto_rmse']):>13} "
              f"{v['theta_dc']:8.3f} {str(v['theta_dc_na_faixa']):>8} "
              f"{v['s_zero']:8.3f} {v['delta_min']:7.3f} {v['delta_max']:7.3f} "
              f"{v['mola_max']:9.3f} {flags:>6} {'~' if v['enrol_troca'] else '':>5}")
    print(f"mola_max = L_LIVRE + δ_max (L_LIVRE = {L_LIVRE} mm): comprimento "
          f"esticado da mola, a conferir contra o curso útil da mola.")
    print(f"\n{'h (mm)':>10} {'m_max':>7} {'θ*':>7} {'τ_max':>8} {'θ*':>7}"
          f" {'τ(θmin)':>8} {'τ(pose)':>8} {'τ(θmax)':>8} {'dτ/dθ pose':>11}")
    for v in notaveis:
        print(f"{v['h']:10.4f} {v['braco_max']:7.3f} {v['theta_braco_max']:7.2f} "
              f"{v['tau_max']:8.3f} {v['theta_tau_max']:7.2f} "
              f"{v['tau_theta_min']:8.3f} {v['tau_pose']:8.3f} "
              f"{v['tau_theta_max']:8.3f} {v['dtau_dtheta_pose']:11.3f}")
    print("dτ/dθ* na pose em u.p./rad (diferença central).")
    print(f"\n{'h (mm)':>10} {'mín(cabo−peso)':>15} {'θ*':>7} {'máx(cabo−peso)':>15}"
          f" {'θ*':>7} {'∫cabo':>9} {'∫peso':>8} {'razão':>7}  cruzamentos θ*")
    for v in notaveis:
        cruz = ", ".join(f"{t:.2f}" for t in v["cruzamentos"]) or "nenhum"
        print(f"{v['h']:10.4f} {v['dif_min']:15.3f} {v['theta_dif_min']:7.2f} "
              f"{v['dif_max']:15.3f} {v['theta_dif_max']:7.2f} "
              f"{v['integral_cabo']:9.2f} {v['integral_peso']:8.2f} "
              f"{v['razao_integrais']:7.2f}  {cruz}")
    print("Integrais em θ* em radianos; cabo − peso mistura u.p. e N·m (ver UNIDADES).")
    print(f"\n{'h (mm)':>10} {'RMSE':>8} {'|res|máx':>9} {'res médio':>10}"
          f" {'zonas':>6} {'rel mín°':>9} {'rel máx°':>9} {'arco+ µm':>9}"
          f" {'trab.virt.':>11}")
    for v in notaveis:
        print(f"{v['h']:10.4f} {v['rmse']:8.4f} {v['residuo_max_abs']:9.3f} "
              f"{v['residuo_medio']:10.3f} {v['zonas_de_sinal']:6d} "
              f"{v['rel_min_grau']:9.4f} {v['rel_max_grau']:9.4f} "
              f"{v['arco_pos_max']*1000:9.2f} {v['trabalho_virtual']:11.1e}")

    # ---------------------------------------------------------- arquivos
    pasta = Path(__file__).parent/"results" if "__file__" in globals() \
        else Path("results")
    pasta.mkdir(exist_ok=True)
    arquivos = [pasta/"vh_varredura_h.csv", pasta/"vh_h_notaveis.csv"]
    vh_salvar_csv(arquivos[0], linhas,
                  ["h", "fechamento", "tracao", "tv_ok", "viavel", "motivo",
                   "rmse", "posto_rmse", "k_estrela", "rmse_k_estrela",
                   "delta_min", "theta_delta_min", "delta_max", "mola_max",
                   "rel_min_grau", "rel_max_grau", "enrol_troca",
                   "arco_pos_max", "trabalho_virtual", "erro_linear_K",
                   "tau_max", "deficit_max"])
    vh_salvar_csv(arquivos[1], notaveis + sem_fechamento,
                  ["h", "papeis", "motivo", "posto_rmse", "theta_dc",
                   "theta_dc_na_faixa", "s_zero", "delta_min", "delta_max",
                   "mola_max", "braco_max", "theta_braco_max", "tau_max",
                   "theta_tau_max", "tau_theta_min", "tau_pose", "tau_theta_max",
                   "dtau_dtheta_pose", "dif_min", "theta_dif_min", "dif_max",
                   "theta_dif_max", "cruzamentos", "integral_cabo",
                   "integral_peso", "razao_integrais", "rmse",
                   "residuo_max_abs", "residuo_medio", "zonas_de_sinal",
                   "tracao", "fechamento", "tv_ok", "viavel", "enrol_troca",
                   "arco_pos_max", "rel_min_grau", "rel_max_grau",
                   "trabalho_virtual"])
    lista_notaveis = [(v["papeis"], v["h"]) for v in notaveis]
    if plot_perfil:
        arquivos.append(pasta/"vh_perfil_rmse.png")
        vh_plot_perfil_rmse(linhas, lista_notaveis, faixas, arquivos[-1])
    if plot_curvas:
        arquivos.append(pasta/"vh_curvas_notaveis.png")
        vh_plot_curvas_notaveis(lista_notaveis, VH_THETA, patente, peso,
                                arquivos[-1])
    print("\nArquivos gerados pela varredura:")
    for a in arquivos:
        print(f"  {a}")
    return {"linhas": linhas, "faixas": faixas, "notaveis": notaveis,
            "sem_fechamento": sem_fechamento, "platos": platos,
            "platos_k": platos_k, "degradacao": degr, "degradacao_k": degr_k,
            "h_dc_entra": h_dc_entra, "h_dc_entra_bissecao": h_dc_entra_bis,
            "h_dc_sai_formula": h_dc_sai_formula, "h_dc_sai_bissecao": h_dc_sai_bis,
            "erro_ancora": erro_ancora, "rmse_congelado": rmse_congelado}


VH_RODAR = True            # desligar para executar sem varrer
VH_PLOT_PERFIL_RMSE = False
VH_PLOT_CURVAS_NOTAVEIS = False
if VH_RODAR and __name__ == "__main__":
    varredura_h()
