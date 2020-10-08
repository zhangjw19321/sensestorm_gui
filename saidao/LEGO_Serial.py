############################  Serial ########################## 
######### 360 xian
######### lunzi 18 cm

import serial
import time
import threading

class LEGO_Serial():
	ser = []
	A_encoder_num = 0
	B_encoder_num = 0
	C_encoder_num = 0
	D_encoder_num = 0
	threadLock = threading.Lock()
	error_count = 0
	 
	def __init__(self):
		# serial port parameter initialtzation
		self.ser = serial.Serial(
		    port='/dev/ttyAMA0',
		    baudrate = 115200,
		    parity=serial.PARITY_NONE,
		    stopbits=serial.STOPBITS_ONE,
		    bytesize=serial.EIGHTBITS,
		    timeout=0.05
			   )
	def speed_check(self,speed):
		if abs(speed) > 100:
			print("wrong parameter")
			return "0"
		else:
			return speed
	# smp0000p0000p00w70w0.15wp00w80w0.15wm0000000000000000e
	def send_data(self,a_motor,b_motor,c_motor,d_motor):
		motor_parameter = a_motor + b_motor+c_motor+d_motor
		#motor_parameter_header = "smp0000p0000" + motor_parameter + "m"
		#total_len = 42
		#original_len = len(motor_parameter)
		#lack_len = total_len - original_len - 1
		#pad_string = ""
		#for i in range(lack_len):
		#	pad_string = pad_string + "0"
		send_data = motor_parameter + "E"+"N"
		#print(send_data)
		self.ser.write(send_data.encode())
		print("go finished")
	def go(self,A_motor,B_motor,C_motor,D_motor,run_time):
		r_time = '1'
		A_motor = self.speed_check(A_motor)
		B_motor = self.speed_check(B_motor)
		C_motor = self.speed_check(C_motor)
		D_motor = self.speed_check(D_motor)  
		A_motor_parameter = "A" + str(A_motor)
		B_motor_parameter = "B" + str(A_motor)
		C_motor_parameter = "C" + str(A_motor)
		D_motor_parameter = "D" + str(A_motor) + "T" + str(run_time)
		self.send_data(A_motor_parameter,B_motor_parameter,C_motor_parameter,D_motor_parameter)
	def A_go(self,):
		go(0,0)
	def go_encoder(self,A_pwm,B_pwm,C_pwm,D_pwm,run_time):
		#s_time = time.time()
		self.threadLock.acquire()
		
		self.go(A_pwm,B_pwm,C_pwm,D_pwm,run_time)
		
		#print(self.ser)
		readData = self.ser.readline()
		self.threadLock.release()
		#e_time = time.time()
		#print(readData)
		readData = str(readData.decode())
		A_index = readData.find('A')
		B_index = readData.find('B')
		C_index = readData.find('C')
		D_index = readData.find('D')
		E_index = readData.find('E')
		
		if A_index != -1 and E_index != -1 and B_index-A_index>1 and E_index-D_index>1:
			A_num = int(readData[A_index+1:B_index])
			B_num = int(readData[B_index+1:C_index])
			C_num = int(readData[C_index+1:D_index])
			D_num = int(readData[D_index+1:E_index])
		else:
			self.error_count +=1
			A_num = -self.A_encoder_num
			B_num = -self.B_encoder_num
			C_num = -self.C_encoder_num
			D_num = -self.D_encoder_num
		print('error_count:'+str(self.error_count))
		#print('Right_num:'+str(Right_num))
		#return -Left_num,-Right_num
		self.A_encoder_num = -A_num
		self.B_encoder_num = -B_num
		self.C_encoder_num = -C_num
		self.D_encoder_num = -D_num
		return (self.A_encoder_num),(self.B_encoder_num),(self.C_encoder_num),(self.D_encoder_num)

