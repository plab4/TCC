"""
Plano da versão condensada para a defesa (até 70 páginas), montada por
tcc/gerar_condensado.py a partir do documento longo revisado.

Decisões do autor que o plano segue:
- até 80 páginas, da capa ao fim;
- base: o arquivo do autor de 13/11/2026, que é o documento longo sem a seção 2.6, as
  seções 3.x.12 e 3.x.13, as comparações 3.4 e 4.4, as verificações 4.2.3 e 4.3.3, o
  apêndice e alguns parágrafos (aberturas das seções, trechos dos capítulos 2, 4 e 5);
- metodologia fundida por tópico: cada seção do capítulo 3 é uma etapa do procedimento,
  com os três exoesqueletos em sequência; os capítulos 4 e 5 seguem por exoesqueleto;
- as seções 4.x.6 a 4.x.9 (comportamento, varredura, confronto e limitações) ficam;
- saem as tabelas longas de pontos extraídos (Tabelas 5 e 15 do documento longo);
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
TOPICO = {1: "t_cad", 2: "t_iner", 3: "t_conv", 4: "t_fech", 5: "t_braco", 6: "t_mola", 7: "t_morto",
          8: "t_grav", 9: "t_ptv", 10: "t_ident", 11: "t_varr", 12: "t_verif", 13: None, 14: "t_verif"}
ALIAS = {"2.6": None, "3.4": None, "4.4": None, "4.2.3": "t_verif", "4.3.3": "t_verif"}
for _e in "123":
    ALIAS.update({f"3.{_e}.{_k}": _t for _k, _t in TOPICO.items()})

# títulos dos tópicos do capítulo 3
TOPICOS = [
    ("t_cad", "Reconstrução geométrica em CAD"),
    ("t_iner", "Parâmetros inerciais e transporte ao eixo"),
    ("t_conv", "Referenciais e convenções angulares e de sinal"),
    ("t_fech", "Equação de fechamento do circuito vetorial"),
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


# título do trabalho na versão para a defesa: só "Modelagem", por decisão do autor, porque o
# texto ficou só com a parte estática
TITULO_LONGO = "Modelagem e simulação de mecanismos passivos de apoio ao braço"
TITULO = "Modelagem de mecanismos passivos de apoio ao braço"

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
               "exoesqueletos 1, 2 e 3.", " No restante do texto, eles são chamados de exoesqueletos 1, 2 e 3.")]),
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
    ("K", 20),
    ("E", 21, [("h) aplicar", "f) aplicar")]),
    ("E", 22, [("i) identificar", "g) identificar")]),
    ("K", 23),
    ("E", 24, [("j) reconstruir", "h) reconstruir")]),
    ("E", 25, [("k) obter", "i) obter")]),
    ("K", 26),
    ("E", 27, [("base quantitativa — algo que", "base quantitativa, algo que")]),
    ("E", 28, [("A escolha de ferramentas livres, Python e MBDyn, torna o modelo reprodutível por outros "
                "grupos e extensível a sistemas multicorpos mais completos.",
                "A implementação em Python, ferramenta livre, torna o modelo reprodutível por outros grupos.")]),
    ("K", 29),
]

# ====================================================================== capítulo 2
# cortes do autor: a última frase do primeiro parágrafo de 2.4 (Palazzi), os parágrafos 48 (Nasr) e
# 49 (preferências da EP), a seção 2.6 e o parágrafo 73 (curvas da EP em 2.10)
CAP2 = [
    ("K", 30, 32),
    ("E", 33, [("linha dos ombros — faixa angular", "linha dos ombros, faixa angular")]),
    ("E", 34, [("braço–antebraço", "braço-antebraço")]),
    ("K", 35, 37),
    ("E", 38, [("projeto do mecanismo — circunstância", "projeto do mecanismo, circunstância")]),
    ("K", 39, 45),
    ("E", 46, [(" Palazzi et al. (2022) mostram, em um exoesqueleto balanceado por gravidade, redução de 89% "
                "no torque de pico do ombro quando esse ajuste é bem resolvido.", "")]),
    ("K", 47),
    ("K", 50, 53),
    ("K", 58),
    ("E", 59, [("mola–cabo–polia", "mola-cabo-polia")]),
    ("K", 60, 67),
    ("E", 68, [("O cálculo do torque gravitacional e das equações de movimento pressupõe",
                "O cálculo do torque gravitacional e a composição inercial do conjunto pressupõem")]),
    ("E", 69, [("que descreve a resistência à aceleração angular e comparece exclusivamente na análise dinâmica.",
                "que descreve a resistência à aceleração angular e não participa do torque estático.")]),
    ("K", 70, 71),
    ("E", 72, [("quanto à origem — medida, de literatura, identificada, derivada ou assumida — de modo que",
                "quanto à origem (medida, de literatura, identificada, derivada ou assumida), de modo que")]),
    ("K", 74),
    ("E", 75, [("construída a partir da documentação pública de patente e conduzida do equilíbrio estático "
                "até a dinâmica multicorpos.",
                "construída a partir da documentação pública de patente.")]),
]

# ====================================================================== capítulo 3, fundido por tópico
CAP3 = [
    ("K", 76),
    ("E", 77, [("Ele foi aplicado, na parte estática, a três mecanismos: o gerador de torque da US 9.889.554 B2 "
                "(seções 3.1, 4.1 e 5.1), o dispositivo da EP 3 504 033 B1 (seções 3.2, 4.2 e 5.2) e o mecanismo "
                "de came da US 9.737.374 B2 (seções 3.3, 4.3 e 5.3). As seções 3.1.9, 3.2.9 e 3.3.9 formulam os "
                "três modelos estáticos pelo princípio dos trabalhos virtuais, e as seções 3.4, 4.4 e 5.4 "
                "comparam os três.",
                "Ele foi aplicado a três mecanismos: o gerador de torque da US 9.889.554 B2 (exoesqueleto 1), o "
                "dispositivo da EP 3 504 033 B1 (exoesqueleto 2) e o mecanismo de came da US 9.737.374 B2 "
                "(exoesqueleto 3). Este capítulo segue as etapas do procedimento, e cada seção trata dos três "
                "mecanismos, nessa ordem; os resultados de cada um estão nas seções 4.1, 4.2 e 4.3, e a seção "
                "5.4 compara os três.")]),
    ("K", 78),
    ("E", 79, [("As seções 3.1, 3.2 e 3.3 seguem a mesma ordem, e as subseções de mesmo número tratam da mesma "
                "etapa; quando uma etapa não se aplica a um mecanismo ou não pôde ser concluída com os dados "
                "disponíveis, a própria subseção registra o motivo. Cada seção tem notação própria, e um mesmo "
                "símbolo pode ter significados diferentes em seções diferentes.",
                "Cada mecanismo tem notação própria, definida no trecho que trata dele em cada seção: um mesmo "
                "símbolo, como R, C, φ, β ou s, pode ter significados diferentes de um mecanismo para outro.")]),
    ("E", 81, [(", e o momento de inércia de cada corpo é levado ao eixo de rotação pelo teorema de Steiner, "
                "IO = Icm + M d2", "")]),

    # ------------------------------------------------------------------ 3.1 reconstrução em CAD
    H("t_cad"),
    ("E", 86, [("A geometria do mecanismo foi reconstruída",
                "No exoesqueleto 1, a geometria do mecanismo foi reconstruída")]),
    ("K", 87),
    ("E", 194, [("A reconstrução parte da arquitetura descrita na patente. A EP 3 504 033 B1 descreve",
                 "No exoesqueleto 2, a reconstrução parte da arquitetura descrita na EP 3 504 033 B1 "
                 "(MIZERA et al., 2023), da Ottobock, que descreve")]),
    ("K", 195, 196),
    ("E", 298, [("A reconstrução parte da arquitetura descrita na patente. Nas Figuras 14C e 14D da "
                 "US 9.737.374 B2, o chassi",
                 "No exoesqueleto 3, a reconstrução parte da arquitetura descrita na US 9.737.374 B2 "
                 "(DOYLE, 2017), da Levitate. Nas Figuras 14C e 14D dessa patente, o chassi")]),
    ("K", 299, 301),

    # ------------------------------------------------------------------ 3.2 parâmetros inerciais
    H("t_iner"),
    ("P", "Nos três modelos, o momento de inércia de cada corpo, do membro de referência e das peças do "
          "exoesqueleto, foi transportado ao eixo de rotação do braço pelo teorema de Steiner:"),
    ("K", 90),
    ("E", 91, [("em relação ao eixo da junta,", "em relação ao eixo de rotação,"),
               ("A composição foi feita em planilha,", "Nos exoesqueletos 1 e 2, a composição foi feita em planilha,"),
               ("; ele se destina à etapa dinâmica prevista na seção 3.1.13.", ".")]),
    ABRE(202, "O membro humano é o de referência (seção 3), em série a partir de O.", 2),
    ABRE(303, "O membro superior é o de referência (seção 3), alinhado ao eixo maior", 3),
    ("K", 304, 306),

    # ------------------------------------------------------------------ 3.3 convenções
    H("t_conv"),
    ("K", 80),
    ("E", 93, [("O mecanismo é tratado como plano, com origem O no eixo da junta (pivô).",
                "No exoesqueleto 1, a origem O fica no eixo da junta (pivô).")]),
    ("K", 94, 101),
    ABRE(204, "A origem O fica no eixo da articulação 20", 2),
    ("K", 205, 211),
    ABRE(308, "A origem O fica no eixo do pivô 584", 3),
    ("K", 309, 312),

    # ------------------------------------------------------------------ 3.4 fechamento
    H("t_fech"),
    ABRE(103, "A cinemática do gerador de torque é descrita", 1),
    ("K", 104, 116),
    # a nota cita a Tabela 1 por número literal no documento longo; reescrita, ela passa a ser marcada
    ("R", 117, "Nota: O é o pivô, A a ancoragem do cabo, D o centro do tambor e T o ponto de tangência. O "
               "painel da direita amplia a região do pivô, onde se distinguem o vetor B e o braço m. As "
               "componentes h e p de B estão tracejadas, e os arcos marcam os ângulos θ*, α, q e φ da Tabela "
               "1, medidos no sentido anti-horário."),
    ("K", 118, 122),
    ABRE(213, "A ancoragem A do elástico fica na barra 18", 2),
    ("K", 214, 222),
    ABRE(314, "O cabo 560 fecha um circuito vetorial", 3),
    ("K", 315, 321),

    # ------------------------------------------------------------------ 3.5 ponto de aplicação e braço
    H("t_braco"),
    ABRE(124, "O ponto em que o cabo deixa o tambor é", 1),
    ("K", 125, 130),
    ("E", 224, [("O contato não é imposto por um ângulo.",
                 "No exoesqueleto 2, o contato do elástico com o elemento 78 não é imposto por um ângulo.")]),
    ("K", 225, 235),
    ABRE(323, "O cabo 560 deixa a polia primária", 3),
    ("K", 324, 327),

    # ------------------------------------------------------------------ 3.6 elemento elástico e torque
    H("t_mola"),
    ABRE(132, "A mola é tracionada pelo cabo", 1),
    ("K", 133, 144),
    ABRE(237, "O elástico é tratado como linear", 2),
    ("K", 238, 242),
    ABRE(329, "A força da mola chega ao cabo 560 pelo par de polias.", 3),
    ("K", 330, 338),

    # ------------------------------------------------------------------ 3.7 ponto morto
    H("t_morto"),
    ABRE(146, "O torque do cabo se anula quando", 1),
    ("K", 147, 150),
    ("E", 244, [("Pela Equação", "No exoesqueleto 2, pela Equação")]),
    ("K", 245, 246),
    ABRE(340, "O braço de momento ma se anula", 3),
    ("K", 341, 342),

    # ------------------------------------------------------------------ 3.8 torque gravitacional
    H("t_grav"),
    ("P", "O torque do peso de cada conjunto é calculado de forma independente do mecanismo, em N·m, unidade "
          "física, e as comparações usam o seu módulo, τ_{g}."),
    ABRE(152, "O torque estático do peso do conjunto braço-exoesqueleto", 1),
    ("K", 153, 154),
    ABRE(248, "O conjunto que gira com o braço tem o centro de massa", 2),
    ("K", 249, 250),
    ABRE(344, "O conjunto que gira com o braço reúne", 3),
    ("K", 345, 346),

    # ------------------------------------------------------------------ 3.9 trabalhos virtuais
    H("t_ptv"),
    ("P", "Nos três mecanismos, o equilíbrio estático é escrito pelo princípio dos trabalhos virtuais. Com "
          "vínculos ideais, as reações não realizam trabalho, e, num giro virtual δq do conjunto em torno de "
          "O, realizam trabalho só a força do elemento elástico, o peso do conjunto e o torque τ_{u} que o "
          "usuário aplica ao braço. O trabalho da força elástica pode ser calculado pelo momento dela em "
          "relação a O ou pela variação do comprimento do caminho do elemento elástico; a igualdade dos dois "
          "dá o braço de momento como a derivada desse comprimento em relação a q, relação que depende só da "
          "geometria e serve de verificação da cinemática."),
    ABRE(156, "O equilíbrio estático do braço pode ser escrito diretamente", 1),
    ("K", 157, 162),
    ("E", 163, [(" (seção 3.1.13)", ""),
                (" Com aceleração nula e Qnc = τu, a Equação (31) reduz-se a essa condição.", "")]),
    ABRE(252, "O equilíbrio é escrito pelo trabalho virtual num giro δq do conjunto", 2),
    ("K", 253, 256),
    ("E", 257, [(" Com aceleração nula e Qnc = τu, a equação de movimento da seção 3.2.13 reduz-se a essa "
                 "condição.", "")]),
    ABRE(348, "O equilíbrio é escrito pelo trabalho virtual num giro δq, em radianos,", 3),
    ("K", 349, 353),

    # ------------------------------------------------------------------ 3.10 dados da patente e identificação
    H("t_ident"),
    ("E", 165, [("A referência de comparação é a curva", "No exoesqueleto 1, a referência de comparação é a curva"),
                (", registrados em θ* e listados na Tabela 5 na ordem da extração.", ", registrados em θ*.")]),
    ("K", 166, 171),
    ("E", 259, [("As Figuras 16 e 17 da patente são apresentadas",
                 "No exoesqueleto 2, as Figuras 16 e 17 da EP 3 504 033 B1 são apresentadas")]),
    ("K", 260, 263),
    # a nota da figura entra na linha da fonte
    ("R", 264, "Fonte: Mizera et al. (2023), Figura 16, p. 31 do documento B1, com a página girada para a "
               "orientação de leitura."),
    ("E", 266, [(" (Tabela 15)", "")]),
    ("K", 267),
    ("E", 268, [(", e está descrita no Apêndice A.", ".")]),
    ("K", 269, 277),
    ("R", 278, "A robustez da identificação foi avaliada com outras faixas de θ_{el}, de 15° a 170°, de 25° a "
               "160° e de 40° a 150°, com ruído de 0,5 px nas duas coordenadas de cada ponto, em 500 sorteios, "
               "com o sinal de θ_{b,pose} oposto e com a abscissa da figura deslocada de ±0,93° ou espelhada; um "
               "teste sintético, com curvas montadas pelo próprio modelo a partir de valores conhecidos de "
               "s_{0}, confere a implementação."),
    ("K", 279, 285),
    ABRE(355, "A Figura 16 da US 9.737.374 B2 foi digitalizada neste trabalho", 3),
    ("K", 356, 358),

    # ------------------------------------------------------------------ 3.11 varredura paramétrica
    H("t_varr"),
    ("P", "Em cada mecanismo, o parâmetro geométrico menos certo foi varrido, com os demais congelados. A "
          "varredura é um diagnóstico, e não uma otimização: nenhum parâmetro do modelo é substituído pelo "
          "resultado, e cada valor é testado por critérios de validade física que não usam a curva da "
          "patente."),
    ABRE(173, "Para separar o que a curva extraída informa sobre h", 1),
    ("K", 174, 177),
    ("E", 287, [("O comprimento", "No exoesqueleto 2, o comprimento")]),
    ABRE(360, "O giro do came em relação à primária é a grandeza menos certa", 3),
    ("K", 361, 362),

    # ------------------------------------------------------------------ 3.12 verificações, ferramentas, delimitação
    H("t_verif"),
    ("E", 179, [("A cadeia de cálculo é conferida a cada execução do modelo",
                 "No exoesqueleto 1, a cadeia de cálculo é conferida a cada execução do modelo")]),
    ("K", 180),
    ("E", 289, [("As verificações estão na Tabela 16. São asserções",
                 "No exoesqueleto 2, as verificações são asserções")]),
    ("P", "Nesse modelo, os resíduos ficaram em até 5,7 × 10^{−14} mm nas equações de fechamento dos dois "
          "regimes e em até 5,0 × 10^{−8} mm/rad no trabalho virtual, este limitado pelo truncamento da "
          "diferença finita, e o fechamento com o comprimento medido no CAD difere dele em 1,4 × 10^{−4} mm, "
          "abaixo da resolução da medida; no teste sintético, a identificação pelo espaçamento recupera os "
          "valores de s_{0} com erro máximo de 0,074 mm."),
    ("E", 364, [("Os scripts executam as verificações da Tabela 24 (seção 4.3.3).",
                 "No exoesqueleto 3, os scripts executam verificações com tolerância declarada.")]),
    ("P", "Nesse modelo, os resíduos da cadeia de cálculo são da ordem do erro de arredondamento, como "
          "2,1 × 10^{−13} mm entre as duas formas do braço de momento, exceto o do trabalho virtual, com "
          "diferença relativa de 1,8 × 10^{−5}, limitado pelo truncamento da diferença finita, e os do "
          "fechamento com o CAD, de 5,9 × 10^{−4} mm, limitados pela resolução da medida. Nas peças do apoio "
          "de braço, as distâncias entre eixos diferem do desenho em até 1,36 mm, os ângulos em menos de 2°, "
          "e o eixo da mola passa a 3,3 mm do centro dos traços da mola 636; a hipótese de came espelhado é "
          "rejeitada pelas duas medidas do giro."),
    ("P", "Foram empregados o Autodesk Fusion, para a reconstrução geométrica e a extração das propriedades "
          "de massa dos exoesqueletos 1 e 2; uma planilha eletrônica, para o transporte de eixos e a "
          "composição inercial; e a linguagem Python, com as bibliotecas NumPy (HARRIS et al., 2020), para o "
          "cálculo vetorizado, SciPy (VIRTANEN et al., 2020), para o processamento das imagens das folhas da "
          "patente, a envoltória convexa do came e o refinamento pelo método de Brent (BRENT, 1973), e "
          "Matplotlib (HUNTER, 2007), para as figuras. A cadeia de cálculo está nos arquivos torque_model.py "
          "e torque_model_ottobock.py e nos scripts da pasta exo3, e os números e as figuras do capítulo 4 "
          "são produzidos pelos scripts tcc_resultados.py, tcc_resultados_ottobock.py e "
          "tcc_resultados_exo3.py, que não alteram parâmetro algum dos modelos."),
    ("P", "Os três modelos são planos e admitem vínculos ideais, sem atrito nas articulações, no tambor e nas "
          "polias, cabos inextensíveis e elementos elásticos lineares e sem massa. O exoesqueleto 1 não "
          "representa a protuberância que, na patente, cria a zona neutra após o ângulo de transição; o 2 "
          "admite o elemento 78 pontual e o eixo da articulação 20 no centro do ombro, com a barra 18 fixa em "
          "relação ao tronco; e o 3 toma a polia 630 no infinito e identifica a mola pela própria curva da "
          "patente, na escala fixada pela AWM. Não integram o escopo a avaliação experimental com "
          "participantes humanos, a eletromiografia, a análise de conforto e usabilidade, a fabricação e o "
          "ensaio de protótipo e o dimensionamento estrutural das peças."),
]

# figuras reduzidas: índice do bloco da imagem → fator
ESCALA_FIGURAS = {228: 0.85, 263: 0.8}

# ====================================================================== capítulo 4, por exoesqueleto
# cortes do autor: as aberturas de 4.2 e 4.3, as verificações 4.2.3 e 4.3.3, os dois últimos
# parágrafos de 4.1.7 e de 4.1.9 e a seção 4.4; saem ainda as tabelas de pontos 5 e 15
NASR = [(" e discutida na seção 2.4", ""),
        (" É também a limitação que motiva as soluções semipassivas de assistência regulável referidas na "
         "seção 2.4.", "")]
CAP4 = [
    ("K", 374),
    ("E", 375, [("; a seção 4.3, os do mecanismo de came da US 9.737.374 B2; e a seção 4.4 compara os três.",
                 "; e a seção 4.3, os do mecanismo de came da US 9.737.374 B2. A comparação entre os três está "
                 "na seção 5.4.")]),
    ("K", 376),
    ("E", 377, [(" As etapas dinâmicas da seção 3.1.13 não foram executadas.", "")]),
    ("K", 378, 386),
    ("E", 387, [("O momento de inércia destina-se à etapa dinâmica, não executada, e não participa do "
                 "cálculo do torque estático.",
                 "O momento de inércia não participa do cálculo do torque estático.")]),
    ("K", 388),
    ("E", 389, [("A Tabela 5 reúne os 29 pontos extraídos da curva da patente, na ordem da extração, com os "
                 "ângulos correspondentes nas convenções da seção 3.1.3, o torque calculado pelo modelo com os "
                 "parâmetros congelados e o resíduo. Os pontos cobrem",
                 "Os 29 pontos extraídos da curva da patente cobrem")]),
    ("K", 394, 423),
    ("E", 424, [("Resíduo estruturado dessa natureza indica", "Resíduo estruturado dessa natureza sugere")]),
    ("K", 425, 455),
    ("K", 458, 467),
    ("E", 468, NASR),
    ("K", 469, 471),
    ("E", 472, [(" e a integração da equação de movimento", "")]),
    ("K", 473),

    ("K", 476),
    ("K", 478, 490),
    ("E", 491, [(" (Tabela 15)", "")]),
    ("K", 502, 503),
    ("E", 504, [(" A Tabela 31 e os detalhes estão no Apêndice A.", "")]),
    ("K", 505, 514),
    ("E", 515, [(" (Tabela 32, no Apêndice A)", "")]),
    ("K", 516, 545),
    ("E", 546, [(" da Tabela 31, no Apêndice A.", " testadas na identificação.")]),
    ("K", 547, 558),
    ("E", 559, [("a limitação discutida na seção 2.4 (NASR; FERGUSON; McPHEE, 2022)",
                 "a limitação apontada por Nasr, Ferguson e McPhee (2022)")]),
    ("K", 560, 562),
    ("E", 563, [("da ordenada da Figura 16, e K", "da ordenada da Figura 16 da patente, e K")]),
    ("K", 564, 565),

    ("K", 566),
    ("K", 568, 588),
    ("K", 595, 626),
    ("E", 627, [("quando a Figura 16 foi gerada.", "quando a Figura 16 da US 9.737.374 B2 foi gerada.")]),
    ("K", 628, 648),
]

# ====================================================================== capítulo 5
CAP5 = [
    ("K", 656, 663),
    ("E", 664, [("O objetivo geral foi atingido para este dispositivo na parte estática, e a extensão à "
                 "dinâmica multicorpos ficou preparada, com o procedimento da seção 3.1.13, mas não foi "
                 "executada.",
                 "O objetivo geral foi atingido para este dispositivo."),
                (" Os objetivos f e g, referentes à equação de movimento e ao acoplamento com o MBDyn, não "
                 "foram executados.", "")]),
    ("E", 665, [("; representar a protuberância responsável pela zona neutra; e, com o torque em unidade física, "
                 "executar as etapas dinâmicas pela formulação de Lagrange e no MBDyn.",
                 " e representar a protuberância responsável pela zona neutra.")]),
    ("K", 666, 672),
    ("E", 673, [("o item h foi cumprido na parte estática, com três ressalvas",
                 "o item f foi cumprido, com três ressalvas"),
                ("O item i foi cumprido", "O item g foi cumprido"),
                (" As etapas dinâmicas não foram executadas, pelas razões da seção 3.2.13.", "")]),
    ("K", 675, 680),
    ("E", 681, [("o item j foi cumprido", "o item h foi cumprido"),
                ("O item k foi cumprido na parte estática, com a ressalva", "O item i foi cumprido, com a ressalva"),
                ("o objetivo geral foi atingido na parte estática; as etapas dinâmicas não foram executadas, "
                 "pelas razões da seção 3.3.13.",
                 "o objetivo geral foi atingido.")]),
    ("K", 683, 686),
    # parágrafo do autor, levado de 4.1.9 para o fim da conclusão
    ("P", "Por fim, os resultados deste trabalho referem-se a três dispositivos, ao indivíduo de referência "
          "adotado e ao membro superior estendido sem ferramenta na mão, e limitam-se à análise estática. A "
          "generalização a outros percentis antropométricos, a outras configurações de cotovelo e à presença "
          "de carga na mão demanda a reexecução do procedimento com os parâmetros correspondentes."),
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
