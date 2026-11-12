"""
Plano da versão condensada para a defesa (até 70 páginas), montada por
tcc/gerar_condensado.py a partir do documento longo revisado.

Decisões do autor que o plano segue:
- o limite de páginas vale para o documento inteiro, da capa ao fim;
- o que sai, sai de vez (não há apêndice nem material suplementar);
- os três exoesqueletos ficam enxutos, com o mesmo peso;
- os capítulos 1 e 2 também podem ser enxugados;
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

# seções do documento longo → seção da versão condensada (None: saiu)
ALIAS = {"2.6": None}
for _e in "123":
    ALIAS.update({
        f"3.{_e}.1": f"m{_e}_cad", f"3.{_e}.2": f"m{_e}_cad",
        f"3.{_e}.3": f"m{_e}_fech", f"3.{_e}.4": f"m{_e}_fech",
        f"3.{_e}.6": f"m{_e}_torque", f"3.{_e}.7": f"m{_e}_torque",
        f"3.{_e}.8": f"m{_e}_grav", f"3.{_e}.9": f"m{_e}_grav",
        f"3.{_e}.10": f"m{_e}_ident",
        f"3.{_e}.11": f"m{_e}_verif", f"3.{_e}.12": f"m{_e}_verif",
        f"3.{_e}.13": None, f"3.{_e}.14": f"m{_e}_verif",
        f"4.{_e}.1": f"r{_e}_geo", f"4.{_e}.3": f"r{_e}_geo",
        f"4.{_e}.2": f"r{_e}_ident", f"4.{_e}.4": f"r{_e}_ident", f"4.{_e}.5": f"r{_e}_ident",
        f"4.{_e}.6": f"r{_e}_comp", f"4.{_e}.7": f"r{_e}_comp",
        f"4.{_e}.8": f"r{_e}_grav", f"4.{_e}.9": f"r{_e}_lim",
    })
# o que não segue a regra acima
ALIAS.update({
    "3.1.5": "m1_torque", "3.2.5": "m2_fech", "3.3.5": "m3_torque",
    "4.2.6": "r2_ident", "4.2.7": "r2_comp", "4.2.8": "r2_comp",
    "4.2.9": "r2_grav", "4.2.10": "r2_lim",
})

T_CAD = "Reconstrução geométrica e propriedades de massa"
T_FECH = "Convenções e fechamento do circuito"
T_GRAV = "Torque gravitacional e trabalho virtual"
T_IDENT = "Dados da patente e identificação dos parâmetros"
T_VERIF = "Varredura paramétrica e verificações"
R_GEO = "Geometria, propriedades de massa e verificações"
R_IDENT = "Identificação e ajuste à curva da patente"
R_COMP = "Comportamento do mecanismo e varredura paramétrica"
R_GRAV = "Confronto com o torque gravitacional"
R_LIM = "Limitações dos resultados"

# ====================================================================== capítulo 1
CAP1 = [
    ("K", 0, 1),
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
    ("E", 8, [("Nesta etapa, o procedimento foi aplicado", "O procedimento foi aplicado")]),
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
CAP2 = [
    ("K", 30, 32),
    ("E", 33, [("linha dos ombros — faixa angular", "linha dos ombros, faixa angular")]),
    ("E", 34, [("braço–antebraço", "braço-antebraço")]),
    ("K", 35, 37),
    # 38 (instrumentação dos dispositivos ativos) sai
    ("K", 39, 51),
    # 52 (estratégias de compensação de desalinhamento) sai
    ("K", 53),
    # 54 a 57: seção 2.6, modelagem dinâmica multicorpos, sai
    ("K", 58),
    ("E", 59, [("mola–cabo–polia", "mola-cabo-polia")]),
    ("K", 60),
    # 61 (variantes das Figuras 1 e 18 da patente) sai; está em 3.2.1
    ("K", 62, 67),
    ("E", 68, [("O cálculo do torque gravitacional e das equações de movimento pressupõe",
                "O cálculo do torque gravitacional e a composição inercial do conjunto pressupõem")]),
    ("E", 69, [("que descreve a resistência à aceleração angular e comparece exclusivamente na análise dinâmica.",
                "que descreve a resistência à aceleração angular e não participa do torque estático.")]),
    ("K", 70, 71),
    ("E", 72, [("quanto à origem — medida, de literatura, identificada, derivada ou assumida — de modo que",
                "quanto à origem (medida, de literatura, identificada, derivada ou assumida), de modo que")]),
    ("K", 73, 74),
    ("E", 75, [("construída a partir da documentação pública de patente e conduzida do equilíbrio estático "
                "até a dinâmica multicorpos.",
                "construída a partir da documentação pública de patente.")]),
]

# ====================================================================== capítulo 3
CAP3_ABERTURA = [
    ("K", 76),
    ("E", 77, [("Ele foi aplicado, na parte estática, a três mecanismos", "Ele foi aplicado a três mecanismos"),
               ("As seções 3.1.9, 3.2.9 e 3.3.9 formulam os três modelos estáticos pelo princípio dos "
                "trabalhos virtuais, e as seções 3.4, 4.4 e 5.4 comparam os três.",
                "Em cada um, o equilíbrio é escrito pelo princípio dos trabalhos virtuais, e as seções 3.4, "
                "4.4 e 5.4 comparam os três.")]),
    ("K", 78, 81),
    ("E", 82, [(" As etapas dinâmicas, pela formulação de Lagrange e no MBDyn, foram previstas para os três "
                "mecanismos e não foram executadas.", "")]),
    ("P", "Os modelos em CAD dos exoesqueletos 1 e 2 foram feitos no Autodesk Fusion, e a composição "
          "inercial desses dois, em planilha eletrônica. Os cálculos estão em Python, com as bibliotecas "
          "NumPy (HARRIS et al., 2020), para o cálculo vetorizado, Matplotlib (HUNTER, 2007), para as "
          "figuras, e SciPy (VIRTANEN et al., 2020), usada no exoesqueleto 3 para o processamento das "
          "imagens das folhas da patente, a envoltória convexa do came e o limite de subida, este pelo "
          "método de Brent (BRENT, 1973)."),
]

EXO1_M = [
    ("K", 83, 84),
    ("H", "3.1", "m1_cad", T_CAD),
    ("P", "A geometria do mecanismo foi reconstruída no Autodesk Fusion sobre os desenhos da patente, em "
          "especial a vista em corte do gerador de torque e o esquema simplificado que define o ângulo "
          "entre os elos e as distâncias características. Como as figuras de patente não são cotadas, o "
          "modelo foi escalado por um fator único, fixado a partir de uma estimativa de medida "
          "antropométrica. Da reconstrução saem as grandezas geométricas do mecanismo, a pose de "
          "referência, com o respectivo comprimento da mola, e a massa, a posição do centro de massa e o "
          "momento de inércia de cada peça (seção ⟦S:r1_geo⟧). Por dependerem do fator de escala, da "
          "interpretação de desenhos não cotados e do material atribuído a cada peça no CAD, essas "
          "grandezas são classificadas como medidas em CAD e são estimativas, e não dimensões ou "
          "propriedades do dispositivo comercial."),
    ("P", "O membro superior é o de referência (seção 3). Os momentos de inércia de cada corpo, do membro "
          "e das peças do exoesqueleto, foram transportados ao eixo da junta pelo teorema de Steiner, em "
          "planilha construída para recalcular o conjunto quando qualquer entrada muda. O momento de "
          "inércia não participa do torque estático do peso, que depende apenas da massa e da posição do "
          "centro de massa (seção ⟦S:m1_grav⟧)."),
    ("H", "3.1", "m1_fech", T_FECH),
    ("P", "O mecanismo é tratado como plano, com origem O no eixo da junta (pivô). A variável independente "
          "do modelo é q, o ângulo interno θ* entre os elos referido ao desenho:"),
    ("K", 94, 96),
    ("P", "em que θ_{off} = 133,017° é a calibração angular identificada (seção ⟦S:m1_ident⟧). A faixa da "
          "patente, φ_{pat} de −60° a +90,1°, corresponde a θ* de 42,917° a 193,017° e a elevação de 30° a "
          "180,1°; a elevação cresce quando θ* decresce. O torque τ do modelo é positivo no sentido "
          "anti-horário, isto é, no sentido de θ* crescente. A patente apresenta o torque do cabo positivo "
          "no sentido oposto, em que ele tende a elevar o braço; por isso, a curva calculada que se compara "
          "à da patente é −τ."),
    ("K", 103, 110),
    ("P", "A grandeza ρ é a distância da ancoragem ao centro do tambor, e a tangente existe somente se "
          "ρ > R, condição verificada em cada ponto calculado."),
    ("K", 114, 116),
    ("R", 117, "Nota: O é o pivô, A a ancoragem do cabo, D o centro do tambor e T o ponto de tangência. O "
               "painel da direita amplia a região do pivô, onde se distinguem o vetor B e o braço m. As "
               "componentes h e p de B estão tracejadas, e os arcos marcam os ângulos θ*, α, q e φ, medidos "
               "no sentido anti-horário."),
    ("H", "3.1", "m1_torque", "Braço de momento, mola e torque"),
    ("K", 124, 129),
    ("E", 130, [("(ponto morto, seção 3.1.7)", "(ponto morto)")]),
    ("K", 132, 135),
    ("P", "Entra no modelo apenas a parcela variável do enrolamento: um arco constante cancela-se na "
          "extensão da mola, porque o caminho e o comprimento de referência são calculados pela mesma "
          "expressão. O sinal do termo do arco foi fixado pelo princípio dos trabalhos virtuais (seção "
          "⟦S:m1_grav⟧). Em um mecanismo conservativo, sem atrito no tambor, o trabalho da tração no cabo "
          "iguala o do torque no elo, o que exige"),
    ("K", 137),
    ("P", "com q em radianos. A Equação (19) é verificada numericamente por diferenças finitas centradas e "
          "permite discriminar entre formulações do caminho do cabo: com o caminho igual apenas ao vão "
          "livre, ela não é satisfeita (seção ⟦S:r1_geo⟧)."),
    ("K", 139, 143),
    ("P", "A identidade τ = −F m/1000 decorre de T e A estarem sobre a mesma linha de ação, e o fator "
          "1/1000 vem dos comprimentos em milímetros. Como K é identificado contra a curva publicada, cuja "
          "ordenada não tem unidade declarada, o torque do cabo é expresso na unidade da própria curva, "
          "denotada u.p. (unidade da patente). A unidade de K é, portanto, aquela que faz K δ m/1000 "
          "resultar em u.p.; ela só seria N/mm se u.p. correspondesse a N·m, o que não pode ser afirmado "
          "com os dados disponíveis (seção ⟦S:r1_comp⟧)."),
    ("K", 146, 147),
    ("P", "A forma fechada é conferida contra a raiz de m(θ*) = 0 obtida por bissecção. Depois do ponto "
          "morto, o torque do cabo troca de sinal; o modelo não representa a protuberância que, na "
          "patente, restringe o gerador de força além do ângulo de transição (seção 2.3)."),
    ("H", "3.1", "m1_grav", T_GRAV),
    ("K", 152, 154),
    ("K", 156, 162),
    ("P", "em que τ_{u} é o torque que o usuário precisa exercer para manter o braço parado. Como τ está "
          "em u.p. e τ_{g,s} em N·m, essa soma só tem valor físico se u.p. corresponder a N·m, e a seção "
          "4.1 compara apenas a forma e os ângulos de τ e τ_{g}."),
    ("H", "3.1", "m1_ident", T_IDENT),
    ("E", 165, [("registrados em θ* e listados na Tabela 5 na ordem da extração.", "registrados em θ*.")]),
    ("K", 166, 168),
    ("P", "Com h e θ_{off} fixados, X_{pose} foi reidentificado por varredura unidimensional, em passo de "
          "0,001 mm, com K dado pela Equação (29) em cada valor. A qualidade do ajuste é avaliada pela raiz "
          "do erro quadrático médio (RMSE), pelo erro absoluto médio (MAE), pelo erro máximo e pelo "
          "coeficiente de determinação R^{2}, com o resíduo dado pelo torque calculado na convenção da "
          "patente, −τ, menos o valor extraído. O RMSE mede a aderência à curva extraída, e não a validade "
          "física. Duas formulações só são comparadas por ele depois de ambas satisfazerem as verificações "
          "físicas da seção ⟦S:m1_verif⟧; essa regra decide, no capítulo 4, a adoção do caminho completo "
          "do cabo, apesar de o caminho sem o arco produzir RMSE menor."),
    ("H", "3.1", "m1_verif", T_VERIF),
    ("K", 173, 175),
    ("P", "Da varredura derivam o valor de h de menor RMSE, os intervalos de h em que o RMSE não excede "
          "1,01 e 2 vezes o mínimo, a fronteira de tração, obtida por bissecção, e o valor de h em que o "
          "ponto morto entra na faixa de operação."),
    ("K", 179),
    ("P", "O projeto mantém, além disso, testes automatizados executados com o pytest. Eles verificam, "
          "entre outros pontos, que o torque é linear em K, que a posição da ancoragem é argumento "
          "obrigatório de toda a cadeia, que a formulação s − Rψ é a única das testadas que satisfaz o "
          "trabalho virtual e que a varredura não reidentifica K por h."),
    ("K", 189),
]

EXO2_M = [
    ("K", 190, 192),
    ("H", "3.2", "m2_cad", T_CAD),
    ("K", 194, 196),
    ("P", "Como preferência, a patente indica que nenhuma força seja aplicada até que o braço ultrapasse um "
          "ângulo em relação à vertical, com 45°, 60° ou 90° como exemplos, e que a força máxima ocorra "
          "entre 70° e 120°, de preferência em 90°. O documento não traz cotas do mecanismo nem rigidez, "
          "pré-tensão ou dimensões do elemento elástico."),
    ("K", 199, 200),
    ("K", 202),
    ("H", "3.2", "m2_fech", T_FECH),
    ("K", 204),
    ("E", 205, [("representada pelo segmento OP, de comprimento e (seção 3.2.4).",
                 "representada pelo segmento OP, de comprimento e.")]),
    ("K", 206, 210),
    ("P", "O ângulo θ_{b,pose} = 7,962° é positivo, como conferido no CAD: na pose, o braço fica acima da "
          "horizontal. O modelo é sensível a esse sinal. Com o sinal oposto, q_{0} seria −11,551° e "
          "θ_{el,pose}, 82,038°, e o contato do elástico com o elemento 78 passaria de 24,55° para 8,62°. "
          "Dois resultados sustentam o sinal adotado: sobreposto à Figura 22 da patente, o pino da alavanca "
          "do modelo fica a 1,8 mm do pino do elástico desenhado com o braço elevado e a 4,7 mm com o braço "
          "baixado, e o espaçamento entre as curvas fecha com resíduo de 0,194 mm, contra 0,406 mm com o "
          "sinal oposto (seção ⟦S:r2_ident⟧)."),
    ("E", 213, [("como na Figura 22 da patente (seção 3.2.5).", "como na Figura 22 da patente.")]),
    ("K", 214, 222),
    ("K", 224, 230),
    ("H", "3.2", "m2_torque", "Braço de momento, elástico e torque"),
    ("K", 237, 242),
    ("K", 244, 246),
    ("H", "3.2", "m2_grav", T_GRAV),
    ("K", 248, 250),
    ("K", 252, 256),
    ("P", "com τ em N·m sob a hipótese K = K_{40} (seção ⟦S:m2_ident⟧)."),
    ("H", "3.2", "m2_ident", T_IDENT),
    ("K", 259, 265),
    ("P", "Os pontos das três curvas foram extraídos neste trabalho e estão no arquivo fig16_curvas.csv. A "
          "extração dividiu a leitura vertical por 21,1311 para obter a razão em divisões da grade, manteve "
          "a abscissa sem correção e teve erro mediano de sobreposição inferior a 0,5 px; a imagem e a "
          "resolução usadas na leitura não foram registradas, e a incerteza da extração não foi avaliada "
          "de forma independente. A Figura 17 da patente não foi digitalizada."),
    ("E", 268, [("pelas razões da seção 4.2.5, e está descrita no Apêndice A.", "pelas razões da seção 4.2.5.")]),
    ("K", 269, 277),
    ("P", "A robustez da identificação foi avaliada com outras faixas de θ_{el}, de 15° a 170°, de 25° a "
          "160° e de 40° a 150°, com ruído de extração de 0,5 px, em 500 sorteios, com o sinal de "
          "θ_{b,pose} oposto e com a abscissa da figura deslocada ou espelhada, e um teste sintético, com "
          "curvas montadas pelo próprio modelo a partir de valores conhecidos de s_{0}, confere a "
          "implementação."),
    ("K", 279, 285),
    ("H", "3.2", "m2_verif", T_VERIF),
    ("K", 287),
    ("P", "As verificações são asserções executadas a cada cálculo, com tolerância declarada, que o "
          "interrompem se alguma for violada; não há um conjunto separado de testes executado com o pytest. "
          "Além das equações de fechamento e do trabalho virtual, elas conferem a continuidade na troca de "
          "regime e o caso limite p = 0, e o modelo confere ainda que o regime II ocorre exatamente para "
          "q ≤ q*, que o elemento 78 fica entre A e P na transição e que toda a cadeia depende de e_{c}. "
          "Os resultados estão na seção ⟦S:r2_geo⟧."),
    ("P", "O modelo é plano, restrito ao plano sagital, e admite elástico linear e sem massa, F = K δ, "
          "elemento 78 pontual e sem atrito e eixo da articulação 20 no centro do ombro, com a barra 18 "
          "fixa em relação ao tronco (seção ⟦S:m2_fech⟧). O torque gravitacional considera o membro de "
          "referência e o braço do exoesqueleto; a alavanca, o elemento 78 e a braçadeira não entram nele."),
]

EXO3_M = [
    ("K", 294, 296),
    ("H", "3.3", "m3_cad", T_CAD),
    ("K", 298, 301),
    ("K", 303, 306),
    ("H", "3.3", "m3_fech", T_FECH),
    ("K", 308, 309),
    ("K", 310, 312),
    ("K", 314, 321),
    ("H", "3.3", "m3_torque", "Braço de momento, came, mola e torque"),
    ("K", 323, 327),
    ("K", 329, 338),
    ("K", 340, 342),
    ("H", "3.3", "m3_grav", T_GRAV),
    ("K", 344, 346),
    ("K", 348, 353),
    ("H", "3.3", "m3_ident", T_IDENT),
    ("K", 355, 358),
    ("H", "3.3", "m3_verif", T_VERIF),
    ("K", 360, 362),
    ("E", 364, [("Os scripts executam as verificações da Tabela 24 (seção 4.3.3).",
                 "Os scripts executam as verificações cujos resultados estão na seção 4.3.3.")]),
    ("P", "O modelo é plano e admite vínculos ideais, sem atrito no pivô e nas polias, cabos inextensíveis "
          "e sem massa, polia 630 no infinito e mola linear identificada pela própria curva da patente, na "
          "escala fixada pela AWM. O giro do came vem do desenho da Figura 14D, que discorda do da 14C. O "
          "torque gravitacional considera o membro de referência, alinhado ao eixo maior e com o ombro no "
          "pivô 584, e os cinco corpos do apoio de braço; outras peças que giram com o braço não entram "
          "nele."),
]

CAP3_FIM = [("K", 369, 373)]

# ====================================================================== capítulo 4
EXO1_R = [
    ("K", 374, 376),
    ("E", 377, [(" As etapas dinâmicas da seção 3.1.13 não foram executadas.", "")]),
    ("H", "4.1", "r1_geo", R_GEO),
    ("K", 379, 380),
    ("L", 381, [1, 2, 3, 4, 5, 6, 8]),       # sem o comprimento útil do alojamento, que não entra no cálculo
    ("K", 382, 386),
    ("E", 387, [("igual ao momento de inércia no eixo da junta, conforme a Equação (1);",
                 "igual ao momento de inércia no eixo da junta, como exige o teorema de Steiner;"),
                ("O momento de inércia destina-se à etapa dinâmica, não executada, e não participa do "
                 "cálculo do torque estático.",
                 "O momento de inércia não participa do cálculo do torque estático.")]),
    ("P", "As verificações automáticas da seção ⟦S:m1_verif⟧ resultaram em resíduos da ordem do erro de "
          "arredondamento da aritmética de ponto flutuante, de no máximo 8,0 × 10^{−13} mm nas relações "
          "geométricas e de 1,3 × 10^{−11} grau no ponto morto, exceto o do trabalho virtual, de "
          "4,7 × 10^{−8} mm/rad, limitado pelo truncamento da diferença finita."),
    ("K", 399),
    ("P", "O efeito do arco é pequeno em valor absoluto: ele varia 1,862 mm na faixa de operação, contra "
          "42,435 mm de variação do caminho total (4,4%)."),
    ("H", "4.1", "r1_ident", R_IDENT),
    ("P", "Os 29 pontos extraídos da curva da patente cobrem θ* de 42,909° a 193,017°, isto é, elevação de "
          "180,1° a 30,0°, com espaçamento irregular, de 2,87° a 8,03° em θ*. O maior valor extraído, "
          "147,310 u.p., ocorre em θ* = 123,196° (elevação de 99,8°), e a média dos 29 valores é "
          "81,840 u.p. Os valores são expressos em u.p. porque a figura de origem não declara unidade "
          "(seção 2.10)."),
    ("K", 402, 407),
    ("P", "A origem de H_{CAL} = 22,701 mm, ao contrário, não pôde ser reproduzida. Numa análise "
          "complementar, em que X_{pose} e K são reidentificados para cada h, de 8 a 60 mm em passo de "
          "0,25 mm, o RMSE tem mínimo interior em h ≈ 24,0 mm, com RMSE de 1,682 u.p., X_{pose} = 38,83 mm "
          "e K = 160,46. O vale é largo: o RMSE fica abaixo de 2 vezes o mínimo de h = 19,25 a 31,00 mm, "
          "faixa em que K vai de 222,1 a 106,6; com K e a extensão na pose livres, a curva extraída não "
          "determina h."),
    ("K", 409, 410),
    ("K", 412, 419),
    ("P", "Os resíduos não se distribuem aleatoriamente. Ordenados por θ*, eles formam três zonas extensas "
          "de sinal alternado, que reúnem 25 dos 29 pontos: o modelo superestima o torque com o braço alto, "
          "acima de 155° de elevação, e entre 45° e 94°, e o subestima entre 100° e 150°. Resíduo "
          "estruturado dessa natureza indica diferença sistemática de forma entre o modelo e a curva, e "
          "não apenas dispersão de digitalização. As causas possíveis são a imprecisão da geometria "
          "reconstruída, um erro sistemático na extração ou uma diferença entre a formulação do modelo e "
          "a que gerou a figura da patente. O último ponto, em θ* = 193,017°, está além do ponto morto "
          "calculado (θ*_{pm} = 192,532°): ali o modelo prevê torque de −1,709 u.p., com sinal invertido, "
          "ao passo que a curva extraída registra 0,443 u.p., diferença coerente com a ausência, no "
          "modelo, da protuberância que mantém o torque residual aproximadamente nulo no dispositivo real."),
    ("H", "4.1", "r1_comp", R_COMP),
    ("P", "Na faixa de operação, de θ* = 42,917° a 193,017°, a extensão da mola vai de 12,044 mm a "
          "54,479 mm, valor que ocorre no ponto morto, e permanece positiva: o cabo continua tracionado em "
          "todos os pontos avaliados. O comprimento livre da mola é de 53,967 mm, e a razão de 1,0095 entre "
          "a extensão máxima e o comprimento livre significa que a mola precisaria ser estendida a "
          "aproximadamente o dobro de seu comprimento livre, requisito que deve ser confrontado com dados "
          "de fabricante. O braço de momento cresce de 12,451 mm em θ* = 42,917° até o teto "
          "|OA| = 22,919 mm em θ* = 97,894°, posição em que o cabo fica perpendicular a OA, e decresce a "
          "partir daí, anulando-se no ponto morto, em θ* = 192,532° (elevação de 30,485°)."),
    ("K", 434),
    ("P", "Na varredura de h com K congelado, o menor RMSE, 1,8270 u.p. (R^{2} = 0,99840), ocorre em "
          "h = 22,735 mm, a 0,034 mm de H_{CAL}, e o RMSE não excede 1,01 vez o mínimo de h = 22,660 a "
          "22,805 mm, intervalo de 0,145 mm. Essa precisão não deve ser lida como identificação "
          "independente de h: K e X_{pose} foram identificados no próprio H_{CAL}, de modo que a "
          "proximidade entre o mínimo da varredura e H_{CAL} é esperada por construção. O resultado mostra "
          "que o trio (K, X_{pose}, H_{CAL}) é internamente consistente e que o ajuste é muito sensível a "
          "h, mas não substitui a medição da ancoragem no dispositivo real."),
    ("P", "Os critérios de fechamento e de trabalho virtual foram atendidos em todos os 10.402 valores de "
          "h, este com resíduo máximo de 7,4 × 10^{−8} mm/rad. O critério decisivo é a tração: com "
          "X_{pose} congelada, o aumento de h rebaixa a extensão mínima, que ocorre sempre em "
          "θ* = 42,917° e se anula na fronteira de tração, h = 32,886 mm. A cota do CAD, "
          "H_{CAD} = 34,785 mm, fica fora do intervalo viável: com X_{pose} congelada, o cabo afrouxaria no "
          "início da faixa, com extensão mínima de −2,257 mm, e o RMSE seria de 43,48 u.p. "
          "(R^{2} = 0,093). A Tabela 12 reúne os valores notáveis de h."),
    ("K", 451, 453),
    ("P", "Em síntese, a varredura separa duas perguntas. A geometria, com a extensão na pose "
          "identificada, admite h ≤ 32,886 mm e exclui a cota do CAD; a curva extraída, com K e X_{pose} "
          "congelados, favorece um intervalo estreito em torno de H_{CAL}. As duas posições da ancoragem "
          "são grandezas distintas: H_{CAD} é a cota do desenho, e H_{CAL}, o parâmetro que, com K e "
          "X_{pose}, reproduz a curva extraída e põe A 12,084 mm abaixo, sobre a mesma perna h. Nenhuma das "
          "duas concordâncias é verificação independente, e os dados disponíveis não decidem qual das duas "
          "posições corresponde ao dispositivo."),
    ("H", "4.1", "r1_grav", R_GRAV),
    ("P", "O torque gravitacional do conjunto, calculado pela Equação (26) de forma independente da cadeia "
          "do cabo, atinge o máximo de 11,1619 N·m na elevação de 89,44°, valor que coincide com M g d da "
          "Tabela 4. Como a ordenada da curva publicada não tem unidade declarada e sua leitura em N·m é "
          "implausível (seção ⟦S:r1_comp⟧), as magnitudes não são comparáveis. O que se pode confrontar é "
          "a forma dos perfis, apresentados na Figura 11 normalizados pelos respectivos valores de pico, "
          "em função da elevação anatômica; como a normalização elimina a escala, o confronto não informa "
          "que fração do torque gravitacional o mecanismo compensa."),
    ("K", 461, 464),
    ("P", "O pico do torque do cabo ocorre na elevação de 97,484°, e o do torque gravitacional, em "
          "89,438°, com defasagem de 8,046°: o mecanismo entrega sua assistência máxima acima da posição "
          "de maior demanda gravitacional, configuração compatível com dispositivo projetado para trabalho "
          "acima da cabeça. As curvas normalizadas cruzam-se na elevação de 93,96° e, entre 105° e 150°, "
          "diferem em no máximo 0,027, o que indica que o perfil elástico reproduz a forma da demanda "
          "gravitacional na faixa de maior interesse para o trabalho acima da cabeça."),
    ("P", "Abaixo de 94°, as diferenças tornam-se negativas e crescentes em módulo, até −0,520 na elevação "
          "de 30°. No ponto morto, na elevação de 30,485°, o torque gravitacional ainda vale 5,757 N·m, "
          "51,6% de seu pico, enquanto o torque do cabo se anula. Trata-se de característica da "
          "arquitetura, e não de deficiência do ajuste: abaixo do ângulo de transição, o torque cai a um "
          "valor residual e o braço recupera a liberdade de movimento (seção 2.3). O confronto ilustra a "
          "limitação apontada por Nasr, Ferguson e McPhee (2022) e discutida na seção 2.4: um mecanismo "
          "passivo entrega torque determinado para cada ângulo, de modo que o ajuste favorável em uma "
          "faixa implica desvio em outra. No caso analisado, o compromisso privilegia a faixa acima da "
          "horizontal, onde a exposição postural concentra o risco documentado por van der Molen et al. "
          "(2017) e Seidler et al. (2020), à custa de subcompensação na faixa inferior."),
    ("H", "4.1", "r1_lim", R_LIM),
    ("P", "O modelo não representa a protuberância que, no dispositivo real, restringe o gerador de força "
          "além do ponto morto, na elevação de 30,485°; a patente indica a zona neutra a partir de 30°, "
          "diferença de 0,485°. Em consequência, o modelo prevê inversão de sinal do torque após o ponto "
          "morto, ao passo que o dispositivo mantém torque residual aproximadamente nulo; a ressalva "
          "restringe-se aos 0,485° finais da faixa e ao último ponto extraído. A ausência de unidade "
          "declarada na ordenada da curva publicada impede a conversão do torque do cabo para N·m e, por "
          "conseguinte, o cálculo do torque resultante sobre a articulação. Essa conversão exige dado "
          "independente, como a especificação de rigidez de uma mola comercial compatível com o mecanismo "
          "ou fonte documentada que estabeleça a escala da figura original."),
    ("P", "A identificação foi reproduzida apenas em parte. K e X_{pose} foram reproduzidos no h adotado, "
          "mas a origem de θ_{off} e de H_{CAL} não pôde ser reconstituída, e os quatro parâmetros foram "
          "identificados e avaliados contra os mesmos 29 pontos, cuja incerteza de extração não está "
          "documentada. O fator de escala propaga-se a todas as grandezas dimensionais e de massa. Por "
          "fim, os resultados referem-se a um único dispositivo, ao indivíduo de referência adotado e ao "
          "membro superior estendido sem ferramenta na mão; a generalização a outros percentis "
          "antropométricos, a outras configurações de cotovelo e à presença de carga na mão demanda a "
          "reexecução do procedimento com os parâmetros correspondentes."),
]

EXO2_R = [
    ("K", 476),
    ("E", 477, [(" As etapas dinâmicas da seção 3.2.13 não foram executadas.", "")]),
    ("H", "4.2", "r2_geo", R_GEO),
    ("E", 479, [("as grandezas medidas no modelo em CAD e as que delas derivam, com a origem de cada uma",
                 "as grandezas medidas no modelo em CAD")]),
    ("R", 480, "Tabela 13: Grandezas medidas no modelo em CAD"),
    ("L", 481, [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12]),     # só as medidas em CAD; as derivadas estão no texto
    ("K", 482, 483),
    ("P", "Na pose do CAD, o circuito dá s = 359,7679 mm até a ponta da peça de fixação do elástico, que "
          "difere do comprimento medido s_{pose} em 1,4 × 10^{−4} mm, valor inferior à resolução de três "
          "casas decimais da medida; até o pino, o comprimento do elástico na pose é de 346,686 mm. O "
          "elemento 78 está a p = 7,754 mm do eixo da articulação, enquanto a patente prefere esse "
          "elemento sobre o eixo; as consequências dessa diferença são tratadas nas seções "
          "⟦S:m2_torque⟧ e ⟦S:r2_grav⟧."),
    ("K", 485, 488),
    ("P", "No modelo em CAD, o braço do exoesqueleto (elemento 8) tem massa de 163,951 g, e o centro de "
          "massa fica a 47,362 mm do eixo da articulação 20. São estimativas obtidas da geometria "
          "reconstruída e de um material atribuído no CAD, náilon 6/6 em peça oca segundo a planilha, e "
          "não propriedades do produto. O braço do exoesqueleto acrescenta 0,1640 kg ao conjunto e "
          "desloca seu centro de massa em 0,194° em relação ao eixo do braço. A alavanca, o elemento 78 e "
          "a braçadeira não estão modelados como corpos separados, e as peças do lado do tronco apoiam-se "
          "no cinto e não giram com o braço."),
    ("P", "As verificações da seção ⟦S:m2_verif⟧ resultaram em resíduos da ordem do erro de "
          "arredondamento da aritmética de ponto flutuante, de até 5,7 × 10^{−14} mm nas equações de "
          "fechamento dos dois regimes, exceto os do trabalho virtual, de até 5,0 × 10^{−8} mm/rad, "
          "limitados pelo truncamento da diferença finita, e o do fechamento com o CAD, limitado pela "
          "resolução da medida. No teste sintético, a identificação pelo espaçamento entre as curvas "
          "recupera os valores de s_{0} com erro máximo de 0,074 mm, limitado pela interpolação linear "
          "entre os pontos de cada curva."),
    ("H", "4.2", "r2_ident", R_IDENT),
    ("P", "Foram extraídos 48 pontos da curva tracejada, 47 da pontilhada e 51 da contínua. As três cruzam "
          "zero, por interpolação linear entre os dois primeiros pontos, em 14,24° (tracejada), 14,36° "
          "(pontilhada) e 14,23° (contínua). A curva pontilhada tem máximo interior de 1,0777 divisão e "
          "termina em 0,0134 divisão em 170,82°. A contínua cresce até 4,6319 divisões em 170,28°, e a "
          "tracejada, depois de um patamar entre 1,37 e 1,40 divisão de cerca de 100° a 150°, sobe até "
          "2,4432 divisões em 169,80°."),
    ("K", 503),
    ("E", 504, [(" A Tabela 31 e os detalhes estão no Apêndice A.", "")]),
    ("K", 505, 511),
    ("K", 513, 514),
    ("E", 515, [("Os valores que ele encontra (Tabela 32, no Apêndice A), 294,34 mm",
                 "Os valores que ele encontra, 294,34 mm")]),
    ("K", 518, 521),
    ("H", "4.2", "r2_comp", R_COMP),
    ("E", 523, [(" A Tabela 18 reúne as grandezas do circuito em ângulos representativos.", "")]),
    ("K", 528),
    ("E", 530, [("A Tabela 19 e a Figura 13 mostram", "A Tabela 19 mostra")]),
    ("K", 531, 535),
    ("P", "A Figura 17 da patente não foi digitalizada, e a comparação com ela é visual. Qualitativamente, "
          "o modelo reproduz a sequência de máximo, vale e subida perto de 180° da figura, mas com o "
          "máximo antes do da patente e o cruzamento das curvas mais cedo, perto de 144°, contra cerca de "
          "155° a 160° na figura. A comparação quantitativa depende da digitalização da Figura 17 da "
          "patente, da definição de sua ordenada e dos valores de excentricidade, que a patente não "
          "informa."),
    ("H", "4.2", "r2_grav", R_GRAV),
    ("K", 541, 545),
    ("E", 546, [("valores da curva tracejada nas faixas de θel da Tabela 31, no Apêndice A.",
                 "valores da curva tracejada nas faixas de θel testadas na identificação.")]),
    ("E", 547, [("e por isso a Figura 15 e a Tabela 20 descrevem um cenário de projeto",
                 "e por isso a Tabela 20 descreve um cenário de projeto")]),
    ("K", 548, 551),
    ("K", 556),
    ("K", 558, 559),
    ("H", "4.2", "r2_lim", R_LIM),
    ("K", 562),
    ("E", 563, [("da ordenada da Figura 16, e K = K40", "da ordenada da Figura 16 da patente, e K = K40"),
                (", e o ajuste de forma usa escala diferente em cada curva.", ".")]),
    ("K", 564),
    ("E", 565, [("e os resultados referem-se ao membro de referência e limitam-se à análise estática.",
                 "e os resultados referem-se ao membro de referência.")]),
]

EXO3_R = [
    ("K", 566),
    ("E", 567, [(" As etapas dinâmicas da seção 3.3.13 não foram executadas.", "")]),
    ("H", "4.3", "r3_geo", R_GEO),
    ("K", 569, 572),
    ("P", "Com esses valores, o fechamento tem resíduo de 0,0006 mm, e a solução fechada devolve S e φ da "
          "tabela. Na imagem da folha 21, a distância de 584 a 572, com C_{2} = 90,587 mm, dá a escala do "
          "desenho, de 1,68 px/mm. Na Figura 14D, q = 61,19°, contra 61,724° no CAD: a pose do CAD é a da "
          "Figura 14D. Na 14C, q = −36,99°, isto é, Θ = 10,25°. Nas duas, o ponto A do CAD fica a 0,6 mm e "
          "a 0,3 mm do 562 desenhado."),
    ("K", 575, 576),
    ("L", 577, [4, 5, 6, 7, 8, 9, 10, 11]),     # sem as linhas de braço, antebraço e mão, iguais às da Tabela 14
    ("K", 578, 580),
    ("P", "No CAD, o apoio de braço tem 0,796 kg: a capa, de náilon 6/6, responde por 0,564 kg, e a mola, "
          "de aço, por 0,105 kg. O centro de massa do apoio, a 116,4 mm de O e 9,7° acima do eixo maior, "
          "desloca o do conjunto em 0,77° em relação ao eixo. As peças do CAD concordam com os desenhos: "
          "a distância entre os pinos 572 e 632 é de 163,6 mm no CAD, contra 165,0 mm na Figura 14D, e o "
          "R_{20} do came do CAD vai de 31,65 a 32,01 mm, conforme se calcule pela área, pela giração ou "
          "pela caixa envolvente."),
    ("P", "Nas verificações da seção ⟦S:m3_verif⟧, os resíduos da cadeia de cálculo são da ordem do erro "
          "de arredondamento, como 2,1 × 10^{−13} mm entre as duas formas do braço de momento, exceto o "
          "do trabalho virtual, com diferença relativa de 1,8 × 10^{−5} entre τ/F_{s} e dx/dq, limitado "
          "pelo truncamento da diferença finita, e os do fechamento com o CAD, de 5,9 × 10^{−4} mm, "
          "limitados pela resolução da medida. Nas peças do apoio de braço, as distâncias entre eixos "
          "diferem do desenho em até 1,36 mm, os ângulos em menos de 2°, e o eixo da mola passa a 3,3 mm "
          "do centro dos traços da mola 636; a hipótese de came espelhado é rejeitada pelas duas medidas "
          "do giro."),
    ("H", "4.3", "r3_ident", R_IDENT),
    ("E", 583, [(" A Tabela 23 traz os valores em ângulos de 15 em 15 graus e no máximo da AASM.", "")]),
    ("K", 588),
    ("K", 600, 603),
    ("K", 605, 609),
    ("H", "4.3", "r3_comp", R_COMP),
    ("P", "Da pose do CAD (Θ = −88,47°) até o limite de subida, o vão S diminui à medida que o braço sobe "
          "e se anula em Θ = 22,01° (seção ⟦S:m3_torque⟧). O braço de momento do cabo 560 cresce de "
          "26,04 mm na pose para 63,26 mm em Θ = 0 e fica positivo em toda a faixa. Com o giro do came da "
          "Figura 14D, o cabo da mola sai na Z12 na pose, no canto entre Z12 e Z11 de Θ = −85,9° a −47,0°, "
          "na Z11 de −47,0° a −18,6° e na Z10 de −2,4° a 18,0°. O raio efetivo vai de 10,55 mm na pose a "
          "32,08 mm na horizontal e coincide com ρ na Z10."),
    ("P", "A transmissão τ/F_{s} = (r/R) C_{1} sin(γ − θ), em N·mm por N, cresce de 10,39 mm na pose a "
          "77,79 mm em Θ = 9,6° e cai perto do limite de subida. Entre Θ = −75°, onde começa a curva da "
          "patente, e a horizontal, ela passa de 17,42 mm a 76,75 mm, isto é, é multiplicada por 4,4. O "
          "came responde por parte disso, com r de 13,57 para 32,08 mm, e o cabo de ancoragem pelo resto, "
          "com o braço de 33,94 para 63,26 mm. Da pose até o limite de subida, a mola encurta 93,1 mm."),
    ("K", 621, 624),
    ("E", 625, [("(Tabela 28 e Figura 19)", "(Tabela 28)")]),
    ("E", 626, [("e a força da mola fica entre 98,3 e 165,5 N (Figura 19a).",
                 "e a força da mola fica entre 98,3 e 165,5 N.")]),
    ("E", 627, [("Com outra mola ajustada a cada montagem (Figura 19b), as montagens",
                 "Com outra mola ajustada a cada montagem, as montagens"),
                ("quando a Figura 16 foi gerada.", "quando a Figura 16 da US 9.737.374 B2 foi gerada.")]),
    ("K", 628, 631),
    ("H", "4.3", "r3_grav", R_GRAV),
    ("K", 637, 642),
    ("H", "4.3", "r3_lim", R_LIM),
    ("K", 645, 647),
    ("E", 648, [("Por fim, os resultados referem-se ao membro de referência e limitam-se à análise estática.",
                 "Por fim, os resultados referem-se ao membro de referência.")]),
]

CAP4_FIM = [("K", 649, 655)]

# ====================================================================== capítulo 5
CAP5 = [
    ("K", 656, 661),
    ("K", 663),
    ("E", 664, [("O objetivo geral foi atingido para este dispositivo na parte estática, e a extensão à "
                 "dinâmica multicorpos ficou preparada, com o procedimento da seção 3.1.13, mas não foi "
                 "executada.",
                 "O objetivo geral foi atingido para este dispositivo."),
                (" Os objetivos f e g, referentes à equação de movimento e ao acoplamento com o MBDyn, não "
                 "foram executados.", "")]),
    ("P", "Como continuidade, recomenda-se obter um dado independente que fixe a escala do torque, como a "
          "especificação de uma mola comercial compatível, e representar a protuberância responsável pela "
          "zona neutra."),
    ("K", 666),
    ("K", 668, 671),
    ("E", 673, [("o item h foi cumprido na parte estática, com três ressalvas",
                 "o item f foi cumprido, com três ressalvas"),
                ("O item i foi cumprido", "O item g foi cumprido"),
                (" As etapas dinâmicas não foram executadas, pelas razões da seção 3.2.13.", "")]),
    ("P", "Como continuidade para esse dispositivo, recomenda-se obter a curva de força e extensão do "
          "elemento elástico, que fixaria K e a escala do torque."),
    ("K", 675),
    ("K", 677, 679),
    ("E", 681, [("o item j foi cumprido", "o item h foi cumprido"),
                ("O item k foi cumprido na parte estática, com a ressalva", "O item i foi cumprido, com a ressalva"),
                ("o objetivo geral foi atingido na parte estática; as etapas dinâmicas não foram executadas, "
                 "pelas razões da seção 3.3.13.",
                 "o objetivo geral foi atingido.")]),
    ("P", "Como continuidade para esse dispositivo, recomenda-se medir a rigidez e o comprimento livre da "
          "mola e o giro do came na peça real, que fixariam a escala e a montagem do came."),
    ("K", 683, 686),
]

REFERENCIAS = [("K", 687, 732)]      # as não citadas saem na montagem

PLANO = (CAP1 + CAP2 + CAP3_ABERTURA + EXO1_M + EXO2_M + EXO3_M + CAP3_FIM
         + EXO1_R + EXO2_R + EXO3_R + CAP4_FIM + CAP5 + REFERENCIAS)

# resumo e abstract: os da versão revisada, sem a frase das etapas dinâmicas
FRASES_FORA_DO_RESUMO = (
    " As etapas dinâmicas, pela formulação de Lagrange e no MBDyn, dependem de um dado independente que "
    "fixe a escala do torque e não foram executadas.",
    " The dynamic steps, through the Lagrange formulation and in MBDyn, depend on independent data that "
    "fix the torque scale and were not carried out.",
)

# termos que não podem aparecer no documento condensado (pedido do autor)
PROIBIDOS = ("MBDyn", "Lagrange", "etapa dinâmica", "etapas dinâmicas", "equação de movimento",
             "equações de movimento", "Apêndice", "APÊNDICE")
