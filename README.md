Pre-Requisites:
project requires initial processing in QGIS to create 2 inputs to the code: a node based network file of the road network to be used, and an origin-destination list for each cyclist

Node-based network file:
assuming you are starting from the Montreal geobase file, you will first need to create a point file that contains a point at every start and end point of the links in the network. There should only be 1 node per junction so if 2 points overlap, they should be collapsed into 1 point.
next, every link needs to be associated with 2 of these nodes, indicating which is the start node and which is the end node. An example of what that looks like can be found in 'shapefiles/2015 verticies with node id_geometry.csv' it should generally have the following format:
| Link_ID   | position  | Node_ID   |
|------------|------------|------------|
| 12345   | 0   | 5   |
| 12345   | -1   | 8   |

The position column indicates if the node is the start point (0) or the end point (-1) of the link. For each link, there should be 2 row entries in the file.

Origin-Destination List:
see 'test_output_od_list.csv' for an example. This file should contain the origin node_id and destination node_id for every cyclist

| cyclist_id   | origin  | destination   |
|------------|------------|------------|
| 52   | 24323   | 20067   |
| 53   | 19768   | 27795   |

Running the code:

step 1 - create the networkx graph:
'generate_road_graph_V2.py' reads the node-based network file and converts it into a networkx graph, it also includes properties for the edges (links) of the network such as length, edge_id, coordinates of the nodes, and any other properties you want to specify. after creating the network it saves it to a .graphml file.

step 2 - BFSLE choice set creation:
this choice model uses Breadth First Search Link Elimination method for creating choice sets for the cyclists. It takes the network and the cyclist OD list, and calculates 80 alternative paths between a cyclists origin and destination using BFSLE. These paths are a list of node ids that are used to travel from the origin to destination and they are saved as a list of lists in a .json file for each cyclist in the folder 'choice set/'. Each cyclist has their own file with the format '{cyclist_id}_choice_set.json'. Any cyclists that either do not create a .json, or who's choice set size is less than the specified minimun (80) will have their id number and reason saved in an error log in the folder 'Past Error ID'.

step 3 - Analyzing paths:
'choice_set_properties.py' takes the network, original cyclist trip data, and any other files that contain relevant data on either the links in the network or on the cyclists (such as a file that gives the average daily traffic for each link_id) as inputs. It calculates various variables and outputs a file that will be used as the training data for the logit model. For every cyclist it calculates parameters such as path length, level of effort, average vehicle volumes, among others, for each path in the choice set and the actual path taken by the cyclist. it puts all of these variables into their own column, with the first column being the path id number (from 0-80). there is also a column 'chosen' which will be the Y column for the model. This column's value is 1 for the cyclists actual chosen path, and 0 for all other path's created by the BFSLE algorithm. The format is similar to the previous step, each cyclist has a csv file with the data saved in the folder 'choice properties/' with the format 'properties_{cyclist_id}.csv'.

step 4 - multinomial logit model:
'Multinomial Model.py' takes the choice properties files as an input and creates a logit model based on the training data. It saves the model to a file and outputs an accuracy report. It is capable of specifying which variables should be included in the model, standardizing variables based on normal or uniform distribution, and outputing a histogram of the distribution for each variable.

optional step 5 - model analysis:
'analyze model parameters.py' is capable of outputing p-values and correlation matrices to analyze how the model performs and if any modifications need to be made.
