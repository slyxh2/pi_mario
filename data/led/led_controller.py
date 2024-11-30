import spidev
import time

class LEDController:
    """LED Controller for low-level SPI communication with LED strips."""
    def __init__(self, num_leds):
        """
        Initialize the LED controller.
        :param num_leds: Number of LEDs in the strip.
        """
        self.num_leds = num_leds  # Number of LEDs in the strip
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # Open SPI bus 0, device 0
        self.spi.max_speed_hz = 6400000  # Set SPI speed
        self.reset_frame = [0] * 50  # Reset frame for WS2812-like LEDs

    def rgb_to_spi_data(self, red, green, blue):
        """
        Convert RGB values to SPI data for LED strip.
        :param red: Red intensity (0-255).
        :param green: Green intensity (0-255).
        :param blue: Blue intensity (0-255).
        :return: List of SPI-formatted data for one LED.
        """
        spi_data = []
        # Process each color in GRB order
        for color in [green, red, blue]:
            for i in range(8):
                if color & (1 << (7 - i)):
                    # High bit representation for '1'
                    spi_data.append(0b11111100)
                else:
                    # Low bit representation for '0'
                    spi_data.append(0b11000000)
        return spi_data

    def set_led_strip_color(self, red, green, blue):
        """
        Set the entire LED strip to the same color.
        :param red: Red intensity (0-255).
        :param green: Green intensity (0-255).
        :param blue: Blue intensity (0-255).
        """
        data = []
        for _ in range(self.num_leds):
            # Add SPI data for each LED
            data.extend(self.rgb_to_spi_data(red, green, blue))
        # Append reset frame
        data.extend(self.reset_frame)
        # Send the data to the LED strip
        self.spi.xfer2(data)

    def clear(self):
        """
        Turn off all LEDs on the strip.
        """
        self.set_led_strip_color(0, 0, 0)

    def flash_all(self, red, green, blue, times=1, delay=0.2):
        """
        Flash all LEDs with the same color.
        :param red: Red intensity (0-255).
        :param green: Green intensity (0-255).
        :param blue: Blue intensity (0-255).
        :param times: Number of flashes.
        :param delay: Delay in seconds between flashes.
        """
        for _ in range(times):
            self.set_led_strip_color(red, green, blue)
            time.sleep(delay)
            self.clear()
            time.sleep(delay)

    def close(self):
        """
        Clean up the SPI connection.
        """
        self.spi.close()

    def pattern_left_to_right(self, red, green, blue, delay=0.1):
        """
        Light up LEDs from left to right.
        :param red: Red intensity (0-255).
        :param green: Green intensity (0-255).
        :param blue: Blue intensity (0-255).
        :param delay: Delay in seconds between lighting each LED.
        """
        self.clear()
        data = []
        for i in range(self.num_leds):
            # Build up the data for the current state of the strip
            data.extend(self.rgb_to_spi_data(red, green, blue) if j <= i else self.rgb_to_spi_data(0, 0, 0) for j in range(self.num_leds))
            data.extend(self.reset_frame)
            self.spi.xfer2(data)
            time.sleep(delay)
