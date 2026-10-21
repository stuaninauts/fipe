# Rodar de dentro de legacy/: os programas leem data/database.csv e gravam/leem bin/ relativos à pasta atual.
CC = gcc
CFLAGS = -Wall -g

.PHONY: all clean

all : create_binaries fipe-app

clean :
	rm -f fipe-app create_binaries

create_binaries : create_binaries.c structs/btree.c structs/trie.c
	$(CC) $(CFLAGS) -o $@ $^

# Na v1 o executável se chamava "app"; aqui vira fipe-app porque app/ é a pasta do código-fonte.
fipe-app : app/main.c structs/btree.c structs/trie.c
	$(CC) $(CFLAGS) -o $@ $^
