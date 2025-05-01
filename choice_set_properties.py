"""module takes choice sets and creates a set_property file for each"""
import json
import csv
import ast
import os
from datetime import datetime

import networkx as nx
import pandas as pd
from utils import check_dir, level_of_effort


def cyclist_error(cyc_id, reason=0):
    """prints problematic cyclist id and appends to error_id dict"""
    if reason == 0:
        print(f"warning: cyclist {cyc_id} did not create a properties file!")
        error_id[cyc_id] = 'error'
    elif reason == 1:
        print(f"cyclist {cyc_id} had a unknown link in chosen path!")
        error_id[cyc_id] = 'path_size-error'



def get_path_properties(cyc_path, chosen_state=0, ini_len=0):
    """takes in a path and outputs the properties for that path"""
    path_length=0
    cycl_length=0
    slope_list=[]
    loe_list = []
    lts_list = []
    lts_weight_list = []
    adt_list = []
    adt_weight_list = []
    q85_list = []
    q85_weight_list = []
    loe_index_list = []
    loe_index_w_list = []
    not_included_links = 0
    num_links = 0
    if ini_len!=0:
        path_length= int(ini_len)
    for edge in cyc_path:
        num_links+=1
        if int(edge) == 1607918:
            pass
        if int(edge) not in db_df.index:
            not_included_links+=1
            continue

        edge_length = pd.Series(db_df['length'].loc[int(edge)]).iloc[0]
        if ini_len==0:
            path_length += int(edge_length)

        if (
            int(edge) in db_df['ID_TRC'].values
            and pd.Series(db_df['ID_TRC'].loc[int(edge)]).iloc[0]
            in lts_df.index
        ):

            slope = pd.Series(
                        lts_df['slope'].loc[db_df['ID_TRC'].loc[int(edge)]]
                    ).iloc[0]
            if  slope != -8888 and slope !=-9999:
                slope_list.append(slope)
                loe_list.append(slope*edge_length)

            lts = pd.Series(
                lts_df['lts'].loc[db_df['ID_TRC'].loc[int(edge)]]
                ).iloc[0]
            if lts not in (-8825, -9999, -8440):
                lts_list.append(lts)
                lts_weight_list.append(lts*edge_length)

            adt = pd.Series(
                lts_df['ADT'].loc[db_df['ID_TRC'].loc[int(edge)]]).iloc[0]
            if adt not in (-8888, -9999):
                adt_list.append(adt)
                adt_weight_list.append(adt*edge_length)

            q85 = pd.Series(
                lts_df['Q85'].loc[db_df['ID_TRC'].loc[int(edge)]]).iloc[0]
            if q85 not in (-8888, -9999):
                q85_list.append(q85)
                q85_weight_list.append(q85*edge_length)
            if slope and edge_length:
                loe_index = level_of_effort(slope, edge_length)
                loe_index_list.append(loe_index)
                loe_index_w_list.append(loe_index*edge_length)
        else:
            lts = 0

            lts_list.append(lts)
            lts_weight_list.append(lts*edge_length)



        if float(edge) in db_df['ID'].values:
            cycl_length += pd.Series(db_df['length'].loc[int(edge)]).iloc[0]
# pylint: disable=C0301
# Breaking up the dictionary into multiple dicts to
# make it more readable
    # dictionary for anything related to LTS
    lts_dict = {
        'avg_lts':(sum(lts_list)/max(len(lts_list),1)),
        'max_lts' : max(lts_list, default=0),
        'avg_lts_dist_w' : (sum(lts_weight_list)/max(len(lts_weight_list),1)),
        'lts_sum':sum(lts_list), 'lts_dist_w_sum':sum(lts_weight_list),
        }
    # dictionary for any raw road attributes
    att_dict = {
        'length':path_length,
        'number_of_links' : num_links,
        'infra_length' : cycl_length,
        'infra_ratio' : min((cycl_length/max(path_length,1)),1),
        'chosen':chosen_state,'not_included_links' : not_included_links,
        }

    # dictionary for any attributes related to slope or level of effort
    loe_dict = {'avg_slope':(sum(slope_list)/max(len(slope_list),1)),
            'slope_sum':sum(slope_list),
            'max_slope' : max(slope_list, default=0),
            'avg_loe':(sum(loe_list)/max(len(loe_list),1)),
            'max_loe' : max(loe_list, default=0),
            'loe_index_sum':sum(loe_index_list),
            'loe_dist_w_sum':sum(loe_index_w_list),
            'loe_index_avg_dist_w':sum(loe_index_w_list)/max(len(loe_index_w_list),1)
            }

    #dictionary for any attributes about the vehicle volume or usage on links
    trf_dict = {'avg_ADT' : (sum(adt_list)/max(len(adt_list),1)),
            'ADT_sum': sum(adt_list),
            'ADT_dist_sum': sum(adt_weight_list), 
            'avg_adt_dist_w' : (sum(adt_weight_list)/max(len(adt_weight_list),1)),
            'Q85_sum' : sum(q85_list), 'Q85_dist_sum': sum(q85_weight_list),
            'avg_Q85' : (sum(q85_list)/max(len(q85_list),1)),
            'avg_Q85_dist_w' : (sum(q85_weight_list)/max(len(q85_weight_list),1)), 
            }
    prop_dict = lts_dict | att_dict | loe_dict | trf_dict

    return prop_dict
# pylint: enable=C0301

G = nx.read_graphml("road_network_2015_with_coords.graphml")

ADD_DEMOGRAPHICS = False
choice_set_filepath = 'choice_set/'
database_filepath = 'shapefiles/2015_attempt/road_properties_2015.csv'
cyclist_trajectory_filepath = 'cyclists/cyclists_trips.csv'
output_filepath = 'choice_properties/'
check_dir(output_filepath)
lts_filepath = 'shapefiles/LTS_links.csv'
demographics_filepath = 'demographics/MonResoVelo_user_anonyme.csv'
db_df = pd.read_csv(database_filepath, index_col='ID_RD')
error_filepath = 'choice_properties/error_log/'
check_dir(error_filepath)
error_id={}

chosen_path_df = pd.read_csv(
    cyclist_trajectory_filepath,
    index_col= 'id_origine'
    )
# Drops any rows with missing trip segments or id numbers which
# usually correspond to blank rows.
chosen_path_df.dropna(subset=['trip_segment','id'], inplace=True)

lts_df = pd.read_csv(lts_filepath, index_col = 'ID_TRC')


if ADD_DEMOGRAPHICS:
    demo_df = pd.read_csv(
        demographics_filepath, index_col='id', sep=';')

# in every loop check if the id is actually in the index,
# otherwise skip that trip
trip_list = [f for f in os.listdir(choice_set_filepath)
             if os.path.isfile(os.path.join(choice_set_filepath, f))]
trip_id_list = chosen_path_df.index.tolist()

debug = False
debug_id = 52
late_start = False
# Files are not sorted in numerical order, for example 3203 is index,
# 3080 but 52 is later, if using late start,
# 3203 will be done but not 52
late_start_by_index = False
start_id = 28942
start_index = 3175
index_count = 0
debug_break_outer = False

for choice_set_file in trip_list:
    idnum = int(choice_set_file.split("_")[0])
    # this section of code checks all the debugging options
    if late_start:
        if idnum<start_id:
            continue
    if late_start_by_index:
        if index_count<start_index:
            index_count+=1
            continue
    if debug:
        idnum =debug_id

    # start of actual loop
    if idnum not in trip_id_list:
        print(idnum,"not in trip list, skipping...")
        continue

    # Initialize all required empty lists
    choice_id = 0
    path_dict = {} # key=alt path id: value=properties of alternative
    path_size_dict = {} # key=alt path id: value=list of edges in path
    shortest_path_list = [] #contains length of all paths in choice set
    print('cyclist:',idnum)

    with open(
            f"{choice_set_filepath}{idnum}_choice_set.json", 'r') as json_file:
        choice_set = json.load(json_file)


    chosen_path = ast.literal_eval(
        chosen_path_df['trip_segment'].loc[idnum])


    path_dict[choice_id] = get_path_properties(
        chosen_path, 1, ini_len=chosen_path_df['length'].loc[idnum])
    path_size_dict[choice_id]=chosen_path
    shortest_path_list.append(path_dict[choice_id]['length'])
    choice_id+=1


    # To get path size, change loop to create a dictionary with
    # key:choice_id value:edge_path_list and then loop through
    # creating PS factor and THEN run get_properties_function
    for path in choice_set:
        edge_path_list=[]
        # Appends all the edges used in the path to edge_path_list
        # and assigns this list to path_size dict with alt_id as key
        for i in range(0,(len(path)-1)):
            j=i+1

            edge_path_list.append(G.edges[path[i],path[j]]['ID_RD'])
        path_size_dict[choice_id] = edge_path_list
        path_dict[choice_id] = get_path_properties(edge_path_list, 0)
        shortest_path_list.append(path_dict[choice_id]['length'])
        choice_id+=1

    # section for getting the path size factor
    shortest_path_len= min(shortest_path_list)
    for choice_id,path_list in path_size_dict.items():
        unknown_count = 0 # debug, delete if not in use
        path_len=path_dict[choice_id]['length']
        path_size=0
        for link in path_list:
            try:
                link_len = pd.Series(
                    db_df['length'].loc[int(link)]).iloc[0]
                #TODO: investigate why so many paths have unknown
                # links, possibly use network to find replacement
            except KeyError:
                # If the length of the link is unknown,
                # assign it the average link length
                link_len = db_df['length'].mean()
                unknown_count+=1
                debug_break_outer = True
                break


            first_term = link_len/path_len
            denomonator = 0
            for alt_id, alt_path in path_size_dict.items():
                if link in alt_path:

                    denomonator += (
                        shortest_path_len
                        /path_dict[alt_id]['length']
                    )
            path_size+= first_term/denomonator
        if debug_break_outer:
            break
        path_dict[choice_id]['path_size']=path_size
        if debug_break_outer:
            break
    if debug_break_outer:
        debug_break_outer = False
        cyclist_error(idnum,reason=1)
        continue
    all_columns = set()
    for value_dict in path_dict.values():
        all_columns.update(value_dict.keys())


    # getting demographic values
    # NOT USABLE UNTIL ID MATCHING METHOD IS RESOLVED
    if ADD_DEMOGRAPHICS:
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
    if ADD_DEMOGRAPHICS:
        csv_columns = (
            ['choice_id']
            + sorted(all_columns)
            + ['gender', 'age','income']
        )
    else:
        csv_columns = ['choice_id'] + sorted(all_columns)
    # Open the CSV file for writing
    output_file = output_filepath+'properties_'+str(idnum)+'.csv'
    with open(output_file, 'w', newline='',) as csvfile:
        # Create a CSV DictWriter object
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)

        # Write the CSV header
        writer.writeheader()

        # Write each entry in path_dict as a row
        for key, value_dict in path_dict.items():
            # Include the 'choice_id' in the row data
            if ADD_DEMOGRAPHICS:
                row = {
                    'choice_id': key,
                    'gender': gender,
                    'age' : age,
                    'income' : income
                    }
            else:
                row = {'choice_id': key}
            # Add the rest of the columns from the value dict
            row.update(value_dict)

            # Write the row to the CSV
            writer.writerow(row)

    print(f"Successfully written to CSV: {output_filepath}_{idnum}")
    if debug:
        break


current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
error_id_filename = 'error_ids_{current_time}.csv'

with open(
    (error_filepath+error_id_filename), mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write header
    writer.writerow(['cyclist_id', 'reason'])

    # Write each key-value pair as a row
    for cyclist_id, err_reason in error_id.items():
        writer.writerow([cyclist_id, err_reason])
print(f"{len(error_id)} cyclist trips had issues")
