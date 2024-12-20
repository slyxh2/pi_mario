import smbus
import queue
import threading
import time

class LCDController:
    def __init__(self, bus=None, address=0x3e): # Please double check address
        """
        :param bus: SMBus instance (e.g., smbus.SMBus(1))
        :param address: I2C address of the LCD (default: 0x3e)
        """
        self.bus = bus if bus else smbus.SMBus(1)  # Default: SMBus(1)
        self.address = address
        self.queue = queue.Queue()
        self.last_display = {"score": -1, "lives": -1}
        self.current_display = {"line1": "", "line2": ""}
        self.update_thread = threading.Thread(target=self._process_updates, daemon=True)
        self.update_thread.start()
        self.clear()

    def clear(self):
        self.command(0x01)  # Clear display command
        time.sleep(0.1)  # Allow LCD to process the clear command

    def command(self, cmd):
        """
        Send a command to the LCD.
        :param cmd: Command byte
        """
        self.bus.write_byte_data(self.address, 0x80, cmd)
        time.sleep(0.05)

    def write(self, text):
        """
        Write a string to the LCD.
        :param text: The text string to write
        """
        for char in text:
            self.bus.write_byte_data(self.address, 0x40, ord(char))
            time.sleep(0.01)

    def set_cursor(self, row, col):
        """
        Set cursor position on the LCD.
        :param row: Row number (0 or 1)
        :param col: Column number (0-15)
        """
        offsets = [0x00, 0x40]
        self.command(0x80 | (offsets[row] + col))

    def update(self, score, lives):
        """
        Queue an update request.
        :param score: Current score
        :param lives: Remaining lives
        """
        self.queue.put({"score": score, "lives": lives})

    def _process_updates(self):
        """Process updates from the queue."""
        last_handled = None  # 记录上一次处理的数据
        while True:
            try:
                update_data = self.queue.get(timeout=0.1)  # 超时时间，防止线程一直阻塞
                if last_handled != update_data:
                    last_handled = update_data
                    self.clear()
                    self.set_cursor(0, 0)
                    self.write(f"Score: {update_data['score']}")
                    self.set_cursor(1, 0)
                    self.write(f"Lives: {update_data['lives']}")
                self.queue.task_done()
            except queue.Empty:
                continue
    
    def clear_queue(self):
        """Clear all pending updates in the queue."""
        with self.queue.mutex:
            self.queue.queue.clear()

    def display_immediately(self, score, lives):
        """
        Immediately update the display with the final score and lives, bypassing the queue.
        """
        self.clear_queue()
        self.clear()
        self.set_cursor(0, 0)
        self.write(f"Score: {score}")
        self.set_cursor(1, 0)
        self.write(f"Lives: {lives}")
    
    def keep_display_message(self, line1, line2=""):
        """
        Display a custom message on the LCD.
        :param line1: Text for the first line.
        :param line2: Text for the second line (optional).
        """
        self.clear_queue()
        self.clear()
        self.set_cursor(0, 0)
        self.write(line1[:16])  # LCD is typically 16 characters wide
        if line2:
            self.set_cursor(1, 0)
            self.write(line2[:16])
    
    def display_message(self, line1, line2="", duration=1):
        """
        Display a custom message on the LCD.
        :param line1: Text for the first line.
        :param line2: Text for the second line (optional).
        """
        self.clear_queue()
        self.clear()
        self.set_cursor(0, 0)
        self.write(line1[:16])  # LCD is typically 16 characters wide
        if line2:
            self.set_cursor(1, 0)
            self.write(line2[:16])
        time.sleep(duration)
        self.clear()