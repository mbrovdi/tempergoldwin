import pywinusb.hid as hid
import threading
import time

VENDOR_ID, PRODUCT_ID = 0x3553, 0xA001
CMD = [0x00, 0x01, 0x80, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00]

class DeviceNotFoundError(Exception):
    """Raised when the TEMPer device is not connected."""
    pass

class TemperatureOutOfRangeError(Exception):
    """Raised when temperature is outside valid range (-55 to 125 °C)."""
    pass

def read_temperature(timeout=2.0):
    """Read temperature from TEMPer device with proper timeout handling."""
    devices = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()
    if not devices:
        raise DeviceNotFoundError("TEMPer device not found. Try replugging it.")

    device = devices[0]
    device.open()
    report = device.find_output_reports()[0]

    event = threading.Event()
    temperature = None

    def handler(data):
        nonlocal temperature
        if len(data) >= 4:
            raw = (data[3] << 8) | data[2]
            if raw > 0x7FFF:
                raw -= 0x10000
            temperature = raw / 100.0
            event.set()

    device.set_raw_data_handler(handler)

    report.set_raw_data(CMD)
    report.send()

    # Wait up to `timeout` seconds for response
    if not event.wait(timeout):
        device.close()
        raise TimeoutError("TEMPer sensor did not respond within timeout period.")

    device.close()

    # Sanity check
    if temperature is None:
        raise TimeoutError("No data received from TEMPer sensor.")
    if not (-55 <= temperature <= 125):
        raise TemperatureOutOfRangeError(f"Invalid temperature: {temperature:.2f} °C")

    return temperature

if __name__ == "__main__":
    try:
        t = read_temperature()
        print(f"Temperature: {t:.2f} °C")
    except DeviceNotFoundError as e:
        print(f"Error: {e}")
    except TimeoutError as e:
        print(f"Error: {e}")
    except TemperatureOutOfRangeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
