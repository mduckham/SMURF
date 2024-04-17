# Graph DB maintenance

This is a fix here to an ontology issue that I applied post the query, to add waterbodyID that was missing:

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX geosparql: <http://www.opengis.net/ont/geosparql#>
PREFIX Ontology_Vicmap: <http://www.semanticweb.org/DV_project#>

INSERT {
	?wb_instance Ontology_Vicmap:waterbodyID ?label .   
} WHERE {
	?wb_instance rdf:type geosparql:Feature . 
    BIND(STRAFTER(STRAFTER(STR(?wb_instance), '#'), 'wb') as ?label).
} 
```
