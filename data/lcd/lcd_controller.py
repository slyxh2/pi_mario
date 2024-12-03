import smbus
import time
import threading

class LCDController:
    """Controller for Grove 16x2 LCD (White on Blue)"""
    def __init__(self, bus=1, address=0x3E):
        self.bus = smbus.SMBus(bus)
        self.address = address
        self.init_lcd()
        self.last_display = {"score": None, "lives": None}  # Record previous display content

    def init_lcd(self):
        """Initialize the LCD."""
        self.command(0x38)  # 8-bit mode, 2 lines
        self.command(0x39)  # Enable instruction table
        self.command(0x14)  # OSC frequency adjustment
        self.command(0x70)  # Contrast set
        self.command(0x56)  # Power/ICON control/contrast set
        self.command(0x6C)  # Follower control
        time.sleep(0.2)
        self.command(0x38)  # Back to normal instruction mode
        self.command(0x0C)  # Display ON, cursor OFF

    def command(self, cmd):
        """Send a command to the LCD."""
        self.bus.write_byte_data(self.address, 0x80, cmd)
        time.sleep(0.05)

    def write(self, text):
        """Write text to the LCD."""
        for char in text:
            self.bus.write_byte_data(self.address, 0x40, ord(char))
            time.sleep(0.05)

    def clear(self):
        """Clear the LCD display."""
        self.command(0x01)
        time.sleep(0.1)

    def set_cursor(self, line, col):
        """Set the cursor position."""
        addr = 0x80 + (0x40 * line + col)
        self.command(addr)

    def update(self, score, lives):
        """
        Update the LCD display if the values have changed.
        :param score: Current score
        :param lives: Remaining lives
        """
        if (
            self.last_display["score"] == score
            and self.last_display["lives"] == lives
        ):
            return  # If nothing changed, no need to refresh

        self.last_display = {"score": score, "lives": lives}
        self.clear()
        self.set_cursor(0, 0)
        self.write(f"Score: {score}")
        self.set_cursor(1, 0)
        self.write(f"Lives: {lives}")
    
    def update_thread(self, score, lives):
        thread = threading.Thread(target=self.update, args=(score, lives))
        thread.start()
