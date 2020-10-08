import threading
from collections import deque
import math
import multiprocessing
import cv2
import time
import imutils
import numpy as np


class Ball:
    def __init__(self, win_width, win_height):
        self.last_distance = 0
        self.r_distance = 0
        self.yellow_low = (10, 120, 120)
        self.yellow_high = (40, 255, 255)
        self.pts = deque(maxlen=32)
        self.window_size = (80, 60)
        self.mutex = multiprocessing.Lock()
        self.distance = multiprocessing.Value("d", 0.0)
        self.vs = None
        self.ballStopped = False
        self.ball_frame = None
        self.window_width = win_width
        self.window_height = win_height


        pass

    def detect(self):
        while not self.ballStopped:
            self.vs = cv2.VideoCapture(0)
            if not self.vs.isOpened():
                time.sleep(1)
                print("camera error")
                continue
            while not self.ballStopped:
                ret, frame = self.vs.read()
                start_time = time.time()
                frame = imutils.resize(frame, width=160, height=120)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, self.yellow_low, self.yellow_high)
                mask = cv2.erode(mask, None, iterations=2)
                mask = cv2.dilate(mask, None, iterations=2)
                cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
                center = None
                if len(cnts) > 0:
                    c = max(cnts, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)
                    end_time = time.time()
                    time_interval = end_time - start_time
                    if M["m00"] != 0:
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    else:
                        continue
                    # if radius > 10:
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 1)
                    cv2.circle(frame, center, 2, (0, 0, 255), -1)
                self.pts.appendleft(center)
                self.ball_frame = frame
                cv2.namedWindow("ball", 0)
                cv2.resizeWindow("ball", int(self.window_width/3*2), self.window_height)
                cv2.moveWindow("ball", 0, 0)
                cv2.imshow("ball", frame)
                cv2.waitKey(1)
                if center:
                    self.mutex.acquire()
                    self.distance.value = center[0] - self.window_size[0]
                    self.mutex.release()
                    #print("from center: ", (center[0] - self.window_size[0], center[1] - self.window_size[1]))
                for i in range(1, len(self.pts)):
                    if self.pts[i - 1] is None or self.pts[i] is None:
                        continue
                    thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
            self.vs.release()
            cv2.destroyAllWindows()

    def PID(self):
        KP = 1
        Kr = -0.3
        KD = -0.45
        self.mutex.acquire()
        dis = self.distance.value
        self.distance.value = -500
        self.mutex.release()
        if dis == -500:
            return 1000
        D_distance = dis - self.last_distance
        if abs(D_distance) > 5:
            self.r_distance += D_distance
        else:
            if 5 > self.r_distance > -5:
                self.r_distance = 0
            elif self.r_distance < -5:
                self.r_distance += 5
            else:
                self.r_distance -= 5
        self.last_distance = dis
        return round(KP * dis + Kr * self.r_distance + KD * D_distance)

    def motor_action(self, P_dis):
        large = 70
        small = 50
        solid_time = 0.15
        if P_dis > 20:
            if P_dis > 60:
                go(small, large, solid_time)
                print("come here")
            else:
                go(small, large, solid_time)
        elif P_dis < -20:
            if P_dis < -60:
                go(large, small, solid_time)
            else:
                go(large, small, solid_time)
        else:
            go(large, large, solid_time)

    def ball_tracking_robot(self):
        while not self.ballStopped:
            P_dis = self.PID()
            if P_dis > 500:
                continue
            print("P_dis %d" % P_dis)
            self.motor_action(P_dis)

    def __del__(self):
        if self.vs is not None:
            self.vs.release()


if __name__ == '__main__':
    ball = Ball(1980, 1080)
    t = threading.Thread(target=ball.detect)
    t.start()