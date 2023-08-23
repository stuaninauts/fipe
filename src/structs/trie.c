/* A TRIE Implementation
 *
 * NOTES
 *      Trienode.code:
 *          the default implementaion of TRIE uses the bool is_terminal attribute 
 *          in this implementation this attribute is contained within the code 
 *          trienodes that are not terminals have the code -1, >0 opposite case
 *      Trienode.data:
 *          exists just for visualization  
 * 
 *      Trie.globalcode:
 *          exists for code reference in the trienodes (can be optimized, TODO)
 *      
 * 
 * FILE STRUCTURE
 *  |-------------|
 *  | Trie *t     |  location of t->root
 *  |-------------|
 *  | TrieNode    |  1
 *  |-------------|
 *  | TrieNode    |  2
 *  |-------------|
 *  | TrieNode    |  3
 *  |-------------|
 *  | ...         |  ...
 *
 *  Where TrieNode:
 *  |---------------------------|
 *  | *children[ALPHABET_SIZE]  | 
 *  |---------------------------|
 *  | int code                  |
 *  |---------------------------|
 *  | char data;                |
 *  |---------------------------|
 * 
 *  TODO
 *  load_trie
 *  Search for alternative alphabets
 *  Documentation
 *  Deletion
 *  Optimize globalcode
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "trie.h"

void create_trie(Trie *t, char *filename) {
    t->root = allocate_trienode();
    strcpy(t->filename, filename);
    t->global_code = 0;
    
    FILE *file = fopen(t->filename, "wb");
    fwrite(&t->root, sizeof(TrieNode*), 1, file);
    fclose(file);

    return;
}

TrieNode *allocate_trienode() {
    int i;
    TrieNode *node = (TrieNode*)malloc(sizeof(TrieNode));
    if (node == NULL) {
        perror("Memory allocation failed");
        return NULL;
    }

    for (i=0; i<ALPHABET_SIZE; i++) {
        node->children[i] = NULL;
    }
    //node->data
    node->code = -1;
    
    return node;
}

void free_trienode(TrieNode *node) {
    int i;
    for (i=0; i<ALPHABET_SIZE; i++) {
        if (node->children[i] != NULL) {
            free_trienode(node->children[i]);
        }
    }

    free(node);
    return;
}

Trie *insert_trienode(Trie *t, char *word) {
    TrieNode *aux = t->root;  
    int i;
    
    // TODO LOOK ATHIS DUDE
    for (i=0; word[i] != '\0'; i++) {
        int index = (int) word[i] - 'a';
        if (aux->children[index] == NULL) {
            aux->children[index] = allocate_trienode();
            aux->children[index]->data = word[i];
        }
        aux = aux->children[index];
    }
    aux->code = ++t->global_code;

    FILE *file = fopen(t->filename, "ab");
    if (file == NULL) {
        perror("Error opening the file");
        return t;
    }

    fwrite(aux, sizeof(TrieNode), 1, file);
    fclose(file);

    return t;
}

int search_trie(Trie *trie, char *word) {
    TrieNode *aux = trie->root;
    int i;

    for(i=0; word[i]!='\0'; i++) {
        int position = word[i] - 'a';
        if (aux->children[position] == NULL)
            return 0;
        aux = aux->children[position];
    }

    if (aux != NULL && aux->code != -1) {
        return aux->code;
    }
    
    return 0;
}

void *load_trie(Trie *t) {
    FILE *file = fopen(t->filename, "r+");
    if (file == NULL) {
        perror("Error opening the trie file");
        return NULL;
    }

    // TODO


    fclose(file);


    return t;
}



void print_search(Trie *t, char *word) {
    int code;
    printf("Searching for %s: ", word);

    if ((code = search_trie(t, word)) == 0)
        printf("Not Found\n");
    else
        printf("Found! Code: %d\n", code);
}

void print_trie_recursive(TrieNode *node, int depth) {
    if (node == NULL) 
        return;
    
    printf("n%d", depth);

    for (int i = 0; i < depth; i++) 
        printf("  "); 

    printf("%c", node->data);
    
    if (node->code != -1) 
        printf(" (code: %d)", node->code);
    
    printf("\n");

    for (int i = 0; i < ALPHABET_SIZE; i++) 
        print_trie_recursive(node->children[i], depth + 1);

}

void print_trie(Trie *t) {
    printf("Trie Structure:\n");
    print_trie_recursive(t->root, 0);
}

// TODO
// void sequencial_print(Trie *t) {

// }
