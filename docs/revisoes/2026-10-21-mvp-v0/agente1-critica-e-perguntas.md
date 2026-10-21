# MVP do fipe: revisão e perguntas candidatas (agente 1)

Data: 2026-10-20. Base: branch `feat/site` (working tree), preview em http://127.0.0.1:4360, `data/processed/prices.parquet`
e os brutos de `~/Desktop/ment/fipe-dados-brutos/mensal-2025/` (só leitura). Todos os números marcados como
"preliminar" saíram de scripts rápidos em
`/tmp/claude-1000/-home-stuani-Desktop-ment/d41a15ec-334f-460b-a4fb-43da1b54c63e/scratchpad/agente1/` (p1.py a p11.py)
e não passaram por `fipe/aggregate.py` nem por teste. Nenhum preço por modelo aparece aqui.

## 1. Resumo

1. A engenharia do MVP é forte e é o que mais vai impressionar um recrutador: um só lugar define número, sempre com n,
   mediana com quartis, testes golden sem dado bruto no CI, ADRs, CSP estrita, bilíngue, cuidado jurídico com a FIPE.
2. As três perguntas são boas como gancho, mas duas das manchetes respondem a uma pergunta diferente da que o leitor
   vai entender: "59% aos 5 anos" compara com o zero km de hoje, não com o que o dono pagou (na versão "do que você
   pagou", descontada a inflação, dá 54%, e varia de 40% a 75% conforme o ano da compra). "Perto de 10%, não 20%"
   compara preço de revenda com preço de revenda; o mito fala do que o dono recebe.
3. Nenhuma página diz que a mediana é do catálogo, não da frota: 27% dos preços são de marcas premium (perto de 2% das
   vendas) e 31% dos pares de 2022 têm 21 anos ou mais. O choque de 2022 resiste, mas fica maior no carro comum
   (+12,5% real em marcas de massa com 1 a 15 anos, contra +9,0% na manchete).
4. Achado de qualidade não documentado: até jan/2010 cerca de 930 carros a diesel aparecem como "Gasolina"; em 2011
   viram "Diesel". Isso quebra os pares 2010-2011 e distorce o grupo diesel antes de 2011.
5. Proponho um MVP de 7 perguntas ancorado em "quanto você perde" (coorte em valor real), "depende de quando comprou",
   o choque de 2022, o zero km reformulado, "quem segura valor" (marca, luxo, picape diesel), nominal vs real e
   "o que a FIPE mede". Sazonalidade mensal e elétricos ficam para a v2.

## 2. Opinião sobre o MVP atual

### Pontos fortes (o que um recrutador técnico vai notar de bom)

- **Disciplina de definição:** `fipe/aggregate.py` como única fonte de número, `web/src/lib/data.ts` só seleciona e
  formata, linha inexistente quebra o build. Isso é raro em portfólio e se explica em uma frase.
- **Transparência estatística:** mediana com p25/p75 e n em todo gráfico e tabela; tabela "Ver os números" em toda
  página; `/data/manifest.json` público.
- **Identidade de carro bem resolvida:** a chave `CAR` e o tratamento da troca de rótulo de 2024 (0 colisões) mostram
  cuidado com o dado de verdade. A página Dados expõe isso.
- **Inflação feita direito:** IPCA número-índice versionado, nominal e real lado a lado, e a observação de que no
  mesmo janeiro a inflação se cancela.
- **Postura descritiva e limitações explícitas** (página Método), e a regra de não publicar preço de um carro.
- **Consistência externa (preliminar):** a Money Times citou a própria FIPE em jan/2022 com alta de 23,9% nos usados e
  24,6% nos zero km em 2021; o site tem +20,4% e +21,4% (janeiro a janeiro). Mesma ordem de grandeza e mesma relação
  (zero km um pouco acima). Vale citar isso no Método como checagem.
- **Visual limpo**, sem erros de console no preview, cards com número grande que funcionam como gancho.

### Problemas por gravidade

#### Alta

**A1. "59% aos 5 anos" responde a outra pergunta e tem viés de sobrevivência forte** (página `/depreciacao/`, título
"Aos 5 anos, um carro vale 59% do novo"; card da home "Do preço de novo é o que um carro mantém aos 5 anos").
- O cálculo divide o usado pelo zero km do mesmo código *no mesmo janeiro*. O leitor vai entender "59% do que eu
  paguei". Preliminar, versão coorte (comprado zero km em jan/Y, valor real em jan/Y+5 sobre o preço real pago):
  **54% aos 5 anos** (n=12.165) e 32% aos 10. A diferença vem de dois efeitos: o zero km do mesmo código fica mais
  barato em termos reais com o tempo (índice encadeado do zero km de mesmo código caiu para 0,55 entre 2004 e 2025,
  perto de -3% real ao ano), e só os modelos de vida longa entram.
- Sobrevivência (preliminar): dos códigos com preço de zero km num janeiro, 78% ainda têm zero km 1 ano depois, 40%
  após 3, **20% após 5 e 4% após 10**. O "36% aos 10" e a cauda até 15 anos se apoiam nesses 4%. O mesmo código FIPE
  também pode atravessar trocas de geração, então "o mesmo carro zero km" aos 10 anos pode ser outro produto.
- Na coorte, o resultado depende muito do ano da compra: retenção aos 5 anos de 40% a 47% para quem comprou entre
  2005 e 2012, contra 73% a 75% para quem comprou entre 2017 e 2020 (que chegou aos 5 anos já com o choque).
- A ADR 0005 rejeitou a coorte dizendo que ela "mistura inflação, choques de mercado e sobrevivência". A inflação sai
  com o IPCA; o choque é justamente o que o dono vive; e a sobrevivência na coorte é baixa, porque a FIPE praticamente
  nunca tira um usado da tabela (ver M3/A4). Sugestão: coorte como manchete (ou ao lado), corte transversal como
  "comparado com um zero km de hoje", e idades acima de 10 só na tabela.

**A2. "O mito do zero km" mede revenda contra revenda** (página `/zero-km/`, título
'"Zero km perde 20% ao sair da loja": nos dados, perto de 10%'; card "A perda ao sair da loja ficou perto de 10%, não
20%").
- A própria FIPE diz que a tabela "expressa preços médios para pagamento à vista, praticados na revenda de veículos" a
  consumidores particulares. O "usado do ano" é o preço que uma loja cobra por um seminovo, não o que o dono recebe ao
  vender ou dar na troca. O mito é sobre o que o dono perde; a perda dele é os ~10% mais a margem de quem compra.
- Preliminar: a razão usado do ano / zero km é muito concentrada (99,6% dos pares entre 80% e 98%) e **nunca chega a
  100%, nem em 2022**, quando a imprensa relatou usados mais caros que zero km similares (AutoPapo). Isso pode ser
  convenção do método da FIPE para o ano corrente, e não mercado. Não achei documento da FIPE que confirme ou negue.
- No mensal de 2025 (preliminar), o usado ano-modelo 2025 vai de 91% do zero km em janeiro para 88% em setembro, e o
  ano-modelo 2026 aparece em março (19 preços) já a ~92%: o "gap de 10%" aparece também para carros de semanas.
- Na coorte, um carro comprado zero km vale ~83,5% (real) um ano depois: mais perto dos 20% do mito do que dos 10%.
- O texto já diz "O que isso não mede", mas o título é categórico. Sugestão: "Na tabela FIPE, o carro do ano usado vale
  ~90% do zero km", com o primeiro ano em coorte ao lado e uma frase sobre troca na concessionária. Ou segurar a página
  até checar o método da FIPE para o ano-modelo corrente.

**A3. Mediana do catálogo apresentada como se fosse do mercado** (home: "431.303 preços de janeiro de carros vendidos no
Brasil"; Método: "A mediana não se deixa levar por carros raros e caros"; todas as análises).
- Cada versão x ano-modelo conta uma vez. Preliminar: marcas premium são 22% (2004) a **27% (2025)** dos preços de
  janeiro; no mercado de novos, o segmento de luxo teve ~51 mil unidades em 2024 (K.Lume), algo perto de 2% das vendas.
  31% dos pares de 2022 têm 21 anos ou mais.
- Efeito no choque (preliminar): marcas de massa +10,3% real, premium +4,8%; carros de 3 a 15 anos +11% a +12%, de 21
  anos ou mais +3% a +5%. Faixa fixa de 1 a 15 anos: +11,2%; massa de 1 a 15 anos: +12,5%. "A única alta real" vale
  em todas as variantes; a magnitude não.
- A frase do Método é verdadeira para outlier e enganosa para composição. Um recrutador de dados vai procurar
  "ponderação" e não vai achar. Sugestão: dizer "mediana do catálogo da FIPE, não da frota", mostrar uma sensibilidade
  (massa, 1 a 15 anos) e trocar "carros vendidos" por "preços de versões e anos-modelo".

**A4. Troca de rótulo diesel em 2011 sem tratamento nem registro** (página `/qualidade/` só cita 2024; Explorar por
combustível).
- Preliminar: 930 pares (código, ano-modelo) de usados mudam de "Gasolina" (até 2010) para "Diesel" (2011). Diesel era
  9,3% dos preços em 2010 e 16,4% em 2011; zero km a diesel eram 13 em 2009 e 2010 e 164 em 2011.
- Consequências: 6,7% dos usados de 2010 não acham par em 2011 (nos outros anos, ~0,03%), o n de 2010-2011 fica
  achatado (13.146 contra 13.137 no ano anterior, com a tabela crescendo) e o grupo "Diesel" do Explorar (escopo
  "todos") antes de 2011 é outro conjunto. Não dá para saber, sem recoletar, se o erro é da FIPE ou do scraper v1.
- Para portfólio isso é oportunidade: documentado na página Dados, mostra auditoria séria; descoberto por terceiros,
  pesa contra.

#### Média

**M1. Título "Em 2022, carro usado virou investimento"** (`/choque-2021-2022/`). Um ano de +9% real na mediana não faz
de nada um investimento: quem comprou em jan/2022 perdeu 3% real em 2023 e 9% em 2024, sem contar IPVA e seguro. Soa
como conselho financeiro e conflita com a postura descritiva. Sugestão: "Em 2022, o usado ficou mais caro mesmo
envelhecendo um ano".

**M2. "Dois tombos que ainda pedem explicação"** (mesma página). Deixar pergunta aberta numa página publicada parece
inacabado, e o entusiasta vai pensar em IPI na hora. O contexto é verificável e datado: corte de IPI de dez/2008 até
mar/2010 (com prorrogações) e de mai/2012 (Decreto 7.725) até 2013-2014. O tombo de 2013 (jan/12 a jan/13: zero km
-4,7%, usado -12,5% nominal) coincide bem com o corte de 2012. O de 2010 coincide pior: o corte já valia em jan/2009,
e a barra de 2009 mostra zero km -0,9%. Sugestão: dar as datas com fonte, dizer "coincide com", ou tirar a seção.

**M3. Composição muda ao longo da série.** A FIPE mantém todos os anos-modelo desde 1985 em todos os janeiros
(preliminar), então a idade mediana dos pares sobe de 7 anos (2005) para 15 (2025). Carro velho perde menos em valor
real (~-6% ao ano aos 25-30 anos contra ~-10% aos 3-5), o que empurra a série para cima com o tempo. Ver números em A3.
O texto "É o esperado: ele fica um ano mais velho" também esconde que boa parte da perda real é inflação com preço
nominal quase parado (ver Q18).

**M4. Lede da home.** "431.303 preços de janeiro de carros vendidos no Brasil" lê como 431 mil carros vendidos.
"Três perguntas, respondidas com o mesmo carro comparado com ele mesmo" só vale para o choque; zero km e idade comparam
usado com o zero km do mesmo código.

**M5. Método descreve a FIPE com palavras que não são da FIPE.** "A FIPE publica preço médio pedido no mercado, não o
preço fechado em cada venda" (`/metodo/`). A FIPE diz "preços médios para pagamento à vista, praticados na revenda".
Melhor citar a fonte literalmente e dizer o que não se sabe (amostra, ponderação, regra do ano corrente).

**M6. "Faixa de preço" com duas definições no mesmo controle do Explorar.** Em "valor mantido por idade" é o quintil do
zero km; em "variação ano a ano" é o quintil do usado no primeiro janeiro. No segundo caso "Mais baratos" são, na
maioria, os carros mais velhos. Exemplo: em 2022 o q1 subiu +4,0% e o q4 +12,0%; o leitor vai concluir "carro popular
subiu menos", o que o dado não diz. Sugestão: usar faixas de idade na variação anual, ou rotular "usados mais baratos
(em geral, os mais velhos)".

**M7. Explorar mostra artefato de sobrevivência como achado.** No escopo "todos", por marca, a curva da Fiat volta a
subir aos 11-12 anos (preview com Volkswagen, Fiat, Toyota, BMW). Isso é o grupo pequeno de códigos que seguem à venda
como zero km, não carro valorizando. Sugestão: cortar a idade em 10 no Explorar ou marcar a cauda. A lista de marcas
também traz Fibravan, BRM, EFFA, Agrale e IVECO, estranhas para o público geral.

**M8. "Conferidos entre si" exagera a validação** (`/qualidade/`: "430.128 dos arquivos coletados em 2023-2025 e 1.175
da coleta atual, conferidos entre si"). Só 1.175 preços de jan/2024 se sobrepõem (1.185 duplicatas, 0 conflitos). Dito
com precisão é um ponto forte: "1.175 preços recoletados pela API batem 100% com os arquivos antigos".

#### Baixa

- **B1.** Sinal duplo: "o usado caiu -13% e -12%", "o zero km caiu -5,9%", "ficou +20,4% mais caro" (`/choque-2021-2022/`).
- **B2.** No gráfico de `/depreciacao/` os rótulos "2004-2025" e "2021-2025" se sobrepõem no fim das linhas (idade 15).
- **B3.** README ainda diz "Being rebuilt. The pipeline and the site are not here yet" (com emoji). O recrutador lê o
  README antes do site.
- **B4.** "Desde 2022 a diferença ficou menor" (`/zero-km/`): em 2025 voltou a 91%, quase no patamar antigo.
- **B5.** "Gasolina e flex" no Explorar inclui também híbrido, elétrico e GNV.
- **B6.** Título do site "Quanto um carro perde de valor no Brasil" com um card sobre ganho; tudo bem, mas "Quanto vale
  um carro no Brasil, 2004-2025" cobre as três.

### O que um leigo não vai entender

"Ano-modelo", "código FIPE", "mediana", "real vs nominal", "quintil/quinto", "par", "ano de chegada no eixo", "usado do
ano", "a inflação se cancela no mesmo janeiro", "grupo de combustível". Um glossário curto no Método e uma frase de
tradução em cada página resolvem ("real = descontada a inflação, em reais de set/2026").

## 3. Perguntas candidatas

Legenda de dados: **sim** = dá com o parquet atual; **precisa de X** = depende de algo novo. "Coorte" = comprado zero km
em jan/Y, valor real em jan/Y+a sobre o preço real pago (mesmo código e grupo de combustível). "Transversal" = método
atual de `retention_by_age`. Todas as verificações são **preliminares**.

| id | Pergunta (como o leitor faria) | Dados | Como responder | Verificação preliminar | Risco |
|---|---|---|---|---|---|
| Q1 | "Zero km perde 20% quando sai da loja?" | sim (já existe `new_vs_used`); coorte do 1º ano é nova | Razão usado do ano / zero km no mesmo janeiro, mais coorte de 1 ano | 88-91% até 2021 (revenda contra revenda); coorte: ~83,5% real após 1 ano; razão nunca >= 100%, nem em 2022 | Alto: FIPE é preço de revenda, não de troca; possível convenção da FIPE no ano corrente; título categórico |
| Q2 | "Carro japonês não desvaloriza?" | sim (marca); controle por faixa | Retenção aos 3 e 5 anos por marca, coorte e transversal, dentro da faixa de preço | Coorte 5 anos: Toyota 65%, Hyundai 64%, Fiat 56%, Honda 56%, VW 55%, GM 55%; comprados 2015+: Honda 78%, Toyota 77%. Japoneses vs demais: 74% vs 59% (q1), 66% vs 54% (q2), sem vantagem em q3-q5. Transversal: diferenças de só 3-5 p.p. | Médio: mistura de modelos por marca, n pequeno em algumas, marca não é país de fabricação; resposta muda com o método (expor os dois) |
| Q3 | "Carro automático vale mais / desvaloriza menos?" | precisa de câmbio tirado do nome | Regex no nome (Aut., CVT, Tiptronic, DSG, Mec.); comparar % retido dentro da faixa | ~60% dos nomes sem rótulo de câmbio (manual costuma ficar implícito). Transversal 5 anos: q2 61% (aut.) vs 58% (mec.), q3 56% vs 57%, q4 54% vs 55%: sem vantagem clara | Médio: erro de classificação; "vale mais" em R$ é trivial (é mais caro novo), a pergunta certa é o % retido |
| Q4 | "SUV segura mais valor?" | precisa de categoria (lista de famílias por nome) | Lista curada de famílias (Compass, HR-V, Creta, T-Cross...) versionada em `reference/` | Coorte 5 anos: SUV 57%, demais 53%; q3: 58% vs 49%; q4: 48,5% vs 49,5% | Médio: curadoria e manutenção; SUVs concentrados nos anos recentes (período confunde) |
| Q5 | "Picape diesel não perde valor?" | sim (diesel como proxy) + lista de picapes | Diesel no Brasil é restrito a picape, SUV 4x4 e van: `fuel_group` serve de proxy; picapes por nome | Coorte 5 anos: diesel 67% vs gasolina 49% (q3), 60% vs 47% (q4); picapes por nome 60% vs 53%. Transversal 8 anos: 49% vs 42% | Médio: quebra de rótulo de 2011 (A4); diesel inclui SUV de luxo e vans |
| Q6 | "Carro de luxo desvaloriza mais?" | sim (faixa de preço e marca) | Quintil do zero km e marcas premium, coorte e transversal | Transversal 5 anos: q1 64% vs q5 56% (já no site). Coorte: alemãs premium 42-47% vs massa ~55%; Porsche é exceção (58%; 77% nos comprados 2015+) | Baixo: bem sustentado; cuidado com a faixa definida dentro de cada janeiro |
| Q7 | "Elétrico desvaloriza rápido?" | parcial: rótulo "Elétrico" só desde 2024; códigos antigos achados pelo código | Marcar o código como elétrico a partir do rótulo de 2024-25 e fazer coorte | 150 códigos, maioria BMW, Porsche, Audi, Mercedes, mais JAC e BYD. Coorte (comprados 2021+): 3 anos EV 65,5% (n=53), híbrido 70%, flex 77%; 4 anos EV 57,5% (n=19) | Alto: n pequeno, mistura premium, cortes de preço de fábrica (BYD) e fontes externas divergentes (Bright: EV de entrada perdeu menos). Melhor para v2 |
| Q8 | "Flex vale mais que só gasolina?" | não de forma justa | Rótulo "Flex" só desde 2024; "Flex" no nome em 28% das linhas em 2025 | Só-gasolina hoje é carro velho, importado ou premium: compara épocas, não combustível | Alto: confusão por idade e origem. Sugiro descartar |
| Q9 | "Carro chinês desvaloriza muito?" | n insuficiente hoje | Marca (BYD, GWM, Caoa Chery, JAC) | JAC 19 pares aos 5 anos; BYD só desde 2023 (2 pares aos 3 anos). Marca muda de rótulo (Caoa Chery para "Caoa Chery/Chery" em 2024; GREAT WALL e GWM) | Alto: amostra; esperar 2026+ |
| Q10 | "Comprar no fim do ano é melhor? O carro perde valor quando vira o ano?" | precisa do mensal (jan-set/2025 bruto; faltam out-dez/2025 e jan/2026) | Mesmo carro mês a mês; salto set/dez para jan | 2025: usado -0,1% a -0,2% nominal por mês; jan-set -0,6% nominal com IPCA +3,5% (~-4% real); 1-3 anos -3,3% nominal, 10-20 anos +1%. Zero km quase parado mês a mês | Alto: um ano só não mostra sazonalidade; FIPE suaviza |
| Q11 | "Carro antigo valoriza? Existe idade em que para de desvalorizar?" | sim | Variação real anual por idade, sem 2022 | Perda real ~10%/ano aos 3-5 anos, 6,7% aos 20, 5,6% aos 30, 2-3,5% aos 35-38 (n pequeno). 23% dos carros com 26+ anos ganharam valor real num ano típico. Carros 30+ ganharam em 2022 (+3,6%) e 2023 (+4,1%) | Médio: FIPE é estado médio, não cobre coleção; n cai muito depois de 35 anos |
| Q12 | "Por que o usado disparou em 2021-22?" | sim (já existe) + contexto externo | Choque com sensibilidade (massa, 1-15 anos) e contexto datado (chips) | +9,0% catálogo; +12,5% massa 1-15 anos; diesel +11%. Anfavea estimou ~300 mil veículos não produzidos em 2021 | Alto se causal; ok como "coincide com" |
| Q13 | "Quando o governo cortou o IPI, o usado caiu junto?" | sim + datas externas; cilindrada do nome para dose-resposta | Variação anual do zero km e do usado em torno dos cortes; comparar 1.0 (IPI zerado) com acima de 2.0 | 2013: zero km -4,7%, usado -12,5% (corte de mai/2012). 2010: -5,9% e -13%, mas o corte já valia em jan/2009 e a barra de 2009 é fraca | Alto: causalidade; janeiro só dá 1 ponto por ano |
| Q14 | "A Ford saiu do Brasil: o Ford usado despencou?" | sim (marca) | Variação anual Ford vs outras marcas de massa, até 10 anos | 2022: Ford +9,8% vs +13,7%; 2021: -5,2% vs -4,5%; 2023: -5,4% vs -5,0%. Diferença de ~4 p.p. só em 2022 | Médio: causal; mistura de modelos (Ka e EcoSport saíram, Ranger ficou) |
| Q15 | "Juros altos derrubam o preço do usado?" | precisa da Selic (BCB) | Série anual ao lado da variação real | Não verificado: são 21 pontos anuais, correlação seria frágil | Alto: correlação espúria e causal. Sugiro descartar ou só contexto |
| Q16 | "O zero km ficou mais caro que a inflação? O carro popular sumiu?" | sim (export precisa de nova tabela) | Índice do zero km de mesmo código vs distribuição do catálogo de zero km | Mesmo código: -45% real em 2004-2025 (~-3%/ano; só 2021-23 subiu). Catálogo: mediana real do zero km foi de ~R$ 134 mil (2015) para ~R$ 303-319 mil (2023-25); p10 de ~R$ 68 mil (2013-14) para ~R$ 118-121 mil | Médio: catálogo não é venda; airbag e ABS obrigatórios desde 2014; publicar R$ exige decisão sobre ADR 0001 |
| Q17 | "Quanto meu carro perdeu depende de quando comprei?" | sim (coorte nova) | Retenção real aos 3 e 5 anos por ano de compra | Aos 5 anos: 40-47% (comprados 2005-2012), 52-60% (2013-2016), 73-75% (2017-2020) | Médio: contraria a escolha da ADR 0005; precisa explicar o choque; ótima narrativa |
| Q18 | "No papel meu carro vale o que paguei: ele não desvalorizou?" | sim (já no export) | Nominal vs IPCA vs real por ano | Variação nominal mediana fica entre -5% e +3% na maioria dos anos (exceções 2010, 2013, 2022); em 2016: nominal -3,6%, IPCA +10,7%, real -13% | Baixo: didático, ótimo para leigo |
| Q19 | "O que a FIPE mede? Ela acompanha o mercado ou atrasa?" | fonte externa + mensal | Texto da FIPE; comparação com atacado; suavidade mês a mês | FIPE: "preços médios para pagamento à vista, praticados na revenda". Auto Avaliar: jan-jun/2026 atacado de carros até 3 anos -9,3%, FIPE -2,4%. Mensal 2025: variações de 0,1-0,2% ao mês | Médio: metodologia da FIPE não é pública em detalhe |
| Q20 | "A FIPE tira carro velho da tabela? (sobrevivência)" | sim | Taxa de saída de usados e de zero km por ano | Usados quase nunca saem (~0,03% ao ano, exceto 2011 pelo rótulo); anos-modelo desde 1985 sempre presentes. Zero km: 78%/40%/20%/4% seguem após 1/3/5/10 anos | Baixo: forte para recrutador, explica por que a variação anual quase não tem viés e a curva por idade tem |
| Q21 | "A mediana da FIPE representa o carro da rua?" | precisa de pesos (Fenabrave, frota Senatran) para versão ponderada | Composição do catálogo vs vendas; sensibilidade por marca e idade | 27% premium no catálogo vs ~2% das vendas; 31% dos pares de 2022 com 21+ anos; manchete muda de 9,0% para 12,5% | Médio: dado de frota por modelo pode não casar com código FIPE |
| Q22 | "O que a FIPE mudou nos rótulos e como isso afeta?" | sim | Página Dados: 2011 (diesel) e 2024 (flex etc.) | 930 trocas em 2011, 31 em 2024 (por grupo); zero km diesel 13 para 164 | Baixo: transparência; precisa decidir se é FIPE ou scraper |
| Q23 | "Quando chega o ano-modelo novo, quanto o do ano anterior perde?" | precisa do mensal completo | Razão usado do ano / zero km mês a mês e entrada do ano-modelo seguinte | Ano-modelo 2026 aparece em mar/2025 (19 preços) e chega a 407 em set; ano-modelo 2025 vai de 91% para 88% do zero km | Médio: um ciclo só |
| Q24 | "Motor 1.0 segura mais valor que 2.0?" | precisa de cilindrada do nome (parseia em 87%) | Retenção por cilindrada dentro da faixa | Transversal 5 anos, q1: 1.0 66%, 1.5-1.6 62%, 1.7-2.0 59% | Médio: cilindrada confunde com modelo e faixa |
| Q25 | "Versão topo de linha perde mais que a de entrada (mesmo modelo)?" | precisa de família do modelo tirada do nome | Dentro da família e do ano-modelo, comparar a versão mais barata e a mais cara | Não verificado | Médio: extração da família; controla modelo, bom para recrutador |

## 4. Proposta de MVP de perguntas

### Critérios (explícitos, em ordem de peso)

1. **Robustez com os dados que já existem:** n alto, sem depender de rótulo novo frágil (câmbio, categoria) nem de
   dado que ainda não está no pipeline.
2. **Pergunta que o leitor já faz:** público geral e entusiasta reconhecem a pergunta sem explicação.
3. **Valor de portfólio:** cada página mostra uma decisão de método (identidade do carro, inflação, coorte vs mesmo
   janeiro, sobrevivência, composição).
4. **Risco baixo:** sem afirmação causal, sem preço de um carro (ADR 0001), sem título que o dado não sustenta.
5. **Narrativa encadeada:** cada página leva à próxima.
6. **Custo:** reaproveita `aggregate.py` (pares por `CAR`, pares de retenção).

### MVP sugerido (7 perguntas, nesta ordem)

1. **"Quanto um carro perde de valor por ano?"** Coorte em valor real como manchete: ~83,5% após 1 ano, ~54% aos 5,
   ~32% aos 10 (preliminar); o corte no mesmo janeiro fica como "comparado com um zero km de hoje". Por quê: é a
   pergunta do título do site, todo leitor tem um carro na cabeça, e a página mostra a escolha de método. Corrige A1.
2. **"Depende de quando você comprou."** Retenção aos 5 anos por ano de compra (40-47% vs 73-75%). Por quê: é o achado
   mais surpreendente e pessoal do conjunto, e faz a ponte para o choque.
3. **"2022: o usado ficou mais caro mesmo envelhecendo um ano."** O choque atual, com sensibilidade (massa, 1-15 anos),
   contexto de chips e IPI com fonte e "coincide com". Por quê: é o número mais forte e verificável do site; com a
   sensibilidade, vira prova de rigor. Corrige M1, M2 e A3.
4. **"O zero km perde 20% ao sair da loja?"** Reformulada: na FIPE o carro do ano vale ~90% do zero km (revenda);
   na coorte, ~83,5% após um ano; o que se recebe na troca é menos e a FIPE não mede. Por quê: o mito é o melhor gancho
   para o público geral; reformulado, deixa de ser frágil. Corrige A2. Se o método da FIPE para o ano corrente não for
   esclarecido, fundir com a pergunta 1.
5. **"Quem segura valor: marca, preço ou picape diesel?"** Três mitos numa página, com coorte e controle por faixa:
   japonês segura mais só nas faixas baratas; luxo perde mais (Porsche é exceção); diesel/picape segura mais nas faixas
   médias. Por quê: é o que o entusiasta procura e alimenta o Explorar. Usa só marca, faixa e `fuel_group`, que já
   existem. Exige tratar a quebra de 2011 (A4) ou limitar o diesel a 2011+.
6. **"No papel meu carro não perdeu nada: e daí?"** Nominal vs real: o preço de face cai 2-4% ao ano e o resto é
   inflação. Por quê: ensina "valor real" ao leigo com o próprio dado e justifica o IPCA em todas as páginas. Pode ser
   uma seção da pergunta 1 se o espaço apertar.
7. **"O que a FIPE mede, e o que este site não mede."** Método e qualidade num lugar: revenda à vista, catálogo vs
   frota, sobrevivência (usado nunca sai, zero km sai), rótulos de 2011 e 2024, FIPE vs atacado, checagem externa de
   2021. Por quê: é a página que o recrutador técnico vai abrir para julgar o resto.

Fica de fora do MVP (v2): sazonalidade e troca de ano-modelo (Q10, Q23) até ter out-dez/2025 e jan/2026 no pipeline;
elétricos e chineses (Q7, Q9) por n; câmbio, SUV e cilindrada (Q3, Q4, Q24) até a extração do nome ter teste;
juros (Q15) e flex (Q8), que eu descartaria. "Carro antigo para de desvalorizar?" (Q11) é a melhor candidata a oitava
pergunta para entusiastas, se couber.

## 5. Perguntas em aberto para o autor

1. Aceita rever a ADR 0005 para usar a coorte em valor real como manchete da depreciação (ou ao lado do corte no mesmo
   janeiro)? A justificativa da ADR sobre sobrevivência parece invertida diante dos dados (usado praticamente nunca
   sai da tabela).
2. A troca diesel de 2011 vem da FIPE ou do scraper v1? Checar exige recoletar uma amostra de janeiro/2010 pela API,
   o que só roda com pedido seu.
3. Tem algum documento da FIPE sobre o preço do ano-modelo corrente e do zero km? Sem isso, o "mito do zero km" pode
   estar medindo uma convenção da tabela.
4. Publicar valores em R$ (quantis de preço do zero km do catálogo, por exemplo) fere a ADR 0001? Hoje o site só
   publica razões e variações.
5. Quer uma versão ponderada (vendas Fenabrave ou frota Senatran), ou basta declarar "mediana do catálogo" com uma
   sensibilidade por marca e idade?
6. Topa manter uma lista curada de famílias (picape, SUV) e regras de câmbio e cilindrada em `reference/`, com teste?
7. O mensal de 2025 entra no pipeline já para o MVP, mudando a regra "só janeiros", ou fica para depois de jan/2026?
8. No Explorar: cortar idade em 10 anos e esconder marcas de nicho (Fibravan, BRM, EFFA, Agrale, IVECO)?
9. Tom dos títulos: até onde vale provocar ("mito", "investimento") numa peça de portfólio vista por recrutador?
10. O README em inglês desatualizado ("pipeline and site are not here yet") será atualizado antes da publicação?

## Fontes

- FIPE, página de consulta (texto sobre o que a tabela expressa): https://veiculos.fipe.org.br/
- IPI 2008-2010 (prorrogação de jun/2009): https://www.conjur.com.br/2009-jun-29/governo-prorroga-tres-isencao-ipi-carros//?print=1
- IPI 2012 (Decreto 7.725, de 21/05/2012): https://www.coad.com.br/home/noticias-detalhe/43257/governo-reduz-aliquota-do-ipi-sobre-automoveis-e-utilitarios
  e https://www2.camara.leg.br/legin/fed/decret/2012/decreto-7725-21-maio-2012-613024-anexo-pe.pdf
- Estudos sobre os cortes de IPI (datas de início e fim): https://repositorio.ipea.gov.br/server/api/core/bitstreams/84c9d6dc-5f62-4ee8-a5e1-d4c7a55c1bea/content
- Ford encerra produção no Brasil em 11/01/2021: https://www.poder360.com.br/economia/ford-anuncia-fim-de-producao-no-brasil-depois-de-perdas-significativas/
- Chips e produção perdida em 2021 (Anfavea): https://maisretorno.com/portal/anfavea-producao-deve-ser-ainda-menor-em-2021-por-falta-de-componentes
- FIPE citada sobre 2021 (usados +23,9%, zero km +24,6%), Money Times, 24/01/2022: https://www.moneytimes.com.br/esta-na-hora-de-vender-o-meu-carro-seminovo-para-comprar-um-zero-quilometro/
- Usados mais caros que zero km similares (2021): https://autopapo.com.br/noticia/carros-usados-alta-precos/
- Mito dos 20% (Jato, Bright: 10-15% no primeiro ano): https://www.motoragora.com.br/carro-zero-desvaloriza-muito-ao-sair/
  e https://autopapo.com.br/blog-do-boris/desvalorizacao-automovel-20-por-cento/
- Atacado vs FIPE em 2026 (Auto Avaliar): https://conexaoto.com.br/2026/09/08/guerra-de-precos-dos-carros-zero-km-derruba-seminovos-em-ate-21
- Elétricos e desvalorização (Bright, Indicata): https://canalve.com.br/carro-eletrico-desvaloriza-entenda-diferencas-faixas/
  e https://www.vrum.com.br/mercado/2026/09/7501877-mercado-de-eletricos-usados-por-que-os-precos-cairam.html
- Segmento de luxo, ~51 mil unidades em 2024 (K.Lume): https://monitormercantil.com.br/mercado-de-carros-de-luxo-cresce-66-em-2025-mas-concentrado-em-poucos-vencedores/
  (o "perto de 2% das vendas" usa um total de mercado aproximado, a confirmar na Fenabrave)
