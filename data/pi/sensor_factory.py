import time
from bluepy.btle import Peripheral, UUID
import struct

PICO_MAC_ADDRESS = "2C:CF:67:07:40:6B" 
MOTION_MAC_ADDRESS = "2C:CF:67:07:45:70"

TEMP_CHAR_UUID = "00002A6E-0000-1000-8000-00805f9b34fb"
MOTION_CHAR_UUID = "00002A5B-0000-1000-8000-00805F9B34FB"

class SensorFactory(object):
    # handle connect and read data from sensor in pi
    def __init__(self, Control):
        self.Control = Control
        self.characteristic = None
        self.motionSensorCharacter = None

    def handle_connect_sensor(self):
        # self.connect_imu_sensor()
        self.connect_motion_sensor()
    
    def connect_imu_sensor(self):
        try:
            print("Connecting to imu sensor...")
            # Connect to the peripheral device
            device = Peripheral(PICO_MAC_ADDRESS)
            print("Connected!")

            # Get the service and characteristic
            service = device.getServiceByUUID(UUID("0000181A-0000-1000-8000-00805f9b34fb"))  # Environmental Sensing
            self.characteristic = service.getCharacteristics(UUID(TEMP_CHAR_UUID))[0]
            
        except Exception as e:
            print(f"Error: {e}")

    def connect_motion_sensor(self):
        try:
            print("Connecting to Motion Sensor...")
            # Connect to the peripheral device
            device = Peripheral(MOTION_MAC_ADDRESS)
            print("Motion Sensor Connected!")

            # Get the service and characteristic
            service = device.getServiceByUUID(UUID("0000181A-0000-1000-8000-00805f9b34fb"))  # Environmental Sensing
            self.motionSensorCharacter = service.getCharacteristics(UUID(MOTION_CHAR_UUID))[0]

        except Exception as e:
            print(f"Error: {e}")
    
    def detect_motion_sensor(self):
        print(11)
        self.connect_motion_sensor()
        while True:
            value = self.get_motion_sensor_value()

            if value == 1:
                print("jump")
                self.Control.handle_jump()
            else:
                self.Control.clear_jump()
    
    def get_motion_sensor_value(self):
        if self.motionSensorCharacter == None:
            return 0
        # Read the value
        motion_sensor_value = self.motionSensorCharacter.read()
        motion_sensor_value = int.from_bytes(motion_sensor_value, 'little')

        print(motion_sensor_value)
        
        return motion_sensor_value