#webdaten abrufen 
from time import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from datetime import datetime
# search function in csv
import csv
from io import StringIO


def get_train_journey(zugnummer, fahrdatum, eva_haltestelle):

    request = f"https://bahn.expert/details/{zugnummer}/{fahrdatum}"

    # Set up the webdriver options
    options = Options()
    options.headless = True

    # Set up the webdriver
    try:
        driver = webdriver.Edge(options=options)

        # Open the website
        driver.get(request)

        # Wait for the page and scripts to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, eva_haltestelle)))

        # save the hole page in a variable
        train_content = driver.find_element(By.TAG_NAME, "header").get_attribute("innerHTML")
        stop_content = driver.find_element(By.TAG_NAME, "main").get_attribute("innerHTML")
        
        main_content = train_content + stop_content
        
        # Close the webdriver
        driver.quit()

        #safe content in file with name of train and the fahrdatum but convert the fahrdatum to only the date
        with open(f"Requests/{zugnummer}_{datetime.strptime(fahrdatum, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')}.html", "w", encoding="utf-8") as f:
            f.write(main_content)

        return main_content
    
    except Exception as e:
        return e

# function that searches for the station in the csv file and retuns the eva number 
def search_station(bahnhof_name):
    # search for the station in the csv file
    data = open("Verzeichnis/bahnhofsverzeichnis.csv", "r").read()
    f = StringIO(data)
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        if row['NAME'] == bahnhof_name:
            return row['EVA_NR']
    return "Station not found"

def get_train_delay(zugnummer, fahrdatum, eva_startbahnhof, eva_endbahnhof):
    # wenn Request file schon vofhanden ist, dann wird dieser verwendet
    # wenn nicht, dann wird ein neuer Request gemacht
    try:
        with open(f"Requests/{zugnummer}_{datetime.strptime(fahrdatum, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')}.html", "r") as f:
            main_content = f.read()
    except:
        main_content = get_train_journey(zugnummer, fahrdatum, eva_startbahnhof)
    
    # get the delay of the train normal time is in span class "css-1q01wyw ebj7okp0" and delay time in span class "css-lia0q ebj7okp0"

    # get the start time of the train
    try:
        start_time = main_content.split(f"id=\"{eva_startbahnhof}\"")[1].split("css-1q01wyw ebj7okp0")[1].split(">")[1].split("<")[0]
    except:
        start_time = "NONE"
    
    # get the delay of the train
    try:
        start_delay = main_content.split(f"id=\"{eva_startbahnhof}\"")[1].split("css-lia0q ebj7okp0")[1].split(">")[1].split("<")[0]
    except:
        start_delay = "NONE"

    # get the end time of the train
    try:
        end_time = main_content.split(f"id=\"{eva_endbahnhof}\"")[1].split("css-1q01wyw ebj7okp0")[1].split(">")[1].split("<")[0]
    except:
        end_time = "NONE"

    # get the delay of the train
    try:
        end_delay = main_content.split(f"id=\"{eva_endbahnhof}\"")[1].split("css-lia0q ebj7okp0")[1].split(">")[1].split("<")[0]
    except:
        end_delay = "NONE"
    
    try:
        association = main_content.split("css-gjnfod er6s5zm4")[1].split(">")[1].split("<")[0] 
    except:
        association = "NONE"

    try: 
        # berechne den unterschied zwichen start_time und start_delay und gib es in minuten aus
        formatet_time = datetime.strptime(start_time, '%H:%M')
        formatet_delay = datetime.strptime(start_delay, '%H:%M')
        start_delay_min =  formatet_delay - formatet_time
        start_delay_minutes = int(start_delay_min.seconds / 60)
        
    except:
        start_delay_minutes = "NONE"
    
    try:
        # berechne den unterschied zwichen end_time und end_delay und gib es in minuten aus
        formatet_time = datetime.strptime(end_time, '%H:%M')
        formatet_delay = datetime.strptime(end_delay, '%H:%M')
        end_delay_min =  formatet_delay - formatet_time
        end_delay_minutes = int(end_delay_min.seconds / 60)
    except:
        end_delay_minutes = "NONE"
    
    
    return association, start_time, start_delay, start_delay_minutes, end_time, end_delay, end_delay_minutes


print(get_train_delay("ICEw370", "2023-03-07T13:38:22.369Z", search_station("Basel Bad Bf"), search_station("Berlin Ostbahnhof")))