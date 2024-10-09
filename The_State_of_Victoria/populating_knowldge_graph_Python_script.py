#%% KG creation stage: Populating Ontology


import geopandas as gpd
import matplotlib.pyplot as plt
import os


from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD
import pandas as pd
import os
from datetime import datetime
import math
import numpy as np
import pickle
import time
import multiprocessing
import utm
from rtree import index


os.chdir('/home/ubuntu/Vicmap_KG/')

start_time = time.time()


#%% Stage 2: Defining Ontology and namespaces


print(" Defining Ontology and namespaces...")

# Create a new RDF graph

g = Graph()

result = g.parse("DV_project.rdf")


# Define the namespaces used in your RDF file

ontology_ns = Namespace("http://www.semanticweb.org/DV_project#")
ontology_prov = Namespace("http://www.w3.org/ns/prov#")
ontology_omg = Namespace("https://w3id.org/omg#")
ontology_foaf = Namespace("http://xmlns.com/foaf/0.1/")
xsd_ns = Namespace("http://www.w3.org/2001/XMLSchema#")
schema_geo = Namespace("http://schema.org/")

rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
dc = Namespace("http://purl.org/dc/elements/1.1/")
dcam = Namespace("http://purl.org/dc/dcam/#")
owl = Namespace("http://www.w3.org/2002/07/owl#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
terms = Namespace("http://purl.org/dc/terms/")
vann = Namespace("http://purl.org/vocab/vann/#")
xml= Namespace("http://www.w3.org/XML/1998/namespace")

dqv = Namespace("http://www.w3.org/ns/dqv#")
dcat = Namespace("http://www.w3.org/ns/dcat#")
geosparql = Namespace("http://www.opengis.net/ont/geosparql#")
ns = Namespace("http://www.w3.org/2006/vcard/ns#")
cube = Namespace("http://purl.org/linked-data/cube#")
fsdf = Namespace("https://linked.data.gov.au/def/fsdf/")


# Add ontology information
g.bind("owl", owl)
g.bind("rdf", rdf)
g.bind("rdfs", rdfs)
g.bind("Ontology_Vicmap", ontology_ns)
g.bind("prov", ontology_prov)
g.bind("omg", ontology_omg)
g.bind("foaf",ontology_foaf)
g.bind("xsd", xsd_ns)
g.bind("schema", schema_geo)

g.bind("dc", dc)
g.bind("dcam", dcam)
g.bind("skos", skos)
g.bind("terms", terms)
g.bind("vann", vann)
g.bind("xml", xml)

g.bind("dqv", dqv)
g.bind("dcat", dcat)
g.bind("geosparql", geosparql)
g.bind("ns", ns)
g.bind("cube", cube)
g.bind("fsdf", fsdf)


## Input Metadata: hydro polygon, hydro point, parcels, and floods

hydro_polygon_metadata = pd.read_csv('Dataset/State_Level/metadata-hydroPolygon.csv')
hydro_polygon_metadata = hydro_polygon_metadata.replace(np.nan,"")

hydro_point_metadata = pd.read_csv('Dataset/State_Level/metadata-hydroPoint.csv')
hydro_point_metadata = hydro_point_metadata.replace(np.nan,"")

parcels_metadata = pd.read_csv('Dataset/State_Level/metadata-parcels.csv')
parcels_metadata = parcels_metadata.replace(np.nan,"")

flood_metadata = pd.read_csv('Dataset/State_Level/metadata-flood.csv')
flood_metadata = flood_metadata.replace(np.nan,"")

## Define classes

Feature = geosparql["Feature"]
Geometry = geosparql["Geometry"]
Dataset = dcat["Dataset"]
Entity = ontology_prov["Entity"]
Agent = ontology_prov["Agent"]
Agency = fsdf["Agency"]
Jurisdiction = fsdf["Jurisdiction"]
# Location = terms["Location"]
Spatial = terms["spatial"]
PeriodOfTime = terms["PeriodOfTime"]
Frequency = terms["Frequency"]
Distribution = dcat["Distribution"]
MediaType = terms["MediaType"]
RightsStatement = terms["RightsStatement"]
Kind = ns["Kind"]
Organization = ontology_prov["Organization"]
TelephoneType = ns["TelephoneType"]
Voice = ns["Voice"]
Fax = ns["Fax"]
Address = ns["Address"]
QualityMeasurement = dqv["QualityMeasurement"]
Metric = dqv["Metric"]
Dimension = dqv["Dimension"]
Category = dqv["Category"]
#Standard = terms["Standard"]

#%% Metadata for Hydro Polygon
## Define Dataset instance

dataset_title = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Resource Name:', 'Description'].values[0]
available_date = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Metadata Date:', 'Description'].values[0]
title = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Title:', 'Description'].values[0]

hydro_dataset_polygon = ontology_ns[dataset_title]
g.add((hydro_dataset_polygon, RDF.type, Dataset))

 
## Define data properties of dataset instance

g.add((hydro_dataset_polygon, terms['abstract'], 
      Literal(hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Abstract:', 'Description'].values[0],
      datatype=xsd_ns["string"])))


g.add((hydro_dataset_polygon, terms['description'],
      Literal(hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Purpose:', 'Description'].values[0],
      datatype=xsd_ns["string"])))
      
g.add((hydro_dataset_polygon, terms['identifier'], 
      Literal(hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Anzlic ID:', 'Description'].values[0],
      datatype=xsd_ns["string"])))
      
      
g.add((hydro_dataset_polygon, dcat['keyword'],
      Literal(hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Search Words:', 'Description'].values[0],
      datatype=xsd_ns["string"])))

      
g.add((hydro_dataset_polygon, terms['source'],
      Literal(hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Data Source:', 'Description'].values[0],
      datatype=xsd_ns["string"])))

g.add((hydro_dataset_polygon, terms['available'], Literal(available_date, datatype=xsd_ns["date"])))

g.add((hydro_dataset_polygon, terms["title"], Literal(title,datatype=xsd_ns["string"])))


## Define object properties of dataset instance

# Contact point

contact = "vcard01"
organization = "organization01"
role = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Contact Position:', 'Description'].values[0]
address = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Address:', 'Description'].values[0]
# if address == "":
#     org_address = ""
# else:
#     org_address = "{0}".format(address)
    
telephone = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Telephone:', 'Description'].values[0]
if telephone == "":
    org_tel = "telephone_unknown01"
else:
    org_tel = "telephone_{0}".format(telephone)


facsimile = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Facsimile:', 'Description'].values[0]
if facsimile == "":
    org_fax = "fax_unknown01"
else:
    org_fax = "fax{0}".format(facsimile)
    
email = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Email Address:', 'Description'].values[0]
# if email == "":
#     org_email = "email_unknown01"
# else:
#     org_email = "email{0}".format(email)

# url = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Additional Metadata:', 'Description'].values[0]
countryName = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Country Name:', 'Description'].values[0]
locality = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Locality:', 'Description'].values[0]
region = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Region:', 'Description'].values[0]


g.add((hydro_dataset_polygon, dcat["contactPoint"],ontology_ns[contact] ))
g.add((ontology_ns[contact], RDF.type, Kind))
#g.add((ontology_ns[organization], RDFS.subClassOf,ontology_ns[contact]))
g.add((ontology_ns[organization], RDF.type, Organization))



g.add((ontology_ns[organization], ns["country-name"], Literal(countryName,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["locality"], Literal(locality,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["region"], Literal(region,datatype=xsd_ns["string"])))
#g.add((ontology_ns[organization], ontology_ns["hasURL"], Literal(url,datatype=xsd_ns["string"])))



g.add((ontology_ns[organization], ns["street-address"], Literal(address,datatype=xsd_ns["string"])))
# g.add((ontology_ns[org_address], RDF.type, Address))

g.add((ontology_ns[organization], ns["hasTelephone"], ontology_ns["Phone01"]))
g.add((ontology_ns["Phone01"], RDF.type, TelephoneType))
# g.add((ontology_ns[org_tel], RDFS.subClassOf, ontology_ns["Phone01"]))
g.add((ontology_ns[org_tel], RDF.type, ns["Cell"]))
# g.add((ontology_ns[org_fax], RDFS.subClassOf, ontology_ns["Phone01"]))
g.add((ontology_ns[org_fax], RDF.type, Fax))

g.add((ontology_ns[organization], ontology_ns["organizationemail"], Literal(email,datatype=xsd_ns["string"])))
# g.add((ontology_ns[org_email], RDF.type, ns["Email"]))

# Custodian
custodian = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Custodian:', 'Description'].values[0]
if pd.isnull(custodian) is True:
    dataset_agency = "custodian_unknown01"
else:
    dataset_agency = "custodian_{0}".format(custodian)

#dataset_agency = ontology_ns["{0}_agency".format(dataset_title)]
g.add((hydro_dataset_polygon, fsdf["hasCustodian"], ontology_ns[dataset_agency] ))
g.add((ontology_ns[dataset_agency] , RDF.type, Agency))
# g.add((ontology_ns[dataset_agency], RDFS.subClassOf, ontology_ns[organization]))


# Jurisdication
jurisdiction = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Jurisdiction:', 'Description'].values[0]
if pd.isnull(jurisdiction) is True:
    dataset_jurisdiction = "jurisdiction_unknown01"
else:
    dataset_jurisdiction = "jurisdiction_{0}".format(jurisdiction)
    
#dataset_jurisdiction = ontology_ns["{0}_jurisdiction".format(dataset_title)]
g.add((hydro_dataset_polygon, fsdf["hasJurisdiction"], ontology_ns[dataset_jurisdiction] ))
g.add((ontology_ns[dataset_jurisdiction], RDF.type, Jurisdiction))
# g.add((ontology_ns[dataset_jurisdiction], RDFS.subClassOf, ontology_ns[organization]))

# Bounding box

dataset_location = "{0}_location".format(dataset_title)
g.add((hydro_dataset_polygon, terms["spatial"], ontology_ns[dataset_location] ))
g.add((ontology_ns[dataset_location], RDF.type, Spatial))
g.add((ontology_ns[dataset_location], dcat["bbox"], 
                              Literal(hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Geographic Bounding Box:', 'Description'].values[0],
                              datatype=xsd_ns["string"])))


# Temporal][]

dataset_temporal = "{0}_temporal".format(dataset_title)
g.add((hydro_dataset_polygon, terms["temporal"], ontology_ns[dataset_temporal] ))
g.add(( ontology_ns[dataset_temporal] , RDF.type, PeriodOfTime))

start_date = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Beginning to Ending Date:', 'Description'].values[0].split(" - ")[0]
end_date = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Beginning to Ending Date:', 'Description'].values[0].split(" - ")[1]
g.add(( ontology_ns[dataset_temporal] , dcat["startDate"], Literal(start_date, datatype=xsd_ns["string"])))
g.add(( ontology_ns[dataset_temporal] , dcat["endDate"], Literal(end_date, datatype=xsd_ns["string"])))


# Frequency
frequency = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Maintainence and Update Frequency:', 'Description'].values[0]
# if pd.isnull(frequency) is True:
#     dataset_frequency = "frequency_unknown01"
# else:
#     dataset_frequency = "frequency_{0}".format(frequency)
    
#dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_polygon, terms["accrualPeriodicity"],Literal(frequency, datatype=xsd_ns["string"])))
# g.add((ontology_ns[dataset_frequency], RDF.type, Frequency))


# Distribution

distribution = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Stored Data Format:', 'Description'].values[0]
if pd.isnull(distribution) is True:
    dataset_distribution = "distribution_unknown01"
else:
    dataset_distribution = "distribution_{0}".format(distribution)


# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_polygon, dcat["distribution"], ontology_ns[dataset_distribution] ))
g.add((ontology_ns[dataset_distribution], RDF.type, Distribution))


# Access right

access = hydro_polygon_metadata.loc[hydro_polygon_metadata['Metadata'] == 'Access Constraint:', 'Description'].values[0]
if pd.isnull(access) is True:
    dataset_access = "access_unknown01"
else:
    dataset_access = "access_{0}".format(distribution)


# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_polygon, terms["accessRights"], ontology_ns[dataset_access] ))
g.add((ontology_ns[dataset_access], RDF.type, RightsStatement))


# Accuracy

positional_accuracy = ontology_ns["{0}_positional_accuracy".format(dataset_title)]
attribute_accuracy = ontology_ns["{0}_attribute_accuracy".format(dataset_title)]
logical_consistency = ontology_ns["{0}_logical_consistency".format(dataset_title)]
accessibility_1 = ontology_ns["{0}_accessibility".format(dataset_title)]


positional_accuracy_metric = ontology_ns["{0}_positional_accuracy_metric".format(dataset_title)]
attribute_accuracy_metric = ontology_ns["{0}_attribute_accuracy_metric".format(dataset_title)]
logical_consistency_metric = ontology_ns["{0}_logical_consistency_metric".format(dataset_title)]
accessibility_metric = ontology_ns["{0}_accessibility_metric".format(dataset_title)]

accuracy = ontology_ns["accuracy"]
consistency = ontology_ns["consistency"]
accessibility = ontology_ns["accessibility"]



g.add((hydro_dataset_polygon, dqv["hasQualityMeasurement"], positional_accuracy))
g.add((positional_accuracy, RDF.type, QualityMeasurement))
g.add((positional_accuracy, dqv["value"], Literal("+/-30", datatype=xsd_ns["string"])))
g.add((positional_accuracy, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((positional_accuracy, dqv["isMeasurementOf"], positional_accuracy_metric))

g.add((positional_accuracy_metric, RDF.type, Metric))
# g.add((positional_accuracy_metric, dqv["value"], Literal("+/-30", datatype=xsd_ns["string"])))
g.add((positional_accuracy_metric, dqv["inDimension"], accuracy))
g.add((accuracy, RDF.type, Dimension))


g.add((hydro_dataset_polygon, dqv["hasQualityMeasurement"], attribute_accuracy))
g.add((attribute_accuracy, RDF.type, QualityMeasurement))
g.add((attribute_accuracy, dqv["value"], Literal("1%-5%", datatype=xsd_ns["string"])))
g.add((attribute_accuracy, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((attribute_accuracy, dqv["isMeasurementOf"], attribute_accuracy_metric))
g.add((attribute_accuracy_metric, RDF.type, Metric))
g.add((attribute_accuracy_metric, dqv["inDimension"], accuracy))


g.add((hydro_dataset_polygon, dqv["hasQualityMeasurement"], logical_consistency))
g.add((logical_consistency, RDF.type, QualityMeasurement))
g.add((logical_consistency, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((logical_consistency, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((logical_consistency, dqv["isMeasurementOf"], logical_consistency_metric))
g.add((logical_consistency_metric, RDF.type, Metric))
g.add((logical_consistency_metric, dqv["inDimension"], consistency))
g.add((consistency, RDF.type, Dimension))


g.add((hydro_dataset_polygon, dqv["hasQualityMeasurement"], accessibility_1))
g.add((accessibility_1, RDF.type, QualityMeasurement))
g.add((accessibility_1, dqv["value"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, dqv["isMeasurementOf"], accessibility_metric))
g.add((accessibility_metric, RDF.type, Metric))
g.add((accessibility_metric, dqv["inDimension"], accessibility))
g.add((accessibility, RDF.type, Dimension))


#%% Metadata for Hydro point

## Define Dataset instance

dataset_title = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Resource Name:', 'Description'].values[0]
available_date = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Metadata Date:', 'Description'].values[0]
title = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Title:', 'Description'].values[0]

hydro_dataset_point = ontology_ns[dataset_title]
g.add((hydro_dataset_point, RDF.type, Dataset))

 
## Define data properties of dataset instance

g.add((hydro_dataset_point, terms['abstract'], 
      Literal(hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Abstract:', 'Description'].values[0],
      datatype=xsd_ns["string"])))


g.add((hydro_dataset_point, terms['description'],
      Literal(hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Purpose:', 'Description'].values[0],
      datatype=xsd_ns["string"])))
      
g.add((hydro_dataset_point, terms['identifier'], 
      Literal(hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Anzlic ID:', 'Description'].values[0],
      datatype=xsd_ns["string"])))
      
      
g.add((hydro_dataset_point, dcat['keyword'],
      Literal(hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Search Words:', 'Description'].values[0],
      datatype=xsd_ns["string"])))

      
g.add((hydro_dataset_point, terms['source'],
      Literal(hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Data Source:', 'Description'].values[0],
      datatype=xsd_ns["string"])))

g.add((hydro_dataset_point, terms['available'], Literal(available_date, datatype=xsd_ns["date"])))

g.add((hydro_dataset_point, terms["title"], Literal(title,datatype=xsd_ns["string"])))


## Define object properties of dataset instance

# Contact point

contact = "vcard02"
organization = "organization02"
role = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Contact Position:', 'Description'].values[0]
address = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Address:', 'Description'].values[0]
# if address == "":
#     org_address = ""
# else:
#     org_address = "{0}".format(address)
    
telephone = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Telephone:', 'Description'].values[0]
if telephone == "":
    org_tel = "telephone_unknown01"
else:
    org_tel = "telephone_{0}".format(telephone)


facsimile = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Facsimile:', 'Description'].values[0]
if facsimile == "":
    org_fax = "fax_unknown01"
else:
    org_fax = "fax{0}".format(facsimile)
    
email = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Email Address:', 'Description'].values[0]
# if email == "":
#     org_email = "email_unknown01"
# else:
#     org_email = "email{0}".format(email)

# url = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Additional Metadata:', 'Description'].values[0]
countryName = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Country Name:', 'Description'].values[0]
locality = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Locality:', 'Description'].values[0]
region = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Region:', 'Description'].values[0]


g.add((hydro_dataset_point, dcat["contactPoint"],ontology_ns[contact] ))
g.add((ontology_ns[contact], RDF.type, Kind))
#g.add((ontology_ns[organization], RDFS.subClassOf,ontology_ns[contact]))
g.add((ontology_ns[organization], RDF.type, Organization))



g.add((ontology_ns[organization], ns["country-name"], Literal(countryName,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["locality"], Literal(locality,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["region"], Literal(region,datatype=xsd_ns["string"])))
#g.add((ontology_ns[organization], ontology_ns["hasURL"], Literal(url,datatype=xsd_ns["string"])))



g.add((ontology_ns[organization], ns["street-address"], Literal(address,datatype=xsd_ns["string"])))
# g.add((ontology_ns[org_address], RDF.type, Address))

g.add((ontology_ns[organization], ns["hasTelephone"], ontology_ns["Phone02"]))
g.add((ontology_ns["Phone02"], RDF.type, TelephoneType))
# g.add((ontology_ns[org_tel], RDFS.subClassOf, ontology_ns["Phone01"]))
g.add((ontology_ns[org_tel], RDF.type, ns["Cell"]))
# g.add((ontology_ns[org_fax], RDFS.subClassOf, ontology_ns["Phone01"]))
g.add((ontology_ns[org_fax], RDF.type, Fax))

g.add((ontology_ns[organization], ontology_ns["organizationemail"], Literal(email,datatype=xsd_ns["string"])))
# g.add((ontology_ns[org_email], RDF.type, ns["Email"]))

# Custodian
custodian = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Custodian:', 'Description'].values[0]
if pd.isnull(custodian) is True:
    dataset_agency = "custodian_unknown02"
else:
    dataset_agency = "custodian_{0}".format(custodian)

#dataset_agency = ontology_ns["{0}_agency".format(dataset_title)]
g.add((hydro_dataset_point, fsdf["hasCustodian"], ontology_ns[dataset_agency] ))
g.add((ontology_ns[dataset_agency] , RDF.type, Agency))
# g.add((ontology_ns[dataset_agency], RDFS.subClassOf, ontology_ns[organization]))


# Jurisdication
jurisdiction = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Jurisdiction:', 'Description'].values[0]
if pd.isnull(jurisdiction) is True:
    dataset_jurisdiction = "jurisdiction_unknown02"
else:
    dataset_jurisdiction = "jurisdiction_{0}".format(jurisdiction)
    
#dataset_jurisdiction = ontology_ns["{0}_jurisdiction".format(dataset_title)]
g.add((hydro_dataset_point, fsdf["hasJurisdiction"], ontology_ns[dataset_jurisdiction] ))
g.add((ontology_ns[dataset_jurisdiction], RDF.type, Jurisdiction))
# g.add((ontology_ns[dataset_jurisdiction], RDFS.subClassOf, ontology_ns[organization]))

# Bounding box

dataset_location = "{0}_location".format(dataset_title)
g.add((hydro_dataset_point, terms["spatial"], ontology_ns[dataset_location] ))
g.add((ontology_ns[dataset_location], RDF.type, Spatial))
g.add((ontology_ns[dataset_location], dcat["bbox"], 
                              Literal(hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Geographic Bounding Box:', 'Description'].values[0],
                              datatype=xsd_ns["string"])))


# Temporal][]

dataset_temporal = "{0}_temporal".format(dataset_title)
g.add((hydro_dataset_point, terms["temporal"], ontology_ns[dataset_temporal] ))
g.add(( ontology_ns[dataset_temporal] , RDF.type, PeriodOfTime))

start_date = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Beginning to Ending Date:', 'Description'].values[0].split(" - ")[0]
end_date = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Beginning to Ending Date:', 'Description'].values[0].split(" - ")[1]
g.add(( ontology_ns[dataset_temporal] , dcat["startDate"], Literal(start_date, datatype=xsd_ns["string"])))
g.add(( ontology_ns[dataset_temporal] , dcat["endDate"], Literal(end_date, datatype=xsd_ns["string"])))


# Frequency
frequency = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Maintainence and Update Frequency:', 'Description'].values[0]
# if pd.isnull(frequency) is True:
#     dataset_frequency = "frequency_unknown01"
# else:
#     dataset_frequency = "frequency_{0}".format(frequency)
    
#dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_point, terms["accrualPeriodicity"],Literal(frequency, datatype=xsd_ns["string"])))
# g.add((ontology_ns[dataset_frequency], RDF.type, Frequency))


# Distribution

distribution = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Stored Data Format:', 'Description'].values[0]
if pd.isnull(distribution) is True:
    dataset_distribution = "distribution_unknown02"
else:
    dataset_distribution = "distribution_{0}".format(distribution)


# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_point, dcat["distribution"], ontology_ns[dataset_distribution] ))
g.add((ontology_ns[dataset_distribution], RDF.type, Distribution))


# Access right

access = hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Access Constraint:', 'Description'].values[0]
if pd.isnull(access) is True:
    dataset_access = "access_unknown02"
else:
    dataset_access = "access_{0}".format(distribution)


# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_point, terms["accessRights"], ontology_ns[dataset_access] ))
g.add((ontology_ns[dataset_access], RDF.type, RightsStatement))


# Accuracy

positional_accuracy = ontology_ns["{0}_positional_accuracy".format(dataset_title)]
attribute_accuracy = ontology_ns["{0}_attribute_accuracy".format(dataset_title)]
logical_consistency = ontology_ns["{0}_logical_consistency".format(dataset_title)]
accessibility_1 = ontology_ns["{0}_accessibility".format(dataset_title)]


positional_accuracy_metric = ontology_ns["{0}_positional_accuracy_metric".format(dataset_title)]
attribute_accuracy_metric = ontology_ns["{0}_attribute_accuracy_metric".format(dataset_title)]
logical_consistency_metric = ontology_ns["{0}_logical_consistency_metric".format(dataset_title)]
accessibility_metric = ontology_ns["{0}_accessibility_metric".format(dataset_title)]

accuracy = ontology_ns["accuracy"]
consistency = ontology_ns["consistency"]
accessibility = ontology_ns["accessibility"]



g.add((hydro_dataset_point, dqv["hasQualityMeasurement"], positional_accuracy))
g.add((positional_accuracy, RDF.type, QualityMeasurement))
g.add((positional_accuracy, dqv["value"], Literal("+/-30", datatype=xsd_ns["string"])))
g.add((positional_accuracy, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((positional_accuracy, dqv["isMeasurementOf"], positional_accuracy_metric))

g.add((positional_accuracy_metric, RDF.type, Metric))
# g.add((positional_accuracy_metric, dqv["value"], Literal("+/-30", datatype=xsd_ns["string"])))
g.add((positional_accuracy_metric, dqv["inDimension"], accuracy))
g.add((accuracy, RDF.type, Dimension))


g.add((hydro_dataset_point, dqv["hasQualityMeasurement"], attribute_accuracy))
g.add((attribute_accuracy, RDF.type, QualityMeasurement))
g.add((attribute_accuracy, dqv["value"], Literal("1%-5%", datatype=xsd_ns["string"])))
g.add((attribute_accuracy, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((attribute_accuracy, dqv["isMeasurementOf"], attribute_accuracy_metric))
g.add((attribute_accuracy_metric, RDF.type, Metric))
g.add((attribute_accuracy_metric, dqv["inDimension"], accuracy))


g.add((hydro_dataset_point, dqv["hasQualityMeasurement"], logical_consistency))
g.add((logical_consistency, RDF.type, QualityMeasurement))
g.add((logical_consistency, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((logical_consistency, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((logical_consistency, dqv["isMeasurementOf"], logical_consistency_metric))
g.add((logical_consistency_metric, RDF.type, Metric))
g.add((logical_consistency_metric, dqv["inDimension"], consistency))
g.add((consistency, RDF.type, Dimension))


g.add((hydro_dataset_point, dqv["hasQualityMeasurement"], accessibility_1))
g.add((accessibility_1, RDF.type, QualityMeasurement))
g.add((accessibility_1, dqv["value"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, dqv["isMeasurementOf"], accessibility_metric))
g.add((accessibility_metric, RDF.type, Metric))
g.add((accessibility_metric, dqv["inDimension"], accessibility))
g.add((accessibility, RDF.type, Dimension))

#%% Metadata for ML


# Define Dataset instance

dataset_title = 'HY_WATER_AREA_ML'
available_date = '00/00/0000'
hydro_dataset_ml = ontology_ns[dataset_title]
g.add((hydro_dataset_ml, RDF.type, Dataset))

 
## Define data properties of dataset instance

g.add((hydro_dataset_ml, terms['abstract'], 
      Literal(" ", datatype=xsd_ns["string"])))


g.add((hydro_dataset_ml, terms['description'],
      Literal('',datatype=xsd_ns["string"])))
      
g.add((hydro_dataset_ml, terms['identifier'], 
      Literal('', datatype=xsd_ns["string"])))
      
      
g.add((hydro_dataset_ml, dcat['keyword'],
      Literal('', datatype=xsd_ns["string"])))

      
g.add((hydro_dataset_ml, terms['source'],
      Literal('', datatype=xsd_ns["string"])))

g.add((hydro_dataset_ml, terms['available'], Literal(available_date, datatype=xsd_ns["date"])))

g.add((hydro_dataset_ml, terms["title"], Literal(dataset_title,datatype=xsd_ns["string"])))





## Define object properties of dataset instance

# Contact point

contact = "vcard03"
organization = "organization03"
role = ''
address = ''
org_address = "address_unknown03"
    
telephone =''
org_tel = "telephone_unknown03"

facsimile = ''
org_fax = "fax_unknown03"

email = ''
org_email = "email_unknown03"


url = ''
countryName = ''
locality = ''
region = ''


g.add((hydro_dataset_ml, dcat["contactPoint"],ontology_ns[contact] ))
g.add((ontology_ns[contact], RDF.type, Kind))
# g.add((ontology_ns[organization], RDFS.subClassOf,ontology_ns[contact]))
g.add((ontology_ns[organization], RDF.type, Organization))



g.add((ontology_ns[organization], ns["country-name"], Literal(countryName,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["locality"], Literal(locality,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["region"], Literal(region,datatype=xsd_ns["string"])))


g.add((ontology_ns[organization], ns["street-address"], Literal(address,datatype=xsd_ns["string"])))


g.add((ontology_ns[organization], ns["hasTelephone"], ontology_ns["Phone03"]))
g.add((ontology_ns["Phone03"], RDF.type, TelephoneType))
g.add((ontology_ns[org_tel], RDF.type, ns["Cell"]))
g.add((ontology_ns[org_fax], RDF.type, Fax))

g.add((ontology_ns[organization], ontology_ns["organizationemail"], Literal(org_email,datatype=xsd_ns["string"])))



# Bounding box


dataset_location = "{0}_location".format(dataset_title)
g.add((hydro_dataset_ml, terms["spatial"], ontology_ns[dataset_location] ))
g.add((ontology_ns[dataset_location], RDF.type, Spatial))
g.add((ontology_ns[dataset_location], dcat["bbox"], 
                              Literal(hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Geographic Bounding Box:', 'Description'].values[0],
                              datatype=xsd_ns["string"])))
# Temporal

dataset_temporal = "{0}_temporal".format(dataset_title)
g.add((hydro_dataset_ml, terms["temporal"], ontology_ns[dataset_temporal] ))
g.add(( ontology_ns[dataset_temporal] , RDF.type, PeriodOfTime))

start_date =''
end_date = ''
g.add(( ontology_ns[dataset_temporal] , dcat["startDate"], Literal(start_date, datatype=xsd_ns["string"])))
g.add(( ontology_ns[dataset_temporal] , dcat["endDate"], Literal(end_date, datatype=xsd_ns["string"])))


# Frequency
frequency = ''

g.add((hydro_dataset_ml, terms["accrualPeriodicity"],Literal(frequency, datatype=xsd_ns["string"])))



# Distribution

distribution = ''
dataset_distribution = "distribution_unknown03"



# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_ml, dcat["distribution"], ontology_ns[dataset_distribution] ))
g.add((ontology_ns[dataset_distribution], RDF.type, Distribution))


# Access right

access = ''
dataset_access = "access_unknown03"



# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_ml, terms["accessRights"], ontology_ns[dataset_access] ))
g.add((ontology_ns[dataset_access], RDF.type, RightsStatement))


# Accuracy

positional_accuracy = ontology_ns["{0}_positional_accuracy".format(dataset_title)]
attribute_accuracy = ontology_ns["{0}_attribute_accuracy".format(dataset_title)]
logical_consistency = ontology_ns["{0}_logical_consistency".format(dataset_title)]
accessibility_1 = ontology_ns["{0}_accessibility".format(dataset_title)]


positional_accuracy_metric = ontology_ns["{0}_positional_accuracy_metric".format(dataset_title)]
attribute_accuracy_metric = ontology_ns["{0}_attribute_accuracy_metric".format(dataset_title)]
logical_consistency_metric = ontology_ns["{0}_logical_consistency_metric".format(dataset_title)]
accessibility_metric = ontology_ns["{0}_accessibility_metric".format(dataset_title)]

accuracy = ontology_ns["accuracy_ML"]
consistency = ontology_ns["consistency_ML"]
accessibility = ontology_ns["accessibility_ML"]



g.add((hydro_dataset_ml, dqv["hasQualityMeasurement"], positional_accuracy))
g.add((positional_accuracy, RDF.type, QualityMeasurement))
g.add((positional_accuracy, dqv["value"], Literal("+/-50", datatype=xsd_ns["string"])))
g.add((positional_accuracy, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((positional_accuracy, dqv["isMeasurementOf"], positional_accuracy_metric))

g.add((positional_accuracy_metric, RDF.type, Metric))
# g.add((positional_accuracy_metric, dqv["value"], Literal("+/-30", datatype=xsd_ns["string"])))
g.add((positional_accuracy_metric, dqv["inDimension"], accuracy))
g.add((accuracy, RDF.type, Dimension))


g.add((hydro_dataset_ml, dqv["hasQualityMeasurement"], attribute_accuracy))
g.add((attribute_accuracy, RDF.type, QualityMeasurement))
g.add((attribute_accuracy, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((attribute_accuracy, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((attribute_accuracy, dqv["isMeasurementOf"], attribute_accuracy_metric))
g.add((attribute_accuracy_metric, RDF.type, Metric))
g.add((attribute_accuracy_metric, dqv["inDimension"], accuracy))


g.add((hydro_dataset_ml, dqv["hasQualityMeasurement"], logical_consistency))
g.add((logical_consistency, RDF.type, QualityMeasurement))
g.add((logical_consistency, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((logical_consistency, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((logical_consistency, dqv["isMeasurementOf"], logical_consistency_metric))
g.add((logical_consistency_metric, RDF.type, Metric))
g.add((logical_consistency_metric, dqv["inDimension"], consistency))
g.add((consistency, RDF.type, Dimension))


g.add((hydro_dataset_ml, dqv["hasQualityMeasurement"], accessibility_1))
g.add((accessibility_1, RDF.type, QualityMeasurement))
g.add((accessibility_1, dqv["value"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, dqv["isMeasurementOf"], accessibility_metric))
g.add((accessibility_metric, RDF.type, Metric))
g.add((accessibility_metric, dqv["inDimension"], accessibility))
g.add((accessibility, RDF.type, Dimension))



#%% Metadata for lidar


# Define Dataset instance

dataset_title = 'HY_WATER_AREA_LIDAR'
available_date = '05/03/2020'
hydro_dataset_lidar = ontology_ns[dataset_title]
g.add((hydro_dataset_lidar, RDF.type, Dataset))

 
## Define data properties of dataset instance

g.add((hydro_dataset_lidar, terms['abstract'], 
      Literal(" ", datatype=xsd_ns["string"])))


g.add((hydro_dataset_lidar, terms['description'],
      Literal('',datatype=xsd_ns["string"])))
      
g.add((hydro_dataset_lidar, terms['identifier'], 
      Literal('', datatype=xsd_ns["string"])))
      
      
g.add((hydro_dataset_lidar, dcat['keyword'],
      Literal('', datatype=xsd_ns["string"])))

      
g.add((hydro_dataset_lidar, terms['source'],
      Literal('', datatype=xsd_ns["string"])))

g.add((hydro_dataset_lidar, terms['available'], Literal(available_date, datatype=xsd_ns["date"])))

g.add((hydro_dataset_lidar, terms["title"], Literal(dataset_title,datatype=xsd_ns["string"])))


## Define object properties of dataset instance

# Contact point

contact = "vcard04"
organization = "organization_Woolpert"
role = ''
address = ''
org_address = "address_Suite3,Level_23,6_O’Connell_Street_Sydney,NSW_2000"
    
telephone =''
org_tel = "telephone_61288791600"

facsimile = ''
org_fax = "fax_unknown04"

email = ''
org_email = "email_unknown04"


url = 'https://aamgroup.com/contact-us/'
countryName = 'Australia'
locality = ''
region = ''


g.add((hydro_dataset_lidar, dcat["contactPoint"],ontology_ns[contact] ))
g.add((ontology_ns[contact], RDF.type, Kind))
# g.add((ontology_ns[organization], RDFS.subClassOf,ontology_ns[contact]))
g.add((ontology_ns[organization], RDF.type, Organization))



g.add((ontology_ns[organization], ns["country-name"], Literal(countryName,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["locality"], Literal(locality,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["region"], Literal(region,datatype=xsd_ns["string"])))


g.add((ontology_ns[organization], ns["street-address"], Literal(address,datatype=xsd_ns["string"])))


g.add((ontology_ns[organization], ns["hasTelephone"], ontology_ns["Phone04"]))
g.add((ontology_ns["Phone04"], RDF.type, TelephoneType))
g.add((ontology_ns[org_tel], RDF.type, ns["Cell"]))
g.add((ontology_ns[org_fax], RDF.type, Fax))

g.add((ontology_ns[organization], ontology_ns["organizationemail"], Literal(org_email,datatype=xsd_ns["string"])))



# Bounding box


dataset_location = "{0}_location".format(dataset_title)
g.add((hydro_dataset_lidar, terms["spatial"], ontology_ns[dataset_location] ))
g.add((ontology_ns[dataset_location], RDF.type, Spatial))
g.add((ontology_ns[dataset_location], dcat["bbox"], 
                              Literal(hydro_point_metadata.loc[hydro_point_metadata['Metadata'] == 'Geographic Bounding Box:', 'Description'].values[0],
                              datatype=xsd_ns["string"])))
# Temporal

dataset_temporal = "{0}_temporal".format(dataset_title)
g.add((hydro_dataset_lidar, terms["temporal"], ontology_ns[dataset_temporal] ))
g.add(( ontology_ns[dataset_temporal] , RDF.type, PeriodOfTime))

start_date =''
end_date = ''
g.add(( ontology_ns[dataset_temporal] , dcat["startDate"], Literal(start_date, datatype=xsd_ns["string"])))
g.add(( ontology_ns[dataset_temporal] , dcat["endDate"], Literal(end_date, datatype=xsd_ns["string"])))


# Frequency
frequency = ''

g.add((hydro_dataset_lidar, terms["accrualPeriodicity"],Literal(frequency, datatype=xsd_ns["string"])))



# Distribution

distribution = ''
dataset_distribution = "distribution_unknown04"



# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_lidar, dcat["distribution"], ontology_ns[dataset_distribution] ))
g.add((ontology_ns[dataset_distribution], RDF.type, Distribution))


# Access right

access = ''
dataset_access = "access_unknown04"



# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_lidar, terms["accessRights"], ontology_ns[dataset_access] ))
g.add((ontology_ns[dataset_access], RDF.type, RightsStatement))


# Accuracy

positional_accuracy = ontology_ns["{0}_positional_accuracy".format(dataset_title)]
attribute_accuracy = ontology_ns["{0}_attribute_accuracy".format(dataset_title)]
logical_consistency = ontology_ns["{0}_logical_consistency".format(dataset_title)]
accessibility_1 = ontology_ns["{0}_accessibility".format(dataset_title)]


positional_accuracy_metric = ontology_ns["{0}_positional_accuracy_metric".format(dataset_title)]
attribute_accuracy_metric = ontology_ns["{0}_attribute_accuracy_metric".format(dataset_title)]
logical_consistency_metric = ontology_ns["{0}_logical_consistency_metric".format(dataset_title)]
accessibility_metric = ontology_ns["{0}_accessibility_metric".format(dataset_title)]

accuracy = ontology_ns["accuracy_LIDAR"]
consistency = ontology_ns["consistency_LIDAR"]
accessibility = ontology_ns["accessibility_LIDAR"]



g.add((hydro_dataset_lidar, dqv["hasQualityMeasurement"], positional_accuracy))
g.add((positional_accuracy, RDF.type, QualityMeasurement))
g.add((positional_accuracy, dqv["value"], Literal("2m", datatype=xsd_ns["string"])))
g.add((positional_accuracy, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((positional_accuracy, dqv["isMeasurementOf"], positional_accuracy_metric))

g.add((positional_accuracy_metric, RDF.type, Metric))
# g.add((positional_accuracy_metric, dqv["value"], Literal("+/-30", datatype=xsd_ns["string"])))
g.add((positional_accuracy_metric, dqv["inDimension"], accuracy))
g.add((accuracy, RDF.type, Dimension))


g.add((hydro_dataset_lidar, dqv["hasQualityMeasurement"], attribute_accuracy))
g.add((attribute_accuracy, RDF.type, QualityMeasurement))
g.add((attribute_accuracy, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((attribute_accuracy, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((attribute_accuracy, dqv["isMeasurementOf"], attribute_accuracy_metric))
g.add((attribute_accuracy_metric, RDF.type, Metric))
g.add((attribute_accuracy_metric, dqv["inDimension"], accuracy))


g.add((hydro_dataset_lidar, dqv["hasQualityMeasurement"], logical_consistency))
g.add((logical_consistency, RDF.type, QualityMeasurement))
g.add((logical_consistency, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((logical_consistency, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((logical_consistency, dqv["isMeasurementOf"], logical_consistency_metric))
g.add((logical_consistency_metric, RDF.type, Metric))
g.add((logical_consistency_metric, dqv["inDimension"], consistency))
g.add((consistency, RDF.type, Dimension))


g.add((hydro_dataset_lidar, dqv["hasQualityMeasurement"], accessibility_1))
g.add((accessibility_1, RDF.type, QualityMeasurement))
g.add((accessibility_1, dqv["value"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, dqv["isMeasurementOf"], accessibility_metric))
g.add((accessibility_metric, RDF.type, Metric))
g.add((accessibility_metric, dqv["inDimension"], accessibility))
g.add((accessibility, RDF.type, Dimension))




#%% Metadata for parcels

## Define Dataset instance

dataset_title = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Resource Name:', 'Description'].values[0]
available_date = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Metadata Date:', 'Description'].values[0]
title = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Title:', 'Description'].values[0]

hydro_dataset_parcels = ontology_ns[dataset_title]
g.add((hydro_dataset_parcels, RDF.type, Dataset))

 
## Define data properties of dataset instance

g.add((hydro_dataset_parcels, terms['abstract'], 
      Literal(parcels_metadata.loc[parcels_metadata['Metadata'] == 'Abstract:', 'Description'].values[0],
      datatype=xsd_ns["string"])))


g.add((hydro_dataset_parcels, terms['description'],
      Literal(parcels_metadata.loc[parcels_metadata['Metadata'] == 'Purpose:', 'Description'].values[0],
      datatype=xsd_ns["string"])))
      
g.add((hydro_dataset_parcels, terms['identifier'], 
      Literal(parcels_metadata.loc[parcels_metadata['Metadata'] == 'Anzlic ID:', 'Description'].values[0],
      datatype=xsd_ns["string"])))
      
      
g.add((hydro_dataset_parcels, dcat['keyword'],
      Literal(parcels_metadata.loc[parcels_metadata['Metadata'] == 'Search Words:', 'Description'].values[0],
      datatype=xsd_ns["string"])))

      
g.add((hydro_dataset_parcels, terms['source'],
      Literal(parcels_metadata.loc[parcels_metadata['Metadata'] == 'Data Source:', 'Description'].values[0],
      datatype=xsd_ns["string"])))

g.add((hydro_dataset_parcels, terms['available'], Literal(available_date, datatype=xsd_ns["date"])))

g.add((hydro_dataset_parcels, terms["title"], Literal(title,datatype=xsd_ns["string"])))


## Define object properties of dataset instance

# Contact point

contact = "vcard05"
organization = "organization05"
role = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Contact Position:', 'Description'].values[0]
address = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Address:', 'Description'].values[0]
# if address == "":
#     org_address = ""
# else:
#     org_address = "{0}".format(address)
    
telephone = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Telephone:', 'Description'].values[0]
if telephone == "":
    org_tel = "telephone_unknown05"
else:
    org_tel = "telephone_{0}".format(telephone)


facsimile = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Facsimile:', 'Description'].values[0]
if facsimile == "":
    org_fax = "fax_unknown05"
else:
    org_fax = "fax{0}".format(facsimile)
    
email = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Email Address:', 'Description'].values[0]
# if email == "":
#     org_email = "email_unknown01"
# else:
#     org_email = "email{0}".format(email)

# url = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Additional Metadata:', 'Description'].values[0]
countryName = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Country Name:', 'Description'].values[0]
locality = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Locality:', 'Description'].values[0]
region = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Region:', 'Description'].values[0]


g.add((hydro_dataset_parcels, dcat["contactPoint"],ontology_ns[contact] ))
g.add((ontology_ns[contact], RDF.type, Kind))
#g.add((ontology_ns[organization], RDFS.subClassOf,ontology_ns[contact]))
g.add((ontology_ns[organization], RDF.type, Organization))



g.add((ontology_ns[organization], ns["country-name"], Literal(countryName,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["locality"], Literal(locality,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["region"], Literal(region,datatype=xsd_ns["string"])))
#g.add((ontology_ns[organization], ontology_ns["hasURL"], Literal(url,datatype=xsd_ns["string"])))



g.add((ontology_ns[organization], ns["street-address"], Literal(address,datatype=xsd_ns["string"])))
# g.add((ontology_ns[org_address], RDF.type, Address))

g.add((ontology_ns[organization], ns["hasTelephone"], ontology_ns["Phone05"]))
g.add((ontology_ns["Phone05"], RDF.type, TelephoneType))
# g.add((ontology_ns[org_tel], RDFS.subClassOf, ontology_ns["Phone01"]))
g.add((ontology_ns[org_tel], RDF.type, ns["Cell"]))
# g.add((ontology_ns[org_fax], RDFS.subClassOf, ontology_ns["Phone01"]))
g.add((ontology_ns[org_fax], RDF.type, Fax))

g.add((ontology_ns[organization], ontology_ns["organizationemail"], Literal(email,datatype=xsd_ns["string"])))
# g.add((ontology_ns[org_email], RDF.type, ns["Email"]))

# Custodian
custodian = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Custodian:', 'Description'].values[0]
if pd.isnull(custodian) is True:
    dataset_agency = "custodian_unknown05"
else:
    dataset_agency = "custodian_{0}".format(custodian)

#dataset_agency = ontology_ns["{0}_agency".format(dataset_title)]
g.add((hydro_dataset_parcels, fsdf["hasCustodian"], ontology_ns[dataset_agency] ))
g.add((ontology_ns[dataset_agency] , RDF.type, Agency))
# g.add((ontology_ns[dataset_agency], RDFS.subClassOf, ontology_ns[organization]))


# Jurisdication
jurisdiction = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Jurisdiction:', 'Description'].values[0]
if pd.isnull(jurisdiction) is True:
    dataset_jurisdiction = "jurisdiction_unknown05"
else:
    dataset_jurisdiction = "jurisdiction_{0}".format(jurisdiction)
    
#dataset_jurisdiction = ontology_ns["{0}_jurisdiction".format(dataset_title)]
g.add((hydro_dataset_parcels, fsdf["hasJurisdiction"], ontology_ns[dataset_jurisdiction] ))
g.add((ontology_ns[dataset_jurisdiction], RDF.type, Jurisdiction))
# g.add((ontology_ns[dataset_jurisdiction], RDFS.subClassOf, ontology_ns[organization]))

# Bounding box

dataset_location = "{0}_location".format(dataset_title)
g.add((hydro_dataset_parcels, terms["spatial"], ontology_ns[dataset_location] ))
g.add((ontology_ns[dataset_location], RDF.type, Spatial))
g.add((ontology_ns[dataset_location], dcat["bbox"], 
                              Literal(parcels_metadata.loc[parcels_metadata['Metadata'] == 'Geographic Bounding Box:', 'Description'].values[0],
                              datatype=xsd_ns["string"])))


# Temporal][]

dataset_temporal = "{0}_temporal".format(dataset_title)
g.add((hydro_dataset_parcels, terms["temporal"], ontology_ns[dataset_temporal] ))
g.add(( ontology_ns[dataset_temporal] , RDF.type, PeriodOfTime))

start_date = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Beginning to Ending Date:', 'Description'].values[0].split(" - ")[0]
end_date = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Beginning to Ending Date:', 'Description'].values[0].split(" - ")[1]
g.add(( ontology_ns[dataset_temporal] , dcat["startDate"], Literal(start_date, datatype=xsd_ns["string"])))
g.add(( ontology_ns[dataset_temporal] , dcat["endDate"], Literal(end_date, datatype=xsd_ns["string"])))


# Frequency
frequency = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Maintainence and Update Frequency:', 'Description'].values[0]
# if pd.isnull(frequency) is True:
#     dataset_frequency = "frequency_unknown01"
# else:
#     dataset_frequency = "frequency_{0}".format(frequency)
    
#dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_parcels, terms["accrualPeriodicity"],Literal(frequency, datatype=xsd_ns["string"])))
# g.add((ontology_ns[dataset_frequency], RDF.type, Frequency))


# Distribution

distribution = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Stored Data Format:', 'Description'].values[0]
if pd.isnull(distribution) is True:
    dataset_distribution = "distribution_unknown05"
else:
    dataset_distribution = "distribution_{0}".format(distribution)


# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_parcels, dcat["distribution"], ontology_ns[dataset_distribution] ))
g.add((ontology_ns[dataset_distribution], RDF.type, Distribution))


# Access right

access = parcels_metadata.loc[parcels_metadata['Metadata'] == 'Access Constraint:', 'Description'].values[0]
if pd.isnull(access) is True:
    dataset_access = "access_unknown05"
else:
    dataset_access = "access_{0}".format(distribution)


# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_parcels, terms["accessRights"], ontology_ns[dataset_access] ))
g.add((ontology_ns[dataset_access], RDF.type, RightsStatement))


# Accuracy

positional_accuracy = ontology_ns["{0}_positional_accuracy".format(dataset_title)]
attribute_accuracy = ontology_ns["{0}_attribute_accuracy".format(dataset_title)]
logical_consistency = ontology_ns["{0}_logical_consistency".format(dataset_title)]
accessibility_1 = ontology_ns["{0}_accessibility".format(dataset_title)]


positional_accuracy_metric = ontology_ns["{0}_positional_accuracy_metric".format(dataset_title)]
attribute_accuracy_metric = ontology_ns["{0}_attribute_accuracy_metric".format(dataset_title)]
logical_consistency_metric = ontology_ns["{0}_logical_consistency_metric".format(dataset_title)]
accessibility_metric = ontology_ns["{0}_accessibility_metric".format(dataset_title)]

accuracy = ontology_ns["accuracy_parcels"]
consistency = ontology_ns["consistency_parcels"]
accessibility = ontology_ns["accessibility_parcels"]



g.add((hydro_dataset_parcels, dqv["hasQualityMeasurement"], positional_accuracy))
g.add((positional_accuracy, RDF.type, QualityMeasurement))
g.add((positional_accuracy, dqv["value"], Literal("+/-25", datatype=xsd_ns["string"])))
g.add((positional_accuracy, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((positional_accuracy, dqv["isMeasurementOf"], positional_accuracy_metric))

g.add((positional_accuracy_metric, RDF.type, Metric))
# g.add((positional_accuracy_metric, dqv["value"], Literal("+/-30", datatype=xsd_ns["string"])))
g.add((positional_accuracy_metric, dqv["inDimension"], accuracy))
g.add((accuracy, RDF.type, Dimension))


g.add((hydro_dataset_parcels, dqv["hasQualityMeasurement"], attribute_accuracy))
g.add((attribute_accuracy, RDF.type, QualityMeasurement))
g.add((attribute_accuracy, dqv["value"], Literal("1%-5%", datatype=xsd_ns["string"])))
g.add((attribute_accuracy, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((attribute_accuracy, dqv["isMeasurementOf"], attribute_accuracy_metric))
g.add((attribute_accuracy_metric, RDF.type, Metric))
g.add((attribute_accuracy_metric, dqv["inDimension"], accuracy))


g.add((hydro_dataset_parcels, dqv["hasQualityMeasurement"], logical_consistency))
g.add((logical_consistency, RDF.type, QualityMeasurement))
g.add((logical_consistency, dqv["value"], Literal("3%-5%", datatype=xsd_ns["string"])))
g.add((logical_consistency, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((logical_consistency, dqv["isMeasurementOf"], logical_consistency_metric))
g.add((logical_consistency_metric, RDF.type, Metric))
g.add((logical_consistency_metric, dqv["inDimension"], consistency))
g.add((consistency, RDF.type, Dimension))


g.add((hydro_dataset_parcels, dqv["hasQualityMeasurement"], accessibility_1))
g.add((accessibility_1, RDF.type, QualityMeasurement))
g.add((accessibility_1, dqv["value"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, dqv["isMeasurementOf"], accessibility_metric))
g.add((accessibility_metric, RDF.type, Metric))
g.add((accessibility_metric, dqv["inDimension"], accessibility))
g.add((accessibility, RDF.type, Dimension))


#%% Metadata for flood authoritative

## Define Dataset instance

dataset_title = flood_metadata.loc[flood_metadata['Metadata'] == 'Resource Name:', 'Description'].values[0]
available_date = flood_metadata.loc[flood_metadata['Metadata'] == 'Metadata Date:', 'Description'].values[0]
title = flood_metadata.loc[flood_metadata['Metadata'] == 'Title:', 'Description'].values[0]

hydro_dataset_flood = ontology_ns[dataset_title]
g.add((hydro_dataset_flood, RDF.type, Dataset))

 
## Define data properties of dataset instance

g.add((hydro_dataset_flood, terms['abstract'], 
      Literal(flood_metadata.loc[flood_metadata['Metadata'] == 'Abstract:', 'Description'].values[0],
      datatype=xsd_ns["string"])))


g.add((hydro_dataset_flood, terms['description'],
      Literal(flood_metadata.loc[flood_metadata['Metadata'] == 'Purpose:', 'Description'].values[0],
      datatype=xsd_ns["string"])))
      
g.add((hydro_dataset_flood, terms['identifier'], 
      Literal(flood_metadata.loc[flood_metadata['Metadata'] == 'Anzlic ID:', 'Description'].values[0],
      datatype=xsd_ns["string"])))
      
      
g.add((hydro_dataset_flood, dcat['keyword'],
      Literal(flood_metadata.loc[flood_metadata['Metadata'] == 'Search Words:', 'Description'].values[0],
      datatype=xsd_ns["string"])))

      
g.add((hydro_dataset_flood, terms['source'],
      Literal(flood_metadata.loc[flood_metadata['Metadata'] == 'Data Source:', 'Description'].values[0],
      datatype=xsd_ns["string"])))

g.add((hydro_dataset_flood, terms['available'], Literal(available_date, datatype=xsd_ns["date"])))

g.add((hydro_dataset_flood, terms["title"], Literal(title,datatype=xsd_ns["string"])))


## Define object properties of dataset instance

# Contact point

contact = "vcard06"
organization = "organization06"
role = flood_metadata.loc[flood_metadata['Metadata'] == 'Contact Position:', 'Description'].values[0]
address = flood_metadata.loc[flood_metadata['Metadata'] == 'Address:', 'Description'].values[0]
# if address == "":
#     org_address = ""
# else:
#     org_address = "{0}".format(address)
    
telephone = flood_metadata.loc[flood_metadata['Metadata'] == 'Telephone:', 'Description'].values[0]
if telephone == "":
    org_tel = "telephone_unknown06"
else:
    org_tel = "telephone_{0}".format(telephone)


facsimile = flood_metadata.loc[flood_metadata['Metadata'] == 'Facsimile:', 'Description'].values[0]
if facsimile == "":
    org_fax = "fax_unknown06"
else:
    org_fax = "fax{0}".format(facsimile)
    
email = flood_metadata.loc[flood_metadata['Metadata'] == 'Email Address:', 'Description'].values[0]
# if email == "":
#     org_email = "email_unknown01"
# else:
#     org_email = "email{0}".format(email)

# url = flood_metadata.loc[flood_metadata['Metadata'] == 'Additional Metadata:', 'Description'].values[0]
countryName = flood_metadata.loc[flood_metadata['Metadata'] == 'Country Name:', 'Description'].values[0]
locality = flood_metadata.loc[flood_metadata['Metadata'] == 'Locality:', 'Description'].values[0]
region = flood_metadata.loc[flood_metadata['Metadata'] == 'Region:', 'Description'].values[0]


g.add((hydro_dataset_flood, dcat["contactPoint"],ontology_ns[contact] ))
g.add((ontology_ns[contact], RDF.type, Kind))
#g.add((ontology_ns[organization], RDFS.subClassOf,ontology_ns[contact]))
g.add((ontology_ns[organization], RDF.type, Organization))



g.add((ontology_ns[organization], ns["country-name"], Literal(countryName,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["locality"], Literal(locality,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["region"], Literal(region,datatype=xsd_ns["string"])))
#g.add((ontology_ns[organization], ontology_ns["hasURL"], Literal(url,datatype=xsd_ns["string"])))



g.add((ontology_ns[organization], ns["street-address"], Literal(address,datatype=xsd_ns["string"])))
# g.add((ontology_ns[org_address], RDF.type, Address))

g.add((ontology_ns[organization], ns["hasTelephone"], ontology_ns["Phone06"]))
g.add((ontology_ns["Phone06"], RDF.type, TelephoneType))
# g.add((ontology_ns[org_tel], RDFS.subClassOf, ontology_ns["Phone01"]))
g.add((ontology_ns[org_tel], RDF.type, ns["Cell"]))
# g.add((ontology_ns[org_fax], RDFS.subClassOf, ontology_ns["Phone01"]))
g.add((ontology_ns[org_fax], RDF.type, Fax))

g.add((ontology_ns[organization], ontology_ns["organizationemail"], Literal(email,datatype=xsd_ns["string"])))
# g.add((ontology_ns[org_email], RDF.type, ns["Email"]))

# Custodian
custodian = flood_metadata.loc[flood_metadata['Metadata'] == 'Custodian:', 'Description'].values[0]
if pd.isnull(custodian) is True:
    dataset_agency = "custodian_unknown06"
else:
    dataset_agency = "custodian_{0}".format(custodian)

#dataset_agency = ontology_ns["{0}_agency".format(dataset_title)]
g.add((hydro_dataset_flood, fsdf["hasCustodian"], ontology_ns[dataset_agency] ))
g.add((ontology_ns[dataset_agency] , RDF.type, Agency))
# g.add((ontology_ns[dataset_agency], RDFS.subClassOf, ontology_ns[organization]))


# Jurisdication
jurisdiction = flood_metadata.loc[flood_metadata['Metadata'] == 'Jurisdiction:', 'Description'].values[0]
if pd.isnull(jurisdiction) is True:
    dataset_jurisdiction = "jurisdiction_unknown06"
else:
    dataset_jurisdiction = "jurisdiction_{0}".format(jurisdiction)
    
#dataset_jurisdiction = ontology_ns["{0}_jurisdiction".format(dataset_title)]
g.add((hydro_dataset_flood, fsdf["hasJurisdiction"], ontology_ns[dataset_jurisdiction] ))
g.add((ontology_ns[dataset_jurisdiction], RDF.type, Jurisdiction))
# g.add((ontology_ns[dataset_jurisdiction], RDFS.subClassOf, ontology_ns[organization]))

# Bounding box

dataset_location = "{0}_location".format(dataset_title)
g.add((hydro_dataset_flood, terms["spatial"], ontology_ns[dataset_location] ))
g.add((ontology_ns[dataset_location], RDF.type, Spatial))
g.add((ontology_ns[dataset_location], dcat["bbox"], 
                              Literal(flood_metadata.loc[flood_metadata['Metadata'] == 'Geographic Bounding Box:', 'Description'].values[0],
                              datatype=xsd_ns["string"])))


# Temporal][]

dataset_temporal = "{0}_temporal".format(dataset_title)
g.add((hydro_dataset_flood, terms["temporal"], ontology_ns[dataset_temporal] ))
g.add(( ontology_ns[dataset_temporal] , RDF.type, PeriodOfTime))

start_date = flood_metadata.loc[flood_metadata['Metadata'] == 'Beginning to Ending Date:', 'Description'].values[0].split(" - ")[0]
end_date = flood_metadata.loc[flood_metadata['Metadata'] == 'Beginning to Ending Date:', 'Description'].values[0].split(" - ")[1]
g.add(( ontology_ns[dataset_temporal] , dcat["startDate"], Literal(start_date, datatype=xsd_ns["string"])))
g.add(( ontology_ns[dataset_temporal] , dcat["endDate"], Literal(end_date, datatype=xsd_ns["string"])))


# Frequency
frequency = flood_metadata.loc[flood_metadata['Metadata'] == 'Maintainence and Update Frequency:', 'Description'].values[0]
# if pd.isnull(frequency) is True:
#     dataset_frequency = "frequency_unknown01"
# else:
#     dataset_frequency = "frequency_{0}".format(frequency)
    
#dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_flood, terms["accrualPeriodicity"],Literal(frequency, datatype=xsd_ns["string"])))
# g.add((ontology_ns[dataset_frequency], RDF.type, Frequency))


# Distribution

distribution = flood_metadata.loc[flood_metadata['Metadata'] == 'Stored Data Format:', 'Description'].values[0]
if pd.isnull(distribution) is True:
    dataset_distribution = "distribution_unknown06"
else:
    dataset_distribution = "distribution_{0}".format(distribution)


# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_flood, dcat["distribution"], ontology_ns[dataset_distribution] ))
g.add((ontology_ns[dataset_distribution], RDF.type, Distribution))


# Access right

access = flood_metadata.loc[flood_metadata['Metadata'] == 'Access Constraint:', 'Description'].values[0]
if pd.isnull(access) is True:
    dataset_access = "access_unknown06"
else:
    dataset_access = "access_{0}".format(distribution)


# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset_flood, terms["accessRights"], ontology_ns[dataset_access] ))
g.add((ontology_ns[dataset_access], RDF.type, RightsStatement))


# Accuracy

positional_accuracy = ontology_ns["{0}_positional_accuracy".format(dataset_title)]
attribute_accuracy = ontology_ns["{0}_attribute_accuracy".format(dataset_title)]
logical_consistency = ontology_ns["{0}_logical_consistency".format(dataset_title)]
accessibility_1 = ontology_ns["{0}_accessibility".format(dataset_title)]


positional_accuracy_metric = ontology_ns["{0}_positional_accuracy_metric".format(dataset_title)]
attribute_accuracy_metric = ontology_ns["{0}_attribute_accuracy_metric".format(dataset_title)]
logical_consistency_metric = ontology_ns["{0}_logical_consistency_metric".format(dataset_title)]
accessibility_metric = ontology_ns["{0}_accessibility_metric".format(dataset_title)]

accuracy = ontology_ns["accuracy_flood"]
consistency = ontology_ns["consistency_flood"]
accessibility = ontology_ns["accessibility_flood"]



g.add((hydro_dataset_flood, dqv["hasQualityMeasurement"], positional_accuracy))
g.add((positional_accuracy, RDF.type, QualityMeasurement))
g.add((positional_accuracy, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((positional_accuracy, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((positional_accuracy, dqv["isMeasurementOf"], positional_accuracy_metric))

g.add((positional_accuracy_metric, RDF.type, Metric))
# g.add((positional_accuracy_metric, dqv["value"], Literal("+/-30", datatype=xsd_ns["string"])))
g.add((positional_accuracy_metric, dqv["inDimension"], accuracy))
g.add((accuracy, RDF.type, Dimension))


g.add((hydro_dataset_flood, dqv["hasQualityMeasurement"], attribute_accuracy))
g.add((attribute_accuracy, RDF.type, QualityMeasurement))
g.add((attribute_accuracy, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((attribute_accuracy, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((attribute_accuracy, dqv["isMeasurementOf"], attribute_accuracy_metric))
g.add((attribute_accuracy_metric, RDF.type, Metric))
g.add((attribute_accuracy_metric, dqv["inDimension"], accuracy))


g.add((hydro_dataset_flood, dqv["hasQualityMeasurement"], logical_consistency))
g.add((logical_consistency, RDF.type, QualityMeasurement))
g.add((logical_consistency, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((logical_consistency, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((logical_consistency, dqv["isMeasurementOf"], logical_consistency_metric))
g.add((logical_consistency_metric, RDF.type, Metric))
g.add((logical_consistency_metric, dqv["inDimension"], consistency))
g.add((consistency, RDF.type, Dimension))


g.add((hydro_dataset_flood, dqv["hasQualityMeasurement"], accessibility_1))
g.add((accessibility_1, RDF.type, QualityMeasurement))
g.add((accessibility_1, dqv["value"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, ontology_ns["isAuthoritativeData"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, dqv["isMeasurementOf"], accessibility_metric))
g.add((accessibility_metric, RDF.type, Metric))
g.add((accessibility_metric, dqv["inDimension"], accessibility))
g.add((accessibility, RDF.type, Dimension))

#%% Metadata for flood Non-authoritative


# Define Dataset instance

dataset_title = 'Flood_NonAuthoritative_25Jan'
available_date = '00/00/0000'
flood_dataset_nonAuth = ontology_ns[dataset_title]
g.add((flood_dataset_nonAuth, RDF.type, Dataset))

 
## Define data properties of dataset instance

g.add((flood_dataset_nonAuth, terms['abstract'], 
      Literal(" ", datatype=xsd_ns["string"])))


g.add((flood_dataset_nonAuth, terms['description'],
      Literal('',datatype=xsd_ns["string"])))
      
g.add((flood_dataset_nonAuth, terms['identifier'], 
      Literal('', datatype=xsd_ns["string"])))
      
      
g.add((flood_dataset_nonAuth, dcat['keyword'],
      Literal('', datatype=xsd_ns["string"])))

      
g.add((flood_dataset_nonAuth, terms['source'],
      Literal('', datatype=xsd_ns["string"])))

g.add((flood_dataset_nonAuth, terms['available'], Literal(available_date, datatype=xsd_ns["date"])))

g.add((flood_dataset_nonAuth, terms["title"], Literal(dataset_title,datatype=xsd_ns["string"])))





## Define object properties of dataset instance

# Contact point

contact = "vcard07"
organization = "organization07"
role = ''
address = ''
org_address = "address_unknown07"
    
telephone =''
org_tel = "telephone_unknown07"

facsimile = ''
org_fax = "fax_unknown07"

email = ''
org_email = "email_unknown07"


url = ''
countryName = ''
locality = ''
region = ''


g.add((flood_dataset_nonAuth, dcat["contactPoint"],ontology_ns[contact] ))
g.add((ontology_ns[contact], RDF.type, Kind))
# g.add((ontology_ns[organization], RDFS.subClassOf,ontology_ns[contact]))
g.add((ontology_ns[organization], RDF.type, Organization))



g.add((ontology_ns[organization], ns["country-name"], Literal(countryName,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["locality"], Literal(locality,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["region"], Literal(region,datatype=xsd_ns["string"])))


g.add((ontology_ns[organization], ns["street-address"], Literal(address,datatype=xsd_ns["string"])))


g.add((ontology_ns[organization], ns["hasTelephone"], ontology_ns["Phone07"]))
g.add((ontology_ns["Phone07"], RDF.type, TelephoneType))
g.add((ontology_ns[org_tel], RDF.type, ns["Cell"]))
g.add((ontology_ns[org_fax], RDF.type, Fax))

g.add((ontology_ns[organization], ontology_ns["organizationemail"], Literal(org_email,datatype=xsd_ns["string"])))



# Bounding box


dataset_location = "{0}_location".format(dataset_title)
g.add((flood_dataset_nonAuth, terms["spatial"], ontology_ns[dataset_location] ))
g.add((ontology_ns[dataset_location], RDF.type, Spatial))
g.add((ontology_ns[dataset_location], dcat["bbox"], 
                              Literal(flood_metadata.loc[hydro_point_metadata['Metadata'] == 'Geographic Bounding Box:', 'Description'].values[0],
                              datatype=xsd_ns["string"])))
# Temporal

dataset_temporal = "{0}_temporal".format(dataset_title)
g.add((flood_dataset_nonAuth, terms["temporal"], ontology_ns[dataset_temporal] ))
g.add(( ontology_ns[dataset_temporal] , RDF.type, PeriodOfTime))

start_date =''
end_date = ''
g.add(( ontology_ns[dataset_temporal] , dcat["startDate"], Literal(start_date, datatype=xsd_ns["string"])))
g.add(( ontology_ns[dataset_temporal] , dcat["endDate"], Literal(end_date, datatype=xsd_ns["string"])))


# Frequency
frequency = ''

g.add((flood_dataset_nonAuth, terms["accrualPeriodicity"],Literal(frequency, datatype=xsd_ns["string"])))



# Distribution

distribution = ''
dataset_distribution = "distribution_unknown07"



# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((flood_dataset_nonAuth, dcat["distribution"], ontology_ns[dataset_distribution] ))
g.add((ontology_ns[dataset_distribution], RDF.type, Distribution))


# Access right

access = ''
dataset_access = "access_unknown07"



# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((flood_dataset_nonAuth, terms["accessRights"], ontology_ns[dataset_access] ))
g.add((ontology_ns[dataset_access], RDF.type, RightsStatement))


# Accuracy

positional_accuracy = ontology_ns["{0}_positional_accuracy".format(dataset_title)]
attribute_accuracy = ontology_ns["{0}_attribute_accuracy".format(dataset_title)]
logical_consistency = ontology_ns["{0}_logical_consistency".format(dataset_title)]
accessibility_1 = ontology_ns["{0}_accessibility".format(dataset_title)]


positional_accuracy_metric = ontology_ns["{0}_positional_accuracy_metric".format(dataset_title)]
attribute_accuracy_metric = ontology_ns["{0}_attribute_accuracy_metric".format(dataset_title)]
logical_consistency_metric = ontology_ns["{0}_logical_consistency_metric".format(dataset_title)]
accessibility_metric = ontology_ns["{0}_accessibility_metric".format(dataset_title)]

accuracy = ontology_ns["accuracy_FloodNA"]
consistency = ontology_ns["consistency_FloodNA"]
accessibility = ontology_ns["accessibility_FloodNA"]



g.add((flood_dataset_nonAuth, dqv["hasQualityMeasurement"], positional_accuracy))
g.add((positional_accuracy, RDF.type, QualityMeasurement))
g.add((positional_accuracy, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((positional_accuracy, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((positional_accuracy, dqv["isMeasurementOf"], positional_accuracy_metric))

g.add((positional_accuracy_metric, RDF.type, Metric))
# g.add((positional_accuracy_metric, dqv["value"], Literal("+/-30", datatype=xsd_ns["string"])))
g.add((positional_accuracy_metric, dqv["inDimension"], accuracy))
g.add((accuracy, RDF.type, Dimension))


g.add((flood_dataset_nonAuth, dqv["hasQualityMeasurement"], attribute_accuracy))
g.add((attribute_accuracy, RDF.type, QualityMeasurement))
g.add((attribute_accuracy, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((attribute_accuracy, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((attribute_accuracy, dqv["isMeasurementOf"], attribute_accuracy_metric))
g.add((attribute_accuracy_metric, RDF.type, Metric))
g.add((attribute_accuracy_metric, dqv["inDimension"], accuracy))


g.add((flood_dataset_nonAuth, dqv["hasQualityMeasurement"], logical_consistency))
g.add((logical_consistency, RDF.type, QualityMeasurement))
g.add((logical_consistency, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((logical_consistency, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((logical_consistency, dqv["isMeasurementOf"], logical_consistency_metric))
g.add((logical_consistency_metric, RDF.type, Metric))
g.add((logical_consistency_metric, dqv["inDimension"], consistency))
g.add((consistency, RDF.type, Dimension))


g.add((flood_dataset_nonAuth, dqv["hasQualityMeasurement"], accessibility_1))
g.add((accessibility_1, RDF.type, QualityMeasurement))
g.add((accessibility_1, dqv["value"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, ontology_ns["isAuthoritativeData"], Literal("False", datatype=xsd_ns["boolean"])))
g.add((accessibility_1, dqv["isMeasurementOf"], accessibility_metric))
g.add((accessibility_metric, RDF.type, Metric))
g.add((accessibility_metric, dqv["inDimension"], accessibility))
g.add((accessibility, RDF.type, Dimension))


#%% KG creation stage: Populating Ontology

# def convert_date(date_string):
#     if len(date_string) == 14:
#         # Format: 'YYYYMMDDHHMMSS'
#         date_object = datetime.strptime(date_string, '%Y%m%d%H%M%S')
#     elif len(date_string) == 8:
#         # Format: 'YYYYMMDD'
#         date_object = datetime.strptime(date_string, '%Y%m%d')
#     else:
#         raise ValueError("Date format not recognized")

#     formatted_date = date_object.strftime('%d/%m/%Y')
#     return formatted_date

total_data = pd.read_pickle('dataset_total.pickle')


  
k =0
source = {"source":"name"}

# RDFname = "KG_State_Hydro_Parcel_Flood.rdf"
RDFname = "KG_State_Updated_10K.rdf"

for index, i in enumerate(total_data[0:10000]):
    

    ## Multi-representation feature: wb_instance
    
    if type(i) ==tuple :
        wb_instance = ontology_ns["wb{0}".format(index)]
        g.add((wb_instance, RDF.type, Feature))        
        # g.add((wb_instance, ontology_ns.isType, Literal("Waterbody", datatype=xsd_ns["string"])))
        g.add((wb_instance, ontology_ns.waterbodyID, Literal(index, datatype=xsd_ns["integer"])))

        
        
        for index1, j in enumerate(i):
            
            if isinstance(j, pd.Series):
            
                
                ## Define geometry instances
                
                wb_geometry = j["geometry"].geom_type
                wb_geometry_instance = ontology_ns["{0}{1}".format(wb_geometry,k)]
                
    
                ## Define wb instance object properties
                
                g.add((wb_instance, geosparql["hasGeometry"], wb_geometry_instance))
                g.add((wb_geometry_instance, RDF.type, Geometry))
                
            
                ## Define geometry data/object properties
                if j['UFI'] is not None and j['PFI'] is not None:
                    
                    if j['geometry'].geom_type =="Polygon":
                        g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_polygon))
                        
                        g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(j['PFI'], datatype=xsd_ns["integer"])))
                        g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(j['UFI'], datatype=xsd_ns["integer"])))
                        g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))

                        # date = datetime.strptime(j['C_DATE_PFI'], '%Y%m%d%H%M%S').strftime('%d/%m/%Y')
                        
                        g.add((wb_geometry_instance, ontology_ns["createDate"],\
                            Literal(j['C_DATE_PFI'] ,datatype=xsd_ns["date"])))
                        
                        g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(j['geometry'], datatype=geosparql['wktLiteral'])))
                                           
                        g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(j['F_TYPE_COD'], datatype=xsd_ns["string"])))
                                      
                        # g.serialize(destination=RDFname, format="xml")
                        k +=1
                        
                    
                    else:
                        g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_point))
                        
                        g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(j['PFI'], datatype=xsd_ns["integer"])))
                        g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(j['UFI'], datatype=xsd_ns["integer"])))
                        g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))
                        
                        # date = datetime.strptime(j['C_DATE_PFI'], '%Y%m%d').strftime('%d/%m/%Y')
                        
                        g.add((wb_geometry_instance, ontology_ns["createDate"],\
                            Literal(j['C_DATE_PFI'] ,datatype=xsd_ns["date"])))
                        
                        g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(j['geometry'], datatype=geosparql['wktLiteral'])))
                                           
                        g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(j['F_TYPE_COD'], datatype=xsd_ns["string"])))
                                      
                        # g.serialize(destination=RDFname, format="xml")
                        k +=1
                    
                    
                    
                elif j['UFI'] is not None and type(j['PFI']) == type(None):
                    
                    
                    g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_ml))
                    
                    g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(j['PFI'], datatype=xsd_ns["integer"])))
                    g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(j['UFI'], datatype=xsd_ns["integer"])))
                    g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))
                    
                    # parsed_date = parser.parse(j['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                    g.add((wb_geometry_instance, ontology_ns["createDate"],\
                        Literal(j['C_DATE_PFI'],datatype=xsd_ns["date"])))
                    
                    g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(j['geometry'], datatype=geosparql['wktLiteral'])))
                                       
                    g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(j['F_TYPE_COD'], datatype=xsd_ns["string"])))
                    
              
                    # g.serialize(destination=RDFname, format="xml")
                    k +=1
                    
                else:
                    g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_lidar))
                    
                    g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(j['PFI'], datatype=xsd_ns["integer"])))
                    g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(j['UFI'], datatype=xsd_ns["integer"])))
                    g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))
                    
                    # parsed_date = parser.parse(j['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                    g.add((wb_geometry_instance, ontology_ns["createDate"],\
                        Literal(j['C_DATE_PFI'],datatype=xsd_ns["date"])))
                    
                    g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(j['geometry'], datatype=geosparql['wktLiteral'])))
                                       
                    g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(j['F_TYPE_COD'], datatype=xsd_ns["string"])))
                    
              
                    # g.serialize(destination=RDFname, format="xml")
                    k +=1
                    
            else:
                
                for index, m in j.iterrows():
                    
                    ## Define geometry instances
                    
                    wb_geometry = m["geometry"].geom_type
                    wb_geometry_instance = ontology_ns["{0}{1}".format(wb_geometry,k)]
                    
        
                    ## Define wb instance object properties
                    
                    g.add((wb_instance, geosparql["hasGeometry"], wb_geometry_instance))
                    g.add((wb_geometry_instance, RDF.type, Geometry))
                    
                    
                    ## Define geometry data/object properties
                    if m['UFI'] is not None and m['PFI'] is not None:
                        
                        if m['geometry'].geom_type =="Polygon":
                            
                            
                            g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_polygon))
                            
                            g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(m['PFI'], datatype=xsd_ns["integer"])))
                            g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(m['UFI'], datatype=xsd_ns["integer"])))
                            g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))
                            # parsed_date = parser.parse(m['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                            
                            # date = datetime.strptime(m['C_DATE_PFI'], '%Y%m%d%H%M%S').strftime('%d/%m/%Y')
                            g.add((wb_geometry_instance, ontology_ns["createDate"],\
                                Literal(m['C_DATE_PFI'] ,datatype=xsd_ns["date"])))
                                
                            
                            g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(m['geometry'], datatype=geosparql['wktLiteral'])))
                                               
                            g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(m['F_TYPE_COD'], datatype=xsd_ns["string"])))
                            
                      
                            # g.serialize(destination=RDFname, format="xml")
    
                            k +=1
                            
                            
                        else:
                            
                        
                            g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_point))
                            
                            g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(m['PFI'], datatype=xsd_ns["integer"])))
                            g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(m['UFI'], datatype=xsd_ns["integer"])))
                            g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))
                            # parsed_date = parser.parse(m['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                            
                            # date = datetime.strptime(m['C_DATE_PFI'], '%Y%m%d').strftime('%d/%m/%Y')
                            
                            g.add((wb_geometry_instance, ontology_ns["createDate"],\
                                Literal(m['C_DATE_PFI'] ,datatype=xsd_ns["date"])))
                            
                           
                            g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(m['geometry'], datatype=geosparql['wktLiteral'])))
                                               
                            g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(m['F_TYPE_COD'], datatype=xsd_ns["string"])))
                            
                      
                            # g.serialize(destination=RDFname, format="xml")
    
                            k +=1

                        
                        
                    elif m['UFI'] is not None and type(m['PFI']) == type(None):
                        
                        g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_ml))
                        
                        g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(m['PFI'], datatype=xsd_ns["integer"])))
                        g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(m['UFI'], datatype=xsd_ns["integer"])))
                        g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))
                        # parsed_date = parser.parse(m['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                        
                        g.add((wb_geometry_instance, ontology_ns["createDate"],\
                            Literal(m['C_DATE_PFI'],datatype=xsd_ns["date"])))
                        
                        g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(m['geometry'], datatype=geosparql['wktLiteral'])))
                                           
                        g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(m['F_TYPE_COD'], datatype=xsd_ns["string"])))
                        
                  
                        # g.serialize(destination=RDFname, format="xml")

                        k +=1
                    
                    else:
                        g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_lidar))
                        
                        g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(m['PFI'], datatype=xsd_ns["integer"])))
                        g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(m['UFI'], datatype=xsd_ns["integer"])))
                        g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))
                        
                        # parsed_date = parser.parse(m['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                        g.add((wb_geometry_instance, ontology_ns["createDate"],\
                            Literal(m['C_DATE_PFI'],datatype=xsd_ns["date"])))
                        
                        g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(m['geometry'], datatype=geosparql['wktLiteral'])))
                                           
                        g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(m['F_TYPE_COD'], datatype=xsd_ns["string"])))
                        
                  
                        # g.serialize(destination=RDFname, format="xml")

                        k +=1
                
       
    
    else:
        
        ## Define waterbody instances of feature
        if 'F_TYPE_COD' in i.keys():
                
            wb_instance = ontology_ns["wb{0}".format(index)]
            g.add((wb_instance, RDF.type, Feature))        
            # g.add((wb_instance, ontology_ns.isType, Literal("Waterbody", datatype=xsd_ns["string"])))
            g.add((wb_instance, ontology_ns.waterbodyID, Literal(index, datatype=xsd_ns["integer"])))
            
            
            wb_geometry = i["geometry"].geom_type
            wb_geometry_instance = ontology_ns["{0}{1}".format(wb_geometry,k)]
            
            g.add((wb_instance, geosparql["hasGeometry"], wb_geometry_instance))
            g.add((wb_geometry_instance, RDF.type, Geometry))   
            
        elif 'parcel_ufi' in i.keys():
            
            parcel_instance = ontology_ns["parcel{0}".format(index)]
            g.add((parcel_instance, RDF.type, Feature))
            # g.add((parcel_instance, ontology_ns.isType, Literal("Parcels", datatype=xsd_ns["string"])))
            g.add((parcel_instance, ontology_ns.waterbodyID, Literal(index, datatype=xsd_ns["integer"])))
            
            parcel_geometry = i["geometry"].geom_type
            parcel_geometry_instance = ontology_ns["{0}{1}".format(parcel_geometry,k)]
            
            g.add((parcel_instance, geosparql["hasGeometry"], parcel_geometry_instance))
            g.add((parcel_geometry_instance, RDF.type, Geometry))  
        
        elif 'FLOOD_OBS_' in i.keys():
            
            floodA_instance = ontology_ns["FloodA{0}".format(index)]
            g.add((floodA_instance, RDF.type, Feature))
            # g.add((floodA_instance, ontology_ns.isType, Literal("Flood_Authoritative", datatype=xsd_ns["string"])))
            g.add((floodA_instance, ontology_ns.waterbodyID, Literal(index, datatype=xsd_ns["integer"])))
            
            floodA_geometry = i["geometry"].geom_type
            floodA_geometry_instance = ontology_ns["{0}{1}".format(floodA_geometry,k)]
            
            g.add((floodA_instance, geosparql["hasGeometry"], floodA_geometry_instance))
            g.add((floodA_geometry_instance, RDF.type, Geometry))  
            
        else:
            floodNA_instance = ontology_ns["floodNA{0}".format(index)]
            g.add((floodNA_instance, RDF.type, Feature))
            # g.add((floodNA_instance, ontology_ns.isType, Literal("Flood_NonAuthoritative", datatype=xsd_ns["string"])))
            g.add((floodNA_instance, ontology_ns.waterbodyID, Literal(index, datatype=xsd_ns["integer"])))

            
            
            floodNA_geometry = i["geometry"].geom_type
            floodNA_geometry_instance = ontology_ns["{0}{1}".format(floodNA_geometry,k)]
            
            g.add((floodNA_instance, geosparql["hasGeometry"], floodNA_geometry_instance))
            g.add((floodNA_geometry_instance, RDF.type, Geometry))  
         ## Define geometry instances
         
        
         
         

         ## Define wb instance properties
         
        
         
        if 'F_TYPE_COD' in i.keys():
             
            if i['UFI'] is not None and i['PFI'] is not None:
                 
                if i['geometry'].geom_type =="Polygon":
                     
                     
                    g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_polygon))
                     
                    g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(i['PFI'], datatype=xsd_ns["integer"])))
                    g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(i['UFI'], datatype=xsd_ns["integer"])))
                     # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                    
                    # date = datetime.strptime(i['C_DATE_PFI'], '%Y%m%d%H%M%S').strftime('%d/%m/%Y')
                    
                    g.add((wb_geometry_instance, ontology_ns["createDate"],\
                        Literal(i['C_DATE_PFI'] ,datatype=xsd_ns["date"])))

                     
                    g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=geosparql['wktLiteral'])))
                                        
                    g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(i['F_TYPE_COD'], datatype=xsd_ns["string"])))
                    g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"]))) 
               
                     # g.serialize(destination=RDFname, format="xml")
        
                    k +=1

                else:
                     
                     
                    g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_point))
                     
                    g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(i['PFI'], datatype=xsd_ns["integer"])))
                    g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(i['UFI'], datatype=xsd_ns["integer"])))
                     # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                    
                    
                    g.add((wb_geometry_instance, ontology_ns["createDate"],\
                        Literal(i['C_DATE_PFI'] ,datatype=xsd_ns["date"])))
                        
                     
                    g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=geosparql['wktLiteral'])))
                                        
                    g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(i['F_TYPE_COD'], datatype=xsd_ns["string"])))
                    g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))
               
                     # g.serialize(destination=RDFname, format="xml")
        
                    k +=1
                 
                 
            elif i['UFI'] is not None and type(i['PFI']) == type(None):
                 
                g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_ml))
                 
                g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(i['PFI'], datatype=xsd_ns["integer"])))
                g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(i['UFI'], datatype=xsd_ns["integer"])))
                 # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                g.add((wb_geometry_instance, ontology_ns["createDate"],\
                     Literal(i['C_DATE_PFI'],datatype=xsd_ns["date"])))
                 
                g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=geosparql['wktLiteral'])))
                                    
                g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(i['F_TYPE_COD'], datatype=xsd_ns["string"])))
                g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))
           
                 # g.serialize(destination=RDFname, format="xml")
    
                k +=1
                 
            else:
        
              
             g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_lidar))
              
             g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(i['PFI'], datatype=xsd_ns["integer"])))
             g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(i['UFI'], datatype=xsd_ns["integer"])))
              # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
             g.add((wb_geometry_instance, ontology_ns["createDate"],\
                  Literal(i['C_DATE_PFI'],datatype=xsd_ns["date"])))
              
             g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=geosparql['wktLiteral'])))
                                 
             g.add((wb_geometry_instance, ontology_ns["varietyOf"], Literal(i['F_TYPE_COD'], datatype=xsd_ns["string"])))
             g.add((wb_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))
        

             k +=1

        elif 'parcel_ufi' in i.keys():
            
            crown = not pd.isnull(i['parcel_cro'])
             
            g.add((parcel_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_parcels))
             
            g.add((parcel_geometry_instance, ontology_ns["hasPFI"], Literal(i['parcel_pfi'], datatype=xsd_ns["integer"])))
            g.add((parcel_geometry_instance, ontology_ns["hasUFI"], Literal(i['parcel_ufi'], datatype=xsd_ns["integer"])))
             # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
            
            g.add((parcel_geometry_instance, ontology_ns["createDate"],\
                 Literal(i['parcel_reg'],datatype=xsd_ns["date"])))
            
            g.add((parcel_geometry_instance, ontology_ns["isCrown"], Literal(crown, datatype=xsd_ns["boolean"])))
            g.add((parcel_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=geosparql['wktLiteral'])))
                                
            g.add((parcel_geometry_instance, ontology_ns["varietyOf"], Literal('parcels', datatype=xsd_ns["string"])))
            k +=1
            
        elif 'FLOOD_OBS_' in i.keys():
            
            g.add((floodA_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_flood))
            
            g.add((floodA_geometry_instance, ontology_ns["hasPFI"], Literal('', datatype=xsd_ns["integer"])))
            g.add((floodA_geometry_instance, ontology_ns["hasUFI"], Literal('', datatype=xsd_ns["integer"])))
            g.add((floodA_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))

            # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
            g.add((floodA_geometry_instance, ontology_ns["createDate"],\
                Literal(i['OBS_CREATE'],datatype=xsd_ns["date"])))
            
            g.add((floodA_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=geosparql['wktLiteral'])))
                               
            g.add((floodA_geometry_instance, ontology_ns["varietyOf"], Literal('Flood_Authoritative', datatype=xsd_ns["string"])))
            k +=1
        
        else:
            
            g.add((floodNA_geometry_instance, ontology_ns['hasGeometryProvenance'], flood_dataset_nonAuth))
            
            g.add((floodNA_geometry_instance, ontology_ns["hasPFI"], Literal(i['PFI'], datatype=xsd_ns["integer"])))
            g.add((floodNA_geometry_instance, ontology_ns["hasUFI"], Literal(i['UFI'], datatype=xsd_ns["integer"])))
            # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
            g.add((floodNA_geometry_instance, ontology_ns["createDate"],\
                Literal(i['C_DATE_PFI'],datatype=xsd_ns["date"])))
            
            g.add((floodNA_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=geosparql['wktLiteral'])))
            g.add((floodNA_geometry_instance, ontology_ns["isCrown"], Literal('False', datatype=xsd_ns["boolean"])))

            g.add((floodNA_geometry_instance, ontology_ns["varietyOf"], Literal('Flood_NonAuthoritative', datatype=xsd_ns["string"])))
            k +=1
        


g.serialize(destination=RDFname, format="xml")

print("--- %s seconds ---" % (time.time() - start_time))
