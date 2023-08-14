#ifndef ENTITIES_H
#define ENTITIES_H

#define STR_MAX 64

typedef enum {
    JAN = 1,
    FEV,
    MAR,
    ABR,
    MAI,
    JUN,
    JUL,
    AGO,
    SET,
    OUT,
    NOV,
    DEZ
} Mes;

typedef enum {
    GASOLINA = 1,
    ALCOOL,
    DIESEL
} Combustivel;

typedef enum {
    AUTOMATICO = 1,
    MANUAL
} Cambio;

typedef struct {
    int id;
    char nome[STR_MAX];
} Marca;

typedef struct {
    int id;
    char nome[STR_MAX];
    int id_marca;
} Modelo;

typedef struct {
    int id;
    int ano_ref;
    Mes mes_ref;
    int id_marca;
    int id_modelo;
    int ano_fab;
    Combustivel combustivel;
    int cod_fipe;
    Cambio cambio;
    float tam_motor;
} Carro;

#endif