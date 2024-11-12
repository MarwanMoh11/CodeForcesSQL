import pandas as pd

# Load the CSV files
contest_problems_df = pd.read_csv("Contest_problemSets.csv")
problem_sets_df = pd.read_csv("ProblemSets.csv")

# Merge on 'ID' to get the problem names in contest problems
merged_df = contest_problems_df.merge(problem_sets_df[['ID', ' Name']], on='ID', how='left')

# Replace 'ID' with 'Problem Name'
merged_df.rename(columns={' Name': 'Problem Name'}, inplace=True)
merged_df.drop(columns=['ID'], inplace=True)

# Save the updated dataframe to a new CSV file
merged_df.to_csv("Updated_Contest_problemSets.csv", index=False)




# Load the CSV files
problem_sets_tags_df = pd.read_csv("ProblemSets_Tags.csv")
problem_sets_df = pd.read_csv("ProblemSets.csv")

# Merge on 'ID' to get the problem names in ProblemSets_Tags
merged_df = problem_sets_tags_df.merge(problem_sets_df[['ID', ' Name']], left_on='ID', right_on='ID', how='left')

# Replace 'ID' with 'Problem Name'
merged_df.rename(columns={' Name': 'Problem Name'}, inplace=True)
merged_df.drop(columns=['ID'], inplace=True)

# Save the updated dataframe to a new CSV file
merged_df.to_csv("Updated_ProblemSets_Tags.csv", index=False)

