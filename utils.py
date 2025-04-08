import os
import pandas as pd

def check_dir(path):
    # Check if the directory exists
    if not os.path.exists(path):
        # Create the directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{path}' created.")
    else:
        print(f"Directory '{path}' already exists.")

def level_of_effort(slope, length): #given a slope and length of a link, what is the level of effort according to scale from 'Slope stress criteria as a complement to traffic stress criteria, and impact on high comfort bicycle accessibility'
    loe = 0
    if length<150:
        if slope<0.065:
            return 1
        elif slope<0.08:
            return 2
        elif slope<0.095:
            return 3
        elif slope<0.11:
            return 4
        else:
            return 5
    elif length<500:
        if slope<0.05:
            return 1
        elif slope<0.065:
            return 2
        elif slope<0.08:
            return 3
        elif slope<0.095:
            return 4
        else:
            return 5
    else:
        if slope<0.035:
            return 1
        elif slope<0.05:
            return 2
        elif slope<0.065:
            return 3
        elif slope<0.08:
            return 4
        else:
            return 5
"""""
used to make the "X" df used in the logit model training. 
Takes the df with all the columns output by choice_set_properties, and the name of the model to be trained
the name of the model corresponds to the models in the file "logit_models/model_variabes.csv" which dictates what variables to include based on model name

"""""
def create_training_df(df, name):

    model_list_df = pd.read_csv('logit_models/model_variables.csv',skiprows=1, header=None, index_col=0, engine='python')
    try:
        var_list = model_list_df.loc[name].dropna().to_list()
    except IndexError:
        print(f'{name} not in model_variables list!')
        raise
    add_list = ['user_id','route_id']
    var_list.extend(add_list)
    X = df[var_list]
    return X

"""""
takes the training df X and checks which columns need to be standardized based on the file "logit_models/variable_distribution.csv"
also takes an optional override list that will ignore any column names that appear in this list
outputs a dictionary that can be used by the 'standardize_columns' function in 'multinomial_model.py'
"""""
def create_standardizing_dict(X, override=[]):
    dist_df = pd.read_csv('logit_models/variable_distribution.csv', header=None)
    var_list = X.columns.tolist()
    dist_dict = dict(zip(dist_df[0],dist_df[1]))
    dist_dict = {key: value for key, value in dist_dict.items() if ((key in var_list) and (key not in override))}
    return dist_dict

def check_infinity(list_df): #used by concat_training_data
    inf_df_indices = []
    for i, df in enumerate(list_df):
        # Convert all columns to numeric (to avoid type errors)
        df_numeric = df.apply(pd.to_numeric, errors='coerce')

        # Check if any infinity value exists
        if np.isinf(df_numeric.to_numpy()).any():
            inf_df_indices.append(index_dict[i])
            del list_df[i]

    # Output the indices
    print("DataFrame indices containing infinity values:", inf_df_indices)


def concat_training_data(directory_path='choice_properties/',output_path='logit_models/model_data/'): #takes the filepath where the individual choice set properties csv files are and creates a single df of all cyclists, will return the df to be used but will also save it as a csv so this can only be called once when the choice set properties are changed, and the csv can be read after instead
    df_list = []
    index_dict = {}
    i = 0
    # Loop through the files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            # Construct the full path to the file
            file_path = os.path.join(directory_path, filename)
            
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            
            # Extract the ID from the filename (remove the .csv extension)
            # Assuming the filename is structured like 'data_1.csv', we take '1' as the ID
            id_number = filename.split('.')[0].split('_')[-1]  # Change this based on your filename pattern
            
            # Add a new column 'id' to the DataFrame
            df['user_id'] = id_number
            index_dict[i]=id_number
            df['route_id']=df.index
            i+=1
            # Append the DataFrame to the list
            df_list.append(df)
       
    check_infinity(df_list)
    # Concatenate all DataFrames in the list into a single DataFrame
    final_df = pd.concat(df_list, ignore_index=True)

    final_df.dropna(inplace=True)
    final_df.to_csv(output_path+'raw_training_data.csv')
    return final_df