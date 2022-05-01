import pandas as pnd
import numpy as np
import sys
import traceback
import geopandas
from shapely.geometry import Point

fichier_dist="C:\\DEV\\GIS\\rwanda\\excel_dist.txt"
fichier_provinces="C:\\DEV\\GIS\\rwanda\\rwa_provinces_osm.gpkg"
output_file= "C:\\DEV\\GIS\\rwanda\\excel_dist_provinces.txt"

prov_shp=geopandas.read_file(fichier_provinces)
prov_shp.set_crs(epsg=4326, inplace=True)
df_dist=pnd.read_csv(fichier_dist, sep='\t', encoding='ISO-8859–1')
df_dist = df_dist.fillna('')
print(df_dist)

def add_prov():
    global df_dist
    global prov_shp
    df_dist["province"]=""
    df_dist['Latitude'] = df_dist['Latitude'].astype(str)
    df_dist['Longitude'] = df_dist['Longitude'].astype(str)
    for index, row_dist in df_dist.iterrows():
        if  len(row_dist["Latitude"])>0 and len(row_dist["Longitude"])>0:
            nom_jointure=row_dist["NOM_JOINTURE"].lower()
            collector=row_dist["COLLECTOR"].replace("&", "\&")
            coll_num=row_dist["COLL_NUM"].replace("&", "\&")             
            lat=row_dist["Latitude"].replace(",",".")
            long=row_dist["Longitude"].replace(",",".")
            point=Point(float(long), float(lat))
            inter=prov_shp.intersects(point)
            flag=any(x == True for x in inter)
            if flag:
                region=prov_shp.iloc[[i for i, x in enumerate(inter) if x]]
                if region is not None:
                    tmp_region=region.iloc[0]["name"]
                    df_dist.at[index, "province"]=tmp_region

add_prov()
df_dist.to_csv(output_file, sep ='\t')