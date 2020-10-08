import cv2
import time
import math
import numpy as np
import pickle


class LEGO_ColorPillarDetection():
    # Green LAB
    Green_low = (103, 84, 126)
    Green_high = (163, 124, 166)
    # print Green_low
    # print Green_high

    # Red LAB
    Red_low = (55, 157, 132)
    Red_high = (115, 197, 172)

    Red_low_1 = (165, 165, 40)
    Red_high_1 = (180, 255, 255)
    Red_low_2 = (0, 165, 40)
    Red_high_2 = (5, 255, 255)

    # print Red_low
    # print Red_high

    # Blue LAB
    Blue_low = (54, 117, 63)
    Blue_high = (114, 157, 103)
    # print Blue_low
    # print Blue_high

    # ratio Calibrate (cm)
    ratioCalibrateDistance = 60
    ratioCalibrateWidth = 85

    # realDistance = realDistanceTimesPixelWidth / pixelWidth
    realDistanceTimesPixelWidth = 1950

    # ohter settings
    font = cv2.FONT_HERSHEY_SIMPLEX

    lab = []

    hsv = []

    def __init__(self):
        pass

    def getpos(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(lab[y, x])

    def getpos_hsv(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(hsv[y, x])

    def AutoLab(self, LEGO_Camera_colorPillar, LEGO_Video_shower):
        global lab, hsv
        targetRectangleWidth = 38
        targetRectangleHidth = targetRectangleWidth * 3
        sampleRectangleWidth = targetRectangleWidth * 0.7

        # vs = cv2.VideoCapture(0)
        time.sleep(0.5)
        frame = LEGO_Camera_colorPillar.frame
        # frame = frame[int(frame.shape[0]/4):frame.shape[0],:,:]
        frame = cv2.blur(frame, (11, 11))
        leftUpperCorner_x = int(frame.shape[1] / 2 - targetRectangleWidth / 2)
        leftUpperCorner_y = int(frame.shape[0] / 2 - targetRectangleHidth * 0.45)
        rightBottomCorner_x = int(frame.shape[1] / 2 + targetRectangleWidth / 2)
        rightBottomCorner_y = int(frame.shape[0] / 2 + targetRectangleHidth * (0.55))

        secondPoint = [int((leftUpperCorner_x + rightBottomCorner_x) / 2),
                       int((leftUpperCorner_y + rightBottomCorner_y) / 2)]
        firstPoint = [secondPoint[0], secondPoint[1] - targetRectangleWidth]
        thirdPoint = [secondPoint[0], secondPoint[1] + targetRectangleWidth]
        print('auto light ing...')

        frame = LEGO_Camera_colorPillar.frame
        avgLight = np.mean(frame)
        LEGO_Camera_colorPillar.Light = avgLight

        while True:
            frame = LEGO_Camera_colorPillar.frame
            frame = cv2.blur(frame, (11, 11))
            frameVisual = frame.copy()
            cv2.rectangle(frameVisual, (int(leftUpperCorner_x), int(leftUpperCorner_y)),
                          (int(rightBottomCorner_x), int(rightBottomCorner_y)), (0, 0, 0), 4)
            cv2.circle(frameVisual, (firstPoint[0], firstPoint[1]), 3, (0, 0, 255), -1)
            cv2.circle(frameVisual, (secondPoint[0], secondPoint[1]), 3, (0, 0, 255), -1)
            cv2.circle(frameVisual, (thirdPoint[0], thirdPoint[1]), 3, (0, 0, 255), -1)
            # cv2.imshow("AutoLab",frameVisual)
            LEGO_Video_shower.AutoColorImage = frameVisual
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            firstSampleRectangleImg = lab[int(firstPoint[1] - sampleRectangleWidth / 4):int(
                firstPoint[1] + sampleRectangleWidth / 4), int(firstPoint[0] - sampleRectangleWidth / 4):int(
                firstPoint[0] + sampleRectangleWidth / 4), :]
            secondSampleRectangleImg = lab[int(secondPoint[1] - sampleRectangleWidth / 4):int(
                secondPoint[1] + sampleRectangleWidth / 4), int(secondPoint[0] - sampleRectangleWidth / 4):int(
                secondPoint[0] + sampleRectangleWidth / 4), :]
            thirdSampleRectangleImg = lab[int(thirdPoint[1] - sampleRectangleWidth / 4):int(
                thirdPoint[1] + sampleRectangleWidth / 4), int(thirdPoint[0] - sampleRectangleWidth / 4):int(
                thirdPoint[0] + sampleRectangleWidth / 4), :]
            # cv2.imshow("lab",lab)
            # cv2.imshow("hsv",hsv)
            # cv2.imshow("fisrtSampleRec",thirdSampleRectangleImg)
            # cv2.setMouseCallback("lab",self.getpos)
            # cv2.setMouseCallback("hsv",self.getpos_hsv)
            # print (firstSampleRectangleImg.shape,)
            firstSampleRectangleAvgLab = firstSampleRectangleImg.mean(0).mean(0)
            secondSampleRectangleAvgLab = secondSampleRectangleImg.mean(0).mean(0)
            thirdSampleRectangleAvgLab = thirdSampleRectangleImg.mean(0).mean(0)
            firstSampleRectangleAvgLab_max = firstSampleRectangleImg.max(0).max(0)
            firstSampleRectangleAvgLab_min = firstSampleRectangleImg.min(0).min(0)
            avgLight = np.mean(frame)

            # key = cv2.waitKey(1) & 0xFF
            if LEGO_Video_shower.autoColorStopped or LEGO_Video_shower.autoColorCancled:
                break
            # if key == ord("q"):
            #   print (firstSampleRectangleAvgLab_min, firstSampleRectangleAvgLab_max)
            #   break 

        # cv2.destroyAllWindows()
        if LEGO_Video_shower.autoColorCancled:
            return 0, 0, 0, 0
        save_file = open("LOCALIZATION/ColorSave.txt", "wb")
        pickle.dump(firstSampleRectangleAvgLab, save_file)
        pickle.dump(secondSampleRectangleAvgLab, save_file)
        pickle.dump(thirdSampleRectangleAvgLab, save_file)
        save_file.close()
        return firstSampleRectangleAvgLab, secondSampleRectangleAvgLab, thirdSampleRectangleAvgLab, avgLight

    def labRangeUpdate(self):

        ### Distance
        load_file = open("LOCALIZATION/ColorSave.txt", "rb")
        firstSampleRectangleAvgLab = pickle.load(load_file)
        secondSampleRectangleAvgLab = pickle.load(load_file)
        thirdSampleRectangleAvgLab = pickle.load(load_file)
        load_file.close()

        self.Green_low = (max(int(firstSampleRectangleAvgLab[0] - 30), 0), int(firstSampleRectangleAvgLab[1] - 20),
                          int(firstSampleRectangleAvgLab[2] - 20))
        self.Green_high = (min(int(firstSampleRectangleAvgLab[0] + 30), 255), int(firstSampleRectangleAvgLab[1] + 20),
                           int(firstSampleRectangleAvgLab[2] + 20))
        print(self.Green_low)
        print(self.Green_high)

        # Red LAB
        self.Red_low = (max(int(secondSampleRectangleAvgLab[0] - 30), 0), int(secondSampleRectangleAvgLab[1] - 20),
                        int(secondSampleRectangleAvgLab[2] - 20))
        self.Red_high = (min(int(secondSampleRectangleAvgLab[0] + 30), 255), int(secondSampleRectangleAvgLab[1] + 20),
                         int(secondSampleRectangleAvgLab[2] + 20))
        print(self.Red_low)
        print(self.Red_high)

        # Blue LAB
        self.Blue_low = (max(int(thirdSampleRectangleAvgLab[0] - 30), 0), int(thirdSampleRectangleAvgLab[1] - 20),
                         int(thirdSampleRectangleAvgLab[2] - 20))
        self.Blue_high = (min(int(thirdSampleRectangleAvgLab[0] + 30), 255), int(thirdSampleRectangleAvgLab[1] + 20),
                          int(thirdSampleRectangleAvgLab[2] + 20))
        print(self.Blue_low)
        print(self.Blue_high)

    def TwoPointDistance(self, x1, y1, x2, y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def RGBSeq(self, r_x, r_y, g_x, g_y, b_x, b_y, r_l, g_l, b_l):

        # print (r_x,g_x,b_x)
        if abs(r_x - g_x) > 20 or abs(r_x - b_x) > 20 or abs(g_x - b_x) > 20:
            return 0, 0, 0, 0

        d_RG = self.TwoPointDistance(r_x, r_y, g_x, g_y)
        d_RB = self.TwoPointDistance(r_x, r_y, b_x, b_y)
        d_GB = self.TwoPointDistance(g_x, g_y, b_x, b_y)
        d_list = [d_RG, d_RB, d_GB]
        d_list.sort()

        # avg_l = int((r_l + g_l + b_l)/3)
        avg_l = int(max(r_l, g_l, b_l))
        if ((d_list[0] + d_list[1]) > d_list[2] * 0.8 and (d_list[0] + d_list[1]) < d_list[2] * 1.2 and avg_l * 0.5 <
                d_list[0] and d_list[0] < avg_l * 1.5 and avg_l * 0.5 < d_list[1] and d_list[
                    1] < avg_l * 1.5 and avg_l * 1.5 < d_list[2] and d_list[2] < avg_l * 2.5):
            if (g_y < r_y and r_y < b_y):  # GRB
                return 1, r_x, r_y, avg_l
            elif (b_y < g_y and g_y < r_y):  # BGR
                return 2, g_x, g_y, avg_l
            elif (r_y < b_y and b_y < g_y):  # RBG
                return 3, b_x, b_y, avg_l
            elif (b_y < r_y and r_y < g_y):  # BRG
                return 4, r_x, r_y, avg_l
            elif (g_y < b_y and b_y < r_y):  # GBR
                return 5, b_x, b_y, avg_l
            elif (r_y < g_y and g_y < b_y):  # RGB
                return 6, g_x, g_y, avg_l
            else:
                return 0, 0, 0, 0
        else:
            return 0, 0, 0, 0

    def Detection_Once(self, image, LEGO_Video_shower):

        frame = image.copy()
        # frame = frame[int(frame.shape[0]/4):frame.shape[0],:,:]
        start_time = time.time()
        blurred = cv2.blur(frame, (5, 5))
        lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)

        Green_mask = cv2.inRange(lab, self.Green_low, self.Green_high)
        LEGO_Video_shower.Mask = image
        # cv2.imshow("mask1", Green_mask)
        Green_mask = cv2.dilate(Green_mask, None, iterations=1)
        Green_mask = cv2.erode(Green_mask, None, iterations=6)
        Green_mask = cv2.dilate(Green_mask, None, iterations=5)
        # Green_mask = cv2.dilate(Green_mask, None, iterations=15)
        # cv2.imshow("mask2", Green_mask)
        Red_mask = cv2.inRange(lab, self.Red_low, self.Red_high)
        # Red_mask_1 = cv2.inRange(lab, self.Red_low_1, self.Red_high_1)
        # Red_mask_2 = cv2.inRange(lab, self.Red_low_2, self.Red_high_2)
        # Red_mask = Red_mask_1 + Red_mask_2

        # cv2.imshow("mask1", Red_mask)
        Red_mask = cv2.dilate(Red_mask, None, iterations=1)
        Red_mask = cv2.erode(Red_mask, None, iterations=6)
        # cv2.imshow("mask2", Red_mask)
        Red_mask = cv2.dilate(Red_mask, None, iterations=5)
        # cv2.imshow("mask3", Red_mask)

        Blue_mask = cv2.inRange(lab, self.Blue_low, self.Blue_high)
        Blue_mask = cv2.dilate(Blue_mask, None, iterations=1)
        Blue_mask = cv2.erode(Blue_mask, None, iterations=6)
        Blue_mask = cv2.dilate(Blue_mask, None, iterations=5)

        Green_points = []
        Red_points = []
        Blue_points = []

        # cv2.imshow("mask_1", Red_mask_1)
        # cv2.imshow("mask_2", Red_mask_2)

        # cv2.imshow("lab", lab)
        # cv2.setMouseCallback("lab",getpos)
        out_binary, contours, hierarchy = cv2.findContours(Green_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in range(len(contours)):
            # print(len(contours[cnt]))
            if len(contours[cnt]) < 3:
                continue
            girth = cv2.arcLength(contours[cnt], True)
            area = cv2.contourArea(contours[cnt])
            # print(area)
            if area < 250:
                continue
            # cv2.drawContours(frame, contours, cnt, (0, 255, 0), 2)
            mm = cv2.moments(contours[cnt])
            cx = int(mm['m10'] / mm['m00'])
            cy = int(mm['m01'] / mm['m00'])
            cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)
            Green_points.append([cx, cy, int(girth / 4)])

        out_binary, contours, hierarchy = cv2.findContours(Red_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in range(len(contours)):
            # print(len(contours[cnt]))
            if len(contours[cnt]) < 3:
                continue
            girth = cv2.arcLength(contours[cnt], True)
            area = cv2.contourArea(contours[cnt])
            # print(area)
            if area < 250:
                continue
            # cv2.drawContours(frame, contours, cnt, (0, 0, 255), 2)
            mm = cv2.moments(contours[cnt])
            cx = int(mm['m10'] / mm['m00'])
            cy = int(mm['m01'] / mm['m00'])
            cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)
            Red_points.append([cx, cy, int(girth / 4)])

        out_binary, contours, hierarchy = cv2.findContours(Blue_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # print(len(contours))
        for cnt in range(len(contours)):
            if len(contours[cnt]) < 3:
                continue
            girth = cv2.arcLength(contours[cnt], True)
            area = cv2.contourArea(contours[cnt])
            if area < 250:
                continue
            # cv2.drawContours(frame, contours, cnt, (255, 0, 0), 2)
            mm = cv2.moments(contours[cnt])
            cx = int(mm['m10'] / mm['m00'])
            cy = int(mm['m01'] / mm['m00'])
            cv2.circle(frame, (cx, cy), 3, (255, 0, 0), -1)
            Blue_points.append([cx, cy, int(girth / 4)])

        results = []
        result = [0, 0, 0, 0]
        for Red_point in Red_points:
            for Green_point in Green_points:
                for Blue_point in Blue_points:
                    result = self.RGBSeq(Red_point[0], Red_point[1], Green_point[0], Green_point[1], Blue_point[0],
                                         Blue_point[1], Red_point[2], Green_point[2], Blue_point[2])
                    if result[0] != 0:
                        # print result

                        # Compute Distance 
                        realDistance = (self.realDistanceTimesPixelWidth / result[3])
                        # print(str(result[0])+'Left------Distance:' + str(realDistance))
                        realTanRatio = math.tan(math.atan((self.ratioCalibrateWidth / self.ratioCalibrateDistance)) * (
                                    (result[1] - 159.5) / 320))
                        # print(math.cos(math.atan(realTanRatio)))
                        realDistance = realDistance / math.cos(math.atan(realTanRatio))
                        realRatio = math.atan(realTanRatio)
                        realAngle = realRatio * 180 / math.pi

                        # print 'Left------Distance:' + str(realDistance)
                        # print 'Left------Ratio:' + str(realRatio)

                        # visual
                        cv2.rectangle(frame, (int(result[1] - result[3] / 2), int(result[2] - result[3] * 3 / 2)),
                                      (int(result[1] + result[3] / 2), int(result[2] + result[3] * 3 / 2)),
                                      (255, 255, 255), 2)
                        cv2.putText(frame, str(int(realDistance)),
                                    (int(result[1] - result[3] * 0.5), int(result[2] - result[3] * 1.5)), self.font,
                                    1.2, (255, 255, 255), 2)
                        cv2.putText(frame, str(int(realAngle)), (int(result[1]), int(result[2] - result[3] * 1.5)),
                                    self.font, 1.2, (0, 0, 255), 2)

                        results.append((result, realDistance, realRatio))

        distanceAll = [9999, 9999, 9999, 9999, 9999, 9999]
        radianAll = [9999, 9999, 9999, 9999, 9999, 9999]
        for result in results:
            if result[0][0] != 0:
                distanceAll[result[0][0] - 1] = result[1] / 100
                radianAll[result[0][0] - 1] = -result[2]

        pillarTheta = np.array(radianAll)  # input
        pillarDistance = np.array(distanceAll)  # input

        end_time = time.time()
        # print('time:',end_time-start_time)
        # cv2.imshow("frame_left", frame)
        return pillarTheta, pillarDistance, frame
