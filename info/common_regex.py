import re
from django.db import connection,IntegrityError,transaction

def validate_name(name):
    if re.match(r"^(?=.{2,50}$)[a-zA-Z]+(?:[ '-][a-zA-Z]+)*$",name.strip()):
        return True
    return False

def validate_mobile_number(mobile_number):
    if re.match(r'^\d{10}$', mobile_number.strip()):
        return True
    return False

def validate_email(email):
    if re.match(r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$', email.strip()):
        return True
    return False