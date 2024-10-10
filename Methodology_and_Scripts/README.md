This folder includes the files and information related to data processing stage and populating the full knowldge graph ([see workflow methodology diagram](methodology_workflow.svg)) for the entire state of Victoria, specifically: 

- Python scripts: for creating wb_instances and integrating flood and parcel dataset into it [data_process.py](data_process.py) and populating instances KG for the whole state of Victoria. 

Populated knowledge graphs are too large to store on this server. Instead, they are stored on an external server:
- [Sample size Knowledge Graph (KG) in rdf file format](https://rmiteduau-my.sharepoint.com/:u:/g/personal/nenad_radosevic_rmit_edu_au/EdUZGYQ0uc1Mk6lsCxwxBrMBD8jY1YKY5se8KTXepWrdWA?e=KRTdeg): Current version of populated KG with Victorian foundation hydro, parcel, and flood datasets with 10000 instances (current as of 07.03.2024).
- [Full size Knowledge Grpah (KG) in rdf file format](https://www.dropbox.com/scl/fi/g8eyvn2upfhck31nfe84z/KG240307.rdf?rlkey=1nnao18gsm7dygrdui1q63pir&st=fsiayzir&dl=0): Current version of populated KG with Victorian fondation hydro, parcel, and flood datasets for entire state including all instances (current as of 07.03.2024).
