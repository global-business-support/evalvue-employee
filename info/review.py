class review:

    def __init__(self):
        self.review_id = None
        self.comment = None
        self.image = None
        self.rating = None
        self.created_on = None
        self.organization_id = None
        self.organization_name = None
        self.employee_id = None
        self.employee_name = None
        self.designation = None
        self.organization_image = None
        self.employee_image = None
        self.employee_email = None
        self.is_reported = None
        self.message = None
        self.report_id= None
    def to_dict(self):
        rev = {}
        
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                rev[attr_name] = attr_value
        return rev