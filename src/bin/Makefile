create_bin : create_binaries.o trie.o btree.o 
	cc -o create_bin create_binaries.o trie.o btree.o 

create_binaries.o : create_binaries.c ../structs/trie.h ../structs/btree.h ../structs/entities.h
	cc -c create_binaries.c

trie.o : ../structs/trie.c ../structs/trie.h
	cc -c ../structs/trie.c

btree.o : ../structs/btree.c ../structs/btree.h
	cc -c ../structs/btree.c