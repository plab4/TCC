# Modelo de torque: derivação e estado atual

Referência vigente: **`torque_model.py`**. Para rodar: `python torque_model.py`
(tabela, autotestes e gráfico) e `python -m pytest`. Os outros arquivos que
calculam torque estão defasados (ver o fim deste documento).

## Cadeia de cálculo

```
θ* (graus) ── q = θ* − π/2 − α  (rad, conversão única)
           ├─ ρ   = |B + C·u(q)|                       ancoragem → centro do tambor
           ├─ s   = √(ρ² − R²)                         vão reto (tangente)
           ├─ φ   = atan2(W_y, W_x) − atan2(R, s),     W = −(B + C·u(q))
           ├─ T   = centro do tambor + R·(sen φ, −cos φ)   ponto de tangência
           ├─ rel = ângulo cabo × elo, em (−π, π]
           ├─ caminho = s − R·rel                      caminho variável do cabo
           ├─ δ   = max(caminho − s_zero(h), 0)        extensão da mola
           ├─ f   = K·δ
           ├─ V   = (−f cos φ, −f sen φ)               força do cabo no tambor
           └─ τ   = T × V = T_x V_y − T_y V_x
```

`u(x) = (cos x, sen x)` e `B = (h sen α − p cos α, h cos α + p sen α)` é o termo
constante das equações de fechamento (pivô → ancoragem). `h` é argumento
obrigatório de toda a cadeia; `H_CAD = 34,785 mm` é só valor documental.

## Cinemática

**Equações de fechamento.** `B + s·u(φ) + R·u⊥(φ) + C·u(q) = 0`, com
`u⊥(x) = (−sen x, cos x)`. Os resíduos de f1 e f2 ficam em ≈ 1e‑13 mm.

O comprimento que multiplica cos φ e sen φ é o vão `s`. Com `q` (radianos)
nessa posição o sistema não tem solução para nenhum θ*: exigiria ρ ≈ 23 mm, e
ρ fica entre 248 e 318 mm.

**φ em forma fechada.** Os termos com φ são o vetor (s, R) girado de φ:

```
s cos φ − R sen φ = ρ cos(φ + γ) = W_x,   γ = atan2(R, s)
s sen φ + R cos φ = ρ sen(φ + γ) = W_y
```

Daí `ρ = |W|`, `s = √(ρ² − R²)` e `φ = atan2(W_y, W_x) − γ`. Não há solver
numérico.

**Ponto de tangência, b e β.** A cadeia usa T direto (`ponto_tangencia`), que
não depende do sinal de β. A via original, `b_vector = b·(−cos(β−q), sen(β−q))`
com `b = distancia_ponto_tangencia` e `β = angulo_beta`, é mantida como
relatório e conferida contra T dentro da cadeia (diferença ≈ 1e‑12 mm).

`b` é a distância do pivô ao ponto de tangência (282,4 a 285,3 mm na operação;
limite teórico C ± R = 261 a 306 mm). **Não é o braço de momento.**

**Braço de momento e torque.** `m = A_x sen φ − A_y cos φ` (`braco_perpendicular`)
é a distância perpendicular do pivô à linha do cabo, limitada por |A| = √(h² + P²).
O torque é o produto vetorial 2D, e vale a identidade **τ = −F·m** (≈ 1e‑13).

Sinal: **τ positivo = anti-horário = sentido de θ* crescente.** A patente dá o
torque do cabo positivo no sentido oposto, por isso a comparação usa −τ.

## Caminho do cabo: vão reto menos arco

O cabo contorna o tambor, e o arco enrolado muda de comprimento com θ*. A mola
se deforma com o **caminho total**, não com o vão reto:

```
rel     = ângulo entre o cabo e o elo, em (−π, π]   (−4,656° a 0,019° na operação)
caminho = s − R·rel
```

**Justificativa por trabalho virtual.** Num mecanismo conservativo, o trabalho
da tração no cabo é igual ao do torque no elo, então d(caminho)/dθ* = m. O
sinal do arco foi escolhido por esse teste, com H = 22,701:

| caminho testado | max\|d/dθ* − m\| |
|---|---|
| s | 1,7129 mm |
| s + R·rel | 3,4258 mm |
| **s − R·rel** | **≈ 5e‑08 mm** (diferença finita com passo 1e‑4°) |

O autoteste `residuo_trabalho_virtual` repete essa conta toda vez que o modelo
roda e exige < 1e‑3 mm.

O arco varia 1,862 mm na faixa (4,49% da variação do vão). Ele entra só no
comprimento do cabo, ou seja, em δ. φ, T, b, β, m, τ = −F·m e o ponto morto não
mudam.

## Lei da mola

δ é referenciado a um comprimento, não a um ângulo:

```
s_zero(h) = caminho_cabo(THETA_POSE, h) − X_POSE
δ         = max(caminho − s_zero(h), 0)        o cabo traciona, mas não empurra
f         = K·δ
```

`X_POSE` é a extensão elástica da mola na pose do CAD. `L_POSE` e `L_LIVRE` só
entram pela diferença `X_POSE = L_POSE − L_LIVRE`: qualquer par com a mesma
diferença dá a mesma curva, bit a bit. Eles ficam como par documental, para
especificar a mola a comprar:

| L_POSE | L_LIVRE coerente |
|---|---|
| 91,35 mm (ativo) | 53,967 mm |
| 90,13 mm (CAD anterior) | 52,747 mm |

O autoteste confere `|(L_POSE − L_LIVRE) − X_POSE| < 1e‑9`.

## Parâmetros congelados

| parâmetro | valor |
|---|---|
| K | 174,68 (K·δ·m/1000 sai em u.p.) |
| H_CALIBRADO | 22,701 mm |
| X_POSE | 37,383 mm |

Com esses valores, `caminho_cabo(THETA_POSE)` = 290,1804 mm e
s_zero = 252,7974 mm. O caminho vai de 264,842 a 307,277 mm e δ de 12,044 a
54,479 mm, sem folga em nenhum dos 302 pontos. Nenhum ajuste é feito dentro de
`torque_model.py`.

**RMSE contra a patente: 1,830 u.p.** Antes da correção do caminho era 1,152.
A piora vem de uma **correção de física**, não do modelo ter ficado pior: o
modelo anterior ajustava melhor porque violava a conservação de energia (o vão
reto erra d(caminho)/dθ* em até 1,71 mm).

O pico calculado é 146,874 u.p. nos pontos da patente (alvo 147,310) e 147,072
na grade de 0,5°.

H_CALIBRADO não foi reajustado junto com K. Reajustá-lo daria H ≈ 24 mm com
RMSE 1,682, mas levaria o ponto morto para φ_pat = −59,09°, mais longe do −60°
da patente (com 22,701 fica em −59,515°).

## Unidades

- **Torque do cabo: u.p.**, a unidade da curva extraída da patente. A fonte não
  declara essa unidade.
- **Torque do peso: N·m** (`torque_peso`).
- **Não existe conversão** entre as duas. O gráfico `results/torque_cabo_peso.png`
  usa dois eixos com escalas independentes e zeros alinhados.

## Faixa de operação e ponto morto

Mapeamento congelado `θ* = ANGLE_OFFSET − φ_pat`, com ANGLE_OFFSET = 133,017°
e φ_pat de −60° a +90,1°. Isso dá **θ* de 42,917° a 193,017°**. O φ_pat é o
ângulo da patente e é diferente do φ deste modelo (direção do cabo).

O ponto morto é onde a linha do cabo passa pelo pivô (m = 0):

```
θ*_pm = 180 + atan2(P, h) + asen(R/C)
```

Dá 192,5317° (φ_pat = −59,515°) com H_CALIBRADO e 189,80° (φ_pat = −56,78°) com
H_CAD. A forma fechada confere com a raiz numérica de m(θ*) a 1e‑11°. Depois do
ponto morto o torque do cabo troca de sinal, e isso é reportado, não escondido.

## Torque do peso

Independente da cadeia do cabo: não usa K, X_POSE nem h.

```
giro  = θ* − THETA_POSE + ALPHA + 90 − ANGLE_OFFSET      (o desenho gira −22,589°)
x_cg  = CG_DX·cos(giro) − CG_DY·sen(giro)
τ_peso = m·g·|x_cg| / 1000                                [N·m]
```

Pico de 11,1619 N·m em θ* = 133,58° (braço na horizontal). O módulo esconde a
troca de sinal em θ* = 43,58°, que afeta 0,66° no início da faixa com
|τ| ≤ 0,13 N·m; foi mantido por decisão. Inércia (Steiner) não entra num torque
estático.

## Correções feitas no código original

| original | problema | correção |
|---|---|---|
| `from math import ...` | funções escalares, falham com arrays | NumPy em tudo |
| `calculate_array_vaos_livres` | devolvia s² | raiz quadrada |
| conversão para radianos | aplicada duas vezes em 10° | uma conversão só |
| `measure_moment_arm` | nome sugeria braço de momento | `distancia_ponto_tangencia`; braço real em `braco_perpendicular` |
| `measure_moment_arm_deflection` | nome | `angulo_beta` |
| `torque_patent` | `np.outer` é tensor 2×2, não torque | parte antissimétrica, b_x F_y − b_y F_x |
| δ referenciado a ângulo (θ* = 10°) | o comprimento livre implícito mudava com H | δ referenciado a comprimento (`X_POSE`) |
| δ a partir do vão reto | viola o trabalho virtual | caminho = s − R·rel |
| `h=H` padrão em 13 funções | chamada sem h dava a curva do CAD em silêncio | h obrigatório (`TypeError`) |
| constantes sem uso (pico do peso, pico do cabo, referência angular) | não entravam na cadeia | removidas; não existem mais no modelo |

**`calculate_array_vaos_livres`.** Usa `+2C(h cos θ + P sen θ)`, sinal oposto ao
das equações de fechamento. Equivale a `calculate_rho(calculate_q(θ* + 180))`
(diferença 5,7e‑14 mm). Não é a formulação usada: a cadeia usa `calculate_rho`.
Fica só como referência histórica.

## CAD a confirmar

| constante | valor ativo | CAD anterior | efeito |
|---|---|---|---|
| `L_CARCACA` | 131,37 mm | 140,0 mm | não entra na cadeia |
| `L_POSE` | 91,35 mm | 90,13 mm | não muda a curva (só `X_POSE` entra); muda o `L_LIVRE` da mola a comprar |

## Arquivos defasados

`torque_model.py` é a **única referência vigente**. Estes arquivos não foram
atualizados, de propósito:

- **`calibration.py`.** Rotula o torque em N·m e calibra K com o H do CAD.
  Como ele chama a cadeia atual de `torque_model.py`, reexecutá-lo hoje **não
  devolve os parâmetros antigos nem os congelados**. Ele devolve uma terceira
  combinação: K = 122,17 com H_CAD, melhor H = 31,0 mm na varredura grossa, RMSE
  15,2. Ele só continua importando porque `torque_model.py` mantém o apelido
  `H = H_CAD` para ele.
- **Gráficos 1 a 4** (`results/1_patente.png` a `results/4_melhor_H.png`) e as
  tabelas `varredura_H_*.csv`: gerados com a lei antiga (δ a partir do vão reto,
  referência em 10°) e rotulados em N·m.
- **Página interativa** (Artifact): mesmos números e rótulos dos gráficos 1 a 4.
- **`svaj.py`**: só usa a geometria (não a lei da mola), mas tem `h = H` (o do
  CAD) como padrão próprio, também pelo apelido.

## Passada de varredura de h (diagnóstico)

Seção anexada ao fim de `torque_model.py`, depois do marcador "PASSADA ADICIONAL".
Nada acima do marcador foi alterado (o `diff` das 506 primeiras linhas contra o
original é vazio). Com `VH_RODAR = False` o arquivo produz a mesma saída e o
mesmo PNG de antes. Saídas: `results/vh_varredura_h.csv` (uma linha por h) e
`results/vh_h_notaveis.csv`. Os dois gráficos da passada ficam desligados por
padrão.

### Critério de otimalidade

"Ótimo" significa só **menor RMSE contra a curva extraída da patente**, que
representa exclusivamente o torque do cabo. A gravidade fica fora do critério,
da normalização e da ponderação, porque a curva extraída não contém o peso:
somá-lo ou subtraí-lo mudaria o alvo, e as unidades não são comparáveis (u.p.
contra N·m). As métricas de compensação do peso aparecem só como descritivas.

h_otimo é **achado diagnóstico, não adoção**. K = 174,68, H_CALIBRADO = 22,701 mm
e X_POSE = 37,383 mm continuam congelados; a seção não religa nenhum deles.

### Convenção de ancoragem

Ao variar h, o comprimento livre é reancorado por X_POSE:

```
s_zero(h) = caminho_cabo(THETA_POSE, h) − X_POSE
```

A extensão na pose fica em X_POSE para todo h, ou seja, a pré-tensão de
montagem é preservada. É **escolha de modelagem**, não consequência da
geometria. Erro máximo verificado: 2,1e‑14 mm.

Alternativa descartada: manter s_zero fixo no valor de H_CALIBRADO
(252,7974 mm) e deixar a extensão na pose variar com h. Nesse caso cada h
mudaria também a pré-tensão, e a varredura misturaria dois efeitos
(geometria e montagem).

### Critérios de validade física

Avaliados em toda a faixa θ* = 42,917° a 193,017°, com 1501 pontos. Nenhuma
grandeza é saturada nem truncada; h inviável é reportado com o motivo e fica
fora dos rankings restritos.

| critério | condição | resultado na grade |
|---|---|---|
| (a) tração | extensão bruta caminho − s_zero ≥ 0 | h de 8,00 (borda) a 32,85 mm |
| (b) enrolamento | `angulo_cabo_elo` não troca de sinal | h de 8,00 (borda) a 22,60 mm |
| (c) fechamento | ρ > R em toda a faixa (solução real) | todos os 1043 h |
| (d) trabalho virtual | max\|d(caminho)/dθ* − m\| < 1e‑6 mm/rad | todos (máx. 7,2e‑08) |

Viáveis, ou seja, (a) a (d) juntos: **h de 8,00 a 22,60 mm** (293 valores).

**Observação sobre (b).** O critério trata a troca de sinal de rel como "o
cabo deixa a polia". Isso pressupõe que o ponto de fixação do cabo no tambor
está em rel = 0, o que a geometria do modelo não determina. Com esse critério,
o próprio **H_CALIBRADO = 22,701 falha (b)**: rel chega a +0,019°, um arco de
0,0076 mm, perto de θ* ≈ 95°. O critério foi aplicado como especificado e o
resultado foi reportado, não corrigido. Antes de usá-lo para excluir h, vale
confirmar onde o cabo é fixado no tambor.

**Observação sobre (a).** `calculate_delta` (acima do marcador) satura δ em
zero, porque o cabo não empurra. Para o critério (a), a varredura usa a
extensão bruta, sem saturação, calculada a partir das mesmas funções do modelo.
O torque usado no RMSE é o do modelo como está.

### Classificação dos h

| grandeza | classificação |
|---|---|
| h | VARRIDO: 8,00 a 60,00 mm em 0,05 mm, mais 22,701 e 34,785 exatos |
| h_otimo, h_pior e os demais h notáveis | DERIVADOS (diagnóstico) |
| h_dc_entra | DERIVADO em forma fechada |
| H_CALIBRADO = 22,701 mm | calibrado (congelado) |
| H_CAD = 34,785 mm | CAD (documental) |

### Definição dos h notáveis

| nome | definição | valor |
|---|---|---|
| h_otimo | argmin RMSE(h), K congelado, sem restrição | 22,750 mm (RMSE 1,8279), **não viável** por (b) |
| h_otimo_viavel | argmin RMSE entre os viáveis | 22,600 mm (RMSE 1,8855): difere de h_otimo |
| h_pior | argmax RMSE entre os viáveis | 8,000 mm (RMSE 54,31), na borda da grade |
| platô | h com RMSE ≤ 1,05·mín | 22,600 a 22,900 mm |
| h_otimo_K | argmin RMSE*(h) com K reidentificado por h | 22,950 mm, K* = 173,18, RMSE* 1,8033 |
| h_tracao_min/max, h_enrolamento_min/max, h_viavel_min/max | bordas dos conjuntos válidos | ver tabela de validade |
| h_dc_entra | θ*_pm(h) = THETA_MAX | 21,3718 mm (forma fechada = bissecção a 4,6e‑14) |
| h_dc_sai | θ*_pm(h) = THETA_MIN | **não existe** (abaixo) |
| h_tau_max (descritivo) | maximiza τ_max entre os viáveis | 22,600 mm (borda dos viáveis) |
| h_min_deficit (descritivo) | minimiza max(τ_peso − τ_cabo) entre os viáveis | 8,000 mm (borda da grade) |

**h_dc_sai não existe.** Para h > 0, θ*_pm = 180 + atan2(P, h) + asen(R/C)
fica entre 184,619° e 274,619°, e nunca chega a THETA_MIN = 42,917°. A inversão
h = P / tan(θ − 180 − asen(R/C)) devolve 3,9953 mm, mas esse valor é de um ramo
espúrio da tangente: θ*_pm(3,9953) = 222,917°. A bissecção própria não encontra
troca de sinal. O ponto morto entra na faixa em h_dc_entra e não sai mais por
THETA_MIN.

### Identificabilidade de H: largura do platô

- **Com K congelado,** o platô (RMSE ≤ 1,05·mín) vai de 22,60 a 22,90 mm:
  **largura de 0,30 mm**. Fora dele, o RMSE cresce depressa, por exemplo 4,79
  em 24,0 mm e 43,5 em H_CAD.
- **Com K reidentificado por h** (crista h–K), o platô de RMSE* vai de 22,50 a
  23,35 mm: **largura de 0,85 mm**. K*/174,68 nas bordas do platô com K
  congelado vale 1,0035 (h = 22,60) e 0,9931 (h = 22,90).

A afirmação de que "H não é identificável pela curva" **não é sustentada nesta
forma**. Com K fixo, a curva localiza H dentro de ±0,15 mm; com K livre, dentro
de ±0,4 mm. O que existe é uma correlação h–K estreita (a crista), não um
platô largo. Se a dissertação mantiver a afirmação, ela precisa ser
qualificada com esses números.

### Delta h_otimo − H_CALIBRADO

delta = 22,750 − 22,701 = **+0,049 mm**, menor que um passo da grade (0,05 mm).
O RMSE em H_CALIBRADO é 1,8305, contra 1,8279 em h_otimo: posto 2 de 1043.

Hipótese registrada: H_CALIBRADO foi identificado antes da correção do
enrolamento da polia (o RMSE passou de 1,152 para 1,830 com a física corrigida),
então o mínimo do modelo corrigido poderia estar deslocado. **Os números indicam
que o deslocamento é desprezível** (0,049 mm e 0,0026 de RMSE). A hipótese fica
registrada, mas os dados não a sustentam como causa de um deslocamento
apreciável. Nenhum parâmetro foi trocado.

### Observações de implementação

- **Efeito da importação.** O `if VH_RODAR: varredura_h()` no fim do arquivo
  roda também quando o módulo é importado: pelo pytest, por `calibration.py` e
  por `svaj.py`. A suíte de testes passou de cerca de 2 s para cerca de 10 s e
  reescreve os dois CSVs. Para importar sem varrer, use `VH_RODAR = False`.
  Acrescentar `and __name__ == "__main__"` ao `if` mantém o comportamento no
  Colab e evita o efeito na importação; ainda não foi feito.
- **Apelido H.** Continua `H = H_CAD` acima do marcador, por causa de
  `calibration.py`. A varredura passa h explicitamente em todas as chamadas e
  tem uma guarda que aborta se duas curvas com h diferentes saírem iguais.
- **Cores no gráfico de curvas.** O gráfico de curvas notáveis tem 9 h para uma
  paleta de 8 cores: o nono usa linha tracejada em vez de uma cor nova.
