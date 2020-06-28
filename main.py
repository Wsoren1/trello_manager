import datetime as dt
from time import sleep
import json


with open('settings.json', 'r') as file:
    settings = json.loads(file.read())
    refresh_time = settings["refresh_time"]


while True:  # loop that bot will run tasks
    # Extract data
    # run data processing script
    # push any re-occuring tasks to appropriate board
    # separate active tasks from previous tasks
    sleep(settings["refresh_time"])
