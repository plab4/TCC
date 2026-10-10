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
