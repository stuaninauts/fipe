# Fipe: MVP atual x MVP sugerido

Síntese das duas revisões (agente 1: crítica e 25 perguntas; agente 2: julgamento por público). Nada foi alterado no
repo ou no site; tudo aqui depende da sua aprovação. Números marcados com (p) são **preliminares**: saíram de scripts
rápidos dos agentes e ainda não passaram por `fipe/aggregate.py` nem por teste.

## Em uma frase

A engenharia fica como está; o que muda é **o método das manchetes**. Hoje elas comparam o usado com um zero km de
hoje (mesmo janeiro). A proposta é seguir o **mesmo carro desde a compra** e mostrar quanto ele perde por idade, que
é a pergunta que o leitor de fato faz.

## Página a página

| Página hoje | O que acontece | Página sugerida | Por quê |
|---|---|---|---|
| **Home** (3 cards: +9,0%, 88–91%, 59%) | Muda | 6 cards, sem número que precise de ressalva | O "59%" e o "88–91%" respondem a outra pergunta; a abertura "431.303 preços de carros vendidos" lê como carros vendidos |
| **O mito do zero km** ("perto de 10%, não 20%") | Muda de enquadramento | **1. O primeiro ano**: "No primeiro ano, o carro perde cerca de 12% na tabela FIPE" | A FIPE mede revenda dos dois lados; o "carro do ano" nunca passou de 97% do zero km em 22 janeiros (parece regra da tabela). A evidência passa a ser o mesmo carro, comprado em janeiro e reavaliado no seguinte: 88% do preço pago, 84% real (p) |
| **Depreciação** ("59% aos 5 anos") | Vira duas páginas | **2. Em que idade o carro perde mais**: "Do 2º ao 5º ano, cerca de 10% ao ano; depois, menos" | Perda real mediana de 10–11% ao ano entre 2 e 5 anos, ~8% aos 10, ~7% aos 20 (p). O corte no mesmo janeiro fica como secundário ("comparado com um zero km de hoje") |
| (idem) | Entra | **3. Depende de quando você comprou**: "Cinco anos depois, o que sobra depende do ano da compra" | Real, 5 anos depois da compra: 40–46% (compras de 2005–2012), 52–60% (2013–2016), 73–75% (2017–2020); no valor de face o último grupo tinha 94–99,5% do que pagou (p). Melhor exemplo de nominal x real do site. Um número único "aos 5 anos" varia de 48% a 54% só mudando a janela, por isso não vira manchete |
| **O choque de 2022** ("carro usado virou investimento") | Fica, com título novo e uma seção a mais | **4. "Em 2022, o usado ficou mais caro mesmo envelhecendo um ano"** + "O que sobrou do choque" | Dados e gráfico ficam. Ganha sensibilidade: +9,0% no catálogo, +12,5% nas marcas de massa com 1–15 anos (p). Nova seção: de jan/2021 a jan/2025 o mesmo carro perdeu só 7% real, contra 24–44% em janelas de 4 anos antes do choque (p). Sai a seção "Dois tombos" (2010 e 2013), que parecia inacabada e vai para a v2 |
| (não existe) | Entra | **5. O que segura valor**: versão de entrada, carro mais barato, algumas marcas e diesel | Sempre comparando carros do mesmo ano de compra e da mesma faixa de preço (p): versão topo retém ~9% menos que a de entrada do mesmo modelo (81% de 1.441 grupos); diesel ~13% a mais que gasolina; Toyota e Honda 7–9% acima do esperado; Citroën, Peugeot, BMW, Audi e Volvo 7–15% abaixo; Mercedes na média; Porsche 17% acima |
| **Método** + **Dados** | Fundem e mudam de foco | **6. O que a tabela FIPE mede, e o que ela não mede** | Citação literal da FIPE ("revenda, à vista"); mediana do catálogo e não da frota (27% dos preços são premium, ~2% das vendas); modelos saem de linha como zero km (só 20% seguem à venda após 5 anos); as trocas de rótulo de 2011 (diesel) e 2024 (flex); o teto de 97%; o que não se sabe |
| **Explorar** | Fica, com correções | Explorar | Idade até 10 anos, marcas de nicho fora, uma só definição de faixa de preço. A curva da Fiat que sobe aos 11–12 anos é efeito de sobrevivência |

## O que fica igual

- Pipeline, limpeza, inflação, testes, CI, CSP, site bilíngue, visual.
- Os dados do choque de 2022 e a comparação por faixa de preço.
- A regra de só publicar agregados (ADR 0001) e a análise descritiva.

## O que muda por baixo

- **ADR 0005 revisada:** coorte por ano de compra e perda por idade viram os métodos principais; o corte no mesmo
  janeiro fica como secundário.
- **`fipe/aggregate.py` ganha:** coorte por ano de compra e idade; perda por idade (a partir dos pares do mesmo carro);
  retenção relativa a ano de compra x faixa, por grupo; sensibilidade do choque (catálogo x massa). Cada uma com teste
  golden.
- **Página 5, parte de versões:** precisa de um parser de família do modelo (primeira palavra do nome, por marca), com
  teste e lista de revisão. Sem ele, essa parte vai para a v2.

## Correções pequenas, independentes do resto

- Título "virou investimento" e a palavra "mito" saem dos títulos; a pergunta do leitor vira subtítulo.
- Sinal duplo no texto ("caiu -13%").
- Rótulos sobrepostos no fim do gráfico de depreciação.
- "Conferidos entre si" exagera: só 1.175 preços se sobrepõem entre coleta nova e arquivos antigos.
- O Método chama o preço FIPE de "preço pedido"; a FIPE diz "preços médios praticados na revenda".
- README ainda diz que o pipeline e o site "are not here yet".

## Achado de dados novo

Até jan/2010, cerca de 930 carros a diesel aparecem como "Gasolina" e viram "Diesel" em 2011: quebra 6,7% dos pares
2010→2011. Não dá para saber se é da FIPE ou do scraper antigo sem recoletar uma amostra de jan/2010.

## Decisões que ficam com você (em ordem de impacto)

| # | Decisão | Recomendação dos agentes |
|---|---|---|
| 1 | Rever a ADR 0005 (coorte e perda por idade como métodos principais) | Sim. É a mudança grande: muda 3 páginas, tabelas, testes e home |
| 2 | Publicar com dados até jan/2025 ou esperar jan/2026 | Publicar dizendo "até jan/2025" e atualizar quando a coleta terminar |
| 3 | Zero km: página separada ou fundida na de idade | Separada, reformulada como "o primeiro ano" |
| 4 | Parser de família de modelo (versões, página 5) | Fazer, com teste e lista de revisão; sem ele, versões vão para a v2 |
| 5 | Marca e combustível: métrica relativa (ano x faixa) ou também a crua | Relativa, com uma frase de tradução para o leigo |
| 6 | Catálogo x frota | Declarar e mostrar a sensibilidade no MVP; ponderar por vendas fica para a v2 |
| 7 | Diesel de 2011 | Documentar como origem desconhecida, ou você autoriza uma recoleta pequena de jan/2010 |
| 8 | Correções pequenas e do Explorar | Fazer; não dependem do resto |

## Para depois (v2)

Sazonalidade mensal (precisa de out–dez/2025 e jan/2026 no pipeline), elétricos e chineses (amostra pequena), câmbio,
SUV e cilindrada tirados do nome do modelo, os dois tombos de 2010 e 2013, ponderação por vendas, valores em R$.

## Relatórios completos

- Agente 1, crítica e 25 perguntas: `agente1-critica-e-perguntas.md`
- Agente 2, notas por público e MVP de 6 perguntas: `agente2-julgamento.md`
