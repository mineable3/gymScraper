import time
import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# To Save Cords
class coordinates: 
    def __init__(self):
    
        try:
            with open("/home/mineable3/file_hole/gymScraper/cordGraph.csv", "x", newline='') as cordFile:
                writer = csv.writer(cordFile)
                writer.writerow(["Month", "Day", "Day_of_Week" ,"Time", "Occupancy"])
        except:
            print("/home/mineable3/file_hole/gymScraper/cordGraph.csv present")
              
    def saveCord(xCord, yCord):
        with open("/home/mineable3/file_hole/gymScraper/cordGraph.csv", "a", newline='') as cordFile:
            month = xCord.split()[1]
            day = xCord.split()[2]
            day_of_week = xCord.split()[0]
            time = xCord.split()[3]
            writer = csv.writer(cordFile)
            writer.writerow([month, day, day_of_week, time, yCord])
        
if __name__ == "__main__":
    # Configure Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--log-level=3") # Suppress logs
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"]) # Suppress DevTools logs

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://app.safespace.io/api/display/live-occupancy/86fb9e11")  # <-- not the API, the real page with the span
     
    # Driver
    try:
        occupancy = ""
        tries = 0

        print("Try #: ", end='')

        # Keep looking at that element until occupancy gets a value
        while not occupancy:
            occupancy = driver.find_element('id', "occupants").text
            tries += 1
            print(f"{tries} ", end='')
            
        coordinates.saveCord(time.ctime(), occupancy)
        print(f"At {time.ctime()}, occupancy: " + occupancy)
    except:
        with open("/home/mineable3/file_hole/gymScraper/cordGraph.csv", "a", newline='') as cordFile:
            writer = csv.writer(cordFile)
            writer.writerow(["Error", "Failed to Pull Data at " + time.ctime()])
        
    driver.quit()
