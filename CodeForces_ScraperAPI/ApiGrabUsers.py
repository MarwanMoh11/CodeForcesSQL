import requests
import csv
import time

def read_contest_ids(filename):
    contest_ids = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            contest_ids.append(row[0])  # Assumes contest ID is in the first column
    return contest_ids

def get_all_rated_handles():
    url = "https://codeforces.com/api/user.ratedList?activeOnly=false"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            return {user["handle"] for user in data["result"]}
    return set()

def get_contest_participants(contest_id, max_retries=3):
    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=5&showUnofficial=true"
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK":
                    return {row["party"]["members"][0]["handle"] for row in data["result"]["rows"]}
                else:
                    print(f"Error in API response status for contest {contest_id}")
            else:
                print(f"HTTP error {response.status_code} for contest {contest_id}")
        except (requests.RequestException, requests.JSONDecodeError):
            print(f"Attempt {attempt + 1} failed for contest {contest_id}")
            time.sleep(2)  # delay before retrying
    print(f"All attempts failed for contest {contest_id}")
    return set()

def get_recent_submission_handles(count=1000):
    url = f"https://codeforces.com/api/problemset.recentStatus?count={count}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            return {submission["author"]["members"][0]["handle"] for submission in data["result"]}
    return set()

def get_rating_change_handles(contest_id):
    url = f"https://codeforces.com/api/contest.ratingChanges?contestId={contest_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            return {change["handle"] for change in data["result"]}
    return set()

def collect_unique_handles(contest_ids, output_file):
    unique_handles = set()

    # Get handles from rated list
    unique_handles.update(get_all_rated_handles())

    # Get handles from recent submissions
    unique_handles.update(get_recent_submission_handles())

    # Use the contest IDs from the CSV file
    for i, contest_id in enumerate(contest_ids):
        print(f"Processing contest {i + 1}/{len(contest_ids)}: ID {contest_id}")
        unique_handles.update(get_contest_participants(contest_id))
        unique_handles.update(get_rating_change_handles(contest_id))
        print(f"Handles collected so far: {len(unique_handles)}")

        # Save current unique handles to the output file
        with open(output_file, 'w') as f:
            for handle in unique_handles:
                f.write(f"{handle}\n")

    return unique_handles

# Read contest IDs from uploaded file
contest_ids = read_contest_ids('D:/Databases_project/CodeForcesSQL/CodeForces_ScraperAPI/Contest.csv')

# Output file path
output_file = 'D:/Databases_project/CodeForcesSQL/CodeForces_ScraperAPI/unique_handles.txt'

# Run the collection
all_handles = collect_unique_handles(contest_ids, output_file)

print(f"Total unique handles collected: {len(all_handles)}")
