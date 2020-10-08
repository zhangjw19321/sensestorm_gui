############################  Serial ########################## 
######### 360 xian
######### lunzi 18 cm

import serial
import time
import threading
import brickpi3

class LEGO_Serial():


    ser = []
    Left_encoder_num = 0
    Right_encoder_num = 0
    threadLock = threading.Lock()
    error_count = 0
    bp = brickpi3.BrickPi3()
    last_Left_num = 0
    last_Right_num = 0
     
    def __init__(self):
        # serial port parameter initialtzation
        self.last_Left_num = self.bp.get_motor_encoder(0x02)
        self.last_Right_num = self.bp.get_motor_encoder(0x04)


    def speed_check(self,speed):
        if abs(speed) > 100:
            print("wrong parameter")
            return "0"
        else:
            return speed


    # smp0000p0000p00w70w0.15wp00w80w0.15wm0000000000000000e
    def send_data(self,a_motor,b_motor):
        motor_parameter = a_motor + b_motor
        #motor_parameter_header = "smp0000p0000" + motor_parameter + "m"
        # 计算字符串缺少的长度
        #total_len = 42
        #original_len = len(motor_parameter)
        #lack_len = total_len - original_len - 1
        # 字符串长度补全
        #pad_string = ""
        #for i in range(lack_len):
        #   pad_string = pad_string + "0"
        # 生成最终字符串
        send_data = motor_parameter + "E"+"\n"
        #print(send_data)
        self.ser.write(send_data.encode())


    def go(self,left,right):
        # 设置占空比
        self.bp.set_motor_power(0x02, left)
        self.bp.set_motor_power(0x04, right)
        #time.sleep(r_time)
        #print('go')

    def stop(self):
        go(0,0)
        #print('stop')

    def go_encoder(self,left_pwm,right_pwm):
        self.go(left_pwm,right_pwm)
        Left_num = self.bp.get_motor_encoder(0x02)
        Right_num = self.bp.get_motor_encoder(0x04)
        self.Left_encoder_num = -(Left_num-self.last_Left_num)
        self.Right_encoder_num = -(Right_num-self.last_Right_num)
        self.last_Left_num = Left_num
        self.last_Right_num = Right_num
