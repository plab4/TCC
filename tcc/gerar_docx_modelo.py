"""Gera o TCC em DOCX com a formatação do PDF do LaTeX (modelo FT/UNICAMP).

Uso: python3 tcc/gerar_docx_modelo.py [saida.docx]

O conteúdo vem do TCC fundido (tcc/TCC_exo1_exo2.docx); os dados da capa,
da folha de rosto e da banca vêm de latex/tese.tex, o resumo de
latex/resumo.tex e as referências de latex/bibliografia.bib. As citações
são impressas exatamente como o biblatex as imprime: o script compila um
documento auxiliar com cada citação e lê o resultado.

Formatação reproduzida do PDF do LaTeX: A4 com margens de 3 e 2 cm, fonte
Linux Libertine O 12 pt (embutida no arquivo), entrelinha de 21,7 pt,
recuo de 18 pt, títulos "Capítulo N" centralizados, cabeçalho corrente com
o capítulo em versalete e o número da página, tabelas com filetes no
estilo booktabs, legendas acima, fonte e nota em 10 pt, referências em
espaço simples. Sumário e listas são campos do Word, preenchidos com as
páginas de uma renderização pelo LibreOffice e atualizados pelo Word ao
abrir o arquivo.
"""
import html
import io
import re
import subprocess
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_latex as gl  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
LATEX = RAIZ / "latex"
FONTE_OTF = Path("/usr/share/fonts/opentype/linux-libertine")

# espaçadores no topo da página (pt): título de capítulo e título pré-textual
ESPACO_CAPITULO = 47.8
ESPACO_PRE = 46.2

# página e medidas, em twips (1 pt = 20 twips)
LARG_TEXTO = 9071          # 160 mm
FONTE = "Linux Libertine O"
FONTE_MONO = "Linux Libertine Mono O"
EMU_TEXTO = 5760000        # 160 mm em EMU

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"')
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def x(t):
    return html.escape(t, quote=False)


# ======================================================================
# blocos de WordprocessingML
# ======================================================================

def rpr(b=False, i=False, sz=None, va=None, caps=False, font=None):
    s = ""
    if font:
        s += f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}"/>'
    if b:
        s += "<w:b/><w:bCs/>"
    if i:
        s += "<w:i/><w:iCs/>"
    if caps:
        s += "<w:smallCaps/>"
    if sz:
        s += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    if va:
        s += f'<w:vertAlign w:val="{ {"sub": "subscript", "sup": "superscript"}[va] }"/>'
    return f"<w:rPr>{s}</w:rPr>" if s else ""


def run(t, **k):
    partes = t.split("\t")
    saida = []
    for j, p in enumerate(partes):
        if j:
            saida.append(f"<w:r>{rpr(**k)}<w:tab/></w:r>")
        if p:
            saida.append(f'<w:r>{rpr(**k)}<w:t xml:space="preserve">{x(p)}</w:t></w:r>')
    return "".join(saida)


def quebra(**k):
    return f"<w:r>{rpr(**k)}<w:br/></w:r>"


def campo(instr, resultado="", **k):
    return (f'<w:r>{rpr(**k)}<w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r>{rpr(**k)}<w:instrText xml:space="preserve"> {x(instr)} </w:instrText></w:r>'
            f'<w:r>{rpr(**k)}<w:fldChar w:fldCharType="separate"/></w:r>'
            + run(resultado, **k) +
            f'<w:r>{rpr(**k)}<w:fldChar w:fldCharType="end"/></w:r>')


def ppr(estilo=None, jc=None, antes=None, depois=None, linha=None, regra="exact",
        recuo=None, esq=None, pendente=None, keep=False, keep_lines=False,
        tabs=None, borda_inf=None, sect=None, nova_pagina=False):
    s = ""
    if estilo:
        s += f'<w:pStyle w:val="{estilo}"/>'
    if keep:
        s += "<w:keepNext/>"
    if keep_lines:
        s += "<w:keepLines/>"
    if nova_pagina:
        s += "<w:pageBreakBefore/>"
    if borda_inf:
        s += f'<w:pBdr><w:bottom w:val="single" w:sz="{borda_inf}" w:space="2" w:color="000000"/></w:pBdr>'
    if tabs:
        s += "<w:tabs>" + "".join(
            f'<w:tab w:val="{v}"' + (f' w:leader="{ld}"' if ld else "") + f' w:pos="{p}"/>'
            for v, p, ld in tabs) + "</w:tabs>"
    if antes is not None or depois is not None or linha is not None:
        s += "<w:spacing" + (f' w:before="{round(antes)}"' if antes is not None else "") + \
             (f' w:after="{round(depois)}"' if depois is not None else "") + \
             (f' w:line="{round(linha)}" w:lineRule="{regra}"' if linha is not None else "") + "/>"
    if recuo is not None or esq is not None or pendente is not None:
        s += "<w:ind" + (f' w:left="{esq}"' if esq is not None else "") + \
             (f' w:hanging="{pendente}"' if pendente is not None else "") + \
             (f' w:firstLine="{recuo}"' if recuo is not None else "") + "/>"
    if jc:
        s += f'<w:jc w:val="{jc}"/>'
    if sect:
        s += sect
    return f"<w:pPr>{s}</w:pPr>" if s else ""


def par(conteudo, **k):
    return f"<w:p>{ppr(**k)}{conteudo}</w:p>"


def campo_tc(texto):
    """Entrada de sumário (TC): só código, sem resultado."""
    return ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> TC "{x(texto)}" \\l 1 </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r>')


def espacador(pontos, nova_pagina=False):
    """Parágrafo vazio de altura fixa. O espaço antes do primeiro parágrafo
    de uma página é ignorado pelo LibreOffice e, em alguns casos, pelo Word;
    a altura de linha, não."""
    return par(run(" ", sz=2), linha=round(pontos * 20), regra="exact", recuo=0,
               nova_pagina=nova_pagina, keep=True)


def marcador(nome, n, conteudo):
    return (f'<w:bookmarkStart w:id="{n}" w:name="{nome}"/>{conteudo}'
            f'<w:bookmarkEnd w:id="{n}"/>')


# ======================================================================
# dados do tese.tex, resumo.tex e bibliografia.bib
# ======================================================================

def sem_comentarios(t):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in t.split("\n"))


def dados_tese():
    t = sem_comentarios((LATEX / "tese.tex").read_text(encoding="utf-8"))

    def um(cmd, n=1):
        m = re.search(r"\\" + cmd + r"\{([^}]*)\}" * n, t)
        return (m.groups() if n > 1 else m.group(1)) if m else None
    d = {
        "instituicao": um("instituicao", 2), "unidade": um("unidadeEnsino", 2),
        "cidade": um("cidade"), "programa": um("programaPosGraduacao"),
        "autor": um("autor"), "titulo": um("titulo"), "orientador": um("orientador"),
        "curso": um("tccGraduacao"), "data": um("datadadefesa", 3),
        "final": not re.search(r"^\s*\\finalversionfalse", t, flags=re.M),
        # \folhadeaprovacaoantecipada (preambulo.tex): banca já na versão
        # entregue antes da defesa
        "aprovacao_antecipada": bool(re.search(r"^\s*\\folhadeaprovacaoantecipada", t,
                                               flags=re.M)),
        "banca": [um(f"avaliador{c}", 2) for c in "ABCDEFGH"],
    }
    d["banca"] = [b for b in d["banca"] if b]
    r = sem_comentarios((LATEX / "resumo.tex").read_text(encoding="utf-8"))
    d["resumo"] = re.search(r"\\begin\{resumo\}(.*?)\\end\{resumo\}", r, flags=re.S).group(1).strip()
    d["abstract"] = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", r, flags=re.S).group(1).strip()
    a = sem_comentarios((LATEX / "agradecimentos.tex").read_text(encoding="utf-8"))
    m = re.search(r"\\prefacesection\{Agradecimentos\}(.*?)(?:\\epigrafe|\Z)", a, flags=re.S)
    d["agradecimentos"] = m.group(1).strip() if m else None
    return d


def entradas_bib():
    """[(chave, tipo, campos)] na ordem do arquivo."""
    bib = (LATEX / "bibliografia.bib").read_text(encoding="utf-8")
    saida = []
    for m in re.finditer(r"^@(\w+)\{([^,]+),\n(.*?)\n\}", bib, flags=re.M | re.S):
        campos = dict(re.findall(r"^\s*(\w+)\s*=\s*\{(.*)\},?\s*$", m.group(3), flags=re.M))
        saida.append((m.group(2), m.group(1), campos))
    return saida


def nomes(campo):
    """'Spada, S. and others' -> ([('Spada', 'S.')], True); {{Org}} -> [('Org', None)]."""
    partes = [p.strip() for p in campo.split(" and ")]
    outros = partes[-1] == "others"
    partes = [p for p in partes if p != "others"]
    lista = []
    for p in partes:
        if p.startswith("{"):
            lista.append((p.strip("{}").replace("\\&", "&"), None))
        else:
            fam, giv = [y.strip() for y in p.split(",", 1)]
            lista.append((fam, giv))
    return lista, outros


def alta(fam):
    return "Mc" + fam[2:].upper() if fam.startswith("Mc") else fam.upper()


def nomes_ref(campo, inicio_de_frase=True):
    """Forma da lista de referências (mista) e a do DOCX (caixa alta)."""
    lista, outros = nomes(campo)
    mista, maiusc = [], []
    for j, (fam, giv) in enumerate(lista):
        if giv is None:
            mista.append(fam)
            maiusc.append(fam.upper())
            continue
        f = fam[0].upper() + fam[1:] if (j == 0 and inicio_de_frase) else fam
        mista.append(f"{f}, {giv}")
        maiusc.append(f"{alta(fam)}, {giv}")
    fim = " et al." if outros else ""
    return "; ".join(mista) + fim, "; ".join(maiusc) + fim


# ======================================================================
# citações renderizadas pelo biblatex
# ======================================================================

def renderizar_citacoes(comandos):
    """{comando LaTeX: texto impresso}, compilando um documento auxiliar com
    a mesma classe, preâmbulo e bibliografia do TCC."""
    comandos = sorted(set(comandos))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for f in ["tese-FT.cls", "preambulo.tex", "bibliografia.bib"]:
            (tmp / f).write_bytes((LATEX / f).read_bytes())
        corpo = "\n".join(f"\\noindent\\mbox{{\\tiny QQ{i}Q {c} QQFIM}}\\par"
                          for i, c in enumerate(comandos))
        (tmp / "cit.tex").write_text(
            "\\documentclass[Portugues,Final]{tese-FT}\n\\addbibresource{bibliografia.bib}\n"
            "\\input{preambulo}\n\\begin{document}\n" + corpo + "\n\\end{document}\n",
            encoding="utf-8")
        for cmd in (["pdflatex", "-interaction=nonstopmode", "cit.tex"], ["biber", "cit"],
                    ["pdflatex", "-interaction=nonstopmode", "cit.tex"]):
            subprocess.run(cmd, cwd=tmp, capture_output=True)
        txt = subprocess.run(["pdftotext", "-raw", str(tmp / "cit.pdf"), "-"],
                             capture_output=True, text=True, check=True).stdout
    txt = re.sub(r"\s+", " ", txt)
    saida = {}
    for i, c in enumerate(comandos):
        m = re.search(rf"QQ{i}Q (.*?) QQFIM", txt)
        assert m, c
        saida[c] = m.group(1).strip()
    return saida


class Textos:
    """Converte (texto, formato) do DOCX fundido em runs, com as citações
    impressas como no LaTeX."""

    def __init__(self, cit):
        self.cit = cit
        self.render = {}

    def citacoes(self, plano):
        saida = []
        for a, b, lx in gl.citacoes_no_texto(plano, self.cit):
            if lx.startswith("\\"):
                saida.append((a, b, lx))
            else:  # obra ausente da lista: texto entre parênteses
                saida.append((a, b, "TXT:" + lx.replace("\\&", "&")))
        return sorted(saida)

    def coletar(self, segs, cortar=0):
        plano = "".join(t for t, _ in segs)[cortar:]
        return [lx for _, _, lx in self.citacoes(plano) if not lx.startswith("TXT:")]

    def runs(self, segs, cortar=0, sz=None, negrito=False):
        chars = [(c, f) for t, f in segs for c in t][cortar:]
        plano = "".join(c for c, _ in chars)
        subs = self.citacoes(plano)
        saida, i, k = [], 0, 0
        while i < len(chars):
            assert k >= len(subs) or subs[k][0] >= i, plano
            if k < len(subs) and i == subs[k][0]:
                a, b, lx = subs[k]
                texto = lx[4:] if lx.startswith("TXT:") else self.render[lx]
                saida.append(run(texto, sz=sz, b=negrito))
                i, k = b, k + 1
                continue
            fim = subs[k][0] if k < len(subs) else len(chars)
            j = i
            while j < fim and chars[j][1] == chars[i][1]:
                j += 1
            ital, va, _ = chars[i][1]
            saida.append(run("".join(c for c, _ in chars[i:j]), i=ital, va=va, sz=sz, b=negrito))
            i = j
        return "".join(saida)


# ======================================================================
# fontes embutidas
# ======================================================================

FAIXAS = [(0x20, 0x7E), (0xA0, 0x24F), (0x370, 0x3FF), (0x1E00, 0x1EFF), (0x2000, 0x206F),
          (0x2070, 0x209F), (0x20A0, 0x20CF), (0x2100, 0x214F), (0x2190, 0x21FF),
          (0x2200, 0x22FF), (0xFB00, 0xFB06)]


def otf_para_ttf(caminho):
    """CFF -> glyf (cu2qu) e subconjunto Latim, Grego e símbolos; o Word só
    embute fontes TrueType."""
    from fontTools.ttLib import TTFont, newTable
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools import subset

    f = TTFont(str(caminho))
    ordem = f.getGlyphOrder()
    gs = f.getGlyphSet()
    glifos = {}
    for nome in ordem:
        pen = TTGlyphPen(gs)
        gs[nome].draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
        glifos[nome] = pen.glyph()
    f["loca"] = newTable("loca")
    f["glyf"] = glyf = newTable("glyf")
    glyf.glyphOrder = ordem
    glyf.glyphs = glifos
    del f["CFF "]
    if "VORG" in f:
        del f["VORG"]
    glyf.compile(f)
    for nome in ordem:
        g = glyf[nome]
        if hasattr(g, "xMin"):
            larg, _ = f["hmtx"][nome]
            f["hmtx"][nome] = (larg, g.xMin)
    f["maxp"] = maxp = newTable("maxp")
    maxp.tableVersion = 0x00010000
    for campo_ in ("maxZones", ):
        setattr(maxp, campo_, 1)
    for campo_ in ("maxTwilightPoints", "maxStorage", "maxFunctionDefs", "maxInstructionDefs",
                   "maxStackElements", "maxSizeOfInstructions", "maxComponentElements"):
        setattr(maxp, campo_, 0)
    maxp.compile(f)
    post = f["post"]
    post.formatType = 2.0
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = ordem
    f["head"].glyphDataFormat = 0
    f.sfntVersion = "\x00\x01\x00\x00"
    buf = io.BytesIO()
    f.save(buf)
    f = TTFont(io.BytesIO(buf.getvalue()))
    op = subset.Options()
    op.layout_features = ["*"]
    op.name_IDs = ["*"]
    op.name_languages = ["*"]
    op.notdef_outline = True
    op.hinting = False
    op.glyph_names = False
    sub = subset.Subsetter(op)
    sub.populate(unicodes=[u for a, b in FAIXAS for u in range(a, b + 1)])
    sub.subset(f)
    buf = io.BytesIO()
    f.save(buf)
    return buf.getvalue()


def ofuscar(dados, chave):
    k = bytes.fromhex(chave.strip("{}").replace("-", ""))[::-1]
    d = bytearray(dados)
    for i in range(32):
        d[i] ^= k[i % 16]
    return bytes(d)


def fontes_embutidas():
    """[(nome da família, {variante: (nome do arquivo, chave, bytes)})]"""
    familias = [
        (FONTE, {"Regular": "LinLibertine_R.otf", "Bold": "LinLibertine_RB.otf",
                 "Italic": "LinLibertine_RI.otf", "BoldItalic": "LinLibertine_RBI.otf"}),
        (FONTE_MONO, {"Regular": "LinLibertine_M.otf"}),
    ]
    saida = []
    n = 0
    for fam, var in familias:
        d = {}
        for v, arq in var.items():
            n += 1
            chave = "{" + str(uuid.uuid5(uuid.NAMESPACE_URL, "tcc-fonte-" + arq)).upper() + "}"
            d[v] = (f"font{n}.odttf", chave, ofuscar(otf_para_ttf(FONTE_OTF / arq), chave))
        saida.append((fam, d))
    return saida


# ======================================================================
# estilos
# ======================================================================

def estilos():
    def est(sid, nome, base="Normal", ppr_="", rpr_="", tipo="paragraph", prox=None, extra=""):
        return (f'<w:style w:type="{tipo}" w:styleId="{sid}"><w:name w:val="{nome}"/>'
                + (f'<w:basedOn w:val="{base}"/>' if base else "")
                + (f'<w:next w:val="{prox}"/>' if prox else "") + extra
                + (f"<w:pPr>{ppr_}</w:pPr>" if ppr_ else "")
                + (f"<w:rPr>{rpr_}</w:rPr>" if rpr_ else "") + "</w:style>")

    def sp(a=0, d=0, ln=None, regra="exact"):
        return f'<w:spacing w:before="{a}" w:after="{d}"' + \
            (f' w:line="{ln}" w:lineRule="{regra}"' if ln else "") + "/>"
    sem_recuo = '<w:ind w:firstLine="0"/>'
    lista = [
        est("Normal", "Normal", base=None, extra="<w:qFormat/>",
            ppr_='<w:widowControl/>' + sp(0, 0, 434) + '<w:ind w:firstLine="360"/><w:jc w:val="both"/>'),
        est("SemRecuo", "Primeiro parágrafo", prox="Normal", ppr_=sem_recuo),
        est("Ttulo1", "heading 1", prox="SemRecuo", extra="<w:qFormat/>",
            ppr_="<w:keepNext/><w:keepLines/>" + sp(0, 488, 996) + sem_recuo +
            '<w:jc w:val="center"/><w:outlineLvl w:val="0"/>', rpr_='<w:b/><w:bCs/><w:sz w:val="50"/><w:szCs w:val="50"/>'),
        est("Ttulo2", "heading 2", prox="SemRecuo", extra="<w:qFormat/>",
            ppr_='<w:keepNext/><w:keepLines/><w:tabs><w:tab w:val="left" w:pos="1000"/></w:tabs>'
                 + sp(538, 94, 620) + '<w:ind w:left="1000" w:hanging="1000"/><w:jc w:val="left"/>'
                 '<w:outlineLvl w:val="1"/>',
            rpr_='<w:b/><w:bCs/><w:sz w:val="35"/><w:szCs w:val="35"/>'),
        est("Ttulo3", "heading 3", prox="SemRecuo", extra="<w:qFormat/>",
            ppr_='<w:keepNext/><w:keepLines/><w:tabs><w:tab w:val="left" w:pos="1100"/></w:tabs>'
                 + sp(460, 44, 520) + '<w:ind w:left="1100" w:hanging="1100"/><w:jc w:val="left"/>'
                 '<w:outlineLvl w:val="2"/>',
            rpr_='<w:b/><w:bCs/><w:sz w:val="29"/><w:szCs w:val="29"/>'),
        est("Legenda", "caption", prox="Normal", extra="<w:qFormat/>",
            ppr_="<w:keepNext/>" + sp(240, 120, 290) + sem_recuo + '<w:jc w:val="center"/>'),
        est("FonteNota", "Fonte e nota", ppr_=sp(40, 0, 240) + sem_recuo + '<w:jc w:val="both"/>',
            rpr_='<w:sz w:val="20"/><w:szCs w:val="20"/>'),
        est("TabelaTexto", "Texto de tabela", ppr_=sp(0, 0, 272) + sem_recuo + '<w:jc w:val="left"/>',
            rpr_='<w:sz w:val="22"/><w:szCs w:val="22"/>'),
        est("TabelaTextoMenor", "Texto de tabela menor", base="TabelaTexto", ppr_=sp(0, 0, 240),
            rpr_='<w:sz w:val="20"/><w:szCs w:val="20"/>'),
        est("Equacao", "Equação", ppr_=sp(0, 0, 240, "auto") + sem_recuo + '<w:jc w:val="center"/>'),
        est("Figura", "Figura", ppr_="<w:keepNext/>" + sp(0, 60, 240, "auto") + sem_recuo + '<w:jc w:val="center"/>'),
        est("ItemLista", "Item de lista",
            ppr_='<w:tabs><w:tab w:val="left" w:pos="586"/></w:tabs>' + sp(178, 0, 434)
                 + '<w:ind w:left="586" w:hanging="300"/>'),
        est("TituloPreTextual", "Título pré-textual", prox="PreTexto",
            ppr_="<w:keepNext/>" + sp(0, 624, 600) + sem_recuo + '<w:jc w:val="center"/>',
            rpr_='<w:b/><w:bCs/><w:sz w:val="50"/><w:szCs w:val="50"/>'),
        est("PreTexto", "Texto pré-textual", ppr_=sp(0, 0, 290) + sem_recuo + '<w:jc w:val="left"/>'),
        est("Referencia", "Referência", ppr_=sp(0, 150, 290) + sem_recuo + '<w:jc w:val="both"/>'),
        est("Sumrio1", "toc 1", base="PreTexto",
            ppr_='<w:tabs><w:tab w:val="left" w:pos="360"/><w:tab w:val="right" w:pos="9071"/></w:tabs>'
                 + sp(324, 0, 288), rpr_="<w:b/><w:bCs/>"),
        est("Sumrio2", "toc 2", base="PreTexto",
            ppr_='<w:tabs><w:tab w:val="left" w:pos="912"/><w:tab w:val="right" w:leader="dot" w:pos="9071"/></w:tabs>'
                 + sp(0, 0, 288) + '<w:ind w:left="912" w:right="567" w:hanging="552"/>'),
        est("Sumrio3", "toc 3", base="PreTexto",
            ppr_='<w:tabs><w:tab w:val="left" w:pos="1679"/><w:tab w:val="right" w:leader="dot" w:pos="9071"/></w:tabs>'
                 + sp(0, 0, 288) + '<w:ind w:left="1679" w:right="567" w:hanging="768"/>'),
        est("ndicedeilustraes", "table of figures", base="PreTexto",
            ppr_='<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9071"/></w:tabs>'
                 + sp(0, 0, 288) + '<w:ind w:left="910" w:right="567" w:hanging="550"/>'),
        est("Cabealho", "header", ppr_='<w:tabs><w:tab w:val="right" w:pos="9071"/></w:tabs>'
            + sp(0, 0, 240, "auto") + sem_recuo + '<w:jc w:val="left"/>'),
        est("Fontepargpadro", "Default Paragraph Font", base=None, tipo="character",
            extra="<w:uiPriority w:val=\"1\"/><w:semiHidden/>"),
        est("TabelaNormal", "Normal Table", base=None, tipo="table",
            extra='<w:uiPriority w:val="99"/><w:semiHidden/><w:tblPr><w:tblInd w:w="0" w:type="dxa"/>'
                  '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/>'
                  '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar></w:tblPr>'),
    ]
    padrao = ('<w:docDefaults><w:rPrDefault><w:rPr>'
              f'<w:rFonts w:ascii="{FONTE}" w:eastAsia="{FONTE}" w:hAnsi="{FONTE}" w:cs="{FONTE}"/>'
              '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="pt-BR" w:eastAsia="en-US" w:bidi="ar-SA"/>'
              '</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="0" w:line="240" '
              'w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>')
    # o estilo de parágrafo padrão e as tabelas sem estilo
    lista[0] = lista[0].replace('w:styleId="Normal">', 'w:default="1" w:styleId="Normal">')
    lista[-2] = lista[-2].replace('w:styleId="Fontepargpadro">', 'w:default="1" w:styleId="Fontepargpadro">')
    lista[-1] = lista[-1].replace('w:styleId="TabelaNormal">', 'w:default="1" w:styleId="TabelaNormal">')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<w:styles {NS}>' + padrao + "".join(lista) + "</w:styles>")


# ======================================================================
# documento
# ======================================================================

class Documento:
    def __init__(self):
        self.corpo = []
        self.rels = {}          # rId -> (tipo, alvo, externo)
        self.media = {}         # caminho no pacote -> bytes
        self.cabecalhos = {}    # nome da parte -> xml
        self.n_marca = 0
        self.n_img = 0
        self.sumario = []       # (nível, número, título, marcador)
        self.legendas = {"Figura": [], "Tabela": []}   # (texto, marcador)

    def rel(self, tipo, alvo, externo=False):
        rid = f"rId{len(self.rels) + 10}"
        self.rels[rid] = (tipo, alvo, externo)
        return rid

    def marca(self):
        self.n_marca += 1
        return f"_Toc{self.n_marca:04d}", self.n_marca

    def imagem(self, dados, ext, cx, cy, descr):
        self.n_img += 1
        nome = f"media/imagem{self.n_img}.{ext}"
        self.media["word/" + nome] = dados
        rid = self.rel("image", nome)
        n = self.n_img
        return (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
                f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
                f'<wp:docPr id="{n}" name="Imagem {n}" descr="{html.escape(descr)}"/>'
                '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/'
                'drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
                '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                f'<pic:nvPicPr><pic:cNvPr id="{n}" name="Imagem {n}"/><pic:cNvPicPr/></pic:nvPicPr>'
                f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
                f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
                '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData>'
                "</a:graphic></wp:inline></w:drawing></w:r>")

    def cabecalho(self, texto_esq, borda):
        nome = f"header{len(self.cabecalhos) + 1}.xml"
        conteudo = (run(texto_esq, caps=True) if texto_esq else "") + run("\t") + campo("PAGE", "1")
        self.cabecalhos[nome] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<w:hdr {NS}>' + par(conteudo, estilo="Cabealho", borda_inf=8 if borda else None) + "</w:hdr>")
        return self.rel("header", nome)

    def vazio(self):
        nome = f"header{len(self.cabecalhos) + 1}.xml"
        self.cabecalhos[nome] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                                 f'<w:hdr {NS}>' + par("", estilo="Cabealho") + "</w:hdr>")
        return self.rel("header", nome)


def sect(cab_padrao=None, cab_primeira=None, ultima=False):
    refs = ""
    if cab_padrao:
        refs += f'<w:headerReference w:type="default" r:id="{cab_padrao}"/>'
    if cab_primeira:
        refs += f'<w:headerReference w:type="first" r:id="{cab_primeira}"/>'
    return (f"<w:sectPr>{refs}<w:type w:val=\"nextPage\"/>"
            '<w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1583" w:right="1134" w:bottom="1134" w:left="1701" w:header="892" '
            'w:footer="567" w:gutter="0"/><w:cols w:space="708"/>'
            + ("<w:titlePg/>" if cab_primeira else "") + "</w:sectPr>")


# ----------------------------------------------------------------------
# pré-textuais
# ----------------------------------------------------------------------

def pre_textuais(doc, d, logo):
    """Capa, folha de rosto, folha de aprovação, resumo, abstract, listas e
    sumário, como em \\paginasiniciais do tese-FT.cls."""
    c = doc.corpo
    inst, sigla = d["instituicao"]
    unid, usig = d["unidade"]
    # capa
    from PIL import Image
    w, h = Image.open(io.BytesIO(logo)).size
    cx = 828000           # 0,92 x 2,5 cm
    cy = round(cx * h / w)
    c.append(par(doc.imagem(logo, "png", cx, cy, "Logotipo"), linha=900, regra="exact",
                 recuo=0, jc="left"))
    c.append(par(run(f"{inst.upper()} ({sigla})", sz=29) + quebra(sz=29) +
                 run(f"{unid.upper()} ({usig})", sz=29),
                 antes=1484, linha=388, jc="center", recuo=0))
    c.append(par(run(d["autor"], sz=29), antes=2005, linha=346, jc="center", recuo=0))
    c.append(par(run(d["titulo"], sz=29), antes=1430, linha=346, jc="center", recuo=0))
    c.append(par(run(d["cidade"], sz=29) + quebra(sz=29) + run(d["data"][2], sz=29),
                 antes=5850, linha=360, jc="center", recuo=0))
    # folha de rosto
    c.append(par(run(d["autor"], sz=29), linha=346, jc="center", recuo=0, antes=0, nova_pagina=True))
    c.append(par(run(d["titulo"], sz=29), antes=2200, linha=346, jc="center", recuo=0))
    texto_rosto = (f"Monografia apresentada à {unid} da {inst} ({sigla}) como parte dos "
                   f"requisitos para a obtenção do título de Bacharel em {d['curso']}.")
    c.append(par(run(texto_rosto), antes=2420, linha=290, esq=4174, recuo=0, jc="both"))
    c.append(par(run(f"Orientador: {d['orientador']}"), antes=2160, linha=290, recuo=0, jc="left"))
    aviso = ("ESTE TRABALHO CORRESPONDE À VERSÃO FINAL DA MONOGRAFIA DEFENDIDA."
             if d["final"] else
             "ESTE EXEMPLAR CORRESPONDE À VERSÃO DA MONOGRAFIA ENTREGUE À BANCA ANTES DA DEFESA.")
    c.append(par(run(aviso), antes=2190, linha=290, recuo=0, jc="both"))
    # folha de aprovação
    if d["final"] or d["aprovacao_antecipada"]:
        dia, mes, ano = d["data"]
        c.append(par(run("Folha de Aprovação", b=True, sz=41), linha=600, jc="center", recuo=0,
                     nova_pagina=True))
        c.append(par(run(d["autor"].upper()), antes=1134, linha=290, jc="center", recuo=0))
        c.append(par(run(f"Monografia apresentada ao {d['programa']}, defendida na data de "
                         f"{dia}/{mes}/{ano}."), antes=1134, linha=290, recuo=0, jc="both"))
        c.append(par(run("Composição da Comissão Examinadora:"), antes=720, linha=290, recuo=0,
                     jc="left"))
        for j, (nome, inst_b) in enumerate(d["banca"]):
            seg = "Presidente da Comissão Julgadora" if j == 0 else inst_b
            # alinhado à esquerda: justificada, a linha antes da quebra se esticaria
            c.append(par(run(nome) + quebra() + run(seg), antes=720, linha=290, recuo=0,
                         jc="left"))
    else:
        c.append(par(run(f"Na versão final, esta página será substituída por outra informando a "
                         f"composição da banca e que a ata de defesa está arquivada pela {inst}."),
                     linha=290, recuo=0, jc="both", nova_pagina=True))

    def titulo_pre(t):
        c.append(espacador(ESPACO_PRE, nova_pagina=True))
        c.append(par(run(t), estilo="TituloPreTextual"))
    if d["agradecimentos"]:
        # como no LaTeX: \parskip de \medskipamount (6 pt) e recuo do corpo do
        # texto a partir do segundo parágrafo (o \parindent volta depois da
        # folha de aprovação)
        corpo = re.sub(r"\\begingroup\\setlength\{\\parskip\}\{\\medskipamount\}|"
                       r"\\par\\endgroup", "", d["agradecimentos"])
        titulo_pre("Agradecimentos")
        for j, bloco in enumerate(re.split(r"\n\s*\n", corpo.strip())):
            c.append(par(runs_pre(" ".join(bloco.split())), estilo="PreTexto", jc="both",
                         antes=120 if j else None, recuo=360 if j else None))
    titulo_pre("Resumo")
    for t, antes in paragrafos_pre(d["resumo"]):
        c.append(par(run(t), estilo="PreTexto", jc="both", antes=antes))
    titulo_pre("Abstract")
    for t, antes in paragrafos_pre(d["abstract"]):
        c.append(par(run(t), estilo="PreTexto", jc="both", antes=antes))


def runs_pre(t):
    """Texto das páginas iniciais com \\textit{...} em itálico."""
    saida = []
    for k, parte in enumerate(re.split(r"\\textit\{([^{}]*)\}", t)):
        assert "\\" not in parte, parte
        if parte:
            saida.append(run(parte, i=bool(k % 2)))
    return "".join(saida)


def paragrafos_pre(t):
    """Parágrafos do resumo.tex como [(texto, espaço antes)]: \\bigskip vale
    12 pt; \\noindent já é o padrão do estilo PreTexto."""
    saida = []
    for bloco in re.split(r"\n\s*\n", t):
        antes = 240 if r"\bigskip" in bloco else None
        bloco = re.sub(r"\\(?:bigskip|noindent)\s*", "", bloco).replace(r"\%", "%")
        assert "\\" not in bloco, bloco
        saida.append((" ".join(bloco.split()), antes))
    return saida


def listas_e_sumario(doc, paginas):
    """Lista de figuras, lista de tabelas e sumário como campos do Word,
    com as entradas já preenchidas (páginas da renderização)."""
    c = doc.corpo

    def titulo_pre(t):
        c.append(espacador(ESPACO_PRE, nova_pagina=True))
        c.append(par(run(t), estilo="TituloPreTextual"))

    def campo_lista(instr, entradas, estilo):
        inicio = (f'<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve">'
                  f' {x(instr)} </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>')
        fim = '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
        if not entradas:
            c.append(par(inicio + fim, estilo=estilo))
            return
        for j, (est, texto, marca) in enumerate(entradas):
            ligacao = (f'<w:hyperlink w:anchor="{marca}" w:history="1">' + texto +
                       run("\t" + str(paginas.get(marca, 0))) + "</w:hyperlink>")
            c.append(par((inicio if j == 0 else "") + ligacao + (fim if j == len(entradas) - 1 else ""),
                         estilo=est))

    titulo_pre("Lista de Figuras")
    campo_lista('TOC \\h \\z \\c "Figura"',
                [("ndicedeilustraes", t, m) for t, m, _ in doc.legendas["Figura"]], "ndicedeilustraes")
    titulo_pre("Lista de Tabelas")
    campo_lista('TOC \\h \\z \\c "Tabela"',
                [("ndicedeilustraes", t, m) for t, m, _ in doc.legendas["Tabela"]], "ndicedeilustraes")
    titulo_pre("Sumário")
    ent = []
    for nivel, num, titulo, marca, _ in doc.sumario:
        texto = (run(num + "\t") if num else "") + titulo
        ent.append((f"Sumrio{nivel}", texto, marca))
    campo_lista('TOC \\o "2-3" \\f \\h \\z', ent, "Sumrio1")


# ----------------------------------------------------------------------
# corpo
# ----------------------------------------------------------------------

def largura_texto(t, tamanho, larguras):
    return sum(larguras.get(ord(ch), 500) for ch in t) * tamanho / 1000


def converter_corpo(doc, docx, tx, larguras):
    z = zipfile.ZipFile(docx)
    xml = z.read("word/document.xml").decode("utf-8")
    rels = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"',
                           z.read("word/_rels/document.xml.rels").decode()))
    blocos = gl.blocos_do_corpo(xml)
    i_ref = next(i for i, b in enumerate(blocos) if gl.texto(b) == "REFERÊNCIAS")
    corpo, refs = blocos[1:i_ref], blocos[i_ref + 1:]
    eq_tab = [b for b in corpo if b.startswith("<w:tbl") and "<m:oMath>" in b]
    assert len(eq_tab) > 0

    c = doc.corpo
    capitulo = None
    primeiro = True          # primeiro parágrafo depois de título: sem recuo
    anterior = None          # tipo do bloco anterior
    lista_aberta = False
    secoes = []              # (número do capítulo, título) para os cabeçalhos

    def fecha_capitulo():
        if capitulo is None:
            return
        cp = doc.cabecalho(f"Capítulo {capitulo}. {secoes[-1][1]}", True)
        pr = doc.cabecalho("", False)
        c.append(par("", linha=20, regra="exact", sect=sect(cp, pr)))

    def notas(j):
        saida = []
        while j < len(corpo) and not corpo[j].startswith("<w:tbl"):
            t = gl.texto(corpo[j])
            m = re.match(r"(Fonte|Nota): ", t)
            if not m:
                break
            saida.append(par(tx.runs(gl.runs(corpo[j]), sz=20), estilo="FonteNota"))
            j += 1
        return saida, j

    def legenda(tipo, segs, cortar):
        marca, n = doc.marca()
        txt_plano = "".join(t for t, _ in segs)[cortar:]
        conteudo = tx.runs(segs, cortar=cortar)
        num = len(doc.legendas[tipo]) + 1
        texto_toc = run(f"{tipo} {num}: ") + conteudo
        doc.legendas[tipo].append((texto_toc, marca, f"{tipo} {num}: " + txt_plano))
        larg = largura_texto(f"{tipo} {num}: " + txt_plano, 12, larguras)
        jc = "center" if larg <= LARG_TEXTO / 20 else "both"
        dentro = run(f"{tipo} ") + campo(f"SEQ {tipo} \\* ARABIC", str(num)) + run(": ") + conteudo
        # tabela: o filete superior fica mais longe da legenda que a imagem
        return par(marcador(marca, n, dentro), estilo="Legenda", jc=jc,
                   depois=258 if tipo == "Tabela" else None)

    i = 0
    while i < len(corpo):
        b = corpo[i]
        t = gl.texto(b)
        if not b.startswith("<w:tbl") and gl.estilo(b) == "Ttulo2":
            nivel, num, nome = gl.classificar_titulo(t)
            if lista_aberta:
                lista_aberta = False
            if nivel == "chapter":
                fecha_capitulo()
                capitulo = int(num)
                titulo = gl.TITULOS_CAPITULO[nome]
                secoes.append((capitulo, titulo))
                marca, n = doc.marca()
                tc = campo_tc(f"{num}\t{titulo}")
                c.append(espacador(ESPACO_CAPITULO))
                c.append(par(marcador(marca, n, run(f"Capítulo {num}") + quebra() + run(titulo)) + tc,
                             estilo="Ttulo1"))
                doc.sumario.append((1, num, run(titulo), marca, f"Capítulo {num} {titulo}"))
            else:
                est = "Ttulo2" if nivel == "section" else "Ttulo3"
                if nome in gl.TITULOS_PARTE:
                    conteudo = run(gl.TITULOS_PARTE[nome])
                else:
                    conteudo = tx.runs(gl.runs(b), cortar=len(num) + 1)
                marca, n = doc.marca()
                antes = None
                if anterior == "Ttulo2" and est == "Ttulo3":
                    antes = 286   # título logo abaixo de outro: LaTeX não soma os espaços
                c.append(par(marcador(marca, n, run(num + "\t") + conteudo), estilo=est, antes=antes))
                doc.sumario.append((2 if est == "Ttulo2" else 3, num, conteudo, marca, f"{num} {t[len(num) + 1:]}"))
                anterior = est
            if nivel == "chapter":
                anterior = "Ttulo1"
            primeiro = True
            i += 1
            continue
        if b.startswith("<w:tbl") and "<m:oMath>" in b:
            c.append(tabela_equacao(b))
            primeiro = False
            anterior = "eq"
            i += 1
            continue
        m = gl.CAPTION.match(t)
        if m:
            tipo, n_doc = m.group(1), int(m.group(2))
            segs = gl.runs(b)
            if tipo == "Tabela":
                c.append(legenda("Tabela", segs, m.end()))
                ns, j = notas(i + 2)
                c.extend(tabela_dados(corpo[i + 1], tx))
                c.extend(ns)
            else:
                if "<w:drawing" in b:
                    img, j0 = b, i + 1
                else:
                    img, j0 = corpo[i + 1], i + 2
                c.append(legenda("Figura", segs, m.end()))
                rid = re.search(r'<a:blip r:embed="([^"]+)"', img).group(1)
                alvo = rels[rid]
                cx0 = int(re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', img).group(1))
                cy0 = int(re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', img).group(2))
                frac = round(min(cx0 / (9360 * 635), 1.0), 2)
                cx = round(frac * EMU_TEXTO)
                cy = round(cy0 * cx / cx0)
                descr = html.unescape(re.search(r'descr="([^"]*)"', img).group(1)) if 'descr="' in img else ""
                c.append(par(doc.imagem(z.read("word/" + alvo), alvo.rsplit(".", 1)[1], cx, cy, descr),
                             estilo="Figura"))
                ns, j = notas(j0)
                c.extend(ns)
            anterior = "float"
            i = j
            continue
        mi = re.match(r"([a-i])\) ", t)
        if mi and capitulo == 1:
            item = run(mi.group(1) + ")\t") + tx.runs(gl.runs(b), cortar=mi.end())
            antes = None if lista_aberta else (178 if anterior not in ("Ttulo2", "Ttulo3") else 0)
            c.append(par(item, estilo="ItemLista", antes=antes))
            lista_aberta = True
            primeiro = False
            anterior = "item"
            i += 1
            continue
        if t.strip():
            est = "SemRecuo" if primeiro else None
            antes = 122 if anterior == "item" else None
            c.append(par(tx.runs(gl.runs(b)), estilo=est, antes=antes))
            primeiro = False
            anterior = "par"
            lista_aberta = False
        i += 1
    fecha_capitulo()
    return refs, rels


def tabela_equacao(b):
    """Tabela de equação do DOCX fundido: a mesma OMML, com o número à
    direita, em tabela sem bordas da largura do texto."""
    linhas = re.findall(r"<w:tr[ >].*?</w:tr>", b, flags=re.S)
    tr = []
    for ln in linhas:
        om = re.search(r"<m:oMathPara>.*?</m:oMathPara>", ln, flags=re.S).group(0)
        om = re.sub(r"<w:sz(?:Cs)? w:val=\"\d+\"/>", "", om)
        num = re.search(r"<w:t>\((\d+)\)</w:t>", ln).group(1)
        tr.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>'
                  '<w:tc><w:tcPr><w:tcW w:w="8171" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
                  f'<w:p>{ppr(estilo="Equacao", antes=150, depois=150)}{om}</w:p></w:tc>'
                  '<w:tc><w:tcPr><w:tcW w:w="900" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
                  f'<w:p>{ppr(estilo="Equacao", jc="right", antes=150, depois=150)}{run(f"({num})")}</w:p></w:tc></w:tr>')
    return ('<w:tbl><w:tblPr><w:tblW w:w="9071" w:type="dxa"/><w:jc w:val="center"/>'
            '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="0" w:type="dxa"/>'
            '<w:right w:w="0" w:type="dxa"/></w:tblCellMar><w:tblLook w:val="0000" w:firstRow="0" '
            'w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="1" w:noVBand="1"/></w:tblPr>'
            '<w:tblGrid><w:gridCol w:w="8171"/><w:gridCol w:w="900"/></w:tblGrid>' + "".join(tr) + "</w:tbl>")


def tabela_dados(b, tx):
    """Tabela com filetes no estilo booktabs, cabeçalho em negrito e
    centralizado, colunas alinhadas como no LaTeX."""
    larg = [int(w) for w in re.findall(r'<w:gridCol w:w="(\d+)"/>', b)]
    linhas = re.findall(r"<w:tr[ >].*?</w:tr>", b, flags=re.S)
    n = len(larg)
    tot = sum(larg)
    # como as colunas X do LaTeX: o conteúdo é proporcional e o espaço entre
    # colunas (6 pt de cada lado, nenhum nas bordas) é somado à célula
    pads = [0 if n == 1 else (120 if k in (0, n - 1) else 240) for k in range(n)]
    util = LARG_TEXTO - sum(pads)
    cols = [round(util * w / tot) + pads[k] for k, w in enumerate(larg)]
    cols[-1] += LARG_TEXTO - sum(cols)
    jcs = [[(re.search(r'<w:jc w:val="(\w+)"/>', re.findall(r"<w:p[ >].*?</w:p>", c, flags=re.S)[0])
             or [None, "left"])[1] for c in re.findall(r"<w:tc>.*?</w:tc>", ln, flags=re.S)]
           for ln in linhas]
    alin = ["center" if gl.alinhamento([jl[k] for jl in jcs[1:]]) == "center" else "left"
            for k in range(n)]
    estilo = "TabelaTextoMenor" if n > 6 else "TabelaTexto"
    sz = 20 if n > 6 else 22
    longa = gl.altura_estimada(larg, linhas, r"\footnotesize" if n > 6 else r"\small") > gl.ALTURA_LONGA
    trs = []
    for r_, ln in enumerate(linhas):
        cels = re.findall(r"<w:tc>.*?</w:tc>", ln, flags=re.S)
        tcs = []
        for k, cel in enumerate(cels):
            bordas = []
            if r_ == 0:
                bordas.append('<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>')
                bordas.append('<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>')
            if r_ == len(linhas) - 1:
                bordas.append('<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>')
            mar = ('<w:tcMar>' + ('<w:left w:w="0" w:type="dxa"/>' if k == 0 else "")
                   + ('<w:right w:w="0" w:type="dxa"/>' if k == n - 1 else "") + "</w:tcMar>"
                   if k in (0, n - 1) else "")
            ps = []
            for p in re.findall(r"<w:p[ >].*?</w:p>", cel, flags=re.S):
                manter = not longa and r_ < len(linhas) - 1
                if r_ == 0:
                    ps.append(par(tx.runs(gl.runs(p), sz=sz, negrito=True), estilo=estilo,
                                  jc="center", keep=manter or longa))
                else:
                    ps.append(par(tx.runs(gl.runs(p), sz=sz), estilo=estilo, jc=alin[k], keep=manter))
            tcs.append(f'<w:tc><w:tcPr><w:tcW w:w="{cols[k]}" w:type="dxa"/>'
                       + (f"<w:tcBorders>{''.join(bordas)}</w:tcBorders>" if bordas else "")
                       + mar + '<w:vAlign w:val="top"/></w:tcPr>' + "".join(ps) + "</w:tc>")
        cab = "<w:tblHeader/>" if r_ == 0 else ""
        trs.append(f"<w:tr><w:trPr><w:cantSplit/>{cab}</w:trPr>" + "".join(tcs) + "</w:tr>")
    return ['<w:tbl><w:tblPr><w:tblW w:w="9071" w:type="dxa"/><w:jc w:val="center"/>'
            '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="45" w:type="dxa"/>'
            '<w:left w:w="120" w:type="dxa"/><w:bottom w:w="45" w:type="dxa"/>'
            '<w:right w:w="120" w:type="dxa"/></w:tblCellMar><w:tblLook w:val="0420" w:firstRow="1" '
            'w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="1" w:noVBand="1"/></w:tblPr>'
            "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in cols) + "</w:tblGrid>"
            + "".join(trs) + "</w:tbl>"]


# ----------------------------------------------------------------------
# referências
# ----------------------------------------------------------------------

def referencias(doc, refs, rels_orig):
    """Lista do DOCX fundido com os nomes na forma do biblatex (caixa
    normal), aspas tipográficas e DOI e URL em fonte mono, como no LaTeX."""
    entradas = entradas_bib()
    assert len(entradas) == len([r for r in refs if gl.texto(r).strip()]), "bib e DOCX diferem"
    c = doc.corpo
    marca, n = doc.marca()
    # título sem número: mais alto que "Capítulo N" (como o \\chapter* do LaTeX)
    c.append(espacador(ESPACO_CAPITULO - 14.1))
    c.append(par(marcador(marca, n, run("Referências")) + campo_tc("Referências"),
                 estilo="Ttulo1", depois=560))
    doc.sumario.append((1, "", run("Referências"), marca, "Referências"))
    for (chave, tipo, campos), b in zip(entradas, [r for r in refs if gl.texto(r).strip()]):
        troca = []
        if "holder" in campos:
            org = campos["holder"].strip("{}").replace("\\&", "&")
            mista, _ = nomes_ref(campos["author"], inicio_de_frase=False)
            fam, giv = nomes(campos["author"])[0][0]
            antes_ = f"{org.upper()}. {giv} {fam} et al."
            depois_ = f"{org}. {giv} {fam} et al."
            troca.append((antes_, depois_))
        else:
            mista, maiusc = nomes_ref(campos["author"])
            troca.append((maiusc, mista))
        if "editor" in campos:
            mista_e, maiusc_e = nomes_ref(campos["editor"], inicio_de_frase=False)
            troca.append(("In: " + maiusc_e, "In: " + mista_e))
        partes = []
        for el in re.findall(r"<w:hyperlink .*?</w:hyperlink>|<w:r[ >].*?</w:r>", b, flags=re.S):
            if el.startswith("<w:hyperlink"):
                rid = re.search(r'r:id="([^"]+)"', el).group(1)
                novo = doc.rel("hyperlink", rels_orig[rid], externo=True)
                partes.append(("link", gl.texto(el), novo))
            else:
                rp = re.search(r"<w:rPr>(.*?)</w:rPr>", el, flags=re.S)
                rp = rp.group(1) if rp else ""
                partes.append(("b" if "<w:b/>" in rp else "n", html.unescape(
                    "".join(re.findall(r"<w:t[^>]*>([^<]*)", el))), None))
        # junta trechos vizinhos de mesmo formato (o DOCX divide nomes em
        # vários trechos por causa da revisão ortográfica)
        juntas = []
        for pt in partes:
            if juntas and pt[0] != "link" and juntas[-1][0] == pt[0]:
                juntas[-1] = (pt[0], juntas[-1][1] + pt[1], None)
            else:
                juntas.append(pt)
        partes = juntas
        texto_total = "".join(p[1] for p in partes)
        for a, d_ in troca:
            assert a in texto_total, (chave, a, texto_total[:80])
        saida = []
        for tipo_p, t, rid in partes:
            for a, d_ in troca:
                t = t.replace(a, d_)
            t = re.sub(r'"([^"]+)"', "“\\1”", t)
            if tipo_p == "link":
                # pontos de quebra invisíveis depois de / . - , como o pacote url
                t = re.sub(r"([/.\-])(?=.)", "\\1\u200b", t) if len(t) > 30 else t
                saida.append(f'<w:hyperlink r:id="{rid}" w:history="1">'
                             + run(t, font=FONTE_MONO, sz=21) + "</w:hyperlink>")
            else:
                saida.append(run(t, b=tipo_p == "b"))
        c.append(par("".join(saida), estilo="Referencia"))


# ======================================================================
# pacote
# ======================================================================

def montar(docx_origem, paginas, fontes, render, d):
    doc = Documento()
    cit = gl.Citacoes((LATEX / "bibliografia.bib").read_text(encoding="utf-8"))
    tx = Textos(cit)
    tx.render = render
    from fontTools.ttLib import TTFont
    larguras = {}
    f = TTFont(str(FONTE_OTF / "LinLibertine_R.otf"))
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    larguras = {u: hmtx[g][0] for u, g in cmap.items()}

    refs, rels_orig = converter_corpo(doc, docx_origem, tx, larguras)
    referencias(doc, refs, rels_orig)
    corpo = doc.corpo
    doc.corpo = []
    logo = (LATEX / "logotipos" / "logo-fca.png").read_bytes()
    pre_textuais(doc, d, logo)
    listas_e_sumario(doc, paginas)
    doc.corpo.append(par("", linha=20, sect=sect()))
    cab_ref = doc.cabecalho("Referências", True)
    pri_ref = doc.cabecalho("", False)
    final = sect(cab_ref, pri_ref).replace('<w:type w:val="nextPage"/>', "")
    xml_doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
               f'<w:document {NS}><w:body>' + "".join(doc.corpo + corpo) + final
               + "</w:body></w:document>")

    tipos = {"image": f"{REL}/image", "header": f"{REL}/header", "hyperlink": f"{REL}/hyperlink"}
    rels = [f'<Relationship Id="rId1" Type="{REL}/styles" Target="styles.xml"/>',
            f'<Relationship Id="rId2" Type="{REL}/settings" Target="settings.xml"/>',
            f'<Relationship Id="rId3" Type="{REL}/fontTable" Target="fontTable.xml"/>']
    for rid, (tipo, alvo, ext) in doc.rels.items():
        rels.append(f'<Relationship Id="{rid}" Type="{tipos[tipo]}" Target="{html.escape(alvo)}"'
                    + (' TargetMode="External"' if ext else "") + "/>")
    fontes_xml, fontes_rels, arquivos_fonte = [], [], {}
    k = 0
    for fam, var in fontes:
        emb = ""
        for v, (arq, chave, dados) in var.items():
            k += 1
            fontes_rels.append(f'<Relationship Id="rIdF{k}" Type="{REL}/font" Target="fonts/{arq}"/>')
            emb += f'<w:embed{v} r:id="rIdF{k}" w:fontKey="{chave}"/>'
            arquivos_fonte["word/fonts/" + arq] = dados
        fontes_xml.append(f'<w:font w:name="{fam}"><w:charset w:val="00"/><w:family w:val="roman"/>'
                          f'<w:pitch w:val="variable"/>{emb}</w:font>')
    fontes_xml.append('<w:font w:name="Cambria Math"><w:panose1 w:val="02040503050406030204"/>'
                      '<w:charset w:val="00"/><w:family w:val="roman"/><w:pitch w:val="variable"/></w:font>')
    ct_hdr = "".join(f'<Override PartName="/word/{n}" ContentType="application/vnd.openxmlformats-'
                     'officedocument.wordprocessingml.header+xml"/>' for n in doc.cabecalhos)
    partes = {
        "[Content_Types].xml":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="png" ContentType="image/png"/>'
            '<Default Extension="odttf" ContentType="application/vnd.openxmlformats-officedocument.obfuscatedFont"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-'
            'officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-'
            'officedocument.wordprocessingml.styles+xml"/>'
            '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-'
            'officedocument.wordprocessingml.settings+xml"/>'
            '<Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-'
            'officedocument.wordprocessingml.fontTable+xml"/>' + ct_hdr +
            '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-'
            'package.core-properties+xml"/>'
            '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-'
            'officedocument.extended-properties+xml"/></Types>',
        "_rels/.rels":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{REL}/officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/'
            'metadata/core-properties" Target="docProps/core.xml"/>'
            f'<Relationship Id="rId3" Type="{REL}/extended-properties" Target="docProps/app.xml"/>'
            "</Relationships>",
        "word/document.xml": xml_doc,
        "word/styles.xml": estilos(),
        "word/settings.xml":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<w:settings {NS}><w:zoom w:percent="100"/><w:embedTrueTypeFonts/>'
            '<w:defaultTabStop w:val="708"/><w:autoHyphenation/><w:hyphenationZone w:val="425"/>'
            '<w:characterSpacingControl w:val="doNotCompress"/><w:updateFields w:val="true"/>'
            '<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/'
            'office/word" w:val="15"/></w:compat>'
            '<m:mathPr><m:mathFont m:val="Cambria Math"/><m:brkBin m:val="before"/>'
            '<m:brkBinSub m:val="--"/><m:smallFrac m:val="0"/><m:dispDef/><m:lMargin m:val="0"/>'
            '<m:rMargin m:val="0"/><m:defJc m:val="centerGroup"/><m:wrapIndent m:val="1440"/>'
            '<m:intLim m:val="subSup"/><m:naryLim m:val="undOvr"/></m:mathPr>'
            '<w:themeFontLang w:val="pt-BR"/><w:decimalSymbol w:val=","/><w:listSeparator w:val=";"/>'
            "</w:settings>",
        "word/fontTable.xml":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<w:fonts {NS}>' + "".join(fontes_xml) + "</w:fonts>",
        "word/_rels/fontTable.xml.rels":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(fontes_rels) + "</Relationships>",
        "word/_rels/document.xml.rels":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(rels) + "</Relationships>",
        "docProps/core.xml":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f"<dc:title>{x(d['titulo'])}</dc:title><dc:creator>{x(d['autor'])}</dc:creator>"
            "<dc:language>pt-BR</dc:language></cp:coreProperties>",
        "docProps/app.xml":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
            "<Application>Microsoft Office Word</Application></Properties>",
    }
    for n, xml_h in doc.cabecalhos.items():
        partes["word/" + n] = xml_h
    binarios = dict(doc.media)
    binarios.update(arquivos_fonte)
    return partes, binarios, doc


def gravar(destino, partes, binarios):
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for n in ["[Content_Types].xml", "_rels/.rels"]:
            z.writestr(n, partes[n])
        for n, v in partes.items():
            if n not in ("[Content_Types].xml", "_rels/.rels"):
                z.writestr(n, v)
        for n, v in binarios.items():
            z.writestr(n, v)


def paginas_renderizadas(docx, doc):
    """Página de cada título e legenda na renderização do LibreOffice."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, str(docx)],
                       capture_output=True, check=True, timeout=600)
        pdf = Path(tmp) / (Path(docx).stem + ".pdf")
        n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(
            ["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
        textos = [subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), str(pdf), "-"],
                                 capture_output=True, text=True).stdout for p in range(1, n + 1)]
    norm = lambda t: re.sub(r"[^0-9a-zà-ÿ]", "", t.lower())  # noqa: E731
    pags = [norm(t) for t in textos]
    inicio = next(i for i, t in enumerate(pags) if "capítulo1introdução" in t)
    saida = {}
    for grupo in (doc.sumario, doc.legendas["Figura"], doc.legendas["Tabela"]):
        p = inicio
        for item in grupo:
            marca, plano = item[-2], item[-1]
            # o número do título pode sair separado do texto na extração
            num, _, resto = plano.partition(" ") if re.match(r"\d", plano) else ("", "", plano)
            chave = norm(resto)[:40]
            while p < len(pags) and not (chave in pags[p] and norm(num) in pags[p]):
                p += 1
            assert p < len(pags), f"não achei {plano!r} na renderização"
            saida[marca] = p + 1
    return saida, n


def main():
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "tcc" / "TCC_modelo_FT.docx"
    origem = RAIZ / "tcc" / "TCC_exo1_exo2.docx"
    d = dados_tese()
    # citações: comandos usados no texto e no que o biblatex imprime para cada um
    cit = gl.Citacoes((LATEX / "bibliografia.bib").read_text(encoding="utf-8"))
    tx = Textos(cit)
    xml = zipfile.ZipFile(origem).read("word/document.xml").decode("utf-8")
    comandos = []
    for b in gl.blocos_do_corpo(xml):
        if gl.texto(b) == "REFERÊNCIAS":
            break
        for p in re.findall(r"<w:p[ >].*?</w:p>", b, flags=re.S) if b.startswith("<w:tbl") else [b]:
            comandos += tx.coletar(gl.runs(p))
    render = renderizar_citacoes(comandos)
    fontes = fontes_embutidas()
    paginas = {}
    for passada in (1, 2, 3):
        partes, binarios, doc = montar(origem, paginas, fontes, render, d)
        gravar(destino, partes, binarios)
        novas, n_pag = paginas_renderizadas(destino, doc)
        if novas == paginas:
            break
        paginas = novas
    else:
        partes, binarios, doc = montar(origem, paginas, fontes, render, d)
        gravar(destino, partes, binarios)
    print(f"{destino.name}: {n_pag} páginas na renderização do LibreOffice; "
          f"{len(doc.sumario)} entradas no sumário, {len(doc.legendas['Figura'])} figuras, "
          f"{len(doc.legendas['Tabela'])} tabelas; {len(render)} citações distintas")


if __name__ == "__main__":
    main()
