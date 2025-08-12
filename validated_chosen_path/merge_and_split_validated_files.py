"""
Used if there are multiple validated path correction files
to create a single file for analysis."""

import os
import pandas as pd

df_list = []
validation_path = "validated_chosen_path"

for filename in os.listdir(validation_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(validation_path, filename)
        df = pd.read_csv(file_path)
        df_list.append(df)


full_df = pd.concat(df_list, ignore_index=True)
full_df = full_df.sort_values(by="trip_id")
#full_df.to_csv(validation_path + "/full_validation/cyclist_chosen_with_errors.csv")

duplicates = full_df[full_df.duplicated('trip_id', keep=False)]

grouped = duplicates.groupby('trip_id')

def dedup_logic(group):
    if group['errors'].nunique() == 1:
        return group.iloc[[0]]  # keep only the first row
    else:
        return group            # keep all rows

# Step 4: Apply the logic to each group
filtered_duplicates = grouped.apply(dedup_logic).reset_index(drop=True)

# Step 5: Combine with the non-duplicates
non_duplicates = full_df[~full_df['trip_id'].isin(duplicates['trip_id'])]
result_df = pd.concat([non_duplicates, filtered_duplicates], ignore_index=True)

duplicates = result_df[result_df.duplicated('trip_id', keep=False)]
print(duplicates)

no_df = result_df[result_df['errors'] == 'no']
minor_df = result_df[result_df['errors'] == 'minor']
major_df = result_df[result_df['errors'] == 'major']

result_df.to_csv(validation_path + "/full_validation/cyclist_chosen_with_errors.csv")
no_df.to_csv(validation_path + "/full_validation/cyclist_no_error.csv")
minor_df.to_csv(validation_path + "/full_validation/cyclist_minor_error.csv")
major_df.to_csv(validation_path + "/full_validation/cyclist_major_error.csv")
