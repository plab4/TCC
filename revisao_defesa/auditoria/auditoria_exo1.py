"""Teste da formulação do exoesqueleto 1: as Equações (2) a (29) da seção 3.1,
escritas como estão no texto, contra o modelo (torque_model.py) e entre si.

Rodar na raiz do repositório:  python3 <este arquivo>
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path.cwd()))
import torque_model as tm  # noqa: E402
from patent_data import load_patent_data  # noqa: E402

h, p, C, R = tm.H_CALIBRADO, tm.P, tm.C, tm.R
al = np.radians(tm.ALPHA)
K, XP = tm.K, tm.X_POSE
th = np.linspace(tm.THETA_MIN, tm.THETA_MAX, 2001)        # θ* em graus
linhas = []


def linha(nome, valor, unidade="", limite=None):
    ok = "" if limite is None else ("ok" if valor <= limite else "FALHA")
    linhas.append((nome, valor, unidade, ok))


def u(a):
    return np.array([np.cos(a), np.sin(a)])


def u_perp(a):
    return np.array([-np.sin(a), np.cos(a)])


def cadeia(ts, hh=h):
    """Equações (2), (5), (9), (10), (12), (16), (17), (18), como escritas."""
    q = np.radians(ts) - np.pi/2 - al                                   # (2)
    B = np.array([hh*np.sin(al) - p*np.cos(al),
                  hh*np.cos(al) + p*np.sin(al)])                        # (5)
    W = -(B[:, None] + C*u(q))                                          # (9)
    rho = np.hypot(W[0], W[1])
    s = np.sqrt(rho**2 - R**2)
    phi = np.arctan2(W[1], W[0]) - np.arctan2(R, s)                     # (10)
    D = -C*u(q)
    T = D + R*np.array([np.sin(phi), -np.cos(phi)])                     # (12)
    m = B[0]*np.sin(phi) - B[1]*np.cos(phi)                             # (16)
    psi = np.angle(np.exp(1j*(phi - (q + np.pi))))                      # (17)
    ell = s - R*psi                                                     # (18)
    return dict(q=q, B=B, W=W, rho=rho, s=s, phi=phi, D=D, T=T, m=m, psi=psi, ell=ell)


c = cadeia(th)
q, B, s, phi, T, m = c["q"], c["B"], c["s"], c["phi"], c["T"], c["m"]

# (2), (9), (10) contra o modelo
linha("Eq. (2) q contra calculate_q", np.max(np.abs(q - tm.calculate_q(th))), "rad", 1e-12)
s_mod = tm.calculate_tangent_span(tm.calculate_rho(q, h))
linha("Eq. (9) s contra o modelo", np.max(np.abs(s - s_mod)), "mm", 1e-9)
linha("Eq. (10) φ contra calculate_phi",
      np.max(np.abs(phi - tm.calculate_phi(q, s_mod, h))), "rad", 1e-12)
linha("Eq. (9): ρ > R em toda a faixa (folga mínima)", -np.min(c["rho"] - R), "mm", 0.0)

# (3) e (4)
phi_pat = tm.ANGLE_OFFSET - th
linha("Eqs. (3) e (4): θ_el = φ_pat + 90° = 223,017° − θ*",
      np.max(np.abs((phi_pat + 90.0) - (223.017 - th))), "°", 1e-9)

# (6) vetorial e (7), (8) escalares
res6 = B[:, None] + s*u(phi) + R*u_perp(phi) + C*u(q)
linha("Eq. (6) B + s u(φ) + R u⊥(φ) + C u(q)", np.max(np.abs(res6)), "mm", 1e-9)
f1 = h*np.sin(al) - p*np.cos(al) + s*np.cos(phi) - R*np.sin(phi) + C*np.cos(q)   # (7)
f2 = h*np.cos(al) + p*np.sin(al) + s*np.sin(phi) + R*np.cos(phi) + C*np.sin(q)   # (8)
linha("Eq. (7) f1", np.max(np.abs(f1)), "mm", 1e-9)
linha("Eq. (8) f2", np.max(np.abs(f2)), "mm", 1e-9)
g1, g2 = tm.calculate_closure_residuals(q, s, phi, h)
linha("Eqs. (7) e (8) contra calculate_closure_residuals",
      max(np.max(np.abs(f1 - g1)), np.max(np.abs(f2 - g2))), "mm", 1e-12)
linha("Eqs. (7) e (8) = componentes x e y da Eq. (6)",
      max(np.max(np.abs(f1 - res6[0])), np.max(np.abs(f2 - res6[1]))), "mm", 1e-12)

# (11): fórmula original = ρ em θ* + 180°
rho_orig = np.sqrt(h**2 + p**2 + C**2 + 2*C*(h*np.cos(np.radians(th)) + p*np.sin(np.radians(th))))
rho_180 = np.hypot(*(-(B[:, None] + C*u(np.radians(th + 180.0) - np.pi/2 - al))))
linha("Eq. (11) ρ_orig(θ*) = ρ(θ* + 180°)", np.max(np.abs(rho_orig - rho_180)), "mm", 1e-9)

# (12) a (15): duas vias para T
Bn = np.hypot(*B)
phiB = np.arctan2(B[1], B[0])
b = np.sqrt(s**2 + Bn**2 + 2*s*Bn*np.cos(phi - phiB))                  # (13)
beta = np.arccos((b**2 + C**2 - R**2)/(2*b*C))                         # (14)
T15 = b*np.array([-np.cos(beta - q), np.sin(beta - q)])                # (15)
linha("Eq. (12) T contra ponto_tangencia",
      np.max(np.abs(T - tm.ponto_tangencia(q, phi))), "mm", 1e-9)
linha("Eqs. (12) e (15): mesmo T", np.max(np.abs(T - T15)), "mm", 1e-9)
linha("Eq. (13): b = |T|", np.max(np.abs(b - np.hypot(*T))), "mm", 1e-9)
linha("Eq. (13): T = B + s u(φ)", np.max(np.abs(T - (B[:, None] + s*u(phi)))), "mm", 1e-9)
linha("b entre C − R e C + R (excesso)",
      max(np.max((C - R) - b), np.max(b - (C + R))), "mm", 0.0)

# (16)
linha("Eq. (16) m contra braco_perpendicular",
      np.max(np.abs(m - tm.braco_perpendicular(phi, h))), "mm", 1e-12)
linha("Eq. (16): |m| ≤ |B| (excesso)", np.max(np.abs(m) - Bn), "mm", 0.0)
linha("|B| = √(h² + p²) com h = 22,701 mm", Bn, "mm")

# (17), (18) e (19)
linha("Eq. (17): ψ ∈ (−π, π) (máx |ψ| em graus)", np.degrees(np.max(np.abs(c["psi"]))), "°", 180.0)
linha("Eq. (18) ℓ contra comprimento_caminho",
      np.max(np.abs(c["ell"] - tm.comprimento_caminho(q, s, phi))), "mm", 1e-12)
dt = 1e-4                                                               # graus
dl = (cadeia(th + dt)["ell"] - cadeia(th - dt)["ell"])/np.radians(2*dt)
linha("Eq. (19) dℓ/dθ* − m (diferenças centradas, passo 1e-4°)",
      np.max(np.abs(dl - m)), "mm/rad", 1e-6)
for nome, cam in (("ℓ = s", c["s"]), ("ℓ = s + Rψ", c["s"] + R*c["psi"])):
    cp = cadeia(th + dt)
    cm = cadeia(th - dt)
    alt_p = cp["s"] if nome == "ℓ = s" else cp["s"] + R*cp["psi"]
    alt_m = cm["s"] if nome == "ℓ = s" else cm["s"] + R*cm["psi"]
    linha(f"Eq. (19) com {nome} (deve falhar)",
          np.max(np.abs((alt_p - alt_m)/np.radians(2*dt) - m)), "mm/rad")

# (20), (21), (22)
s0 = cadeia(np.array([tm.THETA_POSE]))["ell"][0] - XP                  # (20)
linha("Eq. (20) s0 contra s_zero", abs(s0 - tm.s_zero(h)), "mm", 1e-12)
delta = np.maximum(c["ell"] - s0, 0.0)                                  # (21)
F = K*delta
V = -F*u(phi)                                                           # (22)
tau_cruz = (T[0]*V[1] - T[1]*V[0])/1000
tau_m = -F*m/1000
linha("Eq. (22) (TxVy − TyVx)/1000 = −Fm/1000", np.max(np.abs(tau_cruz - tau_m)), "u.p.", 1e-9)
tau_mod = tm.calculate_torque_curve(K, h, th)["tau"]
linha("Eq. (22) τ contra calculate_torque_curve", np.max(np.abs(tau_m - tau_mod)), "u.p.", 1e-9)
linha("Eq. (21): δ > 0 em toda a faixa (δ mínimo)", np.min(c["ell"] - s0), "mm")

# (23) e (24)
th_pm = 180.0 + np.degrees(np.arctan2(p, h)) + np.degrees(np.arcsin(R/C))   # (23)
linha("Eq. (23) θ*_pm contra a bissecção de m = 0",
      abs(th_pm - tm.ponto_morto_numerico(h)), "°", 1e-8)
linha("Eq. (23): m(θ*_pm)", abs(cadeia(np.array([th_pm]))["m"][0]), "mm", 1e-9)
h24 = p/np.tan(np.radians(th_pm - 180.0) - np.arcsin(R/C))               # (24)
linha("Eq. (24) devolve o h da Eq. (23)", abs(h24 - h), "mm", 1e-9)
linha("θ*_pm com h = 22,701 mm", th_pm, "°")

# (25) e (26)
gam = np.radians(th - tm.THETA_POSE + tm.ALPHA + 90.0 - tm.ANGLE_OFFSET)   # (25)
xg = tm.CG_DX_MM*np.cos(gam) - tm.CG_DY_MM*np.sin(gam)
taug = tm.MASS_KG*tm.GRAVITY*np.abs(xg)/1000                              # (26)
linha("Eq. (26) τ_g contra torque_peso", np.max(np.abs(taug - tm.torque_peso(th))), "N·m", 1e-12)

# (27): b × f = bF sin(φ + β − q) = −F m
f = -F*u(phi)
bxf = T15[0]*f[1] - T15[1]*f[0]
linha("Eq. (27) bx fy − by fx = bF sin(φ + β − q)",
      np.max(np.abs(bxf - b*F*np.sin(phi + beta - q))), "N·mm", 1e-6)
linha("Eq. (27): −b sin(φ + β − q) = m",
      np.max(np.abs(-b*np.sin(phi + beta - q) - m)), "mm", 1e-9)

# (28) e (29) com os 29 pontos extraídos
pat = load_patent_data()
g = -tm.calculate_torque_curve(1.0, h, pat["theta_star"])["tau"]          # g_i = −τ(θ*_i; h, 1)
y = pat["torque"]
K28 = (g @ y)/(g @ g)                                                     # (28)
linha("Eq. (28) K com h = 22,701 mm e X_pose = 37,383 mm", K28, "")
e = K*g - y
linha("Eq. (29) RMSE com K = 174,68", np.sqrt(np.mean(e**2)), "u.p.")
linha("Eq. (29) MAE", np.mean(np.abs(e)), "u.p.")
linha("Eq. (29) R²", 1 - np.sum(e**2)/np.sum((y - y.mean())**2), "")

larg = max(len(n) for n, *_ in linhas)
for nome, v, un, ok in linhas:
    print(f"{nome:<{larg}}  {v:12.4g} {un:<7} {ok}")
falhas = [n for n, *_, ok in linhas if ok == "FALHA"]
print("\nFALHAS:", falhas if falhas else "nenhuma")
sys.exit(1 if falhas else 0)
