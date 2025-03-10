import logging
from django.http import HttpResponse
from django.http import JsonResponse
import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.db import connection,IntegrityError,transaction
from Evalvue_Employee import settings
from datetime import datetime, timedelta
import datetime
from django.db import connection,IntegrityError,transaction

from info.utility import convert_to_ist_time

from .employee import *
from .response import *
from  .constant import *
from .organization import *
from  .review import *
from .common_regex import *
from .utility import *

logger = logging.getLogger('info')

def hello_world(request):
    return HttpResponse("Hello, World!")

class ShootOtpToEmployeeAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                employee_email = data.get("employee_email")
                if not employee_email:
                    res.error = 'Email is required.'
                else:
                    url = settings.evalvue_started_api + 'shoot/otp/'
                    data = {
                        'email': employee_email,
                        'login_employee':True,
                    }
                    response_data = requests.post(url, json=data)
                    data = response_data.json()
                    if response_data.status_code == 200:
                        res.employee_id = data.get("employee_id")
                        res.employee_email = data.get("email")
                    else:
                        res.otp_send_successfull = data.get("otp_send_successfull")
                        res.error = data.get("error")
                return JsonResponse(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.otp_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.otp_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOtpLoginAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                employee_email = data.get("employee_email")
                otp = data.get("otp")
                res.otp_verified_successfull = False
                if not otp:
                    res.error = 'OTP is required.'
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT OtpNumber,CreatedOn from OTP where email = %s ORDER BY CreatedOn desc",[employee_email])
                        otp_result = cursor.fetchone()
                        if otp_result:
                            cursor.execute("SELECT GETDATE()")
                            sql_server_time = cursor.fetchone()[0]
                            created_on = otp_result[1]
                            created_time = datetime.datetime.strptime(str(created_on), '%Y-%m-%d %H:%M:%S.%f')  # Convert created_time string to datetime object
                            expiration_time = created_time + timedelta(minutes=2)
                            if sql_server_time > expiration_time:
                                res.otp_is_expired = True
                                res.error = 'OTP is expired.'
                            elif otp != otp_result[0]:
                                res.incorrect_otp = True
                                res.error = 'Incorrect OTP.'
                            elif otp_result[0] == otp:
                                res.otp_verified_successfull = True

                        return Response(res.convertToJSON(), status=status.HTTP_200_OK)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.otp_verified_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.otp_verified_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EmployeeOrganizationDataPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                employee_id = data.get("employee_id")
                with connection.cursor() as cursor:
                    cursor.execute("SELECT Distinct o.OrganizationId, CONVERT(VARCHAR(MAX), o.[Image]) AS [Image], CONVERT(VARCHAR(MAX), o.Area) AS Area FROM Organization o JOIN [EmployeeOrganizationMapping] eom ON eom.OrganizationId = o.OrganizationId WHERE EmployeeId = %s",[employee_id])
                    rows = cursor.fetchall()
                    if rows:
                        organizaton_list = []
                        for row in rows:
                            org = organization()
                            org.organization_id = row[0]
                            org.image = row[1]
                            org.area = row[2]
                            organizaton_list.append(org.to_dict())
                        res.organization_list = organizaton_list
                        res.organization_data_send_successfull = True
                        return Response(res.convertToJSON(), status=status.HTTP_200_OK)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.organization_data_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.organization_data_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeReviewDatAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                employee_id = data.get("employee_id")
                organization_id = data.get("organization_id")
                with connection.cursor() as cursor:
                    cursor.execute("SELECT rem.ReviewId,r.Comment,r.Rating,r.CreatedOn,r.Image,org.OrganizationId,org.Name,org.Image,rem.IsReported FROM ReviewEmployeeOrganizationMapping rem JOIN Review r ON rem.ReviewId = r.ReviewId JOIN Organization org ON rem.OrganizationId = org.OrganizationId JOIN Employee emp ON rem.EmployeeId = emp.EmployeeId where rem.EmployeeId = %s and rem.OrganizationId = %s",[employee_id,organization_id])
                    rows = cursor.fetchall()
                    if rows:
                        review_list = []
                        for row in rows:
                            sql_server_time = row[3]
                            formatted_time = convert_to_ist_time(sql_server_time)
                            rev = review()
                            rev.review_id = row[0]
                            rev.comment = row[1]
                            rev.rating = row[2]
                            rev.created_on = formatted_time
                            rev.image = row[4]
                            rev.organization_id = row[5]
                            rev.organization_name = row[6]
                            rev.organization_image = row[7]
                            if row[8] is None:
                                rev.is_reported = 2
                            else:
                                rev.is_reported = row[8]
                            review_list.append(rev.to_dict())
                        res.review_list = review_list
                        res.is_employee_organization_data_send_successfull = True
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_employee_organization_data_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_employee_organization_data_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeDashboardDataAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                logger.info(data)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT rem.ReviewId,r.Comment,r.Rating,r.CreatedOn,r.Image,org.OrganizationId,org.Name,emp.EmployeeId,emp.Name,emp.Designation,org.Image,emp.Image FROM ReviewEmployeeOrganizationMapping rem JOIN Review r ON rem.ReviewId = r.ReviewId JOIN Organization org ON rem.OrganizationId = org.OrganizationId JOIN Employee emp ON rem.EmployeeId = emp.EmployeeId ORDER BY r.CreatedOn DESC")
                    rows = cursor.fetchall()
                    reviews = []
                    if rows:
                        for row in rows:
                            sql_server_time = row[3]
                            formatted_time = convert_to_ist_time(sql_server_time)
                            rev = review()
                            rev.review_id = row[0]
                            rev.comment = row[1]
                            rev.rating = row[2]
                            rev.created_on = formatted_time
                            rev.image = row[4]
                            rev.organization_id = row[5]
                            rev.organization_name = row[6]
                            rev.employee_id = row[7]
                            rev.employee_name = row[8]
                            rev.designation = row[9]
                            rev.organization_image = row[10]
                            rev.employee_image = row[11]
                            reviews.append(rev.to_dict())
                        res.dashboard_list = reviews
                        res.is_review_mapped = True
                    else:
                        res.is_review_mapped = False
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_review_mapped = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_review_mapped = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EmployeeReviewReportPIView(APIView):
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                employee_id = data.get("employee_id")
                organization_id = data.get("organization_id")
                review_id = data.get("review_id")
                report_message = data.get("report_message")
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO Report(Message,CreatedOn) VALUES(%s,GETDATE())",[report_message])
                    cursor.execute("SELECT TOP 1 ReportId FROM Report ORDER BY CreatedOn DESC")
                    report_id = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO ReportReviewEmployeeOrganizationMapping(ReportId,ReviewId,EmployeeId,OrganizationId,CreatedOn,IsReportRejected) VALUES(%s,%s,%s,%s,GETDATE(),%s)",[report_id,review_id,employee_id,organization_id,0])
                    cursor.execute("UPDATE ReviewEmployeeOrganizationMapping set IsReported = 1,ModifiedOn = GETDATE() where ReviewId = %s",[review_id])
                    res.is_report_created_successfull = True
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_report_created_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_report_created_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)      

class EditEmployeeAPIview(APIView):
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                employee_id = data.get("employee_id")
                first_name = capitalize_words(data.get('first_name'))
                last_name = capitalize_words(data.get('last_name'))
                email = data.get("email")
                mobile_number = data.get("mobile_number")   
                employee_image = data.get("employee_image")
                logger.info(data)
                employee_name = first_name.strip() + " " + last_name.strip()
                res.employee_edit_sucessfull = True
                if not validate_name(employee_name):
                    res.employee_edit_sucessfull = False
                    res.error = 'Invalid Name'
                elif not validate_email(email):
                    res.employee_edit_sucessfull = False
                    res.error = 'Invalid email'
                elif not validate_mobile_number(mobile_number):
                    res.employee_edit_sucessfull = False
                    res.error = 'Invalid mobile number'
                if not res.employee_edit_sucessfull:
                    return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                if validate_employee_on_edit(employee_id,email,None,None,res) or validate_employee_on_edit(employee_id,None,mobile_number,None,res):
                    return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                with connection.cursor() as cursor:      
                    cursor.execute("SELECT Image FROM employee WHERE EmployeeId = %s", [employee_id])
                    img = cursor.fetchone()
                    old_image = img[0]
                    if not isinstance(employee_image, str):
                        is_image_valid = validate_file_extension(employee_image,res)
                        is_image_size_valid = validate_file_size(employee_image,res)
                        if is_image_valid and is_image_size_valid:
                            employee_image = save_image(employee_image_path,employee_image)
                            print(employee_image)
                            if old_image:
                                file_path = extract_path(old_image)
                                delete_file(file_path)
                        else:
                            res.employee_edit_sucessfull = False
                            return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                    
                        cursor.execute("update [Employee] set Name = %s, Email = %s, MobileNumber = %s, Image = %s, modifiedOn = GETDATE() WHERE EmployeeId = %s",[employee_name,email,mobile_number,employee_image,employee_id])
                        res.employee_edit_sucessfull = True
                        res.employee_id = employee_id
                        return Response(res.convertToJSON(), status = status.HTTP_201_CREATED)
                    else:
                        cursor.execute("update [Employee] set Name = %s, Email = %s, MobileNumber = %s, modifiedOn = GETDATE() WHERE EmployeeId = %s",[employee_name,email,mobile_number,employee_id])
                        res.employee_edit_sucessfull = True
                        res.employee_id = employee_id
                        return Response(res.convertToJSON(), status = status.HTTP_201_CREATED)

                
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.employee_edit_sucessfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.employee_edit_sucessfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EmployeeProfileAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                employee_id = data.get("employee_id")
                data = request.data
                logger.info(data)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT EmployeeId,Name,Email,MobileNumber,Image,AadharNumber,Designation FROM Employee WHERE EmployeeId = %s",[employee_id])
                    row = cursor.fetchall()
                    print(row)
                    name = row[0][1]
                    parts = name.split()
                    if len(parts) >= 3:
                        first_name = parts[0] + ' ' + parts[1]
                        last_name = parts[2]
                    else:
                        first_name = parts[0]
                        last_name = parts[1]
                    profile = []
                    for emp_id,emp_name,emp_email,emp_mobile,emp_image,emp_aadhar,emp_designation in row:
                        emp = employee()
                        emp.employee_id = emp_id
                        emp.first_name = first_name
                        emp.last_name = last_name
                        emp.email = emp_email
                        emp.mobile_number = emp_mobile
                        emp.image = emp_image
                        emp.aadhar_number = emp_aadhar
                        emp.designation = emp_designation
                        profile.append(emp.to_dict())
                        res.employee_profile = profile
                        res.is_employee_profile_successfull = True
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_employee_profile_successfull  = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_employee_profile_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VerifyReportedReviewDataAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                employee_id = data.get("employee_id")
                logger.info(data)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT rreom.ReviewId, r.Comment, r.rating, rreom.CreatedOn, r.[Image], rreom.[EmployeeId], e.[Name], e.[Image],e.Designation, rreom.[OrganizationId], o.[Name], o.[Image], reom.IsReported, rep.[Message], rreom.ReportId FROM [ReportReviewEmployeeOrganizationMapping] rreom JOIN Report rep ON rep.ReportId = rreom.ReportId JOIN [ReviewEmployeeOrganizationMapping] reom ON reom.ReviewId = rreom.ReviewId JOIN Review r ON r.ReviewId = rreom.ReviewId JOIN Employee e ON e.EmployeeId = rreom.EmployeeId JOIN Organization o ON o.OrganizationId = rreom.OrganizationId WHERE reom.IsReported = 1 and rreom.IsReportRejected = 0 ORDER BY rreom.CreatedOn desc")
                    rows = cursor.fetchall()
                    reported_reviews_list = []
                    if rows:
                        for row in rows:
                            sql_server_time = row[3]
                            formatted_time = convert_to_ist_time(sql_server_time)
                            rev = review()
                            rev.review_id = row[0]
                            rev.comment = row[1]
                            rev.rating = row[2]
                            rev.created_on = formatted_time
                            rev.image = row[4]
                            rev.employee_id = row[5]
                            rev.employee_name = row[6]
                            rev.employee_image = row[7]
                            rev.designation = row[8]
                            rev.organization_id = row[9]
                            rev.organization_name = row[10]
                            rev.organization_image = row[11]
                            rev.is_reported = row[12]
                            rev.message = row[13]
                            rev.report_id = row[14]
                            reported_reviews_list.append(rev.to_dict())
                    res.reported_reviews_list = reported_reviews_list
                    res.is_reported_reviews_list_send_successfull= True
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_reported_reviews_list_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_reported_reviews_list_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RejectReportedReviewRequestAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                employee_id = data.get("employee_id")
                review_id = data.get("review_id")
                organization_id = data.get("organization_id")
                report_id = data.get("report_id")
                logger.info(data)
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE [ReviewEmployeeOrganizationMapping] SET IsReported = NULL, ModifiedOn = GETDATE() WHERE ReviewId = %s and EmployeeId = %s and OrganizationId = %s",[review_id,employee_id,organization_id])
                    cursor.execute("UPDATE [ReportReviewEmployeeOrganizationMapping] SET IsReportRejected = 1, ModifiedOn = GETDATE() WHERE ReportId = %s and ReviewId = %s and EmployeeId = %s and OrganizationId = %s",[report_id,review_id,employee_id,organization_id])
                    res.is_report_request_rejected_successfull = True
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_report_request_rejected_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_report_request_rejected_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteReportedReviewAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                employee_id = data.get("employee_id")
                review_id = data.get("review_id")
                organization_id = data.get("organization_id")
                report_id = data.get("report_id")
                logger.info(data)
                with connection.cursor() as cursor:
                    cursor.execute("Delete from Review where ReviewId = %s",[review_id])
                    res.is_review_deleted_successfull = True
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_review_deleted_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_review_deleted_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        




