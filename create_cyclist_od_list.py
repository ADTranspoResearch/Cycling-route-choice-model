import pandas as pd
from utils import *

filename = "shapefiles/2015_attempt/cyclist_od_remove_first_last_pt.csv"
output_filepath = "cyclists/"
check_dir(output_filepath)

df = pd.read_csv(filename)
print(df.columns)
od_dict = {}
unique_users = []
index_count = 0
for index, row in df.iterrows():

    cyclist_id = row["id_origine"]
    if cyclist_id not in unique_users:
        matching_rows = df[df["id_origine"] == cyclist_id]

        # Ensure there are exactly two matching rows
        if len(matching_rows) != 2:
            raise ValueError(
                f"Expected exactly 2 rows for cyclist_id {cyclist_id}, but found {len(matching_rows)}."
            )
        other_row = matching_rows[matching_rows.index != row.name]

        if other_row.empty:
            raise ValueError(
                f"No other row found for cyclist_id {cyclist_id}."
            )

        other_row = other_row.iloc[0]  # Get the first (and only) row

        if row["vertex_pos"] == 1 and other_row["vertex_pos"] == -2:
            # origin and other row destination
            origin = row["node_id"]
            dest = other_row["node_id"]

        elif row["vertex_pos"] == -2 and other_row["vertex_pos"] == 1:
            origin = other_row["node_id"]
            dest = row["node_id"]

        else:
            raise ValueError(
                f"cyclist {cyclist_id} does not have origin and/or destination"
            )

        # ['cyclist_id', 'origin', 'destination']
        od_dict[index_count] = [cyclist_id, origin, dest]
        index_count += 1
        unique_users.append(cyclist_id)
od_df = pd.DataFrame.from_dict(
    od_dict, orient="index", columns=["cyclist_id", "origin", "destination"]
)

od_df.to_csv(output_filepath + "cyclist_od_list_remove_first_last_pt.csv")
