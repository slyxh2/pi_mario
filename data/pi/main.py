import time
from bluepy.btle import Peripheral, UUID
import struct

PICO_MAC_ADDRESS = "2C:CF:67:07:40:6B"  # Replace with your Pico's MAC address
TEMP_CHAR_UUID = "00002A6E-0000-1000-8000-00805f9b34fb"

def connect_and_read_temperature(mac_address):
    try:
        print("Connecting to device...")
        # Connect to the peripheral device
        device = Peripheral(mac_address)
        print("Connected!")

        # Get the service and characteristic
        service = device.getServiceByUUID(UUID("0000181A-0000-1000-8000-00805f9b34fb"))  # Environmental Sensing
        characteristic = service.getCharacteristics(UUID(TEMP_CHAR_UUID))[0]

        # Read the value
        while True:
            temperature_value = characteristic.read()
            temperature_value = int.from_bytes(temperature_value, 'little')
            
            if temperature_value >32768:
                temperature_value -= 65536
            print(f"Temperature (raw value): {temperature_value}")
            time.sleep(2)
        # Disconnect
        device.disconnect()
        print("Disconnected")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    connect_and_read_temperature(PICO_MAC_ADDRESS)
