import json
import os

from qgis.core import *
from qgis.utils import iface
import processing 
from PyQt5.QtCore import QVariant


choice_set_filepath = 'J:/Documents/SURE/cycling route choice model/github/Cycling-route-choice-model/edge_lists/'
road_network_filepath = 'J:/Documents/SURE/cycling route choice model/github/Cycling-route-choice-model/shapefiles/map_matching/2015merged_network_file.shp'



idnum = 52

with open(f"{choice_set_filepath}{idnum}_edge_choice_set.json", 'r') as json_file:
    choice_set = json.load(json_file)
    

road_network_layer = iface.addVectorLayer(road_network_filepath, "road_network", "ogr")


# Iterate over each choice set
for choice_num, edge_ids in enumerate(choice_set, start=1):
    # Ensure integers
    edge_ids = tuple(int(x) for x in edge_ids)

    # Build QGIS expression
    expression = f'"ID_RD" IN {edge_ids}'
    print(expression)

    # Select features
    road_network_layer.selectByExpression(expression, QgsVectorLayer.SetSelection)

    # Save selected features
    output_path = f"J:/Documents/SURE/cycling route choice model/github/Cycling-route-choice-model/route_visualization/shapefiles/cyclist_{idnum}/choice{choice_num}.shp"
    result = processing.run("native:saveselectedfeatures", {
        "INPUT": road_network_layer,
        "OUTPUT": output_path
    })

    # Add saved layer to project
    iface.addVectorLayer(output_path, f"choice_route_{choice_num}", "ogr")

    # Clear selection for next loop
    road_network_layer.removeSelection()
QgsProject.instance().removeMapLayer(road_network_layer)