import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
from utils import random_user_agent, random_delay, remove_word, contains_all_search_terms

def scrape_yellow_pages_first_page(search_terms, location, leadid):
    headers = {
        'User-Agent': random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    business_data = []
    session = requests.Session()
    session.headers.update(headers)

    domain = "https://www.yellowpages.com"
    page = 1

    search_terms_formatted = search_terms.replace('&', 'and')
    encoded_search_terms = urllib.parse.quote_plus(search_terms_formatted)
    encoded_location = urllib.parse.quote_plus(location)

    base_url = f"https://www.yellowpages.com/search?search_terms={encoded_search_terms}&geo_location_terms={encoded_location}&page={page}"

    random_delay()

    response = session.get(base_url)
    random_delay()
    # time.sleep(2)
    
    print(f"Processing search term: {search_terms}")

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        time.sleep(3)
        results = soup.find_all(class_="result")

        if not results:
            print(f"No results on page {page}. Ending pagination.")
            return business_data
            
        for result in results:
            title = phone_number = full_address = website_url = city = state = zip_code = None
            try:

                url_section = result.find("div", class_="info-section info-primary")
                secondary_section = result.find("div", class_="info-section info-secondary") 
                
                title_tag = url_section.find("a", class_="business-name")
                title = title_tag.text.strip() if title_tag else None
               

                phone_tag = secondary_section.find("div", class_="phones phone primary")
                phone_number = phone_tag.text.strip() if phone_tag else None
 
                address_tag = secondary_section.find("div", class_="street-address")
                full_address = address_tag.text.strip() if address_tag else None

                try:
                    website_tag = url_section.find("a", class_="track-visit-website")
                    # print(website_tag)
                    website_url = website_tag['href'] if website_tag else None
                except Exception as e:
                    website_url=None

                locality=secondary_section.find('div',class_='locality')
                if locality:
                    locality_text = locality.text.strip()
                    # Assuming the format is always "City, State ZIP"
                    locality_parts = locality_text.split(',')
                    city = locality_parts[0].strip() if len(locality_parts) > 0 else None
                    state_and_zip = locality_parts[1].strip().split(' ') if len(locality_parts) > 1 else [None, None]
                    state = state_and_zip[0] if len(state_and_zip) > 0 else None
                    zip_code = state_and_zip[1] if len(state_and_zip) > 1 else None
            

                # print(title)
                # Check if all details are found; if not, go to the detail page
                if not (title and phone_number and full_address and website_url):
                    random_delay() 
                    link = url_section.find("a", class_="business-name")['href']
                    full_url = urllib.parse.urljoin(domain, link)
                    description_response = session.get(full_url)
                    time.sleep(3)
                    if description_response.status_code == 200:
                        description_content = description_response.text
                        description_soup = BeautifulSoup(description_content, "html.parser")
                        description_results = description_soup.find("div", id="listing-card")
                        if description_results:
                            if not title:
                                try:
                                    title_element = description_results.find("h1", class_="business-name")
                                    title = title_element.text.strip() if title_element else None
                                   

                                except:
                                    title = None           
                                    
                            if not phone_number:
                                try:
                                    phone_element = description_results.find("a", class_="phone")
                                    phone_number = phone_element.text.strip() if phone_element else None
                                except:
                                    phone_number=None

                            if not full_address:
                                try:
                                    address_element = description_results.find("span", class_="address").find('span')
                                    full_address = address_element.text.strip() if address_element else None
                                except:
                                    full_address=None  


                            if not city or state or zip_code:  
                                
                                try:
                                    address_tag = description_results.find("span", class_="address")
                                    if address_tag:
                                        # Extract the inner text from the first span which is the street address
                                        street_address_span = address_tag.find("span")
                                        if street_address_span:
                                            street_address = street_address_span.text.strip()
                                            # Replace the street address with an empty string to get the city, state, ZIP
                                            locality_info = address_tag.text.replace(street_address, '').strip()
                                        else:
                                            locality_info = address_tag.text.strip()
                                        
                                        # Assuming the format is always "City, State ZIP"
                                        locality_parts = locality_info.split(',')
                                        city = locality_parts[0].strip() if len(locality_parts) > 0 else None
                                        state_and_zip = locality_parts[1].strip().split(' ') if len(locality_parts) > 1 else [None, None]
                                        state = state_and_zip[0] if len(state_and_zip) > 0 else None
                                        zip_code = state_and_zip[1] if len(state_and_zip) > 1 else None
                                except Exception as e:
                                    print(f"An error occurred while trying to get the locality information: {e}")
                                    city = None
                                    state = None
                                    zip_code = None
                            if not website_url:
                                try:
                                    website_tag_detail = description_soup.find("a", class_="website-link dockable")
                                    website_url = website_tag_detail['href'] if website_tag_detail else None
                                except Exception:
                                    website_url = None        

                if contains_all_search_terms(title, search_terms):
                    word_to_remove = "- CLOSED"  # Replace with the word you want to remove
                    cleaned_title = remove_word(title, word_to_remove)
                    business_data.append((leadid, cleaned_title, phone_number, website_url, full_address, city, state, zip_code))

                # Removed the break statement to allow for more results to be added

            except Exception as e:
                print(f"An error occurred: {e}")
        
    else:
        print(f"Failed to retrieve page {page}. Status code: {response.status_code}")

   

    if business_data:
        
        return business_data  # Return scraped data for further processing
    else:
        return None
