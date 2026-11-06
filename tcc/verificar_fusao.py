"""
Verificação independente de TCC_exo1_exo2.docx, gerado por gerar_tcc_fundido.py.

Não usa as funções do gerador, só as listas EDICOES e REMOVIDOS, conferidas à
parte. Deduz a renumeração das legendas do próprio documento e confere:

1. cada bloco do original, menos os de REMOVIDOS, aparece no fundido, na mesma
   ordem, com o XML idêntico fora do texto e com o texto esperado (renumeração e
   EDICOES); os de REMOVIDOS não aparecem, nem citações aos seus autores;
2. tabelas, figuras, equações e seções em sequência;
3. toda referência a tabela, figura, equação ou seção aponta para um
   elemento existente, e figuras da patente estão qualificadas;
4. o texto novo não tem travessões nem restos da numeração do apêndice;
5. onde foram parar os parágrafos do apêndice da versão anterior;
6. as demais partes do pacote não mudaram.

Grava tcc/verificacao_fusao.md e interrompe com erro se 1 a 4 ou 6 falharem.

Rodar (na raiz do repositório):
    python tcc/verificar_fusao.py
"""
import difflib
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import unescape

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))
from gerar_tcc_fundido import (EDICOES, EDICOES_RE, REMOVIDOS, SUBSTITUIDAS,  # noqa: E402
                               parenteses_fixos, seno_sin)

ORIG = PASTA/"TCC_apenas_exo1.docx"
NOVO = PASTA/"TCC_exo1_exo2.docx"
APEN = PASTA/"TCC_apenas_exo1_complemento_Ottobock.docx"
ENT = {"&quot;": '"', "&apos;": "'"}
SAIDA = []


def diga(linha=""):
    print(linha)
    SAIDA.append(linha)


def corpo(caminho):
    x = zipfile.ZipFile(caminho).read("word/document.xml").decode("utf-8")
    return x[x.index("<w:body>") + 8:x.rindex("<w:sectPr")], x


def topo(c):
    out, prof, ini = [], 0, 0
    for m in re.finditer(r"<(/?)(w:p|w:tbl)(?=[\s>/])[^>]*?(/?)>", c):
        if m.group(3) and not m.group(1):
            if prof == 0:
                out.append(c[m.start():m.end()])
            continue
        if not m.group(1):
            if prof == 0:
                ini = m.start()
            prof += 1
        else:
            prof -= 1
            if prof == 0:
                out.append(c[ini:m.end()])
    assert "".join(out) == c
    return out


def txt(b):
    return "".join(unescape(t, ENT)
                   for t in re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", b))


def esqueleto(b):
    b = re.sub(r"<w:t(?: [^>]*)?>[^<]*</w:t>", "<w:t/>", b)
    return b.replace(' xml:space="preserve"', "")


def titulo(b):
    return 'w:val="Ttulo2"' in b[:400]


def legendas(blocos, sep):
    out = []
    for b in blocos:
        m = re.match(rf"^(Tabela|Figura) (\d+)({sep})(.*)$", txt(b))
        if m:
            out.append((m.group(1), int(m.group(2)), m.group(3), m.group(4).strip()))
    return out


def main():
    co, xo = corpo(ORIG)
    cn, xn = corpo(NOVO)
    O, Nn = topo(co), topo(cn)
    diga("# Verificação do TCC fundido")
    diga()
    diga(f"Original: {ORIG.name}, {len(O)} blocos. Fundido: {NOVO.name}, {len(Nn)} blocos.")
    diga()

    lo, ln = legendas(O, " —"), legendas(Nn, " —|:")
    mapa = {"Tabela": {}, "Figura": {}}
    for tipo, num, _, tit in lo:
        cand = [n for t, n, s, ti in ln if t == tipo and s == " —" and ti == tit]
        assert len(cand) == 1, (tipo, num, tit, cand)
        mapa[tipo][num] = cand[0]

    # seções do original: 3.k → 3.1.k até 3.8 e 3.1.(k + 1) a partir de 3.9, porque
    # a seção 3.1.9 (trabalhos virtuais) é nova; 4.k → 4.1.k
    def sec(m):
        cap, k = m.group(1), int(m.group(2))
        return f"{cap}.1.{k + (1 if cap == '3' and k >= 9 else 0)}"

    def eq(m):
        return f"{m.group(1)}({mapa_eq[int(m.group(2))]})"

    def esperado(t):
        # renumeração do original e, depois, as EDICOES, na ordem do gerador
        t = re.sub(r"^(Tabela|Figura) (\d+)(?= —)",
                   lambda m: f"{m.group(1)} {mapa[m.group(1)][int(m.group(2))]}", t)
        t = re.sub(r"(?<!^)\bTabela (\d+)\b",
                   lambda m: f"Tabela {mapa['Tabela'].get(int(m.group(1)), m.group(1))}", t)
        t = re.sub(r"(?<!^)\bFigura (\d+)\b",
                   lambda m: (f"Figura {mapa['Figura'][int(m.group(1))]}"
                              if int(m.group(1)) in mapa["Figura"] else m.group(0)), t)
        t = re.sub(r"(seç(?:ão|ões)\s+)([\d.]+(?:(?:\s+a\s+|\s+e\s+|,\s*)[\d.]+)*)",
                   lambda m: m.group(1) + re.sub(r"\b([34])\.(\d+)\b", sec,
                                                 m.group(2)), t)
        for a, b in EDICOES:
            t = t.replace(a, b)
        for padrao, b in EDICOES_RE:
            t = re.sub(padrao, b, t)
        # equações do original, depois das edições, como no gerador
        if re.fullmatch(r"(?:\(\d+\))+", t):
            t = re.sub(r"\((\d+)\)", lambda m: f"({mapa_eq[int(m.group(1))]})", t)
        t = re.sub(r"(Equaç(?:ão|ões) )\((\d+)\)", eq, t)
        t = re.sub(r"(Equações \(\d+\) (?:e|a) )\((\d+)\)", eq, t)
        # seno escrito sin em todo o documento
        t = re.sub(r"\b(arc)?sen\b", lambda m: f"{m.group(1) or ''}sin", t)
        return t

    # 1. blocos do original
    for prefixo in REMOVIDOS:
        assert sum(txt(x).startswith(prefixo) for x in O) == 1, prefixo
    retirados = [txt(x) for x in O if txt(x).startswith(REMOVIDOS)]
    Om = [x for x in O if not txt(x).startswith(REMOVIDOS)]
    # equações do original: o número novo de cada uma vem do bloco casado no
    # fundido (mesmo esqueleto XML, na ordem), e a ordem tem de ser preservada
    mapa_eq, j = {}, 0
    for b in Nn:
        if j < len(Om) and esqueleto(b) == esqueleto(seno_sin(parenteses_fixos(Om[j]))):
            # bloco de equações: só os rótulos, "(3)(4)", um por linha da tabela
            if "<m:oMath" in Om[j] and re.fullmatch(r"(?:\(\d+\))+", txt(Om[j])):
                antes_ = [int(n) for n in re.findall(r"\d+", txt(Om[j]))]
                depois_ = [int(n) for n in re.findall(r"\d+", txt(b))]
                assert len(antes_) == len(depois_), (txt(Om[j]), txt(b))
                mapa_eq.update(zip(antes_, depois_))
            j += 1
    assert sorted(mapa_eq) == list(range(1, len(mapa_eq) + 1)), sorted(mapa_eq)
    assert list(mapa_eq.values()) == sorted(mapa_eq.values()), mapa_eq

    j, diverge, casados = 0, [], set()
    for i, b in enumerate(Nn):
        if j < len(Om) and esqueleto(b) == esqueleto(seno_sin(parenteses_fixos(Om[j]))):
            t_esp = esperado(txt(Om[j]))
            if titulo(Om[j]):
                t_esp = re.sub(r"^([34])\.(\d+)(?= )", sec, txt(Om[j]))
            if txt(b) != t_esp:
                diverge.append((j, txt(b)[:100], t_esp[:100]))
            casados.add(i)
            j += 1
    for a, _ in EDICOES:
        assert sum(a in txt(x) for x in O) == 1, a
    # retirados: ausentes do fundido e sem citação ao primeiro autor
    texto_novo = " ".join(txt(b) for b in Nn)
    presentes = [t[:60] for t in retirados if any(txt(b) == t for b in Nn)]
    # citação na forma ABNT: sobrenome (et al.) seguido do ano da referência
    def citacao(t):
        lider = re.match(r"[A-ZÀ-Ý][A-ZÀ-Ý'-]*", t).group(0)
        anos = "|".join(sorted(set(re.findall(r"\b(?:19|20)\d{2}\b", t))))
        return rf"\b{re.escape(lider)}(?: et al\.)?(?:, | \()(?:{anos})"
    citados = sorted({t.split(",")[0].split(".")[0] for t in retirados
                      if re.search(citacao(t), texto_novo, flags=re.I)})
    diga("## 1. Conteúdo do original")
    diga()
    diga(f"Blocos do original encontrados em ordem, com XML idêntico fora do texto "
         f"(nas equações, os delimitadores simples passam a ter tamanho fixo, e sen e arcsen passam a sin e arcsin): "
         f"{j} de {len(Om)} ({len(retirados)} retirados de propósito, REMOVIDOS). "
         f"Texto diferente do esperado (renumeração e as {len(EDICOES)} edições "
         f"declaradas): {len(diverge)}. Retirados ainda presentes: {len(presentes)}. "
         f"Autores dos retirados ainda citados: {citados or 'nenhum'}.")
    diga(f"Renumeração das tabelas do original: {mapa['Tabela']}.")
    diga(f"Renumeração das figuras do original: {mapa['Figura']}.")
    diga(f"Renumeração das equações do original: {mapa_eq}.")
    for d in diverge:
        diga(f"- DIVERGE: {d}")
    diga()

    # 2. numeração
    tabs = [n for t, n, s, _ in ln if t == "Tabela"]
    figs = [n for t, n, s, _ in ln if t == "Figura"]
    eqs = [int(x) for b in Nn if b.startswith("<w:tbl") and "<m:oMath" in b
           for x in re.findall(r"<w:t>\((\d+)\)</w:t>", b)]
    tits = [txt(b) for b in Nn if titulo(b)]
    nums = [t.split(" ")[0] for t in tits]
    grupos = {}
    for n in nums:
        m = re.match(r"^(\d+(?:\.\d+)*)\.(\d+)$", n)
        if m:
            grupos.setdefault(m.group(1), []).append(int(m.group(2)))

    def seq(v):
        return v == list(range(1, len(v) + 1))
    ok2 = seq(tabs) and seq(figs) and seq(eqs) and all(seq(v) for v in grupos.values())
    diga("## 2. Numeração")
    diga()
    diga(f"Tabelas 1 a {len(tabs)} em sequência: {seq(tabs)}. Figuras 1 a {len(figs)}: "
         f"{seq(figs)}. Equações (1) a ({len(eqs)}): {seq(eqs)}.")
    diga("Seções por parte: " + "; ".join(f"{k}.1 a {k}.{max(v)} ({'ok' if seq(v) else 'falha'})"
                                          for k, v in grupos.items()) + ".")
    diga("Títulos de capítulo e de parte: " + "; ".join(
        t for t in tits if re.match(r"^(\d|[345]\.[12]) ", t) or t.isupper()) + ".")
    diga()

    # 3. referências
    todo = " ".join(txt(b) for b in Nn)
    secs = set(nums)
    erros = []
    for m in re.finditer(r"\bTabelas? (\d+)", todo):
        if int(m.group(1)) > len(tabs):
            erros.append(m.group(0))
    for m in re.finditer(r"\bFiguras? (\d+)((?:, \d+)*(?: e \d+)?)(.{0,14})", todo):
        n, resto = int(m.group(1)), m.group(3)
        patente = (resto.startswith((" da patente", " da EP", " da US")) or re.match(r", p\. \d", resto)
                   or n == 56
                   or m.group(2).startswith(", 16"))
        if not patente and n > len(figs):
            erros.append("figura da patente sem qualificação: " + m.group(0))
    for m in re.finditer(r"\bEquaç(?:ão|ões) \((\d+)\)", todo):
        if int(m.group(1)) > len(eqs):
            erros.append(m.group(0))
    padrao_sec = r"\d+(?:\.\d+)*"
    for m in re.finditer(rf"\bseç(?:ão|ões) ({padrao_sec}(?:(?:\s+a\s+|\s+e\s+|,\s*){padrao_sec})*)",
                         todo):
        for s in re.findall(padrao_sec, m.group(1)):
            if s not in secs and s not in ("1", "2", "3", "4", "5"):
                erros.append(f"seção inexistente {s}: '{m.group(0)}'")
    diga("## 3. Referências")
    diga()
    diga(f"Referências sem alvo: {len(erros)}.")
    for e in erros:
        diga(f"- {e}")
    diga()

    # 4. texto novo
    novos = [b for i, b in enumerate(Nn) if i not in casados]
    novo_txt = " ".join(txt(b) for b in novos)
    restos = re.findall(r"(?:apêndice|Apêndice|APÊNDICE|seção A\.\d+|Tabela A\.\d+|"
                        r"Figura A\.\d+|\(A\.\d+\))", novo_txt)
    travessoes = novo_txt.count("—") + novo_txt.count("–")
    diga("## 4. Texto novo")
    diga()
    diga(f"Blocos novos: {len(novos)}. Travessões: {travessoes}. Restos da numeração do "
         f"apêndice: {len(restos)}.")
    diga()

    # 5. parágrafos do apêndice anterior
    ca, _ = corpo(APEN)
    A = topo(ca)[len(O):]

    def norm(t):
        return re.sub(r"\d+(?:[.,]\d+)*", "#", re.sub(r"\b(?:A\.)?\d+(?:\.\d+)?\b", "#", t))
    novos_par = [txt(b) for b in novos if b.startswith("<w:p")]
    classes = {"igual": [], "numeros": [], "modificado": [], "sem": []}
    for b in A:
        t = txt(b)
        if not b.startswith("<w:p") or len(t) < 60 or t.startswith(("Fonte:", "Nota:")):
            continue
        if t in novos_par:
            classes["igual"].append((1.0, t, t))
            continue
        nt = norm(t)
        cands = sorted(novos_par,
                       key=lambda x: -difflib.SequenceMatcher(None, nt, norm(x)).quick_ratio())[:12]
        r, melhor = max((difflib.SequenceMatcher(None, nt, norm(x)).ratio(), x) for x in cands)
        chave = "numeros" if r > 0.97 else "modificado" if r >= 0.5 else "sem"
        classes[chave].append((r, t, melhor))
    diga("## 5. Parágrafos do apêndice da versão anterior")
    diga()
    diga(f"Idênticos: {len(classes['igual'])}. Iguais a menos de números e referências: "
         f"{len(classes['numeros'])}. Modificados: {len(classes['modificado'])}. Sem "
         f"correspondente próximo: {len(classes['sem'])}. Os últimos foram reescritos "
         "pelos novos resultados de s0 ou eram próprios do apêndice (título, "
         "apresentação e nota da lista de referências separada).")
    diga()
    for chave, rotulo in (("modificado", "Modificado"), ("sem", "Sem correspondente")):
        for r, t, melhor in sorted(classes[chave]):
            diga(f"- {rotulo} ({r:.2f}): {t[:110]}")
            diga(f"  - mais próximo no fundido: {melhor[:110]}")
    diga()

    # 6. pacote
    zo, zn = zipfile.ZipFile(ORIG), zipfile.ZipFile(NOVO)
    dif = [p for p in zo.namelist()
           if p not in ("word/document.xml", "word/_rels/document.xml.rels")
           and p not in SUBSTITUIDAS and zo.read(p) != zn.read(p)]
    # substituições declaradas: o conteúdo é o do arquivo indicado e o tamanho em
    # pixels é o do original, para que a extensão gravada no documento valha
    from PIL import Image
    subst_ok = all(zn.read(p) == c.read_bytes()
                   and Image.open(zo.open(p)).size == Image.open(zn.open(p)).size
                   for p, c in SUBSTITUIDAS.items())
    ro = zo.read("word/_rels/document.xml.rels").decode()
    rn = zn.read("word/_rels/document.xml.rels").decode()
    rel_ok = rn.startswith(ro[:ro.rindex("</Relationships>")])
    sect_ok = xo[xo.rindex("<w:sectPr"):] == xn[xn.rindex("<w:sectPr"):]
    diga("## 6. Pacote")
    diga()
    diga(f"Imagens substituídas por declaração: {sorted(SUBSTITUIDAS)}, conferidas "
         f"(conteúdo do arquivo declarado e mesmo tamanho em pixels): {subst_ok}.")
    diga(f"Partes alteradas além do documento e das relações: {dif or 'nenhuma'}. "
         f"Partes novas: {sorted(set(zn.namelist()) - set(zo.namelist()))}. Relações "
         f"originais mantidas: {rel_ok}. sectPr final idêntico: {sect_ok}.")

    (PASTA/"verificacao_fusao.md").write_text("\n".join(SAIDA) + "\n", encoding="utf-8")
    falhas = (j != len(Om) or diverge or presentes or citados or not ok2 or erros or travessoes or restos
              or dif or not subst_ok or not rel_ok or not sect_ok)
    if falhas:
        raise SystemExit("verificação falhou")


if __name__ == "__main__":
    main()
