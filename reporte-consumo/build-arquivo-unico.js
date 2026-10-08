'use strict';
// Gera reporte-consumo-completo.html: index.html com styles.css, SheetJS e app.js
// embutidos, para abrir com duplo clique sem depender dos outros arquivos.
// Uso: node build-arquivo-unico.js

const fs = require('node:fs');
const path = require('node:path');

const raiz = __dirname;
const ler = (arquivo) => fs.readFileSync(path.join(raiz, arquivo), 'utf8');
// Impede que um "</script>" dentro do JavaScript encerre a tag antes da hora.
const protegerScript = (js) => js.replace(/<\/script/gi, '<\\/script');

let html = ler('index.html');

const substituir = (padrao, conteudo, descricao) => {
  if (!padrao.test(html)) throw new Error(`Trecho não encontrado em index.html: ${descricao}`);
  html = html.replace(padrao, () => conteudo);
};

substituir(/<link rel="stylesheet" href="styles\.css">/, `<style>\n${ler('styles.css')}\n</style>`, 'styles.css');
substituir(
  /<script src="lib\/xlsx\.full\.min\.js"><\/script>/,
  `<script>\n${protegerScript(ler('lib/xlsx.full.min.js'))}\n</script>`,
  'lib/xlsx.full.min.js'
);
substituir(/<script src="app\.js"><\/script>/, `<script>\n${protegerScript(ler('app.js'))}\n</script>`, 'app.js');

const destino = path.join(raiz, 'reporte-consumo-completo.html');
fs.writeFileSync(destino, html);
console.log(`Gerado ${path.basename(destino)} (${Math.round(fs.statSync(destino).size / 1024)} KB)`);
