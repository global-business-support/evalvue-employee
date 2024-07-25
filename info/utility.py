from datetime import datetime
import logging
from .response import *
from django.db import connection,IntegrityError,transaction
from info import constant
import os
from Evalvue_Employee import settings
import uuid

logger = logging.getLogger('info')

def save_image(folder_name,image):
    project_root = settings.BASE_DIR
    

    # Construct the full path for the folder
    folder_path = os.path.join(project_root, folder_name)
    folder_db_path = os.path.join(constant.database_root,folder_name)

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Construct the full path for the file
    unique_id = uuid.uuid4()
    file_path = os.path.join(folder_path,str(unique_id) + image.name)
    file_db_path = folder_db_path + "/" + str(unique_id) + image.name

    with open(file_path, 'wb') as destination:
        for chunk in image.chunks():
            destination.write(chunk)
    return file_db_path

def capitalize_words(s):
    return s.upper()

def convert_to_ist_time(sql_server_time):
    formatted_time = sql_server_time.strftime("%d %B at %I:%M %p")
    return formatted_time

def validate_employee_on_edit(employee_id,email,mobile_number,aadhar_number,res):
    if not mobile_number and not aadhar_number:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Email from Employee WHERE EmployeeId != %s and Email = %s",[employee_id,email])
            result = cursor.fetchone()
            if result:
                res.employee_edit_sucessfull = False
                res.error = constant.email_already_exist_error
                return True
    if not email and not aadhar_number:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MobileNumber from Employee WHERE EmployeeId != %s and MobileNumber = %s",[employee_id,mobile_number])
            result = cursor.fetchone()
            if result:
                res.employee_edit_sucessfull = False
                res.error = constant.mobile_number_already_exist_error
                return True
    if not email and not mobile_number:
        with connection.cursor() as cursor:
            cursor.execute("SELECT AadharNumber from Employee WHERE EmployeeId != %s and AadharNumber = %s",[employee_id,aadhar_number])
            result = cursor.fetchone()
            if result:
                res.employee_edit_sucessfull = False
                res.error = constant.aadhar_number_already_exist_error
                return True
            
ALLOWED_EXTENSIONS = {'.png', '.jpeg', '.jpg'}
def validate_file_extension(image,res):
    try:
        file_extension = os.path.splitext(image.name)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            res.is_image_validate = True
            res.error = constant.file_validation_extension_error
            return False
        else:
            return True
    except Exception as e:
        logger.exception('An unexpected error occurred: {}'.format(str(e)))
        return False

def validate_file_size(image,res):
    try:
        file_size = 1024 * 1024 * 2  #2MB file
        if image.size > file_size:
            res.is_file_validate = True
            res.error = constant.file_validation_size_error
            return False
        else:
            return True
    except Exception as e:
        logger.exception('An unexpected error occurred: {}'.format(str(e)))
        return False
def delete_file(file_path):
    try:
        # Check if the file exists
        if os.path.isfile(file_path):
            os.remove(file_path)
            return True
        else:
            return False
    except Exception as e:
        logger.exception('An unexpected error occurred: {}'.format(str(e)))
        return False    
def extract_path(url):
    # Split the URL by '/' and join the necessary parts
    parts = url.split('/')
    extracted_path = '/'.join(parts[4:])
    return extracted_path



