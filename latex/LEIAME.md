# TCC em LaTeX no modelo FT/UNICAMP

Versão LaTeX do `tcc/TCC_exo1_exo2.docx`. Ela usa o modelo de teses e dissertações da FT/UNICAMP (André Leon Sampaio Gradvohl, versão de 14 de abril de 2026). O arquivo `tese-FT.cls` não foi alterado.

## Compilar

- **Overleaf:** em Novo projeto → Enviar projeto, envie o `.zip` desta pasta e use o compilador pdfLaTeX. O Overleaf roda o biber sozinho.
- **Local:** `latexmk -pdf tese.tex`, que roda pdflatex e biber. Pede o TeX Live com os pacotes `biblatex-abnt`, `libertine`, `libertinust1math`, `xltabular`, `enumitem` e `caption`.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `tese.tex` | Arquivo principal: dados da capa e da folha de rosto, ordem dos elementos |
| `preambulo.tex` | Pacotes e comandos acrescentados ao modelo |
| `capitulos/*.tex` | Os cinco capítulos, gerados a partir do DOCX por `tcc/gerar_latex.py` |
| `bibliografia.bib` | As 47 referências da lista do DOCX |
| `resumo.tex`, `agradecimentos.tex` | Elementos pré-textuais |
| `figuras/` | As 12 figuras, extraídas do DOCX |
| `logotipos/logo-fca.png` | Recorte do logotipo enviado com o modelo |
| `tese-FT.cls`, `README.md`, `CHANGELOG.md` | Arquivos do modelo, sem alteração |
| `tese.pdf` | PDF compilado |

Rótulos usados nas remissões:
- `sec:3B.10`: seção 3B.10; `sec:4`: capítulo 4;
- `eq:47`: Equação (47);
- `tab:...` e `fig:...`: tabelas e figuras, com o nome tirado da legenda (por exemplo, `tab:comparacao-dois-dispositivos-analisados`).

## O que falta completar

Nada. Os agradecimentos estão em `agradecimentos.tex`; dedicatória e epígrafe, se houver, ficam no mesmo arquivo. Não há ficha catalográfica.

Dados já preenchidos: unidade (FCA), banca (os três da FCA/UNICAMP) e data da defesa (18/11/2026, em `\datadadefesa`). O resumo e o abstract (`resumo.tex`) não existem no DOCX e foram redigidos a partir das conclusões, com os números do texto.

A folha de aprovação, com a banca e a data, já aparece nesta versão por causa do `\folhadeaprovacaoantecipada` no `tese.tex` (definido em `preambulo.tex`); sem ele, o modelo só a mostra na versão final. Depois da defesa, apague a linha `\finalversionfalse` do `tese.tex`: ela mantém na folha de rosto o texto da versão entregue à banca.

## Diferenças em relação ao DOCX

O texto dos parágrafos, tabelas, legendas, fontes e notas é o do DOCX. Mudou só o que o modelo ou a norma impõem:

- **Títulos.** Os títulos de capítulo e de parte estão em caixa normal ("Introdução", "Exoesqueleto 1: US 9.889.554 B2"), como no modelo.
- **Legendas.** Todas seguem o formato "Tabela 1: ...". No DOCX, as legendas do exoesqueleto 1 usavam travessão.
- **Citações.** Saem em caixa normal, como "(Spada et al., 2017)", pela NBR 10520:2023 adotada no modelo. Na lista de referências, o sobrenome também sai em caixa normal.
- **"(SHEN et al., 2020)"** passa a "(Shen; Ferguson; Rosen, 2020)": a obra tem três autores, e a norma cita os três.
- **Referências não citadas.** Duas referências da lista não são citadas no texto: Foroutannia e Mohammadian (2026) e Kim, H. et al. (2012). Continuam na lista por causa do `\nocite{*}`.
- **Posição de figuras e tabelas.** As figuras e as tabelas curtas são flutuantes e podem mudar de página em relação ao DOCX. As tabelas 6, 14, 16 e 25 podem atravessar páginas e repetem o cabeçalho na continuação. A numeração continua corrida, como no DOCX: Figura 1 a 12, Tabela 1 a 26, Equação (1) a (52). Para numerar por capítulo, veja o comentário em `preambulo.tex`.
- **Ligações.** As caixas em volta das ligações são o padrão do modelo e aparecem só na tela. Para escondê-las, acrescente `\hypersetup{hidelinks}` ao `preambulo.tex`.

## Versão em Word no mesmo formato

`tcc/TCC_modelo_FT.docx` reproduz em Word a formatação deste PDF: capa, folha de rosto, títulos "Capítulo N", cabeçalho corrente, tabelas com filetes, legendas acima, citações e referências como o biblatex as imprime e a fonte Linux Libertine O, embutida no arquivo. Ele é gerado por `tcc/gerar_docx_modelo.py`, que lê o DOCX fundido e os dados de `tese.tex`, `resumo.tex`, `agradecimentos.tex` e `bibliografia.bib`. Por isso, depois de mudar a capa, a banca, os agradecimentos ou o resumo aqui, basta rodar o gerador de novo. `tcc/verificar_docx_modelo.py` confere o resultado contra este PDF.

## Regenerar e verificar

```
python3 tcc/gerar_latex.py tcc/TCC_exo1_exo2.docx latex/
cd latex && latexmk -pdf tese.tex && cd ..
python3 tcc/verificar_latex.py
```

O primeiro comando sobrescreve `capitulos/` e `figuras/`. Depois que o texto passar a ser editado no LaTeX, não o rode de novo.

O terceiro confere o PDF contra o DOCX: parágrafos, títulos, legendas, células de tabela, numeração das equações, referências e remissões indefinidas. O resultado fica em `tcc/verificacao_latex.md`.
