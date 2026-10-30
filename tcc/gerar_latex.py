"""Converte o TCC fundido (DOCX) para os capítulos LaTeX do modelo FT/FCA.

Uso: python3 tcc/gerar_latex.py tcc/TCC_exo1_exo2.docx latex/

Gera latex/capitulos/*.tex e latex/figuras/*.png. Não toca em tese.tex,
preambulo.tex, resumo.tex, agradecimentos.tex nem bibliografia.bib, que são
editados à mão. O texto vem do DOCX sem alteração; mudam apenas:
- os números de tabela, figura, equação e seção citados no texto, que viram
  \\ref e \\eqref para os rótulos correspondentes;
- as citações (AUTOR, ano) e Autor (ano), que viram \\cite e \\textcite com as
  chaves de bibliografia.bib;
- as equações (OMML), convertidas pelo pandoc para LaTeX.
O conversor interrompe a geração se a numeração resultante não coincidir com
a do DOCX ou se sobrar algo que não saiba converter.
"""
import html
import json
import re
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

ARQUIVOS = {1: "introducao", 2: "fundamentacao", 3: "materiais_metodos",
            4: "resultados", 5: "conclusao"}
TITULOS_CAPITULO = {
    "INTRODUÇÃO": "Introdução",
    "FUNDAMENTAÇÃO TEÓRICA": "Fundamentação teórica",
    "MATERIAIS E MÉTODOS": "Materiais e métodos",
    "RESULTADOS E DISCUSSÃO": "Resultados e discussão",
    "CONCLUSÃO": "Conclusão",
}

# caracteres fora do Latin-1 usados no texto corrido; o preâmbulo declara
# cada um com \DeclareUnicodeCharacter (ver preambulo.tex)
UNICODE_TEXTO = set("θτℓλδφψσαβργηπκεμ−≤≥≈⊥√∂→ŷ—–")

ESCAPE = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$",
          "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_",
          "^": r"\^{}", "~": r"\textasciitilde{}", '"': r"\textquotedbl{}"}

def escapar(t):
    return "".join(ESCAPE.get(c, c) for c in t)


def sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t)
                   if not unicodedata.combining(c))


# ======================================================================
# leitura do DOCX
# ======================================================================

def blocos_do_corpo(doc):
    corpo = doc[doc.index("<w:body>") + 8:]
    return re.findall(r"<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>", corpo, flags=re.S)


def estilo(b):
    m = re.search(r'<w:pStyle w:val="([^"]+)"', b)
    return m.group(1) if m else None


def texto(b):
    return html.unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)", b)))


def runs(p):
    """Lista de (texto, formato) de um parágrafo, sem as equações.
    formato = (itálico, 'sub'|'sup'|None, negrito)."""
    p = re.sub(r"<m:oMath>.*?</m:oMath>", "", p, flags=re.S)
    saida = []
    for r in re.findall(r"<w:r[ >].*?</w:r>", p, flags=re.S):
        rpr = re.search(r"<w:rPr>(.*?)</w:rPr>", r, flags=re.S)
        rpr = rpr.group(1) if rpr else ""
        t = html.unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)", r)))
        assert "<w:tab/>" not in r and "<w:br" not in r, r[:200]
        if not t:
            continue
        ital = bool(re.search(r'<w:i/>|<w:i w:val="(?:1|true)"/>', rpr))
        neg = bool(re.search(r'<w:b/>|<w:b w:val="(?:1|true)"/>', rpr))
        va = re.search(r'<w:vertAlign w:val="(\w+)"/>', rpr)
        va = {"subscript": "sub", "superscript": "sup"}.get(va.group(1)) if va else None
        saida.append((t, (ital, va, neg)))
    return saida


# ======================================================================
# equações pelo pandoc
# ======================================================================

def equacoes_pandoc(docx):
    ast = json.loads(subprocess.run(["pandoc", "-f", "docx", "-t", "json", str(docx)],
                                    check=True, capture_output=True, text=True).stdout)
    eqs = []

    def andar(x):
        if isinstance(x, dict):
            if x.get("t") == "Math":
                assert x["c"][0]["t"] == "DisplayMath"
                eqs.append(x["c"][1])
                return
            for v in x.values():
                andar(v)
        elif isinstance(x, list):
            for v in x:
                andar(v)
    andar(ast["blocks"])
    return [ajustar_tex(e) for e in eqs]


def ajustar_tex(e):
    # funções que o pandoc deixa como texto em itálico
    e = re.sub(r"\{(atan2|arcsen|sen)\}", r"\\operatorname{\1}", e)
    # ℓ: o pandoc escreve \mathcal{l}
    e = e.replace(r"\mathcal{l}", r"\ell")
    # vírgula decimal sem o espaço de pontuação do modo matemático
    e = re.sub(r"(\d),(\d)", r"\1{,}\2", e)
    assert not re.search(r"[^\x00-\x7f]", e), e
    return e


# ======================================================================
# citações
# ======================================================================

def chaves_bib(bib):
    """{(sobrenome normalizado, ano): chave} a partir das chaves do .bib,
    que seguem o padrão sobrenome+ano."""
    tab = {}
    for k in re.findall(r"^@\w+\{([^,]+),", bib, flags=re.M):
        m = re.match(r"([a-z]+)(\d{4}[a-z]?)$", k)
        if m:
            tab[(m.group(1), m.group(2))] = k
    tab[("suitx", "[202-]")] = "suitx"
    return tab


def norm_nome(t):
    return re.sub(r"[^a-z]", "", sem_acento(t).lower())


def caixa_mista(t):
    """ZEIAEE et al. -> Zeiaee et al. (referências ausentes do .bib)."""
    return re.sub(r"\b([A-ZÀ-Ý])([A-ZÀ-Ý]+)\b", lambda m: m.group(1) + m.group(2).lower(), t)


class Citacoes:
    def __init__(self, bib):
        self.tab = chaves_bib(bib)
        self.usadas = set()
        self.ausentes = []

    def chave(self, autores, ano):
        primeiro = re.split(r";| et al\.|,| e ", autores)[0]
        return self.tab.get((norm_nome(primeiro), ano))

    def parenteses(self, conteudo):
        """'BARSOTTI et al., 2015; BOUTERAA; BEN ABDALLAH, 2016' ->
        [(autores, ano), ...] ou None se não for citação."""
        grupos, atual = [], []
        for tok in conteudo.split("; "):
            atual.append(tok)
            m = re.match(r"(.*), (\d{4}[a-z]?|\[202-\])$", "; ".join(atual))
            if m:
                grupos.append((m.group(1), m.group(2)))
                atual = []
        if atual or not grupos:
            return None
        if not all(re.match(r"[A-ZÀ-Ý]{2}", a) for a, _ in grupos):
            return None
        return grupos

    def latex_parenteses(self, grupos, original):
        chaves, literais = [], []
        for autores, ano in grupos:
            k = self.chave(autores, ano)
            if k:
                assert not literais, f"citação sem referência no meio do grupo: {original}"
                chaves.append(k)
            else:
                literais.append(f"{caixa_mista(autores)}, {ano}")
                self.ausentes.append(f"{autores}, {ano}")
        self.usadas.update(chaves)
        if not chaves:
            return "(" + escapar("; ".join(literais)) + ")"
        if literais:
            return r"\citecomsemref{" + escapar("; ".join(literais)) + "}{" + ",".join(chaves) + "}"
        return r"\cite{" + ",".join(chaves) + "}"


# ======================================================================
# transformação do texto de um parágrafo
# ======================================================================

class Rotulos:
    def __init__(self):
        self.tab, self.fig, self.eq, self.sec = {}, {}, {}, {}


def citacoes_no_texto(t, cit):
    """Citações do texto plano: [(ini, fim, comando LaTeX)]. Uma citação a
    obra ausente da lista sai como texto entre parênteses, sem comando."""
    subs = []

    def livre(i, j):
        return all(not (i < b and a < j) for a, b, _ in subs)

    # citações entre parênteses
    for m in re.finditer(r"\(([^()]*?(?:\d{4}[a-z]?|\[202-\]))\)", t):
        g = cit.parenteses(m.group(1))
        if g:
            subs.append((m.start(), m.end(), cit.latex_parenteses(g, m.group(0))))
    # citações no texto: Autor (ano), Autor, Autor e Autor (ano), Autor et al. (ano)
    nome = r"(?:Mc[A-Z]|[A-ZÄÖÜ])[\w'äöü-]+"
    padrao = (rf"(\b(?:[Vv]an der |[Dd]e )?)({nome}((?:, {nome})*(?: e {nome})?)"
              rf"(?: et al\.)?) \((\d{{4}}[a-z]?)\)")
    for m in re.finditer(padrao, t):
        prefixo, autores, ano = m.group(1), m.group(2), m.group(4)
        k = cit.tab.get((norm_nome(prefixo + autores.split(",")[0].split(" e ")[0].split(" et al.")[0]), ano))
        ini = m.start()
        if not k:
            k = cit.chave(autores, ano)
            ini = m.start(2)
        if not k:
            continue
        if not livre(ini, m.end()):
            continue
        comando = r"\Textcite" if t[ini].isupper() and prefixo and prefixo[0].isupper() else r"\textcite"
        cit.usadas.add(k)
        subs.append((ini, m.end(), comando + "{" + k + "}"))
    return subs


def substituicoes(t, rot, cit):
    """Trechos do texto plano a trocar por LaTeX: [(ini, fim, latex)]."""
    subs = citacoes_no_texto(t, cit)

    def livre(i, j):
        return all(not (i < b and a < j) for a, b, _ in subs)

    # tabelas
    for m in re.finditer(r"\b(Tabelas?) (\d+)((?:, \d+)*)((?: e \d+)?)", t):
        nums = re.findall(r"\d+", m.group(0))
        partes = re.split(r"(\d+)", m.group(0)[len(m.group(1)) + 1:])
        saida = m.group(1) + "~"
        for p in partes:
            saida += r"\ref{" + rot.tab[int(p)] + "}" if p.isdigit() else escapar(p)
        assert all(int(n) in rot.tab for n in nums), m.group(0)
        if livre(m.start(), m.end()):
            subs.append((m.start(), m.end(), saida))
    # figuras do documento (as da patente ficam como texto)
    for m in re.finditer(r"\b(Figuras?) (\d+)((?:, \d+)*)((?: e \d+)?)(?=(.{0,14}))", t):
        n, resto = int(m.group(2)), m.group(5)
        patente = (resto.startswith((" da patente", " da EP", " da US")) or re.match(r", p\. \d", resto)
                   or n == 56
                   or m.group(3).startswith(", 16"))
        if patente:
            continue
        fim = m.end(4)
        corpo = t[m.start(2):fim]
        saida = m.group(1) + "~"
        for p in re.split(r"(\d+)", corpo):
            saida += r"\ref{" + rot.fig[int(p)] + "}" if p.isdigit() else escapar(p)
        if livre(m.start(), fim):
            subs.append((m.start(), fim, saida))
    # equações
    for m in re.finditer(r"\b(Equaç(?:ão|ões)) (\(\d+\)(?:(?:, | e | a )\(\d+\))*)", t):
        saida = m.group(1) + "~"
        for p in re.split(r"(\(\d+\))", m.group(2)):
            if re.fullmatch(r"\(\d+\)", p):
                saida += r"\eqref{" + rot.eq[int(p[1:-1])] + "}"
            else:
                saida += escapar(p)
        if livre(m.start(), m.end()):
            subs.append((m.start(), m.end(), saida))
    # seções
    num = r"\d+(?:\.\d+)*"
    for m in re.finditer(rf"\b([Ss]eç(?:ão|ões)) ({num}(?:(?:\s+a\s+|\s+e\s+|,\s*){num})*)", t):
        saida = m.group(1) + "~"
        for p in re.split(rf"({num})", m.group(2)):
            if re.fullmatch(num, p):
                assert p in rot.sec, f"seção sem rótulo: {p} em '{m.group(0)}'"
                saida += r"\ref{" + rot.sec[p] + "}"
            else:
                saida += escapar(p)
        if livre(m.start(), m.end()):
            subs.append((m.start(), m.end(), saida))
    subs.sort()
    for (a, b, _), (c, d, _) in zip(subs, subs[1:]):
        assert b <= c, (t[a:b], t[c:d])
    return subs


def para_latex(segs, rot, cit, ignorar_negrito=True, cortar_inicio=0):
    """Converte (texto, formato) em LaTeX, aplicando as substituições."""
    chars = [(c, f) for t, f in segs for c in t][cortar_inicio:]
    plano = "".join(c for c, _ in chars)
    subs = substituicoes(plano, rot, cit)
    saida, i, k = [], 0, 0
    while i < len(chars):
        if k < len(subs) and i == subs[k][0]:
            a, b, lx = subs[k]
            assert all(chars[j][1][1] is None for j in range(a, b)), plano[a:b]
            saida.append(lx)
            i, k = b, k + 1
            continue
        fim = subs[k][0] if k < len(subs) else len(chars)
        j = i
        while j < fim and chars[j][1] == chars[i][1]:
            j += 1
        trecho = "".join(c for c, _ in chars[i:j])
        ital, va, neg = chars[i][1]
        lx = escapar(trecho)
        if va == "sub":
            lx = r"\textsubscript{" + lx + "}"
        elif va == "sup":
            lx = r"\textsuperscript{" + lx + "}"
        if ital:
            lx = r"\textit{" + lx + "}"
        if neg and not ignorar_negrito:
            lx = r"\textbf{" + lx + "}"
        saida.append(lx)
        i = j
    lx = "".join(saida)
    # o texto corrido não tem aspas retas; se aparecerem, a forma tipográfica
    # (`` e '') precisa ser escolhida à mão
    assert "textquotedbl" not in lx, lx
    for c in set(re.sub(r"\\[a-zA-Z]+|[\x00-\xff]", "", lx)):
        assert c in UNICODE_TEXTO, f"caractere sem declaração: {c!r} em {plano[:80]}"
    return lx


# ======================================================================
# rótulos
# ======================================================================

PARADAS = {"a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "na",
           "no", "nas", "nos", "com", "para", "por", "pela", "pelo", "ao", "um",
           "uma", "entre", "sem", "sob", "seus", "suas", "sua", "seu", "cada"}


def slug(t, usados, prefixo):
    palavras = [w for w in re.findall(r"[a-z0-9]+", sem_acento(t).lower())
                if w not in PARADAS and not w.isdigit()]
    for n in range(min(4, len(palavras)), len(palavras) + 1):
        s = prefixo + ":" + "-".join(palavras[:n])
        if s not in usados:
            usados.add(s)
            return s
    raise ValueError(t)


CAPTION = re.compile(r"^(Tabela|Figura) (\d+)(?: —|:) ")
TITULO = [
    (re.compile(r"^(\d) (.+)$"), "chapter"),
    (re.compile(r"^(\d\.\d+) (.+)$"), "section"),
    (re.compile(r"^(\d\.\d+\.\d+) (.+)$"), "subsection"),
]


def classificar_titulo(t):
    for rx, nivel in TITULO:
        m = rx.match(t)
        if m:
            return nivel, m.group(1), m.group(2)
    raise ValueError(t)


def pre_rotulos(blocos):
    """Primeira passagem: rótulos de tabelas, figuras, equações e seções,
    para resolver referências a elementos que aparecem depois."""
    rot, usados = Rotulos(), set()
    n_eq = 0
    for b in blocos:
        if b.startswith("<w:tbl"):
            for n in re.findall(r"<w:t>\((\d+)\)</w:t>", b) if "<m:oMath>" in b else []:
                n_eq += 1
                assert int(n) == n_eq, (n, n_eq)
                rot.eq[int(n)] = f"eq:{int(n):02d}"
            continue
        t = texto(b)
        if estilo(b) == "Ttulo2" and t != "REFERÊNCIAS":
            _, num, _ = classificar_titulo(t)
            rot.sec[num] = f"sec:{num}"
            continue
        m = CAPTION.match(t)
        if m:
            tipo, n = m.group(1), int(m.group(2))
            alvo = rot.tab if tipo == "Tabela" else rot.fig
            assert n == len(alvo) + 1, t
            alvo[n] = slug(t[m.end():], usados, "tab" if tipo == "Tabela" else "fig")
    return rot


# ======================================================================
# blocos
# ======================================================================

def tabela_equacoes(b, eqs, pos):
    linhas = re.findall(r"<w:tr[ >].*?</w:tr>", b, flags=re.S)
    tex, nums = [], []
    for ln in linhas:
        k = ln.count("<m:oMath>")
        assert k == 1, ln[:200]
        tex.append(eqs[pos + len(tex)])
        nums.append(int(re.search(r"<w:t>\((\d+)\)</w:t>", ln).group(1)))
    if len(tex) == 1:
        corpo = ["\\begin{equation}", "  " + tex[0], f"  \\label{{eq:{nums[0]:02d}}}",
                 "\\end{equation}"]
    else:
        corpo = ["\\begin{gather}"]
        for i, (e, n) in enumerate(zip(tex, nums)):
            fim = " \\\\" if i < len(tex) - 1 else ""
            corpo.append(f"  {e} \\label{{eq:{n:02d}}}{fim}")
        corpo.append("\\end{gather}")
    return corpo, len(tex)


def alinhamento(cels):
    c = sum(1 for x in cels if x == "center")
    return "center" if c > len(cels) / 2 else "left"


def altura_estimada(larg, linhas, tamanho):
    """Altura aproximada da tabela em pt, para decidir se ela precisa
    atravessar páginas (texto com 455 pt de largura e 700 pt de altura)."""
    corpo = 10 if tamanho == r"\footnotesize" else 10.95
    largura_letra = 4.6 * corpo / 10.95
    tot, h = sum(larg), 0.0
    for ln in linhas:
        cels = re.findall(r"<w:tc>.*?</w:tc>", ln, flags=re.S)
        n = 1
        for c, w in zip(cels, larg):
            util = 455 * w / tot - 12
            ps = re.findall(r"<w:p[ >].*?</w:p>", c, flags=re.S)
            n = max(n, sum(max(1, -(-len(texto(p)) * largura_letra // util)) for p in ps))
        h += 14.4 + (n - 1) * corpo * 1.2
    return h


ALTURA_LONGA = 420  # pt; acima disso a tabela usa xltabular e pode quebrar


def tabela_dados(b, legenda, rotulo, rot, cit, notas_lx):
    larg = [int(w) for w in re.findall(r'<w:gridCol w:w="(\d+)"/>', b)]
    linhas = re.findall(r"<w:tr[ >].*?</w:tr>", b, flags=re.S)
    assert "<w:tblHeader/>" in linhas[0] and not any("<w:tblHeader/>" in x for x in linhas[1:])
    assert "gridSpan" not in b and "vMerge" not in b
    matriz, jcs = [], []
    for ln in linhas:
        cels = re.findall(r"<w:tc>.*?</w:tc>", ln, flags=re.S)
        assert len(cels) == len(larg), (len(cels), len(larg))
        linha, jl = [], []
        for c in cels:
            ps = re.findall(r"<w:p[ >].*?</w:p>", c, flags=re.S)
            linha.append(" \\newline ".join(para_latex(runs(p), rot, cit) for p in ps))
            j = re.search(r'<w:jc w:val="(\w+)"/>', ps[0])
            jl.append(j.group(1) if j else "left")
        matriz.append(linha)
        jcs.append(jl)
    n = len(larg)
    tot = sum(larg)
    cols = []
    for i, w in enumerate(larg):
        al = alinhamento([jl[i] for jl in jcs[1:]])
        cmd = r"\centering" if al == "center" else r"\raggedright"
        cols.append(rf">{{\hsize={n * w / tot:.3f}\hsize{cmd}\arraybackslash}}X")
    tamanho = r"\footnotesize" if n > 6 else r"\small"
    # \centering no cabeçalho exige \tabularnewline no fim da linha
    cab = " & ".join(r"\centering\textbf{" + x + "}" for x in matriz[0]) + r" \tabularnewline"
    corpo = [" & ".join(ln) + r" \\" for ln in matriz[1:]]
    espec = "{@{}" + "".join(cols) + "@{}}"
    legenda_lx = "\\caption{" + legenda + "}\\label{" + rotulo + "}"
    if altura_estimada(larg, linhas, tamanho) > ALTURA_LONGA:
        s = ["\\begin{tabelaabnt}{" + tamanho + "}",
             "\\begin{xltabular}{\\textwidth}" + espec,
             legenda_lx + "\\\\",
             "\\toprule", cab, "\\midrule", "\\endfirsthead",
             "\\toprule", cab, "\\midrule", "\\endhead",
             "\\bottomrule", "\\endfoot", "\\bottomrule", "\\endlastfoot"]
        s += corpo + ["\\end{xltabular}"] + notas_lx + ["\\end{tabelaabnt}"]
        return s, True
    s = ["\\begin{table}[!htbp]", "\\estilotabela{" + tamanho + "}", legenda_lx,
         "\\begin{tabularx}{\\textwidth}" + espec,
         "\\toprule", cab, "\\midrule"]
    s += corpo + ["\\bottomrule", "\\end{tabularx}"] + notas_lx + ["\\end{table}"]
    return s, False


def imagem(b, rels, media, destino, rotulo):
    rid = re.search(r'<a:blip r:embed="([^"]+)"', b).group(1)
    alvo = rels[rid]
    cx = int(re.search(r'<wp:extent cx="(\d+)"', b).group(1))
    frac = min(cx / (9360 * 635), 1.0)
    nome = rotulo.split(":", 1)[1] + Path(alvo).suffix
    (destino / "figuras" / nome).write_bytes(media["word/" + alvo])
    return f"\\includegraphics[width={frac:.2f}\\textwidth]{{{nome}}}"


def converter(docx, destino):
    z = zipfile.ZipFile(docx)
    doc = z.read("word/document.xml").decode("utf-8")
    rels = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"',
                           z.read("word/_rels/document.xml.rels").decode()))
    media = {n: z.read(n) for n in z.namelist() if n.startswith("word/media/")}
    bib = (destino / "bibliografia.bib").read_text(encoding="utf-8")
    blocos = blocos_do_corpo(doc)
    titulo_doc = texto(blocos[0])
    assert estilo(blocos[0]) == "Ttulo1"
    fim = next(i for i, b in enumerate(blocos) if texto(b) == "REFERÊNCIAS")
    blocos = blocos[1:fim]
    eqs = equacoes_pandoc(docx)
    assert len(eqs) == doc.count("<m:oMath>")
    rot = pre_rotulos(blocos)
    cit = Citacoes(bib)
    (destino / "figuras").mkdir(exist_ok=True)
    for f in (destino / "figuras").glob("*"):
        f.unlink()

    capitulos = {}
    atual = None
    pos_eq = 0
    i = 0
    lista_aberta = False
    depois_de_tabela = False

    def emitir(linhas):
        nonlocal depois_de_tabela
        capitulos[atual].extend(linhas)
        depois_de_tabela = False

    def fechar_lista():
        nonlocal lista_aberta
        if lista_aberta:
            emitir(["\\end{enumerate}", ""])
            lista_aberta = False

    def notas(j):
        """Parágrafos 'Fonte:' e 'Nota:' que seguem a figura ou tabela."""
        saida = []
        while j < len(blocos) and not blocos[j].startswith("<w:tbl"):
            t = texto(blocos[j])
            m = re.match(r"(Fonte|Nota): ", t)
            if not m:
                break
            cmd = "\\fonte" if m.group(1) == "Fonte" else "\\nota"
            saida.append(cmd + "{" + para_latex(runs(blocos[j]), rot, cit,
                                                 cortar_inicio=m.end()) + "}")
            j += 1
        return saida, j

    while i < len(blocos):
        b = blocos[i]
        t = texto(b)
        if not b.startswith("<w:tbl") and estilo(b) == "Ttulo2":
            fechar_lista()
            nivel, num, nome = classificar_titulo(t)
            if nivel == "chapter":
                atual = int(num)
                capitulos[atual] = [f"% Gerado por tcc/gerar_latex.py a partir de {Path(docx).name}.",
                                    "% Edite à vontade; uma nova geração sobrescreve este arquivo.", ""]
                emitir([f"\\chapter{{{TITULOS_CAPITULO[nome]}}}\\label{{sec:{num}}}", ""])
            else:
                lx = para_latex(runs(b), rot, cit, cortar_inicio=len(num) + 1)
                if "\\" in lx:
                    lx = f"\\texorpdfstring{{{lx}}}{{{escapar(nome)}}}"
                emitir([f"\\{nivel}{{{lx}}}\\label{{sec:{num}}}", ""])
            i += 1
            continue
        if b.startswith("<w:tbl"):
            assert "<m:oMath>" in b, "tabela sem legenda"
            fechar_lista()
            corpo, k = tabela_equacoes(b, eqs, pos_eq)
            pos_eq += k
            emitir(corpo + [""])
            i += 1
            continue
        m = CAPTION.match(t)
        if m:
            fechar_lista()
            tipo, n = m.group(1), int(m.group(2))
            legenda = para_latex(runs(b), rot, cit, cortar_inicio=m.end())
            if tipo == "Tabela":
                assert blocos[i + 1].startswith("<w:tbl")
                ns, j = notas(i + 2)
                corpo, longa = tabela_dados(blocos[i + 1], legenda, rot.tab[n], rot, cit, ns)
                emitir(corpo + [""])
                depois_de_tabela = longa
                i = j
                continue
            else:
                rotulo = rot.fig[n]
                if "<w:drawing" in b:
                    img, j0 = b, i + 1
                else:
                    assert "<w:drawing" in blocos[i + 1] and not texto(blocos[i + 1])
                    img, j0 = blocos[i + 1], i + 2
                inc = imagem(img, rels, media, destino, rotulo)
                ns, j = notas(j0)
                # figura com [h] logo depois de xltabular pode passar do pé
                # da página; nesse caso ela vai para o topo ou o pé
                pos = "!tbp" if depois_de_tabela else "!htbp"
                emitir([f"\\begin{{figure}}[{pos}]", "\\centering",
                        "\\caption{" + legenda + "}\\label{" + rotulo + "}", inc]
                       + ns + ["\\end{figure}", ""])
            i = j
            continue
        assert "<w:drawing" not in b, t
        mi = re.match(r"([a-i])\) ", t)
        if mi and atual == 1:
            if not lista_aberta:
                inicio = ord(mi.group(1)) - ord("a") + 1
                op = "label=\\alph*)" + (f", start={inicio}" if inicio > 1 else "")
                emitir([f"\\begin{{enumerate}}[{op}]"])
                lista_aberta = True
            emitir(["  \\item " + para_latex(runs(b), rot, cit, cortar_inicio=mi.end())])
            i += 1
            continue
        fechar_lista()
        assert not re.match(r"(Fonte|Nota): ", t), t
        if t.strip():
            emitir([para_latex(runs(b), rot, cit), ""])
        i += 1
    assert pos_eq == len(eqs)

    (destino / "capitulos").mkdir(exist_ok=True)
    for n, linhas in capitulos.items():
        (destino / "capitulos" / f"{ARQUIVOS[n]}.tex").write_text(
            "\n".join(linhas).rstrip() + "\n", encoding="utf-8")

    chaves = set(re.findall(r"^@\w+\{([^,]+),", bib, flags=re.M))
    resumo = {
        "titulo": titulo_doc,
        "tabelas": len(rot.tab), "figuras": len(rot.fig), "equacoes": len(rot.eq),
        "secoes": len(rot.sec),
        "citadas": sorted(cit.usadas),
        "nao_citadas": sorted(chaves - cit.usadas),
        "citacoes_sem_referencia": sorted(set(cit.ausentes)),
        "rotulos": {"tab": rot.tab, "fig": rot.fig},
    }
    (destino / "capitulos" / "conversao.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    return resumo


def main():
    docx = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "tcc" / "TCC_exo1_exo2.docx"
    destino = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "latex"
    r = converter(docx, destino)
    print(f"{r['tabelas']} tabelas, {r['figuras']} figuras, {r['equacoes']} equações, "
          f"{r['secoes']} seções; {len(r['citadas'])} referências citadas, "
          f"não citadas: {r['nao_citadas']}; citações sem referência: "
          f"{r['citacoes_sem_referencia']}")


if __name__ == "__main__":
    main()
