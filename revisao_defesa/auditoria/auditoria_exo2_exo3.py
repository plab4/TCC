"""Auditoria independente das equações dos exoesqueletos 2 e 3, escritas como estão
no texto do TCC (Equações 32 a 47 e 55 a 66), contra os valores das tabelas e
contra os modelos do repositório.

Rodar na raiz do repositório:  python3 <este arquivo>
"""
import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path.cwd()
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "exo3"))
linhas = []


def reg(nome, valor, unidade="", limite=None):
    ok = "" if limite is None else ("ok" if abs(valor) <= limite else "FALHA")
    linhas.append((nome, valor, unidade, ok))


def u(graus):
    a = np.radians(graus)
    return np.array([np.cos(a), np.sin(a)])


def ang(v):
    return np.degrees(np.arctan2(v[1], v[0]))


# ====================================================================== exo 2
C1, C2, GAM = 28.978, 340.455, 80.739
E, P78 = 34.785, 7.754
Q_POSE, PHI_ABS, THB = 160.487, 277.937, 7.962
ALF = 90.0 - GAM
FI = PHI_ABS - Q_POSE                      # defasagem entre p e q
Q0 = Q_POSE - (180.0 + THB)                # Equação (33)
rAO = C1*u(-ALF) + C2*u(GAM)               # Equação (34)
A = -rAO
X = np.sqrt(E**2 + P78**2 - 2*E*P78*np.cos(np.radians(FI)))    # Equação (40)
reg("exo 2: α = 90° − γ contra 9,261°", ALF - 9.261, "°", 5e-4)
reg("exo 2: φ contra 117,450°", FI - 117.450, "°", 5e-4)
reg("exo 2: q0 contra −27,475°", Q0 + 27.475, "°", 5e-4)
reg("exo 2: θel,pose contra 97,962°", (90 + THB) - 97.962, "°", 5e-4)
reg("exo 2: |rAO| contra 341,686 mm", np.hypot(*rAO) - 341.686, "mm", 5e-4)
reg("exo 2: x contra 38,972 mm", X - 38.972, "mm", 5e-4)


def exo2(tel):
    """Circuito pelas Equações (32) e (35) a (44), como escritas."""
    q = tel + 90.0 + Q0                                       # (32)
    Pv, C78 = E*u(q), P78*u(q + FI)                           # (35)
    kappa = (Pv - A)[0]*(C78 - A)[1] - (Pv - A)[1]*(C78 - A)[0]   # (43)
    if kappa >= 0:                                            # regime II
        w = rAO + C78
        s = X + np.hypot(*w)                                  # (42)
        psi = ang(w)
        m = P78*np.sin(np.radians(q + FI - psi))              # (44)
        f = np.array([C1*np.cos(np.radians(ALF)) + C2*np.cos(np.radians(GAM))
                      + P78*np.cos(np.radians(q + FI)) - (s - X)*np.cos(np.radians(psi)),
                      -C1*np.sin(np.radians(ALF)) + C2*np.sin(np.radians(GAM))
                      + P78*np.sin(np.radians(q + FI)) - (s - X)*np.sin(np.radians(psi))])   # (38), (39)
        return q, "II", s, psi, m, f, kappa
    w = rAO + Pv
    s, psi = np.hypot(*w), ang(w)                             # (41)
    m = E*np.sin(np.radians(q - psi))                         # (44)
    f = np.array([C1*np.cos(np.radians(ALF)) + C2*np.cos(np.radians(GAM))
                  + E*np.cos(np.radians(q)) - s*np.cos(np.radians(psi)),
                  -C1*np.sin(np.radians(ALF)) + C2*np.sin(np.radians(GAM))
                  + E*np.sin(np.radians(q)) - s*np.sin(np.radians(psi))])                    # (36), (37)
    return q, "I", s, psi, m, f, kappa


# Tabela 18 (θel, q, regime, s, ψ, m)
T18 = [(0.0, 62.525, "II", 378.852, 77.142, 7.560), (10.0, 72.525, "II", 377.565, 77.072, 7.143),
       (30.0, 92.525, "I", 375.145, 77.396, 9.078), (60.0, 122.525, "I", 366.438, 79.832, 23.587),
       (90.0, 152.525, "I", 351.351, 81.402, 32.914), (97.962, 160.487, "I", 346.686, 81.607, 34.132),
       (120.0, 182.525, "I", 333.389, 81.611, 34.156), (150.0, 212.525, "I", 317.291, 80.190, 25.714),
       (180.0, 242.525, "I", 307.946, 77.368, 8.911)]
pior = dict(q=0, s=0, psi=0, m=0, f=0)
for tel, q_t, reg_t, s_t, psi_t, m_t in T18:
    q, r, s, psi, m, f, _ = exo2(tel)
    assert r == reg_t, (tel, r, reg_t)
    pior["q"] = max(pior["q"], abs(q - q_t)); pior["s"] = max(pior["s"], abs(s - s_t))
    pior["psi"] = max(pior["psi"], abs(psi - psi_t)); pior["m"] = max(pior["m"], abs(m - m_t))
    pior["f"] = max(pior["f"], float(np.max(np.abs(f))))
reg("exo 2: Tabela 18, q (9 linhas)", pior["q"], "°", 5e-4)
reg("exo 2: Tabela 18, s", pior["s"], "mm", 5e-4)
reg("exo 2: Tabela 18, ψ", pior["psi"], "°", 5e-4)
reg("exo 2: Tabela 18, m", pior["m"], "mm", 5e-4)
reg("exo 2: fechamento f1..f4 nas linhas da Tabela 18", pior["f"], "mm", 1e-9)

# contato: raiz de κ (Equação 43) e caso p = 0 (Equação 46)
a_, b_ = 20.0, 30.0
for _ in range(200):
    c_ = 0.5*(a_ + b_)
    if (exo2(a_)[6] >= 0) == (exo2(c_)[6] >= 0):
        a_ = c_
    else:
        b_ = c_
tel_c = 0.5*(a_ + b_)
reg("exo 2: contato θel contra 24,549°", tel_c - 24.549, "°", 5e-4)
reg("exo 2: q* contra 87,074°", exo2(tel_c)[0] - 87.074, "°", 5e-4)
sI = np.hypot(*(rAO + E*u(tel_c + 90 + Q0)))
reg("exo 2: s no contato contra 375,869 mm", sI - 375.869, "mm", 5e-4)
reg("exo 2: continuidade de s no contato (I contra II)", sI - (X + np.hypot(*(rAO + P78*u(tel_c + 90 + Q0 + FI)))), "mm", 1e-6)
q_p0 = ang(rAO)                                               # (46)
reg("exo 2: contato com p = 0, θel contra 13,349°", (q_p0 - 90 - Q0) - 13.349, "°", 5e-4)

# trabalho virtual ds/dq = −m (Equação 45), diferenças centradas
tel = np.r_[np.linspace(0.5, 24.0, 200), np.linspace(25.0, 179.5, 1200)]
h = 1e-5
res = [(exo2(t + h)[2] - exo2(t - h)[2])/np.radians(2*h) + exo2(t)[4] for t in tel]
reg("exo 2: ds/dq + m, regimes I e II", float(np.max(np.abs(res))), "mm/rad", 1e-5)

# peso, K40 e Tabela 20
G, M2, D2, ACG = 9.80665, 3.7702, 287.154, 0.194


def tg2(tel):
    return M2*G*D2*abs(np.cos(np.radians(tel - 90.0 + ACG)))/1000.0/1000.0*1000.0   # (47), N·m


reg("exo 2: τg(90°) contra 10,617 N·m", tg2(90.0) - 10.617, "N·m", 5e-4)
S0 = 300.750
_, _, s90, _, m90, _, _ = exo2(90.0)
K40 = 0.4*tg2(90.0)*1000.0/((s90 - S0)*m90)                   # (54)
reg("exo 2: K40 contra 2,54982 N/mm", K40 - 2.54982, "N/mm", 2e-4)
T20 = [(10, 76.815, 7.143, 195.86, 1.399, 1.879, 0.745), (30, 74.395, 9.078, 189.69, 1.722, 5.340, 0.323),
       (60, 65.688, 23.587, 167.49, 3.951, 9.212, 0.429), (90, 50.601, 32.914, 129.02, 4.247, 10.617, 0.400),
       (120, 32.638, 34.156, 83.22, 2.843, 9.176, 0.310), (150, 16.540, 25.714, 42.18, 1.084, 5.277, 0.206),
       (170, 9.306, 15.193, 23.73, 0.361, 1.808, 0.199)]
pior = dict(d=0, F=0, tau=0, tg=0, raz=0)
for tel_, d_t, m_t, F_t, tau_t, tg_t, raz_t in T20:
    _, _, s, _, m, _, _ = exo2(float(tel_))
    d = s - S0; F = 2.54982*d; tau = F*m/1000.0
    pior["d"] = max(pior["d"], abs(d - d_t)); pior["F"] = max(pior["F"], abs(F - F_t))
    pior["tau"] = max(pior["tau"], abs(tau - tau_t)); pior["tg"] = max(pior["tg"], abs(tg2(tel_) - tg_t))
    pior["raz"] = max(pior["raz"], abs(tau/tg2(tel_) - raz_t))
reg("exo 2: Tabela 20, δ", pior["d"], "mm", 6e-4)
reg("exo 2: Tabela 20, F", pior["F"], "N", 6e-3)
reg("exo 2: Tabela 20, τ", pior["tau"], "N·m", 6e-4)
reg("exo 2: Tabela 20, τg", pior["tg"], "N·m", 6e-4)
reg("exo 2: Tabela 20, τ/τg", pior["raz"], "", 6e-4)
tel = np.linspace(0.0, 180.0, 18001)
tau = np.array([2.54982*max(exo2(t)[2] - S0, 0)*exo2(t)[4]/1000.0 for t in tel])
reg("exo 2: pico de τ contra 4,379 N·m", tau.max() - 4.379, "N·m", 5e-4)
reg("exo 2: ângulo do pico contra 79,1°", tel[tau.argmax()] - 79.1, "°", 0.06)
ext = np.array([exo2(t)[2] - S0 for t in tel])
reg("exo 2: extensão em 0° contra 78,10 mm", ext[0] - 78.10, "mm", 6e-3)
reg("exo 2: extensão em 180° contra 7,20 mm", ext[-1] - 7.20, "mm", 6e-3)

# Steiner (Tabela 14)
reg("exo 2: Steiner do membro, 0,113765 + M d² contra 0,434676", 0.113765 + 3.6062*0.298310**2 - 0.434676, "kg·m²", 2e-6)
reg("exo 2: Steiner do conjunto, 0,125134 + M d² contra 0,436010", 0.125134 + 3.7702*0.287154**2 - 0.436010, "kg·m²", 5e-6)

# ====================================================================== exo 3
C1c, C2c, Rc, GAMc, QC = 70.711, 90.587, 26.443, 61.26, 61.724


def exo3(q):
    """Equações (56) a (60), como escritas."""
    d = -(C1c*u(GAMc) + C2c*u(180.0 - q))                     # (58)
    S = np.sqrt(d @ d - Rc**2)
    fi = (ang(d) + np.degrees(np.arctan2(S, Rc))) % 360
    te = (fi - 90.0) % 360
    f1 = S*np.cos(np.radians(te)) + Rc*np.cos(np.radians(fi)) - C2c*np.cos(np.radians(q)) + C1c*np.cos(np.radians(GAMc))   # (56)
    f2 = S*np.sin(np.radians(te)) + Rc*np.sin(np.radians(fi)) + C2c*np.sin(np.radians(q)) + C1c*np.sin(np.radians(GAMc))   # (57)
    b = C2c*u(180.0 - q) + Rc*u(fi)                           # (59)
    bm = np.hypot(*b)
    beta = ((180.0 - q) - ang(b) + 180) % 360 - 180
    ma = C1c*np.sin(np.radians(GAMc - te))                    # (60)
    ma2 = -bm*np.sin(np.radians(te + q + beta))
    return S, fi, te, bm, beta, ma, ma2, max(abs(f1), abs(f2))


S, fi, te, bm, beta, ma, ma2, f = exo3(QC)
reg("exo 3: S na pose contra 139,575 mm (CAD)", S - 139.575, "mm", 5e-4)
reg("exo 3: φ na pose contra 352,869° (CAD)", fi - 352.869, "°", 5e-4)
reg("exo 3: θ na pose contra 262,869° (CAD)", te - 262.869, "°", 5e-4)
reg("exo 3: b na pose contra 78,292 mm (CAD)", bm - 78.292, "mm", 1.5e-3)
reg("exo 3: β na pose contra 15,979° (CAD)", beta - 15.979, "°", 5e-4)
reg("exo 3: braço na pose contra 26,04 mm", ma - 26.04, "mm", 6e-3)
reg("exo 3: Θ na pose contra −88,465°", -(QC + 26.741) + 88.465, "°", 5e-4)
qs = np.linspace(-48.0, 75.0, 2000)
est = np.array([exo3(q) for q in qs])
reg("exo 3: fechamento f1 e f2 na faixa (solução fechada)", float(est[:, 7].max()), "mm", 1e-9)
reg("exo 3: duas formas do braço, Equação (60)", float(np.max(np.abs(est[:, 5] - est[:, 6]))), "mm", 1e-9)
# Tabela 27: Θ, S, ma
for Th, S_t, ma_t in [(-75.0, 129.57, 33.94), (-56.4, 112.75, 43.78), (-40.3, 95.67, 51.11),
                      (-23.8, 76.02, 57.29), (0.0, 44.17, 63.26), (4.0, 38.35, 63.80)]:
    S, *_r = exo3(-Th - 26.741)
    reg(f"exo 3: Tabela 27, Θ = {Th:g}°: S", S - S_t, "mm", 6e-3)
    reg(f"exo 3: Tabela 27, Θ = {Th:g}°: braço", _r[4] - ma_t, "mm", 6e-3)
# ponto morto e limite de subida (Equação 63)
a_, b_ = 90.0, 110.0
for _ in range(200):
    c_ = 0.5*(a_ + b_)
    if np.sign(exo3(a_)[5]) == np.sign(exo3(c_)[5]):
        a_ = c_
    else:
        b_ = c_
reg("exo 3: braço nulo, q contra 101,77°", 0.5*(a_ + b_) - 101.77, "°", 6e-3)
reg("exo 3: braço nulo, θ − (γ + 180°)", exo3(0.5*(a_ + b_))[2] - (GAMc + 180.0), "°", 1e-6)
a_, b_ = -60.0, -40.0
g = lambda q: float(np.sum((C1c*u(GAMc) + C2c*u(180.0 - q))**2) - Rc**2)
for _ in range(200):
    c_ = 0.5*(a_ + b_)
    if np.sign(g(a_)) == np.sign(g(c_)):
        a_ = c_
    else:
        b_ = c_
reg("exo 3: S = 0, q contra −48,75°", 0.5*(a_ + b_) + 48.75, "°", 6e-3)
reg("exo 3: S = 0, Θ contra 22,0°", -(0.5*(a_ + b_) + 26.741) - 22.0, "°", 0.06)
# giro da primária: dθp/dq = −ma/R (Equação 65), θp = φ + q − S/R + constante
def tp3(q):
    S_, fi_, *_ = exo3(q)
    return np.radians(fi_ + q) - S_/Rc


hq = 1e-4                                                     # graus; diferença centrada
res = []
for q in np.linspace(-45.0, 75.0, 1500):
    dfi = ((exo3(q + hq)[1] - exo3(q - hq)[1] + 180) % 360) - 180          # sem salto de 360°
    dtp = (np.radians(dfi + 2*hq) - (exo3(q + hq)[0] - exo3(q - hq)[0])/Rc)/np.radians(2*hq)
    res.append(dtp + exo3(q)[5]/Rc)
reg("exo 3: dθp/dq + ma/R (diferença centrada, passo 1e-4°)", float(np.max(np.abs(res))), "", 1e-6)
# pontos A e D (seção 4.3.1)
Ap, Dp = -C1c*u(GAMc), C2c*u(180.0 - QC)
reg("exo 3: A contra (−34,000; −62,000)", float(np.max(np.abs(Ap - [-34.0, -62.0]))), "mm", 2e-3)
reg("exo 3: D contra (−42,913; 79,778)", float(np.max(np.abs(Dp - [-42.913, 79.778]))), "mm", 2e-3)
# escala e Steiner (Tabela 22)
reg("exo 3: Steiner do conjunto, 0,140841 + M d² contra 0,450320", 0.140841 + 4.4024*0.2651**2 - 0.450320, "kg·m²", 2e-4)
reg("exo 3: M g d do membro contra 10,55 N·m", 3.6062*G*0.298310 - 10.55, "N·m", 6e-3)
reg("exo 3: escala c = 10,5496/78,22 contra 0,1349", 3.6062*G*0.298310/78.223 - 0.1349, "N·m/un.", 6e-5)

# ====================================================================== contra os modelos do repositório
import torque_model_ottobock as tmo          # noqa: E402
import circuito_cabo560 as cc                # noqa: E402
N2 = json.loads((RAIZ/"results/ottobock_tcc_numeros.json").read_text(encoding="utf-8"))
reg("exo 2 (modelo): E_CAD", tmo.E_CAD - E, "mm", 0)
reg("exo 2 (modelo): alvo de 40%", tmo.ALVO_FRACAO - 0.4, "", 0)
for q in (QC, 0.0, -30.0):
    Sm, fim, tem, bmm, betam, bram = cc.circuito(q)
    S, fi, te, bm, beta, ma, *_ = exo3(q)
    reg(f"exo 3 (modelo): circuito em q = {q:g}°", max(abs(S - Sm), abs(fi - fim), abs(te - tem), abs(bm - bmm), abs(beta - betam), abs(ma - bram)), "mm ou °", 1e-9)

larg = max(len(n) for n, *_ in linhas)
for nome, v, un, ok in linhas:
    print(f"{nome:<{larg}}  {v:12.4g} {un:<8} {ok}")
falhas = [n for n, *_, ok in linhas if ok == "FALHA"]
print(f"\n{len(linhas)} conferências; FALHAS:", falhas if falhas else "nenhuma")
sys.exit(1 if falhas else 0)
