# Seguir o mesmo carro: coorte e perda por idade como métodos principais

Data: 2026-10-21. Supera em parte a [ADR 0005](./0005-analises-e-export.md).

A revisão do MVP v0 (`docs/revisoes/2026-10-21-mvp-v0/`) mostrou que as manchetes respondiam a outra pergunta. O
"59% aos 5 anos" comparava o usado com o preço de um zero km de hoje (mesmo janeiro), mas o leitor entende "59% do
que eu paguei". O "perto de 10%, não 20%" comparava duas cotações de revenda da própria FIPE, e o carro do ano nunca
passou de 97% do zero km em 22 janeiros, nem em 2022: tem cara de regra da tabela, não de mercado.

Decidimos:

- **Métodos principais, seguindo o mesmo carro:**
  - **coorte** (`cohort`): carro comprado zero km em janeiro do ano Y, avaliado nos janeiros seguintes. A parcela do
    preço pago que sobra, real e nominal, por ano da compra e idade. Um número agregado de todos os anos não vira
    manchete: ele muda com a janela de anos (de 48% a 54% aos 5 anos);
  - **perda por idade** (`loss_by_age`): o mesmo carro usado de um janeiro para o outro, pela idade, sem o ano do
    choque (2022);
  - **janelas de quatro anos** (`four_year_change`): o que sobrou do choque de 2022.
- **O corte no mesmo janeiro fica como secundário** (`retention_by_age`, `new_vs_used`), sempre descrito como
  "comparado com um zero km de hoje".
- **Comparações de grupo são relativas ao ano da compra e à faixa de preço** (`holds_value`): só o ano da compra
  move a retenção de cerca de 40% para 75%, e comparar grupos sem esse controle inverte resultados.
- **Versões de um mesmo modelo** (`version_gap`): a família do modelo sai do nome (`fipe/family.py`, primeira
  palavra com exceções testadas). É heurística; os casos que precisam funcionar estão em `tests/test_family.py`.
- **Sensibilidade do catálogo:** a mediana é do catálogo da FIPE, não da frota (marcas premium são 27% dos preços).
  O choque de 2022 sai também sem as marcas premium e só com carros de 1 a 15 anos (`mass_*` em `yearly_change`).
- **Trocas de rótulo de combustível documentadas** (`fuel_relabels`): diesel rotulado como "Gasolina" até 2010
  (1.069 carros mudam em 2011, origem desconhecida: FIPE ou scraper v1) e a separação do flex em 2024. Comparações
  por combustível usam compras a partir de 2011.
- **Explorar:** idade até 10 anos e só marcas com pelo menos 1.000 comparações.
- **Publicar com dados até janeiro de 2025**, dizendo isso no site, e atualizar quando janeiro de 2026 entrar.

## Consequences

- O site passa a ter seis análises: o primeiro ano, a perda por idade, o ano da compra, o choque e o que sobrou
  dele, o que segura valor e o que a tabela FIPE mede.
- Novas tabelas no export, cada uma com teste golden em `tests/test_export.py`.
- Os números da revisão, que eram preliminares, agora saem do pipeline; onde mudaram, vale o do pipeline.
