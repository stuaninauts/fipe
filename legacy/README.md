# Legado: índices em C da disciplina (v1, 2023)

Código do trabalho final de INF01124 (Classificação e Pesquisa de Dados, INF/UFRGS), feito em dupla por
Eduardo Stuani e Gustavo Lacroix (@gpl27). O estado entregue está na tag `v1.0-academic`.

Está congelado: fica aqui para mostrar o trabalho original, fora do pipeline, do site e do CI
([ADR 0003](../docs/adr/0003-legado-e-cortes.md)). Não recebe correção de funcionalidade.

## O que tem
- `create_binaries.c`: lê `data/database.csv` e gera os arquivos de índice em `bin/`: o arquivo sequencial
  (`sequencial.bin`), uma B-tree que dá um código único a cada linha (`index.btree`) e tries para busca por prefixo
  de marca (`brands.trie`) e de modelo (`<marca>.trie`).
- `app/main.c`: app de busca em terminal sobre esses índices.
- `structs/`: as implementações de B-tree e trie.

## Como rodar
Os dados não são distribuídos ([ADR 0001](../docs/adr/0001-dados-brutos-locais.md)): é preciso ter um
`database.csv` no formato da v1 em `legacy/data/`.

```bash
cd legacy
make            # gera create_binaries e fipe-app
./create_binaries
./fipe-app
```

## Limitações conhecidas (revisão de 2026)
- Nomes com UTF-8 (por exemplo "Citroën") estouram o índice de caractere na trie (`structs/trie.c`): leitura fora
  dos limites, detectada com AddressSanitizer.
- No app, linha vazia dá falha de segmentação e fim de arquivo (EOF) entra em laço infinito; a busca parcial não
  foi implementada.
- Gerar os índices da base inteira leva perto de meia hora.
