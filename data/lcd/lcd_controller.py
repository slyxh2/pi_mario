import queue
import threading
import time

class LCDController:
    def __init__(self, bus=1, address=0x3e):
        self.bus = bus
        self.address = address
        self.queue = queue.Queue()
        self.last_display = {"score": -1, "lives": -1}
        self.update_thread = threading.Thread(target=self._process_updates, daemon=True)
        self.update_thread.start()
        self.clear()

    def clear(self):
        self.command(0x01)  # Clear display command
        time.sleep(0.1)  # Allow LCD to process the clear command

    def command(self, cmd):
        self.bus.write_byte_data(self.address, 0x80, cmd)
        time.sleep(0.05)

    def write(self, text):
        for char in text:
            self.bus.write_byte_data(self.address, 0x40, ord(char))
            time.sleep(0.05)  # Slow down character writing

    def set_cursor(self, row, col):
        offsets = [0x00, 0x40]
        self.command(0x80 | (offsets[row] + col))

    def update(self, score, lives):
        """Queue an update request."""
        self.queue.put({"score": score, "lives": lives})

    def _process_updates(self):
        """Process updates from the queue."""
        while True:
            update_data = self.queue.get()  # Block until an update is available
            if (
                self.last_display["score"] != update_data["score"]
                or self.last_display["lives"] != update_data["lives"]
            ):
                self.last_display = update_data
                self.clear()
                self.set_cursor(0, 0)
                self.write(f"Score: {update_data['score']}")
                self.set_cursor(1, 0)
                self.write(f"Lives: {update_data['lives']}")

            self.queue.task_done()  # Mark the task as done
            time.sleep(0.1)  # Avoid overwhelming the LCD

    
    def update_thread(self, score, lives):
        thread = threading.Thread(target=self.update, args=(score, lives))
        thread.start()