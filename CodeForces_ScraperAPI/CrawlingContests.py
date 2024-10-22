from selenium import webdriver
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import re
import csv

driver = uc.Chrome()
url = "https://codeforces.com/contests"
driver.get(url)
time.sleep(5)
writer_ID = 0
writers_dict = {}
contest_writer_connections = []

contests = []  # Initialize the list to collect contests

while True:
    html = driver.page_source
    doc = BeautifulSoup(html, "html.parser")
    contest_rows = doc.find_all('tr', attrs={'data-contestid': True})

    # Extract contest information
    for row in contest_rows:
        contest_id = row['data-contestid']

        # Extract contest name without "Enter" or "Virtual participation"
        contest_name_td = row.find('td', class_='left')
        contest_name = contest_name_td.contents[0].strip()  # Get the first text node directly

        contest_date = row.find_all('td')[2].get_text(strip=True)
        contest_time = row.find_all('td')[2].find_next_sibling().get_text(strip=True)

        # Adjusted to only capture numeric participant count
        participant_count_raw = row.find_all('td')[-1].get_text(strip=True)
        participant_count_match = re.search(r'\d+', participant_count_raw)

        if "Before" in participant_count_raw:
            continue
        else:
            participant_count = re.sub(r'\D', '', participant_count_raw)


        # Extract writers (participants) from the second <td>
        writers = []
        participants_td = row.find_all('td')[1]  # This contains the participants
        participant_links = participants_td.find_all('a', class_='rated-user')

        for link in participant_links:
            writer_name = link.get_text(strip=True)

            # Check if writer already has an ID
            if writer_name not in writers_dict:
                # Assign a new ID and increment
                writers_dict[writer_name] = writer_ID
                writer_ID += 1  # Increment the global writer_id

            # Get the writer's ID
            writer_id_assigned = writers_dict[writer_name]

            # Append the connection of contest ID and writer ID only
            contest_writer_connections.append([contest_id, writer_id_assigned])

        DIV = re.search(r'\((.*?)\)', contest_name)
        DIV_value = DIV.group(1) if DIV else None

        if DIV_value is not None:
            if 'Div. 1' not in DIV_value and 'Div. 2' not in DIV_value:
                continue

        contests.append({
            'contest_id': contest_id,
            'DIV' : DIV_value,
            'contest_name': contest_name,
            'contest_date': contest_date,
            'contest_time': contest_time,
            'participant_count': participant_count,
        })

    # Break condition for the loop if we reach the desired count
    inactive_arrow = doc.find('span', class_='inactive',text='→')
    if inactive_arrow:
        print("Reached the inactive pagination arrow. Breaking the loop.")
        break  # Break the loop if the inactive arrow is found

    # Find the "arrow" (next page) link using BeautifulSoup
    next_page_link = doc.find('a', class_='arrow', text='→')
    if next_page_link and 'href' in next_page_link.attrs:
        next_url = "https://codeforces.com" + next_page_link['href']
        print(f"Navigating to: {next_url}")
        driver.get(next_url)  # Navigate to the next page
        time.sleep(5)  # Wait for the next page to load

# Print the total number of contests collected
print(f"Total contests collected: {len(contests)}")

with open('contests.csv', mode='w', newline='', encoding='utf-8') as contests_file:
    contests_writer = csv.writer(contests_file)
    contests_writer.writerow(['Contest ID', 'Contest Name', 'DIV', 'Date', 'Time', 'Participants'])  # Header
    for contest in contests:
        contests_writer.writerow([
            contest['contest_id'],
            contest['contest_name'],
            contest['DIV'],
            contest['contest_date'],
            contest['contest_time'],
            contest['participant_count']
        ])

# Write writers dictionary to CSV
with open('writers.csv', mode='w', newline='', encoding='utf-8') as writers_file:
    writers_writer = csv.writer(writers_file)
    writers_writer.writerow(['Writer Name', 'Writer ID'])  # Header
    for writer_name, id in writers_dict.items():
        writers_writer.writerow([writer_name, id])

# Write contest ID and writer ID connections to CSV
with open('contest_writer_connections.csv', mode='w', newline='', encoding='utf-8') as connections_file:
    connections_writer = csv.writer(connections_file)
    connections_writer.writerow(['Contest ID', 'Writer ID'])  # Header
    for connection in contest_writer_connections:
        connections_writer.writerow(connection)

# Optionally, inform the user
print("Data has been written to CSV files: contests.csv, writers.csv, contest_writer_connections.csv")

# Quit the driver at the end
driver.quit()
