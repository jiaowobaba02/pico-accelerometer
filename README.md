# pico-accelerometer
pico的加速度计与温度计

# 如何安装
准备硬件：树莓派pico、ds18b20温度传感器,ssd1306 oled显示屏,mpu6050陀螺仪加速度计,四个按键分别标"up""down""left""right"
## 对于ds18b20
out接GP16，-接GND，+接5.0v
## 对于mpu6050
vcc接3.3v,GND接GND,SCL接GP15,SDA接GP14
## 对于ssd1306
vcc接3.3v,GND接GND,SCL接GP0,SDA接GP1
## 对于按键
up接GP21 \
down接GP19 \
left接GP20 \
right接GP18
# 操作
up:跳过/重启
down:更换模式/取消
left:更换频率（更快）/更换模式
right:更换频率（更慢）/更换模式
# 屏幕显示信息说明
校验完毕后，你将看到oled上的这种图像：
```
g: 0.00 m/s^2
 0.000 g
temp: 00.00 °C
gx:0.00g   200    x
gy:0.00g   ms/f   |
gz:1.00g  y-------z
```
g:去除竖直重力加速度
temp:温度（ds18b20上的）
gx,gy,gz:校验后gx,gy,gz原始数据
ms/f:毫秒/帧
坐标系：如果mpu6050与ssd1306引脚连线平行，那就是想对于mpu6050的坐标系
