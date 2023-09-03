CC = gcc
CFLAGS = -Wall -g

SRCDIR = src
BINDIR = bin

clean :
	rm -f app create_binaries

create_binaries : $(SRCDIR)/create_binaries.c $(SRCDIR)/structs/btree.c $(SRCDIR)/structs/trie.c
	$(CC) $(CFLAGS) -o $@ $^

app : $(SRCDIR)/app/main.c $(SRCDIR)/structs/btree.c $(SRCDIR)/structs/trie.c
	$(CC) $(CFLAGS) -o $@ $^
