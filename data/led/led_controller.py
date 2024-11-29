import spidev
import time

class LEDController:
    def __init__(self, num_leds):
        self.num_leds = num_leds
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 8000000
        self.leds = [(0, 0, 0)] * num_leds

    def send_data(self):
        """Send color data to the light unit"""
        start_frame = [0x00] * 4
        end_frame = [0xFF] * 4
        data = start_frame
        for r, g, b in self.leds:
            data += [0xFF, r, g, b]
        data += end_frame
        self.spi.xfer2(data)

    def set_color(self, index, color):
        """Set light unit's color"""
        if 0 <= index < self.num_leds:
            self.leds[index] = color

    def clear(self):
        """Turn off the whole light strip"""
        self.leds = [(0, 0, 0)] * self.num_leds
        self.send_data()

    def flash_all(self, color, times=1, delay=0.2):
        """Whole light strip flashes with the same color"""
        for _ in range(times):
            self.leds = [color] * self.num_leds
            self.send_data()
            time.sleep(delay)
            self.clear()
            time.sleep(delay)

    def pattern_left_to_right(self, delay=0.1):
        """Lit the whole light strip from left to right"""
        self.clear()
        for i in range(self.num_leds):
            self.set_color(i, (255, 255, 255))  # 白色
            self.send_data()
            time.sleep(delay)
        self.clear()

    def long_bright(self, color, duration=10):
        """Lit the whole light strip continuously"""
        self.leds = [color] * self.num_leds
        self.send_data()
        time.sleep(duration)
        self.clear()

    def close(self):
        """Close SPI"""
        self.spi.close()
