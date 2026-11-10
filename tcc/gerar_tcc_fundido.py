"""
Gera o TCC com os três exoesqueletos a partir de tcc/TCC_apenas_exo1.docx,
que não é alterado. A cópia gravada:

- mantém todos os parágrafos, tabelas, equações e figuras do original;
- divide os capítulos 3, 4 e 5 em uma parte por exoesqueleto (3.1/3.2, 4.1/4.2,
  5.1/5.2): as seções originais passam a 3.1.k e 4.1.k, e o dispositivo da
  EP 3 504 033 B1 entra em 3.2, 4.2 e 5.2;
- acrescenta, nos tópicos dos capítulos 1 e 2 em que cabe, parágrafos
  próprios sobre o segundo dispositivo;
- renumera seções, tabelas e figuras em ordem de aparição e atualiza as
  referências do texto original; as equações do original mantêm seus
  números, e as novas continuam a sequência;
- insere as referências novas na lista principal, em ordem alfabética.

Além da renumeração, o texto original recebe apenas as edições de EDICOES,
necessárias porque o original dizia que a EP 3 504 033 B1 não tinha sido
analisada. tcc/relatorio_fusao.md lista cada parágrafo original alterado,
com o texto antes e depois.

O texto novo marca números com ⟦T#chave⟧ (definição de tabela), ⟦T:chave⟧
(referência), e o mesmo para F (figura), E (equação) e S (seção); a
numeração é resolvida no fim, em ordem de aparição.

Os números vêm de results/ottobock_tcc_numeros.json (tcc_resultados_ottobock.py)
e de fig16_curvas.csv; as figuras, de results/. As equações são escritas em
LaTeX e convertidas em OMML pelo pandoc.

Rodar (na raiz do repositório):
    python tcc_resultados_ottobock.py
    python tcc/gerar_tcc_fundido.py
com origem tcc/TCC_apenas_exo1.docx e destino tcc/<nomes.FUNDIDO>, que podem
ser dados como argumentos.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, unescape

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ/"results"
N = json.loads((RES/"ottobock_tcc_numeros.json").read_text(encoding="utf-8"))
sys.path.insert(0, str(RAIZ))
import torque_model_ottobock as tmo  # noqa: E402  (só para ler a Fig. 16)

FIG16 = tmo.load_fig16(tmo.FIG16_CSV)
MENOS = "−"
ORDEM = ("pontilhada", "tracejada", "continua")
ENTIDADES = {"&quot;": '"', "&apos;": "'"}


# ======================================================================
# formatação de números
# ======================================================================

def f(x, n=3):
    """Número com vírgula decimal e sinal de menos tipográfico."""
    s = f"{x:.{n}f}".replace(".", ",")
    return s.replace("-", MENOS)


def sci(x, n=1):
    """x em notação científica: '1,1 × 10^{−13}'."""
    if x == 0:
        return "0"
    m, e = f"{x:.{n}e}".split("e")
    return f"{m.replace('.', ',')} × 10^{{{MENOS if int(e) < 0 else ''}{abs(int(e))}}}"


def pct(x, n=2):
    return f(100*x, n) + "%"


def milhar(n):
    """Inteiro com ponto como separador de milhar: 1.658."""
    return f"{n:,}".replace(",", ".")


# ======================================================================
# blocos OOXML no formato do documento original
# ======================================================================

RPR = '<w:rPr><w:lang w:val="pt-BR"/></w:rPr>'


def runs(texto, extra=""):
    """Texto com marcação _{...} (subscrito), ^{...} (sobrescrito) e ‹...›
    (itálico, usado no símbolo ‹e›, que se confundiria com a conjunção)."""
    saida = []
    for parte in re.split(r'(_\{[^}]*\}|\^\{[^}]*\}|‹[^›]*›)', texto):
        if not parte:
            continue
        va, it = "", ""
        if parte.startswith("_{"):
            va, parte = '<w:vertAlign w:val="subscript"/>', parte[2:-1]
        elif parte.startswith("^{"):
            va, parte = '<w:vertAlign w:val="superscript"/>', parte[2:-1]
        elif parte.startswith("‹"):
            it, parte = "<w:i/>", parte[1:-1]
        # ordem do esquema: b, i, sz, szCs, vertAlign, lang
        b = "<w:b/>" if "<w:b/>" in extra else ""
        resto = extra.replace("<w:b/>", "")
        saida.append(f'<w:r><w:rPr>{b}{it}{resto}{va}<w:lang w:val="pt-BR"/></w:rPr>'
                     f'<w:t xml:space="preserve">{escape(parte)}</w:t></w:r>')
    return "".join(saida)


def P(texto):
    return f'<w:p><w:pPr>{RPR}</w:pPr>{runs(texto)}</w:p>'


SECOES = {}          # chave → número da seção (3.2.1, 4.2.4, ...)
_CONTADOR = {}


def H(texto):
    return (f'<w:p><w:pPr><w:pStyle w:val="Ttulo2"/>{RPR}</w:pPr>'
            f'{runs(texto)}</w:p>')


def SEC(prefixo, chave, titulo):
    """Título de seção numerada dentro de 3.2, 4.2 ou 5.2."""
    _CONTADOR[prefixo] = _CONTADOR.get(prefixo, 0) + 1
    numero = f"{prefixo}.{_CONTADOR[prefixo]}"
    assert chave not in SECOES, chave
    SECOES[chave] = numero
    return H(f"{numero} {titulo}")


# apêndices: blocos gerados nas partes 3.2, 3.3 e 4.2 e levados ao fim do
# documento, depois das referências; a marca de seção dá a letra
APENDICE = {"A_rob": [], "A_forma": []}
TITULOS_APENDICE = {
    "A": ("apA", "ROBUSTEZ DA IDENTIFICAÇÃO E AJUSTE DE FORMA NO EXOESQUELETO 2"),
}
for _letra, (_chave, _) in TITULOS_APENDICE.items():
    SECOES[_chave] = _letra


def H_APENDICE(letra):
    """Título de apêndice, depois das referências: 'APÊNDICE A: TÍTULO'."""
    return H(f"APÊNDICE {letra}: {TITULOS_APENDICE[letra][1]}")


def LEGENDA(texto):
    return (f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60"/>'
            f'{RPR}</w:pPr>{runs(texto, "<w:b/>")}</w:p>')


def LEG_T(chave, titulo):
    return LEGENDA(f"Tabela ⟦T#{chave}⟧: {titulo}")


def LEG_F(chave, titulo):
    return LEGENDA(f"Figura ⟦F#{chave}⟧: {titulo}")


def PEQUENO(texto, depois=False):
    esp = '<w:spacing w:before="60" w:after="60"/>' if depois else ""
    return (f'<w:p><w:pPr>{esp}{RPR}</w:pPr>'
            f'{runs(texto, "<w:sz w:val=\"20\"/><w:szCs w:val=\"20\"/>")}</w:p>')


def celula(texto, largura, cabecalho=False, alin="left"):
    shd = '<w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>' if cabecalho else ""
    jc = f'<w:jc w:val="{alin}"/>' if alin != "left" else ""
    paras = "".join(
        f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="20" w:after="20" '
        f'w:line="240" w:lineRule="auto"/>{jc}{RPR}</w:pPr>'
        f'{runs(linha, "<w:b/>" if cabecalho else "")}</w:p>'
        for linha in str(texto).split("\n"))
    return (f'<w:tc><w:tcPr><w:tcW w:w="{largura}" w:type="dxa"/>{shd}'
            f'<w:vAlign w:val="center"/></w:tcPr>{paras}</w:tc>')


def TABELA(cabecalho, linhas, larguras, alins=None):
    assert sum(larguras) == 9360, sum(larguras)
    alins = alins or ["left"]*len(larguras)
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in larguras)
    tr = ('<w:tr><w:trPr><w:cantSplit/><w:tblHeader/><w:jc w:val="center"/></w:trPr>'
          + "".join(celula(c, w, True, "center") for c, w in zip(cabecalho, larguras))
          + "</w:tr>")
    for linha in linhas:
        tr += ('<w:tr><w:trPr><w:cantSplit/><w:jc w:val="center"/></w:trPr>'
               + "".join(celula(c, w, False, a)
                         for c, w, a in zip(linha, larguras, alins)) + "</w:tr>")
    return ('<w:tbl><w:tblPr><w:tblStyle w:val="Tabelacomgrade"/>'
            '<w:tblW w:w="9360" w:type="dxa"/><w:jc w:val="center"/>'
            '<w:tblLayout w:type="fixed"/><w:tblLook w:val="0420" w:firstRow="1" '
            'w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="0" '
            f'w:noVBand="1"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>{tr}</w:tbl>')


EQUACOES = []        # LaTeX na ordem de criação; OMML preenchido depois


def EQ(*pares):
    """Tabela de equações numeradas, como as do capítulo 3: pares (chave, LaTeX)."""
    linhas = ""
    for chave, lx in pares:
        EQUACOES.append(lx)
        k = len(EQUACOES)
        linhas += (
            '<w:tr><w:trPr><w:cantSplit/><w:jc w:val="center"/></w:trPr>'
            '<w:tc><w:tcPr><w:tcW w:w="8460" w:type="dxa"/><w:vAlign w:val="center"/>'
            '</w:tcPr><w:p><w:pPr><w:spacing w:before="60" w:after="60"/>'
            f'<w:jc w:val="center"/>{RPR}</w:pPr>@@OMML{k}@@</w:p></w:tc>'
            '<w:tc><w:tcPr><w:tcW w:w="900" w:type="dxa"/><w:vAlign w:val="center"/>'
            '</w:tcPr><w:p><w:pPr><w:spacing w:before="60" w:after="60"/>'
            f'<w:jc w:val="right"/>{RPR}</w:pPr><w:r>{RPR}<w:t>(⟦E#{chave}⟧)</w:t></w:r>'
            '</w:p></w:tc></w:tr>')
    return ('<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/><w:jc w:val="center"/>'
            '<w:tblBorders><w:top w:val="nil"/><w:left w:val="nil"/>'
            '<w:bottom w:val="nil"/><w:right w:val="nil"/><w:insideH w:val="nil"/>'
            '<w:insideV w:val="nil"/></w:tblBorders><w:tblLayout w:type="fixed"/>'
            '<w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/>'
            '</w:tblCellMar><w:tblLook w:val="0600" w:firstRow="0" w:lastRow="0" '
            'w:firstColumn="0" w:lastColumn="0" w:noHBand="1" w:noVBand="1"/></w:tblPr>'
            '<w:tblGrid><w:gridCol w:w="8460"/><w:gridCol w:w="900"/></w:tblGrid>'
            f'{linhas}</w:tbl>')


IMAGENS = []         # (caminho, rId, docPr id)


def FIGURA(arquivo, largura_pol, descricao):
    from PIL import Image
    caminho = RES/arquivo
    w, h = Image.open(caminho).size
    cx = int(largura_pol*914400)
    cy = int(cx*h/w)
    k = len(IMAGENS) + 1
    rid, pid = f"rIdExo2F{k}", 1000 + k
    IMAGENS.append((caminho, rid, pid))
    d = escape(descricao, {'"': "&quot;"})
    return (
        f'<w:p><w:pPr><w:keepNext/><w:spacing w:after="60"/><w:jc w:val="center"/>'
        f'{RPR}</w:pPr><w:r><w:rPr><w:noProof/><w:lang w:val="pt-BR"/></w:rPr>'
        f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{pid}" name="Imagem {pid}" descr="{d}"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxml'
        'formats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:nvPicPr><pic:cNvPr id="{pid}" name="Imagem {pid}" descr="{d}"/>'
        '<pic:cNvPicPr/></pic:nvPicPr><pic:blipFill>'
        f'<a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
        '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')


FONTE = PEQUENO("Fonte: elaborada pelo autor.", True)


# ======================================================================
# leitura e edição do original
# ======================================================================

TOKEN = re.compile(r"<(/?)(w:p|w:tbl|w:sdt)(?=[\s>/])[^>]*?(/?)>")
WT = re.compile(r"(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)")
PARAGRAFO = re.compile(r"<w:p[ >].*?</w:p>", re.S)


def blocos(corpo):
    """Elementos de primeiro nível do corpo (parágrafos e tabelas), sem perda."""
    saida, prof, ini = [], 0, None
    for m in TOKEN.finditer(corpo):
        fecha, auto = m.group(1), m.group(3)
        if auto and not fecha:
            if prof == 0:
                saida.append(corpo[m.start():m.end()])
            continue
        if not fecha:
            if prof == 0:
                ini = m.start()
            prof += 1
        else:
            prof -= 1
            if prof == 0:
                saida.append(corpo[ini:m.end()])
    assert "".join(saida) == corpo, "o corpo não se decompõe em blocos"
    return saida


def texto(xml):
    return "".join(unescape(t, ENTIDADES) for _, t, _ in WT.findall(xml))


def _editar_paragrafo(p, regras):
    """Aplica as regras ao texto do parágrafo, que o Word divide em vários w:t.

    Cada trecho encontrado é substituído no primeiro w:t que ele toca e removido
    dos seguintes; o restante do XML não muda.
    """
    nos = list(WT.finditer(p))
    if not nos:
        return p
    textos = [unescape(m.group(2), ENTIDADES) for m in nos]
    for padrao, repl in regras:
        inteiro = "".join(textos)
        for m in reversed(list(re.finditer(padrao, inteiro))):
            novo = repl(m)
            if novo == m.group(0):
                continue
            a, b = m.span()
            assert b > a
            pos, primeiro = 0, True
            for k, t in enumerate(list(textos)):
                ini, fim = pos, pos + len(t)
                pos = fim
                if not (ini < b and fim > a):
                    continue
                if primeiro:
                    textos[k] = t[:a - ini] + novo + t[min(b, fim) - ini:]
                    primeiro = False
                else:
                    textos[k] = t[min(b, fim) - ini:]
            assert not primeiro, (padrao, m.group(0))
    saida, pos = [], 0
    for m, t in zip(nos, textos):
        abre = m.group(1)
        if t != t.strip() and "xml:space" not in abre:
            abre = '<w:t xml:space="preserve">'
        saida.append(p[pos:m.start()] + abre + escape(t) + m.group(3))
        pos = m.end()
    return "".join(saida) + p[pos:]


def editar(bloco, regras):
    return PARAGRAFO.sub(lambda m: _editar_paragrafo(m.group(0), regras), bloco)


# a seção 3.1.9 (trabalhos virtuais) é nova; as do original a partir da 3.9
# descem uma posição, e a seção 3.2.k continua a corresponder à 3.1.k
NOVA_31 = 9


def secao_nova(numero):
    """Seções do original: 3.k → 3.1.k até 3.8 e 3.1.(k + 1) a partir de 3.9;
    4.k → 4.1.k; as demais não mudam."""
    cap, _, resto = numero.partition(".")
    if cap not in ("3", "4") or not resto:
        return numero
    k, _, sub = resto.partition(".")
    k = int(k) + (1 if cap == "3" and int(k) >= NOVA_31 else 0)
    return f"{cap}.1.{k}" + (f".{sub}" if sub else "")


def _regra_secoes(m):
    return m.group(1) + re.sub(r"\d+(?:\.\d+)+", lambda n: secao_nova(n.group(0)),
                               m.group(2))


REGRAS_ORIGINAL = [
    # legendas: definição da numeração das tabelas e figuras do original
    (r"^(Tabela|Figura) (\d+)(?= —)",
     lambda m: f"{m.group(1)} ⟦{m.group(1)[0]}#o{m.group(2)}⟧"),
    # referências às tabelas (1 a 11) e figuras (1 a 5) do próprio documento;
    # "Figura 56" é da US 9.889.554 B2 e não muda
    (r"\bTabela (\d+)\b",
     lambda m: f"Tabela ⟦T:o{m.group(1)}⟧" if 1 <= int(m.group(1)) <= 11 else m.group(0)),
    (r"\bFigura (\d+)\b",
     lambda m: f"Figura ⟦F:o{m.group(1)}⟧" if 1 <= int(m.group(1)) <= 5 else m.group(0)),
    (r"(seç(?:ão|ões)\s+)(\d+(?:\.\d+)+(?:(?:\s+a\s+|\s+e\s+|,\s*)\d+(?:\.\d+)+)*)",
     _regra_secoes),
]
REGRA_TITULO = [(r"^([34])\.(\d+) ", lambda m: secao_nova(f"{m.group(1)}.{m.group(2)}") + " ")]

# equações do original: o rótulo "(n)" e as referências "Equação (n)" viram
# marcas, numeradas com as equações novas por ordem de aparição. No texto novo,
# número literal de equação só pode ser do original (as novas usam marcas).
N_EQ_ORIGINAL = 27


def _ref_eq(m):
    n = int(m.group(2))
    assert 1 <= n <= N_EQ_ORIGINAL, m.group(0)
    return f"{m.group(1)}(⟦E:o{n}⟧)"


ROTULO_EQ = [(r"^\((\d+)\)$", lambda m: f"(⟦E#o{m.group(1)}⟧)")]

# seno escrito "sin" em todo o documento, nas equações e no texto, a pedido do
# autor; o original escrevia "sen" e "arcsen"
SENO_TEXTO = [(r"\b(arc)?sen\b", lambda m: f"{m.group(1) or ''}sin")]
SENO_OMML = re.compile(r"(<m:t(?: [^>]*)?>)(arc)?sen(</m:t>)")


def seno_sin(xml):
    """sen → sin e arcsen → arcsin nos nomes de função da OMML."""
    return SENO_OMML.sub(lambda m: f"{m.group(1)}{m.group(2) or ''}sin{m.group(3)}", xml)
# Equações do original reescritas em q, a variável independente (pedido do
# autor): a derivada da Equação (17), dℓ/dθ* = m, e a equação de movimento (27).
# Como dq = dθ* pela Equação (2), o conteúdo não muda.
THETA_EM_Q = (17, 27)
SSUP_THETA = re.compile(
    r"<m:sSup>(?:(?!</m:sSup>).)*?<m:e>((?:(?!</m:e><m:sup>).)*)</m:e>"
    r"<m:sup><m:r>(?:(?!</m:r>).)*?<m:t>\*</m:t></m:r></m:sup></m:sSup>", re.S)


def theta_em_q(bloco):
    """θ* → q nas equações THETA_EM_Q do original (identificadas pelo rótulo):
    o expoente * sai, e θ vira q, também sob o acento de θ̈*."""
    m = re.fullmatch(r"\((\d+)\)", texto(bloco))
    if not m or int(m.group(1)) not in THETA_EM_Q:
        return bloco
    novo = SSUP_THETA.sub(lambda x: x.group(1).replace("<m:t>θ</m:t>", "<m:t>q</m:t>"), bloco)
    assert novo != bloco and "<m:t>θ</m:t>" not in novo, m.group(0)
    return novo


REFS_EQ = [
    (r"(Equaç(?:ão|ões) )\((\d+)\)", _ref_eq),
    (r"(Equações \(⟦E:o\d+⟧\) (?:e|a) )\((\d+)\)", _ref_eq),
]

# Edições do texto original, além da renumeração (antes, depois); cada trecho
# "antes" tem de ocorrer exatamente uma vez no documento.
# vale do RMSE com K e X_pose reidentificados para cada h (análise complementar
# da seção 4.1.4): faixas em torno do mínimo, na malha de 0,25 mm
N1 = json.loads((RES/"tcc_numeros.json").read_text(encoding="utf-8"))
N3 = json.loads((RES/"exo3_tcc_numeros.json").read_text(encoding="utf-8"))


def _vale(fator):
    perfil = N1["alternativo_x_pose_livre"]["perfil"]
    r = [x["rmse"] for x in perfil]
    i0 = r.index(min(r))
    a = b = i0
    while a > 0 and r[a - 1] <= fator*r[i0]:
        a -= 1
    while b < len(r) - 1 and r[b + 1] <= fator*r[i0]:
        b += 1
    return perfil[a], perfil[b]


V1, V2 = _vale(1.01), _vale(2.0)

EDICOES = [
    ("foi executado apenas para o gerador de torque da US 9.889.554 B2, ao qual se "
     "referem todas as equações deste capítulo e todos os resultados do capítulo 4.",
     "foi executado na parte estática: para o gerador de torque da US 9.889.554 B2, "
     "ao qual se referem as seções 3.1, 4.1 e 5.1, para o dispositivo da "
     "EP 3 504 033 B1, ao qual se referem as seções 3.2, 4.2 e 5.2, e para o "
     "mecanismo de came da US 9.737.374 B2, ao qual se referem as seções 3.3, 4.3 e "
     "5.3. As seções 3.1.9, 3.2.9 e 3.3.9 formulam os três modelos estáticos pelo "
     "princípio dos trabalhos virtuais, e as seções 3.4, 4.4 e 5.4 comparam os três."),
    ("O sinal do termo do arco foi fixado pelo princípio dos trabalhos virtuais.",
     "O sinal do termo do arco foi fixado pelo princípio dos trabalhos virtuais, "
     "formulado na seção 3.1.9."),
    ("Os números e as figuras do capítulo 4 são produzidos",
     "Os números e as figuras da seção 4.1 são produzidos"),
    ("Este capítulo apresenta os resultados das etapas",
     "Esta seção apresenta os resultados das etapas"),
    ("e a aplicação do procedimento à US 9.737.374 B2 e à EP 3 504 033 B1 não foram "
     "executadas.",
     "não foram executadas."),
    ("O objetivo geral foi atingido em sua parte estática e para um dos três "
     "dispositivos previstos.",
     "O objetivo geral foi atingido para este dispositivo na parte estática, e a "
     "extensão à dinâmica multicorpos ficou preparada, com o procedimento da seção "
     "3.1.13, mas não foi executada."),
    ("e no MBDyn e estender o procedimento à US 9.737.374 B2 e à EP 3 504 033 B1.",
     "e no MBDyn."),
    ("Por fim, os resultados referem-se a um único dispositivo",
     "Por fim, os resultados desta seção referem-se a um único dispositivo"),
    # fechamento do exoesqueleto 1 escrito em componentes, como nos exos 2 e 3; a
    # frase seguinte do autor vai, sem mudança, para depois das equações
    # (cap3_fechamento_exo1)
    ("As duas componentes da Equação (6) são as equações escalares de fechamento "
     "f1 = 0 e f2 = 0. Isolando-se os termos em φ, o lado esquerdo torna-se o vetor "
     "(s, R) girado de φ, o que permite resolver o sistema em forma fechada, sem "
     "procedimento iterativo:",
     "As duas componentes da Equação (6) são as equações escalares de fechamento:"),
    # f1 e f2 passam a ser citados pelas suas equações (marcas de equação nova,
    # numeradas por numerar)
    (" da Equação (6); a identidade τ = −F m/1000",
     " das Equações (⟦E:e1_f1⟧) e (⟦E:e1_f2⟧); a identidade τ = −F m/1000"),
    # variável independente q (pedido do autor); θ* fica como o ângulo interno
    # entre os elos, em que a patente publica a curva
    ("O ângulo interno θ* entre os elos é a variável independente do modelo, e q é "
     "sua versão referida ao desenho:",
     "A variável independente do modelo é q, o ângulo interno θ* entre os elos "
     "referido ao desenho:"),
    # Tabela 1: designação e uso passam de θ* para q. A ordem importa: "Toda a
    # cadeia de cálculo" sai da linha de θ* antes de entrar na de q
    ("Variável independente, em graus", "Equação (2), em graus"),
    ("Toda a cadeia de cálculo", "Pose do CAD e comparação com a patente"),
    ("θ* referido ao desenho, em radianos",
     "Variável independente: θ* referido ao desenho, em radianos"),
    ("Fechamento do circuito", "Toda a cadeia de cálculo"),
    # derivada e coordenada generalizada em q (Equações (17) e (27) do original,
    # reescritas por theta_em_q)
    ("com θ* em radianos. A Equação (17) é verificada",
     "com q em radianos. A Equação (17) é verificada"),
    ("onde m se anula, dℓ/dθ* também se anula", "onde m se anula, dℓ/dq também se anula"),
    ("com coordenada generalizada θ*.", "com coordenada generalizada q."),
    ("/∂θ* = K δ m", "/∂q = K δ m"),
    # 5.1: a continuidade fica só com trabalho futuro de pesquisa, sem as tarefas
    # internas de conferência e documentação (pedido do autor)
    ("; conferir no CAD a cota de ancoragem, o comprimento do alojamento e o "
     "comprimento da mola na pose; documentar o procedimento de extração dos pontos e "
     "sua incerteza", ""),
    # parte comum do capítulo 3, antes da seção 3.1: as frases gerais saem da
    # seção 3.1, que fica só com o exoesqueleto 1
    ("Massa, posição do centro de massa e raios de giro de braço, antebraço e mão "
     "foram obtidos das tabelas de de Leva (1996) para o indivíduo masculino de "
     "referência, com o cotovelo estendido. Os momentos de inércia de cada corpo, do "
     "membro e das peças do exoesqueleto,",
     "Os momentos de inércia de cada corpo, do membro de referência (seção 3) e das "
     "peças do exoesqueleto,"),
    ("Comprimentos são expressos em milímetros e ângulos em graus na entrada, com uma "
     "única conversão para radianos dentro das contas. ", ""),
    ("Não integram o escopo a avaliação experimental com participantes humanos, a "
     "eletromiografia, a análise de conforto e usabilidade, a fabricação e o ensaio de "
     "protótipo e o dimensionamento estrutural dos elos. ", ""),
    ("Os parâmetros antropométricos correspondem ao indivíduo de referência adotado, e "
     "o torque gravitacional é calculado para o membro superior estendido, sem "
     "ferramenta na mão. ", ""),
    # Okabe: três autores, citados todos (NBR 10520), com a referência
    # acrescentada à lista (ref_okabe); o artigo saiu em 2026. Ning et al.
    # (2022) sai desta citação: sem o artigo, não há como conferir o que lhe é
    # atribuído aqui
    ("(NING et al., 2022; OKABE et al., 2025)", "(OKABE; BRITTES; BRITO, 2026)"),
    # Ning et al. (2022 e 2023) saem do texto e da lista (REMOVIDOS): sem os
    # artigos, não há como conferir o que lhes é atribuído nas seções 2.2 e 2.3
    ("Entre os passivos destinados ao levantamento de cargas, Ning et al. (2023) "
     "organizam a estrutura em módulos de braço, ombro e costas e dimensionam o "
     "conjunto a partir da tração da mola. ", ""),
    # seção 2.3 reescrita: lista de Arakelian sem travessões, "frequentemente"
    # no lugar de "quase sempre" (o elástico da EP atua sem cabo nem polia), a
    # EP num parágrafo próprio (cap2_compensacao) e as escalas como o TCC as
    # descreve: abscissa em graus nas duas patentes, ordenada sem unidade na US
    # e sem valores na EP
    ("A compensação de gravidade constitui problema clássico",
     "A compensação de gravidade é problema clássico"),
    ("definidos pela natureza da força compensadora — contrapesos, molas ou força "
     "ativa proveniente de atuador auxiliar —, e Nguyen",
     "conforme a natureza da força compensadora: contrapesos, molas ou força ativa "
     "de um atuador auxiliar. Nguyen"),
    ("Em exoesqueletos vestíveis, a inviabilidade do contrapeso impõe o predomínio da "
     "solução elástica, quase sempre associada a cabos, polias ou cames encarregados "
     "de moldar a curva de torque; nessa linha, Ning et al. (2022) projetam o perfil "
     "da came a partir do módulo de armazenamento de energia da mola e validam o "
     "resultado por eletromiografia.",
     "Em exoesqueletos vestíveis, o contrapeso é inviável, e predomina a solução "
     "elástica, frequentemente associada a cabos, polias ou cames que moldam a curva "
     "de torque."),
    ("descreve arranjo dessa natureza:", "descreve um arranjo desse tipo:"),
    ("constituído por mola e cabo tensionado", "formado por mola e cabo tensionado"),
    ("uma protuberância situada junto à junta restringe a mola, de modo que o torque "
     "decai a valor residual e o membro recupera liberdade de movimento. A patente "
     "EP 3 504 033 B1 (OTTOBOCK, 2023), por sua vez, endereça o mesmo problema por "
     "caminho construtivo distinto, transmitindo a força de um atuador passivo por "
     "meio de elemento rígido apoiado na pelve.",
     "uma protuberância junto à junta restringe o gerador de força, o torque cai a "
     "um valor residual e o braço recupera a liberdade de movimento."),
    ("Em ambos os documentos, contudo, as figuras exibem apenas a forma dos perfis "
     "de torque, desprovidas de escala nos eixos, o que inviabiliza",
     "Nenhum dos dois documentos, contudo, permite quantificar o torque: as curvas "
     "publicadas têm a abscissa em graus, mas a ordenada não tem unidade declarada "
     "na US 9.889.554 B2 e não tem sequer valores na EP 3 504 033 B1. Isso "
     "inviabiliza"),
    # revisão de banca: precisão coerente entre picos e defasagem
    ("ocorre na elevação de 97,48°, e o do torque gravitacional, em 89,44°, com "
     "defasagem de 8,05°.",
     "ocorre na elevação de 97,484°, e o do torque gravitacional, em 89,438°, com "
     "defasagem de 8,046°."),
    ("O pico do torque do cabo, a 97,5°, fica 8,05° acima do pico gravitacional",
     "O pico do torque do cabo, a 97,5°, fica cerca de 8° acima do pico gravitacional"),
    # resíduo do trabalho virtual em mm/rad, como na seção 3.1.11 e na Tabela 17
    ("é de 1,7129 mm;", "é de 1,7129 mm/rad;"),
    ("é de 3,4258 mm;", "é de 3,4258 mm/rad;"),
    (" mm. Um resíduo da ordem do milímetro significa",
     " mm/rad. Um resíduo da ordem de 1 mm/rad significa"),
    ("com resíduo de 1,71 mm.", "com resíduo de 1,71 mm/rad."),
    # a Tabela 1 lista seis ângulos
    ("Quatro ângulos aparecem no cálculo", "Seis ângulos aparecem no cálculo"),
    # o ponto 29 fica fora da faixa de operação declarada na seção 3.1.3
    ("de 2,87° a 8,03° em θ*.",
     "de 2,87° a 8,03° em θ*; o ponto 29, em θ* = 42,909°, fica 0,008° abaixo do "
     "limite inferior da faixa de operação, θ* = 42,917° (seção 3.1.3)."),
    # a remissão diz só o que a seção 2.3 diz
    ("conforme a seção 2.3, a patente prevê que o dispositivo libere o braço nas "
     "posturas de não trabalho, em que o usuário precisa de mobilidade para alcançar "
     "ferramentas ou repousar o membro.",
     "conforme a seção 2.3, abaixo do ângulo de transição o torque cai a um valor "
     "residual e o braço recupera a liberdade de movimento."),
    # H_CAD já pertence à malha de 0,005 mm: 10.402 valores distintos
    (", num total de 10.403 valores.",
     ", num total de 10.402 valores distintos, porque a cota do CAD, 34,785 mm, já "
     "pertence à malha."),
    ("entre os 10.403 valores, com RMSE", "entre os 10.402 valores, com RMSE"),
    ("em todos os 10.403 valores de h", "em todos os 10.402 valores de h"),
    # citação da EP no formato das US e ressalva sobre os nomes comerciais
    ("e se anula com o braço junto ao corpo (OTTOBOCK, 2023).",
     "e se anula com o braço junto ao corpo (MIZERA et al., 2023). Os nomes "
     "comerciais não aparecem nas patentes citadas, que identificam apenas os "
     "titulares; a associação de cada produto à sua patente não pôde ser conferida "
     "nesses documentos (seção 3.2.1)."),
    # redação
    ("Embora fora constatado que o efeito do arco é pequeno em valor absoluto.",
     "Constatou-se, contudo, que o efeito do arco é pequeno em valor absoluto."),
    ("o que assegura a condição é que o cabo", "o que assegura que o cabo"),
    # objetivo geral e introdução do tamanho do trabalho executado (estático; a
    # dinâmica e a US 9.737.374 B2 ficam como extensão preparada)
    ("Modelar e simular o comportamento estático e dinâmico de mecanismos passivos "
     "de apoio ao braço descritos em patentes, tomando como caso de referência o "
     "gerador de torque de mola da US 9.889.554 B2, US 9.737.374 B2 e da EP 3 504 "
     "033 B1 e comparar o torque entregue pelo mecanismo ao torque gravitacional do "
     "conjunto braço–exoesqueleto ao longo da faixa de elevação.",
     "Modelar o comportamento estático de mecanismos passivos de apoio ao braço "
     "descritos em patentes, tomando como casos de referência os mecanismos da US "
     "9.889.554 B2, da EP 3 504 033 B1 e da US 9.737.374 B2, comparar o torque "
     "entregue por cada mecanismo ao torque gravitacional do conjunto "
     "braço–exoesqueleto ou à curva publicada na patente ao longo da faixa de "
     "elevação e preparar a extensão do procedimento à dinâmica multicorpos."),
    ("Este trabalho trata dessa lacuna: modelar e simular, de forma integrada, o "
     "comportamento estático e dinâmico de mecanismos passivos de apoio ao braço "
     "reconstruídos a partir de suas patentes, usando formulações amplamente "
     "conhecidas como a formulação de Lagrange e parâmetros antropométricos de "
     "referência.",
     "Este trabalho trata dessa lacuna: modelar o comportamento estático de "
     "mecanismos passivos de apoio ao braço reconstruídos a partir de suas patentes, "
     "com parâmetros antropométricos de referência, e preparar a extensão do modelo "
     "à dinâmica multicorpos pela formulação de Lagrange."),
    ("Por essa razão, o torque de um mecanismo passivo resulta do produto",
     "Nesse exercício de projeto, o torque de um mecanismo passivo resulta do produto"),
    # parâmetros de origem não reproduzida e ajuste na própria amostra (itens 1 e 21)
    ("Identificado em etapa anterior", "Congelado; origem não reproduzida"),
    ("Com os parâmetros congelados, o modelo reproduz a forma da curva publicada com "
     "coeficiente de determinação de 0,99839",
     "Com os parâmetros congelados, dois deles de origem não reproduzida, o modelo "
     "reproduz a forma da curva publicada, nos mesmos 29 pontos usados para fixá-los, "
     "com coeficiente de determinação de 0,99839"),
    ("Eles foram identificados por mínimos quadrados contra os 29 pontos extraídos em "
     "etapa anterior do trabalho e estão congelados no modelo vigente, que não "
     "executa ajuste algum. O script dessa etapa e a restrição de projeto então "
     "considerada para h não estão registrados no repositório; por isso, a "
     "identificação foi reproduzida nesta revisão apenas na parte verificável, "
     "descrita a seguir",
     "Eles foram identificados por mínimos quadrados contra os 29 pontos extraídos, "
     "por um procedimento que não foi registrado, e estão congelados no modelo, que "
     "não executa ajuste algum. Como esse procedimento e a restrição de projeto "
     "considerada para h não estão disponíveis, a identificação só pôde ser "
     "reproduzida na parte descrita a seguir"),
    ("com seus valores congelados e a situação de cada um nesta revisão.",
     "com seus valores congelados e a situação de cada um."),
    ("Para auditar essa afirmação, foi executada",
     "Para verificar se esse valor é um ótimo da curva extraída, foi executada"),
    ("e serve apenas para conferir a afirmação anterior.",
     "e serve apenas para essa verificação."),
    (", como na formulação inicialmente pensada,", ","),
    ("a formulação anterior alcança RMSE de 1,152 ",
     "a formulação sem o arco alcança RMSE de 1,152 "),
    ("A formulação anterior ajusta melhor a curva publicada, mas viola a conservação "
     "de energia",
     "A formulação sem o arco ajusta melhor a curva publicada, mas viola a "
     "conservação de energia"),
    ("e, por isso, foi abandonada:", "e, por isso, não foi adotada:"),
    ("e a formulação anterior, fisicamente inconsistente, ajustava melhor a curva.",
     "e a formulação sem o arco, fisicamente inconsistente, ajusta melhor a curva."),
    # verificações internas, e não independentes (item 8)
    ("foi conferida por verificações independentes",
     "foi conferida por verificações internas de consistência"),
    # o critério de tração depende de X_pose, identificado contra a curva (item 9)
    ("e três critérios de validade física independentes da curva extraída:",
     "e três critérios de validade física que não usam os pontos extraídos, embora o "
     "primeiro dependa da extensão na pose, identificada contra eles:"),
    ("A validade física independe da curva extraída.",
     "Os critérios de validade física não usam os pontos extraídos, embora o de "
     "tração dependa da extensão na pose, identificada contra eles."),
    ("A geometria, independentemente da curva extraída, admite h ≤ 32,886 mm e exclui "
     "o valor documental;",
     "A geometria, com a extensão na pose identificada, admite h ≤ 32,886 mm e exclui "
     "a cota do CAD;"),
    ("A varredura de h com K congelado separou o que a geometria impõe do que a curva "
     "extraída sugere. O cabo permanece tracionado em toda a faixa de operação "
     "somente para h ≤ 32,886 mm, o que exclui a cota de 34,785 mm lida no CAD.",
     "A varredura de h com K congelado separou o que os critérios físicos impõem do "
     "que a curva extraída sugere. Com a extensão na pose identificada, o cabo "
     "permanece tracionado em toda a faixa de operação somente para h ≤ 32,886 mm, o "
     "que exclui a cota de 34,785 mm medida no CAD."),
    # largura do vale com K e X_pose livres (item 10) e limites sem critério (item 11)
    ("e cresce para valores maiores de h. A razão entre a extensão máxima e o "
     "comprimento livre vale 1,0095 em h = 22,701 mm, iguala 1 em h ≈ 22,52 mm e só "
     "ultrapassa 10 próximo do extremo superior da varredura, em h = 60 mm.",
     "e cresce para valores maiores de h. O vale é largo: na malha de 0,25 mm, o "
     f"RMSE fica abaixo de 1,01 vez o mínimo de h = {f(V1[0]['h'], 2)} a "
     f"{f(V1[1]['h'], 2)} mm e abaixo de 2 vezes o mínimo de h = {f(V2[0]['h'], 2)} a "
     f"{f(V2[1]['h'], 2)} mm, faixa em que K vai de {f(V2[0]['k'], 1)} a "
     f"{f(V2[1]['k'], 1)}; com K e a extensão na pose livres, a curva extraída não "
     "determina h."),
    ("o critério que levou a h = 22,701 mm não pôde ser reproduzido, e a afirmação "
     "anterior de decrescimento monotônico do erro com h foi refutada pela auditoria.",
     "com K e a extensão na pose livres, o RMSE fica abaixo de 2 vezes o mínimo de h "
     f"= {f(V2[0]['h'], 2)} a {f(V2[1]['h'], 2)} mm, e o critério que levou a h = "
     "22,701 mm não pôde ser reproduzido."),
    ("O comprimento máximo da mola, 108,446 mm, é inferior ao comprimento útil do "
     "alojamento, 131,37 mm (valor a confirmar), com margem de 22,9 mm. ", ""),
    # comprimento livre não identificável e cotas do CAD em conflito (item 12)
    ("mas a origem da posição da ancoragem e da calibração angular não.",
     "mas a origem da posição da ancoragem e da calibração angular não, e o "
     "comprimento livre não é identificável, porque a curva depende só da extensão "
     "na pose."),
    ("e duas cotas do modelo em CAD permanecem a confirmar.",
     "e o modelo em CAD confirma o comprimento da mola na pose, 91,35 mm; o "
     "comprimento útil do alojamento, que não entra na cadeia de cálculo, é de "
     "140,0 mm no CAD."),
    # escala da reconstrução: só a origem, uma estimativa de medida antropométrica,
    # sem o detalhamento do fator (pedido do autor)
    ("por um fator único, fixado pela razão entre o comprimento do elo distal "
     "reconstruído e o comprimento de segmento do indivíduo de referência.",
     "por um fator único, fixado a partir de uma estimativa de medida antropométrica."),
    (" O fator de escala único, fixado pela razão entre o comprimento do elo distal "
     "reconstruído e o comprimento de segmento do indivíduo de referência, resultou "
     "em 0,870.", ""),
    ("O fator de escala de 0,870, fixado pela comparação entre o comprimento do elo "
     "distal e o comprimento de segmento do indivíduo de referência, propaga-se",
     "O fator de escala propaga-se"),
    # H_CAD é medida em CAD (item 13)
    ("é tratada como valor documental, e o valor adotado no modelo é H",
     "é uma medida em CAD, distinta do valor adotado no modelo, H"),
    ("com 4.979 valores. O valor documental H", "com 4.979 valores. A cota do CAD, H"),
    ("não está documentada. O valor documental H", "não está documentada. A cota do CAD, H"),
    # propriedades de massa do CAD dependem do material atribuído (item 14)
    ("e não como dimensões do dispositivo comercial.",
     "e não como dimensões do dispositivo comercial. As propriedades de massa "
     "dependem, além disso, do material atribuído a cada peça no CAD e são "
     "estimativas, e não propriedades do produto."),
    # sinal e módulo na Figura 9 (item 16) e construção da Figura 1 (item 17)
    ("Nota: a linha pontilhada marca o cruzamento das curvas normalizadas.",
     "Nota: a linha pontilhada marca o cruzamento das curvas normalizadas. O torque "
     "gravitacional está em módulo; o do cabo, com sinal (−τ), fica negativo além do "
     "ponto morto."),
    ("onde se distinguem o vetor B e o braço m.",
     "onde se distinguem o vetor B e o braço m. As componentes h e p de B estão "
     "tracejadas, e os arcos marcam os ângulos θ*, α, q e φ da Tabela 1, medidos no "
     "sentido anti-horário."),
    # o modelo não estima forças de interface (item 19)
    (" Tais forças de contato constituem, precisamente, uma das grandezas de saída "
     "que o modelo desenvolvido neste trabalho se propõe a estimar.", ""),
]

# Imagens do original substituídas pelas que o código do repositório gera:
# Figura 1, no estilo da Figura 2 (pernas h e p e ângulos da Tabela 1), e
# Figura 8, que não saía de nenhum código do repositório
SUBSTITUIDAS = {
    "word/media/image1.png": RES/"tcc_fig1_geometria.png",
    "word/media/image4.png": RES/"tcc_fig8_rmse_h.png",
}

# Edições por expressão regular, para trechos que o Word divide em runs de
# formatação diferente: o padrão casa só no run a trocar. A mesma expressão
# vale para o texto do parágrafo (fim em $) e para o do bloco inteiro, que o
# verificador confere (célula seguinte em seguida).
EDICOES_RE = [
    # Tabela 7: resíduo do trabalho virtual em mm/rad; o "−8" é sobrescrito
    (r"(?<=4,7 × 10−8) mm(?=$|Par da mola)", " mm/rad"),
    # Tabela 12: H_CAD é medida em CAD; o "CAD" anterior é subscrito
    (r"(?<=CAD), documental", ", medida em CAD"),
    # Tabela 6: f1 e f2 citados pelas suas equações; o "2" anterior é subscrito
    (r"(?<=fechamento f1 e f2), Equação \(6\)", ", Equações (⟦E:e1_f1⟧) e (⟦E:e1_f2⟧)"),
]

# Blocos do original retirados, pelo início do texto (cada um ocorre uma vez):
# as referências de Ning et al., que deixaram de ser citadas; as de Foroutannia e
# Mohammadian e de Kim, H. et al., que o texto nunca citou; e a da EP, que volta
# no formato das patentes US, pelo inventor (ref_mizera)
REMOVIDOS = ("NING, Y. et al. Design and analysis of upper limb passive exoskeleton",
             "NING, Y. et al. Structure design and analysis of upper limb wearable",
             "FOROUTANNIA, A.; MOHAMMADIAN, M. A comprehensive survey",
             "KIM, H. et al. Redundancy resolution of the human arm",
             "OTTOBOCK SE & CO. KGAA. Oliver Mizera et al.")


# ======================================================================
# conteúdo novo: dados comuns
# ======================================================================

g, mas, aj = N["geometria"], N["massa"], N["ajuste"]
ind, cj, fc = aj["individual"], aj["conjunto"], aj["forca_constante"]
pr, prf, ver, fam = N["projeto"], N["projeto_forma"], N["verificacoes"], N["familia"]
par, der = g["parametros_cad"], g["derivados"]
inv = N["braco_pose_invertido"]
# notação do autor para o exo 2: alavanca como segmento OP, de comprimento e
# e direção q = λ + ε (λ, direção do trecho e_c no código); φ é a defasagem do
# elemento 78 em relação a q
EPS = g["angulo_OP"]
E_OP = g["raio_OP"]
PHI_S = der["phi"] - EPS
QT = g["lambda_t"] + EPS
X_S = g["d78"]
# registro do modelo sobre a Figura 22 da patente (braço elevado, baixado)
SOB22 = N["sobreposicao_fig22"]
fg = N["fig16"]["curvas"]
rz = N["razoes"]
s0r = rz["s0"]
tr, po, co = ind["tracejada"], ind["pontilhada"], ind["continua"]
hum = mas["humano"]
corpos = {c["nome"]: c for c in mas["corpos"]}
n_pts = sum(fg[n]["n_total"] for n in ORDEM)
n_aj = sum(ind[n]["n"] for n in ORDEM)
n_aj_II = sum(int(((FIG16[n]["theta"] > 20.0) & (FIG16[n]["theta"] < 165.0)
                   & (FIG16[n]["theta"] < g["theta_t"])).sum()) for n in ORDEM)
sens = {s["caso"]: s for s in N["sensibilidade_s0"]}
sens_f = {s["caso"]: s for s in N["sensibilidade_s0_forma"]}
nrm = N["normalizado"]["casos"]
nrm_peso_pico = N["normalizado"]["theta_pico_peso"]
nrm_f = N["normalizado_forma"]["casos"]
var = N["varredura"]
tab = {l["theta"]: l for l in pr["tabela"]}
# afirmações do texto que dependem da geometria adotada: θ_b,pose positivo
# (conferido no CAD) e força do elástico no pino do rasgo (decisão do autor)
assert abs(g["raio_OP"] - g["E_CAD"]) < 1e-9 and abs(g["angulo_OP"]) < 1e-9
assert pr["theta_pico"] < mas["theta_tau_g_pico"]
DL = rz["deslocamento_abscissa"]
INICIO16 = sum(fg[n]["inicio"] for n in ORDEM)/len(ORDEM)
assert abs(g["theta_t_p0"] - INICIO16) < 1.5 and g["theta_t"] > INICIO16 + 5
assert abs(DL["valor"]) < 1.5 and abs(DL["varredura"]["rms_min"] - rz["rms"]) < 0.05
assert rz["rms_braco_pose_invertido"] > 1.5*rz["rms"]
assert min(rz["abscissa_espelhada"]["s0"].values()) > N["geometria"]["l_0"]
assert all(x["dP_mm"] < 5.0 for x in N["sobreposicao_fig22"])
# mínimo de τ/τ_g na curva da família com o e_c do CAD (cenário de projeto)
vmin_cad = next(x for x in next(l for l in fam["linhas"] if abs(l["e"] - g["E_CAD"]) < 1e-9)
                ["extremos_razao"] if x["tipo"] == "min")
tab_f = {l["theta"]: l for l in prf["tabela"]}
rob = {tuple(x["faixa"]): x for x in rz["robustez"]}
mc = rz["monte_carlo"]
NOME = {"pontilhada": "pontilhada", "tracejada": "tracejada", "continua": "contínua"}
assert abs(pr["s0"] - s0r["tracejada"]) < 1e-9 and pr["origem"] == "espaçamento entre curvas"


def s0txt(x):
    return f(x["s0"]) + (" (limite inferior)" if x["limite"] == "inferior" else "")


def faixa(x):
    t = f"{f(x['faixa_s0'][0], 2)} a {f(x['faixa_s0'][1], 2)}"
    return t + (" (na borda da grade)" if x["faixa_na_borda"] else "")


# ======================================================================
# capítulos 1 e 2
# ======================================================================

def cap1_introducao():
    return [P(
        "Nesta etapa, o procedimento foi aplicado a três mecanismos de arquitetura "
        "distinta. O primeiro é o gerador de torque de mola, cabo e polia da "
        "US 9.889.554 B2 (VAN ENGELHOVEN; KAZEROONI, 2018). O segundo é o "
        "dispositivo da EP 3 504 033 B1 (MIZERA et al., 2023), em que um elemento "
        "elástico atua diretamente sobre uma alavanca solidária ao braço e um "
        "elemento de encosto junto à articulação reduz o torque com o braço baixado "
        "e o anula quando situado sobre o eixo de rotação. O terceiro é o mecanismo "
        "da US 9.737.374 B2 (DOYLE, 2017), em que um cabo de ancoragem se enrola numa "
        "polia solidária a um came de raio variável, que converte a força de uma mola "
        "em torque no ombro. Os três são tratados em seções separadas dos capítulos 3, "
        "4 e 5, dedicadas aos exoesqueletos 1, 2 e 3.")]


def cap1_objetivos():
    return [P("Para o dispositivo da EP 3 504 033 B1, acrescentam-se os objetivos:"),
            P("h) aplicar a esse dispositivo a reconstrução, a composição inercial, a "
              "cinemática e o confronto com o torque gravitacional previstos nos itens "
              "a, b, c e e, substituindo o cabo e a polia por um circuito de dois "
              "regimes, com o elástico retilíneo ou apoiado no elemento de encosto "
              "junto à articulação;"),
            P("i) identificar o comprimento de referência do elástico a partir das três "
              "curvas de pré-tensão publicadas na patente, por um procedimento que não "
              "dependa da escala da ordenada nem da rigidez."),
            P("Para o dispositivo da US 9.737.374 B2, acrescentam-se os objetivos:"),
            P("j) reconstruir o circuito do cabo de ancoragem e o perfil do came de raio "
              "variável a partir das figuras da patente e do modelo em CAD;"),
            P("k) obter a transmissão entre a força da mola e o torque no ombro ao longo "
              "da faixa de elevação e confrontá-la com a curva de momento publicada na "
              "patente.")]


def cap1_justificativa():
    return [P(
        "O segundo dispositivo acrescenta ao trabalho um caso de teste do "
        "procedimento de identificação. A EP 3 504 033 B1 publica, na mesma figura, "
        "três curvas obtidas com o mesmo atuador e pré-tensões diferentes "
        "(MIZERA et al., 2023). Essa redundância permite obter grandezas que uma única "
        "curva sem escala não determina e confrontar, sobre a mesma base de "
        "cálculo, duas arquiteturas que a seção 2.7 associa a produtos comerciais. O "
        "terceiro dispositivo acrescenta um came de raio variável, cujo perfil a "
        "patente publica só como desenho, e testa o procedimento num mecanismo em que "
        "a geometria do came molda a curva de torque.")]


def cap2_compensacao():
    return [P(
        "A patente EP 3 504 033 B1 (MIZERA et al., 2023) trata o mesmo problema por outro "
        "caminho construtivo: a força de um atuador passivo é transmitida por um "
        "elemento rígido apoiado na pelve, e o elemento elástico atua diretamente "
        "sobre uma alavanca solidária ao braço, sem o arranjo de cabo e polia. A "
        "faixa sem torque com o braço baixado também não depende de uma "
        "protuberância: a partir de um ângulo ajustável, o elástico passa a se "
        "apoiar num elemento de encosto junto à articulação; com esse elemento sobre "
        "o eixo de rotação, as forças dos dois trechos do elástico passam pelo eixo "
        "e não produzem torque, embora o elástico continue tracionado "
        "(MIZERA et al., 2023).")]


def cap2_curva():
    return [P(
        "A EP 3 504 033 B1 explicita esse requisito na forma de preferências de "
        "projeto: nenhuma força abaixo de um ângulo do braço em relação à vertical, "
        "como 45°, 60° ou 90°, e força máxima entre 70° e 120°, de preferência em 90° "
        "(MIZERA et al., 2023). A patente destaca, nas reivindicações, dois meios de "
        "ajustar a força, a pré-tensão do elemento elástico e a excentricidade do "
        "ponto de aplicação, e publica curvas para cada um deles; a descrição cita "
        "ainda o comprimento da mola sem carga, a posição do elemento de encosto "
        "junto à articulação e a troca de atuadores.")]


def cap2_compatibilidade():
    return [P(
        "A EP 3 504 033 B1 trata a compatibilidade cinemática por outro caminho. A "
        "patente atribui ao estado da técnica o alinhamento dos eixos do dispositivo "
        "aos do ombro e observa que, mesmo assim, movimentos do tronco, da coluna e "
        "da cintura escapular não são acompanhados (MIZERA et al., 2023). Em vez disso, o "
        "elemento de apoio do braço liga-se ao elemento de transmissão de força por "
        "uma única articulação, cujo eixo não coincide com o de abdução do ombro, e "
        "esse elemento pode girar em relação ao cinto pélvico. Com isso, a concha do "
        "braço tem três graus de liberdade de translação e três de rotação em relação "
        "ao contra-apoio, e a reação é levada à pelve, o que, segundo a patente, "
        "evita a compressão de partes moles e das costelas.")]


def cap2_arquiteturas():
    return [P(
        "Nas configurações das Figuras 1 e 18 da patente da Ottobock, a força de "
        "apoio é transmitida por uma barra que vai da articulação junto ao ombro a "
        "um cinto pélvico, e o elemento elástico, uma mola de tração ou um cabo "
        "elástico, liga essa barra a uma alavanca do elemento que acompanha o braço, "
        "sem cabo de transmissão nem polia; a descrição admite outras variantes, "
        "como o princípio do cabo Bowden e o uso de cames ou engrenagens (MIZERA et al., "
        "2023).")]


def cap2_balanceamento():
    return [P(
        "No dispositivo da EP 3 504 033 B1, o elástico liga diretamente a barra à "
        "alavanca, sem o arranjo de cabo e polia que, segundo Herder (2001), aproxima "
        "a mola da condição de comprimento livre nulo. O perfil de torque resulta da "
        "variação simultânea do comprimento do elástico e do braço de alavanca com o "
        "ângulo, e o contato com o elemento de encosto introduz uma segunda "
        "configuração geométrica, de torque nulo ou reduzido, na faixa de braço "
        "baixado.")]


def cap2_identificacao():
    return [P(
        "Quando uma mesma figura reúne curvas do mesmo dispositivo que diferem por um "
        "único parâmetro, as razões entre elas eliminam os fatores comuns. Na "
        "EP 3 504 033 B1, três curvas foram obtidas com o mesmo atuador e "
        "pré-tensões diferentes; admitindo-se que a rigidez, a escala da ordenada, o "
        "braço de momento e o torque do peso sejam comuns às três, a razão entre duas "
        "curvas depende apenas do comprimento do elástico e das pré-tensões. Essa "
        "propriedade permite identificar o comprimento de referência do elástico sem "
        "conhecer a escala da ordenada e é a base do procedimento da seção "
        "⟦S:ident⟧.")]


# ======================================================================
# capítulo 3
# ======================================================================

def cap3_sobreposicao_fig42():
    """Circuito da Figura 1 sobre a Figura 42 da patente, logo depois dela."""
    sob = json.loads((RES/"tcc_numeros.json").read_text(encoding="utf-8"))["sobreposicao_fig42"]
    return [
        P("A Figura ⟦F:sobrep42⟧ sobrepõe esse circuito à Figura 42 da US 9.889.554 "
          "B2, na "
          "mesma pose, alinhado pelo pivô 151, que faz o papel de O, e pelo centro do "
          "tambor 183, que faz o papel de D. O vetor B foi desenhado com a cota do CAD, "
          f"h = H_{{CAD}} = {f(sob['h'])} mm, medida de 151 ao longo do 150 até antes "
          f"do 176, e com p = {f(sob['p'])} mm, a 90°, até o 176, onde fica a "
          "ancoragem A."),
        LEG_F("sobrep42", "Circuito vetorial do gerador de torque sobreposto à Figura "
                          "42 da US 9.889.554 B2, na pose de referência "
                          f"(θ* = {f(sob['theta'])}°, h = H_{{CAD}} = {f(sob['h'])} mm)"),
        FIGURA("tcc_fig1_sobreposicao.png", 6.5,
               "Figura 42 da US 9.889.554 B2 em cinza, vista em corte do gerador de "
               "torque, com o circuito vetorial do modelo sobreposto; à direita, "
               "ampliação da região do pivô."),
        PEQUENO("Fonte: adaptada da Figura 42 da US 9.889.554 B2 (VAN ENGELHOVEN; "
                "KAZEROONI, 2018), com o circuito do modelo sobreposto pelo autor.", True),
        PEQUENO("Nota: desenho da patente em cinza; elementos e ângulos do modelo como "
                "na Figura ⟦F:o1⟧. O desenho foi alinhado pelo pivô 151 (O) e pelo "
                "centro do tambor 183 (D), que por isso coincidem por construção; a "
                "posição de A no 176 é o que a sobreposição testa. Com h = "
                f"H_{{CAL}} = {f(sob['h_cal'])} mm, valor adotado no modelo (Figura "
                f"⟦F:o1⟧), A fica {f(sob['h'] - sob['h_cal'])} mm abaixo, sobre a perna h. "
                "O painel da direita amplia a região do pivô."),
    ]


def cap2_okabe():
    """Confronto com Okabe, Brittes e Brito (2026), que usam as mesmas patentes."""
    return [P(
        "Okabe, Brittes e Brito (2026) usaram curvas de patente, entre elas as da US "
        "9.889.554 B2 e da EP 3 504 033 B1, como leis de torque prescritas numa junta "
        "do modelo multicorpos, sem representar a geometria dos mecanismos: as curvas "
        "foram digitalizadas, e o máximo das curvas baseadas na US 9.737.374 B2, na US "
        "9.889.554 B2 e na Figura 17 da EP 3 504 033 B1 foi fixado em 30 N·m. Este "
        "trabalho segue outro caminho, o da reconstrução da geometria, e lê essas "
        "ordenadas de outro modo: a da US 9.889.554 B2 como sem unidade declarada "
        "(seção 4.1.6), e a da Figura 16 da EP 3 504 033 B1 como razão entre o torque "
        "do dispositivo e o do peso (seção ⟦S:dados⟧). As curvas também diferem. A "
        "daquele artigo baseada na US 9.889.554 B2 anula-se com o braço pendente e com "
        "o braço vertical e tem máximo perto de 70° de elevação; a extraída aqui da "
        "Figura 56 da US 9.889.554 B2 tem máximo em 99,8° de elevação (seção 4.1.2). Os "
        "documentos disponíveis não permitem dizer se a diferença vem da figura usada "
        "ou da leitura do eixo.")]


def cap4_ancoragens():
    """H_CAD e H_CAL são grandezas distintas (Figura 2 e Tabela 12)."""
    sob = N1["sobreposicao_fig42"]
    return [P(
        "As duas posições da ancoragem são grandezas distintas. H_{CAD} é a cota do "
        "desenho, e a Figura ⟦F:sobrep42⟧ mostra que ela leva A ao 176, o que se espera "
        "de um modelo em CAD reconstruído sobre a vista em corte da patente. H_{CAL} é "
        "o parâmetro que, com K e X_{pose}, reproduz a curva extraída, e põe A "
        f"{f(sob['h'] - sob['h_cal'])} mm abaixo, sobre a mesma perna h. Nenhuma das "
        "duas concordâncias é verificação independente: a de H_{CAD} vem do próprio "
        "desenho, e a de H_{CAL}, dos pontos usados para identificar K e X_{pose}. Com "
        "X_{pose} congelado, H_{CAD} viola a tração (Tabela ⟦T:o11⟧), e os dados "
        "disponíveis não decidem qual das duas posições corresponde ao dispositivo.")]


def cap3_fechamento_exo1():
    """Seção 3.1.4: as componentes da Equação (6) por extenso, como as equações de
    fechamento das seções 3.2.4 e 3.3.4 e como o modelo as calcula
    (calculate_closure_residuals); a frase do autor que as seguia vem depois."""
    return [EQ(("e1_f1", r"f_{1} = h\sin\alpha - p\cos\alpha + s\cos\varphi - R\sin\varphi + C\cos q = 0"),
               ("e1_f2", r"f_{2} = h\cos\alpha + p\sin\alpha + s\sin\varphi + R\cos\varphi + C\sin q = 0")),
            P("Isolando-se os termos em φ, o lado esquerdo torna-se o vetor (s, R) girado "
              "de φ, o que permite resolver o sistema em forma fechada, sem procedimento "
              "iterativo:")]


def cap3_trabalho_virtual_exo1():
    """Seção 3.1.9: o modelo do exoesqueleto 1 pelo princípio dos trabalhos
    virtuais, com o torque do cabo como b × f, b e β das Equações (11) a (13)."""
    mec = N1["mecanismo"]
    razao = N1["complementares"]["razao_b_min_m_max"]
    SECOES["vt1"] = "3.1.9"
    B = []
    a = B.append
    a(H("3.1.9 Formulação pelo princípio dos trabalhos virtuais"))
    a(P("O equilíbrio estático do braço pode ser escrito diretamente pelo princípio "
        "dos trabalhos virtuais. Com a junta e o tambor sem atrito e o cabo "
        "inextensível e sem massa, os vínculos são ideais, e suas reações não "
        "realizam trabalho. Num giro virtual δq do conjunto em torno de O, em "
        "radianos, igual a δθ* pela Equação (2), realizam trabalho a força do cabo "
        "sobre o tambor, o peso do conjunto e o torque τ_{u} que o usuário aplica ao "
        "braço."))
    a(P("A força do cabo atua no ponto de tangência T. Na formulação, T é o "
        "vetor b, de módulo b = |OT| e a um ângulo β da linha do elo, dados pelas "
        "Equações (11) a (13), e a força é o vetor f = −F u(φ), o V da Equação (20). "
        "Como o elo é rígido e gira em torno de O, o trabalho virtual dessa força é o "
        "do seu momento em relação a O, a componente z de b × f:"))
    a(EQ(("vt1_bf", r"\delta W_{c} = \tau\,\delta q,\quad \tau = \frac{(\mathbf{b}\times\mathbf{f})_{z}}{1000},\quad (\mathbf{b}\times\mathbf{f})_{z} = b_{x}f_{y} - b_{y}f_{x} = bF\sin(\varphi + \beta - q)")))
    a(P("O seno vem do ângulo entre os dois vetores: pela Equação (13), b aponta na "
        "direção q + π − β, e f, na direção φ + π. O produto vetorial retém só a "
        "componente de f perpendicular a b, que é a que gira o elo. Na faixa de "
        f"operação, b vai de {f(mec['b_min'])} a {f(mec['b_max'])} mm e β de "
        f"{f(mec['beta_min_grau'])}° a {f(mec['beta_max_grau'])}°, mas f aponta quase "
        "para o pivô: φ + β − q difere de 180° em no máximo "
        f"{f(mec['desvio_b_f_max_grau'])}°. Por isso, −b sin(φ + β − q), que coincide "
        "com o braço m da Equação (14), não passa de "
        f"|B| = {f(mec['oa'])} mm, e tomar F b como torque, sem a projeção, "
        f"superestimaria o resultado em mais de {int(razao)} vezes."))
    a(P("O mesmo trabalho virtual pode ser calculado do lado da mola. Com o cabo "
        "inextensível, o giro δq estende a mola de δℓ = (dℓ/dq) δq, com ℓ da "
        "Equação (16), e a força F = K δ, que se opõe à extensão, realiza o trabalho "
        "−F δℓ/1000. Como as duas expressões valem para todo δq, "
        "(b × f)_{z} = −F dℓ/dq, isto é, dℓ/dq = m, que é a Equação (17). A força "
        "se cancela, e a igualdade depende só da geometria, não de K, X_{pose} nem "
        "s_{0}. É ela que fixa como o arco enrolado entra no caminho do cabo: das "
        "formulações ℓ = s, ℓ = s + Rψ e ℓ = s − Rψ, só a última a satisfaz (seção "
        "4.1.3)."))
    a(P("O peso deriva do potencial V_{g} = M g y_{G}/1000: num giro δq, o centro de "
        "massa sobe x_{g} δq, com x_{g} da Equação (23), e o trabalho do peso é "
        "τ_{g,s} δq, com τ_{g,s} = −M g x_{g}/1000, o torque gravitacional com sinal, "
        "cujo módulo é o τ_{g} da Equação (24). Somados os três trabalhos, o princípio "
        "dos trabalhos virtuais exige, para todo δq,"))
    a(EQ(("vt1_eq", r"\delta W = (\tau + \tau_{g,s} + \tau_{u})\,\delta q = 0\quad\Rightarrow\quad\tau_{u} = -(\tau + \tau_{g,s})")))
    a(P("em que τ_{u} é o torque que o usuário precisa exercer para manter o braço "
        "parado. Como τ está em u.p. e τ_{g,s} em N·m, essa soma só tem valor físico "
        "se u.p. corresponder a N·m (seção 3.1.13), e a seção 4.1 compara apenas a "
        "forma e os ângulos de τ e τ_{g}. Com aceleração nula e Q_{nc} = τ_{u}, a "
        "Equação (27) reduz-se a essa condição."))
    return B


def nota_mola():
    """Nota da Tabela 9: L_livre vem do L_pose confirmado no CAD."""
    par1 = N1["parametros"]
    return [PEQUENO(
        "Nota: L_{livre} = L_{pose} − X_{pose}, com L_{pose} = "
        f"{f(par1['L_POSE'], 2)} mm, confirmado no CAD. A curva de torque depende só "
        "de X_{pose}.")]


def abertura_comum():
    """Parte comum do capítulo 3, antes da seção 3.1: o que vale para os três
    exoesqueletos. A seção 3.1 fica só com o exoesqueleto 1."""
    return [
        P("As seções 3.1, 3.2 e 3.3 seguem a mesma ordem, e as subseções de mesmo número "
          "tratam da mesma etapa; quando uma etapa não se aplica a um mecanismo ou não "
          "pôde ser concluída com os dados disponíveis, a própria subseção registra o "
          "motivo. Cada seção tem notação própria, e um mesmo símbolo pode ter "
          "significados diferentes em seções diferentes."),
        P("Os três mecanismos são tratados como planos, com origem O no eixo de rotação "
          "do braço. Os ângulos são medidos a partir de +x, no sentido anti-horário, com "
          "u(x) = (cos x, sin x); os comprimentos estão em milímetros, e os ângulos "
          "entram em graus, com uma única conversão para radianos dentro das contas."),
        P("O membro superior é o mesmo nos três modelos: o do indivíduo masculino de "
          "referência de de Leva (1996), de 73,0 kg e 1,741 m, com braço, antebraço e mão "
          "em série, alinhados ao eixo do braço, o cotovelo estendido e sem ferramenta na "
          "mão. Massa, posição do centro de massa e raios de giro dos segmentos vêm das "
          "tabelas desse trabalho, e o momento de inércia de cada corpo é levado ao eixo "
          "de rotação pelo teorema de Steiner, I_{O} = I_{cm} + M d^{2}. O torque do peso "
          "usa g = 9,80665 m/s^{2}."),
        P("Não integram o escopo a avaliação experimental com participantes humanos, a "
          "eletromiografia, a análise de conforto e usabilidade, a fabricação e o ensaio "
          "de protótipo e o dimensionamento estrutural das peças. As etapas dinâmicas, "
          "pela formulação de Lagrange e no MBDyn, foram previstas para os três "
          "mecanismos e não foram executadas."),
    ]


def parte_3B():
    B = []
    a = B.append
    apR, apF = APENDICE["A_rob"].append, APENDICE["A_forma"].append
    a(H("3.2 Exoesqueleto 2"))
    a(P("As seções ⟦S:cad⟧ a ⟦S:ferr⟧ aplicam à EP 3 504 033 B1 (MIZERA et al., 2023), "
        "da Ottobock, o procedimento deste capítulo, com a classificação de origem da "
        "seção 3. A cadeia de cálculo, descrita nas seções ⟦S:conv⟧ a ⟦S:peso⟧, está "
        "implementada no arquivo torque_model_ottobock.py, e os números e as figuras da "
        "seção 4.2 são produzidos pelo script tcc_resultados_ottobock.py, que grava os "
        "valores citados em results/ottobock_tcc_numeros.json e as figuras em results/. "
        "O script de resultados não altera parâmetro algum do modelo; as únicas "
        "identificações são as descritas na seção ⟦S:ident⟧."))

    # ------------------------------------------------------------ fontes
    # (na introdução da parte, sem seção própria, para que 3.2.k pareie com 3.1.k)
    # tabela de fontes cortada pelo autor (versão revisada de 9/11/2026)
    a(P("A patente foi lida no documento B1 completo, de 44 páginas, com a descrição, as "
        "reivindicações em alemão, inglês e francês e as 29 figuras, que ocupam as "
        "páginas 22 a 43."))

    # ------------------------------------------------------------ arquitetura
    a(SEC("3.2", "cad", "Reconstrução geométrica em CAD"))
    SECOES["arq"] = SECOES["cad"]
    a(P("A reconstrução parte da arquitetura descrita na patente. A EP 3 504 033 B1 descreve um dispositivo de apoio de pelo menos um braço do "
        "usuário. O elemento de apoio do braço (6), formado por um elemento "
        "distanciador (8) e uma concha (10) e fixado ao braço por uma braçadeira "
        "(12), liga-se por uma articulação (20) à extremidade superior de um "
        "elemento de transmissão de força (18), uma barra telescópica no exemplo da "
        "Figura 1 da patente. A extremidade inferior da barra apoia-se, por uma "
        "articulação esférica (22), num elemento de contra-apoio (16) em forma de "
        "cinto pélvico, de modo que a reação à força de apoio é levada à pelve. Com "
        "o dispositivo vestido, a articulação 20 fica aproximadamente na altura da "
        "articulação do ombro."))
    a(P("O atuador passivo (26) é uma mola de tração na Figura 1 da patente e um cabo "
        "ou fio elástico na Figura 18 da patente. Uma de suas extremidades fica presa à "
        "barra 18, e a outra atua sobre um elemento de alavanca (28) do elemento "
        "distanciador 8, de modo que a força é aplicada excentricamente em relação "
        "ao eixo da articulação 20. A força pode ser alterada pela pré-tensão do "
        "atuador ou pela excentricidade do ponto de aplicação. A Figura 24 da patente mostra o ponto de ataque "
        "(82) deslocado com uma chave de fenda em relação ao eixo da articulação, e "
        "a patente prevê ainda a regulagem do comprimento do braço de alavanca por "
        "um parafuso."))
    a(P("O elemento 78, chamado na patente de Anlageelement e aqui de elemento de "
        "encosto, fica junto à articulação 20 e encosta no elemento elástico a partir "
        "de um ângulo predeterminado entre o elemento de apoio do braço e a barra "
        "(Figura 22 da patente). A partir do contato, a direção da força deixa de ser a da reta "
        "entre os dois pontos de fixação do elástico e passa a depender do ponto de "
        "contato. A patente prefere o elemento 78 exatamente sobre o eixo da "
        "articulação 20; nesse caso, os dois trechos em que o elástico fica dividido "
        "exercem forças radiais ao eixo e não produzem torque, e o braço desce sem "
        "assistência. O ângulo de contato é ajustável, e esse é o mecanismo da faixa "
        "sem torque com o braço baixado."))
    a(P("Como preferência, a patente indica que nenhuma força seja aplicada até que "
        "o braço ultrapasse um ângulo em relação à vertical, com 45°, 60° ou 90° como "
        "exemplos, e que a força máxima ocorra entre 70° e 120°, de preferência em "
        "90°. O documento não traz cotas do mecanismo nem rigidez, pré-tensão "
        "ou dimensões do elemento elástico. Os dados numéricos que contém são a "
        "largura de 3,0 cm ± 1,0 cm, de preferência 3,5 cm ± 0,2 cm, da extremidade "
        "livre do cinto, o afastamento lateral mínimo de 5 cm entre o "
        "contra-apoio e a linha média da coluna, limites de 1,1 a 5,0 para a "
        "razão entre a distância da articulação ao contra-apoio e a distância da "
        "braçadeira à articulação e as escalas angulares das Figuras 16 e 17 "
        "da patente, nenhum deles utilizável como dimensão do gerador de torque."))
    a(P("Essas informações confirmam o que as seções 2.3 e 2.7 dizem do mecanismo: "
        "a força é transmitida por um elemento rígido apoiado na pelve, e o elemento "
        "elástico atua sobre um braço de alavanca ajustável. O nome comercial do "
        "produto não aparece na patente, de modo que a associação com o Paexo, feita "
        "na seção 2.7, não pode ser conferida no documento. Na configuração analisada, "
        "o elástico liga diretamente a barra à alavanca, e a faixa sem torque descrita "
        "na patente resulta do contato com o elemento 78 (seções ⟦S:cin⟧ a ⟦S:zero⟧)."))
    a(P("O dispositivo admite abdução, adução e movimentos do tronco. O modelo é "
        "plano, restrito ao plano sagital, e representa somente a anteversão, que é o "
        "movimento das Figuras 16 e 17 da patente."))

    # ------------------------------------------------------------ CAD
    a(P("O circuito do mecanismo foi fechado no modelo em CAD do Autodesk Fusion, e "
        "as grandezas medidas nesse modelo, com as derivadas delas, estão na Tabela "
        "⟦T:cad⟧ (seção ⟦S:r_geo⟧). O arquivo do modelo e o critério de escala não "
        "foram documentados, e as medições não têm, por isso, conferência "
        "independente. A "
        "planilha de composição inercial identifica o modelo como Ottobock iX "
        "Shoulder Air; como a patente não nomeia o produto, a "
        "correspondência entre esse produto, o modelo em CAD e os desenhos da "
        "patente não está documentada. As grandezas "
        "são tratadas como medidas em CAD, na classificação da seção 3, e não como "
        "dimensões do dispositivo comercial."))

    # ------------------------------------------------------------ inércia
    a(SEC("3.2", "inercia", "Parâmetros inerciais do membro e transporte ao eixo da "
                           "articulação 20"))
    a(P("O membro humano é o de referência (seção 3), em série a partir de O. O "
        "momento de inércia de cada segmento no centro de massa é M_{s} (k L)^{2}, com "
        "k o raio de giração transversal em fração do comprimento L, e o transporte ao "
        "eixo da articulação 20 usa o teorema de Steiner. A Tabela ⟦T:massa⟧, na seção "
        "⟦S:r_geo⟧, reúne os resultados, que coincidem com os da planilha do autor."))

    # ------------------------------------------------------------ convenções
    a(SEC("3.2", "conv", "Referenciais e convenções angulares e de sinal"))
    a(P("A origem O fica no eixo da articulação 20, admitido coincidente com o centro "
        "do ombro, com eixo x anterior e eixo y para cima, nas convenções da seção 3."))
    a(P("A variável independente é q, a direção da alavanca, representada pelo "
        "segmento OP, de comprimento ‹e› (seção ⟦S:cin⟧). A anteversão do braço, "
        "θ_{el}, com 0° para o braço pendente e 90° para o braço horizontal à frente, "
        "é a abscissa das Figuras 16 e 17 da patente e não precisa ser convertida em "
        "elevação anatômica. O modelo admite que o giro do elemento de "
        "apoio do braço em relação à barra 18 seja igual à anteversão, o que supõe o "
        "eixo da articulação 20 no centro do ombro e a barra 18 fixa em relação ao "
        "tronco. A patente situa a articulação na altura do ombro, na região da "
        "escápula e atrás do corpo com o braço pendente, com eixo que não coincide com "
        "o de abdução do ombro, admite que a barra 18 mude de orientação com o "
        "movimento do braço e não informa a relação entre o giro da articulação e a "
        "anteversão; as comparações angulares com as Figuras 16 e 17 da patente "
        "dependem dessa hipótese. O eixo do braço aponta na direção θ_{el} − 90°, e q "
        "se relaciona com θ_{el} por"))
    a(EQ(("lam", r"q = \theta_{\mathrm{el}} + 90^{\circ} + q_{0}"),
         ("lam0", r"q_{0} = q_{\mathrm{pose}} - \left( 180^{\circ} + \theta_{b,\mathrm{pose}} \right),\quad \theta_{\mathrm{el,pose}} = 90^{\circ} + \theta_{b,\mathrm{pose}}")))
    a(P("em que q_{pose} é a direção de OP na pose do CAD e θ_{b,pose} o ângulo do "
        "braço com a horizontal nessa pose, positivo acima."))
    a(P("O torque τ é positivo no sentido anti-horário, que é o de θ_{el} "
        "crescente; τ > 0 assiste a subida do braço. O torque do peso tem sinal "
        "oposto na faixa de 0° a 180°, e as comparações usam seu módulo τ_{g}."))
    a(P(f"O sinal de θ_{{b,pose}} = {f(par['BRACO_POSE'])}° foi conferido no CAD: na "
        "pose, o braço fica acima da horizontal. Com o sinal oposto, q_{0} seria "
        f"{f(inv['delta'] + EPS)}° e θ_{{el,pose}}, {f(inv['theta_pose'])}°, e o "
        f"contato da seção ⟦S:contato⟧ passaria de {f(g['theta_t'], 2)}° para "
        f"{f(inv['theta_t'], 2)}°; o efeito sobre s_{{0}} está na seção ⟦S:r_s0⟧. Com "
        "o sinal conferido, o pino da alavanca do modelo cai a "
        f"{f(SOB22[0]['dP_mm'], 1)} mm do pino do elástico desenhado na Figura 22 da "
        f"patente com o braço elevado e a {f(SOB22[1]['dP_mm'], 1)} mm com o braço "
        "baixado (seção ⟦S:contato⟧), e o espaçamento entre as curvas fecha com "
        f"resíduo de {f(rz['rms'])} mm, contra {f(rz['rms_braco_pose_invertido'])} mm "
        "com o sinal oposto (seção ⟦S:r_s0⟧)."))

    # ------------------------------------------------------------ cinemática
    a(SEC("3.2", "cin", "Equação de fechamento do circuito vetorial"))
    assert abs(E_OP - g["E_CAD"]) < 1e-9
    a(P("A ancoragem A do elástico fica na barra 18, e o ponto P, no pino do rasgo "
        "da alavanca solidária ao braço (Figura ⟦F:circ⟧). No CAD, o elástico prende "
        f"numa peça de C_{{3}} = {f(par['C3'])} mm articulada nesse pino, desenhada "
        f"girada de β_{{c}} = {f(par['BETA'])}°; articulada, ela se alinha ao elástico, e "
        "a força age no pino, como na Figura 22 da patente (seção ⟦S:contato⟧). A "
        f"alavanca é, assim, o segmento OP, de comprimento ‹e› = e_{{c}} = {f(E_OP)} mm "
        "e direção q, e a peça só entra para fechar o circuito com o comprimento do "
        "elástico medido no CAD (seção ⟦S:r_geo⟧). O vetor fixo de A a O e as "
        "posições de P e do centro do elemento 78 são"))
    a(EQ(("rAO", r"\mathbf{r}_{AO} = C_{1}\,\mathbf{u}\left( - \alpha \right) + C_{2}\,\mathbf{u}\left( \gamma \right),\quad \alpha = 90^{\circ} - \gamma"),
         ("P", r"\mathbf{P} = e\,\mathbf{u}(q),\quad \mathbf{C}_{78} = p\,\mathbf{u}\left( q + \varphi \right)")))
    a(P("com A = −r_{AO} e φ a defasagem constante entre a direção de p e q, "
        f"{f(PHI_S)}° na geometria do CAD. Para q > q*, o elástico é retilíneo de A a "
        "P (regime I), com comprimento s e direção ψ, e o circuito fechado "
        "r_{AO} + P − s u(ψ) = 0 tem as componentes"))
    a(EQ(("f1", r"f_{1} = C_{1}\cos\alpha + C_{2}\cos\gamma + e\cos q - s\cos\psi = 0"),
         ("f2", r"f_{2} = - C_{1}\sin\alpha + C_{2}\sin\gamma + e\sin q - s\sin\psi = 0")))
    a(P("Para q ≤ q*, o elástico encosta no elemento 78 e se divide no trecho de A ao "
        "elemento 78, de comprimento s − x e direção ψ, e no trecho x, do elemento 78 "
        "a P (regime II). O circuito passa a fechar pelo elemento 78, "
        "r_{AO} + C_{78} − (s − x) u(ψ) = 0:"))
    a(EQ(("f3", r"f_{3} = C_{1}\cos\alpha + C_{2}\cos\gamma + p\cos\left( q + \varphi \right) - \left( s - x \right)\cos\psi = 0"),
         ("f4", r"f_{4} = - C_{1}\sin\alpha + C_{2}\sin\gamma + p\sin\left( q + \varphi \right) - \left( s - x \right)\sin\psi = 0")))
    a(P("O trecho x é o lado do triângulo O, P, elemento 78 oposto ao ângulo φ, "
        "entre ‹e› e p, e não depende de q:"))
    a(EQ(("d78", r"x = \left| \mathbf{P} - \mathbf{C}_{78} \right| = \sqrt{e^{2} + p^{2} - 2\,e\,p\cos\varphi}")))
    a(P(f"Com as grandezas do CAD, x = {f(X_S)} mm. Em cada regime, as incógnitas "
        "são s e ψ, e a solução é fechada, porque os demais termos são conhecidos "
        "para cada q; no regime I e no regime II, respectivamente,"))
    a(EQ(("solI", r"\mathbf{w} = \mathbf{r}_{AO} + \mathbf{P},\quad s = \left| \mathbf{w} \right|,\quad \psi = \operatorname{atan2}\left( w_{y},\ w_{x} \right)"),
         ("solII", r"\mathbf{w} = \mathbf{r}_{AO} + \mathbf{C}_{78},\quad s = x + \left| \mathbf{w} \right|,\quad \psi = \operatorname{atan2}\left( w_{y},\ w_{x} \right)")))

    # ------------------------------------------------------------ contato
    a(SEC("3.2", "contato", "Ponto de contato e troca de regime"))
    a(P("O contato não é imposto por um ângulo. Ele é detectado pelo sinal do "
        "produto vetorial"))
    a(EQ(("kappa", r"\kappa = \left\lbrack \left( \mathbf{P} - \mathbf{A} \right) \times \left( \mathbf{C}_{78} - \mathbf{A} \right) \right\rbrack_{z}")))
    a(P("O regime II ocorre quando κ ≥ 0, isto é, quando o elemento 78 ficaria do "
        "outro lado da reta de A a P se o elástico não o contornasse. O ângulo de "
        "contato q* é a raiz de κ, obtida por bissecção, com a condição de que o "
        "elemento 78 fique entre A e P. Para a geometria do CAD, "
        f"q* = {f(QT)}°, isto é, θ_{{el}} = {f(g['theta_t'])}°; "
        f"nesse ponto, s = {f(g['s_t'])} mm e m = {f(g['b_t'])} mm nos dois "
        "regimes, porque A, o elemento 78 e P estão alinhados e o trecho x completa "
        "o comprimento."))
    a(LEG_F("circ", f"Circuitos do mecanismo: regime I na pose do CAD "
                    f"(θ_{{el}} = {f(der['theta_pose'])}°) e regime II em θ_{{el}} = 10°"))
    a(FIGURA("ottobock_tcc_fig_a1_geometria.png", 6.5,
             "Circuitos do mecanismo da Ottobock. Acima, regime I na pose do CAD: "
             "vetores C1, C2, e e s fechando o circuito de A por O e P. Abaixo, "
             "regime II com o braço a 10 graus: circuito C1, C2, p e s menos x, "
             "e triângulo e, p, x. À direita, ampliação da região do pivô."))
    a(FONTE)
    a(PEQUENO("Nota: à direita, ampliação da região do pivô. A alavanca está "
              "representada pelo segmento OP, de comprimento ‹e›. Regime I: "
              "circuito fechado C_{1}, C_{2}, ‹e› e s. Regime II: circuito fechado "
              "C_{1}, C_{2}, p e s − x, e triângulo ‹e›, p e x (‹e› tracejado); o "
              "elemento 78, na ponta de p, só entra depois do contato. As linhas "
              "pontilhadas indicam o eixo do braço."))
    se, sb = SOB22
    a(P("A Figura ⟦F:sobrep⟧ sobrepõe esses circuitos à Figura 22 da patente, com "
        "o braço elevado e com o braço baixado. Em cada desenho, o modelo foi "
        "calculado na anteversão lida na figura, "
        f"θ_{{el}} = {f(se['theta'], 1)}° e {f(sb['theta'], 1)}°, e alinhado pelo "
        "centro da articulação 20, que faz o papel de O, e pela extremidade inferior "
        "do elástico desenhado, junto à braçadeira da barra 18, onde fica a "
        "ancoragem A."))
    a(LEG_F("sobrep", "Circuitos do modelo sobrepostos à Figura 22 da patente, com "
                      f"o braço elevado (regime I, θ_{{el}} = {f(se['theta'], 1)}°) e "
                      f"baixado (regime II, θ_{{el}} = {f(sb['theta'], 1)}°)"))
    a(FIGURA("ottobock_tcc_fig_a7_sobreposicao.png", 6.5,
             "Figura 22 da EP 3 504 033 B1 em cinza, com os vetores do modelo "
             "sobrepostos: acima, braço elevado; abaixo, braço baixado, com o "
             "elástico apoiado no elemento 78; à direita, ampliações da região do "
             "pivô."))
    a(PEQUENO("Fonte: adaptada de Mizera et al. (2023), Figura 22, p. 37 do documento "
              "B1, com os circuitos do modelo sobrepostos pelo autor.", True))
    a(PEQUENO("Nota: desenho da patente em cinza, girado para a orientação de "
              "leitura; vetores, pontos e linhas pontilhadas do modelo como na "
              "Figura ⟦F:circ⟧. À direita, ampliação da região do pivô. Em cada pose, "
              "O e A coincidem por construção, porque o desenho foi alinhado por esses "
              "dois pontos; só P e o elemento 78 testam o modelo. O P do modelo cai a "
              f"{f(se['dP_mm'], 1)} mm do pino do elástico desenhado com o braço "
              f"elevado e a {f(sb['dP_mm'], 1)} mm com o braço baixado; com o braço "
              f"baixado, o centro do elemento 78 do CAD fica a {f(sb['d78_mm'], 1)} mm "
              "do ponto em que o elástico desenhado se dobra."))

    # ------------------------------------------------------------ força
    a(SEC("3.2", "forca", "Comprimento do elástico, lei da mola e torque"))
    a(P("O elástico é tratado como linear e sem massa, com folga abaixo do "
        "comprimento livre: δ = max(s − s_{0}, 0) e F = K δ, em que "
        "s_{0} é o valor de s em que o elástico atinge o comprimento livre. A patente "
        "não informa K, o comprimento livre nem a pré-tensão; s_{0} é identificado "
        "pelo espaçamento entre as curvas da Figura 16 da patente (seção ⟦S:ident⟧)."))
    a(P("A força do trecho ligado a A, f = −F u(ψ), atua em P no regime I e no "
        "centro do elemento 78 no regime II. O trecho x liga dois pontos da "
        "alavanca, e as forças que ele exerce sobre eles são iguais, opostas e "
        "colineares, sem momento resultante. O braço de momento com sinal e o torque "
        "são"))
    a(EQ(("m", r"m_{\mathrm{I}} = e\sin\left( q - \psi \right),\quad m_{\mathrm{II}} = p\sin\left( q + \varphi - \psi \right),\quad \tau = \frac{Fm}{1000}")))
    a(P("com m > 0 quando o torque assiste a subida; o fator 1/1000 converte N·mm em "
        "N·m. Com o elemento 78 pontual e sem atrito, a tração "
        "é igual nos dois trechos, e o princípio dos trabalhos virtuais (seção "
        "⟦S:vt2⟧) dá"))
    a(EQ(("tv", r"\frac{ds}{dq} = - m")))
    a(P("com q em radianos, verificada nos dois regimes (seção ⟦S:r_verif⟧). Como q "
        "cresce com a elevação do braço e m > 0 assiste a subida, o elástico se encurta "
        "quando o braço sobe."))

    # ------------------------------------------------------------ faixa sem torque
    a(SEC("3.2", "zero", "Faixa sem torque com o braço baixado"))
    a(P("Pela Equação (⟦E:m⟧), m_{II} é proporcional a p: abaixo do contato, o torque "
        "só se anula com o elemento 78 sobre o eixo (p = 0), configuração preferida "
        "pela patente. Nesse caso, x = ‹e›, a reta do elástico passa pelo pivô no "
        "contato, e o ângulo de contato tem forma fechada:"))
    a(EQ(("lamt", r"q^{*} = \operatorname{atan2}\left( r_{AO,y},\ r_{AO,x} \right)")))
    a(P(f"Com as demais grandezas do CAD, a Equação (⟦E:lamt⟧) dá θ_{{el}} = {f(g['theta_t_p0'])}°. "
        "As curvas da Figura 16 da patente partem de razão nula entre "
        f"{f(min(fg[n]['inicio'] for n in ORDEM), 2)}° e "
        f"{f(max(fg[n]['inicio'] for n in ORDEM), 2)}° (seção ⟦S:r_dados⟧), em média "
        f"{f(INICIO16 - g['theta_t_p0'], 2)}° acima desse contato e bem abaixo do "
        f"contato com o elemento do CAD, em {f(g['theta_t'], 2)}°: a figura é "
        "compatível com o elemento 78 sobre o eixo, o único caso em que o modelo tem "
        "torque nulo antes do contato (seção ⟦S:r_conf⟧)."))

    # ------------------------------------------------------------ peso
    a(SEC("3.2", "peso", "Torque gravitacional"))
    a(P("O conjunto que gira com o braço tem o centro de massa a uma distância d de "
        "O e a um ângulo a_{CG} do eixo do braço, e"))
    a(EQ(("tg", r"\tau_{g} = \frac{Mgd\left| \cos\left( \theta_{\mathrm{el}} - 90^{\circ} + a_{CG} \right) \right|}{1000}")))
    a(P("O conjunto reúne o membro humano e o braço do exoesqueleto (elemento 8), "
        "cujo centro de massa é referido ao eixo da articulação 20 pela posição desse "
        "eixo no CAD (seção ⟦S:r_geo⟧). O braço do exoesqueleto desloca o centro de "
        f"massa do conjunto em a_{{CG}} = {f(mas['total']['cg_angulo_braco_grau'])}°, "
        f"e o máximo de τ_{{g}}, {f(mas['tau_g_pico'])} N·m, ocorre em "
        f"θ_{{el}} = {f(mas['theta_tau_g_pico'], 1)}°."))

    # ------------------------------------------------------------ trabalho virtual
    a(SEC("3.2", "vt2", "Formulação pelo princípio dos trabalhos virtuais"))
    assert SECOES["vt2"] == "3.2.9", SECOES["vt2"]
    a(P("O equilíbrio é escrito pelo trabalho virtual num giro δq do conjunto, "
        "em radianos, igual a δθ_{el} pela Equação (⟦E:lam⟧). Com o elemento 78 "
        "pontual e sem atrito e o elástico sem massa, o contato é um vínculo ideal, e "
        "realizam trabalho a força do elástico sobre a alavanca, o peso do conjunto e o "
        "torque τ_{u} do usuário. O vetor b vai de O ao ponto de aplicação da força do "
        "trecho ligado a A, com módulo b e a um ângulo β de OP, e f = −F u(ψ); como esse "
        "ponto é fixo na alavanca em cada regime, b e β são constantes:"))
    a(EQ(("vt2_bf", r"\mathbf{b} = b\,\mathbf{u}(q + \beta),\quad \delta W_{e} = \tau\,\delta q = \frac{(\mathbf{b}\times\mathbf{f})_{z}}{1000}\,\delta q,\quad (\mathbf{b}\times\mathbf{f})_{z} = bF\sin(q + \beta - \psi)")))
    a(P("com (b, β) = (‹e›, 0) no regime I, em que b = P, e (b, β) = (p, φ) no "
        "regime II, em que b = C_{78} (Equação (⟦E:P⟧)); com esses valores, "
        "b sin(q + β − ψ) é o braço m da Equação (⟦E:m⟧). Embora b salte de P para "
        "C_{78} na troca de regime, o torque é contínuo: no contato, A, o elemento 78 "
        "e P estão alinhados, f é paralelo a P − C_{78}, e (P − C_{78}) × f = 0."))
    a(P("Do lado do elástico, o giro δq muda s de (ds/dq) δq, e a força realiza o "
        "trabalho −F δs/1000; como o contato não realiza trabalho, igualar as duas "
        "expressões dá (b × f)_{z} = −F ds/dq, isto é, a Equação (⟦E:tv⟧). O peso "
        "realiza o trabalho τ_{g,s} δq, com τ_{g,s} = −M g x_{G}/1000 e "
        "x_{G} = d cos(θ_{el} − 90° + a_{CG}), de módulo τ_{g} (Equação (⟦E:tg⟧)). "
        "Somados os três trabalhos, o princípio dos trabalhos virtuais exige, para todo "
        "δq,"))
    a(EQ(("vt2_eq", r"\delta W = (\tau + \tau_{g,s} + \tau_{u})\,\delta q = 0\quad\Rightarrow\quad\tau_{u} = -(\tau + \tau_{g,s})")))
    a(P("com τ em N·m sob a hipótese K = K_{40} (seção ⟦S:dados⟧). Com aceleração nula e "
        "Q_{nc} = τ_{u}, a equação de movimento da seção ⟦S:din⟧ reduz-se a essa "
        "condição."))

    # ------------------------------------------------------------ dados
    a(SEC("3.2", "dados", "Dados da patente e identificação dos parâmetros"))
    a(P("As Figuras 16 e 17 da patente são apresentadas como representações "
        "exemplares das curvas de força que o dispositivo pode aplicar ao braço; "
        "o documento não informa se foram medidas ou calculadas, nem "
        "a configuração do dispositivo que as gerou. A abscissa é o ângulo de "
        "anteversão, com escala de 0° a 180° e grade a cada 20°. A ordenada não tem "
        "rótulo nem valores, apenas linhas de grade: há cinco divisões acima da "
        "linha de razão nula e uma abaixo (Figura ⟦F:pat16⟧). Segundo a patente, a "
        "ordenada da Figura 16 da patente é uma razão de torques: o torque causado "
        "pelo peso próprio do braço e pela força peso, sem indicação do corpo a que "
        "esta se refere, dividido pelo torque aplicado pelo dispositivo. As curvas "
        "partem de zero perto de 14° e crescem com o ângulo, e com essa definição a "
        "razão seria infinita onde o dispositivo não aplica torque. Das duas "
        "leituras como razão, só a inversa, torque do dispositivo dividido pelo "
        "torque do peso, é coerente com a figura, inclusive com a subida das curvas "
        "tracejada e contínua perto de 180°, onde o torque do peso tende a zero. "
        "Essa interpretação foi a adotada, e a divergência entre o texto e a figura "
        "fica registrada."))
    a(P("Segundo a patente, as três curvas da Figura 16 da patente foram geradas com um único "
        "atuador passivo, com pré-tensões diferentes: quase nula na curva pontilhada "
        "e crescente na tracejada e na contínua. A Figura 17 da patente mantém a pré-tensão e "
        "desloca o ponto de ataque do atuador, cuja distância ao eixo da articulação "
        "cresce da curva pontilhada para a contínua; o texto descreve a "
        "ordenada dessa figura como a força aplicável ao braço, sem outra "
        "definição."))
    a(LEG_F("pat16", "Figura 16 da EP 3 504 033 B1, razão de torques em função da "
                     "anteversão para três pré-tensões do mesmo atuador"))
    a(FIGURA("ottobock_tcc_fig_patente16.png", 6.0,
             "Reprodução da Figura 16 da EP 3 504 033 B1: três curvas, pontilhada, "
             "tracejada e contínua, em função da anteversão de 0 a 180 graus; "
             "ordenada sem escala."))
    a(PEQUENO("Fonte: Mizera et al. (2023), Figura 16, p. 31 do documento B1.", True))
    a(PEQUENO("Nota: página do documento girada para a orientação de leitura. A "
              "patente não traz rótulo nem escala na ordenada."))
    a(P("Os pontos das três curvas foram extraídos pelo autor e estão no arquivo "
        "fig16_curvas.csv (Tabela ⟦T:pontos⟧). A extração "
        "dividiu a leitura vertical por 21,1311 para obter a razão em divisões da "
        "grade, manteve a abscissa sem correção e teve erro mediano de sobreposição "
        "inferior a 0,5 px; a imagem e a resolução usadas na leitura não foram "
        "registradas. No documento B1, a figura está gravada a 300 ppp, com cerca de "
        "215,7 px por divisão vertical e 266,2 px para 20° da abscissa. Se o erro de "
        "0,5 px se refere à unidade da leitura vertical, ele corresponde a "
        f"{f(mc['sigma_div'])} divisão na ordenada e, na mesma unidade, a "
        f"{f(mc['sigma_grau'], 2)}° na abscissa. A incerteza da extração não foi "
        "avaliada de forma independente; a identificação, adiante, propaga esse erro "
        "mediano à identificação por sorteio."))
    a(P("A Figura 17 da patente não foi digitalizada. A seção ⟦S:r_varr⟧ faz apenas uma "
        "comparação visual com ela."))

    # ------------------------------------------------------------ identificação
    SECOES["ident"] = SECOES["dados"]
    a(P("A Figura 16 da patente informa s_{0} de duas maneiras que não dependem da escala da "
        "ordenada: pelo espaçamento entre as três curvas e pelo fim da curva "
        "pontilhada. O ajuste da forma de cada curva, com s_{0} e escala livres, dá "
        "uma terceira estimativa, que depende também do braço de momento e do torque "
        "do peso do modelo. A primeira foi adotada, e a segunda serve de "
        "verificação independente; a terceira é mantida como resultado secundário, "
        "pelas razões da seção ⟦S:r_forma⟧, e está descrita no Apêndice ⟦S:apA⟧."))
    a(P("O modelo da razão de torques é"))
    a(EQ(("mu", r"\mu\left( \theta_{\mathrm{el}};\ s_{0} \right) = \frac{\delta\, m}{1000\,\tau_{g}},\quad \hat{r} = c\,\mu")))
    a(P("em que r é a razão extraída, em divisões, e c um fator de escala. Como τ é "
        "linear em K, μ é o torque por unidade de rigidez dividido por τ_{g}, e c "
        "reúne K e o valor desconhecido de uma divisão da ordenada: c = K/σ, com σ "
        "a razão de torques que corresponde a uma divisão. A curva da patente não "
        "separa K de σ, e por isso K não é identificável a partir dela."))
    a(P("Salvo indicação em contrário, os procedimentos desta seção usam apenas os "
        f"pontos com 20° < θ_{{el}} < 165°. Abaixo de {f(g['theta_t'], 2)}°, o "
        "modelo está no regime II e depende da posição do elemento 78; os pontos entre "
        "20° e esse ângulo estão nesse regime, e a faixa de 40° a 150° da seção "
        "⟦S:r_s0⟧ mostra o efeito de excluí-los. Perto de 180°, τ_{g} tende a zero e "
        "a razão varia rapidamente com o ângulo."))
    a(P("As três curvas foram geradas com o mesmo atuador e pré-tensões diferentes; "
        "admite-se que a geometria e a rigidez sejam as mesmas nas três, "
        "hipótese testada pela coincidência dos fatores G_{i} (seção ⟦S:r_s0⟧). Com "
        "o elástico tracionado, a razão de cada curva i escreve-se"))
    a(EQ(("rG", r"r_{i}\left( \theta_{\mathrm{el}} \right) = G\left( \theta_{\mathrm{el}} \right)\left\lbrack s\left( \theta_{\mathrm{el}} \right) - s_{0,i} \right\rbrack,\quad G = \frac{K\, m}{1000\,\sigma\,\tau_{g}}")))
    a(P("em que G reúne o que as três curvas têm em comum: a rigidez, a escala da "
        "ordenada, o braço de momento e o torque do peso. Para duas curvas i e j, a "
        "razão r_{i}/r_{j} elimina G, e a relação resultante é linear nos "
        "comprimentos de referência:"))
    a(EQ(("pares", r"r_{j}\, s_{0,i} - r_{i}\, s_{0,j} = \left( r_{j} - r_{i} \right)s")))
    a(P("A Equação (⟦E:pares⟧) foi escrita em cada ponto extraído de uma curva, com "
        "a razão da outra interpolada linearmente no mesmo ângulo, para os seis "
        "pares ordenados de curvas, e cada equação foi dividida por r_{i} + r_{j}, "
        "para que os pontos de razão maior não dominem o ajuste. O sistema, com "
        f"{rz['n']} equações e três incógnitas, foi resolvido por mínimos quadrados "
        "lineares, sem procedimento iterativo nem ponto de partida. O método usa "
        "apenas s(θ_{el}) do circuito da seção ⟦S:cin⟧: não depende de K, de σ, de m "
        "nem de τ_{g}."))
    a(P("A robustez da identificação foi avaliada com outras faixas de θ_{el}, com "
        "ruído de extração, com o sinal de θ_{b,pose} oposto e com a abscissa da "
        "figura deslocada ou espelhada, e um teste sintético, com curvas montadas pelo "
        "próprio modelo a partir de valores conhecidos de s_{0}, confere a "
        "implementação; os procedimentos estão no Apêndice ⟦S:apA⟧."))
    apR(P("A identificação foi repetida nas faixas de θ_{el} de 15° a 170°, de 25° a "
          f"160° e de 40° a 150°; em {mc['n']} sorteios com ruído gaussiano de "
          f"{f(mc['sigma_px'], 1)} px, o erro mediano declarado na extração, nas duas "
          "coordenadas de cada ponto; com o sinal de θ_{b,pose} oposto; com a abscissa "
          "da figura deslocada de "
          f"±{f(abs(N['razoes']['deslocamento_abscissa']['valor']), 2)}°, diferença "
          "entre o contato calculado com p = 0 e o início das curvas, e num "
          f"deslocamento varrido de {f(DL['varredura']['de'], 0)}° a "
          f"+{f(DL['varredura']['ate'], 0)}°; e com a abscissa espelhada, "
          "θ_{el} → 180° − θ_{el}, como teste de discriminação. Nos casos de abscissa "
          "deslocada ou espelhada, a faixa de identificação vale para os ângulos da "
          "figura, e os pontos usados são os mesmos da faixa adotada."))
    a(P("Uma verificação independente vem do fim da curva pontilhada, de "
        "pré-tensão quase nula. Como s decresce com θ_{el}, Equação "
        "(⟦E:tv⟧), o elástico afrouxa primeiro com o braço elevado, e a razão da "
        "curva menos tensionada deve chegar a zero onde s = s_{0}. O ângulo desse "
        "zero foi obtido por extrapolação linear dos dois e dos três últimos pontos "
        "da curva."))
    a(P("Com os valores identificados, o fator de cada curva é"))
    a(EQ(("Gi", r"G_{i}\left( \theta_{\mathrm{el}} \right) = \frac{r_{i}\left( \theta_{\mathrm{el}} \right)}{s\left( \theta_{\mathrm{el}} \right) - s_{0,i}}")))
    a(P("A coincidência das três estimativas testa a hipótese de G comum. A média "
        "das curvas tracejada e contínua, de maior extensão, é comparada à forma "
        "m/(1000 τ_{g}) prevista pelo modelo, com as duas normalizadas em 90°."))
    apF(P("No ajuste de forma, para cada s_{0}, a escala e a soma dos quadrados dos "
        "resíduos têm forma fechada:"))
    apF(EQ(("sse", r"c = \frac{\sum_{i}\mu_{i}r_{i}}{\sum_{i}\mu_{i}^{2}},\quad SSE = \sum_{i}\left( c\mu_{i} - r_{i} \right)^{2},\quad RMSE = \sqrt{SSE/n}")))
    apF(P("O mínimo foi procurado em s_{0} de 0 a 390 mm, em grade de 0,01 mm, e "
        "refinado pelo método de Brent limitado (BRENT, 1973) entre os vizinhos do "
        "melhor ponto, com a biblioteca SciPy (VIRTANEN et al., 2020). Valores "
        "negativos de s_{0} não correspondem a um elástico ligado diretamente entre "
        "A e P e foram excluídos. A faixa de identificação é o intervalo de s_{0}, "
        "na mesma grade, em que a raiz do erro quadrático médio não excede 1,01 vez "
        f"o mínimo. Dos {n_aj} pontos ajustados, {n_aj_II} ficam no regime II, entre "
        f"20° e {f(g['theta_t'], 2)}°. A Tabela "
        "⟦T:forma⟧ reúne os resultados, e a Figura ⟦F:ajustes⟧(a) sobrepõe as curvas "
        "ajustadas aos pontos extraídos."))
    apF(P("A patente atribui as três curvas a um único atuador e as desenha no "
        "mesmo eixo, o que implica K e σ comuns e, portanto, um único c. Esse ajuste "
        "conjunto foi feito como verificação independente da hipótese do modelo, "
        "com c comum e um s_{0} por curva:"))
    apF(EQ(("cconj", r"c = \frac{\sum_{j}\sum_{i}\mu_{ij}r_{ij}}{\sum_{j}\sum_{i}\mu_{ij}^{2}}")))
    apF(P("com j a curva e i o ponto. Os três valores de s_{0} foram buscados por "
        "descida coordenada na mesma grade, a partir de 125 combinações iniciais, "
        "com refinamento de Brent. A Tabela ⟦T:conj⟧ compara o resultado com os "
        "ajustes individuais e com uma força constante, forma limite do modelo "
        "quando s_{0} tende a valores muito negativos; a Figura ⟦F:ajustes⟧(b) mostra "
        "o ajuste conjunto."))
    a(P("Para expressar o torque em N·m, K foi fixado por hipótese de projeto, e "
        "não identificado. O alvo é 40% do torque do peso em θ_{el} = 90°; o "
        "percentual é hipótese do autor, baseada na alegação comercial de que o "
        "exoesqueleto IX Shoulder Air reduz em 40% ou mais a sobrecarga no ombro "
        "durante o trabalho acima da cabeça (SUITX, [202-]). A alegação não consta "
        "da patente, não informa as condições em que a redução foi medida e não foi "
        "verificada neste trabalho; o alvo adota o menor valor alegado. O valor "
        "correspondente é"))
    a(EQ(("k40", r"K_{40} = \frac{0{,}4\,\tau_{g}\left( 90^{\circ} \right) \cdot 1000}{\delta\left( 90^{\circ} \right)\,m\left( 90^{\circ} \right)}")))
    a(P("calculado com o s_{0} adotado. Como F(90°) = 0,4 τ_{g}(90°)·1000/m(90°) não "
        "depende de s_{0}, a força em 90° é a mesma para qualquer s_{0}; o valor "
        "escolhido muda K_{40} e a distribuição da força no restante da faixa."))

    # ------------------------------------------------------------ varredura
    a(SEC("3.2", "varr", "Varredura paramétrica do trecho e_{c} da alavanca"))
    a(P("O comprimento e_{c}, do pivô ao pino do rasgo da alavanca, é o comprimento "
        "‹e› do segmento OP, isto é, a excentricidade do ponto de aplicação, um dos "
        "parâmetros de ajuste previstos na patente e objeto da Figura 17 da "
        "patente. A "
        f"varredura manteve s_{{0}} = {f(pr['s0'])} mm e "
        f"K = {f(pr['K'], 5)} N/mm, isto é, o mesmo elástico, e variou apenas "
        "e_{c}, de 20 a 50 mm em passo de 0,05 mm, com o acréscimo do valor do CAD, num "
        f"total de {var['n']} valores. As demais grandezas ficaram congeladas nos "
        "valores da Tabela ⟦T:cad⟧. Trata-se de diagnóstico, e nenhum parâmetro é "
        "substituído pelo resultado."))

    # ------------------------------------------------------------ verificações
    a(SEC("3.2", "verif", "Verificações numéricas"))
    a(P("As verificações estão na Tabela ⟦T:verif⟧: são "
        "asserções executadas a cada cálculo, com tolerância declarada, que "
        "interrompem o cálculo se alguma for violada, e não um conjunto de testes "
        "executado com o pytest. Além das equações de fechamento e do trabalho "
        "virtual, elas conferem a continuidade na troca de regime e o caso limite "
        "p = 0, e o modelo confere ainda que o regime II ocorre exatamente "
        "para q ≤ q*, que o elemento 78 fica entre A e P na transição e que toda a "
        f"cadeia depende de e_{{c}}. Os valores são de e_{{c}} = {f(34.785)} mm, com "
        "s_{0} e K do cenário de projeto, em malha de 0,1° de 0° a 180°; a "
        "identificação pelo espaçamento entre as curvas é conferida pelo teste "
        "sintético da seção ⟦S:ident⟧."))

    # ------------------------------------------------------------ dinâmica
    a(SEC("3.2", "din", "Etapas dinâmicas previstas"))
    a(P("Pela formulação de Lagrange, a equação de movimento seria "
        "I_{O} d^{2}q/dt^{2} = τ + τ_{g,s} + Q_{nc}, com q como coordenada "
        "generalizada, τ o torque do elástico, τ_{g,s} o torque do peso com sinal e "
        "Q_{nc} os esforços não conservativos. Pela Equação (⟦E:tv⟧), a "
        "energia elástica V_{e} = K δ^{2}/2 satisfaz dV_{e}/dq = −K δ m, de modo que a "
        "força generalizada elástica coincide, a menos do fator 1/1000, com o torque "
        "da Equação (⟦E:m⟧); esse pré-requisito estático está verificado (Tabela "
        "⟦T:verif⟧). A integração não foi executada: o torque só está em N·m sob a "
        "hipótese K = K_{40}, o momento de inércia disponível, "
        f"I_{{O}} = {f(mas['total']['izz_o_kgm2'], 6)} kg·m^{{2}}, reúne o membro "
        "humano e o braço do exoesqueleto sem a alavanca e a braçadeira, e Q_{nc} não "
        "pode ser escrito, porque massa e amortecimento do elástico e atrito no "
        "elemento 78 e na articulação 20 são desconhecidos. Nenhum resultado dinâmico "
        "é apresentado."))

    # ------------------------------------------------------------ ferramentas
    a(SEC("3.2", "ferr", "Ferramentas e delimitação"))
    a(P("Foram empregados o Autodesk Fusion, para fechar o circuito do mecanismo e "
        "extrair as propriedades de massa do braço do exoesqueleto; uma planilha "
        "eletrônica, para a composição inercial; e a linguagem Python, com as "
        "bibliotecas NumPy (HARRIS et al., 2020), para o cálculo vetorizado, SciPy "
        "(VIRTANEN et al., 2020), para o refinamento pelo método de Brent (BRENT, "
        "1973) no ajuste de forma, e Matplotlib (HUNTER, 2007), para as figuras. A "
        "identificação pelo espaçamento entre as curvas é um problema de mínimos "
        "quadrados lineares, resolvido em forma fechada, e o MBDyn não foi empregado. "
        "Valem as exclusões de escopo da seção 3. O modelo é "
        "plano, restrito ao plano sagital, e admite elástico linear e sem massa, "
        "F = K δ, elemento 78 pontual e sem atrito e eixo da articulação 20 no centro "
        "do ombro, com a barra 18 fixa em relação ao tronco (seção ⟦S:conv⟧). O "
        "torque gravitacional considera o membro de referência e o braço do "
        "exoesqueleto; a alavanca, o elemento 78 e a braçadeira não entram nele."))
    return B


# ======================================================================
# capítulo 4
# ======================================================================

def parte_3D():
    """Seção 3.4: o que difere entre as três formulações."""
    SECOES["comp_met"] = "3.4"
    return [
        H("3.4 Comparação entre as formulações"),
        P("A Tabela ⟦T:comp_met⟧ reúne o que distingue as formulações das seções 3.1, "
          "3.2 e 3.3. Nas três, a variável independente é q, e o trabalho virtual dá "
          "o braço de momento como a derivada, em relação a q, do comprimento do "
          "caminho do elemento elástico, mas com sinais diferentes, porque q decresce "
          "quando o braço sobe nos exoesqueletos 1 e 3 e cresce no 2."),
        LEG_T("comp_met", "Elementos das formulações dos três exoesqueletos"),
        TABELA(
            ["Aspecto", "US 9.889.554 B2 (seção 3.1)", "EP 3 504 033 B1 (seção 3.2)",
             "US 9.737.374 B2 (seção 3.3)"],
            [["Arquitetura", "Mola, cabo e tambor entre elo proximal e elo distal",
              "Elástico ligado diretamente da barra à alavanca, com elemento de encosto "
              "junto à articulação",
              "Cabo de ancoragem, par de polias com came de raio variável e mola no apoio "
              "de braço"],
             ["Variável independente", "q, θ* referido ao desenho (Equação (2))",
              "q, direção da alavanca OP (Equação (⟦E:lam⟧))",
              "q, ângulo entre C_{2} e a horizontal (Equação (⟦E:e3_Theta⟧))"],
             ["Abscissa da patente",
              "θ*, ângulo interno entre os elos; elevação pela Equação (4)",
              "θ_{el}, anteversão",
              "Θ, eixo maior com a horizontal; elevação Θ + 90°"],
             ["Fechamento e incógnitas", "Equações (⟦E:e1_f1⟧) e (⟦E:e1_f2⟧), com s e φ",
              "Equações (⟦E:f1⟧) a (⟦E:f4⟧), em dois regimes, com s e ψ",
              "Equações (⟦E:e3_f1⟧) e (⟦E:e3_f2⟧), com S e φ"],
             ["Ponto de aplicação da força", "Ponto de tangência no tambor, móvel",
              "P no regime I e centro do elemento 78 no regime II, fixos na alavanca",
              "Ponto de tangência na polia primária; a mola atua pelo raio efetivo do came"],
             ["Trabalho virtual", "dℓ/dq = m, Equação (17)",
              "ds/dq = −m, Equação (⟦E:tv⟧)",
              "τ = (F_{s}/1000) dx/dq, Equação (⟦E:e3_vt⟧)"],
             ["Parâmetro varrido", "h, posição da ancoragem (seção 3.1.11)",
              "e_{c}, trecho da alavanca (seção ⟦S:varr⟧)",
              "Giro do came em relação à primária (seção ⟦S:e3_varr⟧)"]],
            [1500, 2620, 2620, 2620]),
        PEQUENO("Fonte: elaborada pelo autor, com as seções 3.1, 3.2 e 3.3.", True),
    ]


def cap4_introducao():
    return [P("Os resultados estão organizados por dispositivo. A seção 4.1 apresenta "
              "os do gerador de torque da US 9.889.554 B2; a seção 4.2, os do "
              "dispositivo da EP 3 504 033 B1; a seção 4.3, os do mecanismo de came "
              "da US 9.737.374 B2; e a seção 4.4 compara os três."),
            H("4.1 Exoesqueleto 1")]


def parte_4B():
    B = []
    a = B.append
    apR, apF = APENDICE["A_rob"].append, APENDICE["A_forma"].append
    a(H("4.2 Exoesqueleto 2"))
    a(P("Esta seção apresenta os resultados das etapas das seções ⟦S:cad⟧ a "
        "⟦S:verif⟧, aplicadas ao dispositivo da EP 3 504 033 B1. Salvo indicação em "
        f"contrário, os números foram obtidos com a geometria do CAD, e_{{c}} = {f(34.785)} "
        f"mm, s_{{0}} = {f(pr['s0'])} mm, identificado pelo espaçamento entre as "
        f"curvas da Figura 16 da patente, e K = K_{{40}} = {f(pr['K'], 5)} N/mm, "
        "hipótese de projeto. As etapas dinâmicas da seção ⟦S:din⟧ não foram "
        "executadas."))

    # ------------------------------------------------------------ geometria
    a(SEC("4.2", "r_geo", "Geometria reconstruída e propriedades de massa"))
    a(P("A Tabela ⟦T:cad⟧ reúne as grandezas medidas no modelo em CAD e as que delas "
        "derivam, com a origem de cada uma (seção ⟦S:cad⟧)."))
    a(LEG_T("cad", "Grandezas medidas no modelo em CAD e grandezas derivadas"))
    a(TABELA(
        ["Grandeza", "Símbolo", "Valor", "Unidade", "Origem"],
        [["Componente do vetor de A a O na direção u(−α)", "C_{1}",
          f(par["C1"]), "mm", "CAD"],
         ["Componente do vetor de A a O na direção u(γ)", "C_{2}",
          f(par["C2"]), "mm", "CAD"],
         ["Direção de C_{2}", "γ", f(par["GAMMA"]), "graus", "CAD"],
         ["Direção de C_{1}, perpendicular a C_{2}", "α", f(der["alpha"]),
          "graus", "Derivada, α = 90° − γ"],
         ["Trecho do pivô ao pino do rasgo da alavanca, ‹e› do modelo", "e_{c}",
          f(g["E_CAD"]), "mm", "CAD; varrido na seção ⟦S:r_varr⟧"],
         ["Peça de fixação do elástico, articulada no pino", "C_{3}", f(par["C3"]),
          "mm", "CAD; só no fechamento com s_{pose}"],
         ["Giro da peça em relação a e_{c}, na pose do CAD", "β_{c}", f(par["BETA"]),
          "graus", "CAD; só no fechamento com s_{pose}"],
         ["Distância do pivô ao centro do elemento 78", "p", f(par["P"]),
          "mm", "CAD"],
         ["Ângulo do trecho e_{c} na pose do CAD", "q_{c,pose}", f(par["Q_POSE"]),
          "graus", "CAD"],
         ["Comprimento de A à ponta da peça, na pose do CAD", "s_{pose}",
          f(par["S_POSE"]), "mm", "CAD"],
         ["Direção do centro do elemento 78 na pose do CAD", "q_{78,pose}",
          f(par["PHI_ABS_POSE"]), "graus", "CAD"],
         ["Ângulo do braço com a horizontal na pose do CAD, positivo acima",
          "θ_{b,pose}", f(par["BRACO_POSE"]), "graus", "CAD; sinal conferido"],
         ["Direção de OP na pose do CAD", "q_{pose}", f(par["Q_POSE"] + EPS),
          "graus", "Derivada, igual a q_{c,pose}"],
         ["Comprimento do elástico de A a P, na pose do CAD", "s", f(g["s_pose_modelo"]),
          "mm", "Derivada, Equação (⟦E:solI⟧)"],
         ["Defasagem entre a direção de p e q", "φ", f(PHI_S),
          "graus", "Derivada, seção ⟦S:cin⟧"],
         ["Defasagem entre q e θ_{el} + 90°", "q_{0}", f(der["delta"] + EPS), "graus",
          "Derivada, Equação (⟦E:lam0⟧)"],
         ["Anteversão na pose do CAD", "θ_{el,pose}", f(der["theta_pose"]),
          "graus", "Derivada, Equação (⟦E:lam0⟧)"],
         ["Distância de A a O", "|r_{AO}|", f(g["modulo_B"]), "mm",
          "Derivada, Equação (⟦E:rAO⟧)"],
         ["Comprimento do trecho entre o elemento 78 e P", "x", f(X_S),
          "mm", "Derivada, Equação (⟦E:d78⟧)"]],
        [3560, 1200, 1000, 1100, 2500], ["left", "center", "center", "center", "left"]))
    a(FONTE)
    a(PEQUENO("Nota: ângulos medidos a partir de +x, no sentido anti-horário (seção "
              "⟦S:conv⟧). O valor de e_{c} foi conferido no modelo em CAD."))
    a(P(f"Na pose do CAD, o modelo situa P, no pino do rasgo, em ({f(g['P_pose'][0])}; "
        f"{f(g['P_pose'][1])}) mm e o centro do elemento 78 em "
        f"({f(g['C78_pose'][0])}; {f(g['C78_pose'][1])}) mm. Com a peça de fixação "
        f"como desenhada no CAD, a ponta dela fica em ({f(g['P_cad_pose'][0])}; "
        f"{f(g['P_cad_pose'][1])}) mm, e o circuito dá s = {f(g['s_pose_cad'], 4)} mm "
        "até ela, que difere do comprimento medido "
        f"s_{{pose}} em {sci(g['erro_s_pose'])} mm, valor inferior à resolução de "
        "três casas decimais da medida; até o pino, o comprimento do elástico na "
        f"pose é de {f(g['s_pose_modelo'])} mm. O elemento 78 está a "
        f"p = {f(par['P'])} mm do eixo da articulação, enquanto a patente "
        "prefere esse elemento sobre o eixo; as consequências dessa "
        "diferença são tratadas nas seções ⟦S:zero⟧ e ⟦S:r_conf⟧."))
    a(LEG_T("massa", "Propriedades de massa do conjunto que gira com o braço em "
                     "relação ao eixo da articulação 20"))
    linhas = []
    for nm, rot in (("braço", "Braço"), ("antebraço", "Antebraço"), ("mão", "Mão")):
        c = corpos[nm]
        L = next(s["L"] for s in mas["segmentos_de_leva"] if s["nome"] == nm)
        linhas.append([rot, f(c["massa"], 4), f(L, 1), f(c["d"]),
                       f(c["izz_cg"], 6), f(c["izz_o"], 6)])
    linhas.append(["Membro humano", f(hum["massa_kg"], 4), "",
                   f"d = {f(hum['cg_raio_mm'])}", f(hum["izz_cg_kgm2"], 6),
                   f(hum["izz_o_kgm2"], 6)])
    cx = corpos["braço do exo"]
    linhas.append(["Braço do exoesqueleto (elemento 8)", f(cx["massa"], 4), "",
                   f(cx["d"]), f(cx["izz_cg"], 6), f(cx["izz_o"], 6)])
    tot = mas["total"]
    linhas.append(["Conjunto", f(tot["massa_kg"], 4), "",
                   f"d = {f(tot['cg_raio_mm'])}", f(tot["izz_cg_kgm2"], 6),
                   f(tot["izz_o_kgm2"], 6)])
    a(TABELA(["Segmento", "Massa (kg)", "L (mm)", "Distância do centro de massa a O "
              "(mm)", "I_{cm} (kg·m^{2})", "I_{O} (kg·m^{2})"], linhas,
             [1660, 1300, 1100, 2100, 1600, 1600],
             ["left", "center", "center", "center", "center", "center"]))
    a(PEQUENO("Fonte: elaborada pelo autor, com dados de de Leva (1996) e do "
              "modelo em CAD.", True))
    a(P("A consistência foi conferida pelo teorema de Steiner: para o membro humano, "
        f"I_{{cm}} + M d^{{2}} = {f(hum['izz_cg_kgm2'], 6)} + "
        f"{f(hum['izz_o_kgm2'] - hum['izz_cg_kgm2'], 6)} = "
        f"{f(hum['izz_o_kgm2'], 6)} kg·m^{{2}}, e, para o conjunto, "
        f"{f(tot['izz_cg_kgm2'], 6)} + {f(tot['izz_o_kgm2'] - tot['izz_cg_kgm2'], 6)} = "
        f"{f(tot['izz_o_kgm2'], 6)} kg·m^{{2}}. A amplitude do momento "
        f"gravitacional é M g d = {f(mas['tau_g_pico_humano'])} N·m para o membro "
        f"e {f(mas['tau_g_pico'])} N·m para o conjunto."))
    bx = mas["braco_exo"]
    a(P(f"No modelo em CAD, o braço do exoesqueleto (elemento 8) tem massa de "
        f"{f(bx['massa_g'])} g, centro de massa em ({f(bx['cg_fusion'][0])}; "
        f"{f(bx['cg_fusion'][1])}) mm no referencial do Fusion e momento de inércia "
        f"de {sci(bx['izz_cg_gmm2'], 3)} g·mm^{{2}} no centro de massa. São "
        "estimativas obtidas da geometria reconstruída e de um material atribuído no "
        "CAD, náilon 6/6 em peça oca segundo a planilha, e não propriedades do "
        "produto. O eixo da articulação 20 está em "
        f"({f(bx['o_fusion'][0])}; {f(bx['o_fusion'][1])}) mm no mesmo referencial, "
        f"de modo que o centro de massa fica a {f(cx['d'])} mm do eixo. Admitidos os "
        "eixos do Fusion paralelos aos do modelo, esse vetor foi levado ao eixo do "
        "braço pela direção do braço na pose do CAD, cujo sinal foi conferido no "
        "CAD (seção ⟦S:conv⟧), e somado ao membro humano pelo teorema de Steiner. "
        "O braço do exoesqueleto acrescenta "
        f"{f(cx['massa'], 4)} kg ao conjunto e desloca seu centro de massa em "
        f"{f(tot['cg_angulo_braco_grau'])}° em relação ao eixo do braço. A "
        "alavanca, o elemento 78 e a braçadeira não estão modelados como corpos "
        "separados, e as peças do lado do tronco (barra 18, barra de ancoragem e "
        "capas do elástico) apoiam-se no cinto e não giram com o braço."))

    # ------------------------------------------------------------ dados
    a(SEC("4.2", "r_dados", "Dados extraídos da patente"))
    ini = {n: fg[n]["inicio"] for n in ORDEM}
    rmin = {n: FIG16[n]["razao"][0] for n in ORDEM}
    po_max = FIG16["pontilhada"]["razao"].max()
    th_po = FIG16["pontilhada"]["theta"][FIG16["pontilhada"]["razao"] == po_max]
    tt, rt_ = FIG16["tracejada"]["theta"], FIG16["tracejada"]["razao"]
    pat = rt_[(tt >= 100.0) & (tt <= 150.0)]
    a(P(f"Foram extraídos {fg['tracejada']['n_total']} pontos da curva tracejada, "
        f"{fg['pontilhada']['n_total']} da pontilhada e {fg['continua']['n_total']} "
        "da contínua (Tabela ⟦T:pontos⟧). As três começam com razão ligeiramente "
        f"negativa, de {f(max(rmin.values()), 4)} a {f(min(rmin.values()), 4)} "
        "divisão, efeito da leitura, e cruzam zero, por interpolação linear entre os "
        f"dois primeiros pontos, em {f(ini['tracejada'], 2)}° (tracejada), "
        f"{f(ini['pontilhada'], 2)}° (pontilhada) e {f(ini['continua'], 2)}° "
        "(contínua). A curva pontilhada tem máximo interior de "
        f"{f(po_max, 4)} divisão, lido em {len(th_po)} pontos entre "
        f"{f(th_po.min(), 2)}° e {f(th_po.max(), 2)}°, e termina em "
        f"{f(FIG16['pontilhada']['razao'][-1], 4)} divisão em "
        f"{f(FIG16['pontilhada']['theta'][-1], 2)}°. A contínua cresce até "
        f"{f(fg['continua']['r_max'], 4)} divisões em "
        f"{f(fg['continua']['theta_r_max'], 2)}°, e a tracejada, depois de um patamar "
        f"entre {f(pat.min(), 2)} e {f(pat.max(), 2)} divisão de cerca de 100° a 150°, "
        f"sobe até {f(fg['tracejada']['r_max'], 4)} divisões em "
        f"{f(fg['tracejada']['theta_r_max'], 2)}°."))
    a(LEG_T("pontos", "Pontos extraídos da Figura 16 da patente (razão em divisões "
                      "da grade)"))
    nmax = max(len(FIG16[n]["theta"]) for n in ORDEM)
    linhas = []
    for i in range(nmax):
        lin = [str(i + 1)]
        for n in ("tracejada", "pontilhada", "continua"):
            th, r = FIG16[n]["theta"], FIG16[n]["razao"]
            if i < len(th):
                fora = not (20.0 < th[i] < 165.0)
                ft = f(th[i], 2)
                fr = f(r[i], 4)
                lin += [f"({ft})" if fora else ft, f"({fr})" if fora else fr]
            else:
                lin += ["", ""]
        linhas.append(lin)
    a(TABELA(["Nº", "Tracejada\nθ_{el} (°)", "Tracejada\nrazão",
              "Pontilhada\nθ_{el} (°)", "Pontilhada\nrazão",
              "Contínua\nθ_{el} (°)", "Contínua\nrazão"], linhas,
             [720, 1440, 1440, 1440, 1440, 1440, 1440], ["center"]*7))
    a(PEQUENO("Fonte: elaborada pelo autor, a partir da EP 3 504 033 B1 (MIZERA et al., "
              "2023).", True))
    a(PEQUENO("Nota: valores entre parênteses ficam fora da faixa 20° < θ_{el} < "
              "165° usada na identificação (seção ⟦S:ident⟧)."))

    # ------------------------------------------------------------ verificações
    a(SEC("4.2", "r_verif", "Verificação da cadeia de cálculo"))
    sint = rz["sintetico"]
    a(P("As verificações automáticas da seção ⟦S:verif⟧ resultaram nos resíduos da "
        "Tabela ⟦T:verif⟧, todos da ordem do erro de arredondamento da aritmética de "
        "ponto flutuante, exceto os do trabalho virtual, limitados pelo truncamento "
        "da diferença finita, e o do fechamento com o CAD, limitado pela resolução "
        "da medida. No teste sintético, a identificação pelo espaçamento entre as "
        f"curvas recupera os valores de s_{{0}} com erro máximo de "
        f"{f(sint['erro_max'])} mm, limitado pela interpolação linear entre os "
        "pontos de cada curva."))
    pz = ver["p_zero"]
    a(LEG_T("verif", "Verificações da cadeia de cálculo do modelo da Ottobock"))
    a(TABELA(
        ["Verificação", "Resíduo máximo"],
        [["Equações de fechamento do regime I, Equações (⟦E:f1⟧) e (⟦E:f2⟧)",
          f"{sci(max(ver['residuo_f1'], ver['residuo_f2']))} mm"],
         ["Equações de fechamento do regime II, Equações (⟦E:f3⟧) e (⟦E:f4⟧)",
          f"{sci(max(ver['residuo_f3'], ver['residuo_f4']))} mm"],
         ["x constante em q, Equação (⟦E:d78⟧)", f"{sci(ver['d_constante'])} mm"],
         ["Fechamento com o comprimento medido na pose do CAD",
          f"{sci(ver['erro_s_pose'])} mm"],
         ["Trabalho virtual no regime I, Equação (⟦E:tv⟧)",
          f"{sci(ver['tv_I'])} mm/rad"],
         ["Trabalho virtual no regime II, Equação (⟦E:tv⟧)",
          f"{sci(ver['tv_II'])} mm/rad"],
         ["Continuidade de s no contato",
          f"{sci(ver['continuidade_s'])} mm"],
         ["Continuidade de τ/F na transição",
          f"{sci(ver['continuidade_tau'])} mm"],
         ["Caso p = 0: q* numérico contra a Equação (⟦E:lamt⟧)",
          f"{sci(pz['erro_q'])} rad"],
         ["Caso p = 0: s = |r_{AO}| + ‹e› no regime II",
          f"{sci(pz['erro_s'])} mm"],
         ["Caso p = 0: τ no regime II, força unitária",
          f"{sci(pz['tau_max'])} N·mm"],
         ["τ pelo produto vetorial contra τ = F m/1000",
          f"{sci(ver['tau_duas_vias'])} N·m"],
         ["Linearidade em K, τ(K) = K τ(K = 1)", f"{sci(ver['erro_linear_K'])} N·m"],
         ["Ancoragem: s_{0} igual para todo e_{c} (s_{0} adotado)",
          f"{sci(ver['ancoragem'])} mm"],
         ["Espaçamento entre curvas: s_{0} conhecidos recuperados em curvas "
          "sintéticas", f"{f(sint['erro_max'])} mm"]],
        [6360, 3000], ["left", "center"]))
    a(FONTE)
    a(PEQUENO("Nota: o fechamento com o CAD é limitado pela resolução de três casas "
              "decimais da medida; o trabalho virtual, pelo truncamento da "
              "diferença finita centrada em q, com passo de 10^{−6} rad."))

    # ------------------------------------------------------------ s0 por razões
    a(SEC("4.2", "r_s0", "Identificação de s_{0} pelo espaçamento entre as curvas"))
    s0p, s0t, s0c = (s0r[n] for n in ORDEM)
    a(P("Pela Equação (⟦E:pares⟧), na faixa adotada, s_{0} vale "
        f"{f(s0p)} mm na curva "
        f"pontilhada, {f(s0t)} mm na tracejada e {f(s0c)} mm na contínua, com "
        f"RMSE de {f(rz['rms'])} mm nas {rz['n']} equações. A ordem coincide "
        "com a das pré-tensões descritas na patente, porque menor s_{0} significa "
        "maior extensão do elástico em qualquer ângulo, e os passos entre curvas, "
        f"{f(rz['passos']['pontilhada_tracejada'], 2)} e "
        f"{f(rz['passos']['tracejada_continua'], 2)} mm, são da mesma ordem. O "
        "modelo adota o s_{0} da curva tracejada, de pré-tensão intermediária entre "
        "as três, como configuração de referência; a seção ⟦S:r_conf⟧ mostra o "
        "efeito de adotar o das outras duas."))
    apR(LEG_T("s0r", "Comprimento de referência s_{0} identificado pelo espaçamento "
                   "entre as curvas da Figura 16 da patente"))

    def lin(rot, s0, rms):
        return [rot] + [f(s0[n]) for n in ORDEM] + [rms]
    esp = rz["abscissa_espelhada"]
    dl = rz["deslocamento_abscissa"]
    linhas = [lin("Faixa adotada, 20° a 165°", s0r, f(rz["rms"]))]
    for fx in ((15.0, 170.0), (25.0, 160.0), (40.0, 150.0)):
        linhas.append(lin(f"Faixa de {fx[0]:.0f}° a {fx[1]:.0f}°", rob[fx]["s0"],
                          f(rob[fx]["rms"])))
    linhas.append(["Ruído de 0,5 px, intervalo de 95%"]
                  + [f"{f(mc['p2_5'][n], 2)} a {f(mc['p97_5'][n], 2)}" for n in ORDEM]
                  + [""])
    linhas.append(["Ruído de 0,5 px, desvio padrão"]
                  + [f(mc["desvio"][n]) for n in ORDEM] + [""])
    def comsinal(x, n=2):
        return ("+" if x > 0 else "") + f(x, n)
    linhas.append(lin(f"Abscissa deslocada de {comsinal(-dl['valor'])}°",
                      dl["menos"]["s0"], f(dl["menos"]["rms"])))
    linhas.append(lin(f"Abscissa deslocada de {comsinal(dl['valor'])}°",
                      dl["mais"]["s0"], f(dl["mais"]["rms"])))
    linhas.append(lin("Sinal de θ_{b,pose} oposto", rz["braco_pose_invertido"],
                      f(rz["rms_braco_pose_invertido"])))
    linhas.append(lin("Abscissa espelhada, θ_{el} → 180° − θ_{el}", esp["s0"],
                      f(esp["rms"])))
    apR(TABELA(["Caso", "Pontilhada (mm)", "Tracejada (mm)", "Contínua (mm)",
              "RMSE das equações (mm)"], linhas, [2960, 1600, 1600, 1600, 1600],
             ["left", "center", "center", "center", "center"]))
    apR(FONTE)
    apR(PEQUENO(f"Nota: ruído gaussiano de {f(mc['sigma_px'], 1)} px na unidade da "
              f"leitura ({f(mc['sigma_div'])} divisão na ordenada e "
              f"{f(mc['sigma_grau'], 2)}° na abscissa), em {mc['n']} sorteios; a faixa "
              "adotada é a dos demais casos, exceto nas linhas de outras faixas; nas "
              "linhas de abscissa deslocada ou espelhada, ela vale para os ângulos da "
              "figura."))
    rob_t = [x["s0"]["tracejada"] for x in rz["robustez"]]
    pb = rz["projeto_braco_pose_invertido"]
    lim_inv = " (o limite inferior da busca)" if inv["s0"] < 1e-6 else ""
    a(P(f"A identificação é estável: entre as faixas de θ_{{el}} testadas, o "
        f"s_{{0}} da curva tracejada varia de {f(min(rob_t), 2)} a "
        f"{f(max(rob_t), 2)} mm, e o ruído de extração dá desvio padrão de "
        f"{f(mc['desvio']['tracejada'])} mm nessa curva. O sinal oposto de "
        f"θ_{{b,pose}} piora o espaçamento, com RMSE de "
        f"{f(rz['rms_braco_pose_invertido'])} mm contra {f(rz['rms'])} mm; o "
        "deslocamento da abscissa da figura praticamente não o melhora; e a abscissa "
        "espelhada deixaria o elástico frouxo em todos os ângulos. A Tabela ⟦T:s0r⟧ "
        "e os detalhes estão no Apêndice ⟦S:apA⟧."))
    apR(P(f"O sinal oposto de θ_{{b,pose}} levaria o s_{{0}} da tracejada a "
          f"{f(rz['braco_pose_invertido']['tracejada'], 2)} mm, com K_{{40}} de "
          f"{f(pb['K'], 5)} N/mm e pico de τ de {f(pb['tau_pico'])} N·m em "
          f"{f(pb['theta_pico'], 1)}°, e, no ajuste de forma, de {f(tr['s0'])} mm a "
          f"{f(inv['s0'])} mm{lim_inv}. O deslocamento de ±{f(abs(dl['valor']), 2)}° da "
          "abscissa, que levaria o contato calculado com p = 0 exatamente ao início das "
          "curvas, muda pouco o resultado, e o menor RMSE da varredura do deslocamento, "
          f"{f(dl['varredura']['rms_min'])} mm, ocorre em "
          f"{comsinal(dl['varredura']['d_min'])}°, praticamente sem ganho sobre a "
          "abscissa original. Com a abscissa espelhada, os três valores de s_{0} ficam "
          f"acima de s(0°) = {f(g['l_0'], 2)} mm, maior comprimento do elástico na faixa, "
          "o que o deixaria frouxo em todos os ângulos; essa leitura da figura é "
          "rejeitada."))
    col = rz["colapso"]
    lf = rz["l_figura_menos_cad"]
    a(P("Os fatores G_{i} da Equação (⟦E:Gi⟧) coincidem nas três curvas "
        f"(Figura ⟦F:razoes⟧(a)), com dispersão mediana de "
        f"{pct(col['dispersao_mediana'])} entre 20° e 165° e de no máximo "
        f"{pct(col['dispersao_max_ate_150'])} até 150°. Acima de 150°, a dispersão "
        f"cresce, até {pct(col['dispersao_max'], 1)} em "
        f"{f(col['theta_dispersao_max'], 0)}°, porque a extensão da curva "
        "pontilhada tende a zero e o quociente da Equação (⟦E:Gi⟧) fica mal "
        "condicionado. O comprimento do elástico lido no espaçamento entre as "
        "curvas pontilhada e contínua, s = (r_{c} s_{0,p} − r_{p} s_{0,c})/(r_{c} − "
        f"r_{{p}}), difere do s do CAD em {f(lf['rms'], 2)} mm RMS e no máximo "
        f"{f(lf['max_abs'], 2)} mm entre {lf['faixa'][0]:.0f}° e "
        f"{lf['faixa'][1]:.0f}°: a variação de s com o ângulo implícita na figura é "
        "a do modelo."))
    fim = rz["fim_pontilhada"]
    a(P("O fim da curva pontilhada confirma o resultado de forma independente. A "
        "razão dessa curva, extrapolada, chega a zero em "
        f"{f(fim['2']['theta'], 2)}° com os dois últimos pontos e em "
        f"{f(fim['3']['theta'], 2)}° com os três últimos, onde "
        f"s = {f(fim['2']['l'], 2)} e {f(fim['3']['l'], 2)} mm, a "
        f"{f(s0p - fim['2']['l'], 2)} e {f(s0p - fim['3']['l'], 2)} mm do s_{{0}} "
        "identificado pelo espaçamento; com esse s_{0}, o modelo afrouxa a partir de "
        f"{f(rz['theta_frouxo']['pontilhada'], 1)}°. A patente não diz em que "
        "posição a pré-tensão é medida. Interpretando a pré-tensão quase nula "
        "como extensão próxima de zero na posição de menor comprimento do "
        "elástico, perto de 180°, o s_{0} identificado é compatível com essa "
        "descrição: a curva pontilhada fica frouxa perto de 180°, com "
        f"s(180°) − s_{{0}} = {f(rz['pre_tensao_180']['pontilhada'], 2)} mm, e as "
        "curvas tracejada e contínua têm extensão de "
        f"{f(rz['pre_tensao_180']['tracejada'], 2)} e "
        f"{f(rz['pre_tensao_180']['continua'], 2)} mm em 180°."))
    ic = rz["inicio"]
    a(P("O ângulo em que as curvas começam, perto de 14°, não identifica s_{0}. As "
        f"três começam em {f(ic['pontilhada']['theta'], 2)}°, "
        f"{f(ic['tracejada']['theta'], 2)}° e {f(ic['continua']['theta'], 2)}°, "
        "apesar das pré-tensões diferentes, e o elástico se encurta quando o braço "
        "sobe: com s_{0} igual a s no início da curva tracejada, "
        f"{f(ic['tracejada']['l'], 2)} mm, o elástico ficaria frouxo em todos os "
        f"{milhar(ic['tracejada']['n_acima'])} pontos da malha acima desse ângulo, e "
        "o torque seria nulo justamente onde a figura o mostra. O contato do elástico "
        "com o elemento 78, cujo ângulo a patente ajusta pela posição desse elemento, "
        "explica esse início: com o elemento sobre o eixo, configuração preferida "
        f"pela patente, o contato calculado ocorre em {f(g['theta_t_p0'], 2)}°, a "
        f"{f(INICIO16 - g['theta_t_p0'], 2)}° do início médio das curvas, e o torque "
        "é nulo abaixo dele; com o elemento do CAD, a "
        f"{f(par['P'])} mm do eixo, o contato ocorre em {f(g['theta_t'], 2)}°, e o "
        "torque não se anula abaixo dele (seção ⟦S:r_conf⟧)."))
    a(LEG_F("razoes", "Identificação de s_{0} pelo espaçamento entre as curvas, com "
                      "(a) o fator G_{i} de cada curva e (b) o fator G lido na Figura "
                      "16 da patente e a forma prevista pelo modelo, normalizados em "
                      "90°"))
    a(FIGURA("ottobock_tcc_fig_a6_razoes.png", 6.5,
             "À esquerda, razão de cada curva dividida pela extensão do elástico, "
             "em função da anteversão, com as três curvas sobrepostas; à direita, "
             "fator comum lido na figura e forma prevista pelo modelo."))
    a(PEQUENO("Fonte: elaborada pelo autor, a partir da EP 3 504 033 B1 (MIZERA et al., "
              "2023).", True))
    a(PEQUENO("Nota: s_{0} identificado pelo espaçamento, na faixa adotada; em (b), média das curvas "
              "tracejada e contínua."))

    # ------------------------------------------------------------ forma
    a(SEC("4.2", "r_forma", "Forma das curvas e ajuste de forma"))
    fr = rz["forma"]["G_sobre_modelo"]
    lm = rz["forma"]["l_de_m_impl_menos_cad"]
    mcomp = rz["modelo_completo"]["curvas"]
    a(P("Com os valores de s_{0} da seção ⟦S:r_s0⟧, o fator G lido na Figura 16 da patente e a "
        "forma m/(1000 τ_{g}) do modelo diferem (Figura ⟦F:razoes⟧(b)). "
        "Normalizada em 90°, a razão entre os dois vale "
        f"{f(fr['20'], 2)} em 20°, {f(fr['60'], 2)} em 60°, {f(fr['120'], 2)} em "
        f"120°, {f(fr['150'], 2)} em 150° e {f(fr['165'], 2)} em 165°. Com esses "
        "valores de s_{0} e com o m do CAD e o τ_{g} do conjunto, a razão "
        "calculada não reproduz a Figura 16 da patente: com escala comum às três curvas, o "
        f"coeficiente de determinação é {f(mcomp['pontilhada']['comum']['r2'], 3)} "
        f"(pontilhada), {f(mcomp['tracejada']['comum']['r2'], 3)} (tracejada) e "
        f"{f(mcomp['continua']['comum']['r2'], 3)} (contínua). Como o s implícito na "
        "figura concorda com o do CAD (seção ⟦S:r_s0⟧), a diferença não se explica "
        "por s. Restam o braço de momento, que depende da derivada de s, e o torque "
        "do peso que a patente usou para formar a razão, que o texto não define de "
        "forma consistente (seção ⟦S:dados⟧). Entre 35° e 155°, atribuir ao braço de "
        "momento toda a diferença afastaria o s implícito do s do CAD, pela Equação "
        f"(⟦E:tv⟧), em até {f(lm['max_abs'], 2)} mm ({f(lm['rms'], 2)} mm RMS), "
        + (f"mais que os {f(lf['max_abs'], 2)} mm ({f(lf['rms'], 2)} mm RMS) "
           "observados: a concordância de s descarta o braço de momento como causa "
           "principal e favorece o torque do peso usado pela patente ou a definição "
           "da ordenada, que a patente não permite separar."
           if lm["rms"] > 2*lf["rms"] else
           f"menos que os {f(lf['max_abs'], 2)} mm ({f(lf['rms'], 2)} mm RMS) "
           "observados: a concordância de s não separa as duas causas, e a patente "
           "não traz dado que permita fazê-lo.")))
    a(P("O ajuste de forma da seção ⟦S:ident⟧ deixa s_{0} e a escala livres em cada "
        "curva e, por isso, absorve essa diferença em s_{0}. Os valores que ele "
        f"encontra (Tabela ⟦T:forma⟧, no Apêndice ⟦S:apA⟧), {f(po['s0'], 2)} mm na pontilhada, "
        f"{f(tr['s0'], 2)} mm na tracejada e {f(co['s0'], 2)} mm na contínua"
        + (", o limite inferior da busca," if co["limite"] == "inferior" else "")
        + " afastam-se "
        f"dos do espaçamento em {f(abs(po['s0'] - s0r['pontilhada']), 1)}, "
        f"{f(abs(tr['s0'] - s0r['tracejada']), 1)} e "
        f"{f(abs(co['s0'] - s0r['continua']), 1)} mm, e as escalas por curva contrariam "
        "o atuador único "
        "descrito na patente. São mantidos como resultado secundário: descrevem a melhor forma "
        "que o modelo consegue produzir com a geometria do CAD, e não a pré-tensão "
        "do dispositivo."))
    apF(LEG_T("forma", "Ajuste de s_{0} à forma de cada curva da Figura 16 da patente"))
    apF(TABELA(
        ["Indicador", "Pontilhada", "Tracejada", "Contínua"],
        [["Pontos usados, n"] + [str(ind[n]["n"]) for n in ORDEM],
         ["s_{0} (mm)"] + [s0txt(ind[n]) for n in ORDEM],
         ["Faixa de identificação de s_{0} (mm)"] + [faixa(ind[n]) for n in ORDEM],
         ["Escala c"] + [f(ind[n]["c"], 5) for n in ORDEM],
         ["RMSE (divisão)"] + [f(ind[n]["rms"], 4) for n in ORDEM],
         ["RMSE/máx"] + [pct(ind[n]["rms_max"]) for n in ORDEM],
         ["Erro absoluto médio (divisão)"] + [f(ind[n]["mae"], 4) for n in ORDEM],
         ["Erro máximo (divisão), em θ_{el}"] + [
             f"{f(ind[n]['erro_max'], 4)}, em {f(ind[n]['theta_erro_max'], 2)}°"
             for n in ORDEM],
         ["Coeficiente de determinação, R^{2}"] + [f(ind[n]["r2"], 4) for n in ORDEM],
         ["Zonas de sinal do resíduo"] + [str(ind[n]["zonas_sinal"]) for n in ORDEM],
         ["δ(90°) (mm)"] + [f(ind[n]["x_alvo"]) for n in ORDEM],
         ["K_{40} (N/mm), hipótese"] + [f(ind[n]["k_alvo"], 5) for n in ORDEM],
         ["σ = K_{40}/c, hipótese"] + [f(ind[n]["escala_div"], 4) for n in ORDEM]],
        [2900, 2150, 2150, 2160], ["left", "center", "center", "center"]))
    apF(FONTE)
    apF(PEQUENO("Nota: resíduo = cμ − r; RMSE/máx = raiz do erro quadrático médio "
              "dividida pelo maior valor extraído da curva na faixa do ajuste."))
    zs = [ind[n]["zonas_sinal"] for n in ORDEM]
    # onde ficam os maiores erros do ajuste de forma: no regime II (início das
    # curvas) ou no fim da faixa
    def onde_erro(x):
        if x["theta_erro_max"] < g["theta_t"]:
            return "no regime II do modelo, abaixo da transição"
        return "no fim da faixa, onde o elástico do modelo se aproxima do comprimento livre"
    grupos = {}
    for n in ORDEM:
        grupos.setdefault(onde_erro(ind[n]), []).append(NOME[n])

    def curvas(v):
        return (f"na curva {v[0]}" if len(v) == 1 else
                "nas curvas " + ", ".join(v[:-1]) + " e " + v[-1])
    apF(P(f"Os resíduos em {min(zs)} a {max(zs)} zonas de sinal indicam diferença "
          "sistemática de forma entre o modelo e as curvas, e os maiores erros ficam "
          + "; ".join(f"{k}, {curvas(v)}" for k, v in grupos.items())
          + f" (transição em {f(g['theta_t'], 2)}°)."))
    apF(P("Como as três curvas compartilham o mesmo eixo na patente, os valores distintos "
          "de σ = K_{40}/c na Tabela ⟦T:forma⟧ mostram que o alvo de 40% não pode valer "
          "para as três ao mesmo tempo com os s_{0} do ajuste de forma; "
          f"F(90°) = {f(tr['forca_alvo'], 2)} N é o mesmo nas três por construção, "
          "porque F(90°) = 0,4 τ_{g}(90°)·1000/m(90°) não depende de s_{0}."))
    apF(LEG_T("conj", "Ajuste conjunto com escala comum e ajuste com força constante"))
    pcj = cj["por_curva"]
    apF(TABELA(
        ["Indicador", "Pontilhada", "Tracejada", "Contínua"],
        [["s_{0}, ajuste individual (mm)"] + [s0txt(ind[n]) for n in ORDEM],
         ["s_{0}, ajuste conjunto (mm)"] + [f(pcj[n]["s0"]) for n in ORDEM],
         ["RMSE/máx, ajuste individual"] + [pct(ind[n]["rms_max"]) for n in ORDEM],
         ["RMSE/máx, ajuste conjunto"] + [pct(pcj[n]["rms_max"]) for n in ORDEM],
         ["R^{2}, ajuste conjunto"] + [f(pcj[n]["r2"], 4) for n in ORDEM],
         ["RMSE/máx, força constante"] + [pct(fc[n]["rms_max"]) for n in ORDEM],
         ["R^{2}, força constante"] + [f(fc[n]["r2"], 4) for n in ORDEM]],
        [2900, 2150, 2150, 2160], ["left", "center", "center", "center"]))
    apF(FONTE)
    apF(PEQUENO(f"Nota: no ajuste conjunto, c = {f(cj['c'], 4)}, comum às três "
              "curvas; na força constante, c é ajustado por curva."))
    apF(P("O ajuste conjunto ordena os comprimentos de referência como as pré-tensões "
        "descritas na patente, mas a curva pontilhada passa de RMSE/máx de "
        f"{pct(po['rms_max'])} para {pct(pcj['pontilhada']['rms_max'])}: com uma só "
        "escala, o modelo linear reproduz a ordem das pré-tensões, mas não a forma da "
        "curva de menor pré-tensão. A força constante descreve a curva "
        f"contínua com RMSE/máx de {pct(fc['continua']['rms_max'])}, "
        + (f"abaixo dos {pct(co['rms_max'])} do ajuste individual, que encosta no "
           "limite s_{0} = 0, "
           if fc["continua"]["rms_max"] < co["rms_max"] else
           f"contra {pct(co['rms_max'])} do ajuste individual, ")
        + f"e as outras duas com erros de {pct(fc['pontilhada']['rms_max'])} e "
        f"{pct(fc['tracejada']['rms_max'])}: "
        + ("só a curva de maior pré-tensão se aproxima de uma força constante."
           if fc["continua"]["rms_max"] < co["rms_max"] else
           "o elástico com s_{0} finito descreve melhor as três curvas.")))
    x180_po = g["l_180"] - po["s0"]
    x180_po_cj = g["l_180"] - pcj["pontilhada"]["s0"]
    x180_esp = rz["pre_tensao_180"]["pontilhada"]
    if max(x180_po, x180_po_cj, x180_esp) < 0:
        conclusao_180 = "nos três casos, o elástico fica frouxo perto de 180°."
        abertura_180 = "é compatível com os três ajustes"
    else:
        assert x180_esp < 0 < min(x180_po, x180_po_cj)
        conclusao_180 = ("só com o s_{0} do espaçamento o elástico fica frouxo perto "
                         "de 180°, como pede a descrição da patente.")
        abertura_180 = "distingue as identificações"
    a(P(f"A pré-tensão da curva pontilhada, descrita como quase nula, {abertura_180}. "
        "Pelo critério da seção ⟦S:r_s0⟧, a extensão em 180°, "
        f"essa curva teria {f(x180_po, 2)} mm com o s_{{0}} individual, "
        f"{f(x180_po_cj, 2)} mm com o do ajuste conjunto e "
        f"{f(x180_esp, 2)} mm com o do espaçamento: " + conclusao_180))
    apF(LEG_F("ajustes", "Pontos extraídos da Figura 16 da patente e razão calculada "
                       "pelo ajuste de forma, com (a) escala c por curva e (b) escala "
                       "c comum às três curvas"))
    apF(FIGURA("ottobock_tcc_fig_a2_fig16.png", 6.5,
             "Razão de torques em divisões da grade em função da anteversão: pontos "
             "extraídos das três curvas da Figura 16 da patente e curvas do modelo, com a faixa "
             "de 20 a 165 graus sombreada; à esquerda, escala por curva; à direita, "
             "escala comum."))
    apF(PEQUENO("Fonte: elaborada pelo autor, a partir da EP 3 504 033 B1 (MIZERA et al., "
              "2023).", True))
    apF(PEQUENO("Nota: faixa sombreada: 20° < θ_{el} < 165°, usada no ajuste; pontos "
              "cinza: fora dessa faixa."))

    # ------------------------------------------------------------ parâmetros
    a(SEC("4.2", "r_par", "Parâmetros do modelo"))
    a(P("A Tabela ⟦T:par⟧ resume a situação dos parâmetros que a patente não "
        "publica."))
    a(LEG_T("par", "Parâmetros não publicados, origem e identificabilidade"))
    a(TABELA(
        ["Parâmetro", "Símbolo", "Valor adotado", "Origem", "Situação"],
        [["Rigidez do elástico", "K", f"{f(pr['K'], 5)} N/mm",
          "Hipótese de projeto (K_{40})",
          "Não identificável pela Figura 16 da patente, cuja ordenada não tem escala"],
         ["Referência da extensão", "s_{0}", f"{f(pr['s0'])} mm",
          "Identificado pelo espaçamento entre as curvas (tracejada)",
          f"De {f(min(rob_t), 2)} a {f(max(rob_t), 2)} mm entre as faixas de "
          "θ_{el}"],
         ["Trecho da alavanca, que fixa a excentricidade |OP| do ponto de aplicação",
          "e_{c}", f"{f(34.785)} mm", "Medida em CAD",
          "Não identificado; varrido na seção ⟦S:r_varr⟧"],
         ["Posição do elemento 78", "p; φ",
          f"{f(par['P'])} mm; {f(PHI_S)}°", "Medida em CAD e derivada",
          "Não identificada; a patente prefere p = 0"],
         ["Defasagem angular", "q_{0}", f"{f(der['delta'] + EPS)}°",
          "Derivada do CAD", "Sinal de θ_{b,pose} conferido no CAD"],
         ["Massa e centro de massa do braço do exoesqueleto", "",
          f"{f(mas['braco_exo']['massa_g'])} g; {f(corpos['braço do exo']['d'])} mm",
          "Estimada no CAD, com material assumido", "Incluídos no peso e na inércia; eixos do Fusion "
          "admitidos paralelos aos do modelo"]],
        [2300, 1060, 1500, 2000, 2500], ["left", "center", "center", "left", "left"]))
    a(FONTE)

    # ------------------------------------------------------------ mecanismo
    a(SEC("4.2", "r_mec", "Comportamento do elástico e do mecanismo"))
    a(P(f"Na faixa de 0° a 180° de anteversão, q varia de {f(g['lambda_faixa'][0] + EPS)}° "
        f"a {f(g['lambda_faixa'][1] + EPS)}°, e o regime II ocupa θ_{{el}} de 0° a "
        f"{f(g['theta_t'])}°. O braço de momento permanece positivo em toda a "
        f"faixa, com mínimo de {f(g['b_t'])} mm na transição e máximo de "
        f"{f(g['m_max'])} mm em θ_{{el}} = {f(g['theta_m_max'], 1)}°, igual a |OP|: "
        "no regime I, a linha de ação passa por P, e m não pode exceder a "
        "distância do pivô a esse ponto. Como m não se anula, não há ponto morto na "
        "faixa. A "
        "Tabela ⟦T:circ⟧ reúne as grandezas do circuito em ângulos representativos."))
    a(LEG_T("circ", f"Grandezas do circuito em ângulos representativos "
                    f"(e_{{c}} = {f(34.785)} mm)"))
    linhas = []
    for l in N["tabela_geometria"]:
        regime = ("I e II (transição)" if abs(l["theta"] - g["theta_t"]) < 1e-9
                  else l["regime"])
        linhas.append([f(l["theta"]), f(l["lambda"] + EPS), regime, f(l["l"]),
                       f(l["phi"]), "" if l["l_menos_d"] is None else f(l["l_menos_d"]),
                       f(l["m"])])
    a(TABELA(["θ_{el} (°)", "q (°)", "Regime", "s (mm)", "ψ (°)", "s − x (mm)",
              "m (mm)"], linhas, [1250, 1250, 1400, 1350, 1250, 1500, 1360],
             ["center"]*7))
    a(FONTE)
    a(PEQUENO(f"Nota: a linha θ_{{el}} = {f(g['theta_t'])}° é a transição; a linha "
              f"θ_{{el}} = {f(der['theta_pose'])}° é a pose do CAD."))
    a(P(f"Com s_{{0}} = {f(pr['s0'])} mm, a extensão do elástico vai de "
        f"{f(pr['x_max'], 2)} mm com o braço pendente a {f(pr['x_min'], 2)} mm em "
        "180°, e o elástico permanece tracionado em toda a faixa. A deformação "
        f"máxima equivale a {pct(pr['deformacao_max'], 1)} do comprimento de "
        f"referência. Com K = K_{{40}}, a força vai de {f(pr['F_0'], 2)} N a "
        f"{f(pr['F_180'], 2)} N."))
    apF(P(f"Com o s_{{0}} do ajuste de forma da curva tracejada, {f(prf['s0'])} mm, a "
          f"extensão do elástico iria de {f(prf['x_max'], 2)} a {f(prf['x_min'], 2)} mm, "
          f"com deformação de {pct(prf['deformacao_max'], 1)}, e a força, com o "
          f"K_{{40}} correspondente, de {f(prf['F_0'], 2)} a {f(prf['F_180'], 2)} N, "
          "valores bem diferentes dos do cenário de projeto (seção ⟦S:r_mec⟧); a "
          "viabilidade dessas extensões depende do elemento elástico, que a patente "
          "não especifica."))

    # ------------------------------------------------------------ varredura e
    a(SEC("4.2", "r_varr", "Varredura paramétrica do trecho e_{c} da alavanca"))
    ftr = var["faixas"]["tracao"]
    l45 = fam["linhas"][-1]
    a(P("Dos três critérios de validade física, o fechamento dos dois regimes "
        "(s > 0 e s − x > 0) e o trabalho virtual foram atendidos em todos os valores "
        "de e_{c}, com resíduo "
        f"máximo de {sci(var['tv_max'])} mm/rad. A extensão não negativa do elástico "
        f"em toda a faixa só é atendida para e_{{c}} ≤ {f(ftr['max'], 2)} mm, em "
        f"{ftr['n']} dos {var['n']} valores: acima desse valor, com o s_{{0}} "
        "adotado, o elástico afrouxa perto de 180°, como mostra a curva de "
        f"e_{{c}} = {f(l45['e'], 0)} mm, frouxa de {f(l45['frouxo'][0][0], 2)}° a 180°. A "
        f"transição de regime desloca-se de θ_{{el}} = {f(var['theta_t'][1], 2)}° "
        f"(e_{{c}} = 20 mm) para {f(var['theta_t'][0], 2)}° (e_{{c}} = 50 mm). A Tabela "
        "⟦T:fam⟧ e a Figura ⟦F:fam⟧ mostram a família de curvas para cinco valores "
        "de e_{c}."))
    a(LEG_T("fam", f"Família de curvas em e_{{c}}, com s_{{0}} = {f(pr['s0'])} mm e "
                   f"K = {f(pr['K'], 5)} N/mm"))
    linhas = [[f(l["e"]), f(l["d78"]), f(l["theta_t"], 2), f(l["tau_pico"]),
               f(l["theta_pico"], 1), f(l["tau_90"]), f(l["razao_90"]),
               f(l["x_min"], 2), f(l["x_max"], 2)] for l in fam["linhas"]]
    a(TABELA(["e_{c} (mm)", "x (mm)", "θ_{el,t} (°)", "Pico de τ (N·m)",
              "θ_{el} do pico (°)", "τ(90°) (N·m)", "τ/τ_{g} em 90°",
              "δ_{mín} (mm)", "δ_{máx} (mm)"], linhas,
             [1000, 1000, 1000, 1100, 1100, 1040, 1040, 1040, 1040], ["center"]*9))
    a(FONTE)
    a(PEQUENO("Nota: τ em N·m depende da hipótese K = K_{40}; as posições dos picos "
              "e da transição não dependem de K. δ_{mín} negativo indica elástico "
              "frouxo."))
    no1, no2 = var["nos"]
    cz = fam["cruzamentos_e_extremos"][0]
    a(P(f"Nos ângulos abaixo de cerca de {f(cz, 0)}°, onde as curvas dos valores "
        "extremos de e_{c} se cruzam, o torque aumenta com e_{c}; acima desse ângulo, "
        "diminui. Com o aumento de e_{c}, o pico se desloca de "
        f"{f(fam['linhas'][0]['theta_pico'], 1)}° para "
        f"{f(fam['linhas'][-1]['theta_pico'], 1)}° e a transição ocorre mais cedo. "
        "Medido o espalhamento entre as curvas de τ/K, máximo menos mínimo em cada "
        f"θ_{{el}}, há dois nós, em {f(no1[0], 1)}° e {f(no2[0], 1)}°, e a abertura "
        f"máxima ocorre em {f(var['abertura_max'][0], 1)}°."))
    ext = {l["e"]: l["extremos_razao"] for l in fam["linhas"]}
    mx = [x for e_ in ext for x in ext[e_] if x["tipo"] == "max"]
    mn = [x for e_ in ext for x in ext[e_] if x["tipo"] == "min" and x["theta"] > 100]
    a(P("A Figura 17 da patente não foi digitalizada, e a comparação com ela é "
        "visual. Nela, as três curvas partem de perto de 14°; a de maior "
        "excentricidade, contínua, atinge o máximo perto de 100°, decresce e cruza "
        "as outras duas entre cerca de 155° e 160°, e as três sobem acentuadamente "
        "acima de 160°. O texto registra que, acima de cerca de 150°, o andamento "
        "difere do da Figura 16 da patente. No modelo, as curvas de τ/τ_{g} da família "
        f"têm máximo entre {f(min(x['theta'] for x in mx), 1)}° e "
        f"{f(max(x['theta'] for x in mx), 1)}°, que ocorre mais cedo quanto maior "
        f"o trecho e_{{c}}, e mínimo local entre {f(min(x['theta'] for x in mn), 1)}° e "
        f"{f(max(x['theta'] for x in mn), 1)}° nas curvas que permanecem "
        f"tracionadas; as curvas se cruzam perto de {f(cz, 0)}°. Qualitativamente, o "
        "modelo reproduz a sequência de máximo, vale e subida perto de 180°, mas com "
        "o máximo antes do da patente e o cruzamento das curvas mais cedo. A "
        "comparação quantitativa depende da digitalização da Figura 17 da patente, "
        "da definição de sua ordenada e dos valores de excentricidade, que a patente "
        "não informa."))
    a(LEG_F("fam", f"Família de curvas em e_{{c}}, com s_{{0}} = {f(pr['s0'])} mm, com "
                   "(a) o torque por unidade de rigidez e (b) a razão entre o torque "
                   "do elástico e o do peso com K = K_{40}"))
    a(FIGURA("ottobock_tcc_fig_a5_familia.png", 6.5,
             "Cinco curvas para o trecho e de 25 a 45 mm em função da anteversão: à "
             "esquerda, torque por unidade de rigidez; à direita, razão entre o "
             "torque do elástico e o do peso."))
    a(FONTE)

    # ------------------------------------------------------------ confronto
    a(SEC("4.2", "r_conf", "Confronto com o torque gravitacional"))
    ns = nrm["s0"]
    tre = {(round(t["ini"], 2), round(t["fim"], 2)): t for t in ns["trechos"]}
    cz_n = ns["cruzamentos"]
    t0, t1, t2, t3, t4 = ns["trechos"]
    assert (t0["extremo"] > 0 > t1["extremo"] and t2["extremo"] > 0 > t3["extremo"]
            and t4["extremo"] > 0 and len(cz_n) == 4), tre
    a(P("A forma do torque do elástico pode ser comparada à do peso sem depender de "
        "K, normalizando cada curva pelo próprio pico (Figura ⟦F:norm⟧). Com o "
        "s_{0} adotado, o pico normalizado do elástico ocorre em "
        f"θ_{{el}} = {f(ns['theta_pico_exo'], 1)}°, contra {f(nrm_peso_pico, 1)}° do peso, e as curvas "
        f"normalizadas se cruzam em {f(cz_n[0], 2)}° (regime II), "
        f"{f(cz_n[1], 2)}°, {f(cz_n[2], 2)}° e {f(cz_n[3], 2)}°. Abaixo de "
        f"{f(cz_n[0], 2)}°, a forma do elástico fica acima da do peso, que tende a "
        f"zero com o braço pendente; entre {f(cz_n[0], 2)}° e {f(cz_n[1], 2)}°, fica "
        f"abaixo, com diferença de até {f(t1['extremo'])} em {f(t1['theta'], 1)}°, "
        f"perto da transição; entre {f(cz_n[1], 2)}° e {f(cz_n[2], 2)}°, fica "
        f"ligeiramente acima, com no máximo +{f(t2['extremo'])} em "
        f"{f(t2['theta'], 1)}°; entre {f(cz_n[2], 2)}° e {f(cz_n[3], 2)}°, volta a "
        f"ficar abaixo, com diferença de até {f(t3['extremo'])} em "
        f"{f(t3['theta'], 1)}°; e acima de {f(cz_n[3], 2)}° fica de novo acima. "
        "Entre as faixas de θ_{el} testadas na identificação, o pico vai de "
        f"{f(nrm['faixa_max']['theta_pico_exo'], 1)}° a "
        f"{f(nrm['faixa_min']['theta_pico_exo'], 1)}°, de modo que essas "
        "conclusões não dependem da faixa escolhida. A posição do pico fica na faixa "
        "de 70° a 120° em que a patente prefere a força máxima, desde que essa "
        "força seja lida como a força de apoio sobre o braço, proporcional ao torque "
        "na articulação, interpretação do autor; a força do próprio elástico é máxima "
        "com o braço pendente. O mesmo parágrafo cita, como exemplo, força nula até "
        "45°, 60° ou 90°, preferência que nem a Figura 16 da patente, com razão não "
        "nula a partir de cerca de 14°, nem o modelo, com torque desde 0°, seguem; "
        "como esse ângulo é ajustável pela posição do elemento 78, os "
        "valores citados pela patente correspondem a regulagens para as quais a patente "
        "não publica curva."))
    nf = nrm_f["s0"]
    apF(P(f"Com o s_{{0}} do ajuste de forma, {f(prf['s0'])} mm, o pico normalizado "
        f"ficaria em {f(nf['theta_pico_exo'], 1)}°, e as curvas se cruzariam em "
        f"{f(nf['cruzamentos'][0], 2)}° e {f(nf['cruzamentos'][-1], 2)}°, com a forma "
        f"do elástico abaixo da do peso entre {f(nf['cruzamentos'][0], 2)}° e "
        f"{f(nf['cruzamentos'][-1], 2)}° e acima dela fora desse intervalo. A distribuição angular da assistência depende, "
        "portanto, de qual identificação de s_{0} se adota."))
    a(LEG_F("norm", "Torque do elástico e torque do peso normalizados pelos "
                    "respectivos picos, em função da anteversão"))
    a(FIGURA("ottobock_tcc_fig_a4_normalizado.png", 5.6,
             "Torque do elástico e torque do peso normalizados, de 0 a 180 graus, "
             "com a faixa correspondente aos valores de s0 obtidos nas faixas de "
             "ângulo testadas."))
    a(FONTE)
    a(PEQUENO(f"Nota: faixa sombreada: s_{{0}} de {f(min(rob_t), 2)} a "
              f"{f(max(rob_t), 2)} mm, valores da curva tracejada nas faixas de "
              "θ_{el} da Tabela ⟦T:s0r⟧, no Apêndice ⟦S:apA⟧. O torque do peso está em módulo."))
    a(P("Em N·m, a comparação só é possível sob a hipótese K = K_{40}, e por isso "
        "a Figura ⟦F:proj⟧ e a Tabela ⟦T:proj⟧ descrevem um cenário de projeto, e "
        "não o dispositivo comercial. Nesse cenário, o torque do elástico atinge "
        f"{f(pr['tau_pico'])} N·m em θ_{{el}} = {f(pr['theta_pico'], 1)}°, "
        f"{f(abs(pr['theta_pico'] - mas['theta_tau_g_pico']), 1)}° "
        f"{'abaixo' if pr['theta_pico'] < mas['theta_tau_g_pico'] else 'acima'} do "
        f"pico de τ_{{g}}, em {f(mas['theta_tau_g_pico'], 1)}°, e a razão "
        f"τ/τ_{{g}} vai de {f(tab[30.0]['razao'], 2)} em 30° a "
        f"{f(tab[60.0]['razao'], 2)} em 60°, {f(tab[90.0]['razao'], 2)} em 90° e "
        f"{f(tab[150.0]['razao'], 2)} em 150°, com {f(tab[170.0]['razao'], 2)} em "
        f"170° e mínimo local de {f(vmin_cad['razao'], 2)} em "
        f"{f(vmin_cad['theta'], 1)}°, junto à transição. "
        "A força e a extensão do elástico nesse cenário estão na seção ⟦S:r_mec⟧."))
    a(LEG_T("proj", f"Cenário de projeto com s_{{0}} = {f(pr['s0'])} mm e "
                    f"K = K_{{40}} = {f(pr['K'], 5)} N/mm"))
    linhas = [[f(l["theta"], 0), f(l["lambda"] + EPS), l["regime"], f(l["l"]), f(l["x"]),
               f(l["m"]), f(l["F"], 2), f(l["tau"]), f(l["tau_g"]), f(l["razao"])]
              for l in pr["tabela"]]
    a(TABELA(["θ_{el} (°)", "q (°)", "Regime", "s (mm)", "δ (mm)", "m (mm)",
              "F (N)", "τ (N·m)", "τ_{g} (N·m)", "τ/τ_{g}"], linhas,
             [860, 960, 1000, 960, 960, 900, 900, 940, 1000, 880], ["center"]*10))
    a(FONTE)
    a(PEQUENO("Nota: K_{40} é hipótese de projeto (seção ⟦S:ident⟧); τ_{g} considera "
              "o membro humano e o braço do exoesqueleto."))
    a(LEG_F("proj", "Torque do elástico com K = K_{40} no cenário de projeto, torque "
                    "do peso do membro e do braço do exoesqueleto e alvo de 40%"))
    a(FIGURA("ottobock_tcc_fig_a3_projeto.png", 6.0,
             "Torque do elástico no cenário de projeto, torque do peso e 40 por "
             "cento do torque do peso em função da anteversão, com a razão entre "
             "eles indicada em 30, 60, 90, 120 e 150 graus."))
    a(FONTE)
    a(PEQUENO("Nota: os rótulos indicam τ/τ_{g}; a linha pontilhada marca a "
              "transição de regime."))
    a(P("Abaixo da transição, em θ_{el} < "
        f"{f(g['theta_t'], 2)}°, o modelo mantém torque positivo, "
        f"{f(tab[10.0]['tau'])} N·m em 10° no cenário de projeto, porque o elemento "
        f"78 está a {f(par['P'])} mm do eixo. A Figura 16 da patente mostra razão nula abaixo "
        "de cerca de 14°, e a patente prefere o elemento 78 sobre o eixo. "
        "A divergência foi mantida no modelo, e não corrigida: ela depende da "
        "posição real do elemento 78 e de seu raio de contato, que não estão "
        "documentados."))
    s1, s2 = sens["faixa_min"], sens["faixa_max"]
    a(P("Entre os valores de s_{0} obtidos nas faixas de θ_{el} testadas, de "
        f"{f(s1['s0'], 2)} a {f(s2['s0'], 2)} mm, K_{{40}} varia de "
        f"{f(s1['K'], 5)} a {f(s2['K'], 5)} N/mm, e o pico de τ, de "
        f"{f(min(s1['tau_pico'], s2['tau_pico']))} a "
        f"{f(max(s1['tau_pico'], s2['tau_pico']))} N·m; as razões τ/τ_{{g}} em 30°, "
        "60°, 120° e 150° mudam no máximo "
        f"{f(max(abs(s1['razao'][k] - s2['razao'][k]) for k in s1['razao']), 3)}. "
        "A escolha final de K, que a figura não determina, é decisão de projeto."))
    sc_ = {c["caso"]: c for c in N["sensibilidade_curvas"]}
    sp_, sct_ = sc_["pontilhada"], sc_["continua"]
    mud = max(((abs(c["razao"][k] - sens["s0"]["razao"][k]), k) for c in (sp_, sct_)
               for k in c["razao"]))
    a(P("Com o s_{0} das outras duas curvas, "
        f"{f(sp_['s0'])} mm (pontilhada) e {f(sct_['s0'])} mm (contínua), K_{{40}} "
        f"vai a {f(sp_['K'], 5)} e {f(sct_['K'], 5)} N/mm, e o pico de τ, a "
        f"{f(sp_['tau_pico'])} N·m em {f(sp_['theta_pico'], 1)}° e "
        f"{f(sct_['tau_pico'])} N·m em {f(sct_['theta_pico'], 1)}°; as razões "
        "τ/τ_{g} em 30°, 60°, 120° e 150° mudam até "
        f"{f(mud[0], 3)} em relação às da curva tracejada, com a maior mudança em "
        f"{mud[1]}°. A distribuição angular da assistência depende, assim, da curva "
        "tomada como referência."))
    a(P("O resultado ilustra a limitação discutida na seção 2.4 (NASR; FERGUSON; "
        "McPHEE, 2022): com o "
        f"s_{{0}} adotado, a forma do elástico fica abaixo da do peso entre "
        f"{f(cz_n[2], 2)}° e {f(cz_n[3], 2)}°, de modo que, no modelo, a "
        "subcompensação recai sobre a faixa acima da horizontal, onde se concentra o "
        "risco documentado por van der Molen et al. (2017) e Seidler et al. (2020). "
        "Como essa forma depende da geometria do CAD, que não reproduz a Figura 16 "
        "da patente (seção ⟦S:r_forma⟧), a leitura vale para o modelo."))

    # ------------------------------------------------------------ limitações
    a(SEC("4.2", "r_lim", "Limitações dos resultados"))
    a(P("Além das limitações de escopo da seção ⟦S:ferr⟧, os resultados comportam as "
        "ressalvas a seguir."))
    a(P("A principal é a diferença de forma entre o modelo e a Figura 16 da patente "
        "(seção ⟦S:r_forma⟧). Com os s_{0} identificados e escala comum, o modelo "
        "completo não reproduz a figura: o R^{2} fica entre "
        f"{f(min(mcomp[n]['comum']['r2'] for n in ORDEM), 2)} e "
        f"{f(max(mcomp[n]['comum']['r2'] for n in ORDEM), 2)}, e a patente não informa a "
        "configuração do dispositivo que gerou a figura nem a definição de sua ordenada. "
        "O s_{0} identificado pelo espaçamento entre as curvas não depende dessa forma, "
        "mas a distribuição angular do torque calculado, sim."))
    a(P("O torque em N·m é um cenário, e não uma medida: a patente não publica a rigidez "
        "do elástico nem a escala da ordenada da Figura 16, e K = K_{40} vem da alegação "
        "comercial de 40% de assistência (SUITX, [202-]), sem verificação independente. "
        "A identificação pelo espaçamento supõe elástico linear, com o mesmo K nas três "
        "curvas, e o ajuste de forma usa escala diferente em cada curva."))
    a(P("As comparações angulares com a patente, como o início das curvas, a transição "
        "e a posição do pico, dependem da hipótese de eixo da articulação 20 no centro "
        "do ombro e barra 18 fixa no tronco (seção ⟦S:conv⟧). O modelo dá torque não nulo "
        "abaixo da transição, onde a Figura 16 da patente mostra razão nula, e esse "
        "trecho depende da posição e do raio de contato do elemento 78: com o elemento "
        "sobre o eixo, o contato cai no início das curvas."))
    a(P("As grandezas medidas no CAD (Tabela ⟦T:cad⟧) não têm conferência independente. "
        "A incerteza da leitura da Figura 16 da patente foi estimada só pelo erro mediano "
        "declarado, e a identificação supõe que a figura, apresentada como exemplar, seja "
        "fiel em escala, o que a patente não declara; o efeito de e_{c} foi comparado com "
        "a Figura 17 da patente só visualmente. Por fim, o modelo é plano, sem a abdução "
        "e a articulação esférica 22, e os resultados limitam-se à análise estática."))

    return B


# ======================================================================
# capítulo 5 e referências
# ======================================================================

def cap5_titulo():
    return [P("As conclusões estão organizadas por dispositivo: a seção 5.1 trata do "
              "gerador de torque da US 9.889.554 B2; a seção 5.2, do dispositivo da "
              "EP 3 504 033 B1; a seção 5.3, do mecanismo de came da US 9.737.374 B2; e a "
              "seção 5.4 compara os três."),
            H("5.1 Exoesqueleto 1")]


def parte_5B():
    B = []
    a = B.append
    s0p, s0t, s0c = (s0r[n] for n in ORDEM)
    rob_t = [x["s0"]["tracejada"] for x in rz["robustez"]]
    fr = rz["forma"]["G_sobre_modelo"]
    dp = rz["monte_carlo"]["desvio"]
    cad = next(l for l in fam["linhas"] if abs(l["e"] - g["E_CAD"]) < 1e-9)
    vmin = next(x for x in cad["extremos_razao"] if x["tipo"] == "min")
    linhas_e = {l["e"]: l for l in fam["linhas"]}
    res_circ = max(ver["residuo_f1"], ver["residuo_f2"], ver["residuo_f3"],
                   ver["residuo_f4"])
    a(H("5.2 Exoesqueleto 2"))
    a(P("Para a EP 3 504 033 B1, foram executadas a leitura da arquitetura na "
        "patente, a organização das grandezas do CAD com sua origem, a composição "
        "inercial do membro humano, as convenções angulares, a cinemática de dois "
        "regimes em forma fechada, o torque pelo produto vetorial, o torque "
        "gravitacional, o tratamento da Figura 16 da patente, a identificação de "
        "s_{0} pelo espaçamento entre as curvas e pelo ajuste de forma, a varredura "
        "do trecho e_{c} e as verificações numéricas."))
    a(P("O espaçamento entre as três curvas da Figura 16 da patente determina os "
        "comprimentos de referência do elástico sem depender da escala da ordenada, "
        "da rigidez, do braço de momento ou do torque do peso: "
        f"{f(s0p, 2)} mm na curva pontilhada, {f(s0t, 2)} mm na tracejada e "
        f"{f(s0c, 2)} mm na contínua. Na curva tracejada, que fornece o s_{{0}} "
        "adotado, a variação entre as faixas de ângulo testadas é de até "
        f"{f(max(rob_t) - min(rob_t), 2)} mm, e o desvio padrão com o ruído de "
        f"extração, de {f(dp['tracejada'], 2)} mm ({f(dp['pontilhada'], 2)} mm na "
        f"pontilhada e {f(dp['continua'], 2)} mm na contínua). O fim da curva "
        "pontilhada, de pré-tensão quase nula, confirma o resultado de forma "
        "independente: a razão dessa curva, extrapolada, se anula em "
        f"{f(rz['fim_pontilhada']['2']['theta'], 1)}°, o que o modelo interpreta "
        "como afrouxamento do elástico, e com o s_{0} identificado o modelo afrouxa "
        f"a partir de {f(rz['theta_frouxo']['pontilhada'], 1)}°. O início das "
        "curvas, perto de 14°, não informa s_{0}, mas fica a "
        f"{f(INICIO16 - g['theta_t_p0'], 1)}° do contato calculado com o elemento de "
        f"encosto sobre o eixo, em {f(g['theta_t_p0'], 2)}°, configuração preferida "
        f"pela patente; com o elemento do CAD, a {f(par['P'])} mm do eixo, o contato "
        f"ocorre em {f(g['theta_t'], 2)}°. O espaçamento confirma ainda o sinal de "
        f"θ_{{b,pose}} e a abscissa: com o sinal oposto, o resíduo sobe de "
        f"{f(rz['rms'])} para {f(rz['rms_braco_pose_invertido'])} mm, e nenhum "
        "deslocamento da abscissa o reduz de forma apreciável."))
    a(P("A forma do torque prevista com a geometria do CAD e o peso do membro "
        "humano não reproduz as curvas da patente: o fator comum às três curvas "
        f"difere do previsto por um fator que vai de {f(fr['20'], 2)} em 20° a "
        f"{f(fr['165'], 2)} em 165°, normalizado em 90°. O ajuste de forma, que deixa "
        "s_{0} e a escala livres por curva, compensa essa diferença com valores de "
        "s_{0} que se afastam dos do espaçamento"
        + (", como o limite s_{0} = 0 na curva contínua,"
           if rz and N["ajuste"]["individual"]["continua"]["limite"] == "inferior" else "")
        + " e com escalas diferentes por curva, contrárias ao atuador único da patente. "
        + ("Como o s implícito na figura concorda com o do CAD melhor do que "
           "permitiria um braço de momento diferente, a diferença vem, mais "
           "provavelmente, do torque do peso usado pela patente para formar a razão "
           "ou da definição da ordenada, que a patente não permite separar."
           if rz["forma"]["l_de_m_impl_menos_cad"]["rms"] > 2*rz["l_figura_menos_cad"]["rms"]
           else "A origem da diferença não pôde ser determinada: a concordância de s "
           "entre a figura e o CAD não separa o braço de momento do torque do peso ou "
           "da definição da ordenada.")))
    a(P("A rigidez não é identificável pela figura. Sob a hipótese de assistência "
        f"de 40% do torque do peso em 90°, K = {f(pr['K'], 3)} N/mm, e o elástico "
        f"trabalha de {f(pr['F_0'], 1)} N com o braço pendente a "
        f"{f(pr['F_180'], 1)} N com o braço elevado, com deformação máxima de "
        f"{pct(pr['deformacao_max'], 1)} do comprimento de referência. O torque "
        f"atinge {f(pr['tau_pico'])} N·m em {f(pr['theta_pico'], 1)}°, dentro da "
        "faixa de 70° a 120° em que a patente prefere a força máxima, lida aqui como "
        "força de apoio proporcional ao torque, e a razão τ/τ_{g} vale "
        f"{f(tab[10.0]['razao'], 2)} em 10°, {f(tab[30.0]['razao'], 2)} em 30°, "
        f"{f(tab[60.0]['razao'], 2)} em 60°, {f(tab[90.0]['razao'], 2)} em 90° e "
        f"{f(tab[150.0]['razao'], 2)} em 150°, com mínimo local de {f(vmin['razao'], 2)} "
        f"em {f(vmin['theta'], 1)}°. Abaixo da transição de regime, em "
        f"{f(g['theta_t'], 2)}°, o modelo ainda entrega torque, porque o elemento de "
        f"encosto do CAD está a {f(par['P'])} mm do eixo."))
    a(P("As relações de circuito dos dois regimes e o princípio dos trabalhos "
        f"virtuais foram verificados com resíduos de até {sci(res_circ)} mm e "
        f"{sci(max(ver['tv_I'], ver['tv_II']))} mm/rad. Com s_{{0}} e K mantidos, a "
        "varredura do trecho e_{c} mostrou que o elástico permanece tracionado em toda "
        f"a faixa só para e_{{c}} ≤ {f(var['faixas']['tracao']['max'], 2)} mm; o aumento "
        f"de e_{{c}} antecipa a transição de regime, de {f(var['theta_t'][1], 2)}° para "
        f"{f(var['theta_t'][0], 2)}°, e desloca o pico do torque de "
        f"{f(linhas_e[25.0]['theta_pico'], 1)}° para "
        f"{f(linhas_e[45.0]['theta_pico'], 1)}° entre e_{{c}} = 25 mm e e_{{c}} = 45 mm. A "
        "comparação com a Figura 17 da patente ficou restrita à inspeção visual."))
    a(P("Dos objetivos acrescentados para esse dispositivo, o item h foi cumprido "
        "na parte estática, com três ressalvas: a escala do torque depende da "
        "hipótese K = K_{40}; as grandezas do CAD não têm conferência "
        "independente; e a "
        "composição inercial e o torque gravitacional incluem o membro humano e o "
        "braço do exoesqueleto, mas não a alavanca, o elemento 78 e a braçadeira, "
        "previstos nos itens a e e. O item i foi "
        "cumprido pelo espaçamento entre as curvas. Para esse dispositivo, o "
        "objetivo geral foi atingido, com o confronto com o torque "
        "gravitacional feito pela forma normalizada e, em N·m, apenas no cenário de "
        "projeto. As etapas dinâmicas não foram executadas, pelas razões da seção "
        "⟦S:din⟧."))
    a(P("Como continuidade para esse dispositivo, recomenda-se obter a curva de força "
        "e extensão do elemento elástico, que fixaria K e a escala do torque, e, com a "
        "escala resolvida, executar as etapas dinâmicas pela formulação de Lagrange e "
        "no MBDyn."))
    return B


DOI_VIRTANEN = "https://doi.org/10.1038/s41592-019-0686-2"
RID_DOI = "rIdExo2Doi1"
URL_SUITX = "https://www.suitx.com/en/products/ix-shoulder-air-exoskeleton"
RID_SUITX = "rIdExo2Url1"
DOI_ZEIAEE = "https://doi.org/10.1109/ICORR.2017.8009339"
RID_ZEIAEE = "rIdExo2Doi2"
DOI_OKABE = "https://doi.org/10.1115/1.4071946"
RID_OKABE = "rIdExo2Doi3"


# ======================================================================
# exoesqueleto 3: US 9.737.374 B2 (Doyle, 2017), cabo, polia e came
# ======================================================================

def _e3_faixa(z):
    """Faixa de Θ, em graus, em que o cabo da mola sai na zona z (giro do desenho)."""
    (a0, a1), = N3["zonas"][z]
    return a0, a1


def parte_3C():
    p, aj, pa = N3["pontos"], N3["ajuste"], N3["peso_apoio"]
    cm, ver = pa["came"], N3["verificacoes"]
    B = []
    a = B.append
    a(H("3.3 Exoesqueleto 3"))
    a(P("As seções ⟦S:e3_cad⟧ a ⟦S:e3_ferr⟧ aplicam à US 9.737.374 B2 (DOYLE, 2017), da "
        "Levitate, o procedimento deste capítulo, com a classificação de origem da seção "
        "3. Nesse mecanismo, a força da mola chega ao ombro por um par de polias, uma "
        "delas um came de raio variável, e por um cabo de ancoragem. A cadeia de cálculo "
        "está nos scripts da pasta exo3, que extraem o perfil do came, resolvem o "
        "circuito do cabo de ancoragem, tratam as relações entre o came e o cabo da mola, "
        "medem as poses das figuras da patente e compõem a massa do apoio de braço; os "
        "números e as figuras da seção 4.3 são produzidos por tcc_resultados_exo3.py, que "
        "grava os valores em results/exo3_tcc_numeros.json."))
    # tabela de fontes cortada pelo autor (versão revisada de 9/11/2026)
    a(P("O documento da patente, do escritório de patentes dos Estados Unidos, está só "
        "em imagem, com 48 folhas de desenho, e o texto foi lido por reconhecimento "
        "óptico."))

    # ------------------------------------------------------------ CAD
    a(SEC("3.3", "e3_cad", "Reconstrução geométrica em CAD"))
    a(P("A reconstrução parte da arquitetura descrita na patente. Nas Figuras 14C e 14D da "
        "US 9.737.374 B2, o chassi 580 do apoio de braço gira em torno do pivô horizontal do "
        "ombro, 584. O cabo de ancoragem 560 sai do ponto 562, na âncora 558, presa ao "
        "suporte do tronco, enrola-se na polia primária 564 e prende-se a ela no ponto 561. "
        "A polia secundária 570 é solidária à primária, e as duas giram em torno do pino "
        "572, no chassi. O cabo da mola 634 prende-se à secundária no ponto 573, corre no "
        "canal 652, passa pela polia de reversão 630, no pino 632, também no chassi, e "
        "chega à mola 636, cuja outra ponta fica presa ao chassi (DOYLE, 2017). Ao baixar "
        "o braço, o cabo 560 desenrola-se da primária, o par de polias gira, e o cabo 634 "
        "enrola-se na secundária, estendendo a mola; ao erguê-lo, acontece o inverso."))
    a(P("A secundária 570 é o came. A patente divide o canal em três zonas: na Z10, o "
        "raio é constante (R20 = R21); na Z11, ele diminui continuamente, de R22 a R23; e "
        "na Z12, o canal forma um trecho reto (DOYLE, 2017). A Figura 16 da "
        "US 9.737.374 B2 traz o momento do dispositivo (AASM), o do peso do braço (AWM) e "
        "o resultante (RM) em função do ângulo Θ do eixo maior do apoio de braço com a "
        "horizontal, positivo acima dela, com as faixas de Θ atribuídas às zonas Z11 e "
        "Z12. A ordenada não tem unidade. O documento não traz cotas do mecanismo nem a "
        "rigidez e o comprimento livre da mola: os desenhos das Figuras 14C, 14D, 15A e "
        "15B são a única fonte geométrica da patente."))
    a(P("O modelo é plano, no plano das Figuras 14C e 14D, normal ao eixo do pivô 584, e "
        "representa só a rotação do apoio de braço em torno desse eixo. O circuito do "
        "mecanismo foi fechado no modelo em CAD do autor, cuja pose é a da Figura 14D, e "
        "as grandezas medidas nesse modelo estão na Tabela ⟦T:e3_cad⟧ (seção "
        "⟦S:e3_r_geo⟧). O mesmo modelo dá as propriedades de massa de cinco corpos do "
        "apoio de braço (seção ⟦S:e3_inercia⟧). As grandezas são tratadas como medidas em "
        "CAD, na classificação da seção 3, e não como dimensões do dispositivo comercial."))
    a(P("Para conferir o CAD, as poses das Figuras 14C, com o braço erguido, e 14D, com o "
        "braço baixado, foram medidas na imagem da folha 21. O centro do pivô 584 é o do "
        "furo branco no meio do anel do pivô, e os dos pinos 572 e 632 saem de ajustes de "
        "circunferência; a distância de 584 a 572, com o C_{2} do CAD, dá a escala do "
        "desenho. O came desenhado nas duas figuras foi comparado ao contorno externo da "
        "Figura 15A, que é a 15B espelhada, ajustado por escala e giro à distância dos "
        "traços. Os resultados estão na seção ⟦S:e3_r_geo⟧."))

    # ------------------------------------------------------------ inércia
    a(SEC("3.3", "e3_inercia", "Parâmetros inerciais do membro e transporte ao eixo do "
                              "pivô 584"))
    a(P("O membro superior é o de referência (seção 3), alinhado ao eixo maior do "
        "apoio de braço, com o centro do ombro admitido no eixo do pivô 584 e o "
        "transporte ao eixo pelo teorema de Steiner. O artigo de Okabe, Brittes e Brito "
        "(2026), que usa a "
        "curva desta patente numa simulação multicorpos, adota massas que correspondem "
        "às frações de de Leva (1996) para 82,8 kg de massa corporal; esse membro "
        "entra só na comparação da seção ⟦S:e3_r_conf⟧."))
    a(P("O apoio de braço entra com as propriedades de massa de cinco corpos do CAD: a "
        "capa, a mola, as polias interna e externa e o came, com massa, centro de massa e "
        "tensor de inércia no referencial da peça, de eixo z, normal ao plano do mecanismo. "
        "O tensor transportado do centro de massa à origem confere com o relatório. As "
        "duas polias são cilindros cheios, com o centro de massa no eixo: a externa, de "
        "55 mm de diâmetro, é a primária 564, no pino 572, e a interna, de 30 mm, é a "
        "polia de reversão 630, no pino 632. O came é a flange da Figura 15A extrudada em "
        "30 mm, também no pino 572. A capa, as polias e o came são de náilon 6/6, e a "
        "mola, de aço."))
    a(P("O relatório não traz o pivô 584. O came aparece sem espelhamento no CAD e no "
        "desenho, de modo que o referencial da peça é o da Figura 14D girado, e o pivô foi "
        "posto a C_{2} do pino 572, com o ângulo entre C_{2} e a reta de 572 a 632 medido "
        "na Figura 14D, do mesmo lado da mola, como no desenho. O eixo maior fica 26,741° "
        "além de C_{2} (seção ⟦S:e3_conv⟧). Para cada corpo, d_{i} é a distância do "
        "centro de massa a O e a_{i} o ângulo dele com o eixo maior, positivo acima do "
        "eixo, e o momento de inércia em O sai do teorema de Steiner. O centro do came, "
        "excêntrico, gira com as polias em relação ao chassi; os demais corpos são fixos "
        "no chassi."))
    a(P("Duas conferências independentes sustentam esse referencial. Com o came "
        "espelhado, o giro dado pelo centróide e o dado pelos eixos principais de inércia "
        "discordam, e o eixo da mola do CAD, levado ao desenho, cai sobre a mola 636 da "
        "Figura 14D, que não entrou na construção do referencial (seção ⟦S:e3_r_verif⟧). "
        "A Tabela ⟦T:e3_massa⟧, na seção ⟦S:e3_r_geo⟧, reúne os resultados."))

    # ------------------------------------------------------------ convenções
    a(SEC("3.3", "e3_conv", "Referenciais e convenções angulares e de sinal"))
    a(P("A origem O fica no eixo do pivô 584, no referencial do CAD, que é o das "
        "Figuras 14C e 14D girado de 180°, nas convenções da seção 3."))
    a(P("A variável independente é q, o ângulo entre C_{2} e a horizontal, 61,724° "
        "na pose do CAD; q cresce quando o braço desce. A abscissa da Figura 16 da "
        "US 9.737.374 B2 é Θ, o ângulo do eixo maior do apoio de braço com a "
        "horizontal, positivo acima dela; a elevação a partir do braço pendente é "
        "Θ + 90°. O ângulo da patente não precisa ser convertido em elevação "
        "anatômica, mas a comparação com o peso do membro supõe o braço alinhado ao "
        "eixo maior e o centro do ombro no pivô 584. No CAD, o eixo maior do apoio de "
        "braço fica 26,741° além de C_{2}, no sentido em que q cresce, e, portanto,"))
    a(EQ(("e3_Theta", r"\Theta = -\left( q + 26{,}741^{\circ} \right)")))
    a(P(f"e a pose do CAD está em Θ = {f(N3['theta_pose'])}°. As propriedades de massa "
        "da seção ⟦S:e3_inercia⟧ estão em outro referencial, o da peça, que é o da Figura "
        "14D girado; os ângulos a_{i} são medidos a partir do eixo maior."))
    a(P("O torque τ é positivo no sentido anti-horário, que é o de Θ crescente; τ > 0 "
        "assiste a subida do braço. O torque do peso tem sinal oposto, e as comparações "
        "usam seu módulo τ_{g}. No código, τ sai do produto da força da mola pela "
        "transmissão τ/F_{s}, guardada como transm."))

    # ------------------------------------------------------------ circuito
    a(SEC("3.3", "e3_circ", "Equação de fechamento do circuito vetorial"))
    a(P("O cabo 560 fecha um circuito vetorial com o suporte e o chassi "
        "(Figura ⟦F:e3_circ⟧), pelos pontos O, o pivô 584; A, o ponto de ancoragem "
        "562; D, o pino 572; e T, o ponto em que o cabo deixa a polia primária. Os "
        "vetores são C_{1}, de A a O, fixo no suporte, na direção γ; C_{2}, de O a D, "
        "solidário ao chassi, na direção 180° − q do referencial do CAD; R, de D a T, "
        "o raio da polia primária, na direção φ; e S, de T a A, o vão livre do cabo, "
        "na direção θ. O circuito fechado, "
        "S u(θ) + R u(φ) + C_{2} u(180° − q) + C_{1} u(γ) = 0, tem as componentes"))
    a(EQ(("e3_f1", r"f_{1} = S\cos\theta + R\cos\varphi - C_{2}\cos q + C_{1}\cos\gamma = 0"),
         ("e3_f2", r"f_{2} = S\sin\theta + R\sin\varphi + C_{2}\sin q + C_{1}\sin\gamma = 0")))
    a(P("O mecanismo tem um grau de liberdade: a variável primária é q, e as "
        "secundárias são S e φ, porque o cabo sai tangente à polia, com θ = φ − 90° "
        "(seção ⟦S:e3_tang⟧), e a tangência elimina uma incógnita, não uma equação. "
        "Com d = A − D, a solução é fechada:"))
    a(EQ(("e3_sol", r"\mathbf{d} = -\left[ C_{1}\,\mathbf{u}\left( \gamma \right) + C_{2}\,\mathbf{u}\left( 180^{\circ} - q \right) \right],\quad S = \sqrt{\left| \mathbf{d} \right|^{2} - R^{2}},\quad \varphi = \operatorname{atan2}\left( d_{y},\ d_{x} \right) + \operatorname{atan2}\left( S,\ R \right)")))
    a(P("A tangente existe enquanto |d| > R; o limite |d| = R é tratado na seção "
        "⟦S:e3_zero⟧. O caminho inverso também fecha: com θ dado, φ = θ + 90°, "
        "w = −[R u(φ) + C_{1} u(γ)] e q = 180° − φ ± acos(w·u(φ)/C_{2}); dos dois "
        "ramos, o certo se escolhe por continuidade a partir da pose do CAD."))
    a(LEG_F("e3_circ", "Circuito do cabo de ancoragem sobre a Figura 14D da "
            "US 9.737.374 B2, na pose do desenho, e contorno do came da Figura 15A "
            "ajustado ao desenho"))
    a(FIGURA("exo3_tcc_fig_1_circuito.png", 6.3,
             "Circuito vetorial do cabo de ancoragem sobre a Figura 14D, com ampliação "
             "da região das polias"))
    a(PEQUENO("Fonte: adaptada da Figura 14D da US 9.737.374 B2 (DOYLE, 2017), com o "
              "circuito do modelo e o contorno do came sobrepostos pelo autor.", True))

    # ------------------------------------------------------------ tangência
    a(SEC("3.3", "e3_tang", "Ponto de tangência, distância b, ângulo β e braço de momento"))
    a(P("O cabo 560 deixa a polia primária tangente a ela, com θ = φ + σ 90°; o lado "
        "σ = −1, isto é, θ = φ − 90°, é o confirmado na pose do CAD. O vetor de O a T "
        "é"))
    a(EQ(("e3_tang", r"\mathbf{b} = C_{2}\,\mathbf{u}\left( 180^{\circ} - q \right) + R\,\mathbf{u}\left( \varphi \right)")))
    a(P("de módulo b e a um ângulo β de C_{2}; a direção de b é "
        "180° − q − β. Com f = F_{a} u(θ), a tração do cabo 560 aplicada em T, o torque "
        "em torno de O é"))
    a(EQ(("e3_tau", r"\tau = \frac{\left( \mathbf{b}\times\mathbf{f} \right)_{z}}{1000},\quad \left( \mathbf{b}\times\mathbf{f} \right)_{z} = -bF_{a}\sin\left( \theta + q + \beta \right) = F_{a}m_{a},\quad m_{a} = C_{1}\sin\left( \gamma - \theta \right)")))
    a(P("A segunda forma vem do fechamento, b = −S u(θ) − C_{1} u(γ): como a linha do "
        "cabo passa por A, o braço m_{a} só depende de θ e não passa de C_{1}. Esse é o "
        "b certo porque o apoio de braço, com o "
        "chassi, as polias, a mola e o cabo 634, gira em torno de O como um corpo só, "
        "e o único esforço externo do mecanismo é a tração F_{a} do cabo 560, em T."))

    # ------------------------------------------------------------ força
    a(SEC("3.3", "e3_forca", "Caminho do cabo, lei da mola e torque"))
    a(P("A força da mola chega ao cabo 560 pelo par de polias. O cabo da mola 634 sai da "
        "secundária 570 e segue até a polia de reversão 630, e o par gira sem atrito em "
        "torno de D. Com F_{s} a tração no cabo da mola e r o raio efetivo da secundária, "
        "isto é, a distância de D à linha do cabo 634, o equilíbrio do par dá "
        "F_{a} R = F_{s} r."))
    a(P("O perfil do canal saiu da Figura 15B, um corte pelo plano do canal em que a área "
        "hachurada é o fundo do canal: na imagem da folha 22, essa área foi isolada pelos "
        "vãos brancos da hachura e completada pelas lascas junto ao contorno e pelos "
        "entalhes das cotas. O contorno fechado, centrado no furo 654 (pino 572), foi "
        "dividido pelo raio médio da zona Z10, R20, tomado como referência (Figura "
        "⟦F:e3_came⟧a), e as zonas, localizadas pelas linhas de chamada das cotas, vão de "
        "89,6° a 140,4° (Z10), de 152,4° a 218,8° (Z11) e de 242,6° a 292,6° (Z12), no "
        "referencial da Figura 15B."))
    a(P("O cabo tracionado passa reto sobre concavidades. O raio efetivo é, por isso, a "
        "função suporte da envoltória convexa do canal: para cada direção φ_{c} normal "
        "ao cabo, no referencial do came, r(φ_{c}) é a maior projeção dos pontos do "
        "canal nessa direção. Ele difere do raio ρ do came no ponto de saída, que é o "
        "que a patente cota (R20 a R25). A patente trata a força do cabo como tangencial "
        "ao raio (DOYLE, 2017), o que só vale onde o cabo sai perpendicular a ele. Com "
        "β_{c} o ângulo entre o raio do ponto de saída e o cabo,"))
    a(EQ(("e3_rho", r"r = \rho\sin\beta_{c},\quad \rho^{2} = r^{2} + \left( \frac{dr}{d\varphi_{c}} \right)^{2}")))
    a(LEG_F("e3_came", "Fundo do canal do came 570 extraído da Figura 15B da "
            "US 9.737.374 B2 (a) e raio efetivo r e raio no ponto de saída ρ em função "
            "da direção do cabo (b)"))
    a(FIGURA("exo3_tcc_fig_2_came.png", 6.3,
             "Perfil do came 570 com as zonas Z10, Z11 e Z12 e raios efetivo e no ponto "
             "de saída"))
    a(PEQUENO("Fonte: elaborada pelo autor, a partir da Figura 15B da US 9.737.374 B2 "
              "(DOYLE, 2017).", True))
    a(P("O cabo 634 sai do came tangente a ele e segue até a polia de reversão 630, de "
        "modo que a sua direção depende do próprio r; numa geometria de teste, com a "
        "polia a 4,5 R20 de D e raio 0,5 R20, essa dependência muda r em até 0,031 R20. "
        "Por decisão do autor, a polia 630 fica fora da varredura: o cabo é tomado na "
        "direção de 572 para 632, medida na Figura 14D, como se a polia estivesse no "
        "infinito. A mola, cuja rigidez e cujo comprimento livre a patente não informa, "
        "entra como mola linear, e o torque fica"))
    a(EQ(("e3_forca", r"F_{a} = \frac{F_{s}\,r}{R},\quad F_{s} = k\left( x_{0} + \Delta x \right),\quad \tau = \frac{F_{s}}{1000}\,\frac{r}{R}\,C_{1}\sin\left( \gamma - \theta \right)")))
    a(P("em que x_{0} é o alongamento na pose do CAD e Δx o alongamento desde ela, "
        "obtido na seção ⟦S:e3_vt⟧; k e x_{0} são identificados na seção ⟦S:e3_dados⟧. "
        "O resultado da varredura é o torque por unidade de força da mola, "
        "τ/F_{s} = (r/R) C_{1} sin(γ − θ), em N·mm por N."))

    # ------------------------------------------------------------ ponto morto
    pm = N3["ponto_morto"]
    a(SEC("3.3", "e3_zero", "Ponto morto e limite de subida"))
    a(P("O braço de momento m_{a} se anula quando o cabo 560 passa por O, alinhado a "
        "C_{1}, e o vão S se anula quando a ancoragem chega à polia:"))
    a(EQ(("e3_lim", r"m_{a} = 0\quad \Leftrightarrow \quad \theta = \gamma + 180^{\circ},\qquad S = 0\quad \Leftrightarrow \quad \left| \mathbf{d} \right| = R")))
    a(P(f"A primeira condição dá q = {f(pm['q'], 2)}°, isto é, Θ = {f(pm['theta'], 1)}°, "
        "fora da faixa da Figura 16 da US 9.737.374 B2, que começa em −75°: o mecanismo "
        "não tem ponto morto nem faixa sem torque no curso analisado, e m_{a} é positivo "
        "da pose do CAD até o limite de subida. A segunda dá "
        f"q = {f(N3['q_limite'], 2)}°, isto é, Θ = {f(N3['theta_limite'], 1)}°: com esta "
        "ancoragem, o braço não sobe além disso, embora a curva da patente vá até 30°. O "
        "primeiro valor sai do caminho inverso da seção ⟦S:e3_circ⟧, com θ = γ + 180°, e "
        "o segundo, pelo método de Brent (BRENT, 1973)."))

    # ------------------------------------------------------------ peso
    a(SEC("3.3", "e3_peso", "Torque gravitacional"))
    a(P("O conjunto que gira com o braço reúne o membro superior e o apoio de braço, e cada "
        "corpo i, de massa m_{i}, tem o centro de massa a d_{i} de O e a a_{i} do eixo "
        "maior (seção ⟦S:e3_inercia⟧). O módulo do torque do peso é"))
    a(EQ(("e3_tg", r"\tau_{g} = \frac{g}{1000}\left| \sum_{i}m_{i}d_{i}\cos\left( \Theta + a_{i} \right) \right|")))
    a(P("com m_{i} em kg e d_{i} em mm. Para o membro, alinhado ao eixo maior, "
        "a_{i} = 0. O centro do came, a "
        f"{f(cm['excentricidade_mm'], 2)} mm do pino 572, gira com as polias, e o termo "
        "dele usa o giro θ_{p} da Equação (⟦E:e3_vt⟧). A mola entra com o centro de massa "
        "do CAD, embora o comprimento dela no CAD não corresponda à pose: ao longo do "
        "curso, o centro se desloca metade do alongamento, o que muda o torque em no "
        f"máximo {f(pa['mola_incerteza_N_m'], 2)} N·m, e cada 10 mm de erro na posição "
        "dele ao longo do eixo da mola mudam o torque em no máximo "
        f"{f(pa['mola_10mm_N_m'], 2)} N·m."))

    # ------------------------------------------------------------ trabalho virtual
    a(SEC("3.3", "e3_vt", "Formulação pelo princípio dos trabalhos virtuais"))
    assert SECOES["e3_vt"] == "3.3.9", SECOES["e3_vt"]
    a(P("O equilíbrio é escrito pelo trabalho virtual num giro δq, em radianos, em "
        "que o apoio de braço gira δΘ = −δq (Equação (⟦E:e3_Theta⟧)). Realizam trabalho "
        "a tração do cabo 560, que atua em T, o peso do conjunto e o torque τ_{u} do "
        "usuário. Com a primária presa ao chassi, o giro δq mudaria o vão S de "
        "m_{a} δq; como o cabo 560 é inextensível e preso em A, a primária gira "
        "δθ_{p} = −m_{a} δq/R em relação ao chassi, e a mola estende-se de "
        "δx = −r δθ_{p}. Os trabalhos virtuais da força do cabo 560 e da força da mola "
        "são iguais, e"))
    a(EQ(("e3_vt", r"\tau = \frac{F_{s}}{1000}\,\frac{r}{R}\,C_{1}\sin\left( \gamma - \theta \right) = \frac{F_{s}}{1000}\,\frac{dx}{dq},\quad \frac{d\theta_{p}}{dq} = -\frac{C_{1}\sin\left( \gamma - \theta \right)}{R},\quad \frac{dx}{d\theta_{p}} = -r")))
    a(P("que é a Equação (⟦E:e3_forca⟧): as duas vias dão o mesmo torque, e a diferença "
        "numérica entre elas é conferida na seção ⟦S:e3_r_verif⟧. O peso entra com "
        "τ_{g,s}, de sinal oposto ao de τ e módulo τ_{g} da Equação (⟦E:e3_tg⟧). Como os "
        "três torques são positivos no sentido de Θ crescente e δΘ = −δq, o princípio dos "
        "trabalhos virtuais exige, para todo δq,"))
    a(EQ(("e3_vteq", r"\delta W = -(\tau + \tau_{g,s} + \tau_{u})\,\delta q = 0\quad\Rightarrow\quad\tau_{u} = -(\tau + \tau_{g,s})")))
    a(P("Aqui, τ está em N·m na escala fixada pela AWM (seção ⟦S:e3_dados⟧)."))
    a(P("A rotação das polias também sai do enrolamento. Com o cabo 560 inextensível, "
        "S + R w é constante, em que w é o arco enrolado de T a 561, e o giro absoluto "
        "das polias é φ − S/R, mais uma constante. O ponto 561 e o comprimento total do "
        "cabo só fixam essa constante, que vem do giro do came medido na Figura 14D "
        "(seção ⟦S:e3_r_geo⟧)."))

    # ------------------------------------------------------------ dados
    fg = N3["fig16"]
    a(SEC("3.3", "e3_dados", "Dados da patente e identificação dos parâmetros"))
    a(P("A Figura 16 da US 9.737.374 B2 foi digitalizada neste trabalho, com um ponto por "
        "grau de Θ = −75° a 30° nas três curvas, e a RM foi mantida onde fecha com "
        "AASM + AWM. A ordenada não tem unidade, e a AWM é um cosseno puro, o momento de "
        "um peso a distância fixa do pivô. As marcas da figura atribuem à zona Z12 a "
        "faixa de Θ = −56,4° a −40,3° e à Z11, de −23,8° a 4,0°."))
    a(P("A falta de unidade impede identificar a rigidez em valor "
        "físico pela AASM sozinha. A própria figura, porém, traz uma referência: a AWM é o "
        "momento do peso do braço, um cosseno de amplitude A. Igualando A ao torque do "
        "peso do membro de referência na horizontal (seção ⟦S:e3_inercia⟧), a unidade da "
        "figura passa a N·m. Com ela, a mola linear da Equação (⟦E:e3_forca⟧) tem dois "
        "parâmetros, k e x_{0}, e o torque é linear em k e em k x_{0}; os dois foram "
        "ajustados por mínimos quadrados nos pontos de Θ = −75° até o limite de subida:"))
    a(EQ(("e3_aj", r"\min_{k,\,x_{0}}\sum_{i}\left[ c\,y_{i} - \frac{k\left( x_{0} + \Delta x_{i} \right)g_{i}}{1000} \right]^{2},\quad g_{i} = \frac{r_{i}}{R}\,C_{1}\sin\left( \gamma - \theta_{i} \right),\quad c = \frac{M_{m}\,g\,d_{m}}{1000\,A}")))
    a(P("em que y_{i} é a AASM lida em Θ_{i}, M_{m} e d_{m} são a massa do membro e a "
        "distância do centro de massa dele a O, e g_{i}, Δx_{i}, r_{i} e θ_{i} saem da "
        "cadeia de cálculo. Se a AASM for o momento entregue ao braço, a mola também "
        "sustenta o apoio de braço, e o alvo passa a c y_{i} mais o torque do peso do "
        "apoio; os dois ajustes estão na seção ⟦S:e3_r_par⟧. O artigo de Okabe, Brittes e "
        "Brito (2026) adotou outra escala, com o máximo da AASM em 30 N·m, comentada na "
        "seção ⟦S:e3_r_conf⟧. O giro do came, que fixa a constante da rotação das polias, "
        "foi medido na Figura 14D, e R20, nas Figuras 14C e 14D (seção ⟦S:e3_r_geo⟧)."))

    # ------------------------------------------------------------ varredura
    a(SEC("3.3", "e3_varr", "Varredura paramétrica do giro do came"))
    a(P("O giro do came em relação à primária é a grandeza menos certa da cadeia, porque "
        "os dois desenhos discordam (seção ⟦S:e3_r_geo⟧), e é a que decide em que zona o "
        "cabo da mola sai em cada Θ; por isso, foi o parâmetro varrido. A varredura "
        "repetiu o ajuste da "
        "seção ⟦S:e3_dados⟧ com o came girado de −120° a +40° em relação ao desenho da "
        "Figura 14D, de grau em grau, com as demais grandezas nos valores da Tabela "
        "⟦T:e3_cad⟧. Só valem os giros em que o cabo da mola sai do canal em toda a faixa "
        "do ajuste: ele deixa o bolsão do 573 pelo chifre de cima e se enrola no canal até "
        "o chifre de baixo, e a ponte da envoltória sobre o bolsão não é canal. As marcas "
        "das zonas na Figura 16 da US 9.737.374 B2 não entram no ajuste e servem de "
        "conferência. Trata-se de diagnóstico, e nenhum parâmetro é substituído pelo "
        "resultado."))
    a(P("Além do giro contínuo, foram testadas as montagens que os furos permitem. Nas "
        "Figuras 14C e 14D, há cinco furos pequenos num arco em torno do pino 572, no lado "
        "do came oposto ao bolsão, que acompanham o came de uma figura para a outra. Os "
        "centros foram localizados na imagem da folha 21: o raio do arco, pelos furos "
        "isolados, e os ângulos, pela fração de pixels pretos num disco de 3,2 px ao longo "
        "desse arco, o que alcança também os furos tocados por linhas de chamada. "
        "Admitido, como supõe o autor, que a polia externa tem furos correspondentes, o "
        "came pode ser fixado girado de j passos em relação ao desenho, com j de −4 a +4, "
        "e, com os mesmos cinco furos nas duas peças, 5 − |j| pares coincidem; j positivo "
        "é o giro anti-horário na vista das Figuras 14C e 14D."))
    a(P("Cada montagem foi calculada de dois modos. No primeiro, a mola e o cabo são os da "
        "montagem desenhada, com k e x_{0} do ajuste da seção ⟦S:e3_dados⟧, e o "
        "alongamento é a variação do comprimento do cabo da mola entre o chifre de cima e "
        "um plano fixo no chassi, normal ao cabo, com a polia 630 no infinito: o arco "
        "enrolado no canal menos a projeção do ponto de saída na direção do cabo. Como a "
        "âncora 573 gira com o came, esse comprimento vale para qualquer montagem, e o "
        "alongamento é contado do comprimento na pose do CAD com o came desenhado. No "
        "segundo modo, k e x_{0} são ajustados de novo à Figura 16 da US 9.737.374 B2, "
        "como no giro contínuo."))

    # ------------------------------------------------------------ verificações
    a(SEC("3.3", "e3_verif", "Verificações numéricas"))
    a(P("Os scripts executam as verificações da Tabela ⟦T:e3_verif⟧ (seção "
        "⟦S:e3_r_verif⟧). Na cadeia de cálculo, elas vão do fechamento com as grandezas "
        "do CAD ao caminho inverso, ao trabalho virtual, à rotação das polias pelo "
        "enrolamento e aos comprimentos dos cabos; nas conferências com a patente, "
        "incluem o ponto de ancoragem nas Figuras 14C e 14D e, para as massas, o "
        "transporte do tensor, a forma das polias, a distância entre os pinos, o raio e "
        "o giro do came, o espelhamento e a posição da mola. São asserções e "
        "conferências executadas pelos scripts, e não um conjunto de testes executado "
        "com o pytest."))

    # ------------------------------------------------------------ dinâmica
    cj = N3["conjunto"]
    a(SEC("3.3", "e3_din", "Etapas dinâmicas previstas"))
    a(P("Pela formulação de Lagrange, com q como coordenada generalizada, a equação "
        "de movimento seria I_{O} d^{2}q/dt^{2} = −(τ + τ_{g,s} + Q_{nc}), com o sinal "
        "trocado porque q cresce no sentido horário, oposto ao de τ positivo (Equação "
        "(⟦E:e3_Theta⟧)). Pela Equação (⟦E:e3_vt⟧), a energia elástica da mola "
        "satisfaz dV_{e}/dq = F_{s} dx/dq = 1000 τ, de modo que a força generalizada "
        "elástica, −dV_{e}/dq, coincide, a menos do fator −1/1000, com o torque da "
        "Equação (⟦E:e3_forca⟧); esse "
        "pré-requisito estático está verificado (Tabela ⟦T:e3_verif⟧). O momento de "
        f"inércia do conjunto em torno de 584 é de {f(cj['izz_o'], 4)} kg·m^{{2}} "
        "(Tabela ⟦T:e3_massa⟧), e a energia cinética teria ainda o termo do giro do par "
        "de polias em relação ao chassi, que depende de dθ_{p}/dq e, portanto, de q. A "
        "integração não foi executada: a escala do torque vem da AWM igualada ao peso "
        "do membro de referência, a rigidez e o comprimento livre da mola só existem "
        "como ajuste nessa escala, e Q_{nc} não pode ser escrito, porque atrito e "
        "amortecimento são desconhecidos. Nenhum resultado dinâmico é apresentado, e as "
        "condições para executar a etapa estão na seção ⟦S:e3_r_lim⟧."))

    # ------------------------------------------------------------ ferramentas
    a(SEC("3.3", "e3_ferr", "Ferramentas e delimitação"))
    a(P("Foram empregados o modelo em CAD do autor, para fechar o circuito do mecanismo "
        "e extrair as propriedades de massa do apoio de braço, e a linguagem Python, com "
        "as bibliotecas NumPy (HARRIS et al., 2020), para o cálculo vetorizado, SciPy "
        "(VIRTANEN et al., 2020), para o processamento das imagens das folhas da "
        "patente, a envoltória convexa do came, o ajuste da caixa envolvente do came e "
        "o limite de subida, pelo método de Brent (BRENT, 1973), e Matplotlib (HUNTER, "
        "2007), para as figuras. O ajuste da mola é um "
        "problema de mínimos quadrados lineares, resolvido em forma fechada, e o MBDyn "
        "não foi empregado. Valem as exclusões de escopo da seção 3. O modelo é "
        "plano e admite vínculos ideais, sem atrito no pivô e nas polias, cabos "
        "inextensíveis e sem massa, polia 630 no infinito e mola linear identificada "
        "pela própria curva da patente, na escala fixada pela AWM. O giro do came vem "
        "do desenho da Figura 14D, que discorda do da 14C. O torque gravitacional "
        "considera o membro de referência, alinhado ao eixo "
        "maior e com o ombro no pivô 584, e os cinco corpos do apoio de braço; outras "
        "peças que giram com o braço não entram nele."))
    return B


def parte_4C():
    p, aj, mg = N3["pontos"], N3["ajuste"], N3["melhor_giro"]
    pa, cj, mb, ver = N3["peso_apoio"], N3["conjunto"], N3["membro"], N3["verificacoes"]
    apj, cm, fg = pa["ajuste_com_peso"], pa["came"], N3["fig16"]
    z10, z11, z12 = (_e3_faixa(z) for z in ("Z10", "Z11", "Z12"))
    (m11a, m11b), = mg["zonas"]["Z11"]
    (m12a, m12b), = mg["zonas"]["Z12"]
    B = []
    a = B.append
    a(H("4.3 Exoesqueleto 3"))
    a(P("Esta seção apresenta os resultados das etapas das seções ⟦S:e3_cad⟧ a "
        "⟦S:e3_verif⟧, aplicadas ao mecanismo da US 9.737.374 B2. Salvo indicação em "
        f"contrário, os números foram obtidos com a geometria do CAD, R20 = "
        f"{f(N3['R20_mm'], 3)} mm, o giro do came medido na Figura 14D e a escala que "
        "iguala a AWM ao torque do peso do membro de referência (seção ⟦S:e3_dados⟧), de "
        f"{f(N3['escala']['c'], 4)} N·m por unidade da figura. As etapas dinâmicas da seção "
        "⟦S:e3_din⟧ não foram executadas. Os números e as figuras são produzidos pelo "
        "script tcc_resultados_exo3.py."))

    # ------------------------------------------------------------ geometria
    pc = N3["pontos_cad"]
    a(SEC("4.3", "e3_r_geo", "Geometria reconstruída e propriedades de massa"))
    a(P("A Tabela ⟦T:e3_cad⟧ reúne as grandezas medidas no CAD na pose de referência e "
        "as que delas derivam, com a origem de cada uma (seção ⟦S:e3_cad⟧)."))
    a(LEG_T("e3_cad", "Grandezas do circuito do cabo de ancoragem na pose do CAD"))
    a(TABELA(
        ["Grandeza", "Símbolo", "Valor", "Unidade", "Origem"],
        [["Vetor de A a O, fixo no suporte", "C_{1}", f(70.711), "mm", "CAD"],
         ["Vetor de O a D, solidário ao chassi", "C_{2}", f(90.587), "mm", "CAD"],
         ["Raio da polia primária", "R", f(26.443), "mm", "CAD"],
         ["Vão livre do cabo 560", "S", f(139.575), "mm", "CAD"],
         ["Distância de O a T", "b", f(78.292), "mm", "CAD"],
         ["Direção de C_{1}", "γ", f(61.26, 2), "graus", "CAD"],
         ["Ângulo entre C_{2} e a horizontal", "q", f(61.724), "graus", "CAD"],
         ["Direção de R", "φ", f(352.869), "graus", "CAD"],
         ["Direção de S", "θ", f(262.869), "graus", "CAD"],
         ["Ângulo em O entre C_{2} e b", "β", f(15.979), "graus", "CAD"],
         ["Defasagem entre C_{2} e o eixo maior", "", f(26.741), "graus", "CAD"],
         ["Ângulo do apoio de braço na pose", "Θ", f(N3["theta_pose"]), "graus",
          "Derivada, Equação (⟦E:e3_Theta⟧)"],
         ["Raio de referência do came", "R20", f(N3["R20_mm"], 3), "mm",
          "Documental, Figuras 14C e 14D"]],
        [3200, 1000, 1200, 1000, 2960],
        ["left", "center", "right", "center", "left"]))
    a(FONTE)
    a(P(f"Com esses valores, o fechamento tem resíduo de {f(ver['fechamento_cad_mm'], 4)} "
        "mm, a solução fechada devolve S e φ da tabela, e "
        "|C_{2} u(180° − q) + R u(φ)| = 78,291 mm, que é o b medido. Com O na origem, "
        f"A = ({f(pc['A'][0])}; {f(pc['A'][1])}) mm, D = ({f(pc['D'][0])}; "
        f"{f(pc['D'][1])}) mm e T = ({f(pc['T'][0])}; {f(pc['T'][1])}) mm."))
    a(P("Na imagem da folha 21, a distância de 584 a 572 dá 152,6 px na Figura 14C e "
        "152,3 px na 14D, e, com C_{2} = 90,587 mm, a escala do desenho é de 1,68 px/mm. "
        "Na Figura 14D, q = 61,19°, contra 61,724° no CAD: a pose do CAD é a da Figura "
        "14D. Na 14C, q = −36,99°, isto é, Θ = 10,25°. Nas duas, a reta de 572 a 632, ao "
        "longo do chassi, fica 22,1° e 21,8° além de C_{2}, no mesmo sentido da "
        "defasagem do CAD, e o ponto A do CAD cai a "
        f"{f(ver['ancoragem_mm']['14C'], 1)} mm e a {f(ver['ancoragem_mm']['14D'], 1)} mm "
        "do 562 desenhado."))
    a(P("O came desenhado nas duas figuras é o contorno externo da Figura 15A. Levado ao "
        "referencial da 15B e ajustado ao desenho por escala e giro, ele fica a 0,05 px do "
        "traço nas duas figuras, com R20 = 31,96 mm na Figura 14C e 32,11 mm na 14D; "
        f"adotou-se R20 = {f(N3['R20_mm'], 3)} mm, isto é, "
        f"R20/R = {f(N3['R20_sobre_R'], 2)}. Do came da 14C para o da 14D, o giro "
        "absoluto medido é de 61,3°, e a cinemática do cabo 560 com A e D desenhados "
        "prevê 76,8°: a diferença, 15,5°, equivale a 7 mm de cabo na primária, e os dois "
        "desenhos não são exatamente coerentes entre si."))
    a(LEG_T("e3_massa", "Propriedades de massa do conjunto que gira com o braço em "
                        "relação ao pivô 584"))
    linhas = []
    for c in mb["segmentos"]:
        linhas.append([c["nome"].capitalize(), f(c["massa"], 4), f(c["d"], 1), f(0.0, 1),
                       f(c["izz_cg"], 6), f(c["izz_o"], 6)])
    linhas.append(["Membro superior", f(mb["massa"], 4), f(mb["d"], 1), f(0.0, 1),
                   f(mb["izz_cg"], 6), f(mb["izz_o"], 6)])
    for nome, rot in (("capa", "Capa"), ("mola", "Mola"),
                      ("polia interna", "Polia interna (630)"),
                      ("polia externa", "Polia externa (564)"), ("came", "Came 570")):
        c, ic = pa["corpos"][nome], pa["inercia"][nome]
        linhas.append([rot, f(c["massa_g"]/1000, 4), f(c["d"], 1), f(c["a"], 1),
                       f(ic["izz_cg"], 6), f(ic["izz_o"], 6)])
    ma_kg = pa["massa_g"]/1000
    linhas.append(["Apoio de braço", f(ma_kg, 4), f(pa["d"], 1), f(pa["a"], 1),
                   f(pa["izz_o_kgm2"] - ma_kg*(pa["d"]/1000)**2, 6), f(pa["izz_o_kgm2"], 6)])
    linhas.append(["Conjunto", f(cj["massa"], 4), f(cj["d"], 1), f(cj["a"], 1),
                   f(cj["izz_cg"], 6), f(cj["izz_o"], 6)])
    a(TABELA(["Corpo", "Massa (kg)", "d (mm)", "a (graus)", "I_{cm} (kg·m^{2})",
              "I_{O} (kg·m^{2})"], linhas, [2300, 1300, 1200, 1200, 1680, 1680],
             ["left", "center", "center", "center", "center", "center"]))
    a(PEQUENO("Fonte: elaborada pelo autor, com dados de de Leva (1996) e do modelo em "
              "CAD.", True))
    a(PEQUENO("Nota: d é a distância do centro de massa ao pivô 584 e a, o ângulo dele com "
              "o eixo maior, positivo acima. O centro do came está na pose do CAD."))
    a(P("A consistência foi conferida pelo teorema de Steiner: para o conjunto, "
        f"I_{{cm}} + M d^{{2}} = {f(cj['izz_cg'], 6)} + "
        f"{f(cj['izz_o'] - cj['izz_cg'], 6)} = {f(cj['izz_o'], 6)} kg·m^{{2}}. A "
        f"amplitude do torque gravitacional é M g d = {f(mb['momento_horizontal_N_m'], 2)} "
        "N·m para o membro e "
        f"{f(cj['amplitude_N_m'], 2)} N·m para o conjunto."))
    a(P(f"No CAD, o apoio de braço tem {f(ma_kg, 3)} kg: a capa, de náilon 6/6, responde "
        f"por {f(pa['corpos']['capa']['massa_g']/1000, 3)} kg, e a mola, de aço, por "
        f"{f(pa['corpos']['mola']['massa_g']/1000, 3)} kg. O pivô ficou em ({f(pa['O'][0], 2)}; {f(pa['O'][1], 2)}) mm no "
        f"referencial da peça, e o centro de massa do apoio, a {f(pa['d'], 1)} mm de O e "
        f"{f(pa['a'], 1)}° acima do eixo maior, desloca o do conjunto em "
        f"{f(cj['a'], 2)}° em relação ao eixo. As peças caem sobre os desenhos: a "
        f"distância entre os pinos 572 e 632 é de {f(pa['L'], 1)} mm no CAD, contra "
        f"{f(pa['L_14D'], 1)} mm na Figura 14D; o R20 do came do CAD sai de "
        f"{f(min(cm['R20_area'], cm['R20_giracao'], cm['R20_caixa']), 2)} a "
        f"{f(max(cm['R20_area'], cm['R20_giracao'], cm['R20_caixa']), 2)} mm pela área, "
        "pela giração e pela caixa envolvente; e o referencial da Figura 15B fica a "
        f"{f(pa['came_chassi_peca'], 1)}° da reta de 572 a 632 no CAD e a "
        f"{f(pa['came_chassi_14D'], 1)}° na Figura 14D."))

    # ------------------------------------------------------------ dados
    a(SEC("4.3", "e3_r_dados", "Dados extraídos da patente"))
    a(P(f"Da Figura 16 da US 9.737.374 B2 foram extraídos {fg['n_pontos']} pontos de cada "
        f"curva, um por grau de Θ = −75° a 30°; a RM foi mantida em {fg['n_rm']} deles, "
        "onde fecha com AASM + AWM com diferença de no máximo "
        f"{f(fg['fechamento_max'], 2)} unidade. A AASM tem máximo de {f(fg['aasm_max'], 2)} "
        f"em Θ = {fg['theta_max_aasm']}° e fica acima de 95% dele de "
        f"{f(fg['faixa_95'][0], 0)}° a {f(fg['faixa_95'][1], 0)}°, o trecho de "
        "sustentação quase constante que a patente atribui à Z11; ela vale "
        f"{f(fg['aasm_inicio'], 2)} em −75° e {f(fg['aasm_fim'], 2)} em 30°. A AWM é um "
        f"cosseno puro, −{f(cj['awm_amplitude'], 2)} cos Θ, e AASM/|AWM| vale "
        f"{f(fg['aasm_awm_zero'], 2)} na horizontal. A Tabela ⟦T:e3_pts16⟧ traz os valores "
        "em ângulos de 15 em 15 graus e no máximo da AASM."))
    a(LEG_T("e3_pts16", "Pontos extraídos da Figura 16 da US 9.737.374 B2"))
    c16 = aj["escala_N_m_por_unidade"]
    a(TABELA(["Θ (graus)", "AASM", "AWM", "RM", "AASM na escala da AWM (N·m)"],
             [[f(x["theta"], 0), f(x["AASM"], 2), f(x["AWM"], 2),
               f(x["RM"], 2) if x["RM"] is not None else "sem leitura",
               f(c16*x["AASM"], 2)] for x in fg["pontos"]],
             [1400, 1800, 1800, 1800, 2560],
             ["center", "center", "center", "center", "center"]))
    a(FONTE)
    a(PEQUENO("Nota: AASM, AWM e RM sem unidade, como na figura; RM sem leitura onde não "
              "fecha com AASM + AWM."))
    a(P("Do came, a Figura 15B dá o perfil do fundo do canal (Figura ⟦F:e3_came⟧a). Na "
        "Z10, o raio fica entre 0,994 e 1,004 R20, constante como pede R20 = R21; na Z11, "
        "cai continuamente de 0,961 para 0,663 R20, com R23 < R22; e a Z12 é reta, com "
        "desvio máximo de 0,003 R20. Na Z10, r/ρ fica entre 0,999 e 1,000; na Z11, entre "
        "0,894 e 0,974; e na Z12, entre 0,670 e 1,000 (Figura ⟦F:e3_came⟧b): usar ρ no "
        "lugar de r superestimaria o momento da mola em até 12% na Z11 e em até 49% na "
        "Z12. Das Figuras 14C e 14D saíram as poses, a escala do desenho e o giro do came "
        "(seção ⟦S:e3_r_geo⟧)."))

    # ------------------------------------------------------------ verificação
    a(SEC("4.3", "e3_r_verif", "Verificação da cadeia de cálculo"))
    a(P("As verificações da seção ⟦S:e3_verif⟧ resultaram nos valores da Tabela "
        "⟦T:e3_verif⟧. Os resíduos da cadeia de cálculo são da ordem do erro de "
        "arredondamento, exceto os do trabalho virtual e do cabo 634, limitados pelo "
        "truncamento da diferença finita, e os do fechamento com o CAD, limitados pela "
        "resolução da medida. O caminho inverso devolve q por um dos dois ramos: acima de "
        f"Θ = {f(ver['inverso_dois_ramos_desde_theta'], 1)}°, os dois têm S positivo, e "
        "o certo se escolhe por continuidade. Nas peças do apoio de braço, as distâncias "
        f"entre eixos diferem do desenho em até {f(pa['L_14D'] - pa['L'], 2)} mm, os "
        "ângulos em menos de 2°, e o eixo da mola passa a "
        f"{f(pa['mola_desenho']['afastamento_mm'], 1)} mm do centro dos traços da mola "
        "636; o came espelhado não fecha."))
    mo = pa["mola_desenho"]
    esp = pa["espelhamento"]
    a(LEG_T("e3_verif", "Verificações da cadeia de cálculo do modelo da Levitate"))
    a(TABELA(
        ["Verificação", "Resultado"],
        [["Fechamento com as grandezas do CAD, Equações (⟦E:e3_f1⟧) e (⟦E:e3_f2⟧)",
          f"{sci(ver['fechamento_cad_mm'])} mm"],
         ["S e φ da solução fechada contra o CAD, Equação (⟦E:e3_sol⟧)",
          f"{sci(ver['S_cad_mm'])} mm; {sci(ver['fi_cad_grau'])}°"],
         ["b e β do triângulo O, D, T contra o CAD, Equação (⟦E:e3_tang⟧)",
          f"{sci(ver['b_cad_mm'])} mm; {sci(ver['beta_cad_grau'])}°"],
         ["Duas formas do braço de momento, Equação (⟦E:e3_tau⟧)",
          f"{sci(ver['braco_duas_formas_mm'])} mm"],
         ["Caminho inverso: q recuperado de θ", f"{sci(ver['inverso_grau'])}°"],
         ["Trabalho virtual: τ/F_{s} contra dx/dq, Equação (⟦E:e3_vt⟧)",
          f"{sci(ver['trabalho_virtual_rel'])}, relativo"],
         ["Rotação das polias pelo enrolamento contra dθ_{p}/dq, Equação (⟦E:e3_vt⟧)",
          f"{sci(ver['enrolamento'])}"],
         ["Cabo 634 na geometria de teste: dℓ/dθ_{p} contra −r",
          f"{sci(ver['cabo634_R20'])} R20"],
         ["Montagens do came: comprimento do cabo da mola contra Δx integrado, came "
          "desenhado", f"{sci(N3['montagens']['conferencia_comprimento_mm'])} mm"],
         ["Tensor de inércia: transporte do centro de massa à origem",
          f"{sci(ver['tensor_rel'])}, relativo"],
         ["Polias como cilindros cheios: volume", f"{sci(ver['polias_volume_rel'])}, relativo"],
         ["Ponto A do CAD contra o 562 desenhado, Figuras 14C e 14D",
          f"{f(ver['ancoragem_mm']['14C'], 2)} e {f(ver['ancoragem_mm']['14D'], 2)} mm"],
         ["Distância entre os pinos 572 e 632, CAD contra Figura 14D",
          f"{f(pa['L'], 2)} e {f(pa['L_14D'], 2)} mm"],
         ["R20 do came do CAD por área, giração e caixa, contra as figuras",
          f"{f(cm['R20_area'], 2)}, {f(cm['R20_giracao'], 2)} e {f(cm['R20_caixa'], 2)} mm; "
          f"{f(N3['R20_mm'], 3)} mm"],
         ["Giro do came em relação à reta de 572 a 632, CAD contra Figura 14D",
          f"{f(pa['came_chassi_peca'], 1)}° e {f(pa['came_chassi_14D'], 1)}°"],
         ["Came: giro pelo centróide contra giro pelos eixos principais",
          f"{f(esp['sem_espelhar'], 1)}°; espelhado, {f(esp['espelhado'], 1)}°"],
         ["Eixo da mola do CAD sobre a mola 636 da Figura 14D",
          f"{f(mo['dif_direcao_grau'], 1)}° e {f(mo['afastamento_mm'], 1)} mm"],
         ["Figura 16 da US 9.737.374 B2: RM contra AASM + AWM",
          f"{f(fg['fechamento_max'], 2)} unidade"]],
        [6360, 3000], ["left", "center"]))
    a(FONTE)
    a(PEQUENO("Nota: o fechamento com o CAD é limitado pela resolução de três casas "
              "decimais da medida; o trabalho virtual e o cabo 634, pelo truncamento da "
              "diferença finita."))

    # ------------------------------------------------------------ parâmetros
    a(SEC("4.3", "e3_r_par", "Parâmetros do modelo e identificação da mola"))
    a(P("A Tabela ⟦T:e3_par⟧ resume a situação dos parâmetros que a patente não "
        "publica."))
    pv, ea = pa["pivo"], N3["escala_artigo"]
    a(LEG_T("e3_par", "Parâmetros não publicados do mecanismo da Levitate, origem e "
                      "identificabilidade"))
    a(TABELA(
        ["Parâmetro", "Símbolo", "Valor adotado", "Origem", "Situação"],
        [["Rigidez da mola", "k", f"{f(aj['k_N_por_mm'], 3)} N/mm",
          "Identificada por ajuste, na escala da AWM",
          f"Depende da escala; {f(apj['k_N_por_mm'], 3)} N/mm com o peso do apoio e "
          f"{f(ea['k_N_por_mm'], 3)} N/mm na escala do artigo"],
         ["Alongamento da mola na pose do CAD", "x_{0}", f"{f(aj['x0_mm'], 1)} mm",
          "Identificado por ajuste",
          f"{f(apj['x0_mm'], 1)} mm com o peso do apoio; o comprimento da mola no CAD "
          "não corresponde à pose"],
         ["Escala da ordenada da curva da patente", "c",
          f"{f(N3['escala']['c'], 4)} N·m por unidade",
          "Derivada: AWM igualada ao torque do peso do membro de referência",
          "Hipótese; a do artigo (OKABE; BRITTES; BRITO, 2026) é "
          f"{f(ea['razao'], 2)} vezes maior"],
         ["Raio de referência do came", "R20", f"{f(N3['R20_mm'], 3)} mm",
          "Medido nas Figuras 14C e 14D",
          f"CAD de {f(min(cm['R20_area'], cm['R20_giracao'], cm['R20_caixa']), 2)} a "
          f"{f(max(cm['R20_area'], cm['R20_giracao'], cm['R20_caixa']), 2)} mm"],
         ["Giro do came em relação à primária", "", "Como na Figura 14D",
          "Documental (desenho)",
          "As Figuras 14C e 14D discordam em 15,5°; varrido na seção ⟦S:e3_r_varr⟧"],
         ["Posição e raio da polia 630", "L; λ; r_{630}",
          "L infinito, de 572 para 632", "Hipótese, por decisão do autor",
          "Não representada; numa geometria de teste, muda r em até 0,031 R20"],
         ["Posição do pivô 584 no referencial da peça", "O",
          f"({f(pa['O'][0], 2)}; {f(pa['O'][1], 2)}) mm", "Derivada da Figura 14D e de C_{2}",
          f"Com outras escolhas, desloca até {f(max(x['desvio_O_mm'] for x in pv.values()), 1)} "
          "mm e muda o momento máximo do peso em menos de 0,01 N·m"]],
        [2300, 1060, 1500, 2000, 2500], ["left", "center", "center", "left", "left"]))
    a(FONTE)
    a(P(f"Com o giro do came da Figura 14D, o ajuste da Equação (⟦E:e3_aj⟧) nos "
        f"{aj['n_pontos']} pontos de Θ = −75° a {f(aj['theta_max_ajuste'], 0)}°, abaixo "
        f"do limite de subida, dá k = {f(aj['k_N_por_mm'], 3)} N/mm e "
        f"x_{{0}} = {f(aj['x0_mm'], 1)} mm; a mola trabalha de "
        f"{f(aj['forca_inicio_N'], 0)} N em −75° a {f(aj['forca_fim_N'], 0)} N em "
        f"{f(aj['theta_max_ajuste'], 0)}°. Com o peso do apoio de braço somado ao alvo, "
        f"k = {f(apj['k_N_por_mm'], 3)} N/mm e x_{{0}} = {f(apj['x0_mm'], 1)} mm. A "
        "Tabela ⟦T:e3_aj⟧ resume esses ajustes, o do melhor giro da seção ⟦S:e3_r_varr⟧ "
        "e, para comparação, o da escala do artigo de Okabe, Brittes e Brito (2026)."))
    a(LEG_T("e3_aj", "Mola linear ajustada à curva AASM da Figura 16 da "
            "US 9.737.374 B2, na escala da AWM"))
    a(TABELA(["Ajuste", "k (N/mm)", "x_{0} (mm)", "F_{s} na pose (N)", "R²",
              "Erro quadrático médio (N·m)", "Erro máximo (N·m)"],
             [["Came como na Figura 14D", f(aj["k_N_por_mm"], 3), f(aj["x0_mm"], 1),
               f(aj["forca_pose_N"], 0), f(aj["r2"], 3), f(aj["rms_N_m"], 2),
               f(aj["erro_max_N_m"], 2)],
              ["Came como na Figura 14D, com o peso do apoio", f(apj["k_N_por_mm"], 3),
               f(apj["x0_mm"], 1), f(apj["forca_pose_N"], 0), f(apj["r2"], 3),
               f(apj["rms_N_m"], 2), f(apj["erro_max_N_m"], 2)],
              [f"Came girado de {f(mg['giro'], 0)}°", f(mg["k"], 3), f(mg["x0"], 1),
               f(mg["forca_pose_N"], 0), f(mg["r2"], 3), f(mg["rms_N_m"], 2),
               f(mg["erro_max_N_m"], 2)],
              ["Came como na Figura 14D, na escala do artigo", f(ea["k_N_por_mm"], 3),
               f(ea["x0_mm"], 1), f(ea["forca_pose_N"], 0), f(ea["r2"], 3),
               f(ea["rms_N_m"], 2), f(ea["erro_max_N_m"], 2)]],
             [1900, 1000, 1000, 1300, 800, 1700, 1660],
             ["left", "right", "right", "right", "right", "right", "right"]))
    a(FONTE)

    # ------------------------------------------------------------ qualidade
    a(SEC("4.3", "e3_r_ajuste", "Qualidade do ajuste à curva da patente"))
    a(P(f"Com o giro do came da Figura 14D, o ajuste tem R² = {f(aj['r2'], 3)}, erro "
        f"quadrático médio de {f(aj['rms_N_m'], 2)} N·m e erro máximo de "
        f"{f(aj['erro_max_N_m'], 2)} N·m (Figura ⟦F:e3_fig16⟧a); com o peso do apoio "
        f"somado ao alvo, R² = {f(apj['r2'], 3)}. A força que reproduziria a curva AASM "
        "não é linear no alongamento (Figura ⟦F:e3_fig16⟧b): com esse giro, uma mola "
        "linear acompanha a forma geral da curva, mas não o início da subida nem o "
        "patamar. O ajuste contra a mesma curva reproduz a forma sem constituir "
        "validação independente."))
    a(LEG_F("e3_fig16", "Curva AASM da Figura 16 da US 9.737.374 B2 contra o modelo "
            "com mola linear e giro do came como na Figura 14D (a) e força de mola que "
            "reproduziria a curva (b)"))
    a(FIGURA("exo3_tcc_fig_4_fig16.png", 6.3,
             "Ajuste da mola linear à curva de momento publicada, com o came desenhado"))
    a(PEQUENO("Fonte: elaborada pelo autor, a partir da Figura 16 da US 9.737.374 B2 "
              "(DOYLE, 2017).", True))
    a(P("As marcas das zonas não entram no ajuste e servem de conferência. Com esse giro, "
        "a Z11 do modelo tem largura parecida com a da marca da patente, "
        f"{f(z11[1] - z11[0], 1)}° contra 27,8°, mas cai "
        f"{f((4.0 - 23.8)/2 - (z11[0] + z11[1])/2, 1)}° abaixo dela (seção "
        "⟦S:e3_r_mec⟧): a mola ajustada compensa no conjunto a posição das zonas, que o "
        "modelo não reproduz com o came desenhado."))

    # ------------------------------------------------------------ mecanismo
    a(SEC("4.3", "e3_r_mec", "Comportamento da mola e do mecanismo"))
    a(P("A Figura ⟦F:e3_varr⟧a mostra o vão S e o braço de momento do cabo 560 ao longo "
        f"de Θ, da pose do CAD (Θ = {f(N3['theta_pose'], 2)}°) até o limite de subida. O "
        "vão diminui à medida que o braço sobe e se anula em "
        f"Θ = {f(N3['theta_limite'], 2)}° (seção ⟦S:e3_zero⟧). O braço de momento cresce "
        f"de {f(p['pose']['braco'], 2)} mm na pose para {f(p['zero']['braco'], 2)} mm em "
        "Θ = 0 e fica positivo em toda a faixa. A Tabela ⟦T:e3_pts⟧ traz os valores nos "
        "ângulos marcados na Figura 16 da US 9.737.374 B2."))
    a(LEG_T("e3_pts", "Circuito, came e transmissão nos ângulos marcados na Figura 16 "
            "da US 9.737.374 B2"))
    linhas = []
    for nome, rot in (("pose", "pose do CAD"), ("inicio_fig16", "início da curva AASM"),
                      ("base_Z12", "base da marca Z12"), ("topo_Z12", "topo da marca Z12"),
                      ("base_Z11", "base da marca Z11"), ("zero", "horizontal"),
                      ("topo_Z11", "topo da marca Z11")):
        x = p[nome]
        linhas.append([f(x["theta"], 2), rot, f(x["S"], 2), f(x["braco"], 2),
                       x["zona"] or "canto", f(x["r"], 2), f(x["transm"], 2), f(x["dx"], 2)])
    a(TABELA(["Θ (graus)", "Ponto", "S (mm)", "m_{a} (mm)", "Saída", "r (mm)",
              "τ/F_{s} (mm)", "Δx (mm)"],
             linhas, [900, 1900, 900, 1500, 900, 900, 1200, 1160],
             ["right", "left", "right", "right", "center", "right", "right", "right"]))
    a(FONTE)
    a(P("Com o giro do came da Figura 14D, o cabo da mola sai na Z12 na pose, no canto "
        f"entre Z12 e Z11 de Θ = {f(z12[1], 1)}° a {f(z11[0], 1)}°, na Z11 de "
        f"{f(z11[0], 1)}° a {f(z11[1], 1)}° e na Z10 de {f(z10[0], 1)}° a "
        f"{f(z10[1], 1)}° (Figura ⟦F:e3_varr⟧b). O raio efetivo vai de "
        f"{f(p['pose']['r'], 2)} mm na pose a {f(p['zero']['r'], 2)} mm na horizontal e "
        "coincide com ρ na Z10. No canto antes da Z11, os dois se afastam: em Θ = −75°, "
        f"r = {f(p['inicio_fig16']['r'], 2)} mm e ρ = {f(p['inicio_fig16']['rho'], 2)} mm."))
    a(LEG_F("e3_varr", "Vão S e braço de momento do cabo de ancoragem (a), raio efetivo "
            "e zona de saída do cabo da mola (b) e transmissão e alongamento da mola (c) "
            "ao longo de Θ; as faixas sombreadas são as marcas Z12 e Z11 da Figura 16 da "
            "US 9.737.374 B2"))
    a(FIGURA("exo3_tcc_fig_3_varredura.png", 6.0,
             "Varredura em Θ do mecanismo da US 9.737.374 B2"))
    a(PEQUENO("Fonte: elaborada pelo autor, com as marcas das zonas da Figura 16 da "
              "US 9.737.374 B2 (DOYLE, 2017).", True))
    a(P("A transmissão τ/F_{s} = (r/R) C_{1} sin(γ − θ), em N·mm por N, cresce de "
        f"{f(p['pose']['transm'], 2)} mm na pose a {f(N3['transm_max'], 2)} mm em "
        f"Θ = {f(N3['theta_transm_max'], 1)}° e cai perto do limite de subida "
        f"(Figura ⟦F:e3_varr⟧c). Entre Θ = −75°, onde começa a curva da patente, e a "
        f"horizontal, ela passa de {f(p['inicio_fig16']['transm'], 2)} mm a "
        f"{f(p['zero']['transm'], 2)} mm, isto é, é multiplicada por "
        f"{f(p['zero']['transm']/p['inicio_fig16']['transm'], 1)}. O came responde por "
        f"parte disso, com r de {f(p['inicio_fig16']['r'], 2)} para "
        f"{f(p['zero']['r'], 2)} mm, e o cabo de ancoragem pelo resto, com o braço de "
        f"{f(p['inicio_fig16']['braco'], 2)} para {f(p['zero']['braco'], 2)} mm. Da pose "
        f"até o limite de subida, a mola encurta {f(-N3['dx_total_ate_limite'], 1)} mm."))

    # ------------------------------------------------------------ varredura
    a(SEC("4.3", "e3_r_varr", "Varredura paramétrica do giro do came"))
    gv = N3["giro_valido"]
    a(P("Repetido o ajuste com o came girado de −120° a +40° em relação ao desenho, de "
        "grau em grau (Figura ⟦F:e3_giro⟧a), o cabo da mola sai do canal em toda a faixa "
        f"entre {f(gv[0], 0)}° e +{f(gv[1], 0)}°; abaixo de {f(gv[0], 0)}°, ele chegaria "
        "ao chifre de baixo do bolsão, e esses giros foram descartados. Nessa faixa, o "
        "melhor resultado com k e x_{0} positivos "
        f"ocorre com o came girado de {f(mg['giro'], 0)}°: R² = {f(mg['r2'], 3)}, erro "
        f"quadrático médio de {f(mg['rms_N_m'], 2)} N·m, k = {f(mg['k'], 3)} N/mm e "
        f"x_{{0}} = {f(mg['x0'], 1)} mm (Figura ⟦F:e3_giro⟧b). Com esse giro, a Z11 do "
        f"modelo vai de {f(m11a, 1)}° a {f(m11b, 1)}°, e a saída na Z12 ocorre de "
        f"{f(m12a, 1)}° a {f(m12b, 1)}°: as duas caem dentro das marcas da patente, que "
        "não entram no ajuste. O ajuste da mola e as marcas das zonas indicam o mesmo "
        "giro, o que sugere que a curva da patente corresponde a uma montagem diferente "
        "da desenhada nas Figuras 14C e 14D, com o came girado em relação à primária ou "
        "com a âncora em outra posição."))
    a(LEG_F("e3_giro", "Sensibilidade do ajuste da mola ao giro do came: R² em função do "
            "giro em relação ao desenho da Figura 14D (a) e curva AASM da Figura 16 da "
            "US 9.737.374 B2 contra o modelo com o melhor giro (b)"))
    a(FIGURA("exo3_tcc_fig_5_giro.png", 6.3,
             "Sensibilidade do ajuste ao giro do came e ajuste com o melhor giro"))
    a(PEQUENO("Fonte: elaborada pelo autor, a partir da Figura 16 da US 9.737.374 B2 "
              "(DOYLE, 2017).", True))
    fu, mt = N3["furos"], N3["montagens"]
    fc_, fd_ = fu["figuras"]["14C"], fu["figuras"]["14D"]
    ml = {x["furos"]: x for x in mt["linhas"]}
    m2 = ml[-2]
    todos = [x for x in mt["linhas"] if x["toda_faixa"]]
    picos = sorted(mt["linhas"], key=lambda x: x["theta_tau_max"])
    taus = [x["tau_max_N_m"] for x in mt["linhas"]]
    fs = [v for x in mt["linhas"] for v in x["forca_N"]]
    r2m = [x["r2_mesma_mola"] for x in todos if x["furos"] != 0]
    assert m2["ajuste"]["fisico"] and abs(m2["giro"] - mg["giro"]) < 3
    assert all(not ml[j]["ajuste"]["fisico"] for j in (2, 3, 4))
    assert max(r2m) < ml[0]["r2_mesma_mola"]
    assert [x["furos"] for x in mt["linhas"] if not x["toda_faixa"]] == [-4, 3, 4]
    a(P("Os furos em torno do pino 572 reforçam essa leitura. Os cinco ficam a "
        f"{f(fc_['raio_mm'], 2)} mm do centro na Figura 14C e a {f(fd_['raio_mm'], 2)} mm "
        f"na 14D, com passo médio de {f(fc_['passo'], 2)}° e {f(fd_['passo'], 2)}°, "
        f"entre {f(min(fc_['angulos_came'] + fd_['angulos_came']), 1)}° e "
        f"{f(max(fc_['angulos_came'] + fd_['angulos_came']), 1)}° no referencial da "
        "Figura 15B nas duas figuras: giram com o came. Com o passo médio, "
        f"{f(fu['passo'], 2)}°, as nove montagens vão de {f(ml[-4]['giro'], 2)}° a "
        f"+{f(ml[4]['giro'], 2)}° (Tabela ⟦T:e3_mont⟧ e Figura ⟦F:e3_mont⟧). A de dois "
        f"furos no sentido horário, a {f(m2['giro'], 2)}°, fica a "
        f"{f(abs(m2['giro'] - mg['giro']), 1)}° do melhor giro contínuo e reproduz a curva "
        f"da patente com R² = {f(m2['ajuste']['r2'], 3)}, k = "
        f"{f(m2['ajuste']['k'], 3)} N/mm e x_{{0}} = {f(m2['ajuste']['x0'], 1)} mm, contra "
        f"R² = {f(ml[0]['ajuste']['r2'], 3)} da montagem desenhada."))
    a(P("Com a mesma mola e o mesmo cabo, a troca de furo desloca o máximo do torque de "
        f"Θ = {f(picos[0]['theta_tau_max'], 1)}° ({'+' if picos[0]['furos'] > 0 else ''}"
        f"{f(picos[0]['furos'], 0)} furos) a {f(picos[-1]['theta_tau_max'], 1)}° "
        f"({f(picos[-1]['furos'], 0)} furos), com valores de {f(min(taus), 2)} a "
        f"{f(max(taus), 2)} N·m, e a força da mola fica entre {f(min(fs), 1)} e "
        f"{f(max(fs), 1)} N (Figura ⟦F:e3_mont⟧a). Os giros horários atrasam a subida do "
        "torque e o concentram perto do limite de subida; os anti-horários a antecipam e "
        "reduzem o torque com o braço erguido. Nenhuma montagem reproduz a curva da "
        "patente com essa mola melhor que a desenhada, para a qual k e x_{0} foram "
        f"ajustados: R² de {f(min(r2m), 3)} a {f(max(r2m), 3)}, contra "
        f"{f(ml[0]['r2_mesma_mola'], 3)}. Nas montagens de +3 e +4 furos, o cabo da mola "
        "chega ao chifre de cima do bolsão antes do limite de subida, em "
        f"{f(ml[3]['theta_valido'][1], 1)}° e {f(ml[4]['theta_valido'][1], 1)}°, e, na de "
        "−4 furos, ao chifre de baixo abaixo de "
        f"{f(ml[-4]['theta_valido'][0], 1)}°; fora desses trechos, o modelo não vale."))
    a(P("Com outra mola ajustada a cada montagem (Figura ⟦F:e3_mont⟧b), as montagens "
        f"horárias dão R² de {f(ml[-3]['ajuste']['r2'], 3)} (−3 furos), "
        f"{f(ml[-2]['ajuste']['r2'], 3)} (−2) e {f(ml[-1]['ajuste']['r2'], 3)} (−1), todas "
        "com k e x_{0} positivos. Entre as anti-horárias, a de +1 furo chega a "
        f"R² = {f(ml[1]['ajuste']['r2'], 3)} com k = {f(ml[1]['ajuste']['k'], 3)} N/mm "
        f"e x_{{0}} de {f(ml[1]['ajuste']['x0']/1000, 1)} m, isto é, com força quase "
        "constante, e as de +2 a +4 furos só melhoram o ajuste com rigidez negativa, sem "
        "mola física. A curva da patente é, assim, compatível com o came girado de dois "
        "furos no sentido horário em relação ao desenho e com uma mola de cerca de "
        f"{f(m2['ajuste']['k'], 1)} N/mm na escala adotada; a patente não diz em que "
        "furo o came estava quando a Figura 16 foi gerada."))
    a(LEG_T("e3_mont", "Montagens do came nos furos em torno do pino 572"))

    def sinal(x, n):
        return ("+" if x > 0 else "") + f(x, n)
    linhas_m = []
    for x in mt["linhas"]:
        aj_ = x["ajuste"]
        r2o = f(aj_["r2"], 3)
        linhas_m.append([sinal(x["furos"], 0), sinal(x["giro"], 2), str(x["pares"]),
                         f"{f(x['theta_valido'][0], 1)} a {f(x['theta_valido'][1], 1)}",
                         f"{f(x['tau_max_N_m'], 2)} em {f(x['theta_tau_max'], 1)}°",
                         f(x["r2_mesma_mola"], 3) if x["toda_faixa"] else "",
                         f(aj_["k"], 3) if x["toda_faixa"] else "",
                         r2o if x["toda_faixa"] else ""])
    a(TABELA(["Furos", "Giro (°)", "Pares", "Θ válido (°)", "Máximo de τ, mesma mola "
              "(N·m)", "R², mesma mola", "k, outra mola (N/mm)", "R², outra mola"],
             linhas_m, [760, 1000, 720, 1480, 1900, 1080, 1240, 1180],
             ["center"]*8))
    a(FONTE)
    a(PEQUENO("Nota: giro positivo no sentido anti-horário, na vista das Figuras 14C e "
              "14D; pares: furos do came e da polia que coincidem, admitidos iguais nas "
              f"duas peças. Mesma mola: k = {f(aj['k_N_por_mm'], 3)} N/mm e "
              f"x_{{0}} = {f(aj['x0_mm'], 1)} mm, com o alongamento contado do comprimento "
              "do cabo da mola. Outra mola: k e x_{0} ajustados à Figura 16 da "
              "US 9.737.374 B2 em cada montagem; k negativo não corresponde a mola "
              "física. Nas montagens de −4, +3 e +4 furos, o cabo da mola sai do canal em "
              "parte da faixa do ajuste, e os R² não foram calculados."))
    a(LEG_F("e3_mont", "Montagens do came nos furos em torno do pino 572: torque com a "
            "mesma mola e o mesmo cabo da montagem desenhada (a) e R² do ajuste de outra "
            "mola à curva AASM da Figura 16 da US 9.737.374 B2 (b)"))
    a(FIGURA("exo3_tcc_fig_6_montagens.png", 6.3,
             "Curvas de torque das nove montagens do came e R² do ajuste de outra mola "
             "em função do giro"))
    a(PEQUENO("Fonte: elaborada pelo autor, a partir das Figuras 14C, 14D e 16 da "
              "US 9.737.374 B2 (DOYLE, 2017).", True))
    a(PEQUENO("Nota: em (a), faixas sombreadas: marcas das zonas Z12 e Z11 na Figura 16 "
              "da US 9.737.374 B2; cada curva vai até onde o cabo da mola sai do canal. "
              "Em (b), linha: giro contínuo da Figura ⟦F:e3_giro⟧a; as montagens de −4, +3 "
              "e +4 furos não aparecem, pelo motivo da Tabela ⟦T:e3_mont⟧."))

    # ------------------------------------------------------------ confronto
    co, ea, fg = N3["confronto"], N3["escala_artigo"], N3["fig16"]
    c0 = next(x for x in co["linhas"] if x["theta"] == 0.0)
    ra = [x["razao_aasm"] for x in co["linhas"]]
    rm = [x["razao_modelo"] for x in co["linhas"]]
    a(SEC("4.3", "e3_r_conf", "Confronto entre o torque do cabo e o torque gravitacional"))
    a(P("Pela Equação (⟦E:e3_tg⟧), o torque gravitacional do conjunto chega a "
        f"{f(cj['tau_g_max_N_m'], 2)} N·m em Θ = {f(cj['theta_tau_g_max'], 1)}°, quase "
        "com o eixo na horizontal. Na horizontal, o membro responde "
        f"por {f(mb['momento_horizontal_N_m'], 2)} N·m, e o apoio de braço, por "
        f"{f(pa['momento_zero_N_m'], 2)} N·m, "
        f"{f(100*pa['momento_zero_N_m']/mb['momento_horizontal_N_m'], 0)}% do membro. "
        f"Sozinho, o peso do apoio chega a {f(pa['momento_max_N_m'], 2)} N·m em "
        f"Θ = {f(pa['theta_momento_max'], 1)}° e vale {f(pa['momento_pose_N_m'], 2)} N·m na "
        "pose do CAD; o giro do came muda esse valor em até "
        f"{f(pa['came_variacao_max_N_m'], 2)} N·m."))
    a(P("A Tabela ⟦T:e3_conf⟧ compara, nos ângulos marcados na Figura 16 da "
        "US 9.737.374 B2, a curva AASM na escala da AWM e o torque do modelo ajustado "
        "com o torque gravitacional do conjunto. A AASM fica entre "
        f"{f(min(ra), 2)} e {f(max(ra), 2)} vezes τ_{{g}}, e o modelo, entre "
        f"{f(min(rm), 2)} e {f(max(rm), 2)} vezes. Na horizontal, a AASM sustenta "
        f"{f(100*fg['aasm_awm_zero'], 0)}% do peso do membro, a razão AASM/|AWM| da "
        f"própria patente, e {f(100*c0['razao_aasm'], 0)}% do peso do conjunto, com o "
        "apoio de braço. Os picos quase coincidem em ângulo: "
        f"a AASM tem máximo em Θ = {f(co['theta_pico_aasm'], 0)}°, τ_{{g}} em "
        f"{f(co['theta_pico_tau_g'], 1)}° e o modelo ajustado em "
        f"{f(co['theta_pico_modelo'], 1)}°."))
    a(LEG_T("e3_conf", "Curva AASM, modelo ajustado e torque gravitacional nos ângulos "
            "marcados na Figura 16 da US 9.737.374 B2"))
    rot = {-75.0: "início da curva AASM", -56.4: "base da marca Z12",
           -40.3: "topo da marca Z12", -23.8: "base da marca Z11", 0.0: "horizontal",
           4.0: "topo da marca Z11", 21.0: "último ponto do ajuste"}
    a(TABELA(["Θ (graus)", "Ponto", "AASM (N·m)", "Modelo (N·m)", "τ_{g} (N·m)",
              "AASM/τ_{g}", "Modelo/τ_{g}"],
             [[f(x["theta"], 1), rot[x["theta"]], f(x["aasm_N_m"], 2), f(x["modelo_N_m"], 2),
               f(x["tau_g_N_m"], 2), f(x["razao_aasm"], 2), f(x["razao_modelo"], 2)]
              for x in co["linhas"]],
             [1000, 2200, 1200, 1200, 1200, 1280, 1280],
             ["right", "left", "right", "right", "right", "right", "right"]))
    a(FONTE)
    a(P("O artigo de Okabe, Brittes e Brito (2026) adotou outra escala, com o máximo da "
        f"AASM em 30 N·m, {f(ea['razao'], 2)} vezes a adotada aqui. Nela, a AWM valeria "
        f"{f(ea['awm_N_m'], 2)} N·m na horizontal, {f(ea['awm_sobre_membro'], 1)} vezes o "
        "torque do peso do membro de referência e "
        f"{f(ea['awm_sobre_membro_artigo'], 1)} vezes o do membro do próprio artigo, de "
        f"{f(mb['artigo_momento_horizontal_N_m'], 2)} N·m: a escala do artigo corresponde "
        "a uma carga entre duas e meia e três vezes o peso do membro. O ajuste nessa "
        "escala tem o mesmo x_{0} e o mesmo R², e a rigidez e as forças crescem na mesma "
        f"razão, com k = {f(ea['k_N_por_mm'], 3)} N/mm (Tabela ⟦T:e3_aj⟧)."))

    # ------------------------------------------------------------ limitações
    a(SEC("4.3", "e3_r_lim", "Limitações dos resultados"))
    a(P("Além das limitações de escopo da seção ⟦S:e3_ferr⟧, os resultados comportam as "
        "ressalvas a seguir."))
    a(P("A principal é a escala. A ordenada da Figura 16 da US 9.737.374 B2 não tem "
        "unidade, e a escala adotada supõe que a AWM seja o momento do peso do membro de "
        "referência, sem ferramenta na mão e sem o apoio de braço; a escala do artigo é "
        f"{f(N3['escala_artigo']['razao'], 2)} vezes maior. O torque em N·m e a rigidez k "
        "da mola valem nessa escala, e k e x_{0} foram identificados pela forma da curva, "
        "e não medidos."))
    a(P("A curva calculada depende do giro do came em relação à primária, em que as "
        "Figuras 14C e 14D da patente discordam em 15,5°. Com o came girado de "
        f"{f(mg['giro'], 0)}°, o ajuste melhora e as zonas caem nas marcas da patente, e "
        "as montagens do came supõem na polia os furos medidos nas figuras. Com a "
        "ancoragem 562 na posição do CAD, o braço não sobe além de "
        f"Θ = {f(N3['theta_limite'], 1)}°, enquanto a curva da patente vai até 30°."))
    a(P("As simplificações da geometria têm efeito pequeno nos resultados: tomar a polia "
        "630 no infinito muda r em até 0,031 R20 numa geometria de teste; a posição do "
        "pivô 584 no referencial da peça, derivada da Figura 14D, muda o momento máximo "
        "do peso em menos de 0,01 N·m; e cada 10 mm de erro no centro de massa da mola, "
        f"ao longo do eixo, mudam o torque do peso em {f(pa['mola_10mm_N_m'], 2)} N·m."))
    a(P("As leituras do perfil do came e da curva de momento da patente não têm "
        "incerteza estimada, e o torque do peso supõe o braço alinhado ao eixo maior do "
        "apoio de braço e o centro do ombro no pivô 584. Por fim, os resultados referem-se "
        "ao membro de referência e limitam-se à análise estática."))

    # ------------------------------------------------------------ comparação
    return B


def parte_4D():
    """Seção 4.4: comparação dos resultados dos três exoesqueletos."""
    aj, mg, co, cj, fg = (N3["ajuste"], N3["melhor_giro"], N3["confronto"],
                          N3["conjunto"], N3["fig16"])
    B = []
    a = B.append
    # comparação entre os três exoesqueletos (antes, seções 4.2.11 e 4.3.10)
    mc2 = rz["modelo_completo"]["curvas"]
    ns2 = nrm["s0"]
    cz2, t3_2 = ns2["cruzamentos"], ns2["trechos"][3]
    r2_forma = [ind[n]["r2"] for n in ORDEM]
    SECOES["comp_res"] = "4.4"
    a(H("4.4 Comparação entre os três exoesqueletos"))
    a(P("A Tabela ⟦T:comp⟧ compara os três exoesqueletos com os números das seções "
        "4.1, 4.2 e 4.3. Os ângulos são comparáveis porque as três convenções medem o "
        "braço a partir da posição pendente: a elevação anatômica da seção 3.1.3, a "
        "anteversão da seção ⟦S:conv⟧ e Θ + 90° (seção ⟦S:e3_conv⟧)."))
    a(LEG_T("comp", "Comparação entre os três exoesqueletos"))
    a(TABELA(
        ["Aspecto", "US 9.889.554 B2 (seção 4.1)", "EP 3 504 033 B1 (seção 4.2)",
         "US 9.737.374 B2 (seção 4.3)"],
        [["Faixa sem torque com o braço baixado",
          "Protuberância junto à junta, não modelada; ponto morto em 30,485° de "
          "elevação",
          f"Contato com o elemento 78; transição em {f(g['theta_t'], 2)}° de "
          "anteversão no CAD, com torque não nulo abaixo dela",
          "Não há no curso analisado; o braço do cabo de ancoragem só se anularia em "
          f"Θ = {f(N3['ponto_morto']['theta'], 1)}°"],
         ["Dado da patente",
          "Uma curva de torque sem unidade na ordenada; 29 pontos extraídos",
          "Três curvas de razão de torques sem escala na ordenada, com pré-tensões "
          f"diferentes; {n_pts} pontos extraídos",
          "Três curvas na mesma figura (AASM, AWM e RM), sem unidade na ordenada; "
          f"{fg['n_pontos']} pontos extraídos de cada"],
         ["Parâmetros identificados",
          "X_{pose} e K, este em unidade da patente; θ_{off} e h congelados, de "
          "origem não reproduzida",
          "s_{0} das três curvas, pelo espaçamento; K não identificável",
          "k e x_{0} da mola linear, na escala da AWM; R20 e giro do came medidos nas "
          "figuras"],
         ["Reprodução da curva publicada", "R^{2} = 0,99839",
          f"R^{{2}} de {f(min(mc2[n]['comum']['r2'] for n in ORDEM), 3)} a "
          f"{f(max(mc2[n]['comum']['r2'] for n in ORDEM), 3)} com os s_{{0}} "
          f"identificados e escala comum; de {f(min(r2_forma), 3)} a "
          f"{f(max(r2_forma), 3)} no ajuste de forma, com s_{{0}} livre por curva",
          f"R^{{2}} = {f(aj['r2'], 3)} com o came como na Figura 14D; "
          f"{f(mg['r2'], 3)} com o came girado de {f(mg['giro'], 0)}°"],
         ["Escala do torque",
          "Unidade da patente; leitura em N·m implausível, com tração de 9,5 kN",
          f"N·m sob a hipótese K = K_{{40}}, com força de {f(pr['F_min'], 0)} a "
          f"{f(pr['F_max'], 0)} N",
          "N·m pela AWM da própria patente, igualada ao peso do membro de referência, "
          f"com força de mola de {f(aj['forca_fim_N'], 0)} a "
          f"{f(aj['forca_inicio_N'], 0)} N"],
         ["Pico do torque de assistência", "97,48° de elevação",
          f"{f(pr['theta_pico'], 1)}° de anteversão, com o s_{{0}} adotado",
          f"{f(co['theta_pico_aasm'] + 90, 0)}° de elevação na curva da patente; "
          f"{f(co['theta_pico_modelo'] + 90, 1)}° no modelo ajustado"],
         ["Torque gravitacional de referência",
          "Conjunto braço e exoesqueleto, pico de 11,1619 N·m",
          f"Membro humano e braço do exoesqueleto, pico de {f(mas['tau_g_pico'])} N·m",
          f"Membro de referência e apoio de braço, pico de {f(cj['tau_g_max_N_m'], 2)} "
          f"N·m em {f(cj['theta_tau_g_max'] + 90, 1)}° de elevação"]],
        [1500, 2620, 2620, 2620]))
    a(PEQUENO("Fonte: elaborada pelo autor, com os resultados das seções 4.1, 4.2 e 4.3.",
              True))
    a(P("O contraste mais útil para o procedimento está na identificação. Uma única "
        "curva sem unidade, como a da US 9.889.554 B2, fixa a forma do perfil, e o "
        "ajuste de quatro parâmetros contra os mesmos 29 pontos reproduz essa forma "
        "sem constituir validação independente (seção 4.1.5). As três curvas da "
        "EP 3 504 033 B1 trazem uma redundância que separou o comprimento de "
        "referência do elástico, determinado pelo espaçamento entre elas, da forma do "
        "perfil, e essa separação revelou uma diferença de forma que o ajuste de uma "
        "curva isolada teria escondido no valor de s_{0}. Na US 9.737.374 B2, a forma "
        "depende também do perfil do came, que a patente publica só como desenho, e de "
        "um giro que os desenhos não fixam com precisão; as marcas das zonas, que não "
        "entram no ajuste, apontam o mesmo giro que melhora o ajuste da mola, uma "
        "redundância parecida com a das três curvas da EP 3 504 033 B1."))
    a(P("Os mecanismos também distribuem a assistência de modo distinto em relação à "
        "demanda gravitacional. O gerador da US 9.889.554 B2 concentra o torque acima "
        "da horizontal e acompanha a forma do peso entre 105° e 150° de elevação "
        "(seção 4.1.8). Com o s_{0} adotado, a forma normalizada do elástico na "
        f"EP 3 504 033 B1 acompanha a do peso de {f(cz2[1], 0)}° a {f(cz2[2], 0)}° e "
        f"fica abaixo dela entre {f(cz2[2], 0)}° e {f(cz2[3], 0)}°, com diferença "
        f"normalizada de até {f(t3_2['extremo'])} em {f(t3_2['theta'], 1)}° (seção "
        "⟦S:r_conf⟧); como essa forma depende da geometria do CAD, que não reproduz a "
        "Figura 16 da patente, a comparação vale para os modelos, e não para os "
        "produtos. Na US 9.737.374 B2, a curva da patente tem máximo em "
        f"Θ = {f(co['theta_pico_aasm'], 0)}°, quase junto ao do torque do peso, em "
        f"{f(co['theta_pico_tau_g'], 1)}° (seção ⟦S:e3_r_conf⟧). A comparação é "
        "quantitativa quanto aos ângulos e à forma dos perfis, mas não quanto à "
        "magnitude: o torque do primeiro dispositivo está em unidade da patente, o do "
        "segundo chega a N·m pela hipótese K = K_{40}, e o do terceiro, pela hipótese "
        "de que a AWM seja o peso do membro de referência."))
    return B


def parte_5C():
    p, aj, mg = N3["pontos"], N3["ajuste"], N3["melhor_giro"]
    pa, cj, mb, ver = N3["peso_apoio"], N3["conjunto"], N3["membro"], N3["verificacoes"]
    apj, co = pa["ajuste_com_peso"], N3["confronto"]
    ra = [x["razao_aasm"] for x in co["linhas"]]
    c0 = next(x for x in co["linhas"] if x["theta"] == 0.0)
    B = []
    a = B.append
    a(H("5.3 Exoesqueleto 3"))
    a(P("Para a US 9.737.374 B2, foram executadas a leitura da arquitetura na patente, a "
        "organização das grandezas do CAD com sua origem e sua conferência com as Figuras "
        "14C e 14D, a composição inercial do membro e do apoio de braço, as convenções "
        "angulares, o circuito do cabo de ancoragem em forma fechada, o torque pelo "
        "produto vetorial e pelo princípio dos trabalhos virtuais, a extração do perfil "
        "do came da Figura 15B, o torque gravitacional, o tratamento da Figura 16 da "
        "US 9.737.374 B2, a identificação da mola na escala da AWM, a varredura do "
        "giro do came e as verificações numéricas."))
    a(P("A pose do CAD é a da Figura 14D, o ponto de ancoragem do CAD cai a menos de 1 mm "
        "do desenhado, e as peças do apoio de braço caem sobre o desenho: as polias nos "
        "pinos, o came com o giro da figura e a mola sobre a mola 636. O mecanismo molda "
        f"o torque por dois caminhos: o raio efetivo do came, de {f(p['pose']['r'], 1)} a "
        f"{f(p['zero']['r'], 1)} mm, e o braço do cabo de ancoragem, de "
        f"{f(p['pose']['braco'], 1)} a {f(p['zero']['braco'], 1)} mm. A transmissão entre "
        "a força da mola e o torque no ombro é multiplicada por "
        f"{f(p['zero']['transm']/p['inicio_fig16']['transm'], 1)} entre Θ = −75° e a "
        "horizontal. O raio efetivo não é o raio cotado na patente: tomar o raio cotado "
        "como braço superestimaria o momento da mola em até 12% na Z11 e em até 49% na "
        "Z12."))
    a(P("Com o giro do came desenhado, uma mola linear reproduz a forma da curva AASM "
        f"com R² = {f(aj['r2'], 3)}; com o came girado de {f(mg['giro'], 0)}°, "
        f"R² = {f(mg['r2'], 3)}, e as zonas Z11 e Z12 do modelo caem dentro das marcas "
        "da Figura 16 da US 9.737.374 B2. A curva da patente parece corresponder a outra "
        "montagem do came ou a outra posição da âncora, e a ancoragem desenhada limita a "
        f"subida a Θ = {f(N3['theta_limite'], 1)}°, contra 30° na curva. Os cinco furos "
        "em torno do pino 572, a "
        f"{f(N3['furos']['passo'], 1)}° um do outro nas Figuras 14C e 14D, permitem nove "
        "montagens do came; a de dois furos no sentido horário, a "
        f"{f(next(x for x in N3['montagens']['linhas'] if x['furos'] == -2)['giro'], 1)}°, "
        "reproduz a curva com R² = "
        f"{f(next(x for x in N3['montagens']['linhas'] if x['furos'] == -2)['ajuste']['r2'], 3)}"
        ", e as montagens no sentido anti-horário só a aproximam com rigidez negativa. "
        "Com a mesma mola, a troca de furo desloca o máximo do torque de "
        f"{f(min(x['theta_tau_max'] for x in N3['montagens']['linhas']), 1)}° a "
        f"{f(max(x['theta_tau_max'] for x in N3['montagens']['linhas']), 1)}°."))
    a(P("A rigidez não é identificável pela AASM sozinha, que não tem unidade, mas a AWM "
        "da própria patente, igualada ao peso do membro de referência, fixa a escala. "
        f"Nela, k = {f(aj['k_N_por_mm'], 3)} N/mm, e a mola trabalha de "
        f"{f(aj['forca_inicio_N'], 0)} a {f(aj['forca_fim_N'], 0)} N; com o peso do apoio "
        f"de braço somado ao alvo, k = {f(apj['k_N_por_mm'], 3)} N/mm. O apoio tem "
        f"{f(pa['massa_g']/1000, 3)} kg e acrescenta "
        f"{f(100*pa['momento_zero_N_m']/mb['momento_horizontal_N_m'], 0)}% ao torque do "
        "peso do membro com o braço na horizontal, onde a AASM sustenta "
        f"{f(100*N3['fig16']['aasm_awm_zero'], 0)}% do peso do membro e "
        f"{f(100*c0['razao_aasm'], 0)}% do peso do conjunto. A escala de 30 N·m do artigo "
        f"de Okabe, Brittes e Brito (2026) é {f(N3['escala_artigo']['razao'], 1)} vezes "
        "maior e corresponde a uma carga entre duas e meia e três vezes o peso do membro."))
    a(P("As relações do circuito foram verificadas com resíduos de até "
        f"{sci(max(ver['fechamento_cad_mm'], ver['S_cad_mm'], ver['b_cad_mm'], ver['braco_duas_formas_mm']))} mm "
        "contra o CAD e entre as duas formas do braço de momento, e o princípio dos "
        "trabalhos virtuais, com diferença relativa de "
        f"{sci(ver['trabalho_virtual_rel'])}. Na varredura do giro do came, o melhor "
        "ajuste e as marcas das zonas da patente apontam o mesmo giro, "
        f"{f(mg['giro'], 0)}° em relação ao desenho, a "
        f"{f(abs(next(x for x in N3['montagens']['linhas'] if x['furos'] == -2)['giro'] - mg['giro']), 1)}° "
        "da montagem de dois furos."))
    a(P("Dos objetivos acrescentados para esse dispositivo, o item j foi cumprido: o "
        "circuito do cabo de ancoragem e o perfil do came foram reconstruídos das figuras "
        "e do CAD e conferidos entre si. O item k foi cumprido na parte estática, com a "
        "ressalva de que a comparação com a curva publicada depende da escala fixada pela "
        "AWM e "
        "do giro do came. Para esse dispositivo, o objetivo geral foi atingido na parte "
        "estática; as etapas dinâmicas não foram executadas, pelas razões da seção "
        "⟦S:e3_din⟧."))
    a(P("Como continuidade para esse dispositivo, recomenda-se medir a rigidez e o "
        "comprimento livre da mola e o giro do came na peça real, que fixariam a escala e "
        "a montagem do came, e, com a escala resolvida, executar as etapas dinâmicas pela "
        "formulação de Lagrange e no MBDyn."))
    return B


def parte_5D():
    """Seção 5.4: o que as conclusões dos três exoesqueletos têm em comum e em que
    diferem."""
    co = N3["confronto"]
    abaixo = pr["theta_pico"] < mas["theta_tau_g_pico"]
    return [
        H("5.4 Comparação entre os três exoesqueletos"),
        P("Os três dispositivos diferem tanto na arquitetura quanto no que suas patentes "
          "permitem identificar. O gerador da US 9.889.554 B2 reproduz a curva publicada "
          "com R^{2} de 0,99839, mas em unidade da patente; o dispositivo da "
          "EP 3 504 033 B1 tem s_{0} determinado pelo espaçamento entre três curvas, mas "
          "sua forma não é reproduzida pelo modelo do CAD, e o torque só chega a N·m por "
          "hipótese; e o mecanismo da US 9.737.374 B2 molda o torque pelo came, cujo giro "
          "em relação à primária é o parâmetro mais sensível, e chega a N·m pela AWM da "
          "própria patente, sob a hipótese de que ela seja o peso do membro de "
          "referência."),
        P("O pico de assistência fica acima do pico gravitacional no primeiro, 8,1° "
          f"(97,5° contra 89,4°), e {'abaixo' if abaixo else 'acima'} no segundo, "
          f"{f(abs(pr['theta_pico'] - mas['theta_tau_g_pico']), 1)}° "
          f"({f(pr['theta_pico'], 1)}° contra {f(mas['theta_tau_g_pico'], 1)}°); no "
          "terceiro, a curva da patente tem máximo em "
          f"{f(co['theta_pico_aasm'] + 90, 0)}° de elevação, quase junto ao do peso, em "
          f"{f(co['theta_pico_tau_g'] + 90, 1)}°. A faixa sem torque com o braço baixado "
          "é obtida, segundo as patentes, por uma protuberância no primeiro e pelo "
          "contato com o elemento de encosto no segundo, e o terceiro não tem faixa sem "
          "torque no curso analisado. Nos três, a magnitude do torque depende de "
          "hipótese, e a comparação proposta na seção 2.11 fica respondida quanto aos "
          "ângulos e à forma dos perfis, mas não quanto à magnitude."),
    ]


def ref_brent():
    return ('<w:p><w:r><w:t xml:space="preserve">BRENT, R. P. </w:t></w:r>'
            '<w:r><w:rPr><w:b/></w:rPr><w:t>Algorithms for minimization without '
            'derivatives</w:t></w:r><w:r><w:t xml:space="preserve">. Englewood '
            'Cliffs: Prentice-Hall, 1973.</w:t></w:r></w:p>')


def ref_virtanen():
    return ('<w:p><w:r><w:t xml:space="preserve">VIRTANEN, P. et al. SciPy 1.0: '
            'fundamental algorithms for scientific computing in Python. </w:t></w:r>'
            '<w:r><w:rPr><w:b/></w:rPr><w:t>Nature Methods</w:t></w:r>'
            '<w:r><w:t xml:space="preserve">, [S.l.], v. 17, n. 3, p. 261-272, 2020. '
            'DOI: </w:t></w:r>'
            f'<w:hyperlink r:id="{RID_DOI}" w:history="1"><w:r><w:rPr>'
            '<w:rStyle w:val="Hyperlink"/></w:rPr><w:t>10.1038/s41592-019-0686-2</w:t>'
            '</w:r></w:hyperlink><w:r><w:t>.</w:t></w:r></w:p>')


def ref_suitx():
    return ('<w:p><w:r><w:t xml:space="preserve">SUITX. </w:t></w:r>'
            '<w:r><w:rPr><w:b/></w:rPr><w:t>IX SHOULDER AIR</w:t></w:r>'
            '<w:r><w:t xml:space="preserve">. [S.l.], [202-]. Disponível em: '
            '</w:t></w:r>'
            f'<w:hyperlink r:id="{RID_SUITX}" w:history="1"><w:r><w:rPr>'
            f'<w:rStyle w:val="Hyperlink"/></w:rPr><w:t>{URL_SUITX}</w:t>'
            '</w:r></w:hyperlink><w:r><w:t xml:space="preserve">. Acesso em: '
            '23 out. 2026.</w:t></w:r></w:p>')


def ref_mizera():
    """EP no formato das duas patentes US: inventor, título, depositante e titular."""
    return ('<w:p><w:r><w:t xml:space="preserve">MIZERA, O. et al. </w:t></w:r>'
            '<w:r><w:rPr><w:b/></w:rPr><w:t>Vorrichtung zum Unterstützen wenigstens '
            'eines Armes eines Benutzers</w:t></w:r><w:r><w:t xml:space="preserve">. '
            'Depositante e titular: Ottobock SE &amp; Co. KGaA. EP 3 504 033 B1. '
            'Depósito: 6 jun. 2018. Concessão: 29 mar. 2023.</w:t></w:r></w:p>')


def ref_okabe():
    return ('<w:p><w:r><w:t xml:space="preserve">OKABE, E. P.; BRITTES, J. L. P.; BRITO, P. L. A. '
            'Modeling and simulation of an upper limb exoskeleton. </w:t></w:r>'
            '<w:r><w:rPr><w:b/></w:rPr><w:t>Journal of Computational and Nonlinear Dynamics</w:t></w:r>'
            '<w:r><w:t xml:space="preserve">, [S.l.], v. 21, n. 7, art. 071006, '
            'jul. 2026. DOI: </w:t></w:r>'
            f'<w:hyperlink r:id="{RID_OKABE}" w:history="1"><w:r><w:rPr>'
            '<w:rStyle w:val="Hyperlink"/></w:rPr><w:t>10.1115/1.4071946</w:t>'
            '</w:r></w:hyperlink><w:r><w:t>.</w:t></w:r></w:p>')


def ref_zeiaee():
    """No formato das demais do ICORR na lista (Barsotti, Gopura)."""
    return ('<w:p><w:r><w:t xml:space="preserve">ZEIAEE, A. et al. Design and kinematic '
            'analysis of a novel upper limb exoskeleton for rehabilitation of stroke '
            'patients. In: INTERNATIONAL CONFERENCE ON REHABILITATION ROBOTICS (ICORR), '
            '2017, Londres. </w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:t>Proceedings</w:t>'
            '</w:r><w:r><w:t xml:space="preserve"> [...]. [S.l.]: IEEE, 2017. p. 759-764. '
            'DOI: </w:t></w:r>'
            f'<w:hyperlink r:id="{RID_ZEIAEE}" w:history="1"><w:r><w:rPr>'
            '<w:rStyle w:val="Hyperlink"/></w:rPr><w:t>10.1109/ICORR.2017.8009339</w:t>'
            '</w:r></w:hyperlink><w:r><w:t>.</w:t></w:r></w:p>')


# ======================================================================
# OMML pelo pandoc
# ======================================================================

FUNCAO = re.compile(r'<m:r><m:rPr><m:sty m:val="p" /></m:rPr>'
                    r'<m:t>(atan2|max|sin|cos|sen)</m:t></m:r>(?=<m:d>)')


def _como_funcao(inner):
    """Nome de função seguido de parênteses vira m:func, como no original."""
    while (m := FUNCAO.search(inner)):
        ini = m.end()
        prof, k = 0, ini
        for t in re.finditer(r"<(/?)m:d>", inner[ini:]):
            prof += -1 if t.group(1) else 1
            if prof == 0:
                k = ini + t.end()
                break
        nome = (f'<m:fName><m:r><m:rPr><m:sty m:val="p"/></m:rPr>'
                f'<m:t>{m.group(1)}</m:t></m:r></m:fName>')
        inner = (inner[:m.start()] + f"<m:func>{nome}<m:e>{inner[ini:k]}</m:e>"
                 "</m:func>" + inner[k:])
    return inner


def omml(latex):
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp)/"eq.md"
        md.write_text("\n\n".join(f"$${lx}$$" for lx in latex) + "\n",
                      encoding="utf-8")
        out = Path(tmp)/"eq.docx"
        subprocess.run(["pandoc", str(md), "-o", str(out)], check=True)
        with zipfile.ZipFile(out) as z:
            x = z.read("word/document.xml").decode("utf-8")
    maths = re.findall(r"<m:oMathPara>.*?</m:oMathPara>", x, flags=re.S)
    assert len(maths) == len(latex), (len(maths), len(latex))
    saida = []
    for m in maths:
        inner = re.search(r"<m:oMath>.*?</m:oMath>", m, flags=re.S).group(0)
        # ordem exigida pelo esquema OMML: m:nor exclui m:sty, e em m:dPr
        # sepChr vem antes de endChr (o pandoc grava na ordem inversa)
        inner = re.sub(r"(<m:nor\s*/>)<m:sty [^>]*/>", r"\1", inner)
        inner = re.sub(r"(<m:endChr [^>]*/>)(<m:sepChr [^>]*/>)", r"\2\1", inner)
        inner = _como_funcao(inner)
        saida.append('<m:oMathPara><m:oMathParaPr><m:jc m:val="center"/>'
                     f'</m:oMathParaPr>{inner}</m:oMathPara>')
    return saida


# Delimitadores de tamanho fixo. O m:d do Word cresce com o conteúdo, e
# parênteses em volta de φ, ψ, θ* ou de um subscrito saem maiores que os
# vizinhos. Todo m:d sem fração, somatório, raiz ou matriz no argumento vira
# caracteres comuns, do tamanho do texto; os que envolvem frações continuam
# crescendo, como \left( ... \right) no LaTeX. As barras de módulo ficam como
# m:d: soltas, o LibreOffice as lê como operadores.
ALTOS = re.compile(r"<m:(f|nary|rad|m|eqArr|limLow|limUpp|groupChr)>")
DELIM = re.compile(r"<m:d><m:dPr>((?:(?!</m:dPr>).)*)</m:dPr><m:e>"
                   r"((?:(?!<m:d>|</m:d>).)*)</m:e></m:d>", re.S)


def _caractere(c, wrpr):
    return (f'<m:r><m:rPr><m:sty m:val="p"/></m:rPr>{wrpr}'
            f'<m:t>{escape(c)}</m:t></m:r>') if c else ""


def parenteses_fixos(xml):
    def trocar(m):
        pr, arg = m.group(1), m.group(2)
        beg = re.search(r'<m:begChr m:val="([^"]*)"\s*/>', pr)
        end = re.search(r'<m:endChr m:val="([^"]*)"\s*/>', pr)
        if ALTOS.search(arg) or (beg and beg.group(1) == "|"):
            return m.group(0).replace("<m:d>", "<m:d\x00>", 1)   # fica como está
        wrpr = re.search(r"<m:ctrlPr>(<w:rPr>.*?</w:rPr>)</m:ctrlPr>", pr, re.S)
        wrpr = wrpr.group(1) if wrpr else ""
        return (_caractere(unescape(beg.group(1)) if beg else "(", wrpr) + arg
                + _caractere(unescape(end.group(1)) if end else ")", wrpr))
    while True:
        novo = DELIM.sub(trocar, xml)
        if novo == xml:
            break
        xml = novo
    return xml.replace("<m:d\x00>", "<m:d>")


# ======================================================================
# montagem
# ======================================================================

def _unico(lista, prefixo):
    achados = [i for i, (_, t, _) in enumerate(lista) if t.startswith(prefixo)]
    assert len(achados) == 1, (prefixo, achados)
    return achados[0]


def apendices():
    """Apêndice A, com os blocos reunidos em APENDICE pelas partes."""
    B = [H_APENDICE("A"),
         P("Este apêndice reúne as análises de robustez da identificação de s_{0} pelo "
           "espaçamento entre as curvas da Figura 16 da EP 3 504 033 B1 (seções "
           "⟦S:ident⟧ e ⟦S:r_s0⟧) e o ajuste de forma, mantido como resultado "
           "secundário (seção ⟦S:r_forma⟧).")]
    B += APENDICE["A_rob"]
    B.append(P("O ajuste de forma deixa s_{0} e a escala livres em cada curva e, por "
               "isso, depende também do braço de momento e do torque do peso do "
               "modelo; a seção ⟦S:r_forma⟧ explica por que ele não foi adotado."))
    B += APENDICE["A_forma"]
    return B


def montar(corpo_original):
    """Lista final de (origem, xml): 'o' para bloco original, 'n' para novo."""
    orig = blocos(corpo_original)
    info = [(b, texto(b), 'w:val="Ttulo2"' in b[:400]) for b in orig]

    # edições: cada trecho "antes" ocorre uma vez no documento
    editados = []
    for b, t, titulo in info:
        regras = []
        for antes, depois in EDICOES:
            if antes in t:
                regras.append((re.escape(antes), lambda m, d=depois: d))
        for padrao, depois in EDICOES_RE:
            if re.search(padrao, t):
                regras.append((padrao, lambda m, d=depois: d))
        # renumeração antes das edições: o texto das EDICOES já traz números
        # novos ("seções 3.1, 4.1 e 5.1"), que não podem ser renumerados
        b2 = editar(theta_em_q(b), (REGRA_TITULO if titulo else []) + REGRAS_ORIGINAL)
        b2 = editar(b2, regras) if regras else b2
        b2 = editar(b2, REFS_EQ + SENO_TEXTO + (ROTULO_EQ if "<m:oMath" in b else []))
        editados.append(b2)
    for antes, _ in EDICOES:
        assert sum(antes in t for _, t, _ in info) == 1, antes
    for padrao, _ in EDICOES_RE:
        assert sum(bool(re.search(padrao, t)) for _, t, _ in info) == 1, padrao

    # pontos de inserção (índice do bloco original depois do qual entra o novo)
    depois = {
        _unico(info, "Este trabalho trata dessa lacuna"): cap1_introducao(),
        _unico(info, "g) acoplar o modelo ao MBDyn"): cap1_objetivos(),
        _unico(info, "A escolha de ferramentas livres"): cap1_justificativa(),
        _unico(info, "A patente US 9.889.554 B2 (VAN ENGELHOVEN"): cap2_compensacao(),
        _unico(info, "O mapeamento da curva torque"): cap2_okabe(),
        _unico(info, "O ajuste, entretanto, encontra limite"): cap2_curva(),
        _unico(info, "Näf et al. (2018)"): cap2_compatibilidade(),
        _unico(info, "O Airframe, da Levitate"): cap2_arquiteturas(),
        _unico(info, "Wu, Wang e Du (2016)"): cap2_balanceamento(),
        _unico(info, "O procedimento usual consiste no ajuste"): cap2_identificacao(),
        _unico(info, "Nota: O é o pivô"): cap3_sobreposicao_fig42(),
        _unico(info, "em que s é o comprimento do vão livre do cabo"): cap3_fechamento_exo1(),
        _unico(info, "Em síntese, a varredura separa duas perguntas"): cap4_ancoragens(),
        _unico(info, "4 RESULTADOS E DISCUSSÃO"): cap4_introducao(),
        _unico(info, "5 CONCLUSÃO"): cap5_titulo(),
        _unico(info, "BOUTERAA, Y.; BEN ABDALLAH"): [ref_brent()],
        _unico(info, "MASARATI, P."): [ref_mizera()],
        _unico(info, "OBUKHOV, A. et al."): [ref_okabe()],
        _unico(info, "SPADA, S. et al."): [ref_suitx()],
        _unico(info, "VAN ENGELHOVEN, L.; KAZEROONI"): [ref_virtanen()],
        _unico(info, "YOON, J. et al."): [ref_zeiaee()],
    }
    antes = {
        _unico(info, "A extensão da mola permanece positiva"): nota_mola(),
        _unico(info, "3.9 Dados da patente"): cap3_trabalho_virtual_exo1(),
        _unico(info, "A cadeia de cálculo descrita nas seções"):
            abertura_comum() + [H("3.1 Exoesqueleto 1")],
        _unico(info, "4 RESULTADOS E DISCUSSÃO"): parte_3B() + parte_3C() + parte_3D(),
        _unico(info, "5 CONCLUSÃO"): parte_4B() + parte_4C() + parte_4D(),
        _unico(info, "REFERÊNCIAS"): parte_5B() + parte_5C() + parte_5D(),
    }
    removidos = [i for i, (_, t, _) in enumerate(info) if t.startswith(REMOVIDOS)]
    assert len(removidos) == len(REMOVIDOS), removidos
    assert not set(removidos) & (set(depois) | set(antes))
    final = []
    for i, b in enumerate(editados):
        final += [("n", editar(x, REFS_EQ + SENO_TEXTO)) for x in antes.get(i, [])]
        if i not in removidos:
            final.append(("o", b))
        final += [("n", editar(x, REFS_EQ + SENO_TEXTO)) for x in depois.get(i, [])]
    # apêndices depois das referências, com os blocos reunidos pelas partes
    final += [("n", editar(x, REFS_EQ + SENO_TEXTO)) for x in apendices()]
    return orig, final, removidos


def citacoes(txt):
    """Figuras da patente citadas no texto novo, para a Tabela de fontes:
    'Figuras 1, 16 e 17 da patente'."""
    fig = {int(n) for m in re.finditer(r"Figuras? (\d+(?:(?:, | e )\d+)*) da (?:patente|EP)", txt)
           for n in re.findall(r"\d+", m.group(1))}
    # a EP 3 504 033 B1 tem 29 figuras; número maior é figura da US citada como
    # "da patente" no texto novo
    assert max(fig) <= 29, sorted(fig)
    itens = [str(x) for x in sorted(fig)]
    lista = itens[0] if len(itens) == 1 else ", ".join(itens[:-1]) + " e " + itens[-1]
    return f"Figura{'s' if len(itens) > 1 else ''} {lista} da patente"


MARCA = re.compile(r"⟦([TFES])([#:])([^⟧]+)⟧")


def numerar(final, n_eq_original):
    """Resolve as marcas em ordem de aparição; devolve o XML e os mapas.
    n_eq_original: equações já numeradas antes da primeira marca (0 quando as
    do original também são marcas)."""
    num = {"T": {}, "F": {}, "E": {}}
    prox = {"T": 1, "F": 1, "E": n_eq_original + 1}
    for _, xml in final:
        for m in MARCA.finditer(xml):
            tipo, sinal, chave = m.groups()
            if sinal == "#":
                assert chave not in num[tipo], f"definição repetida: {tipo} {chave}"
                num[tipo][chave] = prox[tipo]
                prox[tipo] += 1
    num["S"] = SECOES

    def troca(m):
        tipo, _, chave = m.groups()
        assert chave in num[tipo], f"referência sem definição: {tipo} {chave}"
        return str(num[tipo][chave])
    saida = [(o, MARCA.sub(troca, xml)) for o, xml in final]
    usados = {(t, c) for _, xml in final for t, s, c in MARCA.findall(xml) if s == ":"}
    sem_ref = sorted((t, c) for t in "TF" for c in num[t] if (t, c) not in usados)
    return saida, num, sem_ref


def main(origem, destino):
    origem, destino = Path(origem), Path(destino)
    if origem.resolve() == destino.resolve():
        raise SystemExit("o destino não pode ser o arquivo de origem")
    with zipfile.ZipFile(origem) as zin:
        partes = {n: zin.read(n) for n in zin.namelist()}
        infos = {i.filename: i for i in zin.infolist()}
    doc = partes["word/document.xml"].decode("utf-8")
    b0 = doc.index("<w:body>") + len("<w:body>")
    b1 = doc.rindex("<w:sectPr")
    orig, final, removidos = montar(doc[b0:b1])
    cit = citacoes(" ".join(texto(x) for o, x in final
                            if o == "n" and "⟦CITADOS⟧" not in x))
    final = [(o, x.replace("⟦CITADOS⟧", escape(cit))) for o, x in final]

    # equações do original e novas numeradas juntas, por ordem de aparição; as
    # do original não podem trocar de ordem entre si
    n_eq = len(re.findall(r"<w:t>\((\d+)\)</w:t>", doc[b0:b1]))
    assert n_eq == N_EQ_ORIGINAL, n_eq
    final, num, sem_ref = numerar(final, 0)
    ordem = [num["E"][f"o{k}"] for k in range(1, n_eq + 1)]
    assert ordem == sorted(ordem), "equações do original fora de ordem"

    xml = "".join(x for _, x in final)
    for k, m in enumerate(omml(EQUACOES), start=1):
        xml = xml.replace(f"@@OMML{k}@@", m)
    assert "@@OMML" not in xml and "⟦" not in xml and "‹" not in xml
    xml = seno_sin(parenteses_fixos(xml))
    assert not re.search(r"<m:t(?: [^>]*)?>(?:arc)?sen</m:t>", xml)
    novo_txt = "".join(texto(x) for o, x in final if o == "n")
    proibidos = [c for c in ("—", "–") if c in novo_txt]
    assert not proibidos, f"travessão no texto novo: {proibidos}"
    partes["word/document.xml"] = (doc[:b0] + xml + doc[b1:]).encode("utf-8")

    rels = partes["word/_rels/document.xml.rels"].decode("utf-8")
    existentes = {n for n in partes if n.startswith("word/media/")}
    novas_midias = {}
    for k, (caminho, rid, pid) in enumerate(IMAGENS, start=1):
        alvo = f"media/exo2_{k}.png"
        assert f"word/{alvo}" not in existentes and rid not in rels
        novas_midias[f"word/{alvo}"] = caminho.read_bytes()
        rels = rels.replace(
            "</Relationships>",
            f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
            f'officeDocument/2006/relationships/image" Target="{alvo}"/></Relationships>')
    for rid, url in ((RID_DOI, DOI_VIRTANEN), (RID_SUITX, URL_SUITX),
                     (RID_ZEIAEE, DOI_ZEIAEE), (RID_OKABE, DOI_OKABE)):
        assert rid not in rels
        rels = rels.replace(
            "</Relationships>",
            f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
            f'officeDocument/2006/relationships/hyperlink" Target="{url}" '
            'TargetMode="External"/></Relationships>')
    partes["word/_rels/document.xml.rels"] = rels.encode("utf-8")

    # imagens do original refeitas pelo código, no mesmo tamanho em pixels, para
    # que a extensão gravada no documento continue valendo
    from PIL import Image
    for parte, caminho in SUBSTITUIDAS.items():
        with zipfile.ZipFile(origem) as zin, zin.open(parte) as f:
            assert Image.open(f).size == Image.open(caminho).size, parte
        partes[parte] = caminho.read_bytes()

    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w") as zout:
        for nome_parte, dados in partes.items():
            info = infos[nome_parte]
            zi = zipfile.ZipInfo(nome_parte, date_time=info.date_time)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = info.external_attr
            zout.writestr(zi, dados)
        for nome_parte, dados in novas_midias.items():
            zout.writestr(zipfile.ZipInfo(nome_parte, date_time=(1980, 1, 1, 0, 0, 0)),
                          dados, compress_type=zipfile.ZIP_DEFLATED)
    shutil.move(tmp, destino)
    relatorio(orig, final, num, sem_ref, removidos, destino)
    print(f"{destino}: {len(num['T'])} tabelas, {len(num['F'])} figuras, "
          f"{n_eq + len(EQUACOES)} equações ({len(EQUACOES)} novas), "
          f"{len(SECOES)} seções novas")
    if sem_ref:
        print("sem referência no texto:", sem_ref)


def relatorio(orig, final, num, sem_ref, removidos, destino):
    """tcc/relatorio_fusao.md: parágrafos originais alterados, antes e depois."""
    finais_o = [x for o, x in final if o == "o"]
    mantidos = [b for i, b in enumerate(orig) if i not in removidos]
    assert len(finais_o) == len(mantidos)
    mudados = [(texto(a), texto(b)) for a, b in zip(mantidos, finais_o)
               if texto(a) != texto(b)]

    def mapa(tipo):
        return ", ".join(f"{k[1:]} → {v}" for k, v in
                         sorted(num[tipo].items(), key=lambda kv: kv[1])
                         if re.fullmatch(r"o\d+", k))
    linhas = ["# Relatório da fusão dos exoesqueletos 1 e 2", "",
              f"Documento gerado: `{destino.name}`, a partir de `TCC_apenas_exo1.docx`.",
              "", f"Blocos do original: {len(orig)}; {len(removidos)} retirados "
              "(REMOVIDOS em gerar_tcc_fundido.py), os demais mantidos e na mesma ordem. "
              f"Blocos novos: {sum(o == 'n' for o, _ in final)}. Blocos do original "
              f"com texto alterado: {len(mudados)} (renumeração e as edições de "
              "EDICOES em gerar_tcc_fundido.py).", "",
              "## Numeração", "",
              f"Tabelas do original (antes → depois): {mapa('T')}.", "",
              f"Figuras do original (antes → depois): {mapa('F')}.", "",
              f"Equações do original (antes → depois): {mapa('E')}.", "",
              "## Blocos do original retirados", ""]
    linhas += [f"- {texto(orig[i])}" for i in removidos]
    linhas += ["", "## Blocos do original com texto alterado", ""]
    for n, (ta, tb) in enumerate(mudados, start=1):
        linhas += [f"### {n}", "", f"Antes: {ta}", "", f"Depois: {tb}", ""]
    if sem_ref:
        linhas += ["## Elementos sem referência no texto", "",
                   ", ".join(f"{t} {c}" for t, c in sem_ref), ""]
    (destino.parent/"relatorio_fusao.md").write_text("\n".join(linhas), encoding="utf-8")


if __name__ == "__main__":
    from nomes import FUNDIDO, ORIGINAL
    main(sys.argv[1] if len(sys.argv) > 1 else RAIZ/"tcc"/ORIGINAL,
         sys.argv[2] if len(sys.argv) > 2 else RAIZ/"tcc"/FUNDIDO)
