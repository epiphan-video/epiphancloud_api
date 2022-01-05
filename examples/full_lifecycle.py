"""
This is an example of Epiphan API usage.

Set the environment variables EPIPHAN_API_TOKEN and PAIRING_CODE to run the example.

If PAIRING_CODE is not set, the example will list all devices and exit.
"""

import os
import time
import logging

from epiphancloud import API, exceptions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def use_api():
    API_TOKEN = os.environ["EPIPHAN_API_TOKEN"]
    API_HOST = os.environ["EPIPHAN_HOST"] or "go.epiphan.cloud"
    PAIRING_CODE = os.environ.get("PAIRING_CODE")

    if API_TOKEN is None:
        raise Exception("EPIPHAN_API_TOKEN environment variable is not set")

    # Authenticating
    api = API(API_HOST)
    api.set_auth_token(API_TOKEN)
    logging.info("Authentication completed")

    # Pairing the device (if needed)
    if PAIRING_CODE is None:
        logging.info("PAIRING_CODE environment variable is not set, pairing skipped")

        # Getting all devices
        devices = api.Devices.get_all()
        for device in devices:
            logging.info(device)

        exit(0)

    device_name = f"API example {PAIRING_CODE}"
    api.Devices.pair(PAIRING_CODE, device_name)
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

if __name__ == "__main__":
    try:
        use_api()
    except exceptions.EpiphanCloudException as e:
        logging.error("Cloud error: %s", e)
    except Exception as e:
        logging.error(e)
        exit(1)