class response:

    def __init__(self):
        self.error = None
        self.is_login_successfull = None
        self.otp_send_successfull= None
        self.employee_id = None
        self.employee_email = None
        self.dashboard_list = None

        self.otp_is_expired = None
        self.incorrect_otp = None
        self.otp_verified_successfull = None
        self.organization_list = None
        self.organization_data_send_successfull = None
        self.review_list = None
        self.is_employee_organization_data_send_successfull =  None
        self.is_review_mapped = None  
        self.is_report_created_successfull = None
        self.employee_edit_sucessfull = None
        self.employee_profile = None
        self.is_employee_profile_successfull = None
        self.reported_reviews_list = None
        self.is_reported_reviews_list_send_successfull = None
        self.is_report_request_rejected_successfull = None
        self.is_review_deleted_successfull  = None
    def convertToJSON(self):
        res = {}
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                res[attr_name] = attr_value
        return res
