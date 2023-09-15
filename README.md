# FIPE
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#project-phases">Project Phases</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#requirements">Requirements</a></li>
        <li><a href="#running-from-scratch">Running from scratch</a></li>
        <li><a href="#search-app">Search App</a></li>
        <li><a href="#data-analysis-app">Data Analysis App</a></li>        
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
<a name="about-the-project"></a>
## About The Project
The FIPE project is an outcome of the final assignment for the course INF01124 - Sorting and Searching Data at [INF](https://www.inf.ufrgs.br/site/en), [UFRGS](http://www.ufrgs.br/ufrgs/inicial). This project was undertaken to implement structures of index and data files, as well as explore and create functional applications involving searching and data analysis techniques.

<!-- PROJECT PHASES -->
<a name="#project-phases"></a>
## Project Phases
<ol>
	<li><b>Web Scrapping: </b>The project commenced with the extraction of data from the official <a href=https://fipe.org.br>FIPE</a> website. This involved fetching automotive information such as brands, models, manufacturing years, and prices.</li>
	<li><b>Indexing Structures for the Search Application: </b>
		<ul>
			<li><b>B-Tree Implementation: </b> A B-tree indexing structure was implemented to efficiently organize and access the extracted data. This implementation was used for generate unique codes for each line of the extracted database.</li>
			<li><b>Trie Implementation: </b> Additionally, a Trie-based data structure was developed to support partial string matching. This implementation was used to generate codes for the brands and models.</li>
		</ul>
	</li>
    <li><b>Search Application: </b> This terminal based application provides users the ability to query the datasets using the indexing structures.</li>
    <li><b>Data Analysis Application: </b> This application serves as a tool for exploring and visualizing automotive data. Users can generate graphical representations using a variety of filters, such as brand, model, manufacturing year, type of fuel, type of gear, etc.  
    Note: this app still have planned features (look <a href="#roadmap">roadmap</a>).</li>
</ol>

<!-- GETTING STARTED -->
<a name="#getting-started"></a>
## Getting Started

<!-- REQUIREMENTS -->
<a name="#requirements"></a>
### Requirements
#### For Node.js
1. Install [Node.js](https://nodejs.org/) version 18 or higher.

#### For Python
1. Make sure you have Python installed. If not, you can download it from [here](https://www.python.org/downloads/).
2. Install the required packages using the package manager [pip](https://pip.pypa.io/en/stable/).

   ```bash
   $ pip install pandas mathplotlib pathlib shiny
   
<!-- RUNNING FROM SCRATCH -->
<a name="#running-from-scratch"></a>
### Running from scratch
The following commands were run in 2023, i. e., the data, the database and the binaries files in the repository corresponds to the period from 2004 to 2023.  
If you want to get uploaded data here is short tutorial: 


`NOTE: you must run all executables from repo root`

1) Using `fipe_api.js` to extract data from fipe.org.br
    ```bash
    $ node src/fipe_api.js data/ errors 300 299 298

2) Using `create_database.py` to format extracted data
    ```bash
    $ python src/create_database.py

3) Using `create_binaries.c` to create binary indexing files
    ```bash
    $ make create_binaries  
    $ ./create_binaries
    
<!-- SEARCH APP -->
<a name="#search-app"></a>
### Search App

Compiling `main.c` for database search app

    $ make app
    $ ./app

<!-- DATA ANALYSIS -->
<a name="#data-analysis-app"></a>
### Data Analysis App
This app is hosted on the following website  
TO BE DEFINED

Or, if you want to run locally,

    $ cd src/data_analysis
    $ shiny run --reload


<!-- ROADMAP -->
<a name="roadmap"></a>
## Roadmap
### Data Analisys App
- [x] Refactor hide elements
- [x] Fix first load
- [ ] Refactor max/min tam_motor
- [ ] Add title explanations
- [ ] Add export graphic
- [ ] Implement interactive graphics
- [ ] Implement range of ano_fab 
- [ ] Refactor design
- [ ] Add inflation section
- [ ] Add individual search section

