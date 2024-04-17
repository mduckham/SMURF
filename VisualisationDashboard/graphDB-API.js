 class SPARQLQueryDispatcher {
    constructor( endpoint ) {
        this.endpoint = endpoint;
    }

    query( sparqlQuery ) {
        const fullUrl = this.endpoint + '?query=' + encodeURIComponent( sparqlQuery );
        const headers = { 'Accept': 'application/sparql-results+json' };

        return fetch( fullUrl, { headers } ).then( body => body.json() );
    }
}

const endpointUrl = 'http://localhost:7200/repositories/Dynamic_Vicmap';
const sparqlQuery = `
PREFIX onto: <http://www.ontotext.com/>
prefix Ontology_Vicmap:<http://www.semanticweb.org/mkazemi/ontologies/2023/9/Ontology_Vicmap2#>
prefix dcam:<http://purl.org/dc/dcam/>
prefix dcat:<http://www.w3.org/ns/dcat#>
prefix dcterms:<http://purl.org/dc/terms/>
prefix dqv:<http://www.w3.org/ns/dqv#>
prefix fsdf:<https://linked.data.gov.au/def/fsdf/>
prefix geosparql:<http://www.opengis.net/ont/geosparql#>
prefix ns:<http://www.w3.org/2006/vcard/ns#>
prefix owl:<http://www.w3.org/2002/07/owl#>
prefix prov:<http://www.w3.org/ns/prov#>
prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs:<http://www.w3.org/2000/01/rdf-schema#>
prefix skos:<http://www.w3.org/2004/02/skos/core#>
prefix terms:<http://purl.org/dc/terms/#>
prefix vann:<http://purl.org/vocab/vann/>


SELECT (STRAFTER(STR(?wb_instance), '#') AS ?WaterbodyName)
 	?pfi ?createdate ?geometry_coord
	(STRAFTER(STR(?geometry), '#') AS ?geometryName)



WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry.

            ?geometry rdf:type geosparql:Geometry ;
                Ontology_Vicmap:hasPFI ?pfi;
                Ontology_Vicmap:createDate ?createdate;
                Ontology_Vicmap:geometryCoordinates ?geometry_coord.

    {
SELECT ?wb_instance

		WHERE {?wb_instance rdf:type geosparql:Feature;
				geosparql:hasGeometry ?geometry1.

            ?geometry1 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord1.

     		 FILTER (regex(str(?coord1), "POLYGON", "i"))

			?wb_instance  geosparql:hasGeometry ?geometry2.
  			?geometry2 rdf:type geosparql:Geometry ;
                Ontology_Vicmap:geometryCoordinates ?coord2.

 			FILTER (regex(str(?coord2), "POINT", "i"))}
GROUP BY ?wb_instance
HAVING (COUNT(DISTINCT ?geometry1) >= 1 && COUNT(DISTINCT ?geometry2) >= 1)
    }
}

LIMIT 40
`;


const queryDispatcher = new SPARQLQueryDispatcher( endpointUrl );
// queryDispatcher.query( sparqlQuery ).then( console.log );

// const queryDispatcher = new SPARQLQueryDispatcher(endpointUrl);
queryDispatcher.query(sparqlQuery).then(result => {
    // Check if results exist and have bindings
    if (result.results && result.results.bindings) {
    	var geometries = [];
        // Iterate through each binding
        result.results.bindings.forEach(binding => {
            // Access the values of each binding
            //const waterbodyName = binding.WaterbodyName.value;
           	const pfi = binding.pfi.value;
           // const createDate = binding.createdate.value;
           // const geometryName = binding.geometryName.value;
            const geometry_coord = binding.geometry_coord.value;
            geometries.push(geometry_coord)

            // Use the values as needed
            console.log(`Geometry_Coordinate: ${geometry_coord}`);
        });
    } else {
    	
        console.log('No results found for the given SPARQL query.');
    }
});
