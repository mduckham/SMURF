This folder includes the files and information related to data processing stage and populating the full knowldge graph ([see workflow methodology diagram](methodology_workflow.svg)) for the entire state of Victoria, specifically: 

- Python scripts: for creating wb_instances and integrating flood and parcel dataset into it [data processing Python script](data_processing_Python_script.py) and populating instances KG for the whole state of Victoria [populating knowledge graph Python script](populating_knowledge_graph_Python_script.py). 

Populated knowledge graphs are too large to store on this server. Instead, they are stored on an external server:
- [Sample size Knowledge Graph (KG) in rdf file format](https://www.dropbox.com/scl/fo/ag7hve7ypkwrbxyluwqw5/AHNvoEvkRIjpw_EMrL10ohk/Knowledge%20graphs?dl=0&preview=KG10K240307.rdf&rlkey=na78ectcgvk9hr0mm6oivdup5&subfolder_nav_tracking=1): Current version of populated KG with Victorian foundation hydro, parcel, and flood datasets with 10000 instances (current as of 07.03.2024).
- [Full size Knowledge Grpah (KG) in rdf file format](https://www.dropbox.com/scl/fi/g8eyvn2upfhck31nfe84z/KG240307.rdf?rlkey=1nnao18gsm7dygrdui1q63pir&st=fsiayzir&dl=0): Current version of populated KG with Victorian fondation hydro, parcel, and flood datasets for entire state including all instances (current as of 07.03.2024).
