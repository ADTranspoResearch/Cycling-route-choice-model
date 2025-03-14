import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import os
import joblib
import matplotlib.pyplot as plt
from utils import *
import numpy as np


directory_path = 'choice_properties/'
model_path = 'logit_models/'
training_path = 'logit_models/model data/'
check_dir(model_path)
check_dir(training_path)
model_name = 'while_loop_test'

def distribution_hist(df, output_folder ):
    
    for col in df.columns:
        plt.figure(figsize=(8, 6))  
        plt.hist(df[col].dropna(), bins=20, color='skyblue', edgecolor='black')  
        plt.title(f'Histogram of {col}')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        
        filepath = f'visualization/{output_folder}/'
        check_dir(filepath)
        file_name = filepath+f"{col}_histogram.png"
        plt.savefig(file_name)
        plt.close() 

def standardize_columns(df, col_dict): # takes a dict of column names, where the key are column names and values are desired distributions, and standardizes each column, returning the modified df
    df_copy = df.copy()
    
    for col, dist in col_dict.items():
        if col in df_copy.columns:
            if dist == 'normal':
                # Standardize column using a normal distribution (mean=0, std=1)
                mean =df_copy[col].mean()
                std =df_copy[col].std()
                df_copy[col] =(df_copy[col]-mean)/std
            elif dist =='max-min':
                # Min-Max scaling (rescale between 0 and 1)
                min_val =df_copy[col].min()
                max_val =df_copy[col].max()
                df_copy[col] =(df_copy[col]-min_val)/(max_val-min_val)
            elif dist =='pareto':
                df_copy[col] = np.log1p(df_copy[col]+0.0000001)
                                
            else:
                raise ValueError(f"Unknown distribution type: {dist}")
    
    return df_copy

def check_infinity(list_df):
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
        i+=1
        # Append the DataFrame to the list
        df_list.append(df)


#checking infinity problem
check_infinity(df_list)
check_infinity(df_list)


# Concatenate all DataFrames in the list into a single DataFrame
final_df = pd.concat(df_list, ignore_index=True)

# Display the first few rows of the final DataFrame
print(final_df.head())



X = final_df[['avg_ADT','avg_Q85','avg_loe', 'avg_Q85_dist_w','avg_adt_dist_w',  'avg_slope', 'max_slope', #'avg_lts_dist_w',
              'length','max_loe','max_lts', 'path_size','infra_length','infra_ratio'#,'avg_lts'
              ]]  # Replace with your actual feature names
y = final_df['chosen']  # Target variable (which alternative was chosen)


#print(X['avg_lts_dist_w'].mean)

standardize_columns(X, {'avg_ADT':'normal', 'avg_loe':'normal','avg_slope':'normal', 'infra_ratio':'pareto','length':'pareto','infra_length':'max-min','avg_Q85':'max-min'})
#distribution_hist(X,'while_loop')


#todo: checkdir
final_df.to_csv((training_path+f'training_data_{model_name}.csv'))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# Create the logistic regression model with multinomial option
model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=5000)

# Fit the model on the training data
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Optionally, get the predicted probabilities for each class
y_prob = model.predict_proba(X_test)

# Print classification report
print(classification_report(y_test, y_pred))

# Print confusion matrix
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

joblib.dump(model,model_path+f"multinomial_logit_{model_name}.pkl")