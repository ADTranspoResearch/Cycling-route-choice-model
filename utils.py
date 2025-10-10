"""
Module contains various utility functions that are used across files.
"""

import os
import pandas as pd
import numpy as np
import networkx as nx


def check_dir(path):
    """
    Check if the directory exists, if not, creates it.
    """

    if not os.path.exists(path):
        # Create the directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{path}' created.")
    else:
        print(f"Directory '{path}' already exists.")


def level_of_effort(slope, length):
    """
    Given a slope and length of a link, returns the level of effort.

    Calculated based on scale from 'Slope stress criteria as a
    complement to traffic stress criteria, and impact on high comfort
    bicycle accessibility'.
    """

    if length < 150:
        if slope < 0.065:
            return 1
        elif slope < 0.08:
            return 2
        elif slope < 0.095:
            return 3
        elif slope < 0.11:
            return 4
        else:
            return 5
    elif length < 500:
        if slope < 0.05:
            return 1
        elif slope < 0.065:
            return 2
        elif slope < 0.08:
            return 3
        elif slope < 0.095:
            return 4
        else:
            return 5
    else:
        if slope < 0.035:
            return 1
        elif slope < 0.05:
            return 2
        elif slope < 0.065:
            return 3
        elif slope < 0.08:
            return 4
        else:
            return 5


def create_training_df(df, name, chosen=False):
    """""
    Used to make the "X" df used in the logit model training. 
    Takes the df with all the columns output by choice_set_properties.
    The name of the model to be trained the name of the model
    corresponds to the models in the file
    "logit_models/model_variabes.csv" which dictates the variables to
    include based on model name.
    """ ""

    model_list_df = pd.read_csv(
        "logit_models/model_variables.csv",
        skiprows=1,
        header=None,
        index_col=0,
        engine="python",
    )
    try:
        var_list = model_list_df.loc[name].dropna().to_list()
    except IndexError:
        print(f"{name} not in model_variables list!")
        raise
    add_list = ["user_id", "route_id"]
    if chosen:
        add_list.append("chosen")
    var_list.extend(add_list)
    X = df[var_list]
    return X


def create_standardizing_dict(X, override=None):
    """
    Takes training df X and checks which columns need to be standardized
    based on the file "logit_models/variable_distribution.csv".
    Also takes an optional override list that will ignore any column
    names that appear in this list. Outputs a dictionary that can be
    used by the 'standardize_columns' function in
    'multinomial_model.py'.
    """

    if override is None:
        override = []
    dist_df = pd.read_csv(
        "logit_models/variable_distribution.csv", header=None
    )
    var_list = X.columns.tolist()
    dist_dict = dict(zip(dist_df[0], dist_df[1]))
    dist_dict = {
        key: value
        for key, value in dist_dict.items()
        if ((key in var_list) and (key not in override))
    }
    return dist_dict


def check_infinity(list_df, index_dict):
    """
    Checks a list containing dfs if there is any infinity value in a
    cell. Prints the cyclist id where the infinity is found.
    """
    inf_df_indices = []
    for i, df in enumerate(list_df):
        # Convert all columns to numeric (to avoid type errors)
        df_numeric = df.apply(pd.to_numeric, errors="coerce")

        # Check if any infinity value exists
        if np.isinf(df_numeric.to_numpy()).any():
            inf_df_indices.append(index_dict[i])
            del list_df[i]

    # Output the indices
    print("DataFrame indices containing infinity values:", inf_df_indices)


def concat_training_data(
    directory_path="choice_properties/choice_files/",
    output_path="logit_models/model_data/",
):
    """
    Takes the filepath where the individual choice set properties csv
    files are and creates a single df of all cyclists, will return the
    df to be used but will also save it as a csv so this can only be
    called once when the choice set properties are changed, and the csv
    can be read after instead.
    """

    df_list = []
    index_dict = {}
    i = 0
    # Loop through the files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            # Construct the full path to the file
            file_path = os.path.join(directory_path, filename)

            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Extract ID from the filename (remove the .csv extension)
            # Assuming the filename is structured like 'data_1.csv',
            # we take '1' as the ID.

            # Change this based on your filename pattern
            id_number = filename.split(".")[0].split("_")[-1]

            # Add a new column 'id' to the DataFrame
            df["user_id"] = id_number
            index_dict[i] = id_number
            df["route_id"] = df.index
            i += 1
            # Append the DataFrame to the list
            df_list.append(df)

    check_infinity(df_list, index_dict)
    # Concatenate all DataFrames in the list into a single DataFrame
    final_df = pd.concat(df_list, ignore_index=True)

    final_df.dropna(inplace=True)
    final_df.to_csv(output_path + "raw_training_data.csv")
    return final_df


# TODO: make this function take arguments that set the user_id col name
# and route id col name along with certain options such as randomizing.
def idca_to_idco(df):
    """
    Converts a dataframe in idca format to idco format.

    See https://larch.newman.me/v5.7.0/user-guide/data-fundamentals.html
    """
    df_copy = df.copy()
    df_copy["route_id"] = df_copy.groupby("user_id")["route_id"].transform(
        np.random.permutation
    )

    # Assuming user_id column name contains 'user'
    user_col = [col for col in df_copy.columns if "user" in col.lower()][0]

    # Assuming route_id column name contains 'route'
    route_col = [col for col in df_copy.columns if "route" in col.lower()][0]

    df_pivot = df_copy.set_index([user_col, route_col]).unstack(route_col)

    # Flatten the columns to create new column names
    df_pivot.columns = [f"{col[0]}_{col[1]}" for col in df_pivot.columns]

    # Step 3: Get the chosen route_id for each user_id
    df_chosen_route = (
        df_copy[df_copy["chosen"] == 1].groupby(user_col)[route_col].first()
    )

    # Step 4: Drop all columns that start with 'chosen_' except 'chosen_route_id'
    chosen_columns = [
        col for col in df_pivot.columns if col.startswith("chosen_")
    ]
    df_pivot = df_pivot.drop(columns=chosen_columns)

    # Merge the chosen_route with the pivoted DataFrame
    df_pivot = df_pivot.reset_index()
    df_pivot["chosen_route_id"] = df_pivot[user_col].map(df_chosen_route)

    # Show the resulting DataFrame
    return df_pivot
