import os
import shutil
import glob
import geopandas as gpd

def compare_point_geometries(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame, ignore_order: bool = False) -> bool:
    """
    Check if two point GeoDataFrames have the same geometry.
    
    Parameters
    ----------
    gdf1 : gpd.GeoDataFrame
        First GeoDataFrame containing Point geometries.
    gdf2 : gpd.GeoDataFrame
        Second GeoDataFrame containing Point geometries.
    ignore_order : bool, optional
        If True, checks if both contain the same set of geometries (order doesn't matter).
        If False, compares geometries row by row (order matters).
    
    Returns
    -------
    bool
        True if the geometries are the same, False otherwise.
    """
    # Must have same length
    if len(gdf1) != len(gdf2):
        return False

    if ignore_order:
        # Compare sets of WKT representations (handles uniqueness, order-independent)
        return set(gdf1.geometry.apply(lambda g: g.wkt)) == set(gdf2.geometry.apply(lambda g: g.wkt))
    else:
        # Compare row by row using WKT strings
        return all(g1.equals(g2) for g1, g2 in zip(gdf1.geometry, gdf2.geometry))

#parent_directory = "C:/Users/adapic/Documents/Cycling Route Choice Model/git/Cycling-route-choice-model/manual_map_matching/"
parent_directory = "J:/Documents/SURE/cycling route choice model/github/Cycling-route-choice-model/manual_map_matching/"


raw_folder = "cyclist_raw_data"
matched_trajectory_folder = "cyclist_map_matched"

raw_file_list = glob.glob(os.path.join(parent_directory+raw_folder,"*.shp"))
matched_file_list = glob.glob(os.path.join(parent_directory+matched_trajectory_folder,"*.shp"))
modified_file_folder = 'manual_map_matching/cyclist_modified_trajectories/'

raw_basenames = [os.path.basename(path) for path in raw_file_list]
different_geo = 0
same_geo = 0
no_raw_file = 0
for filename in matched_file_list:
    cyclist_basename = os.path.basename(filename) 

    if cyclist_basename in raw_basenames:
        raw_filename = os.path.join(parent_directory+raw_folder,cyclist_basename)
    else:
        no_raw_file +=1
        continue
    raw_gdf = gpd.read_file(raw_filename)
    matched_gdf = gpd.read_file(filename)
    if compare_point_geometries(raw_gdf,matched_gdf,True):
        for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
            f = filename.replace(".shp", ext)
            if os.path.exists(f):
                shutil.copy(f, modified_file_folder)        
        same_geo+=1
    else:
        different_geo+=1

print(f"trajectories that were changed: {different_geo}")
print(f"trajectories that are the same: {same_geo}")
print(f"trajectories failed: {no_raw_file}")