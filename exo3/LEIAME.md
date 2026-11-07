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

Vetores, com as cores do Paint e u(x) = (cos x, sin x):

- C1 (amarelo), de A a O, fixo no suporte: C1 u(γ);
- C2 (azul), de O a D, solidário ao chassi: C2 u(α), com α = Θ + α0;
- R (verde), de D a T, raio da polia primária: R u(φ);
- S (vermelho), de T a A, vão livre do cabo 560: S u(q).

Fechamento, como no caderno:

    S u(q) + R u(φ) + C2 u(α) + C1 u(γ) = 0
    f1 = S cos q + R cos φ + C2 cos α + C1 cos γ = 0
    f2 = S sin q + R sin φ + C2 sin α + C1 sin γ = 0

**Ponto a confirmar.** No caderno, q aparece como entrada, e S e φ como incógnitas. Como o cabo é tangente à polia, q não é livre: q = φ + σ·90°, com σ = +1 ou −1 conforme o lado em que o cabo deixa a polia. A entrada é o ângulo do apoio de braço, Θ, que entra por α. As incógnitas continuam sendo S e φ, e a solução é fechada, como no exoesqueleto 1:

    d = A − D = −(C1 u(γ) + C2 u(α))
    S = √(|d|² − R²)
    φ = ang(d) − σ·atan2(S, R)

## Torque: τ = b × f

O vetor b vai do encontro de C1 e C2 ao encontro de S e R, isto é, de O a T:

    b = C2 u(α) + R u(φ)
    f = F_a u(q)
    τ = (b × f)_z / 1000        (comprimentos em mm, força em N)

em que F_a é a tração no cabo 560, que puxa T para A.

Esse é o b certo porque o apoio de braço (chassi, polias, mola e cabo 634) gira em torno de 584 como um corpo só. A mola e o cabo 634 exercem forças internas a ele. O único esforço do mecanismo vindo de fora é o do cabo 560, que atua em T. É o mesmo arranjo do exoesqueleto 1, com b = OT e T no tambor. Como a linha do cabo passa por A, o braço de momento não passa de |OA| = C1, assim como |m| ≤ |B| no exoesqueleto 1.

## Relação dos raios

O par de polias gira sem atrito em torno de D, e o equilíbrio dá:

    F_a R = F_s r_e(θ_p)   →   F_a = F_s r_e(θ_p) / R

- **R:** raio padrão, o da polia primária, que é circular.
- **r_e:** raio efetivo da secundária 570, igual à distância de D à linha do cabo 634 no ponto em que ele deixa o canal rumo à polia de reversão 630. Ele muda com a rotação θ_p do par de polias em relação ao chassi, e é por aí que entra o raio anisotrópico.

Rotação das polias. O cabo 560 é inextensível e preso em A e em 561, então S + R·w = L_a, com w o arco enrolado na primária entre T e 561. Para cada Θ:
1. S e φ saem do fechamento;
2. w = (L_a − S)/R;
3. θ_p sai de w e da direção de T no chassi.

L_a, ou w numa pose de referência, vem do CAD.

Mola. A extensão acompanha o comprimento do cabo 634 entre 573 e 640, cuja derivada em relação a θ_p é r_e. A força é F_s = k (x_pose + Δx).

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

O perfil do came 570 não foi extraído. A borda da área hachurada da Figura 15B se mistura com o bolsão do 573 e com as linhas de cota. O caminho mais seguro é inserir a figura como canvas no CAD e traçar a spline sobre ela.

## O que falta do CAD

1. Pose de referência, com o ângulo Θ do eixo maior do apoio de braço.
2. Posições de O (584), A (562) e D (572) nessa pose. Delas saem C1, γ, C2 e α0.
3. Raio R da polia primária 564, na linha de centro do cabo.
4. Ponto 561 na primária e comprimento do cabo 560, ou o arco enrolado na pose.
5. Perfil do canal da secundária 570, em torno do 572, com o ponto 573 e o ângulo entre a secundária e a primária.
6. Polia de reversão 630 (centro 632 e raio), ponto 640 e gancho 638.
7. Mola 636: rigidez, comprimento livre e comprimento na pose, que a patente não informa.
8. Centro de massa do apoio de braço em relação a 584.

## Perguntas em aberto

1. O exo 3 fica num relatório separado até o modelo fechar, ou entra já no TCC, nas seções 3.3, 4.3 e 5.3?
2. Qual é o lado da tangência (σ), e qual o Θ da pose do CAD?
3. O came do exoesqueleto do artigo é o 570 da Figura 15, que gera a Figura 16, ou o 660 da Figura 17, que gera a 17C?
4. Que indivíduo de referência usar: o do TCC (73,0 kg) ou o do artigo (82,8 kg)?
5. Se houver pontos da Figura 16 digitalizados para o artigo (WebPlotDigitizer), vale compará-los com estes.
