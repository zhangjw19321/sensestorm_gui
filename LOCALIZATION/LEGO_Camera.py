from threading import Thread
import cv2
import time
import numpy as np


class LEGO_Camera():
    LEGO_camera = []
    EXPOSURE_Value = 0.025
    set_EXPOSURE_Value = 0.025
    target_Light = 140
    Light = 140

    def __init__(self, LEGO_Camera_Index):
        self.LEGO_camera = cv2.VideoCapture(LEGO_Camera_Index)
        self.LEGO_camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        self.LEGO_camera.set(cv2.CAP_PROP_EXPOSURE, self.set_EXPOSURE_Value)
        (self.grabbed, self.frame) = self.LEGO_camera.read()
        self.stopped = False

        # print('cv2.CAP_PROP_EXPOSURE:'+str(self.LEGO_camera.get(cv2.CAP_PROP_EXPOSURE)))
        # time.sleep(0.5)

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                # self.AutoLight()
                #self.LEGO_camera.set(cv2.CAP_PROP_EXPOSURE, self.set_EXPOSURE_Value)
                (self.grabbed, self.frame_ori) = self.LEGO_camera.read()
                self.frame_ori = cv2.resize(self.frame_ori, (320, 240))
                self.frame_ori = self.frame_ori[int(self.frame_ori.shape[0] / 3):self.frame_ori.shape[0], :, :]
                # self.frame  = self.frame_ori
                self.frame = self.balance()
                #cv2.imshow("frame", self.frame)
                #cv2.waitKey(1)

    def stop(self):
        self.stopped = True

    def balance(self):
        b, g, r = cv2.split(self.frame_ori)
        B = np.mean(b)
        G = np.mean(g)
        R = np.mean(r)
        K = (B + G + R) / 3
        Kb = K / B
        Kg = K / G
        Kr = K / R
        # print(K,Kb,Kg,Kr)
        cv2.addWeighted(b, Kb, 0, 0, 0, b)
        cv2.addWeighted(g, Kg, 0, 0, 0, g)
        cv2.addWeighted(r, Kr, 0, 0, 0, r)
        return cv2.merge([b, g, r])

    def AutoLight(self):
        k = self.target_Light / self.Light - 1
        print(k)
        self.set_EXPOSURE_Value = self.EXPOSURE_Value + 2 * k * self.EXPOSURE_Value
