import re
import time
import logging
from datetime import datetime, timedelta


from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from parsel import Selector

from utils import  get_driver, preprocess_date_string, create_unique_object_id, save_and_upload_image




def scroll_page(driver, url):
    try:
        driver.get(url)

        old_height = driver.execute_script(
            """
            function getHeight() {
                return document.querySelector('.UbEfxe').scrollHeight;
            }
            return getHeight();
        """
        )

        while True:
            driver.execute_script(
                "document.querySelector('.UbEfxe').scrollTo(0, document.querySelector('.UbEfxe').scrollHeight);"
            )
            time.sleep(1)

            new_height = driver.execute_script(
                """
                function getHeight() {
                    return document.querySelector('.UbEfxe').scrollHeight;
                }
                return getHeight();
            """
            )

            if new_height == old_height:
                break

            old_height = new_height

        selector = Selector(driver.page_source)
        # driver.quit()

        return selector
    except WebDriverException as e:
            # Log the error
            logging.error(f"Error occurred while scrolling the page: {e}")
            # Raise the error to propagate it further
            raise e

    except Exception as e:
        # Log other unexpected exceptions
        logging.exception(
            "An unexpected error occurred while scrolling the page")
        # Raise the error to propagate it further
        raise e


def scrape_google_events(events_until_date, selector):
    try:
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
                    "place_name",
                    'ticket_id',
                    "eid",
                    "event category",
                    'price',
                    'ticket_tlimit',
                    'ticket_status',
                    'ticket_booked',
                    'is_soldout',
                    'is_free',
                    "address_url",
                    'organizer',
                    "event_url",
                    "edate",
                    "original_img_name",
                ]
                ]
        print(len(selector.css(".scm-c")))
        for event in selector.css(".scm-c"):
            try: 
                eid = create_unique_object_id()
                event_name = event.css(".dEuIWb::text").get()
                date_start = (
                    f"{event.css('.FTUoSb::text').get()} {event.css('.omoMNe::text').get()}"
                )
                date_start = preprocess_date_string(date_string=date_start)
                
                if (date_start > events_until_date):
                    continue
                
                date_when = event.css(".Gkoz3::text").get()
                full_address = [part.css("::text").get() for part in event.css(".ov85De span")]
                full_address = filter(None, full_address)
                full_address = ', '.join(full_address)
                event_url = event.css(".zTH3xc::attr(href)").get()
                location_link = (
                    "https://www.google.com" + event.css(".ozQmAd::attr(data-url)").get('')
                )
                image_url = file_name = "None"
                image_url = event.css(".YQ4gaf.wA1Bge::attr(src)").get('')
                if image_url:
                    pass
                    image_url = save_and_upload_image(image_url, website_name="googleevents")
                    if image_url == "None":
                        file_name = "None"
                    else:
                        file_name, image_url = image_url

                else:
                    image_url = "None"
                description = event.css(".PVlUWc::text").get('')
                place_name = event.css(".RVclrc::text").get()
                venue_link = (
                    "https://www.google.com" + event.css(".pzNwRe a::attr(href)").get()
                    if event.css(".pzNwRe a::attr(href)").get()
                    else None
                )
                
                results.append(
                [
                    eid,
                    4,      #uid
                    1,      #cid
                    event_name,
                    f"images/event/{file_name}",
                    f"images/event/{file_name}",
                    date_start,
                    'None', #stime
                    "None", #etime
                    full_address,
                    1,      #status
                    description,
                    "None", #disclaimer
                    None,   #latitude
                    None,   #longitude
                    0,  #is_booked
                    "Completed",    #event_status
                    place_name,
                    eid, #ticket_id
                    eid,
                    "None",     #category
                    "0.00",  #ticket_price
                    1000, #ticket_tlimit
                    1,      #ticket_status
                    0,  #ticket_booked
                    "False",   #is_soldout
                    "None",  #is_free
                    location_link,
                    "None",     #organizer
                    event_url,
                    date_when,
                    image_url,
                ])
                logging.info(
                            f"Event {eid} processed successfully. {event_url}")
            except KeyError as e:
                logging.error(
                            f"KeyError: {e} occurred while processing Event {eid}. url = {event_url}")
            
        return results
    except Exception as e:
        logging.exception(
            "An unexpected error occurred while scraping Google events")
        # Raise the error to propagate it further
        raise e


def scrap_geo_code(driver, events):
    try:

        for i, event in enumerate(events[1:], 1):
            try:
                print(event[-5])
                location_link = event[-5]
                driver.get(location_link)

                check_new_url = WebDriverWait(driver, 30).until(EC.url_changes(location_link))

                if check_new_url:
                    new_url = driver.current_url

                    pattern = r"@([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+)"
                    match = re.search(pattern, new_url)

                    if match:
                        latitude = match.group(1)
                        longitude = match.group(2)
                        # events[i][-1] = latitude
                        # events[i][-1] = longitude
                        events[i][13] = latitude
                        events[i][14] = longitude
                        # events[i]["latitude"] = latitude
                        # events[i]["longitude"] = longitude
                        print("Latitude:", latitude)
                        print("Longitude:", longitude)
                    else:
                        print("Latitude and longitude not found in the URL.")
                else:
                    pass
            except Exception as e:
                logging.exception(
                    "An unexpected error occurred while scraping geocode data")
                events[i][13] = "None"
                events[i][14] = "None"
                continue

        driver.quit()
        return events
    except Exception as e:
        logging.exception(
            "An unexpected error occurred while scraping geocode data")

        # Raise the error to propagate it further
        # raise e


def fetch_events_from_google_events(city='San Fransisco', days=30):
    try:
        logging.info(
            f"Google events scraping started for {city}")
        
        params = {
            "q": f"Events in {city}",  # search query
            "ibp": "htl;events",  # Google Events page
            "hl": "en",  # language
            "gl": "us",  # country of the search
        }
        
        events_until_date = datetime.now() + timedelta(days=days)
        print(events_until_date)
        URL = f"https://www.google.com/search?q={params['q']}&ibp={params['ibp']}&hl={params['hl']}&gl={params['gl']}l"

        driver = get_driver()
        result = scroll_page(driver, URL)
        google_events = scrape_google_events(events_until_date=events_until_date, selector=result)
        print(len(google_events))
        google_events_w_cords = scrap_geo_code(driver, google_events)
        
        logging.info(
                f"Google events scrapped successfully. Events scraped: {len(google_events_w_cords)}")
            # Raise the error to propagate it further
        return google_events_w_cords
    except Exception as e:
        logging.exception(
            "An unexpected error occurred in the main() function")
        # Raise the error to propagate it further
        raise e


if __name__ == "__main__":
    fetch_events_from_google_events()
















# from datetime import datetime, timedelta

# def preprocess_date_string(date_string):
#     # Replace some common abbreviations and symbols
#     date_string = date_string.replace(",", "").replace("–", "-").replace("am", "AM").replace("pm", "PM")
#     # Split the date string into individual components
#     date_parts = date_string.split()
#     # Extract the day, month, and year
#     day = int(date_parts[1])
#     month = datetime.strptime(date_parts[2], "%b").month
#     year = datetime.now().year
#     # Extract the time range and timezone offset
#     time_range = date_parts[3].split("–")
#     start_time = time_range[0]
#     end_time = time_range[1] if len(time_range) > 1 else None
#     timezone_offset = date_parts[-1]
#     timezone_offset = int(timezone_offset[4:]) if timezone_offset.startswith("GMT") else 0
#     # Combine the components into a standardized format
#     date_standardized = f"{year:04d}-{month:02d}-{day:02d}"
#     if end_time:
#         # Manually add a leading zero to the hour if necessary
#         if len(start_time) == 6:
#             start_time = "0" + start_time
#         if len(end_time) == 6:
#             end_time = "0" + end_time
#         datetime_start = datetime.strptime(f"{date_standardized} {start_time}", "%Y-%m-%d %I:%M %p")
#         datetime_end = datetime.strptime(f"{date_standardized} {end_time}", "%Y-%m-%d %I:%M %p")
#         datetime_end += timedelta(hours=timezone_offset)
#         return datetime_start, datetime_end
#     else:
#         # Manually add a leading zero to the hour if necessary
#         if len(start_time) == 6:
#             start_time = "0" + start_time
#         datetime_single = datetime.strptime(f"{date_standardized} {start_time}", "%Y-%m-%d %I:%M %p")
#         datetime_single += timedelta(hours=timezone_offset)
#         return datetime_single


# # Example usage:
# date_strings = [
#     "Sat, 12 Aug, 8:30 pm – Sun, 13 Aug, 12:30 am GMT-7",
#     "Sun, 23 Jul, 7:30 – 11:30 pm GMT-7",
#     "Tue, 3 Oct, 7:30 – 11:30 pm GMT-7",
#     # Add more date strings here
# ]

# for date_string in date_strings:
#     datetime_obj = preprocess_date_string(date_string)
#     print(datetime_obj)











# from datetime import datetime, timedelta

# def preprocess_date_string(date_string):
#     # Replace some common abbreviations and symbols
#     date_string = date_string.replace(",", "").replace("–", "-").replace("am", "AM").replace("pm", "PM")

#     # Split the date string into individual components
#     date_parts = date_string.split()

#     # Extract the day, month, and year
#     day = int(date_parts[1])
#     month = datetime.strptime(date_parts[2], "%b").month
#     year = datetime.now().year

#     # Extract the time range and timezone offset
#     start_time = date_parts[3]
#     end_time = date_parts[9]

#     timezone_offset = date_parts[-1]
#     timezone_offset = int(timezone_offset[4:]) if timezone_offset.startswith("GMT") else 0

#     # Combine the components into a standardized format
#     date_standardized = f"{year:04d}-{month:02d}-{day:02d}"

#     if end_time:
#         datetime_start = datetime.strptime(f"{date_standardized} {start_time}", "%Y-%m-%d %I:%M %p")
#         datetime_end = datetime.strptime(f"{date_standardized} {end_time}", "%Y-%m-%d %I:%M %p")
#         datetime_end += timedelta(hours=timezone_offset)
#         return datetime_start, datetime_end
#     else:
#         datetime_single = datetime.strptime(f"{date_standardized} {start_time}", "%Y-%m-%d %I:%M %p")
#         datetime_single += timedelta(hours=timezone_offset)
#         return datetime_single


# # Example usage:
# date_strings = [
#     "Sat, 12 Aug, 8:30 pm – Sun, 13 Aug, 12:30 am GMT-7",
#     "Sun, 23 Jul, 7:30 – 11:30 pm GMT-7",
#     "Tue, 3 Oct, 7:30 – 11:30 pm GMT-7",
#     # Add more date strings here
# ]

# for date_string in date_strings:
#     datetime_objs = preprocess_date_string(date_string)
#     if isinstance(datetime_objs, tuple):
#         datetime_start, datetime_end = datetime_objs
#         print(datetime_start.strftime("%Y-%m-%d %I:%M %p"), datetime_end.strftime("%Y-%m-%d %I:%M %p"))
#     else:
#         datetime_single = datetime_objs
#         print(datetime_single.strftime("%Y-%m-%d %I:%M %p"))







# from datetime import datetime, timedelta

# def preprocess_date_string(date_parts):
#     # Extract the day, month, and year
#     day = int(date_parts[1])
#     month = datetime.strptime(date_parts[2], "%b").month
#     year = datetime.now().year

#     # Extract the time range and timezone offset
#     start_time = date_parts[3]
#     end_time = date_parts[9]

#     timezone_offset = date_parts[-1]
#     timezone_offset = int(timezone_offset[4:]) if timezone_offset.startswith("GMT") else 0

#     # Combine the components into a standardized format
#     date_standardized = f"{year:04d}-{month:02d}-{day:02d}"

#     if end_time:
#         datetime_start = datetime.strptime(f"{date_standardized} {start_time}", "%Y-%m-%d %I:%M %p")
#         datetime_end = datetime.strptime(f"{date_standardized} {end_time}", "%Y-%m-%d %I:%M %p")
#         datetime_end += timedelta(hours=timezone_offset)
#         return datetime_start, datetime_end
#     else:
#         datetime_single = datetime.strptime(f"{date_standardized} {start_time}", "%Y-%m-%d %I:%M %p")
#         datetime_single += timedelta(hours=timezone_offset)
#         return datetime_single


# # # Example usage:
# # date_parts_list = [
# #     ['Sat', '12', 'Aug', '8:30', 'PM', '-', 'Sun', '13', 'Aug', '12:30', 'AM', 'GMT-7'],
# #     ['Sun', '23', 'Jul', '7:30', 'PM', '-', '11:30', 'pm', 'GMT-7'],
# #     ['Tue', '3', 'Oct', '7:30', 'PM', '-', '11:30', 'pm', 'GMT-7'],
# #     # Add more date_parts lists here
# # ]

# # for date_parts in date_parts_list:
# #     datetime_objs = preprocess_date_string(date_parts)
# #     if isinstance(datetime_objs, tuple):
# #         datetime_start, datetime_end = datetime_objs
# #         print(datetime_start.strftime("%Y-%m-%d %I:%M %p"), datetime_end.strftime("%Y-%m-%d %I:%M %p"))
# #     else:
# #         datetime_single = datetime_objs
# #         print(datetime_single.strftime("%Y-%m-%d %I:%M %p"))
