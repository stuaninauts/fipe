main : main.o trie.o btree.o 
	cc -o main main.o trie.o btree.o 

main.o : main.c ../structs/trie.h ../structs/btree.h ../structs/entities.h
	cc -c main.c

trie.o : ../structs/trie.c ../structs/trie.h
	cc -c ../structs/trie.c

btree.o : ../structs/btree.c ../structs/btree.h
	cc -c ../structs/btree.c