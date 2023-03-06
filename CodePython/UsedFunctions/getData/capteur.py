import bme280
import smbus2
import datetime
from time import sleep

port = 1
address = 0x77 # Adafruit BME280 address. Other BME280s may be different
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus, address)

Ts = 10 # Sampling period (should be the same as RINEX one)

file = './BuyoData/METEO/logMETEO.txt'
# Write header 
with open(file, 'w') as f:
    header = "date, temperature_C, pression_hPa, humidity_per\n"
    f.write(header)

while True:
    # Get sensor data
    bme280_data = bme280.sample(bus, address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    temperature = bme280_data.temperature

    # Get current date
    now = datetime.now()
    date = now.strftime("%d%m%Y %H:%M:%S")

    # Write log
    with open(file, 'w') as f:
        line = f"{date}, {temperature}, {pressure}, {humidity}\n"
        f.write(line)

    sleep(Ts)


