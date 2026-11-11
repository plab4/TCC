# Alterações parágrafo a parágrafo

Cada item traz o texto da versão original e o da versão revisada. Subscritos aparecem como `_{...}`, sobrescritos como `^{...}` e itálicos entre `‹ ›`. Parágrafos reescritos estão marcados com R; trocas pontuais, com T.

## 3 MATERIAIS E MÉTODOS

**1. (R) Original**

O trabalho é teórico-computacional. O procedimento parte da reconstrução geométrica do mecanismo e chega ao torque estático que ele entrega em função do ângulo, passando pela identificação dos parâmetros que a patente não publica. Ele foi concebido para os geradores de torque da US 9.889.554 B2, da US 9.737.374 B2 e da EP 3 504 033 B1, mas, nesta etapa do trabalho, foi executado na parte estática: para o gerador de torque da US 9.889.554 B2, ao qual se referem as seções 3.1, 4.1 e 5.1, para o dispositivo da EP 3 504 033 B1, ao qual se referem as seções 3.2, 4.2 e 5.2, e para o mecanismo de came da US 9.737.374 B2, ao qual se referem as seções 3.3, 4.3 e 5.3. As seções 3.1.9, 3.2.9 e 3.3.9 formulam os três modelos estáticos pelo princípio dos trabalhos virtuais, e as seções 3.4, 4.4 e 5.4 comparam os três.

**Revisado**

O trabalho é teórico-computacional. O procedimento parte da reconstrução geométrica do mecanismo e chega ao torque estático que ele entrega em função do ângulo, passando pela identificação dos parâmetros que a patente não publica. Ele foi aplicado, na parte estática, a três mecanismos: o gerador de torque da US 9.889.554 B2 (seções 3.1, 4.1 e 5.1), o dispositivo da EP 3 504 033 B1 (seções 3.2, 4.2 e 5.2) e o mecanismo de came da US 9.737.374 B2 (seções 3.3, 4.3 e 5.3). As seções 3.1.9, 3.2.9 e 3.3.9 formulam os três modelos estáticos pelo princípio dos trabalhos virtuais, e as seções 3.4, 4.4 e 5.4 comparam os três.

## 3.1.1 Reconstrução geométrica em CAD

**2. (T) Original**

Da reconstrução saem as grandezas geométricas do mecanismo — distância do pivô ao centro do tambor, raio do tambor, componentes do vetor que liga o pivô à ancoragem do cabo e defasagem angular do desenho —, a pose de referência, com o respectivo comprimento da mola, e o comprimento útil do alojamento da mola. O mesmo modelo fornece massa, posição do centro de massa e momento de inércia de cada peça do exoesqueleto. Por dependerem do fator de escala e da interpretação de desenhos não cotados, essas grandezas são classificadas como medidas em CAD, e não como dimensões do dispositivo comercial. As propriedades de massa dependem, além disso, do material atribuído a cada peça no CAD e são estimativas, e não propriedades do produto.

**Revisado**

Da reconstrução saem as grandezas geométricas do mecanismo (distância do pivô ao centro do tambor, raio do tambor, componentes do vetor que liga o pivô à ancoragem do cabo e defasagem angular do desenho), a pose de referência, com o respectivo comprimento da mola, e o comprimento útil do alojamento da mola. O mesmo modelo fornece massa, posição do centro de massa e momento de inércia de cada peça do exoesqueleto. Por dependerem do fator de escala e da interpretação de desenhos não cotados, essas grandezas são classificadas como medidas em CAD, e não como dimensões do dispositivo comercial. As propriedades de massa dependem, além disso, do material atribuído a cada peça no CAD e são estimativas, e não propriedades do produto.

## 3.1.3 Referenciais e convenções angulares e de sinal

**3. (T) Original**

O torque τ do modelo é positivo no sentido anti-horário, isto é, no sentido de θ* crescente. A patente apresenta o torque do cabo positivo no sentido oposto, em que ele tende a elevar o braço; para uniformizar, a curva calculada comparada à da patente foi adotada −τ.

**Revisado**

O torque τ do modelo é positivo no sentido anti-horário, isto é, no sentido de θ* crescente. A patente apresenta o torque do cabo positivo no sentido oposto, em que ele tende a elevar o braço; por isso, a curva calculada que se compara à da patente é −τ.

**4. (G) Original**

Ângulo entre o cabo e o elo pivô–tambor

**Revisado**

Ângulo entre o cabo e o elo pivô-tambor

## 3.1.4 Equação de fechamento do circuito vetorial

**5. (T) Original**

A grandeza ρ é a distância da ancoragem ao centro do tambor, e a tangente existe somente se ρ > R, condição verificada em cada ponto calculado. A formulação original do autor para essa distância, obtida pela lei dos cossenos,

**Revisado**

A grandeza ρ é a distância da ancoragem ao centro do tambor, e a tangente existe somente se ρ > R, condição verificada em cada ponto calculado. A primeira formulação dessa distância, obtida pela lei dos cossenos,

## 3.1.5 Ponto de tangência, distância b, ângulo β e braço de momento

**6. (GT) Original**

Na formulação original do autor, o mesmo ponto é obtido a partir da distância b = |OT| e do ângulo β entre a linha do elo (de O a D) e o segmento OT, calculados pela lei dos cossenos nos triângulos pivô–ancoragem–tangência e pivô–tambor–tangência:

**Revisado**

Na primeira formulação, o mesmo ponto é obtido a partir da distância b = |OT| e do ângulo β entre a linha do elo (de O a D) e o segmento OT, calculados pela lei dos cossenos nos triângulos pivô-ancoragem-tangência e pivô-tambor-tangência:

## 3.1.6 Caminho do cabo, lei da mola e torque

**7. (T) Original**

Entra no modelo apenas a parcela variável do enrolamento, um arco constante cancela-se na extensão da mola, porque o caminho e o comprimento de referência são calculados pela mesma expressão. O sinal do termo do arco foi fixado pelo princípio dos trabalhos virtuais, formulado na seção 3.1.9. Em um mecanismo conservativo, sem atrito no tambor, o trabalho da tração no cabo iguala o do torque no elo, o que exige

**Revisado**

Entra no modelo apenas a parcela variável do enrolamento: um arco constante cancela-se na extensão da mola, porque o caminho e o comprimento de referência são calculados pela mesma expressão. O sinal do termo do arco foi fixado pelo princípio dos trabalhos virtuais, formulado na seção 3.1.9. Em um mecanismo conservativo, sem atrito no tambor, o trabalho da tração no cabo iguala o do torque no elo, o que exige

## 3.1.7 Ponto morto

**8. (T) Original**

O torque do cabo se anula quando a linha de ação passa pelo pivô (m = 0). Da geometria do circuito, esse ponto morto tem forma fechada em função de h, formulação original do autor aqui escrita com a notação desta seção:

**Revisado**

O torque do cabo se anula quando a linha de ação passa pelo pivô (m = 0). Da geometria do circuito, esse ponto morto tem forma fechada em função de h, que vem da primeira formulação e é escrita aqui com a notação desta seção:

## 3.1.8 Torque gravitacional

**9. (G) Original**

O torque estático do peso do conjunto braço–exoesqueleto em relação ao pivô é calculado de forma independente da cadeia do cabo: não usa K, X_{pose} nem h. O centro de massa (x_{cm}, y_{cm}), dado na pose de referência no referencial do desenho (Tabela 4), gira com o elo, e o desenho gira ainda α + 90° − θ_{off} = −22,589° para alinhar sua vertical com a da configuração calibrada:

**Revisado**

O torque estático do peso do conjunto braço-exoesqueleto em relação ao pivô é calculado de forma independente da cadeia do cabo: não usa K, X_{pose} nem h. O centro de massa (x_{cm}, y_{cm}), dado na pose de referência no referencial do desenho (Tabela 4), gira com o elo, e o desenho gira ainda α + 90° − θ_{off} = −22,589° para alinhar sua vertical com a da configuração calibrada:

## 3.1.10 Dados da patente e identificação dos parâmetros

**10. (T) Original**

A referência de comparação é a curva torque × ângulo, Figura 56 do gerador de torque publicada na US 9.889.554 B2, da qual foram extraídos 29 pontos, registrados em θ* e listados na Tabela 5 na ordem da extração.

**Revisado**

A referência de comparação é a curva torque × ângulo do gerador de torque, Figura 56 da US 9.889.554 B2, da qual foram extraídos 29 pontos, registrados em θ* e listados na Tabela 5 na ordem da extração.

## 3.1.13 Etapas dinâmicas previstas

**11. (G) Original**

O sistema seria tratado como mecanismo plano de um grau de liberdade, a rotação do conjunto membro–elo distal em torno do eixo da junta, com coordenada generalizada q. A energia cinética seria escrita com o momento de inércia I_{O} da Equação (1), e a energia potencial reuniria a parcela gravitacional e a parcela elástica V_{e} = K δ^{2}/2. Pela Equação (19), ∂V_{e}/∂q = K δ m, de modo que a força generalizada elástica coincide, a menos do fator 1/1000, com o torque do cabo da Equação (22). A equação de movimento teria a forma

**Revisado**

O sistema seria tratado como mecanismo plano de um grau de liberdade, a rotação do conjunto membro-elo distal em torno do eixo da junta, com coordenada generalizada q. A energia cinética seria escrita com o momento de inércia I_{O} da Equação (1), e a energia potencial reuniria a parcela gravitacional e a parcela elástica V_{e} = K δ^{2}/2. Pela Equação (19), ∂V_{e}/∂q = K δ m, de modo que a força generalizada elástica coincide, a menos do fator 1/1000, com o torque do cabo da Equação (22). A equação de movimento teria a forma

## 3.2 Exoesqueleto 2

**12. (R) Original**

As seções 3.2.1 a 3.2.14 aplicam à EP 3 504 033 B1 (MIZERA et al., 2023), da Ottobock, o procedimento deste capítulo, com a classificação de origem da seção 3. A cadeia de cálculo, descrita nas seções 3.2.3 a 3.2.8, está implementada no arquivo torque_model_ottobock.py, e os números e as figuras da seção 4.2 são produzidos pelo script tcc_resultados_ottobock.py, que grava os valores citados em results/ottobock_tcc_numeros.json e as figuras em results/. O script de resultados não altera parâmetro algum do modelo; as únicas identificações são as descritas na seção 3.2.10.

**Revisado**

As seções 3.2.1 a 3.2.14 aplicam à EP 3 504 033 B1 (MIZERA et al., 2023), da Ottobock, o procedimento deste capítulo, com a classificação de origem da seção 3. A cadeia de cálculo das seções 3.2.3 a 3.2.8 está implementada no arquivo torque_model_ottobock.py, e os números e as figuras da seção 4.2 são produzidos pelo script tcc_resultados_ottobock.py, que não altera parâmetro algum do modelo. As únicas identificações são as descritas na seção 3.2.10.

## 3.2.1 Reconstrução geométrica em CAD

**13. (R) Original**

O circuito do mecanismo foi fechado no modelo em CAD do Autodesk Fusion, e as grandezas medidas nesse modelo, com as derivadas delas, estão na Tabela 13 (seção 4.2.1). O arquivo do modelo e o critério de escala não foram documentados, e as medições não têm, por isso, conferência independente. A planilha de composição inercial identifica o modelo como Ottobock iX Shoulder Air; como a patente não nomeia o produto, a correspondência entre esse produto, o modelo em CAD e os desenhos da patente não está documentada. As grandezas são tratadas como medidas em CAD, na classificação da seção 3, e não como dimensões do dispositivo comercial.

**Revisado**

O circuito do mecanismo foi fechado no modelo em CAD, feito no Autodesk Fusion, e as grandezas medidas nesse modelo, com as que delas derivam, estão na Tabela 13 (seção 4.2.1). O critério de escala do modelo não foi registrado, e as medições não têm, por isso, conferência independente. A planilha de composição inercial identifica o modelo como Ottobock iX Shoulder Air; como a patente não nomeia o produto, a correspondência entre esse produto, o modelo em CAD e os desenhos da patente não está documentada. Por isso, as grandezas são tratadas como medidas em CAD, na classificação da seção 3, e não como dimensões do dispositivo comercial.

## 3.2.2 Parâmetros inerciais do membro e transporte ao eixo da articulação 20

**14. (T) Original**

O membro humano é o de referência (seção 3), em série a partir de O. O momento de inércia de cada segmento no centro de massa é M_{s} (k L)^{2}, com k o raio de giração transversal em fração do comprimento L, e o transporte ao eixo da articulação 20 usa o teorema de Steiner. A Tabela 14, na seção 4.2.1, reúne os resultados, que coincidem com os da planilha do autor.

**Revisado**

O membro humano é o de referência (seção 3), em série a partir de O. O momento de inércia de cada segmento no centro de massa é M_{s} (k L)^{2}, com k o raio de giração transversal em fração do comprimento L, e o transporte ao eixo da articulação 20 usa o teorema de Steiner. A Tabela 14, na seção 4.2.1, reúne os resultados, que coincidem com os da planilha de composição inercial.

## 3.2.3 Referenciais e convenções angulares e de sinal

**15. (R) Original**

A variável independente é q, a direção da alavanca, representada pelo segmento OP, de comprimento ‹e› (seção 3.2.4). A anteversão do braço, θ_{el}, com 0° para o braço pendente e 90° para o braço horizontal à frente, é a abscissa das Figuras 16 e 17 da patente e não precisa ser convertida em elevação anatômica. O modelo admite que o giro do elemento de apoio do braço em relação à barra 18 seja igual à anteversão, o que supõe o eixo da articulação 20 no centro do ombro e a barra 18 fixa em relação ao tronco. A patente situa a articulação na altura do ombro, na região da escápula e atrás do corpo com o braço pendente, com eixo que não coincide com o de abdução do ombro, admite que a barra 18 mude de orientação com o movimento do braço e não informa a relação entre o giro da articulação e a anteversão; as comparações angulares com as Figuras 16 e 17 da patente dependem dessa hipótese. O eixo do braço aponta na direção θ_{el} − 90°, e q se relaciona com θ_{el} por

**Revisado**

A variável independente é q, a direção da alavanca, representada pelo segmento OP, de comprimento ‹e› (seção 3.2.4). A anteversão do braço, θ_{el}, com 0° para o braço pendente e 90° para o braço horizontal à frente, é a abscissa das Figuras 16 e 17 da patente e não precisa ser convertida em elevação anatômica.

O modelo admite que o giro do elemento de apoio do braço em relação à barra 18 seja igual à anteversão, o que supõe o eixo da articulação 20 no centro do ombro e a barra 18 fixa em relação ao tronco. A patente não garante essa condição: situa a articulação na altura do ombro, na região da escápula e atrás do corpo com o braço pendente, com eixo que não coincide com o de abdução do ombro, admite que a barra 18 mude de orientação com o movimento do braço e não informa a relação entre o giro da articulação e a anteversão. As comparações angulares com as Figuras 16 e 17 da patente dependem, portanto, dessa hipótese.

O eixo do braço aponta na direção θ_{el} − 90°, e q se relaciona com θ_{el} por

**16. (R) Original**

O sinal de θ_{b,pose} = 7,962° foi conferido no CAD: na pose, o braço fica acima da horizontal. Com o sinal oposto, q_{0} seria −11,551° e θ_{el,pose}, 82,038°, e o contato da seção 3.2.5 passaria de 24,55° para 8,62°; o efeito sobre s_{0} está na seção 4.2.4. Com o sinal conferido, o pino da alavanca do modelo cai a 1,8 mm do pino do elástico desenhado na Figura 22 da patente com o braço elevado e a 4,7 mm com o braço baixado (seção 3.2.5), e o espaçamento entre as curvas fecha com resíduo de 0,194 mm, contra 0,406 mm com o sinal oposto (seção 4.2.4).

**Revisado**

O ângulo θ_{b,pose} = 7,962° é positivo, como conferido no CAD: na pose, o braço fica acima da horizontal. O modelo é sensível a esse sinal. Com o sinal oposto, q_{0} seria −11,551° e θ_{el,pose}, 82,038°, e o contato da seção 3.2.5 passaria de 24,55° para 8,62°; o efeito sobre s_{0} está na seção 4.2.4. Dois resultados sustentam o sinal adotado: o pino da alavanca do modelo fica a 1,8 mm do pino do elástico desenhado na Figura 22 da patente com o braço elevado e a 4,7 mm com o braço baixado (seção 3.2.5), e o espaçamento entre as curvas fecha com resíduo de 0,194 mm, contra 0,406 mm com o sinal oposto (seção 4.2.4).

## 3.2.4 Equação de fechamento do circuito vetorial

**17. (R) Original**

A ancoragem A do elástico fica na barra 18, e o ponto P, no pino do rasgo da alavanca solidária ao braço (Figura 3). No CAD, o elástico prende numa peça de C_{3} = 14,907 mm articulada nesse pino, desenhada girada de β_{c} = −49,647°; articulada, ela se alinha ao elástico, e a força age no pino, como na Figura 22 da patente (seção 3.2.5). A alavanca é, assim, o segmento OP, de comprimento ‹e› = e_{c} = 34,785 mm e direção q, e a peça só entra para fechar o circuito com o comprimento do elástico medido no CAD (seção 4.2.1). O vetor fixo de A a O e as posições de P e do centro do elemento 78 são

**Revisado**

A ancoragem A do elástico fica na barra 18, e o ponto P, no pino do rasgo da alavanca solidária ao braço (Figura 3). No CAD, o elástico prende-se a uma peça de C_{3} = 14,907 mm, articulada nesse pino e desenhada girada de β_{c} = −49,647°. Por ser articulada, a peça se alinha ao elástico, e a força age no pino, como na Figura 22 da patente (seção 3.2.5). A alavanca é, assim, o segmento OP, de comprimento ‹e› = e_{c} = 34,785 mm e direção q; a peça só entra para fechar o circuito com o comprimento do elástico medido no CAD (seção 4.2.1). O vetor fixo de A a O e as posições de P e do centro do elemento 78 são

## 3.2.5 Ponto de contato e troca de regime

**18. (T) Original**

Nota: desenho da patente em cinza, girado para a orientação de leitura; vetores, pontos e linhas pontilhadas do modelo como na Figura 3. À direita, ampliação da região do pivô. Em cada pose, O e A coincidem por construção, porque o desenho foi alinhado por esses dois pontos; só P e o elemento 78 testam o modelo. O P do modelo cai a 1,8 mm do pino do elástico desenhado com o braço elevado e a 4,7 mm com o braço baixado; com o braço baixado, o centro do elemento 78 do CAD fica a 22,7 mm do ponto em que o elástico desenhado se dobra.

**Revisado**

Nota: desenho da patente em cinza, girado para a orientação de leitura; vetores, pontos e linhas pontilhadas do modelo como na Figura 3. À direita, ampliação da região do pivô. Em cada pose, O e A coincidem por construção, porque o desenho foi alinhado por esses dois pontos; só P e o elemento 78 testam o modelo. O P do modelo fica a 1,8 mm do pino do elástico desenhado com o braço elevado e a 4,7 mm com o braço baixado; com o braço baixado, o centro do elemento 78 do CAD fica a 22,7 mm do ponto em que o elástico desenhado se dobra.

## 3.2.10 Dados da patente e identificação dos parâmetros

**19. (R) Original**

As Figuras 16 e 17 da patente são apresentadas como representações exemplares das curvas de força que o dispositivo pode aplicar ao braço; o documento não informa se foram medidas ou calculadas, nem a configuração do dispositivo que as gerou. A abscissa é o ângulo de anteversão, com escala de 0° a 180° e grade a cada 20°. A ordenada não tem rótulo nem valores, apenas linhas de grade: há cinco divisões acima da linha de razão nula e uma abaixo (Figura 5). Segundo a patente, a ordenada da Figura 16 da patente é uma razão de torques: o torque causado pelo peso próprio do braço e pela força peso, sem indicação do corpo a que esta se refere, dividido pelo torque aplicado pelo dispositivo. As curvas partem de zero perto de 14° e crescem com o ângulo, e com essa definição a razão seria infinita onde o dispositivo não aplica torque. Das duas leituras como razão, só a inversa, torque do dispositivo dividido pelo torque do peso, é coerente com a figura, inclusive com a subida das curvas tracejada e contínua perto de 180°, onde o torque do peso tende a zero. Essa interpretação foi a adotada, e a divergência entre o texto e a figura fica registrada.

**Revisado**

As Figuras 16 e 17 da patente são apresentadas como representações exemplares das curvas de força que o dispositivo pode aplicar ao braço; o documento não informa se foram medidas ou calculadas, nem a configuração do dispositivo que as gerou. A abscissa é o ângulo de anteversão, com escala de 0° a 180° e grade a cada 20°. A ordenada não tem rótulo nem valores, apenas linhas de grade: há cinco divisões acima da linha de razão nula e uma abaixo (Figura 5).

Segundo a patente, a ordenada da Figura 16 da patente é uma razão de torques: o torque causado pelo peso próprio do braço e pela força peso, sem indicação do corpo a que esta se refere, dividido pelo torque aplicado pelo dispositivo. As curvas, porém, partem de zero perto de 14° e crescem com o ângulo, e com essa definição a razão seria infinita onde o dispositivo não aplica torque. Das duas leituras como razão, só a inversa, torque do dispositivo dividido pelo torque do peso, é coerente com a figura, inclusive com a subida das curvas tracejada e contínua perto de 180°, onde o torque do peso tende a zero. Essa foi a interpretação adotada, e a divergência entre o texto e a figura fica registrada.

**20. (R) Original**

Os pontos das três curvas foram extraídos pelo autor e estão no arquivo fig16_curvas.csv (Tabela 15). A extração dividiu a leitura vertical por 21,1311 para obter a razão em divisões da grade, manteve a abscissa sem correção e teve erro mediano de sobreposição inferior a 0,5 px; a imagem e a resolução usadas na leitura não foram registradas. No documento B1, a figura está gravada a 300 ppp, com cerca de 215,7 px por divisão vertical e 266,2 px para 20° da abscissa. Se o erro de 0,5 px se refere à unidade da leitura vertical, ele corresponde a 0,024 divisão na ordenada e, na mesma unidade, a 0,38° na abscissa. A incerteza da extração não foi avaliada de forma independente; a identificação, adiante, propaga esse erro mediano à identificação por sorteio.

**Revisado**

Os pontos das três curvas foram extraídos neste trabalho e estão no arquivo fig16_curvas.csv (Tabela 15). A extração dividiu a leitura vertical por 21,1311 para obter a razão em divisões da grade, manteve a abscissa sem correção e teve erro mediano de sobreposição inferior a 0,5 px; a imagem e a resolução usadas na leitura não foram registradas. No documento B1, a figura está gravada a 300 ppp, com cerca de 215,7 px por divisão vertical e 266,2 px para 20° da abscissa. Admitido que o erro de 0,5 px esteja na unidade da leitura vertical, ele corresponde a 0,024 divisão na ordenada e, na mesma unidade, a 0,38° na abscissa. A incerteza da extração não foi avaliada de forma independente; a análise de robustez propaga esse erro mediano à identificação, por sorteio.

**21. (T) Original**

Para expressar o torque em N·m, K foi fixado por hipótese de projeto, e não identificado. O alvo é 40% do torque do peso em θ_{el} = 90°; o percentual é hipótese do autor, baseada na alegação comercial de que o exoesqueleto IX Shoulder Air reduz em 40% ou mais a sobrecarga no ombro durante o trabalho acima da cabeça (SUITX, [202-]). A alegação não consta da patente, não informa as condições em que a redução foi medida e não foi verificada neste trabalho; o alvo adota o menor valor alegado. O valor correspondente é

**Revisado**

Para expressar o torque em N·m, K foi fixado por hipótese de projeto, e não identificado. O alvo é 40% do torque do peso em θ_{el} = 90°; o percentual é hipótese deste trabalho, baseada na alegação comercial de que o exoesqueleto IX Shoulder Air reduz em 40% ou mais a sobrecarga no ombro durante o trabalho acima da cabeça (SUITX, [202-]). A alegação não consta da patente, não informa as condições em que a redução foi medida e não foi verificada neste trabalho; o alvo adota o menor valor alegado. O valor correspondente é

## 3.2.12 Verificações numéricas

**22. (R) Original**

As verificações estão na Tabela 16: são asserções executadas a cada cálculo, com tolerância declarada, que interrompem o cálculo se alguma for violada, e não um conjunto de testes executado com o pytest. Além das equações de fechamento e do trabalho virtual, elas conferem a continuidade na troca de regime e o caso limite p = 0, e o modelo confere ainda que o regime II ocorre exatamente para q ≤ q*, que o elemento 78 fica entre A e P na transição e que toda a cadeia depende de e_{c}. Os valores são de e_{c} = 34,785 mm, com s_{0} e K do cenário de projeto, em malha de 0,1° de 0° a 180°; a identificação pelo espaçamento entre as curvas é conferida pelo teste sintético da seção 3.2.10.

**Revisado**

As verificações estão na Tabela 16. São asserções executadas a cada cálculo, com tolerância declarada, que o interrompem se alguma for violada; não há um conjunto separado de testes executado com o pytest. Além das equações de fechamento e do trabalho virtual, elas conferem a continuidade na troca de regime e o caso limite p = 0, e o modelo confere ainda que o regime II ocorre exatamente para q ≤ q*, que o elemento 78 fica entre A e P na transição e que toda a cadeia depende de e_{c}. Os valores são de e_{c} = 34,785 mm, com s_{0} e K do cenário de projeto, em malha de 0,1° de 0° a 180°; a identificação pelo espaçamento entre as curvas é conferida pelo teste sintético da seção 3.2.10.

## 3.3 Exoesqueleto 3

**23. (R) Original**

As seções 3.3.1 a 3.3.14 aplicam à US 9.737.374 B2 (DOYLE, 2017), da Levitate, o procedimento deste capítulo, com a classificação de origem da seção 3. Nesse mecanismo, a força da mola chega ao ombro por um par de polias, uma delas um came de raio variável, e por um cabo de ancoragem. A cadeia de cálculo está nos scripts da pasta exo3, que extraem o perfil do came, resolvem o circuito do cabo de ancoragem, tratam as relações entre o came e o cabo da mola, medem as poses das figuras da patente e compõem a massa do apoio de braço; os números e as figuras da seção 4.3 são produzidos por tcc_resultados_exo3.py, que grava os valores em results/exo3_tcc_numeros.json.

**Revisado**

As seções 3.3.1 a 3.3.14 aplicam à US 9.737.374 B2 (DOYLE, 2017), da Levitate, o procedimento deste capítulo, com a classificação de origem da seção 3. Nesse mecanismo, a força da mola chega ao ombro por um par de polias, uma delas um came de raio variável, e por um cabo de ancoragem. A cadeia de cálculo está nos scripts da pasta exo3, que extraem o perfil do came, resolvem o circuito do cabo de ancoragem, tratam as relações entre o came e o cabo da mola, medem as poses das figuras da patente e compõem a massa do apoio de braço. Os números e as figuras da seção 4.3 são produzidos pelo script tcc_resultados_exo3.py.

## 3.3.1 Reconstrução geométrica em CAD

**24. (T) Original**

O modelo é plano, no plano das Figuras 14C e 14D, normal ao eixo do pivô 584, e representa só a rotação do apoio de braço em torno desse eixo. O circuito do mecanismo foi fechado no modelo em CAD do autor, cuja pose é a da Figura 14D, e as grandezas medidas nesse modelo estão na Tabela 21 (seção 4.3.1). O mesmo modelo dá as propriedades de massa de cinco corpos do apoio de braço (seção 3.3.2). As grandezas são tratadas como medidas em CAD, na classificação da seção 3, e não como dimensões do dispositivo comercial.

**Revisado**

O modelo é plano, no plano das Figuras 14C e 14D, normal ao eixo do pivô 584, e representa só a rotação do apoio de braço em torno desse eixo. O circuito do mecanismo foi fechado no modelo em CAD deste trabalho, cuja pose é a da Figura 14D, e as grandezas medidas nesse modelo estão na Tabela 21 (seção 4.3.1). O mesmo modelo dá as propriedades de massa de cinco corpos do apoio de braço (seção 3.3.2). As grandezas são tratadas como medidas em CAD, na classificação da seção 3, e não como dimensões do dispositivo comercial.

## 3.3.2 Parâmetros inerciais do membro e transporte ao eixo do pivô 584

**25. (T) Original**

O apoio de braço entra com as propriedades de massa de cinco corpos do CAD: a capa, a mola, as polias interna e externa e o came, com massa, centro de massa e tensor de inércia no referencial da peça, de eixo z, normal ao plano do mecanismo. O tensor transportado do centro de massa à origem confere com o relatório. As duas polias são cilindros cheios, com o centro de massa no eixo: a externa, de 55 mm de diâmetro, é a primária 564, no pino 572, e a interna, de 30 mm, é a polia de reversão 630, no pino 632. O came é a flange da Figura 15A extrudada em 30 mm, também no pino 572. A capa, as polias e o came são de náilon 6/6, e a mola, de aço.

**Revisado**

O apoio de braço entra com as propriedades de massa de cinco corpos do CAD: a capa, a mola, as polias interna e externa e o came, com massa, centro de massa e tensor de inércia no referencial da peça, de eixo z, normal ao plano do mecanismo. O tensor transportado do centro de massa à origem confere com o relatório de propriedades de massa do CAD. As duas polias são cilindros cheios, com o centro de massa no eixo: a externa, de 55 mm de diâmetro, é a primária 564, no pino 572, e a interna, de 30 mm, é a polia de reversão 630, no pino 632. O came é a flange da Figura 15A extrudada em 30 mm, também no pino 572. A capa, as polias e o came são de náilon 6/6, e a mola, de aço.

**26. (T) Original**

O relatório não traz o pivô 584. O came aparece sem espelhamento no CAD e no desenho, de modo que o referencial da peça é o da Figura 14D girado, e o pivô foi posto a C_{2} do pino 572, com o ângulo entre C_{2} e a reta de 572 a 632 medido na Figura 14D, do mesmo lado da mola, como no desenho. O eixo maior fica 26,741° além de C_{2} (seção 3.3.3). Para cada corpo, d_{i} é a distância do centro de massa a O e a_{i} o ângulo dele com o eixo maior, positivo acima do eixo, e o momento de inércia em O sai do teorema de Steiner. O centro do came, excêntrico, gira com as polias em relação ao chassi; os demais corpos são fixos no chassi.

**Revisado**

O relatório do CAD não traz o pivô 584. O came aparece sem espelhamento no CAD e no desenho, de modo que o referencial da peça é o da Figura 14D girado, e o pivô foi posto a C_{2} do pino 572, com o ângulo entre C_{2} e a reta de 572 a 632 medido na Figura 14D, do mesmo lado da mola, como no desenho. O eixo maior fica 26,741° além de C_{2} (seção 3.3.3). Para cada corpo, d_{i} é a distância do centro de massa a O e a_{i} o ângulo dele com o eixo maior, positivo acima do eixo, e o momento de inércia em O sai do teorema de Steiner. O centro do came, excêntrico, gira com as polias em relação ao chassi; os demais corpos são fixos no chassi.

**27. (T) Original**

Duas conferências independentes sustentam esse referencial. Com o came espelhado, o giro dado pelo centróide e o dado pelos eixos principais de inércia discordam, e o eixo da mola do CAD, levado ao desenho, cai sobre a mola 636 da Figura 14D, que não entrou na construção do referencial (seção 4.3.3). A Tabela 22, na seção 4.3.1, reúne os resultados.

**Revisado**

Duas conferências independentes sustentam esse referencial. Com o came espelhado, o giro dado pelo centróide e o dado pelos eixos principais de inércia discordam, e o eixo da mola do CAD, levado ao desenho, coincide com a mola 636 da Figura 14D, que não entrou na construção do referencial (seção 4.3.3). A Tabela 22, na seção 4.3.1, reúne os resultados.

## 3.3.3 Referenciais e convenções angulares e de sinal

**28. (T) Original**

O torque τ é positivo no sentido anti-horário, que é o de Θ crescente; τ > 0 assiste a subida do braço. O torque do peso tem sinal oposto, e as comparações usam seu módulo τ_{g}. No código, τ sai do produto da força da mola pela transmissão τ/F_{s}, guardada como transm.

**Revisado**

O torque τ é positivo no sentido anti-horário, que é o de Θ crescente; τ > 0 assiste a subida do braço. O torque do peso tem sinal oposto, e as comparações usam seu módulo τ_{g}. O torque τ é o produto da força da mola pela transmissão τ/F_{s}.

## 3.3.4 Equação de fechamento do circuito vetorial

**29. (T) Original**

A tangente existe enquanto |d| > R; o limite |d| = R é tratado na seção 3.3.7. O caminho inverso também fecha: com θ dado, φ = θ + 90°, w = −[R u(φ) + C_{1} u(γ)] e q = 180° − φ ± acos(w·u(φ)/C_{2}); dos dois ramos, o certo se escolhe por continuidade a partir da pose do CAD.

**Revisado**

A tangente existe enquanto |d| > R; o limite |d| = R é tratado na seção 3.3.7. O caminho inverso também fecha: com θ dado, φ = θ + 90°, w = −[R u(φ) + C_{1} u(γ)] e q = 180° − φ ± acos(w·u(φ)/C_{2}); dos dois ramos, o correto é escolhido por continuidade a partir da pose do CAD.

## 3.3.5 Ponto de tangência, distância b, ângulo β e braço de momento

**30. (T) Original**

A segunda forma vem do fechamento, b = −S u(θ) − C_{1} u(γ): como a linha do cabo passa por A, o braço m_{a} só depende de θ e não passa de C_{1}. Esse é o b certo porque o apoio de braço, com o chassi, as polias, a mola e o cabo 634, gira em torno de O como um corpo só, e o único esforço externo do mecanismo é a tração F_{a} do cabo 560, em T.

**Revisado**

A segunda forma vem do fechamento, b = −S u(θ) − C_{1} u(γ): como a linha do cabo passa por A, o braço m_{a} só depende de θ e não passa de C_{1}. É esse o vetor que define o torque, porque o apoio de braço, com o chassi, as polias, a mola e o cabo 634, gira em torno de O como um corpo só, e o único esforço externo do mecanismo é a tração F_{a} do cabo 560, em T.

## 3.3.6 Caminho do cabo, lei da mola e torque

**31. (R) Original**

O perfil do canal saiu da Figura 15B, um corte pelo plano do canal em que a área hachurada é o fundo do canal: na imagem da folha 22, essa área foi isolada pelos vãos brancos da hachura e completada pelas lascas junto ao contorno e pelos entalhes das cotas. O contorno fechado, centrado no furo 654 (pino 572), foi dividido pelo raio médio da zona Z10, R20, tomado como referência (Figura 7a), e as zonas, localizadas pelas linhas de chamada das cotas, vão de 89,6° a 140,4° (Z10), de 152,4° a 218,8° (Z11) e de 242,6° a 292,6° (Z12), no referencial da Figura 15B.

**Revisado**

O perfil do canal foi extraído da Figura 15B, um corte pelo plano do canal em que a área hachurada é o fundo do canal. Na imagem da folha 22, essa área foi isolada pelos vãos brancos da hachura e completada pelos fragmentos junto ao contorno e pelos entalhes das cotas. O contorno fechado, centrado no furo 654 (pino 572), foi dividido pelo raio médio da zona Z10, R20, tomado como referência (Figura 7a). As zonas, localizadas pelas linhas de chamada das cotas, vão de 89,6° a 140,4° (Z10), de 152,4° a 218,8° (Z11) e de 242,6° a 292,6° (Z12), no referencial da Figura 15B.

**32. (T) Original**

O cabo 634 sai do came tangente a ele e segue até a polia de reversão 630, de modo que a sua direção depende do próprio r; numa geometria de teste, com a polia a 4,5 R20 de D e raio 0,5 R20, essa dependência muda r em até 0,031 R20. Por decisão do autor, a polia 630 fica fora da varredura: o cabo é tomado na direção de 572 para 632, medida na Figura 14D, como se a polia estivesse no infinito. A mola, cuja rigidez e cujo comprimento livre a patente não informa, entra como mola linear, e o torque fica

**Revisado**

O cabo 634 sai do came tangente a ele e segue até a polia de reversão 630, de modo que a sua direção depende do próprio r; numa geometria de teste, com a polia a 4,5 R20 de D e raio 0,5 R20, essa dependência muda r em até 0,031 R20. Por simplificação, a polia 630 fica fora da varredura: o cabo é tomado na direção de 572 para 632, medida na Figura 14D, como se a polia estivesse no infinito. A mola, cuja rigidez e cujo comprimento livre a patente não informa, entra como mola linear, e o torque fica

## 3.3.11 Varredura paramétrica do giro do came

**33. (R) Original**

O giro do came em relação à primária é a grandeza menos certa da cadeia, porque os dois desenhos discordam (seção 4.3.1), e é a que decide em que zona o cabo da mola sai em cada Θ; por isso, foi o parâmetro varrido. A varredura repetiu o ajuste da seção 3.3.10 com o came girado de −120° a +40° em relação ao desenho da Figura 14D, de grau em grau, com as demais grandezas nos valores da Tabela 21. Só valem os giros em que o cabo da mola sai do canal em toda a faixa do ajuste: ele deixa o bolsão do 573 pelo chifre de cima e se enrola no canal até o chifre de baixo, e a ponte da envoltória sobre o bolsão não é canal. As marcas das zonas na Figura 16 da US 9.737.374 B2 não entram no ajuste e servem de conferência. Trata-se de diagnóstico, e nenhum parâmetro é substituído pelo resultado.

**Revisado**

O giro do came em relação à primária é a grandeza menos certa da cadeia, porque os dois desenhos discordam (seção 4.3.1), e é a que decide em que zona o cabo da mola sai em cada Θ; por isso, foi o parâmetro varrido. A varredura repetiu o ajuste da seção 3.3.10 com o came girado de −120° a +40° em relação ao desenho da Figura 14D, de grau em grau, com as demais grandezas nos valores da Tabela 21. O contorno do came tem um rebaixo, onde fica a âncora 573, ladeado por duas pontas, e a envoltória convexa atravessa esse rebaixo por um segmento reto, que não é canal. Por isso, só valem os giros em que o cabo da mola sai do canal em toda a faixa do ajuste, isto é, em que ele deixa o rebaixo pela ponta de cima e se enrola no canal até a ponta de baixo. As marcas das zonas na Figura 16 da US 9.737.374 B2 não entram no ajuste e servem de conferência. Trata-se de diagnóstico, e nenhum parâmetro é substituído pelo resultado.

**34. (T) Original**

Além do giro contínuo, foram testadas as montagens que os furos permitem. Nas Figuras 14C e 14D, há cinco furos pequenos num arco em torno do pino 572, no lado do came oposto ao bolsão, que acompanham o came de uma figura para a outra. Os centros foram localizados na imagem da folha 21: o raio do arco, pelos furos isolados, e os ângulos, pela fração de pixels pretos num disco de 3,2 px ao longo desse arco, o que alcança também os furos tocados por linhas de chamada. Admitido, como supõe o autor, que a polia externa tem furos correspondentes, o came pode ser fixado girado de j passos em relação ao desenho, com j de −4 a +4, e, com os mesmos cinco furos nas duas peças, 5 − |j| pares coincidem; j positivo é o giro anti-horário na vista das Figuras 14C e 14D.

**Revisado**

Além do giro contínuo, foram testadas as montagens que os furos permitem. Nas Figuras 14C e 14D, há cinco furos pequenos num arco em torno do pino 572, no lado do came oposto ao bolsão, que acompanham o came de uma figura para a outra. Os centros foram localizados na imagem da folha 21: o raio do arco, pelos furos isolados, e os ângulos, pela fração de pixels pretos num disco de 3,2 px ao longo desse arco, o que alcança também os furos tocados por linhas de chamada. Admitido, por hipótese, que a polia externa tenha furos correspondentes, o came pode ser fixado girado de j passos em relação ao desenho, com j de −4 a +4, e, com os mesmos cinco furos nas duas peças, 5 − |j| pares coincidem; j positivo é o giro anti-horário na vista das Figuras 14C e 14D.

**35. (T) Original**

Cada montagem foi calculada de dois modos. No primeiro, a mola e o cabo são os da montagem desenhada, com k e x_{0} do ajuste da seção 3.3.10, e o alongamento é a variação do comprimento do cabo da mola entre o chifre de cima e um plano fixo no chassi, normal ao cabo, com a polia 630 no infinito: o arco enrolado no canal menos a projeção do ponto de saída na direção do cabo. Como a âncora 573 gira com o came, esse comprimento vale para qualquer montagem, e o alongamento é contado do comprimento na pose do CAD com o came desenhado. No segundo modo, k e x_{0} são ajustados de novo à Figura 16 da US 9.737.374 B2, como no giro contínuo.

**Revisado**

Cada montagem foi calculada de dois modos. No primeiro, a mola e o cabo são os da montagem desenhada, com k e x_{0} do ajuste da seção 3.3.10, e o alongamento é a variação do comprimento do cabo da mola entre a ponta de cima do rebaixo e um plano fixo no chassi, normal ao cabo, com a polia 630 no infinito: o arco enrolado no canal menos a projeção do ponto de saída na direção do cabo. Como a âncora 573 gira com o came, esse comprimento vale para qualquer montagem, e o alongamento é contado do comprimento na pose do CAD com o came desenhado. No segundo modo, k e x_{0} são ajustados de novo à Figura 16 da US 9.737.374 B2, como no giro contínuo.

## 3.3.12 Verificações numéricas

**36. (T) Original**

Os scripts executam as verificações da Tabela 24 (seção 4.3.3). Na cadeia de cálculo, elas vão do fechamento com as grandezas do CAD ao caminho inverso, ao trabalho virtual, à rotação das polias pelo enrolamento e aos comprimentos dos cabos; nas conferências com a patente, incluem o ponto de ancoragem nas Figuras 14C e 14D e, para as massas, o transporte do tensor, a forma das polias, a distância entre os pinos, o raio e o giro do came, o espelhamento e a posição da mola. São asserções e conferências executadas pelos scripts, e não um conjunto de testes executado com o pytest.

**Revisado**

Os scripts executam as verificações da Tabela 24 (seção 4.3.3). Na cadeia de cálculo, elas vão do fechamento com as grandezas do CAD ao caminho inverso, ao trabalho virtual, à rotação das polias pelo enrolamento e aos comprimentos dos cabos; nas conferências com a patente, incluem o ponto de ancoragem nas Figuras 14C e 14D e, para as massas, o transporte do tensor, a forma das polias, a distância entre os pinos, o raio e o giro do came, o espelhamento e a posição da mola. São asserções e conferências executadas pelos próprios scripts; não há um conjunto separado de testes executado com o pytest.

## 3.3.13 Etapas dinâmicas previstas

**37. (T) Original**

Pela formulação de Lagrange, com q como coordenada generalizada, a equação de movimento seria I_{O} d^{2}q/dt^{2} = −(τ + τ_{g,s} + Q_{nc}), com o sinal trocado porque q cresce no sentido horário, oposto ao de τ positivo (Equação (55)). Pela Equação (65), a energia elástica da mola satisfaz dV_{e}/dq = F_{s} dx/dq = 1000 τ, de modo que a força generalizada elástica, −dV_{e}/dq, coincide, a menos do fator −1/1000, com o torque da Equação (62); esse pré-requisito estático está verificado (Tabela 24). O momento de inércia do conjunto em torno de 584 é de 0,4503 kg·m^{2} (Tabela 22), e a energia cinética teria ainda o termo do giro do par de polias em relação ao chassi, que depende de dθ_{p}/dq e, portanto, de q. A integração não foi executada: a escala do torque vem da AWM igualada ao peso do membro de referência, a rigidez e o comprimento livre da mola só existem como ajuste nessa escala, e Q_{nc} não pode ser escrito, porque atrito e amortecimento são desconhecidos. Nenhum resultado dinâmico é apresentado, e as condições para executar a etapa estão na seção 4.3.9.

**Revisado**

Pela formulação de Lagrange, com q como coordenada generalizada, a equação de movimento seria I_{O} d^{2}q/dt^{2} = −(τ + τ_{g,s} + Q_{nc}), com o sinal trocado porque q cresce no sentido horário, oposto ao de τ positivo (Equação (55)). Pela Equação (65), a energia elástica da mola satisfaz dV_{e}/dq = F_{s} dx/dq = 1000 τ, de modo que a força generalizada elástica, −dV_{e}/dq, coincide, a menos do fator −1/1000, com o torque da Equação (62); esse pré-requisito estático está verificado (Tabela 24). O momento de inércia do conjunto em torno de 584 é de 0,4503 kg·m^{2} (Tabela 22), e a energia cinética teria ainda o termo do giro do par de polias em relação ao chassi, que depende de dθ_{p}/dq e, portanto, de q. A integração não foi executada: a escala do torque vem da AWM igualada ao peso do membro de referência, a rigidez e o comprimento livre da mola só existem como ajuste nessa escala, e Q_{nc} não pode ser escrito, porque atrito e amortecimento são desconhecidos. Nenhum resultado dinâmico é apresentado.

## 3.3.14 Ferramentas e delimitação

**38. (T) Original**

Foram empregados o modelo em CAD do autor, para fechar o circuito do mecanismo e extrair as propriedades de massa do apoio de braço, e a linguagem Python, com as bibliotecas NumPy (HARRIS et al., 2020), para o cálculo vetorizado, SciPy (VIRTANEN et al., 2020), para o processamento das imagens das folhas da patente, a envoltória convexa do came, o ajuste da caixa envolvente do came e o limite de subida, pelo método de Brent (BRENT, 1973), e Matplotlib (HUNTER, 2007), para as figuras. O ajuste da mola é um problema de mínimos quadrados lineares, resolvido em forma fechada, e o MBDyn não foi empregado. Valem as exclusões de escopo da seção 3. O modelo é plano e admite vínculos ideais, sem atrito no pivô e nas polias, cabos inextensíveis e sem massa, polia 630 no infinito e mola linear identificada pela própria curva da patente, na escala fixada pela AWM. O giro do came vem do desenho da Figura 14D, que discorda do da 14C. O torque gravitacional considera o membro de referência, alinhado ao eixo maior e com o ombro no pivô 584, e os cinco corpos do apoio de braço; outras peças que giram com o braço não entram nele.

**Revisado**

Foram empregados o modelo em CAD, para fechar o circuito do mecanismo e extrair as propriedades de massa do apoio de braço, e a linguagem Python, com as bibliotecas NumPy (HARRIS et al., 2020), para o cálculo vetorizado, SciPy (VIRTANEN et al., 2020), para o processamento das imagens das folhas da patente, a envoltória convexa do came, o ajuste da caixa envolvente do came e o limite de subida, pelo método de Brent (BRENT, 1973), e Matplotlib (HUNTER, 2007), para as figuras. O ajuste da mola é um problema de mínimos quadrados lineares, resolvido em forma fechada, e o MBDyn não foi empregado. Valem as exclusões de escopo da seção 3. O modelo é plano e admite vínculos ideais, sem atrito no pivô e nas polias, cabos inextensíveis e sem massa, polia 630 no infinito e mola linear identificada pela própria curva da patente, na escala fixada pela AWM. O giro do came vem do desenho da Figura 14D, que discorda do da 14C. O torque gravitacional considera o membro de referência, alinhado ao eixo maior e com o ombro no pivô 584, e os cinco corpos do apoio de braço; outras peças que giram com o braço não entram nele.

## 4.1.1 Geometria reconstruída e propriedades de massa

**39. (G) Original**

Componente perpendicular do vetor pivô–ancoragem

**Revisado**

Componente perpendicular do vetor pivô-ancoragem

**40. (G) Original**

A composição inercial do conjunto braço–exoesqueleto, obtida pelo transporte dos momentos ao eixo da junta, consta da Tabela 4. Os segmentos do membro seguem de Leva (1996) para o indivíduo masculino de referência, de 73,0 kg e 1,741 m, com o cotovelo estendido; as peças do exoesqueleto provêm do modelo em CAD.

**Revisado**

A composição inercial do conjunto braço-exoesqueleto, obtida pelo transporte dos momentos ao eixo da junta, consta da Tabela 4. Os segmentos do membro seguem de Leva (1996) para o indivíduo masculino de referência, de 73,0 kg e 1,741 m, com o cotovelo estendido; as peças do exoesqueleto provêm do modelo em CAD.

**41. (G) Original**

Tabela 4 — Propriedades de massa do conjunto braço–exoesqueleto

**Revisado**

Tabela 4 — Propriedades de massa do conjunto braço-exoesqueleto

## 4.1.3 Verificação da cadeia de cálculo

**42. (T) Original**

A verificação do trabalho virtual decidiu a formulação do caminho do cabo. Com a extensão da mola acompanhando apenas o vão livre s, o resíduo da Equação (19) é de 1,7129 mm/rad; com o arco somado ao vão, s + Rψ, é de 3,4258 mm/rad; somente com ℓ = s − Rψ, Equação (18), ele cai a 4,7 × 10^{−8} mm/rad. Um resíduo da ordem de 1 mm/rad significa que o modelo entrega torque sem a correspondente variação da energia da mola, violando assim, a conservação de energia em um mecanismo sem atrito.

**Revisado**

A verificação do trabalho virtual decidiu a formulação do caminho do cabo. Com a extensão da mola acompanhando apenas o vão livre s, o resíduo da Equação (19) é de 1,7129 mm/rad; com o arco somado ao vão, s + Rψ, é de 3,4258 mm/rad; somente com ℓ = s − Rψ, Equação (18), ele cai a 4,7 × 10^{−8} mm/rad. Um resíduo da ordem de 1 mm/rad significa que o modelo entrega torque sem a correspondente variação da energia da mola, violando, assim, a conservação de energia em um mecanismo sem atrito.

## 4.1.5 Qualidade do ajuste à curva da patente

**43. (T) Original**

O coeficiente de determinação de 0,99839 e o erro absoluto médio de 1,94% da média indicam que a forma do perfil é reproduzida com fidelidade, apesar de os parâmetros construtivos não constarem da patente. O resultado deve ser lido com duas ressalvas. Primeiro, os quatro parâmetros não publicados foram identificados contra os mesmos 29 pontos usados na avaliação, de modo que a aderência não constitui validação independente do modelo. A outra é que a incerteza da extração não é conhecida, o que impede afirmar se os resíduos estão ou não dentro dela.

**Revisado**

O coeficiente de determinação de 0,99839 e o erro absoluto médio de 1,94% da média indicam que a forma do perfil é reproduzida com fidelidade, apesar de os parâmetros construtivos não constarem da patente. O resultado deve ser lido com duas ressalvas. A primeira é que os quatro parâmetros não publicados foram identificados contra os mesmos 29 pontos usados na avaliação, de modo que a aderência não constitui validação independente do modelo. A segunda é que a incerteza da extração não é conhecida, o que impede afirmar se os resíduos estão ou não dentro dela.

**44. (T) Original**

O modelo superestima o torque com o braço alto, acima de 155° de elevação (zona 1), e entre 45° e 94° (zona 3), e o subestima entre 100° e 150° (zona 2). Resíduo estruturado dessa natureza indica diferença sistemática de forma entre o modelo e a curva, e não apenas dispersão de digitalização. As causas possíveis: imprecisão da geometria reconstruída, erro sistemático na extração ou diferença entre a formulação do modelo e a que gerou a figura da patente. O fato de a formulação sem o arco reproduzir a curva com RMSE menor é compatível com a última hipótese, mas não o suficiente para provar a hipótese.

**Revisado**

O modelo superestima o torque com o braço alto, acima de 155° de elevação (zona 1), e entre 45° e 94° (zona 3), e o subestima entre 100° e 150° (zona 2). Resíduo estruturado dessa natureza indica diferença sistemática de forma entre o modelo e a curva, e não apenas dispersão de digitalização. As causas possíveis são a imprecisão da geometria reconstruída, um erro sistemático na extração ou uma diferença entre a formulação do modelo e a que gerou a figura da patente. O fato de a formulação sem o arco reproduzir a curva com RMSE menor é compatível com a última hipótese, mas não basta para confirmá-la.

## 4.1.7 Varredura paramétrica de h com K congelado

**45. (T) Original**

Com K e X_{pose} congelados, a curva extraída determina h dentro de 0,145 mm a 1% do RMSE mínimo. Essa precisão, porém, não deve ser lida como identificação independente de h: K e X_{pose} foram identificados no próprio H_{CAL}, de modo que a proximidade entre o mínimo da varredura e H_{CAL} é esperada por construção. O resultado mostra que o trio (K, X_{pose}, H_{CAL}) é internamente consistente e que o ajuste é muito sensível a h — o RMSE dobra a cerca de 0,9 mm do mínimo e decuplica a cerca de 5,2 mm —, mas não substitui a medição da ancoragem no dispositivo real.

**Revisado**

Com K e X_{pose} congelados, a curva extraída determina h dentro de 0,145 mm a 1% do RMSE mínimo. Essa precisão, porém, não deve ser lida como identificação independente de h: K e X_{pose} foram identificados no próprio H_{CAL}, de modo que a proximidade entre o mínimo da varredura e H_{CAL} é esperada por construção. O resultado mostra que o trio (K, X_{pose}, H_{CAL}) é internamente consistente e que o ajuste é muito sensível a h (o RMSE dobra a cerca de 0,9 mm do mínimo e decuplica a cerca de 5,2 mm), mas não substitui a medição da ancoragem no dispositivo real.

**46. (T) Original**

Os critérios de validade física não usam os pontos extraídos, embora o de tração dependa da extensão na pose, identificada contra eles. O critério de fechamento foi atendido em todos os 10.402 valores de h, e o de trabalho virtual também, com resíduo máximo de 7,4 × 10^{−8} mm/rad na grade inteira. O critério decisivo é a tração: com X_{pose} congelada, o aumento de h aumenta o curso do cabo — de 28,942 mm em h = 15 mm para 42,435 mm em h = 22,701 mm e 106,573 mm em h = 60 mm — e rebaixa a extensão mínima, que ocorre sempre em θ* = 42,917°, onde a demanda gravitacional é mínima, de apenas 1,2% do pico. A extensão mínima se anula na fronteira de tração, h = 32,886 mm. Os valores viáveis formam o intervalo contíguo de 8,000 mm, borda inferior da grade, a 32,885 mm, com 4.979 valores. A cota do CAD, H_{CAD} = 34,785 mm fica fora desse intervalo: com X_{pose} congelada, o cabo afrouxaria no início da faixa, com extensão mínima de −2,257 mm, e o RMSE seria de 43,48 u.p. (R^{2} = 0,093). A Tabela 12 reúne os valores notáveis de h.

**Revisado**

Os critérios de validade física não usam os pontos extraídos, embora o de tração dependa da extensão na pose, identificada contra eles. O critério de fechamento foi atendido em todos os 10.402 valores de h, e o de trabalho virtual também, com resíduo máximo de 7,4 × 10^{−8} mm/rad na grade inteira. O critério decisivo é a tração: com X_{pose} congelada, o aumento de h aumenta o curso do cabo (de 28,942 mm em h = 15 mm para 42,435 mm em h = 22,701 mm e 106,573 mm em h = 60 mm) e rebaixa a extensão mínima, que ocorre sempre em θ* = 42,917°, onde a demanda gravitacional é mínima, de apenas 1,2% do pico. A extensão mínima se anula na fronteira de tração, h = 32,886 mm. Os valores viáveis formam o intervalo contíguo de 8,000 mm, borda inferior da grade, a 32,885 mm, com 4.979 valores. A cota do CAD, H_{CAD} = 34,785 mm, fica fora desse intervalo: com X_{pose} congelada, o cabo afrouxaria no início da faixa, com extensão mínima de −2,257 mm, e o RMSE seria de 43,48 u.p. (R^{2} = 0,093). A Tabela 12 reúne os valores notáveis de h.

## 4.1.9 Limitações dos resultados

**47. (T) Original**

A identificação foi reproduzida apenas em parte. K e X_{pose} foram reproduzidos no h adotado, mas a origem de θ_{off} e de H_{CAL} não pôde ser reconstituída, e os quatro parâmetros foram identificados e avaliados contra os mesmos 29 pontos, cuja incerteza de extração não está documentada. A cota do CAD, H_{CAD} é incompatível com os demais parâmetros congelados, pois viola o critério de tração.

**Revisado**

A identificação foi reproduzida apenas em parte. K e X_{pose} foram reproduzidos no h adotado, mas a origem de θ_{off} e de H_{CAL} não pôde ser reconstituída, e os quatro parâmetros foram identificados e avaliados contra os mesmos 29 pontos, cuja incerteza de extração não está documentada. A cota do CAD, H_{CAD}, é incompatível com os demais parâmetros congelados, pois viola o critério de tração.

## 4.2.5 Forma das curvas e ajuste de forma

**48. (R) Original**

Com os valores de s_{0} da seção 4.2.4, o fator G lido na Figura 16 da patente e a forma m/(1000 τ_{g}) do modelo diferem (Figura 12(b)). Normalizada em 90°, a razão entre os dois vale 0,26 em 20°, 0,79 em 60°, 1,34 em 120°, 2,02 em 150° e 2,94 em 165°. Com esses valores de s_{0} e com o m do CAD e o τ_{g} do conjunto, a razão calculada não reproduz a Figura 16 da patente: com escala comum às três curvas, o coeficiente de determinação é −0,417 (pontilhada), −1,529 (tracejada) e −0,620 (contínua). Como o s implícito na figura concorda com o do CAD (seção 4.2.4), a diferença não se explica por s. Restam o braço de momento, que depende da derivada de s, e o torque do peso que a patente usou para formar a razão, que o texto não define de forma consistente (seção 3.2.10). Entre 35° e 155°, atribuir ao braço de momento toda a diferença afastaria o s implícito do s do CAD, pela Equação (45), em até 5,82 mm (2,42 mm RMS), mais que os 1,72 mm (0,84 mm RMS) observados: a concordância de s descarta o braço de momento como causa principal e favorece o torque do peso usado pela patente ou a definição da ordenada, que a patente não permite separar.

**Revisado**

Com os valores de s_{0} da seção 4.2.4, o fator G lido na Figura 16 da patente e a forma m/(1000 τ_{g}) prevista pelo modelo diferem (Figura 12(b)). Normalizada em 90°, a razão entre os dois vale 0,26 em 20°, 0,79 em 60°, 1,34 em 120°, 2,02 em 150° e 2,94 em 165°. Em consequência, com esses valores de s_{0}, o m do CAD e o τ_{g} do conjunto, a razão calculada não reproduz a Figura 16 da patente: com escala comum às três curvas, o coeficiente de determinação é −0,417 (pontilhada), −1,529 (tracejada) e −0,620 (contínua).

A causa da diferença pode ser delimitada. Como o s implícito na figura concorda com o do CAD (seção 4.2.4), ela não se explica por s. Restam o braço de momento, que depende da derivada de s, e o torque do peso que a patente usou para formar a razão, que o texto da patente não define de forma consistente (seção 3.2.10). Se toda a diferença fosse atribuída ao braço de momento, o s implícito se afastaria do s do CAD, pela Equação (45), em até 5,82 mm (2,42 mm RMS) entre 35° e 155°, mais que os 1,72 mm (0,84 mm RMS) observados. A concordância de s descarta, portanto, o braço de momento como causa principal e aponta para o torque do peso usado pela patente ou para a definição da ordenada, que a patente não permite separar.

## 4.2.9 Confronto com o torque gravitacional

**49. (R) Original**

A forma do torque do elástico pode ser comparada à do peso sem depender de K, normalizando cada curva pelo próprio pico (Figura 14). Com o s_{0} adotado, o pico normalizado do elástico ocorre em θ_{el} = 79,1°, contra 89,8° do peso, e as curvas normalizadas se cruzam em 17,08° (regime II), 48,40°, 83,74° e 177,02°. Abaixo de 17,08°, a forma do elástico fica acima da do peso, que tende a zero com o braço pendente; entre 17,08° e 48,40°, fica abaixo, com diferença de até −0,149 em 24,6°, perto da transição; entre 48,40° e 83,74°, fica ligeiramente acima, com no máximo +0,039 em 66,0°; entre 83,74° e 177,02°, volta a ficar abaixo, com diferença de até −0,272 em 139,2°; e acima de 177,02° fica de novo acima. Entre as faixas de θ_{el} testadas na identificação, o pico vai de 78,7° a 79,4°, de modo que essas conclusões não dependem da faixa escolhida. A posição do pico fica na faixa de 70° a 120° em que a patente prefere a força máxima, desde que essa força seja lida como a força de apoio sobre o braço, proporcional ao torque na articulação, interpretação do autor; a força do próprio elástico é máxima com o braço pendente. O mesmo parágrafo cita, como exemplo, força nula até 45°, 60° ou 90°, preferência que nem a Figura 16 da patente, com razão não nula a partir de cerca de 14°, nem o modelo, com torque desde 0°, seguem; como esse ângulo é ajustável pela posição do elemento 78, os valores citados pela patente correspondem a regulagens para as quais a patente não publica curva.

**Revisado**

A forma do torque do elástico pode ser comparada à do peso sem depender de K, normalizando cada curva pelo próprio pico (Figura 14). Com o s_{0} adotado, o pico normalizado do elástico ocorre em θ_{el} = 79,1°, contra 89,8° do peso, e as curvas normalizadas se cruzam em 17,08° (regime II), 48,40°, 83,74° e 177,02°. Abaixo de 17,08°, a forma do elástico fica acima da do peso, que tende a zero com o braço pendente. Entre 17,08° e 48,40°, fica abaixo, com diferença de até −0,149 em 24,6°, perto da transição. Entre 48,40° e 83,74°, fica ligeiramente acima, com no máximo +0,039 em 66,0°. Entre 83,74° e 177,02°, volta a ficar abaixo, com diferença de até −0,272 em 139,2°, e acima de 177,02° fica de novo acima. Entre as faixas de θ_{el} testadas na identificação, o pico vai de 78,7° a 79,4°, de modo que essas conclusões não dependem da faixa escolhida.

A posição do pico fica na faixa de 70° a 120° em que a patente prefere a força máxima, desde que essa força seja lida como a força de apoio sobre o braço, proporcional ao torque na articulação, que é a interpretação adotada aqui; a força do próprio elástico é máxima com o braço pendente. O mesmo trecho da patente cita, como exemplo, força nula até 45°, 60° ou 90°. Nem a Figura 16 da patente, com razão não nula a partir de cerca de 14°, nem o modelo, com torque desde 0°, seguem essa preferência. Como esse ângulo é ajustável pela posição do elemento 78, os valores citados correspondem a regulagens para as quais a patente não publica curva.

## 4.2.10 Limitações dos resultados

**50. (T) Original**

As comparações angulares com a patente, como o início das curvas, a transição e a posição do pico, dependem da hipótese de eixo da articulação 20 no centro do ombro e barra 18 fixa no tronco (seção 3.2.3). O modelo dá torque não nulo abaixo da transição, onde a Figura 16 da patente mostra razão nula, e esse trecho depende da posição e do raio de contato do elemento 78: com o elemento sobre o eixo, o contato cai no início das curvas.

**Revisado**

As comparações angulares com a patente, como o início das curvas, a transição e a posição do pico, dependem da hipótese de eixo da articulação 20 no centro do ombro e barra 18 fixa no tronco (seção 3.2.3). O modelo dá torque não nulo abaixo da transição, onde a Figura 16 da patente mostra razão nula, e esse trecho depende da posição e do raio de contato do elemento 78: com o elemento sobre o eixo, o contato ocorre junto ao início das curvas.

**51. (T) Original**

As grandezas medidas no CAD (Tabela 13) não têm conferência independente. A incerteza da leitura da Figura 16 da patente foi estimada só pelo erro mediano declarado, e a identificação supõe que a figura, apresentada como exemplar, seja fiel em escala, o que a patente não declara; o efeito de e_{c} foi comparado com a Figura 17 da patente só visualmente. Por fim, o modelo é plano, sem a abdução e a articulação esférica 22, e os resultados limitam-se à análise estática.

**Revisado**

As grandezas medidas no CAD (Tabela 13) não têm conferência independente. A incerteza da leitura da Figura 16 da patente foi estimada só pelo erro mediano declarado, e a identificação supõe que a figura, apresentada como exemplar, seja fiel em escala, o que a patente não declara; o efeito de e_{c} foi comparado com a Figura 17 da patente só visualmente. Por fim, o modelo é plano, sem a abdução e a articulação esférica 22, e os resultados referem-se ao membro de referência e limitam-se à análise estática.

## 4.3 Exoesqueleto 3

**52. (T) Original**

Esta seção apresenta os resultados das etapas das seções 3.3.1 a 3.3.12, aplicadas ao mecanismo da US 9.737.374 B2. Salvo indicação em contrário, os números foram obtidos com a geometria do CAD, R20 = 32,035 mm, o giro do came medido na Figura 14D e a escala que iguala a AWM ao torque do peso do membro de referência (seção 3.3.10), de 0,1349 N·m por unidade da figura. As etapas dinâmicas da seção 3.3.13 não foram executadas. Os números e as figuras são produzidos pelo script tcc_resultados_exo3.py.

**Revisado**

Esta seção apresenta os resultados das etapas das seções 3.3.1 a 3.3.12, aplicadas ao mecanismo da US 9.737.374 B2. Salvo indicação em contrário, os números foram obtidos com a geometria do CAD, R20 = 32,035 mm, o giro do came medido na Figura 14D e a escala que iguala a AWM ao torque do peso do membro de referência (seção 3.3.10), de 0,1349 N·m por unidade da figura. As etapas dinâmicas da seção 3.3.13 não foram executadas.

## 4.3.1 Geometria reconstruída e propriedades de massa

**53. (T) Original**

Na imagem da folha 21, a distância de 584 a 572 dá 152,6 px na Figura 14C e 152,3 px na 14D, e, com C_{2} = 90,587 mm, a escala do desenho é de 1,68 px/mm. Na Figura 14D, q = 61,19°, contra 61,724° no CAD: a pose do CAD é a da Figura 14D. Na 14C, q = −36,99°, isto é, Θ = 10,25°. Nas duas, a reta de 572 a 632, ao longo do chassi, fica 22,1° e 21,8° além de C_{2}, no mesmo sentido da defasagem do CAD, e o ponto A do CAD cai a 0,6 mm e a 0,3 mm do 562 desenhado.

**Revisado**

Na imagem da folha 21, a distância de 584 a 572 dá 152,6 px na Figura 14C e 152,3 px na 14D, e, com C_{2} = 90,587 mm, a escala do desenho é de 1,68 px/mm. Na Figura 14D, q = 61,19°, contra 61,724° no CAD: a pose do CAD é a da Figura 14D. Na 14C, q = −36,99°, isto é, Θ = 10,25°. Nas duas, a reta de 572 a 632, ao longo do chassi, fica 22,1° e 21,8° além de C_{2}, no mesmo sentido da defasagem do CAD, e o ponto A do CAD fica a 0,6 mm e a 0,3 mm do 562 desenhado.

**54. (T) Original**

No CAD, o apoio de braço tem 0,796 kg: a capa, de náilon 6/6, responde por 0,564 kg, e a mola, de aço, por 0,105 kg. O pivô ficou em (−112,07; 3,61) mm no referencial da peça, e o centro de massa do apoio, a 116,4 mm de O e 9,7° acima do eixo maior, desloca o do conjunto em 0,77° em relação ao eixo. As peças caem sobre os desenhos: a distância entre os pinos 572 e 632 é de 163,6 mm no CAD, contra 165,0 mm na Figura 14D; o R20 do came do CAD sai de 31,65 a 32,01 mm pela área, pela giração e pela caixa envolvente; e o referencial da Figura 15B fica a −21,5° da reta de 572 a 632 no CAD e a −23,0° na Figura 14D.

**Revisado**

No CAD, o apoio de braço tem 0,796 kg: a capa, de náilon 6/6, responde por 0,564 kg, e a mola, de aço, por 0,105 kg. O pivô ficou em (−112,07; 3,61) mm no referencial da peça, e o centro de massa do apoio, a 116,4 mm de O e 9,7° acima do eixo maior, desloca o do conjunto em 0,77° em relação ao eixo. As peças do CAD concordam com os desenhos: a distância entre os pinos 572 e 632 é de 163,6 mm no CAD, contra 165,0 mm na Figura 14D; o R20 do came do CAD vai de 31,65 a 32,01 mm, conforme se calcule pela área, pela giração ou pela caixa envolvente; e o referencial da Figura 15B fica a −21,5° da reta de 572 a 632 no CAD e a −23,0° na Figura 14D.

## 4.3.3 Verificação da cadeia de cálculo

**55. (T) Original**

As verificações da seção 3.3.12 resultaram nos valores da Tabela 24. Os resíduos da cadeia de cálculo são da ordem do erro de arredondamento, exceto os do trabalho virtual e do cabo 634, limitados pelo truncamento da diferença finita, e os do fechamento com o CAD, limitados pela resolução da medida. O caminho inverso devolve q por um dos dois ramos: acima de Θ = −48,8°, os dois têm S positivo, e o certo se escolhe por continuidade. Nas peças do apoio de braço, as distâncias entre eixos diferem do desenho em até 1,36 mm, os ângulos em menos de 2°, e o eixo da mola passa a 3,3 mm do centro dos traços da mola 636; o came espelhado não fecha.

**Revisado**

As verificações da seção 3.3.12 resultaram nos valores da Tabela 24. Os resíduos da cadeia de cálculo são da ordem do erro de arredondamento, exceto os do trabalho virtual e do cabo 634, limitados pelo truncamento da diferença finita, e os do fechamento com o CAD, limitados pela resolução da medida. O caminho inverso devolve q por um dos dois ramos: acima de Θ = −48,8°, os dois têm S positivo, e o correto é escolhido por continuidade. Nas peças do apoio de braço, as distâncias entre eixos diferem do desenho em até 1,36 mm, os ângulos em menos de 2°, e o eixo da mola passa a 3,3 mm do centro dos traços da mola 636; a hipótese de came espelhado é rejeitada pelas duas medidas do giro.

## 4.3.4 Parâmetros do modelo e identificação da mola

**56. (T) Original**

Hipótese, por decisão do autor

**Revisado**

Hipótese de simplificação

## 4.3.5 Qualidade do ajuste à curva da patente

**57. (T) Original**

As marcas das zonas não entram no ajuste e servem de conferência. Com esse giro, a Z11 do modelo tem largura parecida com a da marca da patente, 28,4° contra 27,8°, mas cai 22,9° abaixo dela (seção 4.3.6): a mola ajustada compensa no conjunto a posição das zonas, que o modelo não reproduz com o came desenhado.

**Revisado**

As marcas das zonas não entram no ajuste e servem de conferência. Com esse giro, a Z11 do modelo tem largura parecida com a da marca da patente, 28,4° contra 27,8°, mas fica 22,9° abaixo dela (seção 4.3.6): a mola ajustada compensa no conjunto a posição das zonas, que o modelo não reproduz com o came desenhado.

## 4.3.7 Varredura paramétrica do giro do came

**58. (T) Original**

Repetido o ajuste com o came girado de −120° a +40° em relação ao desenho, de grau em grau (Figura 18a), o cabo da mola sai do canal em toda a faixa entre −86° e +40°; abaixo de −86°, ele chegaria ao chifre de baixo do bolsão, e esses giros foram descartados. Nessa faixa, o melhor resultado com k e x_{0} positivos ocorre com o came girado de −49°: R² = 0,953, erro quadrático médio de 0,63 N·m, k = 2,053 N/mm e x_{0} = 121,2 mm (Figura 18b). Com esse giro, a Z11 do modelo vai de −22,7° a 2,4°, e a saída na Z12 ocorre de −53,2° a −51,2°: as duas caem dentro das marcas da patente, que não entram no ajuste. O ajuste da mola e as marcas das zonas indicam o mesmo giro, o que sugere que a curva da patente corresponde a uma montagem diferente da desenhada nas Figuras 14C e 14D, com o came girado em relação à primária ou com a âncora em outra posição.

**Revisado**

Repetido o ajuste com o came girado de −120° a +40° em relação ao desenho, de grau em grau (Figura 18a), o cabo da mola sai do canal em toda a faixa entre −86° e +40°; abaixo de −86°, ele chegaria à ponta de baixo do rebaixo, e esses giros foram descartados. Nessa faixa, o melhor resultado com k e x_{0} positivos ocorre com o came girado de −49°: R² = 0,953, erro quadrático médio de 0,63 N·m, k = 2,053 N/mm e x_{0} = 121,2 mm (Figura 18b). Com esse giro, a Z11 do modelo vai de −22,7° a 2,4°, e a saída na Z12 ocorre de −53,2° a −51,2°: as duas ficam dentro das marcas da patente, que não entram no ajuste. O ajuste da mola e as marcas das zonas indicam o mesmo giro, o que sugere que a curva da patente corresponde a uma montagem diferente da desenhada nas Figuras 14C e 14D, com o came girado em relação à primária ou com a âncora em outra posição.

**59. (R) Original**

Os furos em torno do pino 572 reforçam essa leitura. Os cinco ficam a 14,97 mm do centro na Figura 14C e a 14,83 mm na 14D, com passo médio de 25,19° e 25,44°, entre 119,8° e 222,5° no referencial da Figura 15B nas duas figuras: giram com o came. Com o passo médio, 25,31°, as nove montagens vão de −101,25° a +101,25° (Tabela 28 e Figura 19). A de dois furos no sentido horário, a −50,62°, fica a 1,6° do melhor giro contínuo e reproduz a curva da patente com R² = 0,953, k = 2,119 N/mm e x_{0} = 119,0 mm, contra R² = 0,901 da montagem desenhada.

**Revisado**

Os furos em torno do pino 572 reforçam essa leitura. Os cinco ficam a 14,97 mm do centro na Figura 14C e a 14,83 mm na 14D, com passo médio de 25,19° e 25,44°. No referencial da Figura 15B, eles vão de 119,8° a 220,5° na primeira e de 120,8° a 222,5° na segunda: ocupam quase a mesma posição no came nas duas figuras e, portanto, giram com ele. Com o passo médio, 25,31°, as nove montagens vão de −101,25° a +101,25° (Tabela 28 e Figura 19). A de dois furos no sentido horário, a −50,62°, fica a 1,6° do melhor giro contínuo e reproduz a curva da patente com R² = 0,953, k = 2,119 N/mm e x_{0} = 119,0 mm, contra R² = 0,901 da montagem desenhada.

**60. (T) Original**

Com a mesma mola e o mesmo cabo, a troca de furo desloca o máximo do torque de Θ = −24,4° (+4 furos) a 17,4° (−3 furos), com valores de 8,00 a 10,18 N·m, e a força da mola fica entre 98,3 e 165,5 N (Figura 19a). Os giros horários atrasam a subida do torque e o concentram perto do limite de subida; os anti-horários a antecipam e reduzem o torque com o braço erguido. Nenhuma montagem reproduz a curva da patente com essa mola melhor que a desenhada, para a qual k e x_{0} foram ajustados: R² de 0,356 a 0,852, contra 0,901. Nas montagens de +3 e +4 furos, o cabo da mola chega ao chifre de cima do bolsão antes do limite de subida, em 20,5° e 9,9°, e, na de −4 furos, ao chifre de baixo abaixo de −64,2°; fora desses trechos, o modelo não vale.

**Revisado**

Com a mesma mola e o mesmo cabo, a troca de furo desloca o máximo do torque de Θ = −24,4° (+4 furos) a 17,4° (−3 furos), com valores de 8,00 a 10,18 N·m, e a força da mola fica entre 98,3 e 165,5 N (Figura 19a). Os giros horários atrasam a subida do torque e o concentram perto do limite de subida; os anti-horários a antecipam e reduzem o torque com o braço erguido. Nenhuma montagem reproduz a curva da patente com essa mola melhor que a desenhada, para a qual k e x_{0} foram ajustados: R² de 0,356 a 0,852, contra 0,901. Nas montagens de +3 e +4 furos, o cabo da mola chega à ponta de cima do rebaixo antes do limite de subida, em 20,5° e 9,9°, e, na de −4 furos, à ponta de baixo abaixo de −64,2°; fora desses trechos, o modelo não vale.

## 4.3.9 Limitações dos resultados

**61. (T) Original**

A curva calculada depende do giro do came em relação à primária, em que as Figuras 14C e 14D da patente discordam em 15,5°. Com o came girado de −49°, o ajuste melhora e as zonas caem nas marcas da patente, e as montagens do came supõem na polia os furos medidos nas figuras. Com a ancoragem 562 na posição do CAD, o braço não sobe além de Θ = 22,0°, enquanto a curva da patente vai até 30°.

**Revisado**

A curva calculada depende do giro do came em relação à primária, em que as Figuras 14C e 14D da patente discordam em 15,5°. Com o came girado de −49°, o ajuste melhora e as zonas ficam dentro das marcas da patente, e as montagens do came supõem na polia os furos medidos nas figuras. Com a ancoragem 562 na posição do CAD, o braço não sobe além de Θ = 22,0°, enquanto a curva da patente vai até 30°.

## 5.1 Exoesqueleto 1

**62. (G) Original**

No confronto com o torque gravitacional do conjunto braço–exoesqueleto, cujo pico de 11,16 N·m ocorre a 89,4° de elevação, as curvas normalizadas diferem em no máximo 0,027 entre 105° e 150° de elevação. O pico do torque do cabo, a 97,5°, fica cerca de 8° acima do pico gravitacional, e o ponto morto, a 30,5°, libera o braço nas posturas de não trabalho, à custa de subcompensação abaixo de 94°. O resultado quantifica o compromisso de um mecanismo passivo de torque fixo por ângulo, que favorece o trabalho acima da cabeça.

**Revisado**

No confronto com o torque gravitacional do conjunto braço-exoesqueleto, cujo pico de 11,16 N·m ocorre a 89,4° de elevação, as curvas normalizadas diferem em no máximo 0,027 entre 105° e 150° de elevação. O pico do torque do cabo, a 97,5°, fica cerca de 8° acima do pico gravitacional, e o ponto morto, a 30,5°, libera o braço nas posturas de não trabalho, à custa de subcompensação abaixo de 94°. O resultado quantifica o compromisso de um mecanismo passivo de torque fixo por ângulo, que favorece o trabalho acima da cabeça.

## 5.2 Exoesqueleto 2

**63. (R) Original**

Para a EP 3 504 033 B1, foram executadas a leitura da arquitetura na patente, a organização das grandezas do CAD com sua origem, a composição inercial do membro humano, as convenções angulares, a cinemática de dois regimes em forma fechada, o torque pelo produto vetorial, o torque gravitacional, o tratamento da Figura 16 da patente, a identificação de s_{0} pelo espaçamento entre as curvas e pelo ajuste de forma, a varredura do trecho e_{c} e as verificações numéricas.

**Revisado**

Para a EP 3 504 033 B1, o procedimento foi executado até o confronto com o torque gravitacional. A arquitetura foi lida na patente, as grandezas do CAD foram organizadas com sua origem, a cinemática de dois regimes foi resolvida em forma fechada, e o comprimento de referência s_{0} foi identificado a partir da Figura 16 da patente, pelo espaçamento entre as curvas e pelo ajuste de forma. Completam a análise a composição inercial do membro humano, o torque gravitacional, a varredura do trecho e_{c} e as verificações numéricas.

**64. (R) Original**

O espaçamento entre as três curvas da Figura 16 da patente determina os comprimentos de referência do elástico sem depender da escala da ordenada, da rigidez, do braço de momento ou do torque do peso: 311,15 mm na curva pontilhada, 300,75 mm na tracejada e 291,96 mm na contínua. Na curva tracejada, que fornece o s_{0} adotado, a variação entre as faixas de ângulo testadas é de até 2,14 mm, e o desvio padrão com o ruído de extração, de 0,77 mm (0,33 mm na pontilhada e 1,08 mm na contínua). O fim da curva pontilhada, de pré-tensão quase nula, confirma o resultado de forma independente: a razão dessa curva, extrapolada, se anula em 171,2°, o que o modelo interpreta como afrouxamento do elástico, e com o s_{0} identificado o modelo afrouxa a partir de 166,2°. O início das curvas, perto de 14°, não informa s_{0}, mas fica a 0,9° do contato calculado com o elemento de encosto sobre o eixo, em 13,35°, configuração preferida pela patente; com o elemento do CAD, a 7,754 mm do eixo, o contato ocorre em 24,55°. O espaçamento confirma ainda o sinal de θ_{b,pose} e a abscissa: com o sinal oposto, o resíduo sobe de 0,194 para 0,406 mm, e nenhum deslocamento da abscissa o reduz de forma apreciável.

**Revisado**

O espaçamento entre as três curvas da Figura 16 da patente determina os comprimentos de referência do elástico sem depender da escala da ordenada, da rigidez, do braço de momento ou do torque do peso: 311,15 mm na curva pontilhada, 300,75 mm na tracejada e 291,96 mm na contínua. Na curva tracejada, que fornece o s_{0} adotado, a variação entre as faixas de ângulo testadas é de até 2,14 mm, e o desvio padrão com o ruído de extração, de 0,77 mm (0,33 mm na pontilhada e 1,08 mm na contínua). O fim da curva pontilhada, de pré-tensão quase nula, confirma o resultado de forma independente: a razão dessa curva, extrapolada, se anula em 171,2°, o que o modelo interpreta como afrouxamento do elástico, e com o s_{0} identificado o modelo afrouxa a partir de 166,2°.

O início das curvas, perto de 14°, não informa s_{0}, mas fica a 0,9° do contato calculado com o elemento de encosto sobre o eixo, em 13,35°, configuração preferida pela patente; com o elemento do CAD, a 7,754 mm do eixo, o contato ocorre em 24,55°. O espaçamento confirma ainda o sinal de θ_{b,pose} e a abscissa: com o sinal oposto, o resíduo sobe de 0,194 para 0,406 mm, e nenhum deslocamento da abscissa o reduz de forma apreciável.

## 5.3 Exoesqueleto 3

**65. (R) Original**

Para a US 9.737.374 B2, foram executadas a leitura da arquitetura na patente, a organização das grandezas do CAD com sua origem e sua conferência com as Figuras 14C e 14D, a composição inercial do membro e do apoio de braço, as convenções angulares, o circuito do cabo de ancoragem em forma fechada, o torque pelo produto vetorial e pelo princípio dos trabalhos virtuais, a extração do perfil do came da Figura 15B, o torque gravitacional, o tratamento da Figura 16 da US 9.737.374 B2, a identificação da mola na escala da AWM, a varredura do giro do came e as verificações numéricas.

**Revisado**

Para a US 9.737.374 B2, o procedimento foi executado até o confronto com o torque gravitacional. As grandezas do CAD foram organizadas com sua origem e conferidas com as Figuras 14C e 14D, o circuito do cabo de ancoragem foi resolvido em forma fechada, o perfil do came foi extraído da Figura 15B, e o torque foi obtido pelo produto vetorial e pelo princípio dos trabalhos virtuais. A mola foi identificada a partir da Figura 16 da US 9.737.374 B2, na escala da AWM, e a análise se completa com a composição inercial do membro e do apoio de braço, o torque gravitacional, a varredura do giro do came e as verificações numéricas.

**66. (T) Original**

A pose do CAD é a da Figura 14D, o ponto de ancoragem do CAD cai a menos de 1 mm do desenhado, e as peças do apoio de braço caem sobre o desenho: as polias nos pinos, o came com o giro da figura e a mola sobre a mola 636. O mecanismo molda o torque por dois caminhos: o raio efetivo do came, de 10,5 a 32,1 mm, e o braço do cabo de ancoragem, de 26,0 a 63,3 mm. A transmissão entre a força da mola e o torque no ombro é multiplicada por 4,4 entre Θ = −75° e a horizontal. O raio efetivo não é o raio cotado na patente: tomar o raio cotado como braço superestimaria o momento da mola em até 12% na Z11 e em até 49% na Z12.

**Revisado**

A pose do CAD é a da Figura 14D, o ponto de ancoragem do CAD fica a menos de 1 mm do desenhado, e as peças do apoio de braço concordam com o desenho: as polias nos pinos, o came com o giro da figura e a mola sobre a mola 636. O mecanismo molda o torque por dois caminhos: o raio efetivo do came, de 10,5 a 32,1 mm, e o braço do cabo de ancoragem, de 26,0 a 63,3 mm. A transmissão entre a força da mola e o torque no ombro é multiplicada por 4,4 entre Θ = −75° e a horizontal. O raio efetivo não é o raio cotado na patente: tomar o raio cotado como braço superestimaria o momento da mola em até 12% na Z11 e em até 49% na Z12.

**67. (T) Original**

Com o giro do came desenhado, uma mola linear reproduz a forma da curva AASM com R² = 0,901; com o came girado de −49°, R² = 0,953, e as zonas Z11 e Z12 do modelo caem dentro das marcas da Figura 16 da US 9.737.374 B2. A curva da patente parece corresponder a outra montagem do came ou a outra posição da âncora, e a ancoragem desenhada limita a subida a Θ = 22,0°, contra 30° na curva. Os cinco furos em torno do pino 572, a 25,3° um do outro nas Figuras 14C e 14D, permitem nove montagens do came; a de dois furos no sentido horário, a −50,6°, reproduz a curva com R² = 0,953, e as montagens no sentido anti-horário só a aproximam com rigidez negativa. Com a mesma mola, a troca de furo desloca o máximo do torque de −24,4° a 17,4°.

**Revisado**

Com o giro do came desenhado, uma mola linear reproduz a forma da curva AASM com R² = 0,901; com o came girado de −49°, R² = 0,953, e as zonas Z11 e Z12 do modelo ficam dentro das marcas da Figura 16 da US 9.737.374 B2. A curva da patente parece corresponder a outra montagem do came ou a outra posição da âncora, e a ancoragem desenhada limita a subida a Θ = 22,0°, contra 30° na curva. Os cinco furos em torno do pino 572, a 25,3° um do outro nas Figuras 14C e 14D, permitem nove montagens do came; a de dois furos no sentido horário, a −50,6°, reproduz a curva com R² = 0,953, e as montagens no sentido anti-horário só a aproximam com rigidez negativa. Com a mesma mola, a troca de furo desloca o máximo do torque de −24,4° a 17,4°.

## 5.4 Comparação entre os três exoesqueletos

**68. (R) Original**

O pico de assistência fica acima do pico gravitacional no primeiro, 8,1° (97,5° contra 89,4°), e abaixo no segundo, 10,7° (79,1° contra 89,8°); no terceiro, a curva da patente tem máximo em 91° de elevação, quase junto ao do peso, em 89,4°. A faixa sem torque com o braço baixado é obtida, segundo as patentes, por uma protuberância no primeiro e pelo contato com o elemento de encosto no segundo, e o terceiro não tem faixa sem torque no curso analisado. Nos três, a magnitude do torque depende de hipótese, e a comparação proposta na seção 2.11 fica respondida quanto aos ângulos e à forma dos perfis, mas não quanto à magnitude.

**Revisado**

O pico de assistência fica acima do pico gravitacional no primeiro, 8,1° (97,5° contra 89,4°), e abaixo no segundo, 10,7° (79,1° contra 89,8°); no terceiro, a curva da patente tem máximo em 91° de elevação, quase junto ao do peso, em 89,4°. A faixa sem torque com o braço baixado é obtida, segundo as patentes, por uma protuberância no primeiro e pelo contato com o elemento de encosto no segundo, e o terceiro não tem faixa sem torque no curso analisado. Nos três, a magnitude do torque depende de hipótese, e a comparação proposta na seção 2.11 fica respondida quanto aos ângulos e à forma dos perfis, mas não quanto à magnitude.

Nem todos os resultados dependem dessas hipóteses. Não dependem da escala do torque os ângulos dos picos, dos pontos mortos e das transições, a forma normalizada dos perfis, os comprimentos de referência do elástico obtidos pelo espaçamento entre as curvas e as verificações de fechamento e de trabalho virtual. Dependem dela os valores em N·m: no segundo dispositivo, a rigidez K_{40}, fixada pela hipótese de assistência de 40% em 90°, e, no terceiro, a escala que iguala a AWM ao peso do membro de referência; no primeiro, o torque permanece em unidade da patente. Todos dependem, ainda, da geometria reconstruída em CAD a partir de desenhos sem cotas.
