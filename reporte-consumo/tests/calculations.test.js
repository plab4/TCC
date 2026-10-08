'use strict';
// Executar com: node --test tests/   (ou: node tests/calculations.test.js)
// Todos os dados usados aqui são fictícios.

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

const app = require(path.join(__dirname, '..', 'app.js'));
const XLSX = require(path.join(__dirname, '..', 'lib', 'xlsx.full.min.js'));

const { STATUS } = app;
const perto = (atual, esperado, msg) => assert.ok(Math.abs(atual - esperado) < 1e-9, `${msg || ''} esperado ${esperado}, obtido ${atual}`);

/* ------------------------------------------------------------------ */
/* Testes obrigatórios                                                 */
/* ------------------------------------------------------------------ */

test('Teste 1 — 100 KG teórico, perda 2%, real 101 KG → Dentro do esperado', () => {
  const r = app.avaliarConsumo({ teorico: 100, perda: 0.02, real: 101 });
  assert.equal(r.status, STATUS.DENTRO);
  perto(r.limiteSuperior, 102);
  assert.equal(r.excedente, 0);
  perto(r.variacao, 0.01);
  assert.equal(app.exigeJustificativa(r.status, 'Não'), false);
});

test('Teste 2 — 100 KG teórico, perda 2%, real 105 KG → limite 102, excedente 3, acima do contrato', () => {
  const r = app.avaliarConsumo({ teorico: 100, perda: 0.02, real: 105 });
  perto(r.limiteSuperior, 102, 'limite máximo');
  perto(r.excedente, 3, 'excedente');
  assert.equal(r.status, STATUS.ACIMA);
  assert.equal(app.exigeJustificativa(r.status, 'Não'), true);
});

test('Teste 3 — 100 KG teórico, real 98 KG → abaixo do teórico e justificativa obrigatória', () => {
  const r = app.avaliarConsumo({ teorico: 100, perda: 0.02, real: 98 });
  assert.equal(r.status, STATUS.ABAIXO);
  assert.equal(r.excedente, 0);
  perto(r.variacao, -0.02);
  assert.equal(app.exigeJustificativa(r.status, 'Não'), true);
});

test('Teste 4 — formulado 18.000 L, envasado 17.660 L → diferença 340 L com justificativa obrigatória', () => {
  const formulado = app.interpretarNumero('18.000');
  const envasado = app.interpretarNumero('17.660');
  const r = app.calcularDiferencaProducao(formulado, envasado);
  perto(r.diferenca, 340);
  assert.equal(r.exigeJustificativa, true);
  assert.equal(app.calcularDiferencaProducao(18000, 18000).exigeJustificativa, false);
});

test('Teste 5 — conversão de números brasileiros e internacionais', () => {
  assert.equal(app.interpretarNumero('2.000,00'), 2000);
  assert.equal(app.interpretarNumero('1.310,480'), 1310.48);
  assert.equal(app.interpretarNumero('0,02'), 0.02);
  assert.equal(app.interpretarNumero('2%'), 0.02);
});

/* ------------------------------------------------------------------ */
/* Testes complementares                                               */
/* ------------------------------------------------------------------ */

test('Conversão numérica — demais formatos', () => {
  assert.equal(app.interpretarNumero('2000'), 2000);
  assert.equal(app.interpretarNumero('2.000'), 2000);
  assert.equal(app.interpretarNumero('2008,03'), 2008.03);
  assert.equal(app.interpretarNumero('0.02'), 0.02);
  assert.equal(app.interpretarNumero('1,5e3'), 1500);
  assert.equal(app.interpretarNumero('2.5E-2'), 0.025);
  assert.equal(app.interpretarNumero('1,234.56'), 1234.56);
  assert.equal(app.interpretarNumero(' 500 KG '), 500);
  assert.equal(app.interpretarNumero('-3,5'), -3.5);
  assert.equal(app.interpretarNumero(12.5), 12.5);
  assert.equal(app.interpretarNumero('abc'), null);
  assert.equal(app.interpretarNumero(''), null);
  assert.equal(app.interpretarNumero('#DIV/0!'), null);
  assert.equal(app.interpretarNumero(NaN), null);
  assert.equal(app.interpretarNumero(Infinity), null);
  assert.equal(app.interpretarNumero('1.2.3,4'), null);
});

test('Percentual de perda: 0.02, "2%", "0,02" e 2 (pontos percentuais)', () => {
  assert.equal(app.interpretarPercentual(0.02).valor, 0.02);
  assert.equal(app.interpretarPercentual('2%').valor, 0.02);
  assert.equal(app.interpretarPercentual('0,02').valor, 0.02);
  const p = app.interpretarPercentual(2);
  assert.equal(p.valor, 0.02);
  assert.ok(p.nota);
});

test('Exibição pt-BR: milhar com ponto, decimal com vírgula, percentual com 2 casas', () => {
  assert.equal(app.formatarNumero(1310.48), '1.310,48');
  assert.equal(app.formatarNumero(18000), '18.000');
  assert.equal(app.formatarPercentual(0.02), '2,00%');
  assert.equal(app.formatarPercentual(-0.0123), '-1,23%');
  assert.equal(app.formatarNumero(NaN), '—');
});

test('Consumo teórico de matéria-prima: 500 KG / 10.000 L × 18.000 L = 900 KG', () => {
  const r = app.calcularConsumoTeorico(500, 18000, 10000);
  assert.equal(r.valor, 900);
  assert.equal(r.motivo, null);
});

test('Consumo teórico de embalagem usa a quantidade envasada da apresentação', () => {
  // 50 PC por 1.000 L envasados; 17.660 L envasados → 883 PC
  assert.equal(app.calcularConsumoTeorico(50, 17660, 1000).valor, 883);
});

test('Proteções: divisão por zero, campos vazios, negativos, NaN e Infinity', () => {
  assert.equal(app.calcularConsumoTeorico(500, 18000, 0).valor, null);
  assert.equal(app.calcularConsumoTeorico(500, 18000, null).valor, null);
  assert.equal(app.calcularConsumoTeorico(500, null, 10000).valor, null);
  assert.equal(app.calcularConsumoTeorico(NaN, 18000, 10000).valor, null);
  assert.equal(app.calcularConsumoTeorico(500, Infinity, 10000).valor, null);
  assert.equal(app.calcularConsumoTeorico(-1, 18000, 10000).valor, null);
  assert.equal(app.avaliarConsumo({ teorico: 100, perda: 0.02, real: null }).status, STATUS.PENDENTE);
  assert.equal(app.avaliarConsumo({ teorico: 100, perda: 0.02, real: -1 }).status, STATUS.PENDENTE);
  assert.equal(app.avaliarConsumo({ teorico: 100, perda: 1.5, real: 100 }).status, STATUS.PENDENTE);
  assert.equal(app.avaliarConsumo({ teorico: 100, perda: null, real: 100 }).status, STATUS.PENDENTE);
  assert.equal(app.avaliarConsumo({ teorico: null, perda: 0.02, real: 100 }).status, STATUS.PENDENTE);
  assert.equal(app.avaliarConsumo({ teorico: 100, perda: 0.02, real: 100, unidadeCompativel: false }).status, STATUS.PENDENTE);
  const zero = app.avaliarConsumo({ teorico: 0, perda: 0.02, real: 5 });
  assert.equal(zero.status, STATUS.ACIMA);
  assert.equal(zero.variacao, null);
  assert.equal(app.calcularDiferencaProducao(-1, 10).diferenca, null);
});

test('Limites exatos: real = teórico e real = limite máximo ficam dentro do esperado', () => {
  assert.equal(app.avaliarConsumo({ teorico: 100, perda: 0.02, real: 100 }).status, STATUS.DENTRO);
  assert.equal(app.avaliarConsumo({ teorico: 100, perda: 0.02, real: 102 }).status, STATUS.DENTRO);
  assert.equal(app.avaliarConsumo({ teorico: 100, perda: 0.02, real: 102.0001 }).status, STATUS.ACIMA);
});

test('Marcação manual "Sim" exige justificativa mesmo dentro do esperado', () => {
  assert.equal(app.exigeJustificativa(STATUS.DENTRO, 'Sim'), true);
  assert.equal(app.exigeJustificativa(STATUS.PENDENTE, 'Não'), false);
});

test('Unidades: compatibilidade e conversão', () => {
  assert.equal(app.normalizarUnidade('Kg'), 'KG');
  assert.equal(app.normalizarUnidade('Lt'), 'L');
  assert.equal(app.normalizarUnidade('pç'), 'PC');
  assert.equal(app.unidadesCompativeis('KG', 'G'), true);
  assert.equal(app.unidadesCompativeis('KG', 'L'), false);
  assert.equal(app.unidadesCompativeis('PC', 'UN'), true);
  assert.equal(app.converterUnidade(1500, 'G', 'KG'), 1.5);
  assert.equal(app.converterUnidade(10, 'KG', 'L'), null);
});

test('Classificação sugerida por palavras-chave', () => {
  assert.equal(app.classificarMaterial('Rótulo frontal 1L', 'apresentacao'), 'Rótulo');
  assert.equal(app.classificarMaterial('Tampa rosca 38mm', 'apresentacao'), 'Tampa');
  assert.equal(app.classificarMaterial('Caixa de papelão', 'apresentacao'), 'Caixa');
  assert.equal(app.classificarMaterial('Pallet PBR', 'apresentacao'), 'Pallet');
  assert.equal(app.classificarMaterial('Frasco 1L', 'apresentacao'), 'Embalagem primária');
  assert.equal(app.classificarMaterial('Filme stretch', 'apresentacao'), 'Material auxiliar');
  assert.equal(app.classificarMaterial('IA 1', 'formulacao'), 'Ingrediente ativo');
  assert.equal(app.classificarMaterial('Matéria-prima Alfa', 'formulacao'), 'Matéria-prima');
  assert.equal(app.classificarMaterial('Embalagem A', 'apresentacao'), 'Embalagem primária');
  assert.equal(app.classificarMaterial('Item genérico', 'apresentacao'), 'Não classificado');
});

test('Fórmula da usagem teórica: extrai volume-base e linha de referência', () => {
  const colunas = { qtdFormulada: 2, qtdEnvasada: 3 };
  const leitorFalso = { bruta: () => null };
  const r = app.analisarFormulaTeorica('I3*$D$3/10000', colunas, leitorFalso);
  assert.equal(r.base, 10000);
  assert.equal(r.linhaRef, 2);
  const r2 = app.analisarFormulaTeorica('(I7*$D$7)/300', colunas, leitorFalso);
  assert.equal(r2.base, 300);
  assert.equal(r2.linhaRef, 6);
});

/* ------------------------------------------------------------------ */
/* Importação, nomes dos produtos e exportação (planilhas fictícias)   */
/* ------------------------------------------------------------------ */

test('Demonstração: importação, cálculo completo e status esperados', () => {
  const wb = app.criarPastaDemonstracao();
  const analise = app.analisarPasta(wb);
  const modelo = app.interpretarAba(wb, analise.sugerida);
  assert.equal(modelo.produtos.length, 1);
  const p = modelo.produtos[0];
  assert.equal(p.nome, 'Produto 1');
  assert.equal(p.codigo, 'DEMO-000');
  assert.equal(p.apresentacoes.length, 1);
  assert.equal(p.baseFormulacaoDetectada, 10000);
  assert.equal(p.apresentacoes[0].baseDetectada, 1000);
  assert.deepEqual(p.materiais.map((m) => m.codigo), ['MP-001', 'MP-002', 'EMB-001']);

  const form = app.criarFormularioVazio(p, true);
  form.data = '2026-03-15';
  form.unidade = 'L';
  const rep = app.calcularReporte(p, form);
  perto(rep.diferenca, 340);
  const [alfa, beta, emb] = rep.linhas;
  assert.equal(alfa.teorico, 900);
  assert.equal(alfa.status, STATUS.DENTRO);
  perto(beta.teorico, 115.2);
  assert.equal(beta.status, STATUS.ACIMA);
  perto(beta.excedente, 120 - 115.2 * 1.01);
  assert.equal(emb.teorico, 883);
  assert.equal(emb.status, STATUS.ABAIXO);
  assert.equal(rep.podeExportar, false, 'deve bloquear: justificativas pendentes');

  form.justificativaDiferenca = 'Perda de linha no envase.';
  for (const l of [beta, emb]) {
    Object.assign(form.materiais[l.id], { motivo: 'Perda de processo', descricao: 'Ocorrência fictícia', acao: 'Ajuste fictício' });
  }
  const rep2 = app.calcularReporte(p, form);
  assert.deepEqual(rep2.erros, []);
  assert.equal(rep2.podeExportar, true);
  assert.equal(app.nomeArquivoReporte(p, form.data, 'xlsx'), 'reporte_Produto_1_2026-03.xlsx');
});

test('Validações: valores negativos e unidade incompatível', () => {
  const wb = app.criarPastaDemonstracao(XLSX);
  const p = app.interpretarAba(wb, wb.SheetNames[0]).produtos[0];
  const form = app.criarFormularioVazio(p, false);
  form.data = '2026-03-15';
  form.unidade = 'L';
  form.formulado = '-5';
  form.envasado = '100';
  form.materiais[p.materiais[0].id].real = '10';
  form.materiais[p.materiais[0].id].unidadeReal = 'L';
  const rep = app.calcularReporte(p, form);
  assert.ok(rep.erros.some((e) => /não pode ser negativo/.test(e)));
  assert.ok(rep.erros.some((e) => /incompatível/.test(e)));
  assert.equal(rep.podeExportar, false);
});

test('Apresentações: soma diferente do total envasado bloqueia até corrigir ou justificar', () => {
  const p = app.interpretarAba(planilhaFicticiaComNomes(), 'ZETAMAX').produtos[0];
  const form = app.criarFormularioVazio(p, false);
  Object.assign(form, { data: '2026-03-15', unidade: 'L', formulado: '15.000', envasado: '15.000' });
  form.apresentacoes[p.apresentacoes[0].id] = '10.000';
  form.apresentacoes[p.apresentacoes[1].id] = '4.000';
  let rep = app.calcularReporte(p, form);
  assert.equal(rep.somaApresentacoes, 14000);
  assert.equal(rep.diferencaApresentacoes, 1000);
  assert.equal(rep.divergenciaApresentacoes, true);
  assert.ok(rep.erros.some((e) => /soma das apresentações/.test(e)));
  form.justificativaApresentacoes = 'Justificativa fictícia.';
  rep = app.calcularReporte(p, form);
  assert.ok(!rep.erros.some((e) => /soma das apresentações/.test(e)));
  form.justificativaApresentacoes = '';
  form.apresentacoes[p.apresentacoes[1].id] = '5.000';
  rep = app.calcularReporte(p, form);
  assert.equal(rep.divergenciaApresentacoes, false);
  // Embalagem da apresentação 2: 2.000 PC / 10.000 L × 5.000 L = 1.000 PC
  assert.equal(rep.linhas.find((l) => l.codigo === 'EMB-002').teorico, 1000);
});

function planilhaFicticiaComNomes() {
  // Nomes comerciais inventados apenas para os testes.
  const f = (formula) => ({ t: 'n', v: 0, f: formula });
  const linhas = [
    ['Produto', 'Código', 'Quantidade produzida', 'Quantidade envasada', 'Código dos insumos', 'Matérias primas e embalagens',
      'Usagens indicadas na Lista Técnica', 'Usagem Teórica', 'Un.', 'Qtd usada em produção', 'Un.', 'Perdas estabelecidas em contrato (%)'],
    ['ZETAMAX GRANEL', '111111/222222', null, f('D4+D5'), 'MP-001', 'Matéria-prima Alfa', 500, f('G2*$D$2/10000'), 'KG', null, 'KG', 0.02],
    [null, null, null, null, 'MP-002', 'Matéria-prima Beta', '64,5', f('G3*$D$2/10000'), 'KG', null, 'KG', '1%'],
    ['ZETAMAX 10x1 L', '111111', null, null, 'EMB-001', 'Rótulo ZETAMAX 1 L', 10000, f('G4*$D$4/10000'), 'PC', null, 'PC', 0.02],
    ['ZETAMAX 4x5 L', '222222', null, null, 'EMB-002', 'Embalagem A', 2000, f('G5*$D$5/10000'), 'PC', null, 'PC', 0.05],
    ['OMEGAPLUS REENVASE 20 L', '333333', null, null, 'EMB-003', 'Embalagem A', 500, f('G6*$D$6/10000'), 'PC', null, 'PC', 0.05],
  ];
  const ws = XLSX.utils.aoa_to_sheet(linhas);
  ws['!merges'] = [{ s: { r: 1, c: 0 }, e: { r: 2, c: 0 } }, { s: { r: 1, c: 3 }, e: { r: 2, c: 3 } }];
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'ZETAMAX');
  return wb;
}

test('Padrão: nomes e códigos reais dos produtos aparecem no modelo, na exportação e no nome do arquivo', () => {
  assert.equal(app.ANONIMIZAR_PRODUTOS, false);
  assert.equal(app.OCULTAR_CODIGOS_PRODUTOS, false);
  const wb = planilhaFicticiaComNomes();
  const modelo = app.interpretarAba(wb, app.analisarPasta(wb).sugerida);
  assert.deepEqual(modelo.produtos.map((p) => p.nome), ['ZETAMAX GRANEL', 'OMEGAPLUS REENVASE 20 L']);
  assert.deepEqual(modelo.produtos.map((p) => p.codigo), ['111111 / 222222', '333333']);
  const p1 = modelo.produtos[0];
  assert.deepEqual(p1.apresentacoes.map((a) => [a.nome, a.codigo]), [
    ['ZETAMAX 10x1 L', '111111'],
    ['ZETAMAX 4x5 L', '222222'],
  ]);
  assert.equal(p1.unidadeBase, 'L');
  assert.ok(p1.materiais.some((m) => m.descricao === 'Rótulo ZETAMAX 1 L'));
  assert.equal(modelo.nomeAbaExibicao, 'ZETAMAX');

  const form = app.criarFormularioVazio(p1, false);
  form.data = '2026-01-10';
  const rep = app.calcularReporte(p1, form);
  const csv = app.gerarCSV(app.montarDadosExportacao(p1, form, rep, modelo.pendencias));
  assert.ok(csv.includes('Produto;ZETAMAX GRANEL'));
  assert.ok(csv.includes('ZETAMAX 10x1 L;111111'));
  assert.equal(app.nomeArquivoReporte(p1, form.data, 'xlsx'), 'reporte_ZETAMAX_GRANEL_2026-01.xlsx');
  assert.equal(app.nomeArquivoReporte({ nome: 'A/B: C' }, form.data, 'csv'), 'reporte_A_B_C_2026-01.csv');
});

test('Opcional (ANONIMIZAR_PRODUTOS = true): nenhum nome comercial chega ao modelo, à exportação ou ao nome do arquivo', (t) => {
  app.CONFIG.anonimizarProdutos = true;
  app.CONFIG.ocultarCodigosProdutos = true;
  t.after(() => {
    app.CONFIG.anonimizarProdutos = app.ANONIMIZAR_PRODUTOS;
    app.CONFIG.ocultarCodigosProdutos = app.OCULTAR_CODIGOS_PRODUTOS;
  });
  const wb = planilhaFicticiaComNomes();
  const analise = app.analisarPasta(wb);
  const modelo = app.interpretarAba(wb, analise.sugerida);
  assert.deepEqual(modelo.produtos.map((p) => p.nome), ['Produto 1', 'Produto 2']);
  assert.deepEqual(modelo.produtos.map((p) => p.codigo), ['PRD-001', 'PRD-002']);
  const p1 = modelo.produtos[0];
  assert.equal(p1.tipoOperacao, 'Formulação e envase');
  assert.equal(p1.unidadeBase, 'L');
  assert.deepEqual(p1.apresentacoes.map((a) => [a.nome, a.formato, a.codigo, a.vinculo]), [
    ['Apresentação 1', '10X1 L', 'PRD-001.1', 'fórmula do total envasado'],
    ['Apresentação 2', '4X5 L', 'PRD-001.2', 'fórmula do total envasado'],
  ]);
  assert.equal(modelo.produtos[1].tipoOperacao, 'Reenvase');
  assert.equal(p1.materiais[1].usagem, 64.5);
  assert.equal(p1.materiais[1].perda, 0.01);

  const form = app.criarFormularioVazio(p1, false);
  form.data = '2026-01-10';
  const rep = app.calcularReporte(p1, form);
  const dados = app.montarDadosExportacao(p1, form, rep, modelo.pendencias);
  const csv = app.gerarCSV(dados);
  const xlsxBin = XLSX.write(app.gerarPastaExportacao(XLSX, dados), { type: 'binary', bookType: 'xlsx', compression: false });
  const tudo = [JSON.stringify(modelo), csv, JSON.stringify(dados), xlsxBin, modelo.nomeAbaExibicao, app.nomeArquivoReporte(p1, form.data, 'xlsx')].join('\n');
  assert.equal(app.nomeArquivoReporte(p1, form.data, 'xlsx'), 'reporte_Produto_1_2026-01.xlsx');
  for (const proibido of ['ZETAMAX', 'zetamax', 'OMEGAPLUS', '111111', '222222', '333333']) {
    assert.ok(!tudo.includes(proibido), `vazamento de "${proibido}"`);
  }
  assert.ok(rep.linhas.some((l) => l.descricao === 'Rótulo Produto 1 1 L'), 'nome dentro da descrição do material deve ser mascarado');
});

test('Planilha sem volume-base gera pendência e não inventa valores', () => {
  const linhas = [
    ['Produto', 'Matéria-prima', 'Usagem Lista Técnica', 'Un.', 'Perda (%)'],
    ['FICTICIO GRANEL', 'Matéria-prima Alfa', 500, 'KG', '2%'],
  ];
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(linhas), 'Dados');
  const modelo = app.interpretarAba(wb, 'Dados');
  const p = modelo.produtos[0];
  assert.equal(p.baseFormulacaoDetectada, null);
  assert.ok(modelo.pendencias.some((x) => /volume-base/.test(x.mensagem)));
  const form = app.criarFormularioVazio(p, false);
  Object.assign(form, { data: '2026-02-01', formulado: '18.000', unidade: 'KG' });
  form.materiais[p.materiais[0].id].real = '900';
  let rep = app.calcularReporte(p, form);
  assert.equal(rep.linhas[0].status, STATUS.PENDENTE);
  assert.equal(rep.linhas[0].teorico, null);
  form.bases.F = '10.000';
  rep = app.calcularReporte(p, form);
  assert.equal(rep.linhas[0].teorico, 900);
  assert.equal(rep.linhas[0].status, STATUS.DENTRO);
});

test('Embalagem dentro do bloco de formulação fica com vínculo pendente de revisão', () => {
  const linhas = [
    ['Produto', 'Matéria-prima', 'Usagem Lista Técnica', 'Usagem teórica', 'Quantidade envasada', 'Un.', 'Perda (%)'],
    ['FICTICIO GRANEL', 'Matéria-prima Alfa', 500, { t: 'n', v: 0, f: 'C2*$E$2/10000' }, null, 'KG', 0.02],
    [null, 'Caixa de papelão', 10, { t: 'n', v: 0, f: 'C3*$E$2/10000' }, null, 'PC', 0.02],
  ];
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet(linhas);
  ws['!merges'] = [{ s: { r: 1, c: 0 }, e: { r: 2, c: 0 } }];
  XLSX.utils.book_append_sheet(wb, ws, 'Dados');
  const p = app.interpretarAba(wb, 'Dados').produtos[0];
  const form = app.criarFormularioVazio(p, false);
  Object.assign(form, { data: '2026-02-01', formulado: '18000', envasado: '18000', unidade: 'KG' });
  const rep = app.calcularReporte(p, form);
  const caixa = rep.linhas.find((l) => l.categoria === 'Caixa');
  assert.equal(caixa.vinculoPendente, true);
  assert.equal(caixa.status, STATUS.PENDENTE);
  assert.match(caixa.motivoPendencia, /vínculo pendente/);
});
