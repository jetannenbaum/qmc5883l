from array import array
from utime import sleep
from machine import Pin, I2C

I2C_SDA_PIN = 0
I2C_SCL_PIN = 1
Xmin=0
Xmax=-0
Ymin=0
Ymax=-0
gain = 0.73
declination = [0] * 2

print("Find your Magnetic Declination Here: https://www.magnetic-declination.com/")
declination[0] = input("Enter Magnetic Declination (Degrees only): ")
declination[1] = input("Enter Magnetic Declination (Minutes only): ")

print("Rotate your sensor around all axis.  Once the numbers stop changing, hit ctrl-c")

i2c=I2C(0,sda=Pin(I2C_SDA_PIN), scl=Pin(I2C_SCL_PIN), freq=400000)
data = array('B', [0] * 6)

i2c.writeto_mem(0x0D, 0xB, b'\x01')
i2c.writeto_mem(0x0D, 0x9, b'\x011101')

while True:
    try:
        sleep(0.2)
        i2c.readfrom_mem_into(0x0D, 0x00, data)
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]
       
        x = x - (1 << 16) if x & (1 << 15) else x
        y = y - (1 << 16) if y & (1 << 15) else y
        z = z - (1 << 16) if z & (1 << 15) else z

        x = x * gain
        y = y * gain

        Xmin=min(x,Xmin)
        Xmax=max(x,Xmax)
        Ymin=min(y,Ymin)
        Ymax=max(y,Ymax)

        print("Xmin="+str(Xmin)+"; Xmax="+str(Xmax)+"; Ymin="+str(Ymin)+"; Ymax="+str(Ymax))

    except KeyboardInterrupt:
        print()
        print('Got ctrl-c')
        
        xs=1
        ys=(Xmax-Xmin)/(Ymax-Ymin)
        xb =xs*(1/2*(Xmax-Xmin)-Xmax)
        yb =xs*(1/2*(Ymax-Ymin)-Ymax)
        print("Calibration corrections:")
        print("xs="+str(xs))
        print("xb="+str(xb))
        print("ys="+str(ys))
        print("yb="+str(yb))
        with open('calibration.txt', 'w') as f:
            f.write(str(xs) + '|' + str(ys) + '|' + str(xb) + '|' + str(yb) + '|' + str(gain) + '|' + declination[0] + '|' + declination[1])
        break

