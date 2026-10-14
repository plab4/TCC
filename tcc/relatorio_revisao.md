# Relatório da revisão técnico-científica do TCC

**Trabalho:** *Modelagem e simulação de mecanismos passivos de apoio ao braço*
**Escopo:**
- revisão integral dos capítulos 3 (Materiais e Métodos) e 4 (Resultados e Discussão);
- redação do capítulo 5 (Conclusão);
- auditoria do modelo Python;
- atualização da documentação `DERIVATION.md`.

**Data:** outubro de 2026

## 1. Arquivos

| arquivo | situação |
|---|---|
| `tcc/TCC.docx` | cópia do original recebido, sem alteração (md5 44cf176e…) |
| `backup/TCC_original.docx` | cópia de segurança do original (mesmo md5) |
| `backup/DERIVATION_antes_revisao.md` | cópia de segurança da MD antes da revisão |
| `tcc/TCC_revisado.docx` | **criado**: TCC com os capítulos 3 e 4 revisados e o capítulo 5 novo |
| `tcc/conclusao.txt` | **criado**: texto do capítulo 5, idêntico ao do DOCX |
| `tcc/relatorio_revisao.md` | **criado**: este relatório |
| `DERIVATION.md` | **modificado** no lugar: números conferidos e seção "Revisão do TCC" |
| `tcc_resultados.py` | **criado**: gera todos os números e figuras citados no TCC |
| `results/tcc_numeros.json`, `results/tcc_tabela_patente.csv` | **criados** por `tcc_resultados.py` |
| `results/tcc_fig1_geometria.png` … `tcc_fig5_normalizado.png` | **criados**: as cinco figuras do TCC |

Ficaram **intocados**, de propósito:
- `torque_model.py` (`git diff` vazio);
- `patent_data.py`;
- `calibration.py` e `svaj.py` (obsoletos);
- os gráficos 1 a 4 e as tabelas `varredura_H_*.csv`.

Os arquivos `vh_*` foram regravados pela varredura e saíram idênticos aos versionados.

## 2. Ordem de trabalho

1. Inspeção do DOCX e do projeto.
2. Auditoria dos dados e rastreabilidade dos 29 pontos (seção 3 deste relatório).
3. Verificação da matemática original.
4. Revisão do capítulo 3.
5. Revisão do capítulo 4.
6. Tabelas, figuras e referências.
7. Atualização da MD.
8. Redação da conclusão.
9. Verificação final.

A verificação final consistiu em:
- validação do DOCX contra o esquema OOXML;
- renderização em PDF e inspeção página a página;
- conferência dos números contra o JSON;
- `pytest`.

Todo número novo ou alterado no texto vem de `results/tcc_numeros.json`, gerado por `python tcc_resultados.py`. O script importa o modelo vigente, passa h explicitamente e não altera parâmetro algum.

## 3. Auditoria dos dados da patente

São 29 pontos (`patent_data.py`), na ordem da extração, sem reordenação, interpolação nem suavização.
- θ* vai de 42,90947° a 193,017°.
- O maior valor é 147,3101 u.p., em θ* = 123,196°.
- A média é 81,840 u.p.
- O espaçamento em θ* vai de 2,87° a 8,03°.
- A ordenada não tem unidade declarada na fonte (u.p.).
- O método de digitalização e a incerteza não estão documentados no repositório.

**Rastreabilidade.** Modelo com K = 174,68, h = 22,701 mm e X_pose = 37,383 mm; resíduo = modelo − extraído. A mesma tabela está no TCC (Tabela 4) e em `results/tcc_tabela_patente.csv`.

| nº | θ* (°) | φ_pat (°) | elevação (°) | extraído (u.p.) | modelo −τ (u.p.) | resíduo (u.p.) |
|---|---|---|---|---|---|---|
| 1 | 193,01700 | −60,000 | 30,000 | 0,443038 | −1,709 | −2,152 |
| 2 | 189,14603 | −56,129 | 33,871 | 11,518990 | 11,908 | 0,389 |
| 3 | 185,84854 | −52,832 | 37,168 | 23,702530 | 23,428 | −0,274 |
| 4 | 181,69084 | −48,674 | 41,326 | 38,101270 | 37,729 | −0,372 |
| 5 | 177,67650 | −44,660 | 45,340 | 50,506330 | 51,171 | 0,664 |
| 6 | 171,36825 | −38,351 | 51,649 | 70,000000 | 71,259 | 1,259 |
| 7 | 167,35392 | −34,337 | 55,663 | 81,962030 | 83,202 | 1,240 |
| 8 | 162,76610 | −29,749 | 60,251 | 94,145570 | 95,882 | 1,736 |
| 9 | 155,31091 | −22,294 | 67,706 | 111,867100 | 113,925 | 2,058 |
| 10 | 148,42919 | −15,412 | 74,588 | 125,158200 | 127,378 | 2,220 |
| 11 | 143,26790 | −10,251 | 79,749 | 133,354400 | 135,260 | 1,906 |
| 12 | 135,23922 | −2,222 | 87,778 | 142,436700 | 143,561 | 1,124 |
| 13 | 128,93098 | 4,086 | 94,086 | 146,202500 | 146,647 | 0,445 |
| 14 | 123,19621 | 9,821 | 99,821 | 147,310100 | 146,874 | −0,436 |
| 15 | 115,16754 | 17,849 | 107,849 | 144,651900 | 143,291 | −1,361 |
| 16 | 108,28582 | 24,731 | 114,731 | 138,892400 | 136,943 | −1,950 |
| 17 | 100,83062 | 32,186 | 122,186 | 130,031600 | 127,175 | −2,856 |
| 18 | 94,80911 | 38,208 | 128,208 | 120,063300 | 117,532 | −2,532 |
| 19 | 88,50087 | 44,516 | 134,516 | 108,987300 | 106,203 | −2,784 |
| 20 | 83,33958 | 49,677 | 139,677 | 98,354430 | 96,324 | −2,030 |
| 21 | 78,03492 | 54,982 | 144,982 | 87,500000 | 85,889 | −1,611 |
| 22 | 72,58689 | 60,430 | 150,430 | 75,981010 | 75,155 | −0,826 |
| 23 | 68,14245 | 64,875 | 154,875 | 66,455700 | 66,572 | 0,117 |
| 24 | 62,40768 | 70,609 | 160,609 | 55,158230 | 55,955 | 0,797 |
| 25 | 57,81987 | 75,197 | 165,197 | 46,518990 | 47,977 | 1,458 |
| 26 | 54,37901 | 78,638 | 168,638 | 39,873420 | 42,356 | 2,482 |
| 27 | 50,93815 | 82,079 | 172,079 | 34,335440 | 37,078 | 2,743 |
| 28 | 45,77686 | 87,240 | 177,240 | 27,025320 | 29,845 | 2,819 |
| 29 | 42,90947 | 90,108 | 180,108 | 22,816460 | 26,188 | 3,371 |

## 4. Verificação da matemática original

A formulação do autor foi preservada no texto e conferida numericamente.

| formulação original | onde está no TCC revisado | verificação |
|---|---|---|
| ℓ(θ*) = s(θ*) − Rψ(θ*) (antes em OMML, seção 4.2) | Equação (16), seção 3.6 | trabalho virtual dℓ/dθ* = m com resíduo 4,7 × 10⁻⁸ mm. Com s: 1,7129 mm; com s + Rψ: 3,4258 mm |
| θ*_pm(h) = 180° + atan2(p, h) + arcsen(R/C) (antes em LaTeX, como texto) | Equação (21), seção 3.7 | bissecção de m(θ*) = 0: diferença de 1,3 × 10⁻¹¹ grau |
| h = p / tan(θ*_pm − 180° − arcsen(R/C)) (antes em LaTeX, como texto) | Equação (22), seção 3.7 | h de entrada do ponto morto 21,3718 mm, igual à bissecção a 4,6 × 10⁻¹⁴ mm. Ramo espúrio 3,9953 mm identificado |
| b e β pela lei dos cossenos (código original) | Equações (11) a (13), seção 3.5 | mesmo T que a Equação (10), a 8,0 × 10⁻¹³ mm |
| distância por lei dos cossenos, `calculate_array_vaos_livres` (código original) | Equação (9), seção 3.4 | equivale a ρ em θ* + 180° (5,7 × 10⁻¹⁴ mm). Mantida como referência; a cadeia usa a Equação (7) |

**Notação harmonizada.**
- H virou h (variável), com H_CAD e H_CAL como valores.
- P virou p, como na tabela de CAD do próprio TCC.
- Funções em português: sen e arcsen.
- O centro do tambor passou a se chamar D, porque P já designa a componente p.
- As duas equações em LaTeX passaram a ser equações do Word (OMML).

## 5. Alterações no capítulo 3

O capítulo foi reescrito em 13 seções. As principais correções em relação ao texto anterior:

- **Introdução.** O texto anterior descrevia "seis etapas" aplicadas a três patentes. Agora declara que o procedimento foi executado só para a US 9.889.554 B2. Indica também o código de referência (`torque_model.py`) e o gerador de números (`tcc_resultados.py`).
- **3.3, convenções angulares.** O texto anterior citava três convenções sem as relações entre elas. Agora há a Tabela 1, com θ*, q, φ, φ_pat, θ_el, ψ, τ e −τ, e as Equações (2) a (4). A seção separa explicitamente φ (direção do cabo) de φ_pat (ângulo da patente) e fixa a convenção de sinal (−τ positivo quando tende a elevar o braço).
- **3.4, fechamento.** O texto anterior atribuía o fechamento à "formulação de Newton-Euler". Corrigido para circuito vetorial fechado, com solução em forma fechada (Equações 5 a 8) e a Figura 1.
- **3.5, braço de momento.** O texto anterior definia o braço como "distância da ancoragem ao ponto de aplicação da força", o que está errado. Agora b = |OT| (distância ao ponto de tangência) e o braço perpendicular m são distintos (Equação 14), com o teto |m| ≤ |OA|.
- **3.6, lei da mola.** O texto anterior dizia que a mola acompanha apenas o trecho livre. Agora a mola acompanha o caminho completo s − Rψ, justificado pelo trabalho virtual. A seção inclui a ancoragem por X_pose, a lei δ = max(ℓ − s₀, 0) e o torque τ = −F m/1000. A unidade do cabo é u.p., e K tem unidade implícita.
- **3.7 e 3.8.** São novas: ponto morto, com as equações originais e a condição de validade da inversão, e torque gravitacional independente da cadeia do cabo.
- **3.9, identificação.**
  - O texto anterior apresentava a identificação como etapa executada e documentada. Agora declara que θ_off, H_CAL e X_pose vieram de etapa anterior cujo script e cuja restrição não estão no repositório.
  - Define o que foi reproduzido: K em forma fechada (Equação 25) e X_pose por varredura.
  - Fixa a regra de que o RMSE não decide validade física.
- **3.10, varredura de h.** É nova. K fica congelado e não é reidentificado por h. Os critérios de validade são (i) tração, (ii) fechamento e (iii) trabalho virtual; no texto anterior eram "(a), (c), (d)". O enrolamento é diagnóstico, não critério, e a gravidade fica fora dos critérios.
- **3.11, verificações e testes.** É nova e descreve os seis autotestes e o pytest.
- **3.12, etapas dinâmicas.**
  - O texto anterior (antigas 3.5 e 3.6) descrevia Lagrange, SciPy e MBDyn como método em uso. Agora as etapas aparecem como **previstas e não executadas**.
  - A formulação prevista (Equação 27) foi incluída sem resultado.
  - O texto registra o pré-requisito não satisfeito: o torque do cabo precisa estar em unidade física.
- **3.13, ferramentas.** SciPy e pandas, que o projeto não usa, foram removidos. Entraram NumPy, Matplotlib e pytest. A seção registra que o MBDyn não foi empregado e não lista mais como limitação o "trecho livre sem arco", que já foi corrigido.

## 6. Alterações no capítulo 4

| item do texto anterior | problema | correção |
|---|---|---|
| Introdução | dizia que 3.5 e 3.6 estavam "em desenvolvimento" | declara que as etapas dinâmicas e as outras patentes não foram executadas |
| Tabela 1 (CAD) | sem origem das grandezas | coluna de origem: CAD, CAD a confirmar, documental |
| Tabela 2 (massa) | — | conferida: Steiner (0,127111 + M d² = 0,448227) e M g d = 11,1619 N·m |
| — | não havia tabela com os pontos da patente | Tabela 4: 29 pontos, ângulos nas três convenções, modelo e resíduo |
| Tabela 3 (verificações) | sem o par da mola; ponto morto "< 10⁻⁸" | Tabela 5 completa; ponto morto 1,3 × 10⁻¹¹ grau |
| Tabela 4 (parâmetros) | "θ* = 133,017 − φ" (φ em vez de φ_pat); K em "N/(mm)"; H "identificado" | Tabela 6: φ_pat; K com unidade implícita; origem e verificação de cada parâmetro |
| Tabela 5 (ajuste) | unidades "N.m" | Tabela 7 em u.p.; acrescentados resíduo médio e pico nos pontos extraídos |
| §[120] resíduos | 3 zonas, "−1,97 na porção de braço baixo", frase incompleta ("− N.m") | Tabela 8: 6 zonas, com sinal e lado corretos (θ* baixo = braço alto) |
| §[121]–[123] identificação de H | "RMSE decresce monotonicamente… ótimo exigiria extensão > 10× o comprimento livre" | **refutado** pela auditoria (seção 7 deste relatório); H_CAL classificado como congelado de origem não reproduzida |
| §[119] | "1,152 N.m" e "1,830 u.p." misturados | 1,152 e 1,830 u.p., com X_pose e K da lei antiga declarados |
| Tabela 6 (mecanismo) | "9.516,5 N.m /m"; "pré-extensão" | Tabela 9 com unidade implícita, ponto morto, b, β e ψ |
| §[130] | frase incompleta ("A razão… de 1,0095.") | interpretação: a mola estende cerca de 2× o comprimento livre; conferir deflexão admissível |
| — | não havia análise de plausibilidade da unidade | leitura em N·m implica 9,5 kN e pico 13,2× o peso: implausível |
| §[144] varredura | passo 0,05 mm; perfil K*(h) | passo 0,005 mm; K congelado; perfil K* removido do texto |
| §[146] | trabalho virtual "abaixo de 7,2 × 10⁻⁸ na grade inteira" | 7,4 × 10⁻⁸ na grade; 7,2 × 10⁻⁸ é o máximo nos h viáveis |
| §[156] | linearidade 8,4 × 10⁻¹³ | 7,7 × 10⁻¹³ |
| — | não havia família de curvas, RMSE(h), platôs nem h de menor RMSE | Figuras 3 e 4, Tabelas 10 e 11; ressalva de que o mínimo perto de H_CAL é esperado por construção |
| Figura 1 (perfis normalizados) | sem rótulo "Figura N"; imagem antiga | Figura 5 regenerada com os mesmos números (cruzamento em 93,96°; diferenças conferidas) |
| §[133] desvio de 0,56° | atribuído a "CG abaixo do eixo do elo" sem verificação | reescrito: ângulo entre a linha pivô–CG e a direção do braço da convenção da patente |
| §4.7 limitações | — | acrescentadas a identificação parcial, a incompatibilidade de H_CAD e a natureza só estática |

O capítulo novo tem 9 seções. Os números que permaneceram foram todos reconferidos e estavam corretos:
- arco de 1,862 mm; diferença de δ de 1,782 mm (3,3%) e de 6,3%;
- pico de 147,07 u.p. a 97,48° de elevação;
- peso de 11,1619 N·m a 89,44°;
- diferenças normalizadas;
- ponto morto em 30,485°;
- fronteira de tração em 32,886 mm;
- curso de 28,942, 42,435 e 106,573 mm;
- entrada do ponto morto em 21,3718 mm.

## 7. Auditoria da identificação de H

- **Reproduzido.** Em h = 22,701 mm, com θ_off fixo, a varredura de X_pose (passo de 0,001 mm), com K em forma fechada, devolve X_pose = 37,383 mm, K = 174,676 e RMSE 1,83045.
- **Não reproduzido.** Como 22,701 mm e 133,017° foram escolhidos: o script e a restrição não estão no repositório.
- **Análise alternativa (auditoria, não procedimento).** X_pose e K reidentificados para cada h, de 8 a 60 mm em passo de 0,25 mm:
  - lei vigente: mínimo interior em h ≈ 24,0 mm (RMSE 1,682; X_pose 38,83 mm; K 160,46; δmax/L_livre 1,079);
  - lei antiga: mínimo em h ≈ 23,0 mm (RMSE 1,146; razão 0,995);
  - na lei vigente, δmax/L_livre = 1 em h ≈ 22,52 mm e só passa de 10 perto de h = 60 mm.

  A afirmação anterior de decrescimento monotônico não se sustenta em nenhuma das duas leis.

## 8. Capítulo 5, tabelas, figuras e referências

- **Capítulo 5 (novo).** Tem sete parágrafos: síntese, formulação e trabalho virtual, ajuste, varredura, confronto com o peso, situação de cada objetivo específico e continuidade. Todos os números vêm do capítulo 4.
- **Numeração.**
  - 27 equações, numeradas à direita;
  - 11 tabelas, com título acima e fonte abaixo;
  - 5 figuras, com título acima e fonte abaixo;
  - todas citadas no texto antes de aparecerem.
- **Referências.**
  - A lista foi posta em ordem alfabética: ATIA antes de BÄR, BARSOTTI antes de BOUTERAA, GRAZI e GULL antes de HERDER, KIM, H. antes de KIM, S., e NÄF, NASR e NGUYEN antes de NING.
  - Foram acrescentadas duas referências reais, citadas na seção 3.13:
    - HARRIS et al. (2020), NumPy, *Nature* 585, DOI 10.1038/s41586-020-2649-2;
    - HUNTER (2007), Matplotlib, *Computing in Science & Engineering* 9(3), DOI 10.1109/MCSE.2007.55.

    Convém conferir a formatação ABNT de ambas.
  - Nenhuma outra referência foi criada.
- **Outras correções no documento.**
  - Objetivo geral: removida a US 9.889.554 B2 repetida.
  - Removida a seção interna "Pontos do texto anterior que precisam de ajuste", com os itens ☐.
  - Título "4 Resultados e discussão" padronizado em caixa alta.
  - Capítulos 1 e 2: nenhuma outra alteração.

## 9. Testes executados

- `python -m pytest`: **47 passed**. Os testes estão em `test_torque_model.py`, `test_varredura.py`, `test_calibration.py` e `test_svaj.py`.
- `python tcc_resultados.py`: autotestes do modelo e varredura completa de 10.403 valores de h, sem falha. Os arquivos `vh_*` saíram idênticos aos versionados.
- **DOCX:**
  - validação OOXML: "All validations PASSED";
  - renderização em PDF (LibreOffice, 36 páginas): equações, tabelas e figuras inspecionadas página a página.
- **Não executado:** nenhuma simulação dinâmica, integração numérica ou execução do MBDyn. Não existe código para isso no projeto.

## 10. Divergências encontradas

1. **TCC × código.**
   - Zonas de resíduo.
   - Identificação monotônica de H.
   - Unidades N·m no torque do cabo.
   - Passo da varredura.
   - Valores de trabalho virtual e de linearidade.
   - "Newton-Euler".
   - Definição de braço.
   - Lei do trecho livre.
   - SciPy e pandas citados sem uso.
   - Métodos dinâmicos descritos como executados.

   Todas foram corrigidas no texto.
2. **MD × código.** A faixa de b (282,4 a 285,3 mm) era de H_CAD. Corrigida para 282,50 a 284,36 mm com H_CALIBRADO. A frase "reajustá-lo daria H ≈ 24 mm" foi completada com a condição (X_pose e K também reajustados).
3. **H_CAD × parâmetros congelados.** Com X_pose congelado, h = 34,785 mm afrouxa o cabo (δ mínimo de −2,257 mm). A diferença de 12,084 mm entre H_CAD e H_CAL não tem explicação nos registros.

## 11. Limitações e pendências que dependem do autor

- **Unidade da ordenada da patente.** Sem ela não há torque do cabo em N·m, torque resultante nem dinâmica com significado físico. Uma especificação de mola comercial resolveria.
- **Script da identificação anterior.** É necessário o script com a restrição que levou a H_CAL = 22,701 mm e θ_off = 133,017°.
- **Pontos da patente.** Falta documentar o método de extração e a incerteza dos 29 pontos.
- **Cotas de CAD a confirmar.**
  - L_carc: 131,37 contra 140,0 mm.
  - L_pose: 91,35 contra 90,13 mm.
  - A cota de ancoragem H_CAD.
  - O fator de escala 0,870 não é verificável pelo código.
- **Planilha de composição inercial.** Não está no repositório: a Tabela 3 foi conferida apenas por consistência interna.
- **Referências não citadas.** FOROUTANNIA e MOHAMMADIAN (2026) e KIM, H. et al. (2012) estão na lista, mas não são citadas no texto. Foram mantidas; convém citá-las ou removê-las.
- **Objetivos f e g e trechos sobre o MBDyn.** O texto desses objetivos, da introdução e da justificativa (capítulo 1) foi mantido. A conclusão registra que esses objetivos não foram executados.
- **Notação na seção 2.1.** A seção usa θ para a elevação. O capítulo 3 introduz θ_el e faz a ponte, mas uma nota na 2.1 evitaria ambiguidade.
- **Renderização.** As equações foram conferidas no LibreOffice, que mostra as funções e os vetores em fonte diferente da do Word. Convém abrir o arquivo no Word antes da entrega.

## 12. Como regenerar

```
python tcc_resultados.py      # números (JSON), tabela dos 29 pontos e figuras do TCC
python -m pytest              # 47 testes
python torque_model.py        # autotestes, gráfico do modelo e varredura de h
```

## 13. Seção 4.7 reescrita: otimização de h para o máximo torque devolvido

A pedido do autor, a seção 4.7 deixou de discutir o RMSE contra a patente
(platôs, h de menor RMSE, tabela de h notáveis) e passou a tratar de **qual h
devolve o maior torque com a mesma mola**. K = 174,68 e X_pose = 37,383 mm
continuam congelados.

- **Método.** A seção 3.10 foi reescrita com a formulação do problema:
  - Equação (27): maximizar o torque médio de −τ entre 90° e 150° de elevação;
  - Equação (28): restrições de tração com margem δ_marg, de fechamento e de trabalho virtual.

  Critérios complementares: pico e trabalho devolvido na faixa toda. A busca é por enumeração, em passo de 0,01 mm, de 8 mm até a fronteira de tração.
- **Resultado.** Pico, média e trabalho crescem monotonicamente com h, então não há ótimo interior. O ótimo estrito é a fronteira de tração, h* = 32,886 mm:
  - média de 90° a 150°: 163,6 u.p., contra 123,6 no h adotado (+32%);
  - pico: 211,9 u.p., contra 147,1.

  Nesse ponto a extensão mínima da mola é zero, sem pré-tensão no braço elevado.
- **Ótimos com margem de extensão:**
  - 10 mm de margem: h* = 24,44 mm, ganho de +6,0% na média;
  - 5 mm de margem: h* = 28,67 mm, ganho de +19,9% na média;
  - 2 mm de margem: h* = 31,20 mm, ganho de +27,5% na média;
  - o h adotado equivale a uma margem de 12,04 mm.
- **Contrapartidas, do h adotado à fronteira:**
  - a tração máxima cresce 10,5%;
  - a mola chega a 114,1 mm, ainda abaixo do alojamento de 131,37 mm;
  - δmax/L_livre passa de 1,009 para 1,115;
  - o ponto morto vai de 30,49° para 32,92°.
- **Figuras e tabelas.**
  - A Figura 3 (família de curvas) foi mantida.
  - A Figura 4 é nova: `results/tcc_fig4_efeito_h.png`, com pico e média, trabalho, margem de tração e ponto morto em função de h. Ela substitui `tcc_fig4_rmse_h.png`, que foi removida.
  - As Tabelas 10 (torque por h) e 11 (ótimo por margem) substituem as de platôs e de h notáveis.
- **Outros ajustes.** A remissão da seção 4.4 e o quarto parágrafo da conclusão foram atualizados.
- **Ressalva mantida no texto.** Esses h são alternativas de projeto. Só H_CAL reproduz a curva da patente com K e X_pose congelados.
- **Números.** Saem de `tcc_resultados.py`, chave `efeito_h` de `results/tcc_numeros.json`.

## 14. Limite geométrico do CAD para h (76,846 mm)

O autor informou que o CAD admite a ancoragem até h = 76,846 mm.

**O que entrou no documento**
- **Tabela 2:** linha "Maior posição da ancoragem admitida pela geometria", h_máx = 76,846 mm, com origem CAD.
- **Seções 3.10 e 4.7:** a verificação de validade passou a ir até o limite do CAD. São 13.773 valores, em passo de 0,005 mm, mais H_CAL e H_CAD. O resultado:
  - fechamento e trabalho virtual valem em todos os valores (resíduo máximo de 8,0e‑08 mm/rad);
  - a tração continua só até 32,885 mm na grade, com fronteira de 32,886 mm.

  O cálculo está em `tcc_resultados.limites_h()`; `torque_model.py` não foi alterado.
- **Seção 4.7:** parágrafo novo com a hierarquia dos limites:
  - geometria do CAD: 76,846 mm;
  - alojamento da mola: 66,94 mm, para qualquer pré-extensão, porque o comprimento da mola depende só da geometria;
  - tração com a montagem atual: 32,886 mm, o único limite ativo.

  No limite do CAD, a mola teria curso de 134,6 mm e extensão mínima de −52,7 mm. Usar esse espaço exigiria outra mola.

**O que não mudou**
- A otimização continua com a mola e a montagem atuais. A análise com pré-extensão ajustada e deflexão máxima de 1,25 × L_livre foi calculada, mas não entrou no texto, por decisão do autor.
- Uma busca de referência comercial encontrou anúncios de molas de tração de estoque com deflexão máxima entre cerca de 0,2 e 0,95 vez o comprimento livre. É uma amostra pequena e não documentada como norma. O valor atual, 1,0095, fica acima dessa faixa, ponto que convém conferir no catálogo do fabricante escolhido.
