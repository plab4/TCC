"""
Mudanças da versão revisada para a defesa, aplicadas por tcc/gerar_revisado.py
sobre o DOCX fundido de base e conferidas por tcc/verificar_revisao.py.

MUDANCAS: lista de ("R", chave, novo) e ("T", antes, depois); ver gerar_revisado.
GLOBAIS:  trocas por expressão regular nos capítulos 3 a 5 e no apêndice.
EXCECOES: para cada parágrafo (chave = início do texto original) em que um número,
uma sigla ou um símbolo em itálico aparece ou desaparece, o que muda e o motivo.
RESUMO e ABSTRACT: texto dos ambientes de latex/resumo.tex na versão revisada
(None mantém o da base).

Regras seguidas na redação:
- os capítulos 1 e 2 não são alterados (instrução do autor);
- nenhum valor numérico, hipótese ou resultado é alterado; correções de conteúdo
  só entram quando a origem foi verificada, e ficam em EXCECOES;
- sem travessões; sem remissões a tarefas internas; sem "autor" em terceira pessoa
  no corpo do texto (as linhas de fonte das figuras e tabelas seguem a ABNT).
"""

ALTERAR_CAP_1_2 = False

# meia-risca entre palavras (braço–exoesqueleto, pivô–tambor) → hífen, que é a
# grafia do Acordo Ortográfico para encadeamentos vocabulares
GLOBAIS = [
    (r"(?<=\w)–(?=\w)", "-"),
]

MUDANCAS = [
    # ------------------------------------------------------------------ capítulo 3, abertura
    ("R", "O trabalho é teórico-computacional. O procedimento parte",
     "O trabalho é teórico-computacional. O procedimento parte da reconstrução geométrica do "
     "mecanismo e chega ao torque estático que ele entrega em função do ângulo, passando pela "
     "identificação dos parâmetros que a patente não publica. Ele foi aplicado, na parte "
     "estática, a três mecanismos: o gerador de torque da US 9.889.554 B2 (seções 3.1, 4.1 e "
     "5.1), o dispositivo da EP 3 504 033 B1 (seções 3.2, 4.2 e 5.2) e o mecanismo de came da "
     "US 9.737.374 B2 (seções 3.3, 4.3 e 5.3). As seções 3.1.9, 3.2.9 e 3.3.9 formulam os três "
     "modelos estáticos pelo princípio dos trabalhos virtuais, e as seções 3.4, 4.4 e 5.4 "
     "comparam os três."),

    # ------------------------------------------------------------------ 3.1
    ("T", "grandezas geométricas do mecanismo — distância do pivô",
          "grandezas geométricas do mecanismo (distância do pivô"),
    ("T", "defasagem angular do desenho —, a pose de referência",
          "defasagem angular do desenho), a pose de referência"),
    ("T", "para uniformizar, a curva calculada comparada à da patente foi adotada −τ.",
          "por isso, a curva calculada que se compara à da patente é −τ."),
    ("T", "A formulação original do autor para essa distância, obtida pela lei dos cossenos,",
          "A primeira formulação dessa distância, obtida pela lei dos cossenos,"),
    ("T", "Na formulação original do autor, o mesmo ponto é obtido",
          "Na primeira formulação, o mesmo ponto é obtido"),
    ("T", "parcela variável do enrolamento, um arco constante cancela-se",
          "parcela variável do enrolamento: um arco constante cancela-se"),
    ("T", "em função de h, formulação original do autor aqui escrita com a notação desta seção:",
          "em função de h, que vem da primeira formulação e é escrita aqui com a notação desta seção:"),
    ("T", "é a curva torque × ângulo, Figura 56 do gerador de torque publicada na US 9.889.554 B2, da qual",
          "é a curva torque × ângulo do gerador de torque, Figura 56 da US 9.889.554 B2, da qual"),

    # ------------------------------------------------------------------ 3.2
    ("R", "As seções 3.2.1 a 3.2.14 aplicam à EP 3 504 033 B1",
     "As seções 3.2.1 a 3.2.14 aplicam à EP 3 504 033 B1 (MIZERA et al., 2023), da Ottobock, o "
     "procedimento deste capítulo, com a classificação de origem da seção 3. A cadeia de cálculo "
     "das seções 3.2.3 a 3.2.8 está implementada no arquivo torque_model_ottobock.py, e os números "
     "e as figuras da seção 4.2 são produzidos pelo script tcc_resultados_ottobock.py, que não "
     "altera parâmetro algum do modelo. As únicas identificações são as descritas na seção 3.2.10."),
    ("R", "O circuito do mecanismo foi fechado no modelo em CAD do Autodesk Fusion",
     "O circuito do mecanismo foi fechado no modelo em CAD, feito no Autodesk Fusion, e as "
     "grandezas medidas nesse modelo, com as que delas derivam, estão na Tabela 13 (seção 4.2.1). "
     "O critério de escala do modelo não foi registrado, e as medições não têm, por isso, "
     "conferência independente. A planilha de composição inercial identifica o modelo como "
     "Ottobock iX Shoulder Air; como a patente não nomeia o produto, a correspondência entre "
     "esse produto, o modelo em CAD e os desenhos da patente não está documentada. Por isso, as "
     "grandezas são tratadas como medidas em CAD, na classificação da seção 3, e não como "
     "dimensões do dispositivo comercial."),
    ("T", "que coincidem com os da planilha do autor", "que coincidem com os da planilha de composição inercial"),
    ("R", "A variável independente é q, a direção da alavanca",
     ["A variável independente é q, a direção da alavanca, representada pelo segmento OP, de "
      "comprimento ‹e› (seção 3.2.4). A anteversão do braço, θ_{el}, com 0° para o braço pendente "
      "e 90° para o braço horizontal à frente, é a abscissa das Figuras 16 e 17 da patente e não "
      "precisa ser convertida em elevação anatômica.",
      "O modelo admite que o giro do elemento de apoio do braço em relação à barra 18 seja igual "
      "à anteversão, o que supõe o eixo da articulação 20 no centro do ombro e a barra 18 fixa em "
      "relação ao tronco. A patente não garante essa condição: situa a articulação na altura do "
      "ombro, na região da escápula e atrás do corpo com o braço pendente, com eixo que não "
      "coincide com o de abdução do ombro, admite que a barra 18 mude de orientação com o "
      "movimento do braço e não informa a relação entre o giro da articulação e a anteversão. As "
      "comparações angulares com as Figuras 16 e 17 da patente dependem, portanto, dessa hipótese.",
      "O eixo do braço aponta na direção θ_{el} − 90°, e q se relaciona com θ_{el} por"]),
    ("R", "O sinal de θb,pose = 7,962° foi conferido no CAD",
     "O ângulo θ_{b,pose} = 7,962° é positivo, como conferido no CAD: na pose, o braço fica acima "
     "da horizontal. O modelo é sensível a esse sinal. Com o sinal oposto, q_{0} seria −11,551° e "
     "θ_{el,pose}, 82,038°, e o contato da seção 3.2.5 passaria de 24,55° para 8,62°; o efeito "
     "sobre s_{0} está na seção 4.2.4. Dois resultados sustentam o sinal adotado: o pino da "
     "alavanca do modelo fica a 1,8 mm do pino do elástico desenhado na Figura 22 da patente com "
     "o braço elevado e a 4,7 mm com o braço baixado (seção 3.2.5), e o espaçamento entre as "
     "curvas fecha com resíduo de 0,194 mm, contra 0,406 mm com o sinal oposto (seção 4.2.4)."),
    ("R", "A ancoragem A do elástico fica na barra 18",
     "A ancoragem A do elástico fica na barra 18, e o ponto P, no pino do rasgo da alavanca "
     "solidária ao braço (Figura 3). No CAD, o elástico prende-se a uma peça de C_{3} = 14,907 mm, "
     "articulada nesse pino e desenhada girada de β_{c} = −49,647°. Por ser articulada, a peça se "
     "alinha ao elástico, e a força age no pino, como na Figura 22 da patente (seção 3.2.5). A "
     "alavanca é, assim, o segmento OP, de comprimento ‹e› = e_{c} = 34,785 mm e direção q; a peça "
     "só entra para fechar o circuito com o comprimento do elástico medido no CAD (seção 4.2.1). "
     "O vetor fixo de A a O e as posições de P e do centro do elemento 78 são"),
    ("R", "As Figuras 16 e 17 da patente são apresentadas como representações exemplares",
     ["As Figuras 16 e 17 da patente são apresentadas como representações exemplares das curvas "
      "de força que o dispositivo pode aplicar ao braço; o documento não informa se foram medidas "
      "ou calculadas, nem a configuração do dispositivo que as gerou. A abscissa é o ângulo de "
      "anteversão, com escala de 0° a 180° e grade a cada 20°. A ordenada não tem rótulo nem "
      "valores, apenas linhas de grade: há cinco divisões acima da linha de razão nula e uma "
      "abaixo (Figura 5).",
      "Segundo a patente, a ordenada da Figura 16 da patente é uma razão de torques: o torque "
      "causado pelo peso próprio do braço e pela força peso, sem indicação do corpo a que esta se "
      "refere, dividido pelo torque aplicado pelo dispositivo. As curvas, porém, partem de zero "
      "perto de 14° e crescem com o ângulo, e com essa definição a razão seria infinita onde o "
      "dispositivo não aplica torque. Das duas leituras como razão, só a inversa, torque do "
      "dispositivo dividido pelo torque do peso, é coerente com a figura, inclusive com a subida "
      "das curvas tracejada e contínua perto de 180°, onde o torque do peso tende a zero. Essa "
      "foi a interpretação adotada, e a divergência entre o texto e a figura fica registrada."]),
    ("R", "Os pontos das três curvas foram extraídos pelo autor",
     "Os pontos das três curvas foram extraídos neste trabalho e estão no arquivo "
     "fig16_curvas.csv (Tabela 15). A extração dividiu a leitura vertical por 21,1311 para obter "
     "a razão em divisões da grade, manteve a abscissa sem correção e teve erro mediano de "
     "sobreposição inferior a 0,5 px; a imagem e a resolução usadas na leitura não foram "
     "registradas. No documento B1, a figura está gravada a 300 ppp, com cerca de 215,7 px por "
     "divisão vertical e 266,2 px para 20° da abscissa. Admitido que o erro de 0,5 px esteja na "
     "unidade da leitura vertical, ele corresponde a 0,024 divisão na ordenada e, na mesma "
     "unidade, a 0,38° na abscissa. A incerteza da extração não foi avaliada de forma "
     "independente; a análise de robustez propaga esse erro mediano à identificação, por sorteio."),
    ("T", "o percentual é hipótese do autor, baseada", "o percentual é hipótese deste trabalho, baseada"),
    ("R", "As verificações estão na Tabela 16: são asserções executadas a cada cálculo",
     "As verificações estão na Tabela 16. São asserções executadas a cada cálculo, com tolerância "
     "declarada, que o interrompem se alguma for violada; não há um conjunto separado de testes "
     "executado com o pytest. Além das equações de fechamento e do trabalho virtual, elas "
     "conferem a continuidade na troca de regime e o caso limite p = 0, e o modelo confere ainda "
     "que o regime II ocorre exatamente para q ≤ q*, que o elemento 78 fica entre A e P na "
     "transição e que toda a cadeia depende de e_{c}. Os valores são de e_{c} = 34,785 mm, com "
     "s_{0} e K do cenário de projeto, em malha de 0,1° de 0° a 180°; a identificação pelo "
     "espaçamento entre as curvas é conferida pelo teste sintético da seção 3.2.10."),

    # ------------------------------------------------------------------ 3.3
    ("R", "As seções 3.3.1 a 3.3.14 aplicam à US 9.737.374 B2",
     "As seções 3.3.1 a 3.3.14 aplicam à US 9.737.374 B2 (DOYLE, 2017), da Levitate, o "
     "procedimento deste capítulo, com a classificação de origem da seção 3. Nesse mecanismo, a "
     "força da mola chega ao ombro por um par de polias, uma delas um came de raio variável, e "
     "por um cabo de ancoragem. A cadeia de cálculo está nos scripts da pasta exo3, que extraem "
     "o perfil do came, resolvem o circuito do cabo de ancoragem, tratam as relações entre o "
     "came e o cabo da mola, medem as poses das figuras da patente e compõem a massa do apoio de "
     "braço. Os números e as figuras da seção 4.3 são produzidos pelo script "
     "tcc_resultados_exo3.py."),
    ("T", "no modelo em CAD do autor, cuja pose é a da Figura 14D",
          "no modelo em CAD deste trabalho, cuja pose é a da Figura 14D"),
    ("T", "O tensor transportado do centro de massa à origem confere com o relatório.",
          "O tensor transportado do centro de massa à origem confere com o relatório de propriedades de massa do CAD."),
    ("T", "O relatório não traz o pivô 584.", "O relatório do CAD não traz o pivô 584."),
    ("T", " No código, τ sai do produto da força", " O torque τ é o produto da força"),
    ("T", ", guardada como transm.", "."),
    ("T", "Esse é o b certo porque o apoio de braço", "É esse o vetor que define o torque, porque o apoio de braço"),
    ("R", "O perfil do canal saiu da Figura 15B",
     "O perfil do canal foi extraído da Figura 15B, um corte pelo plano do canal em que a área "
     "hachurada é o fundo do canal. Na imagem da folha 22, essa área foi isolada pelos vãos "
     "brancos da hachura e completada pelos fragmentos junto ao contorno e pelos entalhes das "
     "cotas. O contorno fechado, centrado no furo 654 (pino 572), foi dividido pelo raio médio da "
     "zona Z10, R20, tomado como referência (Figura 7a). As zonas, localizadas pelas linhas de "
     "chamada das cotas, vão de 89,6° a 140,4° (Z10), de 152,4° a 218,8° (Z11) e de 242,6° a "
     "292,6° (Z12), no referencial da Figura 15B."),
    ("T", "Por decisão do autor, a polia 630 fica fora da varredura",
          "Por simplificação, a polia 630 fica fora da varredura"),
    ("R", "O giro do came em relação à primária é a grandeza menos certa da cadeia",
     "O giro do came em relação à primária é a grandeza menos certa da cadeia, porque os dois "
     "desenhos discordam (seção 4.3.1), e é a que decide em que zona o cabo da mola sai em cada "
     "Θ; por isso, foi o parâmetro varrido. A varredura repetiu o ajuste da seção 3.3.10 com o "
     "came girado de −120° a +40° em relação ao desenho da Figura 14D, de grau em grau, com as "
     "demais grandezas nos valores da Tabela 21. O contorno do came tem um rebaixo, onde fica a "
     "âncora 573, ladeado por duas pontas, e a envoltória convexa atravessa esse rebaixo por um "
     "segmento reto, que não é canal. Por isso, só valem os giros em que o cabo da mola sai do "
     "canal em toda a faixa do ajuste, isto é, em que ele deixa o rebaixo pela ponta de cima e "
     "se enrola no canal até a ponta de baixo. As marcas das zonas na Figura 16 da US 9.737.374 "
     "B2 não entram no ajuste e servem de conferência. Trata-se de diagnóstico, e nenhum "
     "parâmetro é substituído pelo resultado."),
    ("T", "Admitido, como supõe o autor, que a polia externa tem furos correspondentes",
          "Admitido, por hipótese, que a polia externa tenha furos correspondentes"),
    ("T", "entre o chifre de cima e um plano fixo no chassi",
          "entre a ponta de cima do rebaixo e um plano fixo no chassi"),
    ("T", "São asserções e conferências executadas pelos scripts, e não um conjunto de testes executado com o pytest.",
          "São asserções e conferências executadas pelos próprios scripts; não há um conjunto separado de testes "
          "executado com o pytest."),
    ("T", "Nenhum resultado dinâmico é apresentado, e as condições para executar a etapa "
          "estão na seção 4.3.9.", "Nenhum resultado dinâmico é apresentado."),
    ("T", "Foram empregados o modelo em CAD do autor, para fechar", "Foram empregados o modelo em CAD, para fechar"),

    # ------------------------------------------------------------------ 4.1
    ("T", "violando assim, a conservação", "violando, assim, a conservação"),
    ("T", "Primeiro, os quatro parâmetros não publicados", "A primeira é que os quatro parâmetros não publicados"),
    ("T", "A outra é que a incerteza da extração", "A segunda é que a incerteza da extração"),
    ("T", "As causas possíveis: imprecisão da geometria reconstruída, erro sistemático na extração ou diferença entre",
          "As causas possíveis são a imprecisão da geometria reconstruída, um erro sistemático na extração ou uma "
          "diferença entre"),
    ("T", "mas não o suficiente para provar a hipótese.", "mas não basta para confirmá-la."),
    ("T", "muito sensível a h — o RMSE dobra a cerca de 0,9 mm do mínimo e decuplica a cerca de 5,2 mm —, mas não substitui",
          "muito sensível a h (o RMSE dobra a cerca de 0,9 mm do mínimo e decuplica a cerca de 5,2 mm), mas não substitui"),
    ("T", "aumenta o curso do cabo — de 28,942 mm em h = 15 mm para 42,435 mm em h = 22,701 mm e 106,573 mm em h = 60 mm — e rebaixa",
          "aumenta o curso do cabo (de 28,942 mm em h = 15 mm para 42,435 mm em h = 22,701 mm e 106,573 mm em h = 60 mm) e rebaixa"),
    ("T", " = 34,785 mm fica fora desse intervalo", " = 34,785 mm, fica fora desse intervalo"),
    ("T", " é incompatível com os demais parâmetros congelados, pois viola",
          ", é incompatível com os demais parâmetros congelados, pois viola"),

    # ------------------------------------------------------------------ 4.2
    ("R", "Com os valores de s0 da seção 4.2.4, o fator G lido na Figura 16 da patente",
     ["Com os valores de s_{0} da seção 4.2.4, o fator G lido na Figura 16 da patente e a forma "
      "m/(1000 τ_{g}) prevista pelo modelo diferem (Figura 12(b)). Normalizada em 90°, a razão "
      "entre os dois vale 0,26 em 20°, 0,79 em 60°, 1,34 em 120°, 2,02 em 150° e 2,94 em 165°. Em "
      "consequência, com esses valores de s_{0}, o m do CAD e o τ_{g} do conjunto, a razão "
      "calculada não reproduz a Figura 16 da patente: com escala comum às três curvas, o "
      "coeficiente de determinação é −0,417 (pontilhada), −1,529 (tracejada) e −0,620 (contínua).",
      "A causa da diferença pode ser delimitada. Como o s implícito na figura concorda com o do "
      "CAD (seção 4.2.4), ela não se explica por s. Restam o braço de momento, que depende da "
      "derivada de s, e o torque do peso que a patente usou para formar a razão, que o texto da "
      "patente não define de forma consistente (seção 3.2.10). Se toda a diferença fosse "
      "atribuída ao braço de momento, o s implícito se afastaria do s do CAD, pela Equação (45), "
      "em até 5,82 mm (2,42 mm RMS) entre 35° e 155°, mais que os 1,72 mm (0,84 mm RMS) "
      "observados. A concordância de s descarta, portanto, o braço de momento como causa "
      "principal e aponta para o torque do peso usado pela patente ou para a definição da "
      "ordenada, que a patente não permite separar."]),
    ("R", "A forma do torque do elástico pode ser comparada à do peso sem depender de K",
     ["A forma do torque do elástico pode ser comparada à do peso sem depender de K, normalizando "
      "cada curva pelo próprio pico (Figura 14). Com o s_{0} adotado, o pico normalizado do "
      "elástico ocorre em θ_{el} = 79,1°, contra 89,8° do peso, e as curvas normalizadas se cruzam "
      "em 17,08° (regime II), 48,40°, 83,74° e 177,02°. Abaixo de 17,08°, a forma do elástico fica "
      "acima da do peso, que tende a zero com o braço pendente. Entre 17,08° e 48,40°, fica "
      "abaixo, com diferença de até −0,149 em 24,6°, perto da transição. Entre 48,40° e 83,74°, "
      "fica ligeiramente acima, com no máximo +0,039 em 66,0°. Entre 83,74° e 177,02°, volta a "
      "ficar abaixo, com diferença de até −0,272 em 139,2°, e acima de 177,02° fica de novo "
      "acima. Entre as faixas de θ_{el} testadas na identificação, o pico vai de 78,7° a 79,4°, "
      "de modo que essas conclusões não dependem da faixa escolhida.",
      "A posição do pico fica na faixa de 70° a 120° em que a patente prefere a força máxima, "
      "desde que essa força seja lida como a força de apoio sobre o braço, proporcional ao torque "
      "na articulação, que é a interpretação adotada aqui; a força do próprio elástico é máxima "
      "com o braço pendente. O mesmo trecho da patente cita, como exemplo, força nula até 45°, "
      "60° ou 90°. Nem a Figura 16 da patente, com razão não nula a partir de cerca de 14°, nem o "
      "modelo, com torque desde 0°, seguem essa preferência. Como esse ângulo é ajustável pela "
      "posição do elemento 78, os valores citados correspondem a regulagens para as quais a "
      "patente não publica curva."]),

    # ------------------------------------------------------------------ 4.3
    ("T", " Os números e as figuras são produzidos pelo script tcc_resultados_exo3.py.", ""),
    ("T", "As peças caem sobre os desenhos:", "As peças do CAD concordam com os desenhos:"),
    ("T", "Hipótese, por decisão do autor", "Hipótese de simplificação"),
    ("T", "ele chegaria ao chifre de baixo do bolsão, e esses giros",
          "ele chegaria à ponta de baixo do rebaixo, e esses giros"),
    ("R", "Os furos em torno do pino 572 reforçam essa leitura.",
     "Os furos em torno do pino 572 reforçam essa leitura. Os cinco ficam a 14,97 mm do centro na "
     "Figura 14C e a 14,83 mm na 14D, com passo médio de 25,19° e 25,44°. No referencial da "
     "Figura 15B, eles vão de 119,8° a 220,5° na primeira e de 120,8° a 222,5° na segunda: ocupam "
     "quase a mesma posição no came nas duas figuras e, portanto, giram com ele. Com o passo "
     "médio, 25,31°, as nove montagens vão de −101,25° a +101,25° (Tabela 28 e Figura 19). A de "
     "dois furos no sentido horário, a −50,62°, fica a 1,6° do melhor giro contínuo e reproduz a "
     "curva da patente com R² = 0,953, k = 2,119 N/mm e x_{0} = 119,0 mm, contra R² = 0,901 da "
     "montagem desenhada."),
    ("T", "chega ao chifre de cima do bolsão antes do limite de subida",
          "chega à ponta de cima do rebaixo antes do limite de subida"),
    ("T", "ao chifre de baixo abaixo de −64,2°", "à ponta de baixo abaixo de −64,2°"),

    # ------------------------------------------------------------------ capítulo 5
    ("R", "Para a EP 3 504 033 B1, foram executadas a leitura da arquitetura na patente",
     "Para a EP 3 504 033 B1, o procedimento foi executado até o confronto com o torque "
     "gravitacional. A arquitetura foi lida na patente, as grandezas do CAD foram organizadas "
     "com sua origem, a cinemática de dois regimes foi resolvida em forma fechada, e o "
     "comprimento de referência s_{0} foi identificado a partir da Figura 16 da patente, pelo "
     "espaçamento entre as curvas e pelo ajuste de forma. Completam a análise a composição "
     "inercial do membro humano, o torque gravitacional, a varredura do trecho e_{c} e as "
     "verificações numéricas."),
    ("R", "O espaçamento entre as três curvas da Figura 16 da patente determina os comprimentos",
     ["O espaçamento entre as três curvas da Figura 16 da patente determina os comprimentos de "
      "referência do elástico sem depender da escala da ordenada, da rigidez, do braço de momento "
      "ou do torque do peso: 311,15 mm na curva pontilhada, 300,75 mm na tracejada e 291,96 mm na "
      "contínua. Na curva tracejada, que fornece o s_{0} adotado, a variação entre as faixas de "
      "ângulo testadas é de até 2,14 mm, e o desvio padrão com o ruído de extração, de 0,77 mm "
      "(0,33 mm na pontilhada e 1,08 mm na contínua). O fim da curva pontilhada, de pré-tensão "
      "quase nula, confirma o resultado de forma independente: a razão dessa curva, extrapolada, "
      "se anula em 171,2°, o que o modelo interpreta como afrouxamento do elástico, e com o s_{0} "
      "identificado o modelo afrouxa a partir de 166,2°.",
      "O início das curvas, perto de 14°, não informa s_{0}, mas fica a 0,9° do contato calculado "
      "com o elemento de encosto sobre o eixo, em 13,35°, configuração preferida pela patente; "
      "com o elemento do CAD, a 7,754 mm do eixo, o contato ocorre em 24,55°. O espaçamento "
      "confirma ainda o sinal de θ_{b,pose} e a abscissa: com o sinal oposto, o resíduo sobe de "
      "0,194 para 0,406 mm, e nenhum deslocamento da abscissa o reduz de forma apreciável."]),
    ("R", "Para a US 9.737.374 B2, foram executadas a leitura da arquitetura na patente",
     "Para a US 9.737.374 B2, o procedimento foi executado até o confronto com o torque "
     "gravitacional. As grandezas do CAD foram organizadas com sua origem e conferidas com as "
     "Figuras 14C e 14D, o circuito do cabo de ancoragem foi resolvido em forma fechada, o perfil "
     "do came foi extraído da Figura 15B, e o torque foi obtido pelo produto vetorial e pelo "
     "princípio dos trabalhos virtuais. A mola foi identificada a partir da Figura 16 da US "
     "9.737.374 B2, na escala da AWM, e a análise se completa com a composição inercial do membro "
     "e do apoio de braço, o torque gravitacional, a varredura do giro do came e as verificações "
     "numéricas."),
    ("T", "e as peças do apoio de braço caem sobre o desenho:", "e as peças do apoio de braço concordam com o desenho:"),

    # ------------------------------------------------------------------ segunda passada: registro e alcance
    ("T", "O P do modelo cai a 1,8 mm do pino do elástico desenhado", "O P do modelo fica a 1,8 mm do pino do elástico desenhado"),
    ("T", "cai sobre a mola 636 da Figura 14D", "coincide com a mola 636 da Figura 14D"),
    ("T", "o certo se escolhe por continuidade a partir da pose do CAD", "o correto é escolhido por continuidade a partir da pose do CAD"),
    ("T", "os dois têm S positivo, e o certo se escolhe por continuidade.", "os dois têm S positivo, e o correto é escolhido por continuidade."),
    ("T", "; o came espelhado não fecha.", "; a hipótese de came espelhado é rejeitada pelas duas medidas do giro."),
    ("T", "e o ponto A do CAD cai a 0,6 mm e a 0,3 mm do 562 desenhado", "e o ponto A do CAD fica a 0,6 mm e a 0,3 mm do 562 desenhado"),
    ("T", "o R20 do came do CAD sai de 31,65 a 32,01 mm pela área, pela giração e pela caixa envolvente",
          "o R20 do came do CAD vai de 31,65 a 32,01 mm, conforme se calcule pela área, pela giração ou pela caixa envolvente"),
    ("T", "mas cai 22,9° abaixo dela", "mas fica 22,9° abaixo dela"),
    ("T", "as duas caem dentro das marcas da patente", "as duas ficam dentro das marcas da patente"),
    ("T", "o ajuste melhora e as zonas caem nas marcas da patente", "o ajuste melhora e as zonas ficam dentro das marcas da patente"),
    ("T", "o ponto de ancoragem do CAD cai a menos de 1 mm do desenhado", "o ponto de ancoragem do CAD fica a menos de 1 mm do desenhado"),
    ("T", "do modelo caem dentro das marcas da Figura 16", "do modelo ficam dentro das marcas da Figura 16"),
    ("T", "com o elemento sobre o eixo, o contato cai no início das curvas.",
          "com o elemento sobre o eixo, o contato ocorre junto ao início das curvas."),
    ("T", "e os resultados limitam-se à análise estática.", "e os resultados referem-se ao membro de referência e limitam-se à análise estática."),
    ("R", "O pico de assistência fica acima do pico gravitacional no primeiro, 8,1°",
     ["O pico de assistência fica acima do pico gravitacional no primeiro, 8,1° (97,5° contra 89,4°), e "
      "abaixo no segundo, 10,7° (79,1° contra 89,8°); no terceiro, a curva da patente tem máximo em 91° de "
      "elevação, quase junto ao do peso, em 89,4°. A faixa sem torque com o braço baixado é obtida, segundo "
      "as patentes, por uma protuberância no primeiro e pelo contato com o elemento de encosto no segundo, "
      "e o terceiro não tem faixa sem torque no curso analisado. Nos três, a magnitude do torque depende de "
      "hipótese, e a comparação proposta na seção 2.11 fica respondida quanto aos ângulos e à forma dos "
      "perfis, mas não quanto à magnitude.",
      "Nem todos os resultados dependem dessas hipóteses. Não dependem da escala do torque os ângulos dos "
      "picos, dos pontos mortos e das transições, a forma normalizada dos perfis, os comprimentos de "
      "referência do elástico obtidos pelo espaçamento entre as curvas e as verificações de fechamento e de "
      "trabalho virtual. Dependem dela os valores em N·m: no segundo dispositivo, a rigidez K_{40}, fixada "
      "pela hipótese de assistência de 40% em 90°, e, no terceiro, a escala que iguala a AWM ao peso do "
      "membro de referência; no primeiro, o torque permanece em unidade da patente. Todos dependem, ainda, "
      "da geometria reconstruída em CAD a partir de desenhos sem cotas."]),
]

EXCECOES = {
    "O pico de assistência fica acima do pico gravitacional no primeiro, 8,1°": {
        "entram": ["40", "90", "AWM", "CAD"],
        "motivo": "parágrafo de síntese acrescentado ao fim da seção 5.4 (o que depende e o que não depende da "
                  "escala do torque); a hipótese de 40% em 90° é a da seção 3.2.10, e a da AWM, a da seção 3.3.10",
    },
    "Esta seção apresenta os resultados das etapas das seções 3.3.1 a 3.3.12": {
        "saem": ["3"],
        "motivo": "sai a frase que repetia o nome do script (tcc_resultados_exo3.py), já dito na seção 3.3",
    },
    "Pela formulação de Lagrange, com q como coordenada generalizada": {
        "saem": ["4.3.9"],
        "motivo": "remissão obsoleta: a seção 4.3.9 deixou de listar condições para a etapa dinâmica",
    },
    "Os furos em torno do pino 572 reforçam essa leitura.": {
        "entram": ["220,5", "120,8"],
        "motivo": "intervalo dos furos em cada figura, em vez da envoltória das duas; valores de "
                  "results/exo3_tcc_numeros.json (furos.figuras: 119,75° a 220,5° na 14C e 120,75° a 222,5° na 14D)",
    },
}

RESUMO = r"""Exoesqueletos passivos de apoio ao braço são empregados no trabalho com os braços elevados, associado a distúrbios do ombro, e o auxílio que entregam depende apenas da geometria do mecanismo e da mola. As patentes que descrevem os modelos comerciais detalham o mecanismo, mas não informam massa, inércia nem rigidez. Este trabalho reconstrói, a partir das patentes, três mecanismos de arquitetura distinta e formula modelos estáticos do torque entregue em função do ângulo de elevação, para confrontá-lo com o torque gravitacional do braço ou com a curva publicada: o gerador de torque de mola, cabo e polia da US 9.889.554 B2, o dispositivo da EP 3 504 033 B1, em que um elástico atua diretamente sobre uma alavanca solidária ao braço, e o mecanismo da US 9.737.374 B2, em que a mola age por um came de raio variável. A geometria foi reconstruída em CAD, a cinemática foi resolvida em forma fechada, e cada etapa do cálculo foi conferida por verificações internas de consistência. Entre elas, o princípio dos trabalhos virtuais mostrou, na US 9.889.554 B2, que a extensão da mola deve acompanhar o caminho completo do cabo. Com os parâmetros não publicados congelados, dois deles de origem não reproduzida, o modelo do primeiro mecanismo reproduz a forma da curva publicada, nos mesmos 29 pontos usados para fixá-los, com coeficiente de determinação de 0,99839 e raiz do erro quadrático médio de 1,24\% do maior valor extraído. O pico do torque do cabo, a 97,5° de elevação, fica cerca de 8° acima do pico gravitacional, de 11,16 N·m a 89,4°. Como a ordenada da curva não tem unidade declarada, o modelo determina a forma do torque, mas não sua escala física. Na EP 3 504 033 B1, o espaçamento entre as três curvas de pré-tensão publicadas determina os comprimentos de referência do elástico (311,15 mm, 300,75 mm e 291,96 mm), sem depender da escala da ordenada nem da rigidez, e o início dessas curvas coincide, a menos de 1°, com o contato do elástico com o elemento de encosto sobre o eixo. A forma prevista com a geometria do CAD, contudo, não reproduz as curvas da patente, e a rigidez não é identificável pela figura; sob a hipótese de assistência de 40\% do torque do peso em 90°, o pico do torque é de 4,379 N·m em 79,1°, cerca de 11° abaixo do pico gravitacional. Na US 9.737.374 B2, com o perfil do came extraído do desenho, uma mola linear reproduz a curva publicada com coeficiente de determinação de 0,901, ou de 0,953 com o came fixado dois furos ao lado do desenhado, montagem a 1,6° do melhor giro, que também alinha as zonas do came às da patente. A comparação entre os três mecanismos fica respondida quanto aos ângulos e à forma dos perfis, mas não quanto à magnitude, que depende de hipótese nos três. As etapas dinâmicas, pela formulação de Lagrange e no MBDyn, dependem de um dado independente que fixe a escala do torque e não foram executadas.

\bigskip\noindent Palavras-chave: exoesqueleto passivo; compensação de gravidade; ombro; patentes; identificação de parâmetros."""

ABSTRACT = r"""Passive arm-support exoskeletons are used in work with raised arms, which is associated with shoulder disorders, and the assistance they deliver depends only on the mechanism geometry and the spring. The patents that describe the commercial models detail the mechanism but do not report mass, inertia or stiffness. This work reconstructs, from the patents, three mechanisms of different architecture and formulates static models of the torque delivered as a function of the elevation angle, to compare it with the gravitational torque of the arm or with the published curve: the spring, cable and pulley torque generator of US 9,889,554 B2, the device of EP 3 504 033 B1, in which an elastic element acts directly on a lever attached to the arm, and the mechanism of US 9,737,374 B2, in which the spring acts through a variable-radius cam. The geometry was reconstructed in CAD, the kinematics was solved in closed form, and each step of the calculation was verified by internal consistency checks. Among them, the principle of virtual work showed, for US 9,889,554 B2, that the spring extension must follow the complete cable path. With the unpublished parameters frozen, two of them of unreproducible origin, the model of the first mechanism reproduces the shape of the published curve, on the same 29 points used to fix them, with a coefficient of determination of 0.99839 and a root mean square error of 1.24\% of the largest extracted value. The peak of the cable torque, at 97.5° of elevation, lies about 8° above the gravitational peak of 11.16 N·m at 89.4°. Since the ordinate of the curve has no declared unit, the model determines the shape of the torque but not its physical scale. For EP 3 504 033 B1, the spacing between the three published pretension curves determines the reference lengths of the elastic element (311.15 mm, 300.75 mm and 291.96 mm), independently of the ordinate scale and the stiffness, and the start of these curves matches, within 1°, the contact of the elastic element with the stop element on the axis. The shape predicted with the CAD geometry, however, does not reproduce the patent curves, and the stiffness cannot be identified from the figure; assuming assistance of 40\% of the weight torque at 90°, the torque peak is 4.379 N·m at 79.1°, about 11° below the gravitational peak. For US 9,737,374 B2, with the cam profile extracted from the drawing, a linear spring reproduces the published curve with a coefficient of determination of 0.901, or 0.953 with the cam fixed two holes away from the drawn position, a mounting 1.6° from the best rotation that also aligns the cam zones with those of the patent. The comparison among the three mechanisms is answered regarding the angles and the shape of the profiles, but not regarding magnitude, which depends on an assumption in all three. The dynamic steps, through the Lagrange formulation and in MBDyn, depend on independent data that fix the torque scale and were not carried out.

\bigskip\noindent Keywords: passive exoskeleton; gravity compensation; shoulder; patents; parameter identification."""
