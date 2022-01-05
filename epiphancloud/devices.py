from .models.device import Device
from .access import APIAccess

class Devices(object):
    '''
    Devices class provides Frontapi access for concrete device
    '''
    def __init__(self, api_access:APIAccess):
        self._api_access = api_access

    def get_all(self) -> list:
        """
        covers: GET /front/api/v1t/devices
        """
        self._api_access.logger().info("Getting all devices")
        return [
            Device(dev["Id"], self._api_access, dev)
            for dev in self._api_access.http_get("devices").json()
        ]

    def get(self, device_id) -> Device:
        dev = Device(device_id, self._api_access)
        _ = dev.json
        return dev

    def delete_all(self):
        self._api_access.logger().info("Deleting all devices")
        for dev in self.get_all():
            dev.delete()

    def run_batch_command(self, device_ids, cmd):
        """
        covers: POST /front/api/v1t/devices/batch_task
        """
        self._api_access.logger().info("Running command \"%s\" on devices %s", cmd, device_ids)
        cmd_desc = {"Devices": device_ids, "Task": {"cmd": cmd}}
        return self._api_access.http_post_data("devices/batch_task", cmd_desc).json()

    def pair(self, device_id, name):
        """
        covers: POST /front/api/v1t/devices/pair
        """
        self._api_access.logger().info("Pairing device %s as \"%s\"", device_id, name)
        cmd_desc = {
            "PairingCode": device_id,
            "Name": name
        }

        return self._api_access.http_post_data("devices/pair", cmd_desc).json()
