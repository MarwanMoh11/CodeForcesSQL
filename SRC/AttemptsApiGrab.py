import requests
import pandas as pd
from datetime import datetime

# Replace with your actual Codeforces API key and secret if required
API_KEY = "your_codeforces_api_key"
API_SECRET = "your_codeforces_api_secret"
USER_HANDLE = "user_handle"  # Codeforces user handle to filter submissions


def fetch_contest_submissions(user_handle):
    """
    Fetches submissions for a specific user handle from the Codeforces API.
    """
    url = f"https://codeforces.com/api/user.status?handle={user_handle}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch data from Codeforces API")
        return []

    data = response.json()
    if data['status'] != 'OK':
        print("Error in API response")
        return []

    return data['result']


def parse_submissions(submissions):
    """
    Parses the submissions data into the desired format.
    """
    records = []
    for submission in submissions:
        attempt_id = submission['id']
        attempt_date = datetime.fromtimestamp(submission['creationTimeSeconds']).strftime('%Y-%m-%d %H:%M:%S')
        verdict = submission.get('verdict', 'N/A')
        language = submission.get('programmingLanguage', 'N/A')
        time_ms = submission.get('timeConsumedMillis', 0)
        memory_bytes = submission.get('memoryConsumedBytes', 0)
        screen_name = submission['author']['members'][0]['handle']

        # Contest and problem information
        contest_id = submission['contestId']
        problem_name = submission['problem']['name']
        contest_name = f"Codeforces Round {contest_id}"
        division = 'Div1' if 'Div1' in problem_name else 'Div2'

        # Append record
        records.append([
            attempt_id, attempt_date, verdict, language, time_ms, memory_bytes,
            screen_name, contest_name, problem_name, division
        ])

    return records


def main():
    submissions = fetch_contest_submissions(USER_HANDLE)
    parsed_data = parse_submissions(submissions)

    # Convert to DataFrame
    columns = [
        "Attempt ID", "Attempt Date", "Verdict", "Language Used", "Attempt Time (ms)",
        "Attempt Memory (bytes)", "Screen Name", "Contest Name", "Problem Set Name", "Division"
    ]
    df = pd.DataFrame(parsed_data, columns=columns)

    # Save to CSV
    df.to_csv("codeforces_attempts.csv", index=False)
    print("Data saved to codeforces_attempts.csv")


if __name__ == "__main__":
    main()
