from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys
import time
import json
import sqlite3
import logging

# ------------------- Logging Configuration -------------------
logging.basicConfig(
    filename='trade_scraper.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# --------------------------------------------------------------

def get_trade_links(db_path='urls.db'):
    """
    Fetches trade URLs from the SQLite database.

    Parameters:
        db_path (str): Path to the SQLite database file.

    Returns:
        list: A list of URLs extracted from the database.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT url FROM extracted_data')
        rows = cursor.fetchall()
        links = [row[0] for row in rows if row[0]]  # Ensure URL is not None or empty
        conn.close()
        logging.info(f"Fetched {len(links)} URLs from the database.")
        print(f"Fetched {len(links)} URLs from the database.")
        return links
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        print(f"Database error: {e}")
        return []

def save_all_data_to_json(all_data, run_epoch, json_dir='data_files'):
    """
    Saves all extracted data to a single JSON file named with the run's epoch time.

    Parameters:
        all_data (list): A list of dictionaries containing all extracted data.
        run_epoch (int): The epoch Unix time when the script started.
        json_dir (str): Directory where the JSON file will be saved.
    """
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_dir = os.path.join(script_dir, json_dir)

        # Ensure the directory exists
        os.makedirs(json_dir, exist_ok=True)

        # Generate filename using run epoch time
        filename = f"exchange_data_{run_epoch}.json"
        filepath = os.path.join(json_dir, filename)

        # Print absolute path for debugging
        absolute_filepath = os.path.abspath(filepath)
        print(f"Saving JSON to: {absolute_filepath}")
        logging.info(f"Saving JSON to: {absolute_filepath}")

        # Write all data to the JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)

        # Confirm file was created
        if os.path.exists(filepath):
            logging.info(f"All data successfully saved to '{absolute_filepath}'.")
            print(f"All data successfully saved to '{absolute_filepath}'.")
        else:
            logging.error(f"JSON file '{absolute_filepath}' was not created.")
            print(f"JSON file '{absolute_filepath}' was not created.")
    except Exception as e:
        logging.error(f"Failed to write all data to JSON file: {e}")
        print(f"Failed to write all data to JSON file: {e}")

def test_file_writing(json_dir='data_files'):
    """
    Tests whether the script can write to the specified JSON directory.

    Parameters:
        json_dir (str): Directory where the test JSON file will be saved.
    """
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_dir = os.path.join(script_dir, json_dir)
        os.makedirs(json_dir, exist_ok=True)
        
        test_filename = "test_write.json"
        test_filepath = os.path.join(json_dir, test_filename)
        absolute_test_filepath = os.path.abspath(test_filepath)
        
        test_data = {"test": "This is a test."}
        
        with open(test_filepath, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=4)
        
        if os.path.exists(test_filepath):
            print(f"Test JSON file successfully created at '{absolute_test_filepath}'.")
            logging.info(f"Test JSON file successfully created at '{absolute_test_filepath}'.")
            # Optionally, remove the test file after confirmation
            os.remove(test_filepath)
            print("Test JSON file removed after confirmation.")
            logging.info("Test JSON file removed after confirmation.")
        else:
            print(f"Failed to create test JSON file at '{absolute_test_filepath}'.")
            logging.error(f"Failed to create test JSON file at '{absolute_test_filepath}'.")
    except Exception as e:
        print(f"An error occurred during the test file writing: {e}")
        logging.error(f"An error occurred during the test file writing: {e}")

def main():
    # Optional: Uncomment the line below to perform a test file write before starting
    # test_file_writing()

    # Capture the script's start time in epoch Unix time (seconds)
    run_epoch = int(time.time())
    logging.info(f"Script started at epoch time: {run_epoch}")
    print(f"Script started at epoch time: {run_epoch}")

    # Determine Chrome user data directory based on OS
    if sys.platform.startswith('win'):
        user_data_dir = os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data')
    elif sys.platform.startswith('darwin'):
        user_data_dir = os.path.expanduser('~/Library/Application Support/Google/Chrome')
    elif sys.platform.startswith('linux'):
        user_data_dir = os.path.expanduser('~/.config/google-chrome')
    else:
        logging.error("Unsupported operating system")
        print("Unsupported operating system")
        raise Exception("Unsupported operating system")

    profile = "Profile 1"  # Change to your dedicated profile

    # Fetch URLs from the database
    urls = get_trade_links()
    if not urls:
        logging.info("No URLs found in the database. Exiting.")
        print("No URLs found in the database. Exiting.")
        return

    # Configure Chrome options
    options = Options()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f'--profile-directory={profile}')
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless")  # Uncomment for headless mode

    # Initialize WebDriver
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        logging.info("WebDriver initialized successfully.")
        print("WebDriver initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        print(f"Failed to initialize WebDriver: {e}")
        return

    all_data = []  # To accumulate data from all URLs

    try:
        for idx, url in enumerate(urls, 1):
            print(f"\nProcessing URL {idx}/{len(urls)}: {url}")
            logging.info(f"Processing URL {idx}/{len(urls)}: {url}")
            try:
                driver.get(url)
                logging.info(f"Navigated to URL: {url}")
                print(f"Navigated to URL: {url}")

                # Wait until the search button is clickable
                WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@class="btn search-btn"]'))
                )
                logging.info("Search button is clickable.")
                print("Search button is clickable.")

                # Wait for the exchange containers to load
                WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//*[@class="row exchange"]'))
                )
                logging.info("Exchange containers are present.")
                print("Exchange containers are present.")

                time.sleep(2)  # Additional wait if necessary

                # Extract exchange containers
                containers = driver.find_elements(By.XPATH, '//*[@class="row exchange"]')
                if not containers:
                    logging.warning(f"No exchange containers found for URL {url}")
                    print(f"No exchange containers found for URL {url}")
                    continue  # Skip to the next URL

                data = []
                for i, c in enumerate(containers, 1):
                    try:
                        # Extract "What You Get" details
                        what_get_elements = c.find_elements(By.XPATH, './/*[@class="price-block"]')
                        what_get = ' | '.join(e.text.strip() for e in what_get_elements if e.text.strip())

                        # Extract "What You Pay" details
                        what_pay_elements = c.find_elements(By.XPATH, './/*[@class="price-block s"]')
                        what_pay = ' | '.join(e.text.strip() for e in what_pay_elements if e.text.strip())

                        # Extract Profile Link
                        link_elements = c.find_elements(By.XPATH, './/*[@class="pull-right"]//*[@class="profile-link"]//a')
                        link = link_elements[0].get_attribute('href') if link_elements else "N/A"

                        # Extract Items in Stock
                        stock_elements = c.find_elements(By.XPATH, './/div[@class="stock s"]/span[1]')
                        stock_text = stock_elements[0].text.strip() if stock_elements else "0"
                        try:
                            stock = int(''.join(filter(str.isdigit, stock_text))) if stock_text else 0
                        except ValueError:
                            stock = 0
                            logging.warning(f"Invalid stock number '{stock_text}' for URL {url}")

                        # Extract Player Status
                        status_elements = c.find_elements(By.XPATH, './/*[@title="Settlers"]')
                        status = False
                        if status_elements:
                            status_text = status_elements[0].get_attribute('innerHTML').lower()
                            status = status_text == 'online'

                        # Function to extract per-want and per-have details
                        def extract_details(cls):
                            elements = c.find_elements(By.XPATH, f'.//div[@class="{cls}"]//span')
                            details = []
                            for s in elements:
                                amount_elements = s.find_elements(By.XPATH, './/span[@class="amount"]')
                                img_elements = s.find_elements(By.XPATH, './/img')
                                if amount_elements and img_elements:
                                    amount = amount_elements[0].text.strip()
                                    title = img_elements[0].get_attribute('title').strip()
                                    details.append(f"{amount}x {title}")
                            return ' ⇒ '.join(details) if details else "N/A"

                        per_want = extract_details('per-want') or "N/A"
                        per_have = extract_details('per-have') or "N/A"

                        # Append extracted data
                        data_entry = {
                            "URL": url,  # Reference to the source URL
                            "What You Get": what_get,
                            "What You Pay": what_pay,
                            "Profile Link": link,
                            "Items in Stock": stock,
                            "Player Status": status,
                            "Per-Want": per_want,
                            "Per-Have": per_have
                        }
                        data.append(data_entry)
                        logging.info(f"  Container {i}: {data_entry}")
                        print(f"  Container {i}: {data_entry}")
                    except Exception as e:
                        logging.error(f"  Failed to extract container {i} for URL {url}: {e}")
                        print(f"  Failed to extract container {i} for URL {url}: {e}")

                if data:
                    print(f"  Total containers extracted from URL {idx}: {len(data)}")
                    logging.info(f"  Total containers extracted from URL {idx}: {len(data)}")
                    # Accumulate data
                    all_data.extend(data)
                    # Save data after each URL
                    save_all_data_to_json(all_data, run_epoch, json_dir='data_files')
                else:
                    logging.info(f"No data extracted from URL {url}.")
                    print(f"No data extracted from URL {url}.")

            except Exception as e:
                logging.error(f"Failed to process URL {url}: {e}")
                print(f"Failed to process URL {url}: {e}")

    except Exception as e:
        logging.error(f"An unexpected error occurred during data extraction: {e}")
        print(f"An unexpected error occurred during data extraction: {e}")

    finally:
        try:
            driver.quit()
            logging.info("Browser closed.")
            print("Browser closed.")
        except Exception as e:
            logging.error(f"Failed to close WebDriver: {e}")
            print(f"Failed to close WebDriver: {e}")

        # Final save to ensure all data is written
        if all_data:
            print(f"\nTotal data entries extracted: {len(all_data)}")
            logging.info(f"Total data entries extracted: {len(all_data)}")
            save_all_data_to_json(all_data, run_epoch, json_dir='data_files')
        else:
            logging.info("No data extracted from any URL.")
            print("No data extracted from any URL.")

        print(f"\nData extraction completed for all URLs.")
        logging.info("Data extraction completed for all URLs.")

if __name__ == "__main__":
    main()
