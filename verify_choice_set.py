"""
This module checks how many choice sets contain the chosen path for a 
given cyclist.
"""
import json
import ast
import pandas as pd



choice_set_folder='choice_set/'
chosen_path_filepath = "manual_map_matching/cyclist_chosen_path_node.csv"
chosen_path_df = pd.read_csv(chosen_path_filepath, index_col="id_origine")

count_100 = 0
count_80 = 0
count_50 = 0
count_total = 0
for index, row in chosen_path_df.iterrows():
    try:
        with open(f"{choice_set_folder}{index}_choice_set.json", "r") as json_file:
            choice_set = json.load(json_file)
    except FileNotFoundError:
        continue
    count_total+=1
    choice_set = [[int(x) for x in path] for path in choice_set]
    chosen_path = ast.literal_eval(row["node_path"])
    max_int = 0
    for i, choice in enumerate(choice_set):
        if i == 74:
            pass
        if choice in chosen_path:
            count_100+=1
        else:
            # Check for 80% match
            found_80 = False
            found_50 = False
            chosen_set = set(chosen_path)


            choice = set(choice)
            intersection = chosen_set & choice
            if len(intersection) > max_int:
                max_int = len(intersection)
                print(i) 
            if len(intersection) / len(chosen_set) >= 0.8:
                count_80 += 1
                found_80 = True
                continue
            elif len(intersection) / len(chosen_set) >= 0.5:
                count_50 += 1
                found_50 = True
                continue        
print(max_int, len(chosen_path) )
print(f"100%: {count_100}")
print(f"80%: {count_80}")
print(f"50%: {count_50}")
print(f"total: {count_total}")