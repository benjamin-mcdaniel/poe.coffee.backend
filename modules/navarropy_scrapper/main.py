import os, sys, json, time, sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Database setup
def setup_database(db_name='urls.db'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS extracted_data (img_id TEXT PRIMARY KEY, url TEXT)''')
    conn.commit()
    return conn, c

# Check if img_id is already in database
def is_img_processed(c, img_id):
    c.execute('SELECT 1 FROM extracted_data WHERE img_id=?', (img_id,))
    return c.fetchone() is not None

# Save img_id and URL to database
def store_img_data(c, conn, img_id, url):
    c.execute('INSERT OR IGNORE INTO extracted_data (img_id, url) VALUES (?, ?)', (img_id, url))
    conn.commit()

# Check and handle rate limit
def check_and_handle_rate_limit(driver):
    rate_limit_url = "https://www.pathofexile.com/trade/exchange/Settlers"
    if driver.current_url == rate_limit_url:
        return True

def main():
    # Database connection
    db_conn, db_cursor = setup_database()

    # Determine Chrome user data directory based on OS
    user_data_dir = (
        os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data') if sys.platform.startswith('win') else
        os.path.expanduser('~/Library/Application Support/Google/Chrome') if sys.platform.startswith('darwin') else
        os.path.expanduser('~/.config/google-chrome') if sys.platform.startswith('linux') else
        None
    )
    if not user_data_dir:
        raise Exception("Unsupported operating system")

    profile = "Profile 1"  # Change to your dedicated profile
    url = "https://www.pathofexile.com/trade/exchange/Settlers/9z28fK"

    # Configure Chrome options
    options = Options()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f'--profile-directory={profile}')
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(url)
        print(f"Navigated to {url}")

        # Click "Show Filters" until it is visible and clickable
        while True:
            try:
                show_filters = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(.)='Show Filters']")))
                show_filters.click()
                time.sleep(1)  # Allow for any animations
            except:
                break  # Stop clicking once it's no longer available

        categories = driver.find_elements(By.XPATH, "//*[@class='filter-title filter-title-clickable' and not(descendant::img) and not(preceding-sibling::img) and not(following-sibling::img) and not(preceding-sibling::*[@class='filter-options']) and not(following-sibling::*[@class='filter-options'])]")
        for category in categories:
            category.click()

        # Find all items under "Items I Want"
        item_imgs = driver.find_elements(By.XPATH, "//*[@class='filter-group' and descendant::*[contains(text(), 'Items I Want')]]//*[@class='filter']//img")
        print(f"Found {len(item_imgs)} items in 'Items I Want'.")

        for idx in range(len(item_imgs)):
            try:
                # Get a unique identifier for the img element, e.g., its index
                img_id = f"img_{idx}"

                # Skip if img is already processed
                if is_img_processed(db_cursor, img_id):
                    print(f"Skipping already processed img: {img_id}")
                    continue

                while True:
                    # Reopen filters if they are hidden after a search
                    while True:
                        try:
                            show_filters = driver.find_element(By.XPATH, "//button[normalize-space(.)='Show Filters']")
                            if show_filters.is_displayed():
                                show_filters.click()
                                time.sleep(1)  # Brief pause for UI adjustment
                            break
                        except:
                            break

                    try:
                        categories = driver.find_element(By.XPATH, "//*[@class='filter-title filter-title-clickable' and not(descendant::img) and not(preceding-sibling::img) and not(following-sibling::img) and not(preceding-sibling::*[@class='filter-options']) and not(following-sibling::*[@class='filter-options'])]")
                        for category in categories:
                            category.click()
                    except NoSuchElementException:
                        pass


                    
                    # Deselect any active filter items
                    try:
                        selecteds = driver.find_elements(By.XPATH, '//*[@class="exchange-filter-item active"]')
                        for selected in selecteds:
                            selected.click()
                    except NoSuchElementException:
                        pass

                    # Refresh the list of items to prevent stale elements
                    item_imgs = driver.find_elements(By.XPATH, "//*[@class='filter-group' and descendant::*[contains(text(), 'Items I Want')]]//*[@class='filter']//img")
                    current_item = item_imgs[idx]

                    # Click on the current item
                    current_item.click()
                    print(f"Clicked item {idx + 1}.")

                    # Click the search button
                    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='trade']/div[4]/div/div[3]/div[2]/button")))
                    search_btn.click()
                    print("Clicked search button.")

                    # Wait for URL to change
                    wait.until(EC.url_changes(url))
                    time.sleep(1)
                    current_url = driver.current_url

                    # Check for rate limit immediately after URL change
                    if not check_and_handle_rate_limit(driver):
                        break
                    else:
                        print("Rate limit detected. Waiting for 120 seconds...")
                        time.sleep(120)

                # Store img_id and URL to database if new
                store_img_data(db_cursor, db_conn, img_id, current_url)
                print(f"Stored img and URL: {img_id} -> {current_url}")

                # Allow the page to stabilize after loading the search
                time.sleep(1)

            except Exception as e:
                print(f"Failed to process item {idx + 1}: {e}")
                continue

        # Retrieve all stored URLs to save to JSON
        db_cursor.execute('SELECT url FROM extracted_data')
        all_urls = [row[0] for row in db_cursor.fetchall()]
        if all_urls:
            with open('extracted_urls.json', 'w', encoding='utf-8') as f:
                json.dump(all_urls, f, ensure_ascii=False, indent=4)
            print(f"All extracted URLs have been saved to 'extracted_urls.json'.")
        else:
            print("No URLs were extracted.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        db_conn.close()
        input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    main()
