#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 11:32:42 2023

@author: mkazemi
"""

#%%
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
import pickle
import time
import multiprocessing
from rtree import index
import utm

from pyproj import Proj, transform



### Stage 1: Data preparation

# 1. Geometry checking
# 2. Attributes check
# 3. CRS conversion (convert features to the correct UTM zones in Victoria (54, 55))

## importing dataset and making crs consistent

start_time = time.time()

print("loading layers")

os.chdir("/Users/mkazemi/Library/CloudStorage/OneDrive-RMITUniversity/My Mac Folders/2023/VicMap Project/GitHub/Dynamic-Vicmap/StateLevelTest/")

wb_point = gpd.read_file("VicmapHydro Dataset/HY_WATER_POINT.shp")
wb_polygon = gpd.read_file("VicmapHydro Dataset/HY_WATER_AREA_POLYGON_GeomChecked.shp")
wb_ml = gpd.read_file("VicmapHydro Dataset/DamPredictions_Preliminary_V2.shp")
wb_lidar = gpd.read_file("VicmapHydro Dataset/bendigo_2020mar05_lakes_mga55.shp")


# # ## toy dataset
# wb_point = gpd.read_file("/home/ubuntu/Vicmap_KG/Dataset/Toy/Dataset/Waterbody_point_selected.shp")
# wb_polygon = gpd.read_file("/home/ubuntu/Vicmap_KG/Dataset/Toy/Waterbody_poly_selected.shp")
# wb_ml = gpd.read_file("/home/ubuntu/Vicmap_KG/Dataset/Toy/ML_selected.shp")
# wb_lidar = gpd.read_file("/home/ubuntu/Vicmap_KG/Dataset/Toy/bendigo_2020mar05_lakes_mga55.shp")


## importing other dataset than waterbodies

parcels = gpd.read_file("VicmapHydro Dataset/Vicmap_Parcels.shp")
flood_nonAuth = gpd.read_file("VicmapHydro Dataset/FullFloodExtents_25Jan_Detailed.shp")
flood_auth = gpd.read_file("VicmapHydro Dataset/VIC_FLOOD_HISTORY_PUBLIC.shp")

## checking the crs of layers, they should be consistent: epsg: 4283
wb_point = wb_point.to_crs("epsg:4283")
wb_polygon = wb_polygon.to_crs("epsg:4283")
wb_ml = wb_ml.to_crs("epsg:4283")
wb_lidar = wb_lidar.to_crs("epsg:4283")

parcels = parcels.to_crs("epsg:4283")
flood_nonAuth = flood_nonAuth.to_crs("epsg:4283")
flood_auth = flood_auth.to_crs("epsg:4283")


# print concerted layers' crs

print(wb_point.crs)
print(wb_polygon.crs)
print(wb_ml.crs)
print(wb_lidar.crs)
print(parcels.crs)
print(flood_nonAuth.crs)
print(flood_auth.crs)

## set crs to wb_polygon: 


df_list = [wb_point, wb_polygon, wb_ml, wb_lidar]

df1_polygon = [i for i in df_list if i.geom_type.unique() =="Polygon"][0]

df2_polygon = [i for i in df_list if i.geom_type.unique() =="Polygon"][1]

df3_point = [i for i in df_list if i.geom_type.unique() =="Point"][0]

df4_polygon = [i for i in df_list if i.geom_type.unique() =="Polygon"][2]



## Embedded rules: buffer and intersection

#%% Intersection stage


## intersecting the features within the extent of the first layer

print("intersection stage")

extent_of_df2 = df2_polygon.bounds


# Filter features in the first layer within the extent of the second layer

df1_polygon_within_extent_df2 = df1_polygon.cx[extent_of_df2.minx.min():extent_of_df2.maxx.max(),
                                    extent_of_df2.miny.min():extent_of_df2.maxy.max()]


df2_df1_NotIntersect = df2_polygon[~df2_polygon.intersects(df1_polygon_within_extent_df2.unary_union)]
df4_df2_Notintersect = df4_polygon[~df4_polygon.intersects(df2_polygon.unary_union)]

with open('df2_df1_NotIntersect.pickle', 'wb') as f:
    pickle.dump(df2_df1_NotIntersect,f, protocol=pickle.HIGHEST_PROTOCOL)

with open('df4_df2_Notintersect.pickle', 'wb') as f:
    pickle.dump(df4_df2_Notintersect,f, protocol=pickle.HIGHEST_PROTOCOL)
    

# df2_df1_NotIntersect = pd.read_pickle(r'df2_df1_NotIntersect.pickle')
# df4_df2_Notintersect = pd.read_pickle(r'df4_df2_Notintersect.pickle')

    
    

#%% Buffer stage
print("Buffer stage")

# def convert_utm_zone(feature):
#     # Assuming feature is a GeoDataFrame
#     gdf = feature.copy()
    
#     if gdf.iloc[0].geometry.geom_type =='Polygon' or gdf.iloc[0].geometry.geom_type =='Polyline':
        
#         # Determine the centroid and UTM zone for each geometry
#         gdf = gdf.to_crs("epsg:4283")
#         centroids = gdf['geometry'].centroid
#         utm_zones = [utm.from_latlon(centroid.y, centroid.x)[2] for centroid in centroids]
    
#     else:
#         gdf = gdf.to_crs("epsg:4283")

#         longitude = gdf.geometry.x
#         latitude = gdf.geometry.y
#         coords_tuple = list(zip(latitude, longitude))
        
#         utm_zones = [utm.from_latlon(i[0], i[1])[2] for i in coords_tuple]
        
#     # Determine the EPSG code for each geometry
#     epsg_codes = ['epsg:32755' if zone == 55 else 'epsg:32754' for zone in utm_zones]

#     # Reproject each geometry based on its EPSG code (vectorized operation)
#     for epsg in set(epsg_codes):
#         mask = np.array(epsg_codes) == epsg
#         gdf.loc[mask, 'geometry'] = gdf.loc[mask].set_crs(gdf.crs).to_crs(epsg)['geometry']


#     return gdf


df1_polygon_buffer = df1_polygon
df2_polygon_buffer = df2_df1_NotIntersect
df4_polygon_buffer = df4_df2_Notintersect


# ## make sure the crs set to UTM, which is EPSG:32755 for the study area. This is needed for buffering in meters

df1_polygon_buffer = df1_polygon_buffer.to_crs("epsg:32755")
df2_polygon_buffer = df2_polygon_buffer.to_crs("epsg:32755")
df4_polygon_buffer = df4_polygon_buffer.to_crs("epsg:32755")
df3_point = df3_point.to_crs("epsg:32755")


wb_polygon = wb_polygon.to_crs("epsg:32755")
wb_ml = wb_ml.to_crs("epsg:32755")
wb_lidar = wb_lidar.to_crs("epsg:32755")
wb_point = wb_point.to_crs("epsg:32755")

parcels = parcels.to_crs("epsg:32755")
flood_nonAuth = flood_nonAuth.to_crs("epsg:32755")
flood_auth = flood_auth.to_crs("epsg:32755")



df1_polygon_buffer["geometry"] = df1_polygon_buffer["geometry"].buffer(10)
df2_polygon_buffer["geometry"] = df2_polygon_buffer["geometry"].buffer(10)
df4_polygon_buffer["geometry"] = df4_polygon_buffer["geometry"].buffer(10)


with open('df1_polygon_buffer.pickle', 'wb') as f:
    pickle.dump(df1_polygon_buffer,f, protocol=pickle.HIGHEST_PROTOCOL)

with open('df2_polygon_buffer.pickle', 'wb') as f:
    pickle.dump(df2_polygon_buffer,f, protocol=pickle.HIGHEST_PROTOCOL)


with open('df4_polygon_buffer.pickle', 'wb') as f:
    pickle.dump(df4_polygon_buffer,f, protocol=pickle.HIGHEST_PROTOCOL)
    


# df1_polygon_buffer = pd.read_pickle(r'df1_polygon_buffer.pickle')
# df2_polygon_buffer = pd.read_pickle(r'df2_polygon_buffer.pickle')
# df4_polygon_buffer = pd.read_pickle(r'df4_polygon_buffer.pickle')



#%% creating waterbody instance stage

print("creating waterbody instances")

# df1_polygon_buffer = pd.read_pickle(r'df1_polygon_buffer.pickle')
# a =  pd.read_pickle(r'wb_instances_polygon.pickle')

wb_instances = []

####

def wb_polygon_instance(polygon1_list):
    wb_instances_polygon = []
    for index1, polygon1 in polygon1_list.iterrows():

        polygon_ml_intersect_check = wb_ml[wb_ml.intersects(polygon1["geometry"])]
        polygon_lidar_intersect_check = wb_lidar[wb_lidar.intersects(polygon1["geometry"])]
        polygon_point_intersect_check = wb_point[wb_point.within(polygon1["geometry"])]

        if not polygon_ml_intersect_check.empty and not polygon_lidar_intersect_check.empty and not polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1.squeeze(),
                                 polygon_ml_intersect_check.squeeze(),
                                 polygon_lidar_intersect_check.squeeze(),
                                 polygon_point_intersect_check.squeeze()))

        elif not polygon_ml_intersect_check.empty and not polygon_lidar_intersect_check.empty and polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1.squeeze(),
                                 polygon_ml_intersect_check.squeeze(),
                                 polygon_lidar_intersect_check.squeeze()))

        elif not polygon_ml_intersect_check.empty and polygon_lidar_intersect_check.empty and not polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1.squeeze(),
                                 polygon_ml_intersect_check.squeeze(),
                                 polygon_point_intersect_check.squeeze()))


        elif not polygon_ml_intersect_check.empty and polygon_lidar_intersect_check.empty and polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1.squeeze(),
                                 polygon_ml_intersect_check.squeeze()))

        elif polygon_ml_intersect_check.empty and not polygon_lidar_intersect_check.empty and not polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1.squeeze(),
                                 polygon_lidar_intersect_check.squeeze(),
                                 polygon_point_intersect_check.squeeze()))

        elif polygon_ml_intersect_check.empty and polygon_lidar_intersect_check.empty and not polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1.squeeze(),
                                 polygon_point_intersect_check.squeeze()))

        elif polygon_ml_intersect_check.empty and not polygon_lidar_intersect_check.empty and polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1.squeeze(),
                                 polygon_lidar_intersect_check.squeeze()))

        else:
            wb_instances_polygon.append(polygon1.squeeze())
    return wb_instances_polygon

print("multiprocessing started for wb_polygon")

##  chunking the input dataset based on the number of CPUs of machine.

num_processes  = multiprocessing.cpu_count()

# df1_polygon_buffer = pd.read_pickle(r'df1_polygon_buffer.pickle')

#a = wb_polygon_instance(df1_polygon_buffer)


chunks_polygon1 = np.array_split(df1_polygon_buffer, num_processes)

pool = multiprocessing.Pool()
pool = multiprocessing.Pool(processes=num_processes)

wb_instances_polygon = pool.map(wb_polygon_instance, chunks_polygon1)
pool.close()

with open('wb_instances_polygon.pickle', 'wb') as f:
    pickle.dump(wb_instances_polygon,f,protocol=pickle.HIGHEST_PROTOCOL)
    
#%%  waterbody ml

print("multiprocessing started for wb_ML")


def wb_ml_instance(polygon2_list):
    wb_instances_ml = []
    for index2, polygon2 in polygon2_list.iterrows():
        
        
        ml_lidar_intersect_check = wb_lidar[wb_lidar.intersects(polygon2["geometry"])]
        ml_point_intersect_check = wb_point[wb_point.within(polygon2["geometry"])]
    
        
        ## lidar check
        
        if not ml_lidar_intersect_check.empty and not ml_point_intersect_check.empty:
                    
            wb_instances_ml.append((polygon2.squeeze(), 
                                 ml_lidar_intersect_check.squeeze(),
                                 ml_point_intersect_check.squeeze()))
    
    
        elif not ml_lidar_intersect_check.empty and  ml_point_intersect_check.empty:
                    
            wb_instances_ml.append((polygon2.squeeze(), 
                                 ml_lidar_intersect_check.squeeze()))
        
        elif  ml_lidar_intersect_check.empty and not  ml_point_intersect_check.empty:
                    
            wb_instances_ml.append((polygon2.squeeze(), 
                                 ml_point_intersect_check.squeeze()))
            
        else:
            wb_instances_ml.append(polygon2.squeeze())
    return wb_instances_ml



chunks_ml = np.array_split(df2_polygon_buffer, num_processes)

pool = multiprocessing.Pool()
pool = multiprocessing.Pool(processes=num_processes)

wb_instances_ml = pool.map(wb_ml_instance, chunks_ml)
pool.close()

with open('wb_instances_ml.pickle', 'wb') as f:
    pickle.dump(wb_instances_ml,f, protocol=2)
    
#%%  waterbody lidar

print("multiprocessing started for wb_Lidar")

def wb_lidar_instance(polygon4_list):
    wb_instances_lidar = []
    for index3, polygon4 in polygon4_list.iterrows():
        
        
        lidar_point_intersect_check = wb_point[wb_point.within(polygon4["geometry"])]
    
        
        ## lidar check
        
        if not lidar_point_intersect_check.empty:
                    
            wb_instances_lidar.append((polygon4.squeeze(), 
                                 lidar_point_intersect_check.squeeze()))
            
            
        else:
            wb_instances_lidar.append(polygon4.squeeze())
    return wb_instances_lidar

#c = wb_lidar_instance(df4_polygon_buffer)

chunks_lidar = np.array_split(df4_polygon_buffer, num_processes)

pool = multiprocessing.Pool()
pool = multiprocessing.Pool(processes=num_processes)

wb_instances_lidar = pool.map(wb_lidar_instance, chunks_lidar)
pool.close()

with open('wb_instances_lidar.pickle', 'wb') as f:
    pickle.dump(wb_instances_lidar,f,protocol=pickle.HIGHEST_PROTOCOL)

#%% waterbody point

print("multiprocessing started for wb_Points")

# Combine polygons into one GeoDataFrame
polygons1 = gpd.GeoDataFrame(geometry=df1_polygon_buffer.geometry.append(df2_polygon_buffer.geometry, ignore_index=True))
polygons = gpd.GeoDataFrame(geometry=df4_polygon_buffer.geometry.append(polygons1.geometry, ignore_index=True))



# Build a spatial index for polygons
spatial_index = index.Index()
for i, geom in enumerate(polygons.geometry):
    spatial_index.insert(i, geom.bounds)

# Check if points are not within any polygon efficiently using spatial index
def wb_point_instance(df3_point):
    points_not_within_any_polygon = []
    for i, point in df3_point.iterrows():
        point_geom = point['geometry']
        candidates = list(spatial_index.intersection(point_geom.bounds))
        if not any(polygons.iloc[candidate].geometry.contains(point_geom) for candidate in candidates):
            points_not_within_any_polygon.append(point)
            
    return points_not_within_any_polygon

chunks_points = np.array_split(df3_point, num_processes)

pool = multiprocessing.Pool()
pool = multiprocessing.Pool(processes=num_processes)

wb_instances_points = pool.map(wb_point_instance, chunks_points)
pool.close()

with open('wb_instances_points.pickle', 'wb') as f:
    pickle.dump(wb_instances_points,f, protocol=pickle.HIGHEST_PROTOCOL)

     
print("--- %s seconds ---" % (time.time() - start_time))

#%% preparing wb-instances of all layers

wb_instances_polygon = pd.read_pickle(r'wb_instances_polygon.pickle')
wb_instances_ml = pd.read_pickle(r'wb_instances_ml.pickle')
wb_instances_lidar = pd.read_pickle(r'wb_instances_lidar.pickle')
wb_instances_points = pd.read_pickle(r'wb_instances_points.pickle')


def wb_postprocess(wb_instance):
    a =[]
    for i in wb_instance:
        for j in i:
            a.append(j)
    return a
            
wb_instances = wb_postprocess(wb_instances_polygon) + wb_postprocess(wb_instances_ml) + \
    wb_postprocess(wb_instances_lidar) + wb_postprocess(wb_instances_points)

with open('wb_instances.pickle', 'wb') as f:
    pickle.dump(wb_instances,f, protocol=pickle.HIGHEST_PROTOCOL)
    
#%% add new datasets to wb_instances

wb_instances = pd.read_pickle('wb_instances.pickle')


parcels_list = [parcels.iloc[idx] for idx in range(len(parcels))] 
flood_nonAuth_list = [flood_nonAuth.iloc[idx] for idx in range(len(flood_nonAuth))]
flood_auth_list = [flood_auth.iloc[idx] for idx in range(len(flood_auth))]



dataset_total =  wb_instances + parcels_list + flood_nonAuth_list + flood_auth_list

with open('dataset_total.pickle', 'wb') as f:
    pickle.dump(dataset_total,f, protocol=pickle.HIGHEST_PROTOCOL)

print("--- %s seconds ---" % (time.time() - start_time))

       
#%% Stage 2: Defining Ontology and namespaces


print(" Populating KG stage...")

# Create a new RDF graph

g = Graph()

result = g.parse("Ontology/Ontology_Vicmap_updated.rdf")


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

hydro_polygon_metadata = pd.read_csv('VicmapHydro Dataset/metadata-hydroPolygon.csv')
hydro_polygon_metadata = hydro_polygon_metadata.replace(np.nan,"")

hydro_point_metadata = pd.read_csv('VicmapHydro Dataset/metadata-hydroPoint.csv')
hydro_point_metadata = hydro_point_metadata.replace(np.nan,"")

parcels_metadata = pd.read_csv('VicmapHydro Dataset/metadata-parcels.csv')
parcels_metadata = parcels_metadata.replace(np.nan,"")

flood_metadata = pd.read_csv('VicmapHydro Dataset/metadata-flood.csv')
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


#%% Metadata for Hydro polygon
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

print('reading total dataset ....')

total_data = pd.read_pickle('dataset_total.pickle')

start_time = time.time()

  
k =0
source = {"source":"name"}

RDFname = "KG_State_Updated_20K.rdf"

for index, i in enumerate(total_data):
    

    
    


    ## Multi-representation feature: wb_instance
    
    if type(i) ==tuple :
        wb_instance = ontology_ns["wb{0}".format(index)]
        g.add((wb_instance, RDF.type, Feature))        
        g.add((wb_instance, ontology_ns.Varietyof, Literal("Waterbody", datatype=xsd_ns["string"])))
        
        
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
                        
                        g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(j['PFI'], datatype=xsd_ns["int"])))
                        g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(j['UFI'], datatype=xsd_ns["int"])))
                        
                        # parsed_date = parser.parse(j['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                        g.add((wb_geometry_instance, ontology_ns["createDate"],\
                            Literal(j['C_DATE_PFI'],datatype=xsd_ns["string"])))
                        
                        g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(j['geometry'], datatype=schema_geo["geo"])))
                                           
                        g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(j['F_TYPE_COD'], datatype=xsd_ns["string"])))
                                      
                        # g.serialize(destination=RDFname, format="xml")
                        k +=1
                        
                    
                    else:
                        g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_point))
                        
                        g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(j['PFI'], datatype=xsd_ns["int"])))
                        g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(j['UFI'], datatype=xsd_ns["int"])))
                        
                        # parsed_date = parser.parse(j['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                        g.add((wb_geometry_instance, ontology_ns["createDate"],\
                            Literal(j['C_DATE_PFI'],datatype=xsd_ns["string"])))
                        
                        g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(j['geometry'], datatype=schema_geo["geo"])))
                                           
                        g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(j['F_TYPE_COD'], datatype=xsd_ns["string"])))
                                      
                        # g.serialize(destination=RDFname, format="xml")
                        k +=1
                    
                    
                    
                elif j['UFI'] is not None and type(j['PFI']) == type(None):
                    
                    
                    g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_ml))
                    
                    g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(j['PFI'], datatype=xsd_ns["int"])))
                    g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(j['UFI'], datatype=xsd_ns["int"])))
                    # parsed_date = parser.parse(j['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                    g.add((wb_geometry_instance, ontology_ns["createDate"],\
                        Literal(j['C_DATE_PFI'],datatype=xsd_ns["string"])))
                    
                    g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(j['geometry'], datatype=schema_geo["geo"])))
                                       
                    g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(j['F_TYPE_COD'], datatype=xsd_ns["string"])))
                    
              
                    # g.serialize(destination=RDFname, format="xml")
                    k +=1
                    
                else:
                    g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_lidar))
                    
                    g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(j['PFI'], datatype=xsd_ns["int"])))
                    g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(j['UFI'], datatype=xsd_ns["int"])))
                    # parsed_date = parser.parse(j['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                    g.add((wb_geometry_instance, ontology_ns["createDate"],\
                        Literal(j['C_DATE_PFI'],datatype=xsd_ns["string"])))
                    
                    g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(j['geometry'], datatype=schema_geo["geo"])))
                                       
                    g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(j['F_TYPE_COD'], datatype=xsd_ns["string"])))
                    
              
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
                            
                            g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(m['PFI'], datatype=xsd_ns["int"])))
                            g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(m['UFI'], datatype=xsd_ns["int"])))
                            
                            # parsed_date = parser.parse(m['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                            g.add((wb_geometry_instance, ontology_ns["createDate"],\
                                Literal(m['C_DATE_PFI'],datatype=xsd_ns["string"])))
                            
                            g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(m['geometry'], datatype=schema_geo["geo"])))
                                               
                            g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(m['F_TYPE_COD'], datatype=xsd_ns["string"])))
                            
                      
                            # g.serialize(destination=RDFname, format="xml")
    
                            k +=1
                            
                            
                        else:
                            
                        
                            g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_point))
                            
                            g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(m['PFI'], datatype=xsd_ns["int"])))
                            g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(m['UFI'], datatype=xsd_ns["int"])))
                            
                            # parsed_date = parser.parse(m['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                            g.add((wb_geometry_instance, ontology_ns["createDate"],\
                                Literal(m['C_DATE_PFI'],datatype=xsd_ns["string"])))
                            
                            g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(m['geometry'], datatype=schema_geo["geo"])))
                                               
                            g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(m['F_TYPE_COD'], datatype=xsd_ns["string"])))
                            
                      
                            # g.serialize(destination=RDFname, format="xml")
    
                            k +=1

                        
                        
                    elif m['UFI'] is not None and type(m['PFI']) == type(None):
                        
                        g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_ml))
                        
                        g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(m['PFI'], datatype=xsd_ns["int"])))
                        g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(m['UFI'], datatype=xsd_ns["int"])))
                        
                        # parsed_date = parser.parse(m['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                        g.add((wb_geometry_instance, ontology_ns["createDate"],\
                            Literal(m['C_DATE_PFI'],datatype=xsd_ns["string"])))
                        
                        g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(m['geometry'], datatype=schema_geo["geo"])))
                                           
                        g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(m['F_TYPE_COD'], datatype=xsd_ns["string"])))
                        
                  
                        # g.serialize(destination=RDFname, format="xml")

                        k +=1
                    
                    else:
                        g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_lidar))
                        
                        g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(m['PFI'], datatype=xsd_ns["int"])))
                        g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(m['UFI'], datatype=xsd_ns["int"])))
                        
                        # parsed_date = parser.parse(m['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                        g.add((wb_geometry_instance, ontology_ns["createDate"],\
                            Literal(m['C_DATE_PFI'],datatype=xsd_ns["string"])))
                        
                        g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(m['geometry'], datatype=schema_geo["geo"])))
                                           
                        g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(m['F_TYPE_COD'], datatype=xsd_ns["string"])))
                        
                  
                        # g.serialize(destination=RDFname, format="xml")

                        k +=1
                
       
    
    else:
        
        ## Define waterbody instances of feature
        if 'F_TYPE_COD' in i.keys():
                
            wb_instance = ontology_ns["wb{0}".format(index)]
            g.add((wb_instance, RDF.type, Feature))        
            g.add((wb_instance, ontology_ns.Varietyof, Literal("Waterbody", datatype=xsd_ns["string"])))
            
            
            wb_geometry = i["geometry"].geom_type
            wb_geometry_instance = ontology_ns["{0}{1}".format(wb_geometry,k)]
            
            g.add((wb_instance, geosparql["hasGeometry"], wb_geometry_instance))
            g.add((wb_geometry_instance, RDF.type, Geometry))   
            
        elif 'parcel_ufi' in i.keys():
            
            parcel_instance = ontology_ns["parcel{0}".format(index)]
            g.add((parcel_instance, RDF.type, Feature))
            g.add((parcel_instance, ontology_ns.Varietyof, Literal("Parcels", datatype=xsd_ns["string"])))
            
            parcel_geometry = i["geometry"].geom_type
            parcel_geometry_instance = ontology_ns["{0}{1}".format(parcel_geometry,k)]
            
            g.add((parcel_instance, geosparql["hasGeometry"], parcel_geometry_instance))
            g.add((parcel_geometry_instance, RDF.type, Geometry))  
        
        elif 'FLOOD_OBS_' in i.keys():
            
            floodA_instance = ontology_ns["FloodA{0}".format(index)]
            g.add((floodA_instance, RDF.type, Feature))
            g.add((floodA_instance, ontology_ns.Varietyof, Literal("Flood_Authoritative", datatype=xsd_ns["string"])))
            
            floodA_geometry = i["geometry"].geom_type
            floodA_geometry_instance = ontology_ns["{0}{1}".format(floodA_geometry,k)]
            
            g.add((floodA_instance, geosparql["hasGeometry"], floodA_geometry_instance))
            g.add((floodA_geometry_instance, RDF.type, Geometry))  
            
        else:
            floodNA_instance = ontology_ns["floodNA{0}".format(index)]
            g.add((floodNA_instance, RDF.type, Feature))
            g.add((floodNA_instance, ontology_ns.Varietyof, Literal("Flood_NonAuthoritative", datatype=xsd_ns["string"])))
            
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
                     
                    g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(i['PFI'], datatype=xsd_ns["int"])))
                    g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(i['UFI'], datatype=xsd_ns["int"])))
                     # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                    g.add((wb_geometry_instance, ontology_ns["createDate"],\
                         Literal(i['C_DATE_PFI'],datatype=xsd_ns["string"])))
                     
                    g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=schema_geo["geo"])))
                                        
                    g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(i['F_TYPE_COD'], datatype=xsd_ns["string"])))
                     
               
                     # g.serialize(destination=RDFname, format="xml")
        
                    k +=1

                else:
                     
                     
                    g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_point))
                     
                    g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(i['PFI'], datatype=xsd_ns["int"])))
                    g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(i['UFI'], datatype=xsd_ns["int"])))
                     # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                    g.add((wb_geometry_instance, ontology_ns["createDate"],\
                         Literal(i['C_DATE_PFI'],datatype=xsd_ns["string"])))
                     
                    g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=schema_geo["geo"])))
                                        
                    g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(i['F_TYPE_COD'], datatype=xsd_ns["string"])))
                     
               
                     # g.serialize(destination=RDFname, format="xml")
        
                    k +=1
                 
                 
            elif i['UFI'] is not None and type(i['PFI']) == type(None):
                 
                g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_ml))
                 
                g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(i['PFI'], datatype=xsd_ns["int"])))
                g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(i['UFI'], datatype=xsd_ns["int"])))
                 # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
                g.add((wb_geometry_instance, ontology_ns["createDate"],\
                     Literal(i['C_DATE_PFI'],datatype=xsd_ns["string"])))
                 
                g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=schema_geo["geo"])))
                                    
                g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(i['F_TYPE_COD'], datatype=xsd_ns["string"])))
                 
           
                 # g.serialize(destination=RDFname, format="xml")
    
                k +=1
                 
            else:
        
              
             g.add((wb_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_lidar))
              
             g.add((wb_geometry_instance, ontology_ns["hasPFI"], Literal(i['PFI'], datatype=xsd_ns["int"])))
             g.add((wb_geometry_instance, ontology_ns["hasUFI"], Literal(i['UFI'], datatype=xsd_ns["int"])))
              # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
             g.add((wb_geometry_instance, ontology_ns["createDate"],\
                  Literal(i['C_DATE_PFI'],datatype=xsd_ns["string"])))
              
             g.add((wb_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=schema_geo["geo"])))
                                 
             g.add((wb_geometry_instance, ontology_ns["Varietyof"], Literal(i['F_TYPE_COD'], datatype=xsd_ns["string"])))
              
        

             k +=1

        elif 'parcel_ufi' in i.keys():
             
             
            g.add((parcel_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_parcels))
             
            g.add((parcel_geometry_instance, ontology_ns["hasPFI"], Literal(i['parcel_pfi'], datatype=xsd_ns["int"])))
            g.add((parcel_geometry_instance, ontology_ns["hasUFI"], Literal(i['parcel_ufi'], datatype=xsd_ns["int"])))
             # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
            g.add((parcel_geometry_instance, ontology_ns["createDate"],\
                 Literal(i['parcel_reg'],datatype=xsd_ns["string"])))
             
            g.add((parcel_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=schema_geo["geo"])))
                                
            g.add((parcel_geometry_instance, ontology_ns["Varietyof"], Literal('parcels', datatype=xsd_ns["string"])))
            k +=1
            
        elif 'FLOOD_OBS_' in i.keys():
            
            g.add((floodA_geometry_instance, ontology_ns['hasGeometryProvenance'], hydro_dataset_flood))
            
            g.add((floodA_geometry_instance, ontology_ns["hasPFI"], Literal('', datatype=xsd_ns["int"])))
            g.add((floodA_geometry_instance, ontology_ns["hasUFI"], Literal('', datatype=xsd_ns["int"])))
            # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
            g.add((floodA_geometry_instance, ontology_ns["createDate"],\
                Literal(i['OBS_CREATE'],datatype=xsd_ns["string"])))
            
            g.add((floodA_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=schema_geo["geo"])))
                               
            g.add((floodA_geometry_instance, ontology_ns["Varietyof"], Literal('Flood_Authoritative', datatype=xsd_ns["string"])))
            k +=1
        
        else:
            
            g.add((floodNA_geometry_instance, ontology_ns['hasGeometryProvenance'], flood_dataset_nonAuth))
            
            g.add((floodNA_geometry_instance, ontology_ns["hasPFI"], Literal(i['PFI'], datatype=xsd_ns["int"])))
            g.add((floodNA_geometry_instance, ontology_ns["hasUFI"], Literal(i['UFI'], datatype=xsd_ns["int"])))
            # parsed_date = parser.parse(i['C_DATE_PFI']).strftime("%Y%m%d%H%M%S")
            g.add((floodNA_geometry_instance, ontology_ns["createDate"],\
                Literal(i['C_DATE_PFI'],datatype=xsd_ns["string"])))
            
            g.add((floodNA_geometry_instance, ontology_ns["geometryCoordinates"], Literal(i['geometry'], datatype=schema_geo["geo"])))
                               
            g.add((floodNA_geometry_instance, ontology_ns["Varietyof"], Literal('Flood_NonAuthoritative', datatype=xsd_ns["string"])))
            k +=1
        


g.serialize(destination=RDFname, format="xml")

print("--- %s seconds ---" % (time.time() - start_time))


        
#%% Question for Sparql

# 1. What water features are represented with point and polygon geometries?  

# Response: list of waterbodies with their pfi and geometry.



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

# PREFIX omg: <https://w3id.org/omg#>
# SELECT (STRAFTER(STR(?waterbody), '#') AS ?WaterbodyName)
#  	?pfi 
#  	(STRAFTER(STR(?geometry), '#') AS ?geometryName)

# WHERE 
# {
#   ?waterbody rdf:type geosparql:Feature;
#               geosparql:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi.
              
  
#   { Select ?waterbody
#     where {
#     ?waterbody rdf:type geosparql:Feature;
#               geosparql:hasGeometry ?geometry1;
#               geosparql:hasGeometry ?geometry2;
#               geosparql:hasGeometry ?geometry.

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
# 
# {
#   ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi;
#             Ontology_Vicmap:hasCreateDate ?date.
#   FILTER ( xsd:int(?pfi) = 8253315)
#      
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

# SELECT (STRAFTER(STR(?waterbody), '#') AS ?waterbodyLocalName)
#  	?pfi ?auth  ?name ?gname
#  	(STRAFTER(STR(?geometry), '#') AS ?geometryLocalName)
#  	?date 
#  	(STRAFTER(STR(?geometrycontext), '#') AS ?geometrycontextName)

# WHERE 

# {
#   {
#   ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi;
#             omg:hasGeometryContext ?geometrycontext;
#             Ontology_Vicmap:hasSource ?source;
#             Ontology_Vicmap:hasCreateDate ?date.
#   ?source prov:wasAttributedTo ?attr.
  
#   ?geometrycontext Ontology_Vicmap:isAuthoritative 	"true"^^<http://www.w3.org/2001/XMLSchema#boolean>.
#   ?attr foaf:name ?name.
  
  
#   {
#   select ?waterbody
#  	where
#     {
#       ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   	 ?geometry omg:hasGeometryContext ?geometrycontext.
  
#   FILTER ( contains(str(?geometrycontext), 'true') || contains(str(?geometrycontext),'false'))
#     }
#     GROUP BY ?waterbody 
#  	HAVING (COUNT( ?geometrycontext) > 1)
#   }
#   }
#   union
#   {
#   ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   ?geometry Ontology_Vicmap:hasPFI ?pfi;
#             omg:hasGeometryContext ?geometrycontext;
#             Ontology_Vicmap:hasSource ?source;
#             Ontology_Vicmap:hasCreateDate ?date.
#   ?source prov:wasAttributedTo ?attr.
#   ?attr foaf:givenName ?gname.
  
#   ?geometrycontext Ontology_Vicmap:isAuthoritative 	"false"^^<http://www.w3.org/2001/XMLSchema#boolean>
  
#   {
#   select ?waterbody
#  	where
#     {
#       ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#               omg:hasGeometry ?geometry.
#   	 ?geometry omg:hasGeometryContext ?geometrycontext.
  
#   FILTER ( contains(str(?geometrycontext), 'true') || contains(str(?geometrycontext),'false'))
#     }
#     GROUP BY ?waterbody 
#  	HAVING (COUNT( ?geometrycontext) > 1)
#   }
#   }
  

# }

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

# PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
# prefix Ontology_Vicmap:<http://www.semanticweb.org/mkazemi/ontologies/2023/8/Ontology_Vicmap#>
# prefix omg:<https://w3id.org/omg#>
# prefix owl:<http://www.w3.org/2002/07/owl#>
# prefix prov:<http://www.w3.org/ns/prov#>
# prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# prefix rdfs:<http://www.w3.org/2000/01/rdf-schema#>
# prefix foaf:<http://xmlns.com/foaf/0.1/>

# construct
# {
#     ?waterbody rdf:type Ontology_Vicmap:Waterbody;
#             Ontology_Vicmap:waterbodyID "1"^^xsd:int;
#             omg:hasGeometry ?geometry.
#         ?geometry rdf:type omg:Geometry;
#                   omg:hasGeometryContext ?geomContext;
#                   Ontology_Vicmap:hasSource ?source.
#         ?source rdf:type prov:Entity;
#         	prov:wasAttributedTo ?attr.
#         ?attr rdf:type prov:Agent.

# }

# where
# {
#     {?waterbody rdf:type Ontology_Vicmap:Waterbody;
#             Ontology_Vicmap:waterbodyID "1"^^xsd:int;
#             omg:hasGeometry ?geometry.
#         ?geometry rdf:type omg:Geometry;
#                   omg:hasGeometryContext ?geomContext;
#                   Ontology_Vicmap:hasSource ?source.
#         ?source rdf:type prov:Entity;
#                 prov:wasAttributedTo ?attr.
                
#         ?attr rdf:type prov:Person.}

#             UNION
#     {?waterbody rdf:type Ontology_Vicmap:Waterbody;
#             Ontology_Vicmap:waterbodyID "1"^^xsd:int;
#             omg:hasGeometry ?geometry.
#         ?geometry rdf:type omg:Geometry;
#                   omg:hasGeometryContext ?geomContext;
#                   Ontology_Vicmap:hasSource ?source.
#         ?source rdf:type prov:Entity;
#         	prov:wasAttributedTo ?attr.
                
#         ?attr rdf:type prov:Organization.

#     }
#     }

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
#     g.add((wb_ml_instance, ontology_ns["Varietyof"], Literal(row['feature_ty'], datatype=xsd_ns["string"])))
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
#     g.add((wb_point_instance, ontology_ns["Varietyof"], Literal(row['feature_ty'], datatype=xsd_ns["string"])))
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

# Execute SPARQL query over the populated KG

# from SPARQLWrapper import SPARQLWrapper, JSON
# import string

# p_names = ['alex gillon',
#            'alexander thomson',
#            'alistair knox',
#            'ambrose pratt',
#            'angus mcmillan',
#            'barry simon',
#            'russell clark',
#            'sam jamieson',
#            'william hovell',
#            'ben moore']

# p_names = [string.capwords(i) for i in p_names]

# sparql = SPARQLWrapper("http://dbpedia.org/sparql")

# p_names_abstract = [] 
# for i in p_names:
    
    
#     query = f"""
#     PREFIX owl: <http://www.w3.org/2002/07/owl#>
#     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#     PREFIX foaf: <http://xmlns.com/foaf/0.1/>
#     PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
#     PREFIX quepy: <http://www.machinalis.com/quepy#>
#     PREFIX dbpedia: <http://dbpedia.org/ontology/>
#     PREFIX dbpprop: <http://dbpedia.org/property/>
#     PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
#     SELECT ?person ?name ?abstract
#     WHERE {{
#         ?person a foaf:Person .
#         ?person foaf:name ?name .
#         ?person dbo:abstract ?abstract .
#         FILTER (str(?name) = "{i}")
#         FILTER (LANGMATCHES(LANG(?abstract), "en") && CONTAINS(?abstract, "Australia"))
#     }}
#     LIMIT 1
#     """
#     sparql.setQuery(query)
#     sparql.setReturnFormat(JSON)

#     results = sparql.query().convert()



#     for result in results["results"]["bindings"]:
#         person = result["person"]["value"]
#         name = result["name"]["value"]
#         abstract = result["abstract"]["value"]
#         # print(f"Abstract: {abstract}")
#     p_names_abstract.append(abstract)


# p_names_abstract = list(set(p_names_abstract))


# ## gender detector from a NL text

# import re

# def guess_gender(text):
#     # Define keywords that may indicate gender
#     male_keywords = ["he", "his", "himself", "Mr."]
#     female_keywords = ["she", "her", "herself", "Mrs.", "Ms."]

#     # Split the text into words and remove punctuation
#     words = re.findall(r'\b\w+\b', text.lower())

#     # Count the occurrences of male and female keywords
#     male_count = sum(1 for word in words if word in male_keywords)
#     female_count = sum(1 for word in words if word in female_keywords)

#     # Determine the gender based on keyword counts
#     if male_count > female_count:
#         return "Male"
#     elif female_count > male_count:
#         return "Female"
#     else:
#         return "Unknown"

# # Sample text
# text = p_names_abstract[0]

# # Guess the gender based on the text
# gender_guess = guess_gender(text)

# # Print the result
# # # print(f"Gender guess: {gender_guess}")
# # Gender guess: Male

# gender_detector = [guess_gender(i) for i in p_names_abstract]

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




