library("rgdal")
library("leaflet")
library("leafem")
library("sp")
library("tractor.base")
library("dplyr")


simpleCap <- function(x) {
  s <- strsplit(x, " ")[[1]]
  paste(toupper(substring(s, 1,1)), tolower(substring(s, 2)),
        sep="", collapse=" ")
}

df_aggregate<-function(dt1, item, split_field, aggregate_field, lower_cap=FALSE)
{
  filtered<-dt1[dt1[split_field] == item,aggregate_field]
  filtered<-as.character(filtered)
  if(lower_cap)
  {
    filtered<-sapply(filtered, simpleCap)
  }
  list_unq<-sort(unique(filtered))
  list_unq
}

implode_aggregate<-function(dt1, item, split_field, aggregate_field, lower_cap=FALSE)
{
  list_unq<-df_aggregate(dt1, item, split_field, aggregate_field, lower_cap=FALSE)
  str_unq<-implode(list_unq, ", ")
  str_unq
}

find_aggregate<-function(frmshp1, split_field, aggregate_field,  lower_cap=FALSE)
{
  main_categ<-unique( frmshp1[[split_field]] )
  print(main_categ)
  key<- vector()
  imploded<- vector()
  df_returned<-data.frame(key, imploded)
  names(df_returned)<-c("key","items")
  sapply(main_categ, 
         function(item)
         {
          
           dt1<-frmshp1@data
           str_unq<-implode_aggregate(dt1, item, split_field, aggregate_field, lower_cap)
           print(c(item, str_unq))
           df_tmp<-data.frame(item, str_unq)
           names(df_tmp)<-c("key","items")
           df_returned <<- rbind(df_returned, df_tmp)

         }
    )
   
  df_returned
}

find_range<-function(frmshp1, split_field, aggregate_field)
{
  main_categ<-unique( frmshp1[[split_field]] )
  print(main_categ)
  key<- vector()
  min<- vector()
  max<- vector()
  df_returned<-data.frame(key, min, max)
  names(df_returned)<-c("key","min", "max")
  sapply(main_categ, 
         function(item)
         {
           
           dt1<-frmshp1@data
           filtered<-dt1[dt1[split_field] == item,aggregate_field]
           v_min<-min(as.numeric(as.character(filtered)),na.rm=TRUE)
           v_max<-max(as.numeric(as.character(filtered)),na.rm=TRUE)
           df_tmp<-data.frame(item, v_min, v_max)
           names(df_tmp)<-c("key","min", "max")
           df_returned <<- rbind(df_returned, df_tmp)
           
         }
  )
  
  df_returned
}

points_within_and_merge<-function(frmshp1, frmshp2, split_field, merge_field, name_target_fied)
{
  split_layer<-split(frmshp1, frmshp1[[split_field]])
  frmshp2[[name_target_fied]]<-""
  sapply(split_layer, 
         function(split_geom)
         {
            merge_feature<-split_geom[[merge_field]]
            #print(merge_feature)
            coords_poly<-split_geom@polygons[[1]]@Polygons[[1]]@coords
            in_points<-point.in.polygon(coordinates(frmshp2)[,1], coordinates(frmshp2)[,2], coords_poly[,1], coords_poly[,2], mode.checked=FALSE)
            select_prov=which(in_points!=0)
            frmshp2@data[select_prov,name_target_fied]<<-as.character(merge_feature)
         }
    )
  frmshp2
}

shp<-"C:\\WORK_2021\\MEISE\\2021_aout\\29\\distri_shp\\zone_eco_bdi20210829.shp"
shp2<-"C:\\WORK_2021\\MEISE\\2021_aout\\29\\distri_shp\\checklist_20210829.shp"
shp3<-"C:\\WORK_2021\\MEISE\\2021_aout\\29\\distri_shp\\checklist_20210829_prov.shp"
burundi <- readOGR(shp , GDAL1_integer64_policy = TRUE)

split_prv=split(burundi, burundi$layer)

#View(burundi$data)
flore <- readOGR(shp2)
flore<-points_within_and_merge(burundi, flore, "layer", "layer", "province_geom")
#df_families<-data.frame(find_aggregate(flore, "province_geom", "FAMILY", TRUE))
#df_collectors<-find_aggregate(flore, "province_geom", "COLLECTOR", TRUE)
View(df_families)
#print("save")
#df_year_range<-find_range(flore, "province_geom", "Coll_Year")
writeOGR(flore,shp3, layer="flora burundi with provinces", driver="ESRI Shapefile" )


