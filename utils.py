import uuid
import shutil
import openpyxl
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import requests
import time

#hello
credentials_path = "./file-scraping-983c52577b59.json"
# Set up logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename=f'logs/log_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# def generate_xslx(report_data, file_name="report"):
#     try:
#         workbook = openpyxl.Workbook()
#         worksheet = workbook.active

#         for row_data in report_data:
#             worksheet.append(row_data)

#         for col in worksheet.columns:
#             column = col[0].column_letter
#             worksheet.column_dimensions[column].width = 40
            
#         today = datetime.today()
#         subfolder_name = today.strftime("%Y-%m-%d")
        
#         file_name = f'scrap_results/{today}/{file_name}'
#         # file_name = file_name.replace(":", "-")

#         folder_name = f'scrap_results/{today}/'

#         os.makedirs(f'scrap_results/{today}/',exist_ok=True)
#         workbook.save(f"{file_name}")
#         print(f"{file_name} created")
#         logging.info("XSLX generated successfully.")
#         folder_id = create_folder(credentials_path=credentials_path)
#         today = datetime.today()
#         subfolder_name = today.strftime("%Y-%m-%d")
#         subfolder_id = create_sub_folder(
#             credentials_path=credentials_path, subfolder_name=subfolder_name, parent_folder_id=folder_id)

#         file_link = upload_file(credentials_path=credentials_path,
#                     file_path=file_name, folder_id=subfolder_id, parent_folder_id=folder_id)
#         print(  )
#         if os.path.exists(folder_name):
#             shutil.rmtree(folder_name)
#         print(f"Folder link:")
#         print(f"XLSX File Successfully Uploaded to Google drive: {file_link}")
#         logging.info("File Successfully Uploaded to Google drive")
#     except Exception as e:
#         print(e)
#         logging.error(f"An error occurred while generating XSLX: {e}")

def generate_xslx(report_data, file_name="report"):
    try:
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        for row_data in report_data:
            worksheet.append(row_data)

        for col in worksheet.columns:
            column = col[0].column_letter
            worksheet.column_dimensions[column].width = 40

        today = datetime.today()
        subfolder_name = today.strftime("%Y-%m-%d")

        file_name = f'scrap_results/{today}/{file_name}'
        file_name = file_name.replace(":", "-")
        folder_name = f'scrap_results/{today}/'.replace(":", "-")
        os.makedirs(folder_name, exist_ok=True)
        workbook.save(f"{file_name}")
        print(f"{file_name} created")
        logging.info("XSLX generated successfully.")
        today = datetime.today()
        folder_id = create_folder(
            credentials_path=credentials_path, folder_name=today.strftime("%Y-%m-%d"))
        subfolder_id = create_sub_folder(
            credentials_path=credentials_path, subfolder_name="Reports", parent_folder_id=folder_id)

        file_link = upload_file(credentials_path=credentials_path,
                    file_path=file_name, folder_id=subfolder_id, parent_folder_id=folder_id)
        
        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)
        print(f"XLSX File Successfully Uploaded to Google drive: {file_link}")

        logging.info("File Successfully Uploaded to Google drive")
    except Exception as e:
        print(e)
        logging.error(f"An error occurred while generating XSLX: {e}")

def upload_file(credentials_path, file_path, folder_id, parent_folder_id):
    try:
        # Build the credentials and Drive API service
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=['https://www.googleapis.com/auth/drive'])
        email = credentials.service_account_email
        logger.info(f'Authenticated Google Account Email: {email}')
        service = build("drive", "v3", credentials=credentials)

        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        print(file_metadata["name"])
        media = service.files().create(
            body=file_metadata,
            media_body=file_path,
            fields='id'
        ).execute()

        file_id = media.get('id')
        file_link = f"https://drive.google.com/file/d/{file_id}"
        logger.info(f'File uploaded successfully. File ID: {file_id}')
        logger.info(f'File link: {file_link}')

        permission_body = {
            'role': 'reader',
            'type': 'anyone'
        }
        service.permissions().create(fileId=parent_folder_id,
                                     body=permission_body).execute()
        logger.info("Folder and its children are now publicly accessible.")
        return file_link
    except Exception as e:
        logger.error("An error occurred while uploading the file.")
        logger.exception(e)
        raise

def create_sub_folder(credentials_path, subfolder_name, parent_folder_id):
    try:
        # Build the credentials and Drive API service
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=['https://www.googleapis.com/auth/drive'])
        service = build("drive", "v3", credentials=credentials)

        if parent_folder_id:

            response = service.files().list(
                q=f"name='{subfolder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents",
                fields="files(id)").execute()

            if len(response["files"]) == 0:
                folder_metadata = {
                    "name": subfolder_name,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [parent_folder_id]
                }
                folder = service.files().create(body=folder_metadata, fields="id").execute()
                folder_id = folder.get("id")
                folder_link = f"https://drive.google.com/drive/folders/{folder_id}"
                logger.info(
                    f"Folder '{subfolder_name}' created successfully. Folder ID: {folder_id}")
                logger.info(f"Folder link: {folder_link}")
                return folder_id
            else:
                # Folder already exists, extract the folder_id
                folder_id = response['files'][0]['id']
                folder_link = f"https://drive.google.com/drive/folders/{folder_id}"
                logger.info(
                    f"Folder '{subfolder_name}' already exists. Folder ID: {folder_id}")
                logger.info(f"Folder link: {folder_link}")
                return folder_id

    except Exception as e:
        logger.error("An error occurred while creating the folder.")
        logger.exception(e)
        raise

# def create_folder(credentials_path, folder_name="Event Reports"):
#     try:
#         # Build the credentials and Drive API service
#         credentials = service_account.Credentials.from_service_account_file(
#             credentials_path, scopes=['https://www.googleapis.com/auth/drive'])
#         service = build("drive", "v3", credentials=credentials)

#         response = service.files().list(
#             q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'", fields="files(id)").execute()

#         if len(response['files']) == 0:
#             # Folder doesn't exist, create the folder
#             folder_metadata = {
#                 'name': folder_name,
#                 'mimeType': 'application/vnd.google-apps.folder'
#             }
#             folder = service.files().create(body=folder_metadata, fields='id').execute()
#             folder_id = folder.get('id')
#             folder_link = f"https://drive.google.com/drive/folders/{folder_id}"
#             logger.info(
#                 f"Folder '{folder_name}' created successfully. Folder ID: {folder_id}")
#             logger.info(f"Folder link: {folder_link}")
#         else:
#             # Folder already exists, extract the folder_id
#             folder_id = response['files'][0]['id']
#             folder_link = f"https://drive.google.com/drive/folders/{folder_id}"
#             logger.info(
#                 f"Folder '{folder_name}' already exists. Folder ID: {folder_id}")
#             logger.info(f"Folder link: {folder_link}")

#         return folder_id

#     except Exception as e:
#         logger.error("An error occurred while creating the folder.")
#         logger.exception(e)
#         raise


def create_folder(credentials_path, folder_name="Event Reports"):
    # parent_folder_id = "12rbBMyeMXmbwndU5raLOZrZJsuYVJ2Ay"
    # parent_folder_id = "128gJKSAYIlqtFqkD_EUqMZ2ZlaOhbxSV"
    parent_folder_id = "1tZSHrC8PIkxlAHGqoB-8gDnSmFzxhmdl"
    try:    
        # Build the credentials and Drive API service
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=['https://www.googleapis.com/auth/drive'])
        service = build("drive", "v3", credentials=credentials)

        # response = service.files().list(
        #     q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'", fields="files(id)").execute()
        response = service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents",
            fields="files(id)").execute()

        if len(response['files']) == 0:
            # Folder doesn't exist, create the folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                "parents": [parent_folder_id]
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')
            folder_link = f"https://drive.google.com/drive/folders/{folder_id}"
            logger.info(
                f"Folder '{folder_name}' created successfully. Folder ID: {folder_id}")
            logger.info(f"Folder link: {folder_link}")
        else:
            # Folder already exists, extract the folder_id
            folder_id = response['files'][0]['id']
            folder_link = f"https://drive.google.com/drive/folders/{folder_id}"
            logger.info(
                f"Folder '{folder_name}' already exists. Folder ID: {folder_id}")
            logger.info(f"Folder link: {folder_link}")

        return folder_id

    except Exception as e:
        logger.error("An error occurred while creating the folder.")
        logger.exception(e)
        raise

def preprocess_date_string(date_string):
    # Replace some common abbreviations and symbols
    date_string = date_string.replace(",", "").replace("–", "-")
    # Split the date string into individual components
    date_parts = date_string.split()
    # Extract the day and month
    day = int(date_parts[0])
    if len(date_parts[1]) != 3:
        date_parts[1] = date_parts[1][:-1]
    month = datetime.strptime(date_parts[1],     "%b").month
    year = datetime.now().year
    # Combine the components into a standardized format
    date_standardized = f"{year:04d}-{month:02d}-{day:02d}"
    return datetime.strptime(date_standardized, "%Y-%m-%d")

def get_driver(is_eager=False, disable_images=False, is_none=False):
    service = Service(executable_path="chromedriver")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--lang=en")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    )
    options.add_argument("--no-sandbox")
    
    if is_none:
        options.page_load_strategy = 'none'
    if is_eager:
        options.page_load_strategy = 'eager'   # https://www.selenium.dev/documentation/webdriver/drivers/options/#pageloadstrategy
    if disable_images:
        options.add_argument('--blink-settings=imagesEnabled=false')  # Disable image loading
        
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    return driver

def create_unique_object_id():
    now = datetime.now()
    formatted_value = now.strftime("%y%m%d%f")
    return formatted_value

def save_image(url, website_name):
    start_time = time.time()
    res = requests.get(url)
    prefix = f'.{res.headers["Content-Type"].split("/")[1]}'

    if prefix.lower() in ('.jpeg', '.png', '.jpg', '.gif', '.tiff', '.webp', '.avif', '.apng', '.svg', '.bpm', '.ico'):
        pass
    else:
        return "None"
        
    print("response received")
    today = datetime.today()
    dir_name = f"scrap_results/{today.strftime('%Y-%m-%d')}/images/{website_name}/"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    file_name = f"{create_unique_object_id()}{prefix}"
    print(file_name)
    image_path = f"{dir_name}{file_name}"

    with open(image_path, "wb") as file:
        print("file creation started")
        file.write(res.content)
        print("file creation ended")
    print("total time:", time.time() - start_time)
    # dir_name = f"scrap_results/{today.strftime('%Y-%m-%d')}"
    return file_name, dir_name

def save_and_upload_image(url, website_name):
    
    output = save_image(
        url=url, website_name=website_name)
    if output == "None":
        return output
    else:
        file_name, dir_name = output
        if file_name and dir_name:
            image_path = f"{dir_name}{file_name}"
    today = datetime.today()
    # date/images/websitename
    folder_name = today.strftime("%Y-%m-%d")
    folder_id = create_folder(
        folder_name=folder_name, credentials_path=credentials_path)
    subfolder_name = "images"
    subfolder_id = create_sub_folder(
        subfolder_name=subfolder_name, parent_folder_id=folder_id, credentials_path=credentials_path)
    website_name = website_name
    subfolder_id = create_sub_folder(
        subfolder_name=website_name, parent_folder_id=subfolder_id, credentials_path=credentials_path)

    image_link = upload_file(
        credentials_path=credentials_path, folder_id=subfolder_id, file_path=image_path, parent_folder_id=folder_id)
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    return file_name, image_link

# save_and_upload_image("https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F269663689%2F289180297749%2F1%2Foriginal.20220420-052816?w=512&auto=format%2Ccompress&q=75&sharp=10&rect=0%2C75%2C1284%2C642&s=e29d0238f8a65a6644e27bede67b81f9", 'miamiandbeaches.com')