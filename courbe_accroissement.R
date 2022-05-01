library("vegan")
library("plyr")
library("BiodiversityR")

#p_file<-"C:\\WORK_2021\\MEISE\\2021_oct\\accroissement\\rarefaction_contrl_no_genus.txt"
p_file<-"C:\\DEV\\salvator\\april\\17\\accroissement\\rarefaction_contrl_no_genus.txt"
#p_file<-choose.files()
df<-data.frame(read.csv(file=p_file, sep="\t", header=TRUE))
df<-df[,1:2]

df <- ddply(df, .(df$species_name, df$COLLECTOR), nrow)
colnames(df)<-c("species_name","COLLECTOR", "n")
community<-makecommunitydataset(df, "COLLECTOR","species_name", "n")


comm_agg = colSums(community) # summing species counts by column
S <- specnumber(comm_agg) # observed number of species
raremax = 1 # number of individuals to use in rarefaction

# Plotting rarefied species number
Srare <- rarefy(comm_agg, raremax) # rarefied number of species 
plot(S, Srare, xlab = "Observed No. of Species", ylab = "Rarefied No. of Species")
abline(0, 1)

# Plotting rarefaction curve
rarecurve(matrix(comm_agg, nrow = 1), step = 1, sample = raremax, cex = 0.6)


#alternative CIRAD

#md=specaccum(community, method = "rarefaction")
#plot(md, ci.type="poly",col="darkblue", lwd=2, ci.lty=0, ci.col="lightblue",xlab="Surface prospectée (.10-1 ha)", ylab="Nombre d'espèces")

