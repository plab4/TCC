"""Confere o DOCX no formato do modelo contra o PDF do LaTeX e o DOCX fundido.

Uso: python3 tcc/verificar_docx_modelo.py [docx_modelo] [pdf_latex] [docx_fundido]

Grava tcc/verificacao_docx_modelo.md e sai com código 1 se algum critério
falhar. A comparação de texto distingue maiúsculas de minúsculas, para que
uma citação em caixa diferente da do LaTeX conte como falha.

Critérios:
1. capa, folha de rosto e resumo têm o mesmo texto das páginas do LaTeX;
2. cada parágrafo, título, legenda, item, fonte e nota do corpo aparece no
   texto do PDF do LaTeX;
3. cada célula de tabela tem o texto da célula do DOCX fundido (sem as
   citações, cuja forma mudou) e aparece no PDF do LaTeX depois da legenda;
4. as 52 equações têm a mesma OMML do DOCX fundido, numeradas de (1) a (52);
5. as 12 figuras são os mesmos arquivos de imagem do DOCX fundido;
6. cada referência aparece na lista de referências do PDF do LaTeX;
7. sumário e listas têm todas as entradas, com número de página;
8. as fontes Linux Libertine O estão embutidas.
"""
import html
import re
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verificar_latex as vl  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = []


def diga(t=""):
    SAIDA.append(t)


def norm(t):
    t = unicodedata.normalize("NFKC", t)
    return "".join(c for c in t if c.isalnum())


def texto(b):
    return html.unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)", b))).replace("​", "")


def blocos(xml):
    corpo = xml[xml.index("<w:body>") + 8:]
    return re.findall(r"<w:p[ >].*?</w:p>|<w:p/>|<w:tbl>.*?</w:tbl>", corpo, flags=re.S)


CIT_DOCX = re.compile(r"\((?:[A-ZÀ-Ý][^()]*?, (?:\d{4}[a-z]?|\[202-\]))\)"
                      r"|(?:\b(?:[Vv]an der |[Dd]e )?[A-ZÄÖÜ][\w'äöü-]+(?: et al\.)?) \(\d{4}[a-z]?\)")
CIT_NOVA = re.compile(r"\((?:[A-Za-zÀ-ÿ][^()]*?, (?:\d{4}[a-z]?|\[202-\]))\)")


def main():
    novo = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "tcc" / "TCC_modelo_FT.docx"
    pdf = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "latex" / "tese.pdf"
    fundido = Path(sys.argv[3]) if len(sys.argv) > 3 else RAIZ / "tcc" / "TCC_exo1_exo2.docx"
    zn, zf = zipfile.ZipFile(novo), zipfile.ZipFile(fundido)
    bn = blocos(zn.read("word/document.xml").decode("utf-8"))
    bf = blocos(zf.read("word/document.xml").decode("utf-8"))
    falhas = []

    n_pag = int(re.search(r"Pages:\s+(\d+)", subprocess.run(
        ["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    paginas = [subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), str(pdf), "-"],
                              capture_output=True, text=True).stdout for p in range(1, n_pag + 1)]
    p_cap1 = next(i for i, t in enumerate(paginas, 1) if re.search(r"Capítulo 1\s+Introdução", t))
    p_ref = min(i for i, t in enumerate(paginas, 1)
                if i > p_cap1 and re.match(r"\s*(?:\d+\s*\n)?\s*Referências\s*\n", t))
    # pré-textuais do PDF: as páginas antes da Lista de Figuras
    p_listas = next(i for i, t in enumerate(paginas, 1) if t.lstrip().startswith("Lista de Figuras"))
    fonte_pre = norm(" ".join(paginas[:p_listas - 1]))
    corpo_pdf = vl.texto_pdf(pdf, p_cap1, p_ref - 1)
    fonte = norm(corpo_pdf)
    fonte_ref = norm(vl.texto_pdf(pdf, p_ref, n_pag))

    diga("# Verificação do DOCX no formato do modelo")
    diga()
    diga(f"DOCX: {novo.name}. Referência de formato e texto: {pdf.name} ({n_pag} páginas). "
         f"Conteúdo de origem: {fundido.name}.")
    diga()

    # divisão do DOCX novo: pré-textuais até o primeiro "Capítulo 1"
    i_cap1 = next(i for i, b in enumerate(bn) if norm(texto(b)).startswith("Capítulo1Introdução"))
    i_ref = max(i for i, b in enumerate(bn) if texto(b).strip() == "Referências")
    pre = [texto(b) for b in bn[:i_cap1]]
    i_resumo_fim = next(i for i, t in enumerate(pre) if t.strip() == "Lista de Figuras")

    # 1. pré-textuais
    faltam = [t for t in pre[:i_resumo_fim] if t.strip() and norm(t) not in fonte_pre]
    falhas += ["pré-textual: " + t[:100] for t in faltam]
    diga("## 1. Capa, folha de rosto, folha de aprovação e resumo")
    diga()
    diga(f"Parágrafos conferidos: {sum(1 for t in pre[:i_resumo_fim] if t.strip())}; "
         f"ausentes do PDF do LaTeX: {len(faltam)}.")
    diga()

    # 2 a 5. corpo
    tabs_n = [b for b in bn[i_cap1:i_ref] if b.startswith("<w:tbl")]
    tabs_f = [b for b in bf if b.startswith("<w:tbl")]
    eq_n = [b for b in tabs_n if "<m:oMath>" in b]
    eq_f = [b for b in tabs_f if "<m:oMath>" in b]
    dados_n = [b for b in tabs_n if "<m:oMath>" not in b]
    dados_f = [b for b in tabs_f if "<m:oMath>" not in b]
    n_par = 0
    legenda_pos = None
    i_tab = 0
    n_cel = 0
    for b in bn[i_cap1:i_ref]:
        if b.startswith("<w:tbl"):
            if "<m:oMath>" in b:
                continue
            cel_n = re.findall(r"<w:tc>.*?</w:tc>", b, flags=re.S)
            cel_f = re.findall(r"<w:tc>.*?</w:tc>", dados_f[i_tab], flags=re.S)
            i_tab += 1
            if len(cel_n) != len(cel_f):
                falhas.append(f"tabela {i_tab}: {len(cel_n)} células, no DOCX fundido {len(cel_f)}")
                continue
            for cn, cf in zip(cel_n, cel_f):
                tn = " ".join(texto(p) for p in re.findall(r"<w:p[ >].*?</w:p>", cn, flags=re.S))
                tf = " ".join(texto(p) for p in re.findall(r"<w:p[ >].*?</w:p>", cf, flags=re.S))
                n_cel += 1
                if norm(CIT_NOVA.sub("", tn)) != norm(CIT_DOCX.sub("", tf)):
                    falhas.append(f"célula, tabela {i_tab}: '{tn[:60]}' x '{tf[:60]}'")
                if norm(tn) and (legenda_pos is None or not vl.celula_no_pdf(norm(tn), fonte, legenda_pos)):
                    falhas.append(f"célula (PDF), tabela {i_tab}: {tn[:80]}")
            continue
        t = texto(b).strip()
        if not t:
            continue
        n_par += 1
        m = re.match(r"^Tabela (\d+): ", t)
        if m:
            legenda_pos = fonte.rfind(norm(t)[:60])
            legenda_pos = None if legenda_pos < 0 else legenda_pos
        ok, _ = vl.encontrar(norm(t), fonte)
        if not ok and not vl.titulo_separado(t, fonte, normalizar=norm):
            falhas.append("parágrafo: " + t[:140])
    diga("## 2. Corpo do texto")
    diga()
    diga(f"Parágrafos, títulos, legendas, itens, fontes e notas conferidos: {n_par}; "
         f"ausentes do PDF do LaTeX: {sum(1 for f in falhas if f.startswith('parágrafo'))}.")
    diga()
    diga("## 3. Tabelas")
    diga()
    diga(f"Tabelas: {len(dados_n)} no DOCX novo e {len(dados_f)} no DOCX fundido. Células: {n_cel}; "
         f"diferentes do DOCX fundido: {sum(1 for f in falhas if f.startswith('célula,'))}; "
         f"ausentes do PDF do LaTeX: {sum(1 for f in falhas if f.startswith('célula (PDF)'))}.")
    if len(dados_n) != len(dados_f):
        falhas.append("número de tabelas")
    diga()

    # 4. equações
    def omml(b):
        return [re.sub(r'<w:sz(?:Cs)? w:val="\d+"/>', "", m)
                for m in re.findall(r"<m:oMathPara>.*?</m:oMathPara>", b, flags=re.S)]
    om_n = [o for b in eq_n for o in omml(b)]
    om_f = [o for b in eq_f for o in omml(b)]
    nums = [int(n) for b in eq_n for n in re.findall(r"<w:t[^>]*>\((\d+)\)</w:t>", b)]
    iguais = sum(1 for a, b_ in zip(om_n, om_f) if a == b_)
    if len(om_n) != len(om_f) or iguais != len(om_f) or nums != list(range(1, len(om_f) + 1)):
        falhas.append(f"equações: {len(om_n)} x {len(om_f)}, iguais {iguais}, numeração {nums[:3]}...")
    diga("## 4. Equações")
    diga()
    diga(f"Equações: {len(om_n)} no DOCX novo e {len(om_f)} no fundido; OMML idêntica: {iguais}; "
         f"numeração de (1) a ({max(nums) if nums else 0}).")
    diga()

    # 5. figuras
    def imagens(z, xml):
        rels = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', z.read(
            "word/_rels/document.xml.rels").decode()))
        return [z.read("word/" + rels[r]) for r in re.findall(r'<a:blip r:embed="([^"]+)"', xml)]
    xml_n = zn.read("word/document.xml").decode("utf-8")
    xml_f = zf.read("word/document.xml").decode("utf-8")
    img_n = imagens(zn, xml_n)[1:]   # a primeira é o logotipo da capa
    img_f = imagens(zf, xml_f)
    if img_n != img_f:
        falhas.append(f"figuras: {len(img_n)} x {len(img_f)}")
    diga("## 5. Figuras")
    diga()
    diga(f"Figuras: {len(img_n)} no DOCX novo e {len(img_f)} no fundido; mesmos arquivos e ordem: "
         f"{'sim' if img_n == img_f else 'não'}.")
    diga()

    # 6. referências
    refs = [texto(b) for b in bn[i_ref + 1:] if texto(b).strip()]
    faltam_ref = [r for r in refs if not vl.encontrar(norm(r), fonte_ref)[0]]
    falhas += ["referência: " + r[:100] for r in faltam_ref]
    diga("## 6. Referências")
    diga()
    diga(f"Referências: {len(refs)}; ausentes da lista do PDF do LaTeX: {len(faltam_ref)}.")
    diga()

    # 7. sumário e listas
    def entradas(estilos):
        return [texto(b) for b in bn[:i_cap1]
                if re.search(r'<w:pStyle w:val="(' + estilos + r')"/>', b)]
    sumario = entradas("Sumrio1|Sumrio2|Sumrio3")
    listas = entradas("ndicedeilustraes")
    sem_pag = [t for t in sumario + listas if not re.search(r"\d+$", t.strip())]
    # página de cada entrada: campo PAGEREF para um marcador existente, e o
    # Word não atualiza os campos sozinho ao abrir (recalcularia as listas
    # antes de paginar, com página 1 em todas as entradas)
    blocos_ent = [b for b in bn[:i_cap1]
                  if re.search(r'<w:pStyle w:val="(Sumrio[123]|ndicedeilustraes)"/>', b)]
    marcadores = set(re.findall(r'<w:bookmarkStart [^>]*w:name="([^"]+)"', xml_n))
    alvos = [re.findall(r"PAGEREF (\S+) \\h", b) for b in blocos_ent]
    sem_pageref = sum(1 for a in alvos if len(a) != 1 or a[0] not in marcadores)
    atualiza = "updateFields" in zn.read("word/settings.xml").decode()
    if sem_pageref or atualiza:
        falhas.append(f"entradas sem PAGEREF válido: {sem_pageref}; atualização ao abrir: {atualiza}")
    titulos = sum(1 for b in bn[i_cap1:] if re.search(r'<w:pStyle w:val="Ttulo[123]"/>', b))
    n_fig = len(re.findall(r'SEQ Figura', xml_n))
    n_tab = len(re.findall(r'SEQ Tabela', xml_n))
    if len(sumario) != titulos or len(listas) != n_fig + n_tab or sem_pag:
        falhas.append(f"sumário {len(sumario)}/{titulos}, listas {len(listas)}/{n_fig + n_tab}, "
                      f"sem página {len(sem_pag)}")
    diga("## 7. Sumário e listas")
    diga()
    diga(f"Entradas do sumário: {len(sumario)} (títulos no corpo: {titulos}). Entradas das listas: "
         f"{len(listas)} (legendas: {n_fig} figuras e {n_tab} tabelas). Sem número de página: "
         f"{len(sem_pag)}. Entradas sem PAGEREF para um marcador existente: {sem_pageref}. "
         f"Atualização dos campos ao abrir: {'sim' if atualiza else 'não'}.")
    diga()

    # 8. fontes
    ft = zn.read("word/fontTable.xml").decode()
    emb = re.findall(r'<w:font w:name="([^"]+)">.*?</w:font>', ft, flags=re.S)
    vari = re.findall(r"<w:embed(Regular|Bold|Italic|BoldItalic) ", ft)
    if len(vari) < 4 or "Linux Libertine O" not in emb:
        falhas.append("fontes embutidas")
    diga("## 8. Fontes")
    diga()
    diga(f"Famílias declaradas: {', '.join(emb)}. Variantes embutidas: {len(vari)}.")
    diga()

    diga("## Resultado")
    diga()
    if falhas:
        diga(f"{len(falhas)} falha(s):")
        for f in falhas:
            diga(f"- {f}")
    else:
        diga("Todos os critérios foram atendidos.")
    (RAIZ / "tcc" / "verificacao_docx_modelo.md").write_text("\n".join(SAIDA) + "\n", encoding="utf-8")
    print("\n".join(SAIDA[-(len(falhas) + 3):]))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
