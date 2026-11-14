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
NOME = "TCC_Modelagem_de_mecanismos_passivos_revisado_para_defesa"      # segue o título novo
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


# ======================================================================
# montagem da versão condensada
# ======================================================================

TITULO_NUM = re.compile(r"^(\d+(?:\.\d+)*) (.+)$")
S_MARCA = re.compile(r"⟦S:([^⟧]+)⟧")
REF_SEC = re.compile(rf"([Ss]eç(?:ão|ões)\s+)({LISTA_SEC})")


def _sem_marcas_s(xml):
    """Marcas de seção do gerador → número da seção no documento longo."""
    return S_MARCA.sub(lambda m: str(g.SECOES[m.group(1)]), xml)


def _reescrever(p, novo):
    """Parágrafo com o mesmo w:pPr e o formato de base do original, e outro texto."""
    assert not any(x in p for x in gr.FORA_DA_REESCRITA), g.texto(p)[:60]
    formatos = gr._formato_base(p)
    assert len(formatos) == 1, ("formatos mistos", g.texto(p)[:60])
    m = re.match(r"(<w:p(?: [^>]*)?>)(<w:pPr>.*?</w:pPr>)?", p, re.S)
    return m.group(1) + (m.group(2) or "") + g.runs(novo, formatos.pop()) + "</w:p>"


def _linhas(tabela, manter):
    linhas = re.findall(r"<w:tr[ >].*?</w:tr>", tabela, flags=re.S)
    ini = tabela.index(linhas[0])
    fim = tabela.rindex(linhas[-1]) + len(linhas[-1])
    assert all(1 <= k < len(linhas) for k in manter), (manter, len(linhas))
    return tabela[:ini] + linhas[0] + "".join(linhas[k] for k in manter) + tabela[fim:]


def aplicar_plano(plano, blocos, res, marc, escalas=None):
    """Lista de itens {origem, xml, indice, modo} e, para títulos, {chave, pai, titulo}."""
    itens, usados, ultimo = [], set(), -1

    def remarcar(xml):
        return g.PARAGRAFO.sub(lambda m: marc.paragrafo(m.group(0), legenda=True), xml)

    def mantido(i, modo="K", edicoes=None, texto_novo=None, linhas=None):
        nonlocal ultimo
        # a metodologia é fundida por tópico: os blocos podem vir fora da ordem do documento
        # longo, mas nenhum entra duas vezes
        assert i not in usados, f"bloco {i} repetido"
        usados.add(i)
        ultimo = i
        origem, marcado = blocos[i]
        xml = _sem_marcas_s(marcado)
        if edicoes:
            assert "⟦E#" not in marcado, f"bloco {i}: equação não é editada"
            xml = res[i]
            for antes, depois in edicoes:
                n = g.texto(xml).count(antes)
                assert n == 1, f"bloco {i}: trecho ocorre {n} vezes: {antes[:70]}"
                novo = g.editar(xml, [(re.escape(antes), lambda m, d=depois: d)])
                assert novo != xml, f"bloco {i}: troca sem efeito: {antes[:70]}"
                xml = novo
            xml = remarcar(xml)
        elif texto_novo is not None:
            assert res[i].startswith("<w:p"), f"bloco {i}: R só vale para parágrafo"
            xml = remarcar(_reescrever(res[i], texto_novo))
        elif linhas is not None:
            assert marcado.startswith("<w:tbl") and "⟦E#" not in marcado, f"bloco {i}: L só vale para tabela"
            xml = _linhas(xml, linhas)
        if escalas and i in escalas:
            assert "<w:drawing" in xml, f"bloco {i}: não é figura"
            xml = re.sub(r'(<(?:wp:extent|a:ext) cx=")(\d+)(" cy=")(\d+)(")',
                         lambda m: f"{m.group(1)}{int(int(m.group(2)) * escalas[i])}{m.group(3)}"
                                   f"{int(int(m.group(4)) * escalas[i])}{m.group(5)}", xml)
        item = {"origem": origem, "xml": xml, "indice": i, "modo": modo}
        t = g.texto(res[i])
        m = TITULO_NUM.match(t)
        if estilo(res[i]) == "Ttulo2" and m and not res[i].startswith("<w:tbl"):
            assert modo == "K", f"bloco {i}: título mantido não é editado"
            velho = m.group(1)
            item.update(chave=velho, pai=velho.rpartition(".")[0] or None, titulo=m.group(2))
        itens.append(item)

    for e in plano:
        op = e[0]
        if op == "K":
            for i in range(e[1], (e[2] if len(e) > 2 else e[1]) + 1):
                mantido(i)
        elif op == "E":
            mantido(e[1], "E", edicoes=e[2])
        elif op == "R":
            mantido(e[1], "R", texto_novo=e[2])
        elif op == "L":
            mantido(e[1], "L", linhas=e[2])
        elif op == "P":
            assert not any(c in e[1] for c in ("—", "–")), e[1][:60]
            itens.append({"origem": "n", "xml": g.P(marc.texto(e[1])), "indice": None, "modo": "P"})
        elif op == "H":
            _, pai, chave, titulo = e
            itens.append({"origem": "n", "xml": None, "indice": None, "modo": "H",
                          "chave": chave, "pai": pai, "titulo": titulo})
        else:
            raise ValueError(op)
    return itens


def numerar_secoes(itens, alias):
    """Dá número aos títulos e troca as remissões de seção; devolve o mapa chave → número."""
    numero, contador, erros, avisos = {}, {}, [], []
    for it in itens:
        if "chave" not in it:
            continue
        pai = it["pai"]
        assert it["chave"] not in numero, it["chave"]
        if pai is None:
            contador[None] = contador.get(None, 0) + 1
            n = str(contador[None])
        else:
            assert pai in numero, f"título {it['chave']}: seção-mãe {pai} ausente"
            contador[pai] = contador.get(pai, 0) + 1
            n = f"{numero[pai]}.{contador[pai]}"
        numero[it["chave"]] = n
        if it["modo"] == "H":
            it["xml"] = g.H(f"{n} {it['titulo']}")
        else:
            novo = g._editar_paragrafo(it["xml"], [(r"^\d+(?:\.\d+)*(?= )", lambda m, n=n: n)])
            it["xml"] = novo

    def destino(velho):
        if velho in numero:
            return numero[velho]
        if velho in alias and alias[velho] is not None:
            return numero[alias[velho]]
        return None

    atual = None
    for it in itens:
        if "chave" in it:
            atual = numero[it["chave"]]
            continue

        def troca(m, it=it):
            nums = re.findall(NUM_SEC, m.group(2))
            novos = [destino(v) for v in nums]
            if None in novos:
                erros.append((it["indice"], m.group(0), g.texto(it["xml"])[:90]))
                return m.group(0)
            if len(set(novos)) < len(novos):
                erros.append((it["indice"], "lista repetida: " + m.group(0), g.texto(it["xml"])[:90]))
                return m.group(0)
            if atual in novos:
                avisos.append((it["indice"], atual, m.group(0), g.texto(it["xml"])[:90]))
            k = iter(novos)
            return m.group(1) + re.sub(NUM_SEC, lambda _: next(k), m.group(2))
        xml = g.PARAGRAFO.sub(lambda p: g._editar_paragrafo(p.group(0), [(REF_SEC.pattern, troca)]), it["xml"])

        def marca(m, it=it):
            # a marca leva a chave de um título mantido ou de um título novo; a de uma seção
            # antiga que foi fundida em outra segue o ALIAS, como as remissões dos blocos mantidos
            n = destino(m.group(1))
            if n is None:
                erros.append((it["indice"], m.group(0), g.texto(it["xml"])[:90]))
                return m.group(0)
            if n == atual:
                avisos.append((it["indice"], atual, m.group(0), g.texto(it["xml"])[:90]))
            return n
        it["xml"] = S_MARCA.sub(marca, xml)
    if erros:
        raise SystemExit("remissões de seção sem destino:\n" + "\n".join(f"  {e}" for e in erros))
    return numero, avisos


def _chave_da_referencia(t, chaves):
    """Chave do .bib de uma entrada da lista de referências (sobrenome + ano)."""
    import gerar_latex as gl
    primeiro = gl.norm_nome(re.split(r",|\.", t)[0])
    cand = [k for k in chaves if k.startswith(primeiro) and re.fullmatch(r"\d{4}[a-z]?", k[len(primeiro):])]
    if primeiro == "suitx":
        return "suitx"
    if len(cand) > 1:
        anos = set(re.findall(r"\b(?:19|20)\d{2}[a-z]?\b", t))
        cand = [k for k in cand if k[len(primeiro):] in anos] or cand
        # dois trabalhos do mesmo primeiro autor e ano de publicação distinto do da chave
        cand = sorted(cand, key=lambda k: -t.count(k[len(primeiro):]))[:1] if len(cand) > 1 else cand
    assert len(cand) == 1, (t[:60], cand)
    return cand[0]


def filtrar_referencias(itens):
    """Tira da lista as referências que o texto condensado não cita."""
    import gerar_latex as gl
    bib = (RAIZ / "latex" / "bibliografia.bib").read_text(encoding="utf-8")
    chaves = set(re.findall(r"^@\w+\{([^,]+),", bib, flags=re.M))
    i_ref = next(k for k, it in enumerate(itens) if g.texto(it["xml"]) == "REFERÊNCIAS")
    cit = gl.Citacoes(bib)
    for it in itens[:i_ref]:
        for p in g.PARAGRAFO.findall(it["xml"]):
            gl.citacoes_no_texto(g.MARCA.sub("0", g.texto(p)), cit)
    assert not cit.ausentes, cit.ausentes
    mantidas, fora = [], []
    for it in itens[i_ref + 1:]:
        k = _chave_da_referencia(g.texto(it["xml"]), chaves)
        (mantidas if k in cit.usadas else fora).append((k, it))
    falta = cit.usadas - {k for k, _ in mantidas}
    assert not falta, f"citadas sem entrada na lista: {falta}"
    return itens[:i_ref + 1] + [it for _, it in mantidas], sorted(cit.usadas), [k for k, _ in fora]


def conferir_texto(itens, proibidos):
    """Restos de numeração literal, termos proibidos e travessões."""
    problemas = []
    i_ref = next(k for k, it in enumerate(itens) if g.texto(it["xml"]) == "REFERÊNCIAS")
    for it in itens[:i_ref]:
        for p in g.PARAGRAFO.findall(it["xml"]):
            t = g.texto(p)
            for m in re.finditer(r"\b(Tabelas?|Equaç(?:ão|ões)) \(?\d", t):
                problemas.append(("número literal", it["indice"], t[max(0, m.start() - 30):m.end() + 30]))
            for m in re.finditer(r"\b(Figuras?) (\d+)((?:, \d+)*(?: (?:e|a) \d+)?)(?=(.{0,14}))", t):
                if not _figura_de_patente(int(m.group(2)), m.group(4), m.group(3)):
                    problemas.append(("figura sem patente", it["indice"], t[max(0, m.start() - 30):m.end() + 30]))
            for termo in proibidos:
                if termo.lower() in t.lower():
                    problemas.append(("termo proibido: " + termo, it["indice"], t[:90]))
            sem_legenda = re.sub(r"^(Tabela|Figura) ⟦[TF]#[^⟧]+⟧ — ", "", t)
            for c in ("—", "–"):
                if c in sem_legenda:
                    k = sem_legenda.index(c)
                    problemas.append(("travessão", it["indice"], sem_legenda[max(0, k - 40):k + 40]))
    return problemas


def montar_condensado(verboso=True):
    import condensado_defesa as cd
    blocos, num, ctx = base_marcada()
    res = [x for _, x in ctx["resolvidos"]]
    marc = Marcador(num)
    itens = aplicar_plano(cd.PLANO, blocos, res, marc, getattr(cd, "ESCALA_FIGURAS", None))
    numero, avisos = numerar_secoes(itens, cd.ALIAS)
    itens, citadas, refs_fora = filtrar_referencias(itens)
    problemas = conferir_texto(itens, cd.PROIBIDOS)
    if problemas:
        raise SystemExit("problemas no texto condensado:\n" + "\n".join(f"  {p}" for p in problemas))
    cond = [(it["origem"], it["xml"]) for it in itens]
    final, num2, sem_ref = g.numerar(cond, 0)
    if verboso:
        for a in avisos:
            print("aviso: remissão à própria seção:", a)
        if sem_ref:
            print("sem referência no texto:", sem_ref)
    return {"itens": itens, "final": final, "num": num2, "num_longo": num, "secoes": numero,
            "citadas": citadas, "refs_fora": refs_fora, "sem_ref": sem_ref, "ctx": ctx, "avisos": avisos}


def gravar_fundido(m, destino=FUNDIDO_COND):
    """Empacota o corpo condensado no DOCX de origem (mesma cauda de main() do gerador)."""
    ctx = m["ctx"]
    partes, infos, doc, b0, b1 = (dict(ctx["partes"]), ctx["infos"], ctx["doc"], ctx["b0"], ctx["b1"])
    xml = "".join(x for _, x in m["final"])
    usadas = sorted({int(k) for k in re.findall(r"@@OMML(\d+)@@", xml)})
    todas = g.omml(g.EQUACOES)
    for k in usadas:
        xml = xml.replace(f"@@OMML{k}@@", todas[k - 1])
    assert "@@OMML" not in xml and "⟦" not in xml and "‹" not in xml
    xml = g.seno_sin(g.parenteses_fixos(xml))
    partes["word/document.xml"] = (doc[:b0] + xml + doc[b1:]).encode("utf-8")

    rels = partes["word/_rels/document.xml.rels"].decode("utf-8")
    novas = {}
    for k, (caminho, rid, pid) in enumerate(g.IMAGENS, start=1):
        if f'r:embed="{rid}"' not in xml:
            continue
        alvo = f"media/exo2_{k}.png"
        novas[f"word/{alvo}"] = caminho.read_bytes()
        rels = rels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
                            f'officeDocument/2006/relationships/image" Target="{alvo}"/></Relationships>')
    for rid, url in ((g.RID_DOI, g.DOI_VIRTANEN), (g.RID_SUITX, g.URL_SUITX),
                     (g.RID_ZEIAEE, g.DOI_ZEIAEE), (g.RID_OKABE, g.DOI_OKABE)):
        if f'r:id="{rid}"' in xml:
            rels = rels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
                                f'officeDocument/2006/relationships/hyperlink" Target="{url}" '
                                'TargetMode="External"/></Relationships>')
    # imagens do original que saíram com os blocos cortados
    inteiro = doc[:b0] + xml + doc[b1:]
    for r in re.findall(r"<Relationship [^>]*/>", rels):
        rid = re.search(r'Id="([^"]+)"', r).group(1)
        alvo = re.search(r'Target="([^"]+)"', r).group(1)
        if "/image" in r and f'"{rid}"' not in inteiro:
            rels = rels.replace(r, "")
            partes.pop("word/" + alvo, None)
    partes["word/_rels/document.xml.rels"] = rels.encode("utf-8")
    from PIL import Image
    import io
    for parte, caminho in g.SUBSTITUIDAS.items():
        if parte in partes:
            assert Image.open(io.BytesIO(partes[parte])).size == Image.open(caminho).size, parte
            partes[parte] = caminho.read_bytes()

    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w") as zout:
        for nome, dados in partes.items():
            zi = zipfile.ZipInfo(nome, date_time=infos[nome].date_time)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = infos[nome].external_attr
            zout.writestr(zi, dados)
        for nome, dados in novas.items():
            zout.writestr(zipfile.ZipInfo(nome, date_time=(1980, 1, 1, 0, 0, 0)), dados,
                          compress_type=zipfile.ZIP_DEFLATED)
    tmp.replace(destino)
    registro = [{"modo": it["modo"], "indice": it["indice"], "texto": gr.marcado(x) if x.startswith("<w:p") else
                 "[tabela] " + g.texto(x)[:200]} for it, (_, x) in zip(m["itens"], m["final"])]
    (destino.parent / "registro_condensado.json").write_text(
        json.dumps({"secoes": m["secoes"], "citadas": m["citadas"], "referencias_retiradas": m["refs_fora"],
                    "tabelas": m["num"]["T"], "figuras": m["num"]["F"], "equacoes": m["num"]["E"],
                    "numeracao_longa": {t: m["num_longo"][t] for t in "TFE"}, "blocos": registro},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{destino.relative_to(RAIZ)}: {len(m['itens'])} blocos, {len(m['num']['T'])} tabelas, "
          f"{len(m['num']['F'])} figuras, {len(m['num']['E'])} equações, {len(m['secoes'])} títulos, "
          f"{len(m['citadas'])} referências ({len(m['refs_fora'])} retiradas)")


# ======================================================================
# LaTeX, PDF e DOCX no formato FT
# ======================================================================

def _preparar_latex(m):
    import condensado_defesa as cd
    import revisao_defesa as rd
    base, dest = RAIZ / "latex", BUILD / "latex"
    dest.mkdir(parents=True, exist_ok=True)
    for nome in ("preambulo.tex", "tese-FT.cls", "agradecimentos.tex"):
        shutil.copyfile(base / nome, dest / nome)
    shutil.copytree(base / "logotipos", dest / "logotipos", dirs_exist_ok=True)
    # sem apêndice
    tese = (base / "tese.tex").read_text(encoding="utf-8")
    ap = re.compile(r"% Apêndices, gerados por [^\n]*\n\\appendix\n\\include\{capitulos/apendices\}\n")
    assert len(ap.findall(tese)) == 1
    tese = ap.sub("", tese)
    velho = "\\titulo{" + cd.TITULO_LONGO + "}"
    assert tese.count(velho) == 1, "título não encontrado em tese.tex"
    tese = tese.replace(velho, "\\titulo{" + cd.TITULO + "}")
    data = getattr(cd, "DATA_DEFESA", None)
    if data:
        velho = "\\datadadefesa{XX}{11}{2026}"
        assert tese.count(velho) == 1, "data da defesa não encontrada em tese.tex"
        tese = tese.replace(velho, "\\datadadefesa{%s}{%s}{%s}" % data)
    (dest / "tese.tex").write_text(tese, encoding="utf-8")
    velho = dest / "capitulos" / "apendices.tex"
    if velho.exists():
        velho.unlink()
    # só as referências citadas (tese.tex lista todas as entradas do .bib)
    bib = (base / "bibliografia.bib").read_text(encoding="utf-8")
    pedacos = re.split(r"(?m)^(?=@)", bib)
    saida = [pedacos[0]]
    for e in pedacos[1:]:
        k = re.match(r"@\w+\{([^,]+),", e).group(1)
        if k in m["citadas"]:
            saida.append(e)
    assert len(saida) - 1 == len(m["citadas"]), (len(saida) - 1, len(m["citadas"]))
    (dest / "bibliografia.bib").write_text("".join(saida), encoding="utf-8")
    # resumo e abstract da versão revisada, sem a frase das etapas dinâmicas
    s = (base / "resumo.tex").read_text(encoding="utf-8")
    for ambiente, texto_rev in (("resumo", rd.RESUMO), ("abstract", rd.ABSTRACT)):
        novo = texto_rev
        for frase in cd.FRASES_FORA_DO_RESUMO:
            novo = novo.replace(frase, "")
        assert novo != texto_rev and not any(t.lower() in novo.lower() for t in ("MBDyn", "Lagrange")), ambiente
        padrao = re.compile(r"(\\begin\{%s\}\n).*?(\n\\end\{%s\})" % (ambiente, ambiente), re.S)
        assert len(padrao.findall(s)) == 1
        s = padrao.sub(lambda mm: mm.group(1) + novo.strip() + mm.group(2), s)
    (dest / "resumo.tex").write_text(s, encoding="utf-8")
    return dest


def gerar_pdf(m):
    dest = _preparar_latex(m)
    py = sys.executable
    gr.rodar([py, RAIZ / "tcc" / "gerar_latex.py", FUNDIDO_COND, dest])
    gr.rodar(["latexmk", "-C", f"-jobname={NOME}", "tese.tex"], cwd=dest,
             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(BUILD / "latexmk.log", "w", encoding="utf-8") as log:
        gr.rodar(["latexmk", "-pdf", "-silent", f"-jobname={NOME}", "tese.tex"], cwd=dest,
                 stdout=log, stderr=subprocess.STDOUT)
    return dest / f"{NOME}.pdf"


def paginas_por_capitulo(pdf):
    """Página (do PDF) em que começa cada parte, pelo sumário do próprio PDF."""
    saida = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    pags = saida.split("\f")
    marcos = {}
    for i, t in enumerate(pags, start=1):
        topo = "\n".join(t.strip().splitlines()[:4])
        for rotulo, padrao in (("resumo", r"^\s*Resumo\s*$"), ("lista de figuras", r"^\s*Lista de Figuras\s*$"),
                               ("sumário", r"^\s*Sumário\s*$"), ("cap. 1", r"Capítulo 1\b"),
                               ("cap. 2", r"Capítulo 2\b"), ("cap. 3", r"Capítulo 3\b"),
                               ("cap. 4", r"Capítulo 4\b"), ("cap. 5", r"Capítulo 5\b"),
                               ("referências", r"^\s*Referências\s*$")):
            if rotulo not in marcos and re.search(padrao, topo, flags=re.M):
                marcos[rotulo] = i
    return len(pags) - 1, marcos


def gerar_tudo(m):
    pdf = gerar_pdf(m)
    py = sys.executable
    amb = dict(os.environ, TCC_RELATORIOS=str(BUILD), TCC_LATEX=str(BUILD / "latex"),
               TCC_FUNDIDO=str(FUNDIDO_COND))
    gr.rodar([py, RAIZ / "tcc" / "verificar_latex.py", FUNDIDO_COND, pdf], env=amb)
    gr.rodar([py, RAIZ / "tcc" / "gerar_docx_modelo.py", DOCX_FT], env=amb)
    gr.rodar([py, RAIZ / "tcc" / "verificar_docx_modelo.py", DOCX_FT, pdf, FUNDIDO_COND], env=amb)
    shutil.copyfile(pdf, SAIDA / f"{NOME}.pdf")
    print(f"pronto: {DOCX_FT.relative_to(RAIZ)} e {(SAIDA / (NOME + '.pdf')).relative_to(RAIZ)}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--dump" in args:
        dump(args[args.index("--dump") + 1])
    else:
        m = montar_condensado()
        gravar_fundido(m)
        if "--pdf" in args:
            pdf = gerar_pdf(m)
            total, marcos = paginas_por_capitulo(pdf)
            print(f"PDF: {total} páginas; início de cada parte: {marcos}")
        if "--tudo" in args:
            gerar_tudo(m)
