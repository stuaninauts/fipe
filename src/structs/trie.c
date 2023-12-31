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
 *          exists for code reference in the trienodes (can be optimized)
 *      
 * 
 * FILE STRUCTURE
 *  |-------------|
 *  | word        |  0
 *  |-------------|
 *  | word        |  1
 *  |-------------|
 *  | word        |  2
 *  |-------------|
 *  | word        |  3
 *  |-------------|
 *  | ...         |  ...
 *
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "trie.h"

void create_trie(Trie *t, char *filename) {
    t->root = allocate_trienode();
    strcpy(t->filename, filename);
    t->global_code = 0;
    
    FILE *file = fopen(t->filename, "w");
    if (file == NULL) {
        perror("Error opening the file");
        return;
    }
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
    node->data = 0;
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

int insert_trienode(Trie *t, char *word) {
    TrieNode *aux = t->root;  
    int i;
    
    for (i=0; word[i] != '\0'; i++) {
        int index = (int) word[i];
        if (aux->children[index] == NULL) {
            aux->children[index] = allocate_trienode();
            aux->children[index]->data = word[i];
        }
        aux = aux->children[index];
    }
    aux->code = ++t->global_code;

    FILE *file = fopen(t->filename, "a");
    if (file == NULL) {
        perror("Error opening the file");
        return 0;
    }
    
    fprintf(file, "%s\n", word);
    fclose(file);

    return aux->code;
}

int search_trie(Trie *trie, char *word) {
    TrieNode *aux = trie->root;
    int i;

    for(i=0; word[i]!='\0'; i++) {
        int position = word[i];
        if (aux->children[position] == NULL)
            return 0;
        aux = aux->children[position];
    }

    if (aux != NULL && aux->code != -1) {
        return aux->code;
    }
    
    return 0;
}

void load_trie_from_file(Trie *t, char filename[]) {
    // create the trie
    t->root = allocate_trienode();
    strcpy(t->filename, filename);
    t->global_code = 0;

    FILE *file = fopen(t->filename, "r");
    if (file == NULL) {
        // perror("Error opening the trie file");
        return;
    }

    // read the content
    char word[WORD_SIZE];
    while (fgets(word, sizeof(word), file)) {
        // remove the \n
        size_t length = strcspn(word, "\n");
        word[length] = '\0';
        TrieNode *aux = t->root;  
        int i;
        
        for (i=0; word[i] != '\0'; i++) {
            int index = (int) word[i];
            if (aux->children[index] == NULL) {
                aux->children[index] = allocate_trienode();
                aux->children[index]->data = word[i];
            }
            aux = aux->children[index];
        }
        aux->code = ++t->global_code;
    }
    
    fclose(file);
    return;
}

void print_search(Trie *t, char *word) {
    int code;
    printf("Searching for %s: ", word);

    if ((code = search_trie(t, word)) == 0)
        printf("Not Found\n");
    else
        printf("Found! Code: %d\n", code);
    return;
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

    return;

}

void print_trie(Trie *t) {
    printf("Trie Structure:\n");
    print_trie_recursive(t->root, 0);
    return;
}

void print_trienode(TrieNode *node) {
    int i;
    printf("Code: %d Data: %c Childrens: ", node->code, node->data);
    for (i=0; i<ALPHABET_SIZE; i++)
        if (node->children[i] != NULL)
            printf("%c, ", node->children[i]->data);
    printf("\n");
    return;
}

WordLinkedList *list_trienode_words(TrieNode *node, char word[], WordLinkedList *words) {
    char *word_cpy = calloc(WORD_SIZE, sizeof(char));
    strcpy(word_cpy, word);
    int i = strlen(word_cpy);
    word_cpy[i] = node->data;
    word_cpy[i+1] = '\0';
    if (node->code != -1) { // Found one word
        WordLinkedList *new_word = calloc(1, sizeof(WordLinkedList));
        new_word->next = NULL;
        strcpy(new_word->word, word_cpy);
        new_word->code = node->code;
        if (words == NULL) {
            words = new_word;
        } else {
            new_word->next = words;
            words = new_word;
        }
    } else {
        for (i = 0; i < ALPHABET_SIZE; i++) {
            if (node->children[i] != NULL) {
                words = list_trienode_words(node->children[i], word_cpy, words);
            }
        }
    }
    free(word_cpy);
    return words;
}

WordLinkedList *prefix_trie_search(TrieNode *node, char prefix[], WordLinkedList *words) {
    TrieNode *aux = node;
    int i = 0; int pos;
    while (prefix[i] != '\0') {
        pos = prefix[i];
        if (aux->children[pos] == NULL) {
            // Prefix is invalid
            printf("Invalid prefix at %c\n", prefix[i]);
            return words;
        }
        aux = aux->children[pos];
        i++;
    }
    if (i > 0) {
        prefix[i-1] = '\0';
    }
    return list_trienode_words(aux, prefix, words);
}