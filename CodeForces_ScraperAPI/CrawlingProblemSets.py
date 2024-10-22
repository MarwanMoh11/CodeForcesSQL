import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import concurrent.futures
import time
import logging
import csv
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

from CrawlingContests import contest_writer_connections

problemsetid = -1
problemsets = []

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

        # Find all problem links
        base_url = "https://codeforces.com"
        problem_links = []

        # Extract all links with class 'id left' (which contains the problem URLs)
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            if "/problemset/problem/" in href:  # Look for problem links
                full_url = base_url + href
                problem_links.append(full_url)

        logging.info(f"Found {len(problem_links)} problem links")
        return problem_links

    except TimeoutException:
        logging.error(f"TimeoutException while loading {url}")
        return []
    except WebDriverException as e:
        logging.error(f"WebDriverException for {url}: {str(e)}")
        return []
    finally:
        if driver:
            driver.quit()

# Function to scrape a single website
def scrape_website(url):
    driver = None
    try:
        logging.info(f"Starting scraping for {url}")
        driver = init_driver()
        driver.set_page_load_timeout(30)  # Timeout for page load
        driver.get(url)
        time.sleep(3)  # Short wait to ensure the page is loaded
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        logging.info(f"Successfully scraped {url}")
        return soup  # Return the soup object instead of prettified HTML
    except TimeoutException:
        logging.error(f"TimeoutException while loading {url}")
    except WebDriverException as e:
        logging.error(f"WebDriverException for {url}: {str(e)}")
    finally:
        if driver:
            driver.quit()

# Function to scrape multiple websites concurrently
def scrape_websites_concurrently(urls, max_workers=5):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape_website, url): url for url in urls}
        results = []
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                data = future.result()
                if data:
                    results.append(data)
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

    extracted = text[1090:len(text) - 234]

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
        "title": title,
        "memory_limit": memory_limit,
        "time_limit": time_limit,
        "problemset_id": problemsetid + 1
    }

urls_to_scrape = ["https://codeforces.com/problemset/problem/2030/G2"]



 # urls_to_scrape = scrape_websiteforlinks("https://codeforces.com/problemset")

# Main function to start the scraping process
if __name__ == "__main__":
    start_time = time.time()

    # Scrape websites concurrently
    results = scrape_websites_concurrently(urls_to_scrape, max_workers=10)

    logging.info(f"Scraping completed in {time.time() - start_time} seconds")

    # Process the results
    for result in results:
        problemsets.append(extract_problem_description(result))  # Extract description directly from soup object

        # Write contest ID and writer ID connections to CSV
        with open('ProblemSets.csv', mode='w', newline='', encoding='utf-8') as connections_file:
            connections_writer = csv.writer(connections_file)
            connections_writer.writerow(['description', 'title' , 'memory_limit', 'time_limit', 'problemset_id'])  # Header
            for connection in contest_writer_connections:
                connections_writer.writerow(connection)