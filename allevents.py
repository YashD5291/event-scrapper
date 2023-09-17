import requests
import json
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from utils import create_unique_object_id, save_and_upload_image


logging.basicConfig(filename='event_fetch.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

url = 'https://allevents.in/api/index.php/categorization/web/v1/list'
headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Cookie': 'a=a;',
    'Referer': 'https://allevents.in/hollywood/all?ref=cityhome-popmenuf'
}


def fetch_events_from_allevents(days=1, city="Miami"):
    
    url = 'https://allevents.in/api/index.php/categorization/web/v1/list'
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Cookie': 'a=a;',
        'Referer': 'https://allevents.in/hollywood/all?ref=cityhome-popmenuf'
    }

    try:
        event_urls = []
        events = []

        start_date = datetime.now()
        print(start_date.timestamp())
        end_date = start_date + timedelta(days=days)
        print(end_date.timestamp())

        logging.info(
            f"Fetching events from allevents.in for {city} for the next {days} days.")
        data = {
            "venue": 0,
            "page": 1,
            "rows": 1000,
            "tag_type": None,
            "sdate": start_date.timestamp(),
            "edate": end_date.timestamp(),
            "city": city,
            "keywords": 0,
            "category": [
                "all"
            ],
            "formats": 0,
            "popular": True
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)
        results = [
                [
                    'id',
                    'UID',
                    'cid',
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
                    'place_name',
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
                    'organizer',
                    "event_url",
                    "edate",
                    "original_img_name",
                ]
                ]
        if response.status_code == 200:
            data = response.json()
            data = data.get("item", [])
            logging.info(f"Fetched {len(data)} events from allevents.in.")

            for record in data[:5]:
                # print(record)
                event_urls.append(record["event_url"])
            print(len(data))

            descriptions = get_desc(event_urls)
            # print(record)
            for i, record in enumerate(data[:5]):
                stime = datetime.fromtimestamp(
                    int(record["start_time"]))
                etime = datetime.fromtimestamp(
                    int(record["end_time"]))
                # f"{event['latitude']} {event['longitude']}"
                instance = []
                try:  
                    eid = create_unique_object_id()
                    event_name = record['eventname_raw']
                    event_url = record["event_url"]
                    print(f"Event {i} : {event_url}")
                    venue = record["location"]
                    print(record["banner_url"])
                    image_url = record["banner_url"]
                    if image_url:
                        event_image = save_and_upload_image(image_url, website_name="allevents.in")
                        
                        if event_image == "None":
                            file_name = "None"
                        else:
                            file_name, event_image = event_image
                    start_time = stime.time()
                    end_time = etime.time()
                    start_date = stime.date()
                    end_date = etime.date()
                    latitude = float(record['venue']['latitude'])
                    longitude = float(record['venue']['longitude'])
                    full_address = record["venue"]["full_address"]
                    description = descriptions[i]
                    categories = ", ".join(record["categories"]).lstrip(
                        ", ") if record["categories"] is not None else "No Categories Provided"
                    ticket_price = record['tickets'].get('min_ticket_price', 0)
                    results.append(
                        [
                            eid,
                            4,      #uid
                            1,      #cid
                            event_name,
                            f"images/event/{file_name}" ,
                            f"images/event/{file_name}" ,
                            start_date,
                            start_time,
                            end_time,
                            full_address,
                            1,      #status
                            description,
                            
                            "None",     #disclaimer
                            latitude,
                            longitude,
                            0,  #is_booked
                            "Completed",    #event_status
                            venue,
                            eid,     #ticket_id
                            eid,
                            categories,
                            ticket_price,  #ticket_price
                            1000,   #ticket_tlimit
                            1,          #ticket_status
                            0,          #ticket_booked
                            "False",       # is_soldout
                            "None",       # is_free
                            "None",     #address_url
                            "None",     #organizer
                            event_url,
                            end_date,
                            event_image,
                        ]
                    )
                    # events.append(instance)
                    print(f"Event {i} processed successfully. {event_url}")
                    logging.info(
                        f"Event {i} processed successfully. {event_url}")
                except KeyError as e:
                    logging.error(
                        f"KeyError: {e} occurred while processing Event {i}. url = {event_url}")

            # events = prepare_data_for_excel(events)
            return results
        else:
            logging.error(
                f"Request failed with status code {response.status_code}")
            print("Request failed with status code", response.status_code)
    except Exception as e:
        logging.error(
            f"An error occurred while fetching events from allevents.in: {e}")
        print("An error occurred while fetching events from allevents.in:", e)


def get_desc(urls=None):
    if urls is None:
        logging.error("URLs are not provided")
        raise ValueError("URLs are not provided")
    descriptions = []
    logging.info("Fetching event descriptions from allevents.in")
    for i, url in enumerate(urls):
        try:
            response = requests.get(url)
            html_content = response.content
            soup = BeautifulSoup(html_content, "html.parser")
            element = soup.find("div", class_="event-description-html")
            data = element.get_text(strip=True) if element is not None else ""
            descriptions.append(data)
        except Exception as e:
            logging.warning(
                f"An error occurred while fetching event description for URL {url}: {e}")
            descriptions.append("")

    logging.info("Fetched event descriptions from allevents.in")

    return descriptions

if __name__ == "__main__":
    fetch_events_from_allevents()