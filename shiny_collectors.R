library(shiny)
library("rgdal")
library("leaflet")
library("leafem")
library("sp")
library("knitr")
library("dplyr")
library("plyr")
library("ggplot2")
main_chart<- NULL
main_frame<-NULL


simpleCap <- function(x) {
  s <- strsplit(x, " ")[[1]]
  paste(toupper(substring(s, 1,1)), tolower(substring(s, 2)),
        sep="", collapse=" ")
}

init_frame<-function()
{
  main_frame<<-shp<-"C:\\WORK_2021\\MEISE\\SALVATOR\\flore_pas_de_pt_inter\\flore_burundi_sans_point_inter_provinces.shp"
  flore <- readOGR(shp , GDAL1_integer64_policy = TRUE, use_iconv = TRUE, encoding = "UTF-8")
  flore@data$FAMILY <- sapply(as.character(flore@data$FAMILY),simpleCap)
  main_frame<<-flore@data
}


init_chart<-function(input_frame, t_province)
{
  print("call")
  simpleCap <- function(x) {
    s <- strsplit(x, " ")[[1]]
    paste(toupper(substring(s, 1,1)), tolower(substring(s, 2)),
          sep="", collapse=" ")
  }

  
  
  filtered<-input_frame[flore@data$prvnc_g==t_province,]
  
  nb_observations<-nrow(filtered)
  nb_species<-length(unique(filtered$Species))
  nb_collectors<-length(unique(filtered$COLLECT))
  
  distspecies<-data.frame(filtered %>%
                            dplyr::group_by(FAMILY) %>%
                            dplyr::summarise(dplyr::n_distinct(Species)))
  distspecies[is.na(distspecies)] <- ""
  
  
  min_year<-filtered %>% dplyr::group_by(FAMILY) %>% dplyr::summarise(Coll_Yr = min(as.numeric(as.character(Coll_Yr)),na.rm=TRUE))
  max_year<-filtered %>% dplyr::group_by(FAMILY) %>% dplyr::summarise(Coll_Yr = max(as.numeric(as.character(Coll_Yr)),na.rm=TRUE))
  
  df_families<-data.frame(plyr::count(filtered, "FAMILY"))
  df_families[is.na(df_families)] <- ""
  df_families<-merge(x=df_families, y=distspecies, by="FAMILY", all=TRUE)
  df_families<-merge(x=df_families, y=min_year, by="FAMILY", all=TRUE)
  df_families<-merge(x=df_families, y=max_year, by="FAMILY", all=TRUE)
  df_families<-cbind(seq.int(nrow(df_families)), df_families)
  colnames(df_families) <- c("id", "family","frequency", "distinct species", "min year", "max year")
  
  tmp1<-data.frame(seq(1900,2025, 1))
  colnames(tmp1)<-c("years")
  df_years<-data.frame(plyr::count(filtered, "Coll_Yr"))
  colnames(df_years)<-c("years", "obs" )
  df_years$years<-as.numeric(as.character(df_years$years))
  df_years<-merge(x=tmp1, y=df_years, by="years", all.x=TRUE)
  df_years[is.na(df_years)] <- 0
  graph<-ggplot(df_years, aes(x=years, y=obs))+
    geom_bar(color="blue",stat="identity") + 
    scale_x_continuous(limits=c(1900, 2025),breaks=seq(1900, 2020, 20)) +
    ggtitle("Collecting year distribution")
  
  df_collect<-data.frame(plyr::count(filtered, "COLLECT"))
  colnames(df_collect)<-c("collector", "obs")
  graph_collect<-ggplot(df_collect, aes(x=collector, y=obs, height=1))+
    geom_bar(color="blue",stat="identity") + coord_flip()+
    ggtitle("Collector distribution")
  print("reload")
  main_chart<<-graph_collect
}

r_colors <- rgb(t(col2rgb(colors()) / 255))
names(r_colors) <- colors()

ui <- fluidPage(
  titlePanel("Province"),
  sidebarLayout(
    sidebarPanel(
      selectInput(inputId = "selectedvariable",
                  label = "Select a variable", 
                  choices = c("Bururi","Ngozi", "Cibitoke", "Ruyigi")),
    ),
    mainPanel(
      plotOutput("myplot")
    )
  )
)

server <- function(input, output, session) {
  init_frame()
  
  output$myplot <- renderPlot({
    print(input$selectedvariable)
    init_chart(main_frame, input$selectedvariable)
    main_chart
  })
}

shinyApp(ui, server)