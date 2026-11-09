# Relatório da fusão dos exoesqueletos 1 e 2

Documento gerado: `TCC_Modelagem_e_simulacao_de_mecanismos_passivos_de_apoio_ao_braco.docx`, a partir de `TCC_apenas_exo1.docx`.

Blocos do original: 305; 5 retirados (REMOVIDOS em gerar_tcc_fundido.py), os demais mantidos e na mesma ordem. Blocos novos: 452. Blocos do original com texto alterado: 121 (renumeração e as edições de EDICOES em gerar_tcc_fundido.py).

## Numeração

Tabelas do original (antes → depois): 1 → 1, 2 → 3, 3 → 4, 4 → 5, 5 → 6, 6 → 7, 7 → 8, 8 → 9, 9 → 10, 10 → 11, 11 → 12.

Figuras do original (antes → depois): 1 → 1, 2 → 8, 3 → 9, 4 → 10, 5 → 11.

Equações do original (antes → depois): 1 → 1, 2 → 2, 3 → 3, 4 → 4, 5 → 5, 6 → 6, 7 → 7, 8 → 8, 9 → 9, 10 → 10, 11 → 11, 12 → 12, 13 → 13, 14 → 14, 15 → 15, 16 → 16, 17 → 17, 18 → 18, 19 → 19, 20 → 20, 21 → 21, 22 → 22, 23 → 23, 24 → 24, 25 → 28, 26 → 29, 27 → 30.

## Blocos do original retirados

- FOROUTANNIA, A.; MOHAMMADIAN, M. A comprehensive survey of lower limb assistive exoskeleton robots: models, dynamics, mechanics, and control. Robotics and Autonomous Systems, [S.l.], v. 195, art. 105232, 2026. DOI: 10.1016/j.robot.2025.105232.
- KIM, H. et al. Redundancy resolution of the human arm and an upper limb exoskeleton. IEEE Transactions on Biomedical Engineering, [S.l.], v. 59, n. 6, p. 1770-1779, 2012. DOI: 10.1109/TBME.2012.2194489.
- NING, Y. et al. Design and analysis of upper limb passive exoskeleton robot for lift assist. Journal of Physics: Conference Series, [S.l.], v. 2410, art. 012020, 2022. DOI: 10.1088/1742-6596/2410/1/012020.
- NING, Y. et al. Structure design and analysis of upper limb wearable passive power-assisted exoskeleton robot. Journal of Physics: Conference Series, [S.l.], v. 2489, art. 012008, 2023. DOI: 10.1088/1742-6596/2489/1/012008.
- OTTOBOCK SE & CO. KGAA. Oliver Mizera et al. Vorrichtung zum Unterstützen wenigstens eines Armes eines Benutzers. EP 3 504 033 B1. Depósito: 6 jun. 2018. Concessão: 29 mar. 2023.

## Blocos do original com texto alterado

### 1

Antes: Este trabalho trata dessa lacuna: modelar e simular, de forma integrada, o comportamento estático e dinâmico de mecanismos passivos de apoio ao braço reconstruídos a partir de suas patentes, usando formulações amplamente conhecidas como a formulação de Lagrange e parâmetros antropométricos de referência.

Depois: Este trabalho trata dessa lacuna: modelar o comportamento estático de mecanismos passivos de apoio ao braço reconstruídos a partir de suas patentes, com parâmetros antropométricos de referência, e preparar a extensão do modelo à dinâmica multicorpos pela formulação de Lagrange.

### 2

Antes: Modelar e simular o comportamento estático e dinâmico de mecanismos passivos de apoio ao braço descritos em patentes, tomando como caso de referência o gerador de torque de mola da US 9.889.554 B2, US 9.737.374 B2 e da EP 3 504 033 B1 e comparar o torque entregue pelo mecanismo ao torque gravitacional do conjunto braço–exoesqueleto ao longo da faixa de elevação.

Depois: Modelar o comportamento estático de mecanismos passivos de apoio ao braço descritos em patentes, tomando como casos de referência os mecanismos da US 9.889.554 B2, da EP 3 504 033 B1 e da US 9.737.374 B2, comparar o torque entregue por cada mecanismo ao torque gravitacional do conjunto braço–exoesqueleto ou à curva publicada na patente ao longo da faixa de elevação e preparar a extensão do procedimento à dinâmica multicorpos.

### 3

Antes: Entre os passivos destinados ao levantamento de cargas, Ning et al. (2023) organizam a estrutura em módulos de braço, ombro e costas e dimensionam o conjunto a partir da tração da mola. Os efeitos documentados pela literatura experimental apresentam direção consistente, porém magnitude variável: a meta-análise de Bär et al. (2021) reúne as reduções de esforço físico agudo associadas ao uso de exoesqueletos ocupacionais, e Moeller et al. (2022) registram diminuição da atividade de deltoide e trapézio na maioria dos 35 estudos revisados, acompanhada, entretanto, de efeitos indesejados quando o ajuste do dispositivo não corresponde à tarefa executada.

Depois: Os efeitos documentados pela literatura experimental apresentam direção consistente, porém magnitude variável: a meta-análise de Bär et al. (2021) reúne as reduções de esforço físico agudo associadas ao uso de exoesqueletos ocupacionais, e Moeller et al. (2022) registram diminuição da atividade de deltoide e trapézio na maioria dos 35 estudos revisados, acompanhada, entretanto, de efeitos indesejados quando o ajuste do dispositivo não corresponde à tarefa executada.

### 4

Antes: A compensação de gravidade constitui problema clássico da síntese de mecanismos. Arakelian (2016) sistematiza as soluções em três grupos, definidos pela natureza da força compensadora — contrapesos, molas ou força ativa proveniente de atuador auxiliar —, e Nguyen (2026) atualiza o panorama das alternativas estritamente passivas e de seus limites de aplicação. Em exoesqueletos vestíveis, a inviabilidade do contrapeso impõe o predomínio da solução elástica, quase sempre associada a cabos, polias ou cames encarregados de moldar a curva de torque; nessa linha, Ning et al. (2022) projetam o perfil da came a partir do módulo de armazenamento de energia da mola e validam o resultado por eletromiografia.

Depois: A compensação de gravidade é problema clássico da síntese de mecanismos. Arakelian (2016) sistematiza as soluções em três grupos, conforme a natureza da força compensadora: contrapesos, molas ou força ativa de um atuador auxiliar. Nguyen (2026) atualiza o panorama das alternativas estritamente passivas e de seus limites de aplicação. Em exoesqueletos vestíveis, o contrapeso é inviável, e predomina a solução elástica, frequentemente associada a cabos, polias ou cames que moldam a curva de torque.

### 5

Antes: A patente US 9.889.554 B2 (VAN ENGELHOVEN; KAZEROONI, 2018) descreve arranjo dessa natureza: um elo proximal, solidário a uma base fixada ao tronco, articula-se com um elo distal que acompanha o braço, e um gerador de força de tração, constituído por mola e cabo tensionado sobre uma polia, produz o torque de apoio. Abaixo de um ângulo de transição (toggle angle), uma protuberância situada junto à junta restringe a mola, de modo que o torque decai a valor residual e o membro recupera liberdade de movimento. A patente EP 3 504 033 B1 (OTTOBOCK, 2023), por sua vez, endereça o mesmo problema por caminho construtivo distinto, transmitindo a força de um atuador passivo por meio de elemento rígido apoiado na pelve.

Depois: A patente US 9.889.554 B2 (VAN ENGELHOVEN; KAZEROONI, 2018) descreve um arranjo desse tipo: um elo proximal, solidário a uma base fixada ao tronco, articula-se com um elo distal que acompanha o braço, e um gerador de força de tração, formado por mola e cabo tensionado sobre uma polia, produz o torque de apoio. Abaixo de um ângulo de transição (toggle angle), uma protuberância junto à junta restringe o gerador de força, o torque cai a um valor residual e o braço recupera a liberdade de movimento.

### 6

Antes: Em ambos os documentos, contudo, as figuras exibem apenas a forma dos perfis de torque, desprovidas de escala nos eixos, o que inviabiliza o aproveitamento direto dos dados publicados e motiva a reconstrução geométrica adotada neste trabalho.

Depois: Nenhum dos dois documentos, contudo, permite quantificar o torque: as curvas publicadas têm a abscissa em graus, mas a ordenada não tem unidade declarada na US 9.889.554 B2 e não tem sequer valores na EP 3 504 033 B1. Isso inviabiliza o aproveitamento direto dos dados publicados e motiva a reconstrução geométrica adotada neste trabalho.

### 7

Antes: O mapeamento da curva torque × ângulo gerada pelo mecanismo permite alinhar o perfil de suporte elástico à curva anatômica de carga do braço, otimizando a entrega de torque nas posições de maior exigência (NING et al., 2022; OKABE et al., 2025). Palazzi et al. (2022) mostram, em um exoesqueleto balanceado por gravidade, redução de 89% no torque de pico do ombro quando esse ajuste é bem resolvido.

Depois: O mapeamento da curva torque × ângulo gerada pelo mecanismo permite alinhar o perfil de suporte elástico à curva anatômica de carga do braço, otimizando a entrega de torque nas posições de maior exigência (OKABE; BRITTES; BRITO, 2026). Palazzi et al. (2022) mostram, em um exoesqueleto balanceado por gravidade, redução de 89% no torque de pico do ombro quando esse ajuste é bem resolvido.

### 8

Antes: Näf et al. (2018) revisam nove categorias de estratégias de compensação de desalinhamento e as avaliam segundo o domínio de aplicação e os requisitos específicos de cada um, ao passo que Yoon et al. (2022) demonstram que a otimização da posição das juntas de um exoesqueleto de ombro reduz simultaneamente a força de interação e o volume ocupado pela estrutura. Tais forças de contato constituem, precisamente, uma das grandezas de saída que o modelo desenvolvido neste trabalho se propõe a estimar.

Depois: Näf et al. (2018) revisam nove categorias de estratégias de compensação de desalinhamento e as avaliam segundo o domínio de aplicação e os requisitos específicos de cada um, ao passo que Yoon et al. (2022) demonstram que a otimização da posição das juntas de um exoesqueleto de ombro reduz simultaneamente a força de interação e o volume ocupado pela estrutura.

### 9

Antes: O Airframe, da Levitate Technologies, adota sistema adaptativo de apoio no qual o elemento elástico é progressivamente engajado à medida que o braço se eleva, transferindo-se a carga ao tronco e à cintura pélvica (DOYLE, 2017). Já o Paexo, da Ottobock, emprega elemento elástico atuando sobre braço de alavanca ajustável, de modo que o suporte é máximo com o braço próximo da horizontal e se anula com o braço junto ao corpo (OTTOBOCK, 2023). Apesar das diferenças construtivas, as três soluções perseguem idêntico objetivo funcional: sintetizar, por meio da geometria e de um único elemento elástico, perfil de torque que acompanhe o momento gravitacional do membro superior ao longo da elevação.

Depois: O Airframe, da Levitate Technologies, adota sistema adaptativo de apoio no qual o elemento elástico é progressivamente engajado à medida que o braço se eleva, transferindo-se a carga ao tronco e à cintura pélvica (DOYLE, 2017). Já o Paexo, da Ottobock, emprega elemento elástico atuando sobre braço de alavanca ajustável, de modo que o suporte é máximo com o braço próximo da horizontal e se anula com o braço junto ao corpo (MIZERA et al., 2023). Os nomes comerciais não aparecem nas patentes citadas, que identificam apenas os titulares; a associação de cada produto à sua patente não pôde ser conferida nesses documentos (seção 3.2.1). Apesar das diferenças construtivas, as três soluções perseguem idêntico objetivo funcional: sintetizar, por meio da geometria e de um único elemento elástico, perfil de torque que acompanhe o momento gravitacional do membro superior ao longo da elevação.

### 10

Antes: Wu, Wang e Du (2016) aplicam o princípio a um exoesqueleto de membro superior e relatam redução de 34,6% no consumo de potência em relação à configuração não balanceada. Em exoesqueletos vestíveis, porém, o balanceamento perfeito não constitui o alvo: as restrições de empacotamento, o curso admissível da mola e a exigência de anular o suporte com o braço baixado convertem o problema em exercício de projeto restrito, no qual se busca a melhor aproximação de um perfil desejado dentro de limites construtivos, e não a compensação integral do peso. Por essa razão, o torque de um mecanismo passivo resulta do produto entre a força elástica, função da extensão da mola, e o braço de momento do cabo, ambos dependentes da configuração de forma não linear.

Depois: Wu, Wang e Du (2016) aplicam o princípio a um exoesqueleto de membro superior e relatam redução de 34,6% no consumo de potência em relação à configuração não balanceada. Em exoesqueletos vestíveis, porém, o balanceamento perfeito não constitui o alvo: as restrições de empacotamento, o curso admissível da mola e a exigência de anular o suporte com o braço baixado convertem o problema em exercício de projeto restrito, no qual se busca a melhor aproximação de um perfil desejado dentro de limites construtivos, e não a compensação integral do peso. Nesse exercício de projeto, o torque de um mecanismo passivo resulta do produto entre a força elástica, função da extensão da mola, e o braço de momento do cabo, ambos dependentes da configuração de forma não linear.

### 11

Antes: O trabalho é teórico-computacional. O procedimento parte da reconstrução geométrica do mecanismo e chega ao torque estático que ele entrega em função do ângulo, passando pela identificação dos parâmetros que a patente não publica. Ele foi concebido para os geradores de torque da US 9.889.554 B2, da US 9.737.374 B2 e da EP 3 504 033 B1, mas, nesta etapa do trabalho, foi executado apenas para o gerador de torque da US 9.889.554 B2, ao qual se referem todas as equações deste capítulo e todos os resultados do capítulo 4.

Depois: O trabalho é teórico-computacional. O procedimento parte da reconstrução geométrica do mecanismo e chega ao torque estático que ele entrega em função do ângulo, passando pela identificação dos parâmetros que a patente não publica. Ele foi concebido para os geradores de torque da US 9.889.554 B2, da US 9.737.374 B2 e da EP 3 504 033 B1, mas, nesta etapa do trabalho, foi executado na parte estática: para o gerador de torque da US 9.889.554 B2, ao qual se referem as seções 3.1, 4.1 e 5.1, para o dispositivo da EP 3 504 033 B1, ao qual se referem as seções 3.2, 4.2 e 5.2, e para o mecanismo de came da US 9.737.374 B2, ao qual se referem as seções 3.3, 4.3 e 5.3. As seções 3.1.9, 3.2.9 e 3.3.9 formulam os três modelos estáticos pelo princípio dos trabalhos virtuais, e as seções 3.4, 4.4 e 5.4 comparam os três.

### 12

Antes: A cadeia de cálculo descrita nas seções 3.3 a 3.8 está implementada no arquivo torque_model.py, que contém os parâmetros congelados e não executa ajuste algum. Os números e as figuras do capítulo 4 são produzidos pelo script tcc_resultados.py, que importa esse modelo e chama suas funções com a posição da ancoragem sempre explícita, sem alterar nenhum parâmetro.

Depois: A cadeia de cálculo descrita nas seções 3.1.3 a 3.1.8 está implementada no arquivo torque_model.py, que contém os parâmetros congelados e não executa ajuste algum. Os números e as figuras da seção 4.1 são produzidos pelo script tcc_resultados.py, que importa esse modelo e chama suas funções com a posição da ancoragem sempre explícita, sem alterar nenhum parâmetro.

### 13

Antes: 3.1 Reconstrução geométrica em CAD

Depois: 3.1.1 Reconstrução geométrica em CAD

### 14

Antes: A geometria do mecanismo foi reconstruída no Autodesk Fusion sobre os desenhos da patente, em especial a vista em corte do gerador de torque e o esquema simplificado que define o ângulo entre os elos e as distâncias características. Como as figuras de patente não são cotadas, o modelo foi escalado por um fator único, fixado pela razão entre o comprimento do elo distal reconstruído e o comprimento de segmento do indivíduo de referência.

Depois: A geometria do mecanismo foi reconstruída no Autodesk Fusion sobre os desenhos da patente, em especial a vista em corte do gerador de torque e o esquema simplificado que define o ângulo entre os elos e as distâncias características. Como as figuras de patente não são cotadas, o modelo foi escalado por um fator único, fixado a partir de uma estimativa de medida antropométrica.

### 15

Antes: Da reconstrução saem as grandezas geométricas do mecanismo — distância do pivô ao centro do tambor, raio do tambor, componentes do vetor que liga o pivô à ancoragem do cabo e defasagem angular do desenho —, a pose de referência, com o respectivo comprimento da mola, e o comprimento útil do alojamento da mola. O mesmo modelo fornece massa, posição do centro de massa e momento de inércia de cada peça do exoesqueleto. Por dependerem do fator de escala e da interpretação de desenhos não cotados, essas grandezas são classificadas como medidas em CAD, e não como dimensões do dispositivo comercial.

Depois: Da reconstrução saem as grandezas geométricas do mecanismo — distância do pivô ao centro do tambor, raio do tambor, componentes do vetor que liga o pivô à ancoragem do cabo e defasagem angular do desenho —, a pose de referência, com o respectivo comprimento da mola, e o comprimento útil do alojamento da mola. O mesmo modelo fornece massa, posição do centro de massa e momento de inércia de cada peça do exoesqueleto. Por dependerem do fator de escala e da interpretação de desenhos não cotados, essas grandezas são classificadas como medidas em CAD, e não como dimensões do dispositivo comercial. As propriedades de massa dependem, além disso, do material atribuído a cada peça no CAD e são estimativas, e não propriedades do produto.

### 16

Antes: 3.2 Parâmetros inerciais do membro e transporte ao eixo da junta

Depois: 3.1.2 Parâmetros inerciais do membro e transporte ao eixo da junta

### 17

Antes: Massa, posição do centro de massa e raios de giro de braço, antebraço e mão foram obtidos das tabelas de de Leva (1996) para o indivíduo masculino de referência, com o cotovelo estendido. Os momentos de inércia de cada corpo, do membro e das peças do exoesqueleto, foram transportados ao eixo da junta pelo teorema de Steiner:

Depois: Os momentos de inércia de cada corpo, do membro de referência (seção 3) e das peças do exoesqueleto, foram transportados ao eixo da junta pelo teorema de Steiner:

### 18

Antes: em que IO é o momento de inércia em relação ao eixo da junta, Icm o momento de inércia em relação ao eixo paralelo que passa pelo centro de massa, M a massa e d a distância entre os dois eixos. A composição foi feita em planilha, construída para recalcular o conjunto quando qualquer entrada muda. Conforme a seção 2.9, o momento de inércia não participa do torque estático do peso, que depende apenas da massa e da posição do centro de massa (seção 3.8); ele se destina à etapa dinâmica prevista na seção 3.12.

Depois: em que IO é o momento de inércia em relação ao eixo da junta, Icm o momento de inércia em relação ao eixo paralelo que passa pelo centro de massa, M a massa e d a distância entre os dois eixos. A composição foi feita em planilha, construída para recalcular o conjunto quando qualquer entrada muda. Conforme a seção 2.9, o momento de inércia não participa do torque estático do peso, que depende apenas da massa e da posição do centro de massa (seção 3.1.8); ele se destina à etapa dinâmica prevista na seção 3.1.13.

### 19

Antes: 3.3 Referenciais e convenções angulares e de sinal

Depois: 3.1.3 Referenciais e convenções angulares e de sinal

### 20

Antes: O mecanismo é tratado como plano, com origem O no eixo da junta (pivô). Comprimentos são expressos em milímetros e ângulos em graus na entrada, com uma única conversão para radianos dentro das contas. Quatro ângulos aparecem no cálculo e são mantidos separados, por serem fonte recorrente de erro (Tabela 1). O ângulo interno θ* entre os elos é a variável independente do modelo, e q é sua versão referida ao desenho:

Depois: O mecanismo é tratado como plano, com origem O no eixo da junta (pivô). Seis ângulos aparecem no cálculo e são mantidos separados, por serem fonte recorrente de erro (Tabela 1). O ângulo interno θ* entre os elos é a variável independente do modelo, e q é sua versão referida ao desenho:

### 21

Antes: em que θoff = 133,017° é a calibração angular identificada (seção 3.9). A faixa da patente, φpat de −60° a +90,1°, corresponde a θ* de 42,917° a 193,017° e a elevação de 30° a 180,1°; a elevação cresce quando θ* decresce. O ângulo φpat não deve ser confundido com φ, direção da linha do cabo calculada pelo modelo (seção 3.4).

Depois: em que θoff = 133,017° é a calibração angular identificada (seção 3.1.10). A faixa da patente, φpat de −60° a +90,1°, corresponde a θ* de 42,917° a 193,017° e a elevação de 30° a 180,1°; a elevação cresce quando θ* decresce. O ângulo φpat não deve ser confundido com φ, direção da linha do cabo calculada pelo modelo (seção 3.1.4).

### 22

Antes: 3.4 Equação de fechamento do circuito vetorial

Depois: 3.1.4 Equação de fechamento do circuito vetorial

### 23

Antes: em que h e p são as componentes desse vetor no referencial do elo proximal. A posição da ancoragem h é o parâmetro geométrico mais incerto do mecanismo e permanece explícita em todas as equações; a cota lida no CAD, HCAD = 34,785 mm, é tratada como valor documental, e o valor adotado no modelo é HCAL = 22,701 mm (seção 3.9). Com u(x) = (cos x, sen x) e u⊥(x) = (−sen x, cos x), o fechamento do circuito se escreve

Depois: em que h e p são as componentes desse vetor no referencial do elo proximal. A posição da ancoragem h é o parâmetro geométrico mais incerto do mecanismo e permanece explícita em todas as equações; a cota lida no CAD, HCAD = 34,785 mm, é uma medida em CAD, distinta do valor adotado no modelo, HCAL = 22,701 mm (seção 3.1.10). Com u(x) = (cos x, sin x) e u⊥(x) = (−sin x, cos x), o fechamento do circuito se escreve

### 24

Antes: Nota: O é o pivô, A a ancoragem do cabo, D o centro do tambor e T o ponto de tangência. O painel da direita amplia a região do pivô, onde se distinguem o vetor B e o braço m.

Depois: Nota: O é o pivô, A a ancoragem do cabo, D o centro do tambor e T o ponto de tangência. O painel da direita amplia a região do pivô, onde se distinguem o vetor B e o braço m. As componentes h e p de B estão tracejadas, e os arcos marcam os ângulos θ*, α, q e φ da Tabela 1, medidos no sentido anti-horário.

### 25

Antes: 3.5 Ponto de tangência, distância b, ângulo β e braço de momento

Depois: 3.1.5 Ponto de tangência, distância b, ângulo β e braço de momento

### 26

Antes: em que φB = atan2(By, Bx) é a direção do vetor B. As duas vias são comparadas numericamente (seção 3.11), e a Equação (10) é a usada na cadeia por não depender do sinal de β. A distância b, entretanto, não é o braço de momento do cabo: como T pertence a uma circunferência de raio R centrada a C do pivô, b fica necessariamente entre C − R e C + R. O braço de momento é a distância perpendicular do pivô à linha de ação do cabo, que passa por A com direção u(φ):

Depois: em que φB = atan2(By, Bx) é a direção do vetor B. As duas vias são comparadas numericamente (seção 3.1.12), e a Equação (10) é a usada na cadeia por não depender do sinal de β. A distância b, entretanto, não é o braço de momento do cabo: como T pertence a uma circunferência de raio R centrada a C do pivô, b fica necessariamente entre C − R e C + R. O braço de momento é a distância perpendicular do pivô à linha de ação do cabo, que passa por A com direção u(φ):

### 27

Antes: O braço m tem sinal, anula-se quando a linha do cabo passa pelo pivô (ponto morto, seção 3.7) e é limitado pelo comprimento |B| = |OA|, teto que decorre do traçado do cabo, e não do ajuste.

Depois: O braço m tem sinal, anula-se quando a linha do cabo passa pelo pivô (ponto morto, seção 3.1.7) e é limitado pelo comprimento |B| = |OA|, teto que decorre do traçado do cabo, e não do ajuste.

### 28

Antes: 3.6 Caminho do cabo, lei da mola e torque

Depois: 3.1.6 Caminho do cabo, lei da mola e torque

### 29

Antes: Entra no modelo apenas a parcela variável do enrolamento, um arco constante cancela-se na extensão da mola, porque o caminho e o comprimento de referência são calculados pela mesma expressão. O sinal do termo do arco foi fixado pelo princípio dos trabalhos virtuais. Em um mecanismo conservativo, sem atrito no tambor, o trabalho da tração no cabo iguala o do torque no elo, o que exige

Depois: Entra no modelo apenas a parcela variável do enrolamento, um arco constante cancela-se na extensão da mola, porque o caminho e o comprimento de referência são calculados pela mesma expressão. O sinal do termo do arco foi fixado pelo princípio dos trabalhos virtuais, formulado na seção 3.1.9. Em um mecanismo conservativo, sem atrito no tambor, o trabalho da tração no cabo iguala o do torque no elo, o que exige

### 30

Antes: com θ* em radianos. A Equação (17) é verificada numericamente por diferenças finitas centradas (seção 3.11) e permite discriminar entre formulações do caminho do cabo: com o caminho igual apenas ao vão livre, ela não é satisfeita (seção 4.3).

Depois: com θ* em radianos. A Equação (17) é verificada numericamente por diferenças finitas centradas (seção 3.1.12) e permite discriminar entre formulações do caminho do cabo: com o caminho igual apenas ao vão livre, ela não é satisfeita (seção 4.1.3).

### 31

Antes: A identidade τ = −F m/1000 decorre de T e A estarem sobre a mesma linha de ação e é verificada numericamente (seção 3.11). O fator 1/1000 vem da formulação original, em que os comprimentos estão em milímetros. Como K é identificado contra a curva publicada (seção 3.9), cuja ordenada não tem unidade declarada, o torque do cabo é expresso na unidade da própria curva, denotada u.p. (unidade da patente). A unidade de K é, portanto, aquela que faz K δ m/1000 resultar em u.p.; ela só seria N/mm se u.p. correspondesse a N·m, o que não pode ser afirmado com os dados disponíveis (seção 4.6).

Depois: A identidade τ = −F m/1000 decorre de T e A estarem sobre a mesma linha de ação e é verificada numericamente (seção 3.1.12). O fator 1/1000 vem da formulação original, em que os comprimentos estão em milímetros. Como K é identificado contra a curva publicada (seção 3.1.10), cuja ordenada não tem unidade declarada, o torque do cabo é expresso na unidade da própria curva, denotada u.p. (unidade da patente). A unidade de K é, portanto, aquela que faz K δ m/1000 resultar em u.p.; ela só seria N/mm se u.p. correspondesse a N·m, o que não pode ser afirmado com os dados disponíveis (seção 4.1.6).

### 32

Antes: 3.7 Ponto morto

Depois: 3.1.7 Ponto morto

### 33

Antes: 3.8 Torque gravitacional

Depois: 3.1.8 Torque gravitacional

### 34

Antes: O torque estático do peso do conjunto braço–exoesqueleto em relação ao pivô é calculado de forma independente da cadeia do cabo: não usa K, Xpose nem h. O centro de massa (xcm, ycm), dado na pose de referência no referencial do desenho (Tabela 3), gira com o elo, e o desenho gira ainda α + 90° − θoff = −22,589° para alinhar sua vertical com a da configuração calibrada:

Depois: O torque estático do peso do conjunto braço–exoesqueleto em relação ao pivô é calculado de forma independente da cadeia do cabo: não usa K, Xpose nem h. O centro de massa (xcm, ycm), dado na pose de referência no referencial do desenho (Tabela 4), gira com o elo, e o desenho gira ainda α + 90° − θoff = −22,589° para alinhar sua vertical com a da configuração calibrada:

### 35

Antes: em que M é a massa do conjunto, g = 9,80665 m/s2 e xg, em milímetros, é o braço horizontal do centro de massa. O torque gravitacional resulta em N·m, unidade física, ao contrário do torque do cabo. O módulo na Equação (24) desconsidera o sentido do torque, cuja troca ocorre apenas no início da faixa (seção 4.8).

Depois: em que M é a massa do conjunto, g = 9,80665 m/s2 e xg, em milímetros, é o braço horizontal do centro de massa. O torque gravitacional resulta em N·m, unidade física, ao contrário do torque do cabo. O módulo na Equação (24) desconsidera o sentido do torque, cuja troca ocorre apenas no início da faixa (seção 4.1.8).

### 36

Antes: 3.9 Dados da patente e identificação dos parâmetros

Depois: 3.1.10 Dados da patente e identificação dos parâmetros

### 37

Antes: A referência de comparação é a curva torque × ângulo, Figura 56 do gerador de torque publicada na US 9.889.554 B2, da qual foram extraídos 29 pontos, registrados em θ* e listados na Tabela 4 na ordem da extração.

Depois: A referência de comparação é a curva torque × ângulo, Figura 56 do gerador de torque publicada na US 9.889.554 B2, da qual foram extraídos 29 pontos, registrados em θ* e listados na Tabela 5 na ordem da extração.

### 38

Antes: A patente não informa rigidez, pré-carga, comprimento livre nem posição exata da ancoragem. Os parâmetros não publicados do modelo são a calibração angular θoff, a posição da ancoragem h, a extensão da mola na pose Xpose e a rigidez K. Eles foram identificados por mínimos quadrados contra os 29 pontos extraídos em etapa anterior do trabalho e estão congelados no modelo vigente, que não executa ajuste algum. O script dessa etapa e a restrição de projeto então considerada para h não estão registrados no repositório; por isso, a identificação foi reproduzida nesta revisão apenas na parte verificável, descrita a seguir (resultados na seção 4.4).

Depois: A patente não informa rigidez, pré-carga, comprimento livre nem posição exata da ancoragem. Os parâmetros não publicados do modelo são a calibração angular θoff, a posição da ancoragem h, a extensão da mola na pose Xpose e a rigidez K. Eles foram identificados por mínimos quadrados contra os 29 pontos extraídos, por um procedimento que não foi registrado, e estão congelados no modelo, que não executa ajuste algum. Como esse procedimento e a restrição de projeto considerada para h não estão disponíveis, a identificação só pôde ser reproduzida na parte descrita a seguir (resultados na seção 4.1.4).

### 39

Antes: (25)

Depois: (28)

### 40

Antes: Com h e θoff fixados, Xpose foi reidentificado por varredura unidimensional, em passo de 0,001 mm, com K dado pela Equação (25) em cada valor. A qualidade do ajuste é avaliada pela raiz do erro quadrático médio (RMSE), pelo erro absoluto médio (MAE), pelo erro máximo e pelo coeficiente de determinação R2, com resíduo ei = ŷi − yi, em que ŷi é o torque calculado na convenção da patente, −τ:

Depois: Com h e θoff fixados, Xpose foi reidentificado por varredura unidimensional, em passo de 0,001 mm, com K dado pela Equação (28) em cada valor. A qualidade do ajuste é avaliada pela raiz do erro quadrático médio (RMSE), pelo erro absoluto médio (MAE), pelo erro máximo e pelo coeficiente de determinação R2, com resíduo ei = ŷi − yi, em que ŷi é o torque calculado na convenção da patente, −τ:

### 41

Antes: (26)

Depois: (29)

### 42

Antes: O RMSE mede a aderência à curva extraída, e não a validade física. Duas formulações só são comparadas por ele depois de ambas satisfazerem as verificações físicas da seção 3.11; essa regra decide, no capítulo 4, a adoção do caminho completo do cabo, apesar de o caminho sem o arco produzir RMSE menor.

Depois: O RMSE mede a aderência à curva extraída, e não a validade física. Duas formulações só são comparadas por ele depois de ambas satisfazerem as verificações físicas da seção 3.1.12; essa regra decide, no capítulo 4, a adoção do caminho completo do cabo, apesar de o caminho sem o arco produzir RMSE menor.

### 43

Antes: 3.10 Varredura paramétrica de h com K congelado

Depois: 3.1.11 Varredura paramétrica de h com K congelado

### 44

Antes: Para separar o que a curva extraída informa sobre h do que a geometria impõe, h foi varrido de 8 a 60 mm, em passo de 0,005 mm, com o acréscimo dos valores exatos HCAL e HCAD, num total de 10.403 valores. A varredura é um diagnóstico, não uma otimização: K permanece congelado em 174,68 em todos os valores de h, não é reidentificado por h, e nenhum parâmetro do modelo é substituído pelo resultado.

Depois: Para separar o que a curva extraída informa sobre h do que a geometria impõe, h foi varrido de 8 a 60 mm, em passo de 0,005 mm, com o acréscimo dos valores exatos HCAL e HCAD, num total de 10.402 valores distintos, porque a cota do CAD, 34,785 mm, já pertence à malha. A varredura é um diagnóstico, não uma otimização: K permanece congelado em 174,68 em todos os valores de h, não é reidentificado por h, e nenhum parâmetro do modelo é substituído pelo resultado.

### 45

Antes: Para cada h são calculados o RMSE contra os 29 pontos extraídos, que representam exclusivamente o torque do cabo, e três critérios de validade física independentes da curva extraída: (i) tração, isto é, extensão da mola não negativa em toda a faixa de operação, calculada sem a limitação da Equação (19), para que o afrouxamento do cabo apareça como extensão negativa; (ii) fechamento, isto é, existência de tangente ao tambor (ρ > R) em toda a faixa; e (iii) trabalho virtual, isto é, resíduo da Equação (17) inferior a 10−6 mm/rad. O torque gravitacional não entra em nenhum critério da varredura.

Depois: Para cada h são calculados o RMSE contra os 29 pontos extraídos, que representam exclusivamente o torque do cabo, e três critérios de validade física que não usam os pontos extraídos, embora o primeiro dependa da extensão na pose, identificada contra eles: (i) tração, isto é, extensão da mola não negativa em toda a faixa de operação, calculada sem a limitação da Equação (19), para que o afrouxamento do cabo apareça como extensão negativa; (ii) fechamento, isto é, existência de tangente ao tambor (ρ > R) em toda a faixa; e (iii) trabalho virtual, isto é, resíduo da Equação (17) inferior a 10−6 mm/rad. O torque gravitacional não entra em nenhum critério da varredura.

### 46

Antes: 3.11 Verificações numéricas e testes automatizados

Depois: 3.1.12 Verificações numéricas e testes automatizados

### 47

Antes: 3.12 Etapas dinâmicas previstas

Depois: 3.1.13 Etapas dinâmicas previstas

### 48

Antes: (27)

Depois: (30)

### 49

Antes: em que τg,s é o torque gravitacional com sinal e Qnc reúne os esforços não conservativos, como o atrito. A verificação prevista compreende a conservação da energia na ausência de dissipação, a recuperação do resultado estático quando as velocidades tendem a zero e a consistência entre o braço de momento e a derivada do caminho do cabo, esta última já cumprida no modelo estático (seção 4.3). No acoplamento ao MBDyn, que integra o sistema multicorpos pela formulação de Masarati, Morandini e Mantegazza (2014), o gerador de torque entraria como força externa, com troca de configuração e de torque por socket a cada passo de integração, e a comparação com a integração própria, sob as mesmas condições iniciais, serviria de validação cruzada.

Depois: em que τg,s é o torque gravitacional com sinal e Qnc reúne os esforços não conservativos, como o atrito. A verificação prevista compreende a conservação da energia na ausência de dissipação, a recuperação do resultado estático quando as velocidades tendem a zero e a consistência entre o braço de momento e a derivada do caminho do cabo, esta última já cumprida no modelo estático (seção 4.1.3). No acoplamento ao MBDyn, que integra o sistema multicorpos pela formulação de Masarati, Morandini e Mantegazza (2014), o gerador de torque entraria como força externa, com troca de configuração e de torque por socket a cada passo de integração, e a comparação com a integração própria, sob as mesmas condições iniciais, serviria de validação cruzada.

### 50

Antes: As duas etapas dependem de um pré-requisito ainda não satisfeito: a Equação (27) soma o torque do cabo ao torque gravitacional e exige ambos na mesma unidade física. Enquanto K estiver referido à ordenada sem unidade da patente, a integração da equação de movimento não tem significado físico.

Depois: As duas etapas dependem de um pré-requisito ainda não satisfeito: a Equação (30) soma o torque do cabo ao torque gravitacional e exige ambos na mesma unidade física. Enquanto K estiver referido à ordenada sem unidade da patente, a integração da equação de movimento não tem significado físico.

### 51

Antes: 3.13 Ferramentas e delimitação

Depois: 3.1.14 Ferramentas e delimitação

### 52

Antes: Foram empregados o Autodesk Fusion, para a reconstrução geométrica e a extração das propriedades de massa; uma planilha eletrônica, para o transporte de eixos e a composição inercial; e a linguagem Python, com a biblioteca NumPy (HARRIS et al., 2020) para o cálculo vetorizado, a biblioteca Matplotlib (HUNTER, 2007) para as figuras e o pytest para os testes automatizados. A identificação não depende de biblioteca de otimização: K tem forma fechada, Equação (25), e as demais grandezas são obtidas por varredura direta e por bissecção. O MBDyn, previsto para a simulação multicorpos, não foi empregado nesta etapa.

Depois: Foram empregados o Autodesk Fusion, para a reconstrução geométrica e a extração das propriedades de massa; uma planilha eletrônica, para o transporte de eixos e a composição inercial; e a linguagem Python, com a biblioteca NumPy (HARRIS et al., 2020) para o cálculo vetorizado, a biblioteca Matplotlib (HUNTER, 2007) para as figuras e o pytest para os testes automatizados. A identificação não depende de biblioteca de otimização: K tem forma fechada, Equação (28), e as demais grandezas são obtidas por varredura direta e por bissecção. O MBDyn, previsto para a simulação multicorpos, não foi empregado nesta etapa.

### 53

Antes: Não integram o escopo a avaliação experimental com participantes humanos, a eletromiografia, a análise de conforto e usabilidade, a fabricação e o ensaio de protótipo e o dimensionamento estrutural dos elos. O modelo é plano e admite cabo inextensível, tambor sem atrito e mola linear sem tração inicial, F = K δ. Os parâmetros antropométricos correspondem ao indivíduo de referência adotado, e o torque gravitacional é calculado para o membro superior estendido, sem ferramenta na mão. O modelo não representa a protuberância que, na patente, cria a zona neutra após o ângulo de transição.

Depois: O modelo é plano e admite cabo inextensível, tambor sem atrito e mola linear sem tração inicial, F = K δ. O modelo não representa a protuberância que, na patente, cria a zona neutra após o ângulo de transição.

### 54

Antes: Este capítulo apresenta os resultados das etapas descritas nas seções 3.1 a 3.11, aplicadas ao gerador de torque da US 9.889.554 B2. Salvo indicação em contrário, os números foram obtidos com o modelo vigente e os parâmetros congelados K = 174,68, HCAL = 22,701 mm e Xpose = 37,383 mm. As etapas dinâmicas da seção 3.12 e a aplicação do procedimento à US 9.737.374 B2 e à EP 3 504 033 B1 não foram executadas.

Depois: Esta seção apresenta os resultados das etapas descritas nas seções 3.1.1 a 3.1.12, aplicadas ao gerador de torque da US 9.889.554 B2. Salvo indicação em contrário, os números foram obtidos com o modelo vigente e os parâmetros congelados K = 174,68, HCAL = 22,701 mm e Xpose = 37,383 mm. As etapas dinâmicas da seção 3.1.13 não foram executadas.

### 55

Antes: 4.1 Geometria reconstruída e propriedades de massa

Depois: 4.1.1 Geometria reconstruída e propriedades de massa

### 56

Antes: A reconstrução da vista em corte do gerador de torque forneceu as grandezas da Tabela 2. O fator de escala único, fixado pela razão entre o comprimento do elo distal reconstruído e o comprimento de segmento do indivíduo de referência, resultou em 0,870.

Depois: A reconstrução da vista em corte do gerador de torque forneceu as grandezas da Tabela 3.

### 57

Antes: Tabela 2 — Grandezas medidas na reconstrução em CAD

Depois: Tabela 3 — Grandezas medidas na reconstrução em CAD

### 58

Antes: A composição inercial do conjunto braço–exoesqueleto, obtida pelo transporte dos momentos ao eixo da junta, consta da Tabela 3. Os segmentos do membro seguem de Leva (1996) para o indivíduo masculino de referência, de 73,0 kg e 1,741 m, com o cotovelo estendido; as peças do exoesqueleto provêm do modelo em CAD.

Depois: A composição inercial do conjunto braço–exoesqueleto, obtida pelo transporte dos momentos ao eixo da junta, consta da Tabela 4. Os segmentos do membro seguem de Leva (1996) para o indivíduo masculino de referência, de 73,0 kg e 1,741 m, com o cotovelo estendido; as peças do exoesqueleto provêm do modelo em CAD.

### 59

Antes: Tabela 3 — Propriedades de massa do conjunto braço–exoesqueleto

Depois: Tabela 4 — Propriedades de massa do conjunto braço–exoesqueleto

### 60

Antes: A consistência interna da Tabela 3 foi conferida: Icm + M d2 = 0,127111 + 0,321116 = 0,448227 kg·m2, igual ao momento de inércia no eixo da junta, conforme a Equação (1); e M g d = 11,1619 N·m coincide com o pico do torque gravitacional calculado pela Equação (24) (seção 4.8). O momento de inércia destina-se à etapa dinâmica, não executada, e não participa do cálculo do torque estático.

Depois: A consistência interna da Tabela 4 foi conferida: Icm + M d2 = 0,127111 + 0,321116 = 0,448227 kg·m2, igual ao momento de inércia no eixo da junta, conforme a Equação (1); e M g d = 11,1619 N·m coincide com o pico do torque gravitacional calculado pela Equação (24) (seção 4.1.8). O momento de inércia destina-se à etapa dinâmica, não executada, e não participa do cálculo do torque estático.

### 61

Antes: 4.2 Dados extraídos da patente

Depois: 4.1.2 Dados extraídos da patente

### 62

Antes: A Tabela 4 reúne os 29 pontos extraídos da curva da patente, na ordem da extração, com os ângulos correspondentes nas convenções da seção 3.3, o torque calculado pelo modelo com os parâmetros congelados e o resíduo. Os pontos cobrem θ* de 42,909° a 193,017°, isto é, elevação de 180,1° a 30,0°, com espaçamento irregular, de 2,87° a 8,03° em θ*. O maior valor extraído, 147,310 u.p., ocorre em θ* = 123,196° (elevação de 99,8°), e a média dos 29 valores é 81,840 u.p. Os valores são expressos em u.p. porque a figura de origem não declara unidade (seção 2.10).

Depois: A Tabela 5 reúne os 29 pontos extraídos da curva da patente, na ordem da extração, com os ângulos correspondentes nas convenções da seção 3.1.3, o torque calculado pelo modelo com os parâmetros congelados e o resíduo. Os pontos cobrem θ* de 42,909° a 193,017°, isto é, elevação de 180,1° a 30,0°, com espaçamento irregular, de 2,87° a 8,03° em θ*; o ponto 29, em θ* = 42,909°, fica 0,008° abaixo do limite inferior da faixa de operação, θ* = 42,917° (seção 3.1.3). O maior valor extraído, 147,310 u.p., ocorre em θ* = 123,196° (elevação de 99,8°), e a média dos 29 valores é 81,840 u.p. Os valores são expressos em u.p. porque a figura de origem não declara unidade (seção 2.10).

### 63

Antes: Tabela 4 — Pontos extraídos da curva da patente e torque calculado pelo modelo

Depois: Tabela 5 — Pontos extraídos da curva da patente e torque calculado pelo modelo

### 64

Antes: 4.3 Verificação da cadeia de cálculo

Depois: 4.1.3 Verificação da cadeia de cálculo

### 65

Antes: As verificações automáticas da seção 3.11 resultaram nos resíduos da Tabela 5, todos da ordem do erro de arredondamento da aritmética de ponto flutuante, exceto o do trabalho virtual, limitado pelo truncamento da diferença finita.

Depois: As verificações automáticas da seção 3.1.12 resultaram nos resíduos da Tabela 6, todos da ordem do erro de arredondamento da aritmética de ponto flutuante, exceto o do trabalho virtual, limitado pelo truncamento da diferença finita.

### 66

Antes: Tabela 5 — Verificações da cadeia de cálculo (h = 22,701 mm)

Depois: Tabela 6 — Verificações da cadeia de cálculo (h = 22,701 mm)

### 67

Antes: VerificaçãoResíduo máximoEquações de fechamento f1 e f2, Equação (6)1,4 × 10−13 mmIdentidade τ = −F m/1000, Equação (20), com força unitária1,6 × 10−13 mmPonto de tangência pelas Equações (10) e (13)8,0 × 10−13 mmPonto morto, Equação (21) contra bissecção1,3 × 10−11 grauTrabalho virtual, Equação (17)4,7 × 10−8 mmPar da mola, Xpose = Lpose − Llivre7,1 × 10−15 mm

Depois: VerificaçãoResíduo máximoEquações de fechamento f1 e f2, Equação (6)1,4 × 10−13 mmIdentidade τ = −F m/1000, Equação (20), com força unitária1,6 × 10−13 mmPonto de tangência pelas Equações (10) e (13)8,0 × 10−13 mmPonto morto, Equação (21) contra bissecção1,3 × 10−11 grauTrabalho virtual, Equação (17)4,7 × 10−8 mm/radPar da mola, Xpose = Lpose − Llivre7,1 × 10−15 mm

### 68

Antes: A verificação do trabalho virtual decidiu a formulação do caminho do cabo. Com a extensão da mola acompanhando apenas o vão livre s, como na formulação inicialmente pensada, o resíduo da Equação (17) é de 1,7129 mm; com o arco somado ao vão, s + Rψ, é de 3,4258 mm; somente com ℓ = s − Rψ, Equação (16), ele cai a 4,7 × 10−8 mm. Um resíduo da ordem do milímetro significa que o modelo entrega torque sem a correspondente variação da energia da mola, violando assim, a conservação de energia em um mecanismo sem atrito.

Depois: A verificação do trabalho virtual decidiu a formulação do caminho do cabo. Com a extensão da mola acompanhando apenas o vão livre s, o resíduo da Equação (17) é de 1,7129 mm/rad; com o arco somado ao vão, s + Rψ, é de 3,4258 mm/rad; somente com ℓ = s − Rψ, Equação (16), ele cai a 4,7 × 10−8 mm/rad. Um resíduo da ordem de 1 mm/rad significa que o modelo entrega torque sem a correspondente variação da energia da mola, violando assim, a conservação de energia em um mecanismo sem atrito.

### 69

Antes: Embora fora constatado que o efeito do arco é pequeno em valor absoluto. O arco varia 1,862 mm na faixa de operação, contra 42,435 mm de variação do caminho total (4,4%). Com a mesma ancoragem na pose, sua incorporação altera a extensão da mola em até 1,782 mm, em θ* = 193,017° (elevação de 30°), onde a extensão está próxima do máximo e o desvio relativo é de 3,3%. Em termos relativos, o efeito é maior no extremo oposto, em θ* = 42,917° (elevação de 180,1°), onde a extensão cai a 12,044 mm e o desvio chega a 6,3%.

Depois: Constatou-se, contudo, que o efeito do arco é pequeno em valor absoluto. O arco varia 1,862 mm na faixa de operação, contra 42,435 mm de variação do caminho total (4,4%). Com a mesma ancoragem na pose, sua incorporação altera a extensão da mola em até 1,782 mm, em θ* = 193,017° (elevação de 30°), onde a extensão está próxima do máximo e o desvio relativo é de 3,3%. Em termos relativos, o efeito é maior no extremo oposto, em θ* = 42,917° (elevação de 180,1°), onde a extensão cai a 12,044 mm e o desvio chega a 6,3%.

### 70

Antes: 4.4 Parâmetros do modelo e reprodução da identificação

Depois: 4.1.4 Parâmetros do modelo e reprodução da identificação

### 71

Antes: A Tabela 6 reúne os parâmetros não publicados pela patente, com seus valores congelados e a situação de cada um nesta revisão.

Depois: A Tabela 7 reúne os parâmetros não publicados pela patente, com seus valores congelados e a situação de cada um.

### 72

Antes: Tabela 6 — Parâmetros não publicados, origem e verificação

Depois: Tabela 7 — Parâmetros não publicados, origem e verificação

### 73

Antes: ParâmetroSímboloValorOrigemCalibração angularθoff133,017°Identificado em etapa anteriorPosição da ancoragemHCAL22,701 mmIdentificado em etapa anteriorExtensão da mola na poseXpose37,383 mmIdentificadoRigidez da molaK174,68Identificado

Depois: ParâmetroSímboloValorOrigemCalibração angularθoff133,017°Congelado; origem não reproduzidaPosição da ancoragemHCAL22,701 mmCongelado; origem não reproduzidaExtensão da mola na poseXpose37,383 mmIdentificadoRigidez da molaK174,68Identificado

### 74

Antes: Nota: K tem a unidade que faz K δ m/1000 resultar em u.p. (seção 3.6).

Depois: Nota: K tem a unidade que faz K δ m/1000 resultar em u.p. (seção 3.1.6).

### 75

Antes: Com h = 22,701 mm e θoff congelados, a varredura de Xpose com K dado pela Equação (25) reproduz o par identificado: Xpose = 37,383 mm, K = 174,676 e RMSE de 1,8305 u.p., coincidentes com os valores congelados até a resolução da varredura. O valor 174,68 é, portanto, o arredondamento do K de mínimos quadrados no h adotado, e o par (K, h) é consistente.

Depois: Com h = 22,701 mm e θoff congelados, a varredura de Xpose com K dado pela Equação (28) reproduz o par identificado: Xpose = 37,383 mm, K = 174,676 e RMSE de 1,8305 u.p., coincidentes com os valores congelados até a resolução da varredura. O valor 174,68 é, portanto, o arredondamento do K de mínimos quadrados no h adotado, e o par (K, h) é consistente.

### 76

Antes: A origem de HCAL = 22,701 mm, ao contrário, não pôde ser reproduzida. Para auditar essa afirmação, foi executada uma análise complementar em que Xpose e K são reidentificados para cada h, de 8 a 60 mm em passo de 0,25 mm. Essa análise não é o procedimento principal deste trabalho, que mantém K congelado (seção 3.10), e serve apenas para conferir a afirmação anterior. O RMSE resultante apresenta mínimo interior em h ≈ 24,0 mm, com RMSE de 1,682 u.p., Xpose = 38,83 mm e K = 160,46, e cresce para valores maiores de h. A razão entre a extensão máxima e o comprimento livre vale 1,0095 em h = 22,701 mm, iguala 1 em h ≈ 22,52 mm e só ultrapassa 10 próximo do extremo superior da varredura, em h = 60 mm. 

Depois: A origem de HCAL = 22,701 mm, ao contrário, não pôde ser reproduzida. Para verificar se esse valor é um ótimo da curva extraída, foi executada uma análise complementar em que Xpose e K são reidentificados para cada h, de 8 a 60 mm em passo de 0,25 mm. Essa análise não é o procedimento principal deste trabalho, que mantém K congelado (seção 3.1.11), e serve apenas para essa verificação. O RMSE resultante apresenta mínimo interior em h ≈ 24,0 mm, com RMSE de 1,682 u.p., Xpose = 38,83 mm e K = 160,46, e cresce para valores maiores de h. O vale é largo: na malha de 0,25 mm, o RMSE fica abaixo de 1,01 vez o mínimo de h = 23,75 a 24,50 mm e abaixo de 2 vezes o mínimo de h = 19,25 a 31,00 mm, faixa em que K vai de 222,1 a 106,6; com K e a extensão na pose livres, a curva extraída não determina h. 

### 77

Antes: Em consequência, HCAL é tratado neste trabalho como parâmetro congelado de origem não reproduzida, e não como ótimo identificado. Ele é mantido porque o par (K, Xpose) foi identificado nesse valor e porque o ponto morto correspondente, na elevação de 30,485°, fica a 0,485° do início da zona neutra indicado na patente, ao passo que h = 24,0 mm o deslocaria para 30,909°. A consistência de HCAL com a curva extraída e com as restrições físicas é examinada na seção 4.7.

Depois: Em consequência, HCAL é tratado neste trabalho como parâmetro congelado de origem não reproduzida, e não como ótimo identificado. Ele é mantido porque o par (K, Xpose) foi identificado nesse valor e porque o ponto morto correspondente, na elevação de 30,485°, fica a 0,485° do início da zona neutra indicado na patente, ao passo que h = 24,0 mm o deslocaria para 30,909°. A consistência de HCAL com a curva extraída e com as restrições físicas é examinada na seção 4.1.7.

### 78

Antes: A comparação entre formulações obedece à regra da seção 3.9. Com o caminho do cabo igual ao vão livre, a formulação anterior alcança RMSE de 1,152 u.p. no mesmo h, com Xpose = 37,44 mm e K = 175,50 reidentificados; com o caminho completo, o RMSE é de 1,830 u.p. A formulação anterior ajusta melhor a curva publicada, mas viola a conservação de energia (seção 4.3) e, por isso, foi abandonada: o menor RMSE não é critério de validade física.

Depois: A comparação entre formulações obedece à regra da seção 3.1.10. Com o caminho do cabo igual ao vão livre, a formulação sem o arco alcança RMSE de 1,152 u.p. no mesmo h, com Xpose = 37,44 mm e K = 175,50 reidentificados; com o caminho completo, o RMSE é de 1,830 u.p. A formulação sem o arco ajusta melhor a curva publicada, mas viola a conservação de energia (seção 4.1.3) e, por isso, não foi adotada: o menor RMSE não é critério de validade física.

### 79

Antes: 4.5 Qualidade do ajuste à curva da patente

Depois: 4.1.5 Qualidade do ajuste à curva da patente

### 80

Antes: A Figura 2 sobrepõe o torque calculado com os parâmetros congelados aos 29 pontos extraídos, e a Tabela 7 reúne os indicadores do ajuste. 

Depois: A Figura 8 sobrepõe o torque calculado com os parâmetros congelados aos 29 pontos extraídos, e a Tabela 8 reúne os indicadores do ajuste. 

### 81

Antes: Figura 2 — Torque do cabo calculado (−τ) e pontos extraídos da patente, com os resíduos no painel inferior (K = 174,68; h = 22,701 mm; Xpose = 37,383 mm) 

Depois: Figura 8 — Torque do cabo calculado (−τ) e pontos extraídos da patente, com os resíduos no painel inferior (K = 174,68; h = 22,701 mm; Xpose = 37,383 mm) 

### 82

Antes: Tabela 7 — Indicadores de qualidade do ajuste à curva da patente

Depois: Tabela 8 — Indicadores de qualidade do ajuste à curva da patente

### 83

Antes: Os resíduos não se distribuem aleatoriamente (Tabela 8). Ordenados por θ*, eles formam três zonas extensas de sinal alternado, que reúnem 25 dos 29 pontos, seguidas de quatro pontos próximos ao ponto morto.

Depois: Os resíduos não se distribuem aleatoriamente (Tabela 9). Ordenados por θ*, eles formam três zonas extensas de sinal alternado, que reúnem 25 dos 29 pontos, seguidas de quatro pontos próximos ao ponto morto.

### 84

Antes: Tabela 8 — Zonas de sinal dos resíduos (modelo − extraído), em ordem de θ*

Depois: Tabela 9 — Zonas de sinal dos resíduos (modelo − extraído), em ordem de θ*

### 85

Antes: O último ponto, em θ* = 193,017°, está além do ponto morto calculado (θ*pm = 192,532°). Ali o modelo prevê torque de −1,709 u.p., com sinal invertido, ao passo que a curva extraída registra 0,443 u.p. A diferença, que responde pelo resíduo da zona 6, é coerente com a ausência, no modelo, da protuberância que mantém o torque residual aproximadamente nulo no dispositivo real (seção 4.9).

Depois: O último ponto, em θ* = 193,017°, está além do ponto morto calculado (θ*pm = 192,532°). Ali o modelo prevê torque de −1,709 u.p., com sinal invertido, ao passo que a curva extraída registra 0,443 u.p. A diferença, que responde pelo resíduo da zona 6, é coerente com a ausência, no modelo, da protuberância que mantém o torque residual aproximadamente nulo no dispositivo real (seção 4.1.9).

### 86

Antes: 4.6 Comportamento da mola e do mecanismo

Depois: 4.1.6 Comportamento da mola e do mecanismo

### 87

Antes: A Tabela 9 caracteriza o funcionamento do mecanismo na faixa de operação, de θ* = 42,917° a 193,017°, que corresponde a 150,1° de elevação anatômica, de 30° a 180,1°. As grandezas foram calculadas em malha de 0,001° com os parâmetros congelados.

Depois: A Tabela 10 caracteriza o funcionamento do mecanismo na faixa de operação, de θ* = 42,917° a 193,017°, que corresponde a 150,1° de elevação anatômica, de 30° a 180,1°. As grandezas foram calculadas em malha de 0,001° com os parâmetros congelados.

### 88

Antes: Tabela 9 — Grandezas do mecanismo na faixa de operação

Depois: Tabela 10 — Grandezas do mecanismo na faixa de operação

### 89

Antes: A extensão da mola permanece positiva em toda a faixa, o que assegura a condição é que o cabo continua tracionado em todos os pontos avaliados. O máximo da extensão ocorre no ponto morto, como exige a Equação (17): onde m se anula, dℓ/dθ* também se anula, e o caminho do cabo passa por um extremo. O comprimento máximo da mola, 108,446 mm, é inferior ao comprimento útil do alojamento, 131,37 mm (valor a confirmar), com margem de 22,9 mm. A razão de 1,0095 entre a extensão máxima e o comprimento livre significa que a mola precisaria ser estendida a aproximadamente o dobro de seu comprimento livre; a viabilidade desse requisito depende da deflexão admissível da mola a especificar e deve ser confrontada com dados de fabricante.

Depois: A extensão da mola permanece positiva em toda a faixa, o que assegura que o cabo continua tracionado em todos os pontos avaliados. O máximo da extensão ocorre no ponto morto, como exige a Equação (17): onde m se anula, dℓ/dθ* também se anula, e o caminho do cabo passa por um extremo. A razão de 1,0095 entre a extensão máxima e o comprimento livre significa que a mola precisaria ser estendida a aproximadamente o dobro de seu comprimento livre; a viabilidade desse requisito depende da deflexão admissível da mola a especificar e deve ser confrontada com dados de fabricante.

### 90

Antes: O braço de momento confirma a distinção da seção 3.5. A linha de ação do cabo passa pela ancoragem A, de modo que m não pode exceder |OA| = 22,919 mm em configuração alguma. Ao longo da faixa, m cresce monotonicamente de 12,451 mm em θ* = 42,917° até tocar esse teto em θ* = 97,894°, posição em que o cabo fica perpendicular a OA, e decresce a partir daí, anulando-se no ponto morto; o valor de −0,180 mm no extremo da faixa corresponde ao trecho além desse ponto.

Depois: O braço de momento confirma a distinção da seção 3.1.5. A linha de ação do cabo passa pela ancoragem A, de modo que m não pode exceder |OA| = 22,919 mm em configuração alguma. Ao longo da faixa, m cresce monotonicamente de 12,451 mm em θ* = 42,917° até tocar esse teto em θ* = 97,894°, posição em que o cabo fica perpendicular a OA, e decresce a partir daí, anulando-se no ponto morto; o valor de −0,180 mm no extremo da faixa corresponde ao trecho além desse ponto.

### 91

Antes: A força máxima K δmáx vale 9.516,5 na unidade de K multiplicada por milímetro. Se a ordenada da patente estivesse em N·m, K estaria em N/mm, a tração no cabo chegaria a 9,5 kN e o pico do torque do cabo, 147,07 N·m, seria 13,2 vezes o pico do torque gravitacional do conjunto, de 11,1619 N·m (seção 4.8). Para equilibrar esse pico gravitacional com o maior braço disponível, 22,919 mm, bastaria uma tração de cerca de 487 N. A leitura da ordenada em N·m conduz, portanto, a valores implausíveis para um dispositivo vestível de apoio ao braço, o que reforça o tratamento da curva publicada como qualitativa quanto à magnitude: o modelo reproduz a forma do torque, mas não sua escala física.

Depois: A força máxima K δmáx vale 9.516,5 na unidade de K multiplicada por milímetro. Se a ordenada da patente estivesse em N·m, K estaria em N/mm, a tração no cabo chegaria a 9,5 kN e o pico do torque do cabo, 147,07 N·m, seria 13,2 vezes o pico do torque gravitacional do conjunto, de 11,1619 N·m (seção 4.1.8). Para equilibrar esse pico gravitacional com o maior braço disponível, 22,919 mm, bastaria uma tração de cerca de 487 N. A leitura da ordenada em N·m conduz, portanto, a valores implausíveis para um dispositivo vestível de apoio ao braço, o que reforça o tratamento da curva publicada como qualitativa quanto à magnitude: o modelo reproduz a forma do torque, mas não sua escala física.

### 92

Antes: 4.7 Varredura paramétrica de h com K congelado

Depois: 4.1.7 Varredura paramétrica de h com K congelado

### 93

Antes: A Figura 3 mostra a família de curvas de torque para sete valores de h, com K congelado em 174,68 e a extensão na pose fixada em Xpose.

Depois: A Figura 9 mostra a família de curvas de torque para sete valores de h, com K congelado em 174,68 e a extensão na pose fixada em Xpose.

### 94

Antes: Figura 3 — Família de curvas de torque do cabo para h de 16 a 32,886 mm, com K = 174,68 e Xpose = 37,383 mm congelados, e os 29 pontos extraídos da patente

Depois: Figura 9 — Família de curvas de torque do cabo para h de 16 a 32,886 mm, com K = 174,68 e Xpose = 37,383 mm congelados, e os 29 pontos extraídos da patente

### 95

Antes: A Figura 4 apresenta o RMSE em função de h.

Depois: A Figura 10 apresenta o RMSE em função de h.

### 96

Antes: Figura 4 — RMSE contra os pontos extraídos em função de h, com K congelado: faixa completa, em escala logarítmica, com os valores fisicamente viáveis, e ampliação em torno do mínimo, com os platôs de RMSE

Depois: Figura 10 — RMSE contra os pontos extraídos em função de h, com K congelado: faixa completa, em escala logarítmica, com os valores fisicamente viáveis, e ampliação em torno do mínimo, com os platôs de RMSE

### 97

Antes: O menor RMSE, 1,8270 u.p. (R2 = 0,99840), ocorre em h = 22,735 mm, a 0,034 mm de HCAL, que ocupa a 14ª posição entre os 10.403 valores, com RMSE 0,19% maior. Os platôs constam da Tabela 10. O RMSE ultrapassa 2 vezes o mínimo em h = 21,825 e 23,640 mm e 10 vezes o mínimo em h = 17,570 e 27,900 mm.

Depois: O menor RMSE, 1,8270 u.p. (R2 = 0,99840), ocorre em h = 22,735 mm, a 0,034 mm de HCAL, que ocupa a 14ª posição entre os 10.402 valores, com RMSE 0,19% maior. Os platôs constam da Tabela 11. O RMSE ultrapassa 2 vezes o mínimo em h = 21,825 e 23,640 mm e 10 vezes o mínimo em h = 17,570 e 27,900 mm.

### 98

Antes: Tabela 10 — Platôs de RMSE com K congelado

Depois: Tabela 11 — Platôs de RMSE com K congelado

### 99

Antes: A validade física independe da curva extraída. O critério de fechamento foi atendido em todos os 10.403 valores de h, e o de trabalho virtual também, com resíduo máximo de 7,4 × 10−8 mm/rad na grade inteira. O critério decisivo é a tração: com Xpose congelada, o aumento de h aumenta o curso do cabo — de 28,942 mm em h = 15 mm para 42,435 mm em h = 22,701 mm e 106,573 mm em h = 60 mm — e rebaixa a extensão mínima, que ocorre sempre em θ* = 42,917°, onde a demanda gravitacional é mínima, de apenas 1,2% do pico. A extensão mínima se anula na fronteira de tração, h = 32,886 mm. Os valores viáveis formam o intervalo contíguo de 8,000 mm, borda inferior da grade, a 32,885 mm, com 4.979 valores. O valor documental HCAD = 34,785 mm fica fora desse intervalo: com Xpose congelada, o cabo afrouxaria no início da faixa, com extensão mínima de −2,257 mm, e o RMSE seria de 43,48 u.p. (R2 = 0,093). A Tabela 11 reúne os valores notáveis de h.

Depois: Os critérios de validade física não usam os pontos extraídos, embora o de tração dependa da extensão na pose, identificada contra eles. O critério de fechamento foi atendido em todos os 10.402 valores de h, e o de trabalho virtual também, com resíduo máximo de 7,4 × 10−8 mm/rad na grade inteira. O critério decisivo é a tração: com Xpose congelada, o aumento de h aumenta o curso do cabo — de 28,942 mm em h = 15 mm para 42,435 mm em h = 22,701 mm e 106,573 mm em h = 60 mm — e rebaixa a extensão mínima, que ocorre sempre em θ* = 42,917°, onde a demanda gravitacional é mínima, de apenas 1,2% do pico. A extensão mínima se anula na fronteira de tração, h = 32,886 mm. Os valores viáveis formam o intervalo contíguo de 8,000 mm, borda inferior da grade, a 32,885 mm, com 4.979 valores. A cota do CAD, HCAD = 34,785 mm fica fora desse intervalo: com Xpose congelada, o cabo afrouxaria no início da faixa, com extensão mínima de −2,257 mm, e o RMSE seria de 43,48 u.p. (R2 = 0,093). A Tabela 12 reúne os valores notáveis de h.

### 100

Antes: Tabela 11 — Valores notáveis de h na varredura com K congelado

Depois: Tabela 12 — Valores notáveis de h na varredura com K congelado

### 101

Antes: h (mm)PapelRMSE (u.p.)δmín (mm)δmáx (mm)Llivre + δmáx (mm)θ*pm (°)Tração21,372Ponto morto entra na faixa5,10213,60853,719107,686193,017Atende22,701HCAL, adotado1,83012,04454,479108,446192,532Atende22,735Menor RMSE1,82712,00454,499108,466192,520Atende32,886Fronteira de tração36,4900,00060,175114,142190,099Limite34,785HCAD, documental43,480−2,25761,209115,176189,802Não atende

Depois: h (mm)PapelRMSE (u.p.)δmín (mm)δmáx (mm)Llivre + δmáx (mm)θ*pm (°)Tração21,372Ponto morto entra na faixa5,10213,60853,719107,686193,017Atende22,701HCAL, adotado1,83012,04454,479108,446192,532Atende22,735Menor RMSE1,82712,00454,499108,466192,520Atende32,886Fronteira de tração36,4900,00060,175114,142190,099Limite34,785HCAD, medida em CAD43,480−2,25761,209115,176189,802Não atende

### 102

Antes: Em síntese, a varredura separa duas perguntas. A geometria, independentemente da curva extraída, admite h ≤ 32,886 mm e exclui o valor documental; a curva extraída, com K e Xpose congelados, favorece um intervalo estreito em torno de HCAL, que atende aos três critérios com folga. A diferença de 12,084 mm entre HCAL e HCAD permanece sem explicação e indica que a cota de ancoragem do CAD, a extensão Xpose identificada ou ambas precisam ser conferidas.

Depois: Em síntese, a varredura separa duas perguntas. A geometria, com a extensão na pose identificada, admite h ≤ 32,886 mm e exclui a cota do CAD; a curva extraída, com K e Xpose congelados, favorece um intervalo estreito em torno de HCAL, que atende aos três critérios com folga. A diferença de 12,084 mm entre HCAL e HCAD permanece sem explicação e indica que a cota de ancoragem do CAD, a extensão Xpose identificada ou ambas precisam ser conferidas.

### 103

Antes: 4.8 Confronto entre o torque do cabo e o torque gravitacional

Depois: 4.1.8 Confronto entre o torque do cabo e o torque gravitacional

### 104

Antes: O torque gravitacional do conjunto, calculado pela Equação (24) de forma independente da cadeia do cabo, atinge o máximo de 11,1619 N·m na elevação de 89,44°, o que corrobora a previsão da seção 2.1, de momento gravitacional máximo com o segmento perpendicular à gravidade. O desvio de 0,56° em relação a 90° indica que a linha que une o pivô ao centro de massa do conjunto forma esse ângulo com a direção do braço adotada na convenção da patente. O valor do pico coincide com M g d da Tabela 3. O módulo da Equação (24) oculta a troca de sentido do torque em θ* = 43,579° (elevação de 179,44°), que afeta apenas os 0,66° iniciais da faixa, com torque inferior a 0,13 N·m.

Depois: O torque gravitacional do conjunto, calculado pela Equação (24) de forma independente da cadeia do cabo, atinge o máximo de 11,1619 N·m na elevação de 89,44°, o que corrobora a previsão da seção 2.1, de momento gravitacional máximo com o segmento perpendicular à gravidade. O desvio de 0,56° em relação a 90° indica que a linha que une o pivô ao centro de massa do conjunto forma esse ângulo com a direção do braço adotada na convenção da patente. O valor do pico coincide com M g d da Tabela 4. O módulo da Equação (24) oculta a troca de sentido do torque em θ* = 43,579° (elevação de 179,44°), que afeta apenas os 0,66° iniciais da faixa, com torque inferior a 0,13 N·m.

### 105

Antes: A comparação entre as duas curvas exige cautela metodológica. Como a ordenada da curva publicada não tem unidade declarada e a seção 4.6 mostrou que sua leitura em N·m é implausível, as magnitudes não são comparáveis. O que se pode confrontar é a forma dos perfis, apresentados na Figura 5 normalizados pelos respectivos valores de pico, em função da elevação anatômica. Como a normalização elimina a escala, o confronto não informa que fração do torque gravitacional o mecanismo compensa.

Depois: A comparação entre as duas curvas exige cautela metodológica. Como a ordenada da curva publicada não tem unidade declarada e a seção 4.1.6 mostrou que sua leitura em N·m é implausível, as magnitudes não são comparáveis. O que se pode confrontar é a forma dos perfis, apresentados na Figura 11 normalizados pelos respectivos valores de pico, em função da elevação anatômica. Como a normalização elimina a escala, o confronto não informa que fração do torque gravitacional o mecanismo compensa.

### 106

Antes: Figura 5 — Torque do cabo e torque gravitacional normalizados pelos respectivos picos, em função da elevação anatômica (K = 174,68; h = 22,701 mm; Xpose = 37,383 mm)

Depois: Figura 11 — Torque do cabo e torque gravitacional normalizados pelos respectivos picos, em função da elevação anatômica (K = 174,68; h = 22,701 mm; Xpose = 37,383 mm)

### 107

Antes: Nota: a linha pontilhada marca o cruzamento das curvas normalizadas.

Depois: Nota: a linha pontilhada marca o cruzamento das curvas normalizadas. O torque gravitacional está em módulo; o do cabo, com sinal (−τ), fica negativo além do ponto morto.

### 108

Antes: Três características emergem do confronto. O pico do torque do cabo ocorre na elevação de 97,48°, e o do torque gravitacional, em 89,44°, com defasagem de 8,05°. O mecanismo entrega sua assistência máxima acima da posição de maior demanda gravitacional, configuração compatível com dispositivo projetado para trabalho acima da cabeça.

Depois: Três características emergem do confronto. O pico do torque do cabo ocorre na elevação de 97,484°, e o do torque gravitacional, em 89,438°, com defasagem de 8,046°. O mecanismo entrega sua assistência máxima acima da posição de maior demanda gravitacional, configuração compatível com dispositivo projetado para trabalho acima da cabeça.

### 109

Antes: Abaixo de 94°, as diferenças tornam-se negativas e crescentes em módulo, até −0,520 na elevação de 30°. No ponto morto, na elevação de 30,485°, o torque gravitacional ainda vale 5,757 N·m, 51,6% de seu pico, enquanto o torque do cabo se anula; em 30°, o torque gravitacional é de 5,675 N·m, 50,8% do pico. Trata-se de característica da arquitetura, e não de deficiência do ajuste: conforme a seção 2.3, a patente prevê que o dispositivo libere o braço nas posturas de não trabalho, em que o usuário precisa de mobilidade para alcançar ferramentas ou repousar o membro.

Depois: Abaixo de 94°, as diferenças tornam-se negativas e crescentes em módulo, até −0,520 na elevação de 30°. No ponto morto, na elevação de 30,485°, o torque gravitacional ainda vale 5,757 N·m, 51,6% de seu pico, enquanto o torque do cabo se anula; em 30°, o torque gravitacional é de 5,675 N·m, 50,8% do pico. Trata-se de característica da arquitetura, e não de deficiência do ajuste: conforme a seção 2.3, abaixo do ângulo de transição o torque cai a um valor residual e o braço recupera a liberdade de movimento.

### 110

Antes: 4.9 Limitações dos resultados

Depois: 4.1.9 Limitações dos resultados

### 111

Antes: Além das limitações de escopo da seção 3.13, os resultados comportam as ressalvas a seguir.

Depois: Além das limitações de escopo da seção 3.1.14, os resultados comportam as ressalvas a seguir.

### 112

Antes: A identificação foi reproduzida apenas em parte. K e Xpose foram reproduzidos no h adotado, mas a origem de θoff e de HCAL não pôde ser reconstituída, e os quatro parâmetros foram identificados e avaliados contra os mesmos 29 pontos, cuja incerteza de extração não está documentada. O valor documental HCAD é incompatível com os demais parâmetros congelados, pois viola o critério de tração.

Depois: A identificação foi reproduzida apenas em parte. K e Xpose foram reproduzidos no h adotado, mas a origem de θoff e de HCAL não pôde ser reconstituída, e os quatro parâmetros foram identificados e avaliados contra os mesmos 29 pontos, cuja incerteza de extração não está documentada. A cota do CAD, HCAD é incompatível com os demais parâmetros congelados, pois viola o critério de tração.

### 113

Antes: O fator de escala de 0,870, fixado pela comparação entre o comprimento do elo distal e o comprimento de segmento do indivíduo de referência, propaga-se a todas as grandezas dimensionais e de massa, e duas cotas do modelo em CAD permanecem a confirmar. Alterações nessas grandezas exigem a reexecução integral da identificação.

Depois: O fator de escala propaga-se a todas as grandezas dimensionais e de massa, e o modelo em CAD confirma o comprimento da mola na pose, 91,35 mm; o comprimento útil do alojamento, que não entra na cadeia de cálculo, é de 140,0 mm no CAD. Alterações nessas grandezas exigem a reexecução integral da identificação.

### 114

Antes: Por fim, os resultados referem-se a um único dispositivo, ao indivíduo de referência adotado e ao membro superior estendido sem ferramenta na mão, e limitam-se à análise estática. A generalização a outros percentis antropométricos, a outras configurações de cotovelo e à presença de carga na mão demanda a reexecução do procedimento com os parâmetros correspondentes.

Depois: Por fim, os resultados desta seção referem-se a um único dispositivo, ao indivíduo de referência adotado e ao membro superior estendido sem ferramenta na mão, e limitam-se à análise estática. A generalização a outros percentis antropométricos, a outras configurações de cotovelo e à presença de carga na mão demanda a reexecução do procedimento com os parâmetros correspondentes.

### 115

Antes: Este trabalho reconstruiu, a partir da documentação de patente, o gerador de torque de mola da US 9.889.554 B2 e formulou um modelo estático do torque que ele entrega em função do ângulo. A cinemática foi resolvida em forma fechada a partir da equação de fechamento do circuito vetorial, e cada etapa da cadeia de cálculo foi conferida por verificações independentes, com resíduos da ordem de 10−13 mm nas relações geométricas.

Depois: Este trabalho reconstruiu, a partir da documentação de patente, o gerador de torque de mola da US 9.889.554 B2 e formulou um modelo estático do torque que ele entrega em função do ângulo. A cinemática foi resolvida em forma fechada a partir da equação de fechamento do circuito vetorial, e cada etapa da cadeia de cálculo foi conferida por verificações internas de consistência, com resíduos da ordem de 10−13 mm nas relações geométricas.

### 116

Antes: O princípio dos trabalhos virtuais mostrou-se o critério decisivo na formulação. Ele revelou que a extensão da mola deve acompanhar o caminho completo do cabo, ℓ = s − Rψ, e não apenas o vão livre, que violava a conservação de energia com resíduo de 1,71 mm. A mesma verificação distinguiu o braço de momento perpendicular, limitado a 22,919 mm, da distância do pivô ao ponto de tangência, próxima de 283 mm, cuja confusão superestimaria o torque por um fator superior a 12.

Depois: O princípio dos trabalhos virtuais mostrou-se o critério decisivo na formulação. Ele revelou que a extensão da mola deve acompanhar o caminho completo do cabo, ℓ = s − Rψ, e não apenas o vão livre, que violava a conservação de energia com resíduo de 1,71 mm/rad. A mesma verificação distinguiu o braço de momento perpendicular, limitado a 22,919 mm, da distância do pivô ao ponto de tangência, próxima de 283 mm, cuja confusão superestimaria o torque por um fator superior a 12.

### 117

Antes: Com os parâmetros congelados, o modelo reproduz a forma da curva publicada com coeficiente de determinação de 0,99839 e RMSE de 1,83 u.p., equivalente a 1,24% do maior valor extraído. Os resíduos, contudo, organizam-se em zonas de sinal alternado, o que indica diferença sistemática de forma, e a formulação anterior, fisicamente inconsistente, ajustava melhor a curva. A adoção da formulação consistente, apesar do RMSE maior, reflete o critério de que a escolha entre modelos se faz por validade física, e não pelo indicador de erro.

Depois: Com os parâmetros congelados, dois deles de origem não reproduzida, o modelo reproduz a forma da curva publicada, nos mesmos 29 pontos usados para fixá-los, com coeficiente de determinação de 0,99839 e RMSE de 1,83 u.p., equivalente a 1,24% do maior valor extraído. Os resíduos, contudo, organizam-se em zonas de sinal alternado, o que indica diferença sistemática de forma, e a formulação sem o arco, fisicamente inconsistente, ajusta melhor a curva. A adoção da formulação consistente, apesar do RMSE maior, reflete o critério de que a escolha entre modelos se faz por validade física, e não pelo indicador de erro.

### 118

Antes: A varredura de h com K congelado separou o que a geometria impõe do que a curva extraída sugere. O cabo permanece tracionado em toda a faixa de operação somente para h ≤ 32,886 mm, o que exclui a cota de 34,785 mm lida no CAD. A curva extraída favorece um intervalo de 0,145 mm em torno do valor adotado, mas essa concentração é esperada por construção, porque K e Xpose foram identificados nesse mesmo valor; o critério que levou a h = 22,701 mm não pôde ser reproduzido, e a afirmação anterior de decrescimento monotônico do erro com h foi refutada pela auditoria.

Depois: A varredura de h com K congelado separou o que os critérios físicos impõem do que a curva extraída sugere. Com a extensão na pose identificada, o cabo permanece tracionado em toda a faixa de operação somente para h ≤ 32,886 mm, o que exclui a cota de 34,785 mm medida no CAD. A curva extraída favorece um intervalo de 0,145 mm em torno do valor adotado, mas essa concentração é esperada por construção, porque K e Xpose foram identificados nesse mesmo valor; com K e a extensão na pose livres, o RMSE fica abaixo de 2 vezes o mínimo de h = 19,25 a 31,00 mm, e o critério que levou a h = 22,701 mm não pôde ser reproduzido.

### 119

Antes: No confronto com o torque gravitacional do conjunto braço–exoesqueleto, cujo pico de 11,16 N·m ocorre a 89,4° de elevação, as curvas normalizadas diferem em no máximo 0,027 entre 105° e 150° de elevação. O pico do torque do cabo, a 97,5°, fica 8,05° acima do pico gravitacional, e o ponto morto, a 30,5°, libera o braço nas posturas de não trabalho, à custa de subcompensação abaixo de 94°. O resultado quantifica o compromisso de um mecanismo passivo de torque fixo por ângulo, que favorece o trabalho acima da cabeça.

Depois: No confronto com o torque gravitacional do conjunto braço–exoesqueleto, cujo pico de 11,16 N·m ocorre a 89,4° de elevação, as curvas normalizadas diferem em no máximo 0,027 entre 105° e 150° de elevação. O pico do torque do cabo, a 97,5°, fica cerca de 8° acima do pico gravitacional, e o ponto morto, a 30,5°, libera o braço nas posturas de não trabalho, à custa de subcompensação abaixo de 94°. O resultado quantifica o compromisso de um mecanismo passivo de torque fixo por ângulo, que favorece o trabalho acima da cabeça.

### 120

Antes: O objetivo geral foi atingido em sua parte estática e para um dos três dispositivos previstos. Os objetivos específicos a, b, c e e foram cumpridos; o objetivo d, parcialmente, pois a rigidez e a extensão da mola na pose foram reproduzidas, mas a origem da posição da ancoragem e da calibração angular não. Os objetivos f e g, referentes à equação de movimento e ao acoplamento com o MBDyn, não foram executados. A principal restrição é a ausência de unidade na ordenada da curva da patente: o torque do cabo permanece em unidade da patente, e a leitura em N·m conduz a forças implausíveis, de modo que o modelo determina a forma do torque, mas não sua escala física.

Depois: O objetivo geral foi atingido para este dispositivo na parte estática, e a extensão à dinâmica multicorpos ficou preparada, com o procedimento da seção 3.1.13, mas não foi executada. Os objetivos específicos a, b, c e e foram cumpridos; o objetivo d, parcialmente, pois a rigidez e a extensão da mola na pose foram reproduzidas, mas a origem da posição da ancoragem e da calibração angular não, e o comprimento livre não é identificável, porque a curva depende só da extensão na pose. Os objetivos f e g, referentes à equação de movimento e ao acoplamento com o MBDyn, não foram executados. A principal restrição é a ausência de unidade na ordenada da curva da patente: o torque do cabo permanece em unidade da patente, e a leitura em N·m conduz a forças implausíveis, de modo que o modelo determina a forma do torque, mas não sua escala física.

### 121

Antes: Como continuidade, recomenda-se obter um dado independente que fixe a escala do torque, como a especificação de uma mola comercial compatível; conferir no CAD a cota de ancoragem, o comprimento do alojamento e o comprimento da mola na pose; documentar o procedimento de extração dos pontos e sua incerteza; representar a protuberância responsável pela zona neutra; e, com o torque em unidade física, executar as etapas dinâmicas pela formulação de Lagrange e no MBDyn e estender o procedimento à US 9.737.374 B2 e à EP 3 504 033 B1.

Depois: Como continuidade, recomenda-se obter um dado independente que fixe a escala do torque, como a especificação de uma mola comercial compatível; conferir no CAD a cota de ancoragem, o comprimento do alojamento e o comprimento da mola na pose; documentar o procedimento de extração dos pontos e sua incerteza; representar a protuberância responsável pela zona neutra; e, com o torque em unidade física, executar as etapas dinâmicas pela formulação de Lagrange e no MBDyn.
