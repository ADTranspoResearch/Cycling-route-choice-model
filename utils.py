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