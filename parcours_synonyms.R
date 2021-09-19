

taxonomy_file<-"C:\\WORK_2021\\MEISE\\2021_july\\B_burundi check nom-simple_Geneve_wrk2_juillet_2021.txt" 
output_file<-"C:\\WORK_2021\\MEISE\\2021_july\\list_synonymes.txt" 

df_taxonomy<-read.csv(taxonomy_file, header=TRUE, sep='\t')
df_taxonomy <- df_taxonomy[!apply(is.na(df_taxonomy) | df_taxonomy == "", 1, all),]

vector_clade<-character()
vector_family<-character()

vector_current_name<-character()
vector_current_author<-character()
vector_spec<-character()
vector_auth<-character()
vector_subsp<-character()
vector_auth_subsp<-character()
vector_var<-character()
vector_auth_var<-character()

cluster_synonym<-function(line,  index)
{
  
  clade<-line["clade"]
  family<-line["family"]
  current_name<-line["species_name"]
  current_author<-line["species_author"]
  
  field_spec<-paste0("spec_name_syn", index)
  field_auth<-paste0("spec_auth_syn", index)
  field_subsp<-paste0("subsp_name_syn", index)
  field_auth_subsp<-paste0("subsp_auth_syn", index)
  field_var<-paste0("var_name_syn", index)
  field_auth_var<-paste0("var_auth_syn", index)

  spec<-line[field_spec]
  auth<-line[field_auth]
  subsp<-line[field_subsp]
  auth_subsp<-line[field_auth_subsp]
  var<-line[field_var]
  auth_var<-line[field_auth_var]
  
  if(is.na(spec))
  {
    spec<-""
  }
  if(is.na(auth))
  {
    auth<-""
  }
  
  if(is.na(subsp))
  {
    subsp<-""
  }
  if(is.na(auth_subsp))
  {
    auth_subsp<-""
  }
  
  if(is.na(var))
  {
    var<-""
  }
  if(is.na(auth_var))
  {
    auth_var<-""
  }
  
  if(nchar(spec)>0 || nchar(subsp)>0 || nchar(var)>0)
  {
    vector_clade<<-c(vector_clade, clade)
    vector_family<<-c(vector_family, family)
    vector_current_name<<-c(vector_current_name, current_name)
    vector_current_author<<-c(vector_current_author, current_author)
    vector_spec<<-c(vector_spec, spec)
    vector_auth<<-c(vector_auth, auth)
    vector_subsp<<-c(vector_subsp, subsp)
    vector_auth_subsp<<-c(vector_auth_subsp,auth_subsp)
    vector_var<<-c(vector_var, var)
    vector_auth_var<<-c(vector_auth_var,auth_var )
  }
}

explorer_synonym<-function(df_taxonomy)
{
  invisible(apply(df_taxonomy, 1, function(line)
  {
    
    #print(sp)
    cluster_synonym(line, "1")
    cluster_synonym(line, "2")
    cluster_synonym(line, "3")
    cluster_synonym(line, "4")
    
  }))  
  
}



explorer_synonym(df_taxonomy)
frame_output<-data.frame(
  vector_clade,
  vector_family,
  vector_current_name, 
  vector_current_author,
  vector_spec,
  vector_auth,
  vector_subsp,
  vector_auth_subsp,
  vector_var,
  vector_auth_var,stringsAsFactors =FALSE) 
colnames(frame_output)<-c(
  "clade",
  "family",
  "current_name", 
  "author_current_name",
  "synonym_sp" , 
  "synonym_sp_author",
  "synonym_subsp" ,
  "synonym_subsp_author",
  "synonym_var" ,
  "synonym_var_author"
    )
frame_output <- sapply(frame_output, as.character)
frame_output[is.na(frame_output)] <- ""
frame_output<-frame_output[!duplicated(frame_output), ]
View(frame_output)
write.table(frame_output,file=output_file, sep="\t", quote=FALSE, row.names =FALSE)

