from flask import Blueprint, render_template, url_for, redirect, request, flash, jsonify
from flask_login import current_user
import datetime

from . import service, CAL_ID


calendar = Blueprint("calendar", __name__)

""" ************ API functions ************ """
# Separated these out to keep Google API stuff completely separate

# these are routes so I can test them in browser
# ***** CALENDAR DATA ROUTES *****
@calendar.route("/getEvents", methods=["GET", "POST"])
def getEvents():
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId=CAL_ID, timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
    events = events_result.get('items', [])
    print(events)
    return jsonify(events)

# not a route but idk
def createEvent(name, desc, start, end):
    body = {
        "summary": name,
        "description": desc,
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": "America/New_York"
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": "America/New_York"
        }
    }
    event = service.events().insert(calendarId=CAL_ID, body=body).execute()
    return event['id']
