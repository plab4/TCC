# Pendências e perguntas ao autor

Versão condensada para a defesa do TCC "Modelagem de mecanismos passivos de apoio ao braço".

Este arquivo reúne o que depende de você: decisões, dados que só você tem e confirmações. Nada do que está aqui foi resolvido em silêncio no documento. As perguntas estão em ordem de prioridade. As da parte A mudam o texto final; as demais servem para você chegar à banca com a resposta pronta.

## A. Decisões que mudam o documento

### A1. Retirada da etapa dinâmica e dos objetivos correspondentes

- **O que foi feito, a seu pedido:** saiu tudo o que mencionava a etapa dinâmica e o MBDyn. Na prática: os objetivos específicos sobre a equação de movimento e sobre o acoplamento multicorpos (eram f e g), a seção de fundamentação sobre modelagem dinâmica multicorpos (era a 2.6), as três seções de etapas dinâmicas previstas (eram 3.1.13, 3.2.13 e 3.3.13), a equação de movimento, as frases correspondentes das conclusões e a última frase do resumo e do abstract. Os objetivos seguintes mudaram de letra: os do exoesqueleto 2 são agora f e g, e os do exoesqueleto 3, h e i.
- **Título:** por decisão sua, passou a "Modelagem de mecanismos passivos de apoio ao braço", na capa e na folha de rosto. Os arquivos entregues foram renomeados para acompanhar o título.
- **Por que importa:** se o projeto aprovado previa os objetivos de dinâmica, ou se o título antigo está registrado na coordenação, a banca ou a secretaria podem perguntar.
- **Pergunta:** o orientador está de acordo com a retirada dos dois objetivos e com o título novo? É preciso atualizar o título em algum registro do curso?
- **Situação no documento:** texto só estático, sem menção à dinâmica. O roteiro de defesa traz a resposta que o texto sustenta (pergunta 2.11).

### A2. Correções pontuais nos capítulos 1 e 2

Você autorizou enxugar os capítulos 1 e 2. Além dos cortes, entraram as correções objetivas abaixo. Se preferir a redação original em algum ponto, basta tirar a linha correspondente em `tcc/condensado_defesa.py`.

| Seção | Como estava | Como ficou |
|---|---|---|
| 1, 1º parágrafo | "Vários setores como: Montagem automotiva, construção civil, solda e manutenção industrial exigem" | "Vários setores, como montagem automotiva, construção civil, solda e manutenção industrial, exigem" |
| 1, 1º parágrafo | "distúrbios na articulação ombro" | "distúrbios na articulação do ombro" |
| 1, 2º parágrafo | "4,12 milhões afastamentos" | "4,12 milhões de afastamentos" |
| 1, 4º parágrafo | "Em um dispositivo passivo o auxílio é consequência" | vírgula depois de "passivo" |
| 1.1.2, objetivo d | "que a patente não informa — posição da ancoragem, [...]" | dois-pontos no lugar do travessão |
| 1.2 | "base quantitativa — algo que as patentes" | vírgula no lugar do travessão |
| 2.9 | "quanto à origem — medida, [...] ou assumida — de modo que" | parênteses no lugar dos travessões |
| 1 e 2 | meia-risca em "braço–exoesqueleto" e "braço–antebraço" | hífen, como nos capítulos 3 a 5 |

Ficam fora dessa lista, porque pedem redação sua:

- **Seção 1, 5º parágrafo:** "apesar de conter as curvas de torque nos eixos, nenhuma delas informa massa, inércia ou rigidez". A expressão "nos eixos" não está clara. Sugestão: "embora tragam curvas de torque, nenhuma delas informa massa, inércia ou rigidez".
- **Seção 2.3, último parágrafo:** "Nenhum dos dois documentos, contudo, permite quantificar o torque". O trabalho trata de três patentes, e a seção 2.3 descreve só duas. Sugestão: trocar por "Nenhum dos três documentos" e acrescentar uma frase sobre o came da US 9.737.374 B2, com o que já está na seção 3.3.1.
- **Seção 2.6, último parágrafo:** "o benefício depende menos da magnitude do torque fornecido do que de sua distribuição angular". A frase é uma leitura sua dos resultados de Kim et al. (2018a, 2018b), e não uma conclusão deles. Convém dizer isso com um verbo como "sugere".

### A3. Data da defesa e folha de aprovação

- **Onde:** folha de aprovação, "Limeira, XX de novembro de 2026".
- **Pergunta:** qual é a data da defesa? A composição da banca (Okabe, Brittes e Tuckmantel) está correta?
- **Situação:** mantido "XX". Não inventei data.

### A4. Comprimento útil do alojamento: 131,37 mm ou 140,0 mm

- **O que havia:** a tabela de grandezas do CAD do exoesqueleto 1 trazia "Comprimento útil do alojamento, 131,37 mm", e as limitações diziam "140,0 mm no CAD". No código, a constante é `L_CARCACA = 131.37`, com o comentário "CAD anterior: 140,0".
- **Situação na versão condensada:** a grandeza não entra em nenhum cálculo, e os dois trechos saíram. O documento não traz mais valores conflitantes.
- **Pergunta:** qual é o valor no CAD atual? Vale corrigir a constante ou o comentário no código, para que o repositório não guarde a dúvida.

## B. Perguntas que a banca deve fazer e que só você responde

### B1. Origem de θ_off = 133,017° e H_CAL = 22,701 mm (exoesqueleto 1)

- **Onde:** seções 3.1.5 e 4.1.2; Tabela 4 ("Congelado; origem não reproduzida").
- **Dúvida:** o texto diz que os quatro parâmetros foram identificados por mínimos quadrados "por um procedimento que não foi registrado". A revisão reproduziu K e X_pose no h adotado, mas não como se chegou a θ_off e H_CAL.
- **Por que importa:** é o ponto mais exposto do trabalho. O ajuste de R² = 0,99839 depende de dois parâmetros cuja origem o próprio texto não explica.
- **Pergunta:** você consegue descrever como chegou a esses dois valores (ferramenta, critério, restrição usada para h)? Se sim, a descrição pode entrar na seção 3.1.5 e muda "origem não reproduzida" para "identificado".

### B2. Como os pontos das curvas foram extraídos

- **Onde:** seção 3.1.5 (29 pontos da Figura 56 da US 9.889.554 B2) e seção 3.2.5 (146 pontos da Figura 16 da EP 3 504 033 B1).
- **Dúvida:** o texto registra que a imagem e a resolução usadas na leitura da Figura 16 "não foram registradas" e que a incerteza da extração "não foi avaliada de forma independente". Para os 29 pontos do exoesqueleto 1, o método não é descrito.
- **Pergunta:** qual ferramenta você usou em cada extração e a partir de qual arquivo de imagem? Uma frase com isso resolve as duas ressalvas.

### B3. Escala dos modelos em CAD

- **Onde:** seção 3.1.1 ("fator único, fixado a partir de uma estimativa de medida antropométrica") e seção 3.2.1 ("O critério de escala do modelo não foi registrado").
- **Pergunta para a defesa:** qual medida antropométrica fixou a escala do exoesqueleto 1, e como o CAD do exoesqueleto 2 foi escalado? A banca tende a perguntar, porque todas as grandezas dimensionais e de massa dependem disso.

### B4. Qual produto o CAD do exoesqueleto 2 representa

- **Onde:** a seção 2.6 associa a EP 3 504 033 B1 ao Paexo; a seção 3.2.1 diz que a planilha identifica o modelo como Ottobock iX Shoulder Air; a hipótese de 40% vem da página do IX Shoulder Air (SUITX, [202-]).
- **Dúvida:** são dois nomes de produto para a mesma patente. O texto já ressalva que a correspondência não está documentada, mas não diz se Paexo e iX Shoulder Air são o mesmo dispositivo, gerações diferentes ou produtos distintos.
- **Pergunta:** o CAD foi feito a partir de qual produto ou desenho? Se você souber a relação entre os dois nomes por uma fonte citável, uma frase na seção 3.2.1 fecha a questão.

### B5. Código "CID M75" na citação da Agência Brasil

- **Onde:** seção 1, 2º parágrafo.
- **Dúvida:** a busca confirmou a notícia (27/01/2026), os 4,12 milhões de afastamentos e as 135.093 concessões por lesões de ombro. As cópias da notícia que consegui ler falam em "lesões de ombro", sem o código M75.
- **Pergunta:** o código M75 está na notícia original ou foi acrescentado por você? Se foi acrescentado, convém tirar o código dos parênteses ou citar a fonte da correspondência.

## C. Verificações que não consegui executar

### C1. Dados bibliográficos por DOI

- O ambiente bloqueia o acesso ao Crossref (`api.crossref.org`). Sem ele, não foi possível conferir título, autores, periódico, volume e páginas pelos DOIs da lista.
- Por busca na web, confirmei a existência e os dados da notícia da Agência Brasil (2026). A referência de Okabe, Brittes e Brito (2026), Journal of Computational and Nonlinear Dynamics, v. 21, n. 7, não apareceu na busca. Isso não indica erro, só que não pude confirmar; como o artigo é do seu orientador, é fácil conferir com ele.
- O que está verificado: as 29 referências da versão condensada são citadas no texto, e nenhuma citação fica sem referência (conferência automática).
- **Como resolver:** se você liberar `api.crossref.org` no ambiente, a conferência dos DOIs leva poucos minutos.

### C2. Norma institucional aplicável

- A busca encontrou a Instrução Normativa de TCC da Faculdade de Tecnologia (FT), o regulamento de TCC do curso de Ciências do Esporte da FCA (Deliberação CMG 01/2024) e o modelo LaTeX da FT, que declara seguir a Instrução Normativa CCPG nº 06/2025. Não encontrei um regulamento de TCC específico do curso de Engenharia de Manufatura da FCA.
- O documento segue o modelo da FT (classe `tese-FT`), com a identificação da FCA. Não impus outra norma.
- **Pergunta:** a coordenação do curso ou o orientador indicou um manual ou modelo para a monografia? Se sim, vale conferir capa, folha de aprovação, limite de páginas e a exigência de ficha catalográfica contra ele.

### C3. Arquivos que não estão no repositório

- Planilha de composição inercial: as tabelas de propriedades de massa (Tabelas 3, 7 e 10) foram conferidas pela consistência interna (teorema de Steiner e M g d), e não contra a planilha.
- Arquivos de CAD dos três mecanismos: as grandezas "medidas em CAD" foram tomadas como dadas.
- Texto das patentes: as descrições das seções 2.3, 3.2.1 e 3.3.1 não foram conferidas contra os documentos, só as figuras que estão na pasta `patentes/`.

### C4. Contagem de páginas no Microsoft Word

- A contagem de páginas foi feita com o LibreOffice, que é o que há no ambiente. O Word pode quebrar linhas de modo um pouco diferente.
- **Pergunta:** ao abrir o arquivo no Word, confira o total de páginas. Se passar do limite que você precisa cumprir, me diga quantas páginas deu, e eu corto o que faltar.

## D. Decisão sua e do orientador

### D1. Uso de ferramentas de IA

- O texto não menciona o uso de assistência de IA na revisão do modelo, na programação ou na redação.
- **Por que importa:** a pergunta sobre o que foi feito por você e o que foi feito com ajuda de ferramentas é comum em bancas, e algumas unidades pedem declaração explícita.
- **Pergunta:** há orientação da FCA ou do orientador sobre declarar esse uso? Se houver, o lugar natural são os agradecimentos ou a abertura do capítulo 3. Não acrescentei nada.

## E. Itens já decididos por você, só para constar

- **Limite de 60 a 70 páginas:** vale para o documento inteiro, da capa ao fim.
- **O que saiu, saiu de vez:** não há apêndice nem material suplementar citado no texto.
- **Três exoesqueletos com o mesmo peso:** seis subseções de método e cinco de resultados para cada um.
- **e_c = 34,785 mm (exoesqueleto 2) e H_CAD = 34,785 mm (exoesqueleto 1):** os dois valores coincidem até a terceira casa. Em 8/11 você conferiu e_c no CAD. A banca pode notar; a resposta está no roteiro de defesa.
- **Sem tabelas de pendências no TCC:** as limitações estão em texto corrido nas seções 4.1.5, 4.2.5 e 4.3.5.
