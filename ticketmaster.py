import requests
import logging
import json
from utils import create_unique_object_id, save_and_upload_image
from datetime import datetime, timedelta

logging.basicConfig(filename='event_fetch.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_events_from_ticketmaster(city="Miami", days=30):
    start_time = datetime.now()
    end_time = start_time + timedelta(days=days)
    start_time = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(start_time)

    logging.info(f"Start Time: {start_time}, End Time: {end_time}")
    events = []
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey=iTkEPL9j8mfVUGeTgYSADIphb7pXDMOG&city={city.lower()}&size=200&page=0&startDateTime={start_time}&endDateTime={end_time}"

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
        response = requests.get(url=url)
        response = response.json()
        response = response["_embedded"]["events"][0:30]
        logging.info(f"Number of events: {len(response)}")
        for i, record in enumerate(response):
            print(i)
            instance = []
            try:
                img_name, img_link = save_and_upload_image(
                    record["images"][4]["url"], "ticketmaster.com")
                eid = create_unique_object_id()
                instance.append(eid)  # data:id
                instance.append(4)  # data:uid
                instance.append(1)  # data:cid
                instance.append(record["name"])
                instance.append(f"images/event/{img_name}")  # data:img
                instance.append(f"images/event/{img_name}")  # data:img_url
                instance.append(record["dates"]["start"]
                                ["localDate"])  # data:startdate
                instance.append(record["dates"]["start"]
                                ["localTime"])  # data:starttime
                instance.append("None")  # data:endtime
                instance.append(
                    f'{record["_embedded"]["venues"][0]["name"]} {record["_embedded"]["venues"][0]["postalCode"]}')  # data:event_address
                instance.append(1)  # data:status
                instance.append("None")  # data:description
                instance.append("None")  # data:desclaimer
                # data:latitude
                instance.append(record["_embedded"]
                                ["venues"][0]["location"]["latitude"])
                instance.append(record["_embedded"]
                                ["venues"][0]["location"]["longitude"])
                instance.append(0)  # data:is_booked
                instance.append("Completed")  # data:event_status
                # data:place_name
                instance.append(record["_embedded"]
                                ["venues"][0]["address"]["line1"])
                instance.append(eid)  # data:ticket_id
                instance.append(eid)  # data:eid
                # data:categories
                instance.append(record["classifications"]
                                [0]["segment"]["name"])
                instance.append(record["priceRanges"][0]
                                ["min"])  # data:ticket_price
                instance.append(1000)  # data:ticket_tlimit
                instance.append(1)  # data:ticket_status
                instance.append(0)  # data:ticket_booked
                instance.append("False")  # data:is_soldout
                instance.append("None")  # data:is_free
                instance.append("None")  # data:event_address_url
                instance.append("None")  # data:organizer
                instance.append(record["url"])  # data:url
                instance.append("None")  # data:endtime
                instance.append(img_link)  # data:original_img_name
                results.append(instance)
                print(f"Event {i} processed successfully. {instance[-3]}")
                logging.info(
                    f"Event {i} processed successfully. {instance[-3]}")
            except KeyError as e:
                logging.error(
                    f"KeyError: {e} occurred while processing Event {i}. url = {instance[-3]}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request Exception: {e} occurred.")
    except ValueError as e:
        logging.error(
            f"ValueError: {e} occurred while processing the response JSON.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    return results


# fetch_events_from_ticketmaster()
