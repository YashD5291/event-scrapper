import argparse
import logging
import datetime
from miamiandbeaches import fetch_events_from_miami_and_beaches
from eventbrite import fetch_events_from_eventbrite
from allevents import fetch_events_from_allevents
from google_events import fetch_events_from_google_events
from ticketmaster import fetch_events_from_ticketmaster
from seatgeek import fetch_events_from_seatgeek
from utils import generate_xslx
from datetime import datetime


def main():
    try:
        parser = argparse.ArgumentParser(description='Event web scraping Tool')
        parser.add_argument('-w', "--website", type=str, choices=[
                            'miamiandbeaches.com', 'eventbrite.com', 'allevents.in', 'googleevents', "ticketmaster.com", "seatgeek.com"], help="Enter the name of the website")
        parser.add_argument('-c', "--city", type=str, default="Miami",
                            help="Enter the name of the city")
        parser.add_argument('-d', "--days", type=int, default=30,
                            help="Enter the number of days")
        args = parser.parse_args()

        website = args.website
        # website = "ticketmaster.com"
        city = args.city.capitalize()
        days = int(args.days)
        if len(city) == 0 or (not isinstance(days, int)):
            parser.error("Invalid argument type.")
        time_now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S').replace(":", "_")

        # Configure logging
        log_filename = f"{website}_fetch.log"
        logging.basicConfig(filename=log_filename, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        # website = "miamiandbeaches.com"
        if website == "miamiandbeaches.com":
            try:
                events = fetch_events_from_miami_and_beaches(days=int(days))
                file_name = f"{website[0:-4]}_{time_now}.xlsx"
                generate_xslx(report_data=events, file_name=file_name)
                logging.info(
                    "Events fetched from miamiandbeaches.com and XSLX generated successfully.")
            except Exception as e:
                logging.error(
                    f"An error occurred while fetching events from miamiandbeaches.com: {e}")
        elif website == "eventbrite.com":
            try:
                events = fetch_events_from_eventbrite(
                    city=city, days=int(days))
                file_name = f"{website[0:-4]}_{time_now}.xlsx"
                generate_xslx(report_data=events, file_name=file_name)
                logging.info(
                    "Events fetched from eventbrite.com and XSLX generated successfully.")
            except Exception as e:
                logging.error(
                    f"An error occurred while fetching events from eventbrite.com: {e}")
        elif website == "allevents.in":
            try:
                events = fetch_events_from_allevents(city=city, days=int(days))
                # now = datetime.now()
                file_name = f"{website}_{time_now}.xlsx"
                generate_xslx(report_data=events, file_name=file_name)
                logging.info(
                    "Events fetched from allevents.in and XSLX generated successfully.")
            except Exception as e:
                logging.error(
                    f"An error occurred while fetching events from allevents.in: {e}")
        elif website == 'googleevents':
            try:
                print(int(days))
                events = fetch_events_from_google_events(
                    city=city, days=int(days))
                file_name = f"{website}_{time_now}.xlsx"
                generate_xslx(report_data=events, file_name=file_name)
                logging.info(
                    "Events fetched from Google events and XSLX generated successfully.")
            except Exception as e:
                logging.error(
                    f"An error occurred while fetching events from google events: {e}")
        elif website == "ticketmaster.com":
            try:
                print(int(days))
                events = fetch_events_from_ticketmaster(city=city, days=days)
                file_name = f"{website}_{time_now}.xlsx"
                generate_xslx(report_data=events, file_name=file_name)
                logging.info(
                    "Events fetched from ticketmaster.com and XSLX generated successfully.")
            except Exception as e:
                logging.error(
                    f"An error occurred while fetching events from ticketmaster.com: {e}")
        elif website == "seatgeek.com":
            try:
                print(int(days))
                events = fetch_events_from_seatgeek(city=city, days=days)
                file_name = f"{website}_{time_now}.xlsx"
                generate_xslx(report_data=events, file_name=file_name)
                logging.info(
                    "Events fetched from seatgeek.com and XSLX generated successfully.")
            except Exception as e:
                logging.error(
                    f"An error occurred while fetching events from seatgeek.com: {e}")
        else:
            logging.error("Not a valid website.")
            print("Not a valid website.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print("An error occurred.")


if __name__ == "__main__":
    main()
