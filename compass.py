from array import array
from utime import sleep
from machine import Pin, I2C
import math

def heading(x, y):
    heading_rad = math.atan2(y, x)
    heading_rad += declination

    # Correct reverse heading.
    while heading_rad < 0:
        heading_rad += 2 * math.pi

    # Compensate for wrapping.
    while heading_rad > 2 * math.pi:
        heading_rad -= 2 * math.pi

    # Convert from radians to degrees.
    heading = heading_rad * 180 / math.pi
    degrees = math.floor(heading)
    minutes = round((heading - degrees) * 60)
    return degrees, minutes

# create an incomming data array of 6 bytes
I2C_SDA_PIN = 0
I2C_SCL_PIN = 1
i2c=I2C(0,sda=Pin(I2C_SDA_PIN), scl=Pin(I2C_SCL_PIN), freq=400000)
data = array('B', [0] * 6)


with open('calibration.txt', 'r') as f:
    calibation = f.read().split('|')
xs = float(calibation[0])
ys = float(calibation[1])
xb = float(calibation[2])
yb = float(calibation[3])
gain = float(calibation[4])
declination = (float(calibation[5]) + float(calibation[6]) / 60) * math.pi / 180

i2c.writeto_mem(0x0D, 0xB, b'\x01')
i2c.writeto_mem(13, 0x9, b'\x011101')
    
while True:
    i2c.readfrom_mem_into(0x0D, 0x00, data)
    x = (data[1] << 8) | data[0]
    y = (data[3] << 8) | data[2]
    z = (data[5] << 8) | data[4]
    
    x = x - (1 << 16) if x & (1 << 15) else x
    y = y - (1 << 16) if y & (1 << 15) else y
    z = z - (1 << 16) if z & (1 << 15) else z

    x = x * gain
    y = y * gain
    z = z * gain

    x = x * xs + xb
    y = y * ys + yb

    degrees, minutes = heading(x, y)
    print('Heading: {}° {}′ '.format(degrees, minutes))
    sleep(.5)


