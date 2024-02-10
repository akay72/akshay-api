from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import random

def scrape_data(driver, domain_name, url, max_retries=2):
    retries = 0
    while retries < max_retries:
        try:
            print("Loading page...")
            driver.get(url)
            wait = WebDriverWait(driver, 30)

            print("Waiting for input element...")
            input_element = wait.until(EC.presence_of_element_located((By.ID, "url")))
            input_element.send_keys(domain_name)

            print("Waiting for submit button...")
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit'][@value='Find Email']")))
            submit_button.click()

            try:
                print("Waiting for table element...")
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            except TimeoutException:
                print("Table not found, retrying...")
                retries += 1
                continue  # Continue to the next iteration of the loop

            print("Processing table data...")
            table_html = driver.find_element(By.TAG_NAME, "table").get_attribute('outerHTML')
            soup = BeautifulSoup(table_html, 'html.parser')
            table_rows = soup.find_all('tr')

            data_found = False
            for i, row in enumerate(table_rows):
                if i == 0:  # Skip the header row
                    continue
                cols = row.find_all(['th', 'td'])
                row_data = [ele.text.strip() for ele in cols]
                if row_data and not all(col == 'Not Found' for col in row_data):
                    data_found = True
                    yield [domain_name] + row_data

            if not data_found:
                retries += 1
                print(f"No data found for {domain_name}, retrying... (Attempt {retries}/{max_retries})")
            else:
                break  # Break out of the loop if data is found

        except Exception as e:
            print(f"Error occurred: {e}")
            driver.save_screenshot('error_screenshot.png')  # Save screenshot for debugging
            print(f"Exception type: {type(e)}")
            break  # Break out of the loop on exception
