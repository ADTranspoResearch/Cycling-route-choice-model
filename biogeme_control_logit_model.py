"""estimates a biogeme model for a given dataset specified in code"""
import biogeme.biogeme as bio
from biogeme.expressions import Beta, Variable
from biogeme import models
import biogeme.database as db
import pandas as pd

from utils import create_training_df, idca_to_idco, concat_training_data

MODEL_NAME = 'base_model'
# this cannot be changed yet,
# TODO: must add a line that drops columns above this value
CHOICE_SET_SIZE = 81

#concat_training_data()
full_df = pd.read_csv('logit_models/model_data/raw_training_data.csv')
final_df = create_training_df(full_df,MODEL_NAME,chosen=True)

#normalizing values
final_df['ADT_sum'].astype(float)
final_df['length'].astype(float)
final_df.loc[:,'ADT_sum']=final_df['ADT_sum']/1000
final_df.loc[:,'length']=final_df['length']/1000
wide_df = idca_to_idco(final_df)

# Get a boolean DataFrame where True indicates NaN
nan_mask = wide_df.isna()

# Find the first NaN position
nan_positions = nan_mask.stack()[nan_mask.stack()].index

for row_index, col_name in nan_positions:
    print(f"NaN found at row: {row_index}, column: '{col_name}'")
    print(f'cyclist {wide_df.loc[row_index]} ')
    print("Value at that location:", wide_df.loc[row_index, col_name])





database = db.Database('wide_data_model', wide_df)

user_id = Variable('user_id')

infra_ratio = {}
number_of_links = {}
path_size = {}
ADT_sum = {}
length = {}
avg_Q85_dist_w = {}
slope_sum = {}
for i in range(0, CHOICE_SET_SIZE):
    infra_ratio[i] = Variable(f'infra_ratio_{i}')
    number_of_links[i] = Variable(f'number_of_links_{i}')
    path_size[i] = Variable(f'path_size_{i}')
    ADT_sum[i] = Variable(f'ADT_sum_{i}')
    length[i] = Variable(f'length_{i}')
    avg_Q85_dist_w[i] = Variable(f'avg_Q85_dist_w_{i}')
    slope_sum[i] = Variable(f'slope_sum_{i}')


chosen = Variable('chosen_route_id')
#number_of_links = Variables('number_of_links']
#infra_length = Variable('infra_length')


# Define Parameters (Generic because route_id has no fixed meaning)
B_infra_ratio = Beta('B_infra_ratio', 0, None, None, 0)
B_number_of_links = Beta('B_number_of_links', 0, None, None, 0)
B_path_size = Beta('B_path_size', 0, None, None, 0)
B_length = Beta('B_length', 0, None, None, 0)
B_ADT_sum = Beta('B_ADT_sum', 0, None, None, 0)
B_avg_Q85_dist_w = Beta('B_avg_Q85_dist_w', 0, None, None, 0)
B_slope_sum = Beta('B_slope_sum', 0, None, None, 0)


V = {}
av = {}

for i in range(0, CHOICE_SET_SIZE):  # 0 to 81
    V[i] = (#B_number_of_links*number_of_links[i]
            B_length*length[i]
            + B_ADT_sum*ADT_sum[i]
            #+ B_path_size*bio.log(path_size[i])
            + B_avg_Q85_dist_w*avg_Q85_dist_w[i]
            + B_slope_sum*slope_sum[i]
            #+ B_infra_ratio * infra_ratio[i]
    )
    av[i] = 1  # All alternatives are always available

# Define the logit model
logprob = models.loglogit(V, None, chosen)
the_biogeme = bio.BIOGEME(database, logprob)

the_biogeme.modelName = "biogeme_model/base_mnl"
results = the_biogeme.estimate()

# Print Results
print(results.get_estimated_parameters())
print(results.print_general_statistics())
