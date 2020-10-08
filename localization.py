import time

from LOCALIZATION import LEGO_Localization
from LOCALIZATION import LEGO_Serial
from LOCALIZATION import LEGO_TargetControl
from LOCALIZATION import LEGO_Visualization
from LOCALIZATION import LEGO_ColorPillarDetection
from LOCALIZATION import VideoShow
from LOCALIZATION import LEGO_Camera
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler


class Localization:
    def __init__(self):

        self.LEGO_Camera_colorPillar = LEGO_Camera.LEGO_Camera(0)
        self.LEGO_Video_shower = VideoShow.VideoShow(self.LEGO_Camera_colorPillar.frame)
        self.LEGO_ColorPillarDetection = LEGO_ColorPillarDetection.LEGO_ColorPillarDetection()
        self.LEGO_Serial = LEGO_Serial.LEGO_Serial()
        self.LEGO_Visualization = LEGO_Visualization.LEGO_Visualization()
        self.LEGO_Localization = LEGO_Localization.LEGO_Localization()
        self.LEGO_TargetControl = LEGO_TargetControl.LEGO_TargetControl()

        self.target_index = 0
        self.quit_flag = False
        self.do_flag = 0

    def startCamera(self):
        self.LEGO_Camera_colorPillar.start()

    def stopCamera(self):
        self.LEGO_Camera_colorPillar.stop()

    def autoLight(self):
        _ = self.LEGO_ColorPillarDetection.AutoLab(self.LEGO_Camera_colorPillar, self.LEGO_Video_shower)
        self.LEGO_ColorPillarDetection.labRangeUpdate()

    def startWork(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.set_flag_do, 'interval', max_instances=5, seconds=0.1, id='job_set_flag')
        scheduler.start()
        while not self.quit_flag:
            if self.LEGO_Camera_colorPillar.stopped or self.LEGO_Video_shower.stopped:
                self.LEGO_Video_shower.stop()
                self.LEGO_Camera_colorPillar.stop()
            self.do()
        scheduler.remove_job('job_set_flag')
        scheduler.shutdown(wait=False)

    def set_flag_do(self):
        self.do_flag = 1
        print('set do flag')

    def do(self):
        start_time = time.time()
        Target = self.LEGO_TargetControl.setTarget(self.target_index)
        planTarget, controlMode = self.LEGO_Localization.planning(time.time(), Target)
        Left_speed, Right_speed = self.LEGO_Localization.control(planTarget, controlMode)
        self.LEGO_Serial.go_encoder(Left_speed, Right_speed)
        wl_measure = self.LEGO_Serial.Left_encoder_num * self.LEGO_Localization.encoder_index
        wr_measure = self.LEGO_Serial.Right_encoder_num * self.LEGO_Localization.encoder_index
        pillarTheta, pillarDistance, self.LEGO_Video_shower.frame = \
            self.LEGO_ColorPillarDetection.Detection_Once(self.LEGO_Camera_colorPillar.frame, self.LEGO_Video_shower)
        estimatePose, practical_list = self.LEGO_Localization.practicalLocalization(wr_measure, wl_measure, pillarTheta,pillarDistance)
        self.LEGO_Video_shower.visualImage = self.LEGO_Visualization.practicalVisualization(estimatePose, practical_list, planTarget)
        end_time = time.time()
        interval_time = end_time - start_time
        print("interval time", interval_time)


if __name__ == '__main__':
    loc = Localization()
    loc.startCamera()

    pass
