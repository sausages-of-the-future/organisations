class Order():

    organisation_type = None
    name = None
    activities = None
    data = {}

    def to_dict(self):
        result = {}
        result['organisation_type'] = self.organisation_type
        result['name'] = self.name
        result['activities'] = self.name
        return result

    @classmethod
    def from_dict(cls, data):
        order = Order()
        order.organisation_type = data['organisation_type']
        order.name = data['name']
        order.activities = data['activities']
        return order
