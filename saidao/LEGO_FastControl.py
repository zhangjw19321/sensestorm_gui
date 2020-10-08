############################  Serial ########################## 
######### 360 xian
######### lunzi 18 cm

import numpy as np
class LEGO_FastControl():
	last_angle_error = 0
	integrate_error = 0
	last_control = 0
	def __init__(self):
		pass	

	def control(self,angle_error,controlMode):#controlMode == 1 means only rotation control
		kpa=0.15#角度控制增益
		kda = 0.3
		kia = 0
		kpd=60#距离控制增益
		self.integrate_error = self.integrate_error+angle_error
		delta_angle_error = angle_error - self.last_angle_error
		distance_error = 70
		distance_control = 40#kpd*distance_error*np.cos(angle_error)
		rotation_control = kpa*angle_error+kda*delta_angle_error+kia*self.integrate_error
		rotation_control = rotation_control*-1
		if rotation_control > 70:
			rotation_control = 70
		if rotation_control < -70:
			rotation_control = -70
		if distance_control > 90:
			distance_control = 90
		if controlMode == 1:
			distance_control = 0
		
		if angle_error == 999:
			distance_control = 70
			rotation_control = self.last_control
		#distance_control = 0
		wl_output = -1*int(distance_control-rotation_control)
		wr_output = -1*int(distance_control+rotation_control)
		self.last_angle_error = angle_error
		self.last_control = rotation_control
		
		if wl_output <-100:
			wr_out_put = wr_output-(wl_output+100) 
			wl_output = -100
		if wr_output <-100:
			wl_output = wl_output-(wr_output+100)
			wr_output = -100
				
		#print ('distance_error'+ str(distance_error))
		#print ('angle_error'+ str(angle_error))
		#print ('distance_control'+ str(distance_control))
		print ('rotation_control'+ str(rotation_control))


		return wl_output,wr_output

	
