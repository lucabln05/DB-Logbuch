#https://chaos.social/@marudor
#https://v6.db.transport.rest/api.html#get-tripsid
#locale scripts
import Verzeichnis.stationssearchfunction as search

#webdaten abrufen von bahn.expert
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options

#time
from datetime import datetime, timedelta
from time import time

#api abrufen
import requests


def get_tripid_api(zugnummer, fahrdatum, eva_startbahnhof, eva_endbahnhof):
    #https://v6.db.transport.rest/journeys?from=8000191&to=8000290&departure=2023-03-08T20:42
    # eine stunde abziehen, da api wenn genau gleiche uhrzeit wie fahrplan, zuverlässigen daten zurückgibt, wenn man ihr 20 uhr gibt, dann zeigt sie nur 21 uhr an dehalb eine stunde weniger
    fahrdatum = datetime.strptime(fahrdatum, '%Y-%m-%dT%H:%M')
    fahrdatum = fahrdatum - timedelta(hours=1)
    fahrdatum = fahrdatum.strftime('%Y-%m-%dT%H:%M')

    url = f'https://v6.db.transport.rest/journeys?from={eva_startbahnhof}&to={eva_endbahnhof}&departure={fahrdatum}'
    response = requests.get(url)
    print(url)
    if response.status_code == 200:
        data = response.json()
        try:
            for journey in data['journeys']:
                for leg in journey['legs']:
                    if leg['line']['name'] == zugnummer:
                        return leg['tripId']
        except Exception as e:
            return e
            

def get_trip_api(tripId, eva_startbahnhof, eva_endbahnhof):

    url = f'https://v6.db.transport.rest/trips/{tripId}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        try:


            for stopovers in data['trip']['stopovers']:
                        if stopovers['stop']['id'] == eva_startbahnhof:
                            plannedDeparture = stopovers['plannedDeparture']
                            departure = stopovers['departure']
                            try:
                                departureDelay = int(stopovers['departureDelay']/60)
                            except:
                                departureDelay = 0
                        if stopovers['stop']['id'] == eva_endbahnhof:
                            plannedArrival = stopovers['plannedArrival']
                            arrival = stopovers['arrival']
                            try:
                                arrivalDelay = int(stopovers['arrivalDelay']/60)
                            except:
                                arrivalDelay = 0
            operator_name = data['trip']['line']['operator']['name']
            name = data['trip']['line']['name']
            fahrtNr = data['trip']['line']['fahrtNr']
            try:
                loadFactor = data['trip']['loadFactor']
            except:
                loadFactor = "Not Available"

            if departureDelay == 0 and arrivalDelay == 0:
                zugnummer = data['trip']['line']['productName'] + fahrtNr
                print(f"https://bahn.expert/details/{zugnummer}/{data['trip']['plannedDeparture']}")
                return get_train_delay_marudor(zugnummer, data['trip']['plannedDeparture'], eva_startbahnhof, eva_endbahnhof)
                
            return plannedDeparture, departure, departureDelay, plannedArrival, arrival, arrivalDelay, operator_name, name, fahrtNr, loadFactor
        
        except:
            return "Train not found"
    





def get_train_journey_marudor(zugnummer, fahrdatum, eva_haltestelle):

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

        return main_content
    
    except Exception as e:
        return e


def get_train_delay_marudor(zugnummer, fahrdatum, eva_startbahnhof, eva_endbahnhof):
    # wenn Request file schon vofhanden ist, dann wird dieser verwendet
    # wenn nicht, dann wird ein neuer Request gemacht

    main_content = get_train_journey_marudor(zugnummer, fahrdatum, eva_startbahnhof)
    
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


#print(get_train_delay_marudor("ICE 377", "2023-03-08T16:38:22.369Z", search.station_api("Karlsruhe Hbf"),  search.station_api("Basel Bad Bf")))

#trip_id = get_tripid_api("MEX 17a", "2023-03-08T20:00", search.station_api("Enzberg"), search.station_api("Mühlacker"))
tripid = get_tripid_api("MEX 17a", "2023-03-09T10:53", search.station_api("Enzberg"), search.station_api("Mühlacker"))
print(get_trip_api(tripid, search.station_api("Enzberg"), search.station_api("Mühlacker")))

