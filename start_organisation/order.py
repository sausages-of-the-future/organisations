class Order(object):

    def __init__(self, **kwargs):
        self.organisation_type = kwargs.get('organisation_type')
        self.name = kwargs.get('name')
        self.activities = kwargs.get('activities', [])
        self.directors = kwargs.get('directors', [])
        self.register_data = kwargs.get('register_data', False)
        self.register_employer = kwargs.get('register_employer', False)
        self.register_construction = kwargs.get('register_construction', False)
        self.address = kwargs.get('address')

    def to_dict(self):
        return self.__dict__
