import pandas as pd
import os

folder_path = 'csv_folder'

file_list = os.listdir(folder_path)

combined_df = pd.DataFrame()

# Iterate through each file in the folder
for file_name in file_list:
    if file_name.endswith('.csv'):
        df = pd.read_csv(os.path.join(folder_path, file_name))
        combined_df = pd.concat([combined_df, df])

averages_df = combined_df.groupby('filename').mean().reset_index()

averages_df.to_csv('combined_file_with_averages.csv', index=False)

print("New CSV file 'combined_file_with_averages.csv' has been created with combined data and averages.")