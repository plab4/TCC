#!/usr/bin/env python3
"""
Versão condensada para a defesa (até 70 páginas), sem alterar a base.

Parte do documento longo revisado (os blocos de tcc/gerar_tcc_fundido.py com as
mudanças de tcc/revisao_defesa.py) e monta outro documento com o plano declarado
em tcc/condensado_defesa.py: blocos mantidos, blocos com trechos trocados,
parágrafos e títulos novos. Equações, figuras e tabelas mantidas são as mesmas da
base, e toda a numeração (seções, equações, figuras e tabelas) é refeita.

Uso (na raiz do repositório):
    python3 tcc/gerar_condensado.py --dump   # texto do documento longo, com índices
    python3 tcc/gerar_condensado.py          # conteúdo condensado (DOCX fundido)
    python3 tcc/gerar_condensado.py --tudo   # também LaTeX, PDF e DOCX no formato FT

Nada é gravado em tcc/ nem em latex/; tudo sai em revisao_defesa/.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_tcc_fundido as g  # noqa: E402
import gerar_revisado as gr  # noqa: E402
from nomes import ORIGINAL  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "revisao_defesa"
BUILD = SAIDA / "build_condensado"
NOME = gr.NOME
FUNDIDO_COND = BUILD / "fundido_condensado.docx"
DOCX_FT = SAIDA / f"{NOME}.docx"

NUM_SEC = r"\d+(?:\.\d+)+"
LISTA_SEC = rf"{NUM_SEC}(?:(?:\s+a\s+|\s+e\s+|,\s*){NUM_SEC})*"


# ======================================================================
# marcas de numeração: números do documento longo ↔ ⟦T:chave⟧
# ======================================================================

def _figura_de_patente(n, resto, lista):
    """Mesma regra de tcc/gerar_latex.py: figura com letra, seguida de 'da patente',
    'da EP' ou 'da US', a 56 e a lista '1, 16 e 17' são das patentes."""
    return bool(resto.startswith((" da patente", " da EP", " da US")) or re.match(r", p\. \d", resto)
                or re.match(r"[A-Z]\b", resto) or n == 56 or lista.startswith(", 16"))


class Marcador:
    """Troca os números de tabela, figura e equação (numeração do documento longo)
    por marcas, e conta o que ficou literal."""

    def __init__(self, num):
        self.inv = {t: {v: k for k, v in num[t].items()} for t in "TFE"}

    def _lista(self, tipo, texto):
        return re.sub(r"\d+", lambda m: f"⟦{tipo}:{self.inv[tipo][int(m.group(0))]}⟧", texto)

    def regras(self, legenda=False):
        inv = self.inv
        r = []
        if legenda:
            r.append((r"^(Tabela|Figura) (\d+)(?=: | —)",
                      lambda m: f"{m.group(1)} ⟦{m.group(1)[0]}#{inv[m.group(1)[0]][int(m.group(2))]}⟧"))
        r.append((r"\b(Tabelas?) (\d+(?:, \d+)*(?: (?:e|a) \d+)?)",
                  lambda m: m.group(1) + " " + self._lista("T", m.group(2))))

        def fig(m):
            if _figura_de_patente(int(m.group(2)), m.group(4), m.group(3)):
                return m.group(0)
            return m.group(1) + " " + self._lista("F", m.group(2) + m.group(3))
        r.append((r"\b(Figuras?) (\d+)((?:, \d+)*(?: (?:e|a) \d+)?)(?=(.{0,14}))", fig))
        r.append((r"\b(Equaç(?:ão|ões)) (\(\d+\)(?:(?:, | e | a )\(\d+\))*)",
                  lambda m: m.group(1) + " " + self._lista("E", m.group(2))))
        return r

    def texto(self, t):
        """Marca um texto simples (parágrafo novo, na marcação do gerador)."""
        for padrao, repl in self.regras():
            t = re.sub(padrao, repl, t)
        return t

    def paragrafo(self, p, legenda=False):
        return g._editar_paragrafo(p, self.regras(legenda))


# ======================================================================
# documento longo revisado, com marcas
# ======================================================================

def _ler_original():
    with zipfile.ZipFile(RAIZ / "tcc" / ORIGINAL) as zin:
        partes = {n: zin.read(n) for n in zin.namelist()}
        infos = {i.filename: i for i in zin.infolist()}
    doc = partes["word/document.xml"].decode("utf-8")
    b0 = doc.index("<w:body>") + len("<w:body>")
    b1 = doc.rindex("<w:sectPr")
    return partes, infos, doc, b0, b1


def base_marcada():
    """(blocos, num, contexto): blocos = [(origem, xml com marcas)] do documento
    longo revisado; num = numeração do documento longo; contexto = partes do pacote."""
    import revisao_defesa as rd
    partes, infos, doc, b0, b1 = _ler_original()
    orig, final, removidos = g.montar(doc[b0:b1])
    cit = g.citacoes(" ".join(g.texto(x) for o, x in final if o == "n" and "⟦CITADOS⟧" not in x))
    final = [(o, x.replace("⟦CITADOS⟧", escape(cit))) for o, x in final]
    assert all(len(g.blocos(x)) == 1 for _, x in final)
    res, num, _ = g.numerar(final, 0)
    marc = Marcador(num)

    # 1. a marcação inversa reproduz as marcas da base em todos os parágrafos
    falhas = []
    for (o, xm), (_, xr) in zip(final, res):
        for pm, pr in zip(g.PARAGRAFO.findall(xm), g.PARAGRAFO.findall(xr)):
            volta = marc.paragrafo(pr, legenda=True)
            base = g.MARCA.sub(lambda m: m.group(0) if m.group(1) != "S" else str(num["S"][m.group(3)]),
                               g.texto(pm))
            if base != g.texto(volta) and not re.fullmatch(r"\(⟦E#[^⟧]+⟧\)", base):
                falhas.append((base, g.texto(volta)))
    # 2. mudanças da revisão, aplicadas ao corpo numerado e marcadas de volta
    corpo = "".join(x for _, x in res)
    corpo_rev, registro = gr.aplicar(corpo, list(rd.MUDANCAS), False, getattr(rd, "GLOBAIS", ()), ())
    novos = g.blocos(corpo_rev)
    import difflib
    velhos = [x for _, x in res]
    sm = difflib.SequenceMatcher(a=velhos, b=novos, autojunk=False)
    blocos = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            blocos += final[i1:i2]
            continue
        if op == "insert":       # parágrafo dividido cujo primeiro pedaço ficou igual
            blocos += [(final[i1 - 1][0], marc.paragrafo(novos[j], legenda=True)) for j in range(j1, j2)]
            continue
        assert op == "replace", (op, i1, i2, j1, j2)
        origem = final[i1][0]
        if i2 - i1 == j2 - j1:
            pares = zip(range(i1, i2), range(j1, j2))
            for i, j in pares:
                pm, pr, pn = (g.PARAGRAFO.findall(x) for x in (final[i][1], velhos[i], novos[j]))
                if len(pm) == len(pn):
                    # mesma estrutura: só os parágrafos alterados são marcados de novo
                    xml = novos[j]
                    for a, b, c in zip(pm, pr, pn):
                        if b == c:
                            assert xml.count(c) >= 1
                            xml = xml.replace(c, a, 1)
                        else:
                            xml = xml.replace(c, marc.paragrafo(c, legenda=True), 1)
                    blocos.append((final[i][0], xml))
                else:
                    blocos += [(final[i][0], marc.paragrafo(b, legenda=True)) for b in g.blocos(novos[j])]
        else:
            for j in range(j1, j2):
                assert novos[j].startswith("<w:p"), novos[j][:80]
                blocos.append((origem, marc.paragrafo(novos[j], legenda=True)))
    # conferência: numerados, os blocos reproduzem o corpo revisado
    volta, num2, _ = g.numerar(blocos, 0)
    assert "".join(x for _, x in volta) == corpo_rev, "a marcação inversa não reproduz a revisão"
    assert num2["T"] == num["T"] and num2["F"] == num["F"] and num2["E"] == num["E"]
    return blocos, num, {"partes": partes, "infos": infos, "doc": doc, "b0": b0, "b1": b1,
                         "falhas_marcacao": falhas, "registro": registro, "resolvidos": volta}


def estilo(b):
    m = re.search(r'<w:pStyle w:val="([^"]+)"', b[:400])
    return m.group(1) if m else ""


def descrever(i, origem, xml):
    """Linha(s) de texto de um bloco, para o dump."""
    if xml.startswith("<w:tbl"):
        linhas = re.findall(r"<w:tr[ >].*?</w:tr>", xml, flags=re.S)
        if "@@OMML" in xml:
            rot = re.findall(r"\((\d+)\)", g.texto(xml))
            eqs = [g.EQUACOES[int(k) - 1] for k in re.findall(r"@@OMML(\d+)@@", xml)]
            return [f"[{i}]{origem} EQ {rot}: " + "  ||  ".join(eqs)]
        if "<m:oMath" in xml:
            return [f"[{i}]{origem} EQ(original) {g.texto(xml)}"]
        saida = [f"[{i}]{origem} TABELA {len(linhas)} linhas"]
        for ln in linhas:
            cels = [g.texto(c) for c in re.findall(r"<w:tc>.*?</w:tc>", ln, flags=re.S)]
            saida.append("      | " + " | ".join(cels))
        return saida
    t = g.texto(xml)
    if "<w:drawing" in xml:
        d = re.search(r'descr="([^"]*)"', xml)
        t = f"<FIGURA {d.group(1)[:80] if d else ''}> {t}"
    e = estilo(xml)
    return [f"[{i}]{origem}{'{' + e + '}' if e else ''} {t}"]


def dump(destino):
    blocos, num, ctx = base_marcada()
    linhas = []
    for i, ((o, _), (_, xr)) in enumerate(zip(blocos, ctx["resolvidos"])):
        linhas += descrever(i, o, xr)
    Path(destino).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"{destino}: {len(blocos)} blocos; falhas da marcação inversa: {len(ctx['falhas_marcacao'])}")
    for a, b in ctx["falhas_marcacao"][:20]:
        print("  base :", a)
        print("  volta:", b)
    sha = hashlib.sha256("".join(x for _, x in blocos).encode("utf-8")).hexdigest()
    print("sha256 dos blocos marcados:", sha[:16])


if __name__ == "__main__":
    if "--dump" in sys.argv[1:]:
        dump(sys.argv[sys.argv.index("--dump") + 1])
