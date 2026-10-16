"""
Modelo de torque do exoesqueleto de ombro Ottobock (iX Shoulder Air,
patente EP 3 504 033 B1): elemento elástico + alavanca do braço + pino 78.
Modelo plano, no plano sagital. Adaptado de torque_model.py (SuitX: cabo +
tambor + braço), com a mesma arquitetura e disciplina.

Cadeia de cálculo (cada etapa é uma função abaixo):

    θ  →  q  →  g = (P − A) × (C78 − A)  →  regime (I livre / II contato)
                                              │
                    ┌─────────────────────────┘
                    ├→ s, ψ  (forma fechada do regime)  →  x = max(s − s0, 0)
                    │                                         └→ F = k·x
                    └→ b (P no regime I, 78 no regime II), F⃗ = −F·ê(ψ)
                                                              └→ τ = (b × F⃗)_z

Mecanismo. O elástico vai da ancoragem A (bastão do tronco) ao ponto P da
alavanca OP do braço, com |OP| = e. Perto do pivô O há um pino (elemento 78),
preso ao braço. Acima de q* o elástico é reto (regime I); abaixo de q* ele
encosta no 78 e se divide em A → 78 e 78 → P (regime II). Não há tambor nem
tangência.

Referencial. Origem no pivô O; x e y no plano sagital; z sai do plano. Todo
ângulo é medido a partir do eixo x, no sentido anti-horário. ê(a) = (cos a,
sen a). Posições em relação a O:
    A   = −B                     (B = vetor fixo A → O, calculate_base_vector)
    P   =  e·ê(q)
    C78 = −p·ê(φ + q)            (o 78 fica a φ + 180° da alavanca OP)
Essas posições são as que as equações de circuito f1…f4 implicam.

Unidades. Comprimentos em mm. Ângulos em graus na entrada (θ, parâmetros) e
em radianos dentro das contas; cada conversão é feita uma única vez (θ em
calculate_q, parâmetros em montar_geometria). Com k em N/mm, F sai em N e τ
em N·m (b × F⃗ em N·mm, dividido por 1000). τ/k sai em N·m por N/mm.

Sinal. τ positivo = anti-horário = sentido de q crescente.

Estado dos parâmetros. NADA ESTÁ MEDIDO NEM CALIBRADO. C1, C2, α, γ, p, φ, k,
X_POSE, a pose e a faixa de operação estão em PARAMETROS_ILUSTRATIVOS, só
para o código rodar e gerar gráficos de forma. e (raio da alavanca OP) é o
parâmetro varrido e faz o papel que h fazia no original: é argumento
obrigatório em toda a cadeia; E_CAD é documental (ainda None) e
E_ILUSTRATIVO só existe para o código rodar. Não existe E_CALIBRADO.
"""
from pathlib import Path
from typing import NamedTuple

import numpy as np

# ==========================================================================
# PARÂMETROS ILUSTRATIVOS — NÃO MEDIDOS. SÓ PARA O CÓDIGO RODAR E GERAR
# GRÁFICOS DE FORMA. NENHUM VALOR ABAIXO VEM DO CAD NEM DA PATENTE.
# ==========================================================================
# Todos entram na cadeia como argumentos explícitos (montar_geometria e
# assinaturas das funções); nenhuma função lê este dicionário.
PARAMETROS_ILUSTRATIVOS = {
    # vetor fixo A → O: B = (C1 cos α + C2 cos γ, −C1 sen α + C2 sen γ)
    "C1": 40.0,           # mm      NÃO MEDIDO
    "ALPHA": 10.0,        # graus   NÃO MEDIDO
    "C2": 250.0,          # mm      NÃO MEDIDO
    "GAMMA": 95.0,        # graus   NÃO MEDIDO
    # pino 78
    "P": 8.0,             # mm, distância O → 78                    NÃO MEDIDO
    "PHI": -20.0,         # graus, ângulo fixo do 78 na alavanca     NÃO MEDIDO
    # elástico
    "K": 1.5,             # N/mm, rigidez                            NÃO MEDIDO
    "X_POSE": 80.0,       # mm, pré-carga (extensão) na pose         NÃO MEDIDO
    "THETA_POSE": 90.0,   # graus, pose da pré-carga                 NÃO MEDIDO
    # faixa de operação, em θ (= q pelo mapeamento atual)
    "THETA_MIN": 40.0,    # graus                                    NÃO MEDIDO
    "THETA_MAX": 220.0,   # graus                                    NÃO MEDIDO
    # convenção de sinal da curva da patente (só usada se houver extração)
    "SINAL_PATENTE": 1.0,  # +1: a patente usa τ anti-horário positivo. A CONFIRMAR
}

# ----------------------------------------------------- parâmetro varrido e
E_CAD = None          # mm, raio da alavanca OP no CAD. Documental, ainda sem medida.
E_ILUSTRATIVO = 40.0  # mm, só para o código rodar. NÃO MEDIDO, NÃO CALIBRADO.

GRAVIDADE = 9.80665   # m/s², constante física (usada só por torque_peso)

# Extração da Fig. 16/17 da EP 3 504 033 (gancho opcional, ver load_patent_data).
EXTRACAO_EP = Path(__file__).parent/"ep3504033_fig16_17.csv"


# ======================================================================
# 1. Geometria fixa e mapeamento θ → q
# ======================================================================

class Geometria(NamedTuple):
    """Parâmetros fixos do circuito, com ângulos já em radianos.

    e NÃO faz parte da geometria: é o parâmetro varrido e entra como
    argumento separado em toda função que depende dele.
    """
    c1: float     # mm
    c2: float     # mm
    alpha: float  # rad
    gamma: float  # rad
    p: float      # mm, distância O → 78
    phi: float    # rad, ângulo fixo do 78 em relação à alavanca


def montar_geometria(c1, c2, alpha, gamma, p, phi):
    """Monta a Geometria a partir de ângulos em graus (única conversão)."""
    if p < 0:
        raise ValueError("p é uma distância: precisa ser ≥ 0")
    return Geometria(float(c1), float(c2), np.radians(alpha),
                     np.radians(gamma), float(p), np.radians(phi))


def calculate_q(theta):
    """Mapeamento θ → q [rad], com θ em graus.

    q é o ângulo absoluto da alavanca OP. Por ora q faz o papel de θ, então o
    mapeamento é a identidade. Trocar só esta função quando o mapeamento real
    (ângulo do braço → ângulo da alavanca) for conhecido; o resto da cadeia
    trabalha em q e não muda.
    """
    return np.radians(np.asarray(theta, dtype=float))


def versor(angulo):
    """ê(a) = (cos a, sen a), empilhado no eixo 0."""
    return np.array([np.cos(angulo), np.sin(angulo)])


def calculate_base_vector(geo):
    """B = (C1 cos α + C2 cos γ,  −C1 sen α + C2 sen γ): vetor fixo A → O.

    São os termos constantes de f1…f4. Substitui o (h, p) do original.
    """
    return (geo.c1*np.cos(geo.alpha) + geo.c2*np.cos(geo.gamma),
            -geo.c1*np.sin(geo.alpha) + geo.c2*np.sin(geo.gamma))


def calculate_d(e, geo):
    """d: trecho 78 → P [mm], constante para cada e.

    d = |P − C78| = |e·ê(q) + p·ê(φ + q)| = √(e² + p² + 2·e·p·cos φ).
    """
    return np.sqrt(e**2 + geo.p**2 + 2*e*geo.p*np.cos(geo.phi))


def ponto_A(geo):
    """Ancoragem A em relação ao pivô: A = −B [mm]."""
    bx, by = calculate_base_vector(geo)
    return np.array([-bx, -by])


def ponto_P(q, e):
    """Ponto P da alavanca: P = e·ê(q) [mm]."""
    return e*versor(q)


def ponto_78(q, geo):
    """Centro do pino 78: C78 = −p·ê(φ + q) [mm]. Gira com o braço."""
    return -geo.p*versor(geo.phi + q)


# ======================================================================
# 2. Troca de regime: alinhamento A, 78, P
# ======================================================================

def produto_contato(q, e, geo):
    """g = (P − A) × (C78 − A), componente z [mm²].

    g = 0 quando A, 78 e P estão alinhados. Lado do contato: no limite p = 0
    (78 no pivô), g = e·|B|·sen(q_B − q), com q_B = atan2(By, Bx); g < 0 para
    q > q* (elástico livre) e g > 0 para q < q* (o 78 estaria do outro lado
    da linha A → P, logo empurra o elástico). Essa convenção de lado vale para
    todo p; q_estrela_numerico confere que a ordem dos regimes na faixa é a
    do enunciado (II abaixo de q*, I acima).
    """
    a = ponto_A(geo).reshape(2, *([1]*np.ndim(q)))
    pp = ponto_P(q, e) - a
    cc = ponto_78(q, geo) - a
    return pp[0]*cc[1] - pp[1]*cc[0]


def em_contato(q, e, geo):
    """Regime II (elástico encostado no 78) ⇔ g ≥ 0. Nenhum q* é imposto."""
    return produto_contato(q, e, geo) >= 0.0


def q_estrela_fechado(geo):
    """q* em forma fechada, só para p = 0 [rad]: q* = atan2(By, Bx).

    Com o 78 no pivô, o alinhamento A, O, P (O entre A e P) é ê(q) ∥ B.
    Não depende de e.
    """
    if geo.p != 0.0:
        raise ValueError("forma fechada de q* só existe para p = 0")
    bx, by = calculate_base_vector(geo)
    return np.arctan2(by, bx)


def q_estrela_numerico(e, geo, q_grade, tol=1e-13):
    """q* pela troca de sinal de g na grade q_grade, refinada por bissecção [rad].

    Devolve None se g não troca de sinal na grade (um só regime na faixa).
    Só é aceita a troca contato → livre com q crescente (a do enunciado); uma
    troca livre → contato (por exemplo, o alinhamento antípoda, com P entre A
    e o 78) levanta ValueError: a geometria saiu do modelo de dois regimes.
    """
    q_grade = np.asarray(q_grade, dtype=float)
    contato = em_contato(q_grade, e, geo)
    trocas = np.flatnonzero(contato[:-1] != contato[1:])
    if trocas.size == 0:
        return None
    if trocas.size > 1 or not contato[trocas[0]]:
        raise ValueError("ordem de regimes fora do modelo: esperado contato "
                         "(II) abaixo de q* e livre (I) acima, com uma só troca")
    a, b = q_grade[trocas[0]], q_grade[trocas[0] + 1]
    while b - a > tol:
        meio = 0.5*(a + b)
        if em_contato(meio, e, geo):
            a = meio
        else:
            b = meio
    q_est = 0.5*(a + b)
    # alinhamento verdadeiro: o 78 fica ENTRE A e P
    c78 = ponto_78(q_est, geo)
    entre = np.dot(c78 - ponto_A(geo), ponto_P(q_est, e) - c78)
    assert entre > 0, "alinhamento em q* não tem o 78 entre A e P"
    return q_est


# ======================================================================
# 3. Equações de circuito: soluções fechadas e resíduos
# ======================================================================

def resolver_regime_I(q, e, geo):
    """Regime I (elástico livre): s·ê(ψ) = B + e·ê(q).

    s = |A → P| e ψ = direção de A → P.
    """
    bx, by = calculate_base_vector(geo)
    vx, vy = bx + e*np.cos(q), by + e*np.sin(q)
    return np.hypot(vx, vy), np.arctan2(vy, vx)


def resolver_regime_II(q, e, geo):
    """Regime II (contato com o 78): (s − d)·ê(ψ) = B − p·ê(φ + q).

    s − d = |A → 78|, ψ = direção de A → 78 e s = (s − d) + d(e).
    """
    bx, by = calculate_base_vector(geo)
    ux = bx - geo.p*np.cos(geo.phi + q)
    uy = by - geo.p*np.sin(geo.phi + q)
    return calculate_d(e, geo) + np.hypot(ux, uy), np.arctan2(uy, ux)


def calculate_closure_residuals_I(q, s, psi, e, geo):
    """f1 e f2 como escritos, para conferir a solução (devem dar ≈ 0)."""
    f1 = (geo.c1*np.cos(geo.alpha) + geo.c2*np.cos(geo.gamma)
          + e*np.cos(q) - s*np.cos(psi))
    f2 = (-geo.c1*np.sin(geo.alpha) + geo.c2*np.sin(geo.gamma)
          + e*np.sin(q) - s*np.sin(psi))
    return f1, f2


def calculate_closure_residuals_II(q, s, psi, e, geo):
    """f3 e f4 como escritos, para conferir a solução (devem dar ≈ 0)."""
    d = calculate_d(e, geo)
    f3 = (geo.c1*np.cos(geo.alpha) + geo.c2*np.cos(geo.gamma)
          - geo.p*np.cos(geo.phi + q) - (s - d)*np.cos(psi))
    f4 = (-geo.c1*np.sin(geo.alpha) + geo.c2*np.sin(geo.gamma)
          - geo.p*np.sin(geo.phi + q) - (s - d)*np.sin(psi))
    return f3, f4


def resolver_circuito(q, e, geo):
    """Regime de cada q (pelo sinal de g) e s, ψ da solução desse regime."""
    contato = em_contato(q, e, geo)
    s1, psi1 = resolver_regime_I(q, e, geo)
    s2, psi2 = resolver_regime_II(q, e, geo)
    return contato, np.where(contato, s2, s1), np.where(contato, psi2, psi1)


# ======================================================================
# 4. Elástico: ancoragem por pré-carga, extensão e força
# ======================================================================

def s_zero(e, geo, theta_pose, x_pose):
    """Comprimento em que o elástico atinge o comprimento livre [mm].

    s0(e) = s(q_pose, e) − X_POSE: a pré-carga na pose é fixa e o comprimento
    livre acompanha e.
    """
    _, s_pose, _ = resolver_circuito(calculate_q(theta_pose), e, geo)
    return float(s_pose) - x_pose


def calculate_extension(s, s0):
    """Extensão bruta s − s0, sem saturação [mm] (negativa = frouxo)."""
    return s - s0


def calculate_x(s, s0):
    """x = max(s − s0, 0) [mm]. O elástico traciona, mas não empurra."""
    return np.maximum(calculate_extension(s, s0), 0.0)


def spring_force(k, x):
    """F = k·x, com x em mm (dF = k·ds no trecho tracionado)."""
    return k*x


# ======================================================================
# 5. Torque
# ======================================================================

def ponto_aplicacao(q, e, geo, contato):
    """b: vetor do pivô ao ponto de aplicação da força do trecho A → (…) [mm].

    Regime I: b = P = e·ê(q). Regime II: b = C78 = −p·ê(φ + q). O trecho
    78 → P é interno ao braço (as forças em P e no 78 se anulam, colineares)
    e não entra no torque. É o análogo de ponto_tangencia do original.
    """
    return np.where(contato, ponto_78(q, geo), ponto_P(q, e))


def vetor_forca(force, psi):
    """F⃗ = −F·ê(ψ): o elástico puxa o ponto de aplicação para A [N]."""
    return -force*versor(psi)


def torque_produto_vetorial(b_vector, f_vector):
    """τ = componente z de b × F⃗ = bx·Fy − by·Fx. Positivo = anti-horário."""
    return b_vector[0]*f_vector[1] - b_vector[1]*f_vector[0]


def braco_momento(q, psi, e, geo, contato):
    """Braço de momento escalar com sinal, τ/F [mm]. SÓ PARA O RELATÓRIO.

    Regime I: e·sen(q − ψ). Regime II: p·sen(ψ − φ − q). A cadeia calcula τ
    pelo produto vetorial; esta fórmula serve de conferência (autoteste 6).
    """
    return np.where(contato, geo.p*np.sin(psi - geo.phi - q),
                    e*np.sin(q - psi))


def torque_peso(theta, massa_kg, cg_raio_mm, cg_angulo_grau,
                angulo_gravidade_grau):
    """Torque estático do peso do braço em relação ao pivô [N·m], com sinal
    (positivo = anti-horário). Independente da cadeia do elástico.

    Todos os argumentos são obrigatórios e não há valores padrão: massa e CG
    do conjunto ainda não foram medidos (os valores da SuitX foram removidos).
      cg_raio_mm:            distância O → CG
      cg_angulo_grau:        ângulo do CG em relação à alavanca OP
      angulo_gravidade_grau: direção da gravidade no referencial do modelo
    O CG gira com a alavanca: r_CG = cg_raio·ê(q + cg_angulo). Inércia não
    entra. Diferença em relação ao original: devolve τ com sinal, não |τ|.
    """
    q = calculate_q(theta)
    r_cg = cg_raio_mm*versor(q + np.radians(cg_angulo_grau))
    peso = massa_kg*GRAVIDADE*versor(np.radians(angulo_gravidade_grau))
    peso = peso.reshape(2, *([1]*np.ndim(q)))
    return torque_produto_vetorial(r_cg, peso)/1000.0


# ======================================================================
# 6. Cadeia completa
# ======================================================================

def generate_graph_torque_theta_relation(force, e, geo, theta_pose, x_pose,
                                         theta):
    """Calcula todas as grandezas para cada θ.

    force:      força do elástico F, número ou array do tamanho de theta. Com
                força unitária, τ·1000 = braço de momento. Para F = k·x use
                calculate_torque_curve.
    e:          raio da alavanca OP a testar [mm]. Obrigatório.
    geo:        Geometria (montar_geometria).
    theta_pose: pose da pré-carga [graus]; x_pose: pré-carga [mm].
    theta:      ângulos θ [graus].
    """
    theta = np.asarray(theta, dtype=float)

    # cinemática: regime pelo sinal de g, depois a forma fechada do regime
    q = calculate_q(theta)
    g = produto_contato(q, e, geo)
    contato, s, psi = resolver_circuito(q, e, geo)
    d = calculate_d(e, geo)
    s_I, psi_I = resolver_regime_I(q, e, geo)
    s_II, psi_II = resolver_regime_II(q, e, geo)
    f1, f2 = calculate_closure_residuals_I(q, s_I, psi_I, e, geo)
    f3, f4 = calculate_closure_residuals_II(q, s_II, psi_II, e, geo)

    # elástico
    s0 = s_zero(e, geo, theta_pose, x_pose)
    extensao = calculate_extension(s, s0)
    x = calculate_x(s, s0)

    # força e torque (produto vetorial); braço escalar só para relatório
    f = np.broadcast_to(np.asarray(force, dtype=float), theta.shape)
    b_vector = ponto_aplicacao(q, e, geo, contato)                  # mm
    F_vector = vetor_forca(f, psi)                                  # N
    tau = torque_produto_vetorial(b_vector, F_vector)/1000          # N·m
    braco = braco_momento(q, psi, e, geo, contato)                  # mm
    tau_escalar = f*braco/1000                                      # N·m

    return dict(theta=theta, q=q, g=g, contato=contato, e=e, d=d, s=s,
                psi=psi, s_menos_d=np.where(contato, s - d, np.nan),
                s_I=s_I, psi_I=psi_I, s_II=s_II, psi_II=psi_II,
                f1=f1, f2=f2, f3=f3, f4=f4, s0=s0, extensao=extensao, x=x,
                force=f, b_vector=b_vector, F_vector=F_vector, tau=tau,
                braco=braco, tau_escalar=tau_escalar)


def calculate_torque_curve(k, e, geo, theta_pose, x_pose, theta):
    """Cadeia completa com F = k·x, para um k e um e dados (τ em N·m)."""
    geometry = generate_graph_torque_theta_relation(0.0, e, geo, theta_pose,
                                                    x_pose, theta)
    force = spring_force(k, geometry["x"])
    return generate_graph_torque_theta_relation(force, e, geo, theta_pose,
                                                x_pose, theta)


# ======================================================================
# 7. Autotestes
# ======================================================================

def residuo_trabalho_virtual(e, geo, theta, passo=1e-6):
    """max|ds/dq + τ/F| [mm/rad] em cada regime, por diferença central em q.

    Cada ponto é derivado pela forma fechada do SEU regime, então a troca de
    regime em q* não contamina a diferença. Num mecanismo conservativo,
    ds/dq = −τ/F. Devolve {"I": ..., "II": ...} (None se o regime não ocorre).
    """
    q = calculate_q(theta)
    contato = em_contato(q, e, geo)

    def s_do_regime(qq):
        return np.where(contato, resolver_regime_II(qq, e, geo)[0],
                        resolver_regime_I(qq, e, geo)[0])

    ds_dq = (s_do_regime(q + passo) - s_do_regime(q - passo))/(2*passo)
    _, _, psi = resolver_circuito(q, e, geo)
    tau_por_F = torque_produto_vetorial(ponto_aplicacao(q, e, geo, contato),
                                        vetor_forca(1.0, psi))
    erro = np.abs(ds_dq + tau_por_F)
    return {"I": float(erro[~contato].max()) if (~contato).any() else None,
            "II": float(erro[contato].max()) if contato.any() else None}


def trechos_frouxos(theta, extensao):
    """Intervalos de θ onde o elástico afrouxa (s − s0 < 0), com as bordas
    interpoladas linearmente. Lista de (θ_início, θ_fim) em graus."""
    frouxo = extensao < 0
    if not frouxo.any():
        return []
    trechos, i = [], 0
    while i < len(theta):
        if not frouxo[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(theta) and frouxo[j + 1]:
            j += 1

        def borda(a, b):
            return float(theta[a] - extensao[a]*(theta[b] - theta[a])
                         / (extensao[b] - extensao[a]))
        ini = float(theta[i]) if i == 0 else borda(i - 1, i)
        fim = float(theta[j]) if j == len(theta) - 1 else borda(j, j + 1)
        trechos.append((ini, fim))
        i = j + 1
    return trechos


def guarda_e(e_a, e_b, geo, theta_pose, x_pose, theta):
    """Guarda do e implícito: dois e distintos têm de dar curvas distintas.

    Compara s (sempre depende de e: e no regime I, d(e) no regime II) e τ nos
    pontos em regime I. Levanta RuntimeError se e não chega à cadeia.
    """
    ra = calculate_torque_curve(1.0, e_a, geo, theta_pose, x_pose, theta)
    rb = calculate_torque_curve(1.0, e_b, geo, theta_pose, x_pose, theta)
    livre = ~(ra["contato"] & rb["contato"])
    if (np.array_equal(ra["s"], rb["s"])
            or (livre.any() and np.array_equal(ra["tau"][livre],
                                               rb["tau"][livre]))):
        raise RuntimeError(f"e não está chegando à cadeia: curvas iguais para "
                           f"e = {e_a:g} e e = {e_b:g}. Varredura abortada.")
    return float(np.max(np.abs(ra["tau"] - rb["tau"])))


def erro_ancoragem(e_valores, geo, theta_pose, x_pose):
    """max|x(q_pose, e) − X_POSE| [mm] sobre e_valores (deve ser ≈ 0)."""
    erros = []
    for e in e_valores:
        r = generate_graph_torque_theta_relation(0.0, e, geo, theta_pose,
                                                 x_pose, [theta_pose])
        erros.append(abs(float(r["x"][0]) - x_pose))
    return max(erros)


def grade_q_volta(geo, n=3601):
    """Grade em q de q_B − 0,9π a q_B + 0,9π [rad], para os testes que não
    podem depender da faixa de operação (q* e caso p = 0). Exclui os
    alinhamentos antípodas, perto de q_B ± π."""
    q_b = np.arctan2(*calculate_base_vector(geo)[::-1])
    return q_b + np.linspace(-0.9*np.pi, 0.9*np.pi, n)


def autoteste_p_zero(e_valores, geo):
    """Autoteste 4: com p = 0, s = |B| + e constante e τ = 0 no regime II, e
    q* numérico = forma fechada atan2(By, Bx), igual para todo e."""
    geo0 = geo._replace(p=0.0)
    q = grade_q_volta(geo0)
    modulo_b = float(np.hypot(*calculate_base_vector(geo0)))
    q_fechado = q_estrela_fechado(geo0)
    saida = {"q_fechado": q_fechado, "erro_q": 0.0, "erro_s": 0.0,
             "tau_max": 0.0}
    for e in e_valores:
        contato, s, psi = resolver_circuito(q, e, geo0)
        tau = torque_produto_vetorial(ponto_aplicacao(q, e, geo0, contato),
                                      vetor_forca(1.0, psi))
        q_num = q_estrela_numerico(e, geo0, q)
        saida["erro_q"] = max(saida["erro_q"], abs(q_num - q_fechado))
        saida["erro_s"] = max(saida["erro_s"],
                              float(np.max(np.abs(s[contato] - (modulo_b + e)))))
        saida["tau_max"] = max(saida["tau_max"],
                               float(np.max(np.abs(tau[contato]))))
        assert contato.any() and (~contato).any(), "p = 0: faltou um regime"
    assert saida["erro_q"] < 1e-9, f"q* p = 0: {saida['erro_q']:.1e} rad"
    assert saida["erro_s"] < 1e-9, f"s ≠ |B| + e: {saida['erro_s']:.1e} mm"
    assert saida["tau_max"] < 1e-12, f"τ ≠ 0 no regime II: {saida['tau_max']:.1e}"
    return saida


def autotestes(e, geo, k, theta_pose, x_pose, theta, e_extra):
    """Confere a cadeia em e (força unitária e F = k·x) e devolve os números.

    e_extra: outros valores de e para a guarda de e, a ancoragem e o caso
    p = 0 (o autoteste não pode depender de um e só).
    """
    theta = np.asarray(theta, dtype=float)
    r1 = generate_graph_torque_theta_relation(1.0, e, geo, theta_pose, x_pose,
                                              theta)
    rk = calculate_torque_curve(k, e, geo, theta_pose, x_pose, theta)
    contato = r1["contato"]
    numeros = {"n_regime_I": int((~contato).sum()),
               "n_regime_II": int(contato.sum())}

    # 1. resíduos das equações de circuito nos dois regimes
    numeros["residuo_f1"] = float(np.max(np.abs(r1["f1"])))
    numeros["residuo_f2"] = float(np.max(np.abs(r1["f2"])))
    numeros["residuo_f3"] = float(np.max(np.abs(r1["f3"])))
    numeros["residuo_f4"] = float(np.max(np.abs(r1["f4"])))
    for nome in ("residuo_f1", "residuo_f2", "residuo_f3", "residuo_f4"):
        assert numeros[nome] < 1e-9, f"{nome} = {numeros[nome]:.1e} mm"

    # d pela fórmula = |P − C78|
    q = r1["q"]
    numeros["d_duas_vias"] = float(np.max(np.abs(
        np.hypot(*(ponto_P(q, e) - ponto_78(q, geo))) - r1["d"])))
    assert numeros["d_duas_vias"] < 1e-9

    # 2. trabalho virtual: ds/dq = −τ/F nos dois regimes
    tv = residuo_trabalho_virtual(e, geo, theta)
    numeros["tv_I"], numeros["tv_II"] = tv["I"], tv["II"]
    assert all(v is None or v < 1e-6 for v in tv.values()), f"TV: {tv}"

    # 3. continuidade em q*: s (e τ) do regime I = do regime II
    q_volta = grade_q_volta(geo)
    q_est = q_estrela_numerico(e, geo, q_volta)
    assert q_est is not None, "q* não encontrado na volta em torno de q_B"
    s_I, psi_I = resolver_regime_I(q_est, e, geo)
    s_II, psi_II = resolver_regime_II(q_est, e, geo)
    tau_I = torque_produto_vetorial(ponto_P(q_est, e), vetor_forca(1.0, psi_I))
    tau_II = torque_produto_vetorial(ponto_78(q_est, geo),
                                     vetor_forca(1.0, psi_II))
    numeros["q_estrela"] = q_est
    numeros["q_estrela_faixa"] = q_estrela_numerico(e, geo, q)
    numeros["continuidade_s"] = float(abs(s_I - s_II))
    numeros["continuidade_tau"] = float(abs(tau_I - tau_II))
    assert numeros["continuidade_s"] < 1e-9
    assert numeros["continuidade_tau"] < 1e-9
    # ordem dos regimes na faixa: II para q ≤ q*, I para q > q*
    assert np.array_equal(contato, q <= q_est), "ordem dos regimes violada"

    # 4. caso p = 0
    numeros["p_zero"] = autoteste_p_zero((e,) + tuple(e_extra), geo)

    # 5. tração: x ≥ 0 na faixa ou relatório de onde afrouxa (não é assert)
    numeros["frouxo"] = trechos_frouxos(theta, rk["extensao"])

    # 6. τ pelo produto vetorial = τ pela fórmula escalar
    numeros["tau_duas_vias"] = float(np.max(np.abs(rk["tau"]
                                                   - rk["tau_escalar"])))
    assert numeros["tau_duas_vias"] < 1e-9

    # linearidade em k (com dois k diferentes, para nunca ser trivial)
    rk2 = calculate_torque_curve(2.0*k + 1.0, e, geo, theta_pose, x_pose, theta)
    numeros["erro_linear_K"] = float(max(
        np.max(np.abs(rk["tau"] - k*r1["tau"]*r1["x"])),
        np.max(np.abs(rk2["tau"]/(2.0*k + 1.0) - rk["tau"]/k))))
    assert numeros["erro_linear_K"] < 1e-9

    # 7. guarda de e e ancoragem s0(e)
    numeros["guarda_e"] = guarda_e(e, e_extra[0], geo, theta_pose, x_pose,
                                   theta)
    numeros["ancoragem"] = erro_ancoragem((e,) + tuple(e_extra), geo,
                                          theta_pose, x_pose)
    assert numeros["ancoragem"] < 1e-9, \
        f"ancoragem violada: {numeros['ancoragem']:.1e} mm"

    # e é obrigatório em toda a cadeia
    for chamada in (lambda: calculate_torque_curve(k, geo=geo, theta=theta,
                                                   theta_pose=theta_pose,
                                                   x_pose=x_pose),
                    lambda: s_zero(geo=geo, theta_pose=theta_pose,
                                   x_pose=x_pose),
                    lambda: calculate_d(geo=geo),
                    lambda: q_estrela_numerico(geo=geo, q_grade=q),
                    lambda: resolver_circuito(q, geo=geo)):
        try:
            chamada()
        except TypeError:
            continue
        raise AssertionError("uma função da cadeia aceitou ser chamada sem e")

    # torque_peso: CG na direção da gravidade → 0; perpendicular → m·g·r
    # (valores de teste, não do dispositivo)
    assert abs(torque_peso(0.0, 2.0, 100.0, -90.0, -90.0)) < 1e-12
    assert abs(torque_peso(0.0, 2.0, 100.0, 0.0, -90.0)
               + 2.0*GRAVIDADE*0.1) < 1e-12
    return numeros


# ======================================================================
# 8. Extração da patente (gancho opcional)
# ======================================================================

def load_patent_data(caminho):
    """Gancho opcional para a extração da Fig. 16/17 da EP 3 504 033.

    CSV pt-BR: cabeçalho 'theta;torque', separador ';', vírgula decimal, θ em
    graus (mesma entrada da cadeia, mapeada por calculate_q). Os pontos são
    mantidos na ordem do arquivo, sem reordenar, interpolar nem suavizar.
    Se o arquivo não existe, devolve None e o código roda sem RMSE.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        return None
    linhas = [l for l in caminho.read_text(encoding="utf-8").splitlines()
              if l.strip()]
    cabecalho = [c.strip().lower() for c in linhas[0].split(";")]
    if cabecalho[:2] != ["theta", "torque"]:
        raise ValueError(f"{caminho}: cabeçalho esperado 'theta;torque'")
    dados = np.array([[float(c.replace(",", ".")) for c in l.split(";")[:2]]
                      for l in linhas[1:]])
    return {"theta": dados[:, 0], "torque": dados[:, 1], "fonte": str(caminho)}


# ==========================================================================
# 9. VARREDURA PARAMÉTRICA DE e  (diagnóstico)
# ==========================================================================
#
# Regras (as mesmas da varredura de h do original): toda conta vive dentro de
# funções; e é passado explicitamente em toda chamada; nada aqui calibra
# nenhum parâmetro. Globais novos: só as funções ve_* e varredura_e, e as
# constantes VE_*.
#
# k não é conhecido e τ é linear em k, então a família é plotada como τ/k:
# as curvas mostram só o efeito geométrico de e. Sem a extração da patente
# não há critério de ótimo: o relatório dá pico de τ/k, q*, x_max, faixa de
# tração e os nós da família. Com a extração, o mesmo código calcula o RMSE
# (com k congelado, nunca reidentificado por e) e o e de menor RMSE, como
# ACHADO DIAGNÓSTICO.
#
# Viabilidade = (a) tração + (c) fechamento + (d) trabalho virtual.

VE_GRID = np.arange(10.0, 70.0 + 1e-9, 0.05)   # mm, e VARRIDO. ILUSTRATIVA, ajustável
VE_FAMILIA = (20.0, 30.0, 40.0, 50.0, 60.0)    # mm, curvas τ/k × q. ILUSTRATIVA
VE_THETA = np.linspace(PARAMETROS_ILUSTRATIVOS["THETA_MIN"],
                       PARAMETROS_ILUSTRATIVOS["THETA_MAX"], 1501)  # graus
VE_FOLGAS = (1.01, 1.05, 1.10, 2.00)           # platôs de RMSE (só com extração)
VE_CRITERIOS = ("tracao", "fechamento", "tv_ok")
VE_TOL_TV = 1e-6                               # mm/rad


def ve_avaliar_e(e, geo, k, theta_pose, x_pose, theta, patente, sinal_patente,
                 tol_tv):
    """Validade (a), (c), (d) e indicadores de um e. Nada é saturado nem
    corrigido; k só multiplica (τ/k não depende dele).

    patente: dicionário de load_patent_data ou None (sem RMSE).
    """
    linha = {"e": float(e), "motivo": "", "viavel": False}
    q = calculate_q(theta)
    try:
        q_est = q_estrela_numerico(e, geo, q)
        rk = calculate_torque_curve(k, e, geo, theta_pose, x_pose, theta)
        r1 = calculate_torque_curve(1.0, e, geo, theta_pose, x_pose, theta)
        tv = residuo_trabalho_virtual(e, geo, theta)
    except (ValueError, AssertionError) as erro:
        linha["fechamento"] = False
        linha["motivo"] = f"fechamento: {erro}"
        return linha

    contato = rk["contato"]
    linha["fechamento"] = bool(np.all(rk["s"] > 0)
                               and np.all(rk["s_menos_d"][contato] > 0))
    if not linha["fechamento"]:
        linha["motivo"] = "fechamento: s ≤ 0 ou s − d ≤ 0"
        return linha

    # τ é linear em k (x não depende de k): τ(k) = k·τ(k = 1)
    erro_linear = float(np.max(np.abs(rk["tau"] - k*r1["tau"])))
    assert erro_linear < 1e-9, f"τ não é linear em k: {erro_linear:.1e}"

    tau_k = r1["tau"]                    # N·m por N/mm
    extensao = rk["extensao"]
    frouxo = trechos_frouxos(theta, extensao)
    tracionado = theta[extensao >= 0]
    i_pico, i_min = int(np.argmax(tau_k)), int(np.argmin(tau_k))
    i_xmin, i_xmax = int(np.argmin(extensao)), int(np.argmax(extensao))
    tv_max = max(v for v in tv.values() if v is not None)
    linha.update(
        d=float(rk["d"]),
        s0=float(rk["s0"]),
        q_estrela=None if q_est is None else float(np.degrees(q_est)),
        frac_contato=float(contato.mean()),
        tracao=not frouxo,
        trechos_frouxos=" ".join(f"{a:.2f}–{b:.2f}".replace(".", ",")
                                 for a, b in frouxo),
        theta_tracao_min=float(tracionado.min()) if tracionado.size else None,
        theta_tracao_max=float(tracionado.max()) if tracionado.size else None,
        x_min=float(extensao[i_xmin]), theta_x_min=float(theta[i_xmin]),
        x_max=float(extensao[i_xmax]), theta_x_max=float(theta[i_xmax]),
        tau_k_pico=float(tau_k[i_pico]), theta_pico=float(theta[i_pico]),
        tau_k_min=float(tau_k[i_min]), theta_tau_k_min=float(theta[i_min]),
        braco_max=float(np.max(rk["braco"])),
        tv_I=tv["I"], tv_II=tv["II"], trabalho_virtual=float(tv_max),
        tv_ok=bool(tv_max < tol_tv),
        erro_linear_K=erro_linear,
    )

    if patente is not None:
        y = patente["torque"]
        modelo = sinal_patente*calculate_torque_curve(
            k, e, geo, theta_pose, x_pose, patente["theta"])["tau"]
        residuo = modelo - y
        i_res = int(np.argmax(np.abs(residuo)))
        linha.update(
            rmse=float(np.sqrt(np.mean(residuo**2))),
            mae=float(np.mean(np.abs(residuo))),
            erro_max=float(np.abs(residuo[i_res])),
            theta_erro_max=float(patente["theta"][i_res]),
            r2=float(1 - np.sum(residuo**2)/np.sum((y - y.mean())**2)),
        )

    linha["viavel"] = all(linha[c] for c in VE_CRITERIOS)
    linha["motivo"] = ", ".join(c for c in VE_CRITERIOS if not linha[c])
    return linha


def ve_extensao_minima(e, geo, theta_pose, x_pose, theta):
    """Menor extensão bruta s − s0(e) na faixa [mm]."""
    r = generate_graph_torque_theta_relation(0.0, e, geo, theta_pose, x_pose,
                                             theta)
    return float(r["extensao"].min())


def ve_fronteira_tracao(e_ok, e_falha, geo, theta_pose, x_pose, theta,
                        tol=1e-9):
    """e em que a menor extensão na faixa passa por zero, por bissecção
    própria entre um e que traciona e um que afrouxa."""
    while abs(e_falha - e_ok) > tol:
        meio = 0.5*(e_ok + e_falha)
        if ve_extensao_minima(meio, geo, theta_pose, x_pose, theta) >= 0:
            e_ok = meio
        else:
            e_falha = meio
    return e_ok


def ve_faixa(linhas, chave):
    """Menor e maior e com linhas[chave] verdadeiro, quantos são e se o
    conjunto é contíguo na grade (linhas ordenadas por e)."""
    es = np.array([l["e"] for l in linhas])
    ok = np.array([bool(l.get(chave, False)) for l in linhas])
    if not ok.any():
        return None
    indices = np.flatnonzero(ok)
    primeiro, ultimo = int(indices[0]), int(indices[-1])
    return {"min": float(es[primeiro]), "max": float(es[ultimo]),
            "n": int(ok.sum()),
            "contigua": bool(ok[primeiro:ultimo + 1].all()),
            "borda_min": primeiro == 0, "borda_max": ultimo == len(ok) - 1}


def ve_plato(linhas, folga):
    """e com RMSE ≤ folga·mínimo (entre os e com fechamento). Só com extração."""
    minimo = min(l["rmse"] for l in linhas if l["fechamento"])
    marcas = [{"e": l["e"], "ok": bool(l["fechamento"]
                                       and l["rmse"] <= folga*minimo)}
              for l in linhas]
    faixa = ve_faixa(marcas, "ok")
    faixa.update(folga=folga, minimo=minimo,
                 largura=faixa["max"] - faixa["min"])
    return faixa


def ve_nos_da_familia(familia, geo, theta_pose, x_pose, theta):
    """Curvas τ/k da família, espalhamento máx − mín entre elas em cada θ,
    seus mínimos locais (nós: onde as curvas quase não dependem de e) e o
    máximo."""
    curvas = np.array([calculate_torque_curve(1.0, e, geo, theta_pose, x_pose,
                                              theta)["tau"] for e in familia])
    espalhamento = curvas.max(axis=0) - curvas.min(axis=0)
    nos = [(float(theta[j]), float(espalhamento[j]))
           for j in range(1, len(theta) - 1)
           if espalhamento[j] < espalhamento[j - 1]
           and espalhamento[j] <= espalhamento[j + 1]]
    j = int(np.argmax(espalhamento))
    return {"curvas": curvas, "espalhamento": espalhamento, "nos": nos,
            "maximo": (float(theta[j]), float(espalhamento[j]))}


def ve_salvar_csv(caminho, linhas, colunas,
                  colunas_texto=("papeis", "motivo", "trechos_frouxos")):
    """CSV para Excel pt-BR: separador ';', decimal vírgula, sim/nao."""
    texto = [";".join(colunas)]
    for l in linhas:
        celulas = []
        for c in colunas:
            valor = l.get(c, "")
            if valor is None:
                celula = ""
            elif c in colunas_texto:
                celula = str(valor)
            elif isinstance(valor, (bool, np.bool_)):
                celula = "sim" if valor else "nao"
            elif isinstance(valor, (float, np.floating)):
                celula = f"{valor:.6g}".replace(".", ",")
            else:
                celula = str(valor)
            celulas.append(celula)
        texto.append(";".join(celulas))
    caminho.write_text("\n".join(texto) + "\n", encoding="utf-8")


def ve_formatador_virgula(casas):
    from matplotlib.ticker import FuncFormatter
    return FuncFormatter(lambda x, pos: f"{x:.{casas}f}".replace(".", ","))


def ve_plot_familia(familia, nos, linhas_familia, theta, patente, k,
                    sinal_patente, caminho_png):
    """Família de curvas τ/k × θ num único eixo. e é ordenado: rampa
    sequencial de um só tom, clara → escura. q* de cada curva marcado."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rampa = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#184f95", "#0d366b"]
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=200, facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    ax.axhline(0, color="#52514e", linewidth=0.8)
    for j, (theta_no, _) in enumerate(nos["nos"]):
        ax.axvline(theta_no, color="#7a7974", linewidth=0.8, linestyle=":",
                   label="nós da família" if j == 0 else None)
    ordem = sorted(range(len(familia)), key=lambda i: familia[i])
    for posto, i in enumerate(ordem):
        cor = rampa[round(posto*(len(rampa) - 1)/max(len(ordem) - 1, 1))]
        ax.plot(theta, nos["curvas"][i], color=cor, linewidth=2,
                label=f"e = {familia[i]:g} mm".replace(".", ","))
        q_est = linhas_familia[i].get("q_estrela")
        if q_est is not None:
            y_est = np.interp(q_est, theta, nos["curvas"][i])
            ax.plot([q_est], [y_est], "o", color=cor, markersize=6,
                    markeredgecolor="#fcfcfb", markeredgewidth=1.5, zorder=4)
    ax.plot([], [], "o", color="#52514e", markersize=6, label="q* (troca de regime)")
    if patente is not None:
        ax.plot(patente["theta"], sinal_patente*patente["torque"]/k, "o",
                color="#0b0b0b", markersize=4.5, zorder=5,
                label=f"Extração EP 3 504 033 ÷ k ({len(patente['theta'])} pontos)")
    ax.set_xlabel("θ = q (graus)")
    ax.set_ylabel("τ/k  (N·m por N/mm)")
    ax.set_title("Família τ/k × q, efeito geométrico de e — PARÂMETROS "
                 "ILUSTRATIVOS, NÃO MEDIDOS", loc="left", fontsize=10.5)
    ax.xaxis.set_major_formatter(ve_formatador_virgula(0))
    ax.yaxis.set_major_formatter(ve_formatador_virgula(1))
    ax.grid(color="#e6e5e1", linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ax.spines.values():
        lado.set_color("#b9b8b2")
    ax.tick_params(colors="#52514e")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False,
              fontsize=8)
    fig.subplots_adjust(left=0.08, right=0.74, bottom=0.11, top=0.92)
    fig.savefig(caminho_png, facecolor="#fcfcfb")
    plt.close(fig)


def varredura_e(geo, k, theta_pose, x_pose, theta, grade, familia,
                caminho_extracao, sinal_patente, pasta, plot_familia=True):
    """Varre e, classifica validade física, gera a família τ/k e reporta os
    indicadores. Diagnóstico: não calibra nada. Todos os parâmetros entram
    como argumentos. Devolve um dicionário com linhas, faixas e família."""
    patente = load_patent_data(caminho_extracao)
    theta = np.asarray(theta, dtype=float)

    # guarda do e implícito: dois e distintos têm de dar curvas distintas
    dif_guarda = guarda_e(min(familia), max(familia), geo, theta_pose, x_pose,
                          theta)

    grade = np.unique(np.concatenate([grade, familia, [E_ILUSTRATIVO]]))
    linhas = [ve_avaliar_e(e, geo, k, theta_pose, x_pose, theta, patente,
                           sinal_patente, VE_TOL_TV) for e in grade]
    linha_de = {round(l["e"], 9): l for l in linhas}

    # ancoragem: x(q_pose) = X_POSE para todo e
    erro_ancora = erro_ancoragem(grade, geo, theta_pose, x_pose)
    assert erro_ancora < 1e-9, f"ancoragem violada: {erro_ancora:.1e} mm"

    calculaveis = [l for l in linhas if l["fechamento"]]
    faixas = {nome: ve_faixa(linhas, nome)
              for nome in ("tracao", "tv_ok", "viavel")}

    fronteira = None
    if faixas["tracao"] and not faixas["tracao"]["borda_max"]:
        es = [l["e"] for l in linhas]
        i_ok = es.index(faixas["tracao"]["max"])
        fronteira = ve_fronteira_tracao(es[i_ok], es[i_ok + 1], geo,
                                        theta_pose, x_pose, theta)

    nos = ve_nos_da_familia(familia, geo, theta_pose, x_pose, theta)
    linhas_familia = [linha_de[round(float(e), 9)] for e in familia]
    q_estrelas = [l["q_estrela"] for l in calculaveis
                  if l.get("q_estrela") is not None]
    p_zero = autoteste_p_zero((grade[0], grade[-1]), geo)

    # ---------------------------------------------------------- relatório
    print("\n" + "=" * 78)
    print("VARREDURA PARAMÉTRICA DE e (diagnóstico) — PARÂMETROS ILUSTRATIVOS")
    print("=" * 78)
    print("e = raio da alavanca OP, VARRIDO. Nenhum outro parâmetro está medido;")
    print("os resultados mostram só a FORMA do efeito de e.")
    print(f"Grade: {grade.size} valores de e, de {grade[0]:g} a {grade[-1]:g} mm "
          f"(VE_GRID ilustrativa). Faixa θ: {theta[0]:g}° a {theta[-1]:g}°, "
          f"{theta.size} pontos.")
    print(f"Viabilidade = {' + '.join(VE_CRITERIOS)} (critérios (a), (c), (d)).")
    print(f"Guarda do e implícito: curvas com e = {min(familia):g} e "
          f"e = {max(familia):g} diferem (máx. {dif_guarda:.3e} N·m por N/mm). OK.")
    print(f"Linearidade em k: max|τ(k) − k·τ(k=1)| na grade = "
          f"{max(l['erro_linear_K'] for l in calculaveis):.1e} (< 1e-9). "
          f"Por isso a família é τ/k.")
    print(f"Ancoragem: s0(e) = s(q_pose, e) − X_POSE; extensão na pose fixa em "
          f"X_POSE = {x_pose:g} mm para todo e (erro máx. {erro_ancora:.1e} mm).")

    if geo.p == 0.0:
        print(f"q*: com p = 0, q* = atan2(By, Bx) = "
              f"{np.degrees(q_estrela_fechado(geo)):.4f}° e NÃO depende de e.")
    else:
        print(f"q*: com p = {geo.p:g} mm, q* depende de e: de "
              f"{min(q_estrelas):.3f}° a {max(q_estrelas):.3f}° na grade "
              f"({len(q_estrelas)} de {len(calculaveis)} e com q* dentro da faixa).")
    print(f"   Caso p = 0 (autoteste): q* = {np.degrees(p_zero['q_fechado']):.4f}° "
          f"para e = {grade[0]:g} e e = {grade[-1]:g} mm (numérico × fechado: "
          f"{p_zero['erro_q']:.1e} rad) — independe de e.")

    print("\nValidade física (na grade de e):")
    rotulos = {"tracao": "(a) tração", "tv_ok": "(d) trabalho virtual",
               "viavel": "viável (a), (c), (d)"}
    for nome, rotulo in rotulos.items():
        f = faixas[nome]
        if f is None:
            print(f"  {rotulo:22s} nenhum e atende")
            continue
        print(f"  {rotulo:22s} e de {f['min']:.3f}"
              f"{' (borda da grade)' if f['borda_min'] else ''} a "
              f"{f['max']:.3f}{' (borda da grade)' if f['borda_max'] else ''}"
              f" mm, {f['n']} e{'' if f['contigua'] else ', NÃO contíguo'}")
    print(f"  (c) fechamento         {len(calculaveis)} de {len(linhas)} e com "
          f"s > 0 e s − d > 0 em toda a faixa")
    for l in linhas:
        if not l["fechamento"]:
            print(f"      e = {l['e']:.3f}: {l['motivo']}")
    if fronteira is not None:
        print(f"  fronteira da tração (bissecção): e = {fronteira:.6f} mm, "
              f"menor extensão = "
              f"{ve_extensao_minima(fronteira, geo, theta_pose, x_pose, theta):.1e} mm")
    print(f"  trabalho virtual máximo na grade: "
          f"{max(l['trabalho_virtual'] for l in calculaveis):.1e} mm/rad")

    # concordância com a extração (só se ela existir)
    otimo = None
    if patente is None:
        print(f"\nExtração da Fig. 16/17 da EP 3 504 033: NÃO ENCONTRADA "
              f"({caminho_extracao}).")
        print("  Sem RMSE e sem critério de ótimo: o relatório só descreve o")
        print("  efeito geométrico de e. Para ativar, grave o CSV pt-BR")
        print("  'theta;torque' nesse caminho e rode de novo.")
    else:
        otimo = min(calculaveis, key=lambda l: l["rmse"])
        for posto, l in enumerate(sorted(calculaveis, key=lambda l: l["rmse"]),
                                  start=1):
            l["posto_rmse"] = posto
        g_ref = sinal_patente*calculate_torque_curve(
            1.0, E_ILUSTRATIVO, geo, theta_pose, x_pose, patente["theta"])["tau"]
        k_fechado = float((g_ref @ patente["torque"])/(g_ref @ g_ref))
        print(f"\nConcordância com a extração ({patente['fonte']}, "
              f"{len(patente['theta'])} pontos), k congelado em {k:g}:")
        print("  ATENÇÃO: k é ILUSTRATIVO; o RMSE só tem sentido com k identificado.")
        print(f"  menor RMSE: e = {otimo['e']:.3f} mm  RMSE {otimo['rmse']:.4f}  "
              f"R² {otimo['r2']:.5f}  viável: {otimo['viavel']}"
              + (f" (falha: {otimo['motivo']})" if not otimo["viavel"] else ""))
        print("  ACHADO DIAGNÓSTICO, não adoção: não cria E_CALIBRADO.")
        for folga in VE_FOLGAS:
            p = ve_plato(linhas, folga)
            print(f"  platô RMSE ≤ {folga:.2f}·mín: e de {p['min']:.3f} a "
                  f"{p['max']:.3f} mm, largura {p['largura']:.3f} mm, {p['n']} e"
                  f"{'' if p['contigua'] else ', NÃO contíguo'}")
        print(f"  Consistência (k, e): k pela forma fechada em e = "
              f"{E_ILUSTRATIVO:g} = {k_fechado:.4f} (congelado: {k:g})")

    # família e valores notáveis
    print("\nFamília τ/k (k não entra), e = "
          + ", ".join(f"{e:g}" for e in familia) + " mm:")
    for theta_no, valor in nos["nos"]:
        print(f"  nó (espalhamento mínimo local): θ = {theta_no:.2f}°, "
              f"espalhamento {valor:.3e} N·m por N/mm")
    print(f"  abertura máxima: θ = {nos['maximo'][0]:.2f}°, espalhamento "
          f"{nos['maximo'][1]:.3e} N·m por N/mm")
    print(f"  (malha de θ com passo {theta[1] - theta[0]:.2f}°). Pontos extraídos "
          f"perto dos nós quase não carregam informação sobre e.")

    papeis = [("familia", e) for e in familia] + [("E_ILUSTRATIVO", E_ILUSTRATIVO)]
    for nome in ("tracao", "viavel"):
        if faixas[nome]:
            papeis += [(f"{nome}_min", faixas[nome]["min"]),
                       (f"{nome}_max", faixas[nome]["max"])]
    if fronteira is not None:
        papeis.append(("fronteira_tracao", fronteira))
    if otimo is not None:
        papeis.append(("e_menor_rmse", otimo["e"]))
    agrupados = {}
    for nome, e in papeis:
        agrupados.setdefault(round(float(e), 9), []).append(nome)
    notaveis = []
    for chave in sorted(agrupados):
        v = dict(linha_de.get(chave) or ve_avaliar_e(
            chave, geo, k, theta_pose, x_pose, theta, patente, sinal_patente,
            VE_TOL_TV))
        v["papeis"] = "+".join(agrupados[chave])
        if patente is not None and chave not in linha_de:
            v["posto_rmse"] = "fora da grade"
        notaveis.append(v)

    def num(v, fmt):
        return "—" if v is None else format(v, fmt)

    print("\nPor e (família e notáveis; τ/k em N·m por N/mm; flags a=tração "
          "c=fechamento d=trab. virtual):")
    print(f"{'e (mm)':>10} {'d':>7} {'s0':>8} {'q* (°)':>8} {'%II':>5} "
          f"{'τ/k pico':>9} {'θ pico':>7} {'x_min':>7} {'x_max':>7} "
          f"{'θ x_max':>7} {'tração em θ':>15} {'flags':>5}  papéis")
    for v in notaveis:
        if not v["fechamento"]:
            print(f"{v['e']:10.4f}  sem fechamento: {v['motivo']}  {v['papeis']}")
            continue
        flags = "".join(c if v.get(kk) else "-" for c, kk in
                        (("a", "tracao"), ("c", "fechamento"), ("d", "tv_ok")))
        faixa_q = (f"{num(v['theta_tracao_min'], '.1f')}–"
                   f"{num(v['theta_tracao_max'], '.1f')}")
        print(f"{v['e']:10.4f} {v['d']:7.3f} {v['s0']:8.3f} "
              f"{num(v['q_estrela'], '8.3f'):>8} {100*v['frac_contato']:5.1f} "
              f"{v['tau_k_pico']:9.5f} {v['theta_pico']:7.2f} "
              f"{v['x_min']:7.2f} {v['x_max']:7.2f} {v['theta_x_max']:7.2f} "
              f"{faixa_q:>15} {flags:>5}  {v['papeis']}")
        if v["trechos_frouxos"]:
            print(f"{'':10}   ↳ elástico frouxo em θ = {v['trechos_frouxos']}°")
    print("%II = fração da faixa em contato com o 78. 'tração em θ' = menor e "
          "maior θ com s − s0 ≥ 0.")
    if patente is not None:
        print(f"\n{'e (mm)':>10} {'posto':>6} {'RMSE':>9} {'MAE':>9} "
              f"{'erro máx':>9} {'θ erro':>7} {'R²':>8}")
        for v in notaveis:
            if v["fechamento"]:
                print(f"{v['e']:10.4f} {v.get('posto_rmse', ''):>6} "
                      f"{v['rmse']:9.4f} {v['mae']:9.4f} {v['erro_max']:9.4f} "
                      f"{v['theta_erro_max']:7.2f} {v['r2']:8.5f}")

    # ---------------------------------------------------------- arquivos
    pasta = Path(pasta)
    pasta.mkdir(exist_ok=True)
    arquivos = [pasta/"ve_varredura_e.csv", pasta/"ve_e_notaveis.csv"]
    colunas = ["e", "fechamento", "tracao", "tv_ok", "viavel", "motivo", "d",
               "s0", "q_estrela", "frac_contato", "tau_k_pico", "theta_pico",
               "tau_k_min", "theta_tau_k_min", "x_min", "theta_x_min", "x_max",
               "theta_x_max", "theta_tracao_min", "theta_tracao_max",
               "trechos_frouxos", "braco_max", "tv_I", "tv_II",
               "trabalho_virtual", "erro_linear_K"]
    if patente is not None:
        colunas += ["rmse", "posto_rmse", "mae", "erro_max", "theta_erro_max",
                    "r2"]
    ve_salvar_csv(arquivos[0], linhas, colunas)
    ve_salvar_csv(arquivos[1], notaveis, ["e", "papeis"] + colunas[1:])
    if plot_familia:
        arquivos.append(pasta/"ve_familia_curvas.png")
        ve_plot_familia(familia, nos, linhas_familia, theta, patente, k,
                        sinal_patente, arquivos[-1])
    print("\nArquivos gerados pela varredura:")
    for a in arquivos:
        print(f"  {a}")
    return {"linhas": linhas, "faixas": faixas, "notaveis": notaveis,
            "familia": nos, "fronteira_tracao": fronteira, "otimo": otimo,
            "erro_ancora": erro_ancora, "patente": patente}


# ======================================================================
# 10. Relatório
# ======================================================================

VE_RODAR = True            # desligar para executar sem varrer
VE_PLOT_FAMILIA = True     # entrega principal: família τ/k × q

if __name__ == "__main__":
    par = PARAMETROS_ILUSTRATIVOS
    geo = montar_geometria(par["C1"], par["C2"], par["ALPHA"], par["GAMMA"],
                           par["P"], par["PHI"])
    k, x_pose, theta_pose = par["K"], par["X_POSE"], par["THETA_POSE"]
    theta = np.append(np.arange(par["THETA_MIN"], par["THETA_MAX"], 0.5),
                      par["THETA_MAX"])
    e = E_ILUSTRATIVO
    bx, by = calculate_base_vector(geo)

    print("=" * 78)
    print("PARÂMETROS ILUSTRATIVOS — NÃO MEDIDOS, NADA CALIBRADO")
    print("=" * 78)
    for nome, valor in par.items():
        print(f"  {nome:13s} = {valor:g}")
    print(f"  E_CAD         = {E_CAD}  (documental, sem medida)")
    print(f"  E_ILUSTRATIVO = {e:g} mm  (só para o código rodar)")
    print(f"Derivados em e = {e:g} mm: B = ({bx:.3f}; {by:.3f}) mm, "
          f"|B| = {np.hypot(bx, by):.3f} mm, d = {calculate_d(e, geo):.3f} mm, "
          f"s0 = {s_zero(e, geo, theta_pose, x_pose):.3f} mm")

    a = autotestes(e, geo, k, theta_pose, x_pose, theta,
                   e_extra=(e + 10.0, 0.5*e, 2.0*e))
    print("\nAutotestes:")
    print(f"  1. resíduos regime I:    max|f1| = {a['residuo_f1']:.1e}, "
          f"max|f2| = {a['residuo_f2']:.1e} mm")
    print(f"     resíduos regime II:   max|f3| = {a['residuo_f3']:.1e}, "
          f"max|f4| = {a['residuo_f4']:.1e} mm  "
          f"(pontos na faixa: {a['n_regime_I']} em I, {a['n_regime_II']} em II)")
    print(f"     d pela fórmula × |P − C78|: {a['d_duas_vias']:.1e} mm")
    print(f"  2. trabalho virtual:     max|ds/dq + τ/F| = {a['tv_I']:.1e} (I), "
          f"{a['tv_II'] if a['tv_II'] is None else format(a['tv_II'], '.1e')} "
          f"(II) mm/rad")
    print(f"  3. continuidade em q* = {np.degrees(a['q_estrela']):.6f}°: "
          f"|s_I − s_II| = {a['continuidade_s']:.1e} mm, "
          f"|τ_I − τ_II|/F = {a['continuidade_tau']:.1e} mm; "
          f"ordem II (q ≤ q*) / I (q > q*) conferida")
    pz = a["p_zero"]
    print(f"  4. p = 0: q* fechado {np.degrees(pz['q_fechado']):.6f}° × numérico "
          f"(erro {pz['erro_q']:.1e} rad, igual para todo e testado); "
          f"|s − (|B| + e)| = {pz['erro_s']:.1e} mm; max|τ_II|/F = "
          f"{pz['tau_max']:.1e} mm")
    if a["frouxo"]:
        print("  5. tração: o elástico AFROUXA em θ = "
              + ", ".join(f"{i:.2f}° a {f:.2f}°" for i, f in a["frouxo"]))
    else:
        print("  5. tração: x ≥ 0 em toda a faixa")
    print(f"  6. τ produto vetorial × fórmula escalar: {a['tau_duas_vias']:.1e} N·m")
    print(f"     linearidade em k: {a['erro_linear_K']:.1e} N·m")
    print(f"  7. guarda de e: curvas diferem (máx. {a['guarda_e']:.3e} N·m por "
          f"N/mm); ancoragem x(q_pose) = X_POSE, erro {a['ancoragem']:.1e} mm; "
          f"e obrigatório em toda a cadeia (TypeError sem e)")

    # tabela em ângulos representativos
    angulos = np.array(sorted({par["THETA_MIN"], np.degrees(a["q_estrela"]),
                               theta_pose, 120.0, 150.0, 180.0,
                               par["THETA_MAX"]}))
    r = calculate_torque_curve(k, e, geo, theta_pose, x_pose, angulos)
    print(f"\nTabela em e = {e:g} mm, k = {k:g} N/mm (ilustrativos):")
    print("   θ(°) reg    ψ(°)    s(mm)  s−d(mm)   x(mm)    F(N)  braço(mm)"
          "   τ(N·m)  τ/k(N·m por N/mm)")
    for i, th in enumerate(angulos):
        smd = r["s_menos_d"][i]
        print(f"{th:7.2f} {'II' if r['contato'][i] else 'I':>3} "
              f"{np.degrees(r['psi'][i]):7.2f} {r['s'][i]:8.3f} "
              f"{'—' if np.isnan(smd) else format(smd, '.3f'):>8} "
              f"{r['x'][i]:7.3f} {r['force'][i]:7.2f} {r['braco'][i]:10.4f} "
              f"{r['tau'][i]:8.4f} {r['tau'][i]/k:12.6f}")
    print("τ positivo = anti-horário = sentido de q crescente. braço = τ/F, só "
          "relatório.")

    if VE_RODAR:
        varredura_e(geo, k, theta_pose, x_pose, VE_THETA, VE_GRID, VE_FAMILIA,
                    EXTRACAO_EP, par["SINAL_PATENTE"],
                    Path(__file__).parent/"results", VE_PLOT_FAMILIA)
