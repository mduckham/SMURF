#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 11:32:42 2023

@author: mkazemi
"""

## Indetifying waterbodies with multiple or single representation 

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



os.chdir("/Users/mkazemi/cloudstor/2023/VicMap Project/Toy example")

wb_point = gpd.read_file("/Users/mkazemi/cloudstor/2023/VicMap Project/Toy example/Dataset/Waterbody_point_selected.shp")
wb_polygon = gpd.read_file("")
wb_ml = gpd.read_file("Dataset/ML_selected.shp")


df_list = [wb_point, wb_polygon, wb_ml]

df1_polygon = [i for i in df_list if i.geom_type.unique() =="Polygon"][0]

df2_polygon = [i for i in df_list if i.geom_type.unique() =="Polygon"][1]

df3_point = [i for i in df_list if i.geom_type.unique() =="Point"][0]




df1_polygon_intersected = df1_polygon[df1_polygon.intersects(df2_polygon.unary_union)]
df2_polygon_intersected = df2_polygon[df2_polygon.intersects(df1_polygon.unary_union)]



df1_polygon_intersected_buffer = df1_polygon_intersected
df1_polygon_intersected_buffer["geometry"] = df1_polygon_intersected_buffer["geometry"].buffer(10)


df1_polygon_buffer = df1_polygon
df2_polygon_buffer = df2_polygon

df1_polygon_buffer["geometry"] = df1_polygon_buffer["geometry"].buffer(10)
df2_polygon_buffer["geometry"] = df2_polygon_buffer["geometry"].buffer(10)



df1_polygon_notIntersected = df1_polygon[~df1_polygon.intersects(df2_polygon.unary_union)]
df1_polygon_notIntersected.reset_index(drop=True, inplace=True)

df2_polygon_notIntersected = df2_polygon[~df2_polygon.intersects(df1_polygon.unary_union)]
df2_polygon_notIntersected.reset_index(drop=True, inplace=True)

df1_polygon_notIntersected_buffer = df1_polygon_notIntersected
df2_polygon_notIntersected_buffer = df2_polygon_notIntersected


df1_polygon_notIntersected_buffer["geometry"] = df1_polygon_notIntersected_buffer["geometry"].buffer(10)
df2_polygon_notIntersected_buffer["geometry"] = df2_polygon_notIntersected_buffer["geometry"].buffer(10)



# Rule 1: two wb and ML polygons intersected, AND point within Buffer of 10m of wb_polygon
# Rule 2: two wb and ML polygons intersected, AND point NOT within Buffer of 10m of wb_polygon
# Rule 3: two wb and ML polygons NOT intersected, AND point within Buffer of 10m of wb_polygon
# Rule 4: two wb and ML polygons NOT intersected, AND point within Buffer of 10m of wb_ml
# Rule 5: two wb and ML polygons NOT intersected, AND point NOT within Buffer of 10m of any polygons



wb_instances = []

## waterbody polygon

for index1, polygon1 in df1_polygon_buffer.iterrows():
    
    for index2, polygon2 in df2_polygon_buffer.iterrows():
    
        df1_df2_intersect = df1_polygon.iloc[index1]["geometry"].intersects(df2_polygon.iloc[index2]["geometry"])
        
        if df1_df2_intersect is True:
            
            df3_point_within_intersected = wb_point[wb_point.within(polygon1["geometry"])]
            
        
            if (not df3_point_within_intersected.empty):
        
                wb_instances.append((df1_polygon.iloc[index1], df2_polygon.iloc[index2], df3_point_within_intersected.squeeze()))
    
            else:
                wb_instances.append((df1_polygon.iloc[index1], df2_polygon.iloc[index2]))
        
            break


    else:
        wb_instances.append(df1_polygon.iloc[index1])




## waterbody ML

for index2, polygon2 in df2_polygon_buffer.iterrows():
    
    for index1, polygon1 in df1_polygon_buffer.iterrows():
    
        df1_df2_intersect = df2_polygon.iloc[index2]["geometry"].intersects(df1_polygon.iloc[index1]["geometry"])
        
        if df1_df2_intersect is False:
            
            df3_point_within_Notintersected = wb_point[wb_point.within(polygon2["geometry"])]
            
        
            if (not df3_point_within_Notintersected.empty):
        
                wb_instances.append((df2_polygon.iloc[index2], df3_point_within_Notintersected.squeeze()))
    
            break
    else:
        wb_instances.append(df2_polygon.iloc[index2])



     
## waterbody point

df3_point_within_df1 = wb_point[wb_point.within(df1_polygon_buffer.unary_union)]
df3_point_within_df2 = wb_point[wb_point.within(df2_polygon_buffer.unary_union)]

merged_points_within = df3_point_within_df1.append(df3_point_within_df2)

df3_point_notwithin_df1_df2 = wb_point[~wb_point.within(merged_points_within.unary_union)]


# wb_instances.append(df3_point_notwithin_df1_df2)

for i in range(len(df3_point_notwithin_df1_df2)):

    wb_instances.append(df3_point_notwithin_df1_df2.iloc[i].squeeze())
                
                    
                    
#%% 


# Create a new RDF graph
g = Graph()
result = g.parse("Ontology_Vicmap2.rdf")


# Define the namespaces used in your RDF file
ontology_ns = Namespace("http://www.semanticweb.org/mkazemi/ontologies/2023/9/Ontology_Vicmap2#")
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
terms = Namespace("http://purl.org/dc/terms/#")
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


## Input Metadata

dataset_metadata = pd.read_csv('VicmapHydro/metadata.csv')
dataset_metadata = dataset_metadata.replace(np.nan,"")
## Define classes

Feature = geosparql["Feature"]
Geometry = geosparql["Geometry"]
Dataset = dcat["Dataset"]
Entity = ontology_prov["Entity"]
Agent = ontology_prov["Agent"]
Agency = fsdf["Agency"]
Jurisdiction = fsdf["Jurisdiction"]
Location = terms["Location"]
PeriodOfTime = terms["PeriodOfTime"]
Frequency = terms["Frequency"]
Distribution = dcat["Distribution"]
MediaType = terms["MediaType"]
RightsStatement = terms["RightsStatement"]
Kind = ns["Kind"]
Organization = ns["Organization"]
TelephoneType = ns["TelephoneType"]
Voice = ns["Voice"]
Fax = ns["Fax"]
Address = ns["Address"]
QualityMeasurement = dqv["QualityMeasurement"]
Metric = dqv["Metric"]
Dimension = dqv["Dimension"]
Category = dqv["Category"]
Standard = terms["Standard"]



## Define Dataset instance

dataset_title = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Resource Name:', 'Description'].values[0]
available_date = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Metadata Date:', 'Description'].values[0]
hydro_dataset = ontology_ns[dataset_title]
g.add((hydro_dataset, RDF.type, Dataset))

 
## Define data properties of dataset instance

g.add((hydro_dataset, terms['abstract'], 
      Literal(dataset_metadata.loc[dataset_metadata['Metadata'] == 'Abstract:', 'Description'].values[0],
      datatype=xsd_ns["string"])))


g.add((hydro_dataset, terms['description'],
      Literal(dataset_metadata.loc[dataset_metadata['Metadata'] == 'Purpose:', 'Description'].values[0],
      datatype=xsd_ns["string"])))
      
g.add((hydro_dataset, terms['identifier'], 
      Literal(dataset_metadata.loc[dataset_metadata['Metadata'] == 'Anzlic ID:', 'Description'].values[0],
      datatype=xsd_ns["string"])))
      
      
g.add((hydro_dataset, dcat['keyword'],
      Literal(dataset_metadata.loc[dataset_metadata['Metadata'] == 'Search Words:', 'Description'].values[0],
      datatype=xsd_ns["string"])))

      
g.add((hydro_dataset, terms['source'],
      Literal(dataset_metadata.loc[dataset_metadata['Metadata'] == 'Data Source:', 'Description'].values[0],
      datatype=xsd_ns["string"])))

g.add((hydro_dataset, terms['available'], Literal(available_date, datatype=xsd_ns["date"])))


## Define object properties of dataset instance

# Contact point

contact = "vcard01"
organization = "organization01"
role = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Contact Position:', 'Description'].values[0]
address = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Address:', 'Description'].values[0]
if address == "":
    org_address = "address_unknown01"
else:
    org_address = "address_{0}".format(address)
    
telephone = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Telephone:', 'Description'].values[0]
if address == "":
    org_tel = "telephone_unknown01"
else:
    org_tel = "telephone_{0}".format(telephone)


facsimile = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Facsimile:', 'Description'].values[0]
if facsimile == "":
    org_fax = "fax_unknown01"
else:
    org_fax = "fax{0}".format(facsimile)
    
email = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Email Address:', 'Description'].values[0]
if email == "":
    org_email = "email_unknown01"
else:
    org_email = "email{0}".format(email)

url = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Additional Metadata:', 'Description'].values[0]
countryName = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Country Name:', 'Description'].values[0]
locality = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Locality:', 'Description'].values[0]
region = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Region:', 'Description'].values[0]


g.add((hydro_dataset, dcat["contactPoint"],ontology_ns[contact] ))
g.add((ontology_ns[contact], RDF.type, Kind))
g.add((ontology_ns[organization], RDFS.subClassOf,ontology_ns[contact]))
g.add((ontology_ns[organization], RDF.type, Organization))



g.add((ontology_ns[organization], ns["title"], Literal(role,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["country-name"], Literal(countryName,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["locality"], Literal(locality,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ns["region"], Literal(region,datatype=xsd_ns["string"])))
g.add((ontology_ns[organization], ontology_ns["hasURL"], Literal(url,datatype=xsd_ns["string"])))



g.add((ontology_ns[organization], ns["hasAddress"], ontology_ns[org_address]))
g.add((ontology_ns[org_address], RDF.type, Address))

g.add((ontology_ns[organization], ns["hasTelephone"], ontology_ns["Phone01"]))
g.add((ontology_ns["Phone01"], RDF.type, TelephoneType))
g.add((ontology_ns[org_tel], RDFS.subClassOf, ontology_ns["Phone01"]))
g.add((ontology_ns[org_tel], RDF.type, ns["Cell"]))
g.add((ontology_ns[org_fax], RDFS.subClassOf, ontology_ns["Phone01"]))
g.add((ontology_ns[org_fax], RDF.type, Fax))

g.add((ontology_ns[organization], ns["hasEmail"], ontology_ns[org_email]))
g.add((ontology_ns[org_email], RDF.type, ns["Email"]))

# Custodian
custodian = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Custodian:', 'Description'].values[0]
if pd.isnull(custodian) is True:
    dataset_agency = "custodian_unknown01"
else:
    dataset_agency = "custodian_{0}".format(custodian)

#dataset_agency = ontology_ns["{0}_agency".format(dataset_title)]
g.add((hydro_dataset, fsdf["hasCustodian"], ontology_ns[dataset_agency] ))
g.add((ontology_ns[dataset_agency] , RDF.type, Agency))
g.add((ontology_ns[dataset_agency], RDFS.subClassOf, ontology_ns[organization]))


# Jurisdication
jurisdiction = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Jurisdiction:', 'Description'].values[0]
if pd.isnull(jurisdiction) is True:
    dataset_jurisdiction = "jurisdiction_unknown01"
else:
    dataset_jurisdiction = "jurisdiction_{0}".format(jurisdiction)
    
#dataset_jurisdiction = ontology_ns["{0}_jurisdiction".format(dataset_title)]
g.add((hydro_dataset, fsdf["hasJurisdiction"], ontology_ns[dataset_jurisdiction] ))
g.add((ontology_ns[dataset_jurisdiction], RDF.type, Jurisdiction))
g.add((ontology_ns[dataset_jurisdiction], RDFS.subClassOf, ontology_ns[organization]))

# Bounding box

dataset_location = ontology_ns["{0}_location".format(dataset_title)]
g.add((hydro_dataset, terms["spatial"], ontology_ns[dataset_location] ))
g.add((ontology_ns[dataset_location], RDF.type, Location))
g.add((ontology_ns[dataset_location], dcat["bbox"], 
                              Literal(dataset_metadata.loc[dataset_metadata['Metadata'] == 'Geographic Bounding Box:', 'Description'].values[0],
                              datatype=xsd_ns["string"])))


# Temporal

dataset_temporal = ontology_ns["{0}_temporal".format(dataset_title)]
g.add((hydro_dataset, terms["temporal"], ontology_ns[dataset_temporal] ))
g.add(( ontology_ns[dataset_temporal] , RDF.type, PeriodOfTime))

start_date = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Beginning to Ending Date:', 'Description'].values[0].split(" - ")[0]
end_date = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Beginning to Ending Date:', 'Description'].values[0].split(" - ")[1]
g.add(( ontology_ns[dataset_temporal] , dcat["startDate"], Literal(start_date, datatype=xsd_ns["string"])))
g.add(( ontology_ns[dataset_temporal] , dcat["endDate"], Literal(end_date, datatype=xsd_ns["string"])))


# Frequency
frequency = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Maintainence and Update Frequency:', 'Description'].values[0]
if pd.isnull(frequency) is True:
    dataset_frequency = "frequency_unknown01"
else:
    dataset_frequency = "frequency_{0}".format(frequency)
    
#dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset, fsdf["accrualPeriodicity"], ontology_ns[dataset_frequency] ))
g.add((ontology_ns[dataset_frequency], RDF.type, Frequency))


# Distribution

distribution = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Stored Data Format:', 'Description'].values[0]
if pd.isnull(distribution) is True:
    dataset_distribution = "distribution_unknown01"
else:
    dataset_distribution = "distribution_{0}".format(distribution)


# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset, dcat["distribution"], ontology_ns[dataset_distribution] ))
g.add((ontology_ns[dataset_distribution], RDF.type, Distribution))


# Access right

access = dataset_metadata.loc[dataset_metadata['Metadata'] == 'Access Constraint:', 'Description'].values[0]
if pd.isnull(access) is True:
    dataset_access = "access_unknown01"
else:
    dataset_access = "access_{0}".format(distribution)


# dataset_frequency = ontology_ns["{0}_frequency".format(dataset_title)]
g.add((hydro_dataset, terms["accessRights"], ontology_ns[dataset_access] ))
g.add((ontology_ns[dataset_access], RDF.type, RightsStatement))


# Accuracy

positional_accuracy = ontology_ns["{0}_positional_accuracy".format(dataset_title)]
attribute_accuracy = ontology_ns["{0}_attribute_accuracy".format(dataset_title)]
logical_consistency = ontology_ns["{0}_logical_consistency".format(dataset_title)]
accessibility = ontology_ns["{0}_accessibility".format(dataset_title)]


positional_accuracy_metric = ontology_ns["{0}_positional_accuracy_metric".format(dataset_title)]
attribute_accuracy_metric = ontology_ns["{0}_attribute_accuracy_metric".format(dataset_title)]
logical_consistency_metric = ontology_ns["{0}_logical_consistency_metric".format(dataset_title)]
accessibility_metric = ontology_ns["{0}_accessibility_metric".format(dataset_title)]

accuracy = ontology_ns["accuracy"]
consistency = ontology_ns["consistency"]
accessibility = ontology_ns["accessibility"]



g.add((hydro_dataset, dqv["hasQualityMeasurement"], positional_accuracy))
g.add((positional_accuracy, RDF.type, QualityMeasurement))
g.add((positional_accuracy, dqv["isMeasurementOF"], positional_accuracy_metric))
g.add((positional_accuracy_metric, RDF.type, Metric))
g.add((positional_accuracy_metric, dqv["value"], Literal("+/-30", datatype=xsd_ns["string"])))
g.add((positional_accuracy_metric, dqv["inDimension"], accuracy))
g.add((accuracy, RDF.type, Dimension))


g.add((hydro_dataset, dqv["hasQualityMeasurement"], attribute_accuracy))
g.add((attribute_accuracy, RDF.type, QualityMeasurement))
g.add((attribute_accuracy, dqv["isMeasurementOF"], attribute_accuracy_metric))
g.add((attribute_accuracy_metric, RDF.type, Metric))
g.add((attribute_accuracy_metric, dqv["value"], Literal("1%-5%", datatype=xsd_ns["string"])))
g.add((attribute_accuracy_metric, dqv["inDimension"], accuracy))


g.add((hydro_dataset, dqv["hasQualityMeasurement"], logical_consistency))
g.add((logical_consistency, RDF.type, QualityMeasurement))
g.add((logical_consistency, dqv["isMeasurementOF"], logical_consistency_metric))
g.add((logical_consistency_metric, RDF.type, Metric))
g.add((logical_consistency_metric, dqv["value"], Literal("", datatype=xsd_ns["string"])))
g.add((logical_consistency_metric, dqv["inDimension"], consistency))
g.add((consistency, RDF.type, Dimension))


g.add((hydro_dataset, dqv["hasQualityMeasurement"], accessibility))
g.add((accessibility, RDF.type, QualityMeasurement))
g.add((accessibility, dqv["isMeasurementOF"], accessibility_metric))
g.add((accessibility_metric, RDF.type, Metric))
g.add((accessibility_metric, dqv["value"], Literal("True", datatype=xsd_ns["boolean"])))
g.add((accessibility_metric, dqv["inDimension"], accessibility))
g.add((accessibility, RDF.type, Dimension))



k =0

source = {"source":"name"}
for index, i in enumerate(wb_instances):
    
    
    
    ## Define relations between classes and waterbody instances
    # g.add((organization_class, RDFS.subClassOf, agent_class))
    # g.add((person_class, RDFS.subClassOf, agent_class))
    # g.add((geometryState_class, RDFS.subClassOf, ontology_ns["owl:Thing"]))
    
    
    ## Define waterbody instances of feature
    
    wb_instance = ontology_ns["wb{0}".format(index)]

    g.add((wb_instance, RDF.type, Feature))

    ## Data properties of waterbody instances
    
    g.add((wb_instance, ontology_ns.hasVarietyOf, Literal("reservoir", datatype=xsd_ns["string"])))
    g.add((wb_instance, ontology_ns["waterbodyID"], Literal(index, datatype=xsd_ns["int"])))
    


    ## Multi-representation feature
    
    if type(i) ==tuple :
        for index1, j in enumerate(i):
            
            ## Define geometry instances
            
            wb_geometry = j["geometry"].geom_type
            wb_geometry_instance = ontology_ns["{0}{1}".format(wb_geometry,k)]
            

            ## Define wb instance object properties
            
            g.add((wb_instance, geosparql["hasGeometry"], wb_geometry_instance))
            g.add((wb_geometry_instance, RDF.type, Geometry))
            
            
            ## Define geometry data/object properties
            
            g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset))
            
            g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(j['pfi'], datatype=xsd_ns["int"])))
            g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(j['ufi'], datatype=xsd_ns["int"])))
            g.add((wb_geometry_instance, ontology_ns["createDate"],\
                Literal(datetime.strptime(j['create_dat'], "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%S"),datatype=xsd_ns["dateTime"])))
            
            g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(j['geometry'], datatype=schema_geo["geo"])))
                   
            g.add((wb_geometry_instance, ontology_ns["hasFeatureType"], Literal(j['feature_ty'], datatype=xsd_ns["string"])))

           
            g.serialize(destination="populated_ontology_State.rdf", format="xml")
            k +=1
    else:
        
         ## Define geometry instances
         
         wb_geometry = i["geometry"].geom_type
         wb_geometry_instance = ontology_ns["{0}{1}".format(wb_geometry,k)]
         

         ## Define wb instance properties
         
         g.add((wb_instance, geosparql["hasGeometry"], wb_geometry_instance))
         g.add((wb_geometry_instance, RDF.type, Geometry))
         
         
         ## add attribues into defined properties
         
         g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(i['pfi'], datatype=xsd_ns["int"])))
         g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(i['ufi'], datatype=xsd_ns["int"])))
         g.add((wb_geometry_instance, ontology_ns["createDate"],\
                 Literal(datetime.strptime(i['create_dat'], "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%S"),datatype=xsd_ns["dateTime"])))
                
        
         g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=schema_geo["geo"])))

         g.add((wb_geometry_ont, ontology_ns["hasFeatureType"], Literal(i['feature_ty'], datatype=xsd_ns["string"])))


         g.serialize(destination="populated_ontology_State.rdf", format="xml")
         k +=1   

            
        
#%%            
            
            
            
            
    #         ## Define wb instance properties
    #         if j["CapturedBy"] == "VicMap":
                
    #             ## Define GeometryCOntext relations and instances and properties
                
    #             g.add((wb_geometry_ont, ontology_omg["hasGeometryContext"], geometryContext_instance_true))
    #             g.add((geometryContext_instance_true, RDF.type, geometyryContext_class))

    #             g.add((geometryContext_instance_true, ontology_ns["isAuthoritative"], Literal("True", datatype=xsd_ns["boolean"])))

                
    #             ## Define datasournce instance and its property
    #             source_instance = "{0}_datasource_organisation".format(wb_geometry)
    #             source[source_instance] = j["CapturedBy"]
                
    #             g.add((wb_geometry_ont, ontology_ns["hasSource"], ontology_ns[source_instance] ))
    #             g.add((ontology_ns[source_instance], RDF.type, entity_class))
                
                
    #             ## Define foaf_organization instance and its name property
                
    #             org_instance = ontology_ns[source_instance.split("_")[-1]]
    #             g.add((ontology_ns[source_instance], ontology_prov["wasAttributedTo"], org_instance))
    #             g.add((org_instance, RDF.type, organization_class))

    #             g.add((org_instance, ontology_foaf["name"], Literal(j['CapturedBy'],datatype=rdfs["string"])))
                

                
    #         elif j["CapturedBy"] != "VicMap" and  j["CapturedBy"] not in source.values():
    #             ## Define GeometryCOntext relations and instances and properties
                
    #             g.add((wb_geometry_ont, ontology_omg["hasGeometryContext"], geometryContext_instance_false))
    #             g.add((geometryContext_instance_false, RDF.type, geometyryContext_class))

    #             g.add((geometryContext_instance_false, ontology_ns["isAuthoritative"], Literal("False", datatype=xsd_ns["boolean"])))

                
    #             ## Define datasournce instance and its property
    #             source_instance = "{0}_datasource_person{1}".format(wb_geometry, k)
    #             source[source_instance] = j["CapturedBy"]
                
    #             g.add((wb_geometry_ont, ontology_ns["hasSource"], ontology_ns[source_instance] ))
    #             g.add((ontology_ns[source_instance], RDF.type, entity_class))
                
                
    #             ## Define foaf_organization instance and its name property
                
    #             person_instance = ontology_ns[source_instance.split("_")[-1]]
    #             g.add((ontology_ns[source_instance], ontology_prov["wasAttributedTo"], person_instance))
    #             g.add((person_instance, RDF.type, person_class))

    #             g.add((person_instance, ontology_foaf["givenName"], Literal(j['CapturedBy'], datatype=xsd_ns["string"])))
                
                
    #         else:
    #             ## Define GeometryCOntext relations and instances and properties
                
    #             g.add((wb_geometry_ont, ontology_omg["hasGeometryContext"], geometryContext_instance_false))
    #             g.add((geometryContext_instance_false, RDF.type, geometyryContext_class))

    #             g.add((geometryContext_instance_false, ontology_ns["isAuthoritative"], Literal("False", datatype=xsd_ns["boolean"])))


    #             ## Define datasournce instance and its property
    #             # source_instance = "{0}_datasource_person{1}".format(wb_geometry, k)

    #             source_instance = list(source.keys())[list(source.values()).index(j["CapturedBy"])]
                
    #             g.add((wb_geometry_ont, ontology_ns["hasSource"], ontology_ns[source_instance] ))
    #             g.add((ontology_ns[source_instance], RDF.type, entity_class))
                
                
    #             ## Define foaf_organization instance and its name property
                
    #             person_instance = ontology_ns[source_instance.split("_")[-1]]
    #             g.add((ontology_ns[source_instance], ontology_prov["wasAttributedTo"], person_instance))
    #             g.add((person_instance, RDF.type, person_class))

    #             g.add((person_instance, ontology_foaf["givenName"], Literal(source[source_instance], datatype=xsd_ns["string"])))

                
             
    #         ## add attribues into defined properties
            
    #         g.add((wb_geometry_ont, ontology_ns["hasPFI"], Literal(j['pfi'], datatype=xsd_ns["int"])))
    #         g.add((wb_geometry_ont, ontology_ns["hasUFI"], Literal(j['ufi'], datatype=xsd_ns["int"])))
    #         g.add((wb_geometry_ont, ontology_ns["hasCreateDate"],\
    #             Literal(datetime.strptime(j['create_dat'], "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%S"),datatype=xsd_ns["dateTime"])))
            
    #         g.add((wb_geometry_ont, ontology_ns["spatialLocation"], Literal(j['geometry'], datatype=schema_geo["geo"])))
                   
    #         g.add((wb_geometry_ont, ontology_ns["hasFeatureType"], Literal(j['feature_ty'], datatype=xsd_ns["string"])))

    #         g.serialize(destination="populated_ontology.rdf", format="xml")
    #         k +=1   
            
    # else:
    #     ## Define geometry instances
        
    #     wb_geometry = i["geometry"].geom_type
    #     wb_geometry_ont = ontology_ns["{0}{1}".format(wb_geometry,k)]
        

    #     ## Define wb instance properties
        
    #     g.add((wb_instance, ontology_omg["hasGeometry"], wb_geometry_ont))
    #     g.add((wb_geometry_ont, RDF.type, geometry_class))
        
        
    #     ## Define wb instance properties
    #     if i["CapturedBy"] == "VicMap" :
            
           
    #         ## Define GeometryCOntext relations and instances and properties
            
    #         g.add((wb_geometry_ont, ontology_omg["hasGeometryContext"], geometryContext_instance_true))
    #         g.add((geometryContext_instance_true, RDF.type, geometyryContext_class))

    #         g.add((geometryContext_instance_true, ontology_ns["isAuthoritative"], Literal("True", datatype=xsd_ns["boolean"])))

            
    #         ## Define datasournce instance and its property
    #         source_instance = "{0}_datasource_organisation".format(wb_geometry, k)
    #         source[source_instance] = i["CapturedBy"]
            
    #         g.add((wb_geometry_ont, ontology_ns["hasSource"], ontology_ns[source_instance] ))
    #         g.add((ontology_ns[source_instance], RDF.type, entity_class))
            
            
    #         ## Define foaf_organization instance and its name property
            
    #         org_instance = ontology_ns[source_instance.split("_")[-1]]
    #         g.add((ontology_ns[source_instance], ontology_prov["wasAttributedTo"], org_instance))
    #         g.add((org_instance, RDF.type, organization_class))

    #         g.add((org_instance, ontology_foaf["name"], Literal(i['CapturedBy'], datatype=rdfs["string"])))
            
        
        # elif i["CapturedBy"] != "ML" and i["CapturedBy"] in source.values():
        #     ## Define GeometryCOntext relations and instances and properties
            
        #     g.add((wb_geometry_ont, ontology_omg["hasGeometryContext"], geometryContext_instance_true))
        #     g.add((geometryContext_instance_true, RDF.type, geometyryContext_class))

        #     g.add((geometryContext_instance_true, ontology_ns["isAuthoritative"], Literal("True", datatype=xsd_ns["boolean"])))


        #     ## Define datasournce instance and its property
        #     source_instance = "{0}_datasource_organisation{1}".format(wb_geometry, k)

        #     # source_instance = list(source.keys())[list(source.values()).index(j["CapturedBy"])]
            
        #     g.add((wb_geometry_ont, ontology_ns["hasSource"], ontology_ns[source_instance] ))
        #     g.add((ontology_ns[source_instance], RDF.type, entity_class))
            
            
        #     ## Define foaf_organization instance and its name property
            
        #     org_instance = ontology_ns[source_instance.split("_")[-1]]
        #     g.add((ontology_ns[source_instance], ontology_prov["wasAttributedTo"], org_instance))
        #     g.add((org_instance, RDF.type, organization_class))

        #     g.add((org_instance, ontology_foaf["name"], Literal(source[source_instance], datatype=xsd_ns["string"])))

            
            
        # elif i["CapturedBy"] != "VicMap" and i["CapturedBy"]  not in source.values():
        #     ## Define GeometryCOntext relations and instances and properties
            
        #     g.add((wb_geometry_ont, ontology_omg["hasGeometryContext"], geometryContext_instance_false))
        #     g.add((geometryContext_instance_false, RDF.type, geometyryContext_class))

        #     g.add((geometryContext_instance_false, ontology_ns["isAuthoritative"], Literal("False", datatype=xsd_ns["boolean"])))
                            
        #     ## Define datasournce instance and its property
        #     source_instance = "{0}_datasource_person{1}".format(wb_geometry, k)
        #     source[source_instance] = j["CapturedBy"]
            
        #     g.add((wb_geometry_ont, ontology_ns["hasSource"], ontology_ns[source_instance] ))
        #     g.add((ontology_ns[source_instance], RDF.type, entity_class))
            
            
        #     ## Define foaf_organization instance and its name property
            
        #     person_instance = ontology_ns[source_instance.split("_")[-1]]
        #     g.add((ontology_ns[source_instance], ontology_prov["wasAttributedTo"], person_instance))
        #     g.add((person_instance, RDF.type, person_class))

        #     g.add((person_instance, ontology_foaf["givenName"], Literal(i['CapturedBy'], datatype=xsd_ns["string"])))
            
            
        # else:
        #     ## Define GeometryCOntext relations and instances and properties
            
        #     g.add((wb_geometry_ont, ontology_omg["hasGeometryContext"], geometryContext_instance_false))
        #     g.add((geometryContext_instance_false, RDF.type, geometyryContext_class))

        #     g.add((geometryContext_instance_false, ontology_ns["isAuthoritative"], Literal("False", datatype=xsd_ns["boolean"])))
                   
        #     ## Define datasournce instance and its property
        #     # source_instance = "{0}_datasource_person{1}".format(wb_geometry, k)
        #     source_instance = list(source.keys())[list(source.values()).index(i["CapturedBy"])]

        #     # source_instance = list(source.keys())[list(source.values()).index(i["CapturedBy"])]
            
        #     g.add((wb_geometry_ont, ontology_ns["hasSource"], ontology_ns[source_instance] ))
        #     g.add((ontology_ns[source_instance], RDF.type, entity_class))
            
            
        #     ## Define foaf_organization instance and its name property
            
        #     person_instance = ontology_ns[source_instance.split("_")[-1]]
        #     g.add((ontology_ns[source_instance], ontology_prov["wasAttributedTo"], person_instance))
        #     g.add((person_instance, RDF.type, person_class))

        #     g.add((person_instance, ontology_foaf["givenName"], Literal(source[source_instance], datatype=xsd_ns["string"])))

            
         
        # ## add attribues into defined properties
        
        # g.add((wb_geometry_ont, ontology_ns["hasPFI"], Literal(i['pfi'], datatype=xsd_ns["int"])))
        # g.add((wb_geometry_ont, ontology_ns["hasUFI"], Literal(i['ufi'], datatype=xsd_ns["int"])))
        # g.add((wb_geometry_ont, ontology_ns["hasCreateDate"],\
        #         Literal(datetime.strptime(i['create_dat'], "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%S"),datatype=xsd_ns["dateTime"])))
               
        # g.add((wb_geometry_ont, ontology_ns["hasFeatureType"], Literal(i['feature_ty'], datatype=xsd_ns["string"])))
        # # g.add((wb_instance, ontology_ns["hasCreateDate"], Literal(datetime.strptime(j['create_dat'], "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%S"),\
        # #                                                         datatype=xsd_ns["dateTime"])))
        # # g.add((wb_instance, ontology_ns["geometryType"], Literal(wb_geometry, datatype=xsd_ns["string"])))

        # g.add((wb_geometry_ont, ontology_ns["spatialLocation"], Literal(i['geometry'], datatype=schema_geo["geo"])))

        # g.serialize(destination="populated_ontology.rdf", format="xml")
        # k +=1   

  
        
#%% Questions 

# 1. What water features are represented with point and polygon geometries?  

# Response: list of waterbodies with their pfi and geometry.
prefix Ontology_Vicmap:<http://www.semanticweb.org/mkazemi/ontologies/2023/8/Ontology_Vicmap#>
prefix omg:<https://w3id.org/omg#>
prefix owl:<http://www.w3.org/2002/07/owl#>
prefix prov:<http://www.w3.org/ns/prov#>
prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs:<http://www.w3.org/2000/01/rdf-schema#>

# SELECT (STRAFTER(STR(?waterbody), '#') AS ?WaterbodyName)
#  	?pfi 
#  	(STRAFTER(STR(?geometry), '#') AS ?geometryName)

# WHERE 
# {
#   ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi.
              
  
#   { Select ?waterbody
#     where {
#     ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry1;
#               omg:hasGeometry ?geometry2;
#               omg:hasGeometry ?geometry.

#     FILTER (regex(str(?geometry1), "Point") && regex(str(?geometry2), "Polygon"))
#     }

# GROUP BY  ?waterbody 
# HAVING (COUNT( ?geometry) >= 2)   
#   }
# }

# 2.What is a persistent feature identifier (PFI) of specific water feature represented with different geometries?  
# SELECT (STRAFTER(STR(?waterbody), '#') AS ?waterbodyLocalName)
#  	?pfi
#  	(STRAFTER(STR(?geometry), '#') AS ?geometryLocalName)
#  	?date


# WHERE 

# {
#   ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi;
#             Ontology_Vicmap:hasCreateDate ?date.
#   FILTER ( xsd:int(?pfi) = 8253315)
     
# }


# 3. List all the PFIs of water bodies that have multiple representations. 
# 4. On what date was a selected geometry generated?  
# SELECT (STRAFTER(STR(?waterbody), '#') AS ?WaterbodyName)
#  	?pfi
#  	(STRAFTER(STR(?geometry), '#') AS ?geometryName)
#  	?createDate


# WHERE 

# {
#   ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi;
#             Ontology_Vicmap:hasCreateDate ?createDate.
#           {
#     SELECT ?waterbody
#     WHERE {?waterbody rdf:type Ontology_Vicmap:Waterbody;
#                         omg:hasGeometry ?geometry.
#      	}
    
#        	GROUP BY  ?waterbody 
#      	HAVING (COUNT( ?geometry) >= 2)   
#   		}
# }

# 5. What organisation, person, or process is responsible for the creation of a specific water body geometry?  


# SELECT (STRAFTER(STR(?waterbody), '#') AS ?waterbodyLocalName)
#  	?pfi
#  	(STRAFTER(STR(?geometry), '#') AS ?geometryLocalName)
#  	?date ?OrgName ?PersonName

# WHERE 

# {
#   {?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi;
#             Ontology_Vicmap:hasCreateDate ?date;
#             Ontology_Vicmap:hasSource ?source.
#   ?source prov:wasAttributedTo ?attr.
#  	?attr foaf:name ?OrgName
  
#     FILTER ( xsd:int(?pfi) = 16487979)}
  
#   union
  
#     {?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi;
#             Ontology_Vicmap:hasCreateDate ?date;
#             Ontology_Vicmap:hasSource ?source.
#   ?source prov:wasAttributedTo ?attr.
#  	?attr foaf:givenName ?PersonName.
  
#     FILTER ( xsd:int(?pfi) = 16487979)
#     }
     
# }


# 6. Provide background information on why a specific water feature is represented as a point rather than a polygon.  


# 7. Which water bodies have only an authoritative geometry representation, and which also have a machine-learned alternative? 


# SELECT (STRAFTER(STR(?waterbody), '#') AS ?waterbodyLocalName)


# WHERE 

# {
#   ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi;
#             omg:hasGeometryContext ?geometrycontext;
#             Ontology_Vicmap:hasSource ?source;
#             Ontology_Vicmap:hasCreateDate ?date.
#   ?source prov:wasAttributedTo ?attr.
  
#   ?geometrycontext Ontology_Vicmap:isAuthoritative ?auth.
  
#   Filter( ?auth = "true"^^<http://www.w3.org/2001/XMLSchema#boolean> || ?auth = "false"^^<http://www.w3.org/2001/XMLSchema#boolean>)

# }

# Group by ?waterbody
# having (Count(?geometrycontext) >1)	

# 8. Provide pfi, producer name, and create date of waterbodies having both authoritative and non-authoritative geometry representation?

SELECT (STRAFTER(STR(?waterbody), '#') AS ?waterbodyLocalName)
 	?pfi ?auth  ?name ?gname
 	(STRAFTER(STR(?geometry), '#') AS ?geometryLocalName)
 	?date 
 	(STRAFTER(STR(?geometrycontext), '#') AS ?geometrycontextName)

WHERE 

{
  {
  ?waterbody rdf:type Ontology_Vicmap:Waterbody;
              omg:hasGeometry ?geometry.
  ?geometry Ontology_Vicmap:hasPFI ?pfi;
            omg:hasGeometryContext ?geometrycontext;
            Ontology_Vicmap:hasSource ?source;
            Ontology_Vicmap:hasCreateDate ?date.
  ?source prov:wasAttributedTo ?attr.
  
  ?geometrycontext Ontology_Vicmap:isAuthoritative 	"true"^^<http://www.w3.org/2001/XMLSchema#boolean>.
  ?attr foaf:name ?name.
  
  
  {
  select ?waterbody
 	where
    {
      ?waterbody rdf:type Ontology_Vicmap:Waterbody;
              omg:hasGeometry ?geometry.
  	 ?geometry omg:hasGeometryContext ?geometrycontext.
  
  FILTER ( contains(str(?geometrycontext), 'true') || contains(str(?geometrycontext),'false'))
    }
    GROUP BY ?waterbody 
 	HAVING (COUNT( ?geometrycontext) > 1)
  }
  }
  union
  {
  ?waterbody rdf:type Ontology_Vicmap:Waterbody;
              omg:hasGeometry ?geometry.
  ?geometry Ontology_Vicmap:hasPFI ?pfi;
            omg:hasGeometryContext ?geometrycontext;
            Ontology_Vicmap:hasSource ?source;
            Ontology_Vicmap:hasCreateDate ?date.
  ?source prov:wasAttributedTo ?attr.
  ?attr foaf:givenName ?gname.
  
  ?geometrycontext Ontology_Vicmap:isAuthoritative 	"false"^^<http://www.w3.org/2001/XMLSchema#boolean>
  
  {
  select ?waterbody
 	where
    {
      ?waterbody rdf:type Ontology_Vicmap:Waterbody;
              omg:hasGeometry ?geometry.
  	 ?geometry omg:hasGeometryContext ?geometrycontext.
  
  FILTER ( contains(str(?geometrycontext), 'true') || contains(str(?geometrycontext),'false'))
    }
    GROUP BY ?waterbody 
 	HAVING (COUNT( ?geometrycontext) > 1)
  }
  }
  

}

#9. Which water bodies have no authoritative geometry, and appear only in the machine-learned data set?  

# SELECT (STRAFTER(STR(?waterbody), '#') AS ?waterbodyLocalName)
#  	#?geometrycontext
#  	?pfi   #?name #?gname
#  	(STRAFTER(STR(?geometry), '#') AS ?geometryLocalName)
#  	?date 
#  	(STRAFTER(STR(?geometrycontext), '#') AS ?geometrycontextName)

# WHERE 

# {
#   ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi;
#             omg:hasGeometryContext ?geometrycontext;
#             Ontology_Vicmap:hasSource ?source;
#             Ontology_Vicmap:hasCreateDate ?date.
#   ?source prov:wasAttributedTo ?attr.
  
#   ?geometrycontext Ontology_Vicmap:isAuthoritative "false"^^<http://www.w3.org/2001/XMLSchema#boolean>.
  
# }

# # 10. Provide the chronological history of updates (description and dates) for a specific authoritative geometry. 
# SELECT (STRAFTER(STR(?waterbody), '#') AS ?waterbodyLocalName)
#   		(STRAFTER(STR(?geometry), '#') AS ?geometryLocalName)
# 		?createDate 
# 	   ?orgCaptured ?PersonCaptured

#  	(STRAFTER(STR(?geometrycontext), '#') AS ?Authoritativeness)

# WHERE 

# {
#   {?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI "8253351"^^<http://www.w3.org/2001/XMLSchema#int>;
#             omg:hasGeometryContext ?geometrycontext;
#             Ontology_Vicmap:hasSource ?source;
#             Ontology_Vicmap:hasCreateDate ?createDate.
#   ?source prov:wasAttributedTo ?attr.
#     ?attr foaf:name ?orgCaptured.}
#   union
#   {
#     ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI "8253351"^^<http://www.w3.org/2001/XMLSchema#int>;
#             omg:hasGeometryContext ?geometrycontext;
#             Ontology_Vicmap:hasSource ?source;
#             Ontology_Vicmap:hasCreateDate ?createDate.
#   ?source prov:wasAttributedTo ?attr.
#     ?attr foaf:givenName ?PersonCaptured.
    
#   }
  
# }



# 11. Provide the history of updates to the attributes of a specific authoritative water body. 

# SELECT (STRAFTER(STR(?waterbody), '#') AS ?Waterbody)
#   		(STRAFTER(STR(?geometry), '#') AS ?geometryName)
# 		?createDate 
# 	   ?orgCaptured ?personCaptured

#  	(STRAFTER(STR(?geometrycontext), '#') AS ?Authoritativeness)

# WHERE 

# {
#   {
#   ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               Ontology_Vicmap:waterbodyID "1"^^<http://www.w3.org/2001/XMLSchema#int>;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi;
#             omg:hasGeometryContext ?geometrycontext;
#             Ontology_Vicmap:hasSource ?source;
#             Ontology_Vicmap:hasCreateDate ?createDate.
#   ?source prov:wasAttributedTo ?attr.
#   ?attr foaf:name ?orgCaptured.
#   }
#   Union
#   {
#     ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               Ontology_Vicmap:waterbodyID "1"^^<http://www.w3.org/2001/XMLSchema#int>;
#               omg:hasGeometry ?geometry.
#   	 ?geometry Ontology_Vicmap:hasPFI ?pfi;
#             omg:hasGeometryContext ?geometrycontext;
#             Ontology_Vicmap:hasSource ?source;
#             Ontology_Vicmap:hasCreateDate ?createDate.
#   ?source prov:wasAttributedTo ?attr.
#   ?attr foaf:givenName ?personCaptured.
#   }
  
# }


### construct for visualization of KG

PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
prefix Ontology_Vicmap:<http://www.semanticweb.org/mkazemi/ontologies/2023/8/Ontology_Vicmap#>
prefix omg:<https://w3id.org/omg#>
prefix owl:<http://www.w3.org/2002/07/owl#>
prefix prov:<http://www.w3.org/ns/prov#>
prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs:<http://www.w3.org/2000/01/rdf-schema#>
prefix foaf:<http://xmlns.com/foaf/0.1/>

construct
{
    ?waterbody rdf:type Ontology_Vicmap:Waterbody;
            Ontology_Vicmap:waterbodyID "1"^^xsd:int;
            omg:hasGeometry ?geometry.
        ?geometry rdf:type omg:Geometry;
                  omg:hasGeometryContext ?geomContext;
                  Ontology_Vicmap:hasSource ?source.
        ?source rdf:type prov:Entity;
        	prov:wasAttributedTo ?attr.
        ?attr rdf:type prov:Agent.

}

where
{
    {?waterbody rdf:type Ontology_Vicmap:Waterbody;
            Ontology_Vicmap:waterbodyID "1"^^xsd:int;
            omg:hasGeometry ?geometry.
        ?geometry rdf:type omg:Geometry;
                  omg:hasGeometryContext ?geomContext;
                  Ontology_Vicmap:hasSource ?source.
        ?source rdf:type prov:Entity;
                prov:wasAttributedTo ?attr.
                
        ?attr rdf:type prov:Person.}

            UNION
    {?waterbody rdf:type Ontology_Vicmap:Waterbody;
            Ontology_Vicmap:waterbodyID "1"^^xsd:int;
            omg:hasGeometry ?geometry.
        ?geometry rdf:type omg:Geometry;
                  omg:hasGeometryContext ?geomContext;
                  Ontology_Vicmap:hasSource ?source.
        ?source rdf:type prov:Entity;
        	prov:wasAttributedTo ?attr.
                
        ?attr rdf:type prov:Organization.

    }
    }
#%%

# # Add instances of waterbody_ML

# for index, row in wb_ml.iterrows():
    
#     wb_ml_instance = ontology_ns["wb_ml{0}".format(index)]
#     polygon_ml_instance = ontology_ns["polygon_wb_ml{0}".format(index)]
    
#     waterbody_class = ontology_ns["WaterBody"]
#     geometry_class = ontology_ns["Geometry"]


#     g.add((wb_ml_instance, ontology_ns["hasGeometry"]  , polygon_ml_instance ))
    
#     g.add((polygon_ml_instance, RDF.type, geometry_class))

#     g.add((wb_ml_instance, RDF.type, waterbody_class))
    
#     g.add((wb_ml_instance, ontology_ns["hasPFI"], Literal(row['pfi'], datatype=xsd_ns["int"])))
#     g.add((wb_ml_instance, ontology_ns["hasUFI"], Literal(row['ufi'], datatype=xsd_ns["int"])))
#     g.add((wb_ml_instance, ontology_ns["hasFeatureType"], Literal(row['feature_ty'], datatype=xsd_ns["string"])))
#     g.add((wb_ml_instance, ontology_ns["hasCreateDate"], Literal(datetime.strptime(row['create_dat'], "%Y/%m/%d").strftime("%Y-%m-%dT%H:%M:%S"),\
#                                                            datatype=xsd_ns["dateTime"])))
#     g.serialize(destination="populated_ontology.rdf", format="xml")


# # Add instances of waterbody_point

# for index, row in wb_point.iterrows():
    
#     wb_point_instance = ontology_ns["wb_point{0}".format(index)]
#     point_instance = ontology_ns["point_wb{0}".format(index)]
    
#     waterbody_class = ontology_ns["WaterBody"]
#     geometry_class = ontology_ns["Geometry"]


#     g.add((wb_point_instance, ontology_ns["hasGeometry"]  , point_instance ))
    
#     g.add((point_instance, RDF.type, geometry_class))

#     g.add((wb_point_instance, RDF.type, waterbody_class))
    
#     g.add((wb_point_instance, ontology_ns["hasPFI"], Literal(row['pfi'], datatype=xsd_ns["int"])))
#     g.add((wb_point_instance, ontology_ns["hasUFI"], Literal(row['ufi'], datatype=xsd_ns["int"])))
#     g.add((wb_point_instance, ontology_ns["hasFeatureType"], Literal(row['feature_ty'], datatype=xsd_ns["string"])))
#     g.add((wb_point_instance, ontology_ns["hasCreateDate"], Literal(datetime.strptime(row['create_dat'], "%Y/%m/%d").strftime("%Y-%m-%dT%H:%M:%S"),\
#                                                            datatype=xsd_ns["dateTime"])))
#     g.serialize(destination="populated_ontology.rdf", format="xml")


# # Add instances of waterbody_polygon


# for index, row in wb_polygon.iterrows():
    
#     wb_polygon_instance = ontology_ns["wb_polygon{0}".format(index)]
#     polygon_instance = ontology_ns["polygon_wb{0}".format(index)]
    
#     waterbody_class = ontology_ns["WaterBody"]
#     geometry_class = ontology_ns["Geometry"]


#     g.add((wb_polygon_instance, ontology_ns["hasGeometry"]  , polygon_instance ))
    
#     g.add((polygon_instance, RDF.type, geometry_class))

#     g.add((wb_polygon_instance, RDF.type, waterbody_class))
    
#     g.add((wb_polygon_instance, ontology_ns["hasPFI"], Literal(row['pfi'], datatype=xsd_ns["int"])))
#     g.add((wb_polygon_instance, ontology_ns["hasUFI"], Literal(row['ufi'], datatype=xsd_ns["int"])))
#     g.add((wb_polygon_instance, ontology_ns["hasFeatureType"], Literal(row['feature_ty'], datatype=xsd_ns["string"])))
#     g.add((wb_polygon_instance, ontology_ns["hasCreateDate"], Literal(datetime.strptime(row['create_dat'], "%Y/%m/%d").strftime("%Y-%m-%dT%H:%M:%S"),\
#                                                            datatype=xsd_ns["dateTime"])))
#     g.serialize(destination="populated_ontology.rdf", format="xml")
    




#%%

# Execute SPARQL query over the populated KG

from SPARQLWrapper import SPARQLWrapper, JSON
import string

p_names = ['alex gillon',
           'alexander thomson',
           'alistair knox',
           'ambrose pratt',
           'angus mcmillan',
           'barry simon',
           'russell clark',
           'sam jamieson',
           'william hovell',
           'ben moore']

p_names = [string.capwords(i) for i in p_names]

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

p_names_abstract = [] 
for i in p_names:
    
    
    query = f"""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX quepy: <http://www.machinalis.com/quepy#>
    PREFIX dbpedia: <http://dbpedia.org/ontology/>
    PREFIX dbpprop: <http://dbpedia.org/property/>
    PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
    SELECT ?person ?name ?abstract
    WHERE {{
        ?person a foaf:Person .
        ?person foaf:name ?name .
        ?person dbo:abstract ?abstract .
        FILTER (str(?name) = "{i}")
        FILTER (LANGMATCHES(LANG(?abstract), "en") && CONTAINS(?abstract, "Australia"))
    }}
    LIMIT 1
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()



    for result in results["results"]["bindings"]:
        person = result["person"]["value"]
        name = result["name"]["value"]
        abstract = result["abstract"]["value"]
        # print(f"Abstract: {abstract}")
    p_names_abstract.append(abstract)


p_names_abstract = list(set(p_names_abstract))


## gender detector from a NL text

import re

def guess_gender(text):
    # Define keywords that may indicate gender
    male_keywords = ["he", "his", "himself", "Mr."]
    female_keywords = ["she", "her", "herself", "Mrs.", "Ms."]

    # Split the text into words and remove punctuation
    words = re.findall(r'\b\w+\b', text.lower())

    # Count the occurrences of male and female keywords
    male_count = sum(1 for word in words if word in male_keywords)
    female_count = sum(1 for word in words if word in female_keywords)

    # Determine the gender based on keyword counts
    if male_count > female_count:
        return "Male"
    elif female_count > male_count:
        return "Female"
    else:
        return "Unknown"

# Sample text
text = p_names_abstract[0]

# Guess the gender based on the text
gender_guess = guess_gender(text)

# Print the result
# # print(f"Gender guess: {gender_guess}")
# Gender guess: Male

gender_detector = [guess_gender(i) for i in p_names_abstract]

# #
# prefix owl: <http://www.w3.org/2002/07/owl#> 
# prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
# prefix xml: <http://www.w3.org/XML/1998/namespace> 
# prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
# prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
# prefix KG-toy: <http://www.semanticweb.org/mkazemi/ontologies/2023/7/KG-toy#> 
# base <http://www.semanticweb.org/mkazemi/ontologies/2023/7/KG-toy> 

# SELECT ?pfi ?ufi ?date
# WHERE {?s KG-toy:hasFeatureType "wb_dam";
#           KG-toy:hasPFI ?pfi;
#           KG-toy:hasUFI ?ufi;
#           KG-toy:hasCreateDate ?date}





