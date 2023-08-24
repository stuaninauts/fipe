#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../structs/entities.h"
#include "../structs/trie.h"
#include "../structs/btree.h"

#define MAX_LINE_SIZE 1024
#define NUM_FIELDS 11


int main(void) {
    char csvFilename[] = "../../db.csv";
    char binFilename[] = "sequencial.bin";
    char delim[] = ",";
    char line[MAX_LINE_SIZE];
    int i = 0;

    // cria trie marcas
    // Trie *brand_root;
    // create_trie(brand_root, "brands.trie");
    // cria btree
    BTree btree;
    BTree_create(512, "index.btree", &btree);


    FILE *csvFile = fopen(csvFilename, "r");
    if (csvFile == NULL) {
        perror("Error opening the csv file");
        return -1;
    }

    FILE *binFile = fopen(binFilename, "wb");
    if (binFile == NULL) {
        perror("Error creating the binary file");
        fclose(csvFile);
        return -1;
    }

    Carro car;
    char *fields[NUM_FIELDS];
    char *token;
    int fieldCount = 0;
    // Skip csv header
    fgets(line, sizeof(line), csvFile);
    while (fgets(line, sizeof(line), csvFile) != NULL) {
        fieldCount = 0;

        token = strtok(line, delim);
        while (token != NULL) {
            // Ensure you don't exceed the bounds of the fields array
            if (fieldCount >= NUM_FIELDS) {
                fprintf(stderr, "Too many fields in the line.\n");
                break;
            }

            // Allocate memory for the field and copy the token
            fields[fieldCount] = strdup(token);

            if (fields[fieldCount] == NULL) {
                perror("Memory allocation error");
                return 1;
            }

            fieldCount++;
            token = strtok(NULL, delim);
        }


        int brand_code = 0;
        // printf("%d\n", fieldCount);
        printf("%s\n", fields[0]);
        // brand_code = search_trie(brand_root, fields[3]);
        // printf("%d\n", brand_code);
        // if (brand_code == 0) {
        //     // add the brand to the marcas.trie trie
        //     printf("before %d\n", brand_code);
        //     brand_code = insert_trienode(brand_root, brand_name);
        //     printf("after %d\n", brand_code);
        // }
        

        int model_code = 0; // fix
        char *model_name = fields[4];
        // check if the model not exist in the trie
        /*
        if (!(model_code = search_trie(???, model_name))) {
            // add the model to the cod_marca.trie trie (this .trie refers the models of this brand)
            model_code = insert_trienode(???, model_name);
        }        
        */

        // mount the car struct
        car.cod = atoi(fields[0]);
        car.ano_ref = atoi(fields[1]);
        car.mes_ref = atoi(fields[2]);
        car.cod_marca = brand_code;
        car.cod_modelo = model_code;
        car.ano_fab = atoi(fields[5]);
        car.valor = atof(fields[6]);

        char combustivel = fields[7][0];
        switch (combustivel) {
        case 'g':
            car.combustivel = GASOLINA;
            break;
        case 'a':
            car.combustivel = ALCOOL;
            break;
        case 'd':
            car.combustivel = DIESEL;
            break;
        case 'e':
            car.combustivel = ELETRICO;
            break;        
        }
        car.cod_fipe = atoi(fields[8]);
        char cambio = fields[9][0];
        switch (cambio) {
        case 'a':
            car.cambio = AUTOMATICO;
            break;
        case 'm':
            car.cambio = MANUAL;
        }
        car.tam_motor = atof(fields[10]);

        // encode the struct for the btree
        Data d;
        // ano mes marca modelo fab
        // dd  dd   ddd  dddd    dd
        // 8   8    12    16     8     = 52 bits
        KEY_TYPE btree_key = 0;
        btree_key += (car.ano_ref % 100);
        btree_key << 8;
        btree_key += car.mes_ref;
        btree_key << 8;
        btree_key += car.cod_marca;
        btree_key << 12;
        btree_key += car.cod_modelo;
        btree_key << 16;
        btree_key += car.ano_fab;
        // printf("%16lx\n", btree_key);

        d.key = btree_key;
        d.value = car.cod;
        // add car in the btree
        BTree_insert(d, &btree);

        // write the car fields into the binFile
        fwrite(&car, sizeof(Carro), 1, binFile);

        for (int i = 0; i < fieldCount; i++) {
            free(fields[i]); // Free the allocated memory for each field
        }
    }

    fclose(binFile);
    fclose(csvFile);

    deallocate_node(btree.root);

    return 0;
}