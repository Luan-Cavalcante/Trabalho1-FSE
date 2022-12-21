import time
import board
import adafruit_dht

def read_dht22(gpio):
    gpio = str(gpio)
    print('#############################################################')
    print(gpio)
    print('#############################################################')
    #sleep(5)
    dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

    # Print the values to the serial port
    temperature_c = dhtDevice.temperature
    humidity = dhtDevice.humidity
    print(f"Temp: {temperature_c:.1f}ºC Humidity: {humidity}%")
    return temperature_c,humidity,dhtDevice
