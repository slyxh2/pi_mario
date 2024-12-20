import time
import gpiod
from bluepy.btle import Peripheral, UUID
import struct

PICO_MAC_ADDRESS = "2C:CF:67:07:40:6B" 
MOTION_MAC_ADDRESS = "2C:CF:67:07:45:70"

TEMP_CHAR_UUID = "00002A6E-0000-1000-8000-00805f9b34fb"
MOTION_CHAR_UUID = "00002A5B-0000-1000-8000-00805F9B34FB"

ENV_UUID = "0000181A-0000-1000-8000-00805f9b34fb"
MOTION_ENV_UUID = "0000180A-0000-1000-8000-00805f9b34fb"



class SensorFactory(object):
    # handle connect and read data from sensor in pi
    def __init__(self, Control, Level1):
        self.Control = Control
        self.Level1 = Level1
        self.characteristic = None
        self.motionSensorCharacter = None
        self.jumpFlag = False

    # imu sensor
    def connect_imu_sensor(self):
        try:
            print("Connecting to imu sensor...")
            # Connect to the peripheral device
            device = Peripheral(PICO_MAC_ADDRESS)
            print("IMU Sensor Connected!")

            # Get the service and characteristic
            service = device.getServiceByUUID(UUID(ENV_UUID))  # Environmental Sensing
            self.characteristic = service.getCharacteristics(UUID(TEMP_CHAR_UUID))[0]
            
        except Exception as e:
            print(f"Error: {e}")

    def detect_imu_sensor(self):
        self.connect_imu_sensor()
        while True:
            value = self.connect_and_read_temperature()
            if value > 20:
                self.Control.handle_move_right()
            elif value < -20:
                self.Control.handle_move_left()


    def connect_and_read_temperature(self):
        if self.characteristic == None:
            return 0
        # Read the value
        temperature_value = self.characteristic.read()
        temperature_value = int.from_bytes(temperature_value, 'little')
        
        if temperature_value >32768:
            temperature_value -= 65536
            
        return temperature_value

    
    # motion sensor
    def connect_motion_sensor(self):
        try:
            print("Connecting to Motion Sensor...")
            # Connect to the peripheral device)
            print("Motion Sensor Connected!")
            device = Peripheral(MOTION_MAC_ADDRESS)
            # Get the service and characteristic
            service = device.getServiceByUUID(UUID(MOTION_ENV_UUID))  # Environmental Sensing
            self.motionSensorCharacter = service.getCharacteristics(UUID(MOTION_CHAR_UUID))[0]

        except Exception as e:
            print(f"Error: {e}")
    
    def detect_motion_sensor(self):
        self.connect_motion_sensor()
        while True:
            value = self.get_motion_sensor_value()
            if value == 1:
                self.Control.handle_jump()
            else:
                self.Control.clear_jump()
                self.jumpFlag = False
    
    def get_motion_sensor_value(self):
        if self.motionSensorCharacter == None:
            return 0
        # Read the value
        motion_sensor_value = self.motionSensorCharacter.read()
        motion_sensor_value = int.from_bytes(motion_sensor_value, 'little')
        
        return motion_sensor_value

    # light sensor
    def handle_light_sensor(self):
        LED_PIN = 17
        LIGHT_SENSOR_PIN = 16
        chip = gpiod.Chip('gpiochip4')
        led_line = chip.get_line(LED_PIN)
        button_line = chip.get_line(LIGHT_SENSOR_PIN)
        led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
        button_line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
        try:
            while True:
                button_state = button_line.get_value()
                print(button_state)
                time.sleep(0.1)
                if button_state == 0:
                    self.Level1.setup_dark_background()
                # else:
                #     self.Level1.setup_dark_background()
        finally:
            led_line.release()


        button_line.release()


