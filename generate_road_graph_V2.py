#method of extracting network from shapefile changed so new script was required to construct graph
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def get_node_coords(rd_id, vertex_pos, id_name='ID_TRC' ):
    x = float(df.loc[(df[id_name] == rd_id) & (df['vertex_pos'] == vertex_pos), 'X'].iloc[0])
    y = float(df.loc[(df[id_name] == rd_id) & (df['vertex_pos'] == vertex_pos), 'Y'].iloc[0])
    return x, y


# Load the shapefile
df = pd.read_csv('shapefiles/2015 verticies with node id_geometry.csv')

G = nx.DiGraph()

road_id_list = df['ID_TRC'].dropna().unique().tolist() #gets a list of all the unique ID numbers from the road network, does not include bike network

two_way = False
#create the road network using only road map, bike map is added in next loop
for id_trc in road_id_list:
    SENS_CIR = df.loc[(df['ID_TRC'] == id_trc) & (df['vertex_pos'] == 0), 'SENS_CIR'].iloc[0]

    if SENS_CIR == 0:
        first_node = df.loc[(df['ID_TRC'] == id_trc) & (df['vertex_pos'] == 0), 'node_id'].iloc[0]
        first_x_corr, first_y_corr = get_node_coords(id_trc, 0)

        last_node = df.loc[(df['ID_TRC'] == id_trc) & (df['vertex_pos'] == -1), 'node_id'].iloc[0]
        last_x_corr, last_y_corr = get_node_coords(id_trc, -1)
        two_way = True
        
    elif SENS_CIR == 1:
        first_node = df.loc[(df['ID_TRC'] == id_trc) & (df['vertex_pos'] == 0), 'node_id'].iloc[0]
        first_x_corr, first_y_corr = get_node_coords(id_trc, 0)
        
        last_node = df.loc[(df['ID_TRC'] == id_trc) & (df['vertex_pos'] == -1), 'node_id'].iloc[0]
        last_x_corr, last_y_corr = get_node_coords(id_trc, -1)

    elif SENS_CIR == -1:
        first_node = df.loc[(df['ID_TRC'] == id_trc) & (df['vertex_pos'] == -1), 'node_id'].iloc[0]
        first_x_corr, first_y_corr = get_node_coords(id_trc, -1)

        last_node = df.loc[(df['ID_TRC'] == id_trc) & (df['vertex_pos'] == 0), 'node_id'].iloc[0]
        last_x_corr, last_y_corr = get_node_coords(id_trc, 0)
    
    length = df.loc[(df['ID_TRC'] == id_trc) & (df['vertex_pos'] == 0), 'Length'].iloc[0]
    
    G.add_edge(first_node, last_node, ID_RD=id_trc, length=length)
    if two_way:
        G.add_edge(last_node, first_node, ID_RD=id_trc, length=length)
        two_way = False
    
    G.nodes[first_node]['x'] = first_x_corr
    G.nodes[first_node]['y'] = first_y_corr
    G.nodes[last_node]['x'] = last_x_corr
    G.nodes[last_node]['y'] = last_y_corr



bike_id_list = df['ID'].dropna().unique().tolist() #gets a list of all the unique ID numbers from the bike network, does not include road network

two_way = False
bike_count=0
bike_count_no_network=0
bike_count_network=0
for id_bk in bike_id_list:
    trc = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == 0), 'ID_TRC_GEO'].iloc[0]
    type1 = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == 0), 'TYPE_VOIE'].iloc[0]
    type2 = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == 0), 'TYPE_VOIE2'].iloc[0]
    if round(trc) not in df['ID_TRC'].values:
       
        if type2 == 0:
            bike_count_no_network+=1
            first_node = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == 0), 'node_id'].iloc[0]
            first_x_corr, first_y_corr = get_node_coords(id_bk, 0, id_name='ID')
            last_node = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == -1), 'node_id'].iloc[0]
            last_x_corr, last_y_corr = get_node_coords(id_bk, -1, id_name='ID')

        elif type2 == 33: #todo contraflow off road
            continue
        elif type2 == 31:#todo contraflow off road2
            continue
        else:
            continue
    else:
        
        if type2 == 0: #this means bike network is in direction of traffic
            bike_count_network+=1
            SENS_CIR = df.loc[(df['ID_TRC'] == round(trc)) & (df['vertex_pos'] == 0), 'SENS_CIR'].iloc[0]
            if SENS_CIR == 0:
                first_node = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == 0), 'node_id'].iloc[0]
                first_x_corr, first_y_corr = get_node_coords(id_bk, 0, id_name='ID')
                last_node = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == -1), 'node_id'].iloc[0]
                last_x_corr, last_y_corr = get_node_coords(id_bk, -1, id_name='ID')
                two_way = True
                
            elif SENS_CIR == 1:
                first_node = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == 0), 'node_id'].iloc[0]
                first_x_corr, first_y_corr = get_node_coords(id_bk, 0, id_name='ID')
                last_node = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == -1), 'node_id'].iloc[0]
                last_x_corr, last_y_corr = get_node_coords(id_bk, -1, id_name='ID')

            elif SENS_CIR == -1:
                first_node = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == -1), 'node_id'].iloc[0]
                first_x_corr, first_y_corr = get_node_coords(id_bk, -1, id_name='ID')
                last_node = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == 0), 'node_id'].iloc[0]
                last_x_corr, last_y_corr = get_node_coords(id_bk, 0, id_name='ID')



        elif type2 == 30: #TODO single contraflow lane
            first_node = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == -1), 'node_id'].iloc[0]
            first_x_corr, first_y_corr = get_node_coords(id_bk, -1, id_name='ID')
            last_node = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == 0), 'node_id'].iloc[0]
            last_x_corr, last_y_corr = get_node_coords(id_bk, 0, id_name='ID')

        elif type2 == 31: #TODO sharrow and contraflow
            continue
        elif type2 == 33: #TODO lane and contraflow
            continue
        elif type2 == 34: #rush hour lane NEGLECTING?
            continue
    length = df.loc[(df['ID'] == id_bk) & (df['vertex_pos'] == 0), 'LONGUEUR'].iloc[0]    
    G.add_edge(first_node, last_node, ID_RD=id_bk, length=length)
    bike_count+=1
    if two_way:
        G.add_edge(last_node, first_node, ID_RD=id_bk, length=length)
        two_way = False
    G.nodes[first_node]['x'] = first_x_corr
    G.nodes[first_node]['y'] = first_y_corr
    G.nodes[last_node]['x'] = last_x_corr
    G.nodes[last_node]['y'] = last_y_corr

nx.write_graphml(G, "road_network_2015_with_coords.graphml")
print('written graph to memory')
print(f'bike count: {bike_count}')
print(f'no network count: {bike_count_no_network}')
print(f'network count: {bike_count_network}')
    