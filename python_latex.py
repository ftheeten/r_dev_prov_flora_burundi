print("test")
import pandas as pnd
import re

def writeline(text, file):
    file.write(text)
    file.write("\n")
 
input_file="C:\\WORK_2021\\MEISE\\2021_aout\\22\\output_single_file_corr.txt" 
output_file="C:\\PROJECTS_R\\SALVATOR\\latex\\main.tex" 

output_data={}


df_taxo=pnd.read_csv(input_file, sep='\t', encoding='utf-8')
df_taxo = df_taxo.where(pnd.notnull(df_taxo), "UNKNOWN")
df_syno=df_taxo.copy()
df_taxo.loc[:, 'sort':'AUTEURS_REF']
print(df_taxo.head())
df_taxo=df_taxo.sort_values(by=['clade', 'family','NOM_ACTUEL_A_UTILISER', 'sort'], ascending=True)

current_clade=""
current_family=""
current_species=""
file1 = open(output_file,"w", encoding='utf-8') 
writeline("\\documentclass[12pt]{article}", file1)
writeline("\\usepackage{tabto}", file1)
writeline("\\begin{document}", file1)
writeline("\\spaceskip 0.5 em \\relax \\noindent", file1)
subspecies_index=False
variety_index=False
synonym_index=False
verna_index=False
for index, row in df_taxo.iterrows():
    rank=row["rank"].replace("&", "\&")
    clade=row["clade"].replace("&", "\&")
    family=row["family"].replace("&", "\&")
    name_status=row["name_status"].replace("&", "\&")
    species=row["NOM_ACTUEL_A_UTILISER"].replace("&", "\&").replace("_", "\_")
    synonym=row["SYNONYM"].replace("&", "\&").replace("_", "\_")
    if clade != current_clade:
        current_clade=clade.strip()
        print(current_clade)
        writeline("\\newpage", file1)
        writeline("\\begin{huge}", file1)        
        writeline("\\textbf{"+row["clade"]+"}", file1)
        writeline("\\end{huge}", file1)
        writeline("\\linebreak", file1)
    if current_family != family:
        current_family=family.strip()
        print(current_family)
        writeline("\\begin{large}", file1)
        writeline("\\begin{center}", file1)
        writeline("\\textbf{"+current_family+"}", file1)
        writeline("\\end{center}", file1)
        writeline("\\end{large}", file1)
    if current_species != species and rank=="Species_or_higher" :
        current_species=species.strip()
        #print(current_species)
        writeline(current_species, file1)
        writeline("\\linebreak", file1)
        subspecies_index=False
        variety_index=False
        synonym_index=False
        verna_index=False
    if(rank=="subspecies"):
        #print("subspecies")
        #print(current_species)
        if(not subspecies_index):
            writeline("\\textbf{liste subspecies}", file1)
            writeline("\\linebreak", file1)
        writeline("\\null\\tab "+species, file1)
        writeline("\\linebreak", file1)
        subspecies_index=True
        synonym_index=False
        verna_index=False
    if(rank=="Variety"):
        #print("subspecies")
        #print(current_species)
        if(not variety_index):
            writeline("\\textbf{liste varieties}", file1)
            writeline("\\linebreak", file1)
        writeline("\\null\\tab "+species, file1)
        writeline("\\linebreak", file1)
        variety_index=True
        synonym_index=False
        verna_index=False
    tmp_syno=df_syno[(df_syno['NOM_ACTUEL_A_UTILISER'] == species) & (df_syno['name_status']=="synonym") ]
    for indexsyno, rowsyno in tmp_syno.iterrows():
        if(not synonym_index):
            writeline("\\textbf{liste synonyms}", file1)
            writeline("\\linebreak", file1)
        writeline("\\null\\tab "+rowsyno["SYNONYM"].replace("&", "\&").replace("_", "\_"), file1)
        writeline("\\linebreak", file1)
        synonym_index=True
    tmp_verna=df_syno[(df_syno['NOM_ACTUEL_A_UTILISER'] == species) & (df_syno['name_status']=="vernacular") ]        
    for indexverna, rowverna in tmp_verna.iterrows():
        if(not verna_index):
            writeline("\\textbf{liste vernacular}", file1)
            writeline("\\linebreak", file1)
        verna_tmp=rowverna["VERNACULAR"].replace("&", "\&").replace("_", "\_")
        verna_tmp=re.sub(r"[\n\t\s]*", "", verna_tmp)
        writeline("\\null\\tab "+ verna_tmp, file1)
        writeline("\\linebreak", file1)
        verna_index=True    
       
writeline("\\end{document}", file1)
file1.close()