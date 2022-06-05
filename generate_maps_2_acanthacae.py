import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import geopandas
import rioxarray as rxr
from rasterio.plot import plotting_extent
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep
import shapely
from matplotlib_scalebar.scalebar import ScaleBar
from pyproj import Proj, transform, CRS, Transformer
from shapely.ops import nearest_points
import numpy as np
import pandas
import rasterio
import unidecode

#print(os.environ['PROJ_LIB'])
#print("--------------------")
#del os.environ['PROJ_LIB']
#print(os.environ['PROJ_LIB'])
#print("--------------------")
os.environ["PROJ_LIB"]="C:\\OSGeo4W\\share\\proj"
fp = "C:\\DEV\GIS\\burundi\\bdi_export.tif"

fichier_dist="C:\\DEV\\salvator\\april\\17\\data\\distribution_provinces_ajoutees_corrections.txt"
fichier_taxo="C:\\DEV\\salvator\\april\\17\\data\\taxo_distribution_control_17april.txt"

output_map="C:\\DEV\\salvator\\maps\\"


def detect_distribution(row):
    distribution_acceptee=None
    if 'current_name' in  row:
        current_name=row["current_name"]
        distribution_acceptee=df_dist.loc[df_dist["NOM_JOINTURE"].str.lower().replace("\\&","&")==current_name.lower().replace("\\&","&")]
        distribution_acceptee2=df_dist.loc[(df_dist["JOINTURE"].str.lower().replace("\\&","&")==current_name.lower().replace("\\&","&")) & (df_dist["JOINTURE"].str.lower() !=  df_dist["NOM_JOINTURE"].str.lower()) ]
        if distribution_acceptee is None:
            distribution_acceptee=distribution_acceptee2
        else:
            distribution_acceptee=pandas.DataFrame(np.concatenate([distribution_acceptee.values, distribution_acceptee2.values]), columns=distribution_acceptee.columns)
    synonyms={}
    if 'synonyms' in  row:
        synonyms=row["synonyms"]
    if(len(synonyms)>0):
        ##print(synonyms)
        for syn in synonyms:
            ##print(syn)
            distribution_acceptee_syno=df_dist.loc[df_dist["NOM_JOINTURE"].str.lower().replace("\\&","&")==syn.lower().replace("\\&","&")]
            distribution_acceptee_syno2=df_dist.loc[(df_dist["JOINTURE"].str.lower().replace("\\&","&")==syn.lower().replace("\\&","&")) & (df_dist["JOINTURE"].str.lower() !=  df_dist["NOM_JOINTURE"].str.lower()) ]
            if distribution_acceptee_syno is None:
                distribution_acceptee_syno=distribution_acceptee_syno2
            else:
                distribution_acceptee_syno=pandas.DataFrame(np.concatenate([distribution_acceptee_syno.values, distribution_acceptee_syno2.values]), columns=distribution_acceptee_syno.columns)
            if not distribution_acceptee is None:
               distribution_acceptee=pandas.DataFrame(np.concatenate([distribution_acceptee.values, distribution_acceptee_syno.values]), columns=distribution_acceptee.columns)
            else:
                distribution_acceptee=distribution_acceptee_syno
    return distribution_acceptee

def go_plot(p_bbox, p_raster_data, p_raster_data_extent,  family, species, points, p_xticks, p_jticks, p_xlabels, p_ylabels):     
    f, ax = plt.subplots(figsize=(7,7))
    ep.plot_rgb(p_raster_data.values,
                rgb=[0, 1, 2],
                ax=ax,
                #title="test Burundi",                
                extent=p_raster_data_extent)
    
    p_points=geopandas.GeoDataFrame(geometry=points)
    p_points.set_crs(epsg=3857, inplace=True)
    p_points.plot(ax=ax,  color="black", markersize=80 )
    
    
    ax.set_xticks(p_xticks)
    ax.set_yticks(p_jticks)
    ax.set_xticklabels(p_xlabels)
    ax.set_yticklabels(p_ylabels)
    ax.set_xlim(p_bbox[0], p_bbox[1])
    ax.set_ylim(p_bbox[2], p_bbox[3])
    ax.add_artist(ScaleBar(
        dx=1,
        box_alpha=0.1,
        location='lower left'
    ))    
    print(family)
    print(species)
    ax.set_title(species)
    name_file=(output_map+family+"_"+species).replace("&", "and").replace(" ", "_").replace(".", "_").strip("_")
    name_file= unidecode.unidecode(name_file)
    #plt.subplots(figsize=(1800,1700))
    plt.savefig(name_file+".png", dpi=600, bbox_inches='tight')
    plt.close('all') 
    
# main    
transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
bbox_all=[28.9, 31, -4.7, -2.2]
raster_data = rxr.open_rasterio(fp, masked=True).rio.reproject("epsg:3857")

raster_data_extent = plotting_extent(raster_data[0], 
                                   raster_data.rio.transform())



bbox_1=transformer.transform(bbox_all[0], bbox_all[2])
bbox_2=transformer.transform(bbox_all[0], bbox_all[3])
bbox_3=transformer.transform( bbox_all[1], bbox_all[3])
bbox_4=transformer.transform(bbox_all[1], bbox_all[2])

bbox_conv=[bbox_1[0],bbox_4[0],bbox_1[1], bbox_3[1]]


xticks=[]
jticks=[]
xlabels=[]
jlabels=[]
i=bbox_all[0]
while i <= bbox_all[1] :
    #print(i)
    if (i % 0.5) ==0:
        pt_coord=transformer.transform(i,bbox_all[2])
        xticks.append(pt_coord[0])
        xlabels.append(i)
    i=round(i+0.1,2)
j=bbox_all[2]
while j <= bbox_all[3] :
    if (j % 0.5) ==0:
        pt_coord=transformer.transform(bbox_all[0],j)
        jticks.append(pt_coord[1])
        jlabels.append(j)
    j=round(j+0.1,2)
    
####



df_dist=pandas.read_csv(fichier_dist, sep='\t', encoding='ISO-8859–1')
df_taxo=pandas.read_csv(fichier_taxo, sep='\t', encoding='ISO-8859–1')
df_dist["Species_Trim"]=df_dist["Species_Trim"].str.strip()
df_taxo['NOM_ACTUEL_A_UTILISER'] = df_taxo['NOM_ACTUEL_A_UTILISER'].str.strip()
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].replace(np.nan,"")
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].fillna('')
df_dist['NOM_JOINTURE'] = df_dist['NOM_JOINTURE'].str.strip()

list_species=df_taxo["NOM_ACTUEL_A_UTILISER"].unique()
i=1
def_species=df_taxo[(df_taxo['rank']=="Species_or_higher") & (df_taxo['family']=="Acanthaceae")]
for index, row in def_species.iterrows():
    current_name=row["NOM_ACTUEL_A_UTILISER"] 
    print(current_name)
    row["current_name"]=current_name
    dist=detect_distribution(row)
    #print(dist)
    list_points=[]
    for index2, row2 in dist.iterrows():
        #print(row2)
        #print(row2["Longitude"])
        #print(row2["Latitude"])
        #list_points.append(shapely.geometry.Point(transformer.transform(row2["Longitude"], row2["Latitude"])))
        if len(str(row2["Longitude"])) and len(str(row2["Latitude"])):
            pt=shapely.geometry.Point(transformer.transform(float(str(row2["Longitude"]).replace(",",".")), float(str(row2["Latitude"]).replace(",","."))))
            list_points.append(pt)
        #print(pt)
    #print(list_points)
    species=row["NOM_ACTUEL_A_UTILISER"].strip()
    family=df_taxo.loc[df_taxo["NOM_ACTUEL_A_UTILISER"]==species].iloc[0]["family"]    
    go_plot(bbox_conv, raster_data, raster_data_extent, family, species,list_points,xticks, jticks, xlabels, jlabels)