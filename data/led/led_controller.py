import spidev
import time

class LEDController:
    """LED Controller for low-level SPI communication with LED strips."""
    def __init__(self, num_leds):
        self.num_leds = num_leds
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 6400000
        self.reset_frame = [0] * 50

    def rgb_to_spi_data(self, red, green, blue):
        spi_data = []
        for color in [green, red, blue]:
            for i in range(8):
                if color & (1 << (7 - i)):
                    spi_data.append(0b11111100)
                else:
                    spi_data.append(0b11000000)
        return [int(value) & 0xFF for value in spi_data]

    def set_led_strip_color(self, red, green, blue):
        data = []
        for _ in range(self.num_leds):
            data.extend(self.rgb_to_spi_data(red, green, blue))
        data.extend(self.reset_frame)
        data = [int(value) & 0xFF for value in data]
        self.spi.xfer2(data)

    def clear(self):
        self.set_led_strip_color(0, 0, 0)

    def pattern_left_to_right(self, red, green, blue, delay=0.1):
        self.clear()
        for i in range(self.num_leds):
            data = []
            for j in range(self.num_leds):
                if j <= i:
                    data.extend(self.rgb_to_spi_data(red, green, blue))
                else:
                    data.extend(self.rgb_to_spi_data(0, 0, 0))
            data.extend(self.reset_frame)
            data = [int(value) & 0xFF for value in data]
            print(f"Pattern Step {i}: {data}")
            self.spi.xfer2(data)
            time.sleep(delay)

    def flash_all(self, red, green, blue, times=1, delay=0.2):
        for _ in range(times):
            self.set_led_strip_color(red, green, blue)
            time.sleep(delay)
            self.clear()
            time.sleep(delay)

    def close(self):
        self.spi.close()
