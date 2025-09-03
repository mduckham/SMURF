# Competency questions and queries

## Preliminaries

The following queries assume this preamble. Note that in the latest version of [the web query visualisation board](https://github.com/mduckham/DynamicVicmap/blob/main/VisualisationDashboard/vicmap_main_050324.html) HTML file this preamble is hard-coded into this file. 

```
PREFIX onto: <http://www.ontotext.com/>
PREFIX smurf:<http://geosensor.net/SMURF#>
PREFIX dcam:<http://purl.org/dc/dcam/>
PREFIX dcat:<http://www.w3.org/ns/dcat#>
PREFIX dqv:<http://www.w3.org/ns/dqv#>
PREFIX fsdf:<https://linked.data.gov.au/def/fsdf/>
PREFIX geosparql:<http://www.opengis.net/ont/geosparql#>
PREFIX ns:<http://www.w3.org/2006/vcard/ns#>
PREFIX owl:<http://www.w3.org/2002/07/owl#>
PREFIX prov:<http://www.w3.org/ns/prov#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms:<http://purl.org/dc/terms/#>
PREFIX vann:<http://purl.org/vocab/vann/>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX sf: <http://www.opengis.net/ont/sf#>
PREFIX ext: <http://rdf.useekm.com/ext#>


```
## Multiple geometry representations
### Examples of competency questions and queries:

1) Which water features have multiple geometric representations?
```
PREFIX smurf:<http://geosensor.net/SMURF#>
PREFIX geosparql: <http://www.opengis.net/ont/geosparql#>
PREFIX sf: <http://www.opengis.net/ont/sf#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?pfi ?ufi ?ftype ?auxname WHERE {
    ?wb_instance geosparql:hasGeometry ?geometry ;        # identify instances 
        smurf:waterbodyID ?ID .                           # water body ID 
    ?geometry rdf:type geosparql:Geometry ;               # geometry 
        smurf:hasPFI ?pfi ;                               # persistent identifier 
        smurf:hasUFI ?ufi ;                               # unique identifier 
        smurf:varietyOf ?ftype ;                          # feature type 
        smurf:hasGeometryProvenance ?geomprov .           # geometry provenance
    ?geomprov dcterms:title ?auxname .
    {
    SELECT ?wb_instance WHERE {                           # nested SELECT
        ?wb_instance geosparql:hasGeometry ?geometry1 .   # geometry
        ?geometry1 rdf:type sf:Polygon .                  # Identify polygon
        ?wb_instance geosparql:hasGeometry ?geometry2 .   # geometry
        ?geometry2 rdf:type sf:Point .                    # Identify point
    }
    GROUP BY ?wb_instance                                 # then filter to
    HAVING (COUNT(DISTINCT ?geometry1) >= 1 &&            # features with
    COUNT(DISTINCT ?geometry2) >= 1)                      # both representations
    }
}

```
## Temporal changes
### Examples of competency questions and queries:
1) Which water features have increased in area in the last three years?   
```
PREFIX smurf:<http://geosensor.net/SMURF#>
PREFIX geosparql: <http://www.opengis.net/ont/geosparql#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ext: <http://rdf.useekm.com/ext#>
PREFIX sf: <http://www.opengis.net/ont/sf#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?ID ?pfi ?ufi ?ftype ?date ?areaOld ?areaNew ?auxname WHERE {
    ?wb_instance geosparql:hasGeometry ?geometry ;  # identify instances
        smurf:waterbodyID ?ID .                     # water body ID
    ?geometry rdf:type geosparql:Geometry;          # geometry 
        smurf:hasPFI ?pfi;                          # persistent identifier 
        smurf:hasUFI ?ufi;                          # unique identifier 
        smurf:varietyOf ?ftype;                     # feature type
        smurf:createDate ?date;                     # creation date
        smurf:hasGeometryProvenance ?geomprov.      # geometry provenance
    ?geomprov dcterms:title ?auxname.
    {
        SELECT DISTINCT ?wb_instance ?geometry1 ?geometry2 # nested SELECT
            (ext:area(?coord1) AS ?areaOld)         #calculate old area
            (ext:area(?coord2) AS ?areaNew)         #calculate new area
        WHERE {
            ?wb_instance geosparql:hasGeometry ?geometry1, ?geometry2.
            ?geometry1 rdf:type sf:Polygon;         # geometry1 older polygon
                smurf:geometryCoordinates ?coord1;  # linked geometry
                smurf:createDate ?date1.            # previous date
            ?geometry2 rdf:type sf:Polygon;         # geometry2 newer polygon
                smurf:geometryCoordinates ?coord2;  # linked geometry
                smurf:createDate ?date2.            # latest date
            FILTER(?date2 > ?date1)     # geometry2 is newer than geometry1
            BIND(NOW() - "P3Y"^^xsd:duration AS ?threeYearsAgoDT) # only  
            BIND(xsd:date(?threeYearsAgoDT) AS ?threeYearsAgo)  # geometry2
            FILTER(?date2 >= ?threeYearsAgo)          # within last 3 years
            FILTER(ext:area(?coord2) > ext:area(?coord1)) # Compare areas
        }                                                 
    }
}
```
## Provenance
### Examples of competency questions and queries:
1) What is the geometry provenance (information about source organization and data set) for a specified water feature?
```
PREFIX smurf:<http://geosensor.net/SMURF#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX geosparql:<http://www.opengis.net/ont/geosparql#>
PREFIX dcterms:<http://purl.org/dc/terms/>

SELECT ?pfi ?ufi ?createdate ?ftype ?auxname ?auxcontent WHERE {
	?wb_instance geosparql:hasGeometry ?geometry.	 # Identify instances ...
	?geometry rdf:type geosparql:Geometry;				 # ... geometry ...
		smurf:hasPFI ?pfi;									 # ... persistent identifier ...
		smurf:hasUFI ?ufi;									 # ... unique identifier...
		smurf:varietyOf ?ftype;								 # ... feature type ...
		smurf:createDate ?createdate;					 # ... create date ...  
		smurf:hasGeometryProvenance ?geomprov.		 # ... geometry provenance
	?geomprov dcterms:title ?auxname;				 # with the source name ...
		dcterms:source ?auxcontent.					 # .. and data source details
}
```

1) Can you show multiple geometry representations (point and polygon) for Vicmap authoritative waterbodies located within the City of Greater Shepparton?

   Description: this query retrieves waterbody features that are represented with point and polygon geometries in the current Vicmap Hydro data within the area of the City 
   of Greater Shepparton.
    
```
SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype  ?auxname ?auxcontent
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.

            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
              Ontology_Vicmap:hasGeometryProvenance ?geomprov.
	?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.

FILTER (geof:sfWithin(?geometry_coord, "POLYGON((145.032058 -36.343090, 145.150231 -36.343084, 145.150231 -36.343083, 145.150308 -36.284392, 145.150307 -36.284348, 145.150283 -36.284349, 145.131988 -36.284356, 145.131073 -36.170390, 145.130192 -36.161124, 145.132911 -36.155703, 145.137933 -36.154046, 145.166095 -36.161216, 145.176495 -36.181708, 145.193563 -36.178754, 145.189618 -36.164996, 145.198282 -36.157349, 145.208466 -36.167835, 145.212065 -36.158681, 145.214766 -36.159459, 145.212886 -36.162004, 145.217071 -36.165580, 145.235037 -36.170385, 145.239318 -36.171414, 145.260251 -36.199324, 145.631524 -36.199162, 145.631610 -36.299028, 145.798547 -36.299046, 145.798574 -36.299129, 145.798545 -36.330836, 145.798551 -36.330886, 145.798536 -36.330943, 145.775434 -36.443754, 145.771200 -36.444566, 145.724422 -36.424686, 145.724203 -36.434462, 145.731320 -36.442633, 145.731870 -36.499036, 145.631571 -36.499055, 145.631718 -36.563301, 145.591998 -36.563294, 145.578453 -36.555962, 145.578453 -36.555962, 145.353584 -36.556104, 145.318913 -36.612402, 145.318913 -36.612402, 145.302517 -36.641941, 145.228699 -36.641971, 145.228699 -36.641971, 145.228662 -36.646751, 145.205034 -36.654791, 145.203865 -36.661406, 145.211554 -36.663084, 145.216047 -36.669569, 145.220951 -36.669533, 145.222125 -36.671098, 145.223444 -36.685701, 145.221213 -36.687334, 145.185171 -36.686333, 145.182115 -36.690479, 145.184051 -36.696257, 145.179831 -36.701167, 145.178447 -36.700559, 145.172122 -36.697288, 145.177802 -36.689983, 145.168645 -36.690069, 145.168645 -36.690069, 145.168536 -36.675298, 145.131713 -36.675452, 145.131715 -36.675359, 145.131745 -36.587338, 145.131857 -36.587338, 145.150006 -36.587200, 145.149761 -36.498989, 145.031969 -36.498980, 145.032058 -36.343090))")) 
 
Filter( ?auxname not in ('HY_WATER_AREA_ML'))
    {
SELECT ?wb_instance
	    WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry1.
            ?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord1;
                Ontology_Vicmap:hasGeometryProvenance ?prov.
            ?prov dcterms:title 'Vicmap Hydro - Water Polygon'.

#     		 FILTER (regex(str(?coord1), "POLYGON", "i"))
			?wb_instance  geosparql:hasGeometry ?geometry2.
  			?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord2;
                Ontology_Vicmap:hasGeometryProvenance ?prov2.
            ?prov2 dcterms:title 'Vicmap Hydro - Water Point'.
        }
# 			FILTER (regex(str(?coord2), "POINT", "i"))}
GROUP BY ?wb_instance
HAVING (COUNT(DISTINCT ?geometry1) >= 1 && COUNT(DISTINCT ?geometry2) >= 1)
    }
}

```

2) Can you show machine learned (ML) waterbodies extracted from satellite imagery?

   Description: this query retrieves on the web map machine learned (ML) waterbody features that are extracted from satellite imagery. ML data set was integrated with Vicmap 
   Hydro data (polygon and point) into the Dynamic Vicmap knowledge graph. The execution and visualization of query results takes around 5 seconds for this query.

```
SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.
            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
              ?geomprov dcterms:title ?auxname;
		dcterms:spatial ?qm.
?qm dcat:bbox  ?auxcontent.
            Filter( ?auxname = 'HY_WATER_AREA_ML')
}

```

3) Can you show multiple geometry representations (point and polygon) of waterbodies included in both Vicmap Hydro and machine learned (ML) data sets?

   Description: this query retrieves waterbody features which have multiple three different geometry representations: Vicmap Hydro polygon geometry, Vicmap Hydro point 
   geometry, ML polygon geometry. In particular, the query demonstrates how multiple versions can be integrated and related to one waterbody feature. The execution and 
   visualization of query results takes around 4 seconds for this query.

```
SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.

            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
    {
SELECT ?wb_instance

	    WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry1.
            ?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord1;
                Ontology_Vicmap:hasGeometryProvenance ?prov.
            ?prov dcterms:title ?dataset.
          
            FILTER (?dataset = 'Vicmap Hydro - Water Polygon').
#     		 FILTER (regex(str(?coord1), "POLYGON", "i"))
			?wb_instance  geosparql:hasGeometry ?geometry2.
  			?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord2;
                Ontology_Vicmap:hasGeometryProvenance ?prov2.
            ?prov2 dcterms:title 'Vicmap Hydro - Water Point'.
            
            ?wb_instance  geosparql:hasGeometry ?geometry3.
  			?geometry3 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord3;
                Ontology_Vicmap:hasGeometryProvenance ?prov3.
            ?prov3 dcterms:title 'HY_WATER_AREA_ML'.
        }
# 			FILTER (regex(str(?coord2), "POINT", "i"))}
GROUP BY ?wb_instance
HAVING (COUNT(DISTINCT ?geometry1) >= 1 && COUNT(DISTINCT ?geometry2) >= 1 &&  COUNT(DISTINCT ?geometry3) >= 1)
    }
}

```

4) Can you display waterbody lakes that are on the Vicmap crown land parcel that has specific permanent feature identifier (PFI) with number 52490156?

   Description: this query retrieves waterbody lakes within a specific Vicmap property with the PFI specified in the question. It shows multiple waterbody lakes on one 
   parcel that belongs to the crown land. The execution and visualization of this query takes around 2.5 minutes. Computational time for the query execution is delayed due 
   to a limitation associated with use of free version of commercial GraphDB software for the Dynamic Vicmap prototype. 

```
select ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
where {
    {
        ?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry1.
    	?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:isCrown True;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasUFI ?ufi;
				Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
        
		?geomprov dcterms:title ?auxname;
			dcterms:source ?auxcontent.
    
    Filter (?pfi = '52490156'^^xsd:int)
        }
union
    {
select   ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
where 
{
        ?wb_instance rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry2.
        ?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
        
		?geomprov dcterms:title ?auxname;
			dcterms:source ?auxcontent.
    
    FILTER(?ftype in ('wb_lake'))
    
		?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry1.
    	?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:isCrown True;
                Ontology_Vicmap:hasPFI ?pfi1;
                Ontology_Vicmap:geometryCoordinates ?parcelCoord.
    
    Filter (?pfi1 = '52490156'^^xsd:int)
    Filter (geof:sfIntersects(?geometry_coord, ?parcelCoord))
    }
    
    }
} 

```

5) Can you retrieve and display all Vicmap crown land parcels in the state of Victoria?

   Description: this query retrieves Vicmap properties (parcels) that are within the local government area of the City of Greater Shepparton. The query result shows only 
   Vicmap parcels that belongs to the crown land. The execution and visualization of query results takes around 8 seconds for this query.

```
SELECT ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent

WHERE  
    {
    ?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry2.
        ?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
                Ontology_Vicmap:isCrown true;
				Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
             Ontology_Vicmap:hasGeometryProvenance ?geomprov.
               ?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
    }

```

6) In 2022 what properties were affected by flood in Kerang, a town in northern Victoria?

   Description: this query retrieves information about parcels affected with flooding in Kerang, a town in northern Victoria. The query is 
   executed over Vicmap Property and Vicmap Flood authoritative data sets. The execution and visualization of this query takes around 10-15 seconds.

```
SELECT ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent

WHERE  
    {
    ?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry2.
        ?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
				Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
             Ontology_Vicmap:hasGeometryProvenance ?geomprov.
               ?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
Filter(?auxname != 'Vicmap Hydro - Water Point')
Filter(?auxname != 'Vicmap Hydro - Water Polygon')
Filter(?auxname != 'Flood_NonAuthoritative_25Jan')
Filter(?auxname != 'Flood_Authoritative')

FILTER (geof:sfWithin(?geometry_coord, "POLYGON((143.861473 -35.694010, 143.863302 -35.693154, 143.863625 -35.694772 ,143.865111 -35.693599, 143.868487 -35.692789, 143.879680 -35.701755, 143.879256	-35.699321, 143.893690 -35.699268, 143.894771 -35.700120, 143.894809 -35.702253, 143.896057	-35.702359, 143.897258 -35.695757, 143.899397 -35.696007, 143.903500 -35.698331, 143.910672	-35.694517, 143.911588 -35.689293, 143.907033 -35.688755, 143.904027 -35.687648, 143.908112	-35.661410, 143.909934 -35.661043, 143.920925 -35.664710, 143.943531 -35.664455, 143.945423	-35.658629, 143.959328 -35.659006, 143.965710 -35.658936, 143.967868 -35.659912, 143.967865	-35.661578, 143.982797 -35.661881, 143.987628 -35.669208, 143.999111 -35.674224, 144.002610	-35.681418, 143.987880 -35.685882, 143.997774 -35.699993, 143.998473 -35.711322, 144.002628	-35.711846, 144.007664 -35.708755, 144.013797 -35.714936, 144.010661 -35.714858, 144.010662	-35.724925, 144.003949 -35.725081, 144.004034 -35.733504, 144.006708 -35.733508, 144.006716	-35.736155, 144.019024 -35.736179, 144.022083 -35.735500, 144.025759 -35.735703, 144.027005	-35.737340, 144.027519 -35.740819, 144.029287 -35.741221, 144.032602 -35.739462, 144.033968	-35.747939, 144.032380 -35.747928, 144.032389 -35.754407, 144.027532 -35.754398, 144.027111	-35.756719, 144.023377 -35.756708, 144.023374 -35.758042, 144.008865 -35.757999, 144.008853	-35.762281, 143.999255 -35.762268, 143.999256 -35.757879, 143.996595 -35.757879, 143.996595	-35.756327, 143.992599 -35.756341, 143.992602 -35.760214, 143.990828 -35.760224, 143.990803	-35.769395, 143.964714 -35.772341, 143.957625 -35.772782, 143.953921 -35.769736, 143.952537	-35.760266, 143.950802 -35.755338, 143.952556 -35.741010, 143.949807 -35.741747, 143.948684	-35.745949, 143.945427 -35.745845, 143.938708 -35.720096, 143.928043 -35.720118, 143.932683	-35.715179, 143.930094 -35.713923, 143.922748 -35.717983, 143.914457 -35.718184, 143.914016	-35.720101, 143.908618 -35.720053, 143.909064 -35.728561, 143.907775 -35.729724, 143.916979	-35.738347, 143.919609 -35.744687, 143.919913 -35.747171, 143.918283 -35.747785, 143.915783	-35.746509, 143.912477 -35.749478, 143.912897 -35.752774, 143.920460 -35.762702, 143.951322	-35.763411, 143.950845 -35.767874, 143.937910 -35.769081, 143.940613 -35.789540, 143.916814	-35.789555, 143.914592 -35.786327, 143.902472 -35.785802, 143.895367 -35.771289, 143.905778	-35.763196, 143.892344 -35.751075, 143.891593 -35.735211, 143.885287 -35.735219, 143.881957	-35.728681, 143.881049 -35.721331, 143.870647 -35.722067, 143.869162 -35.699190, 143.864321	-35.699359, 143.867144 -35.704666, 143.867840 -35.712330, 143.863981 -35.712908, 143.863915	-35.696026, 143.861356 -35.695927, 143.861473 -35.694010, 143.861473 -35.694010))"))
    }

```

7) What parcels were affected by flood in the City of Greater Shepparton in 2022?
 
   Description: this query retrieves information about parcels affected with flooding in the City of Greater Shepparton in 2022. The query is 
   executed over Vicmap Property and Vicmap Flood authoritative data sets. The execution and visualization of this query takes around 10-15 seconds.
   
```
SELECT ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent

WHERE  
    {
    ?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry2.
        ?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
				Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
             Ontology_Vicmap:hasGeometryProvenance ?geomprov.
               ?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.

Filter(?auxname != 'Vicmap Hydro - Water Point')
Filter(?auxname != 'Vicmap Hydro - Water Polygon')
Filter(?auxname != 'Flood_NonAuthoritative_25Jan')
Filter(?auxname != 'Flood_Authoritative')

			FILTER (geof:sfWithin(?geometry_coord, "POLYGON((145.4668467 -36.22303826, 145.3669737-36.20005209, 145.3669069 -36.19952816, 145.3668658 -36.19920535, 145.3674758 -36.19920557, 145.4569918 -36.20763745, 145.4536533 -36.22937994, 145.4442391 -36.19920793, 145.4668467 -36.22303826))") || geof:sfWithin(?geometry_coord, "POLYGON((145.4668467, -36.22303826, 145.3669737 -36.20005209, 145.3669069 -36.19952816, 145.3668658 36.19920535, 145.3674758 -36.19920557, 145.4569918 -36.20763745, 145.4536533 -36.22937994, 145.4442391 -36.19920793, 145.4668467 -36.22303826))") || geof:sfWithin(?geometry_coord, "POLYGON((145.1733296 -36.69556836, 145.3468007 -36.4154961, 145.456686 -36.24958319, 145.390706 -36.21549505, 145.2275778 -36.15859706, 145.2626446 -36.19930299, 145.3373289 -36.20004659, 145.1367485 -36.21200745, 145.1379392 -36.15403241, 145.1683665 -36.60622119, 145.5091272 -36.35645314, 145.7772863 -36.43350283, 145.6961504 -36.42983847, 145.7129652 -36.40136049, 145.7489735 -36.39772207, 145.253235 -36.45464879, 145.686325 -36.48722558, 145.43173 -36.477583, 145.1733296 -36.69556836))"))
    }

```

8) What is source information for retrieved Vicmap parcels located within the City of Greater Shepparton?

   Description: the query retrieves metadata and provenance information for spatial features included in the Dynamic Vicmap knowledge graph that integrates Vicmap Hydro, 
   Vicmap Property, Machine Learned, LiDAR, and Flood data sets.

```
SELECT ?pfi ?createdate ?ftype ?ufi ?geometry_coord ?auxname ?auxcontent
WHERE  {
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry.
	?geometry rdf:type geosparql:Geometry ;
		Ontology_Vicmap:hasPFI ?pfi;
		Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
		Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:hasGeometryProvenance ?geomprov;
		Ontology_Vicmap:geometryCoordinates ?geometry_coord.   
	?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
Filter(?auxname != 'Vicmap Hydro - Water Point')
Filter(?auxname != 'Vicmap Hydro - Water Polygon')
Filter(?auxname != 'Flood_NonAuthoritative_25Jan')
Filter(?auxname != 'Flood_Authoritative')

FILTER (geof:sfWithin(?geometry_coord, "POLYGON((145.032058 -36.343090, 145.150231 -36.343084, 145.150231 -36.343083, 145.150308 -36.284392, 145.150307 -36.284348, 145.150283 -36.284349, 145.131988 -36.284356, 145.131073 -36.170390, 145.130192 -36.161124, 145.132911 -36.155703, 145.137933 -36.154046, 145.166095 -36.161216, 145.176495 -36.181708, 145.193563 -36.178754, 145.189618 -36.164996, 145.198282 -36.157349, 145.208466 -36.167835, 145.212065 -36.158681, 145.214766 -36.159459, 145.212886 -36.162004, 145.217071 -36.165580, 145.235037 -36.170385, 145.239318 -36.171414, 145.260251 -36.199324, 145.631524 -36.199162, 145.631610 -36.299028, 145.798547 -36.299046, 145.798574 -36.299129, 145.798545 -36.330836, 145.798551 -36.330886, 145.798536 -36.330943, 145.775434 -36.443754, 145.771200 -36.444566, 145.724422 -36.424686, 145.724203 -36.434462, 145.731320 -36.442633, 145.731870 -36.499036, 145.631571 -36.499055, 145.631718 -36.563301, 145.591998 -36.563294, 145.578453 -36.555962, 145.578453 -36.555962, 145.353584 -36.556104, 145.318913 -36.612402, 145.318913 -36.612402, 145.302517 -36.641941, 145.228699 -36.641971, 145.228699 -36.641971, 145.228662 -36.646751, 145.205034 -36.654791, 145.203865 -36.661406, 145.211554 -36.663084, 145.216047 -36.669569, 145.220951 -36.669533, 145.222125 -36.671098, 145.223444 -36.685701, 145.221213 -36.687334, 145.185171 -36.686333, 145.182115 -36.690479, 145.184051 -36.696257, 145.179831 -36.701167, 145.178447 -36.700559, 145.172122 -36.697288, 145.177802 -36.689983, 145.168645 -36.690069, 145.168645 -36.690069, 145.168536 -36.675298, 145.131713 -36.675452, 145.131715 -36.675359, 145.131745 -36.587338, 145.131857 -36.587338, 145.150006 -36.587200, 145.149761 -36.498989, 145.031969 -36.498980, 145.032058 -36.343090))")) 

}

```

9) Can you identify waterbodies that have been developed on the Vicmap crown land parcel with PFI = 131398958 in the last year?

   Description: this query retrieves information about new waterbodies within a particular Vicmap parcel with the permanent feature identifier (PFI) 131398958 that belongs 
   to the crown land. The query uses date (timestamp) to retrieve all waterbodies that have been developed in the last year. It is executed over Vicmap Hydro and Vicmap 
   Property data sets. The execution and visualization of this query takes around 15 seconds.  

```

select ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
where {
    {
        ?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry1.
    	?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:isCrown True;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasUFI ?ufi;
				Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
        
		?geomprov dcterms:title ?auxname;
			dcterms:source ?auxcontent.
    
    Filter (?pfi = '131398958'^^xsd:int)
        }
union
    {
select   ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
where 
{
        ?wb_instance rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry2.
        ?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
        
		?geomprov dcterms:title ?auxname;
			dcterms:source ?auxcontent.
    
    FILTER(?ftype in ('wb_lake') &&
        xsd:date(?createdate) > "2023-02-22"^^xsd:date)
    
		?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry1.
    	?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:isCrown True;
                Ontology_Vicmap:hasPFI ?pfi1;
                Ontology_Vicmap:geometryCoordinates ?parcelCoord.
    
    Filter (?pfi1 = '131398958'^^xsd:int)

    Filter (geof:sfIntersects(?geometry_coord, ?parcelCoord))
    }
    
    }
}

```

10) By using new machine learned (ML) data can you identify waterbodies (farm dams, reservoirs, etc) that have increased in their size in the last year?

    Description: this query retrieves waterbodies that have been increased in their size by comparing waterbody area size between Vicmap Hydro Water Polygon and machine 
    learned waterbody polygon data. It shows waterbodies for which ML polygon representation has larger area size than Vicmap Hydro Water polygon representation. The 
    execution and visualization of this query takes around 3 minutes. Computational time for the query execution is delayed due to a limitation associated with use of free 
    version of commercial GraphDB software for the Dynamic Vicmap prototype.

```

SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.

            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
    
    Filter(?auxname != 'HY_WATER_AREA_LIDAR')
   
    {
SELECT ?wb_instance

	    WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry1.
            ?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord1;
                Ontology_Vicmap:hasGeometryProvenance ?prov.
            ?prov dcterms:title ?dataset.
          
            FILTER (?dataset = 'Vicmap Hydro - Water Polygon').
            
			?wb_instance  geosparql:hasGeometry ?geometry2.
  			?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord2;
                Ontology_Vicmap:hasGeometryProvenance ?prov2.
            ?prov2 dcterms:title 'HY_WATER_AREA_ML'.
           
            Filter(ext:area(?coord2) > ext:area(?coord1))
        }
GROUP BY ?wb_instance
HAVING (COUNT(DISTINCT ?geometry1) >= 1 && COUNT(DISTINCT ?geometry2) >= 1 )
    }
}

```

11) By using LiDAR captured data can you identify the waterbodies (farm dams, reservoirs, etc) that have increased in their size in last 5 years?

    Description: this query retrieves waterbodies that have been increased in their size by comparing waterbody area size between Vicmap Hydro Water Polygon and LiDAR 
    captured waterbody polygon data. It shows waterbodies for which LiDAR polygon representation has larger area size than Vicmap Hydro Water polygon representation. The 
    execution and visualization of this query takes around 3.5 minutes. Computational time for the query execution is delayed due to a limitation associated with use of free 
    version of commercial GraphDB software for the Dynamic Vicmap prototype.

```
SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.

            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
    
    Filter(?auxname != 'HY_WATER_AREA_ML')
   
    {
SELECT ?wb_instance

	    WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry1.
            ?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord1;
                Ontology_Vicmap:hasGeometryProvenance ?prov.
            ?prov dcterms:title ?dataset.
          
            FILTER (?dataset = 'Vicmap Hydro - Water Polygon').
            
			?wb_instance  geosparql:hasGeometry ?geometry2.
  			?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord2;
                Ontology_Vicmap:hasGeometryProvenance ?prov2.
            ?prov2 dcterms:title 'HY_WATER_AREA_LIDAR'.
           
            Filter(ext:area(?coord2) > ext:area(?coord1))
        }
GROUP BY ?wb_instance
HAVING (COUNT(DISTINCT ?geometry1) >= 1 && COUNT(DISTINCT ?geometry2) >= 1 )
    }
} 

```
12) Can you show multiple geometry representations (point and polygon) for Vicmap authoritative waterbodies?

```
SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype  ?auxname ?auxcontent
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.

            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
              Ontology_Vicmap:hasGeometryProvenance ?geomprov.
	?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.

Filter( ?auxname not in ('HY_WATER_AREA_ML'))

    {
SELECT ?wb_instance
	    WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry1.
            ?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord1;
                Ontology_Vicmap:hasGeometryProvenance ?prov.
            ?prov dcterms:title 'Vicmap Hydro - Water Polygon'.

#     		 FILTER (regex(str(?coord1), "POLYGON", "i"))
			?wb_instance  geosparql:hasGeometry ?geometry2.
  			?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord2;
                Ontology_Vicmap:hasGeometryProvenance ?prov2.
            ?prov2 dcterms:title 'Vicmap Hydro - Water Point'.
        }
# 			FILTER (regex(str(?coord2), "POINT", "i"))}
GROUP BY ?wb_instance
HAVING (COUNT(DISTINCT ?geometry1) >= 1 && COUNT(DISTINCT ?geometry2) >= 1)
    }
}
LIMIT 100
```

13) Can you show machine learned (ML) waterbodies extracted from satellite imagery?

```
SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.
            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
              ?geomprov dcterms:title ?auxname;
		dcterms:spatial ?qm.
?qm dcat:bbox  ?auxcontent.
            Filter( ?auxname = 'HY_WATER_AREA_ML')
}
```

14) Can you show multiple geometry representations (point and polygon) of waterbodies included in both Vicmap Hydro and ML data sets?

```
SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.

            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
    {
SELECT ?wb_instance

	    WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry1.
            ?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord1;
                Ontology_Vicmap:hasGeometryProvenance ?prov.
            ?prov dcterms:title ?dataset.
          
            FILTER (?dataset = 'Vicmap Hydro - Water Polygon').
#     		 FILTER (regex(str(?coord1), "POLYGON", "i"))
			?wb_instance  geosparql:hasGeometry ?geometry2.
  			?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord2;
                Ontology_Vicmap:hasGeometryProvenance ?prov2.
            ?prov2 dcterms:title 'Vicmap Hydro - Water Point'.
            
            ?wb_instance  geosparql:hasGeometry ?geometry3.
  			?geometry3 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord3;
                Ontology_Vicmap:hasGeometryProvenance ?prov3.
            ?prov3 dcterms:title 'HY_WATER_AREA_ML'.
        }
# 			FILTER (regex(str(?coord2), "POINT", "i"))}
GROUP BY ?wb_instance
HAVING (COUNT(DISTINCT ?geometry1) >= 1 && COUNT(DISTINCT ?geometry2) >= 1 &&  COUNT(DISTINCT ?geometry3) >= 1)
    }
}
```

15) Can you display waterbody lakes that are on the Vicmap crown land parcel with specific PFI = 52490156?

```
SELECT 
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent

WHERE  {
		?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry1.
        ?geometry1 Ontology_Vicmap:hasPFI '52490156'^^xsd:int;
                  Ontology_Vicmap:isCrown true;
                  Ontology_Vicmap:geometryCoordinates ?parcelCoord.
       
        ?wb_instance rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry2.
        ?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
    Filter (?ftype IN ('wb_lake'))
    Filter (geof:sfWithin(?geometry_coord, ?parcelCoord)).
}

```
 16) Can you display all Vicmap crown land parcels that are within machine learned spatial data extent?
```
SELECT ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent

WHERE  
    {
    ?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry2.
        ?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
                Ontology_Vicmap:isCrown true;
				Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
             Ontology_Vicmap:hasGeometryProvenance ?geomprov.
               ?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
    
			FILTER (geof:sfWithin(?geometry_coord, "POLYGON((144.17683767728906 -36.673453035742895, 144.17683767728906 -36.5836858867246, 144.2876009046173 -36.5836858867246, 144.2876009046173 -36.673453035742895, 144.17683767728906 -36.673453035742895))") || geof:sfWithin(?geometry_coord, "POLYGON((146.00180320751213 -37.11933855921646, 146.00180320751213 -37.02891715457913, 146.11419264044918 -37.02891715457913, 146.11419264044918 -37.11933855921646, 146.00180320751213 -37.11933855921646))"))
    }
```
   
17) On which Vicmap parcels one or more new waterbodies (farm dams, reservoirs, etc) have been developed in the last year?

   
```

SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
#	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE 
{
	{
     ?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry1.
         ?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
                Ontology_Vicmap:isCrown true;
				Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
              ?geomprov dcterms:title ?auxname;
						dcterms:source ?auxcontent.
    
		FILTER (geof:sfWithin(?geometry_coord, "POLYGON((144.17683767728906 -36.673453035742895, 144.17683767728906 -36.5836858867246, 144.2876009046173 -36.5836858867246, 144.2876009046173 -36.673453035742895, 144.17683767728906 -36.673453035742895))"))
    }
    {
	?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.
            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?wb_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov1.
              ?geomprov1 dcterms:title ?auxname1.
            Filter( ?auxname1 = 'HY_WATER_AREA_ML')
        
    {
        select ?wb_instance where 
        {
            ?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.
        }
        GROUP BY ?wb_instance
        HAVING (COUNT(?wb_instance) =1 )
        }
    
    {
        Filter (geof:sfIntersects(?geometry_coord, ?wb_coord)).
    }
       
    }
}
    
```
   
18) Can you show Victorian properties that have been flooded in last 5 years?

```

SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
#	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE 
{
	{
     ?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry1.
         ?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
                Ontology_Vicmap:isCrown true;
				Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
              ?geomprov dcterms:title ?auxname;
						dcterms:source ?auxcontent.
    
		FILTER (geof:sfWithin(?geometry_coord, "POLYGON((144.17683767728906 -36.673453035742895, 144.17683767728906 -36.5836858867246, 144.2876009046173 -36.5836858867246, 144.2876009046173 -36.673453035742895, 144.17683767728906 -36.673453035742895))"))
    }
    {
	?flood rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.
            ?geometry rdf:type geosparql:Geometry ;
                      Ontology_Vicmap:varietyOf ?ftype2;
                Ontology_Vicmap:createDate ?createdate2;     
                Ontology_Vicmap:geometryCoordinates ?flood_coord.
        
        FILTER(?ftype2 in ('Flood_Authoritative') &&
        xsd:date(?createdate2) > "2022-02-01"^^xsd:date)
        
        FILTER (geof:sfWithin(?flood_coord, "POLYGON((144.17683767728906 -36.673453035742895, 144.17683767728906 -36.5836858867246, 144.2876009046173 -36.5836858867246, 144.2876009046173 -36.673453035742895, 144.17683767728906 -36.673453035742895))"))
    }
      
    {
        Filter (geof:sfIntersects(?geometry_coord, ?flood_coord)).
    }
       
}
```
   
19) By using new machine learned (ML) data can you identify waterbodies (farm dams, reservoirs, etc) that have increased in their size in last year?

```
SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.

            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
    
    Filter(?auxname != 'HY_WATER_AREA_LIDAR')
   
    {
SELECT ?wb_instance

	    WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry1.
            ?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord1;
                Ontology_Vicmap:hasGeometryProvenance ?prov.
            ?prov dcterms:title ?dataset.
          
            FILTER (?dataset = 'Vicmap Hydro - Water Polygon').
            
			?wb_instance  geosparql:hasGeometry ?geometry2.
  			?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord2;
                Ontology_Vicmap:hasGeometryProvenance ?prov2.
            ?prov2 dcterms:title 'HY_WATER_AREA_ML'.
           
            Filter(ext:area(?coord2) > ext:area(?coord1))
        }
GROUP BY ?wb_instance
HAVING (COUNT(DISTINCT ?geometry1) >= 1 && COUNT(DISTINCT ?geometry2) >= 1 )
    }
}
```

20) By using LiDAR captured data can you identify the waterbodies (farm dams, reservoirs, etc) that have increased in their size in last 5 years?

```
SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.

            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
    
    Filter(?auxname != 'HY_WATER_AREA_ML')
   
    {
SELECT ?wb_instance

	    WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry1.
            ?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord1;
                Ontology_Vicmap:hasGeometryProvenance ?prov.
            ?prov dcterms:title ?dataset.
          
            FILTER (?dataset = 'Vicmap Hydro - Water Polygon').
            
			?wb_instance  geosparql:hasGeometry ?geometry2.
  			?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord2;
                Ontology_Vicmap:hasGeometryProvenance ?prov2.
            ?prov2 dcterms:title 'HY_WATER_AREA_LIDAR'.
           
            Filter(ext:area(?coord2) > ext:area(?coord1))
        }
GROUP BY ?wb_instance
HAVING (COUNT(DISTINCT ?geometry1) >= 1 && COUNT(DISTINCT ?geometry2) >= 1 )
    }
}
``` 
21) Can you identify waterbodies that have been developed on the Vicmap crown land parcel with PFI = 131398958 in the last year?
 

```

select ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
where {
    {
        ?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry1.
    	?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:isCrown True;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasUFI ?ufi;
				Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
        
		?geomprov dcterms:title ?auxname;
			dcterms:source ?auxcontent.
    
    Filter (?pfi = '131398958'^^xsd:int)
        }
union
    {
select   ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
where 
{
        ?wb_instance rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry2.
        ?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
        
		?geomprov dcterms:title ?auxname;
			dcterms:source ?auxcontent.
    
    FILTER(?ftype in ('wb_lake') &&
        xsd:date(?createdate) > "2023-02-22"^^xsd:date)
    
		?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry1.
    	?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:isCrown True;
                Ontology_Vicmap:hasPFI ?pfi1;
                Ontology_Vicmap:geometryCoordinates ?parcelCoord.
    
    Filter (?pfi1 = '131398958'^^xsd:int)

    Filter (geof:sfIntersects(?geometry_coord, ?parcelCoord))
    }
    
    }
}
```

22) What are the areas prone to flooding for the Vicmap parcel that has permanent feature identifier (PFI) with number 45537811?

```
select ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
where {
    {
        ?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry1.
    	?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasUFI ?ufi;
				Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
        
		?geomprov dcterms:title ?auxname;
			dcterms:source ?auxcontent.
    
    Filter (?pfi = '45537811'^^xsd:int)
        }

union
    {
select   ?pfi ?createdate ?geometry_coord ?ufi ?ftype ?auxname ?auxcontent
where 
{
        ?wb_instance rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry2.
        ?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
        
		?geomprov dcterms:title ?auxname;
			dcterms:source ?auxcontent.
    
    FILTER(?ftype in ('Flood_Authoritative') &&
        xsd:date(?createdate) > "2019-02-01"^^xsd:date)

	?parcel rdf:type geosparql:Feature;
                     geosparql:hasGeometry ?geometry1.
    	?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi1;
                Ontology_Vicmap:geometryCoordinates ?parcelCoord.
    Filter (?pfi1 = '45537811'^^xsd:int)
    Filter (geof:sfIntersects(?geometry_coord, ?parcelCoord)).
    }
    
    }
}
```

23) What is source information for retrieved spatial feature?

```
SELECT ?pfi ?createdate ?ftype ?ufi ?geometry_coord ?auxname ?auxcontent
WHERE  {
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry.
	?geometry rdf:type geosparql:Geometry ;
		Ontology_Vicmap:hasPFI ?pfi;
		Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
		Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:hasGeometryProvenance ?geomprov;
		Ontology_Vicmap:geometryCoordinates ?geometry_coord.   
	?geomprov dcterms:title ?auxname;
		dcterms:source ?auxcontent.
} LIMIT 200
```


24) The basic SPARQL query expected by [the visualisation dashboard](../VisualisationDashboard/vicmap_main_050324.html) is: 

```
SELECT ?pfi ?ufi ?ftype ?createdate ?geometry_coord
WHERE {
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry.
	?geometry rdf:type geosparql:Geometry ;
		Ontology_Vicmap:hasPFI ?pfi;
		Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
		Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:geometryCoordinates ?geometry_coord.
}
LIMIT 100
```

Consequently, a simple query to show only the wetland swamps would be:
25) Can you show all wetland swamp areas in Victoria?
```
SELECT ?pfi ?ufi ?ftype ?createdate ?geometry_coord
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry.
	?geometry rdf:type geosparql:Geometry ;
		Ontology_Vicmap:hasPFI ?pfi;
		Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
		Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:geometryCoordinates ?geometry_coord.
    FILTER(?ftype = "wetland_swamp").
}
LIMIT 100
```

Or to retrieve waterbody 8094:
26) Can you retreive waterbody with name wb8094?
```
SELECT ?pfi ?ufi ?ftype ?createdate ?geometry_coord
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry.
	?geometry rdf:type geosparql:Geometry ;
		Ontology_Vicmap:hasPFI ?pfi;
		Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
		Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:geometryCoordinates ?geometry_coord.
    FILTER(STRAFTER(STR(?wb_instance), '#') = 'wb8094').
}
LIMIT 100
```

27) A helpful query for a layer: Can you show data set with the title 'HY_WATER_AREA_ML'?

```
SELECT ?pfi ?ufi ?ftype ?createdate ?geometry_coord
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry.
	?geometry rdf:type geosparql:Geometry ;
		Ontology_Vicmap:hasPFI ?pfi;
		Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
		Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:geometryCoordinates ?geometry_coord;
                Ontology_Vicmap:hasGeometryProvenance ?geomprov.
        ?geomprov dcterms:title 'HY_WATER_AREA_ML'.    
}
LIMIT 100
```

28) There is also a flexible second tab in the popup enabled. Anything passed back with the optional ?auxname and ?auxcontent parameters will appear in the second tab of the popup (under the "Metadata" tab). For example, the following query will populate the second tab with the coordinates of the feature. 

```
SELECT ?pfi ?ufi ?ftype ?createdate ?geometry_coord ?auxname ?auxcontent WHERE {
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry.
	?geometry rdf:type geosparql:Geometry ;
		Ontology_Vicmap:hasPFI ?pfi;
		Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
		Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:geometryCoordinates ?geometry_coord.
BIND("Coords" AS ?auxname). 
BIND(?geometry_coord AS ?auxcontent)
} LIMIT 100
```

## The queries in this section are all connected with multiple geometric representations of features. 

29) Show all the waterbodies with multiple geometry representations?

```
SELECT (STRAFTER(STR(?wb_instance), '#') AS ?debug)
	?pfi ?ufi ?ftype ?createdate ?geometry_coord
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry2;
		geosparql:hasGeometry ?geometry.
	?geometry rdf:type geosparql:Geometry ;
		Ontology_Vicmap:hasPFI ?pfi;
		Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:varietyOf ?ftype;
		Ontology_Vicmap:geometryCoordinates ?geometry_coord.
    FILTER(?geometry2 != ?geometry).
}
LIMIT 500
```

30) Show all the waterbodies with both point and polygon representations. 

Note that "LIMIT" won't work with this query, because we won't necessarily get matching point-polygon representations. Instead, the approach is to limit by waterbodyID (between 1000 and 2000, note this query may be slow): 

```
SELECT ?pfi ?ufi ?ftype ?createdate ?geometry_coord (?wbid AS ?debug)
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
WHERE {
	?wb_instance rdf:type geosparql:Feature;
		Ontology_Vicmap:waterbodyID ?wbid;
		geosparql:hasGeometry ?geometry2;
		geosparql:hasGeometry ?geometry.
	?geometry rdf:type geosparql:Geometry ;
		Ontology_Vicmap:hasPFI ?pfi;
		Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:varietyOf ?ftype;
		Ontology_Vicmap:geometryCoordinates ?geometry_coord.
	?geometry2 rdf:type geosparql:Geometry ;
		Ontology_Vicmap:geometryCoordinates ?geometry2_coord.
    FILTER(?wbidi>1000 && ?wbidi<2000 && 
    	((?gtype="POIN" && ?g2type="POLY") || (?g2type="POIN" && ?gtype="POLY"))).
    BIND(xsd:integer(?wbid) AS ?wbidi).
    BIND(SUBSTR(STR(?geometry_coord),1,4) AS ?gtype).
    BIND(SUBSTR(STR(?geometry2_coord),1,4) AS ?g2type).
}
```

31) Show all the waterbodies with both point and polygon representations (alternative)

An alternative formulation uses a nested query that will show water bodies with point and polygon representations where point features have 'wb_dam' and polygon features have 'wb_lake' feature types:

```
SELECT ?pfi ?createdate ?geometry_coord ?ufi ?ftype
WHERE {
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry.
	?geometry rdf:type geosparql:Geometry ;
		Ontology_Vicmap:hasPFI ?pfi;
		Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
		Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:geometryCoordinates ?geometry_coord.
	{SELECT ?wb_instance
	WHERE {
		?wb_instance rdf:type geosparql:Feature;
			geosparql:hasGeometry ?geometry1;
			geosparql:hasGeometry ?geometry2.
		?geometry1 rdf:type geosparql:Geometry ;
			Ontology_Vicmap:geometryCoordinates ?coord1;
			Ontology_Vicmap:varietyOf 'wb_lake'.
		?geometry2 rdf:type geosparql:Geometry ;
			Ontology_Vicmap:geometryCoordinates ?coord2;
			Ontology_Vicmap:varietyOf 'wb_dam'.
		FILTER (regex(str(?coord1), "POLYGON", "i"))
		FILTER (regex(str(?coord2), "POINT", "i"))
 	}
	GROUP BY ?wb_instance
	HAVING (COUNT(DISTINCT ?geometry1) >= 1 && COUNT(DISTINCT ?geometry2) >= 1)
    }
}
```

## Multiple data set queries

32) Identify dams and lakes that are located within the crown land with pfi of 45541397?

This query spans the crown land and hydro data sets, using a spatial join. 

```
SELECT ?pfi ?createdate ?geometry_coord ?ufi ?ftype
WHERE{
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry.
    ?geometry rdf:type geosparql:Geometry ;
    	Ontology_Vicmap:hasPFI ?pfi;
    	Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
        Ontology_Vicmap:createDate ?createdate;
        Ontology_Vicmap:geometryCoordinates ?geometry_coord.
    FILTER(?ftype IN ('wb_dam','wb_lake'))
        ?parcel rdf:type geosparql:Feature;
			geosparql:hasGeometry ?geometry1;
			Ontology_Vicmap:isType 'Parcels'.
       ?geometry1 Ontology_Vicmap:hasPFI '45541397'^^xsd:int;
			Ontology_Vicmap:isCrown true;
			Ontology_Vicmap:geometryCoordinates ?parcelCoord.
	#BIND(STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
  	BIND(STRAFTER(STR(?parcel), '#') AS ?ParcelName)
    FILTER(geof:sfWithin(?geometry_coord, ?parcelCoord)).
}

```

33) Identify the geometries in specific data sets associated with waterbody 3391

```
SELECT ?pfi ?createdate ?geometry_coord ?ufi ?ftype
WHERE{
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry.
    ?geometry rdf:type geosparql:Geometry ;
    	Ontology_Vicmap:hasPFI ?pfi;
    	Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
        Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:hasGeometryProvenance ?geomprov;
        Ontology_Vicmap:geometryCoordinates ?geometry_coord.
	?geomprov dcterms:title ?dataset;
    FILTER(STRAFTER(STR(?wb_instance), '#') = 'wb3391').
	FILTER (?dataset = 'Vicmap Hydro - Water Polygon' || 
		?dataset = 'HY_WATER_AREA_ML' || 
		?dataset = 'HY_WATER_AREA_LIDAR').
}

```

## Metadata queries

34) Identify dataset and source of geometries with pfi of 8136595 in different data sets?


```
SELECT ?pfi ?createdate ?ftype ?dataset ?identifier ?source
WHERE  {
	?wb_instance rdf:type geosparql:Feature;
		geosparql:hasGeometry ?geometry.
	?geometry rdf:type geosparql:Geometry ;
		Ontology_Vicmap:hasPFI ?pfi;
		Ontology_Vicmap:hasUFI ?ufi;
		Ontology_Vicmap:varietyOf ?ftype;
		Ontology_Vicmap:createDate ?createdate;
		Ontology_Vicmap:hasGeometryProvenance ?geomprov;
		Ontology_Vicmap:geometryCoordinates ?geometry_coord.   
	?geomprov dcterms:title ?dataset;
		dcterms:identifier ?identifier;
		dcterms:source ?source.
	FILTER (?pfi = 8136595).
}
```

## Indexing GraphDB

### Check indexing status

```
PREFIX geosparql: <http://www.ontotext.com/plugins/geosparql#>

SELECT DISTINCT ?tree ?precision ?enab WHERE {
    [] geosparql:currentPrefixTree ?tree;
        geosparql:currentPrecision ?precision;
        geosparql:enabled ?enab
}
```

### Set indexing on

```
PREFIX geosparql: <http://www.ontotext.com/plugins/geosparql#>

INSERT DATA {
    [] geosparql:prefixTree "quad"; #geohash
        geosparql:precision "11";
        geosparql:enabled "true".
}
```

### Force reindexing 

```
PREFIX onto-geo: <http://www.ontotext.com/plugins/geosparql#>

INSERT DATA {
    [] onto-geo:forceReindex []
}
```
