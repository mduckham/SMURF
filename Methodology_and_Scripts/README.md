This folder includes the files and information related to data processing stage and populating the full knowldge graph ([see workflow methodology diagram](methodology_workflow.svg)) for the entire state of Victoria, specifically: 

- Python scripts: for creating wb_instances and integrating flood and parcel dataset into it [data processing Python script](data_processing_Python_script.py) and populating instances KG for the whole state of Victoria [populating knowledge graph Python script](populating_knowledge_graph_Python_script.py). 

Populated knowledge graphs are too large to store on this server. Instead, they are stored on an external server:
- [Sample size Knowledge Graph (KG) in rdf file format](https://teams.microsoft.com/l/message/19:49910444-7427-4758-a84d-5b25d4f6f934_4bb86b96-3ed8-46f0-b5ba-b242c842e583@unq.gbl.spaces/1729215098087?context=%7B%22contextType%22%3A%22chat%22%7D): Current version of populated KG with Victorian foundation hydro, parcel, and flood datasets with 10000 instances (current as of 07.03.2024).
- [Full size Knowledge Grpah (KG) in rdf file format](https://www.dropbox.com/scl/fi/g8eyvn2upfhck31nfe84z/KG240307.rdf?rlkey=1nnao18gsm7dygrdui1q63pir&st=fsiayzir&dl=0): Current version of populated KG with Victorian fondation hydro, parcel, and flood datasets for entire state including all instances (current as of 07.03.2024).
