# tempergoldwin.py
import pywinusb.hid as hid
import time

VENDOR_ID, PRODUCT_ID = 0x3553, 0xA001
CMD = [0x00, 0x01, 0x86, 0xFF, 0x01, 0x00, 0x00, 0x00, 0x00]

def read_temperature():
    """Read temperature once and return a float in Celsius."""
    devices = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()
    if not devices:
        print("TEMPer device not found. Try replugging it.")
        return None

    device = devices[0]
    device.open()
    report = device.find_output_reports()[0]
    temp_c = None

    def handler(data):
        nonlocal temp_c
        if len(data) >= 4:
            raw = (data[3] << 8) | data[2]
            if raw > 0x7FFF:
                raw -= 0x10000
            temp_c = raw / 100.0

    device.set_raw_data_handler(handler)
    report.set_raw_data(CMD)
    report.send()
    time.sleep(0.2)  # allow device to respond
    device.close()
    return temp_c

def read_temperature_loop(interval=2):
    """Continuously print temperature every `interval` seconds."""
    devices = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()
    if not devices:
        print("TEMPer device not found. Try replugging it.")
        return

    device = devices[0]
    device.open()
    report = device.find_output_reports()[0]
    temp_c = None

    def handler(data):
        nonlocal temp_c
        if len(data) >= 4:
            raw = (data[3] << 8) | data[2]
            if raw > 0x7FFF:
                raw -= 0x10000
            temp_c = raw / 100.0

    device.set_raw_data_handler(handler)
    print(f"Requesting temperature every {interval} seconds... (Ctrl+C to stop)")

    try:
        while True:
            report.set_raw_data(CMD)
            report.send()
            time.sleep(interval)
            if temp_c is not None:
                print(f"Temperature: {temp_c:.2f} °C")
            else:
                print("Failed to read temperature.")
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        device.close()

if __name__ == "__main__":
    read_temperature_loop()

