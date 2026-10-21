"""
Modelo de torque do exoesqueleto de ombro Ottobock (iX Shoulder Air,
patente EP 3 504 033 B1): elemento elástico + alavanca com cotovelo + pino
78. Modelo plano, no plano sagital. Adaptado de torque_model.py (SuitX: cabo
+ tambor + braço), com a mesma arquitetura e disciplina.

Cadeia de cálculo (cada etapa é uma função abaixo):

    θ*  →  q = θ* + 90° + δ  →  g = (P − A) × (C78 − A)  →  regime (I / II)
                                                              │
                    ┌─────────────────────────────────────────┘
                    ├→ s, ψ  (forma fechada do regime)  →  x = max(s − s0, 0)
                    │                                         └→ F = k·x
                    └→ b (P no regime I, 78 no regime II), F⃗ = −F·ê(ψ)
                                                              └→ τ = (b × F⃗)_z
    θ*  →  τ_peso: membro humano (de Leva) + braço do exo, rígidos em O
    Fig. 16 (exo/peso, sem escala)  →  s0 (forma c)  →  k_40 (alvo de 40 %)

Mecanismo. O elástico vai da ancoragem A (bastão do tronco) ao ponto P da
alavanca presa ao braço. A alavanca tem um cotovelo: um trecho e a partir do
pivô O e, depois dele, um trecho rígido C3 girado de β. Perto do pivô há um
pino (elemento 78), preso ao braço. Acima de q* o elástico é reto (regime
I); abaixo de q* ele encosta no 78 e se divide em A → 78 e 78 → P (regime
II). Não há tambor nem tangência. HIPÓTESE: pino 78 pontual e sem atrito
(mesma tração nos trechos A → 78 e 78 → P).

Referencial. Origem no pivô O (centro do ombro = eixo da junta 20); x
anterior, y para cima, z sai do plano. Todo ângulo é medido a partir de +x,
no sentido anti-horário. ê(a) = (cos a, sen a). Posições em relação a O:
    A   = −B                     (B = vetor fixo A → O, calculate_base_vector)
    P   =  e·ê(q) + C3·ê(q + β)  (fim do cotovelo da alavanca)
    C78 =  p·ê(q + φ)            (gira com o braço)
Essas posições são as que as equações de circuito f1…f4 implicam.

Ângulos. q é o ângulo do trecho e a partir de +x (variável interna). θ* é a
anteversão do braço: 0° = braço pendente, 90° = horizontal à frente (entrada
do usuário e eixo dos gráficos). q = θ* + 90° + δ (calculate_q), com δ fixo
derivado da pose do CAD. O braço aponta na direção θ* − 90° (direcao_braco).

Unidades. Comprimentos em mm. Ângulos em graus na entrada (θ*, parâmetros)
e em radianos dentro das contas; cada conversão é feita uma única vez (θ* em
calculate_q, parâmetros em montar_geometria). Com k em N/mm, F sai em N e τ
em N·m (b × F⃗ em N·mm, dividido por 1000). τ/k sai em N·m por N/mm.

Sinal. τ positivo = anti-horário = sentido de θ* crescente (subida do
braço). O torque do peso é negativo enquanto o CG está à frente do pivô,
0° < θ* + a_CG < 180°, com a_CG o ângulo do CG em relação ao eixo do braço
(a_CG = 0 só com o membro humano); as razões e o alvo usam |τ_peso|.

Origem dos números. Cada constante diz de onde veio: CAD (medido no
modelo), de Leva Tab. 4 (literatura), derivado (calculado no código a partir
de outros), AJUSTADO (sai de um ajuste a dados), hipótese ou ILUSTRATIVO.
Nenhum valor ajustado aparece como medido. e é o parâmetro varrido e faz o
papel que h fazia no original: é argumento obrigatório em toda a cadeia.
Não existe E_CALIBRADO.
"""
import argparse
import unicodedata
from pathlib import Path
from typing import NamedTuple

import numpy as np

# ==========================================================================
# PARÂMETROS DO CAD — cada valor com a origem comentada
# ==========================================================================
# Todos entram na cadeia como argumentos explícitos (montar_geometria e
# assinaturas das funções); nenhuma função lê este dicionário.
PARAMETROS_CAD = {
    # vetor fixo A → O: B = C1·ê(−α) + C2·ê(γ). α é derivado (derivar_alpha)
    "C1": 28.978,            # mm, CAD
    "C2": 340.455,           # mm, CAD
    "GAMMA": 80.739,         # graus, CAD
    # alavanca: trecho e (E_CAD, abaixo) + cotovelo rígido C3 girado de β
    "C3": 14.907,            # mm, CAD
    "BETA": -49.647,         # graus, CAD (ângulo interno do cotovelo 130,353°)
    # pino 78
    "P": 7.754,              # mm, CAD (distância O → 78)
    # pose do CAD
    "Q_POSE": 160.487,       # graus, CAD (q na pose)
    "S_POSE": 359.768,       # mm, CAD (s na pose; conferido no autoteste)
    "PHI_ABS_POSE": 277.937,  # graus, CAD (ângulo do 78 a partir de +x, na pose)
    "BRACO_POSE": -7.962,    # graus, CAD: braço com a horizontal, positivo
                             # acima. SINAL A CONFIRMAR: o código funciona com
                             # o oposto trocando só esta constante.
}

# ----------------------------------------------------- parâmetro varrido e
E_CAD = 34.785        # mm, CAD: trecho O → cotovelo da alavanca. Varrido.

# ----------------------------------------------------- faixa de operação
THETA_MIN, THETA_MAX = 0.0, 180.0  # graus θ*, enunciado da tarefa

# ------------------------------------------------------------- elástico
# s0 é PARÂMETRO DE PROJETO, escolhido por uma das três formas (definir_s0):
#   (a) constante; (b) pré-tensão num ângulo; (c) ajustado à Fig. 16.
S0_PROVISORIO = PARAMETROS_CAD["S_POSE"]  # mm, forma (a): o s da pose do CAD.
                                          # PROVISÓRIO, não é medida de s0.
THETA_PRE = None      # graus θ*, forma (b): NÃO DEFINIDO (passar por argumento)
X_PRE = None          # mm, forma (b): NÃO DEFINIDO (passar por argumento)
K_ILUSTRATIVO = 9.0   # N/mm, formas (a) e (b). ILUSTRATIVO, NÃO MEDIDO.

# ---------------------------------------------- membro humano (de Leva)
# de Leva, P. (1996), J. Biomech. 29(9):1223-1230, Tab. 4, homem, cotovelo
# estendido. (segmento, massa % corporal, L ref mm, CM % de L a partir do
# proximal, r transversal % de L). Segmentos em série a partir de O,
# alinhados ao braço.
DE_LEVA_TAB4 = (
    ("braço", 2.71, 281.7, 57.72, 26.9),       # de Leva Tab. 4
    ("antebraço", 1.62, 268.9, 45.74, 26.5),   # de Leva Tab. 4
    ("mão", 0.61, 86.2, 79.00, 51.3),          # de Leva Tab. 4
)
ESTATURA_REF_DE_LEVA = 1741.0  # mm, de Leva Tab. 4 (comprimentos escalam com
                               # estatura/1741)
MASSA_CORPORAL = 73.0          # kg, de Leva Tab. 4 (sujeito de referência)
ESTATURA = 1741.0              # mm, de Leva Tab. 4 (sujeito de referência)
GRAVIDADE = 9.80665            # m/s², valor padrão (gravidade = −y)

# ------------------------------------------- braço do exo (elemento 8)
MASSA_BRACO_EXO = 163.951                 # g, CAD, Fusion
CG_BRACO_EXO_FUSION = (69.249, 151.559)   # mm, CAD, Fusion (referencial do Fusion)
IZZ_CG_BRACO_EXO = 9.659e5                # g·mm², CAD, Fusion
O_FUSION = None   # mm, centro da junta 20 no referencial do Fusion. NÃO MEDIDO:
                  # enquanto for None, o braço do exo fica fora do peso e da
                  # inércia. Preenchido, o CG relativo a O é
                  # CG_BRACO_EXO_FUSION − O_FUSION, na pose do CAD.
                  # HIPÓTESE: eixos do Fusion paralelos aos do modelo (x
                  # anterior, y para cima, z = eixo da junta 20) e
                  # IZZ_CG_BRACO_EXO em torno de z.

# ---------------------------------------------- Fig. 16 e alvo de projeto
FIG16_CSV = Path(__file__).parent/"fig16_curvas.csv"  # digitalização do autor
FIG16_FAIXA_AJUSTE = (20.0, 165.0)    # graus θ*, ESTRITO (enunciado: abaixo de
                                      # 20° o modelo do CAD está no regime II;
                                      # perto de 180°, τ_peso → 0)
FIG16_GRADE_S0 = (0.0, 390.0, 0.01)   # mm: início, fim, passo da busca de s0
FIG16_FOLGA_FAIXA = 1.01              # faixa de identificação: RMS ≤ 1,01·mín
ALVO_FRACAO = 0.4     # HIPÓTESE de projeto: 0,4·|τ_peso| (o fabricante alega
                      # reduzir até 40 % da carga no ombro), não dado medido
THETA_ALVO = 90.0     # graus θ*, onde k_40 iguala τ_exo ao alvo
CURVA_PROJETO = "tracejada"   # curva da Fig. 16 do projeto padrão
FORMA_S0_PROJETO = "c"        # forma de s0 do projeto padrão

# Gancho antigo para uma curva de TORQUE extraída (theta;torque). A Fig. 16 é
# uma razão sem escala e entra só no ajuste de s0 (load_fig16).
EXTRACAO_EP = Path(__file__).parent/"ep3504033_fig16_17.csv"
SINAL_PATENTE = 1.0   # +1: τ anti-horário positivo na curva extraída. A CONFIRMAR


# ======================================================================
# 1. Geometria fixa e mapeamento θ* → q
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
    c3: float     # mm, cotovelo da alavanca
    beta: float   # rad, giro do cotovelo em relação a e
    p: float      # mm, distância O → 78
    phi: float    # rad, ângulo fixo do 78 em relação a e
    delta: float  # rad, q = θ* + 90° + δ


def derivar_alpha(gamma):
    """α = 90° − γ [graus]: C1 ⟂ C2 no CAD."""
    return 90.0 - gamma


def derivar_phi(phi_abs_pose, q_pose):
    """φ = ângulo do 78 em relação a e [graus], em [0°, 360°)."""
    return (phi_abs_pose - q_pose) % 360.0


def derivar_delta(q_pose, braco_pose):
    """δ = Q_POSE − (180° + BRACO_POSE) [graus].

    O braço aponta na direção θ* − 90° = BRACO_POSE na pose, e e aponta na
    direção q; logo q − (θ* − 90°) = 180° + δ é fixo.
    """
    return q_pose - (180.0 + braco_pose)


def derivar_theta_pose(braco_pose):
    """θ* na pose do CAD = 90° + BRACO_POSE [graus]."""
    return 90.0 + braco_pose


def montar_geometria(c1, c2, alpha, gamma, c3, beta, p, phi, delta):
    """Monta a Geometria a partir de ângulos em graus (única conversão)."""
    if p < 0 or c3 < 0:
        raise ValueError("p e C3 são distâncias: precisam ser ≥ 0")
    return Geometria(float(c1), float(c2), np.radians(alpha),
                     np.radians(gamma), float(c3), np.radians(beta),
                     float(p), np.radians(phi), np.radians(delta))


def calculate_q(theta_star, geo):
    """Mapeamento θ* → q [rad], com θ* em graus: q = θ* + 90° + δ.

    q é o ângulo absoluto do trecho e. Trocar só esta função se o mapeamento
    mudar; o resto da cadeia trabalha em q e não muda.
    """
    return np.radians(np.asarray(theta_star, dtype=float)) + np.pi/2 + geo.delta


def theta_star_de_q(q, geo):
    """Inversa de calculate_q [graus], só para relatório e gráficos."""
    return np.degrees(np.asarray(q, dtype=float) - np.pi/2 - geo.delta)


def direcao_braco(theta_star):
    """Direção do eixo do braço a partir de +x [rad]: θ* − 90°."""
    return np.radians(np.asarray(theta_star, dtype=float) - 90.0)


def versor(angulo):
    """ê(a) = (cos a, sen a), empilhado no eixo 0."""
    return np.array([np.cos(angulo), np.sin(angulo)])


def calculate_base_vector(geo):
    """B = C1·ê(−α) + C2·ê(γ) = (C1 cos α + C2 cos γ, −C1 sen α + C2 sen γ):
    vetor fixo A → O. São os termos constantes de f1…f4."""
    return (geo.c1*np.cos(geo.alpha) + geo.c2*np.cos(geo.gamma),
            -geo.c1*np.sin(geo.alpha) + geo.c2*np.sin(geo.gamma))


def ponto_A(geo):
    """Ancoragem A em relação ao pivô: A = −B [mm]."""
    bx, by = calculate_base_vector(geo)
    return np.array([-bx, -by])


def ponto_P(q, e, geo):
    """Ponto P da alavanca: P = e·ê(q) + C3·ê(q + β) [mm]."""
    return e*versor(q) + geo.c3*versor(q + geo.beta)


def ponto_78(q, geo):
    """Centro do pino 78: C78 = p·ê(q + φ) [mm]. Gira com o braço."""
    return geo.p*versor(q + geo.phi)


def angulo_OP(e, geo):
    """Ângulo fixo de OP em relação a e [rad]: arg(e + C3·ê(β))."""
    return np.arctan2(geo.c3*np.sin(geo.beta), e + geo.c3*np.cos(geo.beta))


def raio_OP(e, geo):
    """|OP| = |e + C3·ê(β)| [mm]."""
    return np.hypot(e + geo.c3*np.cos(geo.beta), geo.c3*np.sin(geo.beta))


def calculate_d(e, geo):
    """d: trecho 78 → P [mm], d = |P − C78|, a partir dos pontos.

    P e C78 giram juntos com q, então d não depende de q (constante para cada
    e); calcula-se em q = 0.
    """
    return float(np.hypot(*(ponto_P(0.0, e, geo) - ponto_78(0.0, geo))))


def calculate_x78(e, geo):
    """x_78 = √(p² + e² − 2·p·e·cos φ) [mm]: distância 78 → cotovelo.

    SÓ RELATÓRIO: NÃO é a extensão do elástico.
    """
    return np.sqrt(geo.p**2 + e**2 - 2*geo.p*e*np.cos(geo.phi))


# ======================================================================
# 2. Troca de regime: alinhamento A, 78, P
# ======================================================================

def produto_contato(q, e, geo):
    """g = (P − A) × (C78 − A), componente z [mm²].

    g = 0 quando A, 78 e P estão alinhados. Lado do contato: no limite p = 0
    (78 no pivô), g = |OP|·|B|·sen(q_B − q − ε), com q_B = atan2(By, Bx) e
    ε = angulo_OP; g < 0 para q > q* (elástico livre) e g > 0 para q < q* (o
    78 estaria do outro lado da linha A → P, logo empurra o elástico). Essa
    convenção de lado vale para todo p; q_estrela_numerico confere que a
    ordem dos regimes na faixa é a do enunciado (II abaixo de q*, I acima).
    """
    a = ponto_A(geo).reshape(2, *([1]*np.ndim(q)))
    pp = ponto_P(q, e, geo) - a
    cc = ponto_78(q, geo) - a
    return pp[0]*cc[1] - pp[1]*cc[0]


def em_contato(q, e, geo):
    """Regime II (elástico encostado no 78) ⇔ g ≥ 0. Nenhum q* é imposto."""
    return produto_contato(q, e, geo) >= 0.0


def q_estrela_fechado(e, geo):
    """q* em forma fechada, só para p = 0 [rad].

    Com o 78 no pivô, o alinhamento A, O, P (O entre A e P) é OP ∥ B:
    q* = atan2(By, Bx) − ε(e), com ε = angulo_OP. A direção de OP em q*
    não depende de e; q* depende de e só por ε(e).
    """
    if geo.p != 0.0:
        raise ValueError("forma fechada de q* só existe para p = 0")
    bx, by = calculate_base_vector(geo)
    return np.arctan2(by, bx) - angulo_OP(e, geo)


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
    entre = np.dot(c78 - ponto_A(geo), ponto_P(q_est, e, geo) - c78)
    assert entre > 0, "alinhamento em q* não tem o 78 entre A e P"
    return q_est


# ======================================================================
# 3. Equações de circuito: soluções fechadas e resíduos
# ======================================================================

def resolver_regime_I(q, e, geo):
    """Regime I (elástico livre): s·ê(ψ) = B + e·ê(q) + C3·ê(q + β).

    s = |A → P| e ψ = direção de A → P.
    """
    bx, by = calculate_base_vector(geo)
    px, py = ponto_P(q, e, geo)
    vx, vy = bx + px, by + py
    return np.hypot(vx, vy), np.arctan2(vy, vx)


def resolver_regime_II(q, e, geo):
    """Regime II (contato com o 78): (s − d)·ê(ψ) = B + p·ê(q + φ).

    s − d = |A → 78|, ψ = direção de A → 78 e s = (s − d) + d(e).
    """
    bx, by = calculate_base_vector(geo)
    ux = bx + geo.p*np.cos(q + geo.phi)
    uy = by + geo.p*np.sin(q + geo.phi)
    return calculate_d(e, geo) + np.hypot(ux, uy), np.arctan2(uy, ux)


def calculate_closure_residuals_I(q, s, psi, e, geo):
    """f1 e f2 como escritos, para conferir a solução (devem dar ≈ 0)."""
    f1 = (geo.c1*np.cos(geo.alpha) + geo.c2*np.cos(geo.gamma)
          + e*np.cos(q) + geo.c3*np.cos(q + geo.beta) - s*np.cos(psi))
    f2 = (-geo.c1*np.sin(geo.alpha) + geo.c2*np.sin(geo.gamma)
          + e*np.sin(q) + geo.c3*np.sin(q + geo.beta) - s*np.sin(psi))
    return f1, f2


def calculate_closure_residuals_II(q, s, psi, e, geo):
    """f3 e f4 como escritos, para conferir a solução (devem dar ≈ 0)."""
    d = calculate_d(e, geo)
    f3 = (geo.c1*np.cos(geo.alpha) + geo.c2*np.cos(geo.gamma)
          + geo.p*np.cos(q + geo.phi) - (s - d)*np.cos(psi))
    f4 = (-geo.c1*np.sin(geo.alpha) + geo.c2*np.sin(geo.gamma)
          + geo.p*np.sin(q + geo.phi) - (s - d)*np.sin(psi))
    return f3, f4


def resolver_circuito(q, e, geo):
    """Regime de cada q (pelo sinal de g) e s, ψ da solução desse regime."""
    contato = em_contato(q, e, geo)
    s1, psi1 = resolver_regime_I(q, e, geo)
    s2, psi2 = resolver_regime_II(q, e, geo)
    return contato, np.where(contato, s2, s1), np.where(contato, psi2, psi1)


# ======================================================================
# 4. Elástico: definição de s0, extensão e força
# ======================================================================

class DefinicaoS0(NamedTuple):
    """Como s0 (comprimento em que a tensão começa) é definido.

    forma "a": constante s0_fixo (ex.: S0_PROVISORIO).
    forma "b": pré-tensão num ângulo, s0 = s(θ*_pre, e) − x_pre.
    forma "c": ajustado à forma de uma curva da Fig. 16 (s0_fixo sai de
               ajustar_fig16 e fica congelado para todo e).
    origem: texto de rastreabilidade, impresso no relatório.
    """
    forma: str
    s0_fixo: float | None
    theta_pre: float | None
    x_pre: float | None
    origem: str


def definir_s0(forma, s0_fixo=None, theta_pre=None, x_pre=None, origem=""):
    """Valida e monta a DefinicaoS0 (nenhum valor é suposto)."""
    if forma in ("a", "c"):
        if s0_fixo is None or theta_pre is not None or x_pre is not None:
            raise ValueError(f"forma ({forma}) pede só s0_fixo")
    elif forma == "b":
        if theta_pre is None or x_pre is None or s0_fixo is not None:
            raise ValueError("forma (b) pede theta_pre e x_pre")
    else:
        raise ValueError("forma de s0 deve ser 'a', 'b' ou 'c'")
    return DefinicaoS0(forma, None if s0_fixo is None else float(s0_fixo),
                       None if theta_pre is None else float(theta_pre),
                       None if x_pre is None else float(x_pre), origem)


def s_zero(e, geo, defs0):
    """Comprimento em que o elástico atinge o comprimento livre [mm].

    Formas (a) e (c): s0 fixo, igual para todo e. Forma (b): s0(e) =
    s(θ*_pre, e) − X_PRE, a pré-tensão em θ*_pre é fixa e o comprimento livre
    acompanha e.
    """
    if defs0.forma == "b":
        _, s_pre, _ = resolver_circuito(calculate_q(defs0.theta_pre, geo), e, geo)
        return float(s_pre) - defs0.x_pre
    return defs0.s0_fixo


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
# 5. Torque do elástico
# ======================================================================

def ponto_aplicacao(q, e, geo, contato):
    """b⃗: vetor do pivô ao ponto de aplicação da força do trecho A → (…) [mm].

    Regime I: b⃗ = P. Regime II: b⃗ = C78. O trecho 78 → P é interno ao braço
    (as forças em P e no 78 se anulam, colineares) e não entra no torque.
    """
    return np.where(contato, ponto_78(q, geo), ponto_P(q, e, geo))


def vetor_forca(force, psi):
    """F⃗ = −F·ê(ψ): o elástico puxa o ponto de aplicação para A [N]."""
    return -force*versor(psi)


def torque_produto_vetorial(b_vector, f_vector):
    """τ = componente z de b × F⃗ = bx·Fy − by·Fx. Positivo = anti-horário."""
    return b_vector[0]*f_vector[1] - b_vector[1]*f_vector[0]


def braco_momento(q, psi, e, geo, contato):
    """Braço de momento escalar com sinal, b = τ/F [mm]. SÓ PARA O RELATÓRIO
    e para o modelo da Fig. 16. b > 0 assiste a subida do braço.

    Regime I: e·sen(q − ψ) + C3·sen(q + β − ψ). Regime II: p·sen(q + φ − ψ).
    A cadeia calcula τ pelo produto vetorial; esta fórmula serve de
    conferência (autoteste 6).
    """
    return np.where(contato, geo.p*np.sin(q + geo.phi - psi),
                    e*np.sin(q - psi) + geo.c3*np.sin(q + geo.beta - psi))


# ======================================================================
# 6. Peso e inércia do conjunto que gira com o braço
# ======================================================================

def montar_conjunto_braco(estatura_mm, massa_corporal_kg, segmentos,
                          braco_exo, o_fusion, braco_pose_grau):
    """Membro humano (de Leva) e, se o_fusion não for None, o braço do exo,
    rígidos em torno de O. Devolve massa, CG e Izz do membro humano e do
    total.

    segmentos: tabela de de Leva (DE_LEVA_TAB4); comprimentos escalam com
               estatura/ESTATURA_REF_DE_LEVA e massas = % × massa corporal.
               Em série a partir de O, alinhados ao braço. Izz(CG) =
               m·(r_transversal·L)².
    braco_exo: (massa g, CG no Fusion mm, Izz no CG g·mm²).
    o_fusion:  centro da junta 20 no Fusion [mm] ou None (exo fora do total).
    braco_pose_grau: direção do braço na pose do CAD (BRACO_POSE), para
               levar o CG do exo ao eixo do braço.

    O CG sai como distância a O e ângulo em relação ao eixo do braço
    (positivo anti-horário). Izz em O por Steiner: Izz(O) = Σ[Izz(CG) + m·d²].
    Unidades: kg, mm, kg·mm² nas contas; o relatório converte para kg·m².
    """
    escala = estatura_mm/ESTATURA_REF_DE_LEVA
    corpos, inicio = [], 0.0
    for nome, massa_pct, l_ref, cm_pct, r_pct in segmentos:
        comprimento = l_ref*escala
        m = massa_pct/100.0*massa_corporal_kg
        corpos.append({"nome": nome, "humano": True, "massa": m,
                       "pos": np.array([inicio + cm_pct/100.0*comprimento, 0.0]),
                       "izz_cg": m*(r_pct/100.0*comprimento)**2})
        inicio += comprimento
    if o_fusion is not None:
        massa_g, cg_fusion, izz_g = braco_exo
        rel = np.asarray(cg_fusion, float) - np.asarray(o_fusion, float)
        giro = -np.radians(braco_pose_grau)        # referencial → eixo do braço
        pos = np.array([rel[0]*np.cos(giro) - rel[1]*np.sin(giro),
                        rel[0]*np.sin(giro) + rel[1]*np.cos(giro)])
        corpos.append({"nome": "braço do exo", "humano": False,
                       "massa": massa_g/1000.0, "pos": pos,
                       "izz_cg": izz_g/1000.0})

    def resumo(lista):
        massa = sum(c["massa"] for c in lista)
        cg = sum(c["massa"]*c["pos"] for c in lista)/massa
        izz_o = sum(c["izz_cg"] + c["massa"]*float(c["pos"] @ c["pos"])
                    for c in lista)
        raio = float(np.hypot(*cg))
        return {"massa_kg": massa, "cg_raio_mm": raio,
                "cg_angulo_braco_grau": float(np.degrees(np.arctan2(cg[1], cg[0]))),
                "izz_o_kgm2": izz_o/1e6,
                "izz_cg_kgm2": (izz_o - massa*raio**2)/1e6}

    humano = resumo([c for c in corpos if c["humano"]])
    return {"humano": humano, "total": resumo(corpos),
            "exo_incluido": o_fusion is not None, "corpos": corpos}


def torque_peso(theta_star, massa_kg, cg_raio_mm, cg_angulo_braco_grau):
    """Torque estático do peso do conjunto em relação ao pivô [N·m], com sinal
    (positivo = anti-horário). Independente da cadeia do elástico.

    O conjunto é rígido: o CG gira junto com o braço, r_CG = D·ê(θ* − 90° +
    ângulo do CG em relação ao eixo do braço). Gravidade = −y (referencial).
    τ = (r_CG × m·g⃗)_z = −M·g·D·cos(direção do CG); |τ| = M·g·D·|cos(…)|.
    Todos os argumentos são obrigatórios. Inércia não entra.
    """
    direcao = direcao_braco(theta_star) + np.radians(cg_angulo_braco_grau)
    r_cg = cg_raio_mm*versor(direcao)
    peso = np.array([0.0, -massa_kg*GRAVIDADE]).reshape(2, *([1]*np.ndim(direcao)))
    return torque_produto_vetorial(r_cg, peso)/1000.0


def argumentos_peso(conjunto):
    """(massa, CG raio, CG ângulo) do conjunto usado em τ_peso: o total se o
    braço do exo está incluído, senão só o membro humano."""
    c = conjunto["total"]
    return c["massa_kg"], c["cg_raio_mm"], c["cg_angulo_braco_grau"]


# ======================================================================
# 7. Cadeia completa
# ======================================================================

def generate_graph_torque_theta_relation(force, e, geo, defs0, theta_star):
    """Calcula todas as grandezas para cada θ*.

    force:      força do elástico F, número ou array do tamanho de theta_star.
                Com força unitária, τ·1000 = braço de momento. Para F = k·x
                use calculate_torque_curve.
    e:          trecho O → cotovelo a testar [mm]. Obrigatório.
    geo:        Geometria (montar_geometria).
    defs0:      DefinicaoS0 (definir_s0).
    theta_star: ângulos θ* [graus].
    """
    theta_star = np.asarray(theta_star, dtype=float)

    # cinemática: regime pelo sinal de g, depois a forma fechada do regime
    q = calculate_q(theta_star, geo)
    g = produto_contato(q, e, geo)
    contato, s, psi = resolver_circuito(q, e, geo)
    d = calculate_d(e, geo)
    s_I, psi_I = resolver_regime_I(q, e, geo)
    s_II, psi_II = resolver_regime_II(q, e, geo)
    f1, f2 = calculate_closure_residuals_I(q, s_I, psi_I, e, geo)
    f3, f4 = calculate_closure_residuals_II(q, s_II, psi_II, e, geo)

    # elástico
    s0 = s_zero(e, geo, defs0)
    extensao = calculate_extension(s, s0)
    x = calculate_x(s, s0)

    # força e torque (produto vetorial); braço escalar só para relatório
    f = np.broadcast_to(np.asarray(force, dtype=float), theta_star.shape)
    b_vector = ponto_aplicacao(q, e, geo, contato)                  # mm
    F_vector = vetor_forca(f, psi)                                  # N
    tau = torque_produto_vetorial(b_vector, F_vector)/1000          # N·m
    braco = braco_momento(q, psi, e, geo, contato)                  # mm
    tau_escalar = f*braco/1000                                      # N·m

    return dict(theta_star=theta_star, q=q, g=g, contato=contato, e=e, d=d,
                s=s, psi=psi, s_menos_d=np.where(contato, s - d, np.nan),
                s_I=s_I, psi_I=psi_I, s_II=s_II, psi_II=psi_II,
                f1=f1, f2=f2, f3=f3, f4=f4, s0=s0, extensao=extensao, x=x,
                force=f, b_vector=b_vector, F_vector=F_vector, tau=tau,
                braco=braco, tau_escalar=tau_escalar)


def calculate_torque_curve(k, e, geo, defs0, theta_star):
    """Cadeia completa com F = k·x, para um k e um e dados (τ em N·m)."""
    geometry = generate_graph_torque_theta_relation(0.0, e, geo, defs0,
                                                    theta_star)
    force = spring_force(k, geometry["x"])
    return generate_graph_torque_theta_relation(force, e, geo, defs0,
                                                theta_star)


# ======================================================================
# 8. Fig. 16 da EP 3 504 033: leitura e ajuste de s0 (forma c)
# ======================================================================

def _nome_curva(nome):
    """Nome de curva sem acento e em minúsculas ('Contínua' → 'continua')."""
    sem_acento = unicodedata.normalize("NFKD", nome.strip().lower())
    return "".join(ch for ch in sem_acento if not unicodedata.combining(ch))


def load_fig16(caminho):
    """Lê as curvas digitalizadas da Fig. 16 (razão exo/peso, sem escala).

    CSV: linhas começando com '#' são ignoradas; separador ';', vírgula
    decimal; colunas curva, theta_grau, razao_div, y_lido. θ* é usado como
    está, sem correção. Devolve {curva: {"theta": θ* [graus], "razao":
    [divisões da grade]}}, na ordem do arquivo.
    """
    caminho = Path(caminho)
    linhas = [(n, l) for n, l in enumerate(
                  caminho.read_text(encoding="utf-8-sig").splitlines(), start=1)
              if l.strip() and not l.lstrip().startswith("#")]
    if not linhas:
        raise ValueError(f"{caminho}: arquivo sem dados")
    cabecalho = [c.strip().lower() for c in linhas[0][1].split(";")]
    esperado = ["curva", "theta_grau", "razao_div", "y_lido"]
    if cabecalho[:4] != esperado:
        raise ValueError(f"{caminho}: cabeçalho esperado {';'.join(esperado)}")
    curvas = {}
    for numero, linha in linhas[1:]:
        celulas = [c.strip() for c in linha.split(";")]
        if len(celulas) < 3:
            raise ValueError(f"{caminho}, linha {numero}: esperadas as colunas "
                             f"{';'.join(esperado)}")
        dados = curvas.setdefault(_nome_curva(celulas[0]),
                                  {"theta": [], "razao": []})
        dados["theta"].append(float(celulas[1].replace(",", ".")))
        dados["razao"].append(float(celulas[2].replace(",", ".")))
    return {nome: {k: np.array(v) for k, v in d.items()}
            for nome, d in curvas.items()}


def modelo_fig16(s, b, tau_peso_abs, s0):
    """m(θ*; s0) = max(s − s0, 0)·b / (1000·|τ_peso|), em (N·m por N/mm)/(N·m).

    É τ_exo/|τ_peso| por unidade de k: com k = c_div, a razão em divisões.
    """
    return calculate_x(s, s0)*b/(1000.0*tau_peso_abs)


def escala_fig16(m, r):
    """Escala por mínimos quadrados em forma fechada, c = ⟨m, r⟩/⟨m, m⟩, e o
    erro SSE = Σ(c·m − r)². Se m for todo zero (elástico frouxo em todos os
    pontos), SSE = ∞."""
    mm = float(m @ m)
    if mm == 0.0:
        return np.nan, np.inf
    c = float(m @ r)/mm
    return c, float(np.sum((c*m - r)**2))


def ajustar_fig16(theta_star, razao, e, geo, peso, faixa_theta, grade_s0,
                  folga, alvo, theta_alvo):
    """Ajusta s0 à FORMA de uma curva da Fig. 16 e escolhe k para o alvo.

    Usa só os pontos com faixa_theta[0] < θ* < faixa_theta[1] (estrito).
    s e b vêm do circuito em e; peso = (massa, CG raio, CG ângulo) de
    argumentos_peso. Para cada s0 da grade (início, fim, passo), a escala c e
    o SSE saem em forma fechada (escala_fig16); o melhor ponto da grade é
    refinado por busca limitada de Brent entre os vizinhos. Se o mínimo cai
    na borda da grade, s0 fica na borda e o limite é reportado (s0 < 0 não é
    físico).

    Faixa de identificação: o intervalo de s0, na mesma grade, com RMS ≤
    folga·RMS_min. A forma da curva só define s0 dentro dela.
    k_40 = alvo·|τ_peso(θ_alvo)| / (x(θ_alvo)·b(θ_alvo)/1000), que dá
    τ_exo(θ_alvo) = alvo·|τ_peso(θ_alvo)|.
    """
    from scipy.optimize import minimize_scalar

    theta_star = np.asarray(theta_star, dtype=float)
    razao = np.asarray(razao, dtype=float)
    usar = (theta_star > faixa_theta[0]) & (theta_star < faixa_theta[1])
    th, r = theta_star[usar], razao[usar]
    if r.size < 2:
        raise ValueError(f"só {r.size} ponto(s) em {faixa_theta[0]:g}° < θ* < "
                         f"{faixa_theta[1]:g}°: ajuste impossível")
    q = calculate_q(th, geo)
    contato, s, psi = resolver_circuito(q, e, geo)
    b = braco_momento(q, psi, e, geo, contato)
    tp = np.abs(torque_peso(th, *peso))

    inicio, fim, passo = grade_s0
    grade = inicio + passo*np.arange(int(round((fim - inicio)/passo)) + 1)
    M = calculate_x(s[None, :], grade[:, None])*b/(1000.0*tp)
    mm = np.einsum("ij,ij->i", M, M)
    with np.errstate(divide="ignore", invalid="ignore"):
        c_grade = (M @ r)/mm
        sse_grade = np.sum((c_grade[:, None]*M - r)**2, axis=1)
    sse_grade[mm == 0.0] = np.inf
    i = int(np.argmin(sse_grade))

    def sse_de(s0):
        return escala_fig16(modelo_fig16(s, b, tp, s0), r)[1]

    limite = None
    if i == 0:
        s0, limite = float(grade[0]), "inferior"
    elif i == grade.size - 1:
        s0, limite = float(grade[-1]), "superior"
    else:
        busca = minimize_scalar(sse_de, bounds=(grade[i - 1], grade[i + 1]),
                                method="bounded", options={"xatol": 1e-10})
        s0 = float(busca.x) if busca.fun <= sse_grade[i] else float(grade[i])
    c, sse = escala_fig16(modelo_fig16(s, b, tp, s0), r)
    n = int(r.size)
    rms = np.sqrt(sse/n)
    dentro = np.sqrt(sse_grade/n) <= folga*rms
    idx = np.flatnonzero(dentro)

    q_a = calculate_q(theta_alvo, geo)
    contato_a, s_a, psi_a = resolver_circuito(q_a, e, geo)
    b_a = float(braco_momento(q_a, psi_a, e, geo, contato_a))
    x_a = float(calculate_x(s_a, s0))
    tp_a = float(np.abs(torque_peso(theta_alvo, *peso)))
    # x_alvo ≤ 0 (elástico frouxo em θ_alvo) não tem k que atinja o alvo
    k_alvo = alvo*tp_a/(x_a*b_a/1000.0) if x_a*b_a > 0 else float("nan")

    return {"s0": s0, "limite": limite, "c": c, "sse": sse, "n": n,
            "rms": rms, "rms_max": rms/float(np.max(r)),
            "faixa_s0": (float(grade[idx[0]]), float(grade[idx[-1]])),
            "faixa_contigua": bool(dentro[idx[0]:idx[-1] + 1].all()),
            "faixa_na_borda": bool(idx[0] == 0 or idx[-1] == grade.size - 1),
            "todos_regime_I": bool(not contato.any()),
            "n_regime_II": int(contato.sum()),
            "theta_regime_II": ((float(th[contato].min()), float(th[contato].max()))
                                if contato.any() else None),
            "x_alvo": x_a, "b_alvo": b_a, "tau_peso_alvo": tp_a,
            "k_alvo": k_alvo, "forca_alvo": k_alvo*x_a,
            "usado": usar, "theta_ajuste": th}


def identificar_s0_razoes(fig16, nomes, e, geo, faixa_theta):
    """s0 de cada curva da Fig. 16 pelo espaçamento entre as curvas.

    As curvas vêm do mesmo atuador, com a mesma geometria e só a pré-tensão
    diferente ([0093]). Com o elástico tracionado, r_i(θ*) = G(θ*)·(s(θ*) − s0_i),
    em que G = c·k·b/(1000·|τ_peso|) é comum às curvas e desconhecido. Cada par
    (i, j) elimina G: r_j·s0_i − r_i·s0_j = (r_j − r_i)·s, linear nos s0. Usa os
    pontos de i com faixa_theta[0] < θ* < faixa_theta[1] e r_j interpolado nos
    mesmos θ*, para todos os pares ordenados; cada equação é dividida por
    r_i + r_j. Não usa b, τ_peso nem k: só s(θ*) do circuito em e.

    Devolve {"s0": {nome: mm}, "rms": resíduo RMS das equações [mm], "n"}.
    """
    linhas = []
    for i, ni in enumerate(nomes):
        for j, nj in enumerate(nomes):
            if i == j:
                continue
            t, ri = fig16[ni]["theta"], fig16[ni]["razao"]
            tj, rj_ = fig16[nj]["theta"], fig16[nj]["razao"]
            usar = ((t > faixa_theta[0]) & (t < faixa_theta[1])
                    & (t >= tj.min()) & (t <= tj.max()))
            rj = np.interp(t[usar], tj, rj_)
            for th, a, b in zip(t[usar], ri[usar], rj):
                linhas.append((th, a, b, i, j))
    if not linhas:
        raise ValueError("nenhum par de pontos na faixa: identificação impossível")
    th, ri, rj, i, j = (np.array(c) for c in zip(*linhas))
    i, j = i.astype(int), j.astype(int)
    _, s, _ = resolver_circuito(calculate_q(th, geo), e, geo)
    w = 1.0/(ri + rj)
    A = np.zeros((th.size, len(nomes)))
    A[np.arange(th.size), i] = rj*w
    A[np.arange(th.size), j] -= ri*w
    y = (rj - ri)*s*w
    s0, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = A @ s0 - y
    return {"s0": {n: float(v) for n, v in zip(nomes, s0)},
            "rms": float(np.sqrt(np.mean(res**2))), "n": int(th.size)}


# ======================================================================
# 9. Autotestes
# ======================================================================

def residuo_trabalho_virtual(e, geo, theta_star, passo=1e-6):
    """max|ds/dq + τ/F| [mm/rad] em cada regime, por diferença central em q.

    Cada ponto é derivado pela forma fechada do SEU regime, então a troca de
    regime em q* não contamina a diferença. Num mecanismo conservativo,
    ds/dq = −τ/F. Devolve {"I": ..., "II": ...} (None se o regime não ocorre).
    """
    q = calculate_q(theta_star, geo)
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


def trechos_negativos(theta, y):
    """Intervalos de θ onde y < 0, com as bordas interpoladas linearmente.
    Lista de (θ_início, θ_fim) em graus."""
    negativo = y < 0
    if not negativo.any():
        return []
    trechos, i = [], 0
    while i < len(theta):
        if not negativo[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(theta) and negativo[j + 1]:
            j += 1

        def borda(a, b):
            return float(theta[a] - y[a]*(theta[b] - theta[a])/(y[b] - y[a]))
        ini = float(theta[i]) if i == 0 else borda(i - 1, i)
        fim = float(theta[j]) if j == len(theta) - 1 else borda(j, j + 1)
        trechos.append((ini, fim))
        i = j + 1
    return trechos


def trechos_frouxos(theta, extensao):
    """Intervalos de θ* onde o elástico afrouxa (s − s0 < 0)."""
    return trechos_negativos(theta, extensao)


def guarda_e(e_a, e_b, geo, defs0, theta_star):
    """Guarda do e implícito: dois e distintos têm de dar curvas distintas.

    Compara s (sempre depende de e: e no regime I, d(e) no regime II) e τ nos
    pontos em regime I. Levanta RuntimeError se e não chega à cadeia.
    """
    ra = calculate_torque_curve(1.0, e_a, geo, defs0, theta_star)
    rb = calculate_torque_curve(1.0, e_b, geo, defs0, theta_star)
    livre = ~(ra["contato"] & rb["contato"])
    if (np.array_equal(ra["s"], rb["s"])
            or (livre.any() and np.array_equal(ra["tau"][livre],
                                               rb["tau"][livre]))):
        raise RuntimeError(f"e não está chegando à cadeia: curvas iguais para "
                           f"e = {e_a:g} e e = {e_b:g}. Varredura abortada.")
    return float(np.max(np.abs(ra["tau"] - rb["tau"])))


def erro_ancoragem(e_valores, geo, defs0):
    """Assert de ancoragem adaptado à forma de s0 [mm] (deve ser ≈ 0).

    Forma (b): max|x(θ*_pre, e) − X_PRE| sobre e_valores.
    Formas (a) e (c): max|s0(e) − s0(e_0)|, s0 igual para todo e.
    """
    if defs0.forma == "b":
        erros = []
        for e in e_valores:
            r = generate_graph_torque_theta_relation(0.0, e, geo, defs0,
                                                     [defs0.theta_pre])
            erros.append(abs(float(r["x"][0]) - defs0.x_pre))
        return max(erros)
    s0s = [s_zero(e, geo, defs0) for e in e_valores]
    return max(abs(v - s0s[0]) for v in s0s)


def grade_q_volta(e, geo, n=3601):
    """Grade em q de q*_0 − 0,9π a q*_0 + 0,9π [rad], com q*_0 o q* fechado
    de p = 0, para os testes que não podem depender da faixa de operação (q*
    e caso p = 0). Exclui os alinhamentos antípodas, perto de q*_0 ± π."""
    centro = q_estrela_fechado(e, geo._replace(p=0.0))
    return centro + np.linspace(-0.9*np.pi, 0.9*np.pi, n)


def autoteste_p_zero(e_valores, geo):
    """Autoteste 4: com p = 0, s = |B| + |OP| constante e τ = 0 no regime II,
    q* numérico = forma fechada atan2(By, Bx) − ε(e), e a direção de OP em q*
    igual para todo e."""
    geo0 = geo._replace(p=0.0)
    bx, by = calculate_base_vector(geo0)
    modulo_b = float(np.hypot(bx, by))
    saida = {"direcao_OP": float(np.arctan2(by, bx)), "q_fechado": {},
             "erro_q": 0.0, "erro_dir": 0.0, "erro_s": 0.0, "tau_max": 0.0}
    for e in e_valores:
        q = grade_q_volta(e, geo0)
        q_fechado = q_estrela_fechado(e, geo0)
        contato, s, psi = resolver_circuito(q, e, geo0)
        tau = torque_produto_vetorial(ponto_aplicacao(q, e, geo0, contato),
                                      vetor_forca(1.0, psi))
        q_num = q_estrela_numerico(e, geo0, q)
        saida["q_fechado"][float(e)] = float(q_fechado)
        saida["erro_q"] = max(saida["erro_q"], abs(q_num - q_fechado))
        saida["erro_dir"] = max(saida["erro_dir"], abs(
            q_num + angulo_OP(e, geo0) - saida["direcao_OP"]))
        saida["erro_s"] = max(saida["erro_s"], float(np.max(np.abs(
            s[contato] - (modulo_b + raio_OP(e, geo0))))))
        saida["tau_max"] = max(saida["tau_max"],
                               float(np.max(np.abs(tau[contato]))))
        assert contato.any() and (~contato).any(), "p = 0: faltou um regime"
    assert saida["erro_q"] < 1e-9, f"q* p = 0: {saida['erro_q']:.1e} rad"
    assert saida["erro_dir"] < 1e-9, "direção de OP em q* depende de e"
    assert saida["erro_s"] < 1e-9, f"s ≠ |B| + |OP|: {saida['erro_s']:.1e} mm"
    assert saida["tau_max"] < 1e-12, f"τ ≠ 0 no regime II: {saida['tau_max']:.1e}"
    return saida


def autotestes(e, geo, k, defs0, theta_star, e_extra, theta_pose_cad,
               s_pose_cad):
    """Confere a cadeia em e (força unitária e F = k·x) e devolve os números.

    e_extra: outros valores de e para a guarda de e, a ancoragem e o caso
    p = 0 (o autoteste não pode depender de um e só).
    theta_pose_cad, s_pose_cad: pose do CAD, para conferir o fechamento do
    circuito contra o s medido.
    """
    theta_star = np.asarray(theta_star, dtype=float)
    r1 = generate_graph_torque_theta_relation(1.0, e, geo, defs0, theta_star)
    rk = calculate_torque_curve(k, e, geo, defs0, theta_star)
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

    # d = |P − C78| constante em q; x_78 pela fórmula = |cotovelo − C78|
    q = r1["q"]
    numeros["d_constante"] = float(np.max(np.abs(
        np.hypot(*(ponto_P(q, e, geo) - ponto_78(q, geo))) - r1["d"])))
    numeros["x78_duas_vias"] = float(np.max(np.abs(
        np.hypot(*(e*versor(q) - ponto_78(q, geo))) - calculate_x78(e, geo))))
    assert numeros["d_constante"] < 1e-9 and numeros["x78_duas_vias"] < 1e-9

    # fechamento com o CAD: s na pose = s medido
    _, s_pose, _ = resolver_circuito(calculate_q(theta_pose_cad, geo), e, geo)
    numeros["s_pose"] = float(s_pose)
    numeros["erro_s_pose"] = abs(float(s_pose) - s_pose_cad)
    assert numeros["erro_s_pose"] < 1e-3, \
        f"s na pose difere do CAD em {numeros['erro_s_pose']:.1e} mm"

    # 2. trabalho virtual: ds/dq = −τ/F nos dois regimes
    tv = residuo_trabalho_virtual(e, geo, theta_star)
    numeros["tv_I"], numeros["tv_II"] = tv["I"], tv["II"]
    assert all(v is None or v < 1e-6 for v in tv.values()), f"TV: {tv}"

    # 3. continuidade em q*: s (e τ) do regime I = do regime II
    q_est = q_estrela_numerico(e, geo, grade_q_volta(e, geo))
    assert q_est is not None, "q* não encontrado na volta em torno de q*_0"
    s_I, psi_I = resolver_regime_I(q_est, e, geo)
    s_II, psi_II = resolver_regime_II(q_est, e, geo)
    tau_I = torque_produto_vetorial(ponto_P(q_est, e, geo),
                                    vetor_forca(1.0, psi_I))
    tau_II = torque_produto_vetorial(ponto_78(q_est, geo),
                                     vetor_forca(1.0, psi_II))
    numeros["q_estrela"] = q_est
    numeros["s_estrela"] = float(s_I)
    numeros["b_estrela"] = float(tau_I)
    numeros["continuidade_s"] = float(abs(s_I - s_II))
    numeros["continuidade_tau"] = float(abs(tau_I - tau_II))
    assert numeros["continuidade_s"] < 1e-9
    assert numeros["continuidade_tau"] < 1e-9
    # ordem dos regimes na faixa: II para q ≤ q*, I para q > q*
    assert np.array_equal(contato, q <= q_est), "ordem dos regimes violada"

    # 4. caso p = 0
    numeros["p_zero"] = autoteste_p_zero((e,) + tuple(e_extra), geo)

    # 5. tração: x ≥ 0 na faixa ou relatório de onde afrouxa (não é assert)
    numeros["frouxo"] = trechos_frouxos(theta_star, rk["extensao"])

    # 6. τ pelo produto vetorial = τ pela fórmula escalar
    numeros["tau_duas_vias"] = float(np.max(np.abs(rk["tau"]
                                                   - rk["tau_escalar"])))
    assert numeros["tau_duas_vias"] < 1e-9

    # linearidade em k (com dois k diferentes, para nunca ser trivial)
    rk2 = calculate_torque_curve(2.0*k + 1.0, e, geo, defs0, theta_star)
    numeros["erro_linear_K"] = float(max(
        np.max(np.abs(rk["tau"] - k*r1["tau"]*r1["x"])),
        np.max(np.abs(rk2["tau"]/(2.0*k + 1.0) - rk["tau"]/k))))
    assert numeros["erro_linear_K"] < 1e-9

    # 7. guarda de e e ancoragem, nas três formas de s0. A forma (b) usa
    # valores de teste: θ*_pre = pose do CAD e X_PRE = 0, que reproduz s0 =
    # s da pose = S0_PROVISORIO da forma (a).
    numeros["guarda_e"] = guarda_e(e, e_extra[0], geo, defs0, theta_star)
    e_teste = (e,) + tuple(e_extra)
    numeros["ancoragem"] = erro_ancoragem(e_teste, geo, defs0)
    teste_b = definir_s0("b", theta_pre=theta_pose_cad, x_pre=0.0,
                         origem="TESTE")
    numeros["ancoragem_b"] = erro_ancoragem(e_teste, geo, teste_b)
    numeros["b_igual_a"] = abs(s_zero(e, geo, teste_b) - s_pose_cad)
    teste_a = definir_s0("a", s0_fixo=s_pose_cad, origem="TESTE")
    numeros["ancoragem_a"] = erro_ancoragem(e_teste, geo, teste_a)
    for nome in ("ancoragem", "ancoragem_a", "ancoragem_b"):
        assert numeros[nome] < 1e-9, f"{nome} violada: {numeros[nome]:.1e} mm"
    assert numeros["b_igual_a"] < 1e-3

    # e é obrigatório em toda a cadeia
    for chamada in (lambda: calculate_torque_curve(k, geo=geo, defs0=defs0,
                                                   theta_star=theta_star),
                    lambda: s_zero(geo=geo, defs0=defs0),
                    lambda: calculate_d(geo=geo),
                    lambda: ponto_P(q, geo=geo),
                    lambda: q_estrela_numerico(geo=geo, q_grade=q),
                    lambda: resolver_circuito(q, geo=geo)):
        try:
            chamada()
        except TypeError:
            continue
        raise AssertionError("uma função da cadeia aceitou ser chamada sem e")

    # torque_peso: CG no eixo do braço pendente → 0; na horizontal → −m·g·r
    # (valores de teste, não do dispositivo)
    assert abs(torque_peso(0.0, 2.0, 100.0, 0.0)) < 1e-12
    assert abs(torque_peso(90.0, 2.0, 100.0, 0.0) + 2.0*GRAVIDADE*0.1) < 1e-12
    return numeros


def autoteste_conjunto(conjunto):
    """Steiner e consistência do conjunto que gira com o braço."""
    for parte in ("humano", "total"):
        c = conjunto[parte]
        assert c["izz_cg_kgm2"] > 0 and c["izz_o_kgm2"] > c["izz_cg_kgm2"]
    soma = sum(c["izz_cg"] + c["massa"]*float(c["pos"] @ c["pos"])
               for c in conjunto["corpos"])/1e6
    assert abs(soma - conjunto["total"]["izz_o_kgm2"]) < 1e-12
    if not conjunto["exo_incluido"]:
        assert conjunto["total"] == conjunto["humano"]
    return True


# ======================================================================
# 10. Extração de torque da patente (gancho opcional, legado)
# ======================================================================

def load_patent_data(caminho):
    """Gancho opcional para uma curva de TORQUE extraída da EP 3 504 033.

    CSV pt-BR: cabeçalho 'theta;torque', separador ';', vírgula decimal, θ*
    em graus (mesma entrada da cadeia). Os pontos são mantidos na ordem do
    arquivo. Se o arquivo não existe, devolve None e o código roda sem RMSE.
    A Fig. 16 (razão sem escala) NÃO entra aqui: ver load_fig16.
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


# ======================================================================
# 11. Gráficos (comuns)
# ======================================================================

COR_EXO = "#2a78d6"     # τ do elástico
COR_PESO = "#eb6834"    # peso e alvo (o alvo deriva do peso: mesma cor)
CORES_FIG16 = {"pontilhada": "#2a78d6", "tracejada": "#eb6834",
               "continua": "#1baf7a"}
ESTILO_FIG16 = {"pontilhada": ":", "tracejada": "--", "continua": "-"}
FUNDO, TINTA, TINTA_2, GRADE = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"


def ve_formatador_virgula(casas):
    from matplotlib.ticker import FuncFormatter
    return FuncFormatter(lambda x, pos: f"{x:.{casas}f}".replace(".", ","))


def _eixo(ax, xlabel, ylabel, casas_y):
    """Estilo comum: grade recessiva, vírgula decimal, tinta secundária."""
    ax.set_facecolor(FUNDO)
    ax.set_xlabel(xlabel, color=TINTA_2)
    ax.set_ylabel(ylabel, color=TINTA_2)
    ax.xaxis.set_major_formatter(ve_formatador_virgula(0))
    ax.yaxis.set_major_formatter(ve_formatador_virgula(casas_y))
    ax.grid(color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=TINTA_2)
    for lado in ax.spines.values():
        lado.set_color("#b9b8b2")


def _sombrear(ax, trechos, rotulo):
    """Sombreia os trechos (θ_início, θ_fim); um só rótulo na legenda."""
    for j, (a, b) in enumerate(trechos):
        ax.axvspan(a, b, color="#b9b8b2", alpha=0.35, linewidth=0,
                   label=rotulo if j == 0 else None)


def plot_ajuste_fig16(fig16, ajustes, e, geo, peso, faixa, caminho_png):
    """As três curvas da Fig. 16 (pontos; fora do ajuste em cinza) e c·m de
    cada uma (linha), em divisões da grade, com a faixa do ajuste marcada."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5.4), dpi=200, facecolor=FUNDO)
    _eixo(ax, "θ* (graus)", "Razão exo/peso (divisões da grade da Fig. 16)", 1)
    ax.axvspan(*faixa, color="#e6e5e1", alpha=0.5, linewidth=0,
               label=f"faixa do ajuste {faixa[0]:g}° < θ* < {faixa[1]:g}°")
    ax.axhline(0, color=TINTA_2, linewidth=0.8)
    topo = 0.0
    for nome, dados in fig16.items():
        aj = ajustes[nome]
        cor = CORES_FIG16.get(nome, TINTA_2)
        th = np.linspace(dados["theta"].min(), dados["theta"].max(), 600)
        q = calculate_q(th, geo)
        contato, s, psi = resolver_circuito(q, e, geo)
        linha = aj["c"]*modelo_fig16(s, braco_momento(q, psi, e, geo, contato),
                                     np.abs(torque_peso(th, *peso)), aj["s0"])
        s0_txt = (f"{aj['s0']:.3f}".replace(".", ",")
                  + (" (limite)" if aj["limite"] else ""))
        ax.plot(th, linha, color=cor, linewidth=2,
                linestyle=ESTILO_FIG16.get(nome, "-"),
                label=f"{nome}: modelo c·m, s0 = {s0_txt} mm")
        usado = aj["usado"]
        ax.plot(dados["theta"][usado], dados["razao"][usado], "o", color=cor,
                markersize=4.5, markeredgecolor=FUNDO, markeredgewidth=0.8,
                label=f"{nome}: patente ({aj['n']} pontos no ajuste)")
        ax.plot(dados["theta"][~usado], dados["razao"][~usado], "o",
                color="#9a9994", markersize=4, markeredgecolor=FUNDO,
                markeredgewidth=0.8)
        topo = max(topo, float(dados["razao"].max()))
    ax.plot([], [], "o", color="#9a9994", markersize=4,
            label="pontos fora do ajuste")
    ax.set_xlim(0, 180)
    ax.set_ylim(-0.2, 1.08*topo)
    ax.set_title("Ajuste de s0 à forma da Fig. 16 (EP 3 504 033 B1), "
                 + f"e = {e:g} mm".replace(".", ","), loc="left", fontsize=11,
                 color=TINTA)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False,
              fontsize=7.5)
    fig.subplots_adjust(left=0.08, right=0.66, bottom=0.11, top=0.92)
    fig.savefig(caminho_png, facecolor=FUNDO)
    plt.close(fig)


def plot_projeto(theta, tau_exo, tau_peso_abs, alvo, theta_estrela, marcas,
                 titulo, caminho_png):
    """Projeto: τ_exo, |τ_peso| e alvo·|τ_peso| em N·m no mesmo eixo, q*
    marcado, τ_exo < 0 sombreado e a razão τ_exo/|τ_peso| nas marcas."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5.4), dpi=200, facecolor=FUNDO)
    _eixo(ax, "θ* (graus)", "Torque (N·m)", 1)
    negativos = trechos_negativos(theta, tau_exo)
    _sombrear(ax, negativos, "τ_exo < 0")
    ax.axhline(0, color=TINTA_2, linewidth=0.8)
    ax.plot(theta, tau_peso_abs, color=COR_PESO, linewidth=2, label="|τ_peso|")
    ax.plot(theta, alvo*tau_peso_abs, color=COR_PESO, linewidth=2,
            linestyle="--",
            label=f"{alvo:g}·|τ_peso| (alvo, hipótese)".replace(".", ","))
    ax.plot(theta, tau_exo, color=COR_EXO, linewidth=2, label="τ_exo")
    if theta_estrela is not None:
        ax.axvline(theta_estrela, color=TINTA_2, linewidth=0.8, linestyle=":",
                   label=f"q* (θ* = {theta_estrela:.2f}°)".replace(".", ","))
    for j, (th, tau, razao) in enumerate(marcas):
        pico = j == len(marcas) - 1          # a última marca é o pico de τ_exo
        ax.plot([th], [tau], "o", color=COR_EXO, markersize=6,
                markeredgecolor=FUNDO, markeredgewidth=1.5, zorder=4)
        texto = f"{razao:.2f}".replace(".", ",")
        ax.annotate(f"pico {texto}" if pico else texto, (th, tau),
                    xytext=(14, 14) if pico else (0, 8),
                    textcoords="offset points",
                    ha="left" if pico else "center", fontsize=8, color=TINTA)
    ax.plot([], [], "o", color=COR_EXO, markersize=6,
            label="τ_exo/|τ_peso| (rótulos)")
    if not negativos:
        ax.plot([], [], " ", label="τ_exo ≥ 0 em toda a faixa")
    ax.set_xlim(theta[0], theta[-1])
    ax.set_title(titulo, loc="left", fontsize=10.5, color=TINTA)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False,
              fontsize=8)
    fig.subplots_adjust(left=0.08, right=0.72, bottom=0.11, top=0.92)
    fig.savefig(caminho_png, facecolor=FUNDO)
    plt.close(fig)


# ==========================================================================
# 12. VARREDURA PARAMÉTRICA DE e  (diagnóstico)
# ==========================================================================
#
# Regras (as mesmas da varredura de h do original): toda conta vive dentro de
# funções; e é passado explicitamente em toda chamada; nada aqui calibra
# nenhum parâmetro. Globais novos: só as funções ve_* e varredura_e, e as
# constantes VE_*.
#
# s0 e k ficam os do projeto padrão, fixos para todo e: o elástico é o mesmo,
# só o parafuso de ajuste (e) muda. τ é linear em k, então a família também
# é plotada como τ/k (só o efeito geométrico de e).
#
# Viabilidade = (a) tração + (c) fechamento + (d) trabalho virtual.

VE_GRID = np.round(20.0 + 0.05*np.arange(601), 10)  # mm, e VARRIDO (20 a 50)
VE_FAMILIA = (25.0, 30.0, E_CAD, 40.0, 45.0)       # mm, curvas τ × θ*
VE_THETA = np.round(np.linspace(THETA_MIN, THETA_MAX, 1801), 10)  # graus θ*, 0,1°
VE_FOLGAS = (1.01, 1.05, 1.10, 2.00)               # platôs de RMSE (só com extração)
VE_CRITERIOS = ("tracao", "fechamento", "tv_ok")
VE_TOL_TV = 1e-6                                   # mm/rad


def ve_avaliar_e(e, geo, k, defs0, theta_star, patente, sinal_patente, tol_tv):
    """Validade (a), (c), (d) e indicadores de um e. Nada é saturado nem
    corrigido; k só multiplica (τ/k não depende dele).

    patente: dicionário de load_patent_data ou None (sem RMSE).
    """
    linha = {"e": float(e), "motivo": "", "viavel": False}
    q = calculate_q(theta_star, geo)
    try:
        q_est = q_estrela_numerico(e, geo, q)
        rk = calculate_torque_curve(k, e, geo, defs0, theta_star)
        r1 = calculate_torque_curve(1.0, e, geo, defs0, theta_star)
        tv = residuo_trabalho_virtual(e, geo, theta_star)
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

    tau = rk["tau"]
    tau_k = r1["tau"]                    # N·m por N/mm
    extensao = rk["extensao"]
    frouxo = trechos_frouxos(theta_star, extensao)
    tracionado = theta_star[extensao >= 0]
    i_pico, i_min = int(np.argmax(tau)), int(np.argmin(tau))
    i_xmin, i_xmax = int(np.argmin(extensao)), int(np.argmax(extensao))
    tv_max = max(v for v in tv.values() if v is not None)
    linha.update(
        d=float(rk["d"]),
        s0=float(rk["s0"]),
        q_estrela=None if q_est is None else float(np.degrees(q_est)),
        theta_estrela=None if q_est is None else float(theta_star_de_q(q_est, geo)),
        frac_contato=float(contato.mean()),
        tracao=not frouxo,
        trechos_frouxos=" ".join(f"{a:.2f}–{b:.2f}".replace(".", ",")
                                 for a, b in frouxo),
        theta_tracao_min=float(tracionado.min()) if tracionado.size else None,
        theta_tracao_max=float(tracionado.max()) if tracionado.size else None,
        x_min=float(extensao[i_xmin]), theta_x_min=float(theta_star[i_xmin]),
        x_max=float(extensao[i_xmax]), theta_x_max=float(theta_star[i_xmax]),
        tau_pico=float(tau[i_pico]), theta_pico=float(theta_star[i_pico]),
        tau_min=float(tau[i_min]), theta_tau_min=float(theta_star[i_min]),
        tau_k_pico=float(tau_k[i_pico]),
        trechos_tau_negativo=" ".join(f"{a:.2f}–{b:.2f}".replace(".", ",")
                                      for a, b in trechos_negativos(theta_star, tau)),
        braco_max=float(np.max(rk["braco"])),
        tv_I=tv["I"], tv_II=tv["II"], trabalho_virtual=float(tv_max),
        tv_ok=bool(tv_max < tol_tv),
        erro_linear_K=erro_linear,
    )

    if patente is not None:
        y = patente["torque"]
        modelo = sinal_patente*calculate_torque_curve(
            k, e, geo, defs0, patente["theta"])["tau"]
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


def ve_extensao_minima(e, geo, defs0, theta_star):
    """Menor extensão bruta s − s0(e) na faixa [mm]."""
    r = generate_graph_torque_theta_relation(0.0, e, geo, defs0, theta_star)
    return float(r["extensao"].min())


def ve_fronteira_tracao(e_ok, e_falha, geo, defs0, theta_star, tol=1e-9):
    """e em que a menor extensão na faixa passa por zero, por bissecção
    própria entre um e que traciona e um que afrouxa."""
    while abs(e_falha - e_ok) > tol:
        meio = 0.5*(e_ok + e_falha)
        if ve_extensao_minima(meio, geo, defs0, theta_star) >= 0:
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


def ve_nos_da_familia(familia, geo, defs0, theta_star):
    """Curvas τ/k da família, espalhamento máx − mín entre elas em cada θ*,
    seus mínimos locais (nós: onde as curvas quase não dependem de e) e o
    máximo."""
    curvas = np.array([calculate_torque_curve(1.0, e, geo, defs0,
                                              theta_star)["tau"]
                       for e in familia])
    espalhamento = curvas.max(axis=0) - curvas.min(axis=0)
    nos = [(float(theta_star[j]), float(espalhamento[j]))
           for j in range(1, len(theta_star) - 1)
           if espalhamento[j] < espalhamento[j - 1]
           and espalhamento[j] <= espalhamento[j + 1]]
    j = int(np.argmax(espalhamento))
    return {"curvas": curvas, "espalhamento": espalhamento, "nos": nos,
            "maximo": (float(theta_star[j]), float(espalhamento[j]))}


def ve_salvar_csv(caminho, linhas, colunas,
                  colunas_texto=("papeis", "motivo", "trechos_frouxos",
                                 "trechos_tau_negativo")):
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


def ve_plot_familia(familia, nos, linhas_familia, theta, k, tau_peso_abs,
                    alvo, patente, sinal_patente, rotulo_projeto, caminho_png):
    """Família de curvas × θ* em dois painéis: τ em N·m (com alvo·|τ_peso|
    sobreposto) e τ/k. e é ordenado: rampa sequencial de um só tom, clara →
    escura; E_CAD mais espesso. q* de cada curva marcado; τ < 0 sombreado.
    Se houver extração de torque (load_patent_data), ela é sobreposta."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rampa = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#184f95", "#0d366b"]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8.2), dpi=200,
                                   facecolor=FUNDO, sharex=True)
    _eixo(ax1, "", "τ (N·m)", 1)
    _eixo(ax2, "θ* (graus)", "τ/k  (N·m por N/mm)", 1)
    negativos = []
    for curva in nos["curvas"]:
        negativos += trechos_negativos(theta, k*curva)
    for ax in (ax1, ax2):
        _sombrear(ax, negativos, "τ < 0 (alguma curva)")
        ax.axhline(0, color=TINTA_2, linewidth=0.8)
        for j, (theta_no, _) in enumerate(nos["nos"]):
            ax.axvline(theta_no, color="#7a7974", linewidth=0.8, linestyle=":",
                       label="nós da família (τ/k)" if j == 0 else None)
    ax1.plot(theta, alvo*tau_peso_abs, color=COR_PESO, linewidth=2,
             linestyle="--",
             label=f"{alvo:g}·|τ_peso| (alvo, hipótese)".replace(".", ","))
    ordem = sorted(range(len(familia)), key=lambda i: familia[i])
    for posto, i in enumerate(ordem):
        cor = rampa[round(posto*(len(rampa) - 1)/max(len(ordem) - 1, 1))]
        cad = abs(familia[i] - E_CAD) < 1e-9
        rotulo = (f"e = {familia[i]:g} mm" + (" (CAD)" if cad else "")
                  ).replace(".", ",")
        for ax, escala in ((ax1, k), (ax2, 1.0)):
            ax.plot(theta, escala*nos["curvas"][i], color=cor,
                    linewidth=2.8 if cad else 1.8,
                    label=rotulo if ax is ax1 else None)
            theta_est = linhas_familia[i].get("theta_estrela")
            if theta_est is not None:
                y_est = np.interp(theta_est, theta, escala*nos["curvas"][i])
                ax.plot([theta_est], [y_est], "o", color=cor, markersize=6,
                        markeredgecolor=FUNDO, markeredgewidth=1.5, zorder=4)
    ax1.plot([], [], "o", color=TINTA_2, markersize=6, label="q* (troca de regime)")
    if patente is not None:
        for ax, escala in ((ax1, 1.0), (ax2, 1.0/k)):
            ax.plot(patente["theta"], escala*sinal_patente*patente["torque"],
                    "o", color=TINTA, markersize=4.5, zorder=5,
                    label=(f"Extração de torque ({len(patente['theta'])} pontos)"
                           if ax is ax1 else None))
    if not negativos:
        ax1.plot([], [], " ", label="τ ≥ 0 em toda a faixa")
    ax1.set_title(f"Família em e com o elástico do {rotulo_projeto} (k = "
                  + f"{k:.5f} N/mm)".replace(".", ","), loc="left",
                  fontsize=10.5, color=TINTA)
    ax2.set_xlim(theta[0], theta[-1])
    ax1.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False,
               fontsize=8)
    fig.subplots_adjust(left=0.09, right=0.74, bottom=0.07, top=0.95,
                        hspace=0.08)
    fig.savefig(caminho_png, facecolor=FUNDO)
    plt.close(fig)


def varredura_e(geo, k, defs0, theta_star, grade, familia, caminho_extracao,
                sinal_patente, peso, alvo, pasta, plot_familia=True,
                rotulo_projeto="projeto padrão", sufixo=""):
    """Varre e com s0 e k fixos, classifica validade física, gera a família e
    reporta os indicadores. Diagnóstico: não calibra nada. Todos os
    parâmetros entram como argumentos; peso = argumentos_peso(conjunto)."""
    patente = load_patent_data(caminho_extracao)
    theta_star = np.asarray(theta_star, dtype=float)

    # guarda do e implícito: dois e distintos têm de dar curvas distintas
    dif_guarda = guarda_e(min(familia), max(familia), geo, defs0, theta_star)

    grade = np.unique(np.concatenate([grade, familia, [E_CAD]]))
    linhas = [ve_avaliar_e(e, geo, k, defs0, theta_star, patente,
                           sinal_patente, VE_TOL_TV) for e in grade]
    linha_de = {round(l["e"], 9): l for l in linhas}

    # ancoragem adaptada à forma de s0
    erro_ancora = erro_ancoragem(grade, geo, defs0)
    assert erro_ancora < 1e-9, f"ancoragem violada: {erro_ancora:.1e} mm"

    calculaveis = [l for l in linhas if l["fechamento"]]
    faixas = {nome: ve_faixa(linhas, nome)
              for nome in ("tracao", "tv_ok", "viavel")}

    fronteira = None
    if faixas["tracao"] and not faixas["tracao"]["borda_max"]:
        es = [l["e"] for l in linhas]
        i_ok = es.index(faixas["tracao"]["max"])
        fronteira = ve_fronteira_tracao(es[i_ok], es[i_ok + 1], geo, defs0,
                                        theta_star)

    nos = ve_nos_da_familia(familia, geo, defs0, theta_star)
    linhas_familia = [linha_de[round(float(e), 9)] for e in familia]
    q_estrelas = [l["q_estrela"] for l in calculaveis
                  if l.get("q_estrela") is not None]
    t_estrelas = [l["theta_estrela"] for l in calculaveis
                  if l.get("theta_estrela") is not None]
    p_zero = autoteste_p_zero((grade[0], grade[-1]), geo)
    tau_peso_abs = np.abs(torque_peso(theta_star, *peso))

    # ---------------------------------------------------------- relatório
    print("\n" + "=" * 78)
    print("VARREDURA PARAMÉTRICA DE e (diagnóstico)")
    print("=" * 78)
    if defs0.forma == "b":
        print(f"e = trecho O → cotovelo da alavanca, VARRIDO, com o elástico do "
              f"{rotulo_projeto}: k = {k:.5f} N/mm e X_PRE = {defs0.x_pre:g} mm "
              f"fixos; s0(e) = s(θ*_pre, e) − X_PRE VARIA com e (forma b).")
    else:
        print(f"e = trecho O → cotovelo da alavanca, VARRIDO, com o elástico do "
              f"{rotulo_projeto}: s0 = {s_zero(E_CAD, geo, defs0):.3f} mm "
              f"(forma {defs0.forma}) e k = {k:.5f} N/mm FIXOS: o elástico é o "
              f"mesmo, só o parafuso muda.")
    print(f"Grade: {grade.size} valores de e, de {grade[0]:g} a {grade[-1]:g} mm "
          f"(passo 0,05 + família + E_CAD). Faixa θ*: {theta_star[0]:g}° a "
          f"{theta_star[-1]:g}°, {theta_star.size} pontos.")
    print(f"Viabilidade = {' + '.join(VE_CRITERIOS)} (critérios (a), (c), (d)).")
    print(f"Guarda do e implícito: curvas com e = {min(familia):g} e "
          f"e = {max(familia):g} diferem (máx. {dif_guarda:.3e} N·m por N/mm). OK.")
    print(f"Linearidade em k: max|τ(k) − k·τ(k=1)| na grade = "
          f"{max(l['erro_linear_K'] for l in calculaveis):.1e} (< 1e-9).")
    if defs0.forma == "b":
        print(f"Ancoragem (forma b): x(θ*_pre = {defs0.theta_pre:g}°) = X_PRE = "
              f"{defs0.x_pre:g} mm para todo e (erro máx. {erro_ancora:.1e} mm).")
    else:
        print(f"Ancoragem (forma {defs0.forma}): s0 igual para todo e "
              f"(erro máx. {erro_ancora:.1e} mm).")
    if q_estrelas:
        print(f"q*: com p = {geo.p:g} mm, q* depende de e: q* de "
              f"{min(q_estrelas):.3f}° a {max(q_estrelas):.3f}° (θ* de "
              f"{min(t_estrelas):.3f}° a {max(t_estrelas):.3f}°); "
              f"{len(q_estrelas)} de {len(calculaveis)} e com q* na faixa.")
    print(f"   Caso p = 0 (autoteste): direção de OP em q* = "
          f"{np.degrees(p_zero['direcao_OP']):.4f}° = atan2(By, Bx) para todo "
          f"e; q* = " + ", ".join(f"{np.degrees(v):.4f}° (e = {ee:g})"
                                  for ee, v in p_zero["q_fechado"].items())
          + f" — depende de e só por ε(e) (erro numérico × fechado "
          f"{p_zero['erro_q']:.1e} rad).")

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
              f"{ve_extensao_minima(fronteira, geo, defs0, theta_star):.1e} mm")
    print(f"  trabalho virtual máximo na grade: "
          f"{max(l['trabalho_virtual'] for l in calculaveis):.1e} mm/rad")

    # concordância com uma curva de torque extraída (gancho, só se existir)
    otimo = None
    if patente is None:
        print(f"\nCurva de TORQUE extraída (gancho theta;torque): não encontrada "
              f"({caminho_extracao}). Sem RMSE de torque; a Fig. 16 é razão sem "
              f"escala e entra só no ajuste de s0.")
    else:
        otimo = min(calculaveis, key=lambda l: l["rmse"])
        for posto, l in enumerate(sorted(calculaveis, key=lambda l: l["rmse"]),
                                  start=1):
            l["posto_rmse"] = posto
        print(f"\nConcordância com a extração de torque ({patente['fonte']}, "
              f"{len(patente['theta'])} pontos), k congelado em {k:g}:")
        print(f"  menor RMSE: e = {otimo['e']:.3f} mm  RMSE {otimo['rmse']:.4f}  "
              f"R² {otimo['r2']:.5f}  viável: {otimo['viavel']}"
              + (f" (falha: {otimo['motivo']})" if not otimo["viavel"] else ""))
        print("  ACHADO DIAGNÓSTICO, não adoção: não cria E_CALIBRADO.")
        for folga in VE_FOLGAS:
            p = ve_plato(linhas, folga)
            print(f"  platô RMSE ≤ {folga:.2f}·mín: e de {p['min']:.3f} a "
                  f"{p['max']:.3f} mm, largura {p['largura']:.3f} mm, {p['n']} e"
                  f"{'' if p['contigua'] else ', NÃO contíguo'}")

    # família e valores notáveis
    print("\nFamília (τ/k, k não entra), e = "
          + ", ".join(f"{e:g}" for e in familia) + " mm:")
    for theta_no, valor in nos["nos"]:
        print(f"  nó (espalhamento mínimo local): θ* = {theta_no:.2f}°, "
              f"espalhamento {valor:.3e} N·m por N/mm")
    print(f"  abertura máxima: θ* = {nos['maximo'][0]:.2f}°, espalhamento "
          f"{nos['maximo'][1]:.3e} N·m por N/mm")
    print(f"  (malha de θ* com passo {theta_star[1] - theta_star[0]:.2f}°).")

    papeis = [("familia", e) for e in familia] + [("E_CAD", E_CAD)]
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
            chave, geo, k, defs0, theta_star, patente, sinal_patente,
            VE_TOL_TV))
        v["papeis"] = "+".join(agrupados[chave])
        if patente is not None and chave not in linha_de:
            v["posto_rmse"] = "fora da grade"
        notaveis.append(v)

    def num(v, fmt):
        return "—" if v is None else format(v, fmt)

    print("\nPor e (família e notáveis; τ em N·m, k do projeto; flags "
          "a=tração c=fechamento d=trab. virtual):")
    print(f"{'e (mm)':>10} {'d':>7} {'q* (°)':>8} {'θ*(q*)':>7} {'%II':>5} "
          f"{'τ pico':>7} {'θ* pico':>7} {'τ mín':>7} {'s−s0 mín':>8} {'x_max':>7} "
          f"{'θ* x_max':>8} {'tração em θ*':>13} {'flags':>5}  papéis")
    for v in notaveis:
        if not v["fechamento"]:
            print(f"{v['e']:10.4f}  sem fechamento: {v['motivo']}  {v['papeis']}")
            continue
        flags = "".join(c if v.get(kk) else "-" for c, kk in
                        (("a", "tracao"), ("c", "fechamento"), ("d", "tv_ok")))
        faixa_q = (f"{num(v['theta_tracao_min'], '.1f')}–"
                   f"{num(v['theta_tracao_max'], '.1f')}")
        print(f"{v['e']:10.4f} {v['d']:7.3f} {num(v['q_estrela'], '8.3f'):>8} "
              f"{num(v['theta_estrela'], '7.3f'):>7} {100*v['frac_contato']:5.1f} "
              f"{v['tau_pico']:7.3f} {v['theta_pico']:7.1f} {v['tau_min']:7.3f} "
              f"{v['x_min']:8.2f} {v['x_max']:7.2f} {v['theta_x_max']:8.1f} "
              f"{faixa_q:>13} {flags:>5}  {v['papeis']}")
        if v["trechos_frouxos"]:
            print(f"{'':10}   ↳ elástico frouxo em θ* = {v['trechos_frouxos']}°")
        if v["trechos_tau_negativo"]:
            print(f"{'':10}   ↳ τ < 0 em θ* = {v['trechos_tau_negativo']}°")
    print("%II = fração da faixa em contato com o 78. 'tração em θ*' = menor e "
          "maior θ* com s − s0 ≥ 0.")
    if patente is not None:
        print(f"\n{'e (mm)':>10} {'posto':>6} {'RMSE':>9} {'MAE':>9} "
              f"{'erro máx':>9} {'θ* erro':>7} {'R²':>8}")
        for v in notaveis:
            if v["fechamento"]:
                print(f"{v['e']:10.4f} {v.get('posto_rmse', ''):>6} "
                      f"{v['rmse']:9.4f} {v['mae']:9.4f} {v['erro_max']:9.4f} "
                      f"{v['theta_erro_max']:7.2f} {v['r2']:8.5f}")

    # ---------------------------------------------------------- arquivos
    pasta = Path(pasta)
    pasta.mkdir(exist_ok=True)
    arquivos = [pasta/f"ve_varredura_e{sufixo}.csv",
                pasta/f"ve_e_notaveis{sufixo}.csv"]
    colunas = ["e", "fechamento", "tracao", "tv_ok", "viavel", "motivo", "d",
               "s0", "q_estrela", "theta_estrela", "frac_contato", "tau_pico",
               "theta_pico", "tau_min", "theta_tau_min", "tau_k_pico",
               "trechos_tau_negativo", "x_min", "theta_x_min", "x_max",
               "theta_x_max", "theta_tracao_min", "theta_tracao_max",
               "trechos_frouxos", "braco_max", "tv_I", "tv_II",
               "trabalho_virtual", "erro_linear_K"]
    if patente is not None:
        colunas += ["rmse", "posto_rmse", "mae", "erro_max", "theta_erro_max",
                    "r2"]
    ve_salvar_csv(arquivos[0], linhas, colunas)
    ve_salvar_csv(arquivos[1], notaveis, ["e", "papeis"] + colunas[1:])
    if plot_familia:
        arquivos.append(pasta/f"ve_familia_curvas{sufixo}.png")
        ve_plot_familia(familia, nos, linhas_familia, theta_star, k,
                        tau_peso_abs, alvo, patente, sinal_patente,
                        rotulo_projeto, arquivos[-1])
    print("\nArquivos gerados pela varredura:")
    for a in arquivos:
        print(f"  {a}")
    return {"linhas": linhas, "faixas": faixas, "notaveis": notaveis,
            "familia": nos, "fronteira_tracao": fronteira, "otimo": otimo,
            "erro_ancora": erro_ancora, "patente": patente}


# ======================================================================
# 13. Relatório
# ======================================================================

VE_RODAR = True            # desligar para executar sem varrer
VE_PLOT_FAMILIA = True     # família τ × θ* e τ/k × θ*

THETA_TABELA_PROJETO = (10.0, 30.0, 60.0, 90.0, 120.0, 150.0, 170.0)  # graus θ*
Q_TABELA = (40.0, 60.0, 90.0, 100.0, 120.0, PARAMETROS_CAD["Q_POSE"], 200.0)
                                    # graus q, ângulos representativos + q*
THETA_MARCAS_RAZAO = (30.0, 60.0, 90.0, 120.0, 150.0)                 # graus θ*


def _argumentos():
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    leitor.add_argument("--forma", choices=("a", "b", "c"),
                        default=FORMA_S0_PROJETO,
                        help="forma de s0: (a) constante S0_PROVISORIO, (b) "
                             "pré-tensão num ângulo, (c) ajustada à Fig. 16")
    leitor.add_argument("--curva", default=CURVA_PROJETO,
                        help="curva da Fig. 16 para a forma (c)")
    leitor.add_argument("--theta-pre", type=float, default=THETA_PRE,
                        help="θ*_pre em graus (forma b)")
    leitor.add_argument("--x-pre", type=float, default=X_PRE,
                        help="X_PRE em mm (forma b)")
    leitor.add_argument("--fig16", type=Path, default=FIG16_CSV,
                        help="CSV das curvas da Fig. 16")
    args = leitor.parse_args()
    if args.forma == "b" and (args.theta_pre is None or args.x_pre is None):
        leitor.error("forma (b) pede --theta-pre e --x-pre (não há valor padrão)")
    if args.x_pre is not None and args.x_pre < 0:
        leitor.error("--x-pre é a extensão do elástico em θ*_pre: precisa ser ≥ 0")
    return args


if __name__ == "__main__":
    args = _argumentos()
    par = PARAMETROS_CAD
    alpha = derivar_alpha(par["GAMMA"])
    phi = derivar_phi(par["PHI_ABS_POSE"], par["Q_POSE"])
    delta = derivar_delta(par["Q_POSE"], par["BRACO_POSE"])
    theta_pose = derivar_theta_pose(par["BRACO_POSE"])
    geo = montar_geometria(par["C1"], par["C2"], alpha, par["GAMMA"],
                           par["C3"], par["BETA"], par["P"], phi, delta)
    e = E_CAD
    theta = VE_THETA
    bx, by = calculate_base_vector(geo)
    q_pose = calculate_q(theta_pose, geo)

    conjunto = montar_conjunto_braco(ESTATURA, MASSA_CORPORAL, DE_LEVA_TAB4,
                                     (MASSA_BRACO_EXO, CG_BRACO_EXO_FUSION,
                                      IZZ_CG_BRACO_EXO),
                                     O_FUSION, par["BRACO_POSE"])
    autoteste_conjunto(conjunto)
    peso = argumentos_peso(conjunto)

    print("=" * 78)
    print("MODELO OTTOBOCK iX SHOULDER AIR — GEOMETRIA DO CAD")
    print("=" * 78)
    if O_FUSION is None:
        print("AVISO: O_FUSION = None (centro da junta 20 no Fusion NÃO MEDIDO).")
        print("       O braço do exo está FORA do peso e da inércia; τ_peso,")
        print("       o ajuste à Fig. 16 e k_40 usam SÓ o membro humano.")
    print(f"AVISO: BRACO_POSE = {par['BRACO_POSE']:g}° tem SINAL A CONFIRMAR.")
    print("\nPARAMETROS_CAD (CAD):")
    for nome, valor in par.items():
        print(f"  {nome:13s} = {valor:g}")
    print(f"  E_CAD         = {e:g} mm  (CAD; parâmetro varrido)")
    print(f"Derivados: α = 90° − γ = {alpha:.3f}°; φ = {phi:.3f}°; "
          f"δ = {delta:.3f}°; θ*_pose = {theta_pose:.3f}°")
    print(f"  B = ({bx:.3f}; {by:.3f}) mm, |B| = {np.hypot(bx, by):.3f} mm, "
          f"d = {calculate_d(e, geo):.3f} mm, x_78 = {calculate_x78(e, geo):.3f} "
          f"mm (só relatório, NÃO é a extensão do elástico)")
    print(f"  |OP| = {raio_OP(e, geo):.3f} mm a "
          f"{np.degrees(angulo_OP(e, geo)):.3f}° de e")
    p_pose, c78_pose = ponto_P(q_pose, e, geo), ponto_78(q_pose, geo)
    print(f"  pose do CAD: q = {np.degrees(q_pose):.3f}°, P = ({p_pose[0]:.3f}; "
          f"{p_pose[1]:.3f}) mm, C78 = ({c78_pose[0]:.3f}; {c78_pose[1]:.3f}) mm")

    # ---------------------------------------------------- peso e inércia
    h, t = conjunto["humano"], conjunto["total"]
    print("\nPeso e inércia do conjunto que gira com o braço (rígido em O):")
    print(f"  membro humano (de Leva Tab. 4; estatura {ESTATURA:g} mm, "
          f"{MASSA_CORPORAL:g} kg): massa {h['massa_kg']:.3f} kg; CG a "
          f"{h['cg_raio_mm']:.3f} mm de O, {h['cg_angulo_braco_grau']:.3f}° do "
          f"eixo do braço; Izz(O) = {h['izz_o_kgm2']:.6f} kg·m², Izz(CG) = "
          f"{h['izz_cg_kgm2']:.6f} kg·m²")
    if conjunto["exo_incluido"]:
        print(f"  total (humano + braço do exo, CAD/Fusion): massa "
              f"{t['massa_kg']:.3f} kg; CG a {t['cg_raio_mm']:.3f} mm de O, "
              f"{t['cg_angulo_braco_grau']:.3f}° do eixo do braço "
              f"({par['BRACO_POSE'] + t['cg_angulo_braco_grau']:.3f}° de +x na "
              f"pose); Izz(O) = {t['izz_o_kgm2']:.6f} kg·m², Izz(CG) = "
              f"{t['izz_cg_kgm2']:.6f} kg·m²")
        print("  HIPÓTESE: eixos do Fusion paralelos aos do modelo; Izz do Fusion "
              "em torno de z.")
    else:
        print("  total = só membro humano (braço do exo fora: O_FUSION = None)")
    print(f"  |τ_peso(90°)| = {abs(float(torque_peso(90.0, *peso))):.3f} N·m; "
          f"|τ_peso(θ*)| = M·g·D·|cos(θ* − 90° + ângulo do CG)|")

    # ------------------------------------------------------ Fig. 16
    fig16, ajustes = None, {}
    sem_ajuste = {}
    if args.fig16.is_file():
        fig16 = load_fig16(args.fig16)
        for nome, dados in fig16.items():
            try:
                ajustes[nome] = ajustar_fig16(dados["theta"], dados["razao"], e,
                                              geo, peso, FIG16_FAIXA_AJUSTE,
                                              FIG16_GRADE_S0, FIG16_FOLGA_FAIXA,
                                              ALVO_FRACAO, THETA_ALVO)
            except ValueError as erro:
                sem_ajuste[nome] = str(erro)
        fig16 = {nome: d for nome, d in fig16.items() if nome in ajustes}
        print(f"\nFig. 16 da EP 3 504 033 B1 ({args.fig16.name}, curvas "
              f"{', '.join(fig16)}):")
        print("  CONTRADIÇÃO REGISTRADA: o texto da patente diz \"torque do peso")
        print("  dividido pelo do exo\", mas as curvas partem de zero e sobem, o")
        print("  que só é coerente com exo/peso. Tratada como exo/peso.")
        print("  Eixo y sem escala na patente: razão em divisões da grade; θ*")
        print("  usado como digitalizado, sem correção.")
        print(f"  Ajuste: {FIG16_FAIXA_AJUSTE[0]:g}° < θ* < "
              f"{FIG16_FAIXA_AJUSTE[1]:g}° (estrito), e = E_CAD, τ_peso = "
              f"{'total' if conjunto['exo_incluido'] else 'só membro humano'}; "
              f"s0 em [{FIG16_GRADE_S0[0]:g}; {FIG16_GRADE_S0[1]:g}] mm, grade "
              f"{FIG16_GRADE_S0[2]:g} mm + Brent limitado.")
        print(f"  Alvo (HIPÓTESE): τ_exo({THETA_ALVO:g}°) = {ALVO_FRACAO:g}·"
              f"|τ_peso({THETA_ALVO:g}°)| → k_40.")
        print(f"  {'curva':>11} {'n':>3} {'s0 (mm)':>22} {'c':>9} {'RMS/max':>8} "
              f"{'faixa 1% de s0 (mm)':>20} {'x(90°)':>8} {'k_40 (N/mm)':>11} "
              f"{'F(90°) N':>8}")
        for nome, aj in ajustes.items():
            s0_txt = (f"{aj['s0']:.3f}" + (f" (limite {aj['limite']})"
                                           if aj["limite"] else ""))
            faixa_txt = (f"{aj['faixa_s0'][0]:.2f} a {aj['faixa_s0'][1]:.2f}"
                         + ("" if aj["faixa_contigua"] else " (NÃO contígua)")
                         + (" †" if aj["faixa_na_borda"] else ""))
            print(f"  {nome:>11} {aj['n']:3d} {s0_txt:>22} {aj['c']:9.5f} "
                  f"{100*aj['rms_max']:7.2f}% {faixa_txt:>20} "
                  f"{aj['x_alvo']:8.3f} {aj['k_alvo']:11.5f} "
                  f"{aj['forca_alvo']:8.2f}")
        print("  A FORMA da curva só define s0 dentro da faixa de identificação")
        print(f"  (RMS ≤ {FIG16_FOLGA_FAIXA:g}·RMS_min). Dentro dela, s0 e k são "
              "decisão de projeto, não medida.")
        if any(aj["faixa_na_borda"] for aj in ajustes.values()):
            print("  † a faixa encosta na borda da grade de s0 (s0 < 0 não é físico).")
        for nome, motivo in sem_ajuste.items():
            print(f"  {nome:>11}: SEM AJUSTE ({motivo})")
        print("  F(90°) é igual nas curvas POR CONSTRUÇÃO: cada curva recebe o seu")
        print("  k_40, e F(90°) = alvo·|τ_peso(90°)|/b(90°) não depende de s0. Com")
        print("  um mesmo atuador (k único) F(90°) seria diferente; só o k_40 da")
        print("  curva de projeto tem significado.")
        regime_I = all(aj["todos_regime_I"] for aj in ajustes.values())
        q_est_e = q_estrela_numerico(e, geo, calculate_q(theta, geo))
        if q_est_e is None:
            onde_q = "sem troca de regime na faixa"
        else:
            th_q = float(theta_star_de_q(q_est_e, geo))
            onde_q = (f"θ*(q*) = {th_q:.3f}° "
                      f"{'<' if th_q < FIG16_FAIXA_AJUSTE[0] else '≥'} "
                      f"{FIG16_FAIXA_AJUSTE[0]:g}°")
        print(f"  Regime: todos os pontos do ajuste caíram no regime I: "
              f"{'SIM' if regime_I else 'NÃO'} ({onde_q}).")
        for nome, aj in ajustes.items():
            if aj["n_regime_II"]:
                print(f"  AVISO: {nome}: {aj['n_regime_II']} ponto(s) do ajuste no "
                      f"regime II (θ* de {aj['theta_regime_II'][0]:.2f}° a "
                      f"{aj['theta_regime_II'][1]:.2f}°); o ajuste usa o b do "
                      f"regime II nesses pontos.")
    else:
        print(f"\nFig. 16: arquivo não encontrado ({args.fig16}).")

    # ----------------------------------------------------- forma de s0 e k
    if args.forma == "a":
        defs0 = definir_s0("a", s0_fixo=S0_PROVISORIO,
                           origem="PROVISÓRIO: s da pose do CAD")
        k, origem_k = K_ILUSTRATIVO, "ILUSTRATIVO, NÃO MEDIDO"
    elif args.forma == "b":
        if not THETA_MIN <= args.theta_pre <= THETA_MAX:
            print(f"AVISO: θ*_pre = {args.theta_pre:g}° fora da faixa "
                  f"{THETA_MIN:g}° a {THETA_MAX:g}°.")
        defs0 = definir_s0("b", theta_pre=args.theta_pre, x_pre=args.x_pre,
                           origem="pré-tensão escolhida por argumento")
        k, origem_k = K_ILUSTRATIVO, "ILUSTRATIVO, NÃO MEDIDO"
    else:
        curva = _nome_curva(args.curva)
        if not args.fig16.is_file():
            raise SystemExit(f"forma (c) pede o arquivo da Fig. 16, não "
                             f"encontrado: {args.fig16}")
        if curva not in ajustes:
            raise SystemExit(f"forma (c) pede a curva '{args.curva}' da Fig. 16 "
                             f"({args.fig16}); disponíveis: {list(ajustes)}")
        aj = ajustes[curva]
        defs0 = definir_s0("c", s0_fixo=aj["s0"],
                           origem=f"AJUSTADO: forma da Fig. 16 ({curva})")
        k = aj["k_alvo"]
        origem_k = "AJUSTADO: forma da Fig. 16 + alvo de 40% (hipótese)"
    if args.forma != "b" and (args.theta_pre is not None or args.x_pre is not None):
        print(f"AVISO: --theta-pre/--x-pre ignorados na forma ({args.forma}).")
    if args.forma != "c" and _nome_curva(args.curva) != _nome_curva(CURVA_PROJETO):
        print(f"AVISO: --curva ignorado na forma ({args.forma}).")
    if s_zero(e, geo, defs0) < 0:
        raise SystemExit(f"s0 = {s_zero(e, geo, defs0):.3f} mm < 0 não é físico")
    padrao = (args.forma == FORMA_S0_PROJETO
              and _nome_curva(args.curva) == _nome_curva(CURVA_PROJETO))
    rotulo_projeto = "projeto padrão" if padrao else (
        f"projeto alternativo, forma ({args.forma})"
        + (f", curva {_nome_curva(args.curva)}" if args.forma == "c" else ""))
    sufixo = "" if padrao else (f"_forma_{args.forma}" + (
        f"_{_nome_curva(args.curva)}" if args.forma == "c" else ""))

    # ------------------------------------------------------- autotestes
    a = autotestes(e, geo, k, defs0, theta, e_extra=(e + 10.0, 0.5*e, 2.0*e),
                   theta_pose_cad=theta_pose, s_pose_cad=par["S_POSE"])
    print("\nAutotestes:")
    print(f"  1. resíduos regime I:    max|f1| = {a['residuo_f1']:.1e}, "
          f"max|f2| = {a['residuo_f2']:.1e} mm")
    print(f"     resíduos regime II:   max|f3| = {a['residuo_f3']:.1e}, "
          f"max|f4| = {a['residuo_f4']:.1e} mm  "
          f"(pontos na faixa: {a['n_regime_I']} em I, {a['n_regime_II']} em II)")
    print(f"     d = |P − C78| constante em q: {a['d_constante']:.1e} mm; "
          f"x_78 fórmula × pontos: {a['x78_duas_vias']:.1e} mm")
    print(f"     fechamento com o CAD: s(pose) = {a['s_pose']:.4f} mm × "
          f"S_POSE = {par['S_POSE']:g} mm (diferença {a['erro_s_pose']:.1e} mm)")
    print(f"  2. trabalho virtual:     max|ds/dq + τ/F| = {a['tv_I']:.1e} (I), "
          f"{a['tv_II'] if a['tv_II'] is None else format(a['tv_II'], '.1e')} "
          f"(II) mm/rad")
    print(f"  3. continuidade em q* = {np.degrees(a['q_estrela']):.6f}° (θ* = "
          f"{theta_star_de_q(a['q_estrela'], geo):.6f}°), 78 entre A e P: "
          f"s = {a['s_estrela']:.3f} mm, b = {a['b_estrela']:.3f} mm; "
          f"|s_I − s_II| = {a['continuidade_s']:.1e} mm, |τ_I − τ_II|/F = "
          f"{a['continuidade_tau']:.1e} mm; ordem II (q ≤ q*) / I conferida")
    pz = a["p_zero"]
    print(f"  4. p = 0: direção de OP em q* = {np.degrees(pz['direcao_OP']):.6f}° "
          f"para todo e testado (erro {pz['erro_dir']:.1e} rad); q* numérico × "
          f"fechado {pz['erro_q']:.1e} rad; |s − (|B| + |OP|)| = "
          f"{pz['erro_s']:.1e} mm; max|τ_II|/F = {pz['tau_max']:.1e} mm")
    if a["frouxo"]:
        print("  5. tração: o elástico AFROUXA em θ* = "
              + ", ".join(f"{i:.2f}° a {f:.2f}°" for i, f in a["frouxo"]))
    else:
        print("  5. tração: x ≥ 0 em toda a faixa")
    print(f"  6. τ produto vetorial × fórmula escalar: {a['tau_duas_vias']:.1e} N·m")
    print(f"     linearidade em k: {a['erro_linear_K']:.1e} N·m")
    print(f"  7. guarda de e: curvas diferem (máx. {a['guarda_e']:.3e} N·m por "
          f"N/mm); ancoragem forma {defs0.forma}: {a['ancoragem']:.1e} mm; "
          f"formas (a) {a['ancoragem_a']:.1e} e (b) {a['ancoragem_b']:.1e} mm "
          f"(teste); (b) com θ*_pre = pose e X_PRE = 0 reproduz (a): "
          f"{a['b_igual_a']:.1e} mm; e obrigatório (TypeError sem e)")

    # ----------------------------------------------------- projeto
    r = calculate_torque_curve(k, e, geo, defs0, theta)
    tp_abs = np.abs(torque_peso(theta, *peso))
    i_xmax, i_xmin = int(np.argmax(r["x"])), int(np.argmin(r["x"]))
    i_ext = int(np.argmin(r["extensao"]))
    i_pico = int(np.argmax(r["tau"]))
    frouxo = trechos_frouxos(theta, r["extensao"])
    q_est = q_estrela_numerico(e, geo, r["q"])
    theta_est = None if q_est is None else float(theta_star_de_q(q_est, geo))
    print(f"\n{rotulo_projeto.replace('projeto', 'PROJETO', 1)}, e = {e:g} mm:")
    print(f"  forma de s0 ativa: ({defs0.forma}); s0 = {r['s0']:.3f} mm — "
          f"{defs0.origem}")
    print(f"  k = {k:.5f} N/mm — {origem_k}")
    print(f"  x_max = {r['x'][i_xmax]:.3f} mm em θ* = {theta[i_xmax]:.1f}°; "
          f"x_min = {r['x'][i_xmin]:.3f} mm em θ* = {theta[i_xmin]:.1f}°")
    if frouxo:
        print("  o elástico AFROUXA em θ* = "
              + ", ".join(f"{i:.2f}° a {f:.2f}°" for i, f in frouxo)
              + f" (menor s − s0 = {r['extensao'][i_ext]:.3f} mm em θ* = "
              f"{theta[i_ext]:.1f}°)")
    else:
        print("  o elástico fica tracionado em toda a faixa")
    print(f"  pico de τ_exo = {r['tau'][i_pico]:.3f} N·m em θ* = "
          f"{theta[i_pico]:.1f}° (grade de {theta[1] - theta[0]:.1f}°)")
    angulos = np.array(THETA_TABELA_PROJETO)
    rt = calculate_torque_curve(k, e, geo, defs0, angulos)
    tp_t = np.abs(torque_peso(angulos, *peso))
    print("   θ*(°)    q(°) reg    s(mm)    x(mm)   b(mm)     F(N)  τ_exo(N·m)"
          "  |τ_peso|  τ_exo/|τ_peso|")
    for i, th in enumerate(angulos):
        print(f"{th:8.2f} {np.degrees(rt['q'][i]):7.3f} "
              f"{'II' if rt['contato'][i] else 'I':>3} {rt['s'][i]:8.3f} "
              f"{rt['x'][i]:8.3f} {rt['braco'][i]:7.3f} {rt['force'][i]:8.2f} "
              f"{rt['tau'][i]:11.3f} {tp_t[i]:9.3f} {rt['tau'][i]/tp_t[i]:14.3f}")
    print("τ positivo = anti-horário = sentido de θ* crescente. b = τ/F, só "
          "relatório.")

    # tabela em q: ângulos representativos e q*, com a forma (a) ao lado
    q_tab = np.radians(sorted(Q_TABELA + (() if q_est is None
                                          else (float(np.degrees(q_est)),))))
    rq = calculate_torque_curve(k, e, geo, defs0, theta_star_de_q(q_tab, geo))
    x_a = calculate_x(rq["s"], S0_PROVISORIO)
    print(f"\nTabela em q (e = {e:g} mm; x(a) = forma (a), s0 = S0_PROVISORIO "
          f"= {S0_PROVISORIO:g} mm; x, F e τ da forma ativa):")
    print("    q(°)    θ*(°) reg    ψ(°)    s(mm)  s−d(mm)   b(mm)  x(a)(mm)"
          "    x(mm)     F(N)   τ(N·m)  τ/k(N·m por N/mm)")
    for i, qq in enumerate(np.degrees(q_tab)):
        th_i = rq["theta_star"][i]
        smd = rq["s_menos_d"][i]
        fora = " (fora da faixa)" if not THETA_MIN <= th_i <= THETA_MAX else ""
        marca = " = q*" if q_est is not None and abs(np.radians(qq) - q_est) < 1e-12 else ""
        print(f"{qq:8.3f} {th_i:8.3f} {'II' if rq['contato'][i] else 'I':>3} "
              f"{np.degrees(rq['psi'][i]):7.3f} {rq['s'][i]:8.3f} "
              f"{'—' if np.isnan(smd) else format(smd, '.3f'):>8} "
              f"{rq['braco'][i]:7.3f} {x_a[i]:9.3f} {rq['x'][i]:8.3f} "
              f"{rq['force'][i]:8.2f} {rq['tau'][i]:8.3f} "
              f"{rq['tau'][i]/k:12.5f}{marca}{fora}")
    if theta_est is not None:
        i10 = int(np.argmin(np.abs(theta - 10.0)))
        print(f"DIVERGÊNCIA REGISTRADA (não corrigida): abaixo de θ*(q*) = "
              f"{theta_est:.2f}° (regime II) o 78 fora do eixo dá b > 0 e "
              f"τ_exo > 0 (τ_exo(10°) = {r['tau'][i10]:.3f} N·m); a patente "
              f"mostra torque zero abaixo de ~14°.")

    # ----------------------------------------------------- gráficos
    pasta = Path(__file__).parent/"results"
    pasta.mkdir(exist_ok=True)
    gerados = []
    if fig16 is not None:
        gerados.append(pasta/"ottobock_ajuste_fig16.png")
        plot_ajuste_fig16(fig16, ajustes, e, geo, peso, FIG16_FAIXA_AJUSTE,
                          gerados[-1])
    with np.errstate(divide="ignore", invalid="ignore"):
        razao = r["tau"]/tp_abs
    marcas = [(float(theta[j]), float(r["tau"][j]), float(razao[j]))
              for j in [int(np.argmin(np.abs(theta - th)))
                        for th in THETA_MARCAS_RAZAO] + [i_pico]]
    gerados.append(pasta/("ottobock_projeto_padrao.png" if padrao
                          else f"ottobock_projeto{sufixo}.png"))
    plot_projeto(theta, r["tau"], tp_abs, ALVO_FRACAO, theta_est, marcas,
                 rotulo_projeto.capitalize() + f": forma ({defs0.forma}), "
                 + f"s0 = {r['s0']:.3f} mm, k = {k:.5f} N/mm, "
                 f"e = {e:g} mm".replace(".", ","), gerados[-1])
    print("\nGráficos:")
    for g in gerados:
        print(f"  {g}")

    if VE_RODAR:
        varredura_e(geo, k, defs0, VE_THETA, VE_GRID, VE_FAMILIA, EXTRACAO_EP,
                    SINAL_PATENTE, peso, ALVO_FRACAO, pasta, VE_PLOT_FAMILIA,
                    rotulo_projeto, sufixo)
