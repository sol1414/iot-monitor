import time
from machine import Pin
import config

led = Pin("LED", Pin.OUT)


def blink(count):
    """LEDをcount回点滅させる"""
    for _ in range(count):
        led.on()
        time.sleep_ms(config.LED_BLINK_INTERVAL_MS)
        led.off()
        time.sleep_ms(config.LED_BLINK_INTERVAL_MS)
