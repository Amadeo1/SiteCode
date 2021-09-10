
class Stats:

    def __init__(self, timestamp=None, type=None, name=None, action_url=None):
        self.data = {
            'timestamp': timestamp,
            'type': type,
            'name': name,
            'action_url': action_url
        }

    def get_id(self):
        return str(self.data['_id'])

    def __repr__(self):
        return '<Stats %r>' % self.data['_id']

    def get_json(self):
        return self.data
