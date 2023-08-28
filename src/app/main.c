/*! Searching the binary files
 * 
 * USAGE:
 *  $ ./main
 * 
 *  $ > list -b
 *  $ Acura - 1
 *  $ Agrale - 2
 *  $ [brand] - [cod]
 *  $ ....
 * 
 *  $ > list -b Su
 *  $ Subaru - 78
 *  $ Suzuki - 79
 * 
 *  $ > list -b Subaru -m
 *  $ Forester ... - 1
 *  $ ...
 *  $ Impreza ... - 8
 *  $ [model] - [cod]
 *  $ ...
 * 
 *  $ > search 22 1 78 8        // TODO add flags eg. -v 10000 -V 40000
 *  $ 2023/1 Subaru Impreza ... 1998
 *  $ 2023/1 Subaru Impreza ... 1999
 *  $ 2023/1 Subaru Impreza ... 2000
 *  $ ...
 * 
 *  $ > search 22 1 78 8 99
 *  $ 2023/1 Subaru Impreza ... 1999
 *  $   Valor: R$ 40.000,00
 *  $   Combustivel: Gasolina
 *  $   Cambio: Manual
 *  $   cc : 2.4
 *  $   Cod-FIPE : 12345-01
 */

// Program loop
    // List brands (all and prefix search)

    // List models of specific brand (all and prefix search)

    // Search for specific car (ano_ref mes_ref marca modelo ano_fab) - returns specific info

    // Partial search (ano_ref mes_ref marca [modelo [ano_fab]]) - returns list of names

    // OPTIONAL: Partial search with requirements (eg. valor < 30.000)

#include "../structs/entities.h"
#include "../structs/btree.h"
#include "../structs/trie.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define MAX_INPUT 256
#define MAX_ARGS 5


typedef struct {
    const char* command;
    void (*function)();
} COMMAND;

typedef struct {
    BTree *index;
    Trie *brands;
} CONTEXT;

void help_command(void);
void list_command(const char *args[], CONTEXT context);
void search_command(const char *args[], CONTEXT context);

void read_car(Carro *c, PTR_TYPE offset); // Read car from sequencial.bin
void print_car(Carro c);

int main(void) {
    // Create command_map
    COMMAND command_map[] = {
        {"help", help_command},
        {"list", list_command},
        {"search", search_command}
    };

    // Load BTree index
    char index_filename[] = "../bin/index.btree";
    BTree index;
    BTree_load(index_filename, &index);

    // Load brands.trie
    char brands_filename[] = "../bin/brands.trie";
    Trie brands;
    load_trie_from_file(&brands, brands_filename);

    CONTEXT context;
    context.index = &index;
    context.brands = &brands;

    int exit = 0;
    char input[MAX_INPUT];
    help_command();
    while(!exit) {
        printf("> ");
        fgets(input, sizeof(input), stdin);
        size_t len = strlen(input);
        if (len > 0 && input[len - 1] == '\n')
            input[len - 1] = '\0';

        
        char *token = strtok(input, " ");
        char *command = strdup(token);
        char *args[MAX_ARGS] = {};
        int k = 0;
        token = strtok(NULL, " ");
        while (token != NULL && k < MAX_ARGS) {
            args[k] = strdup(token);
            token = strtok(NULL, " ");
            k++;
        }
        if (k >= MAX_ARGS && token != NULL) {
            printf("Warning: too many args! Some will be ignored.\n");
        }

        int found = 0;
        for (int i = 0; i < sizeof(command_map) / sizeof(COMMAND); i++) {
            if (strcmp(command, "exit") == 0) {
                found = 1;
                exit = 1;
                break;
            }
            if (strcmp(command, command_map[i].command) == 0) {
                command_map[i].function(args, context);
                found = 1;
                break;
            }
        }
        if (!found)
            printf("Unkown command\n");

        free(command);
        for (int i = 0; i < MAX_ARGS && args[i] != NULL; i++)
            free(args[i]);
    }

    deallocate_node(index.root);
    free_trienode(brands.root);

    return 0;
}

void help_command(void) {
    char help_message[] = 
    "FIPE DB\n"
    "Available Commands:\n"
    "help - displays this help message\n"
    "list - list brands or models\n"
    "\teg. list -b Subaru -m\n"
    "search - search for cars\n"
    "\teg. search 22 1 36 69 2010\n";

    printf("%s", help_message);
}

void list_command(const char *args[], CONTEXT context) {
    for (int i = 0; i < MAX_ARGS && args[i] != NULL; i++) { }
    WordLinkedList *words = NULL;
    char *word = calloc(WORD_SIZE, sizeof(char));
    strcpy(word, "A");
    words = prefix_trie_search(context.brands->root, word, words);
    free(word);
    WordLinkedList *aux = words; 
    while (aux != NULL) {
        printf("%s - %d\n", aux->word, aux->code);
        aux = aux->next;
    }

    aux = words;
    while (aux != NULL) {
        aux = words->next;
        free(words);
        words = aux;
    }
    return;
}

void search_command(const char *args[], CONTEXT context) {
    int i;
    for (i = 0; i < MAX_ARGS && args[i] != NULL; i++) { }
    if (i < 3) {
        printf("Insufficient arguments for search\n");
        return;
    }
    KEY_TYPE key = 0;
    key += atoi(args[0]);
    key = key << 8;
    key += atoi(args[1]);
    key = key << 8;
    key += atoi(args[2]);
    key = key << 12;
    if (3 < i)
        key += atoi(args[3]);
    key = key << 16;
    if (4 < i)
        key += atoi(args[4]);

    Node *x = allocate_node(context.index);
    read_node(x, context.index->root->ptr, context.index);
    Data *d = BTree_search(x, key, context.index);
    if (d != NULL) {
        Carro car;
        read_car(&car, d->value);
        print_car(car);
    } else {
        printf("Could not find that car.\n");
    }
    deallocate_node(x);
    return;
}

void read_car(Carro *c, PTR_TYPE offset) {
    char bin_filename[] = "../bin/sequencial.bin";
    FILE *bin = fopen(bin_filename, "rb");
    fseek(bin, sizeof(Carro)*offset, SEEK_SET);
    if (fread(c, sizeof(Carro), 1, bin) != 1) {
        printf("Error reading from %s\n", bin_filename);
    }
    fclose(bin);
}

void print_car(Carro c) {
    printf("  Ref.: %d/%d - %d %d %d\n", c.ano_ref, c.mes_ref, c.cod_marca, c.cod_modelo, c.ano_fab);
    printf("    Valor: %f\n", c.valor);
    printf("    Combustivel: %d\n", c.combustivel);
    printf("    Cambio: %d\n", c.cambio);
    printf("    cc: %f\n", c.tam_motor);
    printf("    CodigoFipe: %d\n", c.cod_fipe);
}