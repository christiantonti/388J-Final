from google.oauth2 import service_account
from googleapiclient.discovery import build

CAL_ID = 'jh2e08hc78hqbsmp4ctrojug2o@group.calendar.google.com'

credentials = service_account.Credentials.from_service_account_file(
    'cmsc388j-final-350220-85de6fe1bed5.json')

scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/calendar.events'])

service = build('calendar', 'v3', credentials=scoped_credentials)