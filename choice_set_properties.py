import json
import networkx as nx
import pandas as pd
import csv
import ast
import os
from datetime import datetime


#cyclist with error: 1049 divide by zero, 19270 key error when loading JSON

def cyclist_error(idnum):
    error_id[idnum] = 'error'
    print(f"warning: cyclist {idnum} did not create a properties file!")



def get_path_properties(edge_path_list, chosen_state=0, ini_len=0):
    path_length=0
    cycl_length=0
    slope_list=[]
    loe_list = []
    lts_list = []
    lts_weight_list = []
    adt_list = []
    adt_weight_list = []
    Q85_list = []
    Q85_weight_list = []
    not_included_links = 0
    path_size = 0
    if ini_len!=0:
        path_length= ini_len
    for edge in edge_path_list:
        path_size+=1
        if int(edge) == 1607918:
            pass
        if int(edge) not in db_df.index:
            not_included_links+=1
            continue
        
        edge_length = pd.Series(db_df['length'].loc[int(edge)]).iloc[0]
        if ini_len==0:
            path_length += edge_length
            
        if int(edge) in db_df['ID_TRC'].values and pd.Series(db_df['ID_TRC'].loc[int(edge)]).iloc[0] in lts_df.index:
            
            slope = pd.Series(lts_df['slope'].loc[db_df['ID_TRC'].loc[int(edge)]]).iloc[0]      
            if slope != -8888 and slope !=-9999:
                slope_list.append(slope)
                loe_list.append(slope*edge_length)
                
            lts = pd.Series(lts_df['lts'].loc[db_df['ID_TRC'].loc[int(edge)]]).iloc[0] 
            
            adt = pd.Series(lts_df['ADT'].loc[db_df['ID_TRC'].loc[int(edge)]]).iloc[0] 
            if adt !=-8888 and adt != -9999:
                adt_list.append(adt)
                adt_weight_list.append(adt*edge_length)

            Q85 = pd.Series(lts_df['Q85'].loc[db_df['ID_TRC'].loc[int(edge)]]).iloc[0] 
            if adt !=-8888 and adt != -9999:
                Q85_list.append(Q85)
                Q85_weight_list.append(Q85*edge_length)
                
        else:
            lts = 0

        lts_list.append(lts)
        lts_weight_list.append(lts*edge_length)
        


        if float(edge) in db_df['ID'].values:
            cycl_length += pd.Series(db_df['length'].loc[int(edge)]).iloc[0] 
        

    return {'length':path_length,'number of links' : path_size, 'infra_length' : cycl_length, 'infra_ratio' : min((cycl_length/max(path_length,1)),1), 'chosen':chosen_state,'avg_slope':(sum(slope_list)/max(len(slope_list),1)), 'max_slope' : max(slope_list, default=0), 'avg_loe':(sum(loe_list)/max(len(loe_list),1)),
             'max_loe' : max(loe_list, default=0), 'avg_lts':(sum(lts_list)/max(len(lts_list),1)), 'max_lts' : max(lts_list, default=0)

             , 'avg_lts_dist_w' : (sum(lts_weight_list)/max(len(lts_weight_list),1)), 'avg_ADT' : (sum(adt_list)/max(len(adt_list),1)),
             'avg_adt_dist_w' : (sum(adt_weight_list)/max(len(adt_weight_list),1)), 'avg_Q85' : (sum(Q85_list)/max(len(Q85_list),1)),
             'avg_Q85_dist_w' : (sum(Q85_weight_list)/max(len(Q85_weight_list),1)), 'not_included_links' : not_included_links
            }
    

G = nx.read_graphml("road_netowrk_2015_with_coords.graphml")

choice_set_filepath = 'choice set/'
database_filepath = 'shapefiles/2015 attemtp/road_properties_2015.csv'
cyclist_trajectory_filepath = 'cyclists/cyclists_trips.csv'
output_filepath = 'choice properties/'
lts_filepath = 'shapefiles/LTS_links.csv'
demographics_filepath = 'demographics/MonResoVelo_user_anonyme.csv'
db_df = pd.read_csv(database_filepath, index_col='ID_RD')

chosen_path_df = pd.read_csv(cyclist_trajectory_filepath, index_col= 'id_origine')
#chosen_path_df = chosen_path_df.dropna(axis=0, how='any')

#chosen_path_df.index = chosen_path_df.index.astype(int)
lts_df = pd.read_csv(lts_filepath, index_col = 'ID_TRC')

demo_df = pd.read_csv(demographics_filepath, index_col='id', sep=';')

error_id={}

trip_list = [f for f in os.listdir(choice_set_filepath) if os.path.isfile(os.path.join(choice_set_filepath, f))]

debug = True
late_start = False
start_id = 19270
for choice_set_file in trip_list:
    try:
        idnum = int(choice_set_file.split("_")[0])
        if late_start:
            if idnum<start_id:
                continue
        if debug:
            idnum =19270
        choice_id=0
        path_dict = {}
        path_size_dict={}
        edge_path_list=[]
        shortest_path_list=[]
        print('cyclist:',idnum)
        with open(f"{choice_set_filepath}{idnum}_choice_set.json", 'r') as json_file:
            choice_set = json.load(json_file)


        chosen_path = ast.literal_eval(chosen_path_df['trip_segment'].loc[idnum]) 

        #chosen path not working right now, bike network files are new and id's do not match trajectory data
        path_dict[choice_id] = get_path_properties(chosen_path, 1, ini_len=chosen_path_df['length'].loc[idnum])
        path_size_dict[choice_id]=chosen_path
        shortest_path_list.append(path_dict[choice_id]['length'])
        choice_id+=1

        #get edge id list
        
        #to get path size, change loop to create a dictionary with key:choice_id value:edge_path_list and then loop through creating PS factor and THEN run get_properties_function
        for path in choice_set:
            edge_path_list=[]

            for i in range(0,(len(path)-1)):
                j=i+1
                
                edge_path_list.append(G.edges[path[i],path[j]]['ID_RD'])
            path_size_dict[choice_id] = edge_path_list
            path_dict[choice_id] = get_path_properties(edge_path_list, 0)
            shortest_path_list.append(path_dict[choice_id]['length'])
            choice_id+=1
            
            
            
        shortest_path_len= min(shortest_path_list) 
        for choice_id,path_list in path_size_dict.items():
            path_len=path_dict[choice_id]['length']
            path_size=0
            for link in path_list:
                try:
                    link_len = (pd.Series(db_df['length'].loc[int(link)]).iloc[0]) #TODO: investigate why so many paths have unknown links, possibly use network to find replacement
                except KeyError:
                    link_len = db_df['length'].mean() #if the length of the link is unknown, assign it the average link length
                first_term = link_len/path_len
                denomonator = 0
                for alt_id, alt_path in path_size_dict.items():
                    if link in alt_path:
                        denomonator +=shortest_path_len/path_dict[alt_id]['length']
                path_size+= first_term/denomonator
            path_dict[choice_id]['path_size']=path_size
        
        
        all_columns = set()
        for value_dict in path_dict.values():
            all_columns.update(value_dict.keys())


        #getting demographic values NOT USABLE UNTIL ID MATCHING METHOD IS RESOLVED
        try:
            gender = demo_df['gender'].iloc[int(idnum)]
        except IndexError:
            gender = 0
        try:
            age = demo_df['age'].iloc[int(idnum)]
        except IndexError:
            age = 0
        try:
            income = demo_df['income'].iloc[int(idnum)]
        except IndexError:
            income = 0


        # Add 'choice_id' as the first column
        csv_columns = ['choice_id'] + sorted(all_columns)+['gender', 'age','income']

        # Open the CSV file for writing
        with open(output_filepath+'properties_'+str(idnum)+'.csv', 'w', newline='') as csvfile:
            # Create a CSV DictWriter object
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)

            # Write the CSV header
            writer.writeheader()

            # Write each entry in path_dict as a row
            for key, value_dict in path_dict.items():
                # Include the 'choice_id' in the row data
                row = {'choice_id': key, 'gender': gender, 'age' : age, 'income' : income}
                row.update(value_dict)  # Add the rest of the columns from the value dict

                # Write the row to the CSV
                writer.writerow(row)

        print(f"Successfully written to CSV: {output_filepath}_{idnum}")
        if debug:
            break
    except RecursionError:
        cyclist_error(idnum)
        if debug:
            break
        

current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
error_id_filename = f'choice properties/error_log/error_ids_{current_time}.csv'

with open(error_id_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write header
    writer.writerow(['cyclist_id', 'reason'])
    
    # Write each key-value pair as a row
    for cyclist_id, reason in error_id.items():
        writer.writerow([cyclist_id, reason])
print(f"{len(error_id)} cyclist trips had issues")
