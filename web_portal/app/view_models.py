class ProfilesView():
    def __init__(self, id, email, name, device_count, uuid):
        self.id = id
        self.email = email
        self.name = name
        self.device_count = device_count
        self.uuid = uuid

    @property
    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'device_count': self.device_count,
            'uuid': self.uuid,
        }


class DevicesView():
    def __init__(self, id, mac, uuid, user, state):
        self.id = id
        self.mac = mac
        self.uuid = uuid
        self.user = user
        self.state = state

    @property
    def serialize(self):
        return {
            'id': self.id,
            'mac': self.mac,
            'uuid': self.uuid,
            'user': self.user,
            'state': self.state
        }

class UserDevicesView():
    def __init__(self, id, device_name, mac, state, date_added, device_type, device_type_name, publish_interval):
        self.id = id
        self.device_name = device_name
        self.mac = mac
        self.state = state
        self.date_added = date_added
        self.device_type = device_type
        self.device_type_name = device_type_name
        self.publish_interval = publish_interval

    @property
    def serialize(self):
        return {
            'id': self.id,
            'device_name': self.device_name,
            'mac': self.mac,
            'state': self.state,
            'date_added': self.date_added,
            'device_type': self.device_type,
            'device_type_name': self.device_type_name,
            'publish_interval': self.publish_interval
        }