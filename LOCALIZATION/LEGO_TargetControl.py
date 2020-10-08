import cv2
import numpy as np
import math
import time

class LEGO_TargetControl():

    Target_Set = []
    WaitGesture = 1
    Target_Index = 0
    Achieve_Count = 0
    last_gesture_index = 0
    same_gesture_num = 0
    last_time = time.time()

    def __init__(self):
        #self.Target_Set = [[0,0],[0.4,0],[0.2,0.3464],[-0.2,0.3464],[-0.4,0],[-0.2,-0.34],[0.2,-0.34]]
        self.Target_Set = [[0,0],[-0.55,0.53],[0,0.53],[0.55,0.53],[-0.55,-0.53],[0,-0.53],[0.55,-0.53]]

    def setTarget(self, index):

        
        #if time.time() - self.last_time > 30:
        #    self.last_time = time.time()
        #    self.Target_Index = self.Target_Index%6+1
        Target = self.Target_Set[index]
        print('Target',Target)
        #print ('Target_Index'+ str(self.Target_Index))
        return Target
