class employee:

    def __init__(self):
        self.employee_id = None
        self.first_name = None
        self.last_name = None
        self.employee_name = None
        self.email = None
        self.employee_image = None
        self.mobile_number = None
        self.aadhar_number = None
        self.designation = None
        self.image = None
        self.average_rating = None
        self.avg_rating = None
        
    def to_dict(self):
        emp = {}
        
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                emp[attr_name] = attr_value
        return emp