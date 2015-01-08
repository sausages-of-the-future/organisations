class Order(object):

    def __init__(self, **kwargs):
        self.organisation_type = kwargs.get('organisation_type')
        self.name = kwargs.get('name')
        self.activities = kwargs.get('activities', [])
        self.directors = kwargs.get('directors', [])

    def to_dict(self):
        return self.__dict__
