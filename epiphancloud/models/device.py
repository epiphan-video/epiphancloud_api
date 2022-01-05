import typing

from .settings import DeviceSettings

from .desired_state import DesiredState
from .settings import DeviceSettings

def capability(name):
    """
    Decorator for checking device capability

    Usage:
    @capability("presets")
    def do_something(self):
        pass
    """
    def inner_fn(fn):
        the_fn = fn

        def wrapper(self, *args, **kwargs):
            if not self.is_capability_supported(name):
                raise NotImplementedError(f'device {self._device_id} does not support {name}')
            return the_fn(self, *args, **kwargs)

        return wrapper

    return inner_fn


def resets_json(fn):
    """
    Decorator that resets cached device info json
    Usage:
    @resets_json
    def modify_device(self):
        pass
    """
    the_fn = fn

    def wrapper(self, *args, **kwargs):
        try:
            r = the_fn(self, *args, **kwargs)
        except:
            raise
        finally:
            self._json = None

        return r

    return wrapper


class Device(object):
    """
    Device class represents a device and provides methods for device API.
    """

    CMD_LIVE_START = "live.start"
    CMD_URL_SUFFIXIES = {
        CMD_LIVE_START: "/live/start",
    }

    def __init__(self, device_id, api_access, json_data=None):
        assert device_id is not None
        assert type(device_id) is str
        assert device_id != ""

        self._api_access = api_access
        self._device_id = device_id
        self._json = json_data

    def __str__(self):
        if self._json is None:
            return f"Device with id {self._device_id}"
        else:
            return f"Device with id {self._device_id} and name {self.name}"

    def __repr__(self):
        if self._json is None:
            return f"<Device with id {self._device_id}>"
        else:
            return f"<Device with id {self._device_id} and name {self.name}>"

    @property
    def id(self) -> str:
        return self._device_id

    @property
    def json(self) -> dict:
        if self._json is None:
            self.fetch()

        return self._json or {}

    def fetch(self):
        """
        Retrieves device info.
        """
        self._api_access.logger().info("Getting device %s", self._device_id)
        self._json = self._api_access.http_get("devices/" + self._device_id).json()

    @property
    def settings(self) -> typing.Dict[str, DeviceSettings]:
        """
        Returns a dictionary of device settings
        Keys of nested settings are separated by '.'
        E.g.:
          device.settings["recorder.file_format"]
        """
        all_settings = self._api_access.http_get("devices/" + self._device_id + "/settings").json()

        def flattened(rootid:str, settings:list) -> typing.List[typing.Tuple[str, DeviceSettings]]:
            result = []
            for s in settings:
                subitem_id = rootid + "." + s["id"] if rootid != "" else s["id"]
                if "items" in s:
                    result.extend(flattened(subitem_id, s["items"]))
                else:
                    result.append((subitem_id, DeviceSettings(s)))

            return result


        return dict([s for s in flattened("", all_settings)])

    @property
    def children(self):
        child = self.json.get("Child", [])
        if not child:
            child = []
        return [
            Device(ch["DeviceID"], self._api_access) for ch in child
        ]

    @property
    def model(self):
        return self.json.get("Model")

    @resets_json
    def delete(self):
        self._api_access.logger().info("Deleting device %s", self._device_id)
        self._api_access.http_delete("devices/" + self._device_id)

    @resets_json
    def run_command(self, cmd, **kwargs):
        cmd_desc = dict(kwargs.items())
        cmd_desc["cmd"] = cmd
        self._api_access.logger().info("Running command \"%s\" on device %s", cmd, self._device_id)

        url = f"devices/{self._device_id}/task"
        suffix = self.CMD_URL_SUFFIXIES.get(cmd, "")
        url = f"{url}{suffix}"

        return self._api_access.http_post_data(url, cmd_desc)

    def run_live_start(self):
        return self.run_command(self.CMD_LIVE_START)

    @property
    def name(self):
        return self.json.get("Name")

    @name.setter
    @resets_json
    def name(self, name):
        self._api_access.logger().info("Renaming device %s to \"%s\"", self._device_id, name)
        self._api_access.http_post_data(
            f'devices/{self._device_id}/rename',
            {"Name": name})

    @resets_json
    def unpair(self):
        self._api_access.logger().info("Unpairing device %s", self._device_id)
        self._api_access.http_post(f'devices/{self._device_id}/unpair')

    def request_channel_previews(self):
        return self._api_access.http_post_data(
            'devices/request/channel_previews',
            {
                "Devices": [self._device_id]
            })

    def request_source_previews(self):
        return self._api_access.http_post_data(
            'devices/request/source_previews',
            {
                "Devices": [self._device_id]
            })

    def download_channel_preview_old(self, local_filename):
        return self._api_access.http_download_file(f'devices/{self._device_id}/state.jpg', local_filename)

    def download_source_preview_old(self, source_id, local_filename):
        return self._api_access.http_download_file(f'devices/{self._device_id}/{source_id}/state.jpg', local_filename)

    def download_channel_preview(self, local_filename):
        return self._api_access.http_download_file(f'devices/{self._device_id}/preview', local_filename)

    def download_source_preview(self, source_id, local_filename):
        return self._api_access.http_download_file(f'devices/{self._device_id}/{source_id}/preview', local_filename)

    @resets_json
    def set_prop(self, prop_name, prop_value):
        """
        Convenience method for setting device settings via setprop
        """

        if isinstance(prop_value, bool):
            prop_value = "true" if prop_value else "false"

        self.run_command("setprop:{name}={value}".format(name=prop_name, value=prop_value))

        self._json = None

    def get_prop(self, prop_name):
        """
        Convenience method for getting device settings
        """

        # API v2 returns settings as a dictionary.
        settings = self.telemetry.get("settings", {})
        value = self.walk_through_cfg_params(settings, prop_name)
        return value

    def walk_through_cfg_params(self, params, prop_name):
        for p in params:
            if "items" in p:
                return self.walk_through_cfg_params(p["items"], prop_name)
            elif p["id"] == prop_name:
                return p["value"]
        return None

    def is_capability_supported(self, cap_name) -> bool:
        """
        Returns true if capability supported by device, false otherwise
        """
        return cap_name in self.telemetry["info"]["caps"]

    @property
    def online(self) -> bool:
        self.fetch()
        return self.json.get("Status", None) == "Online"

    @property
    def telemetry(self) -> dict:
        if self._json is None:
            self.fetch()

        if self._json is None:
            return {}

        telemetry = self._json.get('Telemetry')
        if not telemetry:
            self._api_access.logger().warning("No telemetry available for device: %s" % self._device_id)

        return telemetry

    @property
    def state(self) -> dict:
        return self.telemetry.get('state', {})

    def state_by_name(self, name) -> typing.Union[dict, None]:
        return self.state.get(name)

    @property
    def desired_states(self) -> typing.List[DesiredState]:
        desired_states = self.json.get('DesiredState', [])
        if desired_states == []:
            self._api_access.logger().warning("No DesiredState available for device: %s" % self._device_id)

        return [DesiredState(d) for d in desired_states]

    def get_desired_state_with_type(self, type: str) -> typing.Union[DesiredState, None]:
        for ds in self.desired_states:
            if ds.type == type:
                return ds

        return None

    @capability("presets")
    @resets_json
    def get_local_presets(self) -> list:
        return self.telemetry.get('presets', {}).get('local', [])

    @capability("presets")
    def apply_cloud_preset(self, preset_id, sections):
        """
        Applies cloud preset to a device
        covers: PUT /front/api/v1t/devices/DEVICEID/presets/cloud
        Params:
          preset_id: id of the preset
        """
        r = self._api_access.http_put_data(
            f'devices/{self._device_id}/presets/cloud',
            {
                "id": preset_id,
                "name": preset_id,
                "sections": sections
            })
        return r.json()

    @capability("presets")
    @resets_json
    def apply_local_preset(self, preset_name, sections):
        """
        Applies device's preset
        covers: PUT /front/api/v1t/devices/DEVICEID/presets/local
        Params:
          preset_name: name of the preset
        """
        r = self._api_access.http_put_data(
            f'devices/{self._device_id}/presets/local',
            {
                "name": preset_name,
                "sections": sections
            })
        return r.json()

    @capability("presets")
    @resets_json
    def create_local_preset(self, preset_name, sections):
        """
        Creates preset on device with given sections
        Params:
          preset_name: name of preset to create
          sections: sections that need to be included in the preset
        """

        r = self._api_access.http_post_data(
            f'devices/{self._device_id}/presets/local',
            {
                "name": preset_name,
                "sections": sections
            })
        return r.json()

    @capability("presets")
    def push_local_preset(self, preset_name):
        """
        Pushes preset from device to cloud
        Params:
          preset_name: name of the preset to be pushed
        """
        r = self._api_access.http_post(f'devices/{self._device_id}/presets/local/{preset_name}/push')
        return r.json()

    @capability("presets")
    @resets_json
    def delete_local_preset(self, preset_name):
        """
        Pushes preset from device to cloud
        Params:
          preset_name: name of the preset to be pushed
        """
        r = self._api_access.http_delete(f'devices/{self._device_id}/presets/local/{preset_name}')
        return r.json()

    @resets_json
    def rename(self, newName):
        """
        changes device name
        covers: POST /front/api/v1t/devices/{device_id}/rename
        """
        self._api_access.logger().info(f'Renaming device {self._device_id} to "{newName}"')
        cmd_desc = {
            "Name": newName
        }

        r = self._api_access.http_post_data(f"devices/{self._device_id}/rename", cmd_desc)
        return r.json()
