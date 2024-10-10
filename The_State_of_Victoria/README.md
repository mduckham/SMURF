This folder includes the files and information for the state-level tests, specifically: 


Other files inside the folder include:
- [Ontology](../Ontology/) folder: Includes the list of standard ontology used in this work. The core DynamicVicmap ontology created for this project is [smurf.ttl](../Ontology/smurf.ttl).
- Data: List of datasets integrated in to the KG (please refer to the [Readme.md](../README.md) for downloading them) and [metadata](../Vicmap_Metadata/) info for Vicmap datasets.
- Python scripts: for creating wb_instances and integrating flood and parcel dataset into it [data_process.py](data_process.py) and populating instances KG for the whole state of Victoria. 


Populated knowledge graphs are too large to store on this server. Instead, they are stored on the internal Teams site:
- [KG10K.rdf](https://rmiteduau-my.sharepoint.com/:u:/g/personal/nenad_radosevic_rmit_edu_au/EdUZGYQ0uc1Mk6lsCxwxBrMBD8jY1YKY5se8KTXepWrdWA?e=KRTdeg): Current version of populated KG with hydro, parcel, and flood datasets for 10K instances (current as of 24.02.13).
- [KG.rdf](https://rmiteduau-my.sharepoint.com/:u:/g/personal/nenad_radosevic_rmit_edu_au/EcOcZhCXLlBIgfnzCRyXjUwBeugUS4LbCdXmQ99mNxlPdg?e=0GXDl1): Current version of populated KG with hydro, parcel, and flood datasets for entire state (current as of 24.02.13).
