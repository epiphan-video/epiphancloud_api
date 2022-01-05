class DeviceSettings:
    def __init__(self, settings):
        self._id = settings["id"]
        self._title = settings["title"]
        self._type = settings["type"]["name"]
        self._value = settings["value"]

    @property
    def id(self):
        return self._id

    @property
    def value(self):
        return self._value
