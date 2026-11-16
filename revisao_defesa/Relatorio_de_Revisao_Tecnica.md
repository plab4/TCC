# Relatório de revisão técnica

TCC "Modelagem de mecanismos passivos de apoio ao braço", de Pedro Luís de Almeida Brito. Revisão técnica, científica e editorial para a defesa.

## 1. O que foi entregue

| Arquivo | O que é |
|---|---|
| `revisao_defesa/TCC_Modelagem_de_mecanismos_passivos_revisado_para_defesa.docx` | Documento para a defesa, no formato FT/FCA, com 82 páginas da capa ao fim |
| `revisao_defesa/TCC_Modelagem_de_mecanismos_passivos_revisado_para_defesa.pdf` | O mesmo conteúdo, composto em LaTeX com o modelo da FT (81 páginas) |
| `revisao_defesa/Relatorio_de_Revisao_Tecnica.md` | Este relatório |
| `revisao_defesa/Pendencias_e_Perguntas_ao_Autor.md` | O que depende de você: decisões, dados e confirmações |
| `revisao_defesa/Roteiro_de_Defesa.md` | Perguntas prováveis da banca, com a resposta que o texto sustenta e a seção correspondente |
| `revisao_defesa/O_que_saiu_e_o_que_ficou.md` | Mapa de seções, tabelas, figuras e equações: numeração antiga, numeração nova ou "saiu" |

O arquivo de origem, `tcc/TCC_apenas_exo1.docx`, e os dois documentos longos de `tcc/` não foram tocados; os três têm o hash conferido ao fim de cada geração.

## 2. Como a versão para a defesa foi construída

O trabalho teve três etapas.

**Etapa 1, revisão do documento longo.** Leitura integral do documento de 123 páginas, auditoria técnica, matemática e computacional e reescrita de 68 parágrafos dos capítulos 3 a 5 (frases longas divididas, jargão interno trocado por termos da patente, remissões corrigidas, travessões retirados). O registro dessas reescritas, antes e depois, está em `revisao_defesa/Alteracoes_paragrafo_a_paragrafo.md`. Essa versão longa revisada ficou no histórico do repositório (commit `c3bee74`).

**Etapa 2, primeira versão condensada (67 páginas).** Você pediu um DOCX de no máximo 60 a 70 páginas e decidiu: o limite vale para o documento inteiro; o que sai, sai de vez; os capítulos 1 e 2 também podem ser enxugados; e sai tudo o que menciona a etapa dinâmica e o MBDyn. O título passou a "Modelagem de mecanismos passivos de apoio ao braço", também por decisão sua, e os arquivos entregues foram renomeados para acompanhá-lo. Para caber, essa versão cortou os resultados das varreduras, o que você apontou como o erro principal.

**Etapa 3, versão de até 82 páginas.** Você mandou o seu arquivo com cortes como base, pediu que as subseções de comportamento, varredura, confronto e limitações (4.x.6 a 4.x.9) ficassem, com o texto encurtado e o essencial mantido, e que voltassem os tópicos de ponto morto, torque gravitacional, trabalhos virtuais e identificação; escolheu fundir a metodologia por tópico e fixou o limite em 80 páginas; depois, aceitou 2 a mais para o exoesqueleto 3 ficar parelho com os outros dois. A versão para a defesa parte do documento longo revisado e é montada por um plano declarado (`tcc/condensado_defesa.py`), que diz, bloco a bloco, o que fica, o que tem um trecho trocado e o que é substituído por um parágrafo mais curto.

| | Documento longo | Versão condensada |
|---|---|---|
| Páginas (DOCX, LibreOffice) | 123 | 82 |
| Títulos numerados | 104 | 35 |
| Equações numeradas | 69 | 64 |
| Figuras | 20 | 20 |
| Tabelas | 33 | 19 |
| Referências | 45 | 37 |

Composição do corpo da versão para a defesa: 501 blocos, dos quais 215 mantidos sem alteração (equações, figuras, tabelas e parágrafos), 134 mantidos com um trecho trocado ou cortado, 33 legendas, notas ou parágrafos reescritos, 68 parágrafos novos, que condensam ou juntam os do documento longo ou trazem o complemento do exoesqueleto 3, 20 títulos novos (as 11 seções do capítulo 3 e as 9 do capítulo 4), 12 tabelas remontadas no formato padrão, 3 notas de tabela novas, 1 tabela nova e 3 figuras novas. Depois do limite de 82 páginas, voltaram, a seu pedido, as quatro figuras que tinham saído (86 páginas); em seguida, as seções 3.4 e 3.5 foram fundidas e saíram trechos repetidos, e o DOCX ficou com 80 páginas. Uma conferência frase a frase contra a versão anterior mostrou que tinham saído também duas conclusões e frases de método, resultado e ressalva que só existiam num lugar; elas voltaram (83 páginas). Por fim, o capítulo 4 foi fundido por assunto, como o 3, e cada tabela ou figura que deixava vão no fim da página passou para depois do parágrafo seguinte que a discute; tabelas acima de 180 pt podem atravessar a página, com o cabeçalho repetido. O DOCX ficou com 81 páginas. Por fim, a seu pedido, saíram as figuras dos circuitos do modelo dos exoesqueletos 1 e 2, que as sobreposições às Figuras 42 da US 9.889.554 B2 e 22 da EP 3 504 033 B1 já mostram; as notas dessas sobreposições passaram a dizer o que é cada ponto e cada circuito, e o DOCX ficou com 80 páginas. Também a seu pedido saiu a reprodução da Figura 16 da EP 3 504 033 B1 em 3.9, para que essa seção não mostre a figura de uma patente só; os pontos extraídos das três patentes aparecem nos resultados. O DOCX continua com 80 páginas. Por fim, as tabelas do mesmo tipo foram padronizadas entre os três exoesqueletos: as de geometria (1, 3 e 5) têm as colunas Grandeza, Símbolo, Valor, Unidade e Origem; as de massa (2, 4 e 6), Corpo, Massa, d, I_cm e I_O, com uma coluna própria de cada mecanismo (L no exoesqueleto 2, a no 3); e as de parâmetros (8, 9 e 10), Parâmetro, Símbolo, Valor adotado, Origem e Situação; as legendas seguem o mesmo padrão, com o número do exoesqueleto. Nenhum número mudou; o verificador confere que cada número das tabelas remontadas está na tabela de origem. O DOCX ficou com 80 páginas. No seu arquivo de 15/11 entraram M.d² no exoesqueleto 1, "Calculada" no lugar de "Derivada" nas tabelas de geometria e as tabelas de parâmetros sem a coluna Situação. Depois, a seu pedido, o capítulo 5 foi fundido por assunto, como os capítulos 3 e 4, e o exoesqueleto 3 ganhou em 4.7 e 4.8 a reprodução da Figura 16 da US 9.737.374 B2 pelos 27 marcadores e o confronto, nesses marcadores, do torque da patente com o torque do braço; os números novos vêm de results/exo3_marcadores.json, escrito por tcc_resultados_exo3_marcadores.py, e o verificador os aceita como origem, além do documento longo. O DOCX ficou com 82 páginas (o PDF do LaTeX, com 83). Por fim, você pediu que a Tabela 17 (curva AASM, modelo e torque do peso nos ângulos marcados) saísse e que o exoesqueleto 3 aparecesse em todas as seções do capítulo 4, com a liberdade de escrever mais. Voltaram trechos do documento longo (o fechamento e as poses das Figuras 14C e 14D em 4.1, a conferência de Steiner e o apoio de braço, a verificação do exoesqueleto 3 em 4.3, com a tabela no mesmo formato da do exoesqueleto 1, a tabela dos ângulos marcados em 4.6 e as simplificações em 4.9), e entraram textos novos a partir dos marcadores: a leitura e a conferência dos marcadores (4.2), o ajuste refeito neles e o perfil em x0, que mostra que a curva fixa o nível da força da mola, e não k e x0 separados (4.4, com a tabela de ajustes ampliada), os indicadores do ajuste numa tabela parelha à do exoesqueleto 1, o padrão do resíduo, o patamar e a reprodução da RM (4.5), a força da mola, a tração no cabo e a energia (4.6), as montagens refeitas nos marcadores (4.7) e, em 4.8, a fração do peso sustentada ao longo de Θ, o trabalho na faixa da curva, as poses das Figuras 14C e 14D, a posição de repouso calculada e o efeito da montagem e do alvo do ajuste, com uma figura nova. A verificação do exoesqueleto 2 continua fora, como no seu arquivo. O DOCX ficou com 89 páginas, e o PDF do LaTeX também; o verificador passou a aceitar até 90. Depois, a seu pedido, o título ganhou subtítulo, "torque estático de três exoesqueletos reconstruídos a partir de patentes", na capa e na folha de rosto, e versão em inglês do título e do subtítulo, na folha de rosto ("Modeling of passive arm-support mechanisms: static torque of three exoskeletons reconstructed from patents"); o verificador confere as duas formas no DOCX. Por fim, também a seu pedido, a seção 4.9 foi enxugada a quatro parágrafos, um por exoesqueleto e um comum aos três, com uma frase por ressalva e sem repetir o que as seções 4.1 a 4.8 já dizem; saíram, por exemplo, a explicação do que a conversão para N·m exigiria (está nas sugestões de 5.6) e o detalhe das montagens do came (está em 4.7). Em seguida, a seu pedido, o texto foi podado nos cinco capítulos: a seção 1.2 (Justificativa) virou a última frase do parágrafo que apresenta o trabalho; no capítulo 2, saiu o parágrafo das configurações da Ottobock (repetia 2.3) e foram encurtados os de epidemiologia (repetia a introdução), de dispositivos ativos, de classificação dos exoesqueletos, do artigo de Okabe, Brittes e Brito (2026), da compatibilidade na EP e do shoulderX; nos capítulos 3 a 5, saíram frases que repetiam outra seção ou uma tabela (sinal de θ_b,pose, regra do RMSE, testes sem pytest, peças do CAD que a Tabela 8 já traz, marcadores, patamar, Nasr) e etapas pouco úteis (o ramo espúrio do ponto morto do exoesqueleto 1, o peso do apoio sozinho, as variantes de giro e de montagem do came na Tabela 12, que ficam só em 4.7). O DOCX ficou com 85 páginas (o PDF do LaTeX, com 86). Por fim, dentro do que a NBR 14724 permite, saíram os títulos internos dos capítulos 1 e 5 (os objetivos ficaram no fim da introdução, e a conclusão virou texto corrido, com cerca de metade do tamanho), os capítulos 1 e 2 foram parafraseados para encurtar e, nos capítulos 3 e 4, saíram só trechos inúteis, sem reescrita. O DOCX ficou com 80 páginas (o PDF do LaTeX, com 81). Depois, a seu pedido, a Figura 6 passou a mostrar também a melhor aproximação do exoesqueleto 1, com a pré-tensão e a rigidez reidentificadas (h = 24,0 mm), feita por tcc_resultados_melhor_h.py; o DOCX ficou com 82 páginas e o PDF, com 81. A lista completa está nas pendências (A2). A base é o seu arquivo de 14/11, com as suas quatro alterações.

**Estrutura.** O capítulo 3 tem 11 seções, uma por etapa do procedimento (reconstrução em CAD; parâmetros inerciais; referenciais e convenções; fechamento do circuito e braço de momento, com cada exoesqueleto completo antes do seguinte; elemento elástico, lei da mola e torque; ponto morto; torque gravitacional; trabalhos virtuais; dados da patente e identificação; varredura paramétrica; verificações, ferramentas e delimitação), e cada seção trata os três exoesqueletos em sequência. O capítulo 4 foi fundido do mesmo modo, a seu pedido: nove seções por assunto (geometria e massa; dados extraídos; verificação; parâmetros e identificação; ajuste às curvas; comportamento; varredura; confronto com o torque gravitacional; limitações), com uma abertura só e, em cada seção, os exoesqueletos 1, 2 e 3 em sequência, cada um aberto por "No exoesqueleto n". A seção de verificação detalha só o exoesqueleto 1, porque as dos exoesqueletos 2 e 3 saíram no seu arquivo. A variável independente é q nas três formulações, e a definição do trabalho virtual, δW = 0, aparece nas três (seção 3.8).

## 3. Diagnóstico

A classificação indica o efeito sobre a defesa. "Declarado" quer dizer que o texto já diz o problema com todas as letras e que a banca vai encontrá-lo escrito.

### 3.1 Críticos

| Problema | Onde | Situação |
|---|---|---|
| θ_off = 133,017° e H_CAL = 22,701 mm têm origem não reproduzida; o ajuste de R² = 0,99839 depende deles | 3.9, 4.4, Tabela 9 | Declarado. A revisão reproduziu K e X_pose no h adotado, mas não o procedimento que levou a esses dois valores. Pergunta B1 |
| Os quatro parâmetros do exoesqueleto 1 foram identificados e avaliados nos mesmos 29 pontos | 4.5, 5.2 | Declarado: "não constitui validação independente" |
| A forma do torque do exoesqueleto 2, com a geometria do CAD, não reproduz as curvas da patente (R² de −1,529 a −0,417) | 4.5, 4.9, 5.2 | Declarado, com a causa delimitada (não é o comprimento s) |
| A magnitude do torque depende de hipótese nos três mecanismos: unidade da patente no primeiro, K40 no segundo, AWM igualada ao peso do membro no terceiro | 4.6, 4.8, 5.4 | Declarado. Um parágrafo de 5.5 separa o que depende e o que não depende de escala |
| O título falava em "simulação" e o texto, por decisão sua, é só estático | título, 1.1 | Resolvido: o título passou a "Modelagem de mecanismos passivos de apoio ao braço" na capa e na folha de rosto. Pergunta A1 |

### 3.2 Importantes

| Problema | Onde | Situação |
|---|---|---|
| Duas remissões a "Figura 16" sem dizer de qual patente; na conversão, viravam remissão à figura de mesmo número do próprio TCC | limitações do exo 2 e montagens do exo 3 | Corrigido na versão condensada: "Figura 16 da patente" e "Figura 16 da US 9.737.374 B2" |
| Remissão desatualizada a uma seção de resultados | método do exo 3 | Corrigida na etapa 1; o parágrafo saiu depois, com a etapa dinâmica |
| Comprimento útil do alojamento com dois valores (131,37 mm na tabela, 140,0 mm no texto) | resultados do exo 1 | Como no seu arquivo, a Tabela 1 mantém 131,37 mm e a frase com 140,0 mm saiu; a grandeza não entra em cálculo algum. A dúvida continua valendo para o comentário do código. Pergunta A5 |
| "Nenhum dos dois documentos" numa seção de um trabalho que trata de três patentes | 2.3 | Mantido. Pede redação sua. Pergunta A2 |
| Dois nomes de produto para a mesma patente (Paexo e iX Shoulder Air) | 2.6 e 3.1 | Mantido e ressalvado no texto. Pergunta B4 |
| Método de extração dos pontos das curvas não descrito; incerteza não avaliada | 3.9 | Declarado. Pergunta B2 |
| Critério de escala dos modelos em CAD | 3.1 | Declarado. Pergunta B3 |
| Código "CID M75" atribuído à notícia da Agência Brasil | 1 | Não confirmado na fonte. Pergunta B5 |
| Data da página do IX Shoulder Air citada como "[202-]" num ponto e "[2026]" em outro, no seu arquivo | 3.9 e 4.9 | Uniformizado em "[202-]", como na lista de referências. Pergunta A6 |
| Sua leitura das curvas da Figura 16 da US 9.737.374 B2 com deslocamento de cerca de 6,2 unidades na ordenada | exoesqueleto 3 | Diagnosticado e conferido contra os 27 marcadores de cada curva; o modelo já usa o traçado calibrado, e nenhum número do texto muda. Pergunta B6 |
| e_c = 34,785 mm (exo 2) igual a H_CAD = 34,785 mm (exo 1) | Tabelas 1 e 3 | Coincidência confirmada por você no CAD em 8/11; resposta pronta no roteiro |

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
- **Sinais e convenções.** As três convenções angulares foram conferidas com as figuras e com os códigos. A variável independente é q nas três formulações; o braço de momento é a derivada do caminho do elemento elástico em relação a q, com o sinal de cada caso (seção 3.8).
- **Um erro de texto encontrado e corrigido na base.** A frase que descrevia a variação do vão do cabo de ancoragem no trabalho virtual do exoesqueleto 3 não correspondia ao cálculo; foi reescrita e conferida numericamente (resíduo de 1,2 × 10⁻⁷ mm/rad).
- **Unidades.** O fator 1/1000 das expressões de torque (milímetros para metros) foi conferido nos três modelos. O torque do exoesqueleto 1 está em unidade da patente, e o texto não o apresenta em N·m em nenhum ponto.
- **Composição inercial.** As tabelas de propriedades de massa foram conferidas pela consistência interna (teorema de Steiner e M g d), e não contra a planilha, que não está no repositório.

## 5. Auditoria computacional

- Os três scripts de resultados (`tcc_resultados.py`, `tcc_resultados_ottobock.py` e `tcc_resultados_exo3.py`), executados numa cópia limpa do repositório, reproduzem byte a byte os arquivos `results/*.json` de onde saem os números do texto.
- Os scripts do exoesqueleto 3 que leem as imagens das folhas da patente reproduzem os valores usados no texto.
- A bateria de testes automatizados passa: 47 testes (`python -m pytest -q`), reexecutada ao fim desta entrega.
- Varredura dos números: os 2.059 valores decimais do documento longo foram procurados nos resultados; 2.005 foram encontrados diretamente, e os 54 restantes, que são derivados (somas, diferenças, razões), foram conferidos à mão.

## 6. Conferências da versão para a defesa

Executadas por `tcc/verificar_condensado.py` e pelos verificadores do pipeline, todas sem falha:

| Conferência | Resultado |
|---|---|
| Numeração de seções, tabelas, figuras e equações em sequência; remissões sem destino | 35 títulos, 19 tabelas, 20 figuras e 64 equações em ordem; nenhuma remissão sem destino; nenhuma tabela ou figura sem chamada no texto |
| Proveniência dos números: todo número do texto condensado existe no documento longo | 2.097 números conferidos; nenhum fora do documento longo e do complemento do exoesqueleto 3 (`results/exo3_marcadores.json`) |
| Equações iguais às do documento longo | 64 equações editáveis, idênticas byte a byte |
| Figuras e tabelas | 20 imagens: 17 do documento longo, idênticas a elas, e as 3 do complemento do exoesqueleto 3; nenhuma linha de tabela que não exista no documento longo, fora das 12 tabelas remontadas, conferidas número a número contra a tabela de origem e o complemento, e da tabela nova de indicadores do exoesqueleto 3, cujos números vêm do complemento |
| Termos retirados (MBDyn, Lagrange, etapa dinâmica, equação de movimento, apêndice) | Nenhuma ocorrência, incluídos o resumo e o abstract |
| Travessões no corpo | Nenhum, fora do separador das legendas do texto original |
| Citações e referências | 37 referências, todas citadas; nenhuma citação sem referência |
| DOCX contra o PDF do LaTeX (`verificar_docx_modelo.py`) | Mesmo texto, mesmas equações, tabelas e figuras; sumário e listas com as páginas do próprio DOCX |
| Integridade do pacote DOCX | Abre sem erro; sem comentários nem alterações controladas; equações editáveis, nenhuma em imagem |
| Páginas | 82, da capa ao fim, na conversão pelo LibreOffice (limite de 90, depois da sua liberação de 15/11) |
| Inspeção visual | Todas as 82 páginas renderizadas e olhadas em conjunto, com o preenchimento de cada uma medido: capa, folha de aprovação, resumo, listas, sumário, equações, figuras e tabelas |

## 7. O que saiu

O mapa completo está em `O_que_saiu_e_o_que_ficou.md`. Em resumo:

- **Etapa dinâmica e MBDyn:** dois objetivos específicos, a seção de fundamentação sobre dinâmica multicorpos, as três seções de etapas dinâmicas previstas, a equação de movimento e as frases correspondentes das conclusões, do resumo e do abstract.
- **Apêndice A** (robustez da identificação e ajuste de forma do exoesqueleto 2), inteiro. O texto guarda o essencial nas seções 3.9 e 4.4: as faixas de ângulo testadas, o ruído de 0,5 px em 500 sorteios e o intervalo de 299,81 a 301,95 mm.
- **Seção de verificação do exoesqueleto 2** nos resultados, como no seu arquivo. As verificações continuam descritas na seção 3.11. A do exoesqueleto 3 voltou em 4.3 (Tabela 8), quando você pediu o exoesqueleto 3 em todas as seções.
- **Tabelas:** a das convenções angulares do exoesqueleto 1 (os ângulos continuam definidos no texto da seção 3.3), a tabela-resumo das três formulações, as de pontos extraídos das três patentes, a de zonas de sinal dos resíduos, as de platôs de RMSE e de valores notáveis de h, a de verificações do exoesqueleto 2, a de grandezas do circuito do exoesqueleto 2 por ângulo (os mesmos ângulos estão na Tabela 19), a de curva AASM, modelo e torque do peso do exoesqueleto 3 nos ângulos marcados (a seu pedido; os números estão no texto de 4.8 e nas Figuras 19 e 20), a de comparação entre os três (a comparação está em texto, nas seções 5.2 e 5.4) e as três do apêndice.
- **Figuras:** nenhuma. As quatro que tinham saído (as duas sobreposições do circuito ao desenho da patente, o cenário de projeto do exoesqueleto 2 em gráfico e a figura do ajuste de forma, que era do apêndice) voltaram a seu pedido.
- **Capítulos 1 e 2:** os cortes do seu arquivo, a seção sobre dinâmica multicorpos e frases que repetiam outras (lista em A3 das pendências).
- **Referências:** as que só os trechos retirados citavam e as das bibliotecas NumPy, SciPy e Matplotlib, que continuam nomeadas no texto sem citação (pendência C5).

## 8. Referências e normas

- Todas as 37 referências são citadas, e toda citação tem referência (conferência automática).
- A conferência dos dados bibliográficos pelos DOIs não foi feita: o ambiente bloqueia `api.crossref.org`. Por busca na web, a notícia da Agência Brasil (2026) foi confirmada; o artigo de Okabe, Brittes e Brito (2026) não apareceu na busca.
- O documento segue o modelo LaTeX da FT (classe `tese-FT`), que declara seguir a Instrução Normativa CCPG nº 06/2025, com a identificação da FCA. Não foi encontrado regulamento de TCC específico do curso de Engenharia de Manufatura da FCA, e nenhuma outra norma foi imposta.

## 9. Verificações pendentes

| Pendente | Por quê | Como resolver |
|---|---|---|
| Contagem de páginas no Microsoft Word | O ambiente só tem LibreOffice; o Word pode quebrar linhas de modo diferente | Abrir o DOCX no Word e conferir o total |
| Dados bibliográficos por DOI | Acesso ao Crossref bloqueado | Liberar `api.crossref.org` ou conferir à mão |
| Norma do curso para a monografia | Não localizada | Confirmar com a coordenação ou com o orientador |
| Grandezas "medidas em CAD" | Os arquivos de CAD e a planilha não estão no repositório | Conferir no CAD as Tabelas 1, 3 e 5 |
| Descrições das patentes | O texto das patentes não está no repositório, só as figuras | Conferir 2.3 e 3.1 contra os documentos |

## 10. Como reproduzir

Na raiz do repositório:

```
python3 tcc/gerar_condensado.py --tudo     # conteúdo, LaTeX, PDF e DOCX no formato FT (cerca de 10 minutos)
python3 tcc/verificar_condensado.py        # conferências da seção 6 e mapa do que saiu
python3 -m pytest -q                       # testes dos modelos
```

Para mudar o que fica e o que sai, edite `tcc/condensado_defesa.py`: cada linha do plano mantém um bloco (`K`), troca um trecho (`E`), reescreve uma legenda ou nota (`R`), corta linhas de uma tabela (`L`) ou põe um parágrafo novo (`P`). A numeração de seções, tabelas, figuras e equações é refeita sozinha, e o verificador acusa qualquer número que não exista no documento longo.
