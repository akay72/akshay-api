from selenium.webdriver.chrome.service import Service
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from yellowpages_scraper import scrape_yellow_pages_first_page
from email_finder import scrape_data
import os

def format_yellow_pages_data(data):
    return [{
        "Lead_id": item[0],
        "Company_name": item[1],
        "Phone_no": item[2],
        "Website": item[3],
        "Address": item[4],
        "City": item[5],
        "State": item[6],
        "Zipcode": item[7]
    } for item in data]

def format_email_data(data):
    return [{
        "Website": item[0],
        "Email": item[1],
        "Contact_Name": item[2] if item[2] != "None" else None,
        "Title": item[3] if item[3] != "None" else None,
        "Source": item[4]
    } for item in data]
def scrape_yellow_pages(searchterm, location, leadid):
    # Set up Selenium WebDriver for Yellow Pages

    try:
        yellow_pages_data = scrape_yellow_pages_first_page(searchterm, location, leadid)
        formatted_data = format_yellow_pages_data(yellow_pages_data)
        return formatted_data
    except Exception as e:
        print(f"An error occurred while scraping Yellow Pages: {e}")



def find_contacts(website_url):
    # Set up Selenium WebDriver for Email Finder
    chrome_options = Options()
    chrome_options.binary_location = os.getenv('GOOGLE_CHROME_BIN')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the Service with the path to ChromeDriver
    service = Service(executable_path=os.getenv('CHROMEDRIVER_PATH'))

    # Create the WebDriver instance specifying both the service and options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        email_data = scrape_data(driver, website_url, "https://emailbydomain.com/")
        formatted_contacts = format_email_data(email_data)
        return formatted_contacts
    except Exception as e:
        print(f"An error occurred while finding contacts: {e}")
    finally:
        if driver:
            driver.quit()





# The following code is for testing purposes
if __name__ == "__main__":
    # Example usage
    yellow_pages_results = scrape_yellow_pages("Some Company", "Some Location", 123)
    print(json.dumps(yellow_pages_results, indent=4))

    contact_results = find_contacts("http://example.com")
    print(json.dumps(contact_results, indent=4))
