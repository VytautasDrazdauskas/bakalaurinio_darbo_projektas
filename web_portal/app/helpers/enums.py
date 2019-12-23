import enum 

class DeviceState(enum.Enum):
    registered = 1
    active = 2
    offline = 3
    error = 4
    blocked = 5
    deleted = 6
