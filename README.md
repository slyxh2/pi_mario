# Mario in Pi
LED and LCD Prep:
1. (1) sudo raspi-config (2) Interface Options (3) Enable I2C and SPI (4) sudo reboot
2. pip install smbus2
3. pip install spidev
4. Test I2C: (1) sudo apt-get install i2c-tools (2) i2cdetect -y 1, see output. If differs from 0x3e, please update led_controller __init__() params - address

LED Wiring: (LED - Raspberry Pi)
+5V - Pin 2 (5v Power)
DIN - Pin 19 (GPIO 10)
GND - Pin 6 (Ground)

LCD Wiring: (LCD - Raspberry Pi)
GND - Pin 6 (Ground)
VCC - Pin 2 (5v Power)
SDA - Pin 3 (GPIO 2)
SCL - Pin 5 (GPIO 3)

Current LED Implementation:
Number of LED light used: 5
1. Enter program: flash - white - from left to right, delay = 0.2s
2. Score: all flash - yellow, 0.2s
3. Die during game: all lit - red, 1s
4. Lives running out/Timed out: all lit - red, 2s
4. Success: all lit when entering castle - white, 3s
Current LCD Implementation:
1. Enter program: "Welcome!" - keep displaying until enter game
2. During game: Score: x Lives: x
3. Lives running out: No lives left, Game Over!
4. Fast count down after succeed: Calculating...
5. Timed out: Timed Out, Try Again!
6. Win (before entering castle): Congratulations, You Win!