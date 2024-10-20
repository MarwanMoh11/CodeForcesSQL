from selenium import webdriver
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import re

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




        contests.append({
            'contest_id': contest_id,
            'DIV' : DIV_value,
            'contest_name': contest_name,
            'contest_date': contest_date,
            'contest_time': contest_time,
            'participant_count': participant_count,
        })

    # Break condition for the loop if we reach the desired count
    if len(contests) >= 200:
        break

    # Find the "arrow" (next page) link using BeautifulSoup
    next_page_link = doc.find('a', class_='arrow', text='→')
    if next_page_link and 'href' in next_page_link.attrs:
        next_url = "https://codeforces.com" + next_page_link['href']
        print(f"Navigating to: {next_url}")
        driver.get(next_url)  # Navigate to the next page
        time.sleep(5)  # Wait for the next page to load

# Print the total number of contests collected
print(f"Total contests collected: {len(contests)}")

# TABLE 1
for contest in contests:
    print(
        f"Contest ID: {contest['contest_id']}, Name: {contest['contest_name']}, "
        f"DIV: {contest['DIV']}, Date: {contest['contest_date']}, Time: {contest['contest_time']}, "
        f"Participants: {contest['participant_count']}"
    )


# Print the writers dictionary with keys
print("Writers Dictionary (Name: ID):")
for writer_name, id in writers_dict.items():
    print(f"Writer Name: {writer_name}, Writer ID: {id}")


# Print the contest ID and writer ID connections
print("\nContest ID and Writer ID Connections:")
for connection in contest_writer_connections:
    print(f"Contest ID: {connection[0]}, Writer ID: {connection[1]}")


driver.quit()
