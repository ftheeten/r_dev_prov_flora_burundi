library("rgdal")
library("leaflet")
library("leafem")
library("sp")

shp<-"C:\\WORK_2021\\MEISE\\SALVATOR\\BDI_adm\\BDI_adm1.shp"
shp2<-"C:\\WORK_2021\\MEISE\\SALVATOR\\flore_pas_de_pt_inter\\flore_burundi_sans_point_inter.shp"
shp3<-"C:\\WORK_2021\\MEISE\\SALVATOR\\flore_pas_de_pt_inter\\flore_burundi_sans_point_inter_provinces.shp"
burundi <- readOGR(shp , GDAL1_integer64_policy = TRUE)

split_prv=split(burundi, burundi$NAME_1)

#View(burundi$data)
flore <- readOGR(shp2)
flore$province_geom<-""
sapply(split_prv, function(prov_geom)
{
  prov_name<-prov_geom$NAME_1
  coords_poly<-prov_geom@polygons[[1]]@Polygons[[1]]@coords
  in_prov<-point.in.polygon(coordinates(flore)[,1], coordinates(flore)[,2], coords_poly[,1], coords_poly[,2], mode.checked=FALSE)
  select_prov=which(in_prov!=0)
  flore@data[select_prov,"province_geom"]<<-as.character(prov_name)
 
})
writeOGR(flore,shp3, layer="flora burundi with provinces", driver="ESRI Shapefile" )
