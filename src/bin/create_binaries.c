#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../structs/entities.h"
#include "../structs/trie.h"
#include "../structs/btree.h"

#define MAX_LINE_SIZE 1024
#define NUM_FIELDS 11


int main() {
    char csvFilename[] = "../../database.csv";
    char binFilename[] = "sequencial.bin";
    char delim[] = ",";
    char line[MAX_LINE_SIZE];
    int i = 0;

    // cria trie marcas
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

    Trie *brand_root;
    create_trie(brand_root, "brands.trie");

    // read the lines from the csvFile
    while(fgets(line, sizeof(line), csvFile) != NULL) {
        Carro car;
        
        char *fields[NUM_FIELDS];
        char *token;
        int fieldCount = 0;
        // get the fields from the line
        token = strtok(line, delim);
        while (token != NULL) { 
            fields[fieldCount++] = token;
            token = strtok(NULL, delim);
        }
        fieldCount = 0;



        int brand_code;
        char *brand_name = fields[3];
        brand_code = search_trie(brand_root, brand_name);
        if (!(brand_code)) {
            // add the brand to the marcas.trie trie
            brand_code = insert_trienode(brand_root, brand_name);
        }
        

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

        char combustivel = (char)fields[7];
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
        char cambio = (char)fields[9];
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
        printf("%16lx\n", btree_key);

        d.key = btree_key;
        d.value = car.cod;
        // add car in the btree
        BTree_insert(d, &btree);

        // write the car fields into the binFile
        fwrite(&car, sizeof(Carro), 1, binFile);
    }

    fclose(binFile);
    fclose(csvFile);

    deallocate_node(btree.root);

    return 0;
}