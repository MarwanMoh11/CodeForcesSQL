import pandas as pd
from collections import defaultdict
from tqdm import tqdm


contests_df = pd.read_csv("D:/Databases_project/CodeForcesSQL/CodeForces_Scraper_API/Contest.csv").head(100)
standings_df = pd.read_csv("D:/Databases_project/CodeForcesSQL/CodeForces_Scraper_API/ContestStandings.csv").head(100)



# Step 1: Create a dictionary with contest names and divisions for lookup
lookup_dict = defaultdict(list)
for _, row in contests_df.iterrows():
    contest_name = row['Contest Name']
    div = row['DIV']
    contest_id = row['Contest ID']
    lookup_dict[(contest_name, div)].append(contest_id)


# Step 2: Define function to find the exact contest ID based on both name and division
def get_contest_id(row):
    contest_name = row['Contest Name']
    division = row['Division']

    # Determine which divisions we need based on the input row
    if division == "Div1":
        needed_divs = ["Div. 1"]
    elif division == "Div2":
        needed_divs = ["Div. 2"]
    elif division == "Div1 & Div2":
        needed_divs = ["Div. 1", "Div. 2"]
    else:
        return None  # Skip if the division format is unexpected

    # Filter matches based on contest name and required divisions
    matching_ids = [
        contest_id
        for (name, div), contest_ids in lookup_dict.items()
        if name == contest_name and all(nd in div for nd in needed_divs)
        for contest_id in contest_ids
    ]

    # Return Contest ID if a unique match is found, otherwise None
    if len(set(matching_ids)) == 1:
        return matching_ids[0]
    return None  # Return None if there are no matches or multiple matches


# Apply the function and save output
tqdm.pandas()
standings_df['Contest ID'] = standings_df.progress_apply(get_contest_id, axis=1)

# Save the results
standings_df.to_csv("UpdatedContestStandings.csv", index=False)

print("Updated Contest IDs have been successfully added.")
