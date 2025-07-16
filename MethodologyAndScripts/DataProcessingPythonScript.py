#%%
## Identifying waterbodies with multiple or single representation 

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

os.chdir("/home/ubuntu/Vicmap_KG/")

wb_point = gpd.read_file("Dataset/State_Level/HY_WATER_POINT.shp")
wb_polygon = gpd.read_file("Dataset/State_Level/HY_WATER_AREA_POLYGON_GeomChecked.shp")
wb_ml = gpd.read_file("Dataset/State_Level/DamPredictions_Preliminary_V2.shp")
wb_lidar = gpd.read_file("Dataset/State_Level/bendigo_2020mar05_lakes_mga55.shp")


# # ## toy dataset
# wb_point = gpd.read_file("/home/ubuntu/Vicmap_KG/Dataset/Toy/Dataset/Waterbody_point_selected.shp")
# wb_polygon = gpd.read_file("/home/ubuntu/Vicmap_KG/Dataset/Toy/Waterbody_poly_selected.shp")
# wb_ml = gpd.read_file("/home/ubuntu/Vicmap_KG/Dataset/Toy/ML_selected.shp")
# wb_lidar = gpd.read_file("/home/ubuntu/Vicmap_KG/Dataset/Toy/bendigo_2020mar05_lakes_mga55.shp")


## importing other dataset than waterbodies

parcels = gpd.read_file("Dataset/State_Level/Vicmap_Parcels.shp")
flood_nonAuth = gpd.read_file("Dataset/State_Level/FullFloodExtents_25Jan_Detailed.shp")
flood_auth = gpd.read_file("Dataset/State_Level/VIC_FLOOD_HISTORY_PUBLIC.shp")

# ## checking the crs of layers, they should be consistent: epsg: 4283
wb_point = wb_point.to_crs("epsg:4283")
wb_polygon = wb_polygon.to_crs("epsg:4283")
wb_ml = wb_ml.to_crs("epsg:4283")
wb_lidar = wb_lidar.to_crs("epsg:4283")

#parcels = parcels.to_crs("epsg:4326")
#flood_nonAuth = flood_nonAuth.to_crs("epsg:4326")
#flood_auth = flood_auth.to_crs("epsg:4326")


# print concerted layers' crs

print(wb_point.crs)
print(wb_polygon.crs)
print(wb_ml.crs)
print(wb_lidar.crs)
#print(parcels.crs)
#print(flood_nonAuth.crs)
#print(flood_auth.crs)

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

parcels = parcels.to_crs("epsg:4326")
flood_nonAuth = flood_nonAuth.to_crs("epsg:4326")
flood_auth = flood_auth.to_crs("epsg:4326")



df1_polygon_buffer["geometry"] = df1_polygon_buffer["geometry"].buffer(10)
df2_polygon_buffer["geometry"] = df2_polygon_buffer["geometry"].buffer(10)
df4_polygon_buffer["geometry"] = df4_polygon_buffer["geometry"].buffer(10)


df1_polygon_buffer = pd.read_pickle(r'df1_polygon_buffer.pickle')
df2_polygon_buffer = pd.read_pickle(r'df2_polygon_buffer.pickle')
df4_polygon_buffer = pd.read_pickle(r'df4_polygon_buffer.pickle')


df1_polygon_buffer_wgs = df1_polygon_buffer.to_crs("epsg:4326")
df2_polygon_buffer_wgs = df2_polygon_buffer.to_crs("epsg:4326")
df4_polygon_buffer_wgs = df4_polygon_buffer.to_crs("epsg:4326")
df3_point_wgs = df3_point.to_crs("epsg:4326")


with open('df1_polygon_buffer.pickle', 'wb') as f:
    pickle.dump(df1_polygon_buffer,f, protocol=pickle.HIGHEST_PROTOCOL)

with open('df2_polygon_buffer.pickle', 'wb') as f:
    pickle.dump(df2_polygon_buffer,f, protocol=pickle.HIGHEST_PROTOCOL)


with open('df4_polygon_buffer.pickle', 'wb') as f:
    pickle.dump(df4_polygon_buffer,f, protocol=pickle.HIGHEST_PROTOCOL)
    




#%% creating waterbody instance stage

print("creating waterbody instances")

# # df1_polygon_buffer = pd.read_pickle(r'df1_polygon_buffer.pickle')
# # a =  pd.read_pickle(r'wb_instances_polygon.pickle')

wb_instances = []

####

def wb_polygon_instance(polygon1_list):
    wb_instances_polygon = []
    for index1, polygon1 in polygon1_list.iterrows():

        polygon_ml_intersect_check = wb_ml[wb_ml.intersects(polygon1["geometry"])]
        polygon_lidar_intersect_check = wb_lidar[wb_lidar.intersects(polygon1["geometry"])]
        polygon_point_intersect_check = wb_point[wb_point.within(polygon1["geometry"])]
        
        objectid = polygon1['OBJECTID']
        
        polygon1['geometry'] = df1_polygon_buffer_wgs[df1_polygon_buffer_wgs['OBJECTID']==objectid]['geometry'].iloc[0]
        polygon_ml_intersect_check = polygon_ml_intersect_check.to_crs("epsg:4326")
        polygon_lidar_intersect_check = polygon_lidar_intersect_check.to_crs("epsg:4326")
        polygon_point_intersect_check = polygon_point_intersect_check.to_crs("epsg:4326")
        
        # polygon1 = gpd.GeoDataFrame(geometry=geometry_series, columns=['geometry'])
        if not polygon_ml_intersect_check.empty and not polygon_lidar_intersect_check.empty and not polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1,
                                  polygon_ml_intersect_check.squeeze(),
                                  polygon_lidar_intersect_check.squeeze(),
                                  polygon_point_intersect_check.squeeze()))

        elif not polygon_ml_intersect_check.empty and not polygon_lidar_intersect_check.empty and polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1,
                                  polygon_ml_intersect_check.squeeze(),
                                  polygon_lidar_intersect_check.squeeze()))

        elif not polygon_ml_intersect_check.empty and polygon_lidar_intersect_check.empty and not polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1,
                                  polygon_ml_intersect_check.squeeze(),
                                  polygon_point_intersect_check.squeeze()))


        elif not polygon_ml_intersect_check.empty and polygon_lidar_intersect_check.empty and polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1,
                                  polygon_ml_intersect_check.squeeze()))

        elif polygon_ml_intersect_check.empty and not polygon_lidar_intersect_check.empty and not polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1,
                                  polygon_lidar_intersect_check.squeeze(),
                                  polygon_point_intersect_check.squeeze()))

        elif polygon_ml_intersect_check.empty and polygon_lidar_intersect_check.empty and not polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1,
                                  polygon_point_intersect_check.squeeze()))

        elif polygon_ml_intersect_check.empty and not polygon_lidar_intersect_check.empty and polygon_point_intersect_check.empty:

            wb_instances_polygon.append((polygon1,
                                  polygon_lidar_intersect_check.squeeze()))

        else:
            wb_instances_polygon.append(polygon1)
    return wb_instances_polygon

print("multiprocessing started for wb_polygon")

#  chunking the input dataset based on the number of CPUs of machine.

num_processes  = multiprocessing.cpu_count()

df1_polygon_buffer = pd.read_pickle(r'df1_polygon_buffer.pickle')

# a = wb_polygon_instance(df1_polygon_buffer)


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
    
        objectid = polygon2['OBJECTID']
        
        polygon2['geometry'] = df2_polygon_buffer_wgs[df2_polygon_buffer_wgs['OBJECTID']==objectid]['geometry'].iloc[0]
        
        ml_lidar_intersect_check = ml_lidar_intersect_check.to_crs("epsg:4326")
        ml_point_intersect_check = ml_point_intersect_check.to_crs("epsg:4326")
        
        
        ## lidar check
        
        if not ml_lidar_intersect_check.empty and not ml_point_intersect_check.empty:
                    
            wb_instances_ml.append((polygon2, 
                                  ml_lidar_intersect_check.squeeze(),
                                  ml_point_intersect_check.squeeze()))
    
    
        elif not ml_lidar_intersect_check.empty and  ml_point_intersect_check.empty:
                    
            wb_instances_ml.append((polygon2, 
                                  ml_lidar_intersect_check.squeeze()))
        
        elif  ml_lidar_intersect_check.empty and not  ml_point_intersect_check.empty:
                    
            wb_instances_ml.append((polygon2, 
                                  ml_point_intersect_check.squeeze()))
            
        else:
            wb_instances_ml.append(polygon2)
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
    
        objectid = polygon4['ORIG_FID']
        
        polygon4['geometry'] = df4_polygon_buffer_wgs[df4_polygon_buffer_wgs['ORIG_FID']==objectid]['geometry'].iloc[0]
        
        ## lidar check
        lidar_point_intersect_check = lidar_point_intersect_check.to_crs("epsg:4326")
        
        if not lidar_point_intersect_check.empty:
                    
            wb_instances_lidar.append((polygon4, 
                                 lidar_point_intersect_check.squeeze()))
            
            
        else:
            wb_instances_lidar.append(polygon4)
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
        
        objectid = point['OBJECTID']
        
        point['geometry'] = df3_point_wgs[df3_point_wgs['OBJECTID']==objectid]['geometry'].iloc[0]
                
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

     
# print("--- %s seconds ---" % (time.time() - start_time))

#%% preparing wb-instances of all layers

print('integrating all waterbodies...')

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

#wb_instances = pd.read_pickle('wb_instances.pickle')


parcels_list = [parcels.iloc[idx] for idx in range(len(parcels))] 
flood_nonAuth_list = [flood_nonAuth.iloc[idx] for idx in range(len(flood_nonAuth))]
flood_auth_list = [flood_auth.iloc[idx] for idx in range(len(flood_auth))]



dataset_total =  wb_instances + parcels_list + flood_nonAuth_list + flood_auth_list

with open('dataset_total.pickle', 'wb') as f:
    pickle.dump(dataset_total,f, protocol=pickle.HIGHEST_PROTOCOL)

print("--- %s seconds ---" % (time.time() - start_time))
