"""Confere o PDF gerado pelo LaTeX contra o TCC fundido em DOCX.

Uso: python3 tcc/verificar_latex.py [docx] [pdf]

Grava tcc/verificacao_latex.md e sai com código 1 se algum critério falhar.

Critérios:
1. cada parágrafo, título, legenda, fonte e nota do DOCX aparece no PDF, na
   mesma ordem interna de palavras e números; a comparação ignora caixa,
   espaços, hifenização e pontuação, de modo que um número de tabela,
   figura, equação ou seção resolvido de forma diferente do DOCX faz o
   parágrafo falhar;
2. cada célula de tabela tem, no código LaTeX gerado, o mesmo texto da célula
   do DOCX, com os \\ref resolvidos pelo .aux e sem as citações (conferidas
   no critério 1 e no PDF); e o texto de cada célula aparece no PDF depois da
   legenda da sua tabela;
3. as 52 equações estão numeradas de (1) a (52) e cada número aparece no PDF;
4. cada referência da lista do DOCX aparece na lista do PDF;
5. o log não tem referência, citação ou rótulo indefinido, e o PDF não tem "??".

As citações que o biblatex escreve de outra forma por regra da ABNT estão
em DIFERENCAS_ESPERADAS e são listadas no relatório.
"""
import html
import re
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# DOCX -> forma que o biblatex imprime (NBR 10520:2023: até três autores
# são todos citados)
DIFERENCAS_ESPERADAS = {
    "SHEN et al., 2020": "SHEN; FERGUSON; ROSEN, 2020",
}

SAIDA = []


def diga(t=""):
    SAIDA.append(t)


def norm(t):
    t = unicodedata.normalize("NFKC", t).lower()
    return "".join(c for c in t if c.isalnum())


def texto(b):
    return html.unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)", b)))


def texto_pdf(pdf, primeira, ultima):
    """Texto das páginas, sem cabeçalho corrente e número de página."""
    partes = []
    for p in range(primeira, ultima + 1):
        t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), str(pdf), "-"],
                           capture_output=True, text=True, check=True).stdout
        linhas = [x for x in t.split("\n") if x.strip()]
        # cabeçalho corrente e número da página, no topo; só a primeira e a
        # última linha podem ser o número, porque colunas de tabela também
        # saem como linhas só com números
        for k in range(min(4, len(linhas))):
            if linhas[k].strip() == str(p):
                linhas.pop(k)
                break
        if linhas and re.match(r"^(Capítulo \d+\.|Referências$)", linhas[0]) and p != primeira:
            linhas.pop(0)
        partes.append("\n".join(linhas))
    return "\n".join(partes)


def titulo_separado(t, fonte, janela=600, normalizar=None):
    """Título numerado que o pdftotext separou do número: o número pode sair
    junto dos números de equação do bloco anterior ("3B.5" antes de "(36)").
    Aceita o título se o número aparece até janela caracteres antes dele.
    normalizar: a mesma normalização usada para montar fonte (norm, por padrão)."""
    normalizar = normalizar or norm
    m = re.match(r"^(\d[A-C]?(?:\.\d+)+)\s*(\S.{14,})$", t)
    if not m:
        return False
    num, tit = normalizar(m.group(1)), normalizar(m.group(2))
    k = fonte.find(tit)
    while k >= 0:
        if num in fonte[max(0, k - janela):k]:
            return True
        k = fonte.find(tit, k + 1)
    return False


def encontrar(alvo, fonte, min_peca=15, janela=8000, min_lacuna=20):
    """Procura alvo em fonte admitindo interrupções do lado do PDF (cabeçalho,
    figura ou tabela no meio do parágrafo). Uma interrupção menor que
    min_lacuna caracteres indica texto acrescentado e conta como falha.
    Devolve (ok, n_pecas)."""
    pos, resto, pecas = None, alvo, 0
    while resto:
        lo, hi = 0, len(resto)
        inicio = 0 if pos is None else pos
        fim_busca = None if pos is None else pos + janela
        while lo < hi:
            m = (lo + hi + 1) // 2
            if fonte.find(resto[:m], inicio, fim_busca) >= 0:
                lo = m
            else:
                hi = m - 1
        if lo == 0 or (lo < min_peca and lo < len(resto)):
            return False, pecas
        achado = fonte.find(resto[:lo], inicio, fim_busca)
        if pos is not None and achado - pos < min_lacuna:
            return False, pecas
        pos = achado + lo
        resto = resto[lo:]
        pecas += 1
    return True, pecas


def celula_no_pdf(alvo, fonte, inicio, janela=40000):
    """Texto da célula em ordem depois da legenda, admitindo que linhas de
    outras células se intercalem (células de várias linhas)."""
    pos = inicio
    resto = alvo
    while resto:
        lo, hi = 0, len(resto)
        while lo < hi:
            m = (lo + hi + 1) // 2
            if fonte.find(resto[:m], pos, inicio + janela) >= 0:
                lo = m
            else:
                hi = m - 1
        if lo == 0 or (lo < 3 and lo < len(resto)):
            return False
        pos = fonte.find(resto[:lo], pos, inicio + janela) + lo
        resto = resto[lo:]
    return True


CITACAO_DOCX = re.compile(r"\((?:[A-ZÀ-Ý][^()]*?, (?:\d{4}[a-z]?|\[202-\]))\)"
                          r"|(?:\b(?:van der |de )?[A-ZÄÖÜ][\w'äöü-]+(?: et al\.)?) \(\d{4}[a-z]?\)")


def rotulos_aux(pasta):
    tab = {}
    for aux in pasta.rglob("*.aux"):
        for nome, num in re.findall(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", aux.read_text(
                encoding="utf-8", errors="replace")):
            tab[nome] = num
    return tab


def tex_para_texto(t, rot):
    t = re.sub(r"\\eqref\{([^}]+)\}", lambda m: "(" + rot[m.group(1)] + ")", t)
    t = re.sub(r"\\ref\{([^}]+)\}", lambda m: rot[m.group(1)], t)
    t = re.sub(r"\\(?:textcite|Textcite|cite)\{[^}]+\}", "", t)
    t = re.sub(r"\\citecomsemref\{[^}]*\}\{[^}]+\}", "", t)
    t = t.replace(r"\newline", " ").replace(r"\centering", "").replace("~", " ")
    t = t.replace(r"\textasciitilde{}", "~").replace(r"\textbackslash{}", "\\")
    t = re.sub(r"\\text(?:subscript|superscript|it|bf)\{", "{", t)
    t = re.sub(r"\\([&%#_{}$])", r"\1", t)
    assert not re.search(r"\\[a-zA-Z]", t), t
    return t.replace("{", "").replace("}", "")


def celulas_tex(pasta):
    """Células das tabelas no código gerado, na ordem do texto."""
    tabelas = []
    for nome in ["introducao", "fundamentacao", "materiais_metodos", "resultados", "conclusao"]:
        src = (pasta / "capitulos" / f"{nome}.tex").read_text(encoding="utf-8")
        for m in re.finditer(r"\\begin\{(tabularx|xltabular)\}\{\\textwidth\}\{.*?\}\n(.*?)"
                             r"\\end\{\1\}", src, flags=re.S):
            corpo = m.group(2)
            if m.group(1) == "xltabular":
                corpo = corpo.split("\\endfirsthead")[0].split("\\toprule\n", 1)[1] + \
                    corpo.split("\\endlastfoot\n", 1)[1]
            else:
                corpo = corpo.split("\\toprule\n", 1)[1]
            corpo = corpo.replace("\\midrule\n", "").replace("\\bottomrule\n", "")
            linhas = [x for x in re.split(r" \\tabularnewline\n| \\\\\n", corpo) if x.strip()]
            tabelas.append([re.split(r"(?<!\\)&", ln) for ln in linhas])
    return tabelas


def main():
    docx = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "tcc" / "TCC_exo1_exo2.docx"
    pdf = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "latex" / "tese.pdf"
    log = pdf.with_suffix(".log").read_text(encoding="latin-1")
    doc = zipfile.ZipFile(docx).read("word/document.xml").decode("utf-8")
    corpo = doc[doc.index("<w:body>") + 8:]
    blocos = re.findall(r"<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>", corpo, flags=re.S)
    i_ref = next(i for i, b in enumerate(blocos) if texto(b) == "REFERÊNCIAS")

    n_pag = int(re.search(r"Pages:\s+(\d+)", subprocess.run(
        ["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    paginas = [subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), str(pdf), "-"],
                              capture_output=True, text=True).stdout for p in range(1, n_pag + 1)]
    p_cap1 = next(i for i, t in enumerate(paginas, 1) if re.search(r"Capítulo 1\s+Introdução", t))
    p_ref = min(i for i, t in enumerate(paginas, 1)
                if i > p_cap1 and re.match(r"\s*(?:\d+\s*\n)?\s*Referências\s*\n", t))
    corpo_pdf = texto_pdf(pdf, p_cap1, p_ref - 1)
    refs_pdf = texto_pdf(pdf, p_ref, n_pag)
    fonte = norm(corpo_pdf)

    falhas = []
    rot = rotulos_aux(pdf.parent)
    tabelas_tex = celulas_tex(pdf.parent)
    n_tab = 0
    n_cel_tex = 0
    diga("# Verificação do TCC em LaTeX")
    diga()
    diga(f"DOCX: {docx.name}. PDF: {pdf.name}, {n_pag} páginas; capítulos nas páginas "
         f"{p_cap1} a {p_ref - 1}, referências a partir da página {p_ref}.")
    diga()

    # 1 e 2. texto corrido e tabelas
    n_par = n_cel = 0
    interrompidos = []
    usadas = []
    legenda_pos = None
    for b in blocos[1:i_ref]:
        if b.startswith("<w:tbl"):
            if "<m:oMath>" in b:
                continue
            linhas_tex = tabelas_tex[n_tab]
            n_tab += 1
            linhas = re.findall(r"<w:tr[ >].*?</w:tr>", b, flags=re.S)
            if len(linhas) != len(linhas_tex):
                falhas.append(f"tabela {n_tab}: {len(linhas)} linhas no DOCX, {len(linhas_tex)} no LaTeX")
                continue
            for ln, ln_tex in zip(linhas, linhas_tex):
                cels = re.findall(r"<w:tc>.*?</w:tc>", ln, flags=re.S)
                if len(cels) != len(ln_tex):
                    falhas.append(f"tabela {n_tab}: linha com {len(cels)} e {len(ln_tex)} células")
                    continue
                for c, c_tex in zip(cels, ln_tex):
                    t_docx = " ".join(texto(p) for p in re.findall(r"<w:p[ >].*?</w:p>", c, flags=re.S))
                    n_cel_tex += 1
                    if norm(CITACAO_DOCX.sub("", t_docx)) != norm(tex_para_texto(c_tex, rot)):
                        falhas.append(f"célula (LaTeX), tabela {n_tab}: {t_docx[:80]} | {c_tex[:80]}")
                    if not norm(t_docx):
                        continue
                    n_cel += 1
                    if legenda_pos is None or not celula_no_pdf(norm(t_docx), fonte, legenda_pos):
                        falhas.append(f"célula (PDF), tabela {n_tab}: " + t_docx[:120])
            continue
        t = texto(b).strip()
        if not t:
            continue
        for antes, depois in DIFERENCAS_ESPERADAS.items():
            if antes in t:
                t = t.replace(antes, depois)
                usadas.append(antes)
        m = re.match(r"^(Tabela|Figura) (\d+)(?: —|:) ", t)
        if m and m.group(1) == "Tabela":
            # posição da legenda no corpo (a última ocorrência; a primeira
            # pode estar numa remissão), para conferir as células depois dela
            chave = norm(t)[:60]
            legenda_pos = fonte.rfind(chave)
            if legenda_pos < 0:
                legenda_pos = None
        n_par += 1
        ok, pecas = encontrar(norm(t), fonte)
        if not ok and not titulo_separado(t, fonte):
            falhas.append("parágrafo: " + t[:160])
        elif pecas > 1:
            interrompidos.append((pecas, t[:80]))
    diga("## 1. Texto corrido, títulos, legendas, fontes e notas")
    diga()
    diga(f"Elementos conferidos: {n_par}. Encontrados no PDF: "
         f"{n_par - sum(1 for f in falhas if f.startswith('parágrafo'))}.")
    diga(f"Encontrados com interrupção do lado do PDF (cabeçalho, figura ou tabela no meio "
         f"do parágrafo): {len(interrompidos)}.")
    diga("Diferenças esperadas, impostas pelo estilo ABNT do modelo: " +
         ("; ".join(f"'{a}' passa a '{DIFERENCAS_ESPERADAS[a]}'" for a in sorted(set(usadas)))
          or "nenhuma") + ".")
    diga()
    diga("## 2. Células de tabela")
    diga()
    diga(f"Tabelas: {n_tab} no DOCX e {len(tabelas_tex)} no código LaTeX.")
    diga(f"Células comparadas no código LaTeX: {n_cel_tex}; diferentes: "
         f"{sum(1 for f in falhas if f.startswith('célula (LaTeX)'))}.")
    diga(f"Células com texto procuradas no PDF: {n_cel}; não encontradas: "
         f"{sum(1 for f in falhas if f.startswith('célula (PDF)'))}.")
    diga()

    # 3. equações
    nums = [int(n) for b in blocos[1:i_ref] if b.startswith("<w:tbl") and "<m:oMath>" in b
            for n in re.findall(r"<w:t>\((\d+)\)</w:t>", b)]
    faltam = [n for n in nums if f"({n})" not in corpo_pdf]
    if nums != list(range(1, len(nums) + 1)) or faltam:
        falhas.append(f"equações: numeração {nums[:3]}..., ausentes no PDF {faltam}")
    diga("## 3. Equações")
    diga()
    diga(f"Equações no DOCX: {len(nums)}, numeradas de (1) a ({max(nums)}). "
         f"Números ausentes do PDF: {faltam or 'nenhum'}.")
    diga()

    # 4. referências
    refs = [texto(b) for b in blocos[i_ref + 1:] if texto(b).strip()]
    fonte_ref = norm(refs_pdf)
    faltam_ref = [r for r in refs if not encontrar(norm(r), fonte_ref)[0]]
    falhas += ["referência: " + r[:120] for r in faltam_ref]
    diga("## 4. Referências")
    diga()
    diga(f"Referências no DOCX: {len(refs)}. Encontradas no PDF: {len(refs) - len(faltam_ref)}.")
    diga()

    # 5. log
    indef = sorted(set(re.findall(r"(?:Reference|Citation|Label) [`'][^']+' (?:on page \d+ )?undefined",
                                  log)))
    if "There were undefined references" in log or indef:
        falhas.append(f"log: {indef}")
    interrog = "??" in corpo_pdf
    if interrog:
        falhas.append("PDF com '??'")
    diga("## 5. Compilação")
    diga()
    diga(f"Referências ou citações indefinidas no log: {len(indef)}. '??' no PDF: "
         f"{'sim' if interrog else 'não'}.")
    diga()

    diga("## Resultado")
    diga()
    if falhas:
        diga(f"{len(falhas)} falha(s):")
        for f in falhas:
            diga(f"- {f}")
    else:
        diga("Todos os critérios foram atendidos.")
    destino = RAIZ / "tcc" / "verificacao_latex.md"
    destino.write_text("\n".join(SAIDA) + "\n", encoding="utf-8")
    print("\n".join(SAIDA[-(len(falhas) + 3):]))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
