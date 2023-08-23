#include "entities.h"
#include <stdio.h>


int main(void) {

    Marca bmw;
    Modelo i116;
    Carro cum;

    printf("%ld %ld %ld\n", sizeof(bmw), sizeof(i116), sizeof(cum));

    return 0;
}