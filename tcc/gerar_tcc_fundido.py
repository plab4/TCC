"""
Gera o TCC com os dois exoesqueletos a partir de tcc/TCC_apenas_exo1.docx,
que não é alterado. A cópia gravada:

- mantém todos os parágrafos, tabelas, equações e figuras do original;
- divide os capítulos 3, 4 e 5 em uma parte por exoesqueleto (3A/3B, 4A/4B,
  5A/5B): as seções originais passam a 3A.k e 4A.k, e o dispositivo da
  EP 3 504 033 B1 entra em 3B, 4B e 5B;
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
    python tcc/gerar_tcc_fundido.py tcc/TCC_apenas_exo1.docx tcc/TCC_exo1_exo2.docx
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


# ======================================================================
# blocos OOXML no formato do documento original
# ======================================================================

RPR = '<w:rPr><w:lang w:val="pt-BR"/></w:rPr>'


def runs(texto, extra=""):
    """Texto com marcação _{...} (subscrito) e ^{...} (sobrescrito)."""
    saida = []
    for parte in re.split(r'(_\{[^}]*\}|\^\{[^}]*\})', texto):
        if not parte:
            continue
        va = ""
        if parte.startswith("_{"):
            va, parte = '<w:vertAlign w:val="subscript"/>', parte[2:-1]
        elif parte.startswith("^{"):
            va, parte = '<w:vertAlign w:val="superscript"/>', parte[2:-1]
        saida.append(f'<w:r><w:rPr>{extra}{va}<w:lang w:val="pt-BR"/></w:rPr>'
                     f'<w:t xml:space="preserve">{escape(parte)}</w:t></w:r>')
    return "".join(saida)


def P(texto):
    return f'<w:p><w:pPr>{RPR}</w:pPr>{runs(texto)}</w:p>'


SECOES = {}          # chave → número da seção (3B.1, 4B.4, ...)
_CONTADOR = {}


def H(texto):
    return (f'<w:p><w:pPr><w:pStyle w:val="Ttulo2"/>{RPR}</w:pPr>'
            f'{runs(texto)}</w:p>')


def SEC(prefixo, chave, titulo):
    """Título de seção numerada dentro de 3B, 4B ou 5B."""
    _CONTADOR[prefixo] = _CONTADOR.get(prefixo, 0) + 1
    numero = f"{prefixo}.{_CONTADOR[prefixo]}"
    assert chave not in SECOES, chave
    SECOES[chave] = numero
    return H(f"{numero} {titulo}")


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


def secao_nova(numero):
    """Seções do original: 3.k → 3A.k e 4.k → 4A.k; as demais não mudam."""
    cap, _, resto = numero.partition(".")
    return f"{cap}A.{resto}" if cap in ("3", "4") and resto else numero


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
REGRA_TITULO = [(r"^([34])\.(\d+) ", lambda m: f"{m.group(1)}A.{m.group(2)} ")]

# Edições do texto original, além da renumeração (antes, depois); cada trecho
# "antes" tem de ocorrer exatamente uma vez no documento.
EDICOES = [
    ("foi executado apenas para o gerador de torque da US 9.889.554 B2, ao qual se "
     "referem todas as equações deste capítulo e todos os resultados do capítulo 4.",
     "foi executado para o gerador de torque da US 9.889.554 B2, ao qual se referem "
     "as seções 3A, 4A e 5A, e para o dispositivo da EP 3 504 033 B1, ao qual se "
     "referem as seções 3B, 4B e 5B."),
    ("Os números e as figuras do capítulo 4 são produzidos",
     "Os números e as figuras da seção 4A são produzidos"),
    ("Este capítulo apresenta os resultados das etapas",
     "Esta seção apresenta os resultados das etapas"),
    ("e a aplicação do procedimento à US 9.737.374 B2 e à EP 3 504 033 B1 não foram "
     "executadas.",
     "e a aplicação do procedimento à US 9.737.374 B2 não foram executadas; a "
     "EP 3 504 033 B1 é tratada na seção 4B."),
    ("e para um dos três dispositivos previstos.",
     "e para o primeiro dos três dispositivos previstos; o segundo é tratado na "
     "seção 5B."),
    ("e estender o procedimento à US 9.737.374 B2 e à EP 3 504 033 B1.",
     "e estender o procedimento à US 9.737.374 B2; a extensão à EP 3 504 033 B1 é "
     "apresentada nas seções 3B, 4B e 5B."),
]


# ======================================================================
# conteúdo novo: dados comuns
# ======================================================================

g, mas, aj = N["geometria"], N["massa"], N["ajuste"]
ind, cj, fc = aj["individual"], aj["conjunto"], aj["forca_constante"]
pr, prf, ver, fam = N["projeto"], N["projeto_forma"], N["verificacoes"], N["familia"]
par, der = g["parametros_cad"], g["derivados"]
inv = N["braco_pose_invertido"]
fg = N["fig16"]["curvas"]
rz = N["razoes"]
s0r = rz["s0"]
tr, po, co = ind["tracejada"], ind["pontilhada"], ind["continua"]
hum = mas["humano"]
corpos = {c["nome"]: c for c in mas["corpos"]}
n_pts = sum(fg[n]["n_total"] for n in ORDEM)
n_aj = sum(ind[n]["n"] for n in ORDEM)
sens = {s["caso"]: s for s in N["sensibilidade_s0"]}
sens_f = {s["caso"]: s for s in N["sensibilidade_s0_forma"]}
nrm = N["normalizado"]["casos"]
nrm_f = N["normalizado_forma"]["casos"]
var = N["varredura"]
tab = {l["theta"]: l for l in pr["tabela"]}
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
        "Nesta etapa, o procedimento foi aplicado a dois mecanismos de arquitetura "
        "distinta. O primeiro é o gerador de torque de mola, cabo e polia da "
        "US 9.889.554 B2 (VAN ENGELHOVEN; KAZEROONI, 2018). O segundo é o "
        "dispositivo da EP 3 504 033 B1 (OTTOBOCK, 2023), em que um elemento "
        "elástico atua diretamente sobre uma alavanca solidária ao braço e um "
        "elemento de apoio junto à articulação anula o torque com o braço baixado. "
        "Os dois são tratados em partes separadas dos capítulos 3, 4 e 5, "
        "identificadas pelas letras A e B.")]


def cap1_objetivos():
    return [P("Para o dispositivo da EP 3 504 033 B1, acrescentam-se os objetivos:"),
            P("h) aplicar a esse dispositivo a reconstrução, a composição inercial, a "
              "cinemática e o confronto com o torque gravitacional previstos nos itens "
              "a, b, c e e, substituindo o cabo e a polia por um circuito de dois "
              "regimes, com o elástico retilíneo ou apoiado no elemento de contato "
              "junto à articulação;"),
            P("i) identificar o comprimento de referência do elástico a partir das três "
              "curvas de pré-tensão publicadas na patente, por um procedimento que não "
              "dependa da escala da ordenada nem da rigidez.")]


def cap1_justificativa():
    return [P(
        "O segundo dispositivo acrescenta ao trabalho um caso de teste do "
        "procedimento de identificação. A EP 3 504 033 B1 publica, na mesma figura, "
        "três curvas obtidas com o mesmo atuador e pré-tensões diferentes "
        "(OTTOBOCK, 2023). Essa redundância permite obter grandezas que uma única "
        "curva sem escala não determina e confrontar, sobre a mesma base de "
        "cálculo, duas arquiteturas que chegaram ao mercado.")]


def cap2_compensacao():
    return [P(
        "Na EP 3 504 033 B1, a faixa sem torque com o braço baixado não depende de "
        "um batente. O elemento elástico passa a encostar, a partir de um ângulo "
        "ajustável, num elemento de apoio situado junto à articulação; com esse "
        "elemento sobre o eixo de rotação, as forças dos dois trechos do elástico "
        "passam pelo eixo e não produzem torque, embora o elástico continue "
        "tracionado (OTTOBOCK, 2023). Na mesma patente, a abscissa das curvas "
        "publicadas tem escala em graus, e só a ordenada é desprovida de escala.")]


def cap2_curva():
    return [P(
        "A EP 3 504 033 B1 explicita esse requisito na forma de preferências de "
        "projeto: nenhuma força abaixo de um ângulo do braço em relação à vertical, "
        "como 45°, 60° ou 90°, e força máxima entre 70° e 120°, de preferência em 90° "
        "(OTTOBOCK, 2023). A patente prevê dois meios de ajustar o perfil, a "
        "pré-tensão do elemento elástico e a excentricidade do ponto de aplicação da "
        "força, e publica curvas para cada um deles.")]


def cap2_arquiteturas():
    return [P(
        "Na patente da Ottobock, a força de apoio é transmitida por uma barra que vai "
        "da articulação junto ao ombro a um cinto pélvico, e o elemento elástico, uma "
        "mola de tração ou um cabo elástico, liga essa barra a uma alavanca do "
        "elemento que acompanha o braço, sem cabo nem polia (OTTOBOCK, 2023). O nome "
        "comercial do produto não aparece no documento, de modo que a associação "
        "com o Paexo não pode ser conferida na patente.")]


def cap2_balanceamento():
    return [P(
        "No dispositivo da EP 3 504 033 B1, o elástico liga diretamente a barra à "
        "alavanca, sem o arranjo de cabo e polia que, segundo Herder (2001), aproxima "
        "a mola da condição de comprimento livre nulo. O perfil de torque resulta da "
        "variação simultânea do comprimento do elástico e do braço de alavanca com o "
        "ângulo, e o contato com o elemento de apoio introduz uma segunda "
        "configuração geométrica, de torque nulo ou reduzido, na faixa de braço "
        "baixado.")]


def cap2_identificacao():
    return [P(
        "Quando uma mesma figura reúne curvas do mesmo dispositivo que diferem por um "
        "único parâmetro, as razões entre elas eliminam os fatores comuns. Na "
        "EP 3 504 033 B1, três curvas foram obtidas com o mesmo atuador e "
        "pré-tensões diferentes; como a rigidez, a escala da ordenada, o braço de "
        "momento e o torque do peso são comuns às três, a razão entre duas curvas "
        "depende apenas do comprimento do elástico e das pré-tensões. Essa "
        "propriedade permite identificar o comprimento de referência do elástico sem "
        "conhecer a escala da ordenada e é a base do procedimento da seção "
        "⟦S:ident⟧.")]


# ======================================================================
# capítulo 3
# ======================================================================

def cap3_introducao():
    return [P(
        "A cadeia de cálculo do dispositivo da EP 3 504 033 B1, descrita nas seções "
        "⟦S:conv⟧ a ⟦S:peso⟧, está implementada no arquivo torque_model_ottobock.py, "
        "e os números e as figuras da seção 4B são produzidos pelo script "
        "tcc_resultados_ottobock.py, que grava os valores citados em "
        "results/ottobock_tcc_numeros.json e as figuras em results/, na mesma "
        "organização usada por torque_model.py e tcc_resultados.py na seção 4A. O "
        "script de resultados não altera parâmetro algum do modelo; as únicas "
        "identificações são as descritas na seção ⟦S:ident⟧.")]


def parte_3B():
    B = []
    a = B.append
    a(H("3B EXOESQUELETO 2: EP 3 504 033 B1"))
    a(P("As seções ⟦S:fontes⟧ a ⟦S:ferr⟧ aplicam à EP 3 504 033 B1 (OTTOBOCK, 2023) "
        "o procedimento das seções 3A.1 a 3A.13, que foi executado para o gerador de "
        "torque da US 9.889.554 B2. Quando uma etapa não se aplica ao mecanismo da "
        "Ottobock ou não pôde ser concluída com os dados disponíveis, a própria "
        "seção registra o motivo."))
    a(P("A classificação de origem é a da introdução deste capítulo: medida no modelo "
        "em CAD, obtida da literatura, documental, identificada por ajuste, derivada "
        "pelo modelo ou assumida como hipótese. Os trechos da patente são citados "
        "pelo número do parágrafo, entre colchetes, pelo número da reivindicação ou "
        "pelo número da figura."))

    # ------------------------------------------------------------ fontes
    a(SEC("3B", "fontes", "Fontes e arquivos utilizados"))
    a(P("A análise usou os documentos e arquivos da Tabela ⟦T:fontes⟧. A patente foi "
        "lida no documento B1 completo, de 44 páginas, com a descrição, os parágrafos "
        "[0001] a [0105], as reivindicações em alemão, inglês e francês e as 29 "
        "figuras, que ocupam as páginas 22 a 43 como imagens bitonais de 300 ppp. Os "
        "dados bibliográficos conferem com a referência já cadastrada: pedido "
        "europeu 18729947.4, depositado em 6 jun. 2018 (PCT/EP2018/064910, "
        "publicado como WO 2018/224555), prioridade alemã DE 10 2017 112 436, de 6 "
        "jun. 2017, e menção da concessão publicada em 29 mar. 2023."))
    a(LEG_T("fontes", "Fontes e arquivos utilizados na análise da EP 3 504 033 B1"))
    a(TABELA(
        ["Fonte", "Conteúdo utilizado", "Classificação", "Verificação nesta análise"],
        [["EP 3 504 033 B1, documento B1 em PDF (OTTOBOCK, 2023)",
          "Arquitetura e numeração dos elementos; [0034], [0043], [0044], [0060], "
          "[0070], [0071], [0092] a [0094], [0099], [0101]; reivindicações 8 e 9; "
          "Figuras 1, 16, 17, 22 e 24", "Documental",
          "Lida integralmente; trechos citados conferidos no original em alemão"],
         ["Modelo em CAD do autor (Autodesk Fusion)",
          "Grandezas da Tabela ⟦T:cad⟧; massa, centro de massa e momento de inércia "
          "do braço do exoesqueleto (elemento 8)", "Medida em CAD",
          "Arquivo do modelo ausente do repositório; valores usados como "
          "informados, sem conferência independente"],
         ["Planilha inercia_steiner_junta20_ottobock.xlsx, do autor",
          "Composição inercial do membro humano e do braço do exoesqueleto",
          "Literatura (de Leva) e medida em CAD",
          "Fórmulas lidas; valores do membro humano reproduzidos pelo modelo "
          "(seção ⟦S:r_geo⟧)"],
         ["Arquivo fig16_curvas.csv, digitalização do autor",
          f"{n_pts} pontos das três curvas da Figura 16 da patente",
          "Documental (extração)",
          "Arquivo lido; procedimento registrado apenas no cabeçalho do arquivo"],
         ["torque_model_ottobock.py e tcc_resultados_ottobock.py",
          "Cadeia de cálculo, identificações, verificações, números e figuras da "
          "seção 4B", "Derivada pelo modelo", "Executados nesta análise"],
         ["torque_model.py e tcc_resultados.py",
          "Organização do modelo e dos resultados da seção 4A",
          "Referência metodológica", "Presentes no repositório; não alterados"]],
        [2000, 3160, 1500, 2700]))
    a(FONTE)

    # ------------------------------------------------------------ arquitetura
    a(SEC("3B", "arq", "Arquitetura descrita na patente"))
    a(P("A EP 3 504 033 B1 descreve um dispositivo de apoio a ao menos um braço do "
        "usuário. O elemento de apoio do braço (6), formado por um elemento "
        "distanciador (8) e uma concha (10) e fixado ao braço por uma braçadeira "
        "(12), liga-se por uma articulação (20) à extremidade superior de um "
        "elemento de transmissão de força (18), uma barra telescópica no exemplo da "
        "Figura 1 da patente [0078], [0079]. A extremidade inferior da barra apoia-se, por uma "
        "articulação esférica (22), num elemento de contra-apoio (16) em forma de "
        "cinto pélvico, de modo que a reação à força de apoio é levada à pelve "
        "[0021], [0022], [0079]. Com o dispositivo vestido, a articulação 20 fica "
        "aproximadamente na altura da articulação do ombro [0021], [0073]."))
    a(P("O atuador passivo (26) é uma mola de tração na Figura 1 da patente [0080] e um cabo "
        "ou fio elástico na Figura 18 da patente [0095]. Uma de suas extremidades fica presa à "
        "barra 18, e a outra atua sobre um elemento de alavanca (28) do elemento "
        "distanciador 8, de modo que a força é aplicada excentricamente em relação "
        "ao eixo da articulação 20 [0043], [0080] (reivindicação 8). A força pode "
        "ser alterada pela pré-tensão do atuador ou pela excentricidade do ponto de "
        "aplicação (reivindicação 9; [0044]). A Figura 24 da patente mostra o ponto de ataque "
        "(82) deslocado com uma chave de fenda em relação ao eixo da articulação "
        "[0101], e [0060] cita o ajuste do comprimento do braço de alavanca por um "
        "parafuso de ajuste."))
    a(P("O elemento 78, chamado na patente de elemento de apoio (Anlageelement), "
        "fica junto à articulação 20 e encosta no elemento elástico a partir de um "
        "ângulo predeterminado entre o elemento de apoio do braço e a barra [0070], "
        "[0099]. A partir do contato, a direção da força deixa de ser a da reta "
        "entre os dois pontos de fixação do elástico e passa a depender do ponto de "
        "contato. A patente prefere o elemento 78 exatamente sobre o eixo da "
        "articulação 20; nesse caso, os dois trechos em que o elástico fica dividido "
        "exercem forças radiais ao eixo e não produzem torque, e o braço desce sem "
        "assistência [0070], [0099]. O ângulo de contato é ajustável [0071], [0099]. "
        "Esse é o mecanismo da faixa sem torque com o braço baixado, que no gerador "
        "da US 9.889.554 B2 resulta da protuberância descrita na seção 2.3."))
    a(P("Como preferência, a patente indica que nenhuma força seja aplicada até que "
        "o braço ultrapasse um ângulo em relação à vertical, com 45°, 60° ou 90° como "
        "exemplos, e que a força máxima ocorra entre 70° e 120°, de preferência em "
        "90° [0043]. O documento não traz cotas do mecanismo nem rigidez, pré-tensão "
        "ou dimensões do elemento elástico. Os dados numéricos que contém são a "
        "largura de 3,0 cm ± 1,0 cm da extremidade livre do cinto [0026], o "
        "afastamento lateral mínimo de 5 cm entre o contra-apoio e a linha média da "
        "coluna [0074], limites para a razão entre a distância da braçadeira à "
        "articulação e a distância da articulação ao contra-apoio [0023] e as "
        "escalas angulares das Figuras 16 da patente e 17, nenhum deles utilizável como "
        "dimensão do gerador de torque."))
    a(P("Essas informações confirmam o que as seções 2.3 e 2.7 dizem do mecanismo: "
        "a força é transmitida por um elemento rígido apoiado na pelve, e o elemento "
        "elástico atua sobre um braço de alavanca ajustável. O nome comercial do "
        "produto não aparece na patente, de modo que a associação com o Paexo, feita "
        "na seção 2.7, não pode ser conferida no documento. A arquitetura não tem "
        "cabo, polia nem tambor: o elástico liga diretamente a barra à alavanca, e a "
        "faixa sem torque resulta do contato com o elemento 78. Por isso, as relações "
        "de tangência, de caminho do cabo e de ponto morto das seções 3A.4 a 3A.7 "
        "não se aplicam e são substituídas pelas das seções ⟦S:cin⟧ e ⟦S:forca⟧."))
    a(P("O dispositivo admite abdução, adução e movimentos do tronco (reivindicação "
        "1; [0016] a [0019]). O modelo é plano, no plano sagital, e representa "
        "somente a anteversão, que é o movimento das Figuras 16 e 17 da patente [0092]."))

    # ------------------------------------------------------------ CAD
    a(SEC("3B", "cad", "Reconstrução geométrica em CAD"))
    a(P("O circuito do mecanismo foi fechado pelo autor no modelo em CAD do Autodesk "
        "Fusion, e as grandezas medidas nesse modelo, com as derivadas delas, estão "
        "na Tabela ⟦T:cad⟧ (seção ⟦S:r_geo⟧). Para o gerador da US 9.889.554 B2, a "
        "seção 4A.1 registra o fator de escala de 0,870 e o critério que o fixou. "
        "Para a Ottobock, nem o arquivo do modelo nem o critério de escala estão no "
        "repositório: as medições não puderam ser conferidas, e a correspondência "
        "entre o modelo e os desenhos da patente não está documentada. As grandezas "
        "são tratadas como medidas em CAD, nos termos da seção 3A.1, e não como "
        "dimensões do dispositivo comercial."))

    # ------------------------------------------------------------ inércia
    a(SEC("3B", "inercia", "Parâmetros inerciais do membro e transporte ao eixo da junta"))
    a(P("O membro humano segue de Leva (1996), com o mesmo indivíduo de referência "
        "da seção 4A: homem de 73,0 kg e 1,741 m, com o cotovelo estendido. Braço, "
        "antebraço e mão estão em série a partir de O, alinhados ao eixo do braço; "
        "os comprimentos escalam com a estatura dividida por 1,741 m, e as massas "
        "são as frações tabeladas da massa corporal. O momento de inércia de cada "
        "segmento no centro de massa é m (r L)^{2}, com r o raio de giração "
        "transversal em fração do comprimento L, e o transporte ao eixo usa a "
        "Equação (1). A Tabela ⟦T:massa⟧, na seção ⟦S:r_geo⟧, reúne os resultados, "
        "que coincidem com os da planilha do autor."))

    # ------------------------------------------------------------ convenções
    a(SEC("3B", "conv", "Referenciais e convenções angulares e de sinal"))
    a(P("O mecanismo é tratado como plano, com origem O no eixo da articulação 20, "
        "admitido coincidente com o centro do ombro, eixo x anterior e eixo y para "
        "cima. Os ângulos são medidos a partir de +x, no sentido anti-horário, com "
        "u(x) = (cos x, sen x), como na seção 3A.4. Comprimentos estão em "
        "milímetros, e os ângulos entram em graus e são convertidos para radianos "
        "uma única vez."))
    a(P("A variável independente é a anteversão do braço, θ_{el}, com 0° para o "
        "braço pendente e 90° para o braço horizontal à frente. É a grandeza da "
        "abscissa das Figuras 16 da patente e 17 da patente, que a define nesses termos [0092]. "
        "Por isso, ao contrário da seção 3A.3, não há calibração angular a "
        "identificar entre o ângulo da patente e a elevação anatômica. O eixo do "
        "braço aponta na direção θ_{el} − 90°. O ângulo λ do trecho e da alavanca, "
        "variável interna da cinemática, relaciona-se com θ_{el} por"))
    a(EQ(("lam", r"\lambda = \theta_{\mathrm{el}} + 90^{\circ} + \lambda_{0}"),
         ("lam0", r"\lambda_{0} = \lambda_{\mathrm{pose}} - \left( 180^{\circ} + \theta_{b,\mathrm{pose}} \right),\quad \theta_{\mathrm{el,pose}} = 90^{\circ} + \theta_{b,\mathrm{pose}}")))
    a(P("em que θ_{b,pose} é o ângulo do braço com a horizontal na pose do CAD, "
        "positivo acima. A Tabela ⟦T:conv⟧ resume as convenções e indica o nome de "
        "cada grandeza no código e sua correspondência com a seção 3A. Alguns "
        "símbolos da seção 3A foram substituídos nesta parte para evitar dois "
        "significados para a mesma letra."))
    a(LEG_T("conv", "Convenções angulares e de sinal do modelo da Ottobock"))
    a(TABELA(
        ["Símbolo", "Definição", "Relação", "No código", "Correspondência na seção 3A"],
        [["θ_{el}", "Anteversão do braço", "Variável independente, em graus",
          "theta_star", "Elevação anatômica θ_{el}, Equação (4)"],
         ["λ", "Ângulo do trecho e a partir de +x", "Equação (⟦E:lam⟧)", "q",
          "Papel de q, Equação (2), com outra definição"],
         ["λ_{0}", "Defasagem constante entre λ e θ_{el} + 90°",
          "Equação (⟦E:lam0⟧)", "delta", "Papel de θ_{off}, sem identificação"],
         ["φ", "Direção do trecho do elástico ligado a A",
          "Equações (⟦E:solI⟧) e (⟦E:solII⟧)", "psi", "Mesmo papel de φ, Equação (8)"],
         ["ℓ", "Comprimento do elástico entre A e P",
          "Equações (⟦E:solI⟧) e (⟦E:solII⟧)", "s", "Mesmo papel de ℓ, Equação (16)"],
         ["s_{0}", "Valor de ℓ em que o elástico atinge o comprimento livre",
          "Seção ⟦S:forca⟧", "s0", "Mesmo papel de s_{0}, Equação (18)"],
         ["δ", "Extensão elástica", "Equação (⟦E:lei⟧)", "x",
          "Mesmo papel de δ, Equação (19)"],
         ["m", "Braço de momento, positivo quando assiste a subida",
          "Equação (⟦E:m⟧)", "braco", "Sinal oposto ao de m na Equação (20)"],
         ["τ", "Torque do elástico", "Positivo no sentido de θ_{el} crescente",
          "tau", "Mesmo sentido de −τ na Tabela ⟦T:o1⟧"],
         ["τ_{g}", "Módulo do torque do peso", "Equação (⟦E:tg⟧)", "torque_peso",
          "Equação (24)"]],
        [1100, 2260, 1900, 1400, 2700], ["center", "left", "left", "center", "left"]))
    a(FONTE)
    a(P("O torque τ é positivo no sentido anti-horário, que é o de θ_{el} "
        "crescente; τ > 0 assiste a subida do braço. O torque do peso tem sinal "
        "oposto na faixa de 0° a 180°, e as comparações usam seu módulo τ_{g}."))
    a(P(f"O sinal de θ_{{b,pose}} = {f(par['BRACO_POSE'])}° está registrado no "
        "código como a confirmar. Com o sinal trocado, λ_{0} passa a "
        f"{f(inv['delta'])}° e θ_{{el,pose}} a {f(inv['theta_pose'])}°; a "
        f"transição de regime da seção ⟦S:cin⟧ vai de {f(g['theta_t'], 2)}° para "
        f"{f(inv['theta_t'], 2)}°; o s_{{0}} da curva tracejada identificado pelo "
        f"espaçamento entre as curvas (seção ⟦S:ident⟧) vai de {f(s0r['tracejada'])} mm "
        f"para {f(rz['braco_pose_invertido']['tracejada'])} mm, e o do ajuste de "
        f"forma, de {f(tr['s0'])} mm para {f(inv['s0'])} mm, com "
        f"{inv['n_regime_II']} dos {tr['n']} pontos ajustados no regime II. Os "
        "resultados da seção 4B dependem, portanto, da confirmação desse sinal "
        "no CAD."))

    # ------------------------------------------------------------ cinemática
    a(SEC("3B", "cin", "Cinemática: equações de circuito e troca de regime"))
    a(P("A ancoragem A do elástico fica na barra 18, e o ponto P, no fim do "
        "cotovelo da alavanca solidária ao braço (Figura ⟦F:circ⟧). O vetor fixo de "
        "A a O, a posição de P e a do centro C_{78} do elemento 78 são"))
    a(EQ(("rAO", r"\mathbf{r}_{AO} = C_{1}\,\mathbf{u}\left( - \alpha_{1} \right) + C_{2}\,\mathbf{u}\left( \gamma_{2} \right),\quad \alpha_{1} = 90^{\circ} - \gamma_{2}"),
         ("P", r"\mathbf{P} = e\,\mathbf{u}(\lambda) + C_{3}\,\mathbf{u}\left( \lambda + \beta_{c} \right),\quad \mathbf{C}_{78} = p_{78}\,\mathbf{u}\left( \lambda + \eta_{78} \right)"),
         ("eta", r"\eta_{78} = \lambda_{78,\mathrm{pose}} - \lambda_{\mathrm{pose}}")))
    a(P("com A = −r_{AO}. Acima do ângulo de transição, o elástico é retilíneo de A "
        "a P (regime I); abaixo dele, encosta no elemento 78 e fica dividido nos "
        "trechos de A ao elemento 78 e do elemento 78 a P (regime II). As equações de "
        "circuito dos dois regimes são"))
    a(EQ(("circI", r"\mathbf{r}_{AO} + e\,\mathbf{u}(\lambda) + C_{3}\,\mathbf{u}\left( \lambda + \beta_{c} \right) - \ell\,\mathbf{u}(\varphi) = \mathbf{0}"),
         ("circII", r"\mathbf{r}_{AO} + p_{78}\,\mathbf{u}\left( \lambda + \eta_{78} \right) - \left( \ell - d_{78} \right)\mathbf{u}(\varphi) = \mathbf{0}")))
    a(P("em que ℓ é o comprimento total do elástico entre A e P, φ a direção do "
        "trecho ligado a A e d_{78} o comprimento do trecho entre o elemento 78 e P. "
        "Como P e o elemento 78 giram juntos com o braço, d_{78} não depende de λ:"))
    a(EQ(("d78", r"d_{78} = \left| \mathbf{P} - \mathbf{C}_{78} \right| = \left| e + C_{3}\,\mathbf{u}\left( \beta_{c} \right) - p_{78}\,\mathbf{u}\left( \eta_{78} \right) \right|")))
    a(P("Cada regime tem solução fechada, sem procedimento iterativo, porque o lado "
        "direito das relações abaixo, a primeira para o regime I e a segunda para o "
        "regime II, é conhecido para cada λ:"))
    a(EQ(("solI", r"\ell\,\mathbf{u}(\varphi) = \mathbf{r}_{AO} + \mathbf{P}"),
         ("solII", r"\left( \ell - d_{78} \right)\mathbf{u}(\varphi) = \mathbf{r}_{AO} + \mathbf{C}_{78}")))
    a(P("A troca de regime não é imposta por um ângulo. Ela é detectada pelo sinal "
        "do produto vetorial"))
    a(EQ(("kappa", r"\kappa = \left\lbrack \left( \mathbf{P} - \mathbf{A} \right) \times \left( \mathbf{C}_{78} - \mathbf{A} \right) \right\rbrack_{z}")))
    a(P("O regime II ocorre quando κ ≥ 0, isto é, quando o elemento 78 ficaria do "
        "outro lado da reta de A a P se o elástico não o contornasse. O ângulo de "
        "transição λ_{t} é a raiz de κ, obtida por bissecção, com a condição de que o "
        "elemento 78 fique entre A e P. Para a geometria do CAD, "
        f"λ_{{t}} = {f(g['lambda_t'])}°, isto é, θ_{{el,t}} = {f(g['theta_t'])}°; "
        f"nesse ponto, ℓ = {f(g['s_t'])} mm e m = {f(g['b_t'])} mm nos dois "
        "regimes."))
    a(P("Com o elemento 78 sobre o eixo (p_{78} = 0), configuração preferida pela "
        "patente [0099], a transição tem forma fechada:"))
    a(EQ(("lamt", r"\lambda_{t} = \operatorname{atan2}\left( r_{AO,y},\ r_{AO,x} \right) - \varepsilon,\quad \varepsilon = \operatorname{atan2}\left( C_{3}\sin\beta_{c},\ e + C_{3}\cos\beta_{c} \right)")))
    a(P("em que ε é o ângulo fixo de OP em relação ao trecho e. Nesse caso, a "
        "direção de OP na transição coincide com a de r_{AO}, a reta do elástico "
        "passa pelo pivô e o torque no regime II é nulo. Com as demais grandezas do "
        f"CAD, a Equação (⟦E:lamt⟧) dá θ_{{el,t}} = {f(g['theta_t_p0'])}°. As curvas "
        "da Figura 16 da patente partem de razão nula entre "
        f"{f(min(fg[n]['inicio'] for n in ORDEM), 2)}° e "
        f"{f(max(fg[n]['inicio'] for n in ORDEM), 2)}° (seção ⟦S:r_dados⟧), entre os "
        "dois valores do modelo; só no caso p_{78} = 0, porém, o modelo tem torque "
        "nulo antes da transição (seção ⟦S:r_conf⟧)."))
    a(LEG_F("circ", f"Circuito do mecanismo na pose do CAD (regime I, "
                    f"θ_{{el}} = {f(der['theta_pose'])}°) e em θ_{{el}} = 10° (regime II)"))
    a(FIGURA("ottobock_tcc_fig_a1_geometria.png", 6.5,
             "Circuito do mecanismo da Ottobock: ancoragem A, pivô O, alavanca com "
             "cotovelo até P, elemento 78 e elástico, na pose do CAD e com o braço "
             "a 10 graus de anteversão; à direita, ampliação da região do pivô."))
    a(FONTE)
    a(PEQUENO("Nota: à direita, ampliação da região do pivô. O traço preto vai de O "
              "ao cotovelo e ao ponto P; os quadrados marcam o centro do elemento "
              "78; as linhas pontilhadas indicam o eixo do braço."))

    # ------------------------------------------------------------ força
    a(SEC("3B", "forca", "Força elástica e torque"))
    a(P("O elástico é tratado como linear e sem massa, com a mesma lei da Equação "
        "(19):"))
    a(EQ(("lei", r"\delta = \max\left( \ell - s_{0},\ 0 \right),\quad F = K\delta")))
    a(P("em que s_{0} é o valor de ℓ em que o elástico atinge o comprimento livre e "
        "K a rigidez. A patente não informa K, o comprimento livre nem a "
        "pré-tensão. O código admite três formas de definir s_{0}: constante, igual "
        f"ao comprimento medido na pose do CAD, ℓ_{{pose}} = {f(par['S_POSE'])} mm, "
        "apenas provisória; por uma pré-tensão X_{pre} num ângulo θ_{el,pre}, com "
        "s_{0} = ℓ(θ_{el,pre}) − X_{pre}, análoga à Equação (18); e identificada a "
        "partir das curvas da Figura 16 da patente (seção ⟦S:ident⟧). As duas "
        "primeiras usam K = 9 N/mm, valor ilustrativo sem origem documental, e não "
        "produzem resultados neste trabalho; a terceira é a adotada, com s_{0} "
        "obtido pelo espaçamento entre as três curvas."))
    a(P("A força do trecho ligado a A atua em P, no regime I, ou no centro do "
        "elemento 78, no regime II, com direção oposta a u(φ):"))
    a(EQ(("tau", r"\tau = \frac{\left\lbrack \mathbf{b} \times \mathbf{V} \right\rbrack_{z}}{1000},\quad \mathbf{V} = - F\,\mathbf{u}(\varphi),\quad \mathbf{b}_{\mathrm{I}} = \mathbf{P},\quad \mathbf{b}_{\mathrm{II}} = \mathbf{C}_{78}")))
    a(P("com b = b_{I} no regime I e b = b_{II} no regime II."))
    a(P("No regime II, o trecho entre o elemento 78 e P liga dois pontos do mesmo "
        "corpo; as forças que exerce sobre P e sobre o elemento 78 são iguais, "
        "opostas e colineares e não contribuem para o torque, o que corresponde à "
        "descrição de [0099]. O braço de momento com sinal é"))
    a(EQ(("m", r"m_{\mathrm{I}} = e\sin\left( \lambda - \varphi \right) + C_{3}\sin\left( \lambda + \beta_{c} - \varphi \right),\quad m_{\mathrm{II}} = p_{78}\sin\left( \lambda + \eta_{78} - \varphi \right),\quad \tau = \frac{Fm}{1000}")))
    a(P("com m = m_{I} no regime I, m = m_{II} no regime II e m > 0 quando o torque "
        "assiste a subida. Como na seção 3A.6, o fator 1/1000 converte N·mm em N·m; "
        "aqui o torque resulta em N·m sempre que K estiver em N/mm. Admitido o "
        "elemento 78 pontual e sem atrito, hipótese que a patente não discute, a "
        "tração é igual nos dois trechos, e o princípio dos trabalhos virtuais exige"))
    a(EQ(("tv", r"\frac{d\ell}{d\lambda} = - m")))
    a(P("com λ em radianos, relação análoga à Equação (17), verificada "
        "numericamente nos dois regimes (seção ⟦S:r_verif⟧). O sinal negativo vem da "
        "convenção de m: o elástico se encurta quando o braço sobe e devolve "
        "energia, como descreve [0034]."))

    # ------------------------------------------------------------ peso
    a(SEC("3B", "peso", "Torque gravitacional"))
    a(P("O torque do peso é calculado de forma independente da cadeia do elástico. "
        "O conjunto que gira com o braço é rígido, e seu centro de massa, a uma "
        "distância D de O e a um ângulo a_{CG} do eixo do braço, acompanha θ_{el}:"))
    a(EQ(("tg", r"\tau_{g} = \frac{MgD\left| \cos\left( \theta_{\mathrm{el}} - 90^{\circ} + a_{CG} \right) \right|}{1000}")))
    a(P("Com apenas o membro humano, a_{CG} = 0 e τ_{g} = M g D sen θ_{el}/1000, "
        f"com máximo de {f(mas['tau_g_pico'])} N·m em θ_{{el}} = 90°. A Equação "
        "(⟦E:tg⟧) mantém a_{CG} para o caso em que o braço do exoesqueleto for "
        "incorporado; nesse caso, o máximo se desloca de a_{CG}, e o torque troca de "
        "sinal perto dos extremos da faixa."))

    # ------------------------------------------------------------ dados
    a(SEC("3B", "dados", "Dados da patente"))
    a(P("As Figuras 16 da patente e 17 da patente mostram curvas obtidas com o dispositivo "
        "[0092]. A abscissa é o ângulo de anteversão, com escala de 0° a 180° e "
        "grade a cada 20°. A ordenada não tem rótulo nem valores, apenas linhas de "
        "grade: há cinco divisões acima da linha de razão nula e uma abaixo (Figura "
        "⟦F:pat16⟧). Segundo [0092], a ordenada da Figura 16 da patente é uma razão de "
        "torques, definida no texto como o torque causado pelo peso do braço "
        "dividido pelo torque aplicado pelo dispositivo. As curvas, porém, partem de "
        "zero perto de 14° e crescem com o ângulo, e com a definição do texto a razão "
        "seria infinita onde o dispositivo não aplica torque. A figura só é coerente "
        "com a razão inversa, torque do dispositivo dividido pelo torque do peso, e "
        "foi assim tratada; a contradição entre o texto e a figura fica registrada."))
    a(P("Segundo [0093], as três curvas da Figura 16 da patente foram obtidas com um único "
        "atuador passivo, com pré-tensões diferentes: quase nula na curva pontilhada "
        "e crescente na tracejada e na contínua. A Figura 17 da patente mantém a pré-tensão e "
        "desloca o ponto de ataque do atuador, cuja distância ao eixo da articulação "
        "cresce da curva pontilhada para a contínua [0094]; o texto descreve a "
        "ordenada dessa figura como a força aplicável ao braço, sem outra "
        "definição."))
    a(LEG_F("pat16", "Figura 16 da EP 3 504 033 B1, razão de torques em função da "
                     "anteversão para três pré-tensões do mesmo atuador"))
    a(FIGURA("ottobock_tcc_fig_patente16.png", 6.0,
             "Reprodução da Figura 16 da EP 3 504 033 B1: três curvas, pontilhada, "
             "tracejada e contínua, em função da anteversão de 0 a 180 graus; "
             "ordenada sem escala."))
    a(PEQUENO("Fonte: OTTOBOCK (2023), Figura 16, p. 31 do documento B1.", True))
    a(PEQUENO("Nota: página do documento girada para a orientação de leitura. A "
              "patente não traz rótulo nem escala na ordenada."))
    a(P("Os pontos das três curvas foram extraídos pelo autor e estão no arquivo "
        "fig16_curvas.csv (Tabela ⟦T:pontos⟧). Segundo o cabeçalho do arquivo, "
        "trata-se da segunda extração; a razão em divisões da grade foi obtida "
        "dividindo a leitura vertical por 21,1311, a abscissa foi mantida sem "
        "correção, e a sobreposição dos pontos à figura teve erro mediano inferior a "
        "0,5 px. O arquivo não informa a imagem nem a resolução usadas na leitura. "
        "No documento B1, a figura está gravada a 300 ppp, com cerca de 215,7 px por "
        "divisão vertical e 266,2 px para 20° da abscissa. Se o erro de 0,5 px se "
        "refere à unidade da leitura vertical, ele corresponde a "
        f"{f(N['fig16']['erro_mediano_div'])} divisão. A incerteza da extração não "
        "foi avaliada de forma independente; a seção ⟦S:ident⟧ propaga esse erro "
        "mediano à identificação por sorteio."))
    a(P("A Figura 17 da patente não foi digitalizada. A seção ⟦S:r_varr⟧ faz apenas uma "
        "comparação visual com ela."))

    # ------------------------------------------------------------ identificação
    a(SEC("3B", "ident", "Identificação dos parâmetros a partir da Figura 16 da patente"))
    a(P("A Figura 16 da patente informa s_{0} de duas maneiras que não dependem da escala da "
        "ordenada: pelo espaçamento entre as três curvas e pelo fim da curva "
        "pontilhada. O ajuste da forma de cada curva, com s_{0} e escala livres, dá "
        "uma terceira estimativa, que depende também do braço de momento e do torque "
        "do peso do modelo. As duas primeiras foram adotadas; a terceira é mantida "
        "como resultado secundário, pelas razões da seção ⟦S:r_forma⟧."))
    a(P("O modelo da razão de torques é"))
    a(EQ(("mu", r"\mu\left( \theta_{\mathrm{el}};\ s_{0} \right) = \frac{\delta\, m}{1000\,\tau_{g}},\quad \hat{r} = c\,\mu")))
    a(P("em que r é a razão extraída, em divisões, e c um fator de escala. Como τ é "
        "linear em K, μ é o torque por unidade de rigidez dividido por τ_{g}, e c "
        "reúne K e o valor desconhecido de uma divisão da ordenada: c = K/σ, com σ "
        "a razão de torques que corresponde a uma divisão. A curva da patente não "
        "separa K de σ, e por isso K não é identificável a partir dela. É a mesma "
        "limitação discutida na seção 4A.6 para o outro mecanismo, aqui explícita "
        "na ausência de escala da ordenada."))
    a(P("Nos procedimentos desta seção, foram usados apenas os pontos com "
        "20° < θ_{el} < 165°. Abaixo de 20°, perto da transição, o modelo está no "
        "regime II e depende da posição do elemento 78; perto de 180°, τ_{g} tende a "
        "zero e a razão varia rapidamente com o ângulo."))
    a(P("As três curvas foram obtidas com o mesmo atuador, na mesma geometria, e "
        "diferem só pela pré-tensão [0093]. Com o elástico tracionado, a razão de "
        "cada curva i escreve-se"))
    a(EQ(("rG", r"r_{i}\left( \theta_{\mathrm{el}} \right) = G\left( \theta_{\mathrm{el}} \right)\left\lbrack \ell\left( \theta_{\mathrm{el}} \right) - s_{0,i} \right\rbrack,\quad G = \frac{K\, m}{1000\,\sigma\,\tau_{g}}")))
    a(P("em que G reúne o que as três curvas têm em comum: a rigidez, a escala da "
        "ordenada, o braço de momento e o torque do peso. Para duas curvas i e j, a "
        "razão r_{i}/r_{j} elimina G, e a relação resultante é linear nos "
        "comprimentos de referência:"))
    a(EQ(("pares", r"r_{j}\, s_{0,i} - r_{i}\, s_{0,j} = \left( r_{j} - r_{i} \right)\ell")))
    a(P("A Equação (⟦E:pares⟧) foi escrita em cada ponto extraído de uma curva, com "
        "a razão da outra interpolada linearmente no mesmo ângulo, para os seis "
        "pares ordenados de curvas, e cada equação foi dividida por r_{i} + r_{j}, "
        "para que os pontos de razão maior não dominem o ajuste. O sistema, com "
        f"{rz['n']} equações e três incógnitas, foi resolvido por mínimos quadrados "
        "lineares, sem procedimento iterativo nem ponto de partida. O método usa "
        "apenas ℓ(θ_{el}) do circuito da seção ⟦S:cin⟧: não depende de K, de σ, de m "
        "nem de τ_{g}."))
    a(P("A identificação foi repetida nas faixas de θ_{el} de 15° a 170°, de 25° a "
        f"160° e de 40° a 150°; em {mc['n']} sorteios com ruído gaussiano de "
        f"{f(mc['sigma_px'], 1)} px, o erro mediano declarado no arquivo, somado às "
        "duas coordenadas de cada ponto; com o sinal de θ_{b,pose} trocado; com a "
        "abscissa da figura deslocada de ±2,47°, diferença entre o início das curvas "
        "e a transição calculada com p_{78} = 0; e com a abscissa espelhada, "
        "θ_{el} → 180° − θ_{el}, como teste de discriminação. Um teste sintético, "
        "com curvas montadas pelo próprio modelo a partir de valores conhecidos de "
        "s_{0} nos ângulos dos pontos extraídos, confere a implementação."))
    a(P("Uma verificação independente vem do fim da curva pontilhada, de "
        "pré-tensão quase nula [0093]. Como ℓ decresce com θ_{el}, Equação "
        "(⟦E:tv⟧), o elástico afrouxa primeiro com o braço elevado, e a razão da "
        "curva menos tensionada deve chegar a zero onde ℓ = s_{0}. O ângulo desse "
        "zero foi obtido por extrapolação linear dos dois e dos três últimos pontos "
        "da curva."))
    a(P("Com os valores identificados, o fator de cada curva é"))
    a(EQ(("Gi", r"G_{i}\left( \theta_{\mathrm{el}} \right) = \frac{r_{i}\left( \theta_{\mathrm{el}} \right)}{\ell\left( \theta_{\mathrm{el}} \right) - s_{0,i}}")))
    a(P("A coincidência das três estimativas testa a hipótese de G comum. A média "
        "das curvas tracejada e contínua, de maior extensão, é comparada à forma "
        "m/(1000 τ_{g}) prevista pelo modelo, com as duas normalizadas em 90°."))
    a(P("No ajuste de forma, para cada s_{0}, a escala e a soma dos quadrados dos "
        "resíduos têm forma fechada:"))
    a(EQ(("sse", r"c = \frac{\sum_{i}\mu_{i}r_{i}}{\sum_{i}\mu_{i}^{2}},\quad SSE = \sum_{i}\left( c\mu_{i} - r_{i} \right)^{2},\quad \frac{RMS}{\max r} = \frac{\sqrt{SSE/n}}{\max_{i}r_{i}}")))
    a(P("O mínimo foi procurado em s_{0} de 0 a 390 mm, em grade de 0,01 mm, e "
        "refinado pelo método de Brent limitado (BRENT, 1973) entre os vizinhos do "
        "melhor ponto, com a biblioteca SciPy (VIRTANEN et al., 2020). Valores "
        "negativos de s_{0} não correspondem a um elástico ligado diretamente entre "
        "A e P e foram excluídos. A faixa de identificação é o intervalo de s_{0}, "
        "na mesma grade, em que a raiz do erro quadrático médio não excede 1,01 vez "
        f"o mínimo. Os {n_aj} pontos ajustados ficaram todos no regime I. A Tabela "
        "⟦T:forma⟧ reúne os resultados, e a Figura ⟦F:ajustes⟧(a) sobrepõe as curvas "
        "ajustadas aos pontos extraídos."))
    a(P("A patente atribui as três curvas a um único atuador [0093] e as desenha no "
        "mesmo eixo, o que implica K e σ comuns e, portanto, um único c. Esse ajuste "
        "conjunto foi feito como verificação independente da hipótese do modelo, "
        "com c comum e um s_{0} por curva:"))
    a(EQ(("cconj", r"c = \frac{\sum_{j}\sum_{i}\mu_{ij}r_{ij}}{\sum_{j}\sum_{i}\mu_{ij}^{2}}")))
    a(P("com j a curva e i o ponto. Os três valores de s_{0} foram buscados por "
        "descida coordenada na mesma grade, a partir de 125 combinações iniciais, "
        "com refinamento de Brent. A Tabela ⟦T:conj⟧ compara o resultado com os "
        "ajustes individuais e com uma força constante, forma limite do modelo "
        "quando s_{0} tende a valores muito negativos; a Figura ⟦F:ajustes⟧(b) mostra "
        "o ajuste conjunto."))
    a(P("Para expressar o torque em N·m, K foi fixado por hipótese de projeto, e "
        "não identificado. O alvo é 40% do torque do peso em θ_{el} = 90°; o "
        "percentual é hipótese do autor, baseada na alegação do fabricante de "
        "redução de até 40% da carga no ombro, alegação que não consta da patente "
        "nem de fonte cadastrada nas referências. O valor correspondente é"))
    a(EQ(("k40", r"K_{40} = \frac{0{,}4\,\tau_{g}\left( 90^{\circ} \right) \cdot 1000}{\delta\left( 90^{\circ} \right)\,m\left( 90^{\circ} \right)}")))
    a(P("calculado com o s_{0} adotado. Como F(90°) = 0,4 τ_{g}(90°)·1000/m(90°) não "
        "depende de s_{0}, a força em 90° é a mesma para qualquer s_{0}; o valor "
        "escolhido muda K_{40} e a distribuição da força no restante da faixa."))

    # ------------------------------------------------------------ varredura
    a(SEC("3B", "varr", "Varredura paramétrica da excentricidade e"))
    a(P("A excentricidade do ponto de aplicação é o parâmetro de ajuste previsto na "
        "patente (reivindicação 9; [0044], [0060], [0101]) e o objeto da Figura 17 da patente "
        "[0094]. Por isso, o papel de h na seção 4A é desempenhado aqui por e. A "
        f"varredura manteve s_{{0}} = {f(pr['s0'])} mm e "
        f"K = {f(pr['K'], 5)} N/mm, isto é, o mesmo elástico, e variou apenas "
        "e, de 20 a 50 mm em passo de 0,05 mm, com o acréscimo do valor do CAD, num "
        f"total de {var['n']} valores. As demais grandezas ficaram congeladas nos "
        "valores da Tabela ⟦T:cad⟧. Como na seção 3A.10, trata-se de diagnóstico, e "
        "nenhum parâmetro é substituído pelo resultado."))

    # ------------------------------------------------------------ verificações
    a(SEC("3B", "verif", "Verificações numéricas"))
    a(P("O modelo executa as verificações da Tabela ⟦T:verif⟧ a cada execução, com "
        "tolerância declarada, e interrompe o cálculo se alguma for violada. As "
        "verificações próprias do cabo e do tambor da seção 3A.11, ponto de "
        "tangência pelas Equações (10) e (13), ponto morto pela Equação (21) e par "
        "da mola, não se aplicam a este mecanismo e foram substituídas pela "
        "continuidade na troca de regime e pelo caso limite p_{78} = 0. Os valores "
        f"são de e = {f(34.785)} mm, com s_{{0}} e K do projeto padrão, em "
        "malha de 0,1° de 0° a 180°."))
    a(P("O modelo verifica ainda que o regime II ocorre exatamente para λ ≤ λ_{t} "
        "na malha, que o elemento 78 fica entre A e P na transição, que e é "
        "argumento obrigatório de toda a cadeia e que dois valores diferentes de e "
        "produzem curvas diferentes. Não há, para este modelo, um conjunto de "
        "testes automatizados executado com o pytest como o da seção 3A.11; as "
        "verificações são asserções executadas a cada cálculo, e a identificação "
        "pelo espaçamento entre as curvas é conferida pelo teste sintético da seção "
        "⟦S:ident⟧."))

    # ------------------------------------------------------------ dinâmica
    a(SEC("3B", "din", "Etapas dinâmicas previstas"))
    a(P("A equação de movimento teria a forma da Equação (27), com θ_{el} como "
        "coordenada generalizada:"))
    a(EQ(("mov", r"I_{O}\,{\ddot{\theta}}_{\mathrm{el}} = \tau\left( \theta_{\mathrm{el}} \right) + \tau_{g,s}\left( \theta_{\mathrm{el}} \right) + Q_{nc}")))
    a(P("em que τ_{g,s} é o torque do peso com sinal e Q_{nc} reúne os esforços não "
        "conservativos. Pela Equação (⟦E:tv⟧), a energia elástica V_{e} = K δ^{2}/2 "
        "satisfaz dV_{e}/dλ = −K δ m, de modo que a força generalizada elástica "
        "coincide, a menos do fator 1/1000, com o torque da Equação (⟦E:m⟧); esse "
        "pré-requisito estático está verificado (Tabela ⟦T:verif⟧)."))
    a(P("A integração não foi executada, pelas razões seguintes. O torque do "
        "elástico só está em N·m sob a hipótese K = K_{40}: a unidade deixou de ser "
        "o impedimento da seção 3A.12, mas a escala resulta de uma hipótese de "
        "projeto, e não de dado do dispositivo. O momento de inércia disponível, "
        f"I_{{O}} = {f(hum['izz_o_kgm2'], 6)} kg·m^{{2}}, é só o do membro humano; o "
        "braço do exoesqueleto, a alavanca e a braçadeira estão fora pela falta da "
        "posição do eixo da articulação no Fusion. Massa e amortecimento do elástico "
        "e atrito no elemento 78 e na articulação 20 são desconhecidos, de modo que "
        "Q_{nc} não pode ser escrito. O MBDyn não está instalado no ambiente em que "
        "esta análise foi executada. Nenhum resultado dinâmico é apresentado, e as "
        "condições para executar a etapa estão na seção ⟦S:r_lim⟧."))

    # ------------------------------------------------------------ ferramentas
    a(SEC("3B", "ferr", "Ferramentas e delimitação"))
    a(P("Foram empregados o Autodesk Fusion, para fechar o circuito do mecanismo e "
        "extrair as propriedades de massa do braço do exoesqueleto; uma planilha "
        "eletrônica, para a composição inercial; e a linguagem Python, com a "
        "biblioteca NumPy (HARRIS et al., 2020) para o cálculo vetorizado, a "
        "biblioteca SciPy (VIRTANEN et al., 2020) para o refinamento pelo método de "
        "Brent (BRENT, 1973) no ajuste de forma e a biblioteca Matplotlib (HUNTER, "
        "2007) para as figuras. A identificação pelo espaçamento entre as curvas é "
        "um problema de mínimos quadrados lineares, resolvido em forma fechada. O "
        "MBDyn não foi empregado."))
    a(P("Valem as exclusões de escopo da seção 3A.13. O modelo é plano, no plano "
        "sagital, e admite elástico linear e sem massa, F = K δ, elemento 78 pontual "
        "e sem atrito e articulação 20 coincidente com o centro do ombro. O torque "
        "gravitacional considera só o membro humano estendido, sem ferramenta na "
        "mão; o braço do exoesqueleto, a alavanca e a braçadeira não entram nele."))
    return B


# ======================================================================
# capítulo 4
# ======================================================================

def cap4_introducao():
    return [P("Os resultados estão organizados por dispositivo. A seção 4A apresenta "
              "os do gerador de torque da US 9.889.554 B2, e a seção 4B, os do "
              "dispositivo da EP 3 504 033 B1, encerrada por uma comparação entre os "
              "dois. O terceiro dispositivo previsto, a US 9.737.374 B2, não foi "
              "analisado nesta etapa."),
            H("4A EXOESQUELETO 1: US 9.889.554 B2")]


def parte_4B():
    B = []
    a = B.append
    a(H("4B EXOESQUELETO 2: EP 3 504 033 B1"))
    a(P("Esta seção apresenta os resultados das etapas das seções ⟦S:cad⟧ a "
        "⟦S:verif⟧, aplicadas ao dispositivo da EP 3 504 033 B1. Salvo indicação em "
        f"contrário, os números foram obtidos com a geometria do CAD, e = {f(34.785)} "
        f"mm, s_{{0}} = {f(pr['s0'])} mm, identificado pelo espaçamento entre as "
        f"curvas da Figura 16 da patente, e K = K_{{40}} = {f(pr['K'], 5)} N/mm, "
        "hipótese de projeto. As etapas dinâmicas da seção ⟦S:din⟧ não foram "
        "executadas."))

    # ------------------------------------------------------------ geometria
    a(SEC("4B", "r_geo", "Geometria reconstruída e propriedades de massa"))
    a(P("A Tabela ⟦T:cad⟧ reúne as grandezas medidas no modelo em CAD e as que delas "
        "derivam, com a origem de cada uma (seção ⟦S:cad⟧)."))
    a(LEG_T("cad", "Grandezas medidas no modelo em CAD e grandezas derivadas"))
    a(TABELA(
        ["Grandeza", "Símbolo", "Valor", "Unidade", "Origem"],
        [["Componente do vetor de A a O na direção u(−α_{1})", "C_{1}",
          f(par["C1"]), "mm", "CAD"],
         ["Componente do vetor de A a O na direção u(γ_{2})", "C_{2}",
          f(par["C2"]), "mm", "CAD"],
         ["Direção de C_{2}", "γ_{2}", f(par["GAMMA"]), "graus", "CAD"],
         ["Direção de C_{1}, perpendicular a C_{2}", "α_{1}", f(der["alpha"]),
          "graus", "Derivada: α_{1} = 90° − γ_{2}"],
         ["Trecho do pivô ao cotovelo da alavanca", "e", f(g["E_CAD"]),
          "mm", "CAD; varrido na seção ⟦S:r_varr⟧"],
         ["Trecho rígido do cotovelo ao ponto P", "C_{3}", f(par["C3"]), "mm", "CAD"],
         ["Giro de C_{3} em relação ao trecho e", "β_{c}", f(par["BETA"]),
          "graus", "CAD"],
         ["Distância do pivô ao centro do elemento 78", "p_{78}", f(par["P"]),
          "mm", "CAD"],
         ["Ângulo do trecho e na pose do CAD", "λ_{pose}", f(par["Q_POSE"]),
          "graus", "CAD"],
         ["Comprimento do elástico na pose do CAD", "ℓ_{pose}", f(par["S_POSE"]),
          "mm", "CAD"],
         ["Direção do centro do elemento 78 na pose do CAD", "λ_{78,pose}",
          f(par["PHI_ABS_POSE"]), "graus", "CAD"],
         ["Ângulo do braço com a horizontal na pose do CAD, positivo acima",
          "θ_{b,pose}", f(par["BRACO_POSE"]), "graus", "CAD; sinal a confirmar"],
         ["Ângulo do elemento 78 em relação ao trecho e", "η_{78}", f(der["phi"]),
          "graus", "Derivado, Equação (⟦E:eta⟧)"],
         ["Defasagem entre λ e θ_{el} + 90°", "λ_{0}", f(der["delta"]), "graus",
          "Derivado, Equação (⟦E:lam0⟧)"],
         ["Anteversão na pose do CAD", "θ_{el,pose}", f(der["theta_pose"]),
          "graus", "Derivado, Equação (⟦E:lam0⟧)"],
         ["Distância de A a O", "|r_{AO}|", f(g["modulo_B"]), "mm",
          "Derivado, Equação (⟦E:rAO⟧)"],
         ["Comprimento do trecho entre o elemento 78 e P", "d_{78}", f(g["d78"]),
          "mm", "Derivado, Equação (⟦E:d78⟧)"],
         ["Distância do pivô ao ponto P", "|OP|", f(g["raio_OP"]), "mm",
          "Derivado"],
         ["Ângulo de OP em relação ao trecho e", "ε", f(g["angulo_OP"]), "graus",
          "Derivado, Equação (⟦E:lamt⟧)"],
         ["Distância do elemento 78 ao cotovelo", "x_{78}", f(g["x78"]), "mm",
          "Derivado; só relatório"]],
        [3560, 1200, 1000, 1100, 2500], ["left", "center", "center", "center", "left"]))
    a(FONTE)
    a(PEQUENO("Nota: ângulos medidos a partir de +x, no sentido anti-horário (seção "
              "⟦S:conv⟧). x_{78} = (p_{78}^{2} + e^{2} − 2 p_{78} e cos η_{78})^{1/2} "
              "não entra no cálculo e não é a extensão do elástico."))
    a(P(f"Na pose do CAD, o modelo situa P em ({f(g['P_pose'][0])}; "
        f"{f(g['P_pose'][1])}) mm e o centro do elemento 78 em "
        f"({f(g['C78_pose'][0])}; {f(g['C78_pose'][1])}) mm, e calcula "
        f"ℓ = {f(g['s_pose_modelo'], 4)} mm, que difere do comprimento medido "
        f"ℓ_{{pose}} em {sci(g['erro_s_pose'])} mm, valor inferior à resolução de "
        "três casas decimais da medida. O elemento 78 está a "
        f"p_{{78}} = {f(par['P'])} mm do eixo da articulação, enquanto a patente "
        "prefere esse elemento sobre o eixo [0099]; as consequências dessa "
        "diferença são tratadas nas seções ⟦S:cin⟧ e ⟦S:r_conf⟧."))
    a(LEG_T("massa", "Propriedades de massa do membro humano em relação ao eixo da "
                     "articulação 20"))
    linhas = []
    for nm, rot in (("braço", "Braço"), ("antebraço", "Antebraço"), ("mão", "Mão")):
        c = corpos[nm]
        L = next(s["L"] for s in mas["segmentos_de_leva"] if s["nome"] == nm)
        linhas.append([rot, f(c["massa"], 4), f(L, 1), f(c["d"]),
                       f(c["izz_cg"], 6), f(c["izz_o"], 6)])
    linhas.append(["Membro humano", f(hum["massa_kg"], 4), "",
                   f"D = {f(hum['cg_raio_mm'])}", f(hum["izz_cg_kgm2"], 6),
                   f(hum["izz_o_kgm2"], 6)])
    a(TABELA(["Segmento", "Massa (kg)", "L (mm)", "Distância do centro de massa a O "
              "(mm)", "I_{cm} (kg·m^{2})", "I_{O} (kg·m^{2})"], linhas,
             [1660, 1300, 1100, 2100, 1600, 1600],
             ["left", "center", "center", "center", "center", "center"]))
    a(PEQUENO("Fonte: elaborada pelo autor, com dados de de Leva (1996).", True))
    a(P("A consistência foi conferida pela Equação (1): "
        f"I_{{cm}} + M D^{{2}} = {f(hum['izz_cg_kgm2'], 6)} + "
        f"{f(hum['izz_o_kgm2'] - hum['izz_cg_kgm2'], 6)} = "
        f"{f(hum['izz_o_kgm2'], 6)} kg·m^{{2}}. A amplitude do momento "
        f"gravitacional do membro é M g D = {f(mas['tau_g_pico'])} N·m."))
    bx = mas["braco_exo"]
    a(P(f"No modelo em CAD, o braço do exoesqueleto (elemento 8) tem massa de "
        f"{f(bx['massa_g'])} g, centro de massa em ({f(bx['cg_fusion'][0])}; "
        f"{f(bx['cg_fusion'][1])}) mm no referencial do Fusion e momento de inércia "
        f"de {sci(bx['izz_cg_gmm2'], 3)} g·mm^{{2}} no centro de massa. São "
        "estimativas obtidas da geometria reconstruída e de um material atribuído no "
        "CAD, náilon 6/6 em peça oca segundo a planilha, e não propriedades do "
        "produto. Esse corpo não entra no torque do peso nem no momento de inércia "
        "desta seção, porque a posição do eixo da articulação 20 no referencial do "
        "Fusion não foi medida; sem ela, a distância do centro de massa ao eixo é "
        "desconhecida. A alavanca, o elemento 78 e a braçadeira não estão modelados "
        "como corpos separados, e as peças do lado do tronco (barra 18, barra de "
        "ancoragem e capas do elástico) apoiam-se no cinto e não giram com o braço. "
        "A Tabela ⟦T:o3⟧ da seção 4A.1 soma ao membro as peças do outro "
        "exoesqueleto; os valores desta seção referem-se só ao membro humano e não "
        "são comparáveis aos totais daquela tabela."))

    # ------------------------------------------------------------ dados
    a(SEC("4B", "r_dados", "Dados extraídos da patente"))
    ini = {n: fg[n]["inicio"] for n in ORDEM}
    rmin = {n: FIG16[n]["razao"][0] for n in ORDEM}
    po_max = FIG16["pontilhada"]["razao"].max()
    th_po = FIG16["pontilhada"]["theta"][FIG16["pontilhada"]["razao"] == po_max]
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
        f"{f(FIG16['pontilhada']['theta'][-1], 2)}°; as curvas tracejada e contínua "
        f"crescem até {f(fg['tracejada']['r_max'], 4)} e "
        f"{f(fg['continua']['r_max'], 4)} divisões em "
        f"{f(fg['tracejada']['theta_r_max'], 2)}° e "
        f"{f(fg['continua']['theta_r_max'], 2)}°."))
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
    a(PEQUENO("Fonte: elaborada pelo autor, a partir da EP 3 504 033 B1 (OTTOBOCK, "
              "2023).", True))
    a(PEQUENO("Nota: valores entre parênteses ficam fora da faixa 20° < θ_{el} < "
              "165° usada na identificação (seção ⟦S:ident⟧)."))

    # ------------------------------------------------------------ verificações
    a(SEC("4B", "r_verif", "Verificação da cadeia de cálculo"))
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
        [["Equações de circuito do regime I, Equação (⟦E:circI⟧)",
          f"{sci(max(ver['residuo_f1'], ver['residuo_f2']))} mm"],
         ["Equações de circuito do regime II, Equação (⟦E:circII⟧)",
          f"{sci(max(ver['residuo_f3'], ver['residuo_f4']))} mm"],
         ["d_{78} constante em λ, Equação (⟦E:d78⟧)", f"{sci(ver['d_constante'])} mm"],
         ["Fechamento com o comprimento medido na pose do CAD",
          f"{sci(ver['erro_s_pose'])} mm"],
         ["Trabalho virtual no regime I, Equação (⟦E:tv⟧)",
          f"{sci(ver['tv_I'])} mm/rad"],
         ["Trabalho virtual no regime II, Equação (⟦E:tv⟧)",
          f"{sci(ver['tv_II'])} mm/rad"],
         ["Continuidade de ℓ na transição",
          f"{sci(ver['continuidade_s'])} mm"],
         ["Continuidade de τ/F na transição",
          f"{sci(ver['continuidade_tau'])} mm"],
         ["Caso p_{78} = 0: λ_{t} numérico contra a Equação (⟦E:lamt⟧)",
          f"{sci(pz['erro_q'])} rad"],
         ["Caso p_{78} = 0: ℓ = |r_{AO}| + |OP| no regime II",
          f"{sci(pz['erro_s'])} mm"],
         ["Caso p_{78} = 0: τ no regime II, força unitária",
          f"{sci(pz['tau_max'])} N·mm"],
         ["τ pelo produto vetorial contra τ = F m/1000",
          f"{sci(ver['tau_duas_vias'])} N·m"],
         ["Linearidade em K, τ(K) = K τ(K = 1)", f"{sci(ver['erro_linear_K'])} N·m"],
         ["Ancoragem: s_{0} igual para todo e (s_{0} adotado)",
          f"{sci(ver['ancoragem'])} mm"],
         ["Espaçamento entre curvas: s_{0} conhecidos recuperados em curvas "
          "sintéticas", f"{f(sint['erro_max'])} mm"]],
        [6360, 3000], ["left", "center"]))
    a(FONTE)
    a(PEQUENO("Nota: o fechamento com o CAD é limitado pela resolução de três casas "
              "decimais da medida; o trabalho virtual, pelo truncamento da "
              "diferença finita centrada em λ, com passo de 10^{−6} rad."))

    # ------------------------------------------------------------ s0 por razões
    a(SEC("4B", "r_s0", "Identificação de s_{0} pelo espaçamento entre as curvas"))
    s0p, s0t, s0c = (s0r[n] for n in ORDEM)
    a(P("A Tabela ⟦T:s0r⟧ reúne os comprimentos de referência identificados pela "
        f"Equação (⟦E:pares⟧). Na faixa adotada, s_{{0}} vale {f(s0p)} mm na curva "
        f"pontilhada, {f(s0t)} mm na tracejada e {f(s0c)} mm na contínua, com "
        f"resíduo RMS de {f(rz['rms'])} mm nas {rz['n']} equações. A ordem coincide "
        "com a das pré-tensões descritas em [0093], porque menor s_{0} significa "
        "maior extensão do elástico em qualquer ângulo, e os passos entre curvas, "
        f"{f(rz['passos']['pontilhada_tracejada'], 2)} e "
        f"{f(rz['passos']['tracejada_continua'], 2)} mm, são da mesma ordem."))
    a(LEG_T("s0r", "Comprimento de referência s_{0} identificado pelo espaçamento "
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
    linhas.append(lin("Abscissa deslocada de −2,47°", dl["-2.47"]["s0"],
                      f(dl["-2.47"]["rms"])))
    linhas.append(lin("Abscissa deslocada de +2,47°", dl["+2.47"]["s0"],
                      f(dl["+2.47"]["rms"])))
    linhas.append(lin("Sinal de θ_{b,pose} trocado", rz["braco_pose_invertido"],
                      f(rz["rms_braco_pose_invertido"])))
    linhas.append(lin("Abscissa espelhada, θ_{el} → 180° − θ_{el}", esp["s0"],
                      f(esp["rms"])))
    a(TABELA(["Caso", "Pontilhada (mm)", "Tracejada (mm)", "Contínua (mm)",
              "Resíduo RMS (mm)"], linhas, [2960, 1600, 1600, 1600, 1600],
             ["left", "center", "center", "center", "center"]))
    a(FONTE)
    a(PEQUENO(f"Nota: ruído gaussiano de {f(mc['sigma_px'], 1)} px nas duas "
              f"coordenadas de cada ponto, em {mc['n']} sorteios; a faixa adotada "
              "é a dos demais casos, exceto nas linhas de outras faixas."))
    rob_t = [x["s0"]["tracejada"] for x in rz["robustez"]]
    a(P(f"Entre as quatro faixas de θ_{{el}}, o s_{{0}} da curva tracejada varia de "
        f"{f(min(rob_t), 2)} a {f(max(rob_t), 2)} mm. O ruído de extração dá desvio "
        f"padrão de {f(mc['desvio']['tracejada'])} mm nessa curva, e o deslocamento "
        f"de ±2,47° da abscissa a muda para {f(dl['-2.47']['s0']['tracejada'], 2)} e "
        f"{f(dl['+2.47']['s0']['tracejada'], 2)} mm, com resíduo maior que o da "
        f"abscissa original, {f(dl['-2.47']['rms'])} e {f(dl['+2.47']['rms'])} mm. "
        "A maior sensibilidade é ao sinal de θ_{b,pose}: com ele trocado, o s_{0} da "
        f"tracejada vai a {f(rz['braco_pose_invertido']['tracejada'], 2)} mm, e o "
        f"resíduo, a {f(rz['rms_braco_pose_invertido'])} mm. Com a abscissa "
        f"espelhada, o resíduo sobe para {f(esp['rms'], 2)} mm e os três valores de "
        f"s_{{0}} ficam acima de ℓ(0°) = {f(g['l_0'], 2)} mm, maior comprimento do "
        "elástico na faixa, o que o deixaria frouxo em todos os ângulos; essa "
        "leitura da figura é rejeitada."))
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
        "curvas pontilhada e contínua, ℓ = (r_{c} s_{0,p} − r_{p} s_{0,c})/(r_{c} − "
        f"r_{{p}}), difere do ℓ do CAD em {f(lf['rms'], 2)} mm RMS e no máximo "
        f"{f(lf['max_abs'], 2)} mm entre {lf['faixa'][0]:.0f}° e "
        f"{lf['faixa'][1]:.0f}°: a variação de ℓ com o ângulo implícita na figura é "
        "a do modelo."))
    fim = rz["fim_pontilhada"]
    a(P("O fim da curva pontilhada confirma o resultado de forma independente. A "
        f"razão dessa curva chega a zero em {f(fim['2']['theta'], 2)}° pela "
        "extrapolação dos dois últimos pontos e em "
        f"{f(fim['3']['theta'], 2)}° pela dos três últimos, onde "
        f"ℓ = {f(fim['2']['l'], 2)} e {f(fim['3']['l'], 2)} mm, a "
        f"{f(s0p - fim['2']['l'], 2)} mm do s_{{0}} identificado pelo espaçamento, "
        f"que põe o afrouxamento do modelo em {f(rz['theta_frouxo']['pontilhada'], 1)}°. "
        "Com esse s_{0}, a curva pontilhada tem extensão de "
        f"{f(rz['delta_0']['pontilhada'], 2)} mm em 0° e fica frouxa perto de 180°, "
        f"com ℓ(180°) − s_{{0}} = {f(rz['pre_tensao_180']['pontilhada'], 2)} mm, o que "
        "corresponde à descrição de pré-tensão quase nula [0093]; nas curvas "
        "tracejada e contínua, a extensão em 180° é de "
        f"{f(rz['pre_tensao_180']['tracejada'], 2)} e "
        f"{f(rz['pre_tensao_180']['continua'], 2)} mm."))
    ic = rz["inicio"]
    a(P("O ângulo em que as curvas começam, perto de 14°, não identifica s_{0}. As "
        f"três começam em {f(ic['pontilhada']['theta'], 2)}°, "
        f"{f(ic['tracejada']['theta'], 2)}° e {f(ic['continua']['theta'], 2)}°, "
        "apesar das pré-tensões diferentes, e o elástico se encurta quando o braço "
        "sobe: com s_{0} igual a ℓ no início da curva tracejada, "
        f"{f(ic['tracejada']['l'], 2)} mm, o elástico ficaria frouxo em todos os "
        f"{ic['tracejada']['n_acima']} pontos da malha acima desse ângulo, e o "
        "torque seria nulo justamente onde a figura o mostra. O início das curvas "
        "corresponde ao contato do elástico com o elemento 78, cujo ângulo a "
        "patente ajusta pela posição desse elemento [0071], [0099]."))
    a(LEG_F("razoes", "Identificação de s_{0} pelo espaçamento entre as curvas: (a) "
                      "fator G_{i} de cada curva; (b) fator G lido na Figura 16 da patente e "
                      "forma prevista pelo modelo, normalizados em 90°"))
    a(FIGURA("ottobock_tcc_fig_a6_razoes.png", 6.5,
             "À esquerda, razão de cada curva dividida pela extensão do elástico, "
             "em função da anteversão, com as três curvas sobrepostas; à direita, "
             "fator comum lido na figura e forma prevista pelo modelo."))
    a(PEQUENO("Fonte: elaborada pelo autor, a partir da EP 3 504 033 B1 (OTTOBOCK, "
              "2023).", True))
    a(PEQUENO("Nota: s_{0} da Tabela ⟦T:s0r⟧, faixa adotada; em (b), média das curvas "
              "tracejada e contínua."))

    # ------------------------------------------------------------ forma
    a(SEC("4B", "r_forma", "Forma das curvas e ajuste de forma"))
    fr = rz["forma"]["G_sobre_modelo"]
    mcomp = rz["modelo_completo"]["curvas"]
    a(P("Com os valores de s_{0} da Tabela ⟦T:s0r⟧, o fator G lido na Figura 16 da patente e a "
        "forma m/(1000 τ_{g}) do modelo diferem (Figura ⟦F:razoes⟧(b)). "
        "Normalizada em 90°, a razão entre os dois vale "
        f"{f(fr['20'], 2)} em 20°, {f(fr['60'], 2)} em 60°, {f(fr['120'], 2)} em "
        f"120°, {f(fr['150'], 2)} em 150° e {f(fr['165'], 2)} em 165°. Com esses "
        "valores de s_{0} e com o m do CAD e o τ_{g} do membro humano, a razão "
        "calculada não reproduz a Figura 16 da patente: com escala comum às três curvas, o "
        f"coeficiente de determinação é {f(mcomp['pontilhada']['comum']['r2'], 3)} "
        f"(pontilhada), {f(mcomp['tracejada']['comum']['r2'], 3)} (tracejada) e "
        f"{f(mcomp['continua']['comum']['r2'], 3)} (contínua). Como o ℓ implícito na "
        "figura concorda com o do CAD (seção ⟦S:r_s0⟧), a diferença não se explica "
        "por ℓ. Ela pode vir do braço de momento, que depende da derivada de ℓ e é "
        "mais sensível a erros de geometria, ou do torque do peso que a patente usou "
        "para formar a razão, que o texto não define de forma consistente (seção "
        "⟦S:dados⟧). A patente não traz dado que permita separar as duas causas."))
    a(P("O ajuste de forma da seção ⟦S:ident⟧ deixa s_{0} e a escala livres em cada "
        "curva e, por isso, absorve essa diferença em s_{0}. Os valores que ele "
        f"encontra (Tabela ⟦T:forma⟧), {f(po['s0'], 2)} mm na pontilhada, "
        f"{f(tr['s0'], 2)} mm na tracejada e o limite s_{{0}} = 0 na contínua, ficam "
        "longe dos do espaçamento, e as escalas por curva contrariam o atuador único "
        "de [0093]. São mantidos como resultado secundário: descrevem a melhor forma "
        "que o modelo consegue produzir com a geometria do CAD, e não a pré-tensão "
        "do dispositivo."))
    a(LEG_T("forma", "Ajuste de s_{0} à forma de cada curva da Figura 16 da patente"))
    a(TABELA(
        ["Indicador", "Pontilhada", "Tracejada", "Contínua"],
        [["Pontos usados, n"] + [str(ind[n]["n"]) for n in ORDEM],
         ["s_{0} (mm)"] + [s0txt(ind[n]) for n in ORDEM],
         ["Faixa de identificação de s_{0} (mm)"] + [faixa(ind[n]) for n in ORDEM],
         ["Escala c"] + [f(ind[n]["c"], 5) for n in ORDEM],
         ["RMS (divisão)"] + [f(ind[n]["rms"], 4) for n in ORDEM],
         ["RMS/max"] + [pct(ind[n]["rms_max"]) for n in ORDEM],
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
    a(FONTE)
    a(PEQUENO("Nota: resíduo = cμ − r; RMS/max = raiz do erro quadrático médio "
              "dividida pelo maior valor extraído da curva na faixa do ajuste."))
    a(P("A forma da curva fixa s_{0} apenas dentro da faixa de identificação, de "
        f"{f(po['faixa_s0'][1] - po['faixa_s0'][0], 2)} mm na curva pontilhada e "
        f"{f(tr['faixa_s0'][1] - tr['faixa_s0'][0], 2)} mm na tracejada; na "
        "contínua, a faixa encosta no limite s_{0} = 0. O ajuste é pior que o da "
        f"seção 4A: R^{{2}} de {f(po['r2'], 3)} (pontilhada), {f(tr['r2'], 3)} "
        f"(tracejada) e {f(co['r2'], 3)} (contínua), contra 0,99839 na Tabela "
        "⟦T:o7⟧, e resíduos em três ou quatro zonas de sinal, o que indica diferença "
        "sistemática de forma entre o modelo e as curvas. Na curva pontilhada, o "
        "modelo não acompanha a queda da razão acima de 100°, com erro máximo de "
        f"{f(po['erro_max'])} divisão em {f(po['theta_erro_max'], 2)}°. Na "
        "contínua, o mínimo da soma dos quadrados fica no limite s_{0} = 0, que "
        "corresponde a um elástico de comprimento livre nulo no sentido de Herder "
        "(2001), e o erro continua a diminuir quando s_{0} se aproxima desse "
        "limite."))
    a(P(f"No ajuste de forma, a curva tracejada dá K_{{40}} = {f(tr['k_alvo'], 5)} "
        f"N/mm e F(90°) = {f(tr['forca_alvo'], 2)} N. O valor de F(90°) é o mesmo nas "
        "três curvas por construção: cada uma recebe seu K_{40}, e "
        "F(90°) = 0,4 τ_{g}(90°)·1000/m(90°) não depende de s_{0}. Sob a mesma "
        "hipótese, uma divisão da ordenada corresponderia a "
        f"σ = {f(tr['escala_div'])} na curva tracejada, {f(po['escala_div'])} na "
        f"pontilhada e {f(co['escala_div'])} na contínua. Como as três curvas "
        "compartilham o mesmo eixo na patente, os valores distintos de σ mostram que "
        "o alvo de 40% não pode valer para as três ao mesmo tempo com os s_{0} do "
        "ajuste de forma."))
    a(LEG_T("conj", "Ajuste conjunto com escala comum e ajuste com força constante"))
    pcj = cj["por_curva"]
    a(TABELA(
        ["Indicador", "Pontilhada", "Tracejada", "Contínua"],
        [["s_{0}, ajuste individual (mm)"] + [s0txt(ind[n]) for n in ORDEM],
         ["s_{0}, ajuste conjunto (mm)"] + [f(pcj[n]["s0"]) for n in ORDEM],
         ["RMS/max, ajuste individual"] + [pct(ind[n]["rms_max"]) for n in ORDEM],
         ["RMS/max, ajuste conjunto"] + [pct(pcj[n]["rms_max"]) for n in ORDEM],
         ["R^{2}, ajuste conjunto"] + [f(pcj[n]["r2"], 4) for n in ORDEM],
         ["RMS/max, força constante"] + [pct(fc[n]["rms_max"]) for n in ORDEM],
         ["R^{2}, força constante"] + [f(fc[n]["r2"], 4) for n in ORDEM]],
        [2900, 2150, 2150, 2160], ["left", "center", "center", "center"]))
    a(FONTE)
    a(PEQUENO(f"Nota: no ajuste conjunto, c = {f(cj['c'], 4)}, comum às três "
              "curvas; na força constante, c é ajustado por curva."))
    a(P("O ajuste conjunto ordena os comprimentos de referência como as pré-tensões "
        f"descritas em [0093]: s_{{0}} = {f(pcj['pontilhada']['s0'])} mm na curva "
        f"pontilhada, {f(pcj['tracejada']['s0'])} mm na tracejada e "
        f"{f(pcj['continua']['s0'])} mm na contínua; menor s_{{0}} significa maior "
        "extensão do elástico em qualquer ângulo. As curvas tracejada e contínua "
        f"ficam com RMS/max de {pct(pcj['tracejada']['rms_max'])} e "
        f"{pct(pcj['continua']['rms_max'])}, e a pontilhada passa de "
        f"{pct(po['rms_max'])} para {pct(pcj['pontilhada']['rms_max'])}. Com uma "
        "só escala, o modelo linear reproduz a ordem das pré-tensões, mas não a "
        "forma da curva de menor pré-tensão. A força constante descreve a curva "
        f"contínua com RMS/max de {pct(fc['continua']['rms_max'])}, menor que os "
        f"{pct(co['rms_max'])} do ajuste em s_{{0}} = 0, e as outras duas com erros "
        f"de {pct(fc['pontilhada']['rms_max'])} e {pct(fc['tracejada']['rms_max'])}."))
    x0_po = g["l_0"] - po["s0"]
    x0_po_cj = g["l_0"] - pcj["pontilhada"]["s0"]
    a(P("A pré-tensão da curva pontilhada, descrita como quase nula [0093], também "
        "diverge do ajuste de forma. Essa curva exige extensão de "
        f"{f(x0_po, 2)} mm em θ_{{el}} = 0° com o s_{{0}} individual e de "
        f"{f(x0_po_cj, 2)} mm com o do ajuste conjunto; nenhuma das duas é pequena "
        f"diante do curso do elástico na faixa, ℓ(0°) − ℓ(180°) = {f(g['curso'], 2)} "
        "mm. No ajuste de forma, a questão não tem solução com os dados disponíveis; "
        "a identificação pelo espaçamento entre as curvas a resolve, com extensão de "
        f"{f(rz['delta_0']['pontilhada'], 2)} mm em 0° e elástico frouxo perto de "
        "180° (seção ⟦S:r_s0⟧)."))
    a(LEG_F("ajustes", "Pontos extraídos da Figura 16 da patente e razão calculada pelo "
                       "ajuste de forma: (a) escala c por curva; (b) escala c comum "
                       "às três curvas"))
    a(FIGURA("ottobock_tcc_fig_a2_fig16.png", 6.5,
             "Razão de torques em divisões da grade em função da anteversão: pontos "
             "extraídos das três curvas da Figura 16 da patente e curvas do modelo, com a faixa "
             "de 20 a 165 graus sombreada; à esquerda, escala por curva; à direita, "
             "escala comum."))
    a(PEQUENO("Fonte: elaborada pelo autor, a partir da EP 3 504 033 B1 (OTTOBOCK, "
              "2023).", True))
    a(PEQUENO("Nota: faixa sombreada: 20° < θ_{el} < 165°, usada no ajuste; pontos "
              "cinza: fora dessa faixa."))

    # ------------------------------------------------------------ parâmetros
    a(SEC("4B", "r_par", "Parâmetros do modelo"))
    a(P("A Tabela ⟦T:par⟧ resume a situação dos parâmetros que a patente não publica, "
        "no formato da Tabela ⟦T:o6⟧."))
    a(LEG_T("par", "Parâmetros não publicados, origem e identificabilidade"))
    a(TABELA(
        ["Parâmetro", "Símbolo", "Valor adotado", "Origem", "Situação"],
        [["Rigidez do elástico", "K", f"{f(pr['K'], 5)} N/mm",
          "Hipótese de projeto (K_{40})",
          "Não identificável pela Figura 16 da patente, cuja ordenada não tem escala"],
         ["Referência da extensão", "s_{0}", f"{f(pr['s0'])} mm",
          "Identificado pelo espaçamento entre as curvas (tracejada)",
          f"De {f(min(rob_t), 2)} a {f(max(rob_t), 2)} mm entre as faixas de "
          f"θ_{{el}}; {f(rz['braco_pose_invertido']['tracejada'], 2)} mm com o sinal "
          "de θ_{b,pose} trocado"],
         ["Excentricidade do ponto de aplicação", "e", f"{f(34.785)} mm",
          "Medida em CAD", "Não identificada; varrida na seção ⟦S:r_varr⟧"],
         ["Posição do elemento 78", "p_{78}; η_{78}",
          f"{f(par['P'])} mm; {f(der['phi'])}°", "Medida em CAD e derivada",
          "Não identificada; a patente prefere p_{78} = 0 [0099]"],
         ["Defasagem angular", "λ_{0}", f"{f(der['delta'])}°",
          "Derivada do CAD", "Depende do sinal de θ_{b,pose}, a confirmar"],
         ["Massa e centro de massa do braço do exoesqueleto", "", "Não incluídos",
          "Medida em CAD", "Falta a posição do eixo da articulação no Fusion"]],
        [2300, 1060, 1500, 2000, 2500], ["left", "center", "center", "left", "left"]))
    a(FONTE)

    # ------------------------------------------------------------ mecanismo
    a(SEC("4B", "r_mec", "Comportamento do elástico e do mecanismo"))
    a(P(f"Na faixa de 0° a 180° de anteversão, λ varia de {f(g['lambda_faixa'][0])}° "
        f"a {f(g['lambda_faixa'][1])}°, e o regime II ocupa θ_{{el}} de 0° a "
        f"{f(g['theta_t'])}°. O braço de momento permanece positivo em toda a "
        f"faixa, com mínimo de {f(g['b_t'])} mm na transição e máximo de "
        f"{f(g['m_max'])} mm em θ_{{el}} = {f(g['theta_m_max'], 1)}°, igual a |OP|: "
        "no regime I, a linha de ação passa por P, e m não pode exceder a "
        "distância do pivô a esse ponto, teto análogo ao |OA| da seção 3A.5. Como m "
        "não se anula, não há ponto morto na faixa, ao contrário da seção 3A.7. A "
        "Tabela ⟦T:circ⟧ reúne as grandezas do circuito em ângulos representativos."))
    a(LEG_T("circ", f"Grandezas do circuito em ângulos representativos "
                    f"(e = {f(34.785)} mm)"))
    linhas = []
    for l in N["tabela_geometria"]:
        linhas.append([f(l["theta"]), f(l["lambda"]), l["regime"], f(l["l"]),
                       f(l["phi"]), "" if l["l_menos_d"] is None else f(l["l_menos_d"]),
                       f(l["m"])])
    a(TABELA(["θ_{el} (°)", "λ (°)", "Regime", "ℓ (mm)", "φ (°)", "ℓ − d_{78} (mm)",
              "m (mm)"], linhas, [1300, 1300, 1000, 1400, 1300, 1700, 1360],
             ["center"]*7))
    a(FONTE)
    a(PEQUENO(f"Nota: a linha θ_{{el}} = {f(g['theta_t'])}° é a transição; a linha "
              f"θ_{{el}} = {f(der['theta_pose'])}° é a pose do CAD."))
    a(P(f"Com s_{{0}} = {f(pr['s0'])} mm, a extensão do elástico vai de "
        f"{f(pr['x_max'], 2)} mm com o braço pendente a {f(pr['x_min'], 2)} mm em "
        "180°, e o elástico permanece tracionado em toda a faixa. A deformação "
        f"máxima equivale a {pct(pr['deformacao_max'], 1)} do comprimento de "
        f"referência. Com K = K_{{40}}, a força vai de {f(pr['F_0'], 2)} N a "
        f"{f(pr['F_180'], 2)} N. O ajuste de forma levaria a valores bem diferentes: "
        f"com s_{{0}} = {f(prf['s0'])} mm, a extensão iria de {f(prf['x_max'], 2)} a "
        f"{f(prf['x_min'], 2)} mm, com deformação de "
        f"{pct(prf['deformacao_max'], 1)}, e a força, com o K_{{40}} "
        f"correspondente, de {f(prf['F_0'], 2)} a {f(prf['F_180'], 2)} N. A "
        "viabilidade dessas extensões depende do elemento elástico, que a patente "
        "não especifica."))

    # ------------------------------------------------------------ varredura e
    a(SEC("4B", "r_varr", "Varredura paramétrica da excentricidade e"))
    ftr = var["faixas"]["tracao"]
    l45 = fam["linhas"][-1]
    a(P("Dos três critérios de validade física da seção 3A.10, adaptados ao "
        "mecanismo, o fechamento dos dois regimes (ℓ > 0 e ℓ − d_{78} > 0) e o "
        "trabalho virtual foram atendidos em todos os valores de e, com resíduo "
        f"máximo de {sci(var['tv_max'])} mm/rad. A extensão não negativa do elástico "
        f"em toda a faixa só é atendida para e ≤ {f(ftr['max'], 2)} mm, em "
        f"{ftr['n']} dos {var['n']} valores: acima desse valor, com o s_{{0}} "
        "adotado, o elástico afrouxa perto de 180°, como mostra a curva de "
        f"e = {f(l45['e'], 0)} mm, frouxa de {f(l45['frouxo'][0][0], 2)}° a 180°. A "
        f"transição de regime desloca-se de θ_{{el}} = {f(var['theta_t'][1], 2)}° "
        f"(e = 20 mm) para {f(var['theta_t'][0], 2)}° (e = 50 mm). A Tabela "
        "⟦T:fam⟧ e a Figura ⟦F:fam⟧ mostram a família de curvas para cinco valores "
        "de e."))
    a(LEG_T("fam", f"Família de curvas em e, com s_{{0}} = {f(pr['s0'])} mm e "
                   f"K = {f(pr['K'], 5)} N/mm"))
    linhas = [[f(l["e"]), f(l["d78"]), f(l["theta_t"], 2), f(l["tau_pico"]),
               f(l["theta_pico"], 1), f(l["tau_90"]), f(l["razao_90"]),
               f(l["x_min"], 2), f(l["x_max"], 2)] for l in fam["linhas"]]
    a(TABELA(["e (mm)", "d_{78} (mm)", "θ_{el,t} (°)", "Pico de τ (N·m)",
              "θ_{el} do pico (°)", "τ(90°) (N·m)", "τ/τ_{g} em 90°",
              "δ_{mín} (mm)", "δ_{máx} (mm)"], linhas,
             [1000, 1000, 1000, 1100, 1100, 1040, 1040, 1040, 1040], ["center"]*9))
    a(FONTE)
    a(PEQUENO("Nota: τ em N·m depende da hipótese K = K_{40}; as posições dos picos "
              "e da transição não dependem de K. δ_{mín} negativo indica elástico "
              "frouxo."))
    no1, no2 = var["nos"]
    cz = fam["cruzamentos_e_extremos"][0]
    a(P(f"Com o aumento de e, o torque cresce até cerca de {f(cz, 0)}°, ângulo em "
        "que as curvas dos valores extremos de e se cruzam, e diminui acima dele; o "
        f"pico se desloca de {f(fam['linhas'][0]['theta_pico'], 1)}° para "
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
        "difere do da Figura 16 da patente [0094]. No modelo, as curvas de τ/τ_{g} da família "
        f"têm máximo entre {f(min(x['theta'] for x in mx), 1)}° e "
        f"{f(max(x['theta'] for x in mx), 1)}°, tanto mais cedo quanto maior e, e "
        f"vale entre {f(min(x['theta'] for x in mn), 1)}° e "
        f"{f(max(x['theta'] for x in mn), 1)}° nas curvas que permanecem "
        f"tracionadas, e as curvas se cruzam perto de {f(cz, 0)}°. A comparação "
        "quantitativa depende da digitalização da Figura 17 da patente, da definição de sua "
        "ordenada e dos valores de excentricidade, que a patente não informa."))
    a(LEG_F("fam", f"Família de curvas em e, com s_{{0}} = {f(pr['s0'])} mm: (a) "
                   "torque por unidade de rigidez; (b) razão entre o torque do "
                   "elástico e o do peso com K = K_{40}"))
    a(FIGURA("ottobock_tcc_fig_a5_familia.png", 6.5,
             "Cinco curvas para e de 25 a 45 mm em função da anteversão: à "
             "esquerda, torque por unidade de rigidez; à direita, razão entre o "
             "torque do elástico e o do peso."))
    a(FONTE)

    # ------------------------------------------------------------ confronto
    a(SEC("4B", "r_conf", "Confronto com o torque gravitacional"))
    ns = nrm["s0"]
    tre = {(round(t["ini"], 2), round(t["fim"], 2)): t for t in ns["trechos"]}
    cz_n = ns["cruzamentos"]
    t1, t2, t3 = ns["trechos"][1], ns["trechos"][2], ns["trechos"][3]
    assert t1["extremo"] < 0 < t2["extremo"] and t3["extremo"] < 0 and len(cz_n) == 4, tre
    a(P("A forma do torque do elástico pode ser comparada à do peso sem depender de "
        "K, normalizando cada curva pelo próprio pico (Figura ⟦F:norm⟧). Com o "
        "s_{0} adotado, o pico normalizado do elástico ocorre em "
        f"θ_{{el}} = {f(ns['theta_pico_exo'], 1)}°, contra 90° do peso, e as curvas "
        f"normalizadas se cruzam em {f(cz_n[0], 2)}°, no regime II, "
        f"{f(cz_n[1], 2)}°, {f(cz_n[2], 2)}° e {f(cz_n[3], 2)}°. Entre "
        f"{f(cz_n[0], 2)}° e {f(cz_n[1], 2)}°, a forma do elástico fica abaixo da do "
        f"peso, com diferença de até {f(t1['extremo'])} em "
        f"{f(t1['theta'], 1)}°, perto da transição; entre {f(cz_n[1], 2)}° e "
        f"{f(cz_n[2], 2)}°, fica ligeiramente acima, com no máximo "
        f"+{f(t2['extremo'])} em {f(t2['theta'], 1)}°; e acima de "
        f"{f(cz_n[2], 2)}°, volta a ficar abaixo, com diferença de até "
        f"{f(t3['extremo'])} em {f(t3['theta'], 1)}°. Entre as faixas de θ_{{el}} "
        "testadas na identificação, o pico vai de "
        f"{f(nrm['faixa_max']['theta_pico_exo'], 1)}° a "
        f"{f(nrm['faixa_min']['theta_pico_exo'], 1)}°, de modo que essas "
        "conclusões não dependem da faixa escolhida. A posição do pico é compatível "
        "com a preferência da patente de que a força de apoio sobre o braço, "
        "proporcional ao torque na articulação, seja máxima entre 70° e 120° "
        "[0043]."))
    nf = nrm_f["s0"]
    a(P(f"Com o s_{{0}} do ajuste de forma, {f(prf['s0'])} mm, o pico normalizado "
        f"ficaria em {f(nf['theta_pico_exo'], 1)}°, e as curvas se cruzariam em "
        f"{f(nf['cruzamentos'][0], 2)}° e {f(nf['cruzamentos'][-1], 2)}°, com a forma "
        f"do elástico abaixo da do peso até {f(nf['cruzamentos'][-1], 2)}° e acima "
        "dela daí em diante. A distribuição angular da assistência depende, "
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
              "θ_{el} da Tabela ⟦T:s0r⟧."))
    a(P("Em N·m, a comparação só é possível sob a hipótese K = K_{40}, e por isso "
        "a Figura ⟦F:proj⟧ e a Tabela ⟦T:proj⟧ descrevem um cenário de projeto, e "
        "não o dispositivo comercial. Nesse cenário, o torque do elástico atinge "
        f"{f(pr['tau_pico'])} N·m em θ_{{el}} = {f(pr['theta_pico'], 1)}°, e a razão "
        f"τ/τ_{{g}} vai de {f(tab[30.0]['razao'], 2)} em 30° a "
        f"{f(tab[60.0]['razao'], 2)} em 60°, {f(tab[90.0]['razao'], 2)} em 90° e "
        f"{f(tab[150.0]['razao'], 2)} em 150°, com {f(tab[170.0]['razao'], 2)} em "
        f"170°. A força no elástico varia de {f(pr['F_max'], 2)} N, com o braço "
        f"pendente, a {f(pr['F_min'], 2)} N em 180°, e a extensão, de "
        f"{f(pr['x_max'], 2)} mm a {f(pr['x_min'], 2)} mm; o elástico permanece "
        "tracionado em toda a faixa. A viabilidade dessa extensão depende do "
        "elemento elástico, que a patente não especifica."))
    a(LEG_T("proj", f"Projeto padrão: s_{{0}} = {f(pr['s0'])} mm e "
                    f"K = K_{{40}} = {f(pr['K'], 5)} N/mm"))
    linhas = [[f(l["theta"], 0), f(l["lambda"]), l["regime"], f(l["l"]), f(l["x"]),
               f(l["m"]), f(l["F"], 2), f(l["tau"]), f(l["tau_g"]), f(l["razao"])]
              for l in pr["tabela"]]
    a(TABELA(["θ_{el} (°)", "λ (°)", "Regime", "ℓ (mm)", "δ (mm)", "m (mm)",
              "F (N)", "τ (N·m)", "τ_{g} (N·m)", "τ/τ_{g}"], linhas,
             [860, 960, 1000, 960, 960, 900, 900, 940, 1000, 880], ["center"]*10))
    a(FONTE)
    a(PEQUENO("Nota: K_{40} é hipótese de projeto (seção ⟦S:ident⟧); τ_{g} considera "
              "só o membro humano."))
    a(LEG_F("proj", "Cenário de projeto: torque do elástico com K = K_{40}, torque "
                    "do peso do membro humano e alvo de 40%"))
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
        "de cerca de 14°, e a patente prefere o elemento 78 sobre o eixo [0099]. "
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

    # ------------------------------------------------------------ limitações
    a(SEC("4B", "r_lim", "Limitações dos resultados"))
    a(P("Além das limitações de escopo da seção ⟦S:ferr⟧, os resultados comportam as "
        "ressalvas da Tabela ⟦T:pend⟧, que reúne o que falta para concluir cada "
        "etapa, a consequência da ausência e a forma de obter o dado. A principal é "
        "a diferença de forma entre o modelo e a Figura 16 da patente (seção ⟦S:r_forma⟧): o "
        "s_{0} identificado pelo espaçamento entre as curvas não depende dela, mas a "
        "distribuição angular do torque calculado, sim."))
    a(LEG_T("pend", "Pendências da análise da EP 3 504 033 B1"))
    a(TABELA(
        ["Pendência", "Consequência", "Como obter"],
        [["Arquivo do modelo em CAD e critério de escala da reconstrução",
          "Grandezas da Tabela ⟦T:cad⟧ sem conferência independente",
          "Incluir o modelo no repositório e registrar o critério de escala, como "
          "na seção 4A.1"],
         ["Sinal de θ_{b,pose}",
          "Altera λ_{0}, a transição, s_{0} e K_{40} (seções ⟦S:conv⟧ e ⟦S:r_s0⟧)",
          "Medir no CAD o ângulo do braço na pose, com o sentido positivo declarado"],
         ["Posição do eixo da articulação 20 no referencial do Fusion",
          "Braço do exoesqueleto fora de τ_{g} e de I_{O}",
          "Medir o centro do eixo no Fusion e confirmar que os eixos do Fusion são "
          "paralelos aos do modelo"],
         ["Forma do fator G: braço de momento ou torque do peso usado na Figura 16 da patente",
          "Modelo completo não reproduz a Figura 16 da patente com os s_{0} identificados "
          "(R^{2} negativo); distribuição angular do torque incerta",
          "Conferir a geometria do protótipo da patente e a definição da ordenada "
          "da Figura 16 da patente"],
         ["Rigidez K e escala da ordenada da Figura 16 da patente",
          "K só por hipótese (K_{40}); torque em N·m apenas como cenário",
          "Especificação ou ensaio de força e extensão do elemento elástico, ou "
          "documento com a escala da figura"],
         ["Lei do elástico e significado de s_{0}",
          "Identificação pelo espaçamento supõe elástico linear e mesmo K nas três "
          "curvas; ajuste de forma no limite s_{0} = 0 na curva contínua",
          "Curva de força e extensão do elástico; testar lei não linear ou "
          "força inicial"],
         ["Posição e raio de contato do elemento 78",
          "Torque não nulo abaixo da transição, contra razão nula na Figura 16 da patente",
          "Conferir no CAD; comparar com p_{78} = 0, preferido em [0099]"],
         ["Procedimento e incerteza da extração da Figura 16 da patente",
          "Incerteza da leitura estimada só pelo erro mediano declarado",
          "Registrar imagem, resolução e método da extração; repetir a leitura"],
         ["Digitalização da Figura 17 da patente",
          "Efeito de e comparado só visualmente",
          "Digitalizar a Figura 17 da patente e obter os valores de excentricidade"],
         ["Movimento fora do plano sagital",
          "Abdução e articulação esférica 22 não representadas",
          "Modelo espacial, fora do escopo deste trabalho"],
         ["Etapas dinâmicas e MBDyn",
          "Nenhum resultado dinâmico", "Resolver as pendências de K, I_{O} e "
          "Q_{nc} e instalar o MBDyn"]],
        [2800, 3080, 3480]))
    a(FONTE)

    # ------------------------------------------------------------ comparação
    a(SEC("4B", "r_comp", "Comparação com o exoesqueleto 1"))
    a(P("A Tabela ⟦T:comp⟧ compara os dois dispositivos com os números das seções "
        "4A e 4B. Os ângulos são comparáveis porque as duas convenções medem o braço "
        "a partir da posição pendente: a elevação anatômica da seção 3A.3 e a "
        "anteversão da seção ⟦S:conv⟧."))
    a(LEG_T("comp", "Comparação entre os dois dispositivos analisados"))
    a(TABELA(
        ["Aspecto", "US 9.889.554 B2 (seção 4A)", "EP 3 504 033 B1 (seção 4B)"],
        [["Arquitetura", "Mola, cabo e polia entre elo proximal e elo distal",
          "Elástico ligado diretamente da barra à alavanca, com elemento de apoio "
          "junto à articulação"],
         ["Faixa sem torque com o braço baixado",
          "Protuberância junto à junta, não modelada; ponto morto em 30,485° de "
          "elevação",
          f"Contato com o elemento 78; transição em {f(g['theta_t'], 2)}° de "
          "anteversão no CAD, com torque não nulo abaixo dela"],
         ["Dado da patente",
          "Uma curva de torque sem unidade na ordenada; 29 pontos extraídos",
          "Três curvas de razão de torques sem escala na ordenada, com pré-tensões "
          f"diferentes; {n_pts} pontos extraídos"],
         ["Parâmetros identificados",
          "θ_{off}, h, X_{pose} e K, este em unidade da patente",
          "s_{0} das três curvas, pelo espaçamento; K não identificável"],
         ["Reprodução da curva publicada", "R^{2} = 0,99839",
          "R^{2} negativo com os s_{0} identificados; de "
          f"{f(po['r2'], 3)} a {f(co['r2'], 3)} no ajuste de forma, com s_{{0}} "
          "livre por curva"],
         ["Escala do torque",
          "Unidade da patente; leitura em N·m implausível, com tração de 9,5 kN",
          f"N·m sob a hipótese K = K_{{40}}, com força de {f(pr['F_min'], 0)} a "
          f"{f(pr['F_max'], 0)} N"],
         ["Pico do torque de assistência", "97,48° de elevação",
          f"{f(pr['theta_pico'], 1)}° de anteversão, no cenário de projeto"],
         ["Torque gravitacional de referência",
          "Conjunto braço e exoesqueleto, pico de 11,1619 N·m",
          f"Só o membro humano, pico de {f(mas['tau_g_pico'])} N·m"]],
        [2300, 3530, 3530]))
    a(PEQUENO("Fonte: elaborada pelo autor, com os resultados das seções 4A e 4B.",
              True))
    a(P("O contraste mais útil para o procedimento está na identificação. Uma única "
        "curva sem unidade, como a da US 9.889.554 B2, fixa a forma do perfil, e o "
        "ajuste de quatro parâmetros contra os mesmos 29 pontos reproduz essa forma "
        "sem constituir validação independente (seção 4A.5). As três curvas da "
        "EP 3 504 033 B1 trazem uma redundância que permitiu separar o comprimento "
        "de referência do elástico, determinado pelo espaçamento entre elas, da "
        "forma do perfil, que depende do braço de momento e do torque do peso. Essa "
        "separação revelou uma diferença de forma que o ajuste de uma curva "
        "isolada teria escondido no valor de s_{0}."))
    a(P("Os dois mecanismos também distribuem a assistência de modo distinto em "
        "relação à demanda gravitacional. O gerador da US 9.889.554 B2 concentra o "
        "torque acima da horizontal e acompanha a forma do peso entre 105° e 150° "
        "de elevação (seção 4A.8). No cenário de projeto da EP 3 504 033 B1, a forma "
        f"do elástico acompanha a do peso de {f(cz_n[1], 0)}° a {f(cz_n[2], 0)}° e "
        "fica abaixo dela acima desse ângulo, com diferença normalizada de até "
        f"{f(t3['extremo'])} em {f(t3['theta'], 1)}° (seção ⟦S:r_conf⟧). Como a "
        "forma desse segundo perfil depende da geometria do CAD, que não reproduz a "
        "Figura 16 da patente, a comparação vale para os modelos, e não para os produtos."))
    return B


# ======================================================================
# capítulo 5 e referências
# ======================================================================

def cap5_titulo():
    return [H("5A EXOESQUELETO 1: US 9.889.554 B2")]


def parte_5B():
    B = []
    a = B.append
    s0p, s0t, s0c = (s0r[n] for n in ORDEM)
    rob_t = [x["s0"]["tracejada"] for x in rz["robustez"]]
    fr = rz["forma"]["G_sobre_modelo"]
    a(H("5B EXOESQUELETO 2: EP 3 504 033 B1"))
    a(P("Para a EP 3 504 033 B1, foram executadas a leitura da arquitetura na "
        "patente, a organização das grandezas do CAD com sua origem, a composição "
        "inercial do membro humano, as convenções angulares, a cinemática de dois "
        "regimes em forma fechada, o torque pelo produto vetorial, o torque "
        "gravitacional, o tratamento da Figura 16 da patente, a identificação de s_{0} pelo "
        "espaçamento entre as curvas e pelo ajuste de forma, a varredura de e e as "
        "verificações numéricas."))
    a(P("O espaçamento entre as três curvas da Figura 16 da patente determina os comprimentos "
        "de referência do elástico sem depender da escala da ordenada, da rigidez, "
        f"do braço de momento ou do torque do peso: {f(s0p, 2)} mm na curva "
        f"pontilhada, {f(s0t, 2)} mm na tracejada e {f(s0c, 2)} mm na contínua, com "
        f"variação de até {f(max(rob_t) - min(rob_t), 2)} mm entre as faixas de "
        f"ângulo testadas e desvio padrão de {f(rz['monte_carlo']['desvio']['tracejada'], 2)} "
        "mm com o ruído de extração. O fim da curva pontilhada, de pré-tensão quase "
        "nula, confirma o resultado de forma independente: a figura indica "
        f"elástico frouxo a partir de {f(rz['fim_pontilhada']['2']['theta'], 1)}°, e "
        f"o modelo, a partir de {f(rz['theta_frouxo']['pontilhada'], 1)}°. O início "
        "das curvas, perto de 14°, não informa s_{0}: decorre do contato do elástico "
        "com o elemento de apoio junto à articulação."))
    a(P("A forma do torque prevista com a geometria do CAD e o peso do membro "
        "humano não reproduz as curvas da patente: o fator comum às três curvas "
        f"difere do previsto por um fator que vai de {f(fr['20'], 2)} em 20° a "
        f"{f(fr['165'], 2)} em 165°, normalizado em 90°. O ajuste de forma, que deixa "
        "s_{0} e a escala livres por curva, compensa essa diferença com valores de "
        "s_{0} sem significado físico, como o limite s_{0} = 0 na curva contínua. A "
        "origem da diferença, no braço de momento ou no torque do peso usado pela "
        "patente para formar a razão, não pôde ser determinada."))
    a(P("A rigidez não é identificável pela figura. Sob a hipótese de assistência "
        f"de 40% do torque do peso em 90°, K = {f(pr['K'], 3)} N/mm, e o elástico "
        f"trabalha de {f(pr['F_0'], 1)} N com o braço pendente a "
        f"{f(pr['F_180'], 1)} N com o braço elevado, com deformação máxima de "
        f"{pct(pr['deformacao_max'], 1)} do comprimento de referência. O torque "
        f"atinge {f(pr['tau_pico'])} N·m em {f(pr['theta_pico'], 1)}°, dentro da "
        "faixa de 70° a 120° preferida pela patente, e a razão τ/τ_{g} cai de "
        f"{f(tab[10.0]['razao'], 2)} em 10° a {f(tab[170.0]['razao'], 2)} em 170°. "
        f"Abaixo da transição de regime, em {f(g['theta_t'], 2)}°, o modelo ainda "
        "entrega torque, porque o elemento de apoio do CAD está a "
        f"{f(par['P'])} mm do eixo."))
    a(P("Dos objetivos acrescentados para esse dispositivo, o item h foi cumprido "
        "na parte estática, com as ressalvas de escala e de conferência do CAD, e o "
        "item i foi cumprido pelo espaçamento entre as curvas. As etapas dinâmicas "
        "não foram executadas, pelas razões da seção ⟦S:din⟧."))
    a(P("Os dois dispositivos diferem tanto na arquitetura quanto no que suas "
        "patentes permitem identificar. O gerador da US 9.889.554 B2 reproduz a "
        "curva publicada com R^{2} de 0,99839, mas em unidade da patente; o "
        "dispositivo da EP 3 504 033 B1 tem s_{0} determinado de forma mais robusta, "
        "por dispor de três curvas, mas sua forma não é reproduzida pelo modelo do "
        "CAD, e o torque só chega a N·m por hipótese. Nos dois casos, o pico de "
        "assistência fica afastado do pico gravitacional, acima dele no primeiro "
        "(97,5° contra 89,4°) e abaixo no segundo "
        f"({f(pr['theta_pico'], 1)}° contra 90°), e a faixa sem torque com o braço "
        "baixado é produzida por meios distintos, uma protuberância no primeiro e o "
        "contato com o elemento de apoio no segundo."))
    a(P("Como continuidade para esse dispositivo, recomenda-se incluir o modelo em "
        "CAD no repositório e confirmar o sinal do ângulo do braço na pose e a "
        "posição do eixo da articulação no Fusion; esclarecer a definição da "
        "ordenada da Figura 16 da patente e a geometria do protótipo que a gerou; obter a curva "
        "de força e extensão do elemento elástico, que fixaria K; digitalizar a "
        "Figura 17 da patente; e, com a escala resolvida, executar as etapas dinâmicas pela "
        "formulação de Lagrange e no MBDyn."))
    return B


DOI_VIRTANEN = "https://doi.org/10.1038/s41592-019-0686-2"
RID_DOI = "rIdExo2Doi1"


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


# ======================================================================
# OMML pelo pandoc
# ======================================================================

FUNCAO = re.compile(r'<m:r><m:rPr><m:sty m:val="p" /></m:rPr>'
                    r'<m:t>(atan2|max|sin|cos)</m:t></m:r>(?=<m:d>)')


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


# ======================================================================
# montagem
# ======================================================================

def _unico(lista, prefixo):
    achados = [i for i, (_, t, _) in enumerate(lista) if t.startswith(prefixo)]
    assert len(achados) == 1, (prefixo, achados)
    return achados[0]


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
        b2 = editar(b, regras) if regras else b
        b2 = editar(b2, (REGRA_TITULO if titulo else []) + REGRAS_ORIGINAL)
        editados.append(b2)
    for antes, _ in EDICOES:
        assert sum(antes in t for _, t, _ in info) == 1, antes

    # pontos de inserção (índice do bloco original depois do qual entra o novo)
    depois = {
        _unico(info, "Este trabalho trata dessa lacuna"): cap1_introducao(),
        _unico(info, "g) acoplar o modelo ao MBDyn"): cap1_objetivos(),
        _unico(info, "A escolha de ferramentas livres"): cap1_justificativa(),
        _unico(info, "Em ambos os documentos, contudo"): cap2_compensacao(),
        _unico(info, "O ajuste, entretanto, encontra limite"): cap2_curva(),
        _unico(info, "O Airframe, da Levitate"): cap2_arquiteturas(),
        _unico(info, "Wu, Wang e Du (2016)"): cap2_balanceamento(),
        _unico(info, "O procedimento usual consiste no ajuste"): cap2_identificacao(),
        _unico(info, "A cadeia de cálculo descrita nas seções"):
            cap3_introducao() + [H("3A EXOESQUELETO 1: US 9.889.554 B2")],
        _unico(info, "4 RESULTADOS E DISCUSSÃO"): cap4_introducao(),
        _unico(info, "5 CONCLUSÃO"): cap5_titulo(),
        _unico(info, "BOUTERAA, Y.; BEN ABDALLAH"): [ref_brent()],
        _unico(info, "VAN ENGELHOVEN, L.; KAZEROONI"): [ref_virtanen()],
    }
    antes = {
        _unico(info, "4 RESULTADOS E DISCUSSÃO"): parte_3B(),
        _unico(info, "5 CONCLUSÃO"): parte_4B(),
        _unico(info, "REFERÊNCIAS"): parte_5B(),
    }
    final = []
    for i, b in enumerate(editados):
        final += [("n", x) for x in antes.get(i, [])]
        final.append(("o", b))
        final += [("n", x) for x in depois.get(i, [])]
    return orig, final


MARCA = re.compile(r"⟦([TFES])([#:])([^⟧]+)⟧")


def numerar(final, n_eq_original):
    """Resolve as marcas em ordem de aparição; devolve o XML e os mapas."""
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
    orig, final = montar(doc[b0:b1])

    # equações do original: números (1) a (n), antes de toda equação nova
    n_eq = len(re.findall(r"<w:t>\((\d+)\)</w:t>", doc[b0:b1]))
    assert n_eq == 27, n_eq
    ultimo_orig = max(i for i, (o, x) in enumerate(final)
                      if o == "o" and "<m:oMath" in x)
    primeiro_novo = min(i for i, (o, x) in enumerate(final) if "⟦E#" in x)
    assert ultimo_orig < primeiro_novo, "equação nova antes de uma original"
    final, num, sem_ref = numerar(final, n_eq)

    xml = "".join(x for _, x in final)
    for k, m in enumerate(omml(EQUACOES), start=1):
        xml = xml.replace(f"@@OMML{k}@@", m)
    assert "@@OMML" not in xml and "⟦" not in xml
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
    assert RID_DOI not in rels
    rels = rels.replace(
        "</Relationships>",
        f'<Relationship Id="{RID_DOI}" Type="http://schemas.openxmlformats.org/'
        f'officeDocument/2006/relationships/hyperlink" Target="{DOI_VIRTANEN}" '
        'TargetMode="External"/></Relationships>')
    partes["word/_rels/document.xml.rels"] = rels.encode("utf-8")

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
    relatorio(orig, final, num, sem_ref, destino)
    print(f"{destino}: {len(num['T'])} tabelas, {len(num['F'])} figuras, "
          f"{n_eq + len(EQUACOES)} equações ({len(EQUACOES)} novas), "
          f"{len(SECOES)} seções novas")
    if sem_ref:
        print("sem referência no texto:", sem_ref)


def relatorio(orig, final, num, sem_ref, destino):
    """tcc/relatorio_fusao.md: parágrafos originais alterados, antes e depois."""
    finais_o = [x for o, x in final if o == "o"]
    assert len(finais_o) == len(orig)
    mudados = [(texto(a), texto(b)) for a, b in zip(orig, finais_o)
               if texto(a) != texto(b)]

    def mapa(tipo):
        return ", ".join(f"{k[1:]} → {v}" for k, v in
                         sorted(num[tipo].items(), key=lambda kv: kv[1])
                         if k.startswith("o"))
    linhas = ["# Relatório da fusão dos exoesqueletos 1 e 2", "",
              f"Documento gerado: `{destino.name}`, a partir de `TCC_apenas_exo1.docx`.",
              "", f"Blocos do original: {len(orig)}, todos mantidos e na mesma ordem. "
              f"Blocos novos: {sum(o == 'n' for o, _ in final)}. Blocos do original "
              f"com texto alterado: {len(mudados)} (renumeração e as edições de "
              "EDICOES em gerar_tcc_fundido.py).", "",
              "## Numeração", "",
              f"Tabelas do original (antes → depois): {mapa('T')}.", "",
              f"Figuras do original (antes → depois): {mapa('F')}.", "",
              "As equações do original mantêm os números (1) a (27).", "",
              "## Blocos do original com texto alterado", ""]
    for n, (ta, tb) in enumerate(mudados, start=1):
        linhas += [f"### {n}", "", f"Antes: {ta}", "", f"Depois: {tb}", ""]
    if sem_ref:
        linhas += ["## Elementos sem referência no texto", "",
                   ", ".join(f"{t} {c}" for t, c in sem_ref), ""]
    (destino.parent/"relatorio_fusao.md").write_text("\n".join(linhas), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
