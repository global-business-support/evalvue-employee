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

from .response import *
from  .constant import *

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
        