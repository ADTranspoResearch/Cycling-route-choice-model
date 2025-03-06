import pandas as pd
import networkx as nx
import json
import csv
from datetime import datetime
import time
from line_profiler import LineProfiler



tik=time.time()

#TODO:add action to sp_edge_removed: look to improve function by containing more actions that are repeated
def sp_edge_removed(graph, edges_list: list[tuple], od_tup: tuple[str]): #this function will take a graph, a list of tups of nodes that define an edge, and an tup of OD IDs, it will remove the edge from the graph and output the shortest path between ODs on the new graph. it will also output the dictionary to be stored in the dictionary that contains all graphs and removed edges


    removed_edges = [(u,v,graph.get_edge_data(u,v)) for u,v in edges_list]

    for u, v in edges_list:
        graph.remove_edge(u,v)
    try:

        sp = nx.astar_path(graph, od_tup[0], od_tup[1], heuristic=euclidian, weight='length') #


    except nx.NetworkXNoPath:
        return None
    finally:
        for u, v, attr in removed_edges:
            graph.add_edge(u,v, **attr)
    return (sp, {'removed edges': edges_list})

def euclidian(a, b):

    x1, y1 = G.nodes[a]['x'], G.nodes[a]['y']
    x2, y2 = G.nodes[b]['x'], G.nodes[b]['y']

    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def manhattan(a,b):

    x1, y1 = G.nodes[a]['x'], G.nodes[a]['y']
    x2, y2 = G.nodes[b]['x'], G.nodes[b]['y']

    return (abs((x2 - x1)) + abs((y2 - y1))) 


#lp = LineProfiler(sp_edge_removed)
#lp.enable()

filename = 'test_output_od_list.csv'
od_df = pd.read_csv(filename)


G = nx.read_graphml("road_netowrk_2015_with_coords.graphml")

#print(nx.shortest_path(G,'22518','29879'))

#print(G.edges['22518','22519']['ID_RD'])

choice_set_size = 80

choice_set_dict = {}

error_id={}

debug = True
skiprows = False
early_stop = False
start_row = 820
stop_row = 841
short_set_count = 0
for index, row in od_df.iterrows(): #iterate over every GPS trace and OD pair to get the full Choice Set
    
    if debug:
        row = od_df[od_df['cyclist_id'] == 52].iloc[0]
    if skiprows:
        if int(row['cyclist_id']) < start_row:
            continue
    if early_stop:
        if int(row['cyclist_id']) >= stop_row:
            break

      
    sp_list = []
    sp_and_removed_edge_dict = {}
    try:
        sp = nx.astar_path(G,str(row['origin']),str(row['destination']),heuristic=euclidian, weight='length') #find shortest path from the original graph, 
    except nx.NetworkXNoPath:
        error_id[row['cyclist_id']] = 'no path from OD'
        print(f"warning: cyclist {row['cyclist_id']} has no path from origin to destination!")
        continue
    sp_list.append(sp) #sp_list contains all shortest paths for a given OD pair
    sp_and_removed_edge_dict[0]={'sp':sp, 'removed_edges':[]}
    
    

    #ATTEMPT AT CREATING A WHILE LOOP TO MAKE 80 CHOICE SET
    od_tuple = (str(row['origin']),str(row['destination']) )

    counter= -1
    while len(sp_list)< choice_set_size:
        counter+=1
        try:    
            current_parent_sp = sp_and_removed_edge_dict[counter]['sp'] #TODO: add counter to run through dict
        except KeyError:
            break
        #for loop that loops through a given shortest path and creates all the paths from the next level, first one would be using sp0, but then would need to be capable of recieving the sps from the first level
        start_nodes = current_parent_sp[:-1]
        end_nodes = current_parent_sp[1:]

        sp_tuples = list(zip(start_nodes,end_nodes))
        for u,v in sp_tuples: #loops through each edge in the given shortest path where u is starting nodes and v is end node.
            removed_edges_list = sp_and_removed_edge_dict[counter]['removed_edges'].copy()
            edge_tuple = (u,v)
            removed_edges_list.append(edge_tuple)
            sp_result = sp_edge_removed(G,removed_edges_list,od_tuple)
            if sp_result is None:
                continue
            sp_1, sp_graph_dict = sp_result           
            if sp_1 not in sp_list:
                sp_list.append(sp_1)
                sp_and_removed_edge_dict[len(sp_and_removed_edge_dict)]={'sp':sp_1, 'removed_edges':removed_edges_list} 
            else:
                continue
            
            if len(sp_list)>= choice_set_size:
                break
        

    
    if len(sp_list)<80:
        print(f"warning: cyclist {row['cyclist_id']}'s choice set is only {len(sp_list)} long!")
        error_id[row['cyclist_id']] = f'choice set size, {len(sp_list)}'
        short_set_count+=1

    output_path = 'choice set/'
    choice_set_filename = f"{row['cyclist_id']}_choice_set.json"
    print(f"{row['cyclist_id']}_choice_set.json")
    with open(output_path+choice_set_filename, 'w') as file:
        json.dump(sp_list, file)
    if debug:
        break

current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
error_id_filename = f'choice set/Past Error ID/error_ids_{current_time}.csv'

with open(error_id_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write header
    writer.writerow(['cyclist_id', 'reason'])
    
    # Write each key-value pair as a row
    for cyclist_id, reason in error_id.items():
        writer.writerow([cyclist_id, reason])
print(f"{len(error_id)} cyclist trips had issues")
print(f"{short_set_count} cyclists have less than 80 choices")
tok=time.time()
print('time taken: ',(tok-tik))


#lp.disable()
#lp.print_stats()
