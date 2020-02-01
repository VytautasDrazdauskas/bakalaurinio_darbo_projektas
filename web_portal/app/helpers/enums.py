import enum 

class DeviceState(enum.Enum):
    Registered = 1
    Active = 2
    Offline = 3
    Error = 4
    Blocked = 5
    Deleted = 6
    Rebooting = 7

class ConfigState(enum.Enum):
    Active = True
    Disabled = False

class DeviceType(enum.Enum):
    Default = 0
    Heater = 1

    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)

    

