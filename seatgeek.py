import requests
import json
import time
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import logging
from utils import create_unique_object_id, save_and_upload_image


logging.basicConfig(filename='event_fetch.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')



def fetch_events_from_seatgeek(days=1, city="Miami"):
    
    url = 'https://api.seatgeek.com/2/events/'

    try:
        event_urls = []
        events = []

        start_date = date.today()
        end_date = start_date + timedelta(days=days)
        end_date_str = end_date.strftime("%Y-%m-%d")

        logging.info(
            f"Fetching events from seatgeek.com for {city} for the next {days} days.")
        
        params = {
        'page': 1,
        'per_page': 30,
        'listing_count.gte': 1,
        'lat': 25.76168,
        'lon': -80.191788,
        'range': '34mi',
        'datetime_utc.lte': end_date_str,
        'sort': 'datetime_local.asc',
        'client_id': 'MTY2MnwxMzgzMzIwMTU4',
        # 'venue.city': 'miami'
        }  

        response = requests.get(url, params=params)
        print(response.url)
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
            data = data.get("events", [])
            logging.info(f"Fetched {len(data)} events from allevents.in.")

            print(len(data))

            # print(record)
            for i, record in enumerate(data):
                # stime = datetime.fromtimestamp(
                #     int(record["start_time"]))
                # etime = datetime.fromtimestamp(
                #     int(record["end_time"]))
                # f"{event['latitude']} {event['longitude']}"
                try:  
                    eid = create_unique_object_id()
                    event_name = record['title']
                    event_url = record["url"]
                    print(f"Event {i} : {event_url}")
                    venue = record['venue'].get('name', "")
                    performers = record["performers"]
                    if performers:
                        image_url = performers[0].get('image')
                    
                        if image_url:
                            event_image = save_and_upload_image(image_url, website_name="seatgeek.com")
                            
                            if event_image == "None":
                                file_name = "None"
                            else:
                                file_name, event_image = event_image
                    else:
                        file_name, event_image = "None", "None"
                    startdate_str = record['datetime_local'].split('T')
                    start_date = startdate_str[0]
                    end_time = "None"
                    start_time = startdate_str[1]
                    end_date = "None"
                    latitude = float(record['venue']['location']['lat'])
                    longitude = float(record['venue']['location']['lon'])
                    full_address = f"{record['venue']['name']}, {record['venue']['address']}, {record['venue']['display_location']} - {record['venue']['postal_code']}"
                    print(full_address)
                    description = "None" if record["description"] == "" else record["description"]
                    categories = ", ".join([taxonomy['name'] for taxonomy in record['taxonomies']])
                    ticket_price = record['stats'].get('median_price', 0)
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

if __name__ == "__main__":
    results = fetch_events_from_seatgeek()
    print(results)