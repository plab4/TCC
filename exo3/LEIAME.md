# Exoesqueleto 3: US 9.737.374 B2

Notas de trabalho do terceiro dispositivo, antes de ele entrar no TCC.

## Fontes

- **Patente:** US 9.737.374 B2, *Adaptive arm support systems and methods for use*, de Mark C. Doyle (Levitate Technologies), concedida em 22/08/2017. O PDF do USPTO é só imagem: são 48 folhas de desenho, e o texto (páginas 51 a 67) foi lido por OCR. As figuras usadas aqui são a 14C e a 14D (mecanismo), a 15A e a 15B (polia secundária 570), a 16 (momentos) e a 17A a 17C (variante circular excêntrica 660). Os recortes estão em `../patentes/US9737374B2_*.png`.
- **Artigo:** Okabe, Brittes e Brito (2026), manuscrito FMANU-CND-25-1354. O "Model 1" do artigo é a curva desta patente. As Tabelas 1 e 2 trazem as propriedades de massa do exoesqueleto comercial modelado em CREO e do membro superior.
- **Circuito do autor:** caderno de 16/10/2026 (`figuras/caderno_circuito_16-10-26.png`) e o traçado no Paint sobre a Figura 14D (`figuras/circuito_paint_fig14d.png`).

## Mecanismo (Figuras 14C e 14D)

- O chassi 580 do apoio de braço 505 gira em torno do pivô horizontal do ombro, 584.
- A âncora 558 é fixa no suporte 554 e dá o ponto de ancoragem 562 do cabo de ancoragem 560.
- O cabo 560 se enrola na polia primária 564 e se prende nela em 561. A primária gira em torno do pino 572, no chassi.
- A polia secundária 570 é solidária à primária e gira com ela em torno do 572 (caminho Pr11 da Figura 14D).
- O cabo da mola 634 se prende na secundária em 573 e corre no canal 652. Depois passa pela polia de reversão 630 (pino 632, no chassi) e chega à mola 636 em 640. A outra ponta da mola fica no gancho 638, no chassi.
- Com o braço erguido (14C), o cabo 560 cobre mais de meia volta da primária, e o cabo 634, menos de meia volta da secundária; a mola está quase recolhida. Com o braço baixado (14D), acontece o inverso, e a mola está estendida.
- A secundária 570 tem raios diferentes ao longo da volta (canal não circular, Figura 15B). Na zona Z10, o raio é constante (R20 = R21); na Z11, ele varia continuamente (de R22 a R23); na Z12, o canal forma um trecho reto. É o came de raio anisotrópico.

## Circuito vetorial

Pontos:

- O: pivô 584, encontro de C1 e C2;
- A: ponto de ancoragem 562, encontro de C1 e S;
- D: pino 572 das polias, encontro de C2 e R;
- T: ponto em que o cabo 560 deixa a polia primária, encontro de S e R.

Vetores, com as cores do Paint e u(x) = (cos x, sin x). Os ângulos γ, φ e θ são do referencial do CAD, anti-horários a partir da horizontal:

- C1 (amarelo), de A a O, fixo no suporte: C1 u(γ);
- C2 (azul), de O a D, solidário ao chassi. q é o ângulo entre C2 e a horizontal (61,724° na pose do CAD); no referencial do CAD, a direção de C2 é 180° − q, e o vetor é C2 u(180° − q) = C2 (−cos q, sin q);
- R (verde), de D a T, raio da polia primária: R u(φ);
- S (vermelho), de T a A, vão livre do cabo 560: S u(θ).

Fechamento, como no caderno:

    S u(θ) + R u(φ) + C2 u(180° − q) + C1 u(γ) = 0
    f1 = S cos θ + R cos φ − C2 cos q + C1 cos γ = 0
    f2 = S sin θ + R sin φ + C2 sin q + C1 sin γ = 0

A variável primária é q, o ângulo entre C2 e a horizontal; C2 gira com o apoio de braço. As secundárias são S e φ. Como o cabo é tangente à polia, θ não é livre: θ = φ + σ·90°, com σ = +1 ou −1 conforme o lado em que o cabo deixa a polia. Na pose do CAD, θ = φ − 90°, então σ = −1. A solução é fechada, como no exoesqueleto 1:

    d = A − D = −(C1 u(γ) + C2 u(180° − q))
    S = √(|d|² − R²)
    φ = ang(d) − σ·atan2(S, R)

## Torque: τ = b × f

O vetor b vai do encontro de C1 e C2 ao encontro de S e R, isto é, de O a T:

    b = C2 u(180° − q) + R u(φ)
    f = F_a u(θ)
    τ = (b × f)_z / 1000        (comprimentos em mm, força em N)

em que F_a é a tração no cabo 560, que puxa T para A.

β é o ângulo em O entre C2 e b, no triângulo O, D, T. A direção de b, no referencial do CAD, é 180° − q − β (102,297° na pose), e:

    (b × f)_z = −b F_a sin(θ + q + β)

Com o triângulo, b e β também saem de C2, R e do ângulo φ + q:

    b² = C2² + R² − 2 C2 R cos(φ + q)
    R² = C2² + b² − 2 C2 b cos β

Esse é o b certo porque o apoio de braço (chassi, polias, mola e cabo 634) gira em torno de 584 como um corpo só. A mola e o cabo 634 exercem forças internas a ele. O único esforço do mecanismo vindo de fora é o do cabo 560, que atua em T. É o mesmo arranjo do exoesqueleto 1, com b = OT e T no tambor. Como a linha do cabo passa por A, o braço de momento não passa de |OA| = C1, assim como |m| ≤ |B| no exoesqueleto 1.

## Pose do CAD

Valores do CAD do autor (comprimentos em mm, ângulos em graus):

| C1 | C2 | R | S | b | γ | q | φ | θ | β |
|---|---|---|---|---|---|---|---|---|---|
| 70,711 | 90,587 | 26,443 | 139,575 | 78,292 | 61,26 | 61,724 | 360 − 7,131 | 360 − 97,131 | 15,979 |

q é o ângulo entre C2 e a horizontal. No referencial do CAD, a direção de C2 é 180° − q = 118,276°.

Conferência:
- o fechamento dá resíduo de 0,0006 mm;
- θ − φ = −90°, isto é, σ = −1;
- a solução fechada, com C1, γ, C2, q e R, devolve S = 139,575 e φ = 352,869;
- |C2 u(180° − q) + R u(φ)| = 78,291, que é o b;
- o ângulo entre b e C2 é 15,979°, que é o β; entre b e C1, seria 41,037°;
- o braço de momento do cabo 560 em torno de O é −b sin(θ + q + β) = 26,042 mm, igual a C1 |sin(θ − γ)|, a distância de O à linha do cabo, que passa por A.

Com O na origem: A = (−34,000; −62,000), D = (−42,913; 79,778) e T = (−16,674; 76,495).

Pelo fechamento, b = −S u(θ) − C1 u(γ), e o braço de momento do cabo 560 em torno de O só depende de θ:

    (b × f)_z = −b F_a sin(θ + q + β) = F_a C1 sin(γ − θ)

Ele zera quando θ = γ + 180°, com o cabo alinhado a C1 e passando por O.

Grau de liberdade: o mecanismo tem um. A primária é q, e as secundárias são S e φ; θ vem de φ pela tangência, que tira uma incógnita, não uma equação. O caminho inverso também fecha: com θ dado, φ = θ + 90°, w = −(R u(φ) + C1 u(γ)), q = 180° − φ ∓ acos(w·u(φ)/C2) e S = (w − C2 u(180° − q))·u(θ). Dos dois ramos, o do sinal de cima devolve a pose do CAD, e o outro dá S negativo.

q cresce quando o apoio de braço desce: S aumenta, e o cabo 560 se desenrola da primária, como a patente descreve para o braço baixado (Figura 14D).

**Ângulo da Figura 16.** No CAD, o eixo maior do apoio de braço fica 26,741° além de C2, para baixo. Como Θ cresce quando o braço sobe:

    Θ = −(q + 26,741°)

e a pose do CAD está em Θ = −88,47°.

Pontos da Figura 16 levados a q (`circuito_cabo560.py`):

| Θ (°) | q (°) | S (mm) | θ (°) | b (mm) | β (°) | C1 sin(γ − θ) (mm) | |
|---|---|---|---|---|---|---|---|
| 22,01 | −48,750 | 0 | 283,352 | 70,711 | −12,510 | 47,399 | limite de subida |
| 4,00 | −30,741 | 38,349 | 305,721 | 64,285 | 2,046 | 63,802 | topo da marca Z11 |
| 0 | −26,741 | 44,174 | 304,730 | 64,505 | 3,266 | 63,265 | |
| −23,80 | −2,941 | 76,017 | 295,374 | 66,910 | 8,674 | 57,289 | base da marca Z11 |
| −40,30 | 13,559 | 95,666 | 287,552 | 69,307 | 11,370 | 51,115 | topo da marca Z12 |
| −56,40 | 29,659 | 112,749 | 279,516 | 72,051 | 13,405 | 43,782 | base da marca Z12 |
| −75,00 | 48,259 | 129,566 | 269,941 | 75,578 | 15,119 | 33,936 | início da Figura 16 |
| −88,47 | 61,724 | 139,575 | 262,869 | 78,292 | 15,979 | 26,041 | pose do CAD |

O braço de momento do cabo 560 fica positivo em toda a faixa: ele só zeraria em q = 101,77° (θ = 241,26°), isto é, Θ = −128,5°.

**Comparação com a patente** (`poses_fig14.py` e `circuito_cabo560.py`):
- O centro do 584 sai do furo branco no meio do pivô; com ele, |584 572| dá 152,6 px na 14C e 152,3 px na 14D, e a escala do desenho é de 1,68 px/mm.
- Na Figura 14D, q = 61,19°, contra 61,724° no CAD: a pose do CAD é a da Figura 14D.
- Na Figura 14C, q = −36,99° (Θ = 10,3°), com S = 29 mm.
- Nas duas figuras, a reta de 572 a 632, ao longo do chassi, fica 22,1° (14C) e 21,8° (14D) além de C2, no mesmo sentido da defasagem do CAD.
- O ponto A do CAD cai a 0,6 mm (14C) e a 0,3 mm (14D) do 562 desenhado.
- O came desenhado nas duas figuras é o contorno externo da Figura 15A (a 15B espelhada): o ajuste fica a 0,05 px do desenho. Dá R20 = 32,0 mm (31,96 mm na 14C e 32,11 mm na 14D), isto é, R20/R = 1,21. Na 14D, o referencial da 15B está girado de 254,0°, e na 14C, de 192,7°, sem espelhamento.
- Do came da 14C para o da 14D, o giro absoluto medido é de 61,3°. A cinemática do cabo 560, com A e D desenhados, prevê 76,8°: a diferença, 15,5°, equivale a 7 mm de cabo na primária, e os dois desenhos não são exatamente coerentes entre si.
- Partindo do came da 14D e girando pela cinemática do cabo 560, com o cabo da mola na direção de 572 para 632, o cabo sai na Z12 na pose (Θ = −88,5°), no canto entre Z12 e Z11 de Θ = −75° a cerca de −45°, na Z11 de cerca de −45° a −20° e na Z10 a partir de cerca de −5°. A marca Z11 da Figura 16 vai de −23,8° a 4,0°: a Z11 do modelo cai uns 20° abaixo, com largura parecida (25° contra 28°).
- S zera em q = −48,75°, isto é, Θ = 22,0°: com esta ancoragem, o braço não sobe além disso. A Figura 16 vai até Θ = 30°.
- Na marca Z11 da Figura 16 (Θ de −23,8° a 4,0°), as polias giram 64,2°; no came, o cabo sai na Z11 ao longo de 58,0° de giro, com a polia 630 no infinito. Entre as marcas Z12 e Z11, e na marca Z12, os giros (33,9° e 29,0°) não batem com o came, o que sugere que essas marcas da patente são só indicativas.
- A rotação das polias tirada do enrolamento do cabo 560 (θp = φ + q − S/R + constante) confirma dθp/dΘ = braço/R, com diferença de 2·10⁻⁷.

## Relação dos raios

O par de polias gira sem atrito em torno de D, e o equilíbrio dá:

    F_a R = F_s r_e(θ_p)   →   F_a = F_s r_e(θ_p) / R

São três raios diferentes:
- **R:** raio padrão, o da polia primária, que é circular.
- **ρ:** raio do came no ponto em que o cabo 634 deixa o canal. São os R20 a R25 da patente.
- **r_e:** raio efetivo da secundária 570, igual à distância de D à linha do cabo 634 no ponto em que ele deixa o canal rumo à polia de reversão 630. Ele muda com a rotação θ_p do par de polias em relação ao chassi, e é por aí que entra o raio anisotrópico.

A patente trata o cabo como uma força tangencial aplicada no raio, isto é, r_e = ρ. Isso só vale onde o cabo sai perpendicular ao raio. Com β o ângulo entre o raio do ponto de saída e o cabo, e φ a direção normal ao cabo no referencial do came:

    r_e = ρ sin β,        ρ² = r_e² + (dr_e/dφ)²

Pelo perfil da Figura 15B (`came570_raio_efetivo.csv`, colunas `raio_saida_R20` e `angulo_raio_cabo_grau`):

| Saída do cabo | r_e/ρ | β |
|---|---|---|
| Zona Z10 | 0,999 a 1,000 | 87° a 90° |
| Zona Z11 | 0,894 a 0,974 | 63° a 77° |
| Zona Z12 | 0,670 a 1,000 | 42° a 89° |

Com ρ no lugar de r_e, o momento da mola sobre o par de polias sairia até 12% maior na Z11 e até 49% maior na Z12.

**Ângulo do cabo da mola.** O cabo 634 sai do came tangente a ele e chega tangente à polia 630. No referencial do chassi, com D na origem, o centro 632 à distância L, na direção λ, e a polia de raio r630, a normal ao cabo é φc = λ − 90° + δ, e a tangência dá:

    r_e(φc − θ_p) − L cos(φc − λ) = r630   →   δ = asin((r_e − r630)/L)

δ é o ângulo entre o cabo e a linha que vai de 572 a 632. O ângulo do cabo depende de θ_p por meio de r_e, e r_e depende do ângulo do cabo, que decide o ponto de saída. A equação é implícita; `relacoes_came570.py` a resolve por ponto fixo.

Numa geometria de teste (L = 4,5 R20 e r630 = 0,5 R20; nas Figuras 14C e 14D a 630 fica a umas quatro a cinco vezes o raio do came), δ varia de −2,3° a 6,4° ao longo do curso, e r_e muda até 0,031 R20 em relação à polia no infinito, no mesmo θ_p. Os valores certos de L, λ e r630 saem do CAD.

Rotação das polias. O cabo 560 é inextensível e preso em A e em 561, então S + R·w = L_a, com w o arco enrolado na primária entre T e 561. Para cada Θ:
1. S e φ saem do fechamento;
2. w = (L_a − S)/R;
3. θ_p sai de w e da direção de T no chassi.

L_a, ou w numa pose de referência, vem do CAD.

O ponto 561 e o comprimento total do cabo 560 (S mais o arco enrolado na primária, R·w) só fixam o ângulo absoluto das polias em cada pose. Com o giro do came medido na Figura 14D, que é a pose do CAD, eles deixam de ser necessários: o giro em qualquer outra pose sai de θ_p = φ + q − S/R + constante.

Mola. A extensão acompanha o comprimento do cabo 634 entre 573 e 640, cuja derivada em relação a θ_p é r_e, em módulo: dx/dθ_p = −r_e na convenção do script (θ_p anti-horário desenrola o cabo). Então x(θ_p) = x(θ_p0) − ∫ r_e dθ_p, e a força é F_s = k (x_pose + Δx). O script confere essa taxa contra o comprimento calculado pela geometria (arco enrolado no came, vão livre e arco na 630): a diferença máxima é de 3·10⁻⁵ R20.

Verificação, como nos exoesqueletos 1 e 2: o trabalho virtual do cabo 560 sobre o apoio de braço, (b × f)_z δΘ, tem de ser igual ao da mola, que vale −F_s δx a menos do sinal das convenções. Os sinais ficam fixados no código.

## Momento do peso

A Figura 16 traz o momento do peso do braço, AWM, em torno de 584. Digitalizado, ele vale AWM = −78,21 cos Θ, com resíduo RMS de 0,19 e sem defasagem. É o momento de um peso W_a a distância fixa do pivô, com W_a·d_a = 78,2 na unidade da figura.

No modelo, o peso entra como nos exoesqueletos 1 e 2: o membro humano por de Leva (1996) e o apoio de braço pelas propriedades do CAD.

## Dados do artigo (Okabe, Brittes e Brito, 2026)

Tabela 1, peças do exoesqueleto (CREO). Tensores em kg·m², na ordem Ixx, Ixy, Ixz, Iyy, Iyz, Izz:

| Peça | Massa (kg) | Tensor de inércia |
|---|---|---|
| Chassi | 0,635 | 2,28·10⁻², −4,42·10⁻⁸, −1,82·10⁻³, 1,92·10⁻², 2,05·10⁻⁷, 5,09·10⁻³ |
| Elo do ombro | 0,0176 | 2,98·10⁻⁵, 0,0, 0,0, 1,53·10⁻⁵, 1,01·10⁻⁵, 1,53·10⁻⁵ |
| Apoio de braço | 0,650 | 5,42·10⁻⁴, −3,06·10⁻⁴, 1,57·10⁻⁴, 4,88·10⁻³, 1,01·10⁻⁴, 4,68·10⁻³ |

Almofadas de fixação: rigidez de 1,0·10⁴ N/m, rigidez torcional do apoio de braço de 750 N·m/rad e amortecimento de 1000 N·s/m.

Tabela 2, membro superior (de Leva, para um homem brasileiro médio). Tensores em kg·m², na ordem Ixx, Iyy, Izz:

| Segmento | Massa (kg) | Comprimento (mm) | Tensor de inércia |
|---|---|---|---|
| Braço | 2,244 | 281,7 | 4,44·10⁻³, 1,44·10⁻², 1,23·10⁻² |
| Antebraço | 1,341 | 269,8 | 1,42·10⁻³, 7,39·10⁻³, 6,81·10⁻³ |
| Mão | 0,505 | 68,1 até o centro de massa | 6,03·10⁻⁴, 9,87·10⁻⁴, 1,44·10⁻³ |

Observações:
- As massas da Tabela 2 correspondem a de Leva com massa corporal de 82,8 kg (2,244/0,0271). O braço (281,7 mm) e a mão (68,1 mm = 0,79 × 86,2 mm) têm os comprimentos de referência dele; o antebraço aparece com 269,8 mm, contra 268,9 mm em de Leva. O TCC usa 73,0 kg e 1,741 m.
- A Tabela 1 não dá a posição dos centros de massa, nem os eixos e o ponto de referência dos tensores. Isso precisa vir do CAD.

## Centros de massa

O artigo dá massas, comprimentos e tensores, mas não a posição dos centros de massa. Para o membro superior, ele usa o método de Zatsiorsky e Seluyanov ajustado por de Leva (1996), e as frações de de Leva para homens dão os centros a partir da articulação proximal:

| Segmento | Massa (kg) | Comprimento (mm) | Fração | Centro de massa (mm) |
|---|---|---|---|---|
| Braço | 2,244 | 281,7 | 0,5772 | 162,6 do ombro |
| Antebraço | 1,341 | 269,8 | 0,4574 | 123,4 do cotovelo |
| Mão | 0,505 | 86,2 (até o 3.º metacarpo) | 0,7900 | 68,1 do punho, como no artigo |

Com o braço estendido, o momento do peso no ombro vale 11,98 N·m na horizontal. As peças do exoesqueleto (Tabela 1 do artigo) só têm massa e tensor; a posição do centro de massa do apoio de braço não está no artigo.

## Propriedades de massa do CAD (_EXOFLEX-V1)

Relatório de massa do CAD do autor, no referencial da montagem _EXOFLEX-V1: massa total de 3,807 kg, densidade média de 2,68 g/cm³ e centro de gravidade em (−283,116; −23,502; 58,242) mm.

| Componente | Massa (kg) | X (mm) | Y (mm) | Z (mm) |
|---|---|---|---|---|
| BARRA-COSTAL-1 | 0,104 | 0 | −0,094 | 52,535 |
| EXO-MONTAGEM1 | 1,807 | −275,757 | −48,212 | 258,960 |
| BARRA-LOMBAR | 0,089 | −24,836 | −445,614 | 63,184 |
| EXO-MONTAGEM-D | 1,807 | −319,462 | 20,533 | −142,388 |

As massas e os centros dos componentes somam o total do relatório. Pela posição das peças, Y é vertical (a barra lombar fica 445,5 mm abaixo da costal), Z é lateral (os dois módulos ficam a 401,3 mm um do outro, com o meio em Z = 58,3 mm, perto da barra costal) e X é anteroposterior.

Tensor de inércia da montagem no centro de gravidade, em t·mm² (10⁻³ kg·m²): Ixx = 185,24, Iyy = 201,90, Izz = 86,29, Ixy = 10,46, Ixz = −14,30 e Iyz = 26,14. Momentos principais: 78,20, 185,39 e 209,84.

Os dois módulos têm a mesma massa, mas os centros diferem 81,5 mm no plano XY: ou estão em poses diferentes, ou não são cópias espelhadas. Para o momento do peso do apoio de braço em torno de 584, faltam a posição do 584 neste referencial e a massa e o centro só da parte que gira com o braço.

## Figura 16 digitalizada

Arquivos: `fig16_curvas.csv` (um ponto por grau), `digitalizar_fig16.py` e `figuras/fig16_conferencia.png`.

- **Eixos lidos na figura:** Θ de −80° a 40°, a cada 10°; momento de −100 a +100, a cada 20, sem unidade. As curvas vão de −75° a +30°.
- **Fechamento:** RM − (AASM + AWM) fica em no máximo 0,94 onde a RM foi mantida.
- **AASM:**
  - máximo de 75,55 em Θ = 1°;
  - acima de 95% do máximo de −20° a +9°, que é a zona Z11, de sustentação quase constante;
  - 16,25 em −75° e 20,78 em +30°;
  - AASM/|AWM| = 0,96 em 0°.
- **Unidade:** como na US 9.889.554 B2, a ordenada não tem unidade.
  - Em N·m, o momento do peso seria 78 N·m, cerca de sete vezes o do membro humano de referência do TCC (cerca de 10,5 N·m).
  - Em lbf·in daria 8,8 N·m, e em kgf·cm, 7,7 N·m. São valores plausíveis, mas a patente não permite decidir entre eles.

## Came 570 (polia secundária)

A Figura 15B é um corte pelo plano do canal, e a área hachurada é o fundo do canal, onde o cabo 634 assenta. Arquivos:
- `came570_contorno.csv`: contorno fechado, com x, y, ângulo e raio divididos por R20;
- `came570_raio_efetivo.csv`: raio efetivo em função da direção do cabo;
- `extrair_came570.py`: o script que gera o contorno, os raios e as figuras;
- `circuito_cabo560.py`: o circuito do cabo 560 na geometria do CAD, com a varredura em q, o inverso com θ como entrada, o Θ da Figura 16 e a rotação das polias;
- `poses_fig14.py`: q, a direção do chassi e o ponto 562 medidos nas Figuras 14C e 14D, contra o CAD;
- `relacoes_came570.py`: a tangência do cabo da mola com a polia 630 (ângulo do cabo e raio efetivo em função da rotação) e a conferência do alongamento da mola;
- `figuras/came570_conferencia.png` e `figuras/came570_conferencia_detalhes.png`: o contorno sobre a figura;
- `figuras/came570_raios.png`: o gráfico do contorno, do raio e do raio efetivo.

Como o contorno sai, em resumo:
1. Os vãos brancos da hachura são faixas retas, a −45° na imagem e com 21 px de largura. O script fica só com elas, o que deixa de fora o canal (mais largo e curvo), as cotas e as chamadas.
2. A região hachurada é a união dessas faixas.
3. Cada pedaço branco fora da região é preenchido se nenhum ponto dele fica a mais de 26 px dela. São as lascas entre a última linha de hachura e o contorno, as cunhas entre as linhas de raio e os entalhes onde as chamadas encostam na borda. O bolsão do 573, os chifres dele e o canal ficam de fora com folga: dos brancos que sobram, o que menos se afasta da região chega a 45,7 px dela.
4. O contorno fechado inclui o lado côncavo do bolsão.

Ângulos anti-horários a partir da horizontal à direita, na figura girada para a leitura, com centro no furo 654 (pino 572). As linhas de chamada das cotas, localizadas na imagem, dão as zonas: Z10 de 89,6° a 140,4°, Z11 de 152,4° a 218,8° e Z12 de 242,6° a 292,6°.

Conferência com a patente:
- **Z10:** o raio fica entre 0,994 e 1,004 R20, constante como pede R20 = R21.
- **Z11:** o raio cai continuamente de 0,961 para 0,663 R20, com R23 < R22.
- **Z12:** o trecho é reto, com desvio máximo de 0,003 R20 (1,7 px) de uma reta.

Resultados, divididos por R20 = 482,7 px:

| Grandeza | Valor |
|---|---|
| Raio nas pontas da Z10 (R20, R21) | 1,004 e 1,003 |
| Raio nas pontas da Z11 (R22, R23) | 0,961 e 0,663 |
| Raio nas pontas da Z12 | 0,513 e 0,329 |
| Furo 654 (raio) | 0,122 |
| Furo 573 | raio 0,098, a 0,374 do centro, a 72,1° |
| Raio efetivo com o cabo saindo na Z10 | 1,000 a 1,004 |
| Raio efetivo com o cabo saindo na Z11 | 0,639 a 0,875 |
| Raio efetivo com o cabo saindo na Z12 | 0,329 a 0,333 |

O raio efetivo é a distância do pino 572 à linha do cabo onde ele deixa o canal, para cada direção do cabo no referencial do came. Como o cabo tracionado passa reto sobre concavidades, ele é a função suporte da envoltória convexa do canal. É o r_e da relação F_a = F_s r_e/R. Falta só a razão R20/R, entre o came e a polia primária, que sai do CAD.

Escala: o furo 654 tem raio de 0,122 R20. Com o diâmetro do eixo 572 no CAD, tudo passa a milímetro.

Zonas no gráfico de momentos: na Figura 16, a zona Z12 vai de Θ = −56,4° a −40,3°, e a Z11 de −23,8° a +4,0°. A Z11 coincide com o trecho de sustentação quase constante do AASM.

## O que falta do CAD

Já vieram do CAD: C1, γ, C2, R, a pose (q = 61,724°, a da Figura 14D) e a defasagem de 26,741° entre C2 e o eixo maior (seção "Pose do CAD").

- O ponto 561 e o comprimento do cabo 560 não são necessários: o giro do came na pose sai da Figura 14D.
- A escala e o giro do came saíram das Figuras 14C e 14D (R20 = 32,0 mm). Vale conferir R20 na peça real.
- A polia 630 e a mola ficam fora da varredura, por decisão do autor; o cabo da mola é tomado na direção de 572 para 632.
- Centros de massa: os do membro superior saem do artigo (seção "Centros de massa"). Do CAD veio o relatório de massa da montagem (seção "Propriedades de massa do CAD"); para o apoio de braço, falta a posição do 584 no mesmo referencial e a separação da parte que gira com o braço.

## Perguntas em aberto

1. O exo 3 fica num relatório separado até o modelo fechar, ou entra já no TCC, nas seções 3.3, 4.3 e 5.3?
2. Qual é o lado da tangência (σ), e qual o Θ da pose do CAD?
3. O came do exoesqueleto do artigo é o 570 da Figura 15, que gera a Figura 16, ou o 660 da Figura 17, que gera a 17C?
4. Que indivíduo de referência usar: o do TCC (73,0 kg) ou o do artigo (82,8 kg)?
5. Se houver pontos da Figura 16 digitalizados para o artigo (WebPlotDigitizer), vale compará-los com estes.
