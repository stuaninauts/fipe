# Dados de referência

Séries públicas pequenas, versionadas para o pipeline e os testes rodarem sem rede. Nada aqui vem da FIPE.

| Arquivo | Conteúdo | Fonte | Atualizar |
|---|---|---|---|
| `ipca.csv` | IPCA, número-índice mensal (base: dezembro de 1993 = 100), de 2000 em diante | IBGE, SIDRA tabela 1737, variável 2266 (https://sidra.ibge.gov.br/tabela/1737). Uso livre com citação da fonte. | `uv run python -m fipe.inflation --update` |
