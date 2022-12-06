# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# Step 1: Get the current job listings from NASA
# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

import os
import pandas as pd
import pymongo
import time
from bs4 import BeautifulSoup
from tempfile import mkdtemp
from twilio.rest import Client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_element_by_xpath(xpath):
    """
    Description: Simply returns the HTML element given the xpath.
    :param xpath (str): the xpath of the element you want to get.
    :return: xpath
    """
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )

    return element

# Declaring some much needed variables
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
NASA_JOB_URL = os.getenv("NASA_JOB_URL")

# Creating the options our web driver should have
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--headless")

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

# Actually creating the web driver and giving it the options we specified
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    
    # Opening up the URL
    driver.get(url=NASA_JOB_URL)

    # Waiting to ensure all HTML elements have loaded
    time.sleep(15)
    
    # Testing and/or waiting to see if the html table is present
    tableXPATH = "/html/body/div[3]/div[2]/div/div[2]/div/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/div/table"
    table = get_element_by_xpath(tableXPATH)

    # Getting the scrollbar so we can scroll down
    scrollbarXPATH = "/html/body/div[3]/div[2]/div/div[2]/div/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]"
    scrollbar = get_element_by_xpath(scrollbarXPATH)

    # Scrolling to the bottom of the html table since it dynamically loads as you scroll down
    scroll = 0
    while scroll < 20:
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', scrollbar)
        scroll += 1
        time.sleep(2)

    # Getting the page source now that we know the html table has loaded
    html = driver.page_source

    # Feeding the html into Beautiful Soup
    soup = BeautifulSoup(html, "html.parser")

    # Getting the Internship table
    internshipTable = str(soup.find_all("table", {"aria-label": "Internships"}))

    # Creating a data frame to be able to better analyze the data
    internshipDF = pd.read_html(internshipTable)
    internshipDF = internshipDF[0]

    # Standardizing the column names so we can query them
    internshipDF.columns = internshipDF.columns.str.replace(' ', '_')
    internshipDF.columns = internshipDF.columns.str.replace('Column_Actions', '')
    internshipDF.columns = internshipDF.columns.str.replace('Sort', '')
    internshipDF.columns = internshipDF.columns.str.replace("Stateed_Ascending", "State")
    internshipDF.columns = internshipDF.columns.str.replace("Stateed_Descending", "State")
    internshipDF['Academic_Level'] = internshipDF['Academic_Level'].fillna("Not Specified")

    # Filtering out any jobs we aren't interested in
    internshipDF = internshipDF.query("Activity_Type == 'Virtual' | Activity_Type == 'In-person / Virtual'")
    internshipDF = internshipDF.query("State == 'Florida'")    
    internshipDF = internshipDF[internshipDF["Academic_Level"].str.contains("Graduate Master's")]

    # Resetting the index since we removed some listings
    internshipDF.reset_index(drop = True, inplace = True)

except Exception as e:

    # Still raising the error so we have it in our logs
    raise(e)
    
finally:

    # If the web driver is still running. . .
    if driver.session_id:

        # Closing the web driver to free up system resources
        driver.quit()


# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# Step 2: Get the job listings we've already known about from our database and extract the new job listings
# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# Connecting to MongoDB
client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)

# Specifying which database to use
db = client["NasaJobFinder"]

# Specifying our collection within the database
collection = db["main"]

# Getting all of the documents within the collection
cursor = collection.find({})

# Converting cursor to the list of dictionaries
oldListings = list(cursor)

# If the collection already has some documents within it. . .
if collection.count_documents({}) != 0:

    # Converting everything we received from the cursor into a data frame
    oldListingsDF = pd.DataFrame(oldListings)
    oldListingsDF = oldListingsDF.drop('_id', axis=1)

    # Merging the new and old job listings 
    #internshipDF.append(oldListingsDF, ignore_index=False, verify_integrity=False, sort=None)

    # Getting our list of job listings we already know about
    oldListings = set(oldListingsDF['Short_Title'].tolist())

    # Getting the current job listings as a list
    currentListings = set(internshipDF['Short_Title'].tolist())

    # These are the new job listings
    newListings = currentListings - oldListings

else: # This is true if there are no documents in the collection (Ex. first time running this script)

    # Getting the current job listings as a list
    currentListings = set(internshipDF['Short_Title'].tolist())

    # These are the new job listings
    newListings = currentListings - set(oldListings)


# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# Step 4: Sending out the alert of new job listings
# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# If we have new job listings to notify about. . .
if len(newListings) != 0:

    # Connecting to Twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # Creating the body of the message that we want to send
    payload = f"""---NASA JOB ALERT---\n\
    You have {len(newListings)} job(s) to potentially apply for! \n
    """

    # Dynamically adding job listings to the body of the message
    for listing in newListings:
        payload += f"• {listing} \n \n"

    # Actually sending the alert notification
    message = client.messages.create(
        to = RECIPIENT_PHONE_NUMBER, 
        from_= TWILIO_PHONE_NUMBER,
        body = payload)
    
    # *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
    # Step 4b: Updating the database if there are new listings
    # *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

    # Clearing out so we can insert the new job listings
    collection.delete_many({})

    # For each listing, adding it to the database
    for listing in currentListings:

        # Actually inserting the data into the collection
        collection.insert_one({"Short_Title": f"{listing}"})
