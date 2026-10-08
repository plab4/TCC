'use strict';

/* =====================================================================
 * CONFIGURAÇÃO
 * ===================================================================== */

// Nomes e códigos dos produtos são exibidos exatamente como estão na planilha.
// Mude para true apenas se precisar compartilhar o reporte sem identificar os
// produtos: os nomes viram "Produto 1", "Produto 2"... (e "Apresentação 1"...).
const ANONIMIZAR_PRODUTOS = false;

// Quando true, os códigos dos produtos e das apresentações são substituídos
// por PRD-001, PRD-002... (e PRD-001.1, PRD-001.2... para apresentações).
const OCULTAR_CODIGOS_PRODUTOS = false;

const CONFIG = {
  anonimizarProdutos: ANONIMIZAR_PRODUTOS,
  ocultarCodigosProdutos: OCULTAR_CODIGOS_PRODUTOS,
  // Quantas linhas do topo de cada aba são examinadas à procura do cabeçalho.
  linhasBuscaCabecalho: 40,
  // Tolerância relativa usada nas comparações de limites (evita falsos desvios
  // por arredondamento de ponto flutuante).
  toleranciaRelativa: 1e-9,
  // Casas decimais máximas na exibição de quantidades.
  casasQuantidade: 3,
  prefixoProduto: 'Produto',
  prefixoCodigo: 'PRD-',
  // Endereço de contingência do SheetJS (usado apenas se lib/xlsx.full.min.js faltar).
  cdnSheetJS: 'https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js',
};

const STATUS = Object.freeze({
  DENTRO: 'Dentro do esperado',
  ABAIXO: 'Consumo abaixo do teórico',
  ACIMA: 'Consumo acima do contrato',
  PENDENTE: 'Pendente',
});

const CATEGORIAS = [
  'Matéria-prima',
  'Ingrediente ativo',
  'Embalagem primária',
  'Embalagem secundária',
  'Rótulo',
  'Tampa',
  'Caixa',
  'Pallet',
  'Material auxiliar',
  'Não classificado',
];

// Categorias cujo consumo teórico é calculado sobre a quantidade envasada.
const CATEGORIAS_EMBALAGEM = new Set([
  'Embalagem primária',
  'Embalagem secundária',
  'Rótulo',
  'Tampa',
  'Caixa',
  'Pallet',
]);

const MOTIVOS_VARIACAO = [
  'Perda de processo',
  'Erro de pesagem ou dosagem',
  'Material fora de especificação',
  'Quebra ou avaria de embalagem',
  'Ajuste de formulação',
  'Retrabalho',
  'Erro de apontamento',
  'Outro',
];

const ESCOPO_FORMULACAO = 'F';
const VINCULO_TOTAL = 'TOTAL';

/* =====================================================================
 * TEXTO E NÚMEROS
 * ===================================================================== */

function normalizarTexto(valor) {
  if (valor === null || valor === undefined) return '';
  return String(valor)
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[\r\n\t]+/g, ' ')
    .replace(/[^a-z0-9%/ ]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function agrupamentoValido(texto, separador) {
  const grupos = texto.split(separador);
  if (grupos.length === 1) return /^\d+$/.test(grupos[0]);
  return /^\d{1,3}$/.test(grupos[0]) && grupos.slice(1).every((g) => /^\d{3}$/.test(g));
}

/**
 * Converte números em formato brasileiro ou internacional para Number.
 * Retorna null quando o valor não pode ser interpretado.
 *   "2.000,00" → 2000 | "1.310,480" → 1310.48 | "0,02" → 0.02 | "2%" → 0.02
 *   "2.000" → 2000 (ponto seguido de 3 dígitos é tratado como milhar)
 */
function interpretarNumero(valor) {
  if (valor === null || valor === undefined) return null;
  if (typeof valor === 'number') return Number.isFinite(valor) ? valor : null;
  if (typeof valor !== 'string') return null;

  let s = valor.replace(/[\s  ]/g, '');
  if (!s) return null;

  let percentual = false;
  if (s.endsWith('%')) {
    percentual = true;
    s = s.slice(0, -1);
  }
  s = s.replace(/^R\$/i, '');
  // Remove unidade grudada ao final ("500KG", "18000L").
  s = s.replace(/(\d)[a-zA-Z]{1,3}$/, '$1');

  let negativo = false;
  if (/^\(.*\)$/.test(s)) {
    negativo = true;
    s = s.slice(1, -1);
  }
  if (s.startsWith('-')) {
    negativo = !negativo;
    s = s.slice(1);
  } else if (s.startsWith('+')) {
    s = s.slice(1);
  }

  let n;
  if (/^\d*(?:[.,]\d+)?e[+-]?\d+$/i.test(s) && /\d/.test(s.split(/e/i)[0])) {
    n = Number(s.replace(',', '.'));
  } else if (/^[\d.,]+$/.test(s) && /\d/.test(s)) {
    const ultimoPonto = s.lastIndexOf('.');
    const ultimaVirgula = s.lastIndexOf(',');
    if (ultimoPonto >= 0 && ultimaVirgula >= 0) {
      const decimal = ultimoPonto > ultimaVirgula ? '.' : ',';
      const milhar = decimal === '.' ? ',' : '.';
      const partes = s.split(decimal);
      if (partes.length !== 2 || !agrupamentoValido(partes[0], milhar)) return null;
      n = Number(partes[0].split(milhar).join('') + '.' + partes[1]);
    } else if (ultimaVirgula >= 0) {
      const partes = s.split(',');
      if (partes.length > 2) {
        if (!agrupamentoValido(s, ',')) return null;
        n = Number(partes.join(''));
      } else {
        n = Number((partes[0] || '0') + '.' + partes[1]);
      }
    } else if (ultimoPonto >= 0) {
      const partes = s.split('.');
      if (partes.length > 2) {
        if (!agrupamentoValido(s, '.')) return null;
        n = Number(partes.join(''));
      } else if (partes[1].length === 3 && /^[1-9]\d{0,2}$/.test(partes[0])) {
        n = Number(partes.join(''));
      } else {
        n = Number((partes[0] || '0') + '.' + partes[1]);
      }
    } else {
      n = Number(s);
    }
  } else {
    return null;
  }

  if (!Number.isFinite(n)) return null;
  if (negativo) n = -n;
  if (percentual) n = n / 100;
  return n;
}

/**
 * Interpreta percentuais armazenados como 0.02, "2%", "0,02" ou 2 (pontos
 * percentuais). Retorna { valor, nota }.
 */
function interpretarPercentual(valor, formatoNumerico) {
  if (valor === null || valor === undefined || valor === '') return { valor: null, nota: null };
  const textoComPct = typeof valor === 'string' && valor.includes('%');
  const n = interpretarNumero(valor);
  if (n === null) return { valor: null, nota: 'valor não numérico' };
  const formatoPct = typeof formatoNumerico === 'string' && formatoNumerico.includes('%');
  if (!textoComPct && !formatoPct && n > 1 && n <= 100) {
    return { valor: n / 100, nota: `valor ${formatarNumero(n)} interpretado como ${formatarNumero(n)}%` };
  }
  return { valor: n, nota: null };
}

function arredondar(x) {
  if (typeof x !== 'number' || !Number.isFinite(x)) return x;
  return Number(x.toPrecision(12));
}

const formatadores = new Map();
function obterFormatador(min, max) {
  const chave = min + ':' + max;
  if (!formatadores.has(chave)) {
    formatadores.set(
      chave,
      new Intl.NumberFormat('pt-BR', { minimumFractionDigits: min, maximumFractionDigits: max })
    );
  }
  return formatadores.get(chave);
}

function formatarNumero(n, maxCasas = CONFIG.casasQuantidade, minCasas = 0) {
  if (typeof n !== 'number' || !Number.isFinite(n)) return '—';
  return obterFormatador(minCasas, maxCasas).format(n);
}

function formatarPercentual(fracao) {
  if (typeof fracao !== 'number' || !Number.isFinite(fracao)) return '—';
  return obterFormatador(2, 2).format(fracao * 100) + '%';
}

/* =====================================================================
 * UNIDADES
 * ===================================================================== */

const UNIDADES = {
  KG: { grupo: 'massa', fator: 1 },
  G: { grupo: 'massa', fator: 0.001 },
  T: { grupo: 'massa', fator: 1000 },
  L: { grupo: 'volume', fator: 1 },
  ML: { grupo: 'volume', fator: 0.001 },
  M3: { grupo: 'volume', fator: 1000 },
  PC: { grupo: 'contagem', fator: 1 },
  UN: { grupo: 'contagem', fator: 1 },
  M: { grupo: 'comprimento', fator: 1 },
  M2: { grupo: 'area', fator: 1 },
};

function normalizarUnidade(u) {
  const n = normalizarTexto(u).replace(/\s+/g, '');
  if (!n) return null;
  const mapa = {
    kg: 'KG', kgs: 'KG', quilo: 'KG', quilos: 'KG', quilograma: 'KG', quilogramas: 'KG',
    g: 'G', gr: 'G', grama: 'G', gramas: 'G',
    t: 'T', ton: 'T', tonelada: 'T', toneladas: 'T',
    l: 'L', lt: 'L', lts: 'L', litro: 'L', litros: 'L',
    ml: 'ML', mililitro: 'ML', mililitros: 'ML',
    m3: 'M3',
    pc: 'PC', pcs: 'PC', pca: 'PC', peca: 'PC', pecas: 'PC',
    un: 'UN', und: 'UN', unid: 'UN', unidade: 'UN', unidades: 'UN', ud: 'UN',
    m: 'M', metro: 'M', metros: 'M', m2: 'M2',
  };
  return mapa[n] || String(u).trim().toUpperCase();
}

function unidadesCompativeis(a, b) {
  const ua = normalizarUnidade(a);
  const ub = normalizarUnidade(b);
  if (!ua || !ub) return false;
  if (ua === ub) return true;
  return Boolean(UNIDADES[ua] && UNIDADES[ub] && UNIDADES[ua].grupo === UNIDADES[ub].grupo);
}

/** Converte valor entre unidades do mesmo grupo. Retorna null se incompatível. */
function converterUnidade(valor, de, para) {
  if (typeof valor !== 'number' || !Number.isFinite(valor)) return null;
  const ud = normalizarUnidade(de);
  const up = normalizarUnidade(para);
  if (!ud || !up) return null;
  if (ud === up) return valor;
  if (!unidadesCompativeis(ud, up)) return null;
  return arredondar((valor * UNIDADES[ud].fator) / UNIDADES[up].fator);
}

/* =====================================================================
 * CÁLCULOS
 * ===================================================================== */

/**
 * consumo_teorico = (usagem_lista_tecnica × quantidade_base) / volume_base
 * A quantidade base é a formulada (matérias-primas) ou a envasada da
 * apresentação correspondente (embalagens).
 */
function calcularConsumoTeorico(usagem, quantidade, volumeBase) {
  if (typeof usagem !== 'number' || !Number.isFinite(usagem) || usagem < 0) {
    return { valor: null, motivo: 'Usagem da Lista Técnica ausente ou inválida' };
  }
  if (typeof volumeBase !== 'number' || !Number.isFinite(volumeBase) || volumeBase <= 0) {
    return { valor: null, motivo: 'Volume-base ausente ou inválido' };
  }
  if (typeof quantidade !== 'number' || !Number.isFinite(quantidade) || quantidade < 0) {
    return { valor: null, motivo: 'Quantidade de referência não informada' };
  }
  return { valor: arredondar((usagem * quantidade) / volumeBase), motivo: null };
}

/**
 * Avalia o consumo real frente ao teórico e à perda contratual.
 *   limite_inferior = teorico
 *   limite_superior = teorico × (1 + perda)
 *   variacao = (real − teorico) / teorico
 *   excedente = max(0, real − limite_superior)
 */
function avaliarConsumo({ teorico, perda, real, unidadeCompativel = true }) {
  const r = {
    limiteInferior: null,
    limiteSuperior: null,
    variacao: null,
    excedente: null,
    status: STATUS.PENDENTE,
    motivo: null,
    desvio: false,
  };
  if (typeof teorico !== 'number' || !Number.isFinite(teorico) || teorico < 0) {
    r.motivo = 'Consumo teórico indisponível';
    return r;
  }
  r.limiteInferior = teorico;
  if (typeof perda !== 'number' || !Number.isFinite(perda) || perda < 0 || perda > 1) {
    r.motivo = 'Perda contratual ausente ou fora do intervalo de 0% a 100%';
    return r;
  }
  r.limiteSuperior = arredondar(teorico * (1 + perda));
  if (!unidadeCompativel) {
    r.motivo = 'Unidade do consumo real incompatível com a unidade do material';
    return r;
  }
  if (real === null || real === undefined || typeof real !== 'number' || !Number.isFinite(real)) {
    r.motivo = 'Consumo real não informado';
    return r;
  }
  if (real < 0) {
    r.motivo = 'Consumo real negativo';
    return r;
  }
  r.variacao = teorico > 0 ? arredondar((real - teorico) / teorico) : null;
  const tolerancia = CONFIG.toleranciaRelativa * Math.max(1, Math.abs(teorico));
  if (real < teorico - tolerancia) {
    r.status = STATUS.ABAIXO;
  } else if (real > r.limiteSuperior + tolerancia) {
    r.status = STATUS.ACIMA;
  } else {
    r.status = STATUS.DENTRO;
  }
  r.excedente = r.status === STATUS.ACIMA ? arredondar(real - r.limiteSuperior) : 0;
  r.desvio = r.status === STATUS.ABAIXO || r.status === STATUS.ACIMA;
  return r;
}

/** Justificativa obrigatória para desvios automáticos ou marcação manual "Sim". */
function exigeJustificativa(status, foraEspecificacaoManual) {
  return status === STATUS.ABAIXO || status === STATUS.ACIMA || foraEspecificacaoManual === 'Sim';
}

/** diferença = formulado − envasado */
function calcularDiferencaProducao(formulado, envasado) {
  const valido = (n) => typeof n === 'number' && Number.isFinite(n) && n >= 0;
  if (!valido(formulado) || !valido(envasado)) return { diferenca: null, exigeJustificativa: false };
  const diferenca = arredondar(formulado - envasado);
  const tolerancia = CONFIG.toleranciaRelativa * Math.max(1, Math.abs(formulado));
  return { diferenca, exigeJustificativa: Math.abs(diferenca) > tolerancia };
}

function somarApresentacoes(valores) {
  let soma = 0;
  let algum = false;
  for (const v of valores) {
    if (typeof v === 'number' && Number.isFinite(v)) {
      soma += v;
      algum = true;
    }
  }
  return algum ? arredondar(soma) : null;
}

function valoresIguais(a, b) {
  if (typeof a !== 'number' || typeof b !== 'number') return false;
  return Math.abs(a - b) <= CONFIG.toleranciaRelativa * Math.max(1, Math.abs(a), Math.abs(b));
}

/* =====================================================================
 * CLASSIFICAÇÃO DE MATERIAIS
 * ===================================================================== */

const REGRAS_CATEGORIA = [
  [/\b(rotulo|rotulos|etiqueta|etiquetas|label|bula|folheto|contra rotulo)\b/, 'Rótulo'],
  [/\b(tampa|tampas|batoque|lacre|tampinha|cap|valvula|selo de inducao|sobretampa)\b/, 'Tampa'],
  [/\b(caixa|caixas|cx|cartucho|papelao|carton|master)\b/, 'Caixa'],
  [/\b(pallet|pallets|palete|paletes|palet)\b/, 'Pallet'],
  [/\b(embalagem secundaria|shrink|termo encolhivel|fardo|display)\b/, 'Embalagem secundária'],
  [
    /\b(frasco|frascos|bombona|bombonas|galao|galoes|balde|garrafa|tambor|tambores|ibc|container|conteiner|lata|saco|sacos|sache|bag|big bag|pote|bisnaga|embalagem primaria)\b/,
    'Embalagem primária',
  ],
  [/\b(stretch|fita|cantoneira|filme|adesivo|cola|tinta|ribbon|separador|intercalador|arquear|fitilho)\b/, 'Material auxiliar'],
  [/\b(ingrediente ativo|principio ativo|ativo|tecnico|ia)\b/, 'Ingrediente ativo'],
  [
    /\b(materia prima|materias primas|mp|solvente|emulsificante|tensoativo|agua|aditivo|corante|espessante|antiespumante|conservante|veiculo|inerte|carga|dispersante|umectante)\b/,
    'Matéria-prima',
  ],
];

/**
 * Sugere a categoria pelo texto da descrição. O escopo ("formulacao" ou
 * "apresentacao") resolve descrições genéricas.
 */
function classificarMaterial(descricao, escopo, temTeor) {
  const n = normalizarTexto(descricao);
  for (const [regra, categoria] of REGRAS_CATEGORIA) {
    if (regra.test(n)) return categoria;
  }
  if (temTeor) return 'Ingrediente ativo';
  if (/\b(embalagem|embalagens|emb)\b/.test(n)) {
    return escopo === 'apresentacao' ? 'Embalagem primária' : 'Não classificado';
  }
  if (escopo === 'formulacao') return 'Matéria-prima';
  return 'Não classificado';
}

function separarCodigos(valor) {
  if (valor === null || valor === undefined) return [];
  return String(valor)
    .split(/[\/;,\n\r|]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

/* =====================================================================
 * LEITURA DA PLANILHA
 * ===================================================================== */

function indiceColuna(letras) {
  let n = 0;
  for (const ch of letras.toUpperCase()) n = n * 26 + (ch.charCodeAt(0) - 64);
  return n - 1;
}

function letraColuna(indice) {
  let s = '';
  let n = indice + 1;
  while (n > 0) {
    const resto = (n - 1) % 26;
    s = String.fromCharCode(65 + resto) + s;
    n = Math.floor((n - 1) / 26);
  }
  return s;
}

function enderecoCelula(r, c) {
  return letraColuna(c) + (r + 1);
}

function decodificarIntervalo(ref) {
  const [a, b] = String(ref).split(':');
  const parse = (x) => {
    const m = /^\$?([A-Z]+)\$?(\d+)$/i.exec(x);
    return m ? { r: Number(m[2]) - 1, c: indiceColuna(m[1]) } : null;
  };
  const s = parse(a);
  const e = b ? parse(b) : s;
  if (!s || !e) return null;
  return { s, e };
}

function criarLeitor(ws) {
  const intervalo = ws && ws['!ref'] ? decodificarIntervalo(ws['!ref']) : null;
  if (!intervalo) return null;
  const mesclas = new Map();
  for (const m of ws['!merges'] || []) {
    for (let r = m.s.r; r <= m.e.r; r++) {
      for (let c = m.s.c; c <= m.e.c; c++) mesclas.set(r + ',' + c, m);
    }
  }
  return {
    intervalo,
    bruta(r, c) {
      return ws[enderecoCelula(r, c)] || null;
    },
    mescla(r, c) {
      return mesclas.get(r + ',' + c) || null;
    },
    // Valor considerando células mescladas (devolve a célula superior esquerda).
    topo(r, c) {
      const m = mesclas.get(r + ',' + c);
      return m ? this.bruta(m.s.r, m.s.c) : this.bruta(r, c);
    },
  };
}

function textoCelula(celula) {
  if (!celula || celula.t === 'e') return '';
  if (celula.v === null || celula.v === undefined) return '';
  return String(celula.v).trim();
}

function numeroCelula(celula) {
  if (!celula || celula.t === 'e') return null;
  return interpretarNumero(celula.v);
}

// Valor numérico informado na planilha. Fórmulas com resultado zero (modelo
// ainda não preenchido) não são tratadas como valor informado.
function valorPreenchido(celula) {
  const n = numeroCelula(celula);
  if (n === null) return false;
  return !(celula.f && n === 0);
}

// Campos procurados no cabeçalho, em ordem de prioridade.
const CAMPOS = [
  { id: 'diferenca', padroes: [/diferenca/] },
  { id: 'analise', padroes: [/analise/] },
  { id: 'codigoInsumo', padroes: [/cod\w* (dos? )?(insumo|material|materiais|componente|mp)/, /^cod\w* insumo/] },
  { id: 'volumeBase', padroes: [/volume base|volume da lista|volume lt|base lt|lote padrao|tamanho do lote|base de calculo/] },
  { id: 'usagemTeorica', padroes: [/teoric/] },
  { id: 'usagemLT', padroes: [/lista tecnica|\blt\b|usagem indicada|\bbom\b|formula padrao/] },
  { id: 'qtdReal', padroes: [/(qtd|quantidade) (usada|consumida|real)|consumo real|usad[ao] em producao|consumid/] },
  { id: 'variacao', padroes: [/variacao/] },
  { id: 'perda', padroes: [/perda/] },
  { id: 'excedente', padroes: [/excedente/] },
  { id: 'teor', padroes: [/\bteor\b|pureza|concentracao/] },
  { id: 'qtdFormulada', padroes: [/produzid|formulad/], exclui: [/envasad/] },
  { id: 'qtdEnvasada', padroes: [/envasad/] },
  { id: 'codigoProduto', padroes: [/^cod\w*( do produto| produto| sku)?$/, /^sku$/, /codigo do produto/] },
  { id: 'produto', padroes: [/^produtos?\b/, /descricao do produto/, /^item$/, /^sku descricao/] },
  {
    id: 'descricao',
    padroes: [/materias? primas?|embalage|descricao (do )?(material|insumo|componente)|^materia(l|is)\b|^insumos?\b|^componentes?\b|^descricao$/],
  },
];

const PADRAO_UNIDADE = /^(un|und|unid|unidade|unidades|um|u m|unidade de medida|unid medida)$/;
const PADRAO_OBSERVACAO = /observac|justificativ/;
const CAMPOS_ESSENCIAIS = ['produto', 'descricao', 'usagemLT'];

const ROTULOS_CAMPOS = {
  produto: 'Produto',
  codigoProduto: 'Código do produto',
  qtdFormulada: 'Quantidade formulada/produzida',
  qtdEnvasada: 'Quantidade envasada',
  diferenca: 'Diferença formulado − envasado',
  observacoes: 'Observações/justificativas',
  codigoInsumo: 'Código do insumo',
  descricao: 'Matéria-prima/embalagem',
  usagemLT: 'Usagem da Lista Técnica',
  usagemTeorica: 'Usagem teórica da campanha',
  unidade: 'Unidade',
  teor: 'Teor',
  qtdReal: 'Quantidade consumida',
  unidadeReal: 'Unidade do consumo',
  variacao: 'Variação',
  perda: 'Perda contratual',
  excedente: 'Excedente',
  justificativaMaterial: 'Justificativa do material',
  analise: 'Análise pós-justificativa',
  volumeBase: 'Volume-base',
};

function mapearColunas(rotulos) {
  const usados = new Set();
  const mapa = {};
  for (const campo of CAMPOS) {
    for (let c = 0; c < rotulos.length; c++) {
      const l = rotulos[c];
      if (!l || usados.has(c)) continue;
      if (PADRAO_UNIDADE.test(l) || (PADRAO_OBSERVACAO.test(l) && campo.id !== 'analise')) continue;
      if (!campo.padroes.some((p) => p.test(l))) continue;
      if ((campo.exclui || []).some((p) => p.test(l))) continue;
      mapa[campo.id] = c;
      usados.add(c);
      break;
    }
  }
  const unidades = [];
  const observacoes = [];
  rotulos.forEach((l, c) => {
    if (!l || usados.has(c)) return;
    if (PADRAO_UNIDADE.test(l)) unidades.push(c);
    else if (PADRAO_OBSERVACAO.test(l)) observacoes.push(c);
  });
  const colDescricao = mapa.descricao !== undefined ? mapa.descricao : -1;
  const unidadeMaterial = unidades.find((c) => c > colDescricao);
  if (unidadeMaterial !== undefined) mapa.unidade = unidadeMaterial;
  else if (unidades.length) mapa.unidade = unidades[0];
  if (mapa.qtdReal !== undefined) {
    const ur = unidades.find((c) => c > mapa.qtdReal && c !== mapa.unidade);
    if (ur !== undefined) mapa.unidadeReal = ur;
  }
  for (const c of observacoes) {
    if (colDescricao >= 0 && c > colDescricao) {
      if (mapa.justificativaMaterial === undefined) mapa.justificativaMaterial = c;
    } else if (mapa.observacoes === undefined) {
      mapa.observacoes = c;
    }
  }
  return mapa;
}

function pontuarMapa(mapa) {
  let pontos = Object.keys(mapa).length;
  for (const id of CAMPOS_ESSENCIAIS) if (mapa[id] !== undefined) pontos += 3;
  return pontos;
}

function localizarCabecalho(leitor) {
  const { s, e } = leitor.intervalo;
  const limite = Math.min(e.r, s.r + CONFIG.linhasBuscaCabecalho);
  let melhor = null;
  for (let r = s.r; r <= limite; r++) {
    const simples = [];
    const duplo = [];
    for (let c = s.c; c <= e.c; c++) {
      const a = leitor.topo(r, c);
      const ta = normalizarTexto(textoCelula(a));
      simples[c] = typeof (a && a.v) === 'number' ? '' : ta;
      if (r + 1 <= e.r) {
        const b = leitor.topo(r + 1, c);
        const tb = b && b !== a && typeof b.v !== 'number' ? normalizarTexto(textoCelula(b)) : '';
        duplo[c] = [simples[c], tb].filter(Boolean).join(' ');
      }
    }
    const candidatos = [{ rotulos: simples, fim: r }];
    if (r + 1 <= e.r) candidatos.push({ rotulos: duplo, fim: r + 1 });
    for (const cand of candidatos) {
      const mapa = mapearColunas(cand.rotulos);
      const pontos = pontuarMapa(mapa);
      if (!melhor || pontos > melhor.pontos) {
        melhor = { inicio: r, fim: cand.fim, mapa, pontos, rotulos: cand.rotulos };
      }
    }
  }
  return melhor;
}

/**
 * Lê a fórmula da usagem teórica (ex.: "I3*$D$3/10000") e extrai a linha da
 * quantidade de referência e o volume-base (divisor).
 */
function analisarFormulaTeorica(formula, colunas, leitor) {
  if (!formula || typeof formula !== 'string') return null;
  const f = formula.replace(/\s+/g, '').toUpperCase().replace(/^=/, '');
  const refs = [];
  for (const m of f.matchAll(/(^|[^A-Z0-9!_$])\$?([A-Z]{1,3})\$?(\d+)(?![\d(])/g)) {
    refs.push({ c: indiceColuna(m[2]), r: Number(m[3]) - 1 });
  }
  const colsQtd = [colunas.qtdEnvasada, colunas.qtdFormulada].filter((c) => c !== undefined);
  const refQtd = refs.find((x) => colsQtd.includes(x.c)) || null;
  let base = null;
  let origemBase = null;
  const div = /\/\(?((?:\d+(?:\.\d+)?)|(?:\$?[A-Z]{1,3}\$?\d+))\)?/.exec(f);
  if (div) {
    if (/^[\d.]+$/.test(div[1])) {
      base = Number(div[1]);
      origemBase = 'fórmula';
    } else {
      const ref = /^\$?([A-Z]{1,3})\$?(\d+)$/.exec(div[1]);
      const cel = ref ? leitor.bruta(Number(ref[2]) - 1, indiceColuna(ref[1])) : null;
      const n = numeroCelula(cel);
      if (n !== null) {
        base = n;
        origemBase = 'célula referenciada na fórmula';
      }
    }
  } else if (refQtd) {
    base = 1;
    origemBase = 'fórmula sem divisor';
  }
  if (base !== null && !(base > 0)) base = null;
  return { linhaRef: refQtd ? refQtd.r : null, base, origemBase };
}

function referenciasNaColuna(formula, coluna) {
  if (!formula || coluna === undefined) return [];
  const f = formula.replace(/\s+/g, '').toUpperCase();
  const linhas = [];
  for (const m of f.matchAll(/(^|[^A-Z0-9!_$])\$?([A-Z]{1,3})\$?(\d+)(?:\:\$?([A-Z]{1,3})\$?(\d+))?/g)) {
    if (indiceColuna(m[2]) !== coluna) continue;
    const ini = Number(m[3]) - 1;
    const fim = m[5] ? Number(m[5]) - 1 : ini;
    for (let r = ini; r <= fim; r++) linhas.push(r);
  }
  return linhas;
}

const PADRAO_GRANEL = /\b(granel|bulk|a granel|semi ?acabado|semiacabado)\b/;
const PADRAO_REENVASE = /\b(reenvase|re envase|reenvasado|reembalagem|reacondicionamento)\b/;
const PADRAO_APRESENTACAO = /\b(apresentacao|apresentacoes|sku)\b|\d+ ?x ?\d+|\b\d+([.,]\d+)? ?(kg|l|lt|ml|g)\b/;
const PADRAO_FORMATO = /(\d+(?:[.,]\d+)?\s*[xX]\s*\d+(?:[.,]\d+)?\s*(?:kg|g|l|lt|ml)\b|\d+(?:[.,]\d+)?\s*(?:kg|g|l|lt|ml)\b)/i;
const PALAVRAS_GENERICAS = /\b(granel|bulk|a granel|semi ?acabado|apresentacao|apresentacoes|reenvase|re envase|sku)\b/g;

function rotuloLimpo(rotulo) {
  return String(rotulo || '').replace(/\s+/g, ' ').trim();
}

/** Nome de exibição da apresentação (com o formato quando o nome é genérico). */
function nomeApresentacao(a) {
  return CONFIG.anonimizarProdutos && a.formato ? `${a.nome} (${a.formato})` : a.nome;
}

function extrairFormato(rotuloReal) {
  const m = PADRAO_FORMATO.exec(String(rotuloReal || ''));
  return m ? m[1].replace(/\s+/g, ' ').toUpperCase() : null;
}

function nomeBaseParaMascara(rotuloReal) {
  let n = normalizarTexto(rotuloReal);
  n = n.replace(new RegExp(PADRAO_FORMATO.source, 'gi'), ' ');
  n = n.replace(PALAVRAS_GENERICAS, ' ').replace(/\s+/g, ' ').trim();
  return n.replace(/[^a-z]/g, '').length >= 4 ? n : null;
}

/**
 * Substitui ocorrências de nomes reais de produtos dentro de outros textos
 * (por exemplo, descrição de rótulos) pelo identificador anônimo.
 */
function mascararTexto(texto, mascaras) {
  if (!texto || !mascaras || !mascaras.length) return texto;
  let original = String(texto);
  for (const { base, substituto } of mascaras) {
    const mapa = [];
    let norm = '';
    for (let i = 0; i < original.length; i++) {
      let ch = original[i].normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
      if (!/[a-z0-9]/.test(ch)) ch = ' ';
      for (const x of ch) {
        norm += x;
        mapa.push(i);
      }
    }
    const alvo = base;
    let saida = '';
    let cursor = 0;
    let idx = norm.indexOf(alvo);
    let alterou = false;
    while (idx >= 0) {
      const ini = mapa[idx];
      const fim = mapa[idx + alvo.length - 1] + 1;
      if (ini >= cursor) {
        saida += original.slice(cursor, ini) + substituto;
        cursor = fim;
        alterou = true;
      }
      idx = norm.indexOf(alvo, idx + alvo.length);
    }
    if (alterou) original = saida + original.slice(cursor);
  }
  return original;
}

function moda(valores) {
  const cont = new Map();
  for (const v of valores) if (v !== null && v !== undefined) cont.set(v, (cont.get(v) || 0) + 1);
  let melhor = null;
  let max = 0;
  for (const [v, n] of cont) {
    if (n > max) {
      melhor = v;
      max = n;
    }
  }
  return melhor;
}

/** Avalia todas as abas e devolve as compatíveis, da mais provável para a menos. */
function analisarPasta(workbook) {
  const abas = [];
  for (const nome of workbook.SheetNames) {
    const leitor = criarLeitor(workbook.Sheets[nome]);
    if (!leitor) {
      abas.push({ nome, compativel: false, materiais: 0, pontos: 0 });
      continue;
    }
    const cab = localizarCabecalho(leitor);
    const essenciais = cab && CAMPOS_ESSENCIAIS.every((id) => cab.mapa[id] !== undefined);
    let materiais = 0;
    if (essenciais) {
      for (let r = cab.fim + 1; r <= leitor.intervalo.e.r; r++) {
        if (numeroCelula(leitor.bruta(r, cab.mapa.usagemLT)) !== null) materiais++;
      }
    }
    abas.push({
      nome,
      compativel: Boolean(essenciais),
      materiais,
      pontos: cab ? cab.pontos : 0,
    });
  }
  const compativeis = abas
    .filter((a) => a.compativel)
    .sort((a, b) => b.materiais - a.materiais || b.pontos - a.pontos);
  const comDados = compativeis.filter((a) => a.materiais > 0);
  return {
    abas,
    compativeis,
    sugerida: (comDados[0] || compativeis[0] || {}).nome || null,
    exigeEscolha: comDados.length > 1,
  };
}

/**
 * Interpreta a aba e devolve o modelo de produtos, apresentações e materiais.
 * Com CONFIG.anonimizarProdutos, os nomes reais ficam só nas variáveis locais
 * desta função e o modelo recebe identificadores genéricos.
 */
function interpretarAba(workbook, nomeAba) {
  const pendencias = [];
  const pend = (nivel, mensagem) => pendencias.push({ nivel, mensagem });
  const leitor = criarLeitor(workbook.Sheets[nomeAba]);
  if (!leitor) {
    pend('erro', 'A aba selecionada está vazia.');
    return { produtos: [], pendencias, colunas: {}, totalMateriais: 0 };
  }
  const cab = localizarCabecalho(leitor);
  const col = cab ? cab.mapa : {};
  const faltando = CAMPOS_ESSENCIAIS.filter((id) => col[id] === undefined);
  if (!cab || faltando.length) {
    pend('erro', 'Cabeçalho não reconhecido. Campos ausentes: ' + faltando.map((id) => ROTULOS_CAMPOS[id]).join(', ') + '.');
    return { produtos: [], pendencias, colunas: col, totalMateriais: 0 };
  }
  const opcionais = ['qtdFormulada', 'qtdEnvasada', 'unidade', 'perda', 'usagemTeorica', 'codigoInsumo', 'qtdReal'];
  for (const id of opcionais) {
    if (col[id] === undefined) pend('aviso', `Coluna "${ROTULOS_CAMPOS[id]}" não identificada no cabeçalho.`);
  }

  const rotuloCabecalhoDescricao = cab.rotulos[col.descricao];
  const blocos = [];
  let atual = null;

  for (let r = cab.fim + 1; r <= leitor.intervalo.e.r; r++) {
    const celProduto = leitor.topo(r, col.produto);
    const mescla = leitor.mescla(r, col.produto);
    const rotulo = textoCelula(celProduto);
    const celDescricao = leitor.bruta(r, col.descricao);
    const descricao = textoCelula(celDescricao);
    const celUsagem = leitor.bruta(r, col.usagemLT);
    const codigoBruto = col.codigoInsumo !== undefined ? leitor.bruta(r, col.codigoInsumo) : null;

    if (normalizarTexto(descricao) && normalizarTexto(descricao) === rotuloCabecalhoDescricao) continue;
    if (/^total\b/.test(normalizarTexto(rotulo)) || /^total\b/.test(normalizarTexto(descricao))) continue;

    if (rotulo) {
      const inicioBloco = mescla ? mescla.s.r : r;
      const mesmoBloco =
        atual &&
        (mescla
          ? atual.inicio === inicioBloco
          : atual.rotuloNorm === normalizarTexto(rotulo) && atual.ultimaLinha === r - 1);
      if (!mesmoBloco) {
        atual = {
          indice: blocos.length,
          inicio: inicioBloco,
          rotuloReal: rotulo,
          rotuloNorm: normalizarTexto(rotulo),
          linhas: [],
          materiais: [],
        };
        blocos.push(atual);
      }
    }

    const temMaterial =
      Boolean(descricao) || textoCelula(codigoBruto) !== '' || (celUsagem && celUsagem.v !== undefined && celUsagem.v !== '');
    if (!temMaterial) {
      if (atual && rotulo) {
        atual.linhas.push(r);
        atual.ultimaLinha = r;
      }
      continue;
    }
    if (!atual) {
      pend('aviso', `Linha ${r + 1}: material sem produto associado; linha ignorada.`);
      continue;
    }
    atual.linhas.push(r);
    atual.ultimaLinha = r;
    atual.materiais.push(lerMaterial(leitor, col, r));
  }

  // Quantidades e fórmulas de cada bloco (células mescladas: superior esquerda).
  const blocoDaLinha = new Map();
  for (const b of blocos) {
    const linhas = b.linhas.length ? b.linhas : [b.inicio];
    const fim = Math.max(...linhas, b.inicio);
    for (let r = b.inicio; r <= fim; r++) blocoDaLinha.set(r, b);
    const cel = (c) => (c === undefined ? null : leitor.topo(b.inicio, c));
    b.celCodigo = cel(col.codigoProduto);
    b.celFormulada = cel(col.qtdFormulada);
    b.celEnvasada = cel(col.qtdEnvasada);
    b.refsEnvasado = b.celEnvasada && b.celEnvasada.f ? referenciasNaColuna(b.celEnvasada.f, col.qtdEnvasada) : [];
  }

  // Classificação dos blocos.
  for (const b of blocos) {
    const n = b.rotuloNorm;
    const refsExternas = b.refsEnvasado.filter((r) => blocoDaLinha.get(r) && blocoDaLinha.get(r) !== b);
    if (PADRAO_REENVASE.test(n)) b.tipo = 'reenvase';
    else if (PADRAO_GRANEL.test(n) || refsExternas.length) b.tipo = 'granel';
    else if (PADRAO_APRESENTACAO.test(n)) b.tipo = 'apresentacao';
    else {
      const cats = b.materiais.map((m) => classificarMaterial(m.descricao, null, m.teor !== null));
      const emb = cats.filter((c) => CATEGORIAS_EMBALAGEM.has(c)).length;
      b.tipo = cats.length && emb === cats.length ? 'apresentacao' : 'produto';
    }
  }

  // Agrupamento em produtos, na ordem em que aparecem.
  const produtos = [];
  const produtoPorNome = new Map();
  const mascaras = [];
  const criarProduto = (b, tipoOperacao) => {
    const existente = produtoPorNome.get(b.rotuloNorm);
    if (existente) {
      existente.blocos.push(b);
      pend('aviso', `${existente.nome}: produto repetido na planilha (linha ${b.inicio + 1}); materiais agrupados no mesmo identificador.`);
      return existente;
    }
    const numero = produtos.length + 1;
    const p = {
      id: 'P' + numero,
      numero,
      nome: CONFIG.anonimizarProdutos ? `${CONFIG.prefixoProduto} ${numero}` : rotuloLimpo(b.rotuloReal),
      codigo: CONFIG.prefixoCodigo + String(numero).padStart(3, '0'),
      tipoBloco: b.tipo,
      tipoOperacao,
      blocos: [b],
      apresentacoes: [],
      materiais: [],
      prefill: { formulado: null, envasado: null, apresentacoes: {} },
      unidadeBase: null,
      baseFormulacaoDetectada: null,
    };
    produtoPorNome.set(b.rotuloNorm, p);
    produtos.push(p);
    const base = CONFIG.anonimizarProdutos ? nomeBaseParaMascara(b.rotuloReal) : null;
    if (base) mascaras.push({ base, substituto: p.nome });
    return p;
  };
  const criarApresentacao = (produto, b, vinculo) => {
    const chave = b.rotuloNorm;
    const existente = produto.apresentacoes.find((a) => a._chave === chave);
    if (existente) {
      existente.blocos.push(b);
      pend('aviso', `${produto.nome} › ${existente.nome}: apresentação repetida (linha ${b.inicio + 1}); materiais agrupados.`);
      return existente;
    }
    const i = produto.apresentacoes.length + 1;
    const a = {
      id: `${produto.id}-A${i}`,
      _chave: chave,
      nome: CONFIG.anonimizarProdutos ? `Apresentação ${i}` : rotuloLimpo(b.rotuloReal),
      formato: extrairFormato(b.rotuloReal),
      codigo: `${produto.codigo}.${i}`,
      vinculo,
      blocos: [b],
      baseDetectada: null,
    };
    produto.apresentacoes.push(a);
    const base = CONFIG.anonimizarProdutos ? nomeBaseParaMascara(b.rotuloReal) : null;
    if (base) mascaras.push({ base, substituto: `${produto.nome} ${a.nome}` });
    return a;
  };

  for (const b of blocos) {
    if (b.tipo === 'granel') b.produto = criarProduto(b, 'Formulação (granel)');
    else if (b.tipo === 'produto') b.produto = criarProduto(b, 'Não identificado');
  }
  let ultimoGranel = null;
  for (const b of blocos) {
    if (b.tipo === 'granel' || b.tipo === 'produto') {
      ultimoGranel = b.produto;
      continue;
    }
    if (b.tipo === 'reenvase') {
      b.produto = criarProduto(b, 'Reenvase');
      b.apresentacao = criarApresentacao(b.produto, b, 'próprio bloco');
      continue;
    }
    const pai = blocos.find(
      (g) => (g.tipo === 'granel' || g.tipo === 'produto') && g.refsEnvasado.some((r) => b.inicio <= r && r <= Math.max(b.inicio, ...b.linhas))
    );
    if (pai) {
      b.produto = pai.produto;
      b.apresentacao = criarApresentacao(pai.produto, b, 'fórmula do total envasado');
    } else if (ultimoGranel) {
      b.produto = ultimoGranel;
      b.apresentacao = criarApresentacao(ultimoGranel, b, 'posição na planilha');
      const temRefs = blocos.some((g) => g.produto === ultimoGranel && g.refsEnvasado.length);
      pend(
        'aviso',
        `${ultimoGranel.nome} › ${b.apresentacao.nome} (linha ${b.inicio + 1}): ` +
          (temRefs
            ? 'apresentação não incluída na fórmula do total envasado da planilha; vínculo atribuído pela posição — revisar.'
            : 'vínculo com o produto atribuído pela posição na planilha.')
      );
    } else {
      b.produto = criarProduto(b, 'Envase');
      b.apresentacao = criarApresentacao(b.produto, b, 'próprio bloco');
    }
  }

  // Materiais: escopo pela fórmula (linha da quantidade referenciada) ou pelo bloco.
  let totalMateriais = 0;
  let codigosAleatorios = 0;
  for (const b of blocos) {
    for (const m of b.materiais) {
      const p = b.produto;
      let alvo = b;
      if (m.linhaRef !== null) {
        const bRef = blocoDaLinha.get(m.linhaRef);
        if (bRef && bRef.produto === p) alvo = bRef;
        else if (bRef && bRef.produto !== p) {
          pend('aviso', `Linha ${m.linha}: a fórmula da usagem teórica referencia outro produto; mantido o bloco de origem.`);
        }
      }
      const escopo = alvo.apresentacao ? alvo.apresentacao.id : ESCOPO_FORMULACAO;
      const escopoTipo = alvo.apresentacao ? 'apresentacao' : 'formulacao';
      totalMateriais++;
      if (m.codigoAleatorio) codigosAleatorios++;
      p.materiais.push({
        id: `${p.id}-M${p.materiais.length + 1}`,
        linha: m.linha,
        codigo: m.codigo,
        descricao: mascararTexto(m.descricao, mascaras) || '(sem descrição)',
        categoriaSugerida: classificarMaterial(m.descricao, escopoTipo, m.teor !== null),
        unidade: m.unidade,
        unidadeReal: m.unidadeReal,
        usagem: m.usagem,
        baseDetectada: m.base,
        origemBase: m.origemBase,
        escopo,
        teor: m.teor,
        perda: m.perda,
        realImportado: m.real,
        analise: mascararTexto(m.analise, mascaras),
        duplicado: false,
      });
    }
  }
  if (codigosAleatorios) {
    pend('info', `${codigosAleatorios} código(s) de insumo vêm de fórmula aleatória (RANDBETWEEN) e podem mudar a cada recálculo da planilha.`);
  }

  // Volumes-base por escopo, unidades, prefill e alertas por produto.
  for (const p of produtos) {
    const basesF = p.materiais.filter((m) => m.escopo === ESCOPO_FORMULACAO).map((m) => m.baseDetectada);
    p.baseFormulacaoDetectada = moda(basesF);
    for (const a of p.apresentacoes) {
      a.baseDetectada = moda(p.materiais.filter((m) => m.escopo === a.id).map((m) => m.baseDetectada));
      const doBloco = p.materiais.filter((m) => m.escopo === a.id);
      if (!doBloco.length) pend('aviso', `${p.nome} › ${a.nome}: apresentação sem materiais vinculados.`);
      else if (a.baseDetectada === null) pend('aviso', `${p.nome} › ${a.nome}: volume-base não identificado — informe em Parâmetros.`);
      if (!CONFIG.ocultarCodigosProdutos) {
        const cods = a.blocos.flatMap((b) => separarCodigos(textoCelula(b.celCodigo)));
        a.codigo = cods.length ? [...new Set(cods)].join(' / ') : '—';
      }
      const env = a.blocos.map((b) => b.celEnvasada).find(valorPreenchido);
      if (env) p.prefill.apresentacoes[a.id] = numeroCelula(env);
    }
    const temF = p.materiais.some((m) => m.escopo === ESCOPO_FORMULACAO);
    if (temF && p.baseFormulacaoDetectada === null) {
      pend('aviso', `${p.nome}: volume-base da formulação não identificado — informe em Parâmetros.`);
    }
    for (const m of p.materiais) {
      const baseEscopo = m.escopo === ESCOPO_FORMULACAO ? p.baseFormulacaoDetectada : (p.apresentacoes.find((a) => a.id === m.escopo) || {}).baseDetectada;
      if (m.baseDetectada !== null && baseEscopo !== null && m.baseDetectada !== baseEscopo) {
        pend('aviso', `${p.nome}, linha ${m.linha}: volume-base próprio (${formatarNumero(m.baseDetectada)}) diferente do restante do bloco (${formatarNumero(baseEscopo)}).`);
      }
    }
    // Unidade-base a partir dos formatos das apresentações (KG ou L).
    const unidades = new Set(
      p.apresentacoes
        .map((a) => a.formato && /(\bKG|\bG)$/.test(a.formato) ? 'KG' : a.formato && /(\bL|\bLT|\bML)$/.test(a.formato) ? 'L' : null)
        .filter(Boolean)
    );
    p.unidadeBase = unidades.size === 1 ? [...unidades][0] : null;
    if (!CONFIG.ocultarCodigosProdutos) {
      // Granel sem código próprio: usa os códigos das suas apresentações.
      let cods = p.blocos.flatMap((b) => separarCodigos(textoCelula(b.celCodigo)));
      if (!cods.length) cods = p.apresentacoes.map((a) => a.codigo).filter((c) => c && c !== '—');
      p.codigo = cods.length ? [...new Set(cods)].join(' / ') : '—';
    }
    const celF = p.blocos.map((b) => b.celFormulada).find(valorPreenchido);
    const celE = p.blocos.filter((b) => b.tipo !== 'apresentacao').map((b) => b.celEnvasada).find(valorPreenchido);
    if (celF) p.prefill.formulado = numeroCelula(celF);
    if (celE) p.prefill.envasado = numeroCelula(celE);
    if (p.apresentacoes.length) {
      p.tipoOperacao = p.tipoOperacao === 'Formulação (granel)' ? 'Formulação e envase' : p.tipoOperacao;
    }

    // Materiais duplicados no mesmo escopo.
    const vistos = new Map();
    for (const m of p.materiais) {
      const chave = m.escopo + '|' + normalizarTexto(m.codigo || '') + '|' + normalizarTexto(m.descricao);
      if (vistos.has(chave)) {
        m.duplicado = true;
        vistos.get(chave).duplicado = true;
      } else vistos.set(chave, m);
    }
    const dups = p.materiais.filter((m) => m.duplicado).length;
    if (dups) pend('aviso', `${p.nome}: ${dups} material(is) duplicado(s) no mesmo bloco.`);

    // Remove referências internas que carregam dados da planilha.
    for (const a of p.apresentacoes) {
      delete a._chave;
      delete a.blocos;
    }
    delete p.blocos;
  }

  for (const b of blocos) {
    for (const m of b.materiais) for (const n of m.notas) pend(n.nivel, n.mensagem);
  }
  if (!produtos.length) pend('erro', 'Nenhum produto foi identificado na aba selecionada.');

  return {
    produtos,
    pendencias,
    totalMateriais,
    nomeAbaExibicao: mascararTexto(nomeAba, mascaras),
    colunas: Object.fromEntries(Object.entries(col).map(([k, v]) => [k, letraColuna(v)])),
    linhaCabecalho: cab.inicio + 1,
  };
}

function lerMaterial(leitor, col, r) {
  const linha = r + 1;
  const notas = [];
  const nota = (nivel, mensagem) => notas.push({ nivel, mensagem: `Linha ${linha}: ${mensagem}` });
  const cel = (c) => (c === undefined ? null : leitor.bruta(r, c));

  const celCodigo = cel(col.codigoInsumo);
  let codigo = null;
  let codigoAleatorio = false;
  if (celCodigo) {
    if (celCodigo.t === 'e') nota('aviso', 'código do insumo com erro de fórmula.');
    else codigo = separarCodigos(textoCelula(celCodigo)).join(' / ') || null;
    codigoAleatorio = Boolean(celCodigo.f && /RANDBETWEEN|ALEATORIOENTRE|RAND\(/i.test(celCodigo.f));
  }

  const descricao = textoCelula(cel(col.descricao));
  const celUsagem = cel(col.usagemLT);
  const usagem = numeroCelula(celUsagem);
  if (usagem === null) nota('aviso', 'usagem da Lista Técnica ausente ou não numérica.');
  else if (usagem < 0) nota('erro', 'usagem da Lista Técnica negativa.');

  const unidade = normalizarUnidade(textoCelula(cel(col.unidade)));
  if (!unidade) nota('aviso', 'unidade de medida não informada.');
  const unidadeReal = normalizarUnidade(textoCelula(cel(col.unidadeReal))) || unidade;

  const celTeor = cel(col.teor);
  const teor = celTeor && celTeor.t !== 'e' ? interpretarPercentual(celTeor.v, celTeor.z).valor : null;

  const celPerda = cel(col.perda);
  let perda = null;
  if (celPerda && celPerda.t !== 'e') {
    const p = interpretarPercentual(celPerda.v, celPerda.z);
    perda = p.valor;
    if (p.nota) nota('aviso', `perda contratual: ${p.nota}.`);
  }
  if (perda === null) nota('aviso', 'perda contratual ausente.');
  else if (perda < 0 || perda > 1) nota('erro', 'perda contratual fora do intervalo de 0% a 100%.');

  const celReal = cel(col.qtdReal);
  const real = valorPreenchido(celReal) ? numeroCelula(celReal) : null;

  let base = null;
  let origemBase = null;
  let linhaRef = null;
  const celVolume = cel(col.volumeBase);
  if (numeroCelula(celVolume) > 0) {
    base = numeroCelula(celVolume);
    origemBase = 'coluna de volume-base';
  }
  const celTeorica = cel(col.usagemTeorica);
  const analise = celTeorica && celTeorica.f ? analisarFormulaTeorica(celTeorica.f, col, leitor) : null;
  if (analise) {
    linhaRef = analise.linhaRef;
    if (base === null && analise.base !== null) {
      base = analise.base;
      origemBase = analise.origemBase;
    }
  }
  if (base === null) nota('aviso', 'volume-base não identificado na fórmula da usagem teórica.');

  return {
    linha,
    codigo,
    codigoAleatorio,
    descricao,
    usagem,
    unidade,
    unidadeReal,
    teor,
    perda,
    real,
    base,
    origemBase,
    linhaRef,
    analise: textoCelula(cel(col.analise)) || textoCelula(cel(col.justificativaMaterial)) || null,
    notas,
  };
}

/* =====================================================================
 * DADOS DE DEMONSTRAÇÃO (totalmente fictícios)
 * ===================================================================== */

/** Monta uma aba no formato do SheetJS a partir de linhas (sem usar a biblioteca). */
function montarAba(linhas) {
  const ws = {};
  let maxC = 0;
  linhas.forEach((linha, r) => {
    linha.forEach((v, c) => {
      if (v === null || v === undefined) return;
      maxC = Math.max(maxC, c);
      if (typeof v === 'object') ws[enderecoCelula(r, c)] = { ...v };
      else ws[enderecoCelula(r, c)] = { t: typeof v === 'number' ? 'n' : 's', v };
    });
  });
  ws['!ref'] = 'A1:' + enderecoCelula(Math.max(0, linhas.length - 1), maxC);
  return ws;
}

// Não depende do SheetJS: a demonstração funciona mesmo sem a biblioteca.
function criarPastaDemonstracao() {
  const f = (formula) => ({ t: 'n', v: 0, f: formula });
  const linhas = [
    ['REPORTE DE PRODUÇÃO - DEMONSTRAÇÃO'],
    [
      'Produto', 'Código', 'Quantidade produzida (Sólidos-KG, Líquidos-L)', 'Quantidade envasada (Sólidos-KG, Líquidos-L)',
      'Diferença: Formulado - Envasado', 'Observações / Justificativas', 'Código dos insumos', 'Matérias primas e embalagens',
      'Usagens indicadas na Lista Técnica', 'Usagem Teórica para Campanha', 'Un.', 'Teor do Ingrediente Ativo',
      'Qtd usada em produção', 'Un.', 'Variação de consumo (%)', 'Perdas estabelecidas em contrato (%)', 'Excedente do contrato (Un.)',
      'Análise pós justificativa',
    ],
    ['Produto 1', 'DEMO-000', 18000, { t: 'n', v: 17660, f: 'D5' }, f('C3-D3'), null, 'MP-001', 'Matéria-prima Alfa', 500, f('I3*$C$3/10000'), 'KG', null, 910, 'KG', null, 0.02],
    [null, null, null, null, null, null, 'MP-002', 'Matéria-prima Beta', 64, f('I4*$C$3/10000'), 'KG', null, '120,000', 'KG', null, '1%'],
    ['Produto 1 - 1x20 L', 'DEMO-001', null, 17660, null, null, 'EMB-001', 'Embalagem A', 50, f('I5*$D$5/1000'), 'PC', null, 880, 'PC', null, 0.02],
  ];
  const ws = montarAba(linhas);
  ws['!merges'] = [
    { s: { r: 2, c: 0 }, e: { r: 3, c: 0 } },
    { s: { r: 2, c: 1 }, e: { r: 3, c: 1 } },
    { s: { r: 2, c: 2 }, e: { r: 3, c: 2 } },
    { s: { r: 2, c: 3 }, e: { r: 3, c: 3 } },
  ];
  return { SheetNames: ['Demonstração'], Sheets: { 'Demonstração': ws } };
}

/* =====================================================================
 * REPORTE (cálculo completo de um produto)
 * ===================================================================== */

function criarFormularioVazio(produto, usarPrefill) {
  const fmt = (n) => (n === null || n === undefined ? '' : formatarNumero(n, 6));
  const form = {
    data: '',
    formulado: usarPrefill ? fmt(produto.prefill.formulado) : '',
    unidade: produto.unidadeBase || '',
    envasado: usarPrefill ? fmt(produto.prefill.envasado) : '',
    observacoes: '',
    justificativaDiferenca: '',
    apresentacoes: {},
    justificativaApresentacoes: '',
    bases: {},
    materiais: {},
  };
  for (const a of produto.apresentacoes) {
    form.apresentacoes[a.id] = usarPrefill ? fmt(produto.prefill.apresentacoes[a.id]) : '';
  }
  for (const m of produto.materiais) {
    form.materiais[m.id] = {
      real: usarPrefill ? fmt(m.realImportado) : '',
      unidadeReal: m.unidadeReal || m.unidade || '',
      categoria: m.categoriaSugerida,
      foraEspec: 'Não',
      vinculo: '',
      perdaManual: '',
      motivo: '',
      descricao: '',
      lote: '',
      acao: '',
      investigacao: 'Não',
      responsavel: '',
      prazo: '',
      observacoes: '',
    };
  }
  return form;
}

function nomeEscopo(produto, escopo) {
  if (escopo === ESCOPO_FORMULACAO) return 'Formulação';
  if (escopo === VINCULO_TOTAL) return 'Total envasado';
  const a = produto.apresentacoes.find((x) => x.id === escopo);
  return a ? a.nome : '—';
}

function lerCampoNumerico(texto, rotulo, erros, { permitirVazio = true } = {}) {
  const vazio = texto === null || texto === undefined || String(texto).trim() === '';
  if (vazio) return null;
  const n = interpretarNumero(String(texto));
  if (n === null) {
    erros.push(`${rotulo}: valor "${String(texto).slice(0, 20)}" não é um número válido.`);
    return null;
  }
  if (n < 0) {
    erros.push(`${rotulo}: não pode ser negativo.`);
    return null;
  }
  return n;
}

function calcularReporte(produto, form) {
  const erros = [];
  const avisos = [];
  const temFormulacao = produto.materiais.some((m) => m.escopo === ESCOPO_FORMULACAO);
  const nApres = produto.apresentacoes.length;

  if (!form.data) erros.push('Informe a data do reporte.');
  const formulado = lerCampoNumerico(form.formulado, 'Quantidade formulada', erros);
  const envasado = lerCampoNumerico(form.envasado, 'Quantidade total envasada', erros);
  if (temFormulacao && formulado === null && String(form.formulado || '').trim() === '') erros.push('Informe a quantidade formulada ou produzida.');
  if (nApres && envasado === null && String(form.envasado || '').trim() === '') erros.push('Informe a quantidade total envasada.');
  if (temFormulacao && !form.unidade) erros.push('Selecione a unidade da formulação (KG ou L).');

  const dif = calcularDiferencaProducao(formulado, envasado);
  const justificativaDiferencaPendente = dif.exigeJustificativa && !String(form.justificativaDiferenca || '').trim();
  if (justificativaDiferencaPendente) erros.push('Informe a justificativa para a diferença entre formulado e envasado.');

  // Apresentações
  const qtdApresentacao = {};
  for (const a of produto.apresentacoes) {
    qtdApresentacao[a.id] =
      nApres === 1 ? envasado : lerCampoNumerico(form.apresentacoes[a.id], `${a.nome} — quantidade envasada`, erros);
  }
  let somaApresentacoes = null;
  let diferencaApresentacoes = null;
  let divergenciaApresentacoes = false;
  if (nApres > 1) {
    somaApresentacoes = somarApresentacoes(Object.values(qtdApresentacao));
    if (envasado !== null || somaApresentacoes !== null) {
      diferencaApresentacoes = arredondar((envasado || 0) - (somaApresentacoes || 0));
      divergenciaApresentacoes = !valoresIguais(envasado || 0, somaApresentacoes || 0);
    }
    if (divergenciaApresentacoes && !String(form.justificativaApresentacoes || '').trim()) {
      erros.push('A soma das apresentações difere do total envasado: corrija os valores ou registre uma justificativa.');
    }
  }

  // Volumes-base
  const bases = {};
  const baseDe = (escopo, detectada, rotulo) => {
    const texto = form.bases[escopo];
    if (texto !== undefined && String(texto).trim() !== '') {
      const n = interpretarNumero(String(texto));
      if (n === null || n <= 0) {
        erros.push(`Volume-base (${rotulo}) deve ser um número maior que zero.`);
        return null;
      }
      return n;
    }
    return detectada;
  };
  bases[ESCOPO_FORMULACAO] = baseDe(ESCOPO_FORMULACAO, produto.baseFormulacaoDetectada, 'Formulação');
  for (const a of produto.apresentacoes) bases[a.id] = baseDe(a.id, a.baseDetectada, a.nome);
  const baseDetectadaEscopo = (escopo) =>
    escopo === ESCOPO_FORMULACAO
      ? produto.baseFormulacaoDetectada
      : (produto.apresentacoes.find((a) => a.id === escopo) || {}).baseDetectada ?? null;

  // Materiais
  const linhas = produto.materiais.map((m) => {
    const st = form.materiais[m.id] || {};
    const categoria = st.categoria || m.categoriaSugerida;
    let escopo = m.escopo;
    let vinculoPendente = false;
    const embalagemNaFormulacao = m.escopo === ESCOPO_FORMULACAO && CATEGORIAS_EMBALAGEM.has(categoria);
    if (embalagemNaFormulacao) {
      const opcoes = new Set([VINCULO_TOTAL, ...produto.apresentacoes.map((a) => a.id)]);
      if (st.vinculo && opcoes.has(st.vinculo)) escopo = st.vinculo;
      else {
        escopo = null;
        vinculoPendente = true;
      }
    }

    let quantidadeRef = null;
    let base = null;
    if (escopo === ESCOPO_FORMULACAO) quantidadeRef = formulado;
    else if (escopo === VINCULO_TOTAL) quantidadeRef = envasado;
    else if (escopo) quantidadeRef = qtdApresentacao[escopo];
    if (escopo) {
      const baseEscopo = escopo === VINCULO_TOTAL ? bases[ESCOPO_FORMULACAO] : bases[escopo];
      const propria = m.baseDetectada;
      const usarPropria =
        propria !== null && escopo === m.escopo && propria !== baseDetectadaEscopo(escopo);
      base = usarPropria ? propria : baseEscopo ?? propria;
    }

    // Perda
    let perda = m.perda;
    let perdaManual = false;
    if (perda === null && String(st.perdaManual || '').trim() !== '') {
      const p = interpretarPercentual(String(st.perdaManual));
      perda = p.valor;
      perdaManual = true;
    }
    if (perda !== null && (perda < 0 || perda > 1)) {
      erros.push(`${m.codigo || 'Material'} — ${m.descricao}: perda contratual deve estar entre 0% e 100%.`);
    }

    // Consumo real
    const errosLocais = [];
    const real = lerCampoNumerico(st.real, `${m.codigo || 'Material'} — consumo real`, errosLocais);
    erros.push(...errosLocais);
    const unidadeReal = st.unidadeReal || m.unidade;
    let unidadeCompativel = true;
    let realConvertido = real;
    if (real !== null && m.unidade && unidadeReal) {
      realConvertido = converterUnidade(real, unidadeReal, m.unidade);
      if (realConvertido === null) {
        unidadeCompativel = false;
        erros.push(`${m.codigo || 'Material'} — ${m.descricao}: unidade do consumo (${unidadeReal}) incompatível com ${m.unidade}.`);
      }
    }

    const teo = vinculoPendente
      ? { valor: null, motivo: 'Material com vínculo pendente de revisão' }
      : calcularConsumoTeorico(m.usagem, quantidadeRef, base);
    const av = avaliarConsumo({ teorico: teo.valor, perda, real: realConvertido, unidadeCompativel });
    const motivoPendencia = av.status === STATUS.PENDENTE ? teo.motivo || av.motivo : null;

    const foraEspecAutomatico = av.desvio;
    const foraEspec = foraEspecAutomatico ? 'Sim' : st.foraEspec === 'Sim' ? 'Sim' : 'Não';
    const exige = exigeJustificativa(av.status, foraEspec);
    const faltando = [];
    if (exige) {
      if (!st.motivo) faltando.push('motivo da variação');
      if (!String(st.descricao || '').trim()) faltando.push('descrição da ocorrência');
      if (!String(st.acao || '').trim()) faltando.push('ação imediata');
      if (st.investigacao === 'Sim') {
        if (!String(st.responsavel || '').trim()) faltando.push('responsável pela investigação');
        if (!st.prazo) faltando.push('prazo');
      }
      if (faltando.length) {
        erros.push(`${m.codigo || 'Material'} — ${m.descricao}: justificativa obrigatória incompleta (${faltando.join(', ')}).`);
      }
    }

    return {
      id: m.id,
      linha: m.linha,
      codigo: m.codigo,
      descricao: m.descricao,
      categoria,
      unidade: m.unidade,
      unidadeReal,
      teor: m.teor,
      usagem: m.usagem,
      base,
      escopo,
      escopoOriginal: m.escopo,
      escopoNome: escopo ? nomeEscopo(produto, escopo) : 'Vínculo pendente',
      embalagemNaFormulacao,
      vinculoPendente,
      quantidadeRef,
      teorico: teo.valor,
      perda,
      perdaManual,
      perdaAusente: m.perda === null,
      limiteInferior: av.limiteInferior,
      limiteSuperior: av.limiteSuperior,
      real,
      realConvertido,
      variacao: av.variacao,
      excedente: av.excedente,
      status: av.status,
      motivoPendencia,
      foraEspec,
      foraEspecAutomatico,
      exigeJustificativa: exige,
      justificativaPendente: exige && faltando.length > 0,
      camposFaltando: faltando,
      duplicado: m.duplicado,
      analise: m.analise,
    };
  });

  const contagem = {
    total: linhas.length,
    dentro: linhas.filter((l) => l.status === STATUS.DENTRO).length,
    abaixo: linhas.filter((l) => l.status === STATUS.ABAIXO).length,
    acima: linhas.filter((l) => l.status === STATUS.ACIMA).length,
    pendentes: linhas.filter((l) => l.status === STATUS.PENDENTE).length,
    justificativasPendentes:
      linhas.filter((l) => l.justificativaPendente).length + (justificativaDiferencaPendente ? 1 : 0),
  };

  const vinculos = linhas.filter((l) => l.vinculoPendente).length;
  if (vinculos) avisos.push(`${vinculos} material(is) com vínculo pendente de revisão (embalagem sem apresentação associada).`);
  const semBase = linhas.filter((l) => !l.vinculoPendente && l.escopo && !(l.base > 0)).length;
  if (semBase) avisos.push(`${semBase} material(is) sem volume-base — informe em Parâmetros.`);
  const dups = linhas.filter((l) => l.duplicado).length;
  if (dups) avisos.push(`${dups} material(is) duplicado(s) na planilha.`);
  const semPerda = linhas.filter((l) => l.perda === null).length;
  if (semPerda) avisos.push(`${semPerda} material(is) sem perda contratual.`);
  const semReal = linhas.filter((l) => l.status === STATUS.PENDENTE && l.motivoPendencia === 'Consumo real não informado').length;
  if (semReal) avisos.push(`${semReal} material(is) sem consumo real informado.`);
  for (const a of produto.apresentacoes) {
    if (!linhas.some((l) => l.escopo === a.id)) avisos.push(`${a.nome}: apresentação sem materiais vinculados.`);
    else if (a.vinculo === 'posição na planilha') avisos.push(`${a.nome}: vínculo com o produto atribuído pela posição na planilha.`);
  }

  return {
    formulado,
    envasado,
    diferenca: dif.diferenca,
    exigeJustificativaDiferenca: dif.exigeJustificativa,
    qtdApresentacao,
    somaApresentacoes,
    diferencaApresentacoes,
    divergenciaApresentacoes,
    bases,
    linhas,
    contagem,
    erros: [...new Set(erros)],
    avisos,
    podeExportar: erros.length === 0,
  };
}

/* =====================================================================
 * EXPORTAÇÃO
 * ===================================================================== */

const REGRAS_APLICADAS = [
  'Matérias-primas: consumo teórico = (usagem da Lista Técnica × quantidade formulada) ÷ volume-base da formulação.',
  'Embalagens: consumo teórico = (usagem da Lista Técnica × quantidade envasada da apresentação) ÷ volume-base da apresentação.',
  'Limite inferior = consumo teórico; limite máximo = consumo teórico × (1 + perda contratual).',
  'Variação = (consumo real − consumo teórico) ÷ consumo teórico.',
  'Excedente contratual = consumo real − limite máximo (zero quando negativo).',
  'Status: abaixo do teórico se real < teórico; acima do contrato se real > limite máximo; dentro do esperado no intervalo.',
  'Teor do ingrediente ativo exibido apenas como informação (sem correção aplicada).',
];

function nomeArquivoReporte(produto, data, extensao) {
  const mes = /^(\d{4})-(\d{2})/.exec(data || '');
  const periodo = mes ? `${mes[1]}-${mes[2]}` : 'sem-data';
  const nome = produto.nome.replace(/[\\/:*?"<>|\x00-\x1f]+/g, ' ').trim().replace(/\s+/g, '_') || 'produto';
  return `reporte_${nome}_${periodo}.${extensao}`;
}

function montarDadosExportacao(produto, form, rep, pendenciasImportacao) {
  const resumo = [
    ['Reporte de Produção e Consumo de Materiais'],
    [],
    ['Produto', produto.nome],
    ['Código', produto.codigo],
    ['Tipo de operação', produto.tipoOperacao],
    ['Data do reporte', form.data || ''],
    ['Unidade da formulação', form.unidade || ''],
    ['Quantidade formulada', rep.formulado],
    ['Quantidade envasada', rep.envasado],
    ['Diferença (formulado − envasado)', rep.diferenca],
    ['Justificativa da diferença', form.justificativaDiferenca || ''],
    [],
    ['Apresentação', 'Código', 'Quantidade envasada', 'Unidade'],
    ...produto.apresentacoes.map((a) => [
      nomeApresentacao(a),
      a.codigo,
      rep.qtdApresentacao[a.id],
      form.unidade || '',
    ]),
  ];
  if (produto.apresentacoes.length > 1) {
    resumo.push(['Soma das apresentações', '', rep.somaApresentacoes, form.unidade || '']);
    resumo.push(['Justificativa da divergência das apresentações', form.justificativaApresentacoes || '']);
  }
  resumo.push(
    [],
    ['Totais por status', 'Quantidade'],
    ['Total de materiais', rep.contagem.total],
    [STATUS.DENTRO, rep.contagem.dentro],
    [STATUS.ABAIXO, rep.contagem.abaixo],
    [STATUS.ACIMA, rep.contagem.acima],
    [STATUS.PENDENTE, rep.contagem.pendentes],
    ['Justificativas pendentes', rep.contagem.justificativasPendentes],
    [],
    ['Observações', form.observacoes || '']
  );

  const cabecalhoMateriais = [
    'Código do insumo', 'Descrição', 'Categoria', 'Vínculo', 'Unidade', 'Usagem Lista Técnica', 'Volume-base',
    'Consumo teórico', 'Perda contratual', 'Limite máximo', 'Consumo real', 'Variação', 'Excedente contratual',
    'Consumo fora da especificação', 'Status', 'Motivo da variação', 'Justificativa (descrição da ocorrência)',
    'Ação imediata', 'Investigação necessária', 'Responsável', 'Prazo', 'Lote', 'Observações',
  ];
  const materiais = [cabecalhoMateriais];
  for (const l of rep.linhas) {
    const st = form.materiais[l.id] || {};
    materiais.push([
      l.codigo || '',
      l.descricao,
      l.categoria,
      l.escopoNome,
      l.unidade || '',
      l.usagem,
      l.base,
      l.teorico,
      l.perda,
      l.limiteSuperior,
      l.realConvertido,
      l.variacao,
      l.excedente,
      l.foraEspec,
      l.status + (l.motivoPendencia ? ` (${l.motivoPendencia})` : ''),
      st.motivo || '',
      st.descricao || '',
      st.acao || '',
      l.exigeJustificativa ? st.investigacao || 'Não' : '',
      st.responsavel || '',
      st.prazo || '',
      st.lote || '',
      st.observacoes || '',
    ]);
  }

  const parametros = [
    ['Identificador', 'Escopo', 'Volume-base', 'Unidade'],
    [produto.nome, 'Formulação', rep.bases[ESCOPO_FORMULACAO], form.unidade || ''],
    ...produto.apresentacoes.map((a) => [
      `${produto.nome} › ${a.nome}`,
      'Apresentação',
      rep.bases[a.id],
      form.unidade || '',
    ]),
    [],
    ['Unidades dos materiais'],
    ...[...new Set(rep.linhas.map((l) => l.unidade).filter(Boolean))].map((u) => [u]),
    [],
    ['Regras aplicadas'],
    ...REGRAS_APLICADAS.map((r) => [r]),
    [],
    ['Pendências de importação'],
    ...(pendenciasImportacao.length ? pendenciasImportacao.map((p) => [p.nivel, p.mensagem]) : [['Nenhuma']]),
  ];

  return { resumo, materiais, parametros, colunasPercentuais: [8, 11], colunasQuantidade: [5, 6, 7, 9, 10, 12] };
}

function gerarCSV(dados) {
  const celula = (v, pct) => {
    if (v === null || v === undefined) return '';
    if (typeof v === 'number' && pct) return formatarPercentual(v);
    if (typeof v === 'number') return Number.isFinite(v) ? String(arredondar(v)).replace('.', ',') : '';
    const s = String(v);
    return /[;"\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  };
  const bloco = (titulo, linhas, pcts = []) =>
    [titulo, ...linhas.map((l, r) => l.map((v, c) => celula(v, r > 0 && pcts.includes(c))).join(';'))].join('\r\n');
  return (
    '\ufeff' +
    [
      bloco('# Resumo', dados.resumo),
      bloco('# Consumo de Materiais', dados.materiais, dados.colunasPercentuais),
      bloco('# Parâmetros', dados.parametros),
    ].join(
      '\r\n\r\n'
    )
  );
}

function gerarPastaExportacao(XLSX, dados) {
  const wb = XLSX.utils.book_new();
  const aba = (linhas, larguras, colunasPct = [], colunasQtd = null) => {
    const ws = XLSX.utils.aoa_to_sheet(linhas);
    ws['!cols'] = larguras.map((w) => ({ wch: w }));
    for (let r = 1; r < linhas.length; r++) {
      for (let c = 0; c < linhas[r].length; c++) {
        const cel = ws[enderecoCelula(r, c)];
        if (!cel || cel.t !== 'n') continue;
        if (colunasPct.includes(c)) cel.z = '0.00%';
        else if (!colunasQtd || colunasQtd.includes(c)) cel.z = '#,##0.000';
      }
    }
    return ws;
  };
  XLSX.utils.book_append_sheet(wb, aba(dados.resumo, [44, 28, 20, 12], [], [1, 2]), 'Resumo');
  XLSX.utils.book_append_sheet(
    wb,
    aba(
      dados.materiais,
      [16, 36, 20, 18, 8, 14, 12, 14, 12, 14, 14, 11, 14, 14, 28, 26, 40, 32, 14, 22, 12, 12, 30],
      dados.colunasPercentuais,
      dados.colunasQuantidade
    ),
    'Consumo de Materiais'
  );
  XLSX.utils.book_append_sheet(wb, aba(dados.parametros, [60, 26, 14, 10], [], [2]), 'Parâmetros');
  return wb;
}

/* =====================================================================
 * INTERFACE
 * ===================================================================== */

function iniciarApp() {
  window.__reporteIniciado = true;
  const $ = (sel) => document.querySelector(sel);
  const esc = (s) =>
    String(s === null || s === undefined ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

  // Estado em memória (nada é gravado em armazenamento do navegador).
  const estado = {
    workbook: null,
    analise: null,
    aba: null,
    modelo: null,
    produtoId: null,
    formularios: {},
    expandidos: new Set(),
    filtros: { busca: '', categoria: '', status: '', ordem: 'linha', direcao: 1 },
    limpezaPendente: null,
  };

  const el = {
    arquivo: $('#arquivo'),
    demo: $('#btn-demo'),
    status: $('#import-status'),
    abaSelect: $('#aba-select'),
    abaInfo: $('#aba-info'),
    nProdutos: $('#n-produtos'),
    nMateriais: $('#n-materiais'),
    nPendencias: $('#n-pendencias'),
    pendencias: $('#pendencias-importacao'),
    pendenciasLista: $('#pendencias-lista'),
    produtoSecao: $('#secao-produto'),
    produtoSelect: $('#produto-select'),
    produtoInfo: $('#produto-info'),
    trabalho: $('#area-trabalho'),
    data: $('#f-data'),
    formulado: $('#f-formulado'),
    unidade: $('#f-unidade'),
    envasado: $('#f-envasado'),
    observacoes: $('#f-observacoes'),
    diferenca: $('#f-diferenca'),
    justDifBox: $('#box-just-dif'),
    justDif: $('#f-just-dif'),
    apresSecao: $('#secao-apresentacoes'),
    apresCorpo: $('#apres-corpo'),
    apresTotal: $('#apres-total'),
    apresAlerta: $('#apres-alerta'),
    justApresBox: $('#box-just-apres'),
    justApres: $('#f-just-apres'),
    parametrosCorpo: $('#parametros-corpo'),
    cards: $('#cards'),
    busca: $('#filtro-busca'),
    filtroCategoria: $('#filtro-categoria'),
    filtroStatus: $('#filtro-status'),
    tabelaCorpo: $('#materiais-corpo'),
    tabelaCabecalho: $('#materiais-cabecalho'),
    contadorTabela: $('#contador-tabela'),
    validacoes: $('#validacoes'),
    btnExcel: $('#btn-excel'),
    btnCSV: $('#btn-csv'),
    btnPDF: $('#btn-pdf'),
    btnLimpar: $('#btn-limpar'),
    exportMsg: $('#export-msg'),
  };

  el.filtroCategoria.innerHTML =
    '<option value="">Todas as categorias</option>' + CATEGORIAS.map((c) => `<option>${esc(c)}</option>`).join('');
  el.filtroStatus.innerHTML =
    '<option value="">Todos os status</option>' + Object.values(STATUS).map((s) => `<option>${esc(s)}</option>`).join('');

  function definirStatus(texto, tipo) {
    el.status.textContent = texto;
    el.status.className = 'status-badge status-' + (tipo || 'neutro');
  }

  function obterXLSX() {
    return typeof XLSX !== 'undefined' ? XLSX : window.XLSX;
  }

  if (!obterXLSX()) {
    definirStatus(
      'Biblioteca SheetJS não carregada (lib/xlsx.full.min.js): a importação de .xlsx e a exportação para Excel ficam indisponíveis. A demonstração e o CSV funcionam. Veja o README.',
      'erro'
    );
    el.arquivo.disabled = true;
  }

  function mostrarFalha(contexto, e) {
    const detalhe = e && e.message ? ` (${e.message})` : '';
    definirStatus(`${contexto}${detalhe}`, 'erro');
  }

  el.arquivo.addEventListener('change', async () => {
    const arquivo = el.arquivo.files && el.arquivo.files[0];
    if (!arquivo) return;
    if (!/\.xlsx$/i.test(arquivo.name)) {
      definirStatus('Selecione um arquivo no formato .xlsx.', 'erro');
      return;
    }
    definirStatus('Lendo planilha…', 'neutro');
    let wb;
    try {
      const buffer = await arquivo.arrayBuffer();
      wb = obterXLSX().read(buffer, { type: 'array', cellFormula: true, cellNF: true, cellDates: false });
    } catch (e) {
      mostrarFalha('Não foi possível ler o arquivo. Confirme se é um .xlsx válido', e);
      return;
    } finally {
      // Libera a referência ao arquivo; o original nunca é alterado.
      el.arquivo.value = '';
    }
    try {
      carregarPasta(wb);
    } catch (e) {
      mostrarFalha('Erro ao interpretar a planilha', e);
    }
  });

  el.demo.addEventListener('click', () => {
    try {
      carregarPasta(criarPastaDemonstracao(), true);
    } catch (e) {
      mostrarFalha('Erro ao carregar a demonstração', e);
    }
  });

  function carregarPasta(wb, demonstracao) {
    estado.workbook = wb;
    estado.analise = analisarPasta(wb);
    estado.demonstracao = Boolean(demonstracao);
    const { compativeis, sugerida, exigeEscolha } = estado.analise;
    el.abaSelect.innerHTML = '';
    if (!compativeis.length) {
      definirStatus('Nenhuma aba compatível encontrada.', 'erro');
      limparModelo([{ nivel: 'erro', mensagem: 'Nenhuma aba contém cabeçalhos equivalentes a produto, material e usagem da Lista Técnica.' }]);
      el.abaSelect.hidden = true;
      return;
    }
    // O nome da aba é exibido somente após mascarar eventuais nomes de produto.
    el.abaSelect.innerHTML = compativeis
      .map((a, i) => `<option value="${i}">${esc(interpretarAba(wb, a.nome).nomeAbaExibicao)} — ${a.materiais} linha(s) de material</option>`)
      .join('');
    el.abaSelect.value = String(compativeis.findIndex((a) => a.nome === sugerida));
    el.abaSelect.hidden = compativeis.length < 2;
    el.abaInfo.textContent = exigeEscolha ? 'Mais de uma aba compatível: confirme a aba desejada.' : '';
    selecionarAba(sugerida);
  }

  el.abaSelect.addEventListener('change', () => {
    const aba = estado.analise.compativeis[Number(el.abaSelect.value)];
    if (aba) selecionarAba(aba.nome);
  });

  function selecionarAba(nome) {
    estado.aba = nome;
    estado.modelo = interpretarAba(estado.workbook, nome);
    estado.formularios = {};
    estado.expandidos.clear();
    const m = estado.modelo;
    el.abaInfo.textContent =
      (estado.analise.exigeEscolha ? 'Mais de uma aba compatível: confirme a aba desejada. ' : '') +
      `Aba selecionada: "${m.nomeAbaExibicao}" (cabeçalho na linha ${m.linhaCabecalho || '—'}).`;
    el.nProdutos.textContent = String(m.produtos.length);
    el.nMateriais.textContent = String(m.totalMateriais);
    el.nPendencias.textContent = String(m.pendencias.length);
    renderizarPendencias(m.pendencias);
    if (!m.produtos.length) {
      definirStatus('Importação concluída com erros.', 'erro');
      el.produtoSecao.hidden = true;
      el.trabalho.hidden = true;
      return;
    }
    definirStatus(
      (estado.demonstracao ? 'Demonstração carregada' : 'Importação concluída') +
        ` — ${m.produtos.length} produto(s) identificado(s).`,
      m.pendencias.some((p) => p.nivel === 'erro') ? 'alerta' : 'ok'
    );
    el.produtoSelect.innerHTML =
      '<option value="">Selecione um produto…</option>' +
      m.produtos.map((p) => `<option value="${esc(p.id)}">${esc(p.nome)}</option>`).join('');
    el.produtoSecao.hidden = false;
    el.trabalho.hidden = true;
    el.produtoInfo.innerHTML = '';
    if (m.produtos.length === 1) {
      el.produtoSelect.value = m.produtos[0].id;
      selecionarProduto(m.produtos[0].id);
    }
  }

  function limparModelo(pendencias) {
    estado.modelo = null;
    el.nProdutos.textContent = '0';
    el.nMateriais.textContent = '0';
    el.nPendencias.textContent = String(pendencias.length);
    renderizarPendencias(pendencias);
    el.produtoSecao.hidden = true;
    el.trabalho.hidden = true;
  }

  function renderizarPendencias(lista) {
    el.pendencias.hidden = !lista.length;
    const ordem = { erro: 0, aviso: 1, info: 2 };
    el.pendenciasLista.innerHTML = [...lista]
      .sort((a, b) => ordem[a.nivel] - ordem[b.nivel])
      .map((p) => `<li class="pend-${esc(p.nivel)}"><span class="tag">${esc(p.nivel)}</span> ${esc(p.mensagem)}</li>`)
      .join('');
  }

  el.produtoSelect.addEventListener('change', () => selecionarProduto(el.produtoSelect.value));

  function produtoAtual() {
    return estado.modelo && estado.modelo.produtos.find((p) => p.id === estado.produtoId);
  }
  function formAtual() {
    return estado.formularios[estado.produtoId];
  }

  function selecionarProduto(id) {
    estado.produtoId = id || null;
    estado.expandidos.clear();
    const p = produtoAtual();
    if (!p) {
      el.produtoInfo.innerHTML = '';
      el.trabalho.hidden = true;
      return;
    }
    if (!estado.formularios[p.id]) estado.formularios[p.id] = criarFormularioVazio(p, true);
    renderizarInfoProduto(p);
    preencherCamposProducao();
    el.trabalho.hidden = false;
    renderizarTudo();
  }

  function renderizarInfoProduto(p) {
    const mps = p.materiais.filter((m) => m.escopo === ESCOPO_FORMULACAO);
    const embs = p.materiais.filter((m) => m.escopo !== ESCOPO_FORMULACAO);
    const lista = (itens) =>
      itens.length
        ? `<ul class="lista-compacta">${itens
            .map((m) => `<li><code>${esc(m.codigo || 's/ código')}</code> ${esc(m.descricao)}${m.teor !== null ? ` <span class="badge roxo">teor ${esc(formatarPercentual(m.teor))}</span>` : ''}</li>`)
            .join('')}</ul>`
        : '<p class="muted">Nenhum item.</p>';
    el.produtoInfo.innerHTML = `
      <div class="info-grid">
        <div class="info importado"><span>Produto</span><strong>${esc(p.nome)}</strong></div>
        <div class="info importado"><span>Código</span><strong>${esc(p.codigo)}</strong></div>
        <div class="info importado"><span>Tipo de operação</span><strong>${esc(p.tipoOperacao)}</strong></div>
        <div class="info importado"><span>Unidade-base</span><strong>${esc(p.unidadeBase || 'Não identificada')}</strong></div>
      </div>
      <div class="info-colunas">
        <div>
          <h4>Apresentações vinculadas (${p.apresentacoes.length})</h4>
          ${
            p.apresentacoes.length
              ? `<ul class="lista-compacta">${p.apresentacoes
                  .map((a) => `<li><strong>${esc(nomeApresentacao(a))}</strong> <code>${esc(a.codigo)}</code> <span class="muted">vínculo: ${esc(a.vinculo)}</span></li>`)
                  .join('')}</ul>`
              : '<p class="muted">Nenhuma apresentação identificada.</p>'
          }
        </div>
        <div><h4>Matérias-primas (${mps.length})</h4>${lista(mps)}</div>
        <div><h4>Embalagens (${embs.length})</h4>${lista(embs)}</div>
      </div>`;
  }

  function preencherCamposProducao() {
    const f = formAtual();
    el.data.value = f.data;
    el.formulado.value = f.formulado;
    el.unidade.value = f.unidade;
    el.envasado.value = f.envasado;
    el.observacoes.value = f.observacoes;
    el.justDif.value = f.justificativaDiferenca;
    el.justApres.value = f.justificativaApresentacoes;
  }

  const camposProducao = [
    ['data', 'data'],
    ['formulado', 'formulado'],
    ['unidade', 'unidade'],
    ['envasado', 'envasado'],
    ['observacoes', 'observacoes'],
    ['justDif', 'justificativaDiferenca'],
    ['justApres', 'justificativaApresentacoes'],
  ];
  for (const [chaveEl, campo] of camposProducao) {
    const evento = el[chaveEl].tagName === 'SELECT' || el[chaveEl].type === 'date' ? 'change' : 'input';
    el[chaveEl].addEventListener(evento, () => {
      const f = formAtual();
      if (!f) return;
      f[campo] = el[chaveEl].value;
      atualizarCalculos();
    });
  }

  function renderizarTudo() {
    renderizarApresentacoes();
    renderizarParametros();
    renderizarTabela();
    atualizarCalculos();
  }

  function renderizarApresentacoes() {
    const p = produtoAtual();
    const f = formAtual();
    el.apresSecao.hidden = p.apresentacoes.length < 2;
    el.apresCorpo.innerHTML = p.apresentacoes
      .map(
        (a) => `<tr>
          <td><strong>${esc(nomeApresentacao(a))}</strong><br><code>${esc(a.codigo)}</code></td>
          <td><input class="editavel num" inputmode="decimal" data-apres="${esc(a.id)}" value="${esc(f.apresentacoes[a.id] || '')}" aria-label="Quantidade envasada ${esc(a.nome)}"></td>
          <td class="unid-apres">${esc(f.unidade || '—')}</td>
        </tr>`
      )
      .join('');
  }

  el.apresCorpo.addEventListener('input', (ev) => {
    const id = ev.target.dataset.apres;
    if (!id) return;
    formAtual().apresentacoes[id] = ev.target.value;
    atualizarCalculos();
  });

  function renderizarParametros() {
    const p = produtoAtual();
    const f = formAtual();
    const escopos = [];
    if (p.materiais.some((m) => m.escopo === ESCOPO_FORMULACAO) || !p.apresentacoes.length) {
      escopos.push({ id: ESCOPO_FORMULACAO, nome: 'Formulação', detectada: p.baseFormulacaoDetectada, ref: 'Quantidade formulada' });
    }
    for (const a of p.apresentacoes) {
      escopos.push({ id: a.id, nome: nomeApresentacao(a), detectada: a.baseDetectada, ref: 'Quantidade envasada da apresentação' });
    }
    el.parametrosCorpo.innerHTML = escopos
      .map(
        (e) => `<tr>
          <td>${esc(e.nome)}</td>
          <td>${esc(e.ref)}</td>
          <td class="importado">${e.detectada !== null ? esc(formatarNumero(e.detectada)) : '<span class="tag-pendente">não identificado</span>'}</td>
          <td><input class="parametro num" inputmode="decimal" data-base="${esc(e.id)}" value="${esc(f.bases[e.id] || '')}" placeholder="${e.detectada !== null ? esc(formatarNumero(e.detectada)) : 'obrigatório'}" aria-label="Volume-base ${esc(e.nome)}"></td>
        </tr>`
      )
      .join('');
  }

  el.parametrosCorpo.addEventListener('input', (ev) => {
    const id = ev.target.dataset.base;
    if (!id) return;
    formAtual().bases[id] = ev.target.value;
    atualizarCalculos();
  });

  // ----- Tabela de materiais -----
  const COLUNAS = [
    ['codigo', 'Código do insumo'],
    ['descricao', 'Descrição do material'],
    ['categoria', 'Categoria'],
    ['unidade', 'Un.'],
    ['usagem', 'Usagem LT'],
    ['base', 'Volume-base'],
    ['teorico', 'Consumo teórico'],
    ['perda', 'Perda contratual'],
    ['limiteSuperior', 'Limite máximo'],
    ['real', 'Consumo real'],
    ['variacao', 'Variação %'],
    ['excedente', 'Excedente contratual'],
    ['foraEspec', 'Fora da especificação?'],
    ['status', 'Status'],
    ['justificativa', 'Justificativa'],
    ['acao', 'Ação'],
  ];
  el.tabelaCabecalho.innerHTML =
    '<tr>' +
    COLUNAS.map(([id, rotulo]) =>
      ['justificativa', 'acao'].includes(id)
        ? `<th>${esc(rotulo)}</th>`
        : `<th data-ordem="${id}" tabindex="0" role="button" aria-label="Ordenar por ${esc(rotulo)}">${esc(rotulo)} <span class="seta"></span></th>`
    ).join('') +
    '</tr>';

  el.tabelaCabecalho.addEventListener('click', (ev) => ordenarPor(ev.target.closest('th[data-ordem]')));
  el.tabelaCabecalho.addEventListener('keydown', (ev) => {
    if (ev.key === 'Enter' || ev.key === ' ') {
      ev.preventDefault();
      ordenarPor(ev.target.closest('th[data-ordem]'));
    }
  });
  function ordenarPor(th) {
    if (!th) return;
    const chave = th.dataset.ordem;
    if (estado.filtros.ordem === chave) estado.filtros.direcao *= -1;
    else {
      estado.filtros.ordem = chave;
      estado.filtros.direcao = 1;
    }
    renderizarTabela();
  }

  el.busca.addEventListener('input', () => {
    estado.filtros.busca = el.busca.value;
    renderizarTabela();
  });
  el.filtroCategoria.addEventListener('change', () => {
    estado.filtros.categoria = el.filtroCategoria.value;
    renderizarTabela();
  });
  el.filtroStatus.addEventListener('change', () => {
    estado.filtros.status = el.filtroStatus.value;
    renderizarTabela();
  });

  function classeStatus(status) {
    return {
      [STATUS.DENTRO]: 'verde',
      [STATUS.ABAIXO]: 'vermelho',
      [STATUS.ACIMA]: 'vermelho',
      [STATUS.PENDENTE]: 'laranja',
    }[status];
  }

  function linhasFiltradas(rep) {
    const { busca, categoria, status, ordem, direcao } = estado.filtros;
    const termo = normalizarTexto(busca);
    let linhas = rep.linhas.filter((l) => {
      if (termo && !normalizarTexto((l.codigo || '') + ' ' + l.descricao).includes(termo)) return false;
      if (categoria && l.categoria !== categoria) return false;
      if (status && l.status !== status) return false;
      return true;
    });
    const valor = (l) => {
      if (ordem === 'justificativa' || ordem === 'acao') return '';
      if (ordem === 'real') return l.realConvertido;
      return l[ordem];
    };
    linhas = [...linhas].sort((a, b) => {
      const va = valor(a);
      const vb = valor(b);
      if (va === vb) return a.linha - b.linha;
      if (va === null || va === undefined) return 1;
      if (vb === null || vb === undefined) return -1;
      if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * direcao;
      return String(va).localeCompare(String(vb), 'pt-BR', { numeric: true }) * direcao;
    });
    return linhas;
  }

  function renderizarTabela() {
    const p = produtoAtual();
    if (!p) return;
    const f = formAtual();
    const rep = calcularReporte(p, f);
    const linhas = linhasFiltradas(rep);
    el.contadorTabela.textContent = `${linhas.length} de ${rep.linhas.length} materiais`;
    for (const th of el.tabelaCabecalho.querySelectorAll('th[data-ordem]')) {
      const ativo = th.dataset.ordem === estado.filtros.ordem;
      th.classList.toggle('ordenado', ativo);
      th.querySelector('.seta').textContent = ativo ? (estado.filtros.direcao > 0 ? '▲' : '▼') : '';
      th.setAttribute('aria-sort', ativo ? (estado.filtros.direcao > 0 ? 'ascending' : 'descending') : 'none');
    }
    const opcoesUnidade = (m, atual) => {
      const grupo = UNIDADES[m.unidade] ? UNIDADES[m.unidade].grupo : null;
      const lista = grupo ? Object.keys(UNIDADES).filter((u) => UNIDADES[u].grupo === grupo) : [m.unidade].filter(Boolean);
      const todas = [...new Set([...lista, atual, ...Object.keys(UNIDADES)])].filter(Boolean);
      return todas.map((u) => `<option ${u === atual ? 'selected' : ''}>${esc(u)}</option>`).join('');
    };
    el.tabelaCorpo.innerHTML =
      linhas
        .map((l) => {
          const st = f.materiais[l.id];
          const expandido = estado.expandidos.has(l.id);
          const desvio = l.status === STATUS.ABAIXO || l.status === STATUS.ACIMA;
          const vinculoSelect = l.embalagemNaFormulacao
            ? `<label class="vinculo">Vínculo:
                 <select class="editavel" data-mat="${l.id}" data-campo="vinculo">
                   <option value="">Pendente de revisão</option>
                   ${p.apresentacoes.map((a) => `<option value="${esc(a.id)}" ${st.vinculo === a.id ? 'selected' : ''}>${esc(a.nome)}</option>`).join('')}
                   <option value="${VINCULO_TOTAL}" ${st.vinculo === VINCULO_TOTAL ? 'selected' : ''}>Total envasado</option>
                 </select></label>`
            : '';
          const perdaCelula = l.perdaAusente
            ? `<input class="parametro num curto" inputmode="decimal" placeholder="ex.: 2%" data-mat="${l.id}" data-campo="perdaManual" value="${esc(st.perdaManual)}" aria-label="Perda contratual">`
            : esc(formatarPercentual(l.perda));
          const principal = `<tr class="linha-material ${desvio ? 'desvio' : ''} ${l.status === STATUS.PENDENTE ? 'pendente' : ''}" data-linha="${l.id}">
            <td class="importado"><code>${esc(l.codigo || 's/ código')}</code></td>
            <td class="importado desc">${esc(l.descricao)}
              <div class="sub">${esc(l.escopoNome)}${l.teor !== null ? ` · <span class="badge roxo">teor ${esc(formatarPercentual(l.teor))}</span>` : ''}${l.duplicado ? ' · <span class="badge laranja">duplicado</span>' : ''}</div>
              ${vinculoSelect}</td>
            <td><select class="editavel" data-mat="${l.id}" data-campo="categoria" aria-label="Categoria">${CATEGORIAS.map((c) => `<option ${c === l.categoria ? 'selected' : ''}>${esc(c)}</option>`).join('')}</select></td>
            <td class="importado">${esc(l.unidade || '—')}</td>
            <td class="importado num">${esc(formatarNumero(l.usagem))}</td>
            <td class="parametro-cel num" data-c="base">${esc(formatarNumero(l.base))}</td>
            <td class="num calc" data-c="teorico">${esc(formatarNumero(l.teorico))}</td>
            <td class="parametro-cel num">${perdaCelula}</td>
            <td class="num calc" data-c="limite">${esc(formatarNumero(l.limiteSuperior))}</td>
            <td><input class="editavel num" inputmode="decimal" data-mat="${l.id}" data-campo="real" value="${esc(st.real)}" aria-label="Consumo real"></td>
            <td class="num calc" data-c="variacao">${esc(formatarPercentual(l.variacao))}</td>
            <td class="num calc" data-c="excedente">${esc(formatarNumero(l.excedente))}</td>
            <td data-c="foraEspec">${celulaForaEspec(l, st)}</td>
            <td data-c="status"><span class="badge ${classeStatus(l.status)}" title="${esc(l.motivoPendencia || '')}">${esc(l.status)}</span>${l.motivoPendencia ? `<div class="sub">${esc(l.motivoPendencia)}</div>` : ''}</td>
            <td data-c="justificativa">${celulaJustificativa(l)}</td>
            <td><button type="button" class="btn-link" data-detalhe="${l.id}" aria-expanded="${expandido}">${expandido ? 'Fechar' : 'Detalhar'}</button>
              <div class="sub" data-c="acao">${esc(st.acao ? st.acao.slice(0, 40) : '')}</div></td>
          </tr>`;
          const detalhe = expandido
            ? `<tr class="linha-detalhe" data-detalhe-de="${l.id}"><td colspan="${COLUNAS.length}">
                <div class="detalhe-grid">
                  <label>Consumo real<input class="editavel num" inputmode="decimal" data-mat="${l.id}" data-campo="real" value="${esc(st.real)}"></label>
                  <label>Unidade<select class="editavel" data-mat="${l.id}" data-campo="unidadeReal">${opcoesUnidade(l, st.unidadeReal || l.unidade)}</select></label>
                  <label>Motivo da variação ${l.exigeJustificativa ? '<em>*</em>' : ''}<select class="editavel" data-mat="${l.id}" data-campo="motivo"><option value="">Selecione…</option>${MOTIVOS_VARIACAO.map((mv) => `<option ${mv === st.motivo ? 'selected' : ''}>${esc(mv)}</option>`).join('')}</select></label>
                  <label>Número do lote (opcional)<input class="editavel" data-mat="${l.id}" data-campo="lote" value="${esc(st.lote)}"></label>
                  <label class="largo">Descrição da ocorrência ${l.exigeJustificativa ? '<em>*</em>' : ''}<textarea class="editavel" rows="2" data-mat="${l.id}" data-campo="descricao">${esc(st.descricao)}</textarea></label>
                  <label class="largo">Ação imediata ${l.exigeJustificativa ? '<em>*</em>' : ''}<textarea class="editavel" rows="2" data-mat="${l.id}" data-campo="acao">${esc(st.acao)}</textarea></label>
                  <label>Investigação necessária?<select class="editavel" data-mat="${l.id}" data-campo="investigacao"><option ${st.investigacao === 'Não' ? 'selected' : ''}>Não</option><option ${st.investigacao === 'Sim' ? 'selected' : ''}>Sim</option></select></label>
                  <label>Responsável pela investigação ${st.investigacao === 'Sim' ? '<em>*</em>' : ''}<input class="editavel" data-mat="${l.id}" data-campo="responsavel" value="${esc(st.responsavel)}"></label>
                  <label>Prazo ${st.investigacao === 'Sim' ? '<em>*</em>' : ''}<input type="date" class="editavel" data-mat="${l.id}" data-campo="prazo" value="${esc(st.prazo)}"></label>
                  <label class="largo">Observações adicionais<textarea class="editavel" rows="2" data-mat="${l.id}" data-campo="observacoes">${esc(st.observacoes)}</textarea></label>
                  ${l.analise ? `<div class="largo importado nota">Análise registrada na planilha: ${esc(l.analise)}</div>` : ''}
                  <div class="largo faltando" data-c="faltando">${l.camposFaltando.length ? 'Campos obrigatórios pendentes: ' + esc(l.camposFaltando.join(', ')) : ''}</div>
                </div></td></tr>`
            : '';
          return principal + detalhe;
        })
        .join('') || `<tr><td colspan="${COLUNAS.length}" class="vazio">Nenhum material encontrado com os filtros atuais.</td></tr>`;
  }

  function celulaForaEspec(l, st) {
    if (l.foraEspecAutomatico) {
      return '<span class="badge vermelho" title="Marcado automaticamente pelo desvio de consumo">Sim (automático)</span>';
    }
    return `<select class="editavel" data-mat="${l.id}" data-campo="foraEspec" aria-label="Houve consumo fora da especificação?">
      <option ${st.foraEspec !== 'Sim' ? 'selected' : ''}>Não</option><option ${st.foraEspec === 'Sim' ? 'selected' : ''}>Sim</option></select>`;
  }

  function celulaJustificativa(l) {
    if (!l.exigeJustificativa) return '<span class="muted">—</span>';
    return l.justificativaPendente
      ? '<span class="badge vermelho">Obrigatória — pendente</span>'
      : '<span class="badge verde">Preenchida</span>';
  }

  // Campos que exigem redesenhar a tabela (mudam estrutura, filtro ou status).
  const CAMPOS_ESTRUTURAIS = new Set(['categoria', 'vinculo', 'foraEspec', 'investigacao', 'unidadeReal']);

  el.tabelaCorpo.addEventListener('input', (ev) => {
    const alvo = ev.target;
    const id = alvo.dataset.mat;
    const campo = alvo.dataset.campo;
    if (!id || !campo || CAMPOS_ESTRUTURAIS.has(campo)) return;
    formAtual().materiais[id][campo] = alvo.value;
    for (const outro of el.tabelaCorpo.querySelectorAll(`[data-mat="${id}"][data-campo="${campo}"]`)) {
      if (outro !== alvo) outro.value = alvo.value;
    }
    atualizarCalculos();
  });

  el.tabelaCorpo.addEventListener('change', (ev) => {
    const alvo = ev.target;
    const id = alvo.dataset.mat;
    const campo = alvo.dataset.campo;
    if (!id || !campo) return;
    formAtual().materiais[id][campo] = alvo.value;
    if (CAMPOS_ESTRUTURAIS.has(campo)) {
      if (campo === 'foraEspec' && alvo.value === 'Sim') estado.expandidos.add(id);
      renderizarTabela();
      atualizarCalculos();
    } else if (campo === 'real' || campo === 'motivo' || campo === 'prazo') {
      // Ao sair do campo, abre o detalhe quando surgir desvio.
      const rep = calcularReporte(produtoAtual(), formAtual());
      const l = rep.linhas.find((x) => x.id === id);
      if (l && l.exigeJustificativa && !estado.expandidos.has(id)) {
        estado.expandidos.add(id);
        renderizarTabela();
      }
      atualizarCalculos();
    }
  });

  el.tabelaCorpo.addEventListener('click', (ev) => {
    const btn = ev.target.closest('[data-detalhe]');
    if (!btn) return;
    const id = btn.dataset.detalhe;
    if (estado.expandidos.has(id)) estado.expandidos.delete(id);
    else estado.expandidos.add(id);
    renderizarTabela();
  });

  // Atualiza valores calculados sem redesenhar inputs (preserva o foco).
  function atualizarCalculos() {
    const p = produtoAtual();
    if (!p) return;
    const f = formAtual();
    const rep = calcularReporte(p, f);

    el.diferenca.textContent = rep.diferenca === null ? '—' : `${formatarNumero(rep.diferenca)} ${f.unidade || ''}`;
    el.diferenca.className = 'valor-calculado ' + (rep.exigeJustificativaDiferenca ? 'laranja' : rep.diferenca === null ? '' : 'verde');
    el.justDifBox.hidden = !rep.exigeJustificativaDiferenca;
    el.justDif.classList.toggle('invalido', rep.exigeJustificativaDiferenca && !f.justificativaDiferenca.trim());

    for (const [chave, campo] of [['formulado', 'formulado'], ['envasado', 'envasado']]) {
      const t = String(f[campo] || '').trim();
      const n = interpretarNumero(t);
      el[chave].classList.toggle('invalido', t !== '' && (n === null || n < 0));
    }

    for (const td of el.apresCorpo.querySelectorAll('.unid-apres')) td.textContent = f.unidade || '—';
    for (const input of el.apresCorpo.querySelectorAll('input[data-apres]')) {
      const t = String(input.value || '').trim();
      const n = interpretarNumero(t);
      input.classList.toggle('invalido', t !== '' && (n === null || n < 0));
    }
    if (p.apresentacoes.length > 1) {
      el.apresTotal.innerHTML = `Soma das apresentações: <strong>${esc(formatarNumero(rep.somaApresentacoes))}</strong> ${esc(f.unidade || '')}
        · Total envasado: <strong>${esc(formatarNumero(rep.envasado))}</strong>
        · Diferença: <strong>${esc(formatarNumero(rep.diferencaApresentacoes))}</strong>`;
      el.apresAlerta.hidden = !rep.divergenciaApresentacoes;
      el.justApresBox.hidden = !rep.divergenciaApresentacoes;
    }

    renderizarCards(rep, f);

    for (const l of rep.linhas) {
      const tr = el.tabelaCorpo.querySelector(`tr[data-linha="${l.id}"]`);
      if (!tr) continue;
      const set = (c, html) => {
        const td = tr.querySelector(`[data-c="${c}"]`);
        if (td) td.innerHTML = html;
      };
      set('base', esc(formatarNumero(l.base)));
      set('teorico', esc(formatarNumero(l.teorico)));
      set('limite', esc(formatarNumero(l.limiteSuperior)));
      set('variacao', esc(formatarPercentual(l.variacao)));
      set('excedente', esc(formatarNumero(l.excedente)));
      set(
        'status',
        `<span class="badge ${classeStatus(l.status)}">${esc(l.status)}</span>${l.motivoPendencia ? `<div class="sub">${esc(l.motivoPendencia)}</div>` : ''}`
      );
      set('justificativa', celulaJustificativa(l));
      const st = f.materiais[l.id];
      const foraTd = tr.querySelector('[data-c="foraEspec"]');
      const temSelect = foraTd && foraTd.querySelector('select');
      if (foraTd && (l.foraEspecAutomatico ? temSelect : !temSelect)) foraTd.innerHTML = celulaForaEspec(l, st);
      set('acao', esc(st.acao ? st.acao.slice(0, 40) : ''));
      const desvio = l.status === STATUS.ABAIXO || l.status === STATUS.ACIMA;
      tr.classList.toggle('desvio', desvio);
      tr.classList.toggle('pendente', l.status === STATUS.PENDENTE);
      const inputReal = tr.querySelector('[data-campo="real"]');
      if (inputReal) inputReal.classList.toggle('invalido', rep.erros.some((e) => e.startsWith(`${l.codigo || 'Material'} — consumo real`)) || l.motivoPendencia === 'Unidade do consumo real incompatível com a unidade do material');
      const det = el.tabelaCorpo.querySelector(`tr[data-detalhe-de="${l.id}"] [data-c="faltando"]`);
      if (det) det.textContent = l.camposFaltando.length ? 'Campos obrigatórios pendentes: ' + l.camposFaltando.join(', ') : '';
    }

    renderizarValidacoes(rep);
  }

  function renderizarCards(rep, f) {
    const u = f.unidade ? ` ${f.unidade}` : '';
    const cards = [
      ['Quantidade formulada', formatarNumero(rep.formulado) + (rep.formulado !== null ? u : ''), 'azul'],
      ['Quantidade envasada', formatarNumero(rep.envasado) + (rep.envasado !== null ? u : ''), 'azul'],
      ['Diferença', formatarNumero(rep.diferenca) + (rep.diferenca !== null ? u : ''), rep.exigeJustificativaDiferenca ? 'laranja' : 'cinza'],
      ['Total de materiais', rep.contagem.total, 'cinza'],
      ['Dentro do esperado', rep.contagem.dentro, 'verde'],
      ['Abaixo do teórico', rep.contagem.abaixo, rep.contagem.abaixo ? 'vermelho' : 'cinza'],
      ['Acima do contrato', rep.contagem.acima, rep.contagem.acima ? 'vermelho' : 'cinza'],
      ['Pendentes', rep.contagem.pendentes, rep.contagem.pendentes ? 'laranja' : 'cinza'],
      ['Justificativas pendentes', rep.contagem.justificativasPendentes, rep.contagem.justificativasPendentes ? 'vermelho' : 'verde'],
    ];
    el.cards.innerHTML = cards
      .map(([t, v, c]) => `<div class="card ${c}"><span>${esc(t)}</span><strong>${esc(v)}</strong></div>`)
      .join('');
  }

  function renderizarValidacoes(rep) {
    const itens = [
      ...rep.erros.map((e) => `<li class="pend-erro"><span class="tag">erro</span> ${esc(e)}</li>`),
      ...rep.avisos.map((a) => `<li class="pend-aviso"><span class="tag">aviso</span> ${esc(a)}</li>`),
    ];
    el.validacoes.innerHTML = itens.length ? itens.join('') : '<li class="pend-ok">Nenhuma inconsistência encontrada.</li>';
    el.btnExcel.disabled = !rep.podeExportar || !obterXLSX();
    el.btnCSV.disabled = !rep.podeExportar;
    el.exportMsg.textContent = rep.podeExportar
      ? rep.avisos.length
        ? 'Exportação liberada. Há avisos não bloqueantes listados em Validações.'
        : 'Exportação liberada.'
      : `Exportação bloqueada: ${rep.erros.length} erro(s) crítico(s) em Validações.`;
    el.exportMsg.className = rep.podeExportar ? 'msg ok' : 'msg erro';
  }

  function exportar(tipo) {
    const p = produtoAtual();
    const f = formAtual();
    const rep = calcularReporte(p, f);
    if (!rep.podeExportar) {
      renderizarValidacoes(rep);
      return;
    }
    const dados = montarDadosExportacao(p, f, rep, estado.modelo.pendencias);
    try {
      if (tipo === 'xlsx') {
        const XL = obterXLSX();
        XL.writeFile(gerarPastaExportacao(XL, dados), nomeArquivoReporte(p, f.data, 'xlsx'), { compression: true });
      } else {
        const blob = new Blob([gerarCSV(dados)], { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = nomeArquivoReporte(p, f.data, 'csv');
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      }
      el.exportMsg.textContent = `Arquivo ${nomeArquivoReporte(p, f.data, tipo)} gerado.`;
      el.exportMsg.className = 'msg ok';
    } catch (e) {
      el.exportMsg.textContent = 'Falha ao gerar o arquivo de exportação.';
      el.exportMsg.className = 'msg erro';
    }
  }

  el.btnExcel.addEventListener('click', () => exportar('xlsx'));
  el.btnCSV.addEventListener('click', () => exportar('csv'));
  el.btnPDF.addEventListener('click', () => {
    // Abre todos os detalhes com justificativa para que saiam na impressão.
    const rep = calcularReporte(produtoAtual(), formAtual());
    for (const l of rep.linhas) if (l.exigeJustificativa) estado.expandidos.add(l.id);
    renderizarTabela();
    atualizarCalculos();
    window.print();
  });

  el.btnLimpar.addEventListener('click', () => {
    if (!estado.limpezaPendente) {
      el.btnLimpar.textContent = 'Confirmar limpeza';
      el.btnLimpar.classList.add('confirmar');
      estado.limpezaPendente = setTimeout(() => {
        el.btnLimpar.textContent = 'Limpar preenchimento';
        el.btnLimpar.classList.remove('confirmar');
        estado.limpezaPendente = null;
      }, 4000);
      return;
    }
    clearTimeout(estado.limpezaPendente);
    estado.limpezaPendente = null;
    el.btnLimpar.textContent = 'Limpar preenchimento';
    el.btnLimpar.classList.remove('confirmar');
    const p = produtoAtual();
    estado.formularios[p.id] = criarFormularioVazio(p, false);
    estado.expandidos.clear();
    preencherCamposProducao();
    renderizarTudo();
    el.exportMsg.textContent = 'Preenchimento limpo.';
    el.exportMsg.className = 'msg ok';
  });
}

/* =====================================================================
 * EXPORTS (Node, para testes) E INICIALIZAÇÃO (navegador)
 * ===================================================================== */

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    ANONIMIZAR_PRODUTOS,
    OCULTAR_CODIGOS_PRODUTOS,
    CONFIG,
    STATUS,
    CATEGORIAS,
    normalizarTexto,
    interpretarNumero,
    interpretarPercentual,
    formatarNumero,
    formatarPercentual,
    normalizarUnidade,
    unidadesCompativeis,
    converterUnidade,
    calcularConsumoTeorico,
    avaliarConsumo,
    exigeJustificativa,
    calcularDiferencaProducao,
    somarApresentacoes,
    classificarMaterial,
    separarCodigos,
    mascararTexto,
    analisarFormulaTeorica,
    analisarPasta,
    interpretarAba,
    criarPastaDemonstracao,
    criarFormularioVazio,
    calcularReporte,
    montarDadosExportacao,
    gerarCSV,
    gerarPastaExportacao,
    nomeArquivoReporte,
  };
}

if (typeof window !== 'undefined' && typeof document !== 'undefined') {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciarApp);
  else iniciarApp();
}
