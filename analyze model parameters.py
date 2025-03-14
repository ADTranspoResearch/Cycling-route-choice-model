import joblib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit  # Multinomial Logit model


model_name = 'while_loop_test'

model = joblib.load(f"logit_models/multinomial_logit_{model_name}.pkl")

final_df = pd.read_csv(f'logit_models/model data/training_data_{model_name}.csv')
'''
X = final_df[['avg_ADT','avg_Q85',
              'avg_lts','infra_ratio','length','max_loe','max_lts', 'path_size']] 
'''
X = final_df[['avg_ADT','avg_Q85','avg_loe', 'avg_Q85_dist_w','avg_adt_dist_w', 'avg_lts_dist_w', 'avg_slope', 'max_slope',
              'avg_lts','length','max_loe','max_lts', 'path_size','infra_length','infra_ratio'
              ]]  # Replace with your actual feature names
        
y = final_df['chosen']  # Target variable (which alternative was chosen)


X['path_size'] = np.log1p(X['path_size'])
# Add an intercept column for statsmodels
X_sm = sm.add_constant(X)

# Fit multinomial logistic regression using statsmodels
mnlogit_model = MNLogit(y, X_sm)
result = mnlogit_model.fit(method='newton')

print(result.summary())
                           
# Get model coefficients
coefficients = model.coef_

# Get feature names
feature_names = X.columns




# Print the coefficients for each class
for i, class_coefs in enumerate(coefficients):
    print(f"Class {model.classes_[i]} Coefficients:")
    for feature, coef in zip(feature_names, class_coefs):
        print(f"{feature}: {coef:.4e}")
    print("\n")
    
    
corr_matrix = X.corr()

# Plot heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Feature Correlation Matrix")
plt.show()