# Pendências e perguntas ao autor

Revisão para a defesa do TCC "Modelagem e simulação de mecanismos passivos de apoio ao braço".

Este arquivo reúne o que depende de você: decisões, dados que só você tem e confirmações. Nada do que está aqui foi alterado em silêncio no documento revisado. As perguntas estão em ordem de prioridade. As três primeiras mudam o texto final; as demais servem para você chegar à banca com a resposta pronta.

## A. Decisões que mudam o documento

### A1. Comprimento útil do alojamento: 131,37 mm ou 140,0 mm

- **Onde:** Tabela 3 (seção 4.1.1), linha "Comprimento útil do alojamento, L_carc = 131,37 mm"; seção 4.1.9, quarto parágrafo: "o comprimento útil do alojamento, que não entra na cadeia de cálculo, é de 140,0 mm no CAD".
- **Dúvida:** os dois trechos dão valores diferentes para a mesma grandeza. No código, a constante é `L_CARCACA = 131.37`, com o comentário "CAD anterior: 140,0". O registro de 8/11 diz que o CAD dá 140,0 mm.
- **Por que importa:** a grandeza não entra em nenhum cálculo, mas a Tabela 3 se chama "Grandezas medidas na reconstrução em CAD". Um membro da banca que compare a tabela com a seção 4.1.9 vê duas medidas de CAD para o mesmo alojamento.
- **Alternativas:** (a) o CAD atual dá 140,0 mm: corrigir a Tabela 3 e a constante do código; (b) o CAD atual dá 131,37 mm: corrigir a frase da seção 4.1.9; (c) são duas medidas distintas (por exemplo, comprimento total e comprimento útil): dizer isso no texto.
- **Pergunta:** qual é o valor do comprimento útil do alojamento no CAD atual?
- **Situação no documento revisado:** os dois trechos ficaram como estavam.

### A2. Correções pontuais nos capítulos 1 e 2

Você pediu que os capítulos 1 e 2 não fossem alterados, e eles estão idênticos ao original. Na leitura apareceram erros objetivos de digitação e pontuação, além de travessões, que a banca vê logo na primeira página. As correções abaixo estão prontas e desativadas; entram com uma única chave (`ALTERAR_CAP_1_2 = True` em `tcc/revisao_defesa.py`) e não reescrevem nada além do trecho indicado.

| Seção | Como está | Correção pronta |
|---|---|---|
| 1, 1º parágrafo | "Vários setores como: Montagem automotiva, construção civil, solda e manutenção industrial exigem" | "Vários setores, como montagem automotiva, construção civil, solda e manutenção industrial, exigem" |
| 1, 1º parágrafo | "distúrbios na articulação ombro" | "distúrbios na articulação do ombro" |
| 1, 2º parágrafo | "4,12 milhões afastamentos" | "4,12 milhões de afastamentos" |
| 1, 4º parágrafo | "Em um dispositivo passivo o auxílio é consequência" | vírgula depois de "passivo" |
| 1.1.2, objetivo d | "que a patente não informa — posição da ancoragem, [...]" | dois-pontos no lugar do travessão |
| 1.2, 1º parágrafo | "base quantitativa — algo que as patentes" | vírgula no lugar do travessão |
| 2.1, 2º parágrafo | "linha dos ombros — faixa angular" | vírgula no lugar do travessão |
| 2.2, 3º parágrafo | "projeto do mecanismo — circunstância" | vírgula no lugar do travessão |
| 2.10, 2º parágrafo | "quanto à origem — medida, [...] ou assumida — de modo que" | parênteses no lugar dos travessões |
| 1 e 2 | meia-risca em "braço–exoesqueleto", "braço–antebraço", "humano–exoesqueleto", "mola–cabo–polia" | hífen, como nos capítulos 3 a 5 |

- **Pergunta:** aplico essas correções pontuais, sem reescrever os capítulos?

Ficam fora dessa lista, porque pedem redação sua:

- **Seção 1, 5º parágrafo:** "apesar de conter as curvas de torque nos eixos, nenhuma delas informa massa, inércia ou rigidez". A expressão "nos eixos" não está clara. Sugestão: "embora tragam curvas de torque, nenhuma delas informa massa, inércia ou rigidez".
- **Seção 2.3, último parágrafo:** "Nenhum dos dois documentos, contudo, permite quantificar o torque". O trabalho trata de três patentes, e a seção 2.3 descreve só duas. A US 9.737.374 B2 aparece na seção 2.7, sem a descrição do came. Sugestão: acrescentar à seção 2.3 um parágrafo curto sobre o mecanismo de came, com o que já está na seção 3.3.1, e trocar a frase por "Nenhum dos três documentos", lembrando que a Figura 16 da US 9.737.374 B2 também não tem unidade na ordenada.
- **Seção 2.7, 5º parágrafo:** "o benefício depende menos da magnitude do torque fornecido do que de sua distribuição angular". A frase é uma leitura sua dos resultados de Kim et al. (2018a, 2018b), e não uma conclusão deles. Convém dizer isso com um verbo como "sugere".

### A3. Data da defesa e folha de aprovação

- **Onde:** folha de aprovação, "Limeira, XX de novembro de 2026".
- **Pergunta:** qual é a data da defesa? A composição da banca (Okabe, Brittes e Tuckmantel) está correta?
- **Situação:** mantido "XX". Não inventei data.

## B. Perguntas que a banca deve fazer e que só você responde

### B1. Origem de θ_off = 133,017° e H_CAL = 22,701 mm (exoesqueleto 1)

- **Onde:** seções 3.1.10, 4.1.4 e 4.1.9; Tabela 7 ("Congelado; origem não reproduzida").
- **Dúvida:** o texto diz que os quatro parâmetros foram identificados por mínimos quadrados "por um procedimento que não foi registrado". A revisão reproduziu K e X_pose no h adotado, mas não como se chegou a θ_off e H_CAL.
- **Por que importa:** é o ponto mais exposto do trabalho. O ajuste de R² = 0,99839 depende de dois parâmetros cuja origem o próprio texto não explica.
- **Pergunta:** você consegue descrever como chegou a esses dois valores (ferramenta, critério, restrição usada para h)? Se sim, a descrição pode entrar na seção 3.1.10 e muda "origem não reproduzida" para "identificado".

### B2. Como os pontos das curvas foram extraídos

- **Onde:** seção 3.1.10 (29 pontos da Figura 56 da US 9.889.554 B2) e seção 3.2.10 (146 pontos da Figura 16 da EP 3 504 033 B1).
- **Dúvida:** o texto registra que a imagem e a resolução usadas na leitura da Figura 16 "não foram registradas" e que a incerteza da extração "não foi avaliada de forma independente". Para os 29 pontos do exoesqueleto 1, o método não é descrito.
- **Pergunta:** qual ferramenta você usou em cada extração e a partir de qual arquivo de imagem? Uma frase com isso resolve as duas ressalvas.

### B3. Escala dos modelos em CAD

- **Onde:** seção 3.1.1 ("fator único, fixado a partir de uma estimativa de medida antropométrica") e seção 3.2.1 ("O critério de escala do modelo não foi registrado").
- **Observação:** em 8/11 você pediu que o fator do exoesqueleto 1 não fosse detalhado no texto. Isso foi mantido.
- **Pergunta para a defesa:** qual medida antropométrica fixou a escala do exoesqueleto 1, e como o CAD do exoesqueleto 2 foi escalado? A banca tende a perguntar, porque todas as grandezas dimensionais e de massa dependem disso.

### B4. Qual produto o CAD do exoesqueleto 2 representa

- **Onde:** seção 2.7 associa a EP 3 504 033 B1 ao Paexo; a seção 3.2.1 diz que a planilha identifica o modelo como Ottobock iX Shoulder Air; a hipótese de 40% vem da página do IX Shoulder Air (SUITX, [202-]).
- **Dúvida:** são dois nomes de produto para a mesma patente. O texto já ressalva que a associação entre produto e patente não pôde ser conferida, mas não diz se Paexo e iX Shoulder Air são o mesmo dispositivo, gerações diferentes ou produtos distintos.
- **Pergunta:** o CAD foi feito a partir de qual produto ou desenho? Se você souber a relação entre os dois nomes por uma fonte citável, uma frase na seção 3.2.1 fecha a questão.

### B5. Número "CID M75" na citação da Agência Brasil

- **Onde:** seção 1, 2º parágrafo.
- **Dúvida:** a busca confirmou a notícia (27/01/2026), os 4,12 milhões de afastamentos e as 135.093 concessões por lesões de ombro. As cópias da notícia que consegui ler falam em "lesões de ombro", sem o código M75.
- **Pergunta:** o código M75 está na notícia original ou foi acrescentado por você? Se foi acrescentado, convém tirar o código dos parênteses ou citar a fonte da correspondência.

## C. Verificações que não consegui executar

### C1. Dados bibliográficos por DOI

- O ambiente bloqueia o acesso ao Crossref (`api.crossref.org`). Sem ele, não foi possível conferir título, autores, periódico, volume e páginas dos 38 DOIs da lista.
- Por busca na web, confirmei a existência e os dados de Agência Brasil (2026) e de Manoel e Cavalcante (2025). Duas referências recentes não apareceram na busca: Nguyen (2026), Mechanism and Machine Theory, v. 220, art. 106345, e Okabe, Brittes e Brito (2026), Journal of Computational and Nonlinear Dynamics, v. 21, n. 7. Isso não indica erro, só que não pude confirmar.
- O que está verificado: as 45 referências são citadas no texto, e nenhuma citação fica sem referência (conferência automática do pipeline).
- **Como resolver:** se você liberar `api.crossref.org` no ambiente, a conferência dos 38 DOIs leva poucos minutos.

### C2. Norma institucional aplicável

- A busca encontrou a Instrução Normativa de TCC da Faculdade de Tecnologia (FT), o regulamento de TCC do curso de Ciências do Esporte da FCA (Deliberação CMG 01/2024) e o modelo LaTeX da FT, que declara seguir a Instrução Normativa CCPG nº 06/2025. Não encontrei um regulamento de TCC específico do curso de Engenharia de Manufatura da FCA.
- O documento segue o modelo da FT (classe `tese-FT`), com a identificação da FCA. Não impus outra norma.
- **Pergunta:** a coordenação do curso ou o orientador indicou um manual ou modelo para a monografia? Se sim, vale conferir capa, folha de aprovação e a exigência de ficha catalográfica contra ele.

### C3. Arquivos que não estão no repositório

- Planilha de composição inercial: as Tabelas 4, 14 e 22 foram conferidas pela consistência interna (teorema de Steiner e M g d), e não contra a planilha.
- Arquivos de CAD dos três mecanismos: as grandezas "medidas em CAD" foram tomadas como dadas.
- Texto das patentes: as descrições das seções 2.3, 3.2.1 e 3.3.1 não foram conferidas contra os documentos, só as figuras que estão na pasta `patentes/`.

## D. Decisão sua e do orientador

### D1. Uso de ferramentas de IA

- O texto não menciona o uso de assistência de IA na revisão do modelo, na programação ou na redação.
- **Por que importa:** a pergunta sobre o que foi feito por você e o que foi feito com ajuda de ferramentas é comum em bancas, e algumas unidades pedem declaração explícita.
- **Pergunta:** há orientação da FCA ou do orientador sobre declarar esse uso? Se houver, o lugar natural é a seção 3.1.14 (ferramentas) ou os agradecimentos. Não acrescentei nada.

## E. Itens já decididos por você, só para constar

- **e_c = 34,785 mm (exoesqueleto 2) e H_CAD = 34,785 mm (exoesqueleto 1):** os dois valores coincidem até a terceira casa. Em 8/11 você conferiu e_c no CAD e a coincidência deixou de ser pendência. A banca pode notar; a resposta está no roteiro de defesa.
- **Tabelas de pendências:** removidas a seu pedido; as limitações estão em texto corrido nas seções 4.1.9, 4.2.10 e 4.3.9.
- **Capítulos 1 e 2:** sem alterações, a seu pedido (ver A2).
