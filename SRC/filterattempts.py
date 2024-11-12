import pandas as pd

# Load the data into a DataFrame (assuming it's in a CSV file)
df = pd.read_csv('D:/Databases_project/CodeForcesSQL/CodeForces_Scraper_API/Final_files/Finals_codeforces_attempts.csv')

# Group by 'Screen Name' and count the number of attempts per user
user_counts = df['Screen Name'].value_counts()

# Filter users with more than 100 contests
active_users = user_counts[user_counts > 100].index

# Filter the original DataFrame to only include these active users
filtered_df = df[df['Screen Name'].isin(active_users)]

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv('filtered_file_attempts.csv', index=False)

print("Filtered data has been saved to 'filtered_file.csv'")
