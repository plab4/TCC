#!/usr/bin/env python3
"""
Versão revisada para a defesa: uma variante do documento, sem alterar a base.

Lê o DOCX fundido de base (tcc/<nomes.FUNDIDO>), aplica as mudanças declaradas em
tcc/revisao_defesa.py e grava, em revisao_defesa/build/:

    fundido_revisado.docx     o conteúdo revisado
    registro_revisao.json     cada parágrafo alterado, antes e depois

Com --tudo, gera também o LaTeX, o PDF e o DOCX no formato FT da versão revisada
(revisao_defesa/build/latex e revisao_defesa/<nome>.docx) e roda os verificadores
do pipeline sobre eles. Nada é gravado em tcc/ nem em latex/.

Mudanças aceitas (revisao_defesa.MUDANCAS), sempre sobre parágrafos:

    ("R", chave, novo)     reescreve o parágrafo cujo texto começa por chave; novo é
                           o texto na marcação do gerador (_{...}, ^{...} e ‹...›)
                           ou uma lista de textos, que divide o parágrafo
    ("T", antes, depois)   troca um trecho dentro de um parágrafo e preserva a
                           formatação do resto

revisao_defesa.GLOBAIS traz ainda trocas por expressão regular, (padrão, novo),
aplicadas a todos os parágrafos dos capítulos 3 a 5 e do apêndice que não foram
reescritos (por exemplo, a meia-risca entre palavras, que vira hífen).

Cada chave e cada trecho têm de ocorrer exatamente uma vez no documento. Não se
criam nem se removem títulos, legendas, tabelas, figuras ou equações, de modo que
a numeração da versão revisada é a da base. Os capítulos 1 e 2 não podem ser
alterados (instrução do autor), salvo com revisao_defesa.ALTERAR_CAP_1_2 = True.

Uso (na raiz do repositório):
    python3 tcc/gerar_revisado.py           # conteúdo revisado e registro
    python3 tcc/gerar_revisado.py --tudo    # também LaTeX, PDF e DOCX no formato FT
"""
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import unescape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_tcc_fundido import ENTIDADES, PARAGRAFO, WT, _editar_paragrafo, runs, texto  # noqa: E402
from nomes import FUNDIDO  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "revisao_defesa"
BUILD = SAIDA / "build"
NOME = "TCC_Modelagem_e_simulacao_de_mecanismos_passivos_revisado_para_defesa"
FUNDIDO_REV = BUILD / "fundido_revisado.docx"
REGISTRO = BUILD / "registro_revisao.json"
DOCX_FT = SAIDA / f"{NOME}.docx"

RUN = re.compile(r"<w:r[ >].*?</w:r>", re.S)
RPR = re.compile(r"<w:rPr>(.*?)</w:rPr>", re.S)
PROIBIDO_NO_NOVO = ("—", "–", "⟦", "⟧")
FORA_DA_REESCRITA = ("<m:oMath", "<w:drawing", "<w:hyperlink", "<w:fldChar", "<w:pict")


def marcado(p):
    """Texto do parágrafo na marcação do gerador: _{sub}, ^{sobre} e ‹itálico›."""
    saida = []
    for r in RUN.findall(p):
        t = "".join(unescape(x, ENTIDADES) for _, x, _ in WT.findall(r))
        if not t:
            continue
        m = RPR.search(r)
        rpr = m.group(1) if m else ""
        if 'w:val="subscript"' in rpr:
            saida.append("_{" + t + "}")
        elif 'w:val="superscript"' in rpr:
            saida.append("^{" + t + "}")
        elif "<w:i/>" in rpr:
            saida.append("‹" + t + "›")
        else:
            saida.append(t)
    return "".join(saida)


def _formato_base(p):
    """Propriedades comuns aos runs com texto, sem sub/sobrescrito, itálico, idioma
    e fonte (o DOCX no formato FT não herda a fonte do fundido)."""
    formatos = set()
    for r in RUN.findall(p):
        if not "".join(x for _, x, _ in WT.findall(r)):
            continue
        m = RPR.search(r)
        rpr = m.group(1) if m else ""
        rpr = re.sub(r'<w:vertAlign [^>]*/>|<w:i/>|<w:lang [^>]*/>|<w:rFonts [^>]*/>', "", rpr)
        formatos.add(rpr)
    return formatos


def reescrever(p, novo):
    """Parágrafo(s) com o mesmo w:pPr e o formato de base do original."""
    ruim = [x for x in FORA_DA_REESCRITA if x in p]
    assert not ruim, (ruim, texto(p)[:60])
    formatos = _formato_base(p)
    assert len(formatos) == 1, ("formatos mistos; use T", formatos, texto(p)[:60])
    extra = formatos.pop()
    m = re.match(r"(<w:p(?: [^>]*)?>)(<w:pPr>.*?</w:pPr>)?", p, re.S)
    abre, ppr = m.group(1), m.group(2) or ""
    textos = [novo] if isinstance(novo, str) else list(novo)
    saida = []
    for k, t in enumerate(textos):
        assert t.strip() and not any(c in t for c in PROIBIDO_NO_NOVO), t[:80]
        # só o primeiro parágrafo mantém os atributos (identificadores) do original
        saida.append((abre if k == 0 else "<w:p>") + ppr + runs(t, extra) + "</w:p>")
    return "".join(saida)


def aplicar(corpo, mudancas, alterar_cap_1_2=False, globais=(), globais_cap_1_2=()):
    """Devolve o corpo revisado e o registro das mudanças."""
    pars = [(m.start(), m.end(), m.group(0)) for m in PARAGRAFO.finditer(corpo)]
    textos = [texto(p) for _, _, p in pars]
    titulo = ['w:val="Ttulo' in p[:400] for _, _, p in pars]
    cap3 = next(i for i, t in enumerate(textos) if titulo[i] and t.startswith("3 MATERIAIS"))
    # mapa mudança → parágrafo
    plano = {}
    for n, (modo, a, b) in enumerate(mudancas):
        if modo == "R":
            assert len(a) >= 20, ("chave curta", a)
            achados = [i for i, t in enumerate(textos) if t.startswith(a)]
        elif modo == "T":
            achados = [i for i, t in enumerate(textos) if a in t]
            assert all(textos[i].count(a) == 1 for i in achados), ("trecho repetido", a)
            assert not any(c in b for c in PROIBIDO_NO_NOVO), b[:80]
        else:
            raise ValueError(modo)
        assert len(achados) == 1, (f"mudança {n}: {len(achados)} parágrafos", a[:70])
        i = achados[0]
        assert alterar_cap_1_2 or i > cap3, ("capítulos 1 e 2 não são alterados", a[:60])
        assert not titulo[i], ("títulos não são alterados", a[:60])
        plano.setdefault(i, []).append((modo, a, b))
    # trocas globais: capítulos 3 a 5 e apêndice, fora dos títulos e das referências
    ref = next(i for i, t in enumerate(textos) if titulo[i] and t.startswith("REFERÊNCIAS"))
    apendice = next((i for i, t in enumerate(textos) if titulo[i] and t.startswith("APÊNDICE")), len(textos))
    for i, t in enumerate(textos):
        if titulo[i] or i <= cap3 or ref <= i < apendice:
            continue
        if any(m == "R" for m, _, _ in plano.get(i, [])):
            continue
        for padrao, novo in globais:
            if re.search(padrao, t):
                plano.setdefault(i, []).append(("G", padrao, novo))
    for i, t in enumerate(textos[:cap3]):           # capítulos 1 e 2, só se autorizado
        if titulo[i] or any(m == "R" for m, _, _ in plano.get(i, [])):
            continue
        for padrao, novo in globais_cap_1_2:
            if re.search(padrao, t):
                plano.setdefault(i, []).append(("G", padrao, novo))
    registro, saida, pos, secao = [], [], 0, ""
    for i, (ini, fim, p) in enumerate(pars):
        if titulo[i]:
            secao = textos[i]
        if i not in plano:
            continue
        novo = p
        modos = [m for m, _, _ in plano[i]]
        assert modos.count("R") <= 1 and (modos == ["R"] or "R" not in modos), \
            ("um parágrafo é reescrito (R) ou tem trocas (T), não os dois", textos[i][:60])
        for modo, a, b in plano[i]:
            if modo == "R":
                novo = reescrever(novo, b)
            elif modo == "G":
                novo = _editar_paragrafo(novo, [(a, lambda m, d=b: d)])
            else:
                novo = _editar_paragrafo(novo, [(re.escape(a), lambda m, d=b: d)])
        assert novo != p, ("mudança sem efeito", textos[i][:60])
        registro.append({"modo": "".join(sorted(set(modos))), "secao": secao,
                         "antes": marcado(p),
                         "depois": [marcado(x) for x in PARAGRAFO.findall(novo)]})
        saida.append(corpo[pos:ini] + novo)
        pos = fim
    saida.append(corpo[pos:])
    return "".join(saida), registro


def gerar_fundido(origem=None, destino=FUNDIDO_REV):
    import revisao_defesa as rd
    origem = Path(origem or RAIZ / "tcc" / FUNDIDO)
    with zipfile.ZipFile(origem) as zin:
        partes = {n: zin.read(n) for n in zin.namelist()}
        infos = {i.filename: i for i in zin.infolist()}
    doc = partes["word/document.xml"].decode("utf-8")
    b0 = doc.index("<w:body>") + len("<w:body>")
    b1 = doc.rindex("<w:sectPr")
    cap12 = getattr(rd, "ALTERAR_CAP_1_2", False)
    mudancas = list(rd.MUDANCAS) + (list(getattr(rd, "MUDANCAS_CAP_1_2", [])) if cap12 else [])
    corpo, registro = aplicar(doc[b0:b1], mudancas, cap12, getattr(rd, "GLOBAIS", ()),
                              getattr(rd, "GLOBAIS_CAP_1_2", ()) if cap12 else ())
    partes["word/document.xml"] = (doc[:b0] + corpo + doc[b1:]).encode("utf-8")
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w") as zout:
        for nome, dados in partes.items():
            zi = zipfile.ZipInfo(nome, date_time=infos[nome].date_time)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = infos[nome].external_attr
            zout.writestr(zi, dados)
    tmp.replace(destino)
    REGISTRO.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
    n_r = sum("R" in r["modo"] for r in registro)
    print(f"{destino.relative_to(RAIZ)}: {len(registro)} parágrafos alterados "
          f"({n_r} reescritos, {len(registro) - n_r} com trocas pontuais ou globais), "
          f"de {len(rd.MUDANCAS)} mudanças declaradas")
    return registro


def _resumo_revisado(latex_base, latex_rev):
    """resumo.tex da variante: o da base, com os textos de revisao_defesa (se houver)."""
    import revisao_defesa as rd
    s = (latex_base / "resumo.tex").read_text(encoding="utf-8")
    for ambiente, chave in (("resumo", "RESUMO"), ("abstract", "ABSTRACT")):
        novo = getattr(rd, chave, None)
        if not novo:
            continue
        assert not any(c in novo for c in PROIBIDO_NO_NOVO), chave
        padrao = re.compile(r"(\\begin\{%s\}\n).*?(\n\\end\{%s\})" % (ambiente, ambiente), re.S)
        assert len(padrao.findall(s)) == 1, ambiente
        s = padrao.sub(lambda m: m.group(1) + novo.strip() + m.group(2), s)
    (latex_rev / "resumo.tex").write_text(s, encoding="utf-8")


def rodar(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd))
    r = subprocess.run([str(c) for c in cmd], **kw)
    if r.returncode != 0:
        raise SystemExit(f"falhou ({r.returncode}): {' '.join(str(c) for c in cmd)}")


def gerar_tudo():
    latex_base, latex_rev = RAIZ / "latex", BUILD / "latex"
    latex_rev.mkdir(parents=True, exist_ok=True)
    for nome in ("tese.tex", "preambulo.tex", "tese-FT.cls", "bibliografia.bib", "agradecimentos.tex"):
        shutil.copyfile(latex_base / nome, latex_rev / nome)
    shutil.copytree(latex_base / "logotipos", latex_rev / "logotipos", dirs_exist_ok=True)
    _resumo_revisado(latex_base, latex_rev)
    py = sys.executable
    rodar([py, RAIZ / "tcc" / "gerar_latex.py", FUNDIDO_REV, latex_rev])
    rodar(["latexmk", "-C", f"-jobname={NOME}", "tese.tex"], cwd=latex_rev,
          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(BUILD / "latexmk.log", "w", encoding="utf-8") as log:
        rodar(["latexmk", "-pdf", "-silent", f"-jobname={NOME}", "tese.tex"], cwd=latex_rev,
              stdout=log, stderr=subprocess.STDOUT)
    pdf = latex_rev / f"{NOME}.pdf"
    amb = dict(os.environ, TCC_RELATORIOS=str(BUILD), TCC_LATEX=str(latex_rev),
               TCC_FUNDIDO=str(FUNDIDO_REV))
    rodar([py, RAIZ / "tcc" / "verificar_latex.py", FUNDIDO_REV, pdf], env=amb)
    rodar([py, RAIZ / "tcc" / "gerar_docx_modelo.py", DOCX_FT], env=amb)
    rodar([py, RAIZ / "tcc" / "verificar_docx_modelo.py", DOCX_FT, pdf, FUNDIDO_REV], env=amb)
    shutil.copyfile(pdf, SAIDA / f"{NOME}.pdf")
    print(f"pronto: {DOCX_FT.relative_to(RAIZ)} e {(SAIDA / (NOME + '.pdf')).relative_to(RAIZ)}")


if __name__ == "__main__":
    gerar_fundido()
    if "--tudo" in sys.argv[1:]:
        gerar_tudo()
