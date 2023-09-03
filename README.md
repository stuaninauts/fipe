# FIPE
FIPE

## Running
Using `fipe_api.js` to extract data from fipe.org.br
```
user@pc:~/fipe$ node src/fipe_api.js data/ errors 300 299 298
```


Using `create_database.py` to format extracted data
```
user@pc:~/fipe$ python src/create_database.py
```


Using `create_binaries.c` to create binary indexing files
```
user@pc:~/fipe$ make create_binaries
user@pc:~/fipe$ ./create_binaries
```


Compiling `main.c` for database search app
```
user@pc:~/fipe$ make app
user@pc:~/fipe$ ./app
```

`NOTE: you must run all executables from repo root`

## Requirements
```
- Node.js v18

# Python packages
- pandas
- shiny
```
