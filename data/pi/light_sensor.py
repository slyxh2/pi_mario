import gpiod
import time

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
    #    if button_state == 1:
    #        led_line.set_value(1)
    #    else:
    #        led_line.set_value(0)
finally:
   led_line.release()


button_line.release()