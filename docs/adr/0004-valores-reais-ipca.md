# Valores reais pelo IPCA, em reais do último mês da série

Data: 2026-10-20.

Os preços da FIPE são nominais. Comparar um carro de 2004 com um de 2025 sem descontar a inflação mistura
desvalorização com perda do poder de compra da moeda.

Decidimos:

- **Índice:** IPCA número-índice mensal do IBGE (SIDRA 1737, variável 2266). Usar o número-índice, e não as
  variações mensais, evita erro de arredondamento ao acumular.
- **Série versionada** em `reference/ipca.csv`, atualizada por comando (`fipe.inflation --update`). O pipeline e
  os testes não dependem de rede.
- **Mês do índice = mês de referência da FIPE.** A tabela de janeiro usa o IPCA de janeiro.
- **Base:** o último mês publicado da série. `price_real_brl` diz "em reais de AAAA-MM", e a base acompanha o
  export (vai no metadado de cada tabela publicada).
- **Nominal e real lado a lado.** `price_brl` continua nominal; nenhuma coluna mistura os dois.
- Mês de referência sem IPCA é erro de execução, nunca um valor vazio silencioso.

## Considered Options

- **IGP-M ou INPC:** o IPCA é o índice oficial de inflação e o mais conhecido do público. Rejeitados.
- **Base fixa (por exemplo, janeiro de 2026):** números estáveis entre atualizações, mas envelhecem. Pode virar
  opção se a página precisar de comparação entre versões.

## Consequences

- Cada atualização do IPCA muda todos os valores reais publicados; os testes golden das análises fixam a base que
  usam.
