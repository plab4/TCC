# Pendências e perguntas ao autor

Versão para a defesa do TCC "Modelagem de mecanismos passivos de apoio ao braço", com 80 páginas.

Este arquivo reúne o que depende de você: decisões, dados que só você tem e confirmações. Nada do que está aqui foi resolvido em silêncio no documento. As perguntas estão em ordem de prioridade. As da parte A mudam o texto final; as demais servem para você chegar à banca com a resposta pronta.

## A. Decisões que mudam o documento

### A1. Retirada da etapa dinâmica e dos objetivos correspondentes

- **O que foi feito, a seu pedido:** saiu tudo o que mencionava a etapa dinâmica e o MBDyn. Na prática: os objetivos específicos sobre a equação de movimento e sobre o acoplamento multicorpos (eram f e g), a seção de fundamentação sobre modelagem dinâmica multicorpos, as três seções de etapas dinâmicas previstas, a equação de movimento, as frases correspondentes das conclusões e a última frase do resumo e do abstract. Os objetivos seguintes mudaram de letra: os do exoesqueleto 2 são agora f e g, e os do exoesqueleto 3, h e i.
- **Título:** por decisão sua, passou a "Modelagem de mecanismos passivos de apoio ao braço", na capa e na folha de rosto. Os arquivos entregues foram renomeados para acompanhar o título.
- **Por que importa:** se o projeto aprovado previa os objetivos de dinâmica, ou se o título antigo está registrado na coordenação, a banca ou a secretaria podem perguntar.
- **Pergunta:** o orientador está de acordo com a retirada dos dois objetivos e com o título novo? É preciso atualizar o título em algum registro do curso?
- **Situação no documento:** texto só estático, sem menção à dinâmica. O roteiro de defesa traz a resposta que o texto sustenta (pergunta 2.11).

### A2. Estrutura nova e o que veio do seu arquivo

- **Capítulo 3 fundido por tópico, como você escolheu:** são 11 seções, uma por etapa do procedimento (reconstrução em CAD, parâmetros inerciais, convenções, fechamento do circuito e braço de momento, elemento elástico e torque, ponto morto, torque gravitacional, trabalhos virtuais, dados da patente e identificação, varredura paramétrica, verificações e delimitação). Cada seção trata os três exoesqueletos, nessa ordem; na 3.4, que junta fechamento e braço de momento, cada exoesqueleto aparece completo antes do seguinte. Cada trecho começa por "No exoesqueleto 1, ...", "No exoesqueleto 2, ..." e assim por diante. A definição do trabalho virtual, δW = 0, está nas três formulações (seção 3.8), e a variável independente é q nas três.
- **Capítulo 4 fundido por assunto (pedido de 14/11):** como o capítulo 3, ele tem nove seções (4.1 geometria e massa, 4.2 dados extraídos, 4.3 verificação, 4.4 parâmetros e identificação, 4.5 ajuste às curvas, 4.6 comportamento, 4.7 varredura, 4.8 confronto com o torque gravitacional e 4.9 limitações), cada uma com os exoesqueletos 1, 2 e 3 em sequência e uma abertura só para o capítulo. Saíram as seções de verificação dos exoesqueletos 2 e 3, como no seu arquivo, e ficaram o comportamento, a varredura, o confronto e as limitações dos três, com o texto encurtado e os resultados mantidos. As varreduras (h, e_c e giro do came) estão inteiras: figuras, números e conclusões.
- **Cortes seus que foram adotados:** a última frase do primeiro parágrafo de 2.4 (Palazzi), o parágrafo sobre Nasr e o das preferências da EP no capítulo 2, a seção sobre dinâmica multicorpos, o parágrafo das curvas da EP em 2.9 e as tabelas de fontes dos exoesqueletos 2 e 3.
- **Tabelas que saíram nesta rodada, porque repetiam números do texto ou de outra tabela:** a de platôs de RMSE e a de valores notáveis de h (exoesqueleto 1; os valores estão no texto de 4.7 e na Figura 11) e a de grandezas do circuito por ângulo (exoesqueleto 2; os mesmos ângulos estão na Tabela 16, do cenário de projeto).
- **Pergunta:** algum desses cortes deve voltar? Se sim, diga qual, e eu compenso em outro ponto.

### A3. Correções pontuais nos capítulos 1 e 2

Você autorizou enxugar os capítulos 1 e 2. Além dos cortes, entraram as correções objetivas abaixo. Se preferir a redação original em algum ponto, basta tirar a linha correspondente em `tcc/condensado_defesa.py`.

| Seção | Como estava | Como ficou |
|---|---|---|
| 1, 1º parágrafo | "Vários setores como: Montagem automotiva, construção civil, solda e manutenção industrial exigem" | "Vários setores, como montagem automotiva, construção civil, solda e manutenção industrial, exigem" |
| 1, 1º parágrafo | "distúrbios na articulação ombro" | "distúrbios na articulação do ombro" |
| 1, 2º parágrafo | "4,12 milhões afastamentos" | "4,12 milhões de afastamentos" |
| 1, 4º parágrafo | "Em um dispositivo passivo o auxílio é consequência" | vírgula depois de "passivo" |
| 1, 7º parágrafo | "... reduz o torque com o braço baixado e o anula quando situado sobre o eixo de rotação" | sem a última oração; o caso do elemento sobre o eixo está nas seções 3.1 e 3.6 |
| 1.1.2 | duas frases de abertura ("Para o dispositivo da EP 3 504 033 B1, acrescentam-se os objetivos:" e a da US 9.737.374 B2) | lista única, de a a i; os itens f e h nomeiam a patente |
| 1.1.2, objetivo d | "que a patente não informa — posição da ancoragem, [...]" | dois-pontos no lugar do travessão |
| 1.2 | "base quantitativa — algo que as patentes" | vírgula no lugar do travessão |
| 1.2 | "A escolha de ferramentas livres, Python e MBDyn, [...]" | "A implementação em Python, ferramenta livre, torna o modelo reprodutível por outros grupos.", no fim do primeiro parágrafo |
| 1.2 | "E o tema tem endereço local: [...]" e o parágrafo "O segundo dispositivo acrescenta [...]" | retirados: repetiam o 2º e o 7º parágrafos da introdução |
| 2.8 | "Cabe distinguir, nesse ponto, [...] comparece exclusivamente na análise dinâmica." | retirada, com a dinâmica |
| 2.9 | "quanto à origem — medida, [...] ou assumida — de modo que" | parênteses no lugar dos travessões |
| 1 e 2 | meia-risca em "braço–exoesqueleto" e "braço–antebraço" | hífen, como nos capítulos 3 a 5 |

Ficam fora dessa lista, porque pedem redação sua:

- **Seção 1, 5º parágrafo:** "apesar de conter as curvas de torque nos eixos, nenhuma delas informa massa, inércia ou rigidez". A expressão "nos eixos" não está clara. Sugestão: "embora tragam curvas de torque, nenhuma delas informa massa, inércia ou rigidez".
- **Seção 2.3, último parágrafo:** "Nenhum dos dois documentos, contudo, permite quantificar o torque". O trabalho trata de três patentes, e a seção 2.3 descreve só duas. Sugestão: trocar por "Nenhum dos três documentos" e acrescentar uma frase sobre o came da US 9.737.374 B2, com o que já está na seção 3.1.
- **Seção 2.6, último parágrafo:** "o benefício depende menos da magnitude do torque fornecido do que de sua distribuição angular". A frase é uma leitura sua dos resultados de Kim et al. (2018a, 2018b), e não uma conclusão deles. Convém dizer isso com um verbo como "sugere".

### A4. Data da defesa e folha de aprovação

- **Situação:** 26/11/2026, como no seu arquivo de 14/11, na folha de aprovação e na folha de rosto.
- **Pergunta:** a composição da banca (Okabe, Brittes e Tuckmantel) está correta?

### A5. Comprimento útil do alojamento: 131,37 mm ou 140,0 mm

- **O que havia:** a tabela de grandezas do CAD do exoesqueleto 1 trazia "Comprimento útil do alojamento, 131,37 mm", e as limitações diziam "140,0 mm no CAD". No código, a constante é `L_CARCACA = 131.37`, com o comentário "CAD anterior: 140,0".
- **Situação:** como no seu arquivo, a Tabela 1 traz 131,37 mm e a frase com 140,0 mm saiu. O documento não traz mais valores conflitantes, e a grandeza não entra em nenhum cálculo.
- **Pergunta:** qual é o valor no CAD atual? Vale corrigir o comentário no código, para que o repositório não guarde a dúvida.

### A6. Data da página do IX Shoulder Air

- **O que há no seu arquivo:** a citação aparece como "(suitX, [202-])" na identificação do exoesqueleto 2 e como "(suitX, [2026])" nas limitações; a lista de referências traz "[202-]".
- **Situação:** o documento usa "[202-]" nos dois lugares, como na lista de referências (data de publicação não informada, acesso em 23 out. 2026).
- **Pergunta:** se a página traz data de publicação, ela entra na referência e nas citações; se não traz, fica "[202-]".

## B. Perguntas que a banca deve fazer e que só você responde

### B1. Origem de θ_off = 133,017° e H_CAL = 22,701 mm (exoesqueleto 1)

- **Onde:** seções 3.9 e 4.4; Tabela 8 (origem "Congelado", situação "Origem não reproduzida").
- **Dúvida:** o texto diz que os quatro parâmetros foram identificados por mínimos quadrados "por um procedimento que não foi registrado". A revisão reproduziu K e X_pose no h adotado, mas não como se chegou a θ_off e H_CAL.
- **Por que importa:** é o ponto mais exposto do trabalho. O ajuste de R² = 0,99839 depende de dois parâmetros cuja origem o próprio texto não explica.
- **Pergunta:** você consegue descrever como chegou a esses dois valores (ferramenta, critério, restrição usada para h)? Se sim, a descrição pode entrar na seção 3.9 e muda "origem não reproduzida" para "identificado".

### B2. Como os pontos das curvas foram extraídos

- **Onde:** seção 3.9 (29 pontos da Figura 56 da US 9.889.554 B2 e 146 pontos da Figura 16 da EP 3 504 033 B1).
- **Dúvida:** o texto registra que a imagem e a resolução usadas na leitura da Figura 16 da EP "não foram registradas" e que a incerteza da extração "não foi avaliada de forma independente". Para os 29 pontos do exoesqueleto 1, o método não é descrito.
- **Pergunta:** qual ferramenta você usou em cada extração e a partir de qual arquivo de imagem? Uma frase com isso resolve as duas ressalvas.

### B3. Escala dos modelos em CAD

- **Onde:** seção 3.1 ("fator único, fixado a partir de uma estimativa de medida antropométrica", no exoesqueleto 1, e "O critério de escala do modelo não foi registrado", no exoesqueleto 2).
- **Pergunta para a defesa:** qual medida antropométrica fixou a escala do exoesqueleto 1, e como o CAD do exoesqueleto 2 foi escalado? A banca tende a perguntar, porque todas as grandezas dimensionais e de massa dependem disso.

### B4. Qual produto o CAD do exoesqueleto 2 representa

- **Onde:** a seção 2.6 associa a EP 3 504 033 B1 ao Paexo; a seção 3.1 diz que a planilha identifica o modelo como Ottobock iX Shoulder Air; a hipótese de 40% vem da página do IX Shoulder Air (SUITX, [202-]).
- **Dúvida:** são dois nomes de produto para a mesma patente. O texto já ressalva que a correspondência não está documentada, mas não diz se Paexo e iX Shoulder Air são o mesmo dispositivo, gerações diferentes ou produtos distintos.
- **Pergunta:** o CAD foi feito a partir de qual produto ou desenho? Se você souber a relação entre os dois nomes por uma fonte citável, uma frase na seção 3.1 fecha a questão.

### B5. Código "CID M75" na citação da Agência Brasil

- **Onde:** seção 1, 2º parágrafo.
- **Dúvida:** a busca confirmou a notícia (27/01/2026), os 4,12 milhões de afastamentos e as 135.093 concessões por lesões de ombro. As cópias da notícia que consegui ler falam em "lesões de ombro", sem o código M75.
- **Pergunta:** o código M75 está na notícia original ou foi acrescentado por você? Se foi acrescentado, convém tirar o código dos parênteses ou citar a fonte da correspondência.

### B6. Sua leitura das curvas da Figura 16 da US 9.737.374 B2 (exoesqueleto 3)

- **O que você mandou:** três blocos de coordenadas (AASM, RM e AWM), lidos nos marcadores da figura.
- **O que a conferência mostrou:** a sua leitura tem um erro de calibração do eixo vertical, e não de leitura dos pontos. Comparada aos 27 marcadores de cada curva (Θ de −74° a 30°, a cada 4°), ela segue M_lido = 0,9416 M − 6,156 e Θ_lido = 0,9982 Θ + 1,036°: a ordenada está deslocada de cerca de 6,2 unidades e comprimida em 6%, e a abscissa, deslocada de cerca de 1°. O sinal disso aparece no fechamento: na figura, RM = AASM + AWM, e na sua leitura AASM + AWM − RM vale em média −6,54, o próprio deslocamento. Antes da correção, a maior diferença na ordenada é de 10,63 unidades; depois de corrigida a calibração, a diferença cai a 0,32 unidade RMS (máximo de 1,66) e 0,63° RMS na abscissa, isto é, os pontos que você marcou estão certos.
- **O que entrou no repositório:** `exo3/marcadores_fig16.py` e `exo3/fig16_marcadores.csv`, com o valor de cada curva nos 27 marcadores, lido no traçado calibrado pela grade da própria figura. Nesse arquivo, o fechamento RM = AASM + AWM vale com resíduo máximo de 0,94 e médio de −0,28 unidade em 26 marcadores, e o traçado passa pelos 76 símbolos encontrados na imagem com desvio de 0,36 unidade RMS. O script aceita uma leitura manual (`--leitura arquivo.csv`) e estima a calibração dela.
- **O que não mudou:** o modelo do exoesqueleto 3 usa o traçado com um ponto por grau, que já é o dos marcadores. Nenhum número do TCC muda.
- **Pergunta:** quer que o ajuste da mola seja refeito só com os 27 marcadores de cada curva, em vez do traçado completo? A diferença esperada é pequena, mas é uma escolha sua.

## C. Verificações que não consegui executar

### C1. Dados bibliográficos por DOI

- O ambiente bloqueia o acesso ao Crossref (`api.crossref.org`). Sem ele, não foi possível conferir título, autores, periódico, volume e páginas pelos DOIs da lista.
- Por busca na web, confirmei a existência e os dados da notícia da Agência Brasil (2026). A referência de Okabe, Brittes e Brito (2026), Journal of Computational and Nonlinear Dynamics, v. 21, n. 7, não apareceu na busca. Isso não indica erro, só que não pude confirmar; como o artigo é do seu orientador, é fácil conferir com ele.
- O que está verificado: as referências da versão para a defesa são todas citadas no texto, e nenhuma citação fica sem referência (conferência automática).
- **Como resolver:** se você liberar `api.crossref.org` no ambiente, a conferência dos DOIs leva poucos minutos.

### C2. Norma institucional aplicável

- A busca encontrou a Instrução Normativa de TCC da Faculdade de Tecnologia (FT), o regulamento de TCC do curso de Ciências do Esporte da FCA (Deliberação CMG 01/2024) e o modelo LaTeX da FT, que declara seguir a Instrução Normativa CCPG nº 06/2025. Não encontrei um regulamento de TCC específico do curso de Engenharia de Manufatura da FCA.
- O documento segue o modelo da FT (classe `tese-FT`), com a identificação da FCA. Não impus outra norma.
- **Pergunta:** a coordenação do curso ou o orientador indicou um manual ou modelo para a monografia? Se sim, vale conferir capa, folha de aprovação, limite de páginas e a exigência de ficha catalográfica contra ele.

### C3. Arquivos que não estão no repositório

- Planilha de composição inercial: as tabelas de propriedades de massa (Tabelas 2, 8 e 13) foram conferidas pela consistência interna (teorema de Steiner e M g d), e não contra a planilha.
- Arquivos de CAD dos três mecanismos: as grandezas "medidas em CAD" foram tomadas como dadas.
- Texto das patentes: as descrições das seções 2.3 e 3.1 não foram conferidas contra os documentos, só as figuras que estão na pasta `patentes/`.

### C4. Contagem de páginas no Microsoft Word

- A contagem de páginas foi feita com o LibreOffice, que é o que há no ambiente. O Word pode quebrar linhas e posicionar figuras de modo um pouco diferente, e figuras inteiras podem mudar de página.
- **Pergunta:** ao abrir o arquivo no Word, confira o total de páginas. Se passar do limite que você precisa cumprir, me diga quantas páginas deu, e eu corto o que faltar.

### C5. Citações das bibliotecas de software

- Para caber no limite, as bibliotecas NumPy, SciPy e Matplotlib continuam nomeadas na seção 3.11, mas sem citação nem entrada na lista de referências (eram as três últimas linhas que transbordavam). O método de Brent continua citado.
- **Pergunta:** se o curso ou o orientador pedir a citação do software usado, elas voltam com três entradas na lista, e eu compenso as linhas em outro ponto.

## D. Decisão sua e do orientador

### D1. Uso de ferramentas de IA

- O texto não menciona o uso de assistência de IA na revisão do modelo, na programação ou na redação.
- **Por que importa:** a pergunta sobre o que foi feito por você e o que foi feito com ajuda de ferramentas é comum em bancas, e algumas unidades pedem declaração explícita.
- **Pergunta:** há orientação da FCA ou do orientador sobre declarar esse uso? Se houver, o lugar natural são os agradecimentos ou a abertura do capítulo 3. Não acrescentei nada.

## E. Itens já decididos por você, só para constar

- **Limite de páginas:** 80 para o documento inteiro, da capa ao fim, mais as 2 que você aceitou para o exoesqueleto 3 ficar parelho com os outros dois: 82. Depois, a seu pedido, voltaram as quatro figuras que tinham saído (86 páginas), e em seguida o texto foi enxugado, sem tirar figuras nem resultados: as seções 3.4 e 3.5 foram fundidas e saíram trechos que repetiam o que já estava dito em outro lugar (80 páginas). Uma conferência frase a frase mostrou que, nesse enxugamento, tinham saído também duas conclusões (a da validade física, em 5.1, e a síntese que abre a 5.4) e frases de método, resultado e ressalva que só existiam num lugar; elas voltaram (83 páginas). Depois, o capítulo 4 foi fundido por assunto, como o 3, e a diagramação foi ajustada (tabelas e figuras depois do parágrafo que as discute, e tabelas maiores podendo atravessar a página com o cabeçalho repetido): o DOCX ficou com 81 páginas. Por fim, a seu pedido, saíram as figuras dos circuitos do modelo dos exoesqueletos 1 e 2 (antigas Figuras 1 e 3), cujo conteúdo está nas sobreposições às figuras das patentes (hoje Figuras 1 e 2): o DOCX ficou com 80 páginas. Saiu também a reprodução da Figura 16 da EP 3 504 033 B1 em 3.9, para essa seção tratar as três patentes do mesmo modo; as curvas das três aparecem nos resultados, com os pontos extraídos.
- **Seu arquivo de 14/11 como base:** ficaram as suas quatro alterações (data da defesa, frase retirada do capítulo 2, parágrafo do CAD do exoesqueleto 1 e retirada do parágrafo do apoio de braço do exoesqueleto 3 em 3.2). Para essa tabela (hoje a Tabela 6) continuar citada no texto, o exoesqueleto 3 ganhou, na seção 4.1, a frase "A Tabela 6 reúne as propriedades de massa do conjunto."
- **Figuras de volta:** (depois, a seu pedido, saíram de novo só as duas figuras de circuito do modelo, que as sobreposições já mostram) o circuito do exoesqueleto 1 sobre a Figura 42 da US 9.889.554 B2 (Figura 1), os circuitos do exoesqueleto 2 sobre a Figura 22 da EP 3 504 033 B1 (Figura 2), o ajuste de forma do exoesqueleto 2, que era do apêndice (Figura 7), e o cenário de projeto do exoesqueleto 2 em gráfico (Figura 17). Algumas legendas longas foram encurtadas, sem perder informação que não esteja na nota ou no texto, para a lista de figuras caber numa página.
- **Exoesqueleto 3 parelho:** a identificação da mola, a qualidade do ajuste e os parâmetros do modelo do exoesqueleto 3 ficaram separados, como no exoesqueleto 2; com o capítulo 4 fundido por assunto, a identificação e os parâmetros estão em 4.4, e a qualidade do ajuste, em 4.5. Voltaram as recomendações de continuidade de 5.2 e 5.3, sem a parte de dinâmica, e as aberturas de cada exoesqueleto no capítulo 4 viraram a abertura única do capítulo.
- **Base:** o seu arquivo com os cortes, sem seguir 100% dele; a metodologia fundida por tópico e os resultados por exoesqueleto.
- **O que saiu, saiu de vez:** não há apêndice nem material suplementar citado no texto.
- **e_c = 34,785 mm (exoesqueleto 2) e H_CAD = 34,785 mm (exoesqueleto 1):** os dois valores coincidem até a terceira casa. Em 8/11 você conferiu e_c no CAD. A banca pode notar; a resposta está no roteiro de defesa.
- **Tabelas do mesmo tipo padronizadas (pedido de 14/11):** geometria (Tabelas 1, 3 e 5): Grandeza, Símbolo, Valor, Unidade e Origem, com "CAD" na origem de todas as grandezas da Tabela 1, que são medidas na reconstrução; massa (Tabelas 2, 4 e 6): Corpo, Massa, d, I_cm e I_O, com L no exoesqueleto 2 e a no 3; na Tabela 2, que só tem o conjunto, o centro de massa e M g d foram para a nota; parâmetros (Tabelas 8, 9 e 10): Parâmetro, Símbolo, Valor adotado, Origem e Situação, com a antiga coluna da Tabela 8 dividida em origem ("Congelado" ou "Identificado") e situação ("Origem não reproduzida" ou "Reproduzido no h adotado", como diz a seção 4.4). Nenhum número mudou.
- **Sem tabelas de pendências no TCC:** as limitações estão em texto corrido na seção 4.9.
