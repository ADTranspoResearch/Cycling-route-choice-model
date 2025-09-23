import os
import glob
import shutil
import re
import tempfile
import gc

from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsSpatialIndex,
    QgsVectorFileWriter,
)
from qgis import processing

def largest_shortest_distance(points_layer, lines_layer, k_nearest=5):
    """
    Compute the largest shortest distance from points to lines.

    :param points_layer: QgsVectorLayer containing point features
    :param lines_layer: QgsVectorLayer containing line features
    :param k_nearest: Number of nearest lines to consider for each point (default 5)
    :return: float, largest shortest distance
    """
    # Build spatial index for line geometries
    index = QgsSpatialIndex(lines_layer.getFeatures())
    
    max_distance = 0.0
    
    for point_feat in points_layer.getFeatures():
        point_geom = point_feat.geometry()
        if point_geom is None or point_geom.isEmpty():
            continue
        
        # Find nearest line IDs using spatial index
        nearest_ids = index.nearestNeighbor(point_geom.asPoint(), k_nearest)
        nearest_lines = [lines_layer.getFeature(fid).geometry() for fid in nearest_ids]
        
        # Compute distance from point to nearest lines
        min_dist = min([point_geom.distance(line_geom) for line_geom in nearest_lines])
        
        # Update maximum
        if min_dist > max_distance:
            max_distance = min_dist
    
    return max_distance

def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)  # remove file or symlink
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # remove folder and all contents
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

parent_directory = "C:/Users/adapic/Documents/Cycling Route Choice Model/git/Cycling-route-choice-model/manual_map_matching/"
#parent_directory = "J:/Documents/SURE/cycling route choice model/github/Cycling-route-choice-model/manual_map_matching/"
matched_trajectory_output_folder = "cyclist_map_matched/"
temporary_folder = "temporary_data"
road_network_filename = "road_network.shp"
road_network = QgsVectorLayer(parent_directory+road_network_filename, "road_network", "ogr")

clear_folder(parent_directory+temporary_folder)
    

trajectory_folder = "cyclist_raw_data"
trajectory_file_list = glob.glob(os.path.join(parent_directory+trajectory_folder,"*.shp"))

matched_file_list = glob.glob(os.path.join(parent_directory+matched_trajectory_output_folder,"*.shp"))

matched_basenames = [os.path.basename(path) for path in matched_file_list]


for filename in trajectory_file_list:
    cylist_basename = os.path.basename(filename)
    if cylist_basename in matched_basenames:
        continue
    match = re.search(r"id_origine_(\d+)\.shp$", filename)
    if match:
        cyclist_id = int(match.group(1))
        print(cyclist_id)
    else:
        print("No match found")
    

    full_trajectory = QgsVectorLayer(filename,"trajectory", "ogr")
    traj_tmp_path = parent_directory+temporary_folder+f"/traj_{cyclist_id}.shp"
    trajectory = processing.run("omm:reduce_trajectory_density", {
        'TRAJECTORY':full_trajectory,
        'KEEP_LAST_FEATURE':False,
        'DISTANCE':50,
        'OUTPUT':traj_tmp_path
        })
    debug_traject = parent_directory+trajectory_folder+"/id_origine_52.shp"

    trajectory_layer = QgsVectorLayer(filename, "traject","ogr")
    # Clip network to reduce compute time
    tmp_path = parent_directory+temporary_folder+f"/clipped_{cyclist_id}.shp"
    clipped_network = processing.run("omm:clip_network", {
        'NETWORK':road_network,
        'TRAJECTORY':trajectory_layer,
        'ORDER_FIELD':'vertex_ind',
        'BUFFER_RADIUS':100,
        'OUTPUT':tmp_path
        })
    clipped_network_layer = QgsVectorLayer(tmp_path,"clipped_network", "ogr")

    #Run map matching
    max_search_distance = largest_shortest_distance(trajectory_layer, clipped_network_layer) + 5
    features = 0
    matching_search_distance = max_search_distance
    print(f"initial search:{matching_search_distance}")
    attempts = 0
    while features == 0 and attempts < 5 :
        matched_path = processing.run("omm:match_trajectory", {
            'NETWORK':clipped_network_layer,
            'TRAJECTORY':trajectory_layer,
            'TRAJECTORY_ID':'vertex_ind',
            'MAX_SEARCH_DISTANCE':matching_search_distance,
            'TYPE':0,
            'OUTPUT':'TEMPORARY_OUTPUT'
            })
        features = matched_path["OUTPUT"].featureCount()
        matching_search_distance += 5
        attempts +=1
    print(matching_search_distance,"final distance")
#    if features != 0:
#        QgsProject.instance().addMapLayer(matched_path["OUTPUT"])

    processing.run("native:snapgeometries", {
        'INPUT':full_trajectory,
        'REFERENCE_LAYER':matched_path["OUTPUT"],
        'TOLERANCE':max_search_distance,
        'BEHAVIOR':3,
        'OUTPUT':parent_directory+matched_trajectory_output_folder+f"id_origine_{cyclist_id}.shp"
        })
    print(f'cylist {cyclist_id}')

print("worked")

QgsProject.instance().removeAllMapLayers()

# Delete Python references
del clipped_network_layer
del trajectory_layer
del full_trajectory
del matched_path

# Force cleanup
import gc
gc.collect()







 