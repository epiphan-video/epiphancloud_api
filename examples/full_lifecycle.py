import os
import time
import logging

from epiphancloud.api import API
from epiphancloud.exceptions import EpiphanCloudException

# Setting up the logger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def use_api():
    API_TOKEN = os.environ["EPIPHAN_API_TOKEN"]
    API_HOST = os.environ["EPIPHAN_HOST"] or "go.epiphan.cloud"
    PAIRING_CODE = os.environ["PAIRING_CODE"] or "go.epiphan.cloud"

    if API_TOKEN is None:
        raise Exception("EPIPHAN_API_TOKEN environment variable is not set")

    # Authenticating
    api = API(API_HOST)
    api.set_auth_token(API_TOKEN)
    logging.info("Authentication completed")

    # Pairing the device (if needed)
    if PAIRING_CODE is None:
        logging.info("PAIRING_CODE environment variable is not set, pairing skipped")
        exit(0)

    device_name = f"Test device {PAIRING_CODE}"
    api.Devices.pair(PAIRING_CODE, f"API example {PAIRING_CODE}")
    logging.info("Pairing completed")

    # Getting the device
    device = api.Devices.get(PAIRING_CODE)
    logging.info("Device %s is paired", device.id)

    # Send command to the device
    rtmp_url = "rtmp://127.0.0.1:3333/live/test"
    device.run_command(f"rtmp.start:{rtmp_url}")

    time.sleep(10)

    # Send another command to the device
    device.run_command(f"rtmp.stop")

    # Deleting the device
    device.delete()

    # Getting all devices
    devices = api.Devices.get_all()
    for device in devices:
        logging.info("Device: %s", device.id)

if __name__ == "__main__":
    try:
        use_api()
    except EpiphanCloudException as e:
        logging.error("Cloud error: %s", e)
    except Exception as e:
        logging.error(e)
        exit(1)