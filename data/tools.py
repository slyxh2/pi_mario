__author__ = 'justinarmstrong'

import os
import pygame as pg
import random

import time
from bluepy.btle import Peripheral, UUID
import struct
from data.led.led_controller import LEDController
from data.lcd.lcd_controller import LCDController

PICO_MAC_ADDRESS = "2C:CF:67:07:40:6B"  # Replace with your Pico's MAC address

TEMP_CHAR_UUID = "00002A6E-0000-1000-8000-00805f9b34fb"

keybinding = {
    'action':pg.K_s,
    'jump':pg.K_a,
    'left':pg.K_LEFT,
    # 'left': 'L',
    'right':pg.K_RIGHT,
    'down':pg.K_DOWN,
    'sensor_left':0,
    'sensor_right':1,
    'sensor_jump':2
}

class Control(object):
    """Control class for entire project. Contains the game loop, and contains
    the event_loop which passes events to States as needed. Logic for flipping
    states is also found here."""
    def __init__(self, caption):
        self.screen = pg.display.get_surface()
        self.done = False
        self.clock = pg.time.Clock()
        self.caption = caption
        self.fps = 60
        self.show_fps = False
        self.current_time = 0.0
        self.keys = pg.key.get_pressed()
        self.sensor_keys = [False,False,False] # left, right, jump
        self.state_dict = {}
        self.state_name = None
        self.state = None
        self.characteristic = None
        self.led_controller = LEDController(num_leds=5, brightness=0.5)
        self.lcd_controller = LCDController()
        self.motionSensorCharacter = None
        
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def update(self):
        self.current_time = pg.time.get_ticks()
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, self.keys, self.current_time, self.sensor_keys)

    def flip_state(self):
        previous, self.state_name, led_controller, lcd_controller = self.state_name, self.state.next, self.state.led_controller, self.state.lcd_controller
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist, led_controller, lcd_controller)
        self.state.previous = previous


    def event_loop(self):
        # self.detect_imu_sensor()
        # keyboard listen event
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            self.state.get_event(event)
    
    def handle_jump(self):
        self.sensor_keys[2] = True
    
    def handle_move_left(self):
        self.sensor_keys[0] = True
        self.sensor_keys[1] = False
    
    def handle_move_right(self):
        self.sensor_keys[0] = False
        self.sensor_keys[1] = True

    def clear_jump(self):
        if self.sensor_keys[2] == False:
            return
        self.sensor_keys[2] = False

    def detect_imu_sensor(self):
        value = self.connect_and_read_temperature(PICO_MAC_ADDRESS)
        self.sensor_keys[0] = False
        self.sensor_keys[1] = False

        if value == None:
            return
        
        if value > 20:
            self.sensor_keys[1] = True
        elif value < -20:
            self.sensor_keys[0] = True

    def connect_and_read_temperature(self, mac_address):
        if self.characteristic == None:
            return 0
        # Read the value
        temperature_value = self.characteristic.read()
        temperature_value = int.from_bytes(temperature_value, 'little')
        
        if temperature_value >32768:
            temperature_value -= 65536
            
        return temperature_value
    
    def toggle_show_fps(self, key):
        if key == pg.K_F5:
            self.show_fps = not self.show_fps
            if not self.show_fps:
                pg.display.set_caption(self.caption)


    def main(self):
        self.connect_imu_sensor()
        
        # LED strip flashes gradually lights up from left to right, then clear
        if self.led_controller:
            self.led_controller.pattern_left_to_right_thread(255, 255, 255, delay=0.5)
            self.led_controller.clear()

        """Main loop for entire program"""
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            # if self.sensor_keys[2] == True:
            #     self.clear_jump()
            self.clock.tick(self.fps)
            if self.show_fps:
                fps = self.clock.get_fps()
                with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
                pg.display.set_caption(with_fps)
    
    def connect_imu_sensor(self):
        try:
            print("Connecting to device...")
            # Connect to the peripheral device
            device = Peripheral(PICO_MAC_ADDRESS)
            print("Connected!")

            # Get the service and characteristic
            service = device.getServiceByUUID(UUID("0000181A-0000-1000-8000-00805f9b34fb"))  # Environmental Sensing
            self.characteristic = service.getCharacteristics(UUID(TEMP_CHAR_UUID))[0]
            

        except Exception as e:
            print(f"Error: {e}")
    
class _State(object):
    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.persist = {}
        self.led_controller = None
        self.lcd_controller = None

    def get_event(self, event):
        pass

    def startup(self, current_time, persistant, led_controller, lcd_controller):
        self.persist = persistant
        self.start_time = current_time
        self.led_controller = led_controller
        self.lcd_controller = lcd_controller

    def cleanup(self):
        self.done = False
        return self.persist

    def update(self, surface, keys, current_time):
        pass



def load_all_gfx(directory, colorkey=(255,0,255), accept=('.png', 'jpg', 'bmp')):
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name]=img
    return graphics


def load_all_music(directory, accept=('.wav', '.mp3', '.ogg', '.mdi')):
    songs = {}
    for song in os.listdir(directory):
        name,ext = os.path.splitext(song)
        if ext.lower() in accept:
            songs[name] = os.path.join(directory, song)
    return songs


def load_all_fonts(directory, accept=('.ttf')):
    return load_all_music(directory, accept)


def load_all_sfx(directory, accept=('.wav','.mpe','.ogg','.mdi')):
    effects = {}
    for fx in os.listdir(directory):
        name, ext = os.path.splitext(fx)
        if ext.lower() in accept:
            effects[name] = pg.mixer.Sound(os.path.join(directory, fx))
    return effects