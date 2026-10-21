# Relatório da fusão dos exoesqueletos 1 e 2

Documento gerado: `TCC_exo1_exo2.docx`, a partir de `TCC_apenas_exo1.docx`.

Blocos do original: 305, todos mantidos e na mesma ordem. Blocos novos: 252. Blocos do original com texto alterado: 78 (renumeração e as edições de EDICOES em gerar_tcc_fundido.py).

## Numeração

Tabelas do original (antes → depois): 1 → 1, 2 → 4, 3 → 5, 4 → 6, 5 → 7, 6 → 8, 7 → 9, 8 → 10, 9 → 11, 10 → 12, 11 → 13.

Figuras do original (antes → depois): 1 → 1, 2 → 4, 3 → 5, 4 → 6, 5 → 7.

As equações do original mantêm os números (1) a (27).

## Blocos do original com texto alterado

### 1

Antes: O trabalho é teórico-computacional. O procedimento parte da reconstrução geométrica do mecanismo e chega ao torque estático que ele entrega em função do ângulo, passando pela identificação dos parâmetros que a patente não publica. Ele foi concebido para os geradores de torque da US 9.889.554 B2, da US 9.737.374 B2 e da EP 3 504 033 B1, mas, nesta etapa do trabalho, foi executado apenas para o gerador de torque da US 9.889.554 B2, ao qual se referem todas as equações deste capítulo e todos os resultados do capítulo 4.

Depois: O trabalho é teórico-computacional. O procedimento parte da reconstrução geométrica do mecanismo e chega ao torque estático que ele entrega em função do ângulo, passando pela identificação dos parâmetros que a patente não publica. Ele foi concebido para os geradores de torque da US 9.889.554 B2, da US 9.737.374 B2 e da EP 3 504 033 B1, mas, nesta etapa do trabalho, foi executado para o gerador de torque da US 9.889.554 B2, ao qual se referem as seções 3A, 4A e 5A, e para o dispositivo da EP 3 504 033 B1, ao qual se referem as seções 3B, 4B e 5B.

### 2

Antes: A cadeia de cálculo descrita nas seções 3.3 a 3.8 está implementada no arquivo torque_model.py, que contém os parâmetros congelados e não executa ajuste algum. Os números e as figuras do capítulo 4 são produzidos pelo script tcc_resultados.py, que importa esse modelo e chama suas funções com a posição da ancoragem sempre explícita, sem alterar nenhum parâmetro.

Depois: A cadeia de cálculo descrita nas seções 3A.3 a 3A.8 está implementada no arquivo torque_model.py, que contém os parâmetros congelados e não executa ajuste algum. Os números e as figuras da seção 4A são produzidos pelo script tcc_resultados.py, que importa esse modelo e chama suas funções com a posição da ancoragem sempre explícita, sem alterar nenhum parâmetro.

### 3

Antes: 3.1 Reconstrução geométrica em CAD

Depois: 3A.1 Reconstrução geométrica em CAD

### 4

Antes: 3.2 Parâmetros inerciais do membro e transporte ao eixo da junta

Depois: 3A.2 Parâmetros inerciais do membro e transporte ao eixo da junta

### 5

Antes: em que IO é o momento de inércia em relação ao eixo da junta, Icm o momento de inércia em relação ao eixo paralelo que passa pelo centro de massa, M a massa e d a distância entre os dois eixos. A composição foi feita em planilha, construída para recalcular o conjunto quando qualquer entrada muda. Conforme a seção 2.9, o momento de inércia não participa do torque estático do peso, que depende apenas da massa e da posição do centro de massa (seção 3.8); ele se destina à etapa dinâmica prevista na seção 3.12.

Depois: em que IO é o momento de inércia em relação ao eixo da junta, Icm o momento de inércia em relação ao eixo paralelo que passa pelo centro de massa, M a massa e d a distância entre os dois eixos. A composição foi feita em planilha, construída para recalcular o conjunto quando qualquer entrada muda. Conforme a seção 2.9, o momento de inércia não participa do torque estático do peso, que depende apenas da massa e da posição do centro de massa (seção 3A.8); ele se destina à etapa dinâmica prevista na seção 3A.12.

### 6

Antes: 3.3 Referenciais e convenções angulares e de sinal

Depois: 3A.3 Referenciais e convenções angulares e de sinal

### 7

Antes: em que θoff = 133,017° é a calibração angular identificada (seção 3.9). A faixa da patente, φpat de −60° a +90,1°, corresponde a θ* de 42,917° a 193,017° e a elevação de 30° a 180,1°; a elevação cresce quando θ* decresce. O ângulo φpat não deve ser confundido com φ, direção da linha do cabo calculada pelo modelo (seção 3.4).

Depois: em que θoff = 133,017° é a calibração angular identificada (seção 3A.9). A faixa da patente, φpat de −60° a +90,1°, corresponde a θ* de 42,917° a 193,017° e a elevação de 30° a 180,1°; a elevação cresce quando θ* decresce. O ângulo φpat não deve ser confundido com φ, direção da linha do cabo calculada pelo modelo (seção 3A.4).

### 8

Antes: 3.4 Equação de fechamento do circuito vetorial

Depois: 3A.4 Equação de fechamento do circuito vetorial

### 9

Antes: em que h e p são as componentes desse vetor no referencial do elo proximal. A posição da ancoragem h é o parâmetro geométrico mais incerto do mecanismo e permanece explícita em todas as equações; a cota lida no CAD, HCAD = 34,785 mm, é tratada como valor documental, e o valor adotado no modelo é HCAL = 22,701 mm (seção 3.9). Com u(x) = (cos x, sen x) e u⊥(x) = (−sen x, cos x), o fechamento do circuito se escreve

Depois: em que h e p são as componentes desse vetor no referencial do elo proximal. A posição da ancoragem h é o parâmetro geométrico mais incerto do mecanismo e permanece explícita em todas as equações; a cota lida no CAD, HCAD = 34,785 mm, é tratada como valor documental, e o valor adotado no modelo é HCAL = 22,701 mm (seção 3A.9). Com u(x) = (cos x, sen x) e u⊥(x) = (−sen x, cos x), o fechamento do circuito se escreve

### 10

Antes: 3.5 Ponto de tangência, distância b, ângulo β e braço de momento

Depois: 3A.5 Ponto de tangência, distância b, ângulo β e braço de momento

### 11

Antes: em que φB = atan2(By, Bx) é a direção do vetor B. As duas vias são comparadas numericamente (seção 3.11), e a Equação (10) é a usada na cadeia por não depender do sinal de β. A distância b, entretanto, não é o braço de momento do cabo: como T pertence a uma circunferência de raio R centrada a C do pivô, b fica necessariamente entre C − R e C + R. O braço de momento é a distância perpendicular do pivô à linha de ação do cabo, que passa por A com direção u(φ):

Depois: em que φB = atan2(By, Bx) é a direção do vetor B. As duas vias são comparadas numericamente (seção 3A.11), e a Equação (10) é a usada na cadeia por não depender do sinal de β. A distância b, entretanto, não é o braço de momento do cabo: como T pertence a uma circunferência de raio R centrada a C do pivô, b fica necessariamente entre C − R e C + R. O braço de momento é a distância perpendicular do pivô à linha de ação do cabo, que passa por A com direção u(φ):

### 12

Antes: O braço m tem sinal, anula-se quando a linha do cabo passa pelo pivô (ponto morto, seção 3.7) e é limitado pelo comprimento |B| = |OA|, teto que decorre do traçado do cabo, e não do ajuste.

Depois: O braço m tem sinal, anula-se quando a linha do cabo passa pelo pivô (ponto morto, seção 3A.7) e é limitado pelo comprimento |B| = |OA|, teto que decorre do traçado do cabo, e não do ajuste.

### 13

Antes: 3.6 Caminho do cabo, lei da mola e torque

Depois: 3A.6 Caminho do cabo, lei da mola e torque

### 14

Antes: com θ* em radianos. A Equação (17) é verificada numericamente por diferenças finitas centradas (seção 3.11) e permite discriminar entre formulações do caminho do cabo: com o caminho igual apenas ao vão livre, ela não é satisfeita (seção 4.3).

Depois: com θ* em radianos. A Equação (17) é verificada numericamente por diferenças finitas centradas (seção 3A.11) e permite discriminar entre formulações do caminho do cabo: com o caminho igual apenas ao vão livre, ela não é satisfeita (seção 4A.3).

### 15

Antes: A identidade τ = −F m/1000 decorre de T e A estarem sobre a mesma linha de ação e é verificada numericamente (seção 3.11). O fator 1/1000 vem da formulação original, em que os comprimentos estão em milímetros. Como K é identificado contra a curva publicada (seção 3.9), cuja ordenada não tem unidade declarada, o torque do cabo é expresso na unidade da própria curva, denotada u.p. (unidade da patente). A unidade de K é, portanto, aquela que faz K δ m/1000 resultar em u.p.; ela só seria N/mm se u.p. correspondesse a N·m, o que não pode ser afirmado com os dados disponíveis (seção 4.6).

Depois: A identidade τ = −F m/1000 decorre de T e A estarem sobre a mesma linha de ação e é verificada numericamente (seção 3A.11). O fator 1/1000 vem da formulação original, em que os comprimentos estão em milímetros. Como K é identificado contra a curva publicada (seção 3A.9), cuja ordenada não tem unidade declarada, o torque do cabo é expresso na unidade da própria curva, denotada u.p. (unidade da patente). A unidade de K é, portanto, aquela que faz K δ m/1000 resultar em u.p.; ela só seria N/mm se u.p. correspondesse a N·m, o que não pode ser afirmado com os dados disponíveis (seção 4A.6).

### 16

Antes: 3.7 Ponto morto

Depois: 3A.7 Ponto morto

### 17

Antes: 3.8 Torque gravitacional

Depois: 3A.8 Torque gravitacional

### 18

Antes: O torque estático do peso do conjunto braço–exoesqueleto em relação ao pivô é calculado de forma independente da cadeia do cabo: não usa K, Xpose nem h. O centro de massa (xcm, ycm), dado na pose de referência no referencial do desenho (Tabela 3), gira com o elo, e o desenho gira ainda α + 90° − θoff = −22,589° para alinhar sua vertical com a da configuração calibrada:

Depois: O torque estático do peso do conjunto braço–exoesqueleto em relação ao pivô é calculado de forma independente da cadeia do cabo: não usa K, Xpose nem h. O centro de massa (xcm, ycm), dado na pose de referência no referencial do desenho (Tabela 5), gira com o elo, e o desenho gira ainda α + 90° − θoff = −22,589° para alinhar sua vertical com a da configuração calibrada:

### 19

Antes: em que M é a massa do conjunto, g = 9,80665 m/s2 e xg, em milímetros, é o braço horizontal do centro de massa. O torque gravitacional resulta em N·m, unidade física, ao contrário do torque do cabo. O módulo na Equação (24) desconsidera o sentido do torque, cuja troca ocorre apenas no início da faixa (seção 4.8).

Depois: em que M é a massa do conjunto, g = 9,80665 m/s2 e xg, em milímetros, é o braço horizontal do centro de massa. O torque gravitacional resulta em N·m, unidade física, ao contrário do torque do cabo. O módulo na Equação (24) desconsidera o sentido do torque, cuja troca ocorre apenas no início da faixa (seção 4A.8).

### 20

Antes: 3.9 Dados da patente e identificação dos parâmetros

Depois: 3A.9 Dados da patente e identificação dos parâmetros

### 21

Antes: A referência de comparação é a curva torque × ângulo, Figura 56 do gerador de torque publicada na US 9.889.554 B2, da qual foram extraídos 29 pontos, registrados em θ* e listados na Tabela 4 na ordem da extração.

Depois: A referência de comparação é a curva torque × ângulo, Figura 56 do gerador de torque publicada na US 9.889.554 B2, da qual foram extraídos 29 pontos, registrados em θ* e listados na Tabela 6 na ordem da extração.

### 22

Antes: A patente não informa rigidez, pré-carga, comprimento livre nem posição exata da ancoragem. Os parâmetros não publicados do modelo são a calibração angular θoff, a posição da ancoragem h, a extensão da mola na pose Xpose e a rigidez K. Eles foram identificados por mínimos quadrados contra os 29 pontos extraídos em etapa anterior do trabalho e estão congelados no modelo vigente, que não executa ajuste algum. O script dessa etapa e a restrição de projeto então considerada para h não estão registrados no repositório; por isso, a identificação foi reproduzida nesta revisão apenas na parte verificável, descrita a seguir (resultados na seção 4.4).

Depois: A patente não informa rigidez, pré-carga, comprimento livre nem posição exata da ancoragem. Os parâmetros não publicados do modelo são a calibração angular θoff, a posição da ancoragem h, a extensão da mola na pose Xpose e a rigidez K. Eles foram identificados por mínimos quadrados contra os 29 pontos extraídos em etapa anterior do trabalho e estão congelados no modelo vigente, que não executa ajuste algum. O script dessa etapa e a restrição de projeto então considerada para h não estão registrados no repositório; por isso, a identificação foi reproduzida nesta revisão apenas na parte verificável, descrita a seguir (resultados na seção 4A.4).

### 23

Antes: O RMSE mede a aderência à curva extraída, e não a validade física. Duas formulações só são comparadas por ele depois de ambas satisfazerem as verificações físicas da seção 3.11; essa regra decide, no capítulo 4, a adoção do caminho completo do cabo, apesar de o caminho sem o arco produzir RMSE menor.

Depois: O RMSE mede a aderência à curva extraída, e não a validade física. Duas formulações só são comparadas por ele depois de ambas satisfazerem as verificações físicas da seção 3A.11; essa regra decide, no capítulo 4, a adoção do caminho completo do cabo, apesar de o caminho sem o arco produzir RMSE menor.

### 24

Antes: 3.10 Varredura paramétrica de h com K congelado

Depois: 3A.10 Varredura paramétrica de h com K congelado

### 25

Antes: 3.11 Verificações numéricas e testes automatizados

Depois: 3A.11 Verificações numéricas e testes automatizados

### 26

Antes: 3.12 Etapas dinâmicas previstas

Depois: 3A.12 Etapas dinâmicas previstas

### 27

Antes: em que τg,s é o torque gravitacional com sinal e Qnc reúne os esforços não conservativos, como o atrito. A verificação prevista compreende a conservação da energia na ausência de dissipação, a recuperação do resultado estático quando as velocidades tendem a zero e a consistência entre o braço de momento e a derivada do caminho do cabo, esta última já cumprida no modelo estático (seção 4.3). No acoplamento ao MBDyn, que integra o sistema multicorpos pela formulação de Masarati, Morandini e Mantegazza (2014), o gerador de torque entraria como força externa, com troca de configuração e de torque por socket a cada passo de integração, e a comparação com a integração própria, sob as mesmas condições iniciais, serviria de validação cruzada.

Depois: em que τg,s é o torque gravitacional com sinal e Qnc reúne os esforços não conservativos, como o atrito. A verificação prevista compreende a conservação da energia na ausência de dissipação, a recuperação do resultado estático quando as velocidades tendem a zero e a consistência entre o braço de momento e a derivada do caminho do cabo, esta última já cumprida no modelo estático (seção 4A.3). No acoplamento ao MBDyn, que integra o sistema multicorpos pela formulação de Masarati, Morandini e Mantegazza (2014), o gerador de torque entraria como força externa, com troca de configuração e de torque por socket a cada passo de integração, e a comparação com a integração própria, sob as mesmas condições iniciais, serviria de validação cruzada.

### 28

Antes: 3.13 Ferramentas e delimitação

Depois: 3A.13 Ferramentas e delimitação

### 29

Antes: Este capítulo apresenta os resultados das etapas descritas nas seções 3.1 a 3.11, aplicadas ao gerador de torque da US 9.889.554 B2. Salvo indicação em contrário, os números foram obtidos com o modelo vigente e os parâmetros congelados K = 174,68, HCAL = 22,701 mm e Xpose = 37,383 mm. As etapas dinâmicas da seção 3.12 e a aplicação do procedimento à US 9.737.374 B2 e à EP 3 504 033 B1 não foram executadas.

Depois: Esta seção apresenta os resultados das etapas descritas nas seções 3A.1 a 3A.11, aplicadas ao gerador de torque da US 9.889.554 B2. Salvo indicação em contrário, os números foram obtidos com o modelo vigente e os parâmetros congelados K = 174,68, HCAL = 22,701 mm e Xpose = 37,383 mm. As etapas dinâmicas da seção 3A.12 e a aplicação do procedimento à US 9.737.374 B2 não foram executadas.

### 30

Antes: 4.1 Geometria reconstruída e propriedades de massa

Depois: 4A.1 Geometria reconstruída e propriedades de massa

### 31

Antes: A reconstrução da vista em corte do gerador de torque forneceu as grandezas da Tabela 2. O fator de escala único, fixado pela razão entre o comprimento do elo distal reconstruído e o comprimento de segmento do indivíduo de referência, resultou em 0,870.

Depois: A reconstrução da vista em corte do gerador de torque forneceu as grandezas da Tabela 4. O fator de escala único, fixado pela razão entre o comprimento do elo distal reconstruído e o comprimento de segmento do indivíduo de referência, resultou em 0,870.

### 32

Antes: Tabela 2 — Grandezas medidas na reconstrução em CAD

Depois: Tabela 4 — Grandezas medidas na reconstrução em CAD

### 33

Antes: A composição inercial do conjunto braço–exoesqueleto, obtida pelo transporte dos momentos ao eixo da junta, consta da Tabela 3. Os segmentos do membro seguem de Leva (1996) para o indivíduo masculino de referência, de 73,0 kg e 1,741 m, com o cotovelo estendido; as peças do exoesqueleto provêm do modelo em CAD.

Depois: A composição inercial do conjunto braço–exoesqueleto, obtida pelo transporte dos momentos ao eixo da junta, consta da Tabela 5. Os segmentos do membro seguem de Leva (1996) para o indivíduo masculino de referência, de 73,0 kg e 1,741 m, com o cotovelo estendido; as peças do exoesqueleto provêm do modelo em CAD.

### 34

Antes: Tabela 3 — Propriedades de massa do conjunto braço–exoesqueleto

Depois: Tabela 5 — Propriedades de massa do conjunto braço–exoesqueleto

### 35

Antes: A consistência interna da Tabela 3 foi conferida: Icm + M d2 = 0,127111 + 0,321116 = 0,448227 kg·m2, igual ao momento de inércia no eixo da junta, conforme a Equação (1); e M g d = 11,1619 N·m coincide com o pico do torque gravitacional calculado pela Equação (24) (seção 4.8). O momento de inércia destina-se à etapa dinâmica, não executada, e não participa do cálculo do torque estático.

Depois: A consistência interna da Tabela 5 foi conferida: Icm + M d2 = 0,127111 + 0,321116 = 0,448227 kg·m2, igual ao momento de inércia no eixo da junta, conforme a Equação (1); e M g d = 11,1619 N·m coincide com o pico do torque gravitacional calculado pela Equação (24) (seção 4A.8). O momento de inércia destina-se à etapa dinâmica, não executada, e não participa do cálculo do torque estático.

### 36

Antes: 4.2 Dados extraídos da patente

Depois: 4A.2 Dados extraídos da patente

### 37

Antes: A Tabela 4 reúne os 29 pontos extraídos da curva da patente, na ordem da extração, com os ângulos correspondentes nas convenções da seção 3.3, o torque calculado pelo modelo com os parâmetros congelados e o resíduo. Os pontos cobrem θ* de 42,909° a 193,017°, isto é, elevação de 180,1° a 30,0°, com espaçamento irregular, de 2,87° a 8,03° em θ*. O maior valor extraído, 147,310 u.p., ocorre em θ* = 123,196° (elevação de 99,8°), e a média dos 29 valores é 81,840 u.p. Os valores são expressos em u.p. porque a figura de origem não declara unidade (seção 2.10).

Depois: A Tabela 6 reúne os 29 pontos extraídos da curva da patente, na ordem da extração, com os ângulos correspondentes nas convenções da seção 3A.3, o torque calculado pelo modelo com os parâmetros congelados e o resíduo. Os pontos cobrem θ* de 42,909° a 193,017°, isto é, elevação de 180,1° a 30,0°, com espaçamento irregular, de 2,87° a 8,03° em θ*. O maior valor extraído, 147,310 u.p., ocorre em θ* = 123,196° (elevação de 99,8°), e a média dos 29 valores é 81,840 u.p. Os valores são expressos em u.p. porque a figura de origem não declara unidade (seção 2.10).

### 38

Antes: Tabela 4 — Pontos extraídos da curva da patente e torque calculado pelo modelo

Depois: Tabela 6 — Pontos extraídos da curva da patente e torque calculado pelo modelo

### 39

Antes: 4.3 Verificação da cadeia de cálculo

Depois: 4A.3 Verificação da cadeia de cálculo

### 40

Antes: As verificações automáticas da seção 3.11 resultaram nos resíduos da Tabela 5, todos da ordem do erro de arredondamento da aritmética de ponto flutuante, exceto o do trabalho virtual, limitado pelo truncamento da diferença finita.

Depois: As verificações automáticas da seção 3A.11 resultaram nos resíduos da Tabela 7, todos da ordem do erro de arredondamento da aritmética de ponto flutuante, exceto o do trabalho virtual, limitado pelo truncamento da diferença finita.

### 41

Antes: Tabela 5 — Verificações da cadeia de cálculo (h = 22,701 mm)

Depois: Tabela 7 — Verificações da cadeia de cálculo (h = 22,701 mm)

### 42

Antes: 4.4 Parâmetros do modelo e reprodução da identificação

Depois: 4A.4 Parâmetros do modelo e reprodução da identificação

### 43

Antes: A Tabela 6 reúne os parâmetros não publicados pela patente, com seus valores congelados e a situação de cada um nesta revisão.

Depois: A Tabela 8 reúne os parâmetros não publicados pela patente, com seus valores congelados e a situação de cada um nesta revisão.

### 44

Antes: Tabela 6 — Parâmetros não publicados, origem e verificação

Depois: Tabela 8 — Parâmetros não publicados, origem e verificação

### 45

Antes: Nota: K tem a unidade que faz K δ m/1000 resultar em u.p. (seção 3.6).

Depois: Nota: K tem a unidade que faz K δ m/1000 resultar em u.p. (seção 3A.6).

### 46

Antes: A origem de HCAL = 22,701 mm, ao contrário, não pôde ser reproduzida. Para auditar essa afirmação, foi executada uma análise complementar em que Xpose e K são reidentificados para cada h, de 8 a 60 mm em passo de 0,25 mm. Essa análise não é o procedimento principal deste trabalho, que mantém K congelado (seção 3.10), e serve apenas para conferir a afirmação anterior. O RMSE resultante apresenta mínimo interior em h ≈ 24,0 mm, com RMSE de 1,682 u.p., Xpose = 38,83 mm e K = 160,46, e cresce para valores maiores de h. A razão entre a extensão máxima e o comprimento livre vale 1,0095 em h = 22,701 mm, iguala 1 em h ≈ 22,52 mm e só ultrapassa 10 próximo do extremo superior da varredura, em h = 60 mm. 

Depois: A origem de HCAL = 22,701 mm, ao contrário, não pôde ser reproduzida. Para auditar essa afirmação, foi executada uma análise complementar em que Xpose e K são reidentificados para cada h, de 8 a 60 mm em passo de 0,25 mm. Essa análise não é o procedimento principal deste trabalho, que mantém K congelado (seção 3A.10), e serve apenas para conferir a afirmação anterior. O RMSE resultante apresenta mínimo interior em h ≈ 24,0 mm, com RMSE de 1,682 u.p., Xpose = 38,83 mm e K = 160,46, e cresce para valores maiores de h. A razão entre a extensão máxima e o comprimento livre vale 1,0095 em h = 22,701 mm, iguala 1 em h ≈ 22,52 mm e só ultrapassa 10 próximo do extremo superior da varredura, em h = 60 mm. 

### 47

Antes: Em consequência, HCAL é tratado neste trabalho como parâmetro congelado de origem não reproduzida, e não como ótimo identificado. Ele é mantido porque o par (K, Xpose) foi identificado nesse valor e porque o ponto morto correspondente, na elevação de 30,485°, fica a 0,485° do início da zona neutra indicado na patente, ao passo que h = 24,0 mm o deslocaria para 30,909°. A consistência de HCAL com a curva extraída e com as restrições físicas é examinada na seção 4.7.

Depois: Em consequência, HCAL é tratado neste trabalho como parâmetro congelado de origem não reproduzida, e não como ótimo identificado. Ele é mantido porque o par (K, Xpose) foi identificado nesse valor e porque o ponto morto correspondente, na elevação de 30,485°, fica a 0,485° do início da zona neutra indicado na patente, ao passo que h = 24,0 mm o deslocaria para 30,909°. A consistência de HCAL com a curva extraída e com as restrições físicas é examinada na seção 4A.7.

### 48

Antes: A comparação entre formulações obedece à regra da seção 3.9. Com o caminho do cabo igual ao vão livre, a formulação anterior alcança RMSE de 1,152 u.p. no mesmo h, com Xpose = 37,44 mm e K = 175,50 reidentificados; com o caminho completo, o RMSE é de 1,830 u.p. A formulação anterior ajusta melhor a curva publicada, mas viola a conservação de energia (seção 4.3) e, por isso, foi abandonada: o menor RMSE não é critério de validade física.

Depois: A comparação entre formulações obedece à regra da seção 3A.9. Com o caminho do cabo igual ao vão livre, a formulação anterior alcança RMSE de 1,152 u.p. no mesmo h, com Xpose = 37,44 mm e K = 175,50 reidentificados; com o caminho completo, o RMSE é de 1,830 u.p. A formulação anterior ajusta melhor a curva publicada, mas viola a conservação de energia (seção 4A.3) e, por isso, foi abandonada: o menor RMSE não é critério de validade física.

### 49

Antes: 4.5 Qualidade do ajuste à curva da patente

Depois: 4A.5 Qualidade do ajuste à curva da patente

### 50

Antes: A Figura 2 sobrepõe o torque calculado com os parâmetros congelados aos 29 pontos extraídos, e a Tabela 7 reúne os indicadores do ajuste. 

Depois: A Figura 4 sobrepõe o torque calculado com os parâmetros congelados aos 29 pontos extraídos, e a Tabela 9 reúne os indicadores do ajuste. 

### 51

Antes: Figura 2 — Torque do cabo calculado (−τ) e pontos extraídos da patente, com os resíduos no painel inferior (K = 174,68; h = 22,701 mm; Xpose = 37,383 mm) 

Depois: Figura 4 — Torque do cabo calculado (−τ) e pontos extraídos da patente, com os resíduos no painel inferior (K = 174,68; h = 22,701 mm; Xpose = 37,383 mm) 

### 52

Antes: Tabela 7 — Indicadores de qualidade do ajuste à curva da patente

Depois: Tabela 9 — Indicadores de qualidade do ajuste à curva da patente

### 53

Antes: Os resíduos não se distribuem aleatoriamente (Tabela 8). Ordenados por θ*, eles formam três zonas extensas de sinal alternado, que reúnem 25 dos 29 pontos, seguidas de quatro pontos próximos ao ponto morto.

Depois: Os resíduos não se distribuem aleatoriamente (Tabela 10). Ordenados por θ*, eles formam três zonas extensas de sinal alternado, que reúnem 25 dos 29 pontos, seguidas de quatro pontos próximos ao ponto morto.

### 54

Antes: Tabela 8 — Zonas de sinal dos resíduos (modelo − extraído), em ordem de θ*

Depois: Tabela 10 — Zonas de sinal dos resíduos (modelo − extraído), em ordem de θ*

### 55

Antes: O último ponto, em θ* = 193,017°, está além do ponto morto calculado (θ*pm = 192,532°). Ali o modelo prevê torque de −1,709 u.p., com sinal invertido, ao passo que a curva extraída registra 0,443 u.p. A diferença, que responde pelo resíduo da zona 6, é coerente com a ausência, no modelo, da protuberância que mantém o torque residual aproximadamente nulo no dispositivo real (seção 4.9).

Depois: O último ponto, em θ* = 193,017°, está além do ponto morto calculado (θ*pm = 192,532°). Ali o modelo prevê torque de −1,709 u.p., com sinal invertido, ao passo que a curva extraída registra 0,443 u.p. A diferença, que responde pelo resíduo da zona 6, é coerente com a ausência, no modelo, da protuberância que mantém o torque residual aproximadamente nulo no dispositivo real (seção 4A.9).

### 56

Antes: 4.6 Comportamento da mola e do mecanismo

Depois: 4A.6 Comportamento da mola e do mecanismo

### 57

Antes: A Tabela 9 caracteriza o funcionamento do mecanismo na faixa de operação, de θ* = 42,917° a 193,017°, que corresponde a 150,1° de elevação anatômica, de 30° a 180,1°. As grandezas foram calculadas em malha de 0,001° com os parâmetros congelados.

Depois: A Tabela 11 caracteriza o funcionamento do mecanismo na faixa de operação, de θ* = 42,917° a 193,017°, que corresponde a 150,1° de elevação anatômica, de 30° a 180,1°. As grandezas foram calculadas em malha de 0,001° com os parâmetros congelados.

### 58

Antes: Tabela 9 — Grandezas do mecanismo na faixa de operação

Depois: Tabela 11 — Grandezas do mecanismo na faixa de operação

### 59

Antes: O braço de momento confirma a distinção da seção 3.5. A linha de ação do cabo passa pela ancoragem A, de modo que m não pode exceder |OA| = 22,919 mm em configuração alguma. Ao longo da faixa, m cresce monotonicamente de 12,451 mm em θ* = 42,917° até tocar esse teto em θ* = 97,894°, posição em que o cabo fica perpendicular a OA, e decresce a partir daí, anulando-se no ponto morto; o valor de −0,180 mm no extremo da faixa corresponde ao trecho além desse ponto.

Depois: O braço de momento confirma a distinção da seção 3A.5. A linha de ação do cabo passa pela ancoragem A, de modo que m não pode exceder |OA| = 22,919 mm em configuração alguma. Ao longo da faixa, m cresce monotonicamente de 12,451 mm em θ* = 42,917° até tocar esse teto em θ* = 97,894°, posição em que o cabo fica perpendicular a OA, e decresce a partir daí, anulando-se no ponto morto; o valor de −0,180 mm no extremo da faixa corresponde ao trecho além desse ponto.

### 60

Antes: A força máxima K δmáx vale 9.516,5 na unidade de K multiplicada por milímetro. Se a ordenada da patente estivesse em N·m, K estaria em N/mm, a tração no cabo chegaria a 9,5 kN e o pico do torque do cabo, 147,07 N·m, seria 13,2 vezes o pico do torque gravitacional do conjunto, de 11,1619 N·m (seção 4.8). Para equilibrar esse pico gravitacional com o maior braço disponível, 22,919 mm, bastaria uma tração de cerca de 487 N. A leitura da ordenada em N·m conduz, portanto, a valores implausíveis para um dispositivo vestível de apoio ao braço, o que reforça o tratamento da curva publicada como qualitativa quanto à magnitude: o modelo reproduz a forma do torque, mas não sua escala física.

Depois: A força máxima K δmáx vale 9.516,5 na unidade de K multiplicada por milímetro. Se a ordenada da patente estivesse em N·m, K estaria em N/mm, a tração no cabo chegaria a 9,5 kN e o pico do torque do cabo, 147,07 N·m, seria 13,2 vezes o pico do torque gravitacional do conjunto, de 11,1619 N·m (seção 4A.8). Para equilibrar esse pico gravitacional com o maior braço disponível, 22,919 mm, bastaria uma tração de cerca de 487 N. A leitura da ordenada em N·m conduz, portanto, a valores implausíveis para um dispositivo vestível de apoio ao braço, o que reforça o tratamento da curva publicada como qualitativa quanto à magnitude: o modelo reproduz a forma do torque, mas não sua escala física.

### 61

Antes: 4.7 Varredura paramétrica de h com K congelado

Depois: 4A.7 Varredura paramétrica de h com K congelado

### 62

Antes: A Figura 3 mostra a família de curvas de torque para sete valores de h, com K congelado em 174,68 e a extensão na pose fixada em Xpose.

Depois: A Figura 5 mostra a família de curvas de torque para sete valores de h, com K congelado em 174,68 e a extensão na pose fixada em Xpose.

### 63

Antes: Figura 3 — Família de curvas de torque do cabo para h de 16 a 32,886 mm, com K = 174,68 e Xpose = 37,383 mm congelados, e os 29 pontos extraídos da patente

Depois: Figura 5 — Família de curvas de torque do cabo para h de 16 a 32,886 mm, com K = 174,68 e Xpose = 37,383 mm congelados, e os 29 pontos extraídos da patente

### 64

Antes: A Figura 4 apresenta o RMSE em função de h.

Depois: A Figura 6 apresenta o RMSE em função de h.

### 65

Antes: Figura 4 — RMSE contra os pontos extraídos em função de h, com K congelado: faixa completa, em escala logarítmica, com os valores fisicamente viáveis, e ampliação em torno do mínimo, com os platôs de RMSE

Depois: Figura 6 — RMSE contra os pontos extraídos em função de h, com K congelado: faixa completa, em escala logarítmica, com os valores fisicamente viáveis, e ampliação em torno do mínimo, com os platôs de RMSE

### 66

Antes: O menor RMSE, 1,8270 u.p. (R2 = 0,99840), ocorre em h = 22,735 mm, a 0,034 mm de HCAL, que ocupa a 14ª posição entre os 10.403 valores, com RMSE 0,19% maior. Os platôs constam da Tabela 10. O RMSE ultrapassa 2 vezes o mínimo em h = 21,825 e 23,640 mm e 10 vezes o mínimo em h = 17,570 e 27,900 mm.

Depois: O menor RMSE, 1,8270 u.p. (R2 = 0,99840), ocorre em h = 22,735 mm, a 0,034 mm de HCAL, que ocupa a 14ª posição entre os 10.403 valores, com RMSE 0,19% maior. Os platôs constam da Tabela 12. O RMSE ultrapassa 2 vezes o mínimo em h = 21,825 e 23,640 mm e 10 vezes o mínimo em h = 17,570 e 27,900 mm.

### 67

Antes: Tabela 10 — Platôs de RMSE com K congelado

Depois: Tabela 12 — Platôs de RMSE com K congelado

### 68

Antes: A validade física independe da curva extraída. O critério de fechamento foi atendido em todos os 10.403 valores de h, e o de trabalho virtual também, com resíduo máximo de 7,4 × 10−8 mm/rad na grade inteira. O critério decisivo é a tração: com Xpose congelada, o aumento de h aumenta o curso do cabo — de 28,942 mm em h = 15 mm para 42,435 mm em h = 22,701 mm e 106,573 mm em h = 60 mm — e rebaixa a extensão mínima, que ocorre sempre em θ* = 42,917°, onde a demanda gravitacional é mínima, de apenas 1,2% do pico. A extensão mínima se anula na fronteira de tração, h = 32,886 mm. Os valores viáveis formam o intervalo contíguo de 8,000 mm, borda inferior da grade, a 32,885 mm, com 4.979 valores. O valor documental HCAD = 34,785 mm fica fora desse intervalo: com Xpose congelada, o cabo afrouxaria no início da faixa, com extensão mínima de −2,257 mm, e o RMSE seria de 43,48 u.p. (R2 = 0,093). A Tabela 11 reúne os valores notáveis de h.

Depois: A validade física independe da curva extraída. O critério de fechamento foi atendido em todos os 10.403 valores de h, e o de trabalho virtual também, com resíduo máximo de 7,4 × 10−8 mm/rad na grade inteira. O critério decisivo é a tração: com Xpose congelada, o aumento de h aumenta o curso do cabo — de 28,942 mm em h = 15 mm para 42,435 mm em h = 22,701 mm e 106,573 mm em h = 60 mm — e rebaixa a extensão mínima, que ocorre sempre em θ* = 42,917°, onde a demanda gravitacional é mínima, de apenas 1,2% do pico. A extensão mínima se anula na fronteira de tração, h = 32,886 mm. Os valores viáveis formam o intervalo contíguo de 8,000 mm, borda inferior da grade, a 32,885 mm, com 4.979 valores. O valor documental HCAD = 34,785 mm fica fora desse intervalo: com Xpose congelada, o cabo afrouxaria no início da faixa, com extensão mínima de −2,257 mm, e o RMSE seria de 43,48 u.p. (R2 = 0,093). A Tabela 13 reúne os valores notáveis de h.

### 69

Antes: Tabela 11 — Valores notáveis de h na varredura com K congelado

Depois: Tabela 13 — Valores notáveis de h na varredura com K congelado

### 70

Antes: 4.8 Confronto entre o torque do cabo e o torque gravitacional

Depois: 4A.8 Confronto entre o torque do cabo e o torque gravitacional

### 71

Antes: O torque gravitacional do conjunto, calculado pela Equação (24) de forma independente da cadeia do cabo, atinge o máximo de 11,1619 N·m na elevação de 89,44°, o que corrobora a previsão da seção 2.1, de momento gravitacional máximo com o segmento perpendicular à gravidade. O desvio de 0,56° em relação a 90° indica que a linha que une o pivô ao centro de massa do conjunto forma esse ângulo com a direção do braço adotada na convenção da patente. O valor do pico coincide com M g d da Tabela 3. O módulo da Equação (24) oculta a troca de sentido do torque em θ* = 43,579° (elevação de 179,44°), que afeta apenas os 0,66° iniciais da faixa, com torque inferior a 0,13 N·m.

Depois: O torque gravitacional do conjunto, calculado pela Equação (24) de forma independente da cadeia do cabo, atinge o máximo de 11,1619 N·m na elevação de 89,44°, o que corrobora a previsão da seção 2.1, de momento gravitacional máximo com o segmento perpendicular à gravidade. O desvio de 0,56° em relação a 90° indica que a linha que une o pivô ao centro de massa do conjunto forma esse ângulo com a direção do braço adotada na convenção da patente. O valor do pico coincide com M g d da Tabela 5. O módulo da Equação (24) oculta a troca de sentido do torque em θ* = 43,579° (elevação de 179,44°), que afeta apenas os 0,66° iniciais da faixa, com torque inferior a 0,13 N·m.

### 72

Antes: A comparação entre as duas curvas exige cautela metodológica. Como a ordenada da curva publicada não tem unidade declarada e a seção 4.6 mostrou que sua leitura em N·m é implausível, as magnitudes não são comparáveis. O que se pode confrontar é a forma dos perfis, apresentados na Figura 5 normalizados pelos respectivos valores de pico, em função da elevação anatômica. Como a normalização elimina a escala, o confronto não informa que fração do torque gravitacional o mecanismo compensa.

Depois: A comparação entre as duas curvas exige cautela metodológica. Como a ordenada da curva publicada não tem unidade declarada e a seção 4A.6 mostrou que sua leitura em N·m é implausível, as magnitudes não são comparáveis. O que se pode confrontar é a forma dos perfis, apresentados na Figura 7 normalizados pelos respectivos valores de pico, em função da elevação anatômica. Como a normalização elimina a escala, o confronto não informa que fração do torque gravitacional o mecanismo compensa.

### 73

Antes: Figura 5 — Torque do cabo e torque gravitacional normalizados pelos respectivos picos, em função da elevação anatômica (K = 174,68; h = 22,701 mm; Xpose = 37,383 mm)

Depois: Figura 7 — Torque do cabo e torque gravitacional normalizados pelos respectivos picos, em função da elevação anatômica (K = 174,68; h = 22,701 mm; Xpose = 37,383 mm)

### 74

Antes: 4.9 Limitações dos resultados

Depois: 4A.9 Limitações dos resultados

### 75

Antes: Além das limitações de escopo da seção 3.13, os resultados comportam as ressalvas a seguir.

Depois: Além das limitações de escopo da seção 3A.13, os resultados comportam as ressalvas a seguir.

### 76

Antes: Por fim, os resultados referem-se a um único dispositivo, ao indivíduo de referência adotado e ao membro superior estendido sem ferramenta na mão, e limitam-se à análise estática. A generalização a outros percentis antropométricos, a outras configurações de cotovelo e à presença de carga na mão demanda a reexecução do procedimento com os parâmetros correspondentes.

Depois: Por fim, os resultados desta seção referem-se a um único dispositivo, ao indivíduo de referência adotado e ao membro superior estendido sem ferramenta na mão, e limitam-se à análise estática. A generalização a outros percentis antropométricos, a outras configurações de cotovelo e à presença de carga na mão demanda a reexecução do procedimento com os parâmetros correspondentes.

### 77

Antes: O objetivo geral foi atingido em sua parte estática e para um dos três dispositivos previstos. Os objetivos específicos a, b, c e e foram cumpridos; o objetivo d, parcialmente, pois a rigidez e a extensão da mola na pose foram reproduzidas, mas a origem da posição da ancoragem e da calibração angular não. Os objetivos f e g, referentes à equação de movimento e ao acoplamento com o MBDyn, não foram executados. A principal restrição é a ausência de unidade na ordenada da curva da patente: o torque do cabo permanece em unidade da patente, e a leitura em N·m conduz a forças implausíveis, de modo que o modelo determina a forma do torque, mas não sua escala física.

Depois: O objetivo geral foi atingido em sua parte estática e para o primeiro dos três dispositivos previstos; o segundo é tratado na seção 5B. Os objetivos específicos a, b, c e e foram cumpridos; o objetivo d, parcialmente, pois a rigidez e a extensão da mola na pose foram reproduzidas, mas a origem da posição da ancoragem e da calibração angular não. Os objetivos f e g, referentes à equação de movimento e ao acoplamento com o MBDyn, não foram executados. A principal restrição é a ausência de unidade na ordenada da curva da patente: o torque do cabo permanece em unidade da patente, e a leitura em N·m conduz a forças implausíveis, de modo que o modelo determina a forma do torque, mas não sua escala física.

### 78

Antes: Como continuidade, recomenda-se obter um dado independente que fixe a escala do torque, como a especificação de uma mola comercial compatível; conferir no CAD a cota de ancoragem, o comprimento do alojamento e o comprimento da mola na pose; documentar o procedimento de extração dos pontos e sua incerteza; representar a protuberância responsável pela zona neutra; e, com o torque em unidade física, executar as etapas dinâmicas pela formulação de Lagrange e no MBDyn e estender o procedimento à US 9.737.374 B2 e à EP 3 504 033 B1.

Depois: Como continuidade, recomenda-se obter um dado independente que fixe a escala do torque, como a especificação de uma mola comercial compatível; conferir no CAD a cota de ancoragem, o comprimento do alojamento e o comprimento da mola na pose; documentar o procedimento de extração dos pontos e sua incerteza; representar a protuberância responsável pela zona neutra; e, com o torque em unidade física, executar as etapas dinâmicas pela formulação de Lagrange e no MBDyn e estender o procedimento à US 9.737.374 B2. A extensão à EP 3 504 033 B1 é apresentada nas seções 3B, 4B e 5B.
