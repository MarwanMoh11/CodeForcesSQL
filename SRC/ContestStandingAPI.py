import requests
import csv
import os
import re


# Function to read contest IDs from a file
def read_contest_ids(filename):
    contest_ids = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            contest_ids.append(row[0])  # Assumes contest ID is in the first column
    return contest_ids


# Function to fetch contest details and standings data from Codeforces API for a specific contest ID
def fetch_contest_details_and_standings(contest_id):
    # API URL for contest information
    contest_info_url = f'https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=1000'
    response = requests.get(contest_info_url)

    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            contest_name = data['result']['contest']['name']
            # Extract division from contest name using regex
            division_match = re.search(r"Div\. ?\d", contest_name)
            division = division_match.group(0) if division_match else 'N/A'
            standings = data['result']['rows']
            return contest_name, division, standings
        else:
            print(f"Error for contest {contest_id}: {data['comment']}")
            return None, None, None
    else:
        print(f"Failed to fetch data for contest {contest_id}, status code: {response.status_code}")
        return None, None, None


# Function to write standings data to CSV
def write_to_csv(contest_name, division, standings, csv_path):
    # Prepare header and rows
    header = ['Contest Name', 'Division', 'Screen Name', 'Standing']
    rows = []

    # Extract rows from standings
    for row in standings:
        standing = row.get('rank', 'N/A')
        screen_name = row['party']['members'][0]['handle']  # first team member handle
        rows.append([contest_name, division, screen_name, standing])

    # Write or append to CSV
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(header)  # Write header only if the file is new
        writer.writerows(rows)


# Main script to process multiple contests
def main():
    contest_ids = read_contest_ids('D:\Databases_project\CodeForcesSQL\CodeForces_Scraper_API\Contest.csv')
    csv_path = 'D:\Databases_project\CodeForcesSQL\CodeForces_Scraper_API\ContestStandings.csv'

    for contest_id in contest_ids:
        contest_name, division, standings = fetch_contest_details_and_standings(contest_id)
        if standings:
            write_to_csv(contest_name, division, standings, csv_path)
            print(f"Standings for contest '{contest_name}' have been written to {csv_path}")
        else:
            print(f"No data to write for contest {contest_id}")


# Run the main function
if __name__ == "__main__":
    main()
