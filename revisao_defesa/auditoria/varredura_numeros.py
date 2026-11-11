import json, re, sys, math
from pathlib import Path
REV = Path(sys.argv[1]); TEX = Path(sys.argv[2])
def flat(d, p=''):
    out = []
    if isinstance(d, dict):
        for k, v in d.items(): out += flat(v, f'{p}.{k}' if p else str(k))
    elif isinstance(d, list):
        for i, v in enumerate(d): out += flat(v, f'{p}[{i}]')
    elif isinstance(d, (int, float)) and not isinstance(d, bool):
        out.append((p, float(d)))
    return out
vals = flat(json.load(open(REV/'results/tcc_numeros.json', encoding='utf8')), 'exo1') + \
       flat(json.load(open(REV/'results/ottobock_tcc_numeros.json', encoding='utf8')), 'exo2') + \
       flat(json.load(open(REV/'results/exo3_tcc_numeros.json', encoding='utf8')), 'exo3')
sys.path.insert(0, str(REV))
import torque_model as tm, torque_model_ottobock as tmo
for nome in dir(tm):
    v = getattr(tm, nome)
    if nome.isupper() and isinstance(v, (int, float)): vals.append((f'tm.{nome}', float(v)))
for k, v in getattr(tmo, 'PARAMETROS_CAD', {}).items():
    if isinstance(v, (int, float)): vals.append((f'tmo.CAD.{k}', float(v)))

import csv
sys.path.insert(0, str(REV/'exo3'))
import circuito_cabo560 as cc3
for nome in dir(cc3):
    v = getattr(cc3, nome)
    if nome.isupper() and isinstance(v, (int, float)): vals.append((f'cc3.{nome}', float(v)))
for arq in ['fig16_curvas.csv','results/tcc_tabela_patente.csv','results/vh_h_notaveis.csv','results/ve_e_notaveis.csv','exo3/fig16_curvas.csv']:
    txt=(REV/arq).read_text(encoding='utf8').splitlines()
    for linha in txt:
        if linha.startswith('#'): continue
        for campo in re.split(r'[;,\t]', linha.replace(',', '.') if ';' in linha else linha):
            try: vals.append((arq, float(campo)))
            except ValueError: pass
from patent_data import load_patent_data
pdat=load_patent_data()
for a,b in zip(pdat['theta_star'],pdat['torque']):
    vals.append(('pat.theta',float(a))); vals.append(('pat.tq',float(b)))
    vals.append(('pat.phi',float(tm.ANGLE_OFFSET-a))); vals.append(('pat.el',float(tm.ANGLE_OFFSET-a+90)))

num = re.compile(r'(?<![\w.,])([−+-]?)(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(?:\s*×\s*10\\textsuperscript\{([−-]?\d+)\})?')
textos = {}
for f in ['resumo.tex'] + [f'capitulos/{c}.tex' for c in ('introducao','fundamentacao','materiais_metodos','resultados','conclusao','apendices')]:
    textos[f] = (TEX/f).read_text(encoding='utf8')
naocasados = []
total = 0
for f, t in textos.items():
    for ln, linha in enumerate(t.splitlines(), 1):
        if linha.lstrip().startswith('%'): continue
        limpa = re.sub(r'\\(label|ref|eqref|cite|textcite|includegraphics|caption\{[^}]*\}\\label)\{[^}]*\}', ' ', linha)
        limpa = re.sub(r'\\hsize=[\d.]+', ' ', limpa)
        for m in num.finditer(limpa):
            sinal, inteiro, dec, exp = m.groups()
            if dec is None and exp is None: continue          # inteiros: à parte
            x = float(inteiro.replace('.', '') + ('.' + dec if dec else ''))
            nd = len(dec) if dec else 0
            if exp: x *= 10 ** int(exp.replace('−', '-'))
            if sinal in ('−', '-'): x = -x
            total += 1
            ok = []
            for p, v in vals:
                for cand in (v, -v, abs(v), 100 * v, 100*abs(v)):
                    if exp:
                        if cand != 0 and abs(cand - x) <= 0.051 * abs(x): ok.append(p); break
                    elif round(cand, nd) == round(x, nd) or abs(cand - x) <= 0.5 * 10 ** (-nd) + 1e-12:
                        ok.append(p); break
                if ok: break
            if not ok:
                ctx = limpa[max(0, m.start()-60):m.end()+30].replace('\n', ' ')
                naocasados.append((f, ln, m.group(0), ctx))
print('decimais no texto:', total, 'sem correspondência direta:', len(naocasados))
for f, ln, s, ctx in naocasados:
    print(f'{f}:{ln}: [{s}]  ...{ctx}...')
