# Análises do MVP e export público

Data: 2026-10-20.

O site precisa de poucos números, bem definidos e verificáveis. Como no CopaData, um número publicado só pode ter
uma definição, e quem lê precisa ver em quantos preços ele se apoia. Diferente do CopaData, o CI não tem os dados
brutos ([ADR 0001](./0001-dados-brutos-locais.md)) e não consegue reconstruir o export.

Decidimos:

- **Um só lugar define achado:** `fipe/aggregate.py`. Toda tabela usa só as referências de janeiro, traz o `n` e
  usa mediana (com p25 e p75), não média: a distribuição de preços tem cauda longa.
- **As quatro tabelas do MVP:**
  - `yearly_change`: o mesmo carro usado (chave `CAR`, que atravessa a troca de rótulo de combustível de 2024) de
    um janeiro para o outro, nominal e real, ao lado do IPCA e da variação dos zero km. O carro envelhece um ano
    entre as duas referências, então a variação mistura idade e mercado; o texto do site diz isso.
  - `new_vs_used`: usado do ano-modelo corrente sobre o mesmo carro zero km, no mesmo janeiro.
  - `retention_by_age`: preço de cada ano-modelo usado sobre o zero km do mesmo código no mesmo janeiro (a
    inflação se cancela), por idade, em todos os anos e nos últimos cinco.
  - `coverage`: quantos preços, zero km, códigos e marcas cada referência tem.
- **Export em `web/public/data/`:** JSON e CSV por tabela e um `manifest.json` com colunas, linhas, a base dos
  valores reais e a atribuição. Gerado só por `fipe/export.py`, nunca editado à mão. Nenhuma coluna identifica um
  carro ou traz o preço dele (um teste garante).
- **Testes golden sobre o export versionado:** fixam os números publicados (por exemplo, +9,0% real em 2021-22).
  Regenerar o export com resultado diferente quebra o teste até ele ser atualizado de propósito, no mesmo PR.
  Com os dados locais presentes, `export --check` também roda dentro do pytest.

## Considered Options

- **Média em vez de mediana:** sensível a carros raros e caros. Rejeitada.
- **Índice encadeado de preços de usados:** depende de escolher um método de índice (Jevons, mediana encadeada)
  e de explicar o encadeamento. Fica para depois; a tabela ano a ano já responde a pergunta do MVP.
- **Curva de depreciação seguindo o mesmo carro ao longo dos anos (coorte):** mais fiel ao "meu carro", mas mistura
  inflação, choques de mercado e sobrevivência das séries. A versão no mesmo mês evita os dois primeiros.

## Consequences

- `retention_by_age` só vê modelos que ainda têm preço de zero km naquele janeiro. Nas idades altas, sobram os
  modelos de vida longa (sobrevivência); o `n` cai e a página mostra isso.
- Mudar uma definição em `aggregate.py` muda teste, export e texto do site no mesmo PR.
