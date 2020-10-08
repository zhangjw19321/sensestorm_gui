from LEGO_FastControl import LEGO_FastControl
from LEGO_Serial import LEGO_Serial
import numpy as np
import cv2
import time

# np.set_printoptions(threshold='nan')
np.set_printoptions(threshold=np.inf)
FastControl = LEGO_FastControl()
FastSerial = LEGO_Serial()
cap = cv2.VideoCapture(0)
while True:

    ret, frame = cap.read()
    frame = cv2.resize(frame,(512,512),interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    ret,thresh1 = cv2.threshold(gray,80,255,cv2.THRESH_BINARY)
    kernel = np.ones((2,2),np.uint8)
    morpho1 = cv2.morphologyEx(thresh1,cv2.MORPH_CLOSE,kernel,iterations=1)
    # print(rows, cols)
    leftline = np.zeros(512)
    rightline = np.zeros(512)
    middleline = np.zeros(512)
    
    i = 511
    j = 255
    begin_time = time.time()
    left_arg = np.where(morpho1[i,0:j]==0)[0]
    if len(left_arg):
        leftline[i] = left_arg[-1]
    else:
        leftline[i] = 1
    right_arg = np.where(morpho1[i,j:512]==0)[0]
    if len(right_arg):
        rightline[i] = right_arg[0]+j
    else:
        rightline[i] = 511
    middleline[i] = int((leftline[i]+rightline[i])/2)
    morpho1[i][int(middleline[i])] = 128
    
    for i in range(510,-1,-1):
        j = middleline[i+1]
        left_arg = np.where(morpho1[i,0:int(j)]==0)[0]
        if len(left_arg):
            leftline[i] = left_arg[-1]
        else:
            leftline[i] = 1
        j = middleline[i+1]
        right_arg = np.where(morpho1[i,int(j):512]==0)[0]
        if len(right_arg):
            rightline[i] = right_arg[0]+j
        else:
            rightline[i] = 511
        middleline[i] = int((leftline[i]+rightline[i])/2)
        morpho1[i][int(middleline[i])] = 128
    center2 = middleline[480] -255   
    end_time = time.time()
    interval_time = end_time-begin_time
    print("interval_time:",interval_time)   
    wl_output,wr_output = FastControl.control(center2,0)
    cv2.putText(morpho1,str(center2) + "   " + str(wr_output),(20,100),cv2.FONT_HERSHEY_COMPLEX,2,(0,0,0),2)
    # cv2.line(thresh1,pstart,pend,(255,155,155),2)
    FastSerial.go_encoder(wl_output,wr_output,0)

    cv2.imshow("ff",morpho1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break




