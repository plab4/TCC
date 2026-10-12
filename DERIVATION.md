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

Seção anexada ao fim de `torque_model.py`, depois do marcador "PASSADA
ADICIONAL". Nada acima do marcador foi alterado: o `diff` das 506 primeiras
linhas contra o original é vazio, e com `VH_RODAR = False` a execução direta
produz a mesma saída e o mesmo PNG de antes.

- **Saídas:** `results/vh_varredura_h.csv` (uma linha por h) e
  `results/vh_h_notaveis.csv`. Separador `;`, decimal com vírgula e booleanos
  `sim`/`nao`, para abrir direto no Excel pt-BR; as colunas de texto (`papeis`,
  `motivo`) não são alteradas.
- **Gráficos:** os dois da passada ficam desligados por padrão
  (`VH_PLOT_PERFIL_RMSE` e `VH_PLOT_CURVAS_NOTAVEIS`).
- **Tempo:** a execução direta completa leva cerca de 5 s.

### Execução: guarda `__main__`

A varredura roda só na execução direta:

```python
if VH_RODAR and __name__ == "__main__":
    varredura_h()
```

`import torque_model` (num notebook, em `calibration.py`, em `svaj.py`, no
pytest) não dispara nada. Na execução direta, o bloco `__main__` do modelo
(acima do marcador) roda primeiro, com o gráfico original, e depois vem a
varredura.

### Critério de otimalidade

"Ótimo" significa só **menor RMSE contra a curva extraída da patente**, que
representa exclusivamente o torque do cabo. A gravidade fica fora do critério,
da normalização e da ponderação, porque a curva extraída não contém o peso:
somá-lo ou subtraí-lo mudaria o alvo, e as unidades não são comparáveis. As
métricas de compensação do peso aparecem só como descritivas.

h_otimo é **achado diagnóstico, não adoção**. K = 174,68, H_CALIBRADO = 22,701 mm
e X_POSE = 37,383 mm continuam congelados; a seção não religa nenhum deles.

### Unidades

A ordenada da curva extraída não tem unidade declarada. A unidade do torque do
cabo é herdada de K, que foi identificado contra essa curva; "N·m" só vale se K
estiver em N/mm. O torque do peso está em N·m por construção. Não há conversão
nem reescala, e as diferenças cabo − peso da varredura só têm sentido físico se
K estiver em N/mm.

### Convenção de ancoragem

Ao variar h, o comprimento livre é reancorado por X_POSE:

```
s_zero(h) = caminho_cabo(THETA_POSE, h) − X_POSE
```

A extensão na pose fica em X_POSE para todo h, ou seja, a pré-tensão de
montagem é preservada. É **escolha de modelagem**, não consequência da
geometria. Erro máximo verificado na grade: 2,1e‑14 mm.

Alternativa descartada: manter s_zero fixo no valor de H_CALIBRADO
(252,7974 mm) e deixar a extensão na pose variar com h. Cada h mudaria também
a pré-tensão, e a varredura misturaria geometria e montagem.

### Critérios de validade física

Viabilidade = `VH_CRITERIOS = ("tracao", "fechamento", "tv_ok")`. A
viabilidade e o motivo de cada h são derivados dessa constante. A avaliação
cobre toda a faixa θ* = 42,917° a 193,017°, com 1501 pontos.

| critério | condição | resultado na grade (1043 h) |
|---|---|---|
| (a) tração | extensão bruta caminho − s_zero ≥ 0 | h de 8,00 (borda) a 32,85 mm, 499 h |
| (c) fechamento | ρ > R em toda a faixa (tangente real) | 1043 de 1043 |
| (d) trabalho virtual | max\|d(caminho)/dθ* − m\| < 1e‑6 mm/rad | 1043 de 1043 (máx. 7,2e‑08) |

Viáveis: **h de 8,00 a 32,85 mm** (499 h), com o limite superior imposto pela
**tração**: o primeiro h fora é 32,90 mm, com δ_min = −0,016 mm.

**A extensão de (a) é calculada sem a saturação.** `calculate_delta` (acima do
marcador) faz δ = máx(caminho − s_zero, 0), porque o cabo não empurra. Para o
critério (a), a varredura usa a extensão bruta, para que o afrouxamento
apareça como δ negativo em vez de ser zerado em silêncio. O torque usado no
RMSE é o do modelo como está.

Uma exceção dentro da avaliação de um h, inclusive no teste de trabalho
virtual, marca aquele h como sem fechamento, com o motivo. A varredura não é
interrompida.

### Por que o enrolamento deixou de ser critério

A versão anterior da passada usava um quarto critério: a troca de sinal de rel
(`angulo_cabo_elo`), interpretada como "o cabo deixa a polia". A premissa era
falsa:

- **rel = 0 é arco de enrolamento nulo,** não cabo fora da polia.
- **Quem garante o cabo no tambor é a tangência,** o critério (c) ρ > R, que vale
  em toda a grade.

Valores na faixa de operação:

| h (mm) | rel (graus) | troca de sinal | maior arco positivo R·rel |
|---|---|---|---|
| 22,550 | −4,6517 a −0,0116 | não | 0 |
| 22,600 | −4,6530 a −0,0016 | não | 0 |
| 22,650 | −4,6544 a +0,0084 | sim | 3,36 µm |
| 22,701 (H_CALIBRADO) | −4,6558 a +0,0186 | sim | 7,42 µm |

O critério anterior **reprovava o próprio ponto congelado e verificado**
(H_CALIBRADO), por causa de um arco de 7 µm. Ele também cortava a faixa viável
em h ≤ 22,60 mm, logo abaixo de H_CALIBRADO. Era um falso negativo que mudava
as conclusões da passada: h_otimo saía como não viável e a faixa viável perdia
de 22,65 a 32,85 mm.

O enrolamento continua reportado como **diagnóstico**, com as colunas
`rel_min_grau`, `rel_max_grau`, `enrol_troca` e `arco_pos_max`. Na grade, rel
troca de sinal em 750 de 1043 h, de 22,65 mm para cima. O maior arco positivo é
3,0 mm, em h = 60 mm. Na tabela de flags, a troca aparece como `~`, fora da
viabilidade.

### Linearidade em K e o K* em forma fechada

δ não depende de K, então τ é exatamente linear em K: τ(K) = K·g, com
g = τ(h, K = 1). Por isso o K que minimiza o erro quadrático para um h fixo tem
forma fechada, K*(h) = Σ g·τ_pat / Σ g². Cada h verifica a linearidade com um
assert (max|τ(K) − K·g| < 1e‑9). O máximo na grade é 8,4e‑13.

### Classificação

| grandeza | classificação |
|---|---|
| h | VARRIDO: 8,00 a 60,00 mm em 0,05 mm, mais 22,701 e 34,785 exatos |
| h_otimo, h_otimo_viavel, h_pior, h_otimo_K, bordas de platô, de validade e de degradação | DERIVADOS (diagnóstico) |
| h_dc_entra | DERIVADO em forma fechada |
| H_CAD = 34,785 mm | DOCUMENTAL |
| H_CALIBRADO = 22,701 mm, K = 174,68, X_POSE = 37,383 mm | AJUSTADOS e congelados |

### h notáveis

| nome | definição | valor |
|---|---|---|
| h_otimo | argmin RMSE(h), K congelado, todos os h com fechamento | 22,750 mm, RMSE 1,8279, viável |
| h_otimo_viavel | argmin RMSE entre os viáveis | 22,750 mm (coincide com h_otimo) |
| h_pior | argmax RMSE entre os viáveis | 8,000 mm, RMSE 54,31, na borda da grade |
| h_plato_min, h_plato_max | bordas do platô RMSE ≤ 1,05·mín | 22,600 e 22,900 mm |
| h_otimo_K | argmin RMSE*(h), com K* por h | 22,950 mm, K* = 173,179, RMSE* 1,8033 |
| h_rmse_2x_esq, h_rmse_2x_dir | primeiro h, de cada lado de h_otimo, com RMSE > 2·mín | 21,800 e 23,650 mm |
| h_rmse_10x_esq, h_rmse_10x_dir | idem com RMSE > 10·mín | 17,550 e 27,950 mm |
| h_tracao_min/max, h_viavel_min/max | bordas dos conjuntos válidos | 8,000 (borda da grade) e 32,850 mm |
| h_dc_entra | θ*_pm(h) = THETA_MAX | 21,3718 mm |
| h_tau_max (descritivo) | maximiza τ_max entre os viáveis | 32,850 mm, na borda da faixa viável |
| h_min_deficit (descritivo) | minimiza max(τ_peso − τ_cabo) entre os viáveis | 8,000 mm, na borda da grade |

**h_pior na borda.** Ali o "pior" mede o intervalo varrido, não o mecanismo. A
medida livre de escala de quanto o ajuste piora é a **degradação** (os h em que
o erro passa de 2× e 10× o mínimo).

| degradação | RMSE (K congelado) | RMSE* (K reidentificado) |
|---|---|---|
| 2× o mínimo | 21,800 e 23,650 mm | 20,350 e 25,250 mm |
| 10× o mínimo | 17,550 e 27,950 mm | não atinge à esquerda na grade; 34,750 mm à direita |

**Platô por tolerância.** A largura de um platô só tem sentido junto com o
limiar que o define. A folga 1,05 é a referência para as bordas usadas no
perfil de K*.

| folga | platô de RMSE (K congelado) | platô de RMSE* (K reidentificado) |
|---|---|---|
| 1,01 | 22,700 a 22,800 mm (0,100 mm) | 22,750 a 23,100 mm (0,350 mm) |
| 1,05 | 22,600 a 22,900 mm (0,300 mm) | 22,500 a 23,350 mm (0,850 mm) |
| 1,10 | 22,500 a 22,950 mm (0,450 mm) | 22,300 a 23,550 mm (1,250 mm) |
| 2,00 | 21,850 a 23,600 mm (1,750 mm) | 20,400 a 25,200 mm (4,800 mm) |

K*/174,68 nas bordas do platô de referência: 1,0035 (h = 22,60) e 0,9931
(h = 22,90).

**h_dc_sai não existe.** Para h > 0, θ*_pm = 180 + atan2(P, h) + asen(R/C)
fica entre 184,619° e 274,619°, e nunca chega a THETA_MIN = 42,917°. A inversão
h = P / tan(θ − 180 − asen(R/C)) devolve 3,9953 mm, mas esse valor é de um ramo
espúrio da tangente: θ*_pm(3,9953) = 222,917°. A bissecção própria não encontra
troca de sinal. Já para h_dc_entra, a inversão analítica (21,371769480329 mm)
bate com a bissecção a 4,6e‑14.

### Referências: H_CALIBRADO e H_CAD

- **H_CALIBRADO = 22,701 mm:** RMSE 1,8305, posto 2 de 1043, **viável**.
  delta = h_otimo − H_CALIBRADO = +0,049 mm, menor que um passo da grade.
  Hipótese registrada sem conserto: H_CALIBRADO foi identificado antes da
  correção do enrolamento da polia, então o mínimo do modelo corrigido poderia
  estar deslocado. Medido: deslocamento de 0,049 mm e diferença de RMSE de
  0,0026.
- **H_CAD = 34,785 mm (documental):** RMSE 43,48, posto 483, **falha a tração**,
  com δ_min = −2,257 mm em θ* = 42,92°. Com a ancoragem por X_POSE, no h
  documental o cabo afrouxaria dentro da faixa de operação.

### Comprimento esticado da mola

`mola_max = L_LIVRE + δ_max` (L_LIVRE = 53,967 mm, par documental com L_POSE =
91,35 mm) é o comprimento máximo da mola esticada para cada h: 108,446 mm em
H_CALIBRADO. É uma checagem de projeto a fazer contra o curso útil da mola.

### Armadilha do h implícito e arquivos obsoletos

Uma chamada que esquece o h já produziu erro silencioso: com o h do CAD no
lugar do calibrado, a curva sai com RMSE 43,48 (posto 483) em vez de 1,8305. Na cadeia do
modelo, h é obrigatório. Acima do marcador ainda existe o apelido `H = H_CAD`,
mantido só para `calibration.py`. A varredura passa h explicitamente em todas
as chamadas, e uma guarda aborta se as curvas de h = 15 e h = 30 saírem iguais.

`calibration.py` e `svaj.py` ficam obsoletos sem serem corrigidos, de propósito:
- **`calibration.py`** usa `model.H` (o do CAD) como padrão e rotula o torque
  em N·m;
- **`svaj.py`** usa o H do CAD como padrão próprio.

Os dois continuam importando por causa do apelido. Corrigi-los está fora do
escopo das passadas, que só acrescentam código depois do marcador.
