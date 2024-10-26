import requests
import csv
import time
from datetime import datetime


def save_user_data_csv(user_data, filename="user_data.csv"):
    """Helper function to save user data to a CSV file."""
    with open(filename, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow([
                "UserID", "Organization", "Country", "ScreenName", "City",
                "Friends Count", "Num Contributions", "Reg Duration", "Problems Solved", "Days In Row"
            ])
        writer.writerow(user_data)


def fetch_user_info(handle):
    """Fetch user information from the Codeforces API."""
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        if data["status"] == "OK":
            user = data["result"][0]
            registration_time = user.get("registrationTimeSeconds")
            reg_duration = calculate_registration_duration(registration_time) if registration_time else 0
            return {
                "UserID": user["handle"],
                "Organization": user.get("organization"),
                "Country": user.get("country"),
                "ScreenName": user["handle"],
                "City": user.get("city"),
                "Friends Count": user.get("friendOfCount", 0),
                "Num Contributions": user.get("contribution", 0),
                "Reg Duration": reg_duration,
            }
    except requests.RequestException as e:
        print(f"Failed to retrieve user info for {handle}: {e}")
    except KeyError:
        print(f"Unexpected data format in user info for {handle}")
    return None


def calculate_registration_duration(registration_time):
    """Calculate registration duration in days."""
    registration_date = datetime.fromtimestamp(registration_time)
    current_date = datetime.now()
    return (current_date - registration_date).days


def fetch_problems_solved_and_days_in_row(handle):
    """Fetch problem-solving information and calculate streaks."""
    url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=10000"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK":
            submissions = data["result"]
            solved_problems = set()
            active_days = set()
            ok_count = 0  # Initialize OK verdict counter

            for submission in submissions:
                if submission["verdict"] == "OK":
                    ok_count += 1  # Increment OK verdict counter

                # Track activity by unique days
                submission_date = datetime.fromtimestamp(submission["creationTimeSeconds"]).date()
                active_days.add(submission_date)

            days_in_row = calculate_days_in_row(active_days)
            return ok_count, days_in_row
    except requests.RequestException as e:
        print(f"Failed to retrieve problem data for {handle}: {e}")

    return 0, 0  # Return 0 for OK count if there's an error


def calculate_days_in_row(active_days):
    """Calculate consecutive active days."""
    sorted_days = sorted(active_days)
    max_streak = current_streak = 1

    for i in range(1, len(sorted_days)):
        if (sorted_days[i] - sorted_days[i - 1]).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    return max_streak


def populate_user_data(handles):
    """Main function to populate data for each user handle."""
    for handle in handles:
        print(f"Processing user: {handle}")

        user_info = fetch_user_info(handle)
        if not user_info:
            print(f"Skipping {handle} due to missing user info.")
            continue

        user_info["Problems Solved"], user_info["Days In Row"] = fetch_problems_solved_and_days_in_row(handle)

        # Save data incrementally to CSV
        save_user_data_csv(list(user_info.values()))
        print(f"Saved data for {handle}")

        # Rate limiting to avoid API overload
        time.sleep(2)


def read_handles_from_file(filename):
    """Read user handles from a file."""
    with open(filename, "r", encoding="utf-8") as f:
        handles = f.read().strip().splitlines()  # Read and split by new lines
    return handles


# Main execution
handles_file = "unique_handles.txt"  # File containing user handles
user_handles = read_handles_from_file(handles_file)
populate_user_data(user_handles)
