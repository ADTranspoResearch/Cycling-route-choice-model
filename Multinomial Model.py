import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import os
import joblib
import matplotlib.pyplot as plt
from utils import *
import numpy as np


directory_path = 'choice_properties/'
model_path = 'logit_models/'
training_path = 'logit_models/model_data/'
check_dir(model_path)
check_dir(training_path)
model_name = 'index_model'

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
                df_copy[col] = np.log1p(df_copy[col])
                                
            else:
                raise ValueError(f"Unknown distribution type: {dist}")
    
    return df_copy

final_df = concat_training_data()

X = create_training_df(final_df,model_name)



##lts and LOE model
#X = final_df[['length','infra_ratio','infra_length','path_size','number_of_links','loe_index_sum','loe_dist_w_sum','loe_index_avg_dist_w','lts_sum','lts_dist_w_sum',
#              ]]  # Replace with your actual feature names

standard_dict = create_standardizing_dict(X)
standardize_columns(X, standard_dict)



y = final_df['chosen']  # Target variable (which alternative was chosen)





#distribution_hist(X,'index_model')


#starting work on running multiple models and comparing outputs
training_dict = {model_name:X}
model_score_dict = {}

one_model = False
test_name = 'base_model'
for name, Xdata in training_dict.items():
    if one_model:
        if name != test_name:
            continue
    training_data = Xdata.copy()
    training_data['chosen']=y
    training_data.to_csv((training_path+f'training_data_{name}.csv'))

    X_train, X_test, y_train, y_test = train_test_split(Xdata, y, test_size=0.2, random_state=42)

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

    model_score_dict[name] = classification_report(y_test, y_pred, output_dict=True)

    joblib.dump(model,model_path+f"multinomial_logit_{model_name}.pkl")
    if one_model:
        break
print(model_score_dict)
