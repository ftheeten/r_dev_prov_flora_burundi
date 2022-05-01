import pandas as pnd
import numpy as np
import sys
import traceback
import geopandas
from shapely.geometry import Point
from os.path import exists



fichier_taxo="C:\\DEV\\GIS\\rwanda\\rwa_taxo_checklist_utf8.txt"
fichier_syno="C:\\DEV\\salvator\\mar\\20\\export_list_syno_fusionne.txt"
fichier_verna="C:\\DEV\\salvator\\mar\\20\\\\ArticleB_Liste des noms vernaculaires.txt" 
fichier_dist="C:\\DEV\\GIS\\rwanda\\excel_dist_provinces_utf8.txt"

fichier_provinces="C:\\DEV\\GIS\\rwanda\\rwa_provinces_osm.gpkg"
prov_shp=geopandas.read_file(fichier_provinces)
prov_shp.set_crs(epsg=4326, inplace=True)


output_file="C:\\Users\\ftheeten\\OneDrive - Africamuseum\\Documents\\salvator\\SALVATOR\\latex\\output_rwa_pdf.tex" 

image_folder="C:\\DEV\\GIS\\rwanda\\maps\\"

output_data={}
array_references={}
dict_geo={}
no_distribution=[]

#print(fichier_taxo)
df_taxo=pnd.read_csv(fichier_taxo, sep='\t', encoding='UTF-8')
df_syno=pnd.read_csv(fichier_syno, sep='\t', encoding='ISO-8859–1')
df_verna=pnd.read_csv(fichier_verna, sep='\t', encoding='UTF-8')
df_dist=pnd.read_csv(fichier_dist, sep='\t', encoding='UTF-8')

df_taxo["Reference1"]=df_taxo["Reference1"].fillna("")
df_taxo["Reference2"]=df_taxo["Reference2"].fillna("")
df_taxo["Reference3"]=df_taxo["Reference3"].fillna("")
df_taxo["Reference4"]=df_taxo["Reference4"].fillna("")
df_taxo["Reference5"]=df_taxo["Reference5"].fillna("")

df_taxo["Reference1"]=df_taxo["Reference1"].str.replace(").",")", regex=False)
df_taxo["Reference2"]=df_taxo["Reference2"].str.replace(").",")", regex=False)
df_taxo["Reference3"]=df_taxo["Reference3"].str.replace(").",")", regex=False)
df_taxo["Reference4"]=df_taxo["Reference4"].str.replace(").",")", regex=False)
df_taxo["Reference5"]=df_taxo["Reference5"].str.replace(").",")", regex=False)

df_taxo['NOM_ACTUEL_A_UTILISER'] = df_taxo['NOM_ACTUEL_A_UTILISER'].str.strip()
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].replace(np.nan,"")
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].fillna('')
df_dist['NOM_JOINTURE'] = df_dist['NOM_JOINTURE'].str.strip()

df_taxo = df_taxo.fillna('')
df_syno = df_syno.fillna('')
df_verna = df_verna.fillna('')
df_dist = df_dist.fillna('')

def replace_latex(text):
    text=text.replace('#','')
    #text=text.replace('&','\&')
    text=text.replace('_',' ')
    return text
    
def split_and_format_latex(text, pos, style,term, delim=" "):
    tmp_arr=str(text).split(delim)
    nominal=tmp_arr[0:pos]
    auth=tmp_arr[pos:]
    return style+" ".join(nominal)+term+" "+" ".join(auth)
    
def writeline(text, file, condition=True):
    if condition:
        file.write(text)
        file.write("\n")
    
def parse_row(row):
    global df_syno
    global df_verna
    global array_references
    returned={}
    genus=row["genus"]
    rank=row["rank"]
    ##print(genus)
    #genus=genus.replace("&", "\&")    
    returned["genus"]=genus
    returned["rank"]=rank
    current_name=row["NOM_ACTUEL_A_UTILISER"]
    ##print("CURRENT : "+current_name)
    name_idx=current_name
    current_name=current_name.replace("&", "\&")    
    returned["current_name"]=current_name
    returned["joint_name"]=" ".join(current_name.split(" ")[:2])
    
    ##print("REF for "+name_idx)
    references=array_references[name_idx]["ref"]
    ##print(references)
    references_txt=""
    if(len(references)>0):
        references_txt='~; '.join(references)
    returned["references"]=references_txt.replace("&", "\&")
    df_syno_2=df_syno.loc[df_syno['nom_actuel_a_utiliser'] == current_name]
    returned["synonyms"]=[]
    for index2, row2 in df_syno_2.iterrows():
        syno=str(row2["synonym"])
        if len(syno)>0:
            ##print(current_name+ " SYNO " + str(syno))
            returned["synonyms"].append(str(syno).replace("&", "\&")  )
    tmp_arr=str(current_name).split(" ")
    name_no_auth=' '.join(tmp_arr[0:2]).strip()
    df_verna_filter=df_verna.loc[df_verna['Scientific names without author'] == name_no_auth]
    returned["vernacular_names"]=[]
    
    for index3, row3 in df_verna_filter.iterrows():
        verna=row3["Vernacular name1"]
        ##print("VERNA")
        ##print(verna)
        returned["vernacular_names"].append(str(verna).replace("&", "\&")  )
    return returned


def detect_distribution(row):
    distribution_acceptee=None
    if 'current_name' in  row and 'joint_name' in  row:
        current_name=row["current_name"]
        joint_name=row["joint_name"]
        distribution_acceptee=df_dist.loc[df_dist["CTRL_JOINT"].str.lower().replace("\\&","&")==joint_name.lower().replace("\\&","&")]
        distribution_acceptee2=df_dist.loc[(df_dist["JOINTURE"].str.lower().replace("\\&","&")==joint_name.lower().replace("\\&","&")) & (df_dist["JOINTURE"].str.lower() !=  df_dist["NOM_JOINTURE"].str.lower()) ]
        if distribution_acceptee is None:
            distribution_acceptee=distribution_acceptee2
        else:
            distribution_acceptee=pnd.DataFrame(np.concatenate([distribution_acceptee.values, distribution_acceptee2.values]), columns=distribution_acceptee.columns)
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
                distribution_acceptee_syno=pnd.DataFrame(np.concatenate([distribution_acceptee_syno.values, distribution_acceptee_syno2.values]), columns=distribution_acceptee_syno.columns)
            if not distribution_acceptee is None:
               distribution_acceptee=pnd.DataFrame(np.concatenate([distribution_acceptee.values, distribution_acceptee_syno.values]), columns=distribution_acceptee.columns)
            else:
                distribution_acceptee=distribution_acceptee_syno
    return distribution_acceptee
    
def print_distribution(row, distribution_acceptee, file1):
    geo_dict={}    
    go=False
    if not distribution_acceptee is None:
        ##print("PARSE_COORD")
        for index, row_dist in distribution_acceptee.iterrows():
            province=row_dist["province"]
            if len(province)>0:
                if province not in geo_dict:
                    geo_dict[province]={}
                collector=row_dist["COLLECTOR"].replace("&", "\&").replace("_", " ")
                if collector is not None:
                    if len(collector)>0:
                        if collector not in geo_dict[province]:
                            geo_dict[province][collector]=[]
                        coll_num=row_dist["COLL_NUM"].replace("&", "\&").replace("_", " ")
                        if coll_num is not None:
                            tmp_arr=geo_dict[province][collector]
                            tmp_arr.append(coll_num)
                            tmp_arr.sort()
                            geo_dict[province][collector] =tmp_arr 
    list_sp=[]
    
    for region, a_region in sorted(geo_dict.items()):
        list_coll=[]    
        for collector, a_collectors in sorted(a_region.items()):
            if len(a_collectors)>0:
                go =True
            #for nums in  a_collectors:
            #    go =True 
            list_nums=", ".join(sorted(list(set(a_collectors))))
            str_coll=""+ collector+ " "+list_nums +""
            list_coll.append(str_coll)
        str_prov="Provinces: \\emph{"+region + "}" + " - "+"; ".join(list_coll)
        list_sp.append(str_prov)
    str_p="\\small{Specimens: "+". ".join(list_sp)+"}."
    if go:
        #writeline("\\linebreak", file1)
        writeline(str_p, file1)
        writeline("\\linebreak", file1)
        writeline("\\newline", file1)                
    
def write_tex(row, file1):
    global no_distribution
    distribution_acceptee=None
    print(row)
    if 'current_name' in  row:        
        if row["rank"]=="Species_or_higher":
            #if "genus" in row:
                #if row["genus"]=='Tetracera':
                #    print("Tetracera found")
                #    print(row)
            tmp_name=split_and_format_latex(row["current_name"], 2,"\\emph{{\\textbf{", "}}}" )
            
        elif row["rank"]=="subspecies":
            tmp_name=split_and_format_latex(row["current_name"], 2,"\\emph{{\\textbf{", "}}}" )
            split_name= tmp_name.split(" ")
            tmp_name_arr=[]
            subsp_found=False
            for tmp in split_name:
                if subsp_found:
                   tmp="\\emph{\\textbf{"+tmp+"}}"
                   subsp_found=False
                if tmp=="subsp.":
                    subsp_found=True
                tmp_name_arr.append(tmp)
            tmp_name=" ".join(tmp_name_arr)
        elif row["rank"]=="Variety":      
            tmp_name=split_and_format_latex(row["current_name"], 2,"\\emph{{\\textbf{", "}}}" )
            split_name= tmp_name.split(" ")
            tmp_name_arr=[]
            subsp_found=False
            for tmp in split_name:
                if subsp_found:
                   tmp="\\emph{\\textbf{"+tmp+"}}"
                   subsp_found=False
                if tmp=="var.":
                    subsp_found=True
                tmp_name_arr.append(tmp)
            tmp_name=" ".join(tmp_name_arr)
        else:
            tmp_name=row["current_name"]
        distribution_acceptee=detect_distribution(row)
        writeline_cond=False
        if distribution_acceptee is not None:
            if len(distribution_acceptee)>0:
                writeline_cond=True
        if not writeline_cond:
            no_distribution.append(row["current_name"])
        writeline("\\normalsize\\raggedright\\textbullet\\hspace{5mm}{"+replace_latex(tmp_name)+"}", file1, writeline_cond)
        writeline("\\linebreak", file1, writeline_cond)
        #if "remark" in row:
        #    writeline("\\normalsize{"+replace_latex(row["remark"])+".}", file1)
        #    writeline("\\linebreak", file1)
        if "synonyms" in row:
            if len(row["synonyms"])>0:
                writeline("\\small{Syn.: "+ replace_latex('~; '.join([split_and_format_latex(x, 2,"\\emph{", "}" ) for x in row["synonyms"]]))+".}", file1, writeline_cond)
                writeline("\\linebreak", file1, writeline_cond)
        if "references" in row:
            if len(row["references"])>0:
                writeline("\\small{Lit.: "+replace_latex(row["references"])+".}", file1, writeline_cond)
                writeline("\\linebreak", file1, writeline_cond)
        if "vernacular_names" in row:
            if len(row["vernacular_names"])>0:
                writeline("\\small{Nom\(s\) vern.: "+ replace_latex('~; '.join(row["vernacular_names"]))+".}", file1, writeline_cond)
                writeline("\\linebreak", file1, writeline_cond)
        if "subspecies" in row:
            ##print("HAS_SUBSP")
            for subsp_row in row["subspecies"]:
                write_tex(row["subspecies"][subsp_row], file1)
        if "variety" in row:
            for var_row in row["variety"]:
                write_tex(row["variety"][var_row], file1)
        print_distribution(row, distribution_acceptee, file1)
        #print(row)
        test_file=image_folder+row["joint_name"].replace(" ","_")+".png"
        file_exists = exists(test_file)
        if file_exists:
            writeline("\\includegraphics[scale=0.5]{"+test_file.replace("\\","/")+"}", file1, True)
            writeline("\\linebreak", file1, True)
        print(test_file)


def check_duplicates_and_ref():
    global df_syno
    global df_taxo
    global df_verna
    global array_references
    check_duplicate={}
    df_syno['nom_actuel_a_utiliser'] = df_syno['nom_actuel_a_utiliser'].str.replace(chr(194),chr(20))
    df_syno['synonym'] = df_syno['synonym'].str.replace(chr(194)," ")
    df_syno['synonym'] = df_syno['synonym'].str.replace('\xc2'," ")
    try:       
        def_check=df_taxo.sort_values(['clade', 'family',"NOM_ACTUEL_A_UTILISER" ], ascending=[True, True, True])
        for index, row in def_check.iterrows():    
            #name_status=row["name_status"].replace("&", "\&")
            species=str(row["NOM_ACTUEL_A_UTILISER"])#.replace("&", "\&").replace("_", " ")
            if(len(species)>0):
                standard=str(row["NOM_STANDARD"])#.replace("&", "\&").replace("_", " ")
                if species in check_duplicate:
                    check_duplicate[species]["count"]=check_duplicate[species]["count"]+1
                    standard=str(row["NOM_STANDARD"])
                else:
                    check_duplicate[species]={}
                    check_duplicate[species]["count"]=1
                    #raise Exception('Duplicate problem on '+species)
                if standard != species:
                    check_duplicate[species]["syno"]=standard
                else:
                    check_duplicate[species]["syno"]=""
                    ##print(rank)
                references=[]
                if(len(str(row["Reference1"]).strip())>0):
                    references.append(str(row["Reference1"]).strip())
                if(len(str(row["Reference2"]).strip())>0):
                    references.append(str(row["Reference2"]).strip())
                if(len(str(row["Reference3"]).strip())>0):
                    references.append(str(row["Reference3"]).strip())
                if(len(str(row["Reference4"]).strip())>0):
                    references.append(str(row["Reference4"]).strip())
                if(len(str(row["Reference5"]).strip())>0):
                    references.append(str(row["Reference5"]).strip())                   
                if species in array_references:
                    tmp_ref=array_references[species]["ref"]
                    for ref in references:
                        if not ref in tmp_ref:
                            tmp_ref.append(ref)
                    array_references[species]["ref"]=tmp_ref
                else:                    
                    array_references[species]={}
                    array_references[species]["ref"]=references
                    
                    
        syno=dict(filter(lambda elem: elem[1]["syno"]!="", check_duplicate.items()))
        for key, val in syno.items():
            #print(key+"\t"+str(val["syno"]))
            df_syno_2=df_syno.loc[df_syno['synonym'] == val["syno"]]
            #if len(df_syno_2)>0:
                #print("found")
            if len(df_syno_2)==0:
                #print("NOT_FOUND")
                df_syno=df_syno.append({'rang': 'undefined', 'nom_actuel_a_utiliser':key,'synonym':val["syno"] }, ignore_index=True)
        dups= dict(filter(lambda elem: elem[1]["count"]>1, check_duplicate.items()))
        #for key, val in dups.items():
            #print(key+"\t"+str(val["count"]))               
    except Exception as e:
        #TODO more efficent exception capture
        print("Issue")
        traceback.print_tb(*sys.exc_info())
  
def entry_point():
    global df_syno
    global df_taxo
    global df_verna
    global df_dist
    check_duplicate={}
    try:
        df_taxo['NOM_ACTUEL_A_UTILISER'] = df_taxo['NOM_ACTUEL_A_UTILISER'].str.strip()
        df_taxo['species_name'] = df_taxo['species_name'].str.strip()

        df_syno['nom_actuel_a_utiliser'] = df_syno['nom_actuel_a_utiliser'].str.replace(chr(194),chr(20))
        df_syno['synonym'] = df_syno['synonym'].str.replace(chr(194)," ")
        df_syno['synonym'] = df_syno['synonym'].str.replace('\xc2'," ")
        #print(len(df_syno))
        df_syno=df_syno.drop_duplicates()
        #print(len(df_syno))


        
        df_taxo["genus"] = df_taxo["genus"].replace(np.nan,"")
        df_taxo["genus"] = df_taxo["genus"].fillna('')
        #print(df_taxo)

        def_species=df_taxo[df_taxo['rank']=="Species_or_higher"]
        def_species=def_species.sort_values(['clade', 'family',"NOM_ACTUEL_A_UTILISER" ], ascending=[True, True, True])

        print("GEO")      
        print("SPECIES")
        df_taxo["CTRL_JOINT"]=""
        df_dist["CTRL_JOINT"]=""
        for x in df_taxo["NOM_ACTUEL_A_UTILISER"].unique():
            #print(x)
            if(len(x)>0):
                tmp=x.split(' ')
                if len(tmp)>1:
                    new_name=' '.join(tmp[:2])
                    #print("=>"+new_name)
                    df_taxo.loc[df_taxo["NOM_ACTUEL_A_UTILISER"]==x, "CTRL_JOINT"]=new_name
        for x in df_dist["NOM_JOINTURE"].unique():
            #print(x)
            if(len(x)>0):
                tmp=x.split(' ')
                if len(tmp)>1:
                    new_name=' '.join(tmp[:2])
                    #print("=>"+new_name)
                    df_dist.loc[df_dist["NOM_JOINTURE"]==x, "CTRL_JOINT"]=new_name
        for index, row in def_species.iterrows():    
            species=str(row["NOM_ACTUEL_A_UTILISER"])#.replace("&", "\&").replace("_", " ")
            #if species=="Tetracera masuiana De Wild. & T.Durand":
            #    print(species)
            if(len(species)>0):
                #print(species)
                rank=row["rank"]#.replace("&", "\&")
                clade=row["clade"]#.replace("&", "\&")
                family=row["family"]#.replace("&", "\&")
                #synonym=row["SYNONYM"].replace("&", "\&").replace("_", " ")
                if not clade in output_data:
                    output_data[clade]={}
                if not family in output_data[clade]:
                    output_data[clade][family]={}
                tmp=parse_row(row)
                if not species in output_data[clade][family]:
                    output_data[clade][family][species]={}
                tmp["sort"]=clade+"_"+family+"_"+ species 
                output_data[clade][family][species]=tmp
                            
        def_subspecies=df_taxo[df_taxo['rank']=="subspecies"]
        def_subspecies=def_subspecies.sort_values(['clade', 'family',"NOM_ACTUEL_A_UTILISER" ], ascending=[True, True, True])
        def_subspecies=def_subspecies.drop_duplicates()
        #print("___SUBSP__________\r\n")
        for index, row in def_subspecies.iterrows():    
            subsp=str(row["NOM_ACTUEL_A_UTILISER"])#.replace("&", "\&").replace("_", " ")
            if(len(subsp)>0):
                rank=row["rank"]#.replace("&", "\&")
                clade=row["clade"]#.replace("&", "\&")
                family=row["family"]#.replace("&", "\&")
                species_name=row["species_name"].replace("&", "\&")
                joint_name=row["CTRL_JOINT"]
                if not family in output_data[clade]:
                    output_data[clade][family]={"remark":"NO_DIRECT_PARENT"}
                if not species_name in output_data[clade][family]:
                    output_data[clade][family][species_name]={"remark":"Only present as subspecies or variety", "current_name":species_name, "rank":"Species_or_higher", "joint_name":joint_name
                    }
                else:    
                    tmp_array=output_data[clade][family][species_name]
                tmp=parse_row(row)
                if not "subspecies" in output_data[clade][family][species_name]:
                    output_data[clade][family][species_name]["subspecies"]={}
                output_data[clade][family][species_name]["subspecies"][subsp]=tmp    

        def_variety=df_taxo[df_taxo['rank']=="Variety"]
        def_variety=def_variety.sort_values(['clade', 'family',"NOM_ACTUEL_A_UTILISER" ], ascending=[True, True, True])
        #print("___VARIETY__________\r\n")
        for index, row in def_variety.iterrows():    
            #name_status=row["name_status"].replace("&", "\&")
            variety=str(row["NOM_ACTUEL_A_UTILISER"]).replace("&", "\&").replace("_", " ")
            if(len(variety)>0):
                ##print(variety)
                rank=row["rank"]#.replace("&", "\&")
                clade=row["clade"]#.replace("&", "\&")
                family=row["family"]#.replace("&", "\&")
                species_name=row["species_name"].replace("&", "\&")
                joint_name=row['CTRL_JOINT']
                if not family in output_data[clade]:
                    output_data[clade][family]={"remark":"NO_DIRECT_PARENT"}
                if not species_name in output_data[clade][family]:
                    output_data[clade][family][species_name]={"remark":"Only identified as subspecies or variety", "current_name":species_name, "rank":"Species_or_higher", "joint_name":joint_name}
                else:   
                    tmp_array=output_data[clade][family][species_name]
                tmp=parse_row(row)
                if not "variety" in output_data[clade][family][species_name]:
                    output_data[clade][family][species_name]["variety"]={}
                output_data[clade][family][species_name]["variety"][variety]=tmp         

        file1 = open(output_file,"w", encoding='utf-8') 
        writeline("\\documentclass[12pt]{book}", file1)
        #writeline("\\usepackage{tabto}", file1)
        writeline("\\usepackage[utf8x]{inputenc}", file1)
        writeline("\\usepackage{xcolor}", file1)
        writeline("\\usepackage{graphicx}", file1)
        writeline("\DeclareUnicodeCharacter{146}{’}", file1)
        writeline("\\begin{document}", file1)
        writeline("\\let\cleardoublepage\\clearpage", file1)
        #print(output_data)
        for clade, nested in output_data.items():           
            writeline("\\newpage", file1)
            #writeline("\\begin{huge}", file1)    
            writeline("\\noindent{\\textbf{\\Huge{"+clade+"}}}", file1)
            writeline("\\newline", file1)
            writeline("\\newline", file1)
            #writeline("\\end{huge}", file1)
            for current_family, nested2 in nested.items():
                #if current_family=="Dilleniaceae":
                #    print(current_family)
                writeline("\\colorbox[RGB]{204,255,102}{\\rlap{\\huge{"+current_family.strip().replace("&","\&")+"}}\\hspace{\\linewidth}\\hspace{-2\\fboxsep}}", file1)
                writeline("\\begin{flushleft}", file1)
                #print(nested2)
                for species, nested3 in nested2.items():
                    #if current_family=="Dilleniaceae":
                    #    print(species)
                    #    print(nested3)
                    write_tex(nested3, file1)
                writeline("\\end{flushleft}", file1)
        writeline("\\end{document}", file1)
        file1.close()
        #print("NO_DISTRIBUTION")
        #no_distribution.sort()
        #for line in no_distribution:
        #    print(line)
    except Exception as e:
        #TODO more efficent exception capture
        #print("Issue")
        traceback.print_tb(*sys.exc_info())
    
#main
check_duplicates_and_ref()
entry_point()