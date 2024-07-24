from datetime import datetime

def convert_to_ist_time(sql_server_time):
    formatted_time = sql_server_time.strftime("%d %B at %I:%M %p")
    return formatted_time