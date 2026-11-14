# Roteiro de defesa

TCC "Modelagem de mecanismos passivos de apoio ao braço", versão condensada para a defesa.

As respostas abaixo usam só o que está no texto entregue, e cada uma indica a seção, a tabela ou a figura em que a banca encontra o que você disser. As perguntas marcadas com **[depende de você]** pedem um dado ou uma decisão que o texto não traz; elas estão detalhadas em `Pendencias_e_Perguntas_ao_Autor.md`.

## 1. A mensagem em três frases

1. As patentes dos exoesqueletos passivos de ombro mostram o mecanismo, mas não dão massa, inércia nem rigidez; o trabalho reconstrói três mecanismos de arquitetura diferente e calcula o torque estático que cada um entrega em função do ângulo.
2. O que os modelos determinam com segurança são os ângulos e a forma dos perfis de torque. A magnitude depende de hipótese nos três casos, porque nenhuma patente publica a escala.
3. O princípio dos trabalhos virtuais foi o critério que decidiu a formulação: ele mostrou que a mola do primeiro mecanismo acompanha o caminho completo do cabo, e não só o vão livre.

## 2. Perguntas gerais

### 2.1 Qual problema de engenharia o trabalho resolve?

O auxílio de um exoesqueleto passivo é uma curva de torque em função do ângulo, fixada no projeto pela geometria e pela mola. As patentes dos dispositivos comerciais descrevem o mecanismo, mas não permitem quantificar essa curva. O trabalho reconstrói a geometria e formula modelos estáticos para obter o torque e compará-lo com o torque do peso do braço ou com a curva publicada. (Seções 1 e 2.10.)

### 2.2 Qual é a contribuição original?

- Um procedimento único, aplicado a três arquiteturas: reconstrução em CAD, cinemática de circuito fechado em forma fechada, identificação dos parâmetros não publicados e conferência pelo princípio dos trabalhos virtuais (capítulo 3).
- No exoesqueleto 1, a demonstração de que a extensão da mola deve seguir ℓ = s − Rψ, e a distinção entre o braço de momento m, limitado a 22,919 mm, e a distância b ao ponto de tangência, perto de 283 mm (seções 3.6, 3.9 e 4.1.3).
- No exoesqueleto 2, a identificação do comprimento de referência do elástico pelo espaçamento entre as três curvas da patente, que não depende da escala da ordenada nem da rigidez (seções 3.10 e 4.2.3).
- No exoesqueleto 3, o raio efetivo do came como função suporte da envoltória convexa, diferente do raio cotado, e a leitura das montagens do came pelos furos (seções 3.6, 3.11 e 4.3.7).

### 2.3 Por que essas três patentes?

Porque descrevem três arquiteturas que a seção 2.6 associa a produtos comerciais e que resolvem o mesmo problema de modos diferentes: mola, cabo e polia (US 9.889.554 B2), elástico ligado direto a uma alavanca com elemento de encosto (EP 3 504 033 B1) e mola com came de raio variável (US 9.737.374 B2). A segunda traz três curvas do mesmo atuador, o que permite um teste de identificação que uma curva só não permite. A terceira testa o procedimento num mecanismo em que o came molda o torque.

**Atenção:** a associação entre patente e nome comercial não pôde ser conferida nos documentos. Diga "a patente da Ottobock" e "a patente da Levitate", e não "o Paexo" ou "o Airframe", ao falar dos modelos. **[depende de você]** A seção 2.6 fala em Paexo e a seção 3.1 em iX Shoulder Air.

### 2.4 Por que três formulações diferentes?

Porque o elemento que transmite a força muda. No primeiro, o cabo tangencia um tambor e o ponto de aplicação se move. No segundo, o elástico é reto ou contorna o elemento de encosto, e há dois regimes. No terceiro, a mola age pelo raio efetivo de um came e o cabo de ancoragem pelo seu próprio braço. O capítulo 3 está organizado por etapa, e cada seção trata os três em sequência, o que facilita mostrar o que muda de um para outro. O que é comum: variável independente q, fechamento vetorial com solução fechada e braço de momento igual à derivada do caminho do elemento elástico em relação a q.

### 2.5 O que foi medido, o que foi identificado e o que é hipótese?

| | Medido em CAD ou em figura | Identificado por ajuste | Hipótese ou origem não reproduzida |
|---|---|---|---|
| Exoesqueleto 1 | p, C, R, α, pose, L_pose, H_CAD (Tabela 1) | X_pose = 37,383 mm e K = 174,68, em unidade da patente | θ_off = 133,017° e H_CAL = 22,701 mm, congelados, de origem não reproduzida (Tabela 4) |
| Exoesqueleto 2 | C1, C2, γ, e_c, p, pose (Tabela 7) | s0 = 311,148, 300,750 e 291,956 mm, pelo espaçamento (seção 4.2.3) | K = K40 = 2,54982 N/mm, pela hipótese de 40% do peso em 90° (seção 3.10 e Tabela 11) |
| Exoesqueleto 3 | C1, C2, R, γ, pose (Tabela 12); R20 e giro do came lidos nas figuras | k = 0,492 N/mm e x0 = 323,6 mm, na escala da AWM (Tabela 14) | escala: AWM igualada ao peso do membro de referência; polia 630 no infinito (seções 3.6 e 3.10) |

As grandezas de CAD são classificadas como medidas em CAD, e não como dimensões do produto (abertura do capítulo 3).

### 2.6 Como a consistência física foi demonstrada?

Por verificações executadas a cada cálculo, descritas para os três na seção 3.12. No exoesqueleto 1, os resíduos estão na Tabela 3 (seção 4.1.3): os de fechamento são da ordem do erro de arredondamento, no máximo 8,0 × 10⁻¹³ mm, e o do trabalho virtual é de 4,7 × 10⁻⁸ mm/rad, limitado pela diferença finita. Há ainda testes automatizados no exoesqueleto 1 e o caso limite p = 0 no 2. Os resíduos numéricos dos exoesqueletos 2 e 3 saíram do texto com as seções de verificação que você cortou; se perguntarem, os valores do documento longo eram estes (fechamento até 5,7 × 10⁻¹⁴ mm e trabalho virtual com 5,0 × 10⁻⁸ mm/rad no 2; trabalho virtual com diferença relativa de 1,8 × 10⁻⁵ no 3).

### 2.7 Por que o princípio dos trabalhos virtuais é importante aqui?

Porque ele decide entre formulações que o ajuste à curva não distingue. No exoesqueleto 1, com a mola acompanhando só o vão livre, o resíduo é de 1,7129 mm/rad; com s + Rψ, 3,4258 mm/rad; só com s − Rψ ele cai a 4,7 × 10⁻⁸ mm/rad. A formulação sem o arco ajusta melhor a curva (RMSE de 1,152 contra 1,830 u.p.), mas viola a conservação de energia e foi rejeitada. A regra do trabalho é esta: primeiro a validade física, depois o indicador de erro (seções 3.10, 4.1.3 e 4.1.4).

### 2.8 Quais são os limites das curvas publicadas nas patentes?

- US 9.889.554 B2: uma curva, sem unidade na ordenada (seções 2.9 e 3.6).
- EP 3 504 033 B1: três curvas, sem rótulo nem valores na ordenada; o texto da patente define a ordenada como uma razão que não é coerente com a figura; o documento as chama de representações exemplares e não diz se foram medidas (seção 3.10 e Figura 7).
- US 9.737.374 B2: três curvas (AASM, AWM, RM) sem unidade (seções 3.1 e 3.10).

Em nenhuma se conhece a incerteza da leitura. **[depende de você]** O método de extração dos pontos não está descrito.

### 2.9 Por que não comparar a magnitude dos três?

Porque cada torque está numa escala diferente. O do primeiro está em unidade da patente; lido em N·m, daria tração de 9,5 kN e pico 13,2 vezes o do peso, o que é implausível (seção 4.1.6). O do segundo só chega a N·m pela hipótese K = K40. O do terceiro, pela hipótese de que a AWM seja o peso do membro de referência; a escala do artigo de Okabe, Brittes e Brito (2026) é 2,94 vezes maior (seção 4.3.8). A comparação vale para ângulos e forma (seção 5.4).

### 2.10 Quais resultados não dependem de hipótese de escala?

Os ângulos dos picos, dos pontos mortos e das transições, a forma normalizada dos perfis, os comprimentos de referência s0 e as verificações de fechamento e de trabalho virtual. Dependem de hipótese os valores em N·m. Tudo depende da geometria reconstruída a partir de desenhos sem cotas (último parágrafo da seção 5.4).

### 2.11 E a dinâmica?

A versão entregue trata só do comportamento estático, e o texto não promete análise dinâmica. O título é "Modelagem de mecanismos passivos de apoio ao braço". Se a banca perguntar pela dinâmica, a resposta que o texto sustenta é esta: o trabalho calcula numericamente o torque estático ao longo de toda a faixa de movimento e faz varreduras paramétricas (h, e_c e giro do came); uma análise dinâmica somaria o torque do mecanismo ao do peso e exigiria os dois na mesma unidade física, e nenhuma das três patentes fornece a escala do torque (seções 4.1.9, 4.2.9 e 4.3.9). Por isso a continuidade recomendada em cada conclusão é obter um dado independente que fixe a escala (seções 5.1, 5.2 e 5.3).

**[depende de você]** Os objetivos sobre equação de movimento e simulação multicorpos saíram do texto a seu pedido. Se eles constavam do projeto aprovado, combine com o orientador como responder.

### 2.12 O que seria necessário para validar os modelos experimentalmente?

Um dado independente que fixe a escala: a especificação ou o ensaio da mola no primeiro, a curva de força e extensão do elástico no segundo, e a rigidez, o comprimento livre e o giro do came medidos na peça real no terceiro (seções 5.1, 5.2 e 5.3). Com a escala fixada, a comparação com o torque medido no dispositivo validaria a magnitude.

### 2.13 Os resultados valem para outras pessoas e outros usos?

Valem para o indivíduo de referência de de Leva (1996), de 73,0 kg e 1,741 m, com o cotovelo estendido e sem ferramenta na mão (abertura do capítulo 3 e último parágrafo da seção 5.4). Outro percentil, outro ângulo de cotovelo ou carga na mão pedem a reexecução do procedimento. A curva do mecanismo não muda com a pessoa; o que muda é o torque do peso com que ela é comparada.

## 3. Perguntas específicas prováveis

### Exoesqueleto 1

**De onde vêm θ_off = 133,017° e H_CAL = 22,701 mm?** **[depende de você]** O texto diz que o procedimento não foi registrado (seção 3.10). O que você pode sustentar com o texto: K e X_pose foram reproduzidos no h adotado; H_CAL foi mantido porque o par (K, X_pose) foi identificado nele e porque o ponto morto fica a 0,485° do início da zona neutra da patente (seção 4.1.4).

**Um R² de 0,99839 não é bom demais?** O texto já responde: os quatro parâmetros foram identificados contra os mesmos 29 pontos usados na avaliação, então a aderência não é validação independente. Além disso, os resíduos formam três zonas de sinal alternado, o que indica diferença sistemática de forma (seção 4.1.5 e Figura 8).

**Por que a cota do CAD (34,785 mm) não foi usada para h?** Com X_pose congelado, ela afrouxa o cabo no início da faixa (extensão mínima de −2,257 mm) e dá RMSE de 43,48 u.p. (seção 4.1.7). A diferença entre H_CAD e H_CAL fica sem explicação no texto: não afirme qual dos dois corresponde ao dispositivo.

**A curva determina h?** Com K e X_pose congelados, sim, dentro de 0,145 mm, mas isso é esperado por construção. Com K e X_pose livres, o RMSE fica abaixo de 2 vezes o mínimo de h = 19,25 a 31,00 mm: a curva sozinha não determina h (seções 4.1.7 e 5.1).

**O que é "u.p."?** Unidade da patente: a unidade da ordenada da curva publicada, que o documento não declara. K só estaria em N/mm se u.p. correspondesse a N·m (seção 3.6 e nota da Tabela 4).

**Por que o pico do mecanismo fica 8° acima do pico do peso?** O pico do cabo ocorre a 97,5° de elevação e o do peso a 89,4°. O mecanismo entrega a assistência máxima acima da posição de maior demanda, à custa de subcompensação abaixo de 94° (seção 4.1.8 e Figura 11).

**O modelo representa a zona neutra?** Não. A protuberância que limita o gerador de força não está no modelo; por isso o torque calculado troca de sinal depois do ponto morto, nos 0,485° finais da faixa (seções 3.7 e 4.1.9).

### Exoesqueleto 2

**Por que o modelo não reproduz as curvas da patente?** Com os s0 identificados e escala comum, o R² fica entre −1,529 e −0,417. O texto delimita a causa: o comprimento s implícito na figura concorda com o do CAD (0,84 mm RMS), então a diferença não vem de s nem, como causa principal, do braço de momento. Sobram o torque do peso usado pela patente e a definição da ordenada, que a patente não permite separar (seção 4.2.4 e Figura 12).

**Se a forma não reproduz, por que confiar no s0?** Porque a identificação pelo espaçamento usa só s(θ_el) e elimina o fator comum às três curvas. Ela é conferida de três modos: as três estimativas do fator G coincidem (dispersão mediana de 0,84%), o fim da curva pontilhada dá s0 a 1,40 mm do identificado, e um teste sintético confere a implementação (seções 3.10 e 4.2.3).

**De onde vem o alvo de 40%?** De uma alegação comercial (SUITX, [202-]) que não consta da patente e não foi verificada. É hipótese de projeto, e o texto diz que os valores em N·m descrevem um cenário, e não o dispositivo (seções 3.10 e 4.2.8).

**Por que a curva tracejada?** É a de pré-tensão intermediária. O texto mostra o efeito de adotar as outras duas: K40 vai a 3,20932 e 2,17230 N/mm e o pico a 4,516 N·m em 75,5° e 4,317 N·m em 81,7° (seção 4.2.8).

**O modelo tem torque com o braço baixado e a patente não. Por quê?** No CAD, o elemento de encosto está a 7,754 mm do eixo; a patente o prefere sobre o eixo. Com ele sobre o eixo, o contato calculado ocorre em 13,35°, a 0,93° do início médio das curvas. A divergência foi mantida e declarada (seções 3.7 e 4.2.8).

**e_c = 34,785 mm é o mesmo valor de H_CAD do exoesqueleto 1. Coincidência?** Sim. São medidas de dois modelos em CAD distintos; e_c foi conferido no CAD do segundo dispositivo (nota da Tabela 7). Tenha essa resposta pronta, porque os dois números aparecem nas Tabelas 1 e 7.

### Exoesqueleto 3

**Por que igualar a AWM ao peso do membro de referência?** Porque a figura não tem unidade e a AWM é, segundo a patente, o momento do peso do braço: um cosseno puro, −78,22 cos Θ. Igualar sua amplitude ao torque do peso do membro na horizontal (10,55 N·m) dá 0,1349 N·m por unidade. É hipótese declarada; na escala do artigo de Okabe, Brittes e Brito (2026), a mesma AWM corresponderia a 2,9 vezes o peso do membro (seções 3.10, 4.3.2 e 4.3.8).

**Por que o came girado de −49° ajusta melhor?** O ajuste da mola (R² de 0,901 para 0,953) e as marcas das zonas da patente, que não entram no ajuste, apontam o mesmo giro. A montagem dois furos no sentido horário (−50,62°) fica a 1,6° dele. O texto conclui que a curva da patente é compatível com essa montagem, e não que ela foi a usada: a patente não diz em que furo o came estava (seção 4.3.7, Figura 19 e Tabela 16).

**Os furos da polia existem?** O texto admite, por hipótese, que a polia externa tem furos correspondentes aos cinco do came vistos nas Figuras 14C e 14D da patente (seção 3.11). Não afirme mais que isso.

**Por que o raio efetivo e não o raio cotado?** O cabo tracionado passa reto sobre as concavidades do canal. Usar o raio do ponto de saída superestimaria o momento da mola em até 12% na Z11 e em até 49% na Z12 (seções 3.6 e 4.3.2 e Figura 6).

**O braço só sobe até Θ = 22° no modelo, e a curva vai a 30°.** Com a ancoragem na posição do CAD, o vão do cabo se anula em 22,0°. O texto registra a diferença (seções 3.7 e 5.3).

### Comparação

**Por que os três torques do peso são diferentes (11,16, 10,617 e 11,45 N·m)?** O membro humano é o mesmo (10,55 N·m na horizontal). O que muda são as peças do exoesqueleto somadas a ele em cada modelo (Tabelas 2, 8 e 13).

**Qual dos três compensa melhor o peso?** O trabalho não responde em magnitude. Em forma: o primeiro acompanha o peso entre 105° e 150°; o segundo, com a geometria do CAD, fica abaixo do peso entre 84° e 177°; no terceiro, o máximo da curva da patente quase coincide com o do peso (seções 4.1.8, 4.2.8, 4.3.8 e 5.4). No segundo, a comparação vale para o modelo, e não para o produto.

## 4. Pontos de atenção na apresentação

- **Não diga "validado".** O texto usa "reproduz a forma" e "verificado". Validação exigiria medida independente.
- **Não cite torque do exoesqueleto 1 em N·m.** Ele está em unidade da patente.
- **Diga cedo o que não foi feito:** ensaio com protótipo, medida independente de escala, análise dinâmica. A banca reage melhor a uma limitação declarada do que a uma descoberta.
- **Tenha de cabeça:** 29 pontos e R² = 0,99839 (exo 1); 97,5° contra 89,4°; s0 = 300,750 mm e K40 = 2,54982 N/mm (exo 2); 4,379 N·m em 79,1°; R² de 0,901 e 0,953 e k = 0,492 N/mm (exo 3); resíduo de 1,7129 mm/rad sem o arco.
- **Três ressalvas que a banca vai procurar:** origem de θ_off e H_CAL; forma do exoesqueleto 2 não reproduzida; escala por hipótese nos três.
- **O que saiu do texto e você pode citar de memória, se perguntarem:** a tabela com os 29 pontos extraídos, a tabela com os pontos das três curvas da EP 3 504 033 B1, o detalhe das análises de robustez do s0 (a figura do ajuste de forma voltou, como Figura 13), as tabelas de platôs de RMSE e de valores notáveis de h, a tabela de grandezas do circuito do exoesqueleto 2 por ângulo e os resíduos das verificações dos exoesqueletos 2 e 3. Os números estão nos arquivos `results/*.json` do repositório.
- **[depende de você]** Se perguntarem sobre uso de ferramentas de IA, responda com o que de fato ocorreu. O texto não trata do assunto.

## 5. Perguntas que exigem dados ou decisões que o texto não tem

| Pergunta | O que falta |
|---|---|
| Como θ_off e H_CAL foram obtidos? | O procedimento e a restrição usada para h |
| Como os pontos foram extraídos das figuras? | Ferramenta, imagem e resolução |
| Qual medida fixou a escala do CAD? | A medida antropométrica (exo 1) e o critério do exo 2 |
| O CAD do exo 2 é de qual produto? | A relação entre Paexo e iX Shoulder Air |
| Por que não há análise dinâmica? | Combinar a resposta com o orientador, se os objetivos de dinâmica constavam do projeto |
| Qual norma a monografia segue? | Confirmação da coordenação do curso |
