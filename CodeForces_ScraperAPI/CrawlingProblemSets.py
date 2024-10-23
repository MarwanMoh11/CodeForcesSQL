import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import concurrent.futures
import time
import logging
import re
import csv
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

problemset_id = 0
problemsets = []

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_all_problem_links(start_url):
    all_problems = []
    driver = init_driver()
    try:
        driver.get(start_url)
        while True:
            time.sleep(3)  # Short wait to ensure the page is loaded
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            problems = scrape_websiteforlinks(driver.current_url)
            all_problems.extend(problems)

            # Find the "arrow" (next page) link using BeautifulSoup
            next_page_link = soup.find('a', class_='arrow', text='→')
            if next_page_link and 'href' in next_page_link.attrs:
                next_url = "https://codeforces.com" + next_page_link['href']
                logging.info(f"Navigating to: {next_url}")
                driver.get(next_url)  # Navigate to the next page
            else:
                logging.info("Reached the end of pagination.")
                break  # Break the loop if no next page is found
    except Exception as e:
        logging.error(f"Error while navigating pages: {str(e)}")
    finally:
        driver.quit()
    return all_problems


# Function to initialize the ChromeDriver with options
def init_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")
    driver = uc.Chrome(options=options)
    return driver

def scrape_websiteforlinks(url):
    driver = None
    try:
        logging.info(f"Starting scraping for {url}")
        driver = init_driver()
        driver.set_page_load_timeout(30)  # Timeout for page load
        driver.get(url)
        time.sleep(3)  # Short wait to ensure the page is loaded
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        logging.info(f"Successfully scraped {url}")

        base_url = "https://codeforces.com"
        problems = []  # List to store problem dictionaries

        # Find all rows that may contain problem information
        for row in soup.find_all('tr'):
            # Check for the presence of an action cell
            action_cell = row.find('td', class_='act') or row.find('td', class_='act dark')
            if action_cell:
                # Extract problem link and title
                problem_id_cell = row.find('td', class_='id')
                if problem_id_cell:
                    problem_link = problem_id_cell.find('a', href=True)
                    if problem_link:
                        full_url = base_url + problem_link['href']
                        problem_title = problem_link.get_text(strip=True)

                        # Extract tags
                        tags = [tag.get_text(strip=True) for tag in row.find_all('a', class_='notice')]

                        # Append problem info to list
                        problems.append({
                            "TitleID": problem_title,
                            "url": full_url,
                            "tags": tags
                        })

        logging.info(f"Found {len(problems)} problems")
        return problems  # Return the list of problems

    except Exception as e:
        logging.error(f"Error while scraping: {str(e)}")
        return []
    finally:
        if driver:
            driver.quit()

url = "https://codeforces.com/problemset/page/54"  # Replace with the actual URL
problems = scrape_all_problem_links(url)

# Convert problems list to a dictionary
problems_dict = {problem['url']: problem for problem in problems}

# Function to scrape a single website
def scrape_website(url, max_retries=3, delay=5):
    driver = None
    try:
        logging.info(f"Starting scraping for {url}")
        driver = init_driver()
        driver.set_page_load_timeout(30)  # Timeout for page load

        for attempt in range(max_retries):
            try:
                driver.get(url)
                time.sleep(3)  # Short wait to ensure the page is loaded
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                logging.info(f"Successfully scraped {url} on attempt {attempt + 1}")
                return soup
            except (TimeoutException, WebDriverException) as e:
                logging.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                time.sleep(delay)  # Wait before retrying

        logging.error(f"Failed to scrape {url} after {max_retries} attempts")
        return None

    except Exception as e:
        logging.error(f"Error while scraping {url}: {str(e)}")
        return None
    finally:
        if driver:
            driver.quit()


def extract_problem_definition(text):
    # Regular expression to capture the problem definition
    pattern = re.compile(r'input\s+standard\s+input\s+output\s+standard\s+output(.*?)(?=Codeforces|Server time)', re.DOTALL | re.IGNORECASE)
    match = pattern.search(text)

    if match:
        extracted = match.group(1).strip()
        return extracted
    else:
        return "No match found"

def scrape_websites_concurrently(urls, max_workers=5, delay=1.5):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for url in urls:
            future = executor.submit(scrape_website, url)
            futures[future] = url
            time.sleep(delay)  # Add a delay after submitting each task
        results = []
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                data = future.result()
                if data:
                    results.append({'Data': data, 'URL': url})
            except Exception as e:
                logging.error(f"Exception occurred for {url}: {str(e)}")
    return results

def extract_problem_description(soup):
    # Remove all <script> and <style> elements
    for script in soup(["script", "style"]):
        script.extract()

    # Function to handle MathJax elements, extracting useful information
    def handle_mathjax(mathjax_element):
        # Try to retrieve the human-readable form from various MathJax sources
        possible_sources = [
            lambda: mathjax_element.find("nobr").text.strip() if mathjax_element.find("nobr") else None,
            lambda: mathjax_element.find("span", class_="MJX_Assistive_MathML").get_text(
                strip=True) if mathjax_element.find("span", class_="MJX_Assistive_MathML") else None,
            lambda: mathjax_element.get("data-mjx-tex", "").strip() or None,
            lambda: mathjax_element.get_text(separator=' ', strip=True)
        ]

        # Return the first non-None result from possible sources
        for source in possible_sources:
            result = source()
            if result:
                return result

        return ""

    # Replace MathJax spans with their contents
    for mathjax in soup.find_all("span", class_="MathJax"):
        math_text = handle_mathjax(mathjax)
        mathjax.replace_with(math_text)

    # Extract and clean the text
    text = soup.get_text(separator=' ', strip=True)

    extracted = extract_problem_definition(text)

    # Find the title
    title_div = soup.find('div', class_='title')
    title = title_div.get_text(strip=True) if title_div else None

    # Find the time limit
    time_limit_div = soup.find('div', class_='time-limit')
    time_limit = time_limit_div.find_all(string=True)[1].strip() if time_limit_div else None

    # Find the memory limit
    memory_limit_div = soup.find('div', class_='memory-limit')
    memory_limit = memory_limit_div.find_all(string=True)[1].strip() if memory_limit_div else None

    return {
        "description": extracted,
        "Name": title,
        "memory_limit": memory_limit,
        "time_limit": time_limit,
        "problemset_id": problemset_id
    }

def get_tags_by_url(problems_dict, url):
    return problems_dict.get(url, {}).get("tags", None)

def get_ID_by_url(problems_dict, url):
    return problems_dict.get(url, {}).get("TitleID", None)

# Main function to start the scraping process
if __name__ == "__main__":
    start_time = time.time()

    urls_to_scrape = [problem['url'] for problem in problems]

    # Scrape websites concurrently
    results = scrape_websites_concurrently(urls_to_scrape, max_workers=10)

    logging.info(f"Scraping completed in {time.time() - start_time} seconds")

    # Process the results and write to CSV
    try:
        with open('ProblemSetsV3.csv', mode='w', newline='', encoding='utf-8') as connections_file:
            connections_writer = csv.writer(connections_file)
            connections_writer.writerow(['ProblemID', 'Name', 'memory_limit', 'time_limit', 'Tags', 'Description'])  # Header

            for result in results:
                problem_data = extract_problem_description(result['Data'])
                connections_writer.writerow([
                    get_ID_by_url(problems_dict, result['URL']),
                    problem_data['Name'],
                    problem_data['memory_limit'],
                    problem_data['time_limit'],
                    get_tags_by_url(problems_dict, result['URL']),
                    problem_data['description']
                ])
        logging.info("Data successfully written to ProblemSets.csv")
    except Exception as e:
        logging.error(f"Error while writing to CSV: {str(e)}")