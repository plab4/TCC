# Reporte de Produção e Consumo de Materiais

Aplicação web estática (HTML5 + CSS3 + JavaScript + SheetJS) para reportar a produção de uma campanha e o consumo de matérias-primas e embalagens, comparando o consumo real com o consumo teórico e com a perda contratual registrada na planilha.

Todo o processamento acontece no navegador. Não há backend, banco de dados, API externa, upload, telemetria ou analytics.

## Estrutura

```
reporte-consumo/
├── index.html               interface
├── styles.css               estilos (inclui layout de impressão/PDF)
├── app.js                   configuração, leitura da planilha, cálculos, interface e exportação
├── lib/
│   └── xlsx.full.min.js     SheetJS (cópia local, funciona sem internet)
├── tests/
│   └── calculations.test.js testes automatizados (Node.js)
└── README.md
```

A configuração fica no início do `app.js`:

```js
const OCULTAR_CODIGOS_PRODUTOS = true;
```

Com `true`, os códigos dos produtos viram `PRD-001`, `PRD-002`… e os das apresentações viram `PRD-001.1`, `PRD-001.2`… Com `false`, são exibidos os códigos da planilha (códigos separados por `/`, `,`, `;` ou quebra de linha são reconhecidos).

## Como executar

1. Abra `index.html` direto no navegador (Chrome, Edge ou Firefox): duplo clique ou arraste o arquivo para o navegador. Não é preciso servidor.
   - Se preferir um servidor local: `python3 -m http.server 8000` dentro da pasta `reporte-consumo` e acesse `http://localhost:8000`.
2. Clique em **Carregar planilha Excel (.xlsx)** e escolha o arquivo. Para testar sem planilha, use **Usar dados de demonstração**.
3. Selecione o produto (`Produto 1`, `Produto 2`…).
4. Preencha a data, a quantidade formulada, a unidade (KG/L) e o total envasado. Se houver mais de uma apresentação, informe a quantidade de cada uma.
5. Confira ou informe os volumes-base em **Parâmetros de cálculo**.
6. Informe o consumo real de cada material. Os desvios são marcados automaticamente e abrem o registro de justificativa.
7. Quando não houver erros críticos em **Validações**, exporte para Excel ou CSV, ou imprima/salve em PDF.

### Testes

Requer Node.js 18 ou superior:

```bash
cd reporte-consumo
node --test tests/calculations.test.js
```

## Como a planilha é interpretada

- **Escolha da aba:** todas as abas são analisadas. Uma aba é compatível quando o cabeçalho tem campos equivalentes a *produto*, *matéria-prima/embalagem* e *usagem da Lista Técnica*. A aba com mais linhas de material é sugerida. Quando há mais de uma aba compatível, aparece um seletor.
- **Cabeçalho:** procurado nas primeiras 40 linhas, com uma ou duas linhas de cabeçalho. Os rótulos são normalizados (sem acentos, sem quebras de linha, sem caixa alta, sem pontuação), e cada coluna é reconhecida por sinônimos, não por posição: produto, código, quantidade produzida/formulada, envasada, diferença, código do insumo, descrição, usagem da Lista Técnica, usagem teórica, unidade, teor, quantidade usada, variação, perda contratual, excedente, observações e análise pós-justificativa.
- **Blocos de produto:** são formados pelas células mescladas (ou repetidas) da coluna de produto. Cada bloco é classificado como:
  - *granel/formulação*: rótulo com "granel" ou "bulk", ou célula de quantidade envasada com fórmula que soma outros blocos;
  - *apresentação*: rótulo com "apresentação", formato do tipo `10x1 KG` ou `20 L`, ou bloco só com embalagens;
  - *reenvase*: rótulo com "reenvase" ou "reembalagem".
- **Vínculo apresentação → produto:** pela fórmula do total envasado do granel (por exemplo, `=D7+D16`). Uma apresentação fora dessa fórmula é vinculada pela posição e gera pendência para revisão.
- **Vínculo material → escopo e volume-base:** lidos da fórmula da usagem teórica. Exemplo: `=I3*$D$3/10000` indica a linha de referência (D3) e o volume-base (10.000). Se o divisor estiver em outra célula, o valor dessa célula é usado. Sem fórmula, também é aceita uma coluna de volume-base. **Quando o volume-base não é encontrado, nada é inventado:** o material fica *Pendente* e o valor é pedido em Parâmetros.
- **Números:** aceita `2000`, `2.000`, `2.000,00`, `2008,03`, `1.310,480`, `0,02`, `0.02`, `2%`, notação científica e números gravados como texto. Perdas gravadas como `2` (sem `%`) são lidas como 2% e geram aviso.
- **Valores já preenchidos** na planilha (quantidades, consumo real) entram como preenchimento inicial. Fórmulas que resultam em zero (modelo vazio) são ignoradas.
- Tudo o que não puder ser interpretado vai para **Pendências de importação**.

## Regras de cálculo

| Item | Fórmula |
|---|---|
| Matéria-prima | `consumo_teorico = usagem_LT × quantidade_formulada ÷ volume_base_formulação` |
| Embalagem | `consumo_teorico = usagem_LT × quantidade_envasada_apresentação ÷ volume_base_apresentação` |
| Limite inferior | `consumo_teorico` |
| Limite máximo | `consumo_teorico × (1 + perda_contratual)` |
| Variação | `(consumo_real − consumo_teorico) ÷ consumo_teorico` |
| Excedente | `consumo_real − limite_máximo` (zero quando ≤ 0) |
| Diferença de produção | `formulado − envasado` |

Status:
- **Dentro do esperado:** teórico ≤ real ≤ limite máximo.
- **Consumo abaixo do teórico:** real < teórico.
- **Consumo acima do contrato:** real > limite máximo.
- **Pendente:** faltam dados ou há inconsistência (volume-base, quantidade, perda, consumo real, unidade incompatível, vínculo).

Nos dois casos de desvio, "Houve consumo fora da especificação?" é marcado como **Sim** automaticamente. Motivo, descrição da ocorrência e ação imediata passam a ser obrigatórios (responsável e prazo também, se houver investigação). O usuário pode marcar "Sim" manualmente para itens dentro do esperado, e a mesma obrigatoriedade passa a valer.

A categoria (matéria-prima, ingrediente ativo, embalagem primária/secundária, rótulo, tampa, caixa, pallet, material auxiliar, não classificado) é sugerida por palavras-chave e pode ser alterada. Uma embalagem que esteja no bloco de formulação aparece como **"Material com vínculo pendente de revisão"** até ser ligada a uma apresentação ou ao total envasado.

O **teor** do ingrediente ativo aparece apenas como informação. Nenhuma correção de teor é aplicada.

## Validações que bloqueiam a exportação

- data do reporte ausente; quantidade formulada ou envasada ausente, inválida ou negativa; unidade da formulação não selecionada;
- diferença formulado − envasado sem justificativa;
- soma das apresentações diferente do total envasado, sem correção ou justificativa;
- consumo real inválido ou negativo; unidade do consumo incompatível (KG×L, por exemplo; G→KG e ML→L são convertidos);
- perda contratual fora do intervalo de 0% a 100%;
- volume-base informado ≤ 0;
- desvio sem justificativa completa.

Não bloqueiam, mas aparecem como avisos: materiais pendentes, sem volume-base, sem perda, duplicados, com vínculo pendente, e apresentações sem materiais ou vinculadas pela posição.

As mensagens aparecem na própria página (sem `alert()`).

## Exportação

- **Excel** (`reporte_Produto_1_AAAA-MM.xlsx`, com AAAA-MM vindo da data do reporte), com três abas:
  - *Resumo*: produto e código anonimizados, data, quantidades, diferença e justificativa, apresentações, totais por status e observações;
  - *Consumo de Materiais*: código, descrição, categoria, unidade, teórico, perda, limite, real, variação, excedente, status, justificativa, ação, responsável e prazo;
  - *Parâmetros*: identificador, volumes-base, unidades, regras aplicadas e pendências de importação.
- **CSV** (`;` como separador, vírgula decimal, UTF-8 com BOM para abrir corretamente no Excel em português), com as mesmas três seções.
- **Imprimir ou salvar em PDF**: layout de impressão em A4 paisagem, com os detalhes das justificativas abertos.

## Confidencialidade

- Produtos aparecem como `Produto 1`, `Produto 2`…, numerados na ordem em que surgem na planilha. Apresentações aparecem como `Apresentação 1`, `Apresentação 2`… do produto. Só o formato da embalagem (ex.: `10X1 KG`) é extraído do rótulo original.
- A associação entre o nome real e o identificador existe apenas em variáveis locais durante a leitura da aba. Nomes reais não entram no modelo de dados, na interface, nos atributos HTML, no console, nos arquivos exportados nem nos nomes de arquivos.
- Se o nome de um produto aparecer dentro de outro texto (descrição de rótulo, nome da aba, análise), ele é substituído pelo identificador anônimo.
- Nada é gravado em `localStorage`, `sessionStorage`, IndexedDB ou cookies. Recarregar a página apaga todo o preenchimento.
- A planilha original só é lida, nunca alterada.

## Biblioteca SheetJS

O arquivo `lib/xlsx.full.min.js` incluído é o build oficial **SheetJS 0.18.5**, do pacote `xlsx` no registro npm. É a versão mais recente publicada pela SheetJS no npm.

Se o arquivo local não existir, `index.html` carrega automaticamente o CDN oficial (`https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js`). Isso exige internet.

**Recomendado:** trocar a cópia local pela versão 0.20.3 (ou mais nova), que corrige vulnerabilidades conhecidas da 0.18.5 na leitura de arquivos maliciosos (CVE-2023-30533 e CVE-2024-22363):

1. Baixe `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js`;
2. Salve o arquivo como `reporte-consumo/lib/xlsx.full.min.js`, substituindo o atual;
3. Recarregue a página. Não há outra alteração a fazer.

O risco da 0.18.5 se limita a abrir planilhas de origem não confiável. Neste uso, a planilha é do próprio usuário e o processamento é local.

## Limitações conhecidas

- Um texto como `2.000` (ponto seguido de exatamente três dígitos) é lido como milhar (2000), seguindo o padrão brasileiro. Valores numéricos gravados como número no Excel não têm essa ambiguidade.
- A classificação de blocos e categorias usa palavras-chave em português. Planilhas com outra nomenclatura podem exigir ajuste manual de categoria ou de vínculo.
- O volume-base é detectado pela fórmula da usagem teórica (ou por uma coluna de volume-base). Planilhas só com valores, sem fórmula nem coluna de base, exigem preenchimento manual em Parâmetros.
- O modelo de planilha calcula a usagem teórica das matérias-primas sobre o **total envasado**. Esta aplicação segue a regra definida para o reporte: matérias-primas sobre a **quantidade formulada** e embalagens sobre o envasado da apresentação.
- Os códigos de insumo do modelo vêm de `RANDBETWEEN` e mudam a cada recálculo no Excel. A aplicação usa o valor gravado no arquivo e registra um aviso.
- O preenchimento não é salvo entre sessões, por causa da regra de não persistir dados. Exporte antes de fechar a página.
