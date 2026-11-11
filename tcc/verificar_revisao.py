#!/usr/bin/env python3
"""
Verificação da versão revisada para a defesa contra a base.

Compara revisao_defesa/build/fundido_revisado.docx com tcc/<nomes.FUNDIDO> e
confere, sem usar o gerador da revisão:

1. só os parágrafos do registro mudaram: todos os outros são idênticos, byte a
   byte, e na mesma ordem; títulos, tabelas, figuras e equações não mudaram;
2. os capítulos 1 e 2 são idênticos aos da base (instrução do autor);
3. em cada parágrafo alterado, nenhum número, sigla ou nome em maiúsculas e
   nenhum símbolo em itálico aparece ou desaparece sem estar declarado em
   revisao_defesa.EXCECOES, com o motivo;
4. o texto novo não tem travessão nem meia-risca, e o relatório conta os que
   restam no documento, por parte;
5. as demais partes do pacote DOCX são as da base.

Grava revisao_defesa/build/verificacao_revisao.md e
revisao_defesa/Alteracoes_paragrafo_a_paragrafo.md; sai com erro se algum
critério falhar.

Rodar (na raiz do repositório):  python3 tcc/verificar_revisao.py
"""
import collections
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_revisado import BUILD, FUNDIDO_REV, REGISTRO, SAIDA, marcado  # noqa: E402
from gerar_tcc_fundido import PARAGRAFO, texto  # noqa: E402
from nomes import FUNDIDO  # noqa: E402
import revisao_defesa as rd  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
LINHAS, FALHAS = [], []


def diga(s=""):
    LINHAS.append(s)


def corpo(caminho):
    with zipfile.ZipFile(caminho) as z:
        partes = {n: z.read(n) for n in z.namelist()}
    doc = partes["word/document.xml"].decode("utf-8")
    return doc[doc.index("<w:body>") + 8:doc.rindex("<w:sectPr")], partes


def sem_subscrito(t):
    """Texto marcado sem os índices dos símbolos (s_{0}, K_{40}), que não são números do texto."""
    return re.sub(r"_\{[^}]*\}", "", t)


def numeros(t):
    return collections.Counter(re.findall(r"\d+(?:[.,]\d+)*", sem_subscrito(t)))


def maiusculas(t):
    # siglas e sobrenomes em maiúsculas (citações no padrão ABNT), com dois ou mais caracteres
    return collections.Counter(re.findall(r"\b[A-ZÀ-Ý][A-ZÀ-Ý0-9]+\b", re.sub(r"[_^]\{[^}]*\}", "", t)))


def italicos(t):
    return collections.Counter(re.findall(r"‹([^›]*)›", t))


def main():
    cb, pb = corpo(RAIZ / "tcc" / FUNDIDO)
    cr, pr = corpo(FUNDIDO_REV)
    registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
    B, R = PARAGRAFO.findall(cb), PARAGRAFO.findall(cr)
    diga("# Verificação da versão revisada contra a base")
    diga()
    diga(f"Base: tcc/{FUNDIDO}, {len(B)} parágrafos. Revisada: {FUNDIDO_REV.relative_to(RAIZ)}, "
         f"{len(R)} parágrafos. Registro: {len(registro)} parágrafos alterados.")
    diga()

    # 1. só o registro mudou
    i = j = k = 0
    fora, alterados = [], []
    while i < len(B):
        # o registro vem antes do atalho de identidade: num parágrafo dividido, o primeiro
        # pedaço pode ser idêntico ao original
        if k < len(registro) and marcado(B[i]) == registro[k]["antes"]:
            n = len(registro[k]["depois"])
            if [marcado(x) for x in R[j:j + n]] == registro[k]["depois"] and (n > 1 or B[i] != R[j]):
                alterados.append((i, j, n))
                i += 1
                j += n
                k += 1
                continue
        if j < len(R) and B[i] == R[j]:
            i += 1
            j += 1
            continue
        fora.append(texto(B[i])[:80])
        i += 1
        j += 1
    if fora or k != len(registro) or j != len(R):
        FALHAS.append(f"parágrafos alterados fora do registro: {fora[:5]} (registro usado: {k} de {len(registro)})")
    esq = lambda c: PARAGRAFO.sub("<P/>", c)                       # noqa: E731
    # fora dos parágrafos (estrutura das tabelas, seções), nada muda; a divisão de um
    # parágrafo acrescenta marcas <P/>, e só elas
    eb, er = esq(cb), esq(cr)
    extra = sum(n - 1 for _, _, n in alterados)
    if eb.replace("<P/>", "") != er.replace("<P/>", "") or er.count("<P/>") - eb.count("<P/>") != extra:
        FALHAS.append("a estrutura fora dos parágrafos mudou")
    conta = lambda c, s: c.count(s)                                # noqa: E731
    for nome, marca in (("tabelas", "<w:tbl>"), ("figuras", "<w:drawing>"), ("equações", "<m:oMathPara>")):
        if conta(cb, marca) != conta(cr, marca):
            FALHAS.append(f"número de {nome} mudou")
    tit = lambda P: [texto(p) for p in P if 'w:val="Ttulo' in p[:400]]   # noqa: E731
    if tit(B) != tit(R):
        FALHAS.append("títulos mudaram")
    eqs = lambda P: [p for p in P if "<m:oMath" in p]              # noqa: E731
    if eqs(B) != eqs(R):
        FALHAS.append("equações mudaram")
    diga("## 1. Alcance das mudanças")
    diga()
    diga(f"Parágrafos idênticos à base: {len(B) - len(alterados)} de {len(B)}. Alterados: {len(alterados)}, "
         f"todos no registro. Parágrafos divididos: {sum(n > 1 for _, _, n in alterados)} "
         f"(+{extra} parágrafos). Títulos: {len(tit(R))}, idênticos. Tabelas: {conta(cr, '<w:tbl>')}, "
         f"figuras: {conta(cr, '<w:drawing>')} e equações: {conta(cr, '<m:oMathPara>')}, como na base; "
         f"equações idênticas byte a byte.")
    diga()

    # 2. capítulos 1 e 2
    c3 = next(n for n, p in enumerate(B) if 'w:val="Ttulo' in p[:400] and texto(p).startswith("3 MATERIAIS"))
    antes_c3 = [a for a in alterados if a[0] < c3]
    if antes_c3 and not getattr(rd, "ALTERAR_CAP_1_2", False):
        FALHAS.append(f"{len(antes_c3)} parágrafos dos capítulos 1 e 2 alterados")
    diga("## 2. Capítulos 1 e 2")
    diga()
    diga(f"Parágrafos alterados antes do capítulo 3: {len(antes_c3)}"
         + (" (permitido por ALTERAR_CAP_1_2)." if antes_c3 else ". Idênticos à base."))
    diga()

    # 3. números, maiúsculas e itálicos
    excecoes = getattr(rd, "EXCECOES", {})
    usadas, pendentes, repeticoes = set(), [], 0
    for r in registro:
        a, d = r["antes"], " ".join(r["depois"])
        for nome, f in (("número", numeros), ("maiúsculas", maiusculas), ("itálico", italicos)):
            ca, cd = f(a), f(d)
            saem, entram = sorted(set(ca) - set(cd)), sorted(set(cd) - set(ca))
            repeticoes += sum(1 for x in set(ca) & set(cd) if ca[x] != cd[x])
            if not (saem or entram):
                continue
            chave = next((c for c in excecoes if texto_simples(a).startswith(c)), None)
            exc = excecoes.get(chave, {})
            falta_s = [x for x in saem if x not in exc.get("saem", [])]
            falta_e = [x for x in entram if x not in exc.get("entram", [])]
            if chave:
                usadas.add(chave)
            if falta_s or falta_e:
                pendentes.append((nome, texto_simples(a)[:70], falta_s, falta_e))
    for nome, ini, s, e in pendentes:
        FALHAS.append(f"{nome} sem declaração em «{ini}»: sai {s}, entra {e}")
    sobra = sorted(set(excecoes) - usadas)
    if sobra:
        FALHAS.append(f"exceções sem uso: {[c[:50] for c in sobra]}")
    diga("## 3. Números, siglas e símbolos nos parágrafos alterados")
    diga()
    diga(f"Parágrafos conferidos: {len(registro)}. Números, siglas ou símbolos em itálico que aparecem "
         f"ou desaparecem sem declaração: {len(pendentes)}. Exceções declaradas e usadas: {len(usadas)}. "
         f"Valores que só mudam de número de ocorrências no parágrafo (repetições): {repeticoes}.")
    for c in sorted(usadas):
        e = excecoes[c]
        diga(f"- «{c[:70]}»: saem {e.get('saem', [])}, entram {e.get('entram', [])}. Motivo: {e['motivo']}")
    diga()

    # 4. travessões
    # o travessão separador das legendas do original ("Tabela 4 — ...") não é prosa
    sem_legenda = lambda t: re.sub(r"^((?:Tabela|Figura) \d+) — ", r"\1: ", t)   # noqa: E731
    novo = " ".join(" ".join(sem_legenda(d) for d in r["depois"]) for r in registro)
    if "—" in novo or "–" in novo:
        FALHAS.append("travessão ou meia-risca no texto novo")
    partes = collections.OrderedDict()
    nome = "Capítulos 1 e 2"
    for p in R:
        t = texto(p)
        if 'w:val="Ttulo' in p[:400]:
            if t.startswith("3 MATERIAIS"):
                nome = "Capítulo 3"
            elif t.startswith("4 RESULTADOS"):
                nome = "Capítulo 4"
            elif t.startswith("5 CONCLUS"):
                nome = "Capítulo 5"
            elif t.startswith("REFERÊNCIAS"):
                nome = "Referências"
            elif t.startswith("APÊNDICE"):
                nome = "Apêndice"
            continue
        legenda = bool(re.match(r"(Tabela|Figura) \d+ —", t))
        d = partes.setdefault(nome, [0, 0, 0])
        d[0] += (t.count("—") - (1 if legenda else 0))
        d[1] += t.count("–")
        d[2] += 1 if legenda else 0
    diga("## 4. Travessões e meias-riscas")
    diga()
    diga("Texto novo dos parágrafos alterados: nenhum travessão ou meia-risca. No documento revisado, "
         "por parte (travessões na prosa; meias-riscas; legendas com travessão separador, que o "
         "formato FT troca por dois-pontos):")
    for n, (trav, meia, leg) in partes.items():
        diga(f"- {n}: {trav}; {meia}; {leg}")
    resto = sum(v[0] + v[1] for n, v in partes.items() if n in ("Capítulo 3", "Capítulo 4", "Capítulo 5", "Apêndice"))
    if resto:
        FALHAS.append(f"{resto} travessões ou meias-riscas na prosa dos capítulos 3 a 5 e do apêndice")
    diga()

    # 5. pacote
    outras = [n for n in pb if n != "word/document.xml" and pb[n] != pr.get(n)]
    if outras or set(pb) != set(pr):
        FALHAS.append(f"partes do pacote alteradas: {outras}")
    diga("## 5. Pacote")
    diga()
    diga(f"Partes do DOCX além de word/document.xml: {len(pb) - 1}, idênticas às da base: {not outras}.")
    diga()

    diga("## Resultado")
    diga()
    if FALHAS:
        diga(f"{len(FALHAS)} falha(s):")
        for f in FALHAS:
            diga(f"- {f}")
    else:
        diga("Todos os critérios foram atendidos.")
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "verificacao_revisao.md").write_text("\n".join(LINHAS) + "\n", encoding="utf-8")

    # lista das alterações, para leitura do autor
    L = ["# Alterações parágrafo a parágrafo", "",
         "Cada item traz o texto da versão original e o da versão revisada. Subscritos aparecem como "
         "`_{...}`, sobrescritos como `^{...}` e itálicos entre `‹ ›`. Parágrafos reescritos estão "
         "marcados com R; trocas pontuais, com T.", ""]
    secao = None
    for n, r in enumerate(registro, 1):
        if r["secao"] != secao:
            secao = r["secao"]
            L += [f"## {secao}", ""]
        L += [f"**{n}. ({r['modo']}) Original**", "", r["antes"], "", "**Revisado**", ""]
        for d in r["depois"]:
            L += [d, ""]
    (SAIDA / "Alteracoes_paragrafo_a_paragrafo.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(LINHAS[-(len(FALHAS) + 3):]))
    sys.exit(1 if FALHAS else 0)


def texto_simples(marc):
    """Texto marcado → texto puro (como gerar_tcc_fundido.texto), para casar com as chaves."""
    return re.sub(r"[_^]\{([^}]*)\}", r"\1", marc).replace("‹", "").replace("›", "")


if __name__ == "__main__":
    main()
