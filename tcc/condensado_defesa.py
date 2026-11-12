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
    ("E", 3, [("4,12 milhões afastamentos", "4,12 milhões de afastamentos"),
              (" Na série de 2008 a 2018, os distúrbios osteomusculares relacionados ao trabalho "
               "responderam por 786.923 benefícios acidentários, e o CID M75 foi a razão de afastamento "
               "mais frequente entre as mulheres (MANOEL; CAVALCANTE, 2025).", "")]),
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
              (" e um elemento de encosto junto à articulação reduz o torque com o braço baixado e o anula "
               "quando situado sobre o eixo de rotação.", "."),
              (" Os três são tratados em seções separadas dos capítulos 3, 4 e 5, dedicadas aos "
               "exoesqueletos 1, 2 e 3.", "")]),
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
                "A implementação em Python, ferramenta livre, torna o modelo reprodutível por outros grupos."),
               (" E o tema tem endereço local: as lesões de ombro continuam entre as principais causas de "
                "afastamento no país, em setores que concentram trabalho acima da cabeça.", "")]),
    # 29 (o que o segundo e o terceiro dispositivos acrescentam) sai; está na introdução
]

# ====================================================================== capítulo 2
CAP2 = [
    ("K", 30, 32),
    ("P", "A evidência epidemiológica indica relação dose-dependente entre a exposição postural e o "
          "desfecho clínico (VAN DER MOLEN et al., 2017; SEIDLER et al., 2020), em especial com as mãos "
          "acima da linha dos ombros, faixa angular na qual se intensifica a compressão subacromial sobre "
          "os tendões do manguito rotador."),
    ("E", 34, [("braço–antebraço", "braço-antebraço")]),
    ("K", 35),
    # 36 (reabilitação), 38 (instrumentação dos dispositivos ativos) e 39 (meta-análises) saem
    ("K", 37),
    ("K", 40),
    ("E", 41, [(" Nguyen (2026) atualiza o panorama das alternativas estritamente passivas e de seus limites "
                "de aplicação.", "")]),
    ("K", 42, 47),
    ("E", 48, [(" Daí decorrem as soluções semipassivas de assistência regulável (GRAZI et al., 2020) e as "
                "configurações ativo-passivas (NASR; BELL; McPHEE, 2023); na primeira direção, Grazi et al. "
                "(2022) regulam o nível de assistência em tempo real a partir dos sinais cinemáticos "
                "captados pelos próprios sensores embarcados no dispositivo.", "")]),
    ("K", 49, 50),
    ("P", "O complexo do ombro é modelável como junta de três graus de rotação cujo centro glenoumeral se "
          "desloca durante a elevação do braço (GOPURA; KIGUCHI, 2009; SHEN et al., 2020), e os "
          "desalinhamentos entre os eixos da estrutura e as articulações biológicas geram forças "
          "parasitas de cisalhamento e pressão excessiva nos apoios de fixação (ZEIAEE et al., 2017). A "
          "EP 3 504 033 B1 atribui ao estado da técnica o alinhamento dos eixos do dispositivo aos do "
          "ombro e observa que, mesmo assim, movimentos do tronco, da coluna e da cintura escapular não "
          "são acompanhados (MIZERA et al., 2023). Em vez disso, o elemento de apoio do braço liga-se ao "
          "elemento de transmissão de força por uma única articulação, cujo eixo não coincide com o de "
          "abdução do ombro, e a reação é levada à pelve."),
    # 52 (estratégias de compensação de desalinhamento) sai
    # 54 a 57: seção 2.6, modelagem dinâmica multicorpos, sai
    ("K", 58),
    ("P", "Três arquiteturas comerciais consolidaram soluções distintas para esse mesmo problema. O "
          "shoulderX, desenvolvido na Universidade da Califórnia em Berkeley, gera o torque pelo conjunto "
          "de mola, cabo e polia descrito na seção 2.3 (VAN ENGELHOVEN; KAZEROONI, 2018)."),
    ("E", 60, [(" Apesar das diferenças construtivas, as três soluções perseguem idêntico objetivo "
                "funcional: sintetizar, por meio da geometria e de um único elemento elástico, perfil de "
                "torque que acompanhe o momento gravitacional do membro superior ao longo da elevação.", "")]),
    # 61 (variantes das Figuras 1 e 18 da patente) sai; está em 3.2.1
    ("K", 62, 64),
    ("E", 65, [("Wu, Wang e Du (2016) aplicam o princípio a um exoesqueleto de membro superior e relatam "
                "redução de 34,6% no consumo de potência em relação à configuração não balanceada. Em "
                "exoesqueletos vestíveis, porém, o balanceamento",
                "Em exoesqueletos vestíveis, porém, o balanceamento")]),
    # 66 (o elástico da EP e o comprimento livre nulo) sai
    ("K", 67),
    ("P", "O cálculo do torque gravitacional pressupõe o conhecimento da massa e da posição do centro de "
          "massa de braço, antebraço e mão. De Leva (1996) ajusta os dados de Zatsiorsky e Seluyanov de "
          "modo que as posições de centro de massa e os raios de giração fiquem referenciados aos centros "
          "articulares usualmente adotados em biomecânica, em frações da massa corporal total e do "
          "comprimento do segmento, o que permite escalar o modelo para o indivíduo de referência "
          "adotado. A transposição desses parâmetros ao eixo da junta do exoesqueleto usa o teorema dos "
          "eixos paralelos. Cabe distinguir as duas grandezas que o procedimento alimenta: o momento "
          "estático do peso, dependente apenas da massa e do braço horizontal do centro de gravidade, e o "
          "momento de inércia, que descreve a resistência à aceleração angular e não participa do torque "
          "estático."),
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
    ("K", 78),
    ("E", 79, [("; quando uma etapa não se aplica a um mecanismo ou não pôde ser concluída com os dados "
                "disponíveis, a própria subseção registra o motivo.", ".")]),
    ("K", 80, 81),
    ("P", "Os modelos em CAD dos exoesqueletos 1 e 2 foram feitos no Autodesk Fusion. Os cálculos estão em "
          "Python, com as bibliotecas NumPy (HARRIS et al., 2020), Matplotlib (HUNTER, 2007) e SciPy "
          "(VIRTANEN et al., 2020), esta usada no exoesqueleto 3 para o processamento das imagens da "
          "patente, a envoltória convexa do came e o limite de subida, pelo método de Brent (BRENT, 1973). "
          "Não integram o escopo a avaliação experimental com participantes humanos, o ensaio de protótipo "
          "e o dimensionamento estrutural das peças."),
]

EXO1_M = [
    ("K", 83),
    ("P", "A cadeia de cálculo está implementada no arquivo torque_model.py, que contém os parâmetros "
          "congelados e não executa ajuste algum, e os números e as figuras da seção 4.1 são produzidos "
          "pelo script tcc_resultados.py, que importa esse modelo sem alterar nenhum parâmetro."),
    ("H", "3.1", "m1_cad", T_CAD),
    ("P", "A geometria do mecanismo foi reconstruída no Autodesk Fusion sobre os desenhos da patente, em "
          "especial a vista em corte do gerador de torque. Como as figuras de patente não são cotadas, o "
          "modelo foi escalado por um fator único, fixado a partir de uma estimativa de medida "
          "antropométrica. Da reconstrução saem as grandezas geométricas, a pose de referência e a massa, "
          "o centro de massa e o momento de inércia de cada peça (seção ⟦S:r1_geo⟧), classificados como "
          "medidas em CAD: são estimativas, que dependem do fator de escala e do material atribuído a "
          "cada peça. O membro superior é o de referência (seção 3), e os momentos de inércia, "
          "transportados ao eixo da junta pelo teorema de Steiner, não participam do torque estático."),
    ("H", "3.1", "m1_fech", T_FECH),
    ("P", "O mecanismo é tratado como plano, com origem O no eixo da junta (pivô). A variável independente "
          "do modelo é q, o ângulo interno θ* entre os elos referido ao desenho:"),
    ("K", 94, 96),
    ("P", "em que θ_{off} = 133,017° é a calibração angular identificada (seção ⟦S:m1_ident⟧). A faixa da "
          "patente corresponde a θ* de 42,917° a 193,017° e a elevação de 30° a 180,1°; a elevação cresce "
          "quando θ* decresce. O torque τ do modelo é positivo no sentido de θ* crescente, oposto ao da "
          "patente; por isso, a curva calculada que se compara à da patente é −τ. A cinemática é descrita "
          "por um circuito vetorial fechado (Figura 1), percorrido do pivô O até a ancoragem A do cabo, "
          "de A até o ponto de tangência T ao longo do vão livre, de T até o centro D do tambor e de D de "
          "volta a O. O vetor fixo do pivô à ancoragem, no referencial do desenho, é"),
    ("K", 104),
    ("P", "em que h e p são as componentes desse vetor no referencial do elo proximal. A posição da "
          "ancoragem h é o parâmetro geométrico mais incerto do mecanismo: a cota lida no CAD, "
          "H_{CAD} = 34,785 mm, difere do valor adotado no modelo, H_{CAL} = 22,701 mm (seção "
          "⟦S:m1_ident⟧). Com u(x) = (cos x, sin x) e u⊥(x) = (−sin x, cos x), o fechamento do circuito se "
          "escreve"),
    ("K", 106, 110),
    ("P", "A grandeza ρ é a distância da ancoragem ao centro do tambor, e a tangente existe somente se "
          "ρ > R, condição verificada em cada ponto calculado."),
    ("K", 114, 116),
    ("R", 117, "Nota: O é o pivô, A a ancoragem do cabo, D o centro do tambor e T o ponto de tangência. O "
               "painel da direita amplia a região do pivô; as componentes h e p de B estão tracejadas."),
    ("H", "3.1", "m1_torque", "Braço de momento, mola e torque"),
    ("P", "O cabo deixa o tambor no ponto de tangência T. A distância b = |OT| e o ângulo β entre a linha "
          "do elo (de O a D) e o segmento OT saem da lei dos cossenos:"),
    ("K", 127),
    ("P", "em que φ_{B} = atan2(B_{y}, B_{x}) é a direção do vetor B. A distância b não é o braço de "
          "momento do cabo: como T pertence a uma circunferência de raio R centrada a C do pivô, b fica "
          "entre C − R e C + R. O braço de momento é a distância perpendicular do pivô à linha de ação do "
          "cabo, que passa por A com direção u(φ):"),
    ("K", 129),
    ("P", "O braço m tem sinal, anula-se quando a linha do cabo passa pelo pivô (ponto morto) e é limitado "
          "por |B| = |OA|. Admitido cabo inextensível, a extensão da mola acompanha a variação do caminho "
          "total do cabo, composto pelo vão livre s e pelo arco enrolado no tambor, que varia porque o vão "
          "livre gira em relação ao elo distal. Sendo ψ o ângulo entre a direção do cabo e a direção do "
          "elo, reduzido ao intervalo (−π, π),"),
    ("K", 133, 135),
    ("P", "O sinal do termo do arco foi fixado pelo princípio dos trabalhos virtuais (seção ⟦S:m1_grav⟧): "
          "em um mecanismo conservativo, o trabalho da tração no cabo iguala o do torque no elo, o que "
          "exige"),
    ("K", 137),
    ("P", "com q em radianos. A extensão da mola é referida a um comprimento, e não a um ângulo. Sendo "
          "X_{pose} a extensão elástica da mola na pose de referência, θ*_{pose} = 115,017°, o valor do "
          "caminho em que a mola atinge o comprimento livre e a lei da mola são"),
    ("K", 140),
    ("P", "em que δ é a extensão elástica, F a tração no cabo e K a rigidez da mola; a extensão é limitada "
          "a valores não negativos porque o cabo traciona, mas não empurra. O comprimento livre da mola só "
          "entra no modelo pela diferença X_{pose} = L_{pose} − L_{livre}. A força do cabo atua sobre o "
          "tambor no ponto T, com direção oposta a u(φ), e o torque em relação ao pivô é o produto "
          "vetorial plano"),
    ("K", 143),
    ("P", "Como K é identificado contra a curva publicada, cuja ordenada não tem unidade declarada, o "
          "torque do cabo é expresso na unidade da própria curva, denotada u.p. (unidade da patente); K "
          "só estaria em N/mm se u.p. correspondesse a N·m, o que não pode ser afirmado com os dados "
          "disponíveis (seção ⟦S:r1_comp⟧). O torque se anula no ponto morto, quando a linha de ação "
          "passa pelo pivô (m = 0); da geometria do circuito, esse ângulo tem forma fechada em função de "
          "h:"),
    ("K", 147),
    ("P", "Depois do ponto morto, o torque do cabo troca de sinal; o modelo não representa a protuberância "
          "que, na patente, restringe o gerador de força além do ângulo de transição (seção 2.3)."),
    ("H", "3.1", "m1_grav", T_GRAV),
    ("K", 152, 153),
    ("P", "em que M é a massa do conjunto, g = 9,80665 m/s^{2} e x_{g}, em milímetros, é o braço "
          "horizontal do centro de massa. O torque gravitacional resulta em N·m, unidade física, ao "
          "contrário do torque do cabo."),
    ("P", "O equilíbrio estático do braço é escrito pelo princípio dos trabalhos virtuais. Com a junta e o "
          "tambor sem atrito e o cabo inextensível e sem massa, os vínculos são ideais, e suas reações "
          "não realizam trabalho. Num giro virtual δq do conjunto em torno de O, em radianos, realizam "
          "trabalho a força do cabo sobre o tambor, o peso do conjunto e o torque τ_{u} que o usuário "
          "aplica ao braço. A força do cabo, f = −F u(φ), atua no ponto de tangência T, que é o vetor b, "
          "de módulo b e a um ângulo β da linha do elo; como o elo é rígido e gira em torno de O, o "
          "trabalho virtual dessa força é o do seu momento em relação a O, a componente z de b × f:"),
    ("K", 158),
    ("P", "O produto vetorial retém só a componente de f perpendicular a b, que é a que gira o elo. Na "
          "faixa de operação, b vai de 282,503 a 284,363 mm, mas f aponta quase para o pivô; por isso, "
          "−b sin(φ + β − q), que coincide com o braço m da Equação (16), não passa de |B| = 22,919 mm, e "
          "tomar F b como torque, sem a projeção, superestimaria o resultado em mais de 12 vezes. Do lado "
          "da mola, o giro δq a estende de δℓ = (dℓ/dq) δq, e a força F = K δ, que se opõe à extensão, "
          "realiza o trabalho −F δℓ/1000. Igualadas as duas expressões, a força se cancela e resta "
          "dℓ/dq = m, a Equação (19), que depende só da geometria: das formulações ℓ = s, ℓ = s + Rψ e "
          "ℓ = s − Rψ, só a última a satisfaz (seção ⟦S:r1_geo⟧)."),
    ("K", 161, 162),
    ("P", "em que τ_{u} é o torque que o usuário precisa exercer para manter o braço parado. Como τ está "
          "em u.p. e τ_{g,s} em N·m, essa soma só tem valor físico se u.p. corresponder a N·m, e a seção "
          "4.1 compara apenas a forma e os ângulos de τ e τ_{g}."),
    ("H", "3.1", "m1_ident", T_IDENT),
    ("E", 165, [("registrados em θ* e listados na Tabela 5 na ordem da extração.", "registrados em θ*.")]),
    ("P", "A patente não informa rigidez, pré-carga, comprimento livre nem posição exata da ancoragem. Os "
          "parâmetros não publicados do modelo são a calibração angular θ_{off}, a posição da ancoragem "
          "h, a extensão da mola na pose X_{pose} e a rigidez K. Eles foram identificados por mínimos "
          "quadrados contra os 29 pontos extraídos, por um procedimento que não foi registrado, e estão "
          "congelados no modelo; a identificação só pôde ser reproduzida na parte descrita a seguir."),
    ("K", 167, 168),
    ("P", "Com h e θ_{off} fixados, X_{pose} foi reidentificado por varredura unidimensional, em passo de "
          "0,001 mm, com K dado pela Equação (29) em cada valor. O ajuste é avaliado pela raiz do erro "
          "quadrático médio (RMSE), pelo erro absoluto médio (MAE) e pelo coeficiente de determinação "
          "R^{2}. O RMSE mede a aderência à curva extraída, e não a validade física: duas formulações só "
          "são comparadas por ele depois de ambas satisfazerem as verificações físicas da seção "
          "⟦S:m1_verif⟧."),
    ("H", "3.1", "m1_verif", T_VERIF),
    ("P", "Para separar o que a curva extraída informa sobre h do que a geometria impõe, h foi varrido de 8 "
          "a 60 mm, num total de 10.402 valores distintos. A varredura é um "
          "diagnóstico, não uma otimização: K permanece congelado em 174,68, e a referência s_{0}(h) da "
          "Equação (20) é recalculada para que a extensão da mola na pose permaneça X_{pose} = 37,383 mm. "
          "Para cada h são calculados o RMSE contra os 29 pontos extraídos e três critérios de validade "
          "física: tração, isto é, extensão da mola não negativa em toda a faixa de operação; fechamento, "
          "isto é, existência de tangente ao tambor (ρ > R); e trabalho virtual, isto é, resíduo da "
          "Equação (19) inferior a 10^{−6} mm/rad."),
    ("P", "A cadeia de cálculo é conferida a cada execução por verificações automáticas, com tolerância "
          "declarada: os resíduos f_{1} e f_{2} das Equações (7) e (8), a identidade τ = −F m/1000 da "
          "Equação (22), a coincidência da Equação (23) com a raiz de m(θ*) = 0 obtida por bissecção e o "
          "resíduo da Equação (19), por diferenças finitas centradas; há ainda testes automatizados, "
          "executados com o pytest. O modelo é plano e admite cabo inextensível, "
          "tambor sem atrito e mola linear sem tração inicial, F = K δ."),
]

EXO2_M = [
    ("K", 190),
    ("P", "Esta seção aplica o procedimento à EP 3 504 033 B1 (MIZERA et al., 2023), da Ottobock. A cadeia "
          "de cálculo está implementada no arquivo torque_model_ottobock.py, e os números e as figuras da "
          "seção 4.2 são produzidos pelo script tcc_resultados_ottobock.py, que não altera parâmetro "
          "algum do modelo."),
    ("H", "3.2", "m2_cad", T_CAD),
    ("P", "A EP 3 504 033 B1 descreve um dispositivo em que o elemento de apoio do braço, formado por um "
          "elemento distanciador (8) e uma concha, liga-se por uma articulação (20) à extremidade "
          "superior de um elemento de transmissão de força (18), uma barra cuja extremidade inferior se "
          "apoia num cinto pélvico. O atuador passivo, uma mola de tração na Figura 1 da patente e um "
          "cabo ou fio elástico na Figura 18 da patente, tem uma extremidade presa à barra 18, e a outra "
          "atua sobre um elemento de alavanca do elemento distanciador 8, de modo que a força é aplicada "
          "excentricamente em relação ao eixo da articulação 20."),
    ("P", "O elemento 78, chamado na patente de Anlageelement e aqui de elemento de encosto, fica junto à "
          "articulação 20 e encosta no elemento elástico a partir de um ângulo predeterminado entre o "
          "elemento de apoio do braço e a barra (Figura 22 da patente). A patente prefere o elemento 78 "
          "exatamente sobre o eixo da articulação 20; nesse caso, os dois trechos em que o elástico fica "
          "dividido exercem forças radiais ao eixo e não produzem torque, e o braço desce sem "
          "assistência. O documento não traz cotas do mecanismo nem rigidez, pré-tensão ou dimensões do "
          "elemento elástico."),
    ("P", "O modelo é plano, restrito ao plano sagital, e representa somente a anteversão, que é o "
          "movimento das Figuras 16 e 17 da patente. O circuito do mecanismo foi fechado no modelo em "
          "CAD, e as grandezas medidas nesse modelo estão na Tabela 13 (seção ⟦S:r2_geo⟧). O critério de "
          "escala do modelo não foi registrado, e a planilha de composição inercial identifica o modelo "
          "como Ottobock iX Shoulder Air; como a patente não nomeia o produto, a correspondência entre "
          "esse produto, o modelo em CAD e os desenhos da patente não está documentada, e as grandezas "
          "são tratadas como medidas em CAD. O membro humano é o de referência (seção 3), com o "
          "transporte dos momentos de inércia ao eixo da articulação 20 pelo teorema de Steiner (Tabela "
          "14)."),
    ("H", "3.2", "m2_fech", T_FECH),
    ("P", "A origem O fica no eixo da articulação 20, admitido coincidente com o centro do ombro, com eixo "
          "x anterior e eixo y para cima. A variável independente é q, a direção da alavanca, "
          "representada pelo segmento OP. A anteversão do braço, θ_{el}, com 0° para o braço pendente e "
          "90° para o braço horizontal à frente, é a abscissa das Figuras 16 e 17 da patente. O modelo "
          "admite que o giro do elemento de apoio do braço em relação à barra 18 seja igual à anteversão; "
          "a patente não garante essa condição, e as comparações angulares com as figuras dependem dessa "
          "hipótese. O eixo do braço aponta na "
          "direção θ_{el} − 90°, e q se relaciona com θ_{el} por"),
    ("K", 208),
    ("P", "em que q_{pose} é a direção de OP na pose do CAD e θ_{b,pose} = 7,962° o ângulo do braço com a "
          "horizontal nessa pose, positivo acima, como conferido no CAD. O modelo é sensível a esse "
          "sinal: com o sinal oposto, o contato do elástico com o elemento 78 passaria de 24,55° para "
          "8,62°, e o espaçamento entre as curvas da Figura 16 da patente, usado na identificação, "
          "fecharia com resíduo de 0,406 mm, contra 0,194 mm com o sinal adotado (seção ⟦S:r2_ident⟧). O torque τ é positivo no sentido de θ_{el} crescente, de "
          "modo que τ > 0 assiste a subida do braço, e as comparações com o peso usam o módulo τ_{g}."),
    ("P", "A ancoragem A do elástico fica na barra 18, e o ponto P, no pino do rasgo da alavanca solidária "
          "ao braço (Figura 3). A alavanca é o segmento OP, de comprimento ‹e› = e_{c} = 34,785 mm e "
          "direção q. No CAD, o elástico prende-se a uma peça articulada nesse pino, que só entra para "
          "fechar o circuito com o comprimento do elástico medido no CAD (seção ⟦S:r2_geo⟧). O vetor fixo "
          "de A a O e as posições de P e do centro do elemento 78, a uma distância p de O, são"),
    ("K", 214, 220),
    ("P", "Com as grandezas do CAD, x = 38,972 mm. Em cada regime, as incógnitas são s e ψ, e a solução é "
          "fechada, porque os demais termos são conhecidos para cada q. O contato não é imposto por um "
          "ângulo: ele é detectado pelo sinal do produto vetorial"),
    ("K", 225),
    ("P", "O regime II ocorre quando κ ≥ 0, isto é, quando o elemento 78 ficaria do outro lado da reta de "
          "A a P se o elástico não o contornasse, e o ângulo de contato q* é a raiz de κ, obtida por "
          "bissecção. Para a geometria do CAD, q* = 87,074°, isto é, θ_{el} = 24,549°; nesse ponto, "
          "s = 375,869 mm e m = 6,142 mm nos dois regimes."),
    ("K", 227, 229),
    ("R", 230, "Nota: à direita, ampliação da região do pivô. O elemento 78, na ponta de p, só entra "
               "depois do contato. As linhas pontilhadas indicam o eixo do braço."),
    ("H", "3.2", "m2_torque", "Braço de momento, elástico e torque"),
    ("P", "O elástico é tratado como linear e sem massa, com folga abaixo do comprimento livre: "
          "δ = max(s − s_{0}, 0) e F = K δ, em que s_{0} é o valor de s em que o elástico atinge o "
          "comprimento livre. A patente não informa K, o comprimento livre nem a pré-tensão. A força do "
          "trecho ligado a A, f = −F u(ψ), atua em P no regime I e no centro do elemento 78 no regime II; "
          "o trecho x liga dois pontos da alavanca e não tem momento resultante. O braço de momento com "
          "sinal e o torque são"),
    ("K", 239),
    ("P", "com m > 0 quando o torque assiste a subida. Com o elemento 78 pontual e sem atrito, a tração é "
          "igual nos dois trechos, e o princípio dos trabalhos virtuais (seção ⟦S:m2_grav⟧) dá"),
    ("K", 241),
    ("P", "com q em radianos: o elástico se encurta quando o braço sobe. Pela Equação (44), m_{II} é "
          "proporcional a p, de modo que, abaixo do contato, o torque só se anula com o elemento 78 sobre "
          "o eixo (p = 0), configuração preferida pela patente. Nesse caso, a reta do elástico passa pelo "
          "pivô no contato, e o ângulo de contato tem forma fechada, a direção do vetor de A a O, o que "
          "dá θ_{el} = 13,349° com as demais grandezas do CAD. As curvas da Figura 16 da "
          "patente partem de razão nula entre 14,23° e 14,36°, em média 0,93° acima desse contato e bem "
          "abaixo do contato com o elemento do CAD, em 24,55°: a figura é compatível com o elemento 78 "
          "sobre o eixo, o único caso em que o modelo tem torque nulo antes do contato."),
    ("H", "3.2", "m2_grav", T_GRAV),
    ("K", 248, 249),
    ("P", "O conjunto reúne o membro humano e o braço do exoesqueleto (elemento 8), que desloca o centro "
          "de massa em a_{CG} = 0,194°; o máximo de τ_{g}, 10,617 N·m, ocorre em θ_{el} = 89,8°. O "
          "equilíbrio é escrito pelo trabalho virtual num giro δq do conjunto, em radianos. Com o "
          "elemento 78 pontual e sem atrito e o elástico sem massa, o contato é um vínculo ideal, e "
          "realizam trabalho a força do elástico sobre a alavanca, o peso do conjunto e o torque τ_{u} do "
          "usuário. O vetor b vai de O ao ponto de aplicação da força do trecho ligado a A, com módulo b "
          "e a um ângulo β de OP, e f = −F u(ψ); como esse ponto é fixo na alavanca em cada regime, b e β "
          "são constantes:"),
    ("K", 253, 256),
    ("P", "com τ em N·m sob a hipótese K = K_{40} (seção ⟦S:m2_ident⟧)."),
    ("H", "3.2", "m2_ident", T_IDENT),
    ("P", "As Figuras 16 e 17 da patente são apresentadas no documento como representações exemplares "
          "das curvas de força, sem informação sobre se foram medidas ou calculadas. A abscissa é o ângulo de anteversão, e a ordenada não tem rótulo nem valores, "
          "apenas linhas de grade (Figura 5). As três curvas da Figura 16 da patente foram geradas com um "
          "único atuador passivo, com pré-tensões diferentes: quase nula na curva pontilhada e crescente "
          "na tracejada e na contínua. Segundo a patente, a ordenada é o torque causado pelo peso do "
          "braço dividido pelo torque aplicado pelo dispositivo. As curvas, porém, partem de zero perto "
          "de 14° e crescem com o ângulo, e com essa definição a razão seria infinita onde o dispositivo "
          "não aplica torque. Só a leitura inversa, torque do dispositivo dividido pelo torque do peso, "
          "é coerente com a figura; essa foi a interpretação adotada."),
    ("K", 262, 263),
    # a nota da figura (página girada; ordenada sem rótulo, já dita no texto) entra na linha da fonte
    ("R", 264, "Fonte: Mizera et al. (2023), Figura 16, p. 31 do documento B1, com a página girada para a "
               "orientação de leitura."),
    ("P", "Os pontos das três curvas foram extraídos neste trabalho, com a razão em divisões da grade e "
          "erro mediano de sobreposição inferior a 0,5 px; a imagem e a resolução usadas na leitura não "
          "foram registradas, e a incerteza da extração não foi avaliada de forma independente. A Figura "
          "16 da patente informa s_{0} de duas maneiras que não dependem da escala da ordenada: pelo "
          "espaçamento entre as três curvas, que foi a adotada, e pelo fim da curva pontilhada, que serve "
          "de verificação independente. O ajuste da forma de cada curva, com s_{0} e escala livres, "
          "depende também do braço de momento e do torque do peso do modelo e é mantido como resultado "
          "secundário (seção ⟦S:r2_ident⟧). O modelo da razão de torques é"),
    ("K", 270),
    ("P", "em que r é a razão extraída, em divisões, e c = K/σ um fator de escala, com σ a razão de "
          "torques que corresponde a uma divisão da ordenada. A curva da patente não separa K de σ, e por "
          "isso K não é identificável a partir dela. Os procedimentos usam apenas os pontos com "
          "20° < θ_{el} < 165°: abaixo de 24,55°, o modelo depende da posição do elemento 78, e, perto de "
          "180°, τ_{g} tende a zero. Admitido que a geometria e a rigidez sejam as mesmas nas três "
          "curvas, a razão de cada curva i escreve-se"),
    ("K", 274, 276),
    ("P", "A Equação (52) foi escrita em cada ponto extraído de uma curva, com a razão da outra "
          "interpolada linearmente no mesmo ângulo, para os seis pares ordenados de curvas. O sistema, "
          "com 234 equações e três incógnitas, foi resolvido por mínimos quadrados lineares e usa apenas "
          "s(θ_{el}) do circuito: não depende de K, de σ, de m nem de τ_{g}. A robustez foi avaliada com "
          "outras faixas de θ_{el}, de 15° a 170°, de 25° a 160° e de 40° a 150°, e com ruído de extração "
          "de 0,5 px, em 500 sorteios, e um teste sintético confere a implementação. Com os valores "
          "identificados, a razão de cada curva dividida pela extensão do elástico, s − s_{0}, dá uma "
          "estimativa do fator G, e a coincidência das três estimativas testa a hipótese de G comum."),
    ("P", "Para expressar o torque em N·m, "
          "K foi fixado por hipótese de projeto, e não identificado: o alvo é 40% do torque do peso "
          "em θ_{el} = 90°, percentual baseado na alegação comercial de que o exoesqueleto IX Shoulder "
          "Air reduz em 40% ou mais a sobrecarga no ombro durante o trabalho acima da cabeça (SUITX, "
          "[202-]). A alegação não consta da patente, não informa as condições em que a redução foi "
          "medida e não foi verificada neste trabalho. O valor correspondente é"),
    ("K", 284),
    ("P", "calculado com o s_{0} adotado. A força em 90° é a mesma para qualquer s_{0}; o valor escolhido "
          "muda K_{40} e a distribuição da força no restante da faixa."),
    ("H", "3.2", "m2_verif", T_VERIF),
    ("P", "O trecho e_{c}, do pivô ao pino do rasgo da alavanca, é a excentricidade do ponto de aplicação, "
          "um dos parâmetros de ajuste previstos na patente e objeto da Figura 17 da patente. A varredura "
          "manteve s_{0} = 300,750 mm e K = 2,54982 N/mm, isto é, o mesmo elástico, e variou apenas "
          "e_{c}, de 20 a 50 mm, num total de 602 valores. As verificações são "
          "asserções executadas a cada cálculo, com tolerância declarada: as equações de fechamento, o "
          "trabalho virtual, a continuidade na troca de regime e o caso limite p = 0. O torque "
          "gravitacional considera o membro de referência e o braço do "
          "exoesqueleto, sem a alavanca, o elemento 78 e a braçadeira."),
]

EXO3_M = [
    ("K", 294),
    ("P", "Esta seção aplica o procedimento à US 9.737.374 B2 (DOYLE, 2017), da Levitate, em que a força "
          "da mola chega ao ombro por um par de polias, uma delas um came de raio variável, e por um cabo "
          "de ancoragem. A cadeia de cálculo está nos scripts da pasta exo3, e os números e as figuras da "
          "seção 4.3 são produzidos pelo script tcc_resultados_exo3.py. O documento da patente está só em "
          "imagem, e o texto foi lido por reconhecimento óptico."),
    ("H", "3.3", "m3_cad", T_CAD),
    ("P", "Nas Figuras 14C e 14D da US 9.737.374 B2, o chassi 580 do apoio de braço gira em torno do pivô "
          "horizontal do ombro, 584. O cabo de ancoragem 560 sai do ponto 562, preso ao "
          "suporte do tronco, enrola-se na polia primária 564 e prende-se a ela. A polia secundária 570 é "
          "solidária à primária, e as duas giram em torno do pino 572, no chassi. O cabo da mola 634 "
          "prende-se à secundária no ponto 573, passa pela polia de reversão 630, no pino 632, e chega à "
          "mola 636, cuja outra ponta fica presa ao chassi (DOYLE, 2017). Ao baixar o braço, o cabo 560 "
          "desenrola-se da primária, o par de polias gira, e o cabo 634 enrola-se na secundária, "
          "estendendo a mola."),
    ("P", "A secundária 570 é o came. A patente divide o canal em três zonas: na Z10, o raio é constante; "
          "na Z11, ele diminui continuamente; e na Z12, o canal forma um trecho reto (DOYLE, 2017). A "
          "Figura 16 da US 9.737.374 B2 traz o momento do dispositivo (AASM), o do peso do braço (AWM) e "
          "o resultante (RM) em função do ângulo Θ do eixo maior do apoio de braço com a horizontal, "
          "positivo acima dela, sem unidade na ordenada. O documento não traz cotas do mecanismo nem a "
          "rigidez e o comprimento livre da mola: os desenhos das Figuras 14C, 14D, 15A e 15B são a única "
          "fonte geométrica da patente."),
    ("P", "O modelo é plano e representa só a rotação do apoio de braço em torno do eixo do pivô 584. O "
          "circuito do mecanismo foi fechado no modelo em CAD deste trabalho, cuja pose é a da Figura "
          "14D, e as grandezas medidas nesse modelo estão na Tabela 21 (seção ⟦S:r3_geo⟧). O membro superior é "
          "o de referência (seção 3), alinhado ao eixo maior do apoio de braço, com o centro do ombro "
          "admitido no eixo do pivô 584. O apoio de braço entra com as propriedades de massa de cinco "
          "corpos do CAD, a capa, a mola, as polias interna e externa e o came, levadas ao pivô pelo "
          "teorema de Steiner (Tabela 22). As grandezas são tratadas como medidas em CAD, e não como "
          "dimensões do dispositivo comercial."),
    ("H", "3.3", "m3_fech", T_FECH),
    ("P", "A origem O fica no eixo do pivô 584, no referencial do CAD, que é o das Figuras 14C e 14D "
          "girado de 180°. A variável independente é q, o ângulo entre C_{2} e a horizontal, 61,724° na "
          "pose do CAD; q cresce quando o braço desce. A abscissa da Figura 16 da US 9.737.374 B2 é Θ, o "
          "ângulo do eixo maior do apoio de braço com a horizontal, positivo acima dela, e a elevação a "
          "partir do braço pendente é Θ + 90°. No CAD, o eixo maior fica 26,741° além de C_{2}, no "
          "sentido em que q cresce, e, portanto,"),
    ("K", 310),
    ("P", "e a pose do CAD está em Θ = −88,465°. O torque τ é positivo no sentido de Θ crescente, de modo "
          "que τ > 0 assiste a subida do braço, e as comparações com o peso usam o módulo τ_{g}."),
    ("K", 314, 317),
    ("P", "A tangente existe enquanto |d| > R. O caminho inverso, de θ para q, também fecha, por dois "
          "ramos, e o correto é escolhido por continuidade a partir da pose do CAD."),
    ("K", 319, 321),
    ("H", "3.3", "m3_torque", "Braço de momento, came, mola e torque"),
    ("K", 323, 326),
    ("P", "A segunda forma vem do fechamento: como a linha do cabo passa por A, o braço m_{a} só depende "
          "de θ e não passa de C_{1}. O apoio de braço, com o chassi, as polias, a mola e o cabo 634, "
          "gira em torno de O como um corpo só, e o único esforço externo do mecanismo é a tração F_{a} "
          "do cabo 560, em T."),
    ("P", "A força da mola chega ao cabo 560 pelo par de polias, que gira sem atrito em torno de D: com "
          "F_{s} a tração no cabo da mola 634 e r o raio efetivo da secundária, isto é, a distância de D "
          "à linha do cabo 634, o equilíbrio do par dá F_{a} R = F_{s} r. O perfil do canal foi extraído "
          "da Figura 15B, um corte pelo plano do canal, e dividido pelo raio médio da zona Z10, R_{20}, "
          "tomado como referência (Figura 7a). O cabo tracionado passa reto sobre concavidades, e o raio "
          "efetivo é, por isso, a função suporte da envoltória convexa do canal: para cada direção "
          "φ_{c} normal ao cabo, r(φ_{c}) é a maior projeção dos pontos do canal nessa direção. Ele "
          "difere do raio ρ do came no ponto de saída, que é o que a patente cota. Com β_{c} o ângulo "
          "entre o raio do ponto de saída e o cabo,"),
    ("K", 332, 335),
    ("P", "Por simplificação, a polia de reversão 630 fica fora da varredura: o cabo 634 é tomado na "
          "direção de 572 para 632, medida na Figura 14D, como se a polia estivesse no infinito. A mola, "
          "cuja rigidez e cujo comprimento livre a patente não informa, entra como mola linear, e o "
          "torque fica"),
    ("K", 337),
    ("P", "em que x_{0} é o alongamento na pose do CAD e Δx o alongamento desde ela; k e x_{0} são "
          "identificados na seção ⟦S:m3_ident⟧. O braço de momento m_{a} se anula quando o cabo 560 "
          "passa por O, alinhado a C_{1}, o que ocorre em Θ = −128,5°, fora da faixa da Figura 16 da "
          "US 9.737.374 B2, que começa em −75°: o mecanismo não tem ponto morto nem faixa sem torque no "
          "curso analisado. O vão S se anula quando a ancoragem chega à polia, em Θ = 22,0°: com esta "
          "ancoragem, o braço não sobe além disso, embora a curva da patente vá até 30°."),
    ("H", "3.3", "m3_grav", T_GRAV),
    ("E", 344, [(" do eixo maior (seção 3.3.2).", " do eixo maior.")]),
    ("K", 345),
    ("P", "com m_{i} em kg e d_{i} em mm. Para o membro, alinhado ao eixo maior, a_{i} = 0; o centro do "
          "came, a 12,35 mm do pino 572, gira com as polias, e o termo dele usa o giro θ_{p} da Equação "
          "(65)."),
    ("K", 348, 352),
    ("H", "3.3", "m3_ident", T_IDENT),
    ("P", "A Figura 16 da US 9.737.374 B2 foi digitalizada neste trabalho, com um ponto por grau de "
          "Θ = −75° a 30° nas três curvas. A ordenada não tem unidade, o que impede identificar a rigidez "
          "em valor físico pela AASM sozinha. A própria figura, porém, traz uma referência: a AWM é o "
          "momento do peso do braço, um cosseno de amplitude A. Igualando A ao torque do peso do membro "
          "de referência na horizontal, a unidade da figura passa a N·m. Com ela, a mola linear da "
          "Equação (62) tem dois parâmetros, k e x_{0}, ajustados por mínimos quadrados nos pontos de "
          "Θ = −75° até o limite de subida:"),
    ("K", 357),
    ("P", "em que y_{i} é a AASM lida em Θ_{i}, M_{m} e d_{m} são a massa do membro e a distância do "
          "centro de massa dele a O, e g_{i}, Δx_{i}, r_{i} e θ_{i} saem da cadeia de cálculo. O giro do "
          "came, que fixa a constante da rotação das polias, foi medido na Figura 14D, e R_{20}, nas "
          "Figuras 14C e 14D (seção ⟦S:r3_geo⟧)."),
    ("H", "3.3", "m3_verif", T_VERIF),
    ("P", "O giro do came em relação à primária é a grandeza menos certa da cadeia, porque os dois "
          "desenhos discordam, e é a que decide em que zona o cabo da mola sai em cada Θ; por isso, foi o "
          "parâmetro varrido. A varredura repetiu o ajuste com o came girado de −120° a +40° em relação "
          "ao desenho da Figura 14D, de grau em grau, e só valem os giros em que o cabo da mola sai do "
          "canal em toda a faixa do ajuste."),
    ("P", "Além do giro contínuo, foram testadas as montagens que os furos permitem. Nas Figuras 14C e "
          "14D, há cinco furos pequenos num arco em torno do pino 572, que acompanham o came de uma "
          "figura para a outra. Admitido, por hipótese, que a polia externa tenha furos correspondentes, "
          "o came pode ser fixado girado de j passos em relação ao desenho, com j de −4 a +4. Cada "
          "montagem foi calculada de dois modos: com a mola e o cabo da montagem desenhada e com k e "
          "x_{0} ajustados de novo à curva da patente. Os scripts executam verificações que vão do "
          "fechamento com as grandezas do CAD ao trabalho virtual (seção ⟦S:r3_geo⟧)."),
]

CAP3_FIM = [
    ("K", 369, 371),
    ("L", 372, [2, 3, 4, 6, 7]),         # sem as linhas de arquitetura e de ponto de aplicação da força
    ("K", 373),
]

# figuras reduzidas para caber no limite de páginas: índice do bloco da imagem → fator
ESCALA_FIGURAS = {228: 0.78, 263: 0.75}

# ====================================================================== capítulo 4
EXO1_R = [
    ("K", 374, 376),
    ("E", 377, [(" As etapas dinâmicas da seção 3.1.13 não foram executadas.", "")]),
    ("H", "4.1", "r1_geo", R_GEO),
    ("P", "A reconstrução da vista em corte do gerador de torque forneceu as grandezas da Tabela 3, e a "
          "composição inercial do conjunto braço-exoesqueleto, obtida pelo transporte dos momentos ao "
          "eixo da junta, consta da Tabela 4."),
    ("K", 380),
    ("L", 381, [1, 2, 3, 4, 5, 6, 8]),       # sem o comprimento útil do alojamento, que não entra no cálculo
    ("K", 382),
    ("K", 384, 386),
    ("E", 387, [("igual ao momento de inércia no eixo da junta, conforme a Equação (1);",
                 "igual ao momento de inércia no eixo da junta, como exige o teorema de Steiner;"),
                ("O momento de inércia destina-se à etapa dinâmica, não executada, e não participa do "
                 "cálculo do torque estático.",
                 "O momento de inércia não participa do cálculo do torque estático.")]),
    ("P", "As verificações automáticas da seção ⟦S:m1_verif⟧ resultaram em resíduos da ordem do erro de "
          "arredondamento, de no máximo 8,0 × 10^{−13} mm nas relações geométricas, exceto o do trabalho "
          "virtual, limitado pelo truncamento da diferença finita. Essa verificação decidiu a formulação "
          "do caminho do cabo: com a extensão da mola acompanhando apenas o vão livre s, o resíduo da "
          "Equação (19) é de 1,7129 mm/rad; com o arco somado ao vão, s + Rψ, é de 3,4258 mm/rad; somente "
          "com ℓ = s − Rψ, Equação (18), ele cai a 4,7 × 10^{−8} mm/rad. Um resíduo da ordem de 1 mm/rad "
          "significa que o modelo entrega torque sem a correspondente variação da energia da mola, o que "
          "viola a conservação de energia em um mecanismo sem atrito."),
    ("H", "4.1", "r1_ident", R_IDENT),
    ("P", "Os 29 pontos extraídos cobrem θ* de 42,909° a 193,017°, isto é, elevação de 180,1° a 30,0°; o "
          "maior valor, 147,310 u.p., ocorre em θ* = 123,196° (elevação de 99,8°). A Tabela 7 reúne os "
          "parâmetros não publicados pela patente, com seus valores congelados e a situação de cada um."),
    ("K", 403, 406),
    ("P", "Com h = 22,701 mm e θ_{off} congelados, a varredura de X_{pose} com K dado pela Equação (29) "
          "reproduz o par identificado: X_{pose} = 37,383 mm, K = 174,676 e RMSE de 1,8305 u.p. A origem "
          "de H_{CAL}, ao contrário, não pôde ser reproduzida. Numa análise complementar, em que "
          "X_{pose} e K são reidentificados para cada h, o RMSE tem mínimo interior em h ≈ 24,0 mm, com "
          "RMSE de 1,682 u.p., e fica abaixo de 2 vezes o mínimo de h = 19,25 a 31,00 mm: com K e a "
          "extensão na pose livres, a curva extraída não determina h. Por isso, H_{CAL} é tratado como "
          "parâmetro congelado de origem não reproduzida; ele é mantido porque o par (K, X_{pose}) foi "
          "identificado nesse valor e porque o ponto morto correspondente, na elevação de 30,485°, fica a "
          "0,485° do início da zona neutra indicado na patente."),
    ("P", "A formulação sem o arco alcança RMSE de 1,152 u.p. no mesmo h, contra 1,830 u.p. com o caminho "
          "completo. Ela ajusta melhor a curva publicada, mas viola a conservação de energia e não foi "
          "adotada: o menor RMSE não é critério de validade física."),
    ("P", "A Figura 8 sobrepõe o torque calculado com os parâmetros congelados aos 29 pontos extraídos. O "
          "ajuste tem RMSE de 1,8305 u.p., equivalente a 1,24% do maior valor extraído, erro absoluto "
          "médio de 1,5866 u.p., 1,94% da média dos valores extraídos, erro máximo de 3,3712 u.p., em "
          "θ* = 42,909°, e coeficiente de determinação de 0,99839."),
    ("K", 413, 415),
    ("P", "A forma do perfil é reproduzida com fidelidade, com duas ressalvas: os quatro parâmetros não "
          "publicados foram identificados contra os mesmos 29 pontos usados na avaliação, de modo que a "
          "aderência não constitui validação independente do modelo, e a incerteza da extração não é "
          "conhecida. Os resíduos não se distribuem aleatoriamente: ordenados por θ*, formam três zonas "
          "extensas de sinal alternado, que reúnem 25 dos 29 pontos. O modelo superestima o torque acima "
          "de 155° de elevação e entre 45° e 94° e o subestima entre 100° e 150°, o que indica diferença "
          "sistemática de forma entre o modelo e a curva, e não apenas dispersão de digitalização. No "
          "último ponto, além do ponto morto calculado (θ*_{pm} = 192,532°), o modelo prevê torque de "
          "−1,709 u.p., com sinal invertido, e a curva extraída registra 0,443 u.p., diferença coerente "
          "com a ausência, no modelo, da protuberância do dispositivo real."),
    ("H", "4.1", "r1_comp", R_COMP),
    ("P", "Na faixa de operação, a extensão da mola vai de 12,044 mm a 54,479 mm, valor que ocorre no "
          "ponto morto, e permanece positiva: o cabo continua tracionado em todos os pontos avaliados. A "
          "razão de 1,0095 entre a extensão máxima e o comprimento livre, de 53,967 mm, significa que a "
          "mola precisaria ser estendida a aproximadamente o dobro de seu comprimento livre. O braço de momento cresce de 12,451 mm em "
          "θ* = 42,917° até o teto |OA| = 22,919 mm em θ* = 97,894° e decresce a partir daí, anulando-se "
          "no ponto morto, em θ* = 192,532° (elevação de 30,485°)."),
    ("P", "A força máxima K δ_{máx} vale 9.516,5 na unidade de K multiplicada por milímetro. Se a ordenada "
          "da patente estivesse em N·m, K estaria em N/mm, a tração no cabo chegaria a 9,5 kN e o pico do "
          "torque do cabo, 147,07 N·m, seria 13,2 vezes o pico do torque gravitacional do conjunto; para "
          "equilibrar esse pico com o maior braço disponível, bastaria uma tração de cerca de 487 N. A "
          "leitura da ordenada em N·m conduz, portanto, a valores implausíveis para um dispositivo "
          "vestível, e a curva publicada é tratada como qualitativa quanto à magnitude: o modelo "
          "reproduz a forma do torque, mas não sua escala física."),
    ("P", "Na varredura de h com K congelado, o menor RMSE, 1,8270 u.p., ocorre em h = 22,735 mm, a "
          "0,034 mm de H_{CAL}, e o RMSE não excede 1,01 vez o mínimo num intervalo de 0,145 mm. Essa "
          "precisão não é identificação independente de h: K e X_{pose} foram identificados no próprio "
          "H_{CAL}, de modo que a proximidade é esperada por construção. Os critérios de fechamento e de "
          "trabalho virtual foram atendidos em todos os 10.402 valores de h, e o critério decisivo é a "
          "tração: com X_{pose} congelada, o aumento de h rebaixa a extensão mínima, que se anula na "
          "fronteira de tração, h = 32,886 mm. A cota do CAD, H_{CAD} = 34,785 mm, fica fora do intervalo "
          "viável: o cabo afrouxaria no início da faixa, com extensão mínima de −2,257 mm, e o RMSE seria "
          "de 43,48 u.p. (Tabela 12)."),
    ("K", 451, 453),
    ("P", "As duas posições da ancoragem são grandezas distintas: H_{CAD} é a cota do desenho, e H_{CAL}, "
          "o parâmetro que, com K e X_{pose}, reproduz a curva extraída e põe A 12,084 mm abaixo, sobre a "
          "mesma perna h. Nenhuma das duas concordâncias é verificação independente, e os dados "
          "disponíveis não decidem qual das duas posições corresponde ao dispositivo."),
    ("H", "4.1", "r1_grav", R_GRAV),
    ("P", "O torque gravitacional do conjunto, calculado pela Equação (26) de forma independente da cadeia "
          "do cabo, atinge o máximo de 11,1619 N·m na elevação de 89,44°. Como a ordenada da curva "
          "publicada não tem unidade declarada, as magnitudes não são comparáveis, e o que se confronta é "
          "a forma dos perfis, normalizados pelos respectivos valores de pico (Figura 11); o confronto "
          "não informa que fração do torque gravitacional o mecanismo compensa."),
    ("K", 461, 464),
    ("P", "O pico do torque do cabo ocorre na elevação de 97,484°, e o do torque gravitacional, em "
          "89,438°, com defasagem de 8,046°: o mecanismo entrega sua assistência máxima acima da posição "
          "de maior demanda gravitacional. As curvas normalizadas cruzam-se na elevação de 93,96° e, entre 105° e 150°, "
          "diferem em no máximo 0,027. Abaixo de 94°, as diferenças tornam-se negativas e crescentes em "
          "módulo, até −0,520 na elevação de 30°; no ponto morto, o torque gravitacional ainda vale "
          "5,757 N·m, 51,6% de seu pico, enquanto o torque do cabo se anula. Trata-se de característica "
          "da arquitetura, e não de deficiência do ajuste (seção 2.3)."),
    ("P", "O confronto ilustra a limitação apontada por Nasr, Ferguson e McPhee (2022): um mecanismo "
          "passivo entrega torque determinado para cada ângulo, de modo que o ajuste favorável em uma "
          "faixa implica desvio em outra. No caso analisado, o compromisso privilegia a faixa acima da "
          "horizontal, onde a exposição postural concentra o risco documentado por van der Molen et al. "
          "(2017) e Seidler et al. (2020), à custa de subcompensação na faixa inferior."),
    ("H", "4.1", "r1_lim", R_LIM),
    ("P", "O modelo não representa a protuberância que, no dispositivo real, restringe o gerador de força "
          "além do ponto morto; em consequência, prevê inversão de sinal do torque nos 0,485° finais da "
          "faixa, onde o dispositivo mantém torque residual aproximadamente nulo. A ausência de unidade "
          "declarada na ordenada da curva publicada impede a conversão do torque do cabo para N·m e o "
          "cálculo do torque resultante sobre a articulação; essa conversão exige dado independente, "
          "como a especificação de rigidez de uma mola comercial compatível com o mecanismo. A "
          "identificação foi reproduzida apenas em parte: a origem de θ_{off} e de H_{CAL} não pôde ser "
          "reconstituída, e os quatro parâmetros foram identificados e avaliados contra os mesmos 29 "
          "pontos, cuja incerteza de extração não está documentada. O fator de escala propaga-se a todas "
          "as grandezas dimensionais e de massa, e os resultados referem-se ao indivíduo de referência, "
          "com o membro superior estendido e sem ferramenta na mão."),
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
          "difere do comprimento medido s_{pose} em 1,4 × 10^{−4} mm, valor inferior à resolução da "
          "medida. O elemento 78 está a p = 7,754 mm do eixo da articulação, enquanto a patente prefere "
          "esse elemento sobre o eixo (seção ⟦S:r2_grav⟧)."),
    ("K", 485, 488),
    ("P", "O braço do exoesqueleto (elemento 8) tem, no CAD, massa de 163,951 g e centro de massa a "
          "47,362 mm do eixo da articulação 20, estimativas obtidas da geometria reconstruída e de um "
          "material atribuído no CAD, e não propriedades do produto. Nas verificações da seção "
          "⟦S:m2_verif⟧, os resíduos são da ordem do erro de arredondamento, de até 5,7 × 10^{−14} mm nas "
          "equações de fechamento dos dois regimes, exceto os do trabalho virtual, de até "
          "5,0 × 10^{−8} mm/rad, limitados pelo truncamento da diferença finita. No teste sintético, a "
          "identificação pelo espaçamento entre as curvas recupera os valores de s_{0} com erro máximo de "
          "0,074 mm."),
    ("H", "4.2", "r2_ident", R_IDENT),
    ("P", "Foram extraídos 48 pontos da curva tracejada, 47 da pontilhada e 51 da contínua, que cruzam "
          "zero em 14,24°, 14,36° e 14,23°. Pela Equação (52), na faixa adotada, s_{0} vale 311,148 mm na "
          "curva pontilhada, 300,750 mm na tracejada e 291,956 mm na contínua, com RMSE de 0,194 mm nas "
          "234 equações. A ordem coincide com a das pré-tensões descritas na patente, porque menor s_{0} "
          "significa maior extensão do elástico em qualquer ângulo. O modelo adota o s_{0} da curva "
          "tracejada, de pré-tensão intermediária. A identificação é estável: entre as faixas de θ_{el} "
          "testadas, o s_{0} da curva tracejada varia de 299,81 a 301,95 mm, e o ruído de extração dá "
          "desvio padrão de 0,772 mm nessa curva."),
    ("P", "As três estimativas do fator G coincidem (Figura 12(a)), com dispersão "
          "mediana de 0,84% entre 20° e 165°. O fim da curva pontilhada confirma o resultado de forma "
          "independente: a razão dessa curva, extrapolada, chega a zero em 171,19° com os dois últimos "
          "pontos, onde s = 309,75 mm, a 1,40 mm do s_{0} identificado pelo espaçamento. O início das "
          "curvas, perto de 14°, não identifica s_{0}, mas é explicado pelo contato do elástico com o "
          "elemento 78: com o elemento sobre o eixo, configuração preferida pela patente, o contato "
          "calculado ocorre em 13,35°, a 0,93° do início médio das curvas; com o elemento do CAD, a "
          "7,754 mm do eixo, o contato ocorre em 24,55°, e o torque não se anula abaixo dele."),
    ("K", 508, 511),
    ("P", "Com esses valores de s_{0}, o fator G lido na Figura 16 da patente e a forma m/(1000 τ_{g}) "
          "prevista pelo modelo diferem (Figura 12(b)): normalizada em 90°, a razão entre os dois vale "
          "0,26 em 20°, 0,79 em 60°, 1,34 em 120° e 2,94 em 165°. Em consequência, a razão calculada não "
          "reproduz a Figura 16 da patente: com escala comum às três curvas, o coeficiente de "
          "determinação é −0,417 (pontilhada), −1,529 (tracejada) e −0,620 (contínua). Como o s implícito "
          "na figura concorda com o do CAD, com diferença de 0,84 mm RMS, a causa não é s nem, como causa "
          "principal, o braço de momento, que depende da derivada de s; ela aponta para o torque do peso "
          "usado pela patente ou para a definição da ordenada, que a patente não permite separar."),
    ("P", "O ajuste de forma, que deixa s_{0} e a escala livres em cada curva, absorve essa diferença em "
          "s_{0}. Os valores que ele encontra, 294,34 mm na pontilhada, 213,40 mm na tracejada e 0,00 mm "
          "na contínua, o limite inferior da busca, afastam-se dos do espaçamento, e as escalas por curva "
          "contrariam o atuador único descrito na patente. São mantidos como resultado secundário."),
    ("H", "4.2", "r2_comp", R_COMP),
    ("P", "Na faixa de 0° a 180° de anteversão, o regime II ocupa θ_{el} de 0° a 24,549°. O braço de "
          "momento permanece positivo em toda a faixa, com mínimo de 6,142 mm na transição e máximo de "
          "34,785 mm em θ_{el} = 109,2°, igual a |OP|; como m não se anula, não há ponto morto na faixa. "
          "Com s_{0} = 300,750 mm, a extensão do elástico vai de 78,10 mm com o braço pendente a 7,20 mm "
          "em 180°, e o elástico permanece tracionado em toda a faixa. A deformação máxima equivale a "
          "26,0% do comprimento de referência, e, com K = K_{40}, a força vai de 199,15 N a 18,35 N."),
    ("P", "Na varredura de e_{c}, o fechamento dos dois regimes e o trabalho virtual foram atendidos em "
          "todos os valores, e a extensão não negativa do elástico em toda a faixa só é atendida para "
          "e_{c} ≤ 42,20 mm: acima desse valor, com o s_{0} adotado, o elástico afrouxa perto de 180°. "
          "Entre e_{c} = 25 mm e e_{c} = 45 mm, a transição de regime ocorre mais cedo, e o pico do "
          "torque se desloca de 82,4° para 77,0°. A Figura 17 da patente não foi digitalizada, e a "
          "comparação com ela ficou restrita à inspeção visual."),
    ("H", "4.2", "r2_grav", R_GRAV),
    ("P", "A forma do torque do elástico pode ser comparada à do peso sem depender de K, normalizando "
          "cada curva pelo próprio pico (Figura 14). Com o s_{0} adotado, o pico normalizado do elástico "
          "ocorre em θ_{el} = 79,1°, contra 89,8° do peso. Entre 48,40° e 83,74°, a forma do elástico fica "
          "ligeiramente acima da do peso, com no máximo +0,039; entre 83,74° e 177,02°, fica abaixo, com "
          "diferença de até −0,272 em 139,2°. A posição do pico fica na faixa de 70° a 120° em que a "
          "patente prefere a força máxima, lida aqui como a força de apoio sobre o braço, proporcional "
          "ao torque na articulação."),
    ("K", 543, 545),
    ("E", 546, [(" da Tabela 31, no Apêndice A.", " testadas na identificação.")]),
    ("P", "Em N·m, a comparação só é possível sob a hipótese K = K_{40}, e por isso a Tabela 20 descreve "
          "um cenário de projeto, e não o dispositivo comercial. Nesse cenário, o torque do elástico "
          "atinge 4,379 N·m em θ_{el} = 79,1°, 10,7° abaixo do pico de τ_{g}. Abaixo da transição, o "
          "modelo mantém torque positivo, porque o elemento 78 está a 7,754 mm do eixo, ao passo que a "
          "Figura 16 da patente mostra razão nula abaixo de cerca de 14°; a divergência foi mantida no "
          "modelo, porque depende da posição real do elemento 78 e de seu raio de contato, que não estão "
          "documentados."),
    ("K", 548, 551),
    ("P", "Com o s_{0} das outras duas curvas, K_{40} vai a 3,20932 e 2,17230 N/mm, e o pico de τ, a "
          "4,516 N·m em 75,5° e 4,317 N·m em 81,7°: a distribuição angular da assistência depende da "
          "curva tomada como referência. O resultado ilustra a limitação discutida na seção 2.4 (NASR; "
          "FERGUSON; McPHEE, 2022): no modelo, a subcompensação recai sobre a faixa acima da horizontal. "
          "Como essa forma depende da geometria do CAD, que não reproduz a Figura 16 da patente, a "
          "leitura vale para o modelo."),
    ("H", "4.2", "r2_lim", R_LIM),
    ("P", "A principal ressalva é a diferença de forma entre o modelo e a Figura 16 da patente: o s_{0} "
          "identificado pelo espaçamento entre as curvas não depende dessa forma, mas a distribuição "
          "angular do torque calculado, sim. O torque em N·m é um cenário, e não uma medida: a patente "
          "não publica a rigidez do elástico nem a escala da ordenada, e K = K_{40} vem da alegação "
          "comercial de 40% de assistência (SUITX, [202-]), sem verificação independente. As comparações "
          "angulares com a patente dependem da hipótese de eixo da articulação 20 no centro do ombro e "
          "barra 18 fixa no tronco, e o trecho abaixo da transição depende da posição e do raio de "
          "contato do elemento 78. As grandezas medidas no CAD não têm conferência independente, e os "
          "resultados referem-se ao membro de referência, num modelo plano."),
]

EXO3_R = [
    ("K", 566),
    ("E", 567, [(" As etapas dinâmicas da seção 3.3.13 não foram executadas.", "")]),
    ("H", "4.3", "r3_geo", R_GEO),
    ("K", 569, 572),
    ("P", "Com esses valores, o fechamento tem resíduo de 0,0006 mm. Na imagem da folha 21, a pose da "
          "Figura 14D dá q = 61,19°, contra 61,724° no CAD, e o ponto A do CAD fica a 0,3 mm do 562 "
          "desenhado: a pose do CAD é a da Figura 14D. O came "
          "desenhado nas duas figuras é o contorno externo da Figura 15A; ajustado ao desenho, ele dá "
          "R_{20} = 31,96 mm na Figura 14C e 32,11 mm na 14D, e adotou-se R_{20} = 32,035 mm. Do came da "
          "14C para o da 14D, o giro absoluto medido é de 61,3°, e a cinemática do cabo 560 prevê 76,8°: "
          "a diferença, 15,5°, mostra que os dois desenhos não são exatamente coerentes entre si."),
    ("K", 576),
    ("L", 577, [4, 5, 6, 7, 8, 9, 10, 11]),     # sem as linhas de braço, antebraço e mão, iguais às da Tabela 14
    ("K", 578, 579),
    ("P", "A amplitude do torque gravitacional é M g d = 10,55 N·m para o membro e 11,45 N·m para o "
          "conjunto. Nas verificações da seção ⟦S:m3_verif⟧, os "
          "resíduos da cadeia de cálculo são da ordem do erro de arredondamento, exceto o do trabalho "
          "virtual, com diferença relativa de 1,8 × 10^{−5}, limitado pelo truncamento da diferença "
          "finita, e os do fechamento com o CAD, limitados pela resolução da medida."),
    ("H", "4.3", "r3_ident", R_IDENT),
    ("P", "Da Figura 16 da US 9.737.374 B2 foram extraídos 106 pontos de cada curva. A AASM tem máximo de "
          "75,55 em Θ = 1° e fica acima de 95% dele de −20° a 9°, o trecho de sustentação quase constante "
          "que a patente atribui à Z11. A AWM é um cosseno puro, −78,22 cos Θ, e AASM/|AWM| vale 0,96 na "
          "horizontal. No perfil do came (Figura 7), o raio é constante na Z10 e cai continuamente na "
          "Z11, de 0,961 para 0,663 R_{20}; usar ρ no lugar de r superestimaria o momento da mola em até "
          "12% na Z11 e em até 49% na Z12."),
    ("P", "Com o giro do came da Figura 14D, o ajuste da Equação (67) nos 97 pontos de Θ = −75° a 21°, "
          "abaixo do limite de subida, dá k = 0,492 N/mm e x_{0} = 323,6 mm, e a mola trabalha de 158 N em "
          "−75° a 114 N em 21°. A Tabela 26 resume esse ajuste, o que soma o peso do apoio de braço ao "
          "alvo, o do melhor giro da seção ⟦S:r3_comp⟧ e, para comparação, o da escala do artigo de "
          "Okabe, Brittes e Brito (2026)."),
    ("K", 601, 603),
    ("P", "Com o giro do came da Figura 14D, o ajuste tem R^{2} = 0,901, erro quadrático médio de "
          "0,91 N·m e erro máximo de 1,69 N·m (Figura 16a). A força que reproduziria a curva AASM não é "
          "linear no alongamento (Figura 16b): uma mola linear acompanha a forma geral da curva, mas não "
          "o início da subida nem o patamar, e o ajuste contra a mesma curva não constitui validação "
          "independente. As marcas das zonas não entram no ajuste e servem de conferência: com esse giro, "
          "a Z11 do modelo tem largura parecida com a da marca da patente, 28,4° contra 27,8°, mas fica "
          "22,9° abaixo dela."),
    ("K", 606, 608),
    ("H", "4.3", "r3_comp", R_COMP),
    ("P", "Da pose do CAD (Θ = −88,47°) até o limite de subida, em Θ = 22,01°, o braço de momento do cabo "
          "560 cresce de 26,04 mm para 63,26 mm em Θ = 0 e fica positivo em toda a faixa, e o raio efetivo "
          "do came vai de 10,55 mm na pose a 32,08 mm na horizontal. A transmissão τ/F_{s}, em N·mm por "
          "N, passa de 17,42 mm em Θ = −75°, onde começa a curva da patente, a 76,75 mm na horizontal, "
          "isto é, é multiplicada por 4,4: o came responde por parte disso, e o cabo de ancoragem, pelo "
          "resto."),
    ("P", "Repetido o ajuste com o came girado de −120° a +40° em relação ao desenho (Figura 18a), o cabo "
          "da mola sai do canal em toda a faixa entre −86° e +40°. Nessa faixa, o melhor resultado com k "
          "e x_{0} positivos ocorre com o came girado de −49°: R^{2} = 0,953, k = 2,053 N/mm e "
          "x_{0} = 121,2 mm (Figura 18b). Com esse giro, a Z11 do modelo vai de −22,7° a 2,4°, e a saída "
          "na Z12 ocorre de −53,2° a −51,2°: as duas ficam dentro das marcas da patente, que não entram "
          "no ajuste. O ajuste da mola e as marcas das zonas indicam o mesmo giro, o que sugere que a "
          "curva da patente corresponde a uma montagem diferente da desenhada nas Figuras 14C e 14D."),
    ("K", 622, 624),
    ("P", "Os furos em torno do pino 572 reforçam essa leitura. Os cinco têm passo médio de 25,31° e "
          "ocupam quase a mesma posição no came nas duas figuras; portanto, giram com ele, e as nove "
          "montagens vão de −101,25° a +101,25° (Tabela 28). A de dois furos no sentido horário, a "
          "−50,62°, fica a 1,6° do melhor giro contínuo e reproduz a curva da patente com R^{2} = 0,953 "
          "e k = 2,119 N/mm, contra R^{2} = 0,901 da montagem desenhada. Com a mesma mola e o mesmo cabo, "
          "a troca de furo desloca o máximo do torque de Θ = −24,4° a 17,4°, e, entre as montagens "
          "anti-horárias, as de +2 a +4 furos só melhoram o ajuste com rigidez negativa, sem mola "
          "física. A patente não diz em que furo o came estava quando a Figura 16 da US 9.737.374 B2 foi "
          "gerada."),
    ("K", 628, 630),
    ("R", 631, "Nota: giro positivo no sentido anti-horário, na vista das Figuras 14C e 14D; pares: furos "
               "do came e da polia que coincidem. Mesma mola: k = 0,492 N/mm e x_{0} = 323,6 mm. Outra "
               "mola: k e x_{0} ajustados à Figura 16 da US 9.737.374 B2 em cada montagem; k negativo não "
               "corresponde a mola física. Nas montagens de −4, +3 e +4 furos, o cabo da mola sai do canal "
               "em parte da faixa do ajuste, e os R^{2} não foram calculados."),
    ("H", "4.3", "r3_grav", R_GRAV),
    ("P", "Pela Equação (64), o torque gravitacional do conjunto chega a 11,45 N·m em Θ = −0,6°; na "
          "horizontal, o membro responde por 10,55 N·m, e o apoio de braço, por 0,90 N·m, 9% do membro. "
          "Nos ângulos marcados na Figura 16 da US 9.737.374 B2, a AASM, na escala da AWM, fica entre "
          "0,53 e 0,89 vezes τ_{g}, e o modelo ajustado, entre 0,71 e 0,88 vezes. Na horizontal, a AASM sustenta 96% do peso do membro, a razão "
          "AASM/|AWM| da própria patente, e 89% do peso do conjunto. Os picos quase coincidem em ângulo: "
          "a AASM tem máximo em Θ = 1°, τ_{g} em −0,6° e o modelo ajustado em −4,6°."),
    ("P", "O artigo de Okabe, Brittes e Brito (2026) adotou outra escala, com o máximo da AASM em 30 N·m, "
          "2,94 vezes a adotada aqui. Nela, a AWM valeria 31,06 N·m na horizontal, 2,9 vezes o torque do "
          "peso do membro de referência: a escala do artigo corresponde a uma carga entre duas e meia e "
          "três vezes o peso do membro. O ajuste nessa escala tem o mesmo x_{0} e o mesmo R^{2}, com "
          "k = 1,448 N/mm."),
    ("H", "4.3", "r3_lim", R_LIM),
    ("P", "A principal ressalva é a escala. A ordenada da Figura 16 da US 9.737.374 B2 não tem unidade, e "
          "a escala adotada supõe que a AWM seja o momento do peso do membro de referência, sem "
          "ferramenta na mão e sem o apoio de braço; o torque em N·m e a rigidez k valem nessa escala, e "
          "k e x_{0} foram identificados pela forma da curva, e não medidos. A curva calculada depende do "
          "giro do came em relação à primária, em que as Figuras 14C e 14D discordam em 15,5°, e as "
          "montagens do came supõem na polia os furos medidos nas figuras. Com a ancoragem 562 na posição "
          "do CAD, o braço não sobe além de Θ = 22,0°, enquanto a curva da patente vai até 30°. As "
          "leituras do perfil do came e da curva de momento não têm incerteza estimada."),
]

CAP4_FIM = [
    ("K", 649, 653),
    ("P", "O contraste mais útil para o procedimento está na identificação. Uma única curva sem unidade, "
          "como a da US 9.889.554 B2, fixa a forma do perfil, e o ajuste de quatro parâmetros contra os "
          "mesmos 29 pontos reproduz essa forma sem constituir validação independente. As três curvas da "
          "EP 3 504 033 B1 trazem uma redundância que separou o comprimento de referência do elástico, "
          "determinado pelo espaçamento entre elas, da forma do perfil, e essa separação revelou uma "
          "diferença de forma que o ajuste de uma curva isolada teria escondido no valor de s_{0}. Na "
          "US 9.737.374 B2, a forma depende também do perfil do came e de um giro que os desenhos não "
          "fixam com precisão; as marcas das zonas, que não entram no ajuste, apontam o mesmo giro que "
          "melhora o ajuste da mola."),
    ("P", "Os mecanismos também distribuem a assistência de modo distinto em relação à demanda "
          "gravitacional. O gerador da US 9.889.554 B2 concentra o torque acima da horizontal; a forma "
          "normalizada do elástico na EP 3 504 033 B1, que depende da geometria do CAD, fica abaixo da do "
          "peso entre 84° e 177°; e, na US 9.737.374 B2, o máximo da curva da patente quase coincide com o "
          "do torque do peso. A comparação é quantitativa quanto aos ângulos e à forma dos perfis, mas "
          "não quanto à magnitude, que depende de hipótese nos três."),
]

# ====================================================================== capítulo 5
CAP5 = [
    ("K", 656, 658),
    ("P", "Este trabalho reconstruiu, a partir da documentação de patente, o gerador de torque de mola da "
          "US 9.889.554 B2 e formulou um modelo estático do torque que ele entrega em função do ângulo, "
          "com a cinemática resolvida em forma fechada e cada etapa conferida por verificações internas "
          "de consistência. O princípio dos trabalhos virtuais mostrou-se o critério decisivo na "
          "formulação: revelou que a extensão da mola deve acompanhar o caminho completo do cabo, "
          "ℓ = s − Rψ, e não apenas o vão livre, que violava a conservação de energia com resíduo de "
          "1,71 mm/rad, e distinguiu o braço de momento perpendicular, limitado a 22,919 mm, da distância "
          "do pivô ao ponto de tangência, próxima de 283 mm, cuja confusão superestimaria o torque por um "
          "fator superior a 12."),
    ("K", 661),
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
    ("P", "Para a EP 3 504 033 B1, o espaçamento entre as três curvas da Figura 16 da patente determina os "
          "comprimentos de referência do elástico sem depender da escala da ordenada, da rigidez, do "
          "braço de momento ou do torque do peso: 311,15 mm na curva pontilhada, 300,75 mm na tracejada e "
          "291,96 mm na contínua. O fim da curva pontilhada, de pré-tensão quase nula, confirma o "
          "resultado de forma independente, e o início das curvas, perto de 14°, fica a 0,9° do contato "
          "calculado com o elemento de encosto sobre o eixo, em 13,35°, configuração preferida pela "
          "patente."),
    ("P", "A forma do torque prevista com a geometria do CAD e o peso do membro humano não reproduz as "
          "curvas da patente: o fator comum às três curvas difere do previsto por um fator que vai de "
          "0,26 em 20° a 2,94 em 165°, normalizado em 90°. Como o s implícito na figura concorda com o do "
          "CAD, a diferença vem, mais provavelmente, do torque do peso usado pela patente para formar a "
          "razão ou da definição da ordenada, que a patente não permite separar. A rigidez não é "
          "identificável pela figura. Sob a hipótese de assistência de 40% do torque do peso em 90°, "
          "K = 2,550 N/mm, e o torque atinge 4,379 N·m em 79,1°, dentro da faixa de 70° a 120° em que a "
          "patente prefere a força máxima, com razão τ/τ_{g} de 0,32 em 30°, 0,43 em 60°, 0,40 em 90° e "
          "0,21 em 150°."),
    ("E", 673, [("o item h foi cumprido na parte estática, com três ressalvas",
                 "o item f foi cumprido, com três ressalvas"),
                ("O item i foi cumprido", "O item g foi cumprido"),
                (" As etapas dinâmicas não foram executadas, pelas razões da seção 3.2.13.", "")]),
    ("P", "Como continuidade para esse dispositivo, recomenda-se obter a curva de força e extensão do "
          "elemento elástico, que fixaria K e a escala do torque."),
    ("K", 675),
    ("E", 677, [("A pose do CAD é a da Figura 14D, o ponto de ancoragem do CAD fica a menos de 1 mm do "
                 "desenhado, e as peças do apoio de braço concordam com o desenho: as polias nos pinos, o "
                 "came com o giro da figura e a mola sobre a mola 636. O mecanismo molda",
                 "O mecanismo molda")]),
    ("P", "Com o giro do came desenhado, uma mola linear reproduz a forma da curva AASM com "
          "R^{2} = 0,901; com o came girado de −49°, R^{2} = 0,953, e as zonas Z11 e Z12 do modelo ficam "
          "dentro das marcas da Figura 16 da US 9.737.374 B2. Os cinco furos em torno do pino 572 "
          "permitem nove montagens do came; a de dois furos no sentido horário, a −50,6°, reproduz a "
          "curva com R^{2} = 0,953, a 1,6° do melhor giro. A curva da patente parece corresponder a outra "
          "montagem do came, e a ancoragem desenhada limita a subida a Θ = 22,0°, contra 30° na curva."),
    ("P", "A rigidez não é identificável pela AASM sozinha, que não tem unidade, mas a AWM da própria "
          "patente, igualada ao peso do membro de referência, fixa a escala. Nela, k = 0,492 N/mm, e a "
          "mola trabalha de 158 a 114 N. O apoio de braço tem 0,796 kg e acrescenta 9% ao torque do peso "
          "do membro com o braço na horizontal, onde a AASM sustenta 96% do peso do membro e 89% do peso "
          "do conjunto. A escala de 30 N·m do artigo de Okabe, Brittes e Brito (2026) é 2,9 vezes maior."),
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
