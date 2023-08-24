#ifndef TRIE_H
#define TRIE_H

#include <stdlib.h>

#define MAX_FILENAME 64
#define ALPHABET_SIZE 255 // redefine
#define WORD_SIZE 128

typedef struct TrieNode TrieNode;
struct TrieNode {
    TrieNode *children[ALPHABET_SIZE];
    int code; // if -1 node is not terminal
    char data; // just for testing
};

typedef struct Trie Trie;
struct Trie {
    TrieNode *root;
    char filename[MAX_FILENAME];
    int global_code;
};

void create_trie(Trie *t, char *filename);
// this function does not need params because of globalcode
TrieNode *allocate_trienode();
void free_trienode(TrieNode *node);
int insert_trienode(Trie *t, char *word);
int search_trie(Trie *trie, char *word);
void load_trie_from_file(Trie *t, char filename[]);
void print_search(Trie *t, char *word);
void print_trie(Trie *t);
void print_trienode(TrieNode *node);

#endif