# Relatório de revisão técnica

TCC "Modelagem e simulação de mecanismos passivos de apoio ao braço", de Pedro Luís de Almeida Brito. Revisão técnica, científica e editorial para a defesa.

## 1. O que foi entregue

| Arquivo | O que é |
|---|---|
| `revisao_defesa/TCC_Modelagem_e_simulacao_de_mecanismos_passivos_revisado_para_defesa.docx` | Documento para a defesa, no formato FT/FCA, com 67 páginas da capa ao fim |
| `revisao_defesa/TCC_Modelagem_e_simulacao_de_mecanismos_passivos_revisado_para_defesa.pdf` | O mesmo conteúdo, composto em LaTeX com o modelo da FT (68 páginas) |
| `revisao_defesa/Relatorio_de_Revisao_Tecnica.md` | Este relatório |
| `revisao_defesa/Pendencias_e_Perguntas_ao_Autor.md` | O que depende de você: decisões, dados e confirmações |
| `revisao_defesa/Roteiro_de_Defesa.md` | Perguntas prováveis da banca, com a resposta que o texto sustenta e a seção correspondente |
| `revisao_defesa/O_que_saiu_e_o_que_ficou.md` | Mapa de seções, tabelas, figuras e equações: numeração antiga, numeração nova ou "saiu" |

O arquivo de origem, `tcc/TCC_apenas_exo1.docx`, e os dois documentos longos de `tcc/` não foram tocados; os três têm o hash conferido ao fim de cada geração.

## 2. Como a versão para a defesa foi construída

O trabalho teve duas etapas.

**Etapa 1, revisão do documento longo.** Leitura integral do documento de 123 páginas, auditoria técnica, matemática e computacional e reescrita de 68 parágrafos dos capítulos 3 a 5 (frases longas divididas, jargão interno trocado por termos da patente, remissões corrigidas, travessões retirados). O registro dessas reescritas, antes e depois, está em `revisao_defesa/Alteracoes_paragrafo_a_paragrafo.md`. Essa versão longa revisada ficou no histórico do repositório (commit `c3bee74`).

**Etapa 2, versão condensada.** Você pediu um DOCX de no máximo 60 a 70 páginas e decidiu: o limite vale para o documento inteiro; o que sai, sai de vez; os três exoesqueletos ficam enxutos, com o mesmo peso; os capítulos 1 e 2 também podem ser enxugados; e sai tudo o que menciona a etapa dinâmica e o MBDyn. A versão condensada parte do documento longo revisado e é montada por um plano declarado (`tcc/condensado_defesa.py`), que diz, bloco a bloco, o que fica, o que tem um trecho trocado e o que é substituído por um parágrafo mais curto.

| | Documento longo | Versão condensada |
|---|---|---|
| Páginas (DOCX, LibreOffice) | 123 | 67 |
| Títulos numerados | 104 | 64 |
| Equações numeradas | 69 | 56 |
| Figuras | 20 | 11 |
| Tabelas | 33 | 13 |
| Referências | 45 | 29 |

Composição do corpo da versão condensada: 391 blocos, dos quais 201 mantidos sem alteração (equações, figuras, tabelas e parágrafos), 36 mantidos com um trecho trocado ou cortado, 5 legendas ou notas reescritas, 4 tabelas com linhas retiradas, 112 parágrafos novos, que condensam os do documento longo, e 33 títulos novos.

Cada exoesqueleto ficou com seis subseções de método (reconstrução e propriedades de massa; convenções e fechamento do circuito; braço de momento, elemento elástico e torque; torque gravitacional e trabalho virtual; dados da patente e identificação; varredura paramétrica e verificações) e cinco de resultados (geometria e verificações; identificação e ajuste; comportamento e varredura; confronto com o torque gravitacional; limitações). A variável independente é q nas três formulações, e a definição do trabalho virtual, δW = 0, aparece em destaque nas três.

## 3. Diagnóstico

A classificação indica o efeito sobre a defesa. "Declarado" quer dizer que o texto já diz o problema com todas as letras e que a banca vai encontrá-lo escrito.

### 3.1 Críticos

| Problema | Onde | Situação |
|---|---|---|
| θ_off = 133,017° e H_CAL = 22,701 mm têm origem não reproduzida; o ajuste de R² = 0,99839 depende deles | 3.1.5, 4.1.2, Tabela 4 | Declarado. A revisão reproduziu K e X_pose no h adotado, mas não o procedimento que levou a esses dois valores. Pergunta B1 |
| Os quatro parâmetros do exoesqueleto 1 foram identificados e avaliados nos mesmos 29 pontos | 4.1.2, 5.1 | Declarado: "não constitui validação independente" |
| A forma do torque do exoesqueleto 2, com a geometria do CAD, não reproduz as curvas da patente (R² de −1,529 a −0,417) | 4.2.2, 4.2.5, 5.2 | Declarado, com a causa delimitada (não é o comprimento s) |
| A magnitude do torque depende de hipótese nos três mecanismos: unidade da patente no primeiro, K40 no segundo, AWM igualada ao peso do membro no terceiro | 4.1.3, 4.2.4, 4.3.4, 5.4 | Declarado. O último parágrafo de 5.4 separa o que depende e o que não depende de escala |
| O título fala em "simulação" e o texto, por decisão sua, é só estático | título, 1.1 | Decisão do autor. Pergunta A1 e pergunta 2.11 do roteiro |

### 3.2 Importantes

| Problema | Onde | Situação |
|---|---|---|
| Duas remissões a "Figura 16" sem dizer de qual patente; na conversão, viravam remissão à figura de mesmo número do próprio TCC | limitações do exo 2 e montagens do exo 3 | Corrigido na versão condensada: "Figura 16 da patente" e "Figura 16 da US 9.737.374 B2" |
| Remissão desatualizada a uma seção de resultados | método do exo 3 | Corrigida na etapa 1; o parágrafo saiu depois, com a etapa dinâmica |
| Comprimento útil do alojamento com dois valores (131,37 mm na tabela, 140,0 mm no texto) | resultados do exo 1 | A grandeza não entra em cálculo algum; os dois trechos saíram no corte. A dúvida continua valendo para o código. Pergunta A4 |
| "Nenhum dos dois documentos" numa seção de um trabalho que trata de três patentes | 2.3 | Mantido. Pede redação sua. Pergunta A2 |
| Dois nomes de produto para a mesma patente (Paexo e iX Shoulder Air) | 2.6 e 3.2.1 | Mantido e ressalvado no texto. Pergunta B4 |
| Método de extração dos pontos das curvas não descrito; incerteza não avaliada | 3.1.5, 3.2.5 | Declarado. Pergunta B2 |
| Critério de escala dos modelos em CAD | 3.1.1, 3.2.1 | Declarado. Pergunta B3 |
| Código "CID M75" atribuído à notícia da Agência Brasil | 1 | Não confirmado na fonte. Pergunta B5 |
| e_c = 34,785 mm (exo 2) igual a H_CAD = 34,785 mm (exo 1) | Tabelas 2 e 6 | Coincidência confirmada por você no CAD em 8/11; resposta pronta no roteiro |

### 3.3 Editoriais

| Problema | Situação |
|---|---|
| Erros de digitação e de pontuação no primeiro parágrafo da introdução ("como: Montagem", "articulação ombro", "milhões afastamentos") | Corrigidos. Lista em A2 das pendências |
| Travessões e meias-riscas entre palavras | Retirados do corpo inteiro. Restam o separador das legendas das tabelas e figuras do seu texto original ("Tabela 2 — ...") e os das referências, que fazem parte dos títulos citados |
| Jargão interno ("bolsão", "chifres", nomes de variáveis do código) e verbos informais | Trocados na etapa 1 |
| Parágrafos de mais de dez linhas, com várias ideias | Divididos na etapa 1; na etapa 2, condensados |
| Listas de tarefas internas e tabelas de pendências dentro do TCC | Fora do texto, a seu pedido; as limitações estão em texto corrido |

## 4. Auditoria técnica e matemática

Feita sobre o documento longo; a versão condensada herda as equações, as figuras, as tabelas e os números sem alteração, o que é conferido por máquina (seção 6).

- **Equações como impressas.** As equações dos três exoesqueletos foram reimplementadas de forma independente, a partir do texto, e comparadas com as saídas dos modelos: 38 conferências no exoesqueleto 1 (`revisao_defesa/auditoria/auditoria_exo1.py`) e 66 nos exoesqueletos 2 e 3 (`auditoria_exo2_exo3.py`). Todas fecham: fechamento do circuito, solução fechada, braço de momento, lei da mola, torque, ponto morto, torque gravitacional e as igualdades do trabalho virtual (dℓ/dq = m; ds/dq = −m; τ = (F_s/1000) dx/dq).
- **Sinais e convenções.** As três convenções angulares foram conferidas com as figuras e com os códigos. A variável independente é q nas três formulações; o braço de momento é a derivada do caminho do elemento elástico em relação a q, com o sinal de cada caso (Tabela 1).
- **Um erro de texto encontrado e corrigido na base.** A frase que descrevia a variação do vão do cabo de ancoragem no trabalho virtual do exoesqueleto 3 não correspondia ao cálculo; foi reescrita e conferida numericamente (resíduo de 1,2 × 10⁻⁷ mm/rad).
- **Unidades.** O fator 1/1000 das expressões de torque (milímetros para metros) foi conferido nos três modelos. O torque do exoesqueleto 1 está em unidade da patente, e o texto não o apresenta em N·m em nenhum ponto.
- **Composição inercial.** As tabelas de propriedades de massa foram conferidas pela consistência interna (teorema de Steiner e M g d), e não contra a planilha, que não está no repositório.

## 5. Auditoria computacional

- Os três scripts de resultados (`tcc_resultados.py`, `tcc_resultados_ottobock.py` e `tcc_resultados_exo3.py`), executados numa cópia limpa do repositório, reproduzem byte a byte os arquivos `results/*.json` de onde saem os números do texto.
- Os scripts do exoesqueleto 3 que leem as imagens das folhas da patente reproduzem os valores usados no texto.
- A bateria de testes automatizados passa: 47 testes (`python -m pytest -q`), reexecutada ao fim desta entrega.
- Varredura dos números: os 2.059 valores decimais do documento longo foram procurados nos resultados; 2.005 foram encontrados diretamente, e os 54 restantes, que são derivados (somas, diferenças, razões), foram conferidos à mão.

## 6. Conferências da versão condensada

Executadas por `tcc/verificar_condensado.py` e pelos verificadores do pipeline, todas sem falha:

| Conferência | Resultado |
|---|---|
| Numeração de seções, tabelas, figuras e equações em sequência; remissões sem destino | 64 títulos, 13 tabelas, 11 figuras e 56 equações em ordem; nenhuma remissão sem destino; nenhuma tabela ou figura sem chamada no texto |
| Proveniência dos números: todo número do texto condensado existe no documento longo | 1.376 números conferidos; nenhum novo |
| Equações iguais às do documento longo | 56 equações editáveis, idênticas byte a byte |
| Figuras e tabelas | 11 imagens idênticas às do documento longo (duas reduzidas em tamanho na página: os circuitos do exoesqueleto 2 e a reprodução da Figura 16 da EP 3 504 033 B1); nenhuma linha de tabela que não exista no documento longo |
| Termos retirados (MBDyn, Lagrange, etapa dinâmica, equação de movimento, apêndice) | Nenhuma ocorrência, incluídos o resumo e o abstract |
| Travessões no corpo | Nenhum, fora do separador das legendas do texto original |
| Citações e referências | 29 referências, todas citadas; nenhuma citação sem referência |
| DOCX contra o PDF do LaTeX (`verificar_docx_modelo.py`) | Mesmo texto, mesmas equações, tabelas e figuras; sumário e listas com as páginas do próprio DOCX |
| Integridade do pacote DOCX | Abre sem erro; sem comentários nem alterações controladas; equações editáveis, nenhuma em imagem |
| Páginas | 67, da capa ao fim, na conversão pelo LibreOffice |
| Inspeção visual | Todas as 67 páginas renderizadas e olhadas: capa, folha de aprovação, resumo, listas, sumário, equações, figuras e tabelas; nenhuma nota ou fonte separada da sua figura |

## 7. O que saiu

O mapa completo está em `O_que_saiu_e_o_que_ficou.md`. Em resumo:

- **Etapa dinâmica e MBDyn:** dois objetivos específicos, a seção de fundamentação sobre dinâmica multicorpos, as três seções de etapas dinâmicas previstas, a equação de movimento e as frases correspondentes das conclusões, do resumo e do abstract.
- **Apêndice A** (robustez da identificação e ajuste de forma do exoesqueleto 2), inteiro. O texto guarda o essencial em 3.2.5 e 4.2.2: as faixas de ângulo testadas, o ruído de 0,5 px em 500 sorteios e o intervalo de 299,81 a 301,95 mm.
- **Tabelas longas:** os 29 pontos extraídos do exoesqueleto 1, os pontos das três curvas da EP 3 504 033 B1, as tabelas de resíduos das verificações (os valores principais estão no texto), as tabelas de grandezas por ângulo e as tabelas de parâmetros dos exoesqueletos 2 e 3.
- **Figuras:** as duas sobreposições do circuito ao desenho da patente (exos 1 e 2), a família de curvas e o RMSE em função de h, a família em e_c, o cenário de projeto em gráfico, a varredura em Θ do exoesqueleto 3 e as curvas das nove montagens do came.
- **Equações:** a de Steiner (está em linha na abertura do capítulo 3), a primeira formulação de ρ, o ponto de tangência em forma vetorial, a inversão do ponto morto, a definição dos indicadores de erro, a solução fechada por regime do exoesqueleto 2, o ângulo de contato com p = 0 (dito em palavras), o fator G por curva (dito em palavras) e as condições de ponto morto e de limite de subida do exoesqueleto 3 (ditas em palavras).
- **Capítulos 1 e 2:** parágrafos sobre reabilitação, instrumentação de dispositivos ativos, estratégias de compensação de desalinhamento e meta-análises, e as 16 referências que só eles e as seções retiradas citavam.

## 8. Referências e normas

- Todas as 29 referências são citadas, e toda citação tem referência (conferência automática).
- A conferência dos dados bibliográficos pelos DOIs não foi feita: o ambiente bloqueia `api.crossref.org`. Por busca na web, a notícia da Agência Brasil (2026) foi confirmada; o artigo de Okabe, Brittes e Brito (2026) não apareceu na busca.
- O documento segue o modelo LaTeX da FT (classe `tese-FT`), que declara seguir a Instrução Normativa CCPG nº 06/2025, com a identificação da FCA. Não foi encontrado regulamento de TCC específico do curso de Engenharia de Manufatura da FCA, e nenhuma outra norma foi imposta.

## 9. Verificações pendentes

| Pendente | Por quê | Como resolver |
|---|---|---|
| Contagem de páginas no Microsoft Word | O ambiente só tem LibreOffice; o Word pode quebrar linhas de modo diferente | Abrir o DOCX no Word e conferir o total |
| Dados bibliográficos por DOI | Acesso ao Crossref bloqueado | Liberar `api.crossref.org` ou conferir à mão |
| Norma do curso para a monografia | Não localizada | Confirmar com a coordenação ou com o orientador |
| Grandezas "medidas em CAD" | Os arquivos de CAD e a planilha não estão no repositório | Conferir no CAD as Tabelas 2, 6 e 9 |
| Descrições das patentes | O texto das patentes não está no repositório, só as figuras | Conferir 2.3, 3.2.1 e 3.3.1 contra os documentos |
| Data da defesa | Não informada | Preencher "XX" na folha de aprovação |

## 10. Como reproduzir

Na raiz do repositório:

```
python3 tcc/gerar_condensado.py --tudo     # conteúdo, LaTeX, PDF e DOCX no formato FT (cerca de 10 minutos)
python3 tcc/verificar_condensado.py        # conferências da seção 6 e mapa do que saiu
python3 -m pytest -q                       # testes dos modelos
```

Para mudar o que fica e o que sai, edite `tcc/condensado_defesa.py`: cada linha do plano mantém um bloco (`K`), troca um trecho (`E`), reescreve uma legenda ou nota (`R`), corta linhas de uma tabela (`L`) ou põe um parágrafo novo (`P`). A numeração de seções, tabelas, figuras e equações é refeita sozinha, e o verificador acusa qualquer número que não exista no documento longo.
