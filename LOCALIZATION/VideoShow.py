from threading import Thread
import cv2


class VideoShow:
    """
    Class that continuously shows a frame using a dedicated thread.
    """

    def __init__(self, frame=None):
        self.frame = frame
        self.hsvframe = frame
        self.labframe = frame
        self.visualImage = frame
        self.AutoColorImage = frame
        self.Mask = frame
        self.stopped = False
        self.autoColorStopped = True
        self.autoColorCancled = False
        self.guideMapStopped = True

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        # cv2.namedWindow("Mask")
        # cv2.resizeWindow("Mask", 640, 480);

        while not self.stopped:
            # print('show')
            # cv2.imshow("hsv", self.hsv)
            # cv2.imshow("lab",self.labframe)
            if not self.autoColorStopped:
                # cv2.imshow("Mask",self.Mask)
                # cv2.imshow("AutoColorImage",self.AutoColorImage)
                pass
            if not self.guideMapStopped:
                # cv2.imshow("Video", self.frame)
                # cv2.imshow("Visual", self.visualImage)
                pass
            cv2.waitKey(1)

    def stop(self):
        self.stopped = True
