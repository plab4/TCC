# Exoesqueleto 3 (US 9.737.374 B2, Levitate): como Okabe obteve as curvas e viabilidade de replicar

Análise preliminar, sem início do trabalho no exo 3. Fontes: manuscrito CND-25-1354
(Okabe, Brittes e Brito, *Modeling and simulation of an upper limb exoskeleton*) e a
patente US 9.737.374 B2 (Doyle, 2017), 67 páginas digitalizadas; o texto da patente foi
lido por OCR.

## Como o manuscrito obteve as curvas

- As curvas de torque das três patentes (Doyle, Van Engelhoven e Kazerooni, Mizera et
  al.) foram digitalizadas no WebPlotDigitizer e interpoladas com a SciPy (manuscrito,
  linhas 230 a 235).
- O "Model 1" é a patente de Doyle. O esquema da Figura 6 do manuscrito desenha a polia
  variável (came) da Figura 15A da patente, e a forma da curva (subida, patamar, queda)
  coincide com a do momento de elevação AASM da Figura 16 da patente.
- Escala: o máximo das curvas dos Models 1, 2 e 3B foi fixado em 30 N·m, e o Model 3A
  recebeu o mesmo fator do 3B; os níveis mínimo e intermediário são 0,33 e 0,66 do
  máximo (linhas 251 a 256). É uma escala de comparação, não identificada.
- Ângulo: 0° com o braço na horizontal, negativo abaixo. O Model 1 vai de −75° a +30°.
- As curvas entram no MBDyn como funções escalares do ângulo numa junta deformável; a
  geometria do mecanismo não é modelada (linhas 257 a 261).

## O que a patente oferece

- Mecanismo das Figuras 14C e 14D, em duas poses (braço levantado e abaixado): cabo de
  ancoragem 560, preso em 562 no suporte (posição ajustável), enrolado na polia primária
  564; polia secundária 570 (came) solidária à primária, com pivô 572 no chassi 580;
  cabo da mola 634 no canal do came, polia de reversão 630 e mola de tração 636 presa ao
  chassi em 638; o chassi gira em torno do pivô horizontal do ombro 584.
- Duas polias secundárias: came assimétrico com zonas Z10, Z11 e Z12 e raios R20 a R25
  (Figuras 15A e 15B, sem cotas) e polia circular com furo excêntrico, raios R28 e R29
  (Figuras 17A e 17B).
- Dois gráficos com o momento de elevação do dispositivo (AASM), o momento do peso do
  braço (AWM) e o resultante (RM) em função do ângulo do braço com a horizontal:
  Figura 16 (came assimétrico) e Figura 17C (polia excêntrica).
- Figura 16: nesta cópia, os números dos dois eixos são ilegíveis (rótulos em cinza
  perdidos na digitalização bitonal). O manuscrito não diz de onde vieram a faixa de
  −75° a +30° nem os valores.
- Figura 17C: eixos legíveis, ângulo de −90° a +25° (pontos a cada 10° e em +25°),
  momento de −1200 a 800, sem unidade. Leitura visual aproximada: AWM perto de 0 em −90°
  e perto de −905 em 0°, compatível com −905·cos θ; AASM perto de +450 de −90° a −50°,
  máximo perto de +985 em +5°. Os marcadores R28P (cerca de −78°) e R29P (cerca de +5°)
  indicam os ângulos em que o cabo atua nos raios R28 e R29.
- O texto não traz dimensões, rigidez nem pré-carga (busca por unidades no OCR).

## Viabilidade

1. Replicar o procedimento do manuscrito (digitalizar e escalar): imediato para a
   Figura 17C. Para a Figura 16, depende de uma cópia legível (por exemplo, a publicação
   US 2014/0158839 A1) ou de registrar seus eixos pela curva AWM, se for o mesmo braço
   da Figura 17C; o resíduo desse ajuste testa a hipótese.
2. Replicar pelo método do TCC (reconstrução geométrica, cinemática e identificação):
   viável, com uma vantagem sobre os exos 1 e 2 e mais parâmetros sem cota.
   - Vantagem: o momento do peso do braço está no mesmo eixo do momento do dispositivo.
     A razão AASM/AWM sai sem unidade, e a amplitude de AWM, comparada ao momento do
     braço de de Leva (10,550 N·m em 90° no TCC), permite estimar a unidade da ordenada
     sob a hipótese de um braço semelhante.
   - Os ângulos de R28P e R29P fixam a fase da polia, papel que θoff teve no exo 1.
   - Dificuldades: dois cabos, came e polia de reversão; sem cota para o raio da polia
     primária, a posição da ancoragem 562, a posição da polia 630 e a escala do came;
     rigidez e pré-carga só por identificação, como no exo 1.
   - Ordem sugerida: primeiro a polia excêntrica (Figuras 17A a 17C), de geometria
     simples e gráfico legível; depois o came assimétrico (Figuras 15 e 16).
   - Se o exoesqueleto comercial desmontado no manuscrito tiver o mesmo mecanismo,
     medir a mola e o came daria a escala física que faltou nos exos 1 e 2.

## Pontos a conferir no manuscrito, no confronto com os exos 1 e 2

- Models 3A e 3B (EP 3 504 033 B1): o manuscrito usa as Figuras 16 e 17 da patente
  como curvas de torque escaladas. O TCC lê a ordenada da Figura 16 como razão entre o
  torque do dispositivo e o do peso ([0092], seção 3B.9); uma razão multiplicada por
  constante não vira torque, porque o torque do peso varia com o ângulo. As três curvas
  de cada figura são pré-tensões (Figura 16) e posições do ponto de ataque (Figura 17)
  do mesmo atuador [0093], [0094].
- Model 2 (US 9.889.554 B2): a curva do manuscrito vai a zero em −90° e +90°, com pico
  perto de −20°. A curva extraída no TCC (Figura 56 da patente, Tabela 6) vai de −60°
  (torque quase nulo) a +90° (cerca de 18% do pico), com pico em +9,8°. Pode ser outra
  figura ou outra leitura do eixo.
