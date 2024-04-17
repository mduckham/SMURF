#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 16:10:09 2023

@author: mkazemi
"""

### This script provides the GraphDB api, where any query could run over the GraphDB sparql endpoint. 

### GraphDB workbench should be running to establish the localhost connection.

#%%

## repository name in graphDB



from SPARQLWrapper import SPARQLWrapper, JSON

def graphDB_sparql(sparql_query, repository_name):
    
    sparql_query_url = 'http://localhost:7200/repositories/'
    
    repository = repository_name
    
    sparql_endpoint = sparql_query_url + repository


    # sparql_query_url = 'http://localhost:7200/repositories/Dynamic_Vicmap'

    sparql = SPARQLWrapper(sparql_endpoint)

    sparql_query = """{0}""".format(sparql_query)
                    
    
    # Set the SPARQL query
    sparql.setQuery(sparql_query)

    # Set the response format to JSON
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    
    return results



## Example: graphDB_sparql(sample_query, 'Dynamic_Vicmap')

#### sample sparql_query

# sample_query = 
#         """
# PREFIX onto: <http://www.ontotext.com/>
# prefix Ontology_Vicmap:<http://www.semanticweb.org/mkazemi/ontologies/2023/9/Ontology_Vicmap2#>
# prefix dcam:<http://purl.org/dc/dcam/>
# prefix dcat:<http://www.w3.org/ns/dcat#>
# prefix dcterms:<http://purl.org/dc/terms/>
# prefix dqv:<http://www.w3.org/ns/dqv#>
# prefix fsdf:<https://linked.data.gov.au/def/fsdf/>
# prefix geosparql:<http://www.opengis.net/ont/geosparql#>
# prefix ns:<http://www.w3.org/2006/vcard/ns#>
# prefix owl:<http://www.w3.org/2002/07/owl#>
# prefix prov:<http://www.w3.org/ns/prov#>
# prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# prefix rdfs:<http://www.w3.org/2000/01/rdf-schema#>
# prefix skos:<http://www.w3.org/2004/02/skos/core#>
# prefix terms:<http://purl.org/dc/terms/#>
# prefix vann:<http://purl.org/vocab/vann/>


# SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
#  	?pfi ?createdate
#  	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
 	

# WHERE {?wb_instance rdf:type geosparql:Feature;
# 				geosparql:hasGeometry ?geometry.
  
#             ?geometry rdf:type geosparql:Geometry ;
#                 Ontology_Vicmap:hasPFI ?pfi;
#                 Ontology_Vicmap:createDate ?createdate.

#     {
# SELECT ?wb_instance

# 		WHERE {?wb_instance rdf:type geosparql:Feature;
# 				geosparql:hasGeometry ?geometry1.
            
#             ?geometry1 rdf:type geosparql:Geometry ;
#                 Ontology_Vicmap:geometryCoordinates ?coord1.
            
#      		 FILTER (regex(str(?coord1), "POLYGON", "i"))
    
#  			?wb_instance  geosparql:hasGeometry ?geometry2.
#    			?geometry2 rdf:type geosparql:Geometry ;
#                 Ontology_Vicmap:geometryCoordinates ?coord2.

#  			FILTER (regex(str(?coord2), "POINT", "i"))}
# GROUP BY ?wb_instance
# HAVING (COUNT(DISTINCT ?geometry1) >= 1 && COUNT(DISTINCT ?geometry2) >= 1)
#     }
# }

# LIMIT 100

# """

