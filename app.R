library(shiny)
library(leaflet)
library("leafem")
library(rgdal)

main_map<- NULL

init_map<-function()
{
    shp<-"C:\\WORK_2021\\MEISE\\SALVATOR\\BDI_adm\\BDI_adm1.shp"
    shp2<-"C:\\WORK_2021\\MEISE\\SALVATOR\\flore_pas_de_pt_inter\\flore_burundi_sans_point_inter.shp"
    burundi <- readOGR(shp , GDAL1_integer64_policy = TRUE)
    flore <- readOGR(shp2)
    main_map<<-leaflet(data=flore) %>% addProviderTiles(providers$OpenStreetMap) %>%
        addPolygons(data=burundi,weight=5,col = 'red') %>%
        addMarkers(~Longitude, ~Latitude, popup = ~as.character(Species), label = ~as.character(Species)) %>% 
        addScaleBar( position="bottomleft", options = scaleBarOptions()) %>%
        addMouseCoordinates()
}

r_colors <- rgb(t(col2rgb(colors()) / 255))
names(r_colors) <- colors()

ui <- fluidPage(
    leafletOutput("mymap"),
    p(),
    actionButton("recalc", "New points")
)

server <- function(input, output, session) {
    
    init_map()
    
    output$mymap <- renderLeaflet({
       main_map
    })
}

shinyApp(ui, server)
