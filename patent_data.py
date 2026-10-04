"""Dados extraídos da curva torque × θ* da patente (fornecidos pelo autor).

Unidades: θ* em GRAUS (o comentário original dizia "rad", mas os valores vão
de 42,9 a 193,0, o que só faz sentido em graus; a pose do CAD também está em
graus, 115,017°). Torque em N·m, positivo no sentido usado pela patente.
"""
import numpy as np

THETA_STAR_EXTRACTION = np.array([
    193.017000, 189.146030, 185.848540, 181.690840, 177.676500, 171.368250,
    167.353920, 162.766100, 155.310910, 148.429190, 143.267900, 135.239222,
    128.930978, 123.196211, 115.167540, 108.285820, 100.830620,  94.809110,
     88.500870,  83.339580,  78.034920,  72.586890,  68.142450,  62.407680,
     57.819870,  54.379010,  50.938150,  45.776860,  42.909470,
])  # graus

TORQUE_EXTRACTION = np.array([
      0.443038,  11.518990,  23.702530,  38.101270,  50.506330,  70.000000,
     81.962030,  94.145570, 111.867100, 125.158200, 133.354400, 142.436700,
    146.202500, 147.310100, 144.651900, 138.892400, 130.031600, 120.063300,
    108.987300,  98.354430,  87.500000,  75.981010,  66.455700,  55.158230,
     46.518990,  39.873420,  34.335440,  27.025320,  22.816460,
])  # N·m


def load_patent_data():
    """Dados da patente ordenados por θ* crescente."""
    order = np.argsort(THETA_STAR_EXTRACTION)
    return {
        "theta_star": THETA_STAR_EXTRACTION[order],
        "torque": TORQUE_EXTRACTION[order],
    }


def estimate_peak(theta, torque):
    """Pico da curva amostrada: parábola pelo maior ponto e seus vizinhos."""
    i = int(np.clip(np.argmax(torque), 1, len(torque) - 2))
    a, b, c = np.polyfit(theta[i-1:i+2], torque[i-1:i+2], 2)
    theta_peak = -b/(2*a)
    return theta_peak, np.polyval([a, b, c], theta_peak)
