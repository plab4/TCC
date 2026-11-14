#!/usr/bin/env python3
"""
Verificação da versão condensada (tcc/gerar_condensado.py) contra o documento
longo revisado, de que ela foi tirada.

Confere, no conteúdo condensado (revisao_defesa/build_condensado/fundido_condensado.docx):
1. numeração: seções em sequência e hierarquia; tabelas, figuras e equações de 1 a N
   na ordem em que aparecem; toda remissão aponta para algo que existe;
2. proveniência: todo número do texto condensado existe no documento longo;
3. equações, imagens e linhas de tabela iguais às do documento longo;
4. termos que não podem aparecer (etapa dinâmica, MBDyn, apêndice) e travessões;
5. citações e referências: toda citação tem referência e toda referência é citada;
e, no DOCX entregue (formato FT):
6. termos proibidos também nas páginas iniciais (resumo e abstract);
7. número de páginas, pelo LibreOffice, dentro do limite pedido pelo autor;
8. arquivos de origem intactos.

Grava revisao_defesa/build_condensado/verificacao_condensado.md e sai com erro se
algum critério falhar.

Uso (na raiz do repositório):  python3 tcc/verificar_condensado.py [--sem-docx]
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_tcc_fundido as g  # noqa: E402
import gerar_condensado as gc  # noqa: E402
import condensado_defesa as cd  # noqa: E402
from nomes import FUNDIDO, MODELO_FT, ORIGINAL  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
LIMITE_PAGINAS = 80   # pedido do autor (14/11): enxugar para perto de 78, com todas as figuras
L, FALHAS = [], []
NUMERO = re.compile(r"\d+(?:\.\d{3})+(?:,\d+)?|\d+,\d+|\d+")
HASHES = {ORIGINAL: "7e188436c05ff859"}


def diga(s=""):
    L.append(s)


def corpo(caminho):
    with zipfile.ZipFile(caminho) as z:
        assert z.testzip() is None
        doc = z.read("word/document.xml").decode("utf-8")
        midia = {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith("word/media/")}
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    b0 = doc.index("<w:body>") + len("<w:body>")
    return g.blocos(doc[b0:doc.rindex("<w:sectPr")]), midia, rels, doc


def sem_remissoes(t):
    """Texto sem os números de seção, tabela, figura do documento e equação."""
    t = re.sub(rf"([Ss]eç(?:ão|ões)\s+){gc.LISTA_SEC}", r"\1", t)
    t = re.sub(r"\b(Tabelas?) \d+(?:, \d+)*(?: (?:e|a) \d+)?", r"\1", t)
    t = re.sub(r"\b(Equaç(?:ão|ões)) \(\d+\)(?:(?:, | e | a )\(\d+\))*", r"\1", t)

    def fig(m):
        return m.group(0) if gc._figura_de_patente(int(m.group(2)), m.group(4), m.group(3)) else m.group(1)
    return re.sub(r"\b(Figuras?) (\d+)((?:, \d+)*(?: (?:e|a) \d+)?)(?=(.{0,14}))", fig, t)


def numeros(t):
    return set(NUMERO.findall(sem_remissoes(t)))


def mapa_do_corte(registro, res_longo):
    """revisao_defesa/O_que_saiu_e_o_que_ficou.md: seções, tabelas, figuras e equações do
    documento longo, com o número novo de cada uma ou a indicação de que saiu."""
    longa = registro["numeracao_longa"]
    novo = {"T": registro["tabelas"], "F": registro["figuras"], "E": registro["equacoes"]}
    legendas, secoes = {"T": {}, "F": {}}, []
    for x in res_longo:
        if x.startswith("<w:tbl"):
            continue
        t = g.texto(x)
        m = re.match(r"(Tabela|Figura) (\d+)(?: —|:) (.*)", t)
        if m:
            legendas[m.group(1)[0]][int(m.group(2))] = m.group(3).strip()
        elif gc.estilo(x) == "Ttulo2" and gc.TITULO_NUM.match(t):
            secoes.append(gc.TITULO_NUM.match(t).groups())
    sec_nova = registro["secoes"]
    linhas = ["# O que saiu e o que ficou na versão condensada", "",
              "Gerado por `tcc/verificar_condensado.py`. A coluna da esquerda traz a numeração do documento "
              "longo (tcc/" + FUNDIDO + "); a da direita, a da versão condensada.", "",
              "## Seções", "", "| Documento longo | Versão condensada |", "|---|---|"]
    for num, titulo in secoes:
        if num in sec_nova:
            destino = f"{sec_nova[num]} (título mantido)"
        elif cd.ALIAS.get(num):
            destino = f"conteúdo condensado em {sec_nova[cd.ALIAS[num]]}"
        else:
            destino = "saiu"
        linhas.append(f"| {num} {titulo} | {destino} |")
    linhas += ["", "## Apêndice", "", "O Apêndice A (robustez da identificação e ajuste de forma no "
               "exoesqueleto 2) saiu inteiro, com as Tabelas 31 a 33, a Figura 20 e as Equações (68) e (69)."]
    for tipo, nome in (("T", "Tabelas"), ("F", "Figuras")):
        linhas += ["", f"## {nome}", "", "| Documento longo | Versão condensada | Legenda |", "|---|---|---|"]
        por_numero = {v: k for k, v in longa[tipo].items()}
        for n in sorted(por_numero):
            k = por_numero[n]
            linhas.append(f"| {n} | {novo[tipo].get(k, 'saiu')} | {legendas[tipo].get(n, '')[:110]} |")
    por_numero = {v: k for k, v in longa["E"].items()}
    ficam = [f"({n}) → ({novo['E'][por_numero[n]]})" for n in sorted(por_numero) if por_numero[n] in novo["E"]]
    saem = [f"({n})" for n in sorted(por_numero) if por_numero[n] not in novo["E"]]
    linhas += ["", "## Equações", "", "Mantidas, com o número novo: " + ", ".join(ficam) + ".", "",
               "Retiradas: " + ", ".join(saem) + ".", "",
               "## Referências", "", "Saíram da lista, por não serem mais citadas no texto: "
               + ", ".join(registro["referencias_retiradas"]) + " (chaves de latex/bibliografia.bib).", ""]
    (gc.SAIDA / "O_que_saiu_e_o_que_ficou.md").write_text("\n".join(linhas), encoding="utf-8")


def main():
    com_docx = "--sem-docx" not in sys.argv[1:]
    blocos, midia, rels, doc = corpo(gc.FUNDIDO_COND)
    registro = json.loads((gc.BUILD / "registro_condensado.json").read_text(encoding="utf-8"))
    longo, num_longo, ctx = gc.base_marcada()
    res_longo = [x for _, x in ctx["resolvidos"]]
    textos = [g.texto(b) for b in blocos]
    i_ref = textos.index("REFERÊNCIAS")
    mapa_do_corte(registro, res_longo)
    diga("# Verificação da versão condensada")
    diga()
    diga(f"Conteúdo: {gc.FUNDIDO_COND.relative_to(RAIZ)}, {len(blocos)} blocos, contra o documento longo "
         f"revisado, {len(res_longo)} blocos.")
    diga()

    # 1. numeração
    secoes, tab, fig, eqs = [], [], [], []
    for b, t in zip(blocos[:i_ref], textos[:i_ref]):
        if b.startswith("<w:tbl"):
            if "<m:oMath" in b:
                eqs += [int(n) for n in re.findall(r"<w:t>\((\d+)\)</w:t>", b)]
            continue
        if gc.estilo(b) == "Ttulo2":
            secoes.append(gc.TITULO_NUM.match(t).group(1))
            continue
        m = re.match(r"(Tabela|Figura) (\d+)(?: —|:) ", t)
        if m:
            (tab if m.group(1) == "Tabela" else fig).append(int(m.group(2)))
    for nome, lista in (("tabelas", tab), ("figuras", fig), ("equações", eqs)):
        if lista != list(range(1, len(lista) + 1)):
            FALHAS.append(f"{nome} fora de sequência: {lista}")
    conta, ordem_ok = {}, True
    for s in secoes:
        pai, _, k = s.rpartition(".")
        conta[pai] = conta.get(pai, 0) + 1
        if int(k) != conta[pai] or (pai and pai not in secoes):
            ordem_ok = False
    if not ordem_ok:
        FALHAS.append(f"seções fora de sequência: {secoes}")
    soltas = []
    for b, t in zip(blocos[:i_ref], textos[:i_ref]):
        for p in g.PARAGRAFO.findall(b):
            tp = g.texto(p)
            for m in re.finditer(rf"[Ss]eç(?:ão|ões)\s+({gc.LISTA_SEC})", tp):
                soltas += [("seção", n) for n in re.findall(gc.NUM_SEC, m.group(1)) if n not in secoes]
            for m in re.finditer(r"\bTabelas? (\d+(?:, \d+)*(?: (?:e|a) \d+)?)", tp):
                soltas += [("tabela", n) for n in re.findall(r"\d+", m.group(1)) if int(n) not in tab]
            for m in re.finditer(r"\bEquaç(?:ão|ões) (\(\d+\)(?:(?:, | e | a )\(\d+\))*)", tp):
                soltas += [("equação", n) for n in re.findall(r"\d+", m.group(1)) if int(n) not in eqs]
            for m in re.finditer(r"\b(Figuras?) (\d+)((?:, \d+)*(?: (?:e|a) \d+)?)(?=(.{0,14}))", tp):
                if not gc._figura_de_patente(int(m.group(2)), m.group(4), m.group(3)):
                    soltas += [("figura", n) for n in re.findall(r"\d+", m.group(2) + m.group(3))
                               if int(n) not in fig]
    if soltas:
        FALHAS.append(f"remissões sem destino: {soltas[:10]}")
    citados = " ".join(textos[:i_ref])
    sem_cit = [f"Tabela {n}" for n in tab if not re.search(rf"\bTabelas? (?:\d+(?:, | e | a ))*{n}\b", re.sub(
        r"(?m)^Tabela \d+(?: —|:)", "", "\n".join(textos[:i_ref])))]
    sem_cit += [f"Figura {n}" for n in fig if len(re.findall(rf"\bFiguras? (?:\d+(?:, | e | a ))*{n}(?!\d)", citados)) < 2]
    if sem_cit:
        FALHAS.append(f"tabelas ou figuras sem chamada no texto: {sem_cit}")
    diga("## 1. Numeração e remissões")
    diga()
    diga(f"Títulos numerados: {len(secoes)}, em sequência dentro de cada seção. Tabelas: {len(tab)}; figuras: "
         f"{len(fig)}; equações: {len(eqs)}; todas de 1 a N na ordem em que aparecem. Remissões a seção, "
         f"tabela, figura ou equação sem destino: {len(soltas)}. Tabelas ou figuras sem chamada no texto: "
         f"{len(sem_cit)}.")
    diga()

    # 2. proveniência dos números
    base = set()
    for x in res_longo:
        for p in g.PARAGRAFO.findall(x):
            base |= numeros(g.texto(p))
    novos, total = [], 0
    for b, r in zip(blocos[:i_ref], registro["blocos"][:i_ref]):
        if gc.estilo(b) == "Ttulo2" and not b.startswith("<w:tbl"):
            continue
        for p in g.PARAGRAFO.findall(b):
            t = g.texto(p)
            if re.fullmatch(r"\(\d+\)", t):
                continue
            t = re.sub(r"^(Tabela|Figura) \d+(?: —|:) ", "", t)
            ns = numeros(t)
            total += len(ns)
            novos += [(n, r["modo"], t[:70]) for n in ns if n not in base]
    if novos:
        FALHAS.append(f"números que não estão no documento longo: {novos[:12]}")
    diga("## 2. Proveniência dos números")
    diga()
    diga(f"Números distintos por parágrafo conferidos: {total}. Números do texto condensado que não existem no "
         f"documento longo: {len(novos)}. Os números de seção, tabela, figura e equação ficam fora dessa conta, "
         "porque são refeitos pela montagem e conferidos no item 1.")
    diga()

    # 3. equações, imagens e tabelas
    with zipfile.ZipFile(RAIZ / "tcc" / FUNDIDO) as z:
        doc_longo = z.read("word/document.xml").decode("utf-8")
        midia_longa = {hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith("word/media/")}
    om = lambda x: set(re.findall(r"<m:oMathPara>.*?</m:oMathPara>", x, re.S))      # noqa: E731
    eq_fora = om(doc) - om(doc_longo)
    usadas = set(re.findall(r'r:embed="([^"]+)"', "".join(blocos)))
    alvo = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
    img_fora = [r for r in usadas if midia.get("word/" + alvo[r]) not in midia_longa]
    orfas = [n for n in midia if n[5:] not in alvo.values()]

    def linhas(x):
        saida = set()
        for tb in re.findall(r"<w:tbl>.*?</w:tbl>", x, re.S):
            if "<m:oMath" in tb or "@@OMML" in tb:
                continue
            for ln in re.findall(r"<w:tr[ >].*?</w:tr>", tb, re.S):
                saida.add(sem_remissoes(" | ".join(g.texto(c) for c in re.findall(r"<w:tc>.*?</w:tc>", ln, re.S))))
        return saida
    # as tabelas remontadas no formato padrão (modo T) mudam cabeçalho, ordem ou colunas; nelas, cada
    # número das células tem de estar na tabela de origem do documento longo
    base_linhas = linhas("".join(res_longo))
    lin_fora, remontadas = set(), []
    for b, r in zip(blocos[:i_ref], registro["blocos"][:i_ref]):
        if not b.startswith("<w:tbl"):
            continue
        if r["modo"] == "T":
            origem = set().union(*(numeros(g.texto(q)) for q in g.PARAGRAFO.findall(res_longo[r["indice"]])))
            fora = sorted({n for q in g.PARAGRAFO.findall(b) for n in numeros(g.texto(q))} - origem)
            remontadas.append((r["indice"], fora))
            if fora:
                FALHAS.append(f"tabela remontada (bloco {r['indice']}) com números fora da tabela de origem: {fora[:8]}")
            continue
        lin_fora |= linhas(b) - base_linhas
    if eq_fora or img_fora or lin_fora:
        FALHAS.append(f"equações ({len(eq_fora)}), imagens ({len(img_fora)}) ou linhas de tabela "
                      f"({len(lin_fora)}) que não estão no documento longo: {list(lin_fora)[:3]}")
    diga("## 3. Equações, figuras e tabelas")
    diga()
    diga(f"Equações (OMML) do condensado: {doc.count('<m:oMathPara>')}, todas idênticas, byte a byte, às do "
         f"documento longo: "
         f"{not eq_fora}. Imagens usadas: {len(usadas)}, todas idênticas às do documento longo: {not img_fora}; "
         f"imagens sem uso deixadas no pacote: {len(orfas)}. Linhas de tabela do condensado que não estão no "
         f"documento longo (a menos da numeração): {len(lin_fora)}. Tabelas remontadas no formato padrão: "
         f"{len(remontadas)}, todas com os números da tabela de origem: {not any(f for _, f in remontadas)}.")
    diga()

    # 4. termos proibidos e travessões
    diga("## 4. Termos retirados e travessões")
    diga()
    achados = []
    for t in textos[:i_ref]:
        achados += [(termo, t[:70]) for termo in cd.PROIBIDOS if termo.lower() in t.lower()]
    trav = []
    for t in textos[:i_ref]:
        s = re.sub(r"^(Tabela|Figura) \d+ — ", "", t)
        trav += [(c, s[max(0, s.index(c) - 30):s.index(c) + 30]) for c in ("—", "–") if c in s]
    if achados or trav:
        FALHAS.append(f"termos proibidos {achados[:5]} ou travessões {trav[:5]}")
    diga(f"Ocorrências de {', '.join(cd.PROIBIDOS)} no corpo: {len(achados)}. Travessões e meias-riscas no "
         f"corpo, fora do separador das legendas das tabelas e figuras do texto original: {len(trav)}.")
    diga()

    # 5. citações e referências
    conv = json.loads((gc.BUILD / "latex" / "capitulos" / "conversao.json").read_text(encoding="utf-8"))
    n_refs = len(blocos) - i_ref - 1
    if conv["nao_citadas"] or conv["citacoes_sem_referencia"] or len(conv["citadas"]) != n_refs:
        FALHAS.append(f"citações e referências: {conv['nao_citadas']} {conv['citacoes_sem_referencia']} "
                      f"{len(conv['citadas'])} x {n_refs}")
    diga("## 5. Citações e referências")
    diga()
    diga(f"Referências na lista: {n_refs}; citadas no texto: {len(conv['citadas'])}; referências não citadas: "
         f"{len(conv['nao_citadas'])}; citações sem referência: {len(conv['citacoes_sem_referencia'])}. "
         f"Referências do documento longo que saíram, por não serem mais citadas: "
         f"{len(registro['referencias_retiradas'])} ({', '.join(registro['referencias_retiradas'])}).")
    diga()

    # composição
    modos = {}
    for r in registro["blocos"][:i_ref]:
        modos[r["modo"]] = modos.get(r["modo"], 0) + 1
    diga("## Composição")
    diga()
    diga(f"Blocos do corpo: {i_ref}. Mantidos sem alteração: {modos.get('K', 0)}; mantidos com trechos trocados "
         f"ou cortados: {modos.get('E', 0)}; legendas e notas reescritas: {modos.get('R', 0)}; tabelas com "
         f"linhas retiradas: {modos.get('L', 0)}; parágrafos novos, que condensam os do documento longo: "
         f"{modos.get('P', 0)}; títulos novos: {modos.get('H', 0)}; tabelas remontadas no formato padrão: "
         f"{modos.get('T', 0)}; notas novas: {modos.get('N', 0)}.")
    diga()

    # 6 e 7. DOCX entregue
    if com_docx:
        with zipfile.ZipFile(gc.DOCX_FT) as z:
            assert z.testzip() is None
            xft = z.read("word/document.xml").decode("utf-8")
        tft = " ".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", xft))
        ruins = [t for t in cd.PROIBIDOS + ("dynamic steps",) if t.lower() in tft.lower()]
        if ruins:
            FALHAS.append(f"termos proibidos no DOCX entregue: {ruins}")
        n_titulo = tft.count(cd.TITULO)
        if cd.TITULO_LONGO in tft or n_titulo < 2:
            FALHAS.append(f"título: {n_titulo} ocorrências do novo; o antigo ainda aparece: {cd.TITULO_LONGO in tft}")
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, str(gc.DOCX_FT)],
                           check=True, capture_output=True, timeout=600)
            info = subprocess.run(["pdfinfo", str(Path(tmp) / (gc.DOCX_FT.stem + ".pdf"))],
                                  capture_output=True, text=True).stdout
        paginas = int(re.search(r"Pages:\s+(\d+)", info).group(1))
        pdf = gc.SAIDA / f"{gc.NOME}.pdf"
        pag_pdf = int(re.search(r"Pages:\s+(\d+)", subprocess.run(
            ["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
        if paginas > LIMITE_PAGINAS:
            FALHAS.append(f"o DOCX tem {paginas} páginas, acima do limite de {LIMITE_PAGINAS}")
        diga("## 6. DOCX entregue")
        diga()
        diga(f"Arquivo: {gc.DOCX_FT.relative_to(RAIZ)}. Páginas, da capa ao fim, na conversão pelo LibreOffice: "
             f"{paginas} (limite pedido: {LIMITE_PAGINAS}); o PDF do LaTeX tem {pag_pdf}. Termos retirados no "
             f"texto inteiro, incluídos o resumo e o abstract: {ruins or 'nenhum'}. Título \"{cd.TITULO}\" na "
             f"capa e na folha de rosto: {n_titulo} ocorrências; título antigo: nenhuma. Equações editáveis: "
             f"{xft.count('<m:oMathPara>')}; figuras: {xft.count('<w:drawing>')}.")
        diga()

    # 8. origem
    diga("## Arquivos de origem")
    diga()
    for nome in (ORIGINAL, FUNDIDO, MODELO_FT):
        h = hashlib.sha256((RAIZ / "tcc" / nome).read_bytes()).hexdigest()
        if nome in HASHES and not h.startswith(HASHES[nome]):
            FALHAS.append(f"{nome} foi alterado")
        diga(f"- tcc/{nome}: sha256 {h[:16]}")
    diga()
    diga("## Resultado")
    diga()
    if FALHAS:
        diga(f"{len(FALHAS)} falha(s):")
        for f in FALHAS:
            diga(f"- {f}")
    else:
        diga("Todos os critérios foram atendidos.")
    (gc.BUILD / "verificacao_condensado.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[-(len(FALHAS) + 3):]))
    sys.exit(1 if FALHAS else 0)


if __name__ == "__main__":
    main()
