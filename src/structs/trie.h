#ifndef TRIE_H
#define TRIE_H

#include <stdlib.h>

#define MAX_FILENAME 64
#define ALPHABET_SIZE 255 // redefine
#define WORD_SIZE 128

// represent a single node with pointers to its children
typedef struct TrieNode TrieNode;
struct TrieNode {
    TrieNode *children[ALPHABET_SIZE];
    int code; // if -1 node is not terminal
    char data; // just for visualization
};

// represent a Trie struct, 
// containing the node representing the root, the filename and the global_code (for insert controls)
typedef struct Trie Trie;
struct Trie {
    TrieNode *root;
    char filename[MAX_FILENAME];
    int global_code;
};

typedef struct WordLinkedListS {
    struct WordLinkedListS *next;
    char word[WORD_SIZE];
    int code;
} WordLinkedList;

// given a pointer to Trie and a filename allocate a new TrieNode for the root and create a file representing this Trie
void create_trie(Trie *t, char *filename);

// allocate a new trienode and return a pointer to this node
// this function does not need params because of globalcode
TrieNode *allocate_trienode();

// given a TrieNode, free this node 
void free_trienode(TrieNode *node);

// given a pointer to Trie and a word, insert this word in the Trie
int insert_trienode(Trie *t, char *word);

// given a pointer to Trie and a word, search this word in the Trie
// if the Trie does not contain the word return 0 
// else return the code of the word
int search_trie(Trie *trie, char *word);

// given a pointer to Trie and a filename, load the .trie file with this filename
// and the pointer to Trie start to represent the loaded Trie
void load_trie_from_file(Trie *t, char filename[]);

// print the search of a word
void print_search(Trie *t, char *word);

// print the Trie in a tree format
void print_trie(Trie *t);

// print the TrieNode and the respectives childrens
void print_trienode(TrieNode *node);

WordLinkedList *prefix_trie_search(TrieNode *node, char prefix[], WordLinkedList *words);
WordLinkedList *list_trienode_words(TrieNode *node, char word[], WordLinkedList *words);

#endif