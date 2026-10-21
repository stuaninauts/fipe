# MVP do fipe: julgamento das perguntas (agente 2)

Data: 2026-10-21. Base: relatório do agente 1 (`mvp-agente1-perguntas.md`), repo `~/Desktop/ment/fipe` (CLAUDE.md, ADRs
0001 a 0005, `fipe/aggregate.py`, `web/src/views/`), preview em http://127.0.0.1:4360 e `data/processed/prices.parquet`.
Todos os números que eu acrescento são **preliminares**: saíram de scripts rápidos em
`/tmp/claude-1000/-home-stuani-Desktop-ment/d41a15ec-334f-460b-a4fb-43da1b54c63e/scratchpad/agente2/` (v1.py, v2.py,
v3.py, scores.py) e não passaram por `aggregate.py` nem por teste. Nenhum preço por modelo aparece aqui.

## 1. Resumo

1. MVP recomendado, em 6 perguntas (5 análises e 1 de método): **o primeiro ano** (o mito dos 20%, contado do lado de quem compra);
   **em que idade o carro perde mais**; **o que sobra em 5 anos depende do ano da compra**; **o choque de 2022 e o que
   sobrou dele**; **o que segura valor** (versão, faixa, marca, diesel, sempre comparando carros do mesmo ano de
   compra e da mesma faixa); **o que a tabela FIPE mede**.
2. Por quê: são as únicas candidatas com nota de viabilidade 3 ou mais *e* valor alto para recrutador ou público.
   Juntas, contam uma história só e cada página mostra uma escolha de método (coorte, pares por idade, janela fixa,
   controle por ano e faixa, controle dentro do modelo, composição do catálogo).
3. Duas verificações do agente 1 não se sustentam. (a) As comparações de grupo feitas na coorte agregada confundem grupo com
   período: controlando o ano de compra, a vantagem das japonesas "só nas faixas baratas" se inverte, e Hyundai e Jeep
   deixam de parecer fortes. (b) O "zero km do mesmo código cai ~3% real ao ano" vem de mediana encadeada: em
   comparação direta, 2015-2025 dá +27% real.
4. Duas perguntas sobem: a Q25 (topo de linha contra entrada do mesmo modelo, que ele não verificou) é o resultado mais
   robusto de "quem segura valor"; e entra uma pergunta nova, "o choque já passou?".
5. Sai do MVP atual: o título "investimento", a seção "dois tombos" e o "59% aos 5 anos" como manchete.

## 2. Tabela de julgamento

### Pesos

| Critério | Peso | Por quê |
|---|---|---|
| R, recrutador técnico | 25% | É peça de portfólio: o leitor que decide é o recrutador. |
| V, viabilidade e risco | 25% | O site vai ao ar com o nome do autor: um título errado custa mais que uma pergunta a menos. |
| M, mostra método | 20% | Sobrepõe-se a R; com peso cheio, o mesmo mérito contaria duas vezes. |
| P, público geral | 20% | Sem leitor o portfólio não circula; o público só pesa menos que R e V. |
| E, entusiastas | 10% | Público mais estreito e que se sobrepõe a P. |

Regra de corte: **V de 2 ou menos não entra no MVP**, qualquer que seja o total (v2 ou descarte). Com os cinco pesos
iguais, as mesmas 7 primeiras perguntas ficam no topo (só Q20 e Q21 trocam de lugar com Q5), então a escolha não
depende dos pesos.

### Notas

Total = 0,25R + 0,20P + 0,20M + 0,10E + 0,25V (escala 1 a 5). Q26 e Q27 são perguntas minhas.

| id | Pergunta | R | P | M | E | V | Total | Veredito |
|---|---|---|---|---|---|---|---|---|
| Q17 | Quanto perdi depende de quando comprei? | 5 | 5 | 5 | 4 | 4 | **4,65** | MVP (página 3) |
| Q25 | Versão topo perde mais que a de entrada? | 5 | 5 | 5 | 4 | 3 | **4,40** | MVP (página 5, seção principal; condicionada ao parser de família) |
| Q26 | Em que idade o carro perde mais por ano? (nova) | 4 | 5 | 4 | 4 | 4 | **4,20** | MVP (página 2) |
| Q2 | Carro japonês não desvaloriza? | 4 | 4 | 5 | 5 | 3 | **4,05** | MVP (seção da página 5) |
| Q27 | O preço do usado já voltou ao normal depois de 2022? (nova) | 4 | 5 | 4 | 5 | 3 | **4,05** | MVP (segunda metade da página 4) |
| Q12 | O que aconteceu com o usado em 2021-22? | 4 | 4 | 4 | 4 | 4 | **4,00** | MVP (página 4) |
| Q1 | Zero km perde 20% ao sair da loja? | 4 | 5 | 4 | 4 | 3 | **3,95** | MVP (página 1, reformulada) |
| Q16 | Zero km subiu acima da inflação? O popular sumiu? | 4 | 5 | 5 | 4 | 2 | 3,90 | v2 (barrada pelo corte V) |
| Q20 | A FIPE tira carro da tabela? (sobrevivência) | 5 | 1 | 5 | 2 | 5 | 3,90 | MVP (seção da página 6) |
| Q21 | A mediana representa o carro da rua? | 5 | 2 | 5 | 2 | 4 | 3,85 | MVP (seção da página 6 e sensibilidade na 4); ponderação em v2 |
| Q5 | Picape diesel não perde valor? | 3 | 3 | 4 | 5 | 4 | 3,65 | MVP (seção da página 5) |
| Q18 | No papel meu carro vale o que paguei? | 3 | 4 | 3 | 2 | 5 | 3,60 | MVP como seção (páginas 2 e 3), não como página |
| Q6 | Carro de luxo desvaloriza mais? | 3 | 3 | 4 | 4 | 4 | 3,55 | MVP (seção da página 5) |
| Q19 | O que a FIPE mede? Ela atrasa? | 4 | 3 | 4 | 3 | 3 | 3,45 | MVP (seção da página 6, só o que tem fonte) |
| Q10 | Comprar no fim do ano é melhor? | 4 | 5 | 3 | 4 | 1 | 3,25 | v2 (mensal no pipeline) |
| Q4 | SUV segura mais valor? | 3 | 4 | 3 | 4 | 2 | 3,05 | v2 |
| Q22 | O que a FIPE mudou nos rótulos? | 4 | 1 | 3 | 2 | 4 | 3,00 | MVP como nota da página 6 (não é pergunta de leitor) |
| Q7 | Elétrico desvaloriza rápido? | 3 | 4 | 3 | 5 | 1 | 2,90 | v2 (2027+) |
| Q3 | Automático desvaloriza menos? | 3 | 3 | 3 | 4 | 2 | 2,85 | v2, só se o parser de nome existir |
| Q13 | Corte de IPI derrubou o usado? | 3 | 3 | 3 | 4 | 2 | 2,85 | v2; tirar a seção do MVP |
| Q23 | Quanto o ano-modelo anterior perde quando chega o novo? | 3 | 4 | 3 | 4 | 1 | 2,80 | v2 |
| Q11 | Carro antigo para de desvalorizar? | 2 | 3 | 3 | 5 | 2 | 2,70 | v2; no MVP, só uma frase cautelosa na página 2 |
| Q9 | Carro chinês desvaloriza muito? | 2 | 4 | 2 | 5 | 1 | 2,45 | v2 (2027+) |
| Q14 | Ford usado despencou com a saída? | 2 | 3 | 2 | 4 | 2 | 2,40 | descartar (fica no Explorar) |
| Q24 | Motor 1.0 segura mais que 2.0? | 2 | 3 | 2 | 4 | 2 | 2,40 | descartar (Q25 responde melhor) |
| Q8 | Flex vale mais que só gasolina? | 2 | 2 | 2 | 2 | 1 | 1,75 | descartar |
| Q15 | Juros altos derrubam o usado? | 2 | 3 | 1 | 2 | 1 | 1,75 | descartar |

### Justificativas (uma frase por critério)

- **Q17.** R5: desenho de coorte, separação entre idade e período, conversa de entrevista pronta. P5: pessoal e
  contraintuitivo (quem comprou zero km em 2017-2020 tinha, 5 anos depois, 94% a 99,5% do preço pago no valor de face).
  M5: coorte, inflação e período ficam explícitos. E4: rende discussão. V4: n de 500 a 900 por ano de compra; exige
  rever a ADR 0005.
- **Q25.** R5: o controle dentro do modelo elimina a maior confusão de qualquer comparação por grupo. P5: decide
  qual versão comprar. M5: comparação pareada dentro de família e ano. E4: discutido. V3: estável nos três períodos
  (preliminar), mas a família sai da primeira palavra do nome e precisa de parser com teste.
- **Q26.** R4: pares do mesmo carro (`CAR`), sem viés de sobrevivência, n acima de 10 mil por idade até 20 anos. P5:
  decide quando comprar e quando trocar, e contraria a ideia de que "depois do 1º ano a pior parte passou". M4: separa idade de
  período (sem 2022, mostrado por período). E4: discutido. V4: o formato se repete em 2005-12 e 2013-19; só a cauda
  acima de 20 anos depende do período.
- **Q2.** R4: história de confusão por período que se conta em dois minutos. P4: pesa na escolha da marca. M5: a
  leitura crua inverte quando se controla ano de compra e faixa. E5: discussão eterna. V3: marca mistura modelos e o
  número muda com o método (publicar coorte e transversal juntos).
- **Q27.** R4: janela fixa do mesmo carro, sem encadear medianas. P5: "é hora de comprar?" é a dúvida de quem está
  no mercado. M4: compara com janelas anteriores de mesma duração. E5: muito compartilhável. V3: dado termina em
  jan/2025, a FIPE pode atrasar em relação ao atacado, jan/2026 pode mudar a resposta.
- **Q12.** R4: análise de sensibilidade (massa, faixa de idade fixa) sobre um número de manchete. P4: todo mundo
  lembra de 2021-22. M4: pares do mesmo carro e variantes. E4: discutido. V4: alta real em todas as variantes,
  contado sem causa.
- **Q1.** R4: mostra a diferença entre o que a FIPE mede (revenda) e o que o mito afirma, e um teto suspeito na tabela.
  P5: a pergunta mais feita; do lado do comprador, vira um número de decisão. M4: exige coorte de 1 ano e desconfiar da
  razão no mesmo janeiro. E4: gancho certo. V3: a regra da FIPE para o ano corrente não é pública e revenda não é troca.
- **Q16.** R4: o mesmo produto contra a composição do catálogo é problema clássico de índice de preços. P5: "o carro
  popular acabou" é assunto nacional. M5: exige separar preço do mesmo código e mudança de catálogo. E4: discutido.
  V2: o índice do mesmo código muda de sinal conforme o método, catálogo não é venda e publicar R$ esbarra na ADR 0001.
- **Q20.** R5: justifica a escolha de método (usado quase nunca sai, zero km sai). P1: leigo não liga. M5: argumento
  central da coorte. E2: pouco. V5: dado pronto.
- **Q21.** R5: "e a ponderação?" é a primeira pergunta de quem revisa dados. P2: abstrato. M5: a composição muda a
  manchete (+9,0% para +12,5%). E2: pouco. V4: a sensibilidade sai hoje; ponderação por venda depende de dado externo.
- **Q5.** R3: usa um campo que já existe, pouco novo. P3: confirma o senso comum, útil para um nicho. M4: sobrevive ao
  controle ano x faixa. E5: público de picape é fiel. V4: n de 1.403 aos 5 anos; a quebra de 2011 se resolve
  restringindo a 2011+.
- **Q18.** R3: didático, já no export. P4: "meu carro não desvalorizou" é crença comum. M3: conceito simples. E2: pouco
  compartilhável sozinho. V5: sem risco.
- **Q6.** R3: já está no site. P3: confirma senso comum, e pouca gente compra luxo. M4: separa faixa de marca. E4: rende
  discussão. V4: n alto.
- **Q19.** R4: leitura crítica da fonte. P3: ajuda a entender, não decide. M4: leitura da definição contra o uso. E3:
  médio. V3: a metodologia da FIPE não é pública em detalhe e a comparação com atacado tem uma fonte só.
- **Q10.** R4: o mensal no pipeline é uma boa história de engenharia. P5: decide quando comprar. M3: comparação simples.
  E4: interessa. V1: nove meses de um ano, sem out-dez/2025 e jan/2026.
- **Q4.** R3: curadoria manual. P4: SUV é a compra da moda. M3: precisa controlar período (SUVs são recentes). E4:
  discutido. V2: lista curada e confusão com período.
- **Q22.** R4: auditoria visível. P1: irrelevante para leigo. M3: detecção simples. E2: pouco. V4: falta só dizer
  se o erro é da FIPE ou do scraper.
- **Q7.** R3: rótulo reconstruído pelo código é bom detalhe. P4: tema quente. M3: coorte simples. E5: muito
  compartilhável. V1: n de 19 a 53, mistura premium e cortes de preço de fábrica.
- **Q3.** R3: regex de nome é engenharia, mas classificação sem teste. P3: o resultado provável é "sem diferença". M3:
  controle por faixa. E4: interessa. V2: 60% dos nomes sem rótulo de câmbio.
- **Q13.** R3: contexto externo datado. P3: história. M3: um ponto por ano. E4: o entusiasta pensa em IPI na hora. V2:
  causal, e o tempo de 2010 não casa com o corte.
- **Q23.** R3: depende do mensal. P4: interessa a quem vai trocar. M3: simples. E4: interessa. V1: um ciclo parcial.
- **Q11.** R2: pouco método. P3: curiosidade. M3: precisa separar período. E5: o assunto favorito do entusiasta. V2:
  a desaceleração é quase toda de 2020-2025, e idades de 35 anos ou mais só existem a partir de 2020.
- **Q9.** R2, M2: um groupby por marca. P4, E5: tema quente. V1: de 2 a 19 pares.
- **Q14.** R2, M2: groupby com mistura de modelos. P3, E4: curioso. V2: diferença só em 2022 e leitura causal.
- **Q24.** R2, M2: cilindrada confunde com modelo e faixa. P3, E4: algum interesse. V2: Q25 controla isso melhor.
- **Q8.** Notas 1-2: compara épocas e origem, não combustível.
- **Q15.** Notas 1-2: 21 pontos anuais, correlação espúria e leitura causal.

## 3. MVP recomendado

Seis perguntas, nesta ordem de leitura. A ordem vai do que todo leitor pergunta (primeiro ano, idade) para o que
explica a variação (ano da compra, choque), depois para a escolha do carro (o que segura valor), e fecha com o método.
Os títulos afirmam só o que o dado sustenta; a pergunta do leitor vai como subtítulo.

### 1. "Zero km perde 20% ao sair da loja?" (Q1 reformulada)

- **Título:** "No primeiro ano, o carro perde cerca de 12% na tabela FIPE"
- **Resposta (preliminar):** um ano depois de comprado zero km, o mesmo carro vale na FIPE 88% do preço de novo em
  mediana (84% descontada a inflação); em anos sem choque, de 80% a 95%. Para quem compra: um seminovo de 1 ano custa
  ~14% menos que o mesmo carro zero km no mesmo janeiro (`retention_by_age`, idade 1: 86%). O mito dos 20% fala do que
  o dono recebe ao vender para uma loja, e isso a FIPE não mede.
- **Cuidado principal:** a evidência principal é a coorte de 1 ano, não a razão no mesmo janeiro. Em 22 janeiros e
  ~13 mil pares, o "carro do ano usado" nunca passou de 97% do zero km, nem em 2022, enquanto a coorte de 1 ano
  passou de 100% em 2021-22 (111% no valor de face). Isso tem cara de regra da tabela para o ano corrente; a página deve
  dizer isso e tratar os ~10% da razão no mesmo janeiro como "o que a tabela mostra", não como mercado.

### 2. "Em que idade o carro perde mais valor?" (Q26, com Q18 e uma frase de Q11)

- **Título:** "Do 2º ao 5º ano, o carro perde cerca de 10% ao ano; depois, menos"
- **Resposta (preliminar):** seguindo o mesmo carro de um janeiro para o outro (sem 2022), a perda real mediana é de
  10% a 11% ao ano entre 2 e 5 anos (5% a 6% no valor de face), cerca de 8% aos 10 anos e 7% aos 20. Em carro velho,
  boa parte da perda real é inflação: o valor de face cai 1% a 2% ao ano.
- **Cuidado principal:** são medianas de 2005 a 2025 sem o ano do choque. O formato até 10 anos se repete por período, mas a
  desaceleração depois dos 15 anos é bem mais forte em 2023-25 (-3,5% aos 25 anos) do que em 2013-19 (-7,7%). Acima
  de 30 anos, n pequeno e só a partir de 2020: no máximo uma frase, sem "carro antigo valoriza".

### 3. "Quanto sobra depois de 5 anos depende de quando você comprou?" (Q17, com Q18)

- **Título:** "Cinco anos depois, o que sobra depende do ano da compra"
- **Resposta (preliminar):** descontada a inflação, quem comprou zero km entre 2005 e 2012 tinha, 5 anos depois, de
  40% a 46% do que pagou; entre 2013 e 2016, de 52% a 60%; entre 2017 e 2020, de 73% a 75%. No valor de face, o último
  grupo viu o carro valer de 94% a 99,5% do que pagou. Esse é o melhor exemplo de nominal contra real do site.
- **Cuidado principal:** não publicar um número agregado de todos os anos como manchete. Ele depende da janela (48% com
  compras até 2015, 54% com 2004-2020) e esconde a faixa de 40% a 75%. O corte no mesmo janeiro (o "59%") fica como "comparado
  com um zero km de hoje", com idades acima de 10 só na tabela. Exige rever a ADR 0005 e um agregado novo com teste golden.

### 4. "O que aconteceu com o usado em 2021-22, e já passou?" (Q12 com Q27)

- **Título:** "Em 2022, o usado ficou mais caro mesmo envelhecendo um ano"; segunda seção: "O que sobrou do choque".
- **Resposta (preliminar):** +9,0% real na mediana do catálogo e +12,5% nas marcas de massa com 1 a 15 anos; 2022 é a
  única alta real em 21 anos em todas as variantes. Depois disso, a queda foi menor que o normal: o mesmo carro de jan/2021 a jan/2025
  perdeu 7% real (e subiu 19% no valor de face), contra 24% a 44% nas janelas de 4 anos antes do choque. Quem comprou
  usado no pico (jan/2022) perdeu 15% real em 3 anos, menos que os 19% a 20% de quem comprou em 2017 ou 2018.
- **Cuidado principal:** descritivo, com contexto datado e com fonte ("coincide com" a falta de chips). A FIPE pode
  andar atrás do atacado (em 2026, a Auto Avaliar mediu -9,3% no atacado contra -2,4% na FIPE para carros de até 3 anos). O
  dado termina em jan/2025: dizer "até jan/2025" e atualizar quando entrar jan/2026. Mostrar a sensibilidade
  (catálogo, massa 1-15) também resolve parte da A3 do agente 1.

### 5. "O que segura valor: versão, faixa de preço, marca ou diesel?" (Q25, Q2, Q5, Q6)

- **Título:** "O que segura valor: versão de entrada, carro mais barato, algumas marcas e diesel"
- **Resposta (preliminar), comparando carros do mesmo ano de compra e da mesma faixa de preço, aos 5 anos:**
  - dentro do mesmo modelo, a versão mais cara retém ~9% menos que a de entrada (em 8 de cada 10 modelos, estável em
    2004-10, 2011-16 e 2017-20);
  - diesel retém ~13% a mais que gasolina;
  - Toyota e Honda ficam 7% a 9% acima do esperado. Nissan e Mitsubishi ficam na média ou abaixo, e Citroën, Peugeot, BMW, Audi e
    Volvo, 7% a 15% abaixo. Mercedes-Benz não perde mais que a média, e Porsche fica 17% acima;
  - o quinto mais barato dos zero km segura mais que o mais caro (já está no site).
- **Cuidado principal:** toda comparação é **relativa ao ano de compra e à faixa**, porque o ano da compra sozinho move a
  retenção de 40% para 75%. Comparar sem esse controle inverte resultados (ver a seção 5). Marca mistura modelos e não é país de
  origem. A Q25 depende de um parser de família (primeira palavra do nome) com teste e revisão manual. O diesel fica
  restrito a 2011+ por causa da troca de rótulo. Publicar coorte e corte transversal lado a lado: os rankings de
  marca concordam razoavelmente (Spearman 0,78).

### 6. "O que a tabela FIPE mede, e o que este site não mede?" (Q19, Q20, Q21, Q22)

- **Título:** "O que a tabela FIPE mede, e o que ela não mede"
- **Resposta:** a página reúne seis pontos.
  - Citação literal da FIPE: "preços médios para pagamento à vista, praticados na revenda".
  - Mediana do catálogo, não da frota: 27% dos preços são de marcas premium, que vendem perto de 2% dos novos. A sensibilidade muda o choque de +9,0% para +12,5%.
  - Usados quase nunca saem da tabela (~0,03% ao ano). Zero km sai: 20% seguem à venda após 5 anos. Isso decide a coorte.
  - Duas trocas de rótulo: diesel em 2011 e flex em 2024.
  - O teto de 97% do carro do ano.
  - Checagem externa de 2021 e as 1.175 recoletas que batem 100%.
- **Cuidado principal:** não especular sobre a regra da FIPE; dizer o que não se sabe. Na troca de 2011, dizer que não dá
  para saber se o erro é da FIPE ou do scraper v1 sem recoletar uma amostra.

### O que muda em relação ao MVP atual

- **Fica:**
  - o choque de 2022 (dados, gráfico e tabela);
  - a comparação por faixa de preço;
  - o Explorar, com as correções M6 e M7 (idade até 10, marcas de nicho fora, uma só definição de faixa);
  - a página Dados (pode virar a parte de qualidade da página 6).
- **Sai:**
  - o título "Em 2022, carro usado virou investimento";
  - a seção "Dois tombos que ainda pedem explicação" (Q13 vai para v2; o tempo do corte de 2010 não casa, e com um ponto por ano "coincide com" fica fraco);
  - "59% aos 5 anos" como manchete e card;
  - "a perda ao sair da loja ficou perto de 10%, não 20%";
  - a frase "a mediana não se deixa levar por carros raros e caros" sem a ressalva de composição.
- **Muda o enquadramento:**
  - zero km: de "mito derrubado" para "o primeiro ano, do lado de quem compra", com a coorte de 1 ano como evidência;
  - depreciação: de uma página com corte no mesmo janeiro para duas (perda por idade e coorte por ano de compra);
  - choque: ganha a sensibilidade e a seção pós-choque;
  - Método: vira "o que a FIPE mede".
- **Entra:** "depende de quando comprou", "o que segura valor" (com controles e a Q25) e a seção pós-choque.
- **Home:** seis cards, sem número no card que exija ressalva (o "59%" sai). Na abertura, trocar "431.303 preços de janeiro de carros
  vendidos no Brasil" por algo como "431.303 preços de janeiro (versões e anos-modelo) da tabela FIPE". Trocar também
  "comparado com ele mesmo", que só vale para algumas páginas.
- **Pipeline:** `aggregate.py` ganha três tabelas novas (coorte por ano de compra e idade, perda por idade a partir de
  `_yearly_pairs`, e retenção relativa a ano x faixa por grupo) e uma sensibilidade do choque. Cada uma com teste golden,
  como pede a ADR 0005.

## 4. Por público

| Público | As 3 mais fortes | Por quê |
|---|---|---|
| Recrutador técnico | Q17, Q25, Q20+Q21 (página 6) | Coorte contra corte transversal, controle dentro do modelo, sobrevivência e composição: os quatro assuntos que um entrevistador de dados puxa. Reserva: Q2, pela inversão ao controlar o período. |
| Público geral | Q1, Q26, Q25 | As três mudam uma decisão: zero km ou seminovo, quando trocar, qual versão comprar. Q17 e Q27 contam o passado; são ótimas, mas decidem menos. |
| Método | Q17, Q2, Q21 | Período contra idade, confusão por composição de grupo (a leitura crua inverte) e catálogo contra frota. Q16 seria a quarta, na v2. |
| Entusiastas | Q2, Q27, Q5 | Marca, "já passou?" e picape diesel são o que se discute em fórum e grupo. Q7 (elétrico) entra quando houver n. |

## 5. Onde discordo do agente 1

1. **Comparações de grupo na coorte agregada (Q2, Q4, Q5, Q7) estão confundidas pelo período.** O ano da compra
   sozinho leva a retenção aos 5 anos de 40% para 75%, e marcas e segmentos entram na tabela em anos diferentes.
   Recalculei relativo à mediana do mesmo ano de compra (preliminar, v1.py e v2.py):
   - "japonesas só nas faixas baratas" se inverte: na faixa mais barata elas ficam até um pouco abaixo (1,09 contra 1,12
     da mediana do ano) e ganham vantagem nas faixas médias (+5% a +7%);
   - os "Hyundai 64%" e o Jeep alto são efeito do período (ano mediano de compra 2016-2017): controlados, ficam na média
     ou abaixo;
   - "alemãs premium perdem mais" não vale para Mercedes-Benz (1,03 com controle de ano e faixa). Vale para BMW, Audi e
     Volvo;
   - o diesel sobrevive ao controle (+13%), e o SUV precisa do mesmo teste antes de qualquer conclusão.
2. **"54% aos 5 anos" não serve de manchete, nem na versão coorte.** É uma média ponderada de anos muito diferentes:
   48% com compras até 2015, 54% com 2004-2020, 52% como mediana das medianas anuais. O agregado por idade também mistura
   janelas (a idade 10 só tem compras até 2015). A manchete honesta é a faixa por ano de compra, ou seja, a Q17. Por isso
   fundi as perguntas 1 e 2 do MVP dele.
3. **O "zero km do mesmo código cai ~3% real ao ano" (índice encadeado 0,55) é frágil.** Encadear medianas acumula
   desvio, e a própria ADR 0005 adiou o índice encadeado por isso. Em comparação direta do mesmo código zero km:
   2005→2015 dá -36% real (n=41), 2015→2025 dá +27% (n=39) e 2019→2025 dá +22% (n=126). A explicação dele para a
   diferença entre coorte e corte transversal vale para 2004-2015, não para a série toda. A Q16 é de risco alto, não médio.
4. **A Q25 merecia verificação, e é a melhor candidata a "quem segura valor".** Comparei a versão mais cara com a de
   entrada dentro da mesma família (marca mais a primeira palavra do nome), mesmo ano de compra e mesmo combustível, com
   pelo menos 3 versões e diferença de preço de 15% ou mais. A mais cara retém 9% menos aos 5 anos (6% aos 3), em 81% de
   1.441 grupos, com a mesma magnitude em 2004-10, 2011-16 e 2017-20. Ele a deixou para a v2 como "não verificado".
5. **Q11 não é a "melhor oitava pergunta".** A desaceleração da perda em carro velho é sobretudo de 2020-2025: em
   2013-19, carros de 20 a 30 anos perdiam ~8% real ao ano, quase como os de 8 a 10. Idades de 35 anos ou mais só
   existem a partir de 2020, que inclui o choque. Para mim, é v2.
6. **A2 está certa, e a evidência é mais forte que a apresentada.** O máximo da razão "carro do ano / zero km" em 22
   janeiros é 0,97, sem nenhum par a partir de 0,99, enquanto a coorte de 1 ano passa de 100% em 2021-22. Isso desloca a
   página: a evidência passa a ser a coorte, e o enquadramento passa a ser o do comprador (a FIPE mede o que se paga na
   loja, não o que se recebe na troca). Não precisa segurar a página até ouvir a FIPE.
7. **Q18 não precisa de página própria.** A melhor demonstração de nominal contra real está dentro da Q17 (comprados
   em 2017-2020: 94% a 99,5% no valor de face, 73% a 75% real). Como página solta, compete com o resto e repete.
8. **A quebra de 2011 pesa menos na Q5 do que ele diz.** A coorte casa por `fuel_group`, então os diesel rotulados
   "Gasolina" antes de 2011 simplesmente não casam e caem fora. O grupo diesel da coorte já é, na prática, 2011+. Vale
   restringir de forma explícita, mas não é um bloqueio.
9. **Faltou uma pergunta óbvia: "o choque já passou?"** Ele usa as quedas de 2023-24 só para criticar o título
   "investimento". A janela fixa de 4 anos (mesmo carro, sem encadear) mostra o nível ainda acima do anterior, o
   resultado mais atual do site.
10. **Concordo** com A1 (o argumento de sobrevivência da ADR 0005 está invertido), A3, A4, M1, M4 a M8 e com
    descartar Q8 e Q15. Uma ressalva menor: a checagem externa da Money Times (FIPE +23,9% em 2021) deve citar que a
    definição da FIPE (variação do ano, outra ponderação) não é a do site. "Mesma ordem de grandeza" é o máximo que se
    pode dizer.
11. **Verificações dele com detalhe frágil:** p1.py e p6.py usam conjuntos de marcas premium com grafias diferentes
    ("Aston Martin" e "ASTON MARTIN", "McLaren" e "Mclaren"). O efeito é pequeno, mas o "27% premium" precisa de uma lista única
    versionada se for publicado. A coorte agregada da p2.py é a origem do problema do item 2.

## 6. Decisões que ficam com o autor (em ordem de impacto)

1. **Rever a ADR 0005:** coorte por ano de compra e perda por idade (pares do mesmo carro) como métodos principais; o
   corte no mesmo janeiro como secundário. Muda três páginas, `aggregate.py`, testes golden e a home.
2. **Publicar com dados até jan/2025 ou esperar jan/2026.** Hoje o dado mais novo tem 21 meses. A página 4 (pós-choque)
   é a mais sensível; minha sugestão é publicar dizendo "até jan/2025" e atualizar.
3. **Página do zero km:** separada e reformulada (minha recomendação) ou fundida na página 2. Em qualquer caso, a coorte
   de 1 ano como evidência e o teto de 97% declarado.
4. **Parser de família para a Q25** (primeira palavra do nome por marca, com teste em `tests/` e lista de revisão em
   `reference/`). Sem ele, a Q25 vai para a v2 e a página 5 roda só com faixa, marca e diesel.
5. **Métrica relativa (ano x faixa) para marca e combustível:** é mais correta e mais difícil de explicar ao leigo.
   Opções: mostrar a crua e a relativa lado a lado, ou só a relativa com uma frase de tradução ("comparado com carros
   do mesmo ano e da mesma faixa de preço").
6. **Catálogo contra frota:** declarar e mostrar uma sensibilidade (MVP), ou ponderar por vendas Fenabrave ou frota
   Senatran (v2).
7. **Troca diesel de 2011:** documentar como "origem desconhecida" ou recolher uma amostra de jan/2010 pela API (só
   com pedido explícito, por regra do projeto).
8. **Tom dos títulos:** tirar "mito" e "investimento" do título e deixar a pergunta do leitor como subtítulo.
9. **Explorar:** idade até 10, marcas de nicho fora e uma só definição de faixa (ou rótulo explícito).
10. **README** atualizado antes de publicar (B3): o recrutador lê o README antes do site.
11. **v2:** valores em R$ do catálogo (Q16, decisão sobre a ADR 0001) e mensal no pipeline (Q10, Q23).

## Anexo: verificações preliminares que pesaram na decisão

Todas em `.../scratchpad/agente2/`, com `uv run --no-sync python` dentro do repo, sobre os janeiros de 2004 a 2025.

| Checagem | Resultado | Script |
|---|---|---|
| Coorte agregada por idade (real, valor de face) | 1 ano: 83,5% e 88,0%; 5 anos: 53,9% e 71,4%; 10 anos: 31,6% e 55,7% | v1.py |
| Coorte aos 5 anos por ano de compra (real) | 2005-2012: 40% a 47%; 2013-2016: 52% a 60%; 2017-2020: 73% a 75% (valor de face 94% a 99,5%) | v1.py |
| Agregado aos 5 anos conforme a janela | 48% (compras até 2015), 54% (2004-2020), 52% (mediana das medianas anuais) | v1.py |
| Coorte de 1 ano por ano de compra | 2021: 100,7% real, 111% no valor de face; anos sem choque: 77% a 88% real | v1.py |
| Preço de face congelado de um ano para o outro | 0% em todas as idades: a FIPE atualiza todos os preços | v1.py |
| Perda real por idade, sem 2022 | -7,7% (1 ano), -10% a -11% (2 a 5), -8,1% (10), -6,7% (20), -5,6% (30); por período, cauda bem mais suave em 2023-25 | v1.py, v3.py |
| Razão carro do ano / zero km | máximo 0,97 em 22 janeiros; nenhum par a partir de 0,99 | v1.py |
| Japonesas contra demais, relativo ao ano de compra | faixa 1: 1,09 contra 1,12; faixas 2 a 4: +5% a +7%; relativo a ano x faixa: 1,03 contra 0,995 | v1.py, v2.py |
| Marcas relativo a ano x faixa (5 anos) | Porsche 1,17, Toyota 1,09, Honda 1,07, Mercedes 1,03; Volvo 0,85, Citroën 0,90, BMW 0,91, Peugeot 0,92, Audi 0,93; Spearman 0,78 com o corte transversal | v2.py |
| Diesel contra gasolina, relativo a ano x faixa | 1,13 contra 0,99 (n=1.403 diesel) | v2.py |
| Choque com sensibilidade | catálogo +9,0%; massa 1-15 anos +12,5%; massa 1-10 +12,7%; 2022 é a única alta real nas três | v2.py |
| Mesmo carro em janelas de 4 anos (real) | 2009-13 -44%; 2012-16 -40%; 2015-19 -31%; 2017-21 -24%; 2021-25 -7% (+19% no valor de face); jan/2022 a jan/2025 -15% contra -19% a -20% antes | v2.py |
| Zero km do mesmo código, comparação direta (real) | 2005→2015 -36% (n=41); 2015→2025 +27% (n=39); 2019→2025 +22% (n=126) | v2.py |
| Versão topo contra entrada na mesma família | 5 anos: -9% (81% de 1.441 grupos); 3 anos: -6% (75%); estável por período | v3.py |

## Fontes

- Relatório e fontes do agente 1 (lista completa em `mvp-agente1-perguntas.md`), em especial: texto da FIPE sobre o que a
  tabela expressa (https://veiculos.fipe.org.br/), Auto Avaliar sobre atacado contra FIPE em 2026
  (https://conexaoto.com.br/2026/09/08/guerra-de-precos-dos-carros-zero-km-derruba-seminovos-em-ate-21) e Anfavea
  sobre a produção perdida em 2021 (https://maisretorno.com/portal/anfavea-producao-deve-ser-ainda-menor-em-2021-por-falta-de-componentes).
- Como a FIPE calcula a tabela (coleta em 24 estados, transações, corte de pontos fora da curva; não trata do zero km
  nem do ano corrente): [Vrum, abr/2026](https://www.vrum.com.br/mercado/2026/04/7388484-como-a-tabela-fipe-e-calculada-entenda-o-que-define-o-preco.html)
  e [ValorFinal, metodologia](https://valorfinal.com.br/tabela-fipe/metodologia). Não achei documento da FIPE sobre a
  regra do ano-modelo corrente; o teto de 97% segue como hipótese.
