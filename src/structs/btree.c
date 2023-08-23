/* A B-Tree Implementation
 *
 * NOTES
 *  Must free b->root before end of program
 *  n->ptr or n->c[i] == 0, means a NULL pointer
 *      this means it does not yet have a place in the binary file
 *
 * FILE STRUCTURE
 *  |-------------|
 *  | uint32_t t  |  minimum degree t of b
 *  |-------------|
 *  | PTR_TYPE r  |  location of b->root
 *  |-------------|
 *  | Node        |  1
 *  |-------------|
 *  | Node        |  2
 *  |-------------|
 *  | Node        |  3
 *  |-------------|
 *  | ...         |  ...
 *
 *  Where Node:
 *  |---------------------|
 *  | bool leaf           |
 *  |---------------------|
 *  | uint64_t n          |
 *  |---------------------|
 *  | PTR_TYPE ptr        |
 *  |---------------------|
 *  | KEY_TYPE keys[2t-1] |
 *  |---------------------|
 *  | PTR_TYPE c[2t]      |
 *  |---------------------|
 *
 * TODO
 * Add values to Node
 * Implement defragmentation
 * Add memory error handling
 * Optimize memory usage (early deallocation)
 */

#include "btree.h"
#include <stdio.h>
#include <string.h>


void BTree_delete_find_internal(KEY_TYPE k, uint64_t i, Node *x, BTree *b);
void BTree_delete_internal(KEY_TYPE k, uint64_t i, Node *x, BTree *b);

Node *allocate_node(BTree *b) {
    Node *n = malloc(sizeof(Node));
    n->d = malloc(b->d_size);
    n->c = malloc(b->c_size);
    n->n = 0;
    n->leaf = true;
    n->ptr = 0;
    for (int i = 0; i < (2 * b->t - 1); i++) {
        n->d[i].key = 0;
    }
    for (int i = 0; i < 2 * b->t; i++) {
        n->c[i] = 0;
    }
    return n;
}

void deallocate_node(Node *n) {
    free(n->d);
    free(n->c);
    free(n);
    return;
}

Node *read_node(Node *n, PTR_TYPE c, BTree *b) {
    size_t offset = (c - 1) * b->node_size;
    FILE *file = fopen(b->filename, "rb");
    if (file == NULL)
        return NULL;
    fseek(file, sizeof(uint32_t) + sizeof(PTR_TYPE), SEEK_SET);
    fseek(file, offset, SEEK_CUR);
    if (fread(&n->leaf, sizeof(bool), 1, file) != 1) {
        fclose(file);
        return NULL;
    }
    if (fread(&n->n, sizeof(uint64_t), 1, file) != 1) {
        fclose(file);
        return NULL;
    }
    if (fread(&n->ptr, sizeof(PTR_TYPE), 1, file) != 1) {
        fclose(file);
        return NULL;
    }
    if (fread(n->d, b->d_size, 1, file) != 1) {
        fclose(file);
        return NULL;
    }
    if (fread(n->c, b->c_size, 1, file) != 1) {
        fclose(file);
        return NULL;
    }
    fclose(file);
    return n;
}

Node *write_node(Node *n, BTree *b) {
    FILE *file = fopen(b->filename, "r+b");
    if (file == NULL)
        return NULL;
    if (n->ptr == 0) {
        fseek(file, 0, SEEK_END);
        uint64_t eof = ftell(file);
        fseek(file, sizeof(uint32_t) + sizeof(PTR_TYPE), SEEK_SET);
        uint64_t first_node = ftell(file);
        n->ptr = (size_t)((eof - first_node) / b->node_size) + 1;
    }
    size_t offset = (n->ptr - 1) * b->node_size;
    fseek(file, sizeof(uint32_t) + sizeof(PTR_TYPE), SEEK_SET);
    fseek(file, offset, SEEK_CUR);
    if (fwrite(&n->leaf, sizeof(bool), 1, file) != 1) {
        fclose(file);
        return NULL;
    }
    if (fwrite(&n->n, sizeof(uint64_t), 1, file) != 1) {
        fclose(file);
        return NULL;
    }
    if (fwrite(&n->ptr, sizeof(PTR_TYPE), 1, file) != 1) {
        fclose(file);
        return NULL;
    }
    if (fwrite(n->d, b->d_size, 1, file) != 1) {
        fclose(file);
        return NULL;
    }
    if (fwrite(n->c, b->c_size, 1, file) != 1) {
        fclose(file);
        return NULL;
    }
    fclose(file);
    return n;
}

void BTree_create(uint32_t t, char filename[], BTree *b) {
    b->t = t;
    b->d_size = (2 * b->t - 1) * sizeof(Data);
    b->c_size = (2 * b->t) * sizeof(PTR_TYPE);
    b->node_size = sizeof(bool) + sizeof(uint64_t) + sizeof(PTR_TYPE) + b->d_size + b->c_size;
    strcpy(b->filename, filename);
    FILE *file = fopen(b->filename, "wb");
    fwrite(&b->t, sizeof(uint32_t), 1, file);
    PTR_TYPE c = 1;
    fwrite(&c, sizeof(PTR_TYPE), 1, file);
    fclose(file);
    b->root = allocate_node(b);
    write_node(b->root, b);
    return;
}

void BTree_load(char filename[], BTree *b) {
    strcpy(b->filename, filename);
    FILE *file = fopen(b->filename, "rb");
    fread(&b->t, sizeof(uint32_t), 1, file);
    PTR_TYPE c;
    fread(&c, sizeof(PTR_TYPE), 1, file);
    fclose(file);
    b->d_size = (2 * b->t - 1) * sizeof(Data);
    b->c_size = (2 * b->t) * sizeof(PTR_TYPE);
    b->node_size = sizeof(bool) + sizeof(uint64_t) + sizeof(PTR_TYPE) + b->d_size + b->c_size;
    b->root = allocate_node(b);
    read_node(b->root, c, b);
    return;
}

void print_node(Node *n, BTree *b) {
    printf("%08lx  ", n->ptr);
    for (int j = 0; j < (2 * b->t - 1); j++) {
        printf("%02lx ", n->d[j].key);
    }
    printf("    %02lx %d\n          ", n->n, n->leaf);
    for (int j = 0; j < (2 * b->t); j++) {
        printf("%02lx ", n->c[j]);
    }
    printf("\n");
}

void sequential_print(BTree *b) {
    Node *n = allocate_node(b);

    FILE *file = fopen(b->filename, "rb");
    uint32_t t;
    PTR_TYPE root_loc;
    fread(&t, sizeof(uint32_t), 1, file);
    fread(&root_loc, sizeof(PTR_TYPE), 1, file);
    fclose(file);
    printf("t = %d\nr->ptr = %ld\n", t, root_loc);
    uint64_t i = 1;
    while (read_node(n, i, b) != NULL) {
        print_node(n, b);
        i++;
    }

    deallocate_node(n);
    return;
}

// Node *x must already be allocated
Data *BTree_search(Node *x, KEY_TYPE k, BTree *b) {
    int i = 0;
    while (i < x->n && k > x->d[i].key) {
        i++;
    }
    if (i < x->n && k == x->d[i].key)
        return &x->d[i];
    else if (x->leaf)
        return NULL;
    else {
        read_node(x, x->c[i], b);
        return BTree_search(x, k, b);
    }
}

// Node *x must already be allocated
void BTree_split_child(Node *x, uint64_t i, BTree *b) {
    Node *y = allocate_node(b);
    read_node(y, x->c[i], b);

    Node *z = allocate_node(b); // NOTE does not yet have z->ptr
    z->leaf = y->leaf;
    z->n = b->t - 1;
    for (int j = 0; j < (b->t - 1); j++) {
        z->d[j] = y->d[j + b->t];
    }
    if (!y->leaf) {
        for (int j = 0; j < b->t; j++) {
            z->c[j] = y->c[j + b->t];
        }
    }
    y->n = b->t - 1;
    for (uint64_t j = x->n + 1; j > i + 1; j--) {
        x->c[j] = x->c[j - 1];
    }
    write_node(z, b);
    x->c[i + 1] = z->ptr;
    for (uint64_t j = x->n; j > i; j--) {
        x->d[j] = x->d[j - 1];
    }
    x->d[i] = y->d[b->t - 1];
    x->n = x->n + 1;
    write_node(y, b);
    write_node(x, b);
    deallocate_node(y);
    deallocate_node(z);
    return;
}

Node *BTree_split_root(BTree *b) {
    Node *s = allocate_node(b);
    s->leaf = false;
    s->c[0] = b->root->ptr;
    deallocate_node(b->root);
    b->root = s;
    write_node(s, b);
    FILE *file = fopen(b->filename, "r+b"); // Update root location
    fseek(file, sizeof(uint32_t), SEEK_SET);
    fwrite(&s->ptr, sizeof(PTR_TYPE), 1, file);
    fclose(file);
    BTree_split_child(s, 0, b);
    return s;
}

void BTree_insert_nonfull(Data k, Node *x, BTree *b) {
    uint64_t i = x->n;
    if (x->leaf) {
        while (i > 0 && k.key < x->d[i - 1].key) {
            x->d[i] = x->d[i - 1];
            i--;
        }
        x->d[i] = k;
        x->n = x->n + 1;
        write_node(x, b);
    } else {
        while (i > 0 && k.key < x->d[i - 1].key) {
            i--;
        }
        Node *n = allocate_node(b);
        read_node(n, x->c[i], b);
        if (n->n == 2 * b->t - 1) {
            BTree_split_child(x, i, b);
            if (k.key > x->d[i].key) {
                read_node(n, x->c[i + 1], b);
            } else {
                read_node(n, x->c[i], b);
            }
        }
        BTree_insert_nonfull(k, n, b);
        deallocate_node(n);
    }
    return;
}

void BTree_insert(Data k, BTree *b) {
    if (b->root->n == 2 * b->t - 1) {
        Node *s = BTree_split_root(b);
        BTree_insert_nonfull(k, s, b);
    } else {
        BTree_insert_nonfull(k, b->root, b);
    }
    return;
}

// Merges keys[i] and c[i+1] into c[i]
PTR_TYPE BTree_merge(Node *x, uint64_t i, BTree *b) {
    Node *ci = allocate_node(b);
    Node *ci1 = allocate_node(b);
    read_node(ci, x->c[i], b);
    read_node(ci1, x->c[i + 1], b);
    ci->d[ci->n] = x->d[i]; // Move x->keys[i]
    ci->n++;
    for (uint64_t j = 0; j < ci1->n; j++) { // Move c[i+1]
        ci->d[ci->n] = ci1->d[j];
        ci->c[ci->n] = ci1->c[j];
        ci->n++;
    }
    ci->c[ci->n] = ci1->c[ci1->n];
    uint64_t j = i + 1;
    while (j < x->n) { // Shift keys in x
        x->d[j - 1] = x->d[j];
        j++;
    }
    j = i + 2;
    while (j < x->n + 1) { // Shift c in x
        x->c[j - 1] = x->c[j];
        j++;
    }
    x->n--;
    write_node(x, b);
    write_node(ci, b);
    // What to do with ci1? How to remove from file without fragmentation
    // For now will simply set n to 0, and save to file
    ci1->n = 0;
    write_node(ci1, b);
    deallocate_node(ci1);
    if (x->ptr == b->root->ptr && x->n == 0) {  // New root
        FILE *file = fopen(b->filename, "r+b"); // Update root location
        fseek(file, sizeof(uint32_t), SEEK_SET);
        fwrite(&ci->ptr, sizeof(PTR_TYPE), 1, file);
        fclose(file);
        read_node(b->root, ci->ptr, b);
    }
    PTR_TYPE ptr = ci->ptr;
    deallocate_node(ci);
    return ptr;
}

void BTree_rotate_left(uint64_t i, Node *nci_, Node *x, Node *nci, BTree *b) {
    uint64_t j = nci->n;
    while (j > 0) { // Insert x->keys[i-1] into nci->keys[0]
        nci->d[j] = nci->d[j - 1];
        nci->c[j + 1] = nci->c[j];
        j--;
    }
    nci->c[1] = nci->c[0];
    nci->d[0] = x->d[i - 1];
    x->d[i - 1] = nci_->d[nci_->n - 1]; // Move nci_->keys[n-1] into x->keys[i-1]
    nci->c[0] = nci_->c[nci_->n];             // Move nci_->c[n] into nci->c[0]
    nci->n++;
    nci_->n--;
    write_node(x, b);
    write_node(nci_, b);
    write_node(nci, b);
}

void BTree_rotate_right(uint64_t i, Node *nci, Node *x, Node *nci1, BTree *b) {
    nci->d[nci->n] = x->d[i]; // Insert x->keys[i] into nci->keys[n]
    x->d[i] = nci1->d[0];     // Move nci1->keys[0] into x->keys[i]
    uint64_t j = 0;
    nci->c[nci->n + 1] = nci1->c[0]; // Move nci1->c[0] into nci->c[n+1]
    nci->n++;
    nci1->n--;
    while (j < nci1->n) {
        nci1->d[j] = nci1->d[j + 1];
        nci1->c[j] = nci1->c[j + 1];
        j++;
    }
    nci1->c[nci1->n] = nci1->c[nci1->n + 1];
    write_node(x, b);
    write_node(nci1, b);
    write_node(nci, b);
}

void BTree_delete_find_internal(KEY_TYPE k, uint64_t i, Node *x, BTree *b) {
    Node *nci = allocate_node(b); // Find x->c[i] that must contain key
    read_node(nci, x->c[i], b);
    if (nci->n < b->t) { // Node has less than t keys
        Node *nci_ = allocate_node(b);
        Node *nci1 = allocate_node(b);
        if (i > 0) {
            read_node(nci_, x->c[i - 1], b);
        }
        if (i < x->n) {
            read_node(nci1, x->c[i + 1], b);
        }
        if (nci_->n >= b->t || nci1->n >= b->t) { // Immediate sibling has at least keys
            if (nci_->n >= b->t) {
                BTree_rotate_left(i, nci_, x, nci, b);
                BTree_delete(k, nci, b);
            } else {
                BTree_rotate_right(i, nci, x, nci1, b);
                BTree_delete(k, nci, b);
            }
        } else { // No siblings eligible, must merge them
            i = (i == x->n) ? i - 1 : i;
            read_node(x, BTree_merge(x, i, b), b);
            BTree_delete(k, x, b);
        }
        deallocate_node(nci_);
        deallocate_node(nci1);
    } else {
        BTree_delete(k, nci, b);
    }
    deallocate_node(nci);
}

void BTree_delete_internal(KEY_TYPE k, uint64_t i, Node *x, BTree *b) {
    if (i > 0 && x->d[i - 1].key == k) { // Found k in internal node
        Node *nci = allocate_node(b);
        read_node(nci, x->c[i - 1], b);
        if (nci->n >= b->t) {                    // x->c[i-1] (predecessor) has at least t keys
            Data pred = nci->d[x->n - 1]; // Find predecessor in x->c[i-1]
            x->d[i - 1] = pred;               // Replace k with predecessor
            write_node(x, b);
            BTree_delete(pred.key, nci, b); // Delete predecesor from x->c[i-1]
        } else {
            Node *nciplus = allocate_node(b);
            read_node(nciplus, x->c[i], b);
            if (nciplus->n >= b->t) {             // x->c[i] (successor) has at least t keys
                Data succ = nciplus->d[0]; // Find sucessor in x->c[i]
                x->d[i - 1] = succ;            // Replace k with sucessor
                write_node(x, b);
                BTree_delete(succ.key, nciplus, b);            // Delete successor from x->c[i]
            } else {                                       // pre and succ have t-1 keys, merge
                read_node(x, BTree_merge(x, i - 1, b), b); // Merge c[i-1] and c[i] and move k
                BTree_delete(k, x, b);                     // Delete k from merged
            }
            deallocate_node(nciplus);
        }
        deallocate_node(nci);
    } else { // k is not in this internal node
        BTree_delete_find_internal(k, i, x, b);
    }
}

void BTree_delete(KEY_TYPE k, Node *x, BTree *b) {
    uint64_t i = x->n;
    while (i > 0 && x->d[i - 1].key > k) { // Searches for k
        i--;
    }
    if (x->leaf) {
        if (i > 0 && x->d[i - 1].key == k) { // Found k in leaf
            while (i < x->n) {              // Shift >keys to the left
                x->d[i - 1] = x->d[i];
                i++;
            }
            x->n--;
            write_node(x, b);
        }
    } else {
        BTree_delete_internal(k, i, x, b);
    }
}
