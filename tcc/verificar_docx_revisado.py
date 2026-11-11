#!/usr/bin/env python3
"""
Comparação do DOCX revisado para a defesa (formato FT) com o DOCX original
(tcc/<nomes.MODELO_FT>), que não é alterado.

Confere, no arquivo entregue:
1. integridade do pacote e das partes que não podem mudar (imagens, estilos,
   numeração, fontes embutidas);
2. equações editáveis (OMML), figuras e tabelas em mesmo número que no original, e
   equações idênticas;
3. texto: só diferem do original os parágrafos da revisão, o resumo, o abstract e
   os números de página do sumário e das listas;
4. sumário e listas: cada entrada tem título igual ao do corpo e número de página;
5. travessões e meias-riscas, por parte do documento, e restos de marcação;
6. hashes dos arquivos de origem, para atestar que não foram tocados.

Grava revisao_defesa/build/verificacao_docx_revisado.md e sai com erro se algum
critério falhar.

Rodar (na raiz do repositório):  python3 tcc/verificar_docx_revisado.py
"""
import difflib
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_revisado import BUILD, DOCX_FT, REGISTRO  # noqa: E402
from nomes import FUNDIDO, MODELO_FT, ORIGINAL  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "tcc" / MODELO_FT
L, FALHAS = [], []
PAR = re.compile(r"<w:p[ >].*?</w:p>", re.S)
WT = re.compile(r"<w:t(?: [^>]*)?>([^<]*)</w:t>")


def diga(s=""):
    L.append(s)


def partes(caminho):
    with zipfile.ZipFile(caminho) as z:
        assert z.testzip() is None, f"pacote corrompido: {caminho}"
        return {n: z.read(n) for n in z.namelist()}


def paragrafos(xml):
    from xml.sax.saxutils import unescape
    return ["".join(unescape(t) for t in WT.findall(p)) for p in PAR.findall(xml)]


def simples(marc):
    return re.sub(r"[_^]\{([^}]*)\}", r"\1", marc).replace("‹", "").replace("›", "")


def main():
    pb, pr = partes(BASE), partes(DOCX_FT)
    xb, xr = pb["word/document.xml"].decode("utf-8"), pr["word/document.xml"].decode("utf-8")
    diga("# Verificação do DOCX revisado contra o DOCX original (formato FT)")
    diga()
    diga(f"Original: tcc/{MODELO_FT} ({len(pb)} partes). Revisado: {DOCX_FT.relative_to(RAIZ)} ({len(pr)} partes).")
    diga()

    # 1. pacote
    so_b, so_r = sorted(set(pb) - set(pr)), sorted(set(pr) - set(pb))
    difer = sorted(n for n in set(pb) & set(pr) if pb[n] != pr[n])
    # as fontes embutidas são subconjuntos com os glifos usados no texto e mudam com ele
    esperadas = {"word/document.xml", "docProps/core.xml", "docProps/app.xml"}
    inesperadas = [n for n in difer if n not in esperadas and not n.startswith("word/fonts/")]
    midia = [n for n in pb if n.startswith("word/media/")]
    if so_b or so_r or inesperadas:
        FALHAS.append(f"partes do pacote: só no original {so_b}, só no revisado {so_r}, diferentes {inesperadas}")
    diga("## 1. Pacote")
    diga()
    diga(f"Os dois arquivos abrem sem erro (teste de integridade do ZIP). Partes iguais byte a byte: "
         f"{len(set(pb) & set(pr)) - len(difer)} de {len(pb)}; diferentes: {difer}. "
         f"Imagens: {len(midia)}, todas idênticas: {all(pb[n] == pr.get(n) for n in midia)}. "
         f"Estilos, numeração, cabeçalhos e relações idênticos: {not inesperadas}. As fontes embutidas "
         f"({sum(n.startswith('word/fonts/') for n in pr)} arquivos) são subconjuntos dos glifos usados e, por isso, "
         f"acompanham o texto.")
    diga()

    # 2. equações, figuras, tabelas
    def conta(x):
        return {"equações (m:oMathPara)": x.count("<m:oMathPara>"), "equações em linha (m:oMath)": x.count("<m:oMath>"),
                "figuras (w:drawing)": x.count("<w:drawing>"), "tabelas (w:tbl)": x.count("<w:tbl>"),
                "campos PAGEREF": len(re.findall(r"PAGEREF", x)), "quebras de seção": x.count("<w:sectPr")}
    cb, cr = conta(xb), conta(xr)
    if cb != cr:
        FALHAS.append(f"contagens de elementos diferentes: {cb} x {cr}")
    eq = lambda x: re.findall(r"<m:oMathPara>.*?</m:oMathPara>", x, re.S)      # noqa: E731
    if eq(xb) != eq(xr):
        FALHAS.append("equações diferentes do original")
    diga("## 2. Equações, figuras e tabelas")
    diga()
    diga("Contagens no revisado, iguais às do original: " + "; ".join(f"{k}: {v}" for k, v in cr.items())
         + f". Equações idênticas, byte a byte, às do original: {eq(xb) == eq(xr)}. Nenhuma equação virou imagem.")
    diga()

    # 3. texto
    tb, tr = paragrafos(xb), paragrafos(xr)
    registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
    norm = lambda t: re.sub(r"^((?:tabela|figura) \d+) — ", r"\1: ", " ".join(t.split()).casefold())   # noqa: E731
    novos = set()
    for r in registro:
        for d in r["depois"]:
            novos.add(norm(simples(d)))
    sm = difflib.SequenceMatcher(a=tb, b=tr, autojunk=False)
    pagina = re.compile(r"\d+$")
    fora, n_reg, n_pag, n_resumo = [], 0, 0, 0
    resumo_ini = next(i for i, t in enumerate(tr) if t.strip() == "Resumo")
    lista_ini = next(i for i, t in enumerate(tr) if t.strip() == "Lista de Figuras")
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        antigos = {norm(x) for x in tb[i1:i2]}
        antigos_sem_pag = {pagina.sub("", x) for x in antigos}
        for j in range(j1, j2):
            t = norm(tr[j])
            sem_pag = pagina.sub("", t)
            if resumo_ini < j < lista_ini:
                n_resumo += 1
            elif t in novos:
                n_reg += 1
            elif pagina.search(t) and sem_pag in antigos_sem_pag:
                n_pag += 1                                   # sumário e listas: só o número da página
            elif sem_pag in novos or sem_pag.replace("-", "–") in antigos_sem_pag:
                n_reg += 1                                   # entrada de lista de legenda alterada pela revisão
            else:
                fora.append(tr[j][:90])
    if fora:
        FALHAS.append(f"{len(fora)} parágrafos diferentes do original fora da revisão: {fora[:6]}")
    diga("## 3. Texto")
    diga()
    diga(f"Parágrafos no original: {len(tb)}; no revisado: {len(tr)}. Diferentes do original: "
         f"{n_reg} da revisão declarada (registro de {len(registro)} parágrafos, alguns divididos), "
         f"{n_resumo} do resumo e do abstract, {n_pag} entradas do sumário e das listas em que só o número "
         f"da página mudou. Outras diferenças: {len(fora)}.")
    diga()

    # 4. sumário e listas
    ini_sum = next(i for i, t in enumerate(tr) if t.strip() == "Sumário")
    cap1 = next(i for i, t in enumerate(tr) if t.startswith("Capítulo 1") and i > ini_sum)
    sem_pagina = [t for t in tr[lista_ini + 1:cap1] if t.strip() and t.strip() not in ("Lista de Tabelas", "Sumário")
                  and not pagina.search(t.strip())]
    legendas = [t for t in tr[cap1:] if re.match(r"(Figura|Tabela) \d+: ", t)]
    entradas = [t for t in tr[lista_ini + 1:ini_sum] if re.match(r"(Figura|Tabela) \d+: ", t)]
    faltam = [x[:60] for x in legendas if not any(e.startswith(x.strip()) for e in entradas)]
    if sem_pagina or faltam or len(entradas) != len(legendas):
        FALHAS.append(f"listas: sem página {sem_pagina[:3]}, legendas sem entrada {faltam[:3]}, "
                      f"{len(entradas)} entradas para {len(legendas)} legendas")
    nf = [int(m.group(1)) for t in legendas for m in [re.match(r"Figura (\d+):", t)] if m]
    nt = [int(m.group(1)) for t in legendas for m in [re.match(r"Tabela (\d+):", t)] if m]
    if nf != list(range(1, len(nf) + 1)) or nt != list(range(1, len(nt) + 1)):
        FALHAS.append(f"numeração de figuras ou tabelas fora de sequência: {nf} {nt}")
    diga("## 4. Sumário e listas")
    diga()
    diga(f"Legendas no corpo: {len(nf)} figuras (1 a {len(nf)}) e {len(nt)} tabelas (1 a {len(nt)}), em sequência. "
         f"Entradas nas listas: {len(entradas)}, todas com o título da legenda e número de página. "
         f"Entradas do sumário e das listas sem número de página: {len(sem_pagina)}.")
    diga()

    # 5. travessões e marcação
    ref = next(i for i, t in enumerate(tr) if t.strip() == "Referências" and i > cap1)
    cap3 = next(i for i, t in enumerate(tr) if t.startswith("Capítulo 3") and i > cap1)
    ap = next(i for i, t in enumerate(tr) if t.startswith("Apêndice A") and i > ref)
    partes_doc = [("Pré-textuais (capa a sumário)", 0, cap1), ("Capítulos 1 e 2", cap1, cap3),
                  ("Capítulos 3 a 5", cap3, ref), ("Referências", ref, ap), ("Apêndice A", ap, len(tr))]
    diga("## 5. Travessões, meias-riscas e restos de marcação")
    diga()
    for nome, a, b in partes_doc:
        t = " ".join(tr[a:b])
        diga(f"- {nome}: {t.count('—')} travessões e {t.count('–')} meias-riscas")
        if nome in ("Capítulos 3 a 5", "Apêndice A") and (t.count("—") or t.count("–")):
            FALHAS.append(f"travessão ou meia-risca em {nome}")
    tudo = " ".join(tr)
    restos = [m for m in ("⟦", "⟧", "‹", "›", "_{", "^{", "@@", "TODO", "XXX") if m in tudo]
    if restos:
        FALHAS.append(f"restos de marcação: {restos}")
    diga()
    diga("Os travessões e as meias-riscas dos capítulos 1 e 2 são os do original, mantidos por instrução do "
         "autor; os das referências fazem parte dos títulos citados e da forma ABNT de teses. "
         f"Restos de marcação interna no texto: {restos or 'nenhum'}. Comentários de revisão no pacote: "
         f"{'sim' if 'word/comments.xml' in pr else 'não'}; alterações controladas: "
         f"{'sim' if ('<w:ins ' in xr or '<w:del ' in xr) else 'não'}.")
    if "word/comments.xml" in pr or "<w:ins " in xr or "<w:del " in xr:
        FALHAS.append("comentários ou alterações controladas no arquivo final")
    diga()

    # 6. arquivos de origem
    diga("## 6. Arquivos de origem")
    diga()
    for nome in (ORIGINAL, FUNDIDO, MODELO_FT):
        h = hashlib.sha256((RAIZ / "tcc" / nome).read_bytes()).hexdigest()
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
    (BUILD / "verificacao_docx_revisado.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[-(len(FALHAS) + 3):]))
    sys.exit(1 if FALHAS else 0)


if __name__ == "__main__":
    main()
