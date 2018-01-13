import datetime, time
import os, errno

#global funtion here
GDRIVE_FOLDER = "/home/pi/drive"

def get_current_timestamp():
    return time.time()

def get_current_timestamp_str(displayType):
    return time.strftime(displayType)

def get_server_time():
    now = datetime.datetime.fromtimestamp(get_current_timestamp())
    return now

def get_saving_dir():
    return get_year_folder()

def get_year_folder():
    now = get_server_time()
    folder_year = GDRIVE_FOLDER+"/"+str(now.year)
    if not os.path.exists(folder_year): 
       try:
           os.makedirs(folder_year)
       except OSError as e:
           raise
    return get_month_folder(folder_year)

def get_month_folder(folder_name):
    now = get_server_time()
    folder_name += "/"+str(now.month)
    if not os.path.exists(folder_name):
       try:
           os.makedirs(folder_name)
       except OSError as e:
           raise
    
    return get_day_folder(folder_name)
    
def get_day_folder(folder_name):
    now = get_server_time()
    folder_name += "/"+str(now.day)
    if not os.path.exists(folder_name):
       try:
           os.makedirs(folder_name)
       except OSError as e:
           raise
    return folder_name
    
