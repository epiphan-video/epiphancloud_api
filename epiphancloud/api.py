from .access import APIAccess
from .devices import Devices
from .exceptions import *


class API(object):
    def __init__(self, host="go.epiphan.cloud"):
        self.HTTP = APIAccess(host)
        self.Devices = Devices(self.HTTP)

    def set_auth_token(self, token):
        self.HTTP.set_auth_token(token)
