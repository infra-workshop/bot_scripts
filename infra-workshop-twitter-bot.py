#!/usr/bin/python3
# vim: set fileencoding=utf-8 :

# require `export PYTHONIOENCODING=utf-8`
import os

import requests
import json

from datetime import datetime, timedelta, timezone
from subprocess import call

import post_twitter

# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CLIENT_SECRET_FILE = BASE_DIR + '/client_id.json'
# APPLICATION_NAME = 'iw-post-workshop-announce'
# CALENDAR_ID = "phq7gugri9ra9mcpq0rr37rrp56bllrv@import.calendar.google.com"
# SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

DEBUG = True
def log(msg):
    if DEBUG:
        f = open(BASE_DIR + "/run.log","a")
        f.write(str(msg) + "\n")
        f.close()

JST = timezone(timedelta(hours=+9), 'JST')
# def iso_to_jstdt(iso_str):
#     dt = datetime.strptime(iso_str, '%Y-%m-%dT%H:%M:%SZ')
#     dt = dt.replace(tzinfo=timezone.utc)
#     dt = dt.astimezone(JST)
#     return dt

def post_reservation_by_at(message,time="now"):
    command = "/bin/echo python3 \"" + BASE_DIR + "/post_twitter.py \'" + message + "\'\" | /usr/bin/at " + time
    command = command.replace('\n','\\\\n')
    log("----")
    log(command)
    ret = call(command, shell=True)
    log(ret)
    return ret

# ### GOOGLE ###
# def get_credentials():
#     credential_dir = os.path.join(BASE_DIR, '.credentials')
#     if not os.path.exists(credential_dir):
#         os.makedirs(credential_dir)
#     credential_path = os.path.join(credential_dir,
#                                    'calendar-python-googleapi.json')
 
#     store = Storage(credential_path)
#     credentials = store.get()
#     if not credentials or credentials.invalid:
#         flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
#         flow.user_agent = APPLICATION_NAME
#         if flags:
#             credentials = tools.run_flow(flow, store, flags)
#         else: # Needed only for compatibility with Python 2.6
#             credentials = tools.run(flow, store)
#         print('Storing credentials to ' + credential_path)
#     return credentials
 
def main():
    log("main start")
    ### GOOGLE ###
    # # Create credential
    # log("Create credintial")
    # credentials = get_credentials()
    # http = credentials.authorize(httplib2.Http())
    # service = discovery.build('calendar', 'v3', http=http)
 
    # # Create timeobject
    # log("Create timeobject")    
    # sdt = datetime.now(timezone.utc)
    # sdt = sdt.replace(hour=0, minute=0, second=0, microsecond=0)
    # sdt = sdt.isoformat()
    # edt = (datetime.now(timezone.utc) + timedelta(days=1))
    # edt = edt.replace(hour=23, minute=59, second=59)
    # edt = edt.isoformat()

    # # Get Events from Google
    # log("Get Events from Google")    
    # eventsResult = service.events().list(calendarId=CALENDAR_ID, timeMin=sdt, timeMax=edt,singleEvents=True, orderBy='startTime').execute()
    # events = eventsResult.get('items', [])
 
    # # purse event
    # log("Purse")
    # if not events:
    #     log('No events found.')
    # for event in events:
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     start = iso_to_jstdt(start)
    #     day = start.strftime('%Y/%m/%d')
    #     start = start.strftime('%H:%M')
    #     end = event['end'].get('dateTime', event['end'].get('date'))
    #     end = iso_to_jstdt(end)
    #     end = end.strftime('%H:%M')
    #     title = str(event['summary'])
    #     url = "https://wp.infra-workshop.tech/?tribe_events=" + urllib.parse.quote(title.replace(" ","-"))
        
    ### WORDPRESS API ###
    sdt = datetime.now(JST)
    sdt = sdt.replace(hour=0, minute=0, second=0, microsecond=0)
    sdt = sdt.strftime('%Y/%m/%dT%H:%MZ')
    edt = (datetime.now(JST) + timedelta(days=1))
    edt = edt.replace(hour=23, minute=59, second=59, microsecond=0)
    edt = edt.strftime('%Y/%m/%dT%H:%MZ')

    API_URI = 'https://wp.infra-workshop.tech/?rest_route=/tribe/events/v1/events'
    url = API_URI + "&start_date=" + sdt + "&end_date=" + edt
    log(url)
    response = requests.get(url)

    if response.status_code != 200:
        log("error : " + str(response.status_code))
        return

    wss = json.loads(response.text)
    next_post = datetime.now(JST).replace(hour=21, minute=0, second=0, microsecond=0)
    if not "events" in wss:
        log('No events found.')
    for event in wss["events"]:
        title = event["title"]
        url = event["url"]
        esd = event["start_date_details"]
        eed = event["end_date_details"]
        day = esd["year"] + "/" + esd["month"]  + "/" + esd["day"]
        day_s = "(" + esd["month"]  + "/" + esd["day"] + ")"
        start = esd["hour"] + ":" + esd["minutes"]
        end = eed["hour"] + ":" + eed["minutes"]

        log(start + "-" + end + "\n" + title)
        if day == datetime.now(JST).date().strftime('%Y/%m/%d'):
            end_datetime = datetime(tzinfo=JST, year=int(eed["year"]),month=int(eed["month"]),day=int(eed["day"]) ,hour=int(eed["hour"]), minute=int(eed["minutes"]),)
            if next_post < end_datetime:
                next_post = end_datetime
            log("Today Workshop")
            word = "今日" + day_s + "の #インフラ勉強会 は...\n" + title + "\n" + start + " - " + end + "\n" + url
            post_reservation_by_at(word, "now + 1min")

            word = "今日" + day_s + "の勉強会がそろそろ始まるよ！\n" + title + "\n" + start + " - " + end + "\n" + url + "\n#インフラ勉強会"
            post_reservation_by_at(word, start + " - 30min")

            word = "勉強会が始まるよ！ 本日のお題は...\n" + title + "\n" + url + "\n#インフラ勉強会"
            post_reservation_by_at(word, start)

        if day == (datetime.now(JST) + timedelta(days=1)).date().strftime('%Y/%m/%d'):
            log("Next Workshop")
            next_post_time = next_post.strftime('%H:%M')
            word = "#インフラ勉強会 、次回" + day_s + "は...\n" + title + "\n" + start + " - " + end + "\n" + url
            post_reservation_by_at(word, next_post_time)

    log("end main")

if __name__ == '__main__':
    main()