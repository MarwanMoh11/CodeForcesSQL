import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import concurrent.futures
import time
import logging
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

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
        return soup.prettify()
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


# Example URLs to scrape
urls_to_scrape = [
    'https://codeforces.com/problemset',
    # Add more URLs here
]

# Main function to start the scraping process
if __name__ == "__main__":
    start_time = time.time()

    # Scrape websites concurrently, adjust max_workers as needed
    results = scrape_websites_concurrently(urls_to_scrape, max_workers=10)

    logging.info(f"Scraping completed in {time.time() - start_time} seconds")

    # Process the results (e.g., save to a file or database)
    for result in results:
        print(result)
