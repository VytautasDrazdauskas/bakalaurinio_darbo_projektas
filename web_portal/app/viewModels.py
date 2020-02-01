class ProfilesView():
    def __init__(self, id, email, name, devCount, uuid):
        self.id = id
        self.email = email
        self.name = name
        self.devCount = devCount
        self.uuid = uuid

    @property
    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'devCount': self.devCount,
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
    def __init__(self, id, deviceName, mac, state, dateAdded, deviceType, deviceTypeName):
        self.id = id
        self.deviceName = deviceName
        self.mac = mac
        self.state = state
        self.dateAdded = dateAdded
        self.deviceType = deviceType
        self.deviceTypeName = deviceTypeName

    @property
    def serialize(self):
        return {
            'id': self.id,
            'deviceName': self.deviceName,
            'mac': self.mac,
            'state': self.state,
            'dateAdded': self.dateAdded,
            'deviceType': self.deviceType,
            'deviceTypeName': self.deviceTypeName
        }