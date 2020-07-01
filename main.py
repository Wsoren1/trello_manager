from Slackbot import Slackbot
from TrelloBoard import TrelloBoard
from DatabaseManager import DatabaseManager
from time import sleep
import json
import threading
import datetime
from difflib import SequenceMatcher


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def overdue_check(TB, DM):
    SB = Slackbot()

    with open('data/OverdueBufferCheck.txt', 'r') as f:
        ids = f.readlines()
        ids = [id[:-1] for id in ids]

    with open('data/active.json', 'r') as f:
        j = json.load(f)

    obj = None

    for j_obj in j:
        if ids[0] == j_obj['id']:
            obj = j_obj
    if obj is not None:
        title = obj["name"]

        SB.send_message(SB.construct_text("due_passed", title))

        while SB.get_last_user_message() is '':
            sleep(4)

        response = SB.get_last_user_message()

        highest_similarity = similarity(response, "Excused")  # convert to array comparison instead of if chain

        log = ''

        if highest_similarity < similarity(response, "Task Overload"):
            highest_similarity = similarity(response, "Task Overload")
            log = "task_overload"
        if highest_similarity < similarity(response, "Forgot to Update"):
            highest_similarity = similarity(response, "Forgot to Update")
            log = "forgot_update"
        if highest_similarity < similarity(response, "Ambitious Due Date"):
            log = 'ambitious_due_date'

        SB.send_message(SB.construct_text("set_due_date"))

        while SB.get_last_user_message() is '':
            sleep(4)

        response = SB.get_last_user_message()

        response = response.split(' ')

        days_to_extend = int(response[0])

        if similarity(response[1], "days") < similarity(response[1], "weeks"):
            days_to_extend = days_to_extend * 7

        new_deadline = datetime.datetime.today() + datetime.timedelta(days=days_to_extend)

        query = {}
        query['due'] = new_deadline.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        DM.edit_object(obj['id'], 'overdue_log', [log])
        TB.set_card_query(obj['id'], query)

        SB.send_message(SB.construct_text("thank_for_data"))


def overdue_loop(TB, DM):
    last_run = datetime.datetime.now()
    while True:
        with open('OverdueBufferCheck.txt', 'r') as f:
            pass
        if last_run - datetime.datetime.now() > datetime.timedelta(hours=2):
            overdue_check(TB, DM)


with open('settings.json', 'r') as file:
    settings = json.loads(file.read())
    refresh_time = settings["refresh_time"]

TB = TrelloBoard()
DM = DatabaseManager()

last_run = datetime.datetime.now() + datetime.timedelta(hours=2)

while True:  # loop that bot will run tasks
    TB.light_update_self()
    DM.update_archive()

    if last_run - datetime.datetime.now() < datetime.timedelta(hours=0):
        overdue_check(TB, DM)
        last_run = datetime.datetime.now() + datetime.timedelta(hours=2)

    # Extract data
    # run data processing script
    # push any re-occuring tasks to appropriate board
    # separate active tasks from previous tasks
    sleep(refresh_time)
