from selenium import webdriver
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import csv
import re

driver = uc.Chrome()
url = "https://codeforces.com/contests"
driver.get(url)
time.sleep(5)

contest_writer_connections = []

while True:
    html = driver.page_source
    doc = BeautifulSoup(html, "html.parser")
    contest_rows = doc.find_all('tr', attrs={'data-contestid': True})

    # Extract contest information
    for row in contest_rows:
        # Extract the contest name without "Enter" or "Virtual participation"
        contest_name_td = row.find('td', class_='left')
        contest_name_raw = contest_name_td.contents[0].strip()  # Get the first text node directly

        # Extract Division and standardize "Div. 1 + Div. 2" to "Div. 1 & Div. 2"
        division_match = re.search(r'\(?(Div\. 1(?: \+ | & )?Div\. 2|Div\. 1|Div\. 2)\)?', contest_name_raw)

        if division_match:
            division = division_match.group(1)
            # Standardizing outputs
            if "Div. 1" in division and "Div. 2" in division:
                division = "Div1 & Div2"
            elif "Div. 1" in division:
                division = "Div1"
            elif "Div. 2" in division:
                division = "Div2"
        else:
            division = "No Division"

        # Remove any parentheses and enclosed text to get a clean contest name
        contest_name = re.sub(r'\s*\(.*?\)\s*', '', contest_name_raw).strip()

        # Extract writers (participants) from the second <td>
        participants_td = row.find_all('td')[1]
        participant_links = participants_td.find_all('a', class_='rated-user')

        for link in participant_links:
            writer_name = link.get_text(strip=True)
            # Append contest name, division, and writer name connection
            contest_writer_connections.append([contest_name, division, writer_name])

    # Check for pagination end
    inactive_arrow = doc.find('span', class_='inactive', text='→')
    if inactive_arrow:
        print("Reached the last page. Exiting loop.")
        break

    # Navigate to the next page if available
    next_page_link = doc.find('a', class_='arrow', text='→')
    if next_page_link and 'href' in next_page_link.attrs:
        next_url = "https://codeforces.com" + next_page_link['href']
        print(f"Navigating to: {next_url}")
        driver.get(next_url)
        time.sleep(5)

# Write contest name, division, and writer name connections to CSV
with open('contest_writer_connections.csv', mode='w', newline='', encoding='utf-8') as connections_file:
    connections_writer = csv.writer(connections_file)
    connections_writer.writerow(['Contest Name', 'Division', 'Writer Name'])  # Header
    for connection in contest_writer_connections:
        connections_writer.writerow(connection)

# Inform the user and quit the driver
print("Contest-writer connections have been written to contest_writer_connections.csv")
driver.quit()
