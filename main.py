#!/usr/bin/python3
from machine import Pin
import utime
import math
import mpu6050
import machine
import onewire
import ds18x20
import time
import uos
from machine import I2C,Pin
from ssd1306 import SSD1306_I2C
i2c=I2C(0,sda=Pin(0),scl=Pin(1),freq=400000)
oled=SSD1306_I2C(128,64,i2c)
background=1
text=0
freq=100
gxoffset = -0.05962
gyoffset = 0.00475
gzoffset = 0.06684
mode_selector=0
print()
ds_pin = machine.Pin(16)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
mpu = mpu6050.MPU6050()
mpu.setSampleRate(200)
mpu.setGResolution(2)
#button=Pin(Btn_Pin,Pin.IN,Pin.PULL_UP)
up=Pin(21,Pin.IN,Pin.PULL_UP)
down=Pin(19,Pin.IN,Pin.PULL_UP)
right=Pin(18,Pin.IN,Pin.PULL_UP)
left=Pin(20,Pin.IN,Pin.PULL_UP)
def calibration_loop(sum):
    gx=0
    gy=0
    gz=0
    oled.fill(background)
    oled.text("please wait",20,0,text)
    oled.text("1 minute",30,9,text)
    oled.show()
    i=1
    while i<=sum:
        oled.fill(background)
        oled.text("please wait",20,0,text)
        g=mpu.readData()
        time_left = (sum-i)/10
        gx+=g.Gx
        gy+=g.Gy
        gz+=g.Gz
        oled.text(f"{time_left} s",30,9,text)
        oled.text(f"gx: {gx/i:.3f}",0,18,text)
        oled.text(f"gy: {gy/i:.3f}",0,27,text)
        oled.text(f"gz: {gz/i:.3f}",0,36,text)
        oled.show()
        utime.sleep_ms(100)
        i+=1
    gx=gx/sum
    gz=gz/sum
    gy=gy/sum
    return -gx,-gy,-gz+1
def init():
    global text,background,gxoffset,gyoffset,gzoffset
    oled.fill(background)
    oled.text("Auto calibration",0,0,text)
    oled.text("Press'up'",20,9,text)
    oled.show()
    while up.value()!=0:
        utime.sleep_ms(10)
    oled.fill(background)
    oled.text("Now choose mode",0,0,text)
    oled.show()
    utime.sleep_ms(750)
    oled.fill(background)
    oled.text("left:fast_mode",0,0,text)
    oled.text("down:medium_mode",0,9,text)
    oled.text("right:slow_mode",0,18,text)
    oled.text("up:use older",0,27,text)
    oled.text("data",0,36,text)
    oled.show()
    sum=0
    sign=0
    while sign!=1:
        utime.sleep_ms(20)
        if up.value()==0:
            sign=1
            with open('data.txt','r') as file:
                gxoffset = float(file.readline().strip())
                gyoffset = float(file.readline().strip())
                gzoffset = float(file.readline().strip())
        if left.value()==0:
            sign=1
            sum=100
            gxoffset,gyoffset,gzoffset=calibration_loop(sum)
            with open('data.txt','w') as file:
                file.write(str(gxoffset) + '\n')
                file.write(str(gyoffset) + '\n')
                file.write(str(gzoffset) + '\n')
        if down.value()==0:
            sign=1
            sum=300
            gxoffset,gyoffset,gzoffset=calibration_loop(sum)
            with open('data.txt','w') as file:
                file.write(str(gxoffset) + '\n')
                file.write(str(gyoffset) + '\n')
                file.write(str(gzoffset) + '\n')
        if right.value()==0:
            sign=1
            sum=600
            gxoffset,gyoffset,gzoffset=calibration_loop(sum)
            with open('data.txt','w') as file:
                file.write(str(gxoffset) + '\n')
                file.write(str(gyoffset) + '\n')
                file.write(str(gzoffset) + '\n')
def watch_dog():
    global mode_selector
    if down.value()==0:
        if mode_selector==0:
            mode_selector=1
        elif mode_selector==1:
            mode_selector=0
        mode_switcher()
    elif up.value()==0:
        oled.fill(background)
        oled.text("Reboot?",40,0,text)
        oled.text("press 'up' to",0,9,text)
        oled.text("confrim",0,18,text)
        oled.text("press 'down' to",0,36,text)
        oled.text("cancel",0,45,text)
        oled.show()
        utime.sleep_ms(500)
        sign=0
        while sign==0:
            utime.sleep_ms(20)
            if up.value()==0:
                machine.reset()
            elif down.value()==0:
                sign=1
def mode_switcher():
    global text,background
    if mode_selector==0:
        text=1
        background=0
    elif mode_selector==1:
        text=0
        background=1
def freq_switcher():
    global freq
    if left.value()==0:
        if (freq-25)>=25:
            freq-=25
    if right.value()==0:
        freq+=25
    print("freq:",freq*2)
def averageMPU(count, timing_ms):
    global gxoffset,gyoffset,gzoffset
    gx = 0
    gy = 0
    gz = 0
    for i in range(count):
        g = mpu.readData()
        gx += g.Gx + gxoffset
        gy += g.Gy + gyoffset
        gz += g.Gz + gzoffset
        utime.sleep_ms(timing_ms)
    return gx / count, gy / count, gz / count
#def loop():
#    while True:
#        g = mpu.readData()
#        print('加速度X：{0:0.2f} g'.format(g.Gx-0.04))
#        print('加速度Y：{0:0.2f} g'.format(g.Gy))
#        print('加速度Z：{0:0.2f} g'.format(g.Gz+0.05))
#        utime.sleep_ms(1000)
def g_sensor():
    gx, gy, gz = averageMPU(50, 2)
    gx = 9.8 * gx
    gy = 9.8 * gy
    gz = 9.8 * gz -9.8
    a = math.sqrt(gx**2 + gy**2 + gz**2)
    return a , gx/9.8 , gy/9.8 , gz/9.8
def get_temp():
    ds_sensor.convert_temp()
    time.sleep_ms(freq)
    temps = []
    for rom in roms:
        temps.append(ds_sensor.read_temp(rom))
    return temps[0] if temps else None
def main_loop():
    while True:
        watch_dog()
        freq_switcher()
        a , gx , gy , gz = g_sensor()
        gz+=1
        temp_now = get_temp()
        g = a/9.8
        print(f"g: {a:.2f} m/s^2 ( {g:.2f} g )  temp: {temp_now} °C")
        #oled.fill(1)
        #oled.show()
        oled.fill(background)
        oled.text(f"g: {a:.2f} m/s^2",0,0,text)
        oled.line(0,9,128,9,text)
        oled.text(f"{g:.3f} g",10,12,text)
        oled.line(0,21,128,21,text)
        oled.text(f"temp: {temp_now:.2f}",0,24,text)
        oled.text(f" C",94,24,text)
        oled.pixel(96,25,text)
        oled.pixel(96,26,text)
        oled.pixel(97,24,text)
        oled.pixel(98,24,text)
        oled.pixel(99,25,text)
        oled.pixel(99,26,text)
        oled.pixel(97,27,text)
        oled.pixel(98,27,text)
        oled.line(0,33,128,33,text)
        oled.text(f"gx:{gx:.2f}g",0,34,text)
        oled.text(f"gy:{gy:.2f}g",0,44,text)
        oled.text(f"gz:{gz:.2f}g",0,54,text)
        oled.text("y",80,54,text)
        oled.line(88,58,116,58,text)
        oled.text("z",118,54,text)
        oled.line(121,42,121,54,text)
        oled.text("x",118,34,text)
        oled.text(f"{freq*2}",76,36,text)
        oled.text("ms/f",76,45,text)
        oled.show()
        utime.sleep_ms(freq)

if __name__ == '__main__':
    init()
    oled.fill(1)
    oled.show()
    oled.fill(0)
    oled.show()
    utime.sleep_ms(500)
    main_loop()

