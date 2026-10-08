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
├── reporte-consumo-completo.html  versão em arquivo único (gerada)
├── build-arquivo-unico.js   gera a versão em arquivo único
└── README.md
```

A configuração fica no início do `app.js`:

```js
const ANONIMIZAR_PRODUTOS = false;
const OCULTAR_CODIGOS_PRODUTOS = false;
```

Por padrão, os nomes e códigos dos produtos e das apresentações aparecem exatamente como estão na planilha. Códigos separados por `/`, `,`, `;` ou quebra de linha são reconhecidos. Um granel sem código próprio mostra os códigos das suas apresentações.

As duas opções só servem para compartilhar o reporte sem identificar os produtos:
- `ANONIMIZAR_PRODUTOS = true` troca os nomes por `Produto 1`, `Produto 2`… e `Apresentação 1`, `Apresentação 2`…, na ordem em que aparecem na planilha. O nome real também é mascarado dentro de outros textos (descrição de rótulo, nome da aba).
- `OCULTAR_CODIGOS_PRODUTOS = true` troca os códigos por `PRD-001`, `PRD-002`… e `PRD-001.1`, `PRD-001.2`…

## Como executar

1. Abra a aplicação no navegador (Chrome, Edge, Firefox ou Safari 14+). Não é preciso servidor nem internet. Há duas formas:
   - **Mais simples:** dê duplo clique em `reporte-consumo-completo.html`. É um único arquivo com tudo embutido (interface, estilos, SheetJS e código), que funciona sozinho, inclusive copiado para outra pasta ou enviado por e-mail.
   - **Pasta completa:** abra `index.html` **de dentro da pasta `reporte-consumo`**, com `app.js`, `styles.css` e `lib/` ao lado. Se baixou um .zip, extraia antes de abrir.
   - Se preferir um servidor local: `python3 -m http.server 8000` dentro da pasta `reporte-consumo` e acesse `http://localhost:8000`.
2. Clique em **Carregar planilha Excel (.xlsx)** e escolha o arquivo. Para testar sem planilha, use **Usar dados de demonstração**.
3. Selecione o produto (o bulk, com todas as matérias-primas). Os nomes aparecem como estão na planilha.
4. Em **Apresentações produzidas**, marque as apresentações que foram envasadas. Pode marcar mais de uma; se o produto tiver uma só, ela já vem marcada. Só as embalagens das apresentações marcadas entram no reporte.
5. Em **Produção do produto (bulk)**, preencha a data, a quantidade formulada, a unidade (KG/L) e o total envasado.
6. Em **Produção por apresentação**, informe quanto foi envasado em cada apresentação marcada. A soma tem de ser igual ao total envasado; enquanto não for, a exportação fica bloqueada.
7. Confira ou informe os volumes-base em **Parâmetros de cálculo**.
8. Informe o consumo real de cada material. Os desvios são marcados automaticamente e abrem o registro de justificativa.
9. Quando não houver erros críticos em **Validações**, exporte para Excel ou CSV, ou imprima/salve em PDF.

### Se nada acontecer ao clicar nos botões

- **Aparece "A aplicação não foi carregada…":** o `index.html` foi aberto sem o `app.js` ao lado. Isso acontece quando só o HTML foi baixado, quando ele é aberto de dentro de um .zip ou pelo painel de visualização de outro aplicativo. Use `reporte-consumo-completo.html` ou abra a partir da pasta completa.
- **Aparece "Biblioteca SheetJS não carregada…":** falta `lib/xlsx.full.min.js`. A demonstração e o CSV continuam funcionando, mas a importação de .xlsx e a exportação para Excel ficam desativadas até o arquivo ser restaurado.
- **Aparece "Erro ao iniciar a aplicação…":** o navegador é antigo demais. Atualize-o ou use Chrome/Edge.

### Versão em arquivo único

Depois de alterar `index.html`, `styles.css`, `app.js` ou a biblioteca, gere de novo o arquivo único:

```bash
cd reporte-consumo
node build-arquivo-unico.js
```

### Testes

Requer Node.js 18 ou superior:

```bash
cd reporte-consumo
node --test tests/calculations.test.js
```

## Como a planilha é interpretada

- **Escolha da aba:** todas as abas são analisadas. Uma aba é compatível quando o cabeçalho tem campos equivalentes a *produto*, *matéria-prima/embalagem* e *usagem da Lista Técnica*. A aba com mais linhas de material é sugerida. Quando há mais de uma aba compatível, aparece um seletor.
- **Cabeçalho:** procurado nas primeiras 40 linhas, com uma ou duas linhas de cabeçalho. Os rótulos são normalizados (sem acentos, sem quebras de linha, sem caixa alta, sem pontuação), e cada coluna é reconhecida por sinônimos, não por posição: produto, código, quantidade produzida/formulada, envasada, diferença, código do insumo, descrição, usagem da Lista Técnica, usagem teórica, unidade, teor, quantidade usada, variação, perda contratual, excedente, observações e análise pós-justificativa.
- **Produto (bulk) x apresentação:** na planilha os dois ficam na mesma coluna. O produto é o bloco que contém o bulk, ou seja, todas as matérias-primas. Ele é reconhecido por qualquer um destes sinais:
  - "granel" ou "bulk" no nome;
  - mais de um código na célula (ex.: `4058009029, 4058021472`);
  - fórmula do total envasado somando outras apresentações;
  - cor de fundo diferente do branco das apresentações (ex.: a célula bege do granel).

  Todos os produtos aparecem na lista, inclusive os que ainda não têm quantidades. Nome e código são os da planilha.
- **Apresentações:** todos os demais blocos (ex.: `Produto X,24X0,25 L,MX`) são apresentações (envases) de um produto. O vínculo vem da fórmula do total envasado do produto (por exemplo, `=D7+D16`). Sem essa fórmula, a apresentação é ligada ao produto imediatamente acima (ou abaixo, se não houver produto antes) e uma pendência pede revisão.
- **Planilha sem nenhum produto reconhecido:** cada bloco vira um produto, com aviso nas pendências.
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
| Diferença de produção | `formulado − envasado` e `% = diferença ÷ formulado` |

A justificativa da diferença entre formulado e envasado só é pedida (e exigida) quando a diferença for de **10% ou mais** do formulado, em qualquer sentido. Abaixo disso, o campo não aparece. O limite fica em `LIMITE_DIFERENCA_FORMULADO_ENVASADO`, no topo do `app.js`.

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
- diferença formulado − envasado de 10% ou mais sem justificativa;
- nenhuma apresentação marcada, apresentação marcada sem quantidade, ou soma das apresentações diferente do total envasado;
- consumo real inválido ou negativo; unidade do consumo incompatível (KG×L, por exemplo; G→KG e ML→L são convertidos);
- perda contratual fora do intervalo de 0% a 100%;
- volume-base informado ≤ 0;
- desvio sem justificativa completa.

Não bloqueiam, mas aparecem como avisos: materiais pendentes, sem volume-base, sem perda, duplicados, com vínculo pendente, e apresentações sem materiais ou vinculadas pela posição.

As mensagens aparecem na própria página (sem `alert()`).

## Exportação

- **Excel** (`reporte_<nome do produto>_AAAA-MM.xlsx`, por exemplo `reporte_GRANEL_1_2026-10.xlsx`; espaços viram `_`, caracteres inválidos em nomes de arquivo são removidos e AAAA-MM vem da data do reporte), com três abas:
  - *Resumo*: produto e código, data, quantidades, diferença e justificativa, apresentações, totais por status e observações;
  - *Consumo de Materiais*: código, descrição, categoria, unidade, teórico, perda, limite, real, variação, excedente, status, justificativa, ação, responsável e prazo;
  - *Parâmetros*: identificador, volumes-base, unidades, regras aplicadas e pendências de importação.
- **CSV** (`;` como separador, vírgula decimal, UTF-8 com BOM para abrir corretamente no Excel em português), com as mesmas três seções.
- **Imprimir ou salvar em PDF**: layout de impressão em A4 paisagem, com os detalhes das justificativas abertos.

## Privacidade dos dados

- Os dados da planilha ficam só na memória do navegador. Nada é enviado para servidores.
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
