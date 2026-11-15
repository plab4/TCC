"""
Plano da versão para a defesa, montada por
tcc/gerar_condensado.py a partir do documento longo revisado.

Decisões do autor que o plano segue:
- até 82 páginas, da capa ao fim (80, mais as 2 que o autor aceitou para o exoesqueleto 3 ficar parelho);
  depois, a pedido do autor, voltaram todas as figuras dos três exoesqueletos (86 páginas);
- base: o DOCX do autor de 14/11/2026, com as quatro alterações dele (data da defesa, frase do
  capítulo 2, parágrafo do CAD do exoesqueleto 1 e parágrafo do apoio do exoesqueleto 3 em 3.2);
- base: o arquivo do autor de 13/11/2026, que é o documento longo sem a seção 2.6, as
  seções 3.x.12 e 3.x.13, as comparações 3.4 e 4.4, as verificações 4.2.3 e 4.3.3, o
  apêndice e alguns parágrafos (aberturas das seções, trechos dos capítulos 2, 4 e 5);
- metodologia fundida por tópico: cada seção do capítulo 3 é uma etapa do procedimento,
  com os três exoesqueletos em sequência; o capítulo 4 também é fundido por assunto (pedido de
  14/11), com uma abertura só e cada exoesqueleto aberto por "No exoesqueleto n"; o capítulo 5
  também é fundido por assunto (pedido de 15/11);
- as seções 4.x.6 a 4.x.9 (comportamento, varredura, confronto e limitações) ficam;
- arquivo do autor de 15/11/2026: M.d² no exoesqueleto 1, "Calculada" no lugar de "Derivada"
  nas tabelas de geometria e tabelas de parâmetros sem a coluna Situação;
- 3.4 e 3.5 fundidas (fechamento do circuito e braço de momento), com cada exoesqueleto completo
  antes do seguinte; saem trechos que repetem o que já está dito em outra seção (pedido de 14/11),
  mas ficam as conclusões, as remissões de método e as ressalvas que só aparecem num lugar;
- saem as tabelas longas de pontos extraídos (Tabelas 5 e 15 do documento longo) e as que
  repetem números do texto ou de outra tabela;
- no DOCX, cada figura entra depois do parágrafo que a antecede no fluxo da página, para não
  deixar meia página em branco (o LaTeX posiciona as figuras sozinho);
- sai tudo o que menciona a etapa dinâmica e o MBDyn.

Entradas do PLANO (os índices são os do documento longo, como em
`python3 tcc/gerar_condensado.py --dump arquivo.txt`):

    ("K", a) ou ("K", a, b)   mantém o bloco a, ou os blocos de a até b
    ("E", i, [(antes, depois), ...])
                              mantém o bloco i com trechos trocados; o trecho
                              novo é texto simples, sem subscrito nem itálico
    ("R", i, texto)           mantém o parágrafo i (legenda, nota) com outro texto
    ("L", i, [linhas])        mantém a tabela i só com as linhas indicadas
                              (1 = primeira linha depois do cabeçalho)
    ("P", texto)              parágrafo novo, na marcação do gerador
    ("H", pai, chave, titulo) título novo, dentro da seção de chave `pai`

Nos textos novos, tabelas, figuras e equações são citadas pelo número que têm no
documento longo (Tabela 13, Figura 12, Equação (45)); o montador troca esses
números pelos da versão condensada. Seções são citadas por chave, ⟦S:chave⟧: a
chave de um título mantido é o número que ele tem no documento longo, e a de um
título novo é a declarada em "H". ALIAS diz em que seção nova foi parar o conteúdo
de cada seção antiga, para as remissões dos blocos mantidos.

Regras de redação: sem travessões; nenhum número que não esteja no documento
longo (conferido por tcc/verificar_condensado.py); patente sempre qualificada
quando se cita uma figura dela.
"""

# seções do documento longo → seção da versão condensada (None: saiu). O capítulo 3 é fundido
# por tópico: a subseção 3.e.k do exoesqueleto e vai para o tópico k.
TOPICO = {1: "t_cad", 2: "t_iner", 3: "t_conv", 4: "t_fech", 5: "t_fech", 6: "t_mola", 7: "t_morto",
          8: "t_grav", 9: "t_ptv", 10: "t_ident", 11: "t_varr", 12: "t_verif", 13: None, 14: "t_verif"}
ALIAS = {"2.6": None, "3.4": None, "4.4": None}
for _e in "123":
    ALIAS.update({f"3.{_e}.{_k}": _t for _k, _t in TOPICO.items()})

# títulos dos tópicos do capítulo 3
TOPICOS = [
    ("t_cad", "Reconstrução geométrica em CAD"),
    ("t_iner", "Parâmetros inerciais e transporte ao eixo"),
    ("t_conv", "Referenciais e convenções angulares e de sinal"),
    ("t_fech", "Fechamento do circuito vetorial e braço de momento"),
    ("t_braco", "Ponto de aplicação da força e braço de momento"),
    ("t_mola", "Caminho do elemento elástico, lei da mola e torque"),
    ("t_morto", "Ponto morto e faixa sem torque"),
    ("t_grav", "Torque gravitacional"),
    ("t_ptv", "Formulação pelo princípio dos trabalhos virtuais"),
    ("t_ident", "Dados da patente e identificação dos parâmetros"),
    ("t_varr", "Varredura paramétrica"),
    ("t_verif", "Verificações, ferramentas e delimitação"),
]
_T = dict(TOPICOS)


def H(chave):
    return ("H", "3", chave, _T[chave])



def ABRE(i, antes, exo):
    """Mantém o bloco i e abre o parágrafo com 'No exoesqueleto n, ...'."""
    return ("E", i, [(antes, f"No exoesqueleto {exo}, " + antes[0].lower() + antes[1:])])


# números do complemento do exoesqueleto 3 (reprodução da Figura 16 pelos marcadores e
# confronto nos marcadores), escritos por tcc_resultados_exo3_marcadores.py como aparecem no texto;
# o verificador aceita os números desse arquivo, além dos do documento longo
import json as _json
from pathlib import Path as _Path
COMPLEMENTO_EXO3 = _Path(__file__).resolve().parent.parent / "results" / "exo3_marcadores.json"
M3 = _json.loads(COMPLEMENTO_EXO3.read_text(encoding="utf-8"))["texto"]
FIGURAS_NOVAS = ["exo3_tcc_fig_7_marcadores.png", "exo3_tcc_fig_8_confronto.png", "exo3_tcc_fig_9_razao.png"]

# título do trabalho na versão para a defesa: só "Modelagem", por decisão do autor, porque o
# texto ficou só com a parte estática
TITULO_LONGO = "Modelagem e simulação de mecanismos passivos de apoio ao braço"
TITULO = "Modelagem de mecanismos passivos de apoio ao braço"
# subtítulo e título e subtítulo em língua estrangeira (pedido de 15/11): o subtítulo vem depois
# de dois-pontos, na capa e na folha de rosto; a versão em inglês fica na folha de rosto
SUBTITULO = "torque estático de três exoesqueletos reconstruídos a partir de patentes"
TITULO_EN = "Modeling of passive arm-support mechanisms"
SUBTITULO_EN = "static torque of three exoskeletons reconstructed from patents"
TITULO_COMPLETO = f"{TITULO}: {SUBTITULO}"
TITULO_COMPLETO_EN = f"{TITULO_EN}: {SUBTITULO_EN}"
DATA_DEFESA = ("26", "11", "2026")   # dia, mês e ano, como no DOCX do autor de 14/11/2026

# ====================================================================== capítulo 1
CAP1 = [
    ("E", 0, [(TITULO_LONGO, TITULO)]),
    ("K", 1),
    ("E", 2, [("Vários setores como: Montagem automotiva, construção civil, solda e manutenção industrial exigem",
               "Vários setores, como montagem automotiva, construção civil, solda e manutenção industrial, exigem"),
              ("distúrbios na articulação ombro", "distúrbios na articulação do ombro")]),
    ("E", 3, [("4,12 milhões afastamentos", "4,12 milhões de afastamentos")]),
    ("K", 4),
    ("E", 5, [("Em um dispositivo passivo o auxílio", "Em um dispositivo passivo, o auxílio")]),
    ("E", 6, [("resolver o problema em duas etapas, o equilíbrio estático, que dimensiona a compensação de "
               "gravidade, e a dinâmica multicorpos, que expõe inércia, forças de Coriolis e atrito durante o "
               "movimento real.",
               "resolver o equilíbrio estático, que dimensiona a compensação de gravidade.")]),
    ("E", 7, [(", com parâmetros antropométricos de referência, e preparar a extensão do modelo à dinâmica "
               "multicorpos pela formulação de Lagrange.",
               ", com parâmetros antropométricos de referência.")]),
    ("E", 8, [("Nesta etapa, o procedimento foi aplicado", "O procedimento foi aplicado"),
              (" Os três são tratados em seções separadas dos capítulos 3, 4 e 5, dedicadas aos "
               "exoesqueletos 1, 2 e 3.", " No restante do texto, eles são chamados de exoesqueletos 1, 2 e 3."),
              (" e o anula quando situado sobre o eixo de rotação", "")]),
    ("K", 9, 10),
    ("E", 11, [("da US 9.737.374 B2, comparar o torque", "da US 9.737.374 B2, e comparar o torque"),
               ("braço–exoesqueleto", "braço-exoesqueleto"),
               (" ao longo da faixa de elevação e preparar a extensão do procedimento à dinâmica multicorpos.",
                " ao longo da faixa de elevação.")]),
    ("K", 12, 15),
    ("E", 16, [("que a patente não informa — posição", "que a patente não informa: posição")]),
    ("E", 17, [("braço–exoesqueleto", "braço-exoesqueleto"),
               ("ao longo da faixa de elevação;", "ao longo da faixa de elevação.")]),
    # objetivos f e g (equação de movimento e MBDyn) saem; os seguintes mudam de letra
    ("E", 21, [("h) aplicar a esse dispositivo", "f) aplicar ao dispositivo da EP 3 504 033 B1")]),
    ("E", 22, [("i) identificar", "g) identificar")]),
    ("E", 24, [("j) reconstruir o circuito do cabo de ancoragem e o perfil do came de raio variável",
                "h) reconstruir o circuito do cabo de ancoragem e o perfil do came de raio variável da "
                "US 9.737.374 B2")]),
    ("E", 25, [("k) obter", "i) obter")]),
    ("K", 26),
    ("E", 27, [("base quantitativa — algo que as patentes, por si, não oferecem.",
                "base quantitativa, algo que as patentes, por si, não oferecem. A implementação em Python, "
                "ferramenta livre, torna o modelo reprodutível por outros grupos.")]),
]

# ====================================================================== capítulo 2
# cortes do autor: a última frase do primeiro parágrafo de 2.4 (Palazzi), os parágrafos 48 (Nasr) e
# 49 (preferências da EP), a seção 2.6 e o parágrafo 73 (curvas da EP em 2.10)
CAP2 = [
    ('K', 30, 32),
    ("E", 33, [('linha dos ombros — faixa angular',
                'linha dos ombros, faixa angular'),
               ('A evidência epidemiológica disponível indica relação dose-dependente entre a exposição '
                'postural e o desfecho clínico. ', '')]),
    ("E", 34, [('braço–antebraço',
                'braço-antebraço')]),
    ('K', 35, 37),
    ("E", 38, [('projeto do mecanismo — circunstância',
                'projeto do mecanismo, circunstância')]),
    ('K', 39, 45),
    ("E", 46, [('Palazzi et al. (2022) mostram, em um exoesqueleto balanceado por gravidade, '
                'redução de 89% no torque de pico do ombro quando esse ajuste é bem resolvido.',
                '')]),
    ('K', 47),
    ('K', 50, 53),
    ('K', 58),
    ("E", 59, [('mola–cabo–polia',
                'mola-cabo-polia')]),
    ('K', 60, 67),
    ("E", 68, [('O cálculo do torque gravitacional e das equações de movimento pressupõe',
                'O cálculo do torque gravitacional e a composição inercial do conjunto pressupõem')]),
    ("E", 69, [(' Cabe distinguir, nesse ponto, as duas grandezas que o procedimento alimenta: o momento '
                'estático do peso, dependente apenas da massa e do braço horizontal do centro de gravidade, e o '
                'momento de inércia, que descreve a resistência à aceleração angular e comparece exclusivamente '
                'na análise dinâmica.', '')]),
    ('K', 70, 71),
    ("E", 72, [('quanto à origem — medida, de literatura, identificada, derivada ou assumida — de '
                'modo que',
                'quanto à origem (medida, de literatura, identificada, derivada ou assumida), de '
                'modo que')]),
    ('K', 74),
    ("E", 75, [('construída a partir da documentação pública de patente e conduzida do equilíbrio '
                'estático até a dinâmica multicorpos.',
                'construída a partir da documentação pública de patente.')]),
]

# ====================================================================== capítulo 3, fundido por tópico
# cada seção é uma etapa do procedimento, com os exoesqueletos 1, 2 e 3 nessa ordem
CAP3 = [
    ('K', 76),
    ("E", 77, [('Ele foi aplicado, na parte estática, a três mecanismos: o gerador de torque da '
                'US 9.889.554 B2 (seções 3.1, 4.1 e 5.1), o dispositivo da EP 3 504 033 B1 '
                '(seções 3.2, 4.2 e 5.2) e o mecanismo de came da US 9.737.374 B2 (seções 3.3, '
                '4.3 e 5.3). As seções 3.1.9, 3.2.9 e 3.3.9 formulam os três modelos estáticos '
                'pelo princípio dos trabalhos virtuais, e as seções 3.4, 4.4 e 5.4 comparam os '
                'três.',
                'Este capítulo segue as etapas do procedimento, e cada seção trata dos '
                'exoesqueletos 1, 2 e 3, nessa ordem; o capítulo 4 apresenta os resultados na '
                'mesma organização, e o capítulo 5 reúne as conclusões, com a comparação entre os três.')]),
    ("E", 79, [('As seções 3.1, 3.2 e 3.3 seguem a mesma ordem, e as subseções de mesmo número '
                'tratam da mesma etapa; quando uma etapa não se aplica a um mecanismo ou não pôde '
                'ser concluída com os dados disponíveis, a própria subseção registra o motivo. '
                'Cada seção tem notação própria, e um mesmo símbolo pode ter significados '
                'diferentes em seções diferentes.',
                'Cada mecanismo tem notação própria, definida no trecho que trata dele em cada '
                'seção: um mesmo símbolo, como R, C, φ, β ou s, pode ter significados diferentes '
                'de um mecanismo para outro.')]),
    ("E", 81, [(', e o momento de inércia de cada corpo é levado ao eixo de rotação pelo teorema '
                'de Steiner, IO = Icm + M d2',
                '')]),
    H("t_cad"),
    ("P", 'No exoesqueleto 1, a geometria do gerador de torque da US 9.889.554 B2 foi '
          'reconstruída no Autodesk Fusion sobre os desenhos da patente, em especial a vista em '
          'corte do gerador de torque, e escalada a partir de uma estimativa de medida '
          'antropométrica. Da reconstrução saem as constantes geométricas, a pose de referência, e '
          'a massa, o centro de massa e o momento de inércia de cada peça (seção ⟦S:4.1.1⟧). Por '
          'dependerem do fator de escala, da interpretação de desenhos não cotados e do material '
          'atribuído a cada peça, essas grandezas são classificadas como “medidas em CAD”, e não '
          'como dimensões ou propriedades do dispositivo comercial.'),
    ("P", 'No exoesqueleto 2, a EP 3 504 033 B1 (MIZERA et al., 2023), da Ottobock, descreve um '
          'dispositivo em que o elemento de apoio do braço, formado por um elemento distanciador '
          '(8) e uma concha, liga-se por uma articulação (20) à extremidade superior de um '
          'elemento de transmissão de força (18), uma barra cuja extremidade inferior se apoia '
          'num cinto pélvico. O atuador passivo, uma mola de tração na Figura 1 da patente e um '
          'cabo ou fio elástico na Figura 18 da patente, tem uma extremidade presa à barra 18, e '
          'a outra atua sobre um elemento de alavanca do elemento distanciador 8, de modo que a '
          'força é aplicada excentricamente em relação ao eixo da articulação 20.'),
    ("P", 'O elemento 78, chamado na patente de Anlageelement e aqui de elemento de encosto, fica '
          'junto à articulação 20 e encosta no elemento elástico a partir de um ângulo '
          'predeterminado entre o elemento de apoio do braço e a barra (Figura 22 da patente). A '
          'patente prefere o elemento 78 sobre o eixo da articulação 20. O circuito foi fechado no modelo em CAD, '
          'cujas grandezas estão na Tabela 13 (seção ⟦S:4.2.1⟧). O critério de escala do modelo não foi '
          'registrado, e a planilha de composição inercial identifica o modelo como Ottobock iX Shoulder Air; '
          'como a patente não nomeia o produto, a correspondência entre esse produto, o modelo em CAD e os '
          'desenhos da patente não está documentada.'),
    ("P", 'No exoesqueleto 3, nas Figuras 14C e 14D da US 9.737.374 B2 (DOYLE, 2017), da '
          'Levitate, o chassi 580 do apoio de braço gira em torno do pivô horizontal do ombro, '
          '584. O cabo de ancoragem 560 sai do ponto 562, preso ao suporte do tronco, enrola-se '
          'na polia primária 564 e prende-se a ela. A polia secundária 570 é solidária à '
          'primária, e as duas giram em torno do pino 572, no chassi. O cabo da mola 634 '
          'prende-se à secundária no ponto 573, passa pela polia de reversão 630, no pino 632, e '
          'chega à mola 636, cuja outra ponta fica presa ao chassi. Ao baixar o braço, o cabo 560 '
          'desenrola-se da primária, o par de polias gira, e o cabo 634 enrola-se na secundária, '
          'estendendo a mola.'),
    ("P", 'A secundária 570 é o came. A patente divide o canal em três zonas: na Z10, o raio é '
          'constante; na Z11, ele diminui continuamente; e na Z12, o canal forma um trecho reto '
          '(DOYLE, 2017). A Figura 16 da US 9.737.374 B2 traz o momento do dispositivo (AASM), o '
          'do peso do braço (AWM) e o resultante (RM) em função do ângulo Θ do eixo maior do '
          'apoio de braço com a horizontal, positivo acima dela, sem unidade na ordenada. O '
          'documento não traz cotas do mecanismo nem a rigidez e o comprimento livre da mola: os '
          'desenhos das Figuras 14C, 14D, 15A e 15B são a única fonte geométrica da patente.'),
    ("P", 'O modelo é plano e representa só a rotação do apoio de braço em torno do eixo do pivô '
          '584. O circuito do mecanismo foi fechado no modelo em CAD deste trabalho, cuja pose é '
          'a da Figura 14D, e as grandezas medidas nesse modelo estão na Tabela 21 (seção '
          '⟦S:4.3.1⟧).'),
    H("t_iner"),
    ("P", 'Nos três modelos, o momento de inércia de cada corpo, do membro de referência e das '
          'peças do exoesqueleto, foi transportado ao eixo de rotação do braço pelo teorema de '
          'Steiner:'),
    ('K', 90),
    ("E", 91, [('em relação ao eixo da junta,',
                'em relação ao eixo de rotação,'),
               (' A composição foi feita em planilha, construída para recalcular o conjunto quando qualquer '
                'entrada muda.', ''),
               ('; ele se destina à etapa dinâmica prevista na seção 3.1.13.',
                '.')]),
    ("E", 202, [('O membro humano é o de referência (seção 3), em série a partir de O.',
                'No exoesqueleto 2, o membro humano é o de referência (seção 3), em série a '
                'partir de O.')]),
    ("E", 303, [('O membro superior é o de referência (seção 3), alinhado ao eixo maior',
                'No exoesqueleto 3, o membro superior é o de referência (seção 3), alinhado ao '
                'eixo maior')]),
    H("t_conv"),
    ('K', 80),
    ("E", 93, [('O mecanismo é tratado como plano, com origem O no eixo da junta (pivô). Seis '
                'ângulos aparecem no cálculo e são mantidos separados, por serem fonte recorrente '
                'de erro (Tabela 1).',
                'No exoesqueleto 1, a origem O fica no eixo da junta (pivô).')]),
    ('K', 94),
    ("E", 95, [("curva publicada na patente, medido", "curva da patente, medido")]),
    ('K', 96, 98),
    ("E", 204, [('A origem O fica no eixo da articulação 20',
                'No exoesqueleto 2, a origem O fica no eixo da articulação 20')]),
    ('K', 205),
    ("R", 206, 'O modelo admite que o giro do elemento de apoio do braço em relação à barra 18 '
               'seja igual à anteversão, o que supõe o eixo da articulação 20 no centro do ombro '
               'e a barra 18 fixa em relação ao tronco. A patente não garante essa condição, e as '
               'comparações angulares com as Figuras 16 e 17 da patente dependem dessa hipótese.'),
    ('K', 207, 209),
    ("E", 210, [(", e as comparações usam seu módulo τg", "")]),
    ("R", 211, 'O ângulo θ_{b,pose} = 7,962° é positivo, como conferido no CAD: na pose, o braço '
               'fica acima da horizontal. Com o sinal oposto, o contato do elástico com o '
               'elemento 78 passaria de 24,55° para 8,62°, e o espaçamento entre as curvas da '
               'Figura 16 da patente fecharia com resíduo de 0,406 mm, contra 0,194 mm com o '
               'sinal adotado (seção 4.2.4).'),
    ("E", 308, [('A origem O fica no eixo do pivô 584',
                'No exoesqueleto 3, a origem O fica no eixo do pivô 584')]),
    ('K', 309, 310),
    ('K', 311),
    ("E", 312, [(", e as comparações usam seu módulo τg", ""),
                (" O torque τ é o produto da força da mola pela transmissão τ/Fs.", "")]),
    H("t_fech"),
    ("E", 103, [('A cinemática do gerador de torque é descrita',
                'No exoesqueleto 1, a cinemática do gerador de torque é descrita'),
               (' (Figura 1)', '')]),
    ('K', 104, 110),
    ("P", 'A grandeza ρ é a distância da ancoragem ao centro do tambor, e a tangente existe '
          'somente se ρ > R, condição verificada em cada ponto calculado.'),
    # a Figura 1 do documento longo (circuito do modelo) saiu a pedido do autor (14/11): o mesmo
    # circuito está na sobreposição à Figura 42 da US, cuja nota passa a dizer o que cada ponto é
    ("E", 118, [("na mesma pose,", "na pose de referência,")]),
    ('K', 124),
    ('K', 125, 127),
    ("E", 119, [(", na pose de referência (θ* = 115,017°, h = HCAD = 34,785 mm)", "")]),
    ('K', 120, 121),
    ("R", 122, 'Nota: desenho da patente em cinza. O é o pivô, A a ancoragem do cabo, D o centro do '
               'tambor e T o ponto de tangência; as componentes h e p de B estão tracejadas. O '
               'desenho foi alinhado pelo pivô 151 (O) e pelo centro do tambor 183 (D), que por isso '
               'coincidem por construção; a posição de A no 176 é o que a sobreposição testa. Com h '
               '= H_{CAL} = 22,701 mm, valor adotado no modelo, A fica 12,084 mm abaixo, sobre a '
               'perna h. O painel da direita amplia a região do pivô, onde se distinguem o vetor B '
               'e o braço m.'),
    ("E", 128, [(" A distância b, entretanto, não é o braço de momento do cabo: como T pertence a uma "
                 "circunferência de raio R centrada a C do pivô, b fica necessariamente entre C − R e C + R. O braço",
                 " O braço")]),
    ('K', 129, 130),
    ("E", 213, [('A ancoragem A do elástico fica na barra 18',
                'No exoesqueleto 2, a ancoragem A do elástico fica na barra 18'),
               (" (seção 3.2.5)", ""),
               (" (Figura 3)", "")]),
    ('K', 214, 222),
    ('K', 231),
    ("E", 232, [(" (regime I, θel = 96,5°)", ""), (" (regime II, θel = −2,2°)", "")]),
    ('K', 233, 234),
    ("R", 235, 'Nota: desenho da patente em cinza, girado para a orientação de leitura. Regime I, com '
               'o braço elevado: circuito fechado C_{1}, C_{2}, ‹e› e s. Regime II, com o braço '
               'baixado: circuito fechado C_{1}, C_{2}, p e s − x, e triângulo ‹e›, p e x; o '
               'elemento 78, na ponta de p, só entra depois do contato. As linhas pontilhadas indicam '
               'o eixo do braço. À direita, ampliação da região do pivô. Em cada pose, O e A coincidem '
               'por construção, porque o desenho foi alinhado por esses dois pontos; só P e o elemento '
               '78 testam o modelo. O P do modelo fica a 1,8 mm do pino do elástico desenhado com o '
               'braço elevado e a 4,7 mm com o braço baixado; com o braço baixado, o centro do '
               'elemento 78 do CAD fica a 22,7 mm do ponto em que o elástico desenhado se dobra.'),
    ("E", 224, [('O contato não é imposto por um ângulo.',
                'O contato do elástico com o elemento 78 não é imposto por um ângulo.')]),
    # a Figura 3 do documento longo (circuitos do modelo) saiu a pedido do autor (14/11): os dois
    # regimes estão na sobreposição à Figura 22 da EP, cuja nota passa a descrevê-los
    ('K', 225, 226),
    ("E", 314, [('O cabo 560 fecha um circuito vetorial',
                'No exoesqueleto 3, o cabo 560 fecha um circuito vetorial')]),
    ('K', 315),
    ("E", 316, [(" (seção 3.3.5)", "")]),
    ('K', 317, 321),
    ('K', 323),
    ('K', 324, 327),
    H("t_mola"),
    ("E", 132, [('A mola é tracionada pelo cabo',
                'No exoesqueleto 1, a mola é tracionada pelo cabo')]),
    ('K', 133, 135),
    ("P", 'O sinal do termo do arco foi fixado pelo princípio dos trabalhos virtuais (seção '
          '⟦S:t_ptv⟧): em um mecanismo conservativo, o trabalho da tração no cabo iguala o do '
          'torque no elo, o que exige'),
    ('K', 137),
    ("P", 'com q em radianos. A extensão da mola é referida a um comprimento, e não a um ângulo. '
          'Sendo X_{pose} a extensão elástica da mola na pose de referência, θ*_{pose} = '
          '115,017°, o valor do caminho em que a mola atinge o comprimento livre e a lei da mola '
          'são'),
    ('K', 140),
    ("P", 'em que δ é a extensão elástica, F a tração no cabo e K a rigidez da mola; a extensão é '
          'limitada a valores não negativos porque o cabo traciona, mas não empurra. O '
          'comprimento livre da mola só entra no modelo pela diferença X_{pose} = L_{pose} − '
          'L_{livre}. A força do cabo atua sobre o tambor no ponto T, com direção oposta a u(φ), '
          'e o torque em relação ao pivô é o produto vetorial plano'),
    ('K', 143),
    ("P", 'Como K é identificado contra a curva publicada, cuja ordenada não tem unidade '
          'declarada, o torque do cabo é expresso na unidade da própria curva, denotada u.p. '
          '(unidade da patente); K só estaria em N/mm se u.p. correspondesse a N·m, o que não '
          'pode ser afirmado com os dados disponíveis (seção ⟦S:4.1.6⟧).'),
    ("E", 237, [('O elástico é tratado como linear',
                'No exoesqueleto 2, o elástico é tratado como linear')]),
    ('K', 238, 242),
    ("E", 329, [('A força da mola chega ao cabo 560 pelo par de polias.',
                'No exoesqueleto 3, a força da mola chega ao cabo 560 pelo par de polias.')]),
    ("E", 330, [(" Na imagem da folha 22, essa área foi isolada pelos vãos brancos da hachura e completada "
                 "pelos fragmentos junto ao contorno e pelos entalhes das cotas.", ""),
                (" As zonas, localizadas pelas linhas de chamada das cotas, vão de 89,6° a 140,4° (Z10), de 152,4° a "
                 "218,8° (Z11) e de 242,6° a 292,6° (Z12), no referencial da Figura 15B.", "")]),
    ('K', 331, 332),
    ("R", 336, 'Por simplificação, a polia de reversão 630 fica fora da varredura: o cabo 634 é '
               'tomado na direção de 572 para 632, medida na Figura 14D, como se a polia '
               'estivesse no infinito; numa geometria de teste, essa simplificação muda r em até '
               '0,031 R_{20}. A mola, cuja rigidez e cujo comprimento livre a patente não '
               'informa, entra como mola linear, e o torque fica'),
    ('K', 337),
    ("E", 338, [(" O resultado da varredura é o torque por unidade de força da mola, τ/Fs = (r/R) C1 sin(γ − θ), "
                 "em N·mm por N.", "")]),
    ("E", 333, [(" e raio efetivo r e raio no ponto de saída ρ em função da direção do cabo (b)",
                 " e raios efetivo e no ponto de saída em função da direção do cabo (b)")]),
    ('K', 334, 335),
    H("t_morto"),
    ("E", 146, [('O torque do cabo se anula quando',
                'No exoesqueleto 1, o torque do cabo se anula quando')]),
    ('K', 147, 149),
    ("E", 150, [("Para h > 0, o termo atan2(p, h) fica entre 0° e 90°, de modo que a inversão só é válida "
                 "quando o argumento da tangente pertence a esse intervalo; fora dele, a Equação (24) devolve "
                 "um ramo espúrio, identificado pela substituição do resultado na Equação (23).",
                 "Fora do intervalo de 0° a 90° de atan2(p, h), a Equação (24) devolve um ramo espúrio, "
                 "identificado pela substituição do resultado na Equação (23).")]),
    ("E", 244, [('Pela Equação',
                'No exoesqueleto 2, pela Equação')]),
    ('K', 245, 246),
    ("E", 340, [('O braço de momento',
                'No exoesqueleto 3, o braço de momento')]),
    ('K', 341, 342),
    H("t_grav"),
    ("P", 'O torque do peso de cada conjunto é calculado de forma independente do mecanismo, em '
          'N·m, unidade física, e as comparações usam o seu módulo, τ_{g}.'),
    ("E", 152, [('O torque estático do peso do conjunto braço-exoesqueleto',
                'No exoesqueleto 1, o torque estático do peso do conjunto braço-exoesqueleto')]),
    ('K', 153),
    ("E", 154, [(" O torque gravitacional resulta em N·m, unidade física, ao contrário do torque do cabo.", "")]),
    ("E", 248, [('O conjunto que gira com o braço tem o centro de massa',
                'No exoesqueleto 2, o conjunto que gira com o braço tem o centro de massa')]),
    ('K', 249, 250),
    ("E", 344, [('O conjunto que gira com o braço reúne',
                'No exoesqueleto 3, o conjunto que gira com o braço reúne'),
               (' (seção 3.3.2)',
                '')]),
    ('K', 345),
    ("E", 346, [(" A mola entra com o centro de massa do CAD, embora o comprimento dela no CAD não corresponda à "
                 "pose: ao longo do curso, o centro se desloca metade do alongamento, o que muda o torque em no "
                 "máximo 0,05 N·m, e cada 10 mm de erro na posição dele ao longo do eixo da mola mudam o torque em "
                 "no máximo 0,01 N·m.", "")]),
    H("t_ptv"),
    ("P", 'Nos três mecanismos, o equilíbrio estático é escrito pelo princípio dos trabalhos '
          'virtuais. Com vínculos ideais, as reações não realizam trabalho, e, num giro virtual '
          'δq do conjunto em torno de O, realizam trabalho só a força do elemento elástico, o '
          'peso do conjunto e o torque τ_{u} que o usuário aplica ao braço. O trabalho da força '
          'elástica pode ser calculado pelo momento dela em relação a O ou pela variação do '
          'comprimento do caminho do elemento elástico; a igualdade dos dois dá o braço de '
          'momento como a derivada desse comprimento em relação a q, relação que depende só da '
          'geometria e serve de verificação da cinemática.'),
    ("P", 'No exoesqueleto 1, o giro virtual δq é igual a δθ* pela Equação (2), e a força do '
          'cabo, f = −F u(φ), atua no ponto de tangência T, que é o vetor b das Equações (13) a '
          '(15), de módulo b e a um ângulo β da linha do elo. Como o elo é rígido e gira em torno '
          'de O, o trabalho virtual dessa força é o do seu momento em relação a O, a componente z '
          'de b × f:'),
    ('K', 158),
    ("E", 159, [("O seno vem do ângulo entre os dois vetores: pela Equação (15), b aponta na direção q + π − β, e "
                 "f, na direção φ + π. O produto vetorial retém só a componente de f perpendicular a b, que é a que "
                 "gira o elo. Na faixa de operação, b vai de 282,503 a 284,363 mm e β de 4,604° a 4,619°, mas f "
                 "aponta quase para o pivô: φ + β − q difere de 180° em no máximo 4,623°. Por isso, −b",
                 "O produto vetorial retém só a componente de f perpendicular a b, que é a que gira o elo, e, na "
                 "faixa de operação, f aponta quase para o pivô: φ + β − q difere de 180° em no máximo 4,623°. "
                 "Por isso, −b")]),
    ('K', 160, 162),
    ("E", 163, [(' (seção 3.1.13)',
                ''),
               ('e a seção 4.1 compara apenas', 'e a seção 4.1.8 compara apenas'),
               (' Com aceleração nula e Qnc = τu, a Equação (31) reduz-se a essa condição.',
                '')]),
    ("E", 252, [('O equilíbrio é escrito pelo trabalho virtual num giro δq do conjunto, em radianos, igual a',
                 'No exoesqueleto 2, o giro δq é igual a'),
                ('Com o elemento 78 pontual e sem atrito e o elástico sem massa, o contato é um vínculo ideal, e '
                 'realizam trabalho a força do elástico sobre a alavanca, o peso do conjunto e o torque τu do '
                 'usuário.', 'Com o elemento 78 pontual e sem atrito, o contato é um vínculo ideal.')]),
    ('K', 253, 256),
    ("E", 257, [('Com aceleração nula e Qnc = τu, a equação de movimento da seção 3.2.13 reduz-se '
                'a essa condição.',
                '')]),
    ("E", 348, [('O equilíbrio é escrito pelo trabalho virtual num giro δq, em radianos,',
                'No exoesqueleto 3, o equilíbrio é escrito pelo trabalho virtual num giro δq, em '
                'radianos,')]),
    ('K', 349, 353),
    H("t_ident"),
    ("E", 165, [('A referência de comparação é a curva',
                'No exoesqueleto 1, a referência de comparação é a curva'),
               (', registrados em θ* e listados na Tabela 5 na ordem da extração.',
                ', registrados em θ*.')]),
    ('K', 166, 168),
    ("P", 'Com h e θ_{off} fixados, X_{pose} foi reidentificado por varredura unidimensional, em '
          'passo de 0,001 mm, com K dado pela Equação (29) em cada valor. A qualidade do ajuste é '
          'avaliada pela raiz do erro quadrático médio (RMSE), pelo erro absoluto médio (MAE), '
          'pelo erro máximo e pelo coeficiente de determinação R^{2}, com o resíduo dado pelo '
          'torque calculado na convenção da patente, −τ, menos o valor extraído.'),
    ('K', 171),
    ("E", 259, [('As Figuras 16 e 17 da patente são apresentadas',
                'No exoesqueleto 2, as Figuras 16 e 17 da EP 3 504 033 B1 são apresentadas'),
               (' (Figura 5)', '')]),
    ('K', 260, 261),
    ("R", 266, 'Os pontos das três curvas foram extraídos neste trabalho e estão no arquivo '
               'fig16_curvas.csv. A extração dividiu a leitura vertical por 21,1311 para obter a '
               'razão em divisões da grade e teve erro mediano de sobreposição inferior a 0,5 px, '
               'que corresponde a 0,024 divisão na ordenada e a 0,38° na abscissa; a imagem e a '
               'resolução usadas na leitura não foram registradas, e a incerteza da extração não '
               'foi avaliada de forma independente.'),
    ("E", 268, [(', e está descrita no Apêndice A.',
                '.')]),
    ('K', 269, 272),
    # a reprodução da Figura 16 da EP saiu a pedido do autor (14/11), para o 3.9 não mostrar a
    # figura de uma patente só; os pontos extraídos dela aparecem nos resultados
    ('K', 273, 277),
    ("R", 278, 'A robustez da identificação foi avaliada com outras faixas de θ_{el}, de 15° a '
               '170°, de 25° a 160° e de 40° a 150°, com ruído de 0,5 px nas duas coordenadas de '
               'cada ponto, em 500 sorteios, com o sinal de θ_{b,pose} oposto e com a abscissa da '
               'figura deslocada de ±0,93° ou espelhada; um teste sintético, com curvas montadas '
               'pelo próprio modelo a partir de valores conhecidos de s_{0}, confere a '
               'implementação.'),
    ('K', 279, 285),
    ("E", 355, [('A Figura 16 da US 9.737.374 B2 foi digitalizada neste trabalho',
                'No exoesqueleto 3, a Figura 16 da US 9.737.374 B2 foi digitalizada neste trabalho'),
                (", e a RM foi mantida onde fecha com AASM + AWM", ""),
                ("nas três curvas.", "nas três curvas. Cada curva da figura tem 27 marcadores, de Θ = −74° a "
                 "30°, a cada 4°, ligados por linhas; os valores nos marcadores, que são os dados publicados, "
                 "foram lidos no mesmo traçado e conferidos pelos símbolos encontrados na imagem e pelo "
                 "fechamento RM = AASM + AWM."),
                (" A ordenada não tem unidade, e a AWM é um cosseno puro, o momento de um peso a distância fixa do "
                 "pivô.", "")]),
    ('K', 356, 357),
    ("E", 358, [(" O giro do came, que fixa a constante da rotação das polias, foi medido na Figura 14D, e R20, "
                 "nas Figuras 14C e 14D (seção 4.3.1).", ""),
                ("os dois ajustes estão na seção 4.3.4.",
                 "os dois ajustes estão na seção 4.3.4. Todos os ajustes foram feitos na curva grau a grau e "
                 "repetidos só nos marcadores abaixo do limite de subida.")]),
    H("t_varr"),
    ("P", 'Em cada mecanismo, o parâmetro geométrico menos certo foi varrido, com os demais '
          'congelados. A varredura é um diagnóstico, e não uma otimização: nenhum parâmetro do '
          'modelo é substituído pelo resultado, e cada valor é testado por critérios de validade '
          'física que não usam a curva da patente.'),
    ("E", 173, [('Para separar o que a curva extraída informa sobre h',
                'No exoesqueleto 1, para separar o que a curva extraída informa sobre h'),
               (" A varredura é um diagnóstico, não uma otimização: K permanece congelado em 174,68 em todos "
                "os valores de h, não é reidentificado por h, e nenhum parâmetro do modelo é substituído pelo "
                "resultado.", " K permanece congelado em 174,68 em todos os valores de h e não é reidentificado "
                "por h.")]),
    ('K', 174),
    ("R", 175, 'Para cada h são calculados o RMSE contra os 29 pontos extraídos e três critérios '
               'de validade física: (i) tração, isto é, extensão da mola não negativa em toda a '
               'faixa de operação, calculada sem a limitação da Equação (21), para que o '
               'afrouxamento do cabo apareça como extensão negativa; (ii) fechamento, isto é, '
               'existência de tangente ao tambor (ρ > R) em toda a faixa; e (iii) trabalho '
               'virtual, isto é, resíduo da Equação (19) inferior a 10^{−6} mm/rad. O torque '
               'gravitacional não entra em nenhum critério da varredura.'),
    ("R", 177, "Da varredura derivam o h de menor RMSE, os platôs de RMSE, a fronteira de tração, obtida por "
               "bissecção, o h em que o ponto morto entra na faixa de operação, dado pela Equação (24), e os nós "
               "da família de curvas, ângulos em que as curvas para sete valores de h quase coincidem."),
    ("E", 287, [('O comprimento',
                'No exoesqueleto 2, o comprimento'),
               ("é o comprimento e do segmento OP, isto é, a excentricidade", "é a excentricidade"),
               (" Trata-se de diagnóstico, e nenhum parâmetro é substituído pelo resultado.", "")]),
    ("E", 360, [('O giro do came em relação à primária é a grandeza menos certa',
                'No exoesqueleto 3, o giro do came em relação à primária é a grandeza menos certa'),
               ("O contorno do came tem um rebaixo, onde fica a âncora 573, ladeado por duas pontas, e a "
                "envoltória convexa atravessa esse rebaixo por um segmento reto, que não é canal. Por isso, só "
                "valem os giros em que o cabo da mola sai do canal em toda a faixa do ajuste, isto é, em que ele "
                "deixa o rebaixo pela ponta de cima e se enrola no canal até a ponta de baixo.",
                "Só valem os giros em que o cabo da mola sai do canal em toda a faixa do ajuste, entre as duas "
                "pontas do rebaixo onde fica a âncora 573, que a envoltória convexa atravessa por um segmento "
                "reto."),
               (" Trata-se de diagnóstico, e nenhum parâmetro é substituído pelo resultado.", "")]),
    ("R", 361, 'Além do giro contínuo, foram testadas as montagens que os furos permitem. Nas '
               'Figuras 14C e 14D, há cinco furos pequenos num arco em torno do pino 572, que '
               'acompanham o came de uma figura para a outra. Admitido, por hipótese, que a polia externa tenha furos '
               'correspondentes, o came pode ser fixado girado de j passos em relação ao desenho, '
               'com j de −4 a +4, e, com os mesmos cinco furos nas duas peças, 5 − |j| pares '
               'coincidem; j positivo é o giro anti-horário na vista das Figuras 14C e 14D.'),
    ("R", 362, "Cada montagem foi calculada de dois modos: com a mola e o cabo da montagem desenhada, com "
               "k e x_{0} do ajuste da seção 3.3.10 e o alongamento dado pela variação do comprimento do cabo "
               "da mola desde a pose do CAD com o came desenhado; e com k e x_{0} ajustados de novo à Figura 16 "
               "da US 9.737.374 B2, como no giro contínuo."),
    H("t_verif"),
    ("E", 179, [('A cadeia de cálculo é conferida a cada execução do modelo',
                'No exoesqueleto 1, a cadeia de cálculo é conferida a cada execução do modelo'),
               (": os resíduos f1 e f2 das Equações (7) e (8); a identidade τ = −F m/1000 da Equação (22); a "
                "coincidência das Equações (12) e (15) para o ponto de tangência; a coincidência da Equação (23) "
                "com a raiz de m(θ*) = 0 obtida por bissecção; o resíduo da Equação (19), calculado",
                ", com os resíduos na Tabela 6; o do trabalho virtual, Equação (19), é calculado"),
               ("; e a identidade Xpose = Lpose − Llivre.", ".")]),
    ("R", 180, 'Testes automatizados, executados com o pytest, verificam ainda, entre outros '
               'pontos, que o torque é linear em K e que a formulação s − Rψ é a única das '
               'testadas que satisfaz o trabalho virtual.'),
    ("E", 289, [('As verificações estão na Tabela 16. São asserções',
                'No exoesqueleto 2, as verificações são asserções'),
               (", e o modelo confere ainda que o regime II ocorre exatamente para q ≤ q*, que o elemento 78 "
                "fica entre A e P na transição e que toda a cadeia depende de ec. Os valores são de ec = 34,785 "
                "mm, com s0 e K do cenário de projeto, em malha de 0,1° de 0° a 180°; a identificação",
                ". A identificação")]),
    ("R", 364, "No exoesqueleto 3, os scripts executam verificações com tolerância declarada, do fechamento "
               "com as grandezas do CAD ao caminho inverso, ao trabalho virtual e à rotação das polias pelo "
               "enrolamento, e conferem as massas e o came contra as figuras da patente; não há um conjunto "
               "separado de testes executado com o pytest."),
    ("P", 'Foram empregados o Autodesk Fusion, para a reconstrução geométrica e a extração das '
          'propriedades de massa dos exoesqueletos 1 e 2; uma planilha eletrônica, para o '
          'transporte de eixos e a composição inercial; e a linguagem Python, com as bibliotecas '
          'NumPy, para o cálculo vetorizado, SciPy, '
          'para o processamento das imagens das folhas da patente, a envoltória convexa do came e '
          'o refinamento pelo método de Brent (BRENT, 1973), e Matplotlib, para as '
          'figuras. Os números e as figuras do capítulo 4 são produzidos pelos scripts '
          'tcc_resultados.py, tcc_resultados_ottobock.py e tcc_resultados_exo3.py, que não '
          'alteram parâmetro algum dos modelos.'),
    ("P", 'Os três modelos são planos e admitem vínculos ideais, sem atrito nas articulações, no '
          'tambor e nas polias, cabos inextensíveis e elementos elásticos lineares e sem massa. '
          'Não integram o escopo a avaliação experimental com participantes humanos, a '
          'eletromiografia, a análise de conforto e usabilidade, a fabricação e o ensaio de '
          'protótipo e o dimensionamento estrutural das peças.'),
]

# figuras reduzidas: índice do bloco da imagem → fator
ESCALA_FIGURAS = {320: 0.9,
                  413: 0.9, 438: 0.9, 443: 0.9, 462: 0.9, 509: 0.9, 538: 0.9, 544: 0.9, 553: 0.9, 607: 0.9,
                  617: 0.85, 623: 0.9, 633: 0.9, 760: 0.9}

# ====================================================================== capítulo 4, fundido por tópico
# a pedido do autor (14/11), o capítulo 4 segue o 3: cada seção é um assunto, com os exoesqueletos
# 1, 2 e 3 em sequência, e as subseções 4.e.k do documento longo vão para o tópico correspondente
# (RESULTADOS e ALIAS). Saem os títulos por exoesqueleto e as três aberturas, trocadas por uma só.
# Continuam fora as tabelas de pontos (5, 15 e 23), a de zonas (9), as de platôs e valores notáveis
# de h (11 e 12), a de grandezas por ângulo do exoesqueleto 2 (18), coberta pela 20, e a 29, do
# exoesqueleto 3, coberta pelas figuras novas do confronto (pedido de 15/11); todas as figuras ficam. A pedido do
# autor (15/11), o exoesqueleto 3 tem as mesmas seções dos outros dois: voltam as verificações
# do exoesqueleto 3 (Tabela 24, com a 6 no mesmo formato; as do 2 continuam fora, como no arquivo do autor), a Tabela 27 e os parágrafos de 4.3.1 e 4.3.9, e
# entram a reprodução da Figura 16 pelos marcadores, os indicadores do ajuste, o perfil em x0, a
# força da mola e a energia, as poses medidas e a fração do peso sustentada por configuração
RESULTADOS = [
    ("r_geo", "Geometria reconstruída e propriedades de massa"),
    ("r_dados", "Dados extraídos das patentes"),
    ("r_verif", "Verificação da cadeia de cálculo"),
    ("r_ident", "Parâmetros do modelo e identificação"),
    ("r_ajuste", "Qualidade do ajuste às curvas das patentes"),
    ("r_comp", "Comportamento do elemento elástico e do mecanismo"),
    ("r_varr", "Varredura paramétrica"),
    ("r_conf", "Confronto com o torque gravitacional"),
    ("r_lim", "Limitações dos resultados"),
]
_R = dict(RESULTADOS)


def HR(chave):
    return ("H", "4", chave, _R[chave])


# subseção do documento longo → tópico do capítulo 4 (no documento longo, o exoesqueleto 2 tem
# 4.2.3 de verificação, 4.2.4 de identificação, 4.2.5 de forma e 4.2.6 de parâmetros)
ALIAS.update({"4.1": None, "4.2": None, "4.3": None})
ALIAS.update({f"4.1.{k}": t for k, t in enumerate(
    ["r_geo", "r_dados", "r_verif", "r_ident", "r_ajuste", "r_comp", "r_varr", "r_conf", "r_lim"], 1)})
ALIAS.update({f"4.2.{k}": t for k, t in enumerate(
    ["r_geo", "r_dados", "t_verif", "r_ident", "r_ajuste", "r_ident", "r_comp", "r_varr", "r_conf",
     "r_lim"], 1)})
ALIAS.update({f"4.3.{k}": t for k, t in enumerate(
    ["r_geo", "r_dados", "r_verif", "r_ident", "r_ajuste", "r_comp", "r_varr", "r_conf", "r_lim"], 1)})

# tabelas de mesmo tipo têm o mesmo formato nos três exoesqueletos (pedido de 14/11): mesmo
# cabeçalho, mesmas larguras e mesmo alinhamento; só os números e as linhas mudam
GEO = {"cab": ["Grandeza", "Símbolo", "Valor", "Unidade", "Origem"],
       "larg": [3400, 1100, 1100, 1000, 2760], "alin": ["left", "center", "center", "center", "left"]}
MASSA = {"larg6": [2300, 1300, 1200, 1200, 1680, 1680], "larg5": [3000, 1500, 1500, 1680, 1680],
         "alin6": ["left"] + ["center"]*5, "alin5": ["left"] + ["center"]*4}
# o autor tirou a coluna Situação das três (arquivo de 15/11/2026)
PARAM = {"cab": ["Parâmetro", "Símbolo", "Valor adotado", "Origem"],
         "larg": [2900, 1600, 2120, 2740], "alin": ["left", "center", "center", "left"]}

# as tabelas de verificação dos exoesqueletos 1 e 3, no mesmo formato (pedido de 15/11: tabelas de mesmo tipo iguais)
VERIF = {"cab": ["Verificação", "Resultado"], "larg": [6300, 3060], "alin": ["left", "center"]}

CAP4 = [
    ('K', 374),
    ("P", 'Este capítulo segue a ordem do capítulo 3: cada seção trata de um assunto e apresenta '
          'os resultados dos exoesqueletos 1, 2 e 3, nessa ordem. Salvo indicação em contrário, os '
          'números do exoesqueleto 1 foram obtidos com o modelo vigente e os parâmetros congelados '
          'K = 174,68, H_{CAL} = 22,701 mm e X_{pose} = 37,383 mm; os do exoesqueleto 2, com a '
          'geometria do CAD, e_{c} = 34,785 mm, s_{0} = 300,750 mm, identificado pelo espaçamento '
          'entre as curvas da Figura 16 da EP 3 504 033 B1, e K = K_{40} = 2,54982 N/mm, hipótese '
          'de projeto; e os do exoesqueleto 3, com a geometria do CAD, R_{20} = 32,035 mm, o giro '
          'do came medido na Figura 14D da US 9.737.374 B2 e a escala que iguala a AWM ao torque do '
          'peso do membro de referência (seção ⟦S:t_ident⟧), de 0,1349 N·m por unidade da figura.'),

    # ------------------------------------------------------------------ geometria e massa
    HR("r_geo"),
    ("P", 'No exoesqueleto 1, a reconstrução da vista em corte do gerador de torque forneceu as '
          'grandezas da Tabela 3.'),
    ("E", 383, [(" Os segmentos do membro seguem de Leva (1996) para o indivíduo masculino de referência, de "
                 "73,0 kg e 1,741 m, com o cotovelo estendido; as peças do exoesqueleto provêm do modelo em CAD.",
                 "")]),
    ("E", 387, [(' O momento de inércia destina-se à etapa dinâmica, não executada, e não participa '
                'do cálculo do torque estático.', ''),
               (' + M d', ' + M.d')]),
    ("E", 380, [("Grandezas medidas na reconstrução em CAD", "Grandezas geométricas do exoesqueleto 1 na pose do CAD")]),
    ("T", 381, dict(GEO, extra=["CAD"]*8)),
    ('K', 382),
    ("E", 384, [("Propriedades de massa do conjunto braço-exoesqueleto",
                 "Propriedades de massa do conjunto que gira com o braço do exoesqueleto 1, em relação "
                 "ao eixo da junta")]),
    ("T", 385, {"cab": ["Corpo", "Massa (kg)", "d (mm)", "I_{cm} (kg·m^{2})", "I_{O} (kg·m^{2})"],
                "linhas": [["Conjunto braço-exoesqueleto", "4,034309", "282,128", "0,127111", "0,448227"]],
                "larg": MASSA["larg5"], "alin": MASSA["alin5"]}),
    ('K', 386),
    ("N", 'Nota: d é a distância do centro de massa ao eixo da junta. Na pose de referência, o centro '
          'de massa fica em (x_{cm}; y_{cm}) = (−281,432; −19,812) mm, e a amplitude do momento '
          'gravitacional é M g d = 11,1619 N·m.'),
    ("E", 479, [("A Tabela 13 reúne", "No exoesqueleto 2, a Tabela 13 reúne")]),
    ("E", 480, [("Grandezas medidas no modelo em CAD e grandezas derivadas",
                 "Grandezas geométricas do exoesqueleto 2 na pose do CAD")]),
    ("T", 481, dict(GEO, troca=[("Derivada", "Calculada")])),
    ('K', 482, 483),
    ("P", 'Na pose do CAD, o circuito dá s = 359,7679 mm até a ponta da peça de fixação do '
          'elástico, que difere do comprimento medido s_{pose} em 1,4 × 10^{−4} mm, valor '
          'inferior à resolução da medida. O elemento 78 está a p = 7,754 mm do eixo da '
          'articulação, enquanto a patente prefere esse elemento sobre o eixo (seção ⟦S:4.2.9⟧).'),
    ("P", 'No modelo em CAD, o braço do exoesqueleto (elemento 8) tem massa de 163,951 g e centro '
          'de massa a 47,362 mm do eixo da articulação 20, estimativas obtidas da geometria '
          'reconstruída e de um material atribuído no CAD, náilon 6/6 em peça oca segundo a '
          'planilha, e não propriedades do produto. O braço do exoesqueleto acrescenta 0,1640 kg '
          'ao conjunto e desloca seu centro de massa em 0,194° em relação ao eixo do braço; a '
          'alavanca, o elemento 78 e a braçadeira não estão modelados como corpos separados.'),
    ("E", 485, [("Propriedades de massa do conjunto que gira com o braço em relação ao eixo da articulação 20",
                 "Propriedades de massa do conjunto que gira com o braço do exoesqueleto 2, em relação ao "
                 "eixo da articulação 20")]),
    ("T", 486, {"cab": ["Corpo", "Massa (kg)", "d (mm)", "L (mm)", "I_{cm} (kg·m^{2})", "I_{O} (kg·m^{2})"],
                "ordem": [0, 1, 3, 2, 4, 5], "troca": [("d = ", "")],
                "larg": MASSA["larg6"], "alin": MASSA["alin6"]}),
    ('K', 487),
    ("N", "Nota: d é a distância do centro de massa ao eixo da articulação 20, e L, o comprimento do "
          "segmento."),
    ('K', 488),
    ("E", 569, [("A Tabela 21 reúne", "No exoesqueleto 3, a Tabela 21 reúne")]),
    ("E", 570, [("Grandezas do circuito do cabo de ancoragem na pose do CAD",
                 "Grandezas geométricas do exoesqueleto 3 na pose do CAD")]),
    ("T", 571, dict(GEO, troca=[("Derivada", "Calculada")])),
    ('K', 572, 575),
    ("P", 'A Tabela 22 reúne as propriedades de massa do conjunto que gira com o braço em torno do '
          'pivô 584: os segmentos do membro de referência, segundo de Leva (1996), e as peças do '
          'apoio de braço, medidas no modelo em CAD.'),
    ("E", 576, [("Propriedades de massa do conjunto que gira com o braço em relação ao pivô 584",
                 "Propriedades de massa do conjunto que gira com o braço do exoesqueleto 3, em relação ao "
                 "pivô 584")]),
    ('K', 577, 581),

    # ------------------------------------------------------------------ dados extraídos
    HR("r_dados"),
    ("E", 389, [('A Tabela 5 reúne os 29 pontos extraídos da curva da patente, na ordem da '
                'extração, com os ângulos correspondentes nas convenções da seção 3.1.3, o torque '
                'calculado pelo modelo com os parâmetros congelados e o resíduo. Os pontos cobrem',
                'No exoesqueleto 1, os 29 pontos extraídos da curva da patente cobrem'),
               (" Os valores são expressos em u.p. porque a figura de origem não declara unidade (seção 2.10).", "")]),
    ("E", 491, [('Foram extraídos 48 pontos da curva tracejada',
                 'No exoesqueleto 2, foram extraídos da Figura 16 da patente 48 pontos da curva tracejada'),
                (' (Tabela 15)', '')]),
    ("E", 583, [('Da Figura 16 da US 9.737.374 B2 foram extraídos 106 pontos de cada curva',
                 'No exoesqueleto 3, foram extraídos 106 pontos de cada curva da Figura 16 da US 9.737.374 B2'),
                (' A Tabela 23 traz os valores em ângulos de 15 em 15 graus e no máximo da AASM.', '')]),
    ("P", f'A Figura 16 da US 9.737.374 B2, porém, não é só um traçado: cada curva tem 27 '
          f'marcadores, de Θ = −74° a 30°, a cada 4°, e a linha entre eles apenas os liga. Os '
          f'marcadores são, portanto, os dados que a patente publica, e seus valores foram lidos no '
          f'mesmo traçado digitalizado. Dos {M3["simb_tot"]} marcadores com leitura nas três curvas, '
          f'{M3["simb_n"]} têm o símbolo encontrado na imagem junto ao valor lido, com desvio '
          f'mediano de {M3["simb_med"]} e RMS de {M3["simb_rms"]} unidade. Nos marcadores, as três '
          f'curvas fecham RM = AASM + AWM com diferença de no máximo {M3["fecha"]} unidade nos '
          f'{M3["n_rm"]} em que a RM foi lida, e a AWM é um cosseno de amplitude {M3["awm_marc"]}, '
          f'contra {M3["awm_curva"]} na curva grau a grau, com resíduo RMS de {M3["awm_res"]}.'),
    ("P", f'O maior valor marcado da AASM é {M3["aasm_mmax"]}, em Θ = {M3["aasm_mmax_th"]}, e ela '
          f'fica acima de 95% dele em {M3["pat_m_n"]} marcadores, de Θ = {M3["pat_m_ini"]}° a '
          f'{M3["pat_m_fim"]}°; vale {M3["aasm_mini"]} no primeiro marcador e {M3["aasm_mfim"]} no '
          f'último. A RM é negativa em todos os marcadores, isto é, a figura nunca mostra o peso do '
          f'braço todo sustentado; ela vai de {M3["rm_mmax"]}, em Θ = {M3["rm_mmax_th"]}°, a '
          f'{M3["rm_mmin"]}, em Θ = {M3["rm_mmin_th"]}°. Os {M3["n_acima"]} últimos marcadores ficam '
          f'acima do limite de subida do modelo, Θ = {M3["lim"]}°, e não entram nos ajustes.'),
    ("E", 588, [(" Das Figuras 14C e 14D saíram as poses, a escala do desenho e o giro do came (seção 4.3.1).",
                 "")]),

    # ------------------------------------------------------------------ verificação
    HR("r_verif"),
    ("P", 'As verificações descritas na seção ⟦S:t_verif⟧ acompanham o cálculo nos três modelos, e '
          'esta seção detalha as dos exoesqueletos 1 e 3.'),
    ("E", 395, [('As verificações automáticas da seção 3.1.12 resultaram nos resíduos da Tabela 6,',
                 'No exoesqueleto 1, os resíduos estão na Tabela 6,')]),
    ("E", 396, [("Verificações da cadeia de cálculo (h = 22,701 mm)",
                 "Verificações da cadeia de cálculo do exoesqueleto 1 (h = 22,701 mm)")]),
    ("T", 397, VERIF),
    ('K', 398, 399),
    ("P", 'O efeito do arco é pequeno em valor absoluto: ele varia 1,862 mm na faixa de operação, '
          'contra 42,435 mm de variação do caminho total (4,4%), e altera a extensão da mola em '
          'até 1,782 mm.'),
    ("E", 590, [("As verificações da seção 3.3.12 resultaram",
                 "No exoesqueleto 3, as verificações da seção 3.3.12 resultaram")]),
    ("E", 591, [("Verificações da cadeia de cálculo do modelo da Levitate",
                 "Verificações da cadeia de cálculo do exoesqueleto 3")]),
    ("T", 592, VERIF),
    ('K', 593, 594),

    # ------------------------------------------------------------------ parâmetros e identificação
    HR("r_ident"),
    ("E", 402, [('A Tabela 7 reúne', 'No exoesqueleto 1, a Tabela 7 reúne')]),
    ("E", 403, [("Parâmetros não publicados, origem e verificação",
                 "Parâmetros não publicados do exoesqueleto 1, origem e situação")]),
    ("T", 404, dict(PARAM, linhas=[
        ["Calibração angular", "θ_{off}", "133,017°", "Congelado"],
        ["Posição da ancoragem", "H_{CAL}", "22,701 mm", "Congelado"],
        ["Extensão da mola na pose", "X_{pose}", "37,383 mm", "Identificado"],
        ["Rigidez da mola", "K", "174,68", "Identificado"]])),
    ('K', 405, 406),
    ("P", 'Com h = 22,701 mm e θ_{off} congelados, a varredura de X_{pose} com K dado pela '
          'Equação (29) reproduz o par identificado: X_{pose} = 37,383 mm, K = 174,676 e RMSE de '
          '1,8305 u.p. A origem de H_{CAL}, ao contrário, não pôde ser reproduzida. Numa análise '
          'complementar, em que X_{pose} e K são reidentificados para cada h, o RMSE tem mínimo '
          'interior em h ≈ 24,0 mm, com RMSE de 1,682 u.p., e fica abaixo de 2 vezes o mínimo de '
          'h = 19,25 a 31,00 mm: com K e a extensão na pose livres, a curva extraída não '
          'determina h. Por isso, H_{CAL} é tratado como parâmetro congelado de origem não '
          'reproduzida; ele é mantido porque o par (K, X_{pose}) foi identificado nesse valor e '
          'porque o ponto morto correspondente, na elevação de 30,485°, fica a 0,485° do início '
          'da zona neutra indicado na patente.'),
    ("P", 'A formulação sem o arco alcança RMSE de 1,152 u.p. no mesmo h, contra 1,830 u.p. com o '
          'caminho completo. Ela ajusta melhor a curva publicada, mas viola a conservação de '
          'energia (seção 4.1.3) e não foi adotada: o menor RMSE não é critério de validade '
          'física.'),
    ("E", 518, [("A Tabela 17 resume", "No exoesqueleto 2, a Tabela 17 resume")]),
    ("E", 519, [("Parâmetros não publicados, origem e identificabilidade",
                 "Parâmetros não publicados do exoesqueleto 2, origem e situação")]),
    ("T", 520, dict(PARAM, ordem=[0, 1, 2, 3])),
    ('K', 521),
    ("E", 503, [("Pela Equação", "Identificado pelo espaçamento entre as curvas, pela Equação")]),
    ("E", 504, [(' A Tabela 31 e os detalhes estão no Apêndice A.',
                '')]),
    ("P", 'As três estimativas do fator G coincidem (Figura 12(a)), com dispersão mediana de '
          '0,84% entre 20° e 165°. O fim da curva pontilhada confirma o resultado de forma '
          'independente: a razão dessa curva, extrapolada, chega a zero em 171,19° com os dois '
          'últimos pontos, onde s = 309,75 mm, a 1,40 mm do s_{0} identificado pelo espaçamento.'),
    ('K', 508, 511),
    ("E", 596, [("A Tabela 25 resume", "No exoesqueleto 3, a Tabela 25 resume")]),
    ("E", 600, [("A Tabela 26 resume esses ajustes, o do melhor giro da seção 4.3.7 e, para comparação,",
                 "A Tabela 26 resume esses ajustes, refeitos também só nos marcadores, os do melhor giro e da "
                 "montagem de dois furos no sentido horário (seção 4.3.7) e, para comparação,")]),
    ("E", 597, [("Parâmetros não publicados do mecanismo da Levitate, origem e identificabilidade",
                 "Parâmetros não publicados do exoesqueleto 3, origem e situação")]),
    ("T", 598, dict(PARAM, ordem=[0, 1, 2, 3])),
    ('K', 599),
    ("E", 601, [("Mola linear ajustada à curva AASM da Figura 16 da US 9.737.374 B2, na escala da AWM",
                 "Mola linear ajustada à curva AASM e aos marcadores da Figura 16 da US 9.737.374 B2, na "
                 "escala da AWM")]),
    ("T", 602, {"cab": ["Ajuste", "Pontos", "k (N/mm)", "x_{0} (mm)", "F_{s} na pose (N)", "R^{2}",
                        "Erro quadrático médio (N·m)", "Erro máximo (N·m)"],
                "linhas": [
                    ["Came como na Figura 14D", "Curva", "0,492", "323,6", "159", "0,901", "0,91", "1,69"],
                    ["Came como na Figura 14D", "Marcadores", M3["d_k"], M3["d_x0"], M3["d_fpose"], M3["d_r2"],
                     M3["d_rms"], M3["d_max"]],
                    ["Came como na Figura 14D, com o peso do apoio", "Curva", "0,610", "293,6", "179", "0,918",
                     "0,87", "1,56"],
                    ["Came como na Figura 14D, com o peso do apoio", "Marcadores", M3["mp_k"], M3["mp_x0"],
                     M3["mp_f"], M3["mp_r2"], M3["mp_rms"], M3["mp_max"]],
                    ["Came girado de −49°", "Curva", "2,053", "121,2", "249", "0,953", "0,63", "1,09"],
                    ["Came dois furos no sentido horário", "Curva", M3["d2_k"], M3["d2_x0"], M3["d2_f"],
                     M3["d2_r2"], M3["d2_rms"], M3["d2_max"]],
                    ["Came dois furos no sentido horário", "Marcadores", M3["df_k"], M3["df_x0"], M3["df_f"],
                     M3["df_r2"], M3["df_rms"], M3["df_max"]],
                    ["Came como na Figura 14D, na escala do artigo", "Curva", "1,448", "323,6", "468", "0,901",
                     "2,68", "4,99"]],
                "larg": [2200, 1250, 950, 850, 950, 700, 1260, 1200],
                "alin": ["left", "left"] + ["center"]*6}),
    ('K', 603),
    ("N", f'Nota: curva: os {M3["ic_n"]} pontos grau a grau de Θ = {M3["ic_ini"]}° a {M3["ic_fim"]}°; '
          f'marcadores: os {M3["im_n"]} marcadores de Θ = {M3["im_ini"]}° a {M3["im_fim"]}°, abaixo do '
          f'limite de subida. Came dois furos no sentido horário: montagem a {M3["df_giro"]}°.'),
    ("P", f'Nos marcadores, a qualidade do ajuste é praticamente a mesma da curva, mas a divisão '
          f'entre k e x_{{0}} muda: com o came como na Figura 14D, k = {M3["d_k"]} N/mm e x_{{0}} = '
          f'{M3["d_x0"]} mm, contra {M3["d_kc"]} N/mm e {M3["d_x0c"]} mm, enquanto a força na pose '
          f'fica em {M3["d_fpose"]} N, contra {M3["d_fpose_c"]} N. O perfil do ajuste em x_{{0}} mostra '
          f'por quê. Com x_{{0}} fixado e só k ajustado, o R^{{2}} fica a menos de {M3["tol_r2"]} do '
          f'máximo de x_{{0}} = {M3["pc_x0a"]} a {M3["pc_x0b"]} mm na curva, com k de {M3["pc_ka"]} a '
          f'{M3["pc_kb"]} N/mm, e de {M3["pm_x0a"]} a {M3["pm_x0b"]} mm nos marcadores, com k de '
          f'{M3["pm_ka"]} a {M3["pm_kb"]} N/mm; nessas faixas, a força na pose varia só de '
          f'{M3["pc_fa"]} a {M3["pc_fb"]} N na curva e de {M3["pm_fa"]} a {M3["pm_fb"]} N nos '
          f'marcadores. A curva da patente fixa, assim, o nível da força da mola, mas não separa a '
          f'rigidez do alongamento: k e x_{{0}} são identificados como par, e o par adotado é o de '
          f'maior R^{{2}} na curva grau a grau.'),
    ("P", f'O mesmo vale para as outras configurações da Tabela 26. Com o peso do apoio somado ao '
          f'alvo, os marcadores dão k = {M3["mp_k"]} N/mm e força de {M3["mp_f"]} N na pose, com '
          f'R^{{2}} = {M3["mp_r2"]}; com o came dois furos no sentido horário, k = {M3["df_k"]} N/mm, '
          f'contra {M3["d2_k"]} N/mm na curva. Em todas, curva e marcadores dão praticamente o mesmo '
          f'R^{{2}}, e a escala do artigo multiplica k e as forças por 2,94 sem mudar x_{{0}} nem o '
          f'R^{{2}}.'),

    # ------------------------------------------------------------------ ajuste às curvas
    HR("r_ajuste"),
    ("E", 412, [('A Figura 8 sobrepõe', 'No exoesqueleto 1, a Figura 8 sobrepõe')]),
    ("P", 'A forma do perfil é reproduzida com fidelidade, com duas ressalvas: os quatro '
          'parâmetros não publicados foram identificados contra os mesmos 29 pontos usados na '
          'avaliação, de modo que a aderência não constitui validação independente do modelo, e a '
          'incerteza da extração não é conhecida. Os resíduos não se distribuem aleatoriamente: '
          'ordenados por θ*, formam três zonas extensas de sinal alternado, que reúnem 25 dos 29 '
          'pontos. O modelo superestima o torque acima de 155° de elevação e entre 45° e 94° e o '
          'subestima entre 100° e 150°, o que sugere diferença sistemática de forma entre o '
          'modelo e a curva, e não apenas dispersão de digitalização. No último ponto, além do '
          'ponto morto calculado (θ*_{pm} = 192,532°), o modelo prevê torque de −1,709 u.p., com '
          'sinal invertido, e a curva extraída registra 0,443 u.p., diferença coerente com a '
          'ausência, no modelo, da protuberância do dispositivo real.'),
    ('K', 413, 415),
    ("E", 416, [("Indicadores de qualidade do ajuste à curva da patente",
                 "Indicadores de qualidade do ajuste do exoesqueleto 1 à curva da patente")]),
    ("T", 417, {"cab": ["Indicador", "Valor"], "larg": [4400, 4960], "alin": ["left", "left"]}),
    ('K', 418),
    ("P", 'No exoesqueleto 2, com os valores de s_{0} identificados pelo espaçamento, o fator G lido '
          'na Figura 16 da patente e a forma m/(1000 τ_{g}) prevista pelo modelo diferem (Figura '
          '12(b)): normalizada em 90°, a razão entre os dois vale 0,26 em 20°, 0,79 em 60°, 1,34 '
          'em 120° e 2,94 em 165°. Em consequência, a razão calculada não reproduz a Figura 16 da '
          'patente: com escala comum às três curvas, o coeficiente de determinação é −0,417 '
          '(pontilhada), −1,529 (tracejada) e −0,620 (contínua). Como o s implícito na figura '
          'concorda com o do CAD, com diferença de 0,84 mm RMS, a causa não é s nem, como causa '
          'principal, o braço de momento, que depende da derivada de s; ela aponta para o torque '
          'do peso usado pela patente ou para a definição da ordenada, que a patente não permite '
          'separar.'),
    ("P", 'O ajuste de forma, que deixa s_{0} e a escala livres em cada curva, absorve essa '
          'diferença em s_{0}. Os valores que ele encontra, 294,34 mm na pontilhada, 213,40 mm na '
          'tracejada e 0,00 mm na contínua, o limite inferior da busca, afastam-se dos do '
          'espaçamento, e as escalas por curva contrariam o atuador único descrito na patente. '
          'São mantidos como resultado secundário (Figura 20(a)). Com uma escala comum às três '
          'curvas (Figura 20(b)), o ajuste ordena os comprimentos de referência como as '
          'pré-tensões descritas na patente, mas não reproduz a forma da curva pontilhada, de '
          'menor pré-tensão.'),
    ("E", 759, [("Pontos extraídos da Figura 16 da patente e razão calculada pelo ajuste de forma",
                 "Ajuste de forma às curvas da Figura 16 da patente")]),
    ('K', 760, 762),
    ("E", 605, [("Com o giro do came da Figura 14D, o ajuste tem",
                 "No exoesqueleto 3, com o giro do came da Figura 14D, o ajuste tem")]),
    ("E", 609, [("As marcas das zonas não entram no ajuste e servem de conferência. Com esse giro",
                 "Com esse giro")]),
    ("E", 606, [("Curva AASM da Figura 16 da US 9.737.374 B2 contra", "Curva AASM contra"),
                 (" e giro do came como na Figura 14D (a)", " e o giro do came da Figura 14D (a)")]),
    ('K', 607, 608),
    ("P", f'Nos {M3["im_n"]} marcadores abaixo do limite de subida, que são os dados que a patente '
          f'efetivamente publica, o ajuste tem a mesma qualidade (Tabela ⟦T:e3_ind⟧): R^{{2}} = '
          f'{M3["im_r2"]}, contra {M3["ic_r2"]} na curva, e erro quadrático médio de {M3["im_rmse"]} '
          f'N·m, contra {M3["ic_rmse"]} N·m, {M3["im_rmse_rel"]}% do maior valor da AASM nos dois '
          f'casos. Os dois ajustes superestimam a AASM em média, com resíduo médio de '
          f'{M3["im_resm"]} N·m, e o erro máximo ocorre perto do limite de subida, em Θ = '
          f'{M3["ic_th_max"]}° na curva e {M3["im_th_max"]}° nos marcadores.'),
    ("TN", "e3_ind", "Indicadores de qualidade do ajuste do exoesqueleto 3 à curva AASM da patente",
     {"cab": ["Indicador", "Curva grau a grau", "Marcadores"],
      "linhas": [
          ["Pontos do ajuste", f'{M3["ic_n"]}, de Θ = {M3["ic_ini"]}° a {M3["ic_fim"]}°',
           f'{M3["im_n"]}, de Θ = {M3["im_ini"]}° a {M3["im_fim"]}°'],
          ["Raiz do erro quadrático médio, RMSE", f'{M3["ic_rmse"]} N·m', f'{M3["im_rmse"]} N·m'],
          ["Erro absoluto médio, MAE", f'{M3["ic_mae"]} N·m', f'{M3["im_mae"]} N·m'],
          ["Erro máximo", f'{M3["ic_max"]} N·m, em Θ = {M3["ic_th_max"]}°',
           f'{M3["im_max"]} N·m, em Θ = {M3["im_th_max"]}°'],
          ["Coeficiente de determinação, R^{2}", M3["ic_r2"], M3["im_r2"]],
          ["MAE relativo à média da AASM", f'{M3["ic_mae_rel"]}%', f'{M3["im_mae_rel"]}%'],
          ["RMSE relativo ao maior valor da AASM", f'{M3["ic_rmse_rel"]}%', f'{M3["im_rmse_rel"]}%'],
          ["Resíduo médio", f'{M3["ic_resm"]} N·m', f'{M3["im_resm"]} N·m'],
          ["Pico do modelo", f'{M3["ic_pico"]} N·m, em Θ = {M3["ic_th_pico"]}°',
           f'{M3["im_pico"]} N·m, em Θ = {M3["im_th_pico"]}°'],
          ["Maior valor da AASM", f'{M3["ic_maior"]} N·m, em Θ = {M3["ic_th_maior"]}',
           f'{M3["im_maior"]} N·m, em Θ = {M3["im_th_maior"]}'],
          ["Trecho acima de 95% do pico, AASM", f'Θ = {M3["ic_pata_ini"]}° a {M3["ic_pata_fim"]}°',
           f'Θ = {M3["im_pata_ini"]}° a {M3["im_pata_fim"]}°'],
          ["Trecho acima de 95% do pico, modelo", f'Θ = {M3["ic_patm_ini"]}° a {M3["ic_patm_fim"]}°',
           f'Θ = {M3["im_patm_ini"]}° a {M3["im_patm_fim"]}°']],
      "larg": [3400, 2980, 2980], "alin": ["left", "left", "left"]},
     "Fonte: elaborada pelo autor, a partir da Figura 16 da US 9.737.374 B2 (DOYLE, 2017).",
     f'Nota: AASM na escala da AWM; resíduo = modelo − patente; came como na Figura 14D. Curva: mola '
     f'adotada, k = {M3["d_kc"]} N/mm e x_{{0}} = {M3["d_x0c"]} mm; marcadores: k = {M3["d_k"]} N/mm e '
     f'x_{{0}} = {M3["d_x0"]} mm.'),
    ("P", f'O resíduo nos marcadores, modelo menos patente, forma três trechos de sinal alternado '
          f'(Figura ⟦F:e3_marc⟧b): o modelo fica acima da AASM de Θ = {M3["d_trechos"][0][0]}° a '
          f'{M3["d_trechos"][0][1]}°, abaixo dela de {M3["d_trechos"][1][0]}° a {M3["d_trechos"][1][1]}° e '
          f'de novo acima de {M3["d_trechos"][2][0]}° a {M3["d_trechos"][2][1]}°. Com o came como na '
          f'Figura 14D, a mola linear sobe antes da AASM, não alcança o patamar e cai mais devagar '
          f'perto do limite. O patamar resume a diferença de forma: a AASM fica acima de 95% do '
          f'próprio pico de Θ = {M3["ic_pata_ini"]}° a {M3["ic_pata_fim"]}° na curva e de '
          f'{M3["im_pata_ini"]}° a {M3["im_pata_fim"]}° nos marcadores, e o modelo, só de '
          f'{M3["ic_patm_ini"]}° a {M3["ic_patm_fim"]}°, num trecho mais curto e que começa mais '
          f'tarde; o pico do modelo, {M3["ic_pico"]} N·m em Θ = {M3["ic_th_pico"]}°, fica abaixo do '
          f'maior valor da curva, {M3["ic_maior"]} N·m em Θ = {M3["ic_th_maior"]}.'),
    ("P", f'Como a AWM entra igual no modelo e na patente, a RM do modelo, a AASM do modelo mais a '
          f'AWM, herda o erro da AASM: nos {M3["rmr_n"]} marcadores com RM lida abaixo do limite, o '
          f'erro quadrático médio é de {M3["rmr_rmse"]} N·m. A RM, porém, varia bem menos que a AASM '
          f'nessa faixa, {M3["rmr_amp"]} unidades contra {M3["rmr_amp_aasm"]}, e o mesmo erro absoluto '
          f'dá R^{{2}} de só {M3["rmr_r2"]} (Figura ⟦F:e3_marc⟧a): o torque que sobra para o usuário, '
          f'pequeno perto da horizontal, é a parte da figura que a mola linear reproduz pior.'),
    ("F", "e3_marc", "exo3_tcc_fig_7_marcadores.png", 6.3,
     "Reprodução da Figura 16 da patente pelos marcadores e resíduo do ajuste",
     "Figura 16 da US 9.737.374 B2 reproduzida pelos marcadores, com o modelo (a), e resíduo do "
     "ajuste em cada marcador (b)",
     "Fonte: elaborada pelo autor, a partir da Figura 16 da US 9.737.374 B2 (DOYLE, 2017).",
     "Nota: em (a), linhas cheias: AASM do modelo; tracejadas: RM do modelo, a AASM do modelo mais "
     "a AWM; ajustes só nos marcadores abaixo do limite de subida. Faixas sombreadas: marcas Z12 e "
     "Z11 da patente."),

    # ------------------------------------------------------------------ comportamento
    HR("r_comp"),
    ("E", 427, [("A Tabela 10 caracteriza", "No exoesqueleto 1, a Tabela 10 caracteriza"),
                (" As grandezas foram calculadas em malha de 0,001° com os parâmetros congelados.", "")]),
    ("P", 'Na faixa de operação, a extensão da mola vai de 12,044 mm a 54,479 mm, valor que '
          'ocorre no ponto morto, e permanece positiva: o cabo continua tracionado em todos os '
          'pontos avaliados. A razão de 1,0095 entre a extensão máxima e o comprimento livre, de '
          '53,967 mm, significa que a mola precisaria ser estendida a aproximadamente o dobro de '
          'seu comprimento livre. O braço de momento cresce de 12,451 mm em θ* = 42,917° até o '
          'teto |OA| = 22,919 mm em θ* = 97,894° e decresce a partir daí, anulando-se no ponto '
          'morto, em θ* = 192,532° (elevação de 30,485°).'),
    ('K', 428, 431),
    ("P", 'A força máxima K δ_{máx} vale 9.516,5 na unidade de K multiplicada por milímetro. Se a '
          'ordenada da patente estivesse em N·m, K estaria em N/mm, a tração no cabo chegaria a '
          '9,5 kN e o pico do torque do cabo, 147,07 N·m, seria 13,2 vezes o pico do torque '
          'gravitacional do conjunto; para equilibrar esse pico com o maior braço disponível, '
          'bastaria uma tração de cerca de 487 N. A leitura da ordenada em N·m conduz, portanto, '
          'a valores implausíveis para um dispositivo vestível, e a curva publicada é tratada '
          'como qualitativa quanto à magnitude: o modelo reproduz a forma do torque, mas não sua '
          'escala física.'),
    ("E", 523, [("Na faixa de 0° a 180° de anteversão", "No exoesqueleto 2, na faixa de 0° a 180° de anteversão"),
                ("A Tabela 18 reúne as grandezas do circuito em ângulos representativos.",
                 "A Tabela 20, na seção 4.2.9, traz s e m em ângulos representativos.")]),
    ('K', 528),
    ("E", 611, [("A Figura 17a mostra", "No exoesqueleto 3, a Figura 17a mostra")]),
    ('K', 612, 615),
    ('K', 619),
    ("P", f'Com a mola adotada, a força cai de {M3["fs_pose"]} N na pose a {M3["fs_lim"]} N no limite '
          f'de subida, e a mola continua alongada em toda a faixa, com no mínimo {M3["al_min"]} mm. A '
          f'tração no cabo 560, F_{{a}} = F_{{s}} r/R, cresce de {M3["fa_pose"]} N na pose a {M3["fa_max"]} N em '
          f'Θ = {M3["fa_th"]}° e cai a {M3["fa_lim"]} N no limite: o came amplia a força da mola '
          f'enquanto ela diminui, e é o crescimento da transmissão, e não o da força, que faz o '
          f'torque subir. Da pose ao limite de subida, a mola libera {M3["e_mola"]} J, e o torque '
          f'calculado realiza o mesmo trabalho nesse trecho, como pede o princípio dos trabalhos '
          f'virtuais; para erguer o conjunto da pose ao limite, o peso exige {M3["w_peso"]} J, e a '
          f'mola devolve {M3["e_pct"]}% dessa energia.'),
    ("E", 616, [("; as faixas sombreadas são as marcas Z12 e Z11 da Figura 16 da US 9.737.374 B2", "")]),
    ('K', 617, 618),

    # ------------------------------------------------------------------ varredura
    HR("r_varr"),
    ("P", 'Em cada mecanismo, foi varrido o parâmetro geométrico menos certo, com os demais '
          'congelados (seção ⟦S:t_varr⟧): a posição h da ancoragem no exoesqueleto 1, o trecho '
          'e_{c} da alavanca no exoesqueleto 2 e o giro do came no exoesqueleto 3.'),
    ("E", 440, [("A família não se abre de modo uniforme.",
                 "No exoesqueleto 1, a família de curvas para sete valores de h (Figura 9) não se abre "
                 "de modo uniforme.")]),
    ("E", 437, [(", com K = 174,68 e Xpose = 37,383 mm congelados, e os 29 pontos extraídos da patente",
                 "")]),
    ('K', 438, 439),
    ('K', 441),
    ("E", 445, [(" Os platôs constam da Tabela 11.", "")]),
    ('K', 449),
    ("E", 442, [(", em escala logarítmica, com os valores fisicamente viáveis, e ampliação", " e ampliação"),
                (", com os platôs de RMSE", "")]),
    ('K', 443, 444),
    ("E", 450, [(" A Tabela 12 reúne os valores notáveis de h.", "")]),
    ('K', 454),
    ("E", 530, [("Dos três critérios de validade física", "No exoesqueleto 2, dos três critérios de validade física")]),
    ('K', 531, 534),
    ("E", 535, [(" e a transição ocorre mais cedo", "")]),
    ("R", 536, 'A Figura 17 da patente não foi digitalizada, e a comparação com ela é visual. '
               'Nela, as três curvas partem de perto de 14°, e a de maior excentricidade atinge o '
               'máximo perto de 100° e cruza as outras duas entre cerca de 155° e 160°. No '
               'modelo, as curvas de τ/τ_{g} da família têm máximo entre 62,4° e 69,3°, que '
               'ocorre mais cedo quanto maior o trecho e_{c}, e se cruzam perto de 144°: o modelo '
               'reproduz a sequência de máximo, vale e subida perto de 180°, mas com o máximo '
               'antes do da patente e o cruzamento das curvas mais cedo.'),
    ("E", 537, [(", com s0 = 300,750 mm, com (a)", ", com (a)")]),
    ('K', 538, 539),
    ("E", 621, [("Repetido o ajuste com o came girado", "No exoesqueleto 3, o ajuste foi repetido com o came girado"),
                (", o cabo da mola sai do canal em toda a faixa", ", e o cabo da mola sai do canal em toda a faixa")]),
    ("E", 622, [(": R² em função do giro em relação ao desenho da Figura 14D (a)", " (a)"),
                (" e curva AASM da Figura 16 da US 9.737.374 B2 contra", " e curva AASM contra")]),
    ('K', 623, 624),
    ("P", 'Os furos em torno do pino 572 reforçam essa leitura. Os cinco têm passo médio de '
          '25,31° e ocupam quase a mesma posição no came nas duas figuras; portanto, giram com '
          'ele, e as nove montagens vão de −101,25° a +101,25° (Tabela 28).'),
    ("E", 626, [(" Nas montagens de +3 e +4 furos, o cabo da mola chega à ponta de cima do rebaixo antes do "
                 "limite de subida, em 20,5° e 9,9°, e, na de −4 furos, à ponta de baixo abaixo de −64,2°; fora "
                 "desses trechos, o modelo não vale.", "")]),
    ("E", 627, [('quando a Figura 16 foi gerada.',
                'quando a Figura 16 da US 9.737.374 B2 foi gerada.'),
                ('no sentido horário em relação ao desenho', 'no sentido horário em relação ao desenho, a −50,62°, '
                 'a 1,6° do melhor giro contínuo,')]),
    ('K', 628, 630),
    ("R", 631, 'Nota: giro positivo no sentido anti-horário, na vista das Figuras 14C e 14D; '
               'pares: furos do came e da polia que coincidem. Mesma mola: k = 0,492 N/mm e x_{0} '
               '= 323,6 mm. Outra mola: k e x_{0} ajustados à Figura 16 da US 9.737.374 B2 em '
               'cada montagem; k negativo não corresponde a mola física. Nas montagens de −4, +3 '
               'e +4 furos, o cabo da mola sai do canal em parte da faixa do ajuste, e os R^{2} '
               'não foram calculados.'),
    ("E", 632, [(" à curva AASM da Figura 16 da US 9.737.374 B2 (b)", " (b)"),
                (" e o mesmo cabo da montagem desenhada (a)", " (a)")]),
    ('K', 633, 635),
    ("P", f'Refeitos só nos marcadores, os ajustes de outra mola por montagem mantêm a ordem da '
          f'curva: R^{{2}} = {M3["mt_m3_r2"]} com −3 furos, {M3["mt_m2_r2"]} com −2 e {M3["mt_m1_r2"]} '
          f'com −1, todos com k e x_{{0}} positivos. Com o came dois furos no sentido horário, a '
          f'{M3["df_giro"]}°, k = {M3["df_k"]} N/mm e x_{{0}} = {M3["df_x0"]} mm, com erro quadrático '
          f'médio de {M3["df_rms"]} N·m e erro máximo de {M3["df_max"]} N·m, em Θ = '
          f'{M3["df_th_max"]}° (Figura ⟦F:e3_marc⟧b), e o melhor giro contínuo, {M3["mg_giro"]}°, dá '
          f'R^{{2}} = {M3["mg_r2"]}. Entre as anti-horárias, a de +1 furo, que na curva chega a k = '
          f'0,008 N/mm, passa a k negativo nos marcadores, {M3["mt_p1_k"]} N/mm, e a de +2 furos '
          f'continua sem mola física, com k = {M3["mt_p2_k"]} N/mm: nos dados da patente, só as '
          f'montagens horárias admitem uma mola linear.'),

    # ------------------------------------------------------------------ confronto
    HR("r_conf"),
    ("P", 'O que o confronto com o torque gravitacional pode mostrar depende do que se sabe da '
          'escala do torque: no exoesqueleto 1, só a forma é comparável; no exoesqueleto 2, a '
          'forma e, sob a hipótese K = K_{40}, a magnitude; e, no exoesqueleto 3, a magnitude na '
          'escala fixada pela AWM.'),
    ("P", 'No exoesqueleto 1, o torque gravitacional do conjunto, calculado pela Equação (26), '
          'atinge o máximo de 11,1619 N·m na elevação de 89,44°. Como as magnitudes não são '
          'comparáveis, confronta-se a forma dos perfis, normalizados pelos respectivos picos '
          '(Figura 11), e o confronto não informa que fração do torque gravitacional o mecanismo '
          'compensa.'),
    ("P", 'O pico do torque do cabo ocorre na elevação de 97,484°, e o do torque gravitacional, '
          'em 89,438°, com defasagem de 8,046°: o mecanismo entrega sua assistência máxima acima '
          'da posição de maior demanda gravitacional. As curvas normalizadas cruzam-se na '
          'elevação de 93,96° e, entre 105° e 150°, diferem em no máximo 0,027. Abaixo de 94°, as '
          'diferenças tornam-se negativas e crescentes em módulo, até −0,520 na elevação de 30°; '
          'no ponto morto, o torque gravitacional ainda vale 5,757 N·m, 51,6% de seu pico, '
          'enquanto o torque do cabo se anula. Trata-se de característica da arquitetura, e não '
          'de deficiência do ajuste (seção 2.3).'),
    ("E", 461, [(" (K = 174,68; h = 22,701 mm; Xpose = 37,383 mm)", "")]),
    ('K', 462, 464),
    ("P", 'O confronto ilustra a limitação apontada por Nasr, Ferguson e McPhee (2022): um '
          'mecanismo passivo entrega torque determinado para cada ângulo, de modo que o ajuste '
          'favorável em uma faixa implica desvio em outra. No caso analisado, o compromisso '
          'privilegia a faixa acima da horizontal, onde a exposição postural concentra o risco '
          'documentado por van der Molen et al. (2017) e Seidler et al. (2020), à custa de '
          'subcompensação na faixa inferior.'),
    ("P", 'No exoesqueleto 2, a forma do torque do elástico pode ser comparada à do peso sem '
          'depender de K, normalizando cada curva pelo próprio pico (Figura 14). Com o s_{0} '
          'adotado, o pico normalizado do elástico ocorre em θ_{el} = 79,1°, contra 89,8° do peso. '
          'Entre 48,40° e 83,74°, a forma do elástico fica ligeiramente acima da do peso, com no '
          'máximo +0,039; entre 83,74° e 177,02°, fica abaixo, com diferença de até −0,272 em '
          '139,2°. A posição do pico fica na faixa de 70° a 120° em que a patente prefere a força '
          'máxima.'),
    ('K', 543, 545),
    ("E", 546, [(' da Tabela 31, no Apêndice A.',
                ' testadas na identificação.')]),
    ("P", 'Em N·m, a comparação só é possível sob a hipótese K = K_{40}, e por isso a Figura 15 e a '
          'Tabela 20 descrevem um cenário de projeto, e não o dispositivo comercial. Nesse cenário, o torque '
          'do elástico atinge 4,379 N·m em θ_{el} = 79,1°, 10,7° abaixo do pico de τ_{g}. Abaixo '
          'da transição, o modelo mantém torque positivo, porque o elemento 78 está a 7,754 mm do '
          'eixo, ao passo que a Figura 16 da patente mostra razão nula abaixo de cerca de 14°.'),
    ("P", 'Com o s_{0} das outras duas curvas, K_{40} vai a 3,20932 e 2,17230 N/mm, e o pico de '
          'τ, a 4,516 N·m em 75,5° e 4,317 N·m em 81,7°: a distribuição angular da assistência '
          'depende da curva tomada como referência. O resultado ilustra a limitação discutida na '
          'seção 2.4 (NASR; FERGUSON; McPHEE, 2022): no modelo, a subcompensação recai sobre a '
          'faixa acima da horizontal. Como essa forma depende da geometria do CAD, que não '
          'reproduz a Figura 16 da patente, a leitura vale para o modelo.'),
    ('K', 548, 551),
    ("E", 552, [(" do membro e do braço do exoesqueleto", "")]),
    ('K', 553, 555),
    ("E", 637, [("Pela Equação", "No exoesqueleto 3, pela Equação")]),
    ("P", f'Na escala adotada, a AWM é o torque do peso do membro de referência, e a curva da '
          f'patente pode ser comparada com ele nos próprios marcadores. A razão AASM/|AWM| vai de '
          f'{M3["ra_min"]}, em Θ = {M3["ra_th_min"]}°, a {M3["ra_max"]}, em Θ = {M3["ra_th_max"]}°, e '
          f'passa de 90% em {M3["a90_n"]} marcadores, de {M3["a90_ini"]}° a {M3["a90_fim"]}°, o trecho '
          f'de sustentação quase constante da Z11; na horizontal, a AASM sustenta 96% do peso do '
          f'membro. A RM é o que o usuário ainda sustenta: vai de {M3["rmN_min"]} N·m, em Θ = '
          f'{M3["rmN_th_min"]}°, a {M3["rmN_max"]} N·m, em Θ = {M3["rmN_th_max"]}°, e cresce nas duas '
          f'pontas da faixa (Figura ⟦F:e3_conf⟧a).'),
    ("P", f'Com o apoio de braço, o peso a sustentar cresce, e a AASM cobre de {M3["rc_min_pct"]}%, '
          f'em Θ = {M3["rc_th_min"]}°, a {M3["rc_max_pct"]}%, em Θ = {M3["rc_th_max"]}°, do torque do '
          f'peso do conjunto nos {M3["n_dentro"]} marcadores abaixo do limite de subida, com média de '
          f'{M3["rc_media_pct"]}%; na horizontal, 89%. O que sobra fica entre {M3["sobra_min"]} N·m, em '
          f'Θ = {M3["sobra_th_min"]}°, e {M3["sobra_max"]} N·m, em Θ = {M3["sobra_th_max"]}°. Integrada '
          f'de Θ = −75° ao limite de subida, a AASM realiza {M3["w_aasm"]} J, {M3["w_aasm_pct"]}% dos '
          f'{M3["w_tg"]} J que o peso do conjunto exige nessa faixa. O modelo com a mola adotada '
          f'cobre de {M3["ca_rmin_pct"]}%, em Θ = {M3["ca_rmin_th"]}°, a {M3["ca_rmax_pct"]}%, em Θ = '
          f'{M3["ca_rmax_th"]}°, do peso do conjunto nos mesmos marcadores, com média de '
          f'{M3["ca_rmed_pct"]}%, e realiza {M3["w_mod"]} J, {M3["w_mod_pct"]}% do trabalho do peso: '
          f'sustenta menos que a patente perto da horizontal e mais nas pontas, e o que sobra para o '
          f'usuário vai de {M3["sm_min"]} N·m, em Θ = {M3["sm_th_min"]}°, a {M3["sm_max"]} N·m, em Θ = '
          f'{M3["sm_th_max"]}°.'),
    ("P", f'Normalizadas pelos picos (Figura ⟦F:e3_conf⟧b), as formas da AASM e de τ_{{g}} quase '
          f'coincidem de Θ = {M3["cruz_ini"]}° a {M3["cruz_fim"]}°, com diferença de no máximo '
          f'{M3["meio_max"]}: o pico da AASM, em Θ = {M3["pico_aasm"]}° ({M3["elev_aasm"]}° de '
          f'elevação), fica {M3["defas_aasm"]}° acima do de τ_{{g}}, em Θ = {M3["pico_tg"]}° '
          f'({M3["elev_tg"]}°), e o do modelo, em Θ = {M3["pico_mod"]}°, {M3["defas_mod"]}° abaixo. '
          f'Fora desse trecho, a assistência acompanha o peso pior: abaixo de {M3["cruz_ini"]}°, a '
          f'AASM cresce mais devagar, com diferença de até {M3["abaixo_min"]} em Θ = '
          f'{M3["th_abaixo_min"]}°, e, acima de {M3["cruz_fim"]}°, cai mais cedo, até {M3["dif_min"]} '
          f'em Θ = {M3["th_dif_min"]}°, perto do limite de subida. A curva da patente concentra a '
          f'sustentação em torno da horizontal, onde a demanda é maior, e deixa sobrar torque nas '
          f'pontas da faixa.'),
    ("F", "e3_conf", "exo3_tcc_fig_8_confronto.png", 6.3,
     "Torque da patente, do modelo e do peso no exoesqueleto 3",
     "Torque da patente, do modelo e do peso no exoesqueleto 3, em N·m (a) e normalizados pelos "
     "picos (b)",
     "Fonte: elaborada pelo autor, a partir da Figura 16 da US 9.737.374 B2 (DOYLE, 2017).",
     "Nota: AASM e AWM nos marcadores, na escala que iguala a AWM ao torque do peso do membro de "
     "referência; τ_{g} inclui o apoio de braço; modelo com a mola adotada. Linha pontilhada em (a): "
     "limite de subida; em (b), entre as linhas pontilhadas, as formas da AASM e de τ_{g} quase "
     "coincidem."),
    ("P", f'Nas duas poses que a patente desenha, medidas nas Figuras 14C e 14D (seção '
          f'⟦S:r_geo⟧), a comparação muda de natureza. Na da Figura 14C, Θ = {M3["p14c_th"]}°, dentro '
          f'da faixa da curva, o peso do conjunto vale {M3["p14c_tg"]} N·m, {M3["p14c_membro"]} N·m do '
          f'membro e {M3["p14c_apoio"]} N·m do apoio, e a AASM, {M3["p14c_aasm"]} N·m, e o modelo, '
          f'{M3["p14c_mod"]} N·m, sustentam {M3["p14c_raasm_pct"]}% dele. Na da Figura 14D, Θ = '
          f'{M3["p14d_th"]}°, com o braço quase pendente, a curva da patente não chega: ela começa em '
          f'Θ = −75°. Extrapolado com a mesma mola, o modelo dá ali {M3["p14d_mod"]} N·m, contra '
          f'{M3["p14d_tg"]} N·m do peso, {M3["p14d_rmod"]} vezes mais. Modelo e peso se igualam em Θ = '
          f'{M3["ca_eq"]}°: abaixo desse ângulo, a mola supera o peso, e o braço solto, no modelo sem '
          f'atrito, sobe até ele, que é a posição de repouso do conjunto (Figura ⟦F:e3_razao⟧).'),
    ("P", f'A fração sustentada depende da montagem e do alvo do ajuste. Com o came dois furos no '
          f'sentido horário e a mola ajustada a essa montagem, o modelo cobre de {M3["cd_rmin_pct"]}%, '
          f'em Θ = {M3["cd_rmin_th"]}°, a {M3["cd_rmax_pct"]}%, em Θ = {M3["cd_rmax_th"]}°, do peso do '
          f'conjunto nos marcadores, com média de {M3["cd_rmed_pct"]}%, iguala o peso em Θ = '
          f'{M3["cd_eq"]}°, já dentro da faixa da curva, e dá {M3["cd_pose"]} N·m na pose da Figura '
          f'14D, {M3["cd_r14d"]} vezes o peso. Com o peso do apoio somado ao alvo, a mola cobre de '
          f'{M3["cp_rmin_pct"]}% a {M3["cp_rmax_pct"]}%, com média de {M3["cp_rmed_pct"]}%, e iguala o '
          f'peso em Θ = {M3["cp_eq"]}°. Em todas as configurações ajustadas à curva da patente, a '
          f'assistência fica abaixo do peso em quase toda a faixa da curva e só passa dele perto da '
          f'posição pendente, abaixo de um ângulo que vai de Θ = {M3["ca_eq"]}° a {M3["cd_eq"]}°, '
          f'conforme a configuração.'),
    ("F", "e3_razao", "exo3_tcc_fig_9_razao.png", 6.3,
     "Fração do peso do conjunto sustentada no exoesqueleto 3 e torque que sobra para o usuário",
     "Fração do peso do conjunto sustentada no exoesqueleto 3 (a) e torque do peso que sobra para o "
     "usuário (b), da pose da Figura 14D ao limite de subida",
     "Fonte: elaborada pelo autor, a partir das Figuras 14C, 14D e 16 da US 9.737.374 B2 (DOYLE, 2017).",
     "Nota: modelos com o came e a mola de cada configuração ajustada à curva (Tabela 26); trecho "
     "pontilhado: abaixo de Θ = −75°, onde a curva da patente não chega, o modelo extrapolado. Linhas "
     "tracejadas: poses das Figuras 14D e 14C; pontilhada: limite de subida. Pontos: AASM nos "
     "marcadores, na escala da AWM. Faixas sombreadas: marcas Z12 e Z11 da patente."),
    ("E", 642, [(" e 2,6 vezes o do membro do próprio artigo, de 11,97 N·m: a escala do artigo corresponde a "
                 "uma carga entre duas e meia e três vezes o peso do membro.",
                 " e 2,6 vezes o do membro do próprio artigo, de 11,97 N·m."),
                ("2,94 vezes a adotada aqui. Nela, a AWM valeria 31,06 N·m na horizontal, 2,9 vezes",
                 "2,94 vezes a adotada aqui; nela, a AWM valeria 2,9 vezes"),
                ("o mesmo R², e a rigidez e as forças crescem na mesma razão, com k", "o mesmo R², com k"),
                ("(Tabela 26).", f"(Tabela 26). Nessa escala, a AASM passaria de {M3['art_rmin']} a "
                 f"{M3['art_rmax']} vezes o torque do peso do conjunto nos marcadores, e a assistência "
                 f"excederia o peso em toda a faixa.")]),
    ("P", 'O confronto mostra, no exoesqueleto 3, a limitação apontada por Nasr, Ferguson e McPhee '
          '(2022): o torque de um mecanismo passivo é determinado pelo ângulo, e ajustá-lo bem numa '
          'faixa implica desvio em outra. Aqui, o came dá liberdade para moldar a transmissão, e a '
          'curva da patente a usa para sustentar quase todo o peso do membro em torno da '
          'horizontal, onde a demanda é maior, à custa de deixar mais torque para o usuário nas '
          'pontas da faixa: na subida a partir do braço pendente e perto do limite de subida.'),

    # ------------------------------------------------------------------ limitações
    HR("r_lim"),
    ('K', 470),
    ("E", 471, [("O ponto morto do mecanismo situa-se", "No exoesqueleto 1, o ponto morto do mecanismo situa-se")]),
    ("E", 472, [(' e a integração da equação de movimento',
                '')]),
    ('K', 473),
    ("P", 'No exoesqueleto 2, a principal ressalva é a diferença de forma entre o modelo e a '
          'Figura 16 da patente: o s_{0} identificado pelo espaçamento entre as curvas não depende '
          'dessa forma, mas a distribuição angular do torque calculado, sim. O torque em N·m é um '
          'cenário, e não uma medida: a patente não publica a rigidez do elástico nem a escala da '
          'ordenada, e K = K_{40} vem da alegação comercial de 40% de assistência (SUITX, [202-]), '
          'sem verificação independente. As comparações angulares com a patente dependem da '
          'hipótese de eixo da articulação 20 no centro do ombro e barra 18 fixa no tronco, e o '
          'trecho abaixo da transição depende da posição e do raio de contato do elemento 78. As '
          'grandezas medidas no CAD não têm conferência independente, e os resultados referem-se '
          'ao membro de referência, num modelo plano.'),
    ("P", 'No exoesqueleto 3, a principal ressalva é a escala: a ordenada da Figura 16 da US '
          '9.737.374 B2 não tem unidade, e o torque em N·m e a rigidez k supõem que a AWM seja o '
          'momento do peso do membro de referência, sem ferramenta na mão e sem o apoio de braço; '
          'na escala do artigo de Okabe, Brittes e Brito (2026), 2,94 vezes maior, a assistência '
          'excederia o peso. A curva fixa só o nível da força da mola: k e x_{0} foram '
          'identificados juntos, pela forma da curva, e não medidos. Os marcadores, que são os '
          'dados da patente, foram lidos no mesmo traçado digitalizado da curva, e a incerteza '
          'dessa leitura foi estimada só pelos símbolos encontrados na imagem e pelo fechamento RM '
          '= AASM + AWM.'),
    ("P", 'A curva calculada depende do giro do came em relação à primária, em que as Figuras 14C '
          'e 14D da patente discordam em 15,5°. Com o came girado de −49°, o ajuste melhora e as '
          'zonas ficam dentro das marcas da patente; a montagem de dois furos no sentido horário, a '
          '1,6° desse giro, dá o mesmo R^{2}, e as montagens supõem na polia os furos medidos nas '
          'figuras. Com a ancoragem 562 na posição '
          'do CAD, o braço não sobe além de Θ = 22,0°, enquanto a curva da patente vai até 30°, e '
          'os três últimos marcadores ficam fora dos ajustes. Abaixo de Θ = −75°, inclusive na '
          'pose da Figura 14D, o torque do modelo é extrapolado com a mola ajustada na faixa da '
          'curva, e a posição de repouso calculada depende dessa extrapolação.'),
    ('K', 647),
    ("E", 648, [(" e limitam-se à análise estática", ", num modelo plano")]),
]

# ====================================================================== capítulo 5, fundido por assunto
# a pedido do autor (15/11), a conclusão segue os assuntos dos capítulos 3 e 4, com os três
# exoesqueletos em cada seção; a comparação entre eles fecha as seções de identificação e de
# confronto, e as recomendações de continuidade viram uma seção só
CONCLUSOES = [
    ("c_form", "Formulação dos modelos"),
    ("c_ident", "Identificação dos parâmetros e reprodução das curvas das patentes"),
    ("c_varr", "Varredura paramétrica"),
    ("c_conf", "Confronto com o torque gravitacional"),
    ("c_obj", "Objetivos e alcance dos resultados"),
    ("c_fut", "Sugestões para trabalhos futuros"),
]
_C = dict(CONCLUSOES)


def HC(chave):
    return ("H", "5", chave, _C[chave])


ALIAS.update({"5.1": None, "5.2": None, "5.3": None, "5.4": "c_conf"})

CAP5 = [
    ('K', 656),
    ("P", 'Este trabalho reconstruiu, a partir da documentação de patente, três mecanismos passivos '
          'de apoio ao braço, o gerador de torque da US 9.889.554 B2, o dispositivo da EP 3 504 033 '
          'B1 e o mecanismo de came da US 9.737.374 B2, e formulou para cada um um modelo estático '
          'do torque que ele entrega em função do ângulo, com a cinemática resolvida em forma '
          'fechada e cada etapa conferida por verificações internas de consistência. As conclusões '
          'seguem os assuntos dos capítulos 3 e 4, com os três exoesqueletos em cada seção.'),

    HC("c_form"),
    ("P", 'No exoesqueleto 1, o princípio dos trabalhos virtuais mostrou-se o critério decisivo na '
          'formulação: revelou que a extensão da mola deve acompanhar o caminho completo do cabo, '
          'ℓ = s − Rψ, e não apenas o vão livre, que violava a conservação de energia com resíduo '
          'de 1,71 mm/rad, e distinguiu o braço de momento perpendicular, limitado a 22,919 mm, da '
          'distância do pivô ao ponto de tangência, próxima de 283 mm, cuja confusão '
          'superestimaria o torque por um fator superior a 12.'),
    ("P", 'Nos exoesqueletos 2 e 3, as mesmas verificações fecham. No 2, as relações de circuito '
          'dos dois regimes e o princípio dos trabalhos virtuais têm resíduos de até 5,7 × '
          '10^{−14} mm e 5,0 × 10^{−8} mm/rad; no 3, as relações do circuito têm resíduos de até '
          '5,9 × 10^{−4} mm contra o CAD e entre as duas formas do braço de momento, e o '
          'princípio dos trabalhos virtuais, diferença relativa de 1,8 × 10^{−5}.'),
    ("E", 677, [('A pose do CAD é a da Figura 14D, o ponto de ancoragem do CAD fica a menos de 1 '
                'mm do desenhado, e as peças do apoio de braço concordam com o desenho: as polias '
                'nos pinos, o came com o giro da figura e a mola sobre a mola 636. O mecanismo '
                'molda',
                'No exoesqueleto 3, o mecanismo molda')]),

    HC("c_ident"),
    ("E", 661, [("Com os parâmetros congelados", "No exoesqueleto 1, com os parâmetros congelados")]),
    ("P", 'No exoesqueleto 2, o espaçamento entre as três curvas da Figura 16 da patente determina '
          'os comprimentos de referência do elástico sem depender da escala da ordenada, da '
          'rigidez, do braço de momento ou do torque do peso: 311,15 mm na curva pontilhada, '
          '300,75 mm na tracejada e 291,96 mm na contínua. O fim da curva pontilhada, de '
          'pré-tensão quase nula, confirma o resultado de forma independente, e o início das '
          'curvas, perto de 14°, fica a 0,9° do contato calculado com o elemento de encosto sobre '
          'o eixo, em 13,35°, configuração preferida pela patente. A forma do torque prevista com '
          'a geometria do CAD e o peso do membro humano, contudo, não reproduz as curvas da '
          'patente: o fator comum às três curvas difere do previsto por um fator que vai de 0,26 '
          'em 20° a 2,94 em 165°, normalizado em 90°. Como o s implícito na figura concorda com o '
          'do CAD, a diferença vem, mais provavelmente, do torque do peso usado pela patente para '
          'formar a razão ou da definição da ordenada, que a patente não permite separar, e a '
          'rigidez não é identificável pela figura.'),
    ("P", f'No exoesqueleto 3, com o giro do came desenhado, uma mola linear reproduz a forma da '
          f'curva AASM com R^{{2}} = 0,901, e o ajuste refeito só nos marcadores que a patente '
          f'desenha dá R^{{2}} = {M3["d_r2"]}. A rigidez não é identificável pela AASM sozinha, que '
          f'não tem unidade, mas a AWM da própria patente, igualada ao peso do membro de '
          f'referência, fixa a escala. Nela, k = 0,492 N/mm, e a mola trabalha de 158 a 114 N. A '
          f'curva e os marcadores fixam esse nível de força, mas não separam k de x_{{0}}: com o '
          f'R^{{2}} a menos de {M3["tol_r2"]} do máximo, x_{{0}} vai de {M3["pc_x0a"]} a {M3["pc_x0b"]} '
          f'mm, e a força na pose, só de {M3["pc_fa"]} a {M3["pc_fb"]} N. O resíduo tem três trechos de '
          f'sinal alternado, e a mola linear não alcança o patamar da AASM; a RM, que varia três '
          f'vezes menos, é reproduzida com R^{{2}} de só {M3["rmr_r2"]}.'),
    ("E", 684, [(" com R2 de 0,99839", ""),
                (", mas sua forma não é reproduzida pelo modelo do CAD, e o torque", ", mas o torque"),
                (" molda o torque pelo came, cujo giro em relação à primária é o parâmetro mais sensível, e chega",
                 " chega"),
                (", sob a hipótese de que ela seja o peso do membro de referência.", "."),
                ("Os três dispositivos diferem", "Os três dispositivos diferem, assim,")]),

    HC("c_varr"),
    ("E", 662, [("A varredura de h com K congelado", "No exoesqueleto 1, a varredura de h com K congelado")]),
    ("E", 672, [("As relações de circuito dos dois regimes e o princípio dos trabalhos virtuais foram "
                 "verificados com resíduos de até 5,7 × 10−14 mm e 5,0 × 10−8 mm/rad. ", ""),
                ("Com ", "No exoesqueleto 2, com ")]),
    ("P", f'No exoesqueleto 3, a varredura do giro do came mostrou que, girado de −49°, ele '
          f'reproduz a curva com R^{{2}} = 0,953, e as zonas Z11 e Z12 do modelo ficam dentro das '
          f'marcas da Figura 16 da US 9.737.374 B2. Os cinco furos em torno do pino 572 permitem '
          f'nove montagens do came; a de dois furos no sentido horário, a −50,6°, reproduz a curva '
          f'com R^{{2}} = 0,953, a 1,6° do melhor giro, e mantém R^{{2}} = {M3["df_r2"]} nos '
          f'marcadores, onde só as montagens horárias admitem uma mola linear. A curva da patente '
          f'parece corresponder a outra montagem do came, e a ancoragem desenhada limita a subida a '
          f'Θ = 22,0°, contra 30° na curva.'),

    HC("c_conf"),
    ("E", 663, [(" O resultado quantifica o compromisso de um mecanismo passivo de torque fixo por ângulo, que "
                 "favorece o trabalho acima da cabeça.", ""),
                ("No confronto com o torque gravitacional do conjunto braço-exoesqueleto, cujo pico de",
                 "No exoesqueleto 1, o torque gravitacional do conjunto braço-exoesqueleto tem pico de"),
                (" ocorre a 89,4° de elevação, as curvas normalizadas", " a 89,4° de elevação, e as curvas normalizadas")]),
    ("P", 'No exoesqueleto 2, sob a hipótese de assistência de 40% do torque do peso em 90°, K = '
          '2,550 N/mm, e o torque atinge 4,379 N·m em 79,1°, dentro da faixa de 70° a 120° em que '
          'a patente prefere a força máxima. Acima de 83,74°, a forma normalizada do elástico fica '
          'abaixo da do peso, com diferença de até −0,272 em 139,2°.'),
    ("P", f'No exoesqueleto 3, o apoio de braço tem 0,796 kg e acrescenta 9% ao torque do peso do '
          f'membro com o braço na horizontal, onde a AASM sustenta 96% do peso do membro e 89% do '
          f'peso do conjunto. Nos marcadores, a AASM chega a {M3["ra_max_pct"]}% do torque do braço '
          f'que a própria patente desenha, passa de 90% dele de Θ = {M3["a90_ini"]}° a '
          f'{M3["a90_fim"]}° e cobre de {M3["rc_min_pct"]}% a {M3["rc_max_pct"]}% do peso do conjunto; as formas quase '
          f'coincidem perto da horizontal, com o pico da patente {M3["defas_aasm"]}° acima do do '
          f'peso, e a sobra cresce nas pontas da faixa. Integrada na faixa da curva, a AASM realiza '
          f'{M3["w_aasm_pct"]}% do trabalho do peso do conjunto, e a mola adotada devolve '
          f'{M3["e_pct"]}% da energia que o peso exige da pose ao limite de subida. Com o braço quase '
          f'pendente, na pose da Figura 14D, o modelo extrapolado dá {M3["p14d_rmod"]} vezes o peso e '
          f'o iguala em Θ = {M3["ca_eq"]}°, que seria, no modelo, a posição de repouso do conjunto; na pose da Figura 14C, a '
          f'patente e o modelo sustentam {M3["p14c_raasm_pct"]}% do peso. A escala de 30 N·m do artigo '
          f'de Okabe, Brittes e Brito (2026) é 2,9 vezes maior, e nela a assistência excederia o '
          f'peso em toda a faixa.'),
    ("E", 685, [("O pico de assistência fica acima do pico gravitacional no primeiro, 8,1° (97,5° contra "
                 "89,4°), e abaixo no segundo, 10,7° (79,1° contra 89,8°);",
                 "Comparados os três, o pico de assistência fica 8,1° acima do pico gravitacional no "
                 "primeiro e 10,7° abaixo no segundo;")]),

    HC("c_obj"),
    ("E", 664, [('O objetivo geral foi atingido para este dispositivo na parte estática, e a '
                'extensão à dinâmica multicorpos ficou preparada, com o procedimento da seção '
                '3.1.13, mas não foi executada.',
                'No exoesqueleto 1, o objetivo geral foi atingido.'),
               (' Os objetivos f e g, referentes à equação de movimento e ao acoplamento com o '
                'MBDyn, não foram executados.',
                '')]),
    ("E", 673, [('Dos objetivos acrescentados para esse dispositivo, o item h foi cumprido na parte '
                 'estática, com três ressalvas',
                'No exoesqueleto 2, dos objetivos acrescentados, o item f foi cumprido, com três ressalvas'),
               ('O item i foi cumprido',
                'O item g foi cumprido'),
               (' As etapas dinâmicas não foram executadas, pelas razões da seção 3.2.13.',
                '')]),
    ("E", 681, [('Dos objetivos acrescentados para esse dispositivo, o item j foi cumprido',
                'No exoesqueleto 3, dos objetivos acrescentados, o item h foi cumprido'),
               ('O item k foi cumprido na parte estática, com a ressalva',
                'O item i foi cumprido, com a ressalva'),
               ('o objetivo geral foi atingido na parte estática; as etapas dinâmicas não foram '
                'executadas, pelas razões da seção 3.3.13.',
                'o objetivo geral foi atingido.')]),
    ("E", 686, [("Nem todos os resultados dependem dessas hipóteses.",
                 "Nem todos os resultados dependem dessas hipóteses de escala."),
                ("Dependem dela os valores em N·m: no segundo dispositivo, a rigidez K40, fixada pela hipótese "
                 "de assistência de 40% em 90°, e, no terceiro, a escala que iguala a AWM ao peso do membro de "
                 "referência; no primeiro, o torque permanece em unidade da patente.",
                 "Dependem dela os valores em N·m.")]),
    ("P", 'Por fim, os resultados deste trabalho referem-se a três dispositivos, ao indivíduo de '
          'referência adotado e ao membro superior estendido sem ferramenta na mão, e limitam-se '
          'à análise estática. A generalização a outros percentis antropométricos, a outras '
          'configurações de cotovelo e à presença de carga na mão demanda a reexecução do '
          'procedimento com os parâmetros correspondentes.'),

    HC("c_fut"),
    ("P", 'Nos três dispositivos, a lacuna principal é a escala do torque. Para o exoesqueleto 1, '
          'recomenda-se obter um dado independente que a fixe, como a especificação de uma mola '
          'comercial compatível, e representar a protuberância responsável pela zona neutra; para '
          'o exoesqueleto 2, obter a curva de força e extensão do elemento elástico, que fixaria K '
          'e a escala do torque; e, para o exoesqueleto 3, medir a rigidez e o comprimento livre '
          'da mola e o giro do came na peça real, que fixariam a escala, a divisão entre rigidez e '
          'alongamento e a montagem do came.'),
]

REFERENCIAS = [("K", 687, 732)]      # as não citadas saem na montagem

PLANO = CAP1 + CAP2 + CAP3 + CAP4 + CAP5 + REFERENCIAS

# resumo e abstract: os da versão revisada, sem a frase das etapas dinâmicas
FRASES_FORA_DO_RESUMO = (
    " As etapas dinâmicas, pela formulação de Lagrange e no MBDyn, dependem de um dado independente que "
    "fixe a escala do torque e não foram executadas.",
    " The dynamic steps, through the Lagrange formulation and in MBDyn, depend on independent data that "
    "fix the torque scale and were not carried out.",
)

# termos que não podem aparecer no documento condensado (pedido do autor)
PROIBIDOS = ("MBDyn", "Lagrange", "etapa dinâmica", "etapas dinâmicas", "simulação dinâmica",
             "equação de movimento", "equações de movimento", "Apêndice", "APÊNDICE")
