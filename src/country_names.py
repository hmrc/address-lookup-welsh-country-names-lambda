import time
from tempfile import mkdtemp

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from waiting import wait

import os
import logging
import boto3

from botocore.exceptions import ClientError

bucket_name = os.environ["BUCKET_NAME"]
chrome_path = os.environ.get("CHROME_PATH", '/opt/chrome/chrome')
chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/opt/chromedriver")

base_url = "https://www.gov.wales/bydtermcymru/international-place-names"
download_location = "/tmp/"
downloaded_file_name = "download"
downloaded_file_absolute_path = download_location + downloaded_file_name

# NB for debugging you can use
# driver.save_screenshot("ss.png")


def is_file_size_static(file_absolute_path):
    initial = os.path.getsize(file_absolute_path)
    time.sleep(1)
    final = os.path.getsize(file_absolute_path)
    return initial == final


def create_driver_object():
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_path
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")
    prefs = {"download.default_directory": download_location}
    options.add_experimental_option("prefs", prefs)

    service = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=options)


def download_data(event=None, context=None):
    driver = create_driver_object()
    selenium_wait = WebDriverWait(driver, 30)

    driver.get(base_url)
    # print("got")

    driver.implicitly_wait(2)

    # footer = driver.find_element(By.ID, "page-feedback-link")
    # footer.location_once_scrolled_into_view
    # driver.save_screenshot("ss2.png")

    element = driver.find_element(By.PARTIAL_LINK_TEXT, "Enwau gwledydd – Country names")
    element.click()

    # print("clicked")

    wait(lambda: os.path.exists(downloaded_file_absolute_path), timeout_seconds=30, waiting_for=downloaded_file_name + " to exist")
    wait(lambda: is_file_size_static(downloaded_file_absolute_path), timeout_seconds=360, waiting_for=downloaded_file_name + " to finish downloading")

    return downloaded_file_absolute_path


def upload_to_s3(file_name, bucket, object_name = None):
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def handler(event=None, context=None):
    print(bucket_name)
    print(chrome_path)
    print(chromedriver_path)

    report_file = download_data()
    upload_to_s3(report_file, bucket_name, "welsh-country-names.csv")