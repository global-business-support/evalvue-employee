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


from .response import *
from  .constant import *
from .organization import *
from  .review import *

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
                    cursor.execute("SELECT Name, Image from Organization where OrganizationId = %s",[organization_id])
                    organization_details = cursor.fetchone()
                    organization_list = []
                    org = organization()
                    org.name = organization_details[0]
                    org.image = organization_details[1]
                    organization_list.append(org.to_dict())
                    res.organization_list = organization_list
                    cursor.execute("SELECT rem.ReviewId,r.Comment,r.Rating,r.CreatedOn,r.Image,org.OrganizationId,org.Name,org.Image FROM ReviewEmployeeOrganizationMapping rem JOIN Review r ON rem.ReviewId = r.ReviewId JOIN Organization org ON rem.OrganizationId = org.OrganizationId JOIN Employee emp ON rem.EmployeeId = emp.EmployeeId where rem.EmployeeId = %s and rem.OrganizationId = %s",[employee_id,organization_id])
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
      