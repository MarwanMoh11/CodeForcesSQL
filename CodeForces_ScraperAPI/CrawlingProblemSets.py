import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import concurrent.futures
import time
import logging
import csv
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_driver():
    """Initialize ChromeDriver with specific options."""
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")
    return uc.Chrome(options=options)

def scrape_all_problem_links(start_url):
    """Scrape all problem links from the given starting URL."""
    all_problems = []
    driver = init_driver()
    try:
        driver.get(start_url)
        while True:
            time.sleep(3)  # Wait for page to load
            problems = scrape_website_for_links(driver.current_url)
            all_problems.extend(problems)
            break

            # Check for next page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            next_page_link = soup.find('a', class_='arrow', text='→')
            if next_page_link and 'href' in next_page_link.attrs:
                next_url = "https://codeforces.com" + next_page_link['href']
                logging.info(f"Navigating to: {next_url}")
                driver.get(next_url)
            else:
                logging.info("Reached the end of pagination.")
                break
    except Exception as e:
        logging.error(f"Error while navigating pages: {str(e)}")
    finally:
        driver.quit()
    return all_problems

def scrape_website_for_links(url):
    """Scrape the problem links and metadata from the given URL."""
    problems = []
    driver = init_driver()
    try:
        logging.info(f"Starting scraping for {url}")
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(3)  # Short wait to ensure the page is loaded
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        logging.info(f"Successfully scraped {url}")

        base_url = "https://codeforces.com"

        for row in soup.find_all('tr'):
            action_cell = row.find('td', class_='act') or row.find('td', class_='act dark')
            if action_cell:
                problem_id_cell = row.find('td', class_='id')
                if problem_id_cell:
                    problem_link = problem_id_cell.find('a', href=True)
                    if problem_link:
                        full_url = base_url + problem_link['href']
                        problem_title = problem_link.get_text(strip=True)
                        tags = [tag.get_text(strip=True) for tag in row.find_all('a', class_='notice')]
                        problems.append({"TitleID": problem_title, "url": full_url, "tags": tags})

        logging.info(f"Found {len(problems)} problems")
        return problems

    except Exception as e:
        logging.error(f"Error while scraping: {str(e)}")
        return []
    finally:
        driver.quit()

def scrape_website(url, max_retries=5, delay=3):
    """Scrape a single website with retry logic."""
    time.sleep(1)  # Delay before starting to avoid conflicts
    driver = init_driver()
    try:
        logging.info(f"Starting scraping for {url}")
        driver.set_page_load_timeout(30)

        for attempt in range(max_retries):
            try:
                driver.get(url)
                time.sleep(3)  # Wait for page to load
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                logging.info(f"Successfully scraped {url} on attempt {attempt + 1}")
                return soup
            except (TimeoutException, WebDriverException) as e:
                logging.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                time.sleep(delay)

        logging.error(f"Failed to scrape {url} after {max_retries} attempts")
        return None

    except Exception as e:
        logging.error(f"Error while scraping {url}: {str(e)}")
        return None
    finally:
        driver.quit()

def scrape_websites_concurrently(urls, max_workers=5, delay=1.5):
    """Scrape multiple websites concurrently."""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape_website, url): url for url in urls}
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
    """Extract the problem description and other details from the soup object."""
    for script in soup(["script", "style"]):
        script.extract()

    def handle_mathjax(mathjax_element):
        possible_sources = [
            lambda: mathjax_element.find("nobr").text.strip() if mathjax_element.find("nobr") else None,
            lambda: mathjax_element.find("span", class_="MJX_Assistive_MathML").get_text(strip=True) if mathjax_element.find("span", class_="MJX_Assistive_MathML") else None,
            lambda: mathjax_element.get("data-mjx-tex", "").strip() or None,
            lambda: mathjax_element.get_text(separator=' ', strip=True)
        ]
        for source in possible_sources:
            result = source()
            if result:
                return result
        return ""

    for mathjax in soup.find_all("span", class_="MathJax"):
        math_text = handle_mathjax(mathjax)
        mathjax.replace_with(math_text)

    input_spec = extract_specification(soup, 'input-specification')
    output_spec = extract_specification(soup, 'output-specification')
    description_text = extract_description(soup, input_spec)

    title = soup.find('div', class_='title').get_text(strip=True) if soup.find('div', class_='title') else None
    time_limit = extract_limit(soup, 'time-limit')
    memory_limit = extract_limit(soup, 'memory-limit')

    return {
        "description": description_text,
        "Input": input_spec,
        "Output": output_spec,
        "Name": title,
        "memory_limit": digitify(memory_limit),
        "time_limit": digitify(time_limit)
    }

def extract_specification(soup, class_name):
    """Extract input/output specifications from the soup."""
    spec_elem = soup.find(class_=class_name)
    return " ".join([p.text.strip() for p in spec_elem.find_all('p')]) if spec_elem else "NULL"

def extract_description(soup, input_spec):
    """Extract the problem description, stopping at input specification."""
    description = []
    problem_statement = soup.find('div', class_='problem-statement')
    if problem_statement:
        for para in problem_statement.find_all('p'):
            if para.text in (input_spec or ""):
                break
            description.append(para.text.strip())
    return " ".join(description) if description else "NULL"

def extract_limit(soup, class_name):
    """Extract time or memory limit from the soup."""
    limit_div = soup.find('div', class_=class_name)
    return limit_div.find_all(string=True)[1].strip() if limit_div else None

def digitify(s):
    """Extract digits from a string."""
    return ''.join([char for char in s if char.isdigit()])

def get_tags_by_url(problems_dict, url):
    """Retrieve tags for a given problem URL."""
    return problems_dict.get(url, {}).get("tags", [])

def get_id_by_url(problems_dict, url):
    """Retrieve problem ID by URL."""
    return problems_dict.get(url, {}).get("TitleID", None)

def write_problem_tags_to_csv(problems_dict, results, output_file='ProblemsTags.csv'):
    """Write problem tags to a CSV file."""
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as tags_file:
            tags_writer = csv.writer(tags_file)
            tags_writer.writerow(['ProblemID', 'TAG'])  # Header
            for result in results:
                problem_id = get_id_by_url(problems_dict, result['URL'])
                tags = get_tags_by_url(problems_dict, result['URL']) or []
                for tag in tags:
                    tags_writer.writerow([problem_id, tag])
        logging.info(f"Tags successfully written to {output_file}")
    except Exception as e:
        logging.error(f"Error while writing to {output_file}: {str(e)}")

def write_results_to_csv(problems_dict, results, output_file='ProblemSetsV3.csv'):
    """Write the main results to a CSV file."""
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as connections_file:
            connections_writer = csv.writer(connections_file)
            connections_writer.writerow(['ProblemID', 'Name', 'memory_limit', 'time_limit', 'Tags', 'Description', 'Input', 'Output'])  # Header

            for result in results:
                problem_data = extract_problem_description(result['Data'])
                connections_writer.writerow([
                    get_id_by_url(problems_dict, result['URL']),
                    problem_data['Name'],
                    problem_data['memory_limit'],
                    problem_data['time_limit'],
                    ", ".join(get_tags_by_url(problems_dict, result['URL']) or []),
                    problem_data['description'],
                    problem_data['Input'],
                    problem_data['Output']
                ])
        logging.info("Data successfully written to ProblemSetsV3.csv")
    except Exception as e:
        logging.error(f"Error while writing to CSV: {str(e)}")

if __name__ == "__main__":
    start_time = time.time()
    url = "https://codeforces.com/problemset"  # Replace with the actual URL
    problems = scrape_all_problem_links(url)

    problems_dict = {problem['url']: problem for problem in problems}
    urls_to_scrape = [problem['url'] for problem in problems]

    # Scrape websites concurrently
    results = scrape_websites_concurrently(urls_to_scrape, max_workers=10)

    logging.info(f"Scraping completed in {time.time() - start_time} seconds")

    # Process the results and write to CSV
    write_results_to_csv(problems_dict, results)

    # Write problem tags to a separate CSV file
    write_problem_tags_to_csv(problems_dict, results)
