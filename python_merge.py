print("test")
import pandas as pnd


fichier_taxo="C:\\WORK_2021\\MEISE\\2021_aout\\22\\nom_simple_geneve_rank_nomref.txt"
#C:\\WORK_2021\\MEISE\\2021_sept\\data_3\\B_burundi check nom-simple_Geneve_wrk2_juillet_2021.txt
fichier_syno="C:\\WORK_2021\\MEISE\\2021_aout\\22\\export_list_syno_fusionne.txt"
fichier_verna="C:\\WORK_2021\\MEISE\\2021_aout\\22\\B_Liste des noms vernaculaires.txt" 
output_files="C:\\WORK_2021\\MEISE\\2021_aout\\22\\output_single_file.txt" 

output_data={}


df_taxo=pnd.read_csv(fichier_taxo, sep='\t', encoding='ISO-8859–1')
df_syno=pnd.read_csv(fichier_syno, sep='\t', encoding='ISO-8859–1')
df_verna=pnd.read_csv(fichier_verna, sep='\t', encoding='ISO-8859–1')

df_taxo['NOM_ACTUEL_A_UTILISER'] = df_taxo['NOM_ACTUEL_A_UTILISER'].str.strip()
df_taxo['species_name'] = df_taxo['species_name'].str.strip()

df_syno['nom_actuel_a_utiliser'] = df_syno['nom_actuel_a_utiliser'].str.replace(chr(194),chr(20))
df_syno['synonym'] = df_syno['synonym'].str.replace(chr(194)," ")
df_syno['synonym'] = df_syno['synonym'].str.replace('\xc2'," ")
print(len(df_syno))
df_syno=df_syno.drop_duplicates()
print(len(df_syno))
header_line="sort"+ "\t" +  "species_name" + "\t" +  "rank"+ "\t"+ "name_status" +"\t"+ "NOM_ACTUEL_A_UTILISER" + "\t" +"SYNONYM"+ "\t" +"VERNACULAR" + "\t" + "clade"+  "\t" +  "family"+ "\t"  +  "AUTEURS" + "\t"+  "AUTEURS_REF" + "\t"
output_data[header_line]=header_line

#sort
df_taxo.insert(1, "sort", 1)
for index, row in df_taxo.iterrows():
    rank=row["rank"]
    if(rank=="Variety"):
        df_taxo.at[index,'sort']=30
    elif(rank=="subspecies"):
        df_taxo.at[index,'sort']=20
    else:
        df_taxo.at[index,'sort']=10

df_taxo = df_taxo.sort_values(["species_name", "sort"], ascending = (True, True))  


author_ref=""
for index, row in df_taxo.iterrows():
    #print(row["species_name"])
    cn=row["NOM_ACTUEL_A_UTILISER"]
    #print(cn)
    df_filter=df_syno.loc[df_syno['nom_actuel_a_utiliser'] == cn]
    if(str(row["AUTEURS"])=="nan"):
        row["AUTEURS"]=""
    if(row["sort"]==10):
        author_ref=row["AUTEURS"]
    #if(str(row["AUTEURS"])=="nan"):
    #    #print("TRY FIX VAR AUTH")
    #    if(row["rank"]=="Variety"):
    #        if(str(row["var. author"])!="nan"):
    #            #print("FIX VAR AUTH")
    #            row["AUTEURS"]=row["var. author"]           
    row_to_add=str(row["sort"]) + "\t"+  str(row["species_name"]) +"\t" + str(row["rank"]) + "\t" + "current_name"+"\t"+ str(cn) + "\t" +"" + "\t" +""+"\t" + str(row["clade"]) + "\t"+ str(row["family"]) +"\t" + str(row["AUTEURS"]) +"\t" + author_ref
    row_to_add=row_to_add.replace(chr(194)," ")
    row_to_add=row_to_add.replace('\xc2'," ")
    output_data[row_to_add]=row_to_add
    tmp_arr=cn.split(" ")
    name_no_auth=' '.join(tmp_arr[0:2]).strip()
    #print(name_no_auth)
    for index2, row2 in df_filter.iterrows():
        syno=row2["synonym"]
        row_to_add="\t\t\t"+"synonym"+"\t"+ str(cn) + "\t" +str(syno)
        row_to_add=row_to_add.replace(chr(194)," ")
        row_to_add=row_to_add.replace(chr(160)," ")
        row_to_add=row_to_add.replace('\xc2'," ")
        output_data[row_to_add]=row_to_add
    df_verna_filter=df_verna.loc[df_verna['Scientific names without author'] == name_no_auth]
    for index2, row3 in df_verna_filter.iterrows():
        verna=row3["Vernacular name1"]
        #print(verna)
        row_to_add="\t\t\t"+ "vernacular"+"\t"+ str(cn) + "\t" +""+"\t"+ verna
        row_to_add=row_to_add.replace(chr(194)," ")
        row_to_add=row_to_add.replace(chr(160)," ")
        row_to_add=row_to_add.replace('\xc2'," ")
        output_data[row_to_add]=row_to_add
        
file1 = open(output_files,"w", encoding='ISO-8859–1')      
for key, new_line in output_data.items():
    #print(new_line)
    file1.write(new_line)
    file1.write("\n")

file1.close()
    