import time
import json
import requests
import logging
from datetime import datetime, timedelta

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from utils import get_driver, create_unique_object_id, save_and_upload_image


def get_api_params(driver, city:str='Miami', days:int=30):

    try:
        print(driver)
        driver.get("https://www.eventbrite.com/d/fl--miami/all-events/?page=1")
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@id='locationPicker']"))
        )
        location_input = driver.find_element(By.XPATH, "//input[@id='locationPicker']")
        location_input.click()
        location_input.clear()
        location_input.send_keys(city)
        time.sleep(1)
        location_input.send_keys(Keys.ENTER)
        body_element = driver.find_element(By.TAG_NAME, "body")
        body_element.click()
        time.sleep(5)
        history_value = driver.execute_script("return window.localStorage.getItem('location:autocomplete:history');")
        # driver.quit()

        if history_value:
            history_value = json.loads(history_value.replace(';', ','))
            place_id = history_value.get('placeId')
            # return place_id
        else:
            
            logging.error("Place ID not found in local storage.")
            return None
        
        csrf_token = get_csrf_token(driver.get_cookies())
        
        if place_id and csrf_token:
            return place_id, csrf_token
    except Exception as e:
        logging.error(f"Error occurred while retrieving API Params: {str(e)}")
        return None

def get_place_id(driver):
    
    max_attempts = 5
    attempt = 0
    history_value = None

    while attempt < max_attempts:
        try:
            history_value = driver.execute_script("return window.localStorage.getItem('location:autocomplete:history');")
            if history_value:
                history_value = json.loads(history_value.replace(';', ','))
                place_id = history_value.get('placeId')
                return place_id
            else:
                time.sleep(2)
                attempt += 1
        except Exception as e:
            logging.error(f"Error occurred while getting history value: {str(e)}")
            break


def get_csrf_token(cookies):
    try:
        csrf_token = None
        for cookie in cookies:
            if cookie['name'] == 'csrftoken':
                csrf_token = cookie['value']
                break
        if csrf_token:
            return csrf_token
        else:
            logging.error("CSRF token not found in cookies.")
            return None
    except Exception as e:
        logging.error(f"Error occurred while retrieving CSRF token: {str(e)}")
        return None

def scrape_event_data(place_id, csrf_token, dates):
    try:
        url = 'https://www.eventbrite.com/api/v3/destination/search/'

        headers = {
            'authority': 'www.eventbrite.com',
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://www.eventbrite.com',
            'referer': 'https://www.eventbrite.com/d/ca--san-francisco/all-events/?page=4',
            'sec-ch-ua': '',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '""',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            'x-csrftoken': csrf_token,
            'x-requested-with': 'XMLHttpRequest',
            'cookie': f'csrftoken={csrf_token};'
        }

        data = {
            "event_search": {
                "dates": "current_future",
                "date_range": {
                    "from": dates['start_date'],
                    "to": dates['end_date']
                },
                "dedup": True,
                "places": [
                    place_id
                ],
                "page": 1,
                "page_size": 50,
                "online_events_only": False,
                "include_promoted_events_for": {
                    "interface": "search",
                    "request_source": "web"
                }
            },
            "expand.destination_event": [
                "primary_venue",
                "image",
                "ticket_availability",
                "primary_organizer",
            ],
            "debug_experiment_overrides": {
                "search_exp_1": "D"
            }
        }

        results = [
                [
                    
                    
                    "id",
                    "UID",
                    "cid",
                    "title",
                    "img",
                    "cover_img",
                    "sdate",
                    "stime",
                    "etime",
                    "address",
                    "status",
                    "description",
                    "disclaimer",
                    "latitude",
                    "longitude",
                    "is_booked",
                    "event_status",
                    "place_name",
                    "ticket_id",
                    "eid",
                    "event category",
                    "price",
                    'ticket_tlimit',
                    "ticket_status",
                    "ticket_booked",
                    "is_soldout",
                    "is_free",
                    "address_url",
                    "organizer",
                    "event_url",
                    "edate",
                    "original_img_name",
                    
                ]
            ]

        page_number = 1
        while True:
            data["event_search"]["page"] = page_number

            response = requests.post(url, headers=headers, json=data)
            response_json = response.json()

            event_results = response_json.get("events", {}).get("results", [])

            if not event_results:
                break
            else:
                for event in event_results[:5]:
                    try:
                        eid = create_unique_object_id()
                        image_url = event.get('image', None)
                        if image_url:
                            # image_url = event.get('image', None)
                            image_url = image_url['original']['url']
                            image_url = save_and_upload_image(
                                image_url, website_name="eventbrite.com")
                            if image_url == "None":
                                file_name = "None"
                            else:
                                file_name, image_url = image_url
                        categories = ', '.join([tag['display_name'] for tag in event['tags'] if tag.get('prefix', '').startswith('Eventbrite')])
                        start_date = event['start_date']
                        if (start_date > dates['end_date']):
                            continue
                        end_date = event['end_date']
                        start_time = event['start_time']
                        end_time = event['end_time']
                        place_name = event['primary_venue']['name']
                        full_address = event['primary_venue']['address']['localized_address_display']
                        latitude = float(event['primary_venue']['address']['latitude'])
                        longitude = float(event['primary_venue']['address']['longitude'])
                        organizer_name = event['primary_organizer']['name']
                        event_summary = event['summary']
                        event_name = event['name']
                        event_url = event['url']
                        
                        is_soldout = event['ticket_availability']['is_sold_out']
                        is_free = event['ticket_availability']['is_free']
                        ticket_price = event['ticket_availability'].get('minimum_ticket_price', None)
                        if ticket_price:
                            ticket_price = ticket_price.get('major_value', "None")
                        else:
                            ticket_price = "None"
                        # ticket_status = event['ticket_availability']['has_available_tickets']


                        results.append(
                        [
                            
                            eid,
                            4,      #uid
                            1,      #cid
                            event_name,
                            f"images/event/{file_name}",
                            f"images/event/{file_name}",
                            start_date,
                            start_time,
                            end_time,
                            full_address,
                            1,      #status
                            event_summary,
                            "None",   #disclaimer
                            latitude,
                            longitude,
                            0,
                            "Completed",
                            place_name,
                            eid,
                            eid,
                            categories,
                            ticket_price,
                            1000,   #ticket_tlimit
                            1,   #ticket_status
                            0,  #ticket_booked
                            is_soldout,
                            is_free,
                            "None",     #address_url
                            organizer_name,
                            event_url,
                            end_date,
                            image_url,
                        ]
                        )
                        print(f"Event processed successfully. {event_url}")
                        logging.info(
                                f"Event processed successfully. {event_url}")
                    except Exception as e:
                        logging.error(
                            f"KeyError: {e} occurred while processing Event. url = {event_url}")
                        continue

            page_number +=1   
            break
    

        return results
    except Exception as e:
        logging.error(f"Error occurred while scraping event data({event_url}): {str(e)}")
        return []

def fetch_events_from_eventbrite(city='Miami', days=1):

        try:
            driver = get_driver()        
            place_id, csrf_token = get_api_params(driver, city, days)
            driver.quit()

            dates = {
                'start_date': datetime.today().strftime("%Y-%m-%d"),
                'end_date': (datetime.today() + timedelta(days)).strftime("%Y-%m-%d")
            }
            event_data = scrape_event_data(place_id=place_id, csrf_token=csrf_token, dates=dates)
            
            return event_data


        except Exception as e:
            logging.error(f"Error occurred during event data scraping and processing: {str(e)}")

if __name__ == "__main__":
    fetch_events_from_eventbrite()
