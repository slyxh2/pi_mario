from machine import Pin
import time

# Set up the PIR sensor on pin D16
pir_pin = Pin(16, Pin.IN)

print("PIR Motion Sensor Test (press Ctrl+C to exit)")

prev = 0

try:
    while True:
        if pir_pin.value() == 1:
            print("Motion detected!")
        else:
            print("No motion")

except KeyboardInterrupt:
    print("Exiting program")
