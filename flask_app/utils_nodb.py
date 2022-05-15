from datetime import datetime
from enum import Enum

# returns datetime as a more human-readable string
def date_str(date):
    return date.strftime("%m/%d/%y @ %H:%M:%S")

# return fresh datetime now
def now():
    return datetime.now()


# returns current time as a string for logging
def current_time() -> str:
    return date_str(datetime.now())

# ***** FORM CREATION STUFF *****
class FormField(Enum):
    STRING_FIELD = 1
    INT_FIELD = 2
    BOOL_FIELD = 3
    EMAIL_FIELD = 4