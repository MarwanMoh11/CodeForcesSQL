import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed


def convert_to_days(time_period, num_str):
    if 'years' in time_period or 'year' in time_period:
        return int(num_str) * 365
    elif 'months' in time_period or 'month' in time_period:
        return int(num_str) * 30
    else:
        return int(num_str)


def fetch_data(handle, session):
    main_url = f"https://codeforces.com/profile/{handle}"

    # Make a request to the URL
    response = session.get(main_url)

    # Check for 403 Forbidden error and retry with a different User-Agent
    if response.status_code == 403:
        print(f"403 Forbidden error for {handle}, trying again with a different User-Agent...")
        session.headers.update({"User-Agent": random.choice(user_agents)})
        response = session.get(main_url)

    # Check if the response was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract data
        screen_name = soup.find(class_='main-info').find('h1').text.strip() if soup.find(class_='main-info') else ""
        city, country, organisation = "", "", ""
        contribution, num_of_friends, reg_duration, problems_solved, days_in_row = 0, 0, 0, 0, 0

        # Extract location info (City and Country)
        try:
            city_div = soup.find(class_='main-info').find_all('div')[1]
            city = city_div.find('a').text.strip()
            country = city_div.find_all('a')[1].text.strip()
        except (AttributeError, IndexError):
            pass

        # Extract Organisation
        try:
            organisation = soup.find(class_='main-info').find_all('div')[1].find_all('div')[1].find('a').text.strip()
        except (AttributeError, IndexError):
            pass

        # Extract Contributions
        try:
            contributions = soup.find(class_='info').find_all('li')
            contribution = next(
                int(item.find('span').text.strip()) for item in contributions if "Contribution" in item.text)
        except (AttributeError, IndexError, ValueError, StopIteration):
            pass

        # Extract Number of Friends
        try:
            friends = soup.find(class_='info').find_all('li')
            num_of_friends = next(
                int(''.join(filter(str.isdigit, item.text))) for item in friends if "Friend of" in item.text)
        except (AttributeError, IndexError, StopIteration):
            pass

        # Extract Registration Duration
        try:
            reg_duration_text = soup.find_all('span', class_='format-humantime')[1].text.strip()
            number = ''.join(filter(str.isdigit, reg_duration_text))
            reg_duration = convert_to_days(reg_duration_text, number)
        except (AttributeError, IndexError):
            pass

        # Extract Problems Solved
        try:
            problems_solved = int(
                ''.join(filter(str.isdigit, soup.find(class_='_UserActivityFrame_counterValue').text.strip())))
        except AttributeError:
            pass

        # Extract Days in Row
        try:
            days_in_row = int(
                ''.join(filter(str.isdigit, soup.find_all(class_='_UserActivityFrame_counterValue')[3].text.strip())))
        except (AttributeError, IndexError):
            pass

        # Return the collected data
        return [screen_name, city, country, organisation, contribution, num_of_friends, reg_duration, problems_solved,
                days_in_row]
    else:
        print(f"Failed to fetch data for {handle}. Status code: {response.status_code}")
        return None


def main(start_index=0):
    global user_agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0.2 Safari/605.1.15",
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Ubuntu 20.04; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 12; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Mobile Safari/537.36"
    ]

    # Read user handles from file
    with open("unique_handles.txt", "r") as file:
        handles = [line.strip() for line in file]

    # Start from the specified index
    handles_to_process = handles[start_index:]

    # Prepare the CSV file for writing
    csv_file = 'contestants_data.csv'

    # Use a session to maintain connection and improve performance
    with requests.Session() as session:
        session.headers.update({"User-Agent": random.choice(user_agents)})

        with open(csv_file, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write the header only if the file is empty
            if os.stat(csv_file).st_size == 0:
                writer.writerow(
                    ["ScreenName", "City", "Country", "Organisation", "Contribution", "NumOfFriends", "RegDuration",
                     "ProblemsSolved", "DaysInRow"])

            results = []
            row_count = 0  # Counter for rows written

            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_handle = {executor.submit(fetch_data, handle, session): handle for handle in
                                    handles_to_process}

                for future in as_completed(future_to_handle):
                    handle = future_to_handle[future]
                    data = future.result()  # Get the result without handling exceptions
                    if data:
                        writer.writerow(data)  # Write to file row by row
                        row_count += 1  # Increment row count
                        print(f"Row {row_count}: Data for {handle} written: {data}")
                    else:
                        print(f"No data returned for {handle}.")

                    # Introduce a random delay to avoid being flagged for rapid requests
                    time.sleep(random.uniform(1, 3))  # Delay between 1 to 3 seconds

    # Print the row number of the last handle processed
    print(f"The row number of the last handle processed: {row_count}")


if __name__ == "__main__":
    start_index = int(input("Enter the starting index: "))  # Get starting index from user
    main(start_index)
