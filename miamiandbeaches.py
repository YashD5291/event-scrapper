import re
import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils import get_driver, create_unique_object_id, save_and_upload_image
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

# Set up logging
logging.basicConfig(filename='event_fetch.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')




def fetch_events_from_miami_and_beaches(days=1):
    
    headers = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Origin": "https://www.miamiandbeaches.com",
    "Referer": "https://www.miamiandbeaches.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
    }

    url = "https://y72zzu5ph1-1.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.17.1)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(4.55.0)%3B%20Vue%20(3.2.47)%3B%20Vue%20InstantSearch%20(4.9.0)%3B%20JS%20Helper%20(3.13.0)&x-algolia-api-key=08bbc181e65b799cb34162e4de5bb3fb&x-algolia-application-id=Y72ZZU5PH1"


    start_time = datetime.now()
    end_time = start_time + timedelta(days=days)
    logging.info(f"Start Time: {start_time}, End Time: {end_time}")

    data = {
        "requests": [
            {
                "indexName": "prd-item",
                "params": f"aroundLatLng=&aroundRadius=all&facets=%5B%22region%22%2C%22categories%22%2C%22subcategories%22%2C%22eventTypes%22%5D&filters=_datesFilter%3A{int(start_time.timestamp())}%20TO%20{int(end_time.timestamp())}%20AND%20(type%3Aevent)&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=1000&maxValuesPerFacet=200&page=&query=Miami&tagFilters="
            }
        ]
    }

    logging.info(f"Request Params: {data['requests'][0]['params']}")
    events = []

    try:
        results = [
                [
                    'id',
                    'UID',
                    'cid',
                    'title',
                    'img',
                    'cover_img',
                    'sdate',
                    'stime',
                    'etime',
                    'address',
                    'status',
                    'description',
                    'disclaimer',
                    'latitude',
                    'longitude',
                    'is_booked',
                    'event_status',
                    'place_name',
                    'ticket_id',
                    'eid',
                    'event_category',
                    'price',
                    'ticket_tlimit',
                    'ticket_status',
                    'ticket_booked',
                    'is_soldout',
                    'is_free',
                    'address_url',
                    'organizer',
                    'event_url',
                    'edate',
                    "original_img_name",
                ]
            ]
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        response = response.json()
        response = response.get("results", [])[0].get("hits", [])
        print(len(response))
        logging.info(f"Number of events: {len(response)}")
        for i, record in enumerate(response[:5]):
            start_time = datetime.fromtimestamp(
                int(record["_datesFilter"][0] if len(
                    record["_datesFilter"]) > 1 else record["_datesFilter"][0]))
            end_time = datetime.fromtimestamp(
                int(record["_datesFilter"][-1] if len(
                    record["_datesFilter"]) > 1 else record["_datesFilter"][0]))

            instance = []
            try:
                eid = create_unique_object_id()
                instance.append(eid)                              #data:id
                instance.append(4)                                                      #data:uid
                instance.append(1)                                                      #data:cid
                instance.append(record["name"])                                         #data:event_name
                instance.append(None)                                                   #data:img
                instance.append(None)                                                   #data:image_url
                instance.append(start_time.date())              #data:enddate
                instance.append(start_time.time())              #data:startdate
                instance.append(end_time.time())                #data:starttime
                instance.append("None")       #data:event_address
                instance.append(1)          #data:status
                description = record["description"]
                if description:
                    description = BeautifulSoup(description, 'html.parser').get_text()
                else:
                    description = "None"
                instance.append(description),        #data:description
                instance.append("None")     #data:disclaimer
                instance.append(record["_geoloc"]["lat"] if "_geoloc" in record else "")       #data:latitude
                instance.append(record["_geoloc"]["lng"] if "_geoloc" in record else record["_geoloc"]["long"] if "_geoloc" in record else "")   #data:longitude
                instance.append(0)      #data:is_booked
                instance.append("Completed")      #data:event_status
                instance.append(record["region"])               #data:place name
                instance.append(eid)       #data:ticket_id
                instance.append(eid)        #data:eid
                instance.append(", ".join(record["categories"]).lstrip(", "))           #data:categories
                instance.append("0.00") #data:ticket_price
                instance.append(1000)        #data:ticket_tlimit
                instance.append(1)          #data:ticket_status
                instance.append(0)          #data:ticket_booked
                instance.append("False")         #data:is_soldout
                instance.append("None")         #data:is_free
                instance.append("None")       #data:event_address_url
                instance.append("None")     #data:organizer
                instance.append(f'https://www.miamiandbeaches.com{record["pageUrl"]}')   #data:url
                instance.append(end_time.date())                #data:endtime
                instance.append(None)                                                   #data:original_img_name
                
                results.append(instance)
                
                print(f"Event {i} processed successfully. {instance[-3]}")
                logging.info(
                    f"Event {i} processed successfully. {instance[-3]}")
            except KeyError as e:
                logging.error(
                    f"KeyError: {e} occurred while processing Event {i}. url = {instance[-2]}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request Exception: {e} occurred.")
    except ValueError as e:
        logging.error(
            f"ValueError: {e} occurred while processing the response JSON.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    # events = prepare_data_for_excel(events)
    driver = get_driver()
    # print(events)
    results = scrap_address_and_image(driver=driver, events=results)
    return results

def scrap_address_and_image(driver, events):

        for i, event in enumerate(events[1:], 1):
            event_url = event[-3]       # getting event URL
            driver.get(event_url)
            # print(driver.page_source)
            # with open('image_processing.html', 'w') as file:
            #     file.write(driver.page_source)
            # fetching image
            wait = WebDriverWait(driver, 12)
            try:
                image_div = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ys-event-details__hero-section__image")))
                # image_div = driver.find_element(By.CLASS_NAME, 'ys-event-details__hero-section__image')
                style_attribute = image_div.get_attribute('style')
                url_match = re.search(r'url\((.*?)\)', style_attribute)
                if url_match:
                    image_url = url_match.group(1).strip("\"")
                    
                    if image_url.startswith("/getmedia/"):
                        image_url = f"https://www.miamiandbeaches.com{image_url}"
                    else:
                        pass
                    print('Background Image URL:', image_url)
                    if image_url:
                        image_url = save_and_upload_image(
                        url=image_url, website_name="miamiandbeaches.com")
                        if image_url == "None":
                            file_name = "None"
                        else:

                            file_name, image_url = image_url
                
                #change index here
                events[i][4] = f"images/event/{file_name}"       #data:image_url
                events[i][5] = f"images/event/{file_name}"        #data:image_url
                events[i][-1] = image_url     #data:original_img_name

            except Exception as e:
                logging.exception(
                    f"An unexpected error occurred while scraping event image for {event_url}")
                # Raise the error to propagate it further
                raise e
                # continue
            
            try:
                address_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "contact-info")))
                # address_div = driver.find_element(By.CLASS_NAME, "contact-info")
                address_anchor = address_div.find_element(By.TAG_NAME, "a")
                address_url = address_anchor.get_attribute('href')
                address = address_anchor.text
                
                #CHANGE INDEX
                events[i][9] = address #data:full_address
                events[i][-5] = address_url  #data:address_url

            except Exception as e:
                logging.exception(
                    f"An unexpected error occurred while scraping event address for {event_url}")
                # Raise the error to propagate it further
                raise e
                # continue
        # print(events)
        return events

if __name__ == '__main__':
    fetch_events_from_miami_and_beaches()