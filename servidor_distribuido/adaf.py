import time
import board
import adafruit_dht

# Initial the dht device, with data pin connected to:

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

def read_dht22(gpio):
    gpio = str(gpio)
    dhtDevice = adafruit_dht.DHT22((getattr(board,'D'+gpio)),use_pulseio = False)

    # Print the values to the serial port
    temperature_c = dhtDevice.temperature
    humidity = dhtDevice.humidity
    print(f"Temp: {temperature_c:.1f}ºC Humidity: {humidity}%")
    return temperature_c,humidity,dhtDevice

