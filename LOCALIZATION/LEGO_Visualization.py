import cv2
import numpy as np
import math


class LEGO_Visualization():
    car_img_original = cv2.imread("LOCALIZATION/newsmallcar.png", -1)
    background = cv2.imread("LOCALIZATION/newmap.jpg")

    def rotateImage(self, img, angle):
        height, width = (img.shape[0], img.shape[1])
        size = (width, height)
        center = (width / 2, height / 2)

        matrix = np.zeros((height, width, 4), np.uint8)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale=1)
        img = cv2.warpAffine(img, rotation_matrix, size, matrix,
                             flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_TRANSPARENT)
        return img

    def localizationVisualization(self, estimatePose):
        x_offset, y_offset = estimatePose[0, 0], estimatePose[1, 0]
        x_offset = (x_offset * 500 + 850 / 2 - 100) / 5
        y_offset = (-y_offset * 500 + 850 / 2 - 100) / 5
        angle = (estimatePose[2, 0] - 90 / 180 * math.pi) / math.pi * 180
        # print(estimatePose[2,0])
        car_img = self.rotateImage(self.car_img_original, angle)

        y1, y2 = y_offset, y_offset + car_img.shape[0]
        x1, x2 = x_offset, x_offset + car_img.shape[1]
        alpha_upper = car_img[:, :, 3] / 255.0
        alpha_lower = 1.0 - alpha_upper
        background_new = self.background.copy()
        print('y1:', y1)
        print('y_offset:', y_offset)
        for channel in range(0, 3):
            background_new[y1:y2, x1:x2, channel] = (alpha_upper * car_img[:, :, channel] +
                                                     alpha_lower * self.background[y1:y2, x1:x2, channel])

        cv2.imshow('VisualImage', background_new)

    def practicalVisualization(self, estimatePose, practicle_list, planningTarget):
        x_offset, y_offset = estimatePose[0, 0], estimatePose[1, 0]
        x_offset = (x_offset * 500 + 850 / 2 - 100) / 5
        y_offset = (-y_offset * 500 + 850 / 2 - 100) / 5
        angle = (estimatePose[2, 0] - 90 / 180 * math.pi) / math.pi * 180
        # print(estimatePose[2,0])
        car_img = self.rotateImage(self.car_img_original, angle)

        y1, y2 = y_offset, y_offset + car_img.shape[0]
        x1, x2 = x_offset, x_offset + car_img.shape[1]
        alpha_upper = car_img[:, :, 3] / 255.0
        alpha_lower = 1.0 - alpha_upper
        background_new = self.background.copy()
        print('y1:', y1)
        print('y_offset:', y_offset)
        if x1 > 0 and x2 < 170 and y1 > 0 and y2 < 170:
            for channel in range(0, 3):
                y1 = int(y1)
                y2 = int(y2)
                x1 = int(x1)
                x2 = int(x2)
                background_new[y1:y2, x1:x2, channel] = (alpha_upper * car_img[:, :, channel] +
                                                         alpha_lower * self.background[y1:y2, x1:x2, channel])
        practicle_list = practicle_list.T
        for particle in practicle_list:
            if (-particle[1] * 500 + 850 / 2) > 100 and (-particle[1] * 500 + 850 / 2) < 750 and (
                    -particle[0] * 500 + 850 / 2) > 100 and (-particle[0] * 500 + 850 / 2) < 750:
                background_new[int((-particle[1] * 500 + 850 / 2 - 2) / 5):int((-particle[1] * 500 + 850 / 2 + 2) / 5),
                int((particle[0] * 500 + 850 / 2 - 2) / 5):int((particle[0] * 500 + 850 / 2 + 2) / 5)] = [50, 50, 50]
        background_new[
        int((-planningTarget[1] * 500 + 850 / 2) / 5 - 2):int((-planningTarget[1] * 500 + 850 / 2) / 5 + 2),
        int((planningTarget[0] * 500 + 850 / 2) / 5 - 2):int((planningTarget[0] * 500 + 850 / 2) / 5 + 2)] = [0, 255, 0]
        return background_new
