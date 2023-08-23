#ifndef BTREE_H
#define BTREE_H

#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_FILENAME 64
#define KEY_TYPE uint64_t
#define VALUE_TYPE uint64_t
#define PTR_TYPE uint64_t

typedef struct {
    KEY_TYPE key;
    VALUE_TYPE value;
} Data;

typedef struct {
    bool leaf;
    uint64_t n;
    PTR_TYPE ptr;
    Data *d;
    PTR_TYPE *c;
} Node;

typedef struct {
    uint32_t t;
    size_t node_size;
    size_t d_size;
    size_t c_size;
    Node *root;
    char filename[MAX_FILENAME];
} BTree;

Node *allocate_node(BTree *b);
void deallocate_node(Node *n);
Node *read_node(Node *n, PTR_TYPE c, BTree *b);
void BTree_create(uint32_t t, char filename[], BTree *b);
void BTree_load(char filename[], BTree *b);
Data *BTree_search(Node *x, KEY_TYPE k, BTree *b);
void BTree_insert(Data k, BTree *b);
void BTree_delete(KEY_TYPE k, Node *x, BTree *b);
void print_node(Node *n, BTree *b);
void sequential_print(BTree *b);

#endif