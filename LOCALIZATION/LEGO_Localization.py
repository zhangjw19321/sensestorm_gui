############################  Serial ########################## 
######### 360 xian
######### lunzi 18 cm

import numpy as np

'''
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
'''


class LEGO_Localization():
    wr_measure = 0
    wl_measure = 0
    pillarTheta = 0
    pillarDistance = 0
    pi = 3.141592653
    s = np.array([[0], [0], [0]])
    A = np.eye(3)
    k = 0
    dt = 0.2
    L = 0.185
    R = 0.00001
    R_dis = 0.2
    Q = 0.000002
    QS = 0.001  # START SQUARE ERROR
    tf = 200
    encoder_index = 0.0005
    ValueRatio = 1000
    ValueRatio_dis = 10
    visual_angle = pi / 6
    N = 100
    P = 0.002 * np.eye(3)
    A = np.eye(3)
    N_eff = N
    s_record = []
    s_x = []
    s_y = []
    s_z = []
    sF_x = []
    sF_y = []
    sF_z = []
    filterResult = []
    sResult = []
    visualNum_record = []
    last_angle_error = 0
    pillar = np.array([[-0.825, 0.8],
                       [0, 0.8],
                       [0.825, 0.8],
                       [-0.825, -0.8],
                       [0, -0.8],
                       [0.825, -0.8]])
    # print(pillar)
    spart = np.ones([3, N]) * s + np.random.randn(3, N) * np.sqrt(QS)
    spartVector = np.zeros([4, N])
    estimatePose = np.zeros([3, 1])

    planningTime = 0
    planningPos = np.array([0, 0])
    lastTarget = np.array([0, 0])
    planTarget = np.array([0, 0])
    avoidTarget = np.array([0, 0])
    planstep = [0, 1]
    TrajectoryTime = 1
    from LOCALIZATION import LEGO_Astar
    avoidancePlan = LEGO_Astar.LEGO_Astar()
    avoidanceTraj = []
    avoidNum = 1

    def __init__(self):
        pass

    def piRound(self, w):
        wtemp = w - 2 * np.pi * (w > np.pi) + 2 * np.pi * (w < -np.pi)
        wtemp[np.abs(w) > 10] = 9999
        # print('wtep________',wtemp)
        return wtemp

    def update(self, A, s2, wl, wr, L):
        w = (wr + wl) / 2
        dtheta = (wr - wl) / self.L
        u1 = w * np.cos(s2[2, :] + dtheta / 2)
        u2 = w * np.sin(s2[2, :] + dtheta / 2)
        u3 = dtheta
        u = np.vstack((u1, u2, u3))
        s2 = s2 + u
        return s2

    def practicalLocalization(self, wr_measure, wl_measure, pillarTheta, pillarDistance):
        # 右轮编码距离，float，左轮编码距离，float，柱子角度观测值,array，柱子距离观测值,array
        if wr_measure != -1 or wl_measure != -1:
            pillarTheta = self.piRound(pillarTheta)  # 得到角度估计值后先行预处理
            # print('w_a',pillarTheta)
            y = pillarTheta  # 本程序中，y代表角度测量值，y_dis代表距离测量值
            y_dis = pillarDistance * pillarDistance  # 距离全部按照平方项处理
            # print(y)
            visual_num = np.sum(np.abs(y) < 10)  # 看不到的柱子会被设定为9999，计算能看到的柱子数量
            visual_pos = np.abs(y) < self.visual_angle  # 计算能看到的柱子位置
            spartTemp = self.update(self.A, self.spart, wl_measure + 1 * np.sqrt(self.Q) * np.random.randn(1, self.N),
                                    wr_measure + 1 * np.sqrt(self.Q) * np.random.randn(1, self.N), self.L)
            # spartTemp为粒子更新过程中的暂时变量，这一步对所有粒子进行动力学更新
            spartTemp[2, :] = self.piRound(spartTemp[2, :])  # 对更新后的粒子角度进行预处理
            s_angle_y = self.pillar[:, 1].reshape(-1, 1) * np.ones([1, self.N]) - np.ones(
                [self.pillar.shape[0], 1]) * spartTemp[1, :].reshape(1, -1)
            s_angle_x = self.pillar[:, 0].reshape(-1, 1) * np.ones([1, self.N]) - np.ones(
                [self.pillar.shape[0], 1]) * spartTemp[0, :].reshape(1, -1)
            ypart = np.arctan2(s_angle_y, s_angle_x) - np.ones([self.pillar.shape[0], 1]) * spartTemp[2, :].reshape(1,
                                                                                                                    -1)
            ypart = self.piRound(ypart)  # 以上四句为计算所有粒子应该看到的柱子角度
            s_dis_y = self.pillar[:, 1].reshape(-1, 1) * np.ones([1, self.N]) - np.ones(
                [self.pillar.shape[0], 1]) * spartTemp[1, :]
            s_dis_x = self.pillar[:, 0].reshape(-1, 1) * np.ones([1, self.N]) - np.ones(
                [self.pillar.shape[0], 1]) * spartTemp[0, :]
            y_dispart = s_dis_y * s_dis_y + s_dis_x * s_dis_x  # 以上三句为计算所有粒子应该看到的柱子距离
            vhat = y.reshape(-1, 1) * np.ones([1, self.N]) - ypart
            vhat = self.piRound(vhat)  # vhat为粒子与测量值在角度上的差值
            vhat_dis = y_dis.reshape(-1, 1) * np.ones([1, self.N]) - y_dispart  # 粒子与测量值在距离上的差值
            q = (1 / np.sqrt(self.R * 2 * np.pi)) * np.exp(-vhat * vhat * self.ValueRatio)  # 计算粒子在角度的适应程度，将角度差值进行非线性处理
            q_dis = (1 / np.sqrt(self.R * 2 * np.pi)) * np.exp(
                -vhat_dis * vhat_dis * self.ValueRatio_dis)  # 计算粒子在距离上的适应程度，将距离差值进行非线性处理
            # ValueRatio越大，粒子选择越精英化
            q[q < 0.000001] = 0.000001
            q_dis[q_dis < 0.000001] = 0.000001  # 防止出现0值造成计算bug
            qsum = np.sum(q, 1) + 0.000001  # 求和所有的角度适应度
            q_dissum = np.sum(q_dis, 1) + 0.000001  # 球和所有的距离适应度
            q = q / (qsum.reshape(-1, 1) * np.ones([1, self.N]))  # 相加粒子在所有柱子角度适应度
            q_dis = q_dis / (q_dissum.reshape(-1, 1) * np.ones([1, self.N]))  # 相加粒子在所有柱子距离适应度
            q = (q + q_dis) / 2  # 距离适应度与角度适应度1：1相加
            weight = np.sum(q, 0) / self.pillar.shape[0]  # 适应度归一化，成为各个粒子的权重
            i = 1
            letto = np.ones([self.N])  # letto彩券，共N张，粒子权重越高，占有彩券数量越多
            old_pos = 0
            N_eff = np.sum(weight > 1 / self.N)  # 计算有效粒子数量，有效粒子数量较低时，进行重采样，更新粒子spart
            print('N_eff', N_eff)
            if (N_eff < 0.3 * self.N) and (visual_num > 0):
                qtempsum = 0
                for j in range(self.N):
                    qtempsum = qtempsum + np.sum(q[:, j] * visual_pos) / visual_num
                    new_pos = int(np.round(qtempsum * self.N))
                    if new_pos != old_pos:
                        letto[old_pos:new_pos] = j
                    old_pos = new_pos
                u = np.floor(np.random.rand(1, self.N) * self.N)
                self.spart = spartTemp[:, letto[u.astype(int).reshape(-1)].astype(int)]
                q = 1 / self.N * np.ones([self.pillar.shape[0], self.N])  # 重采样后，所有粒子权重均等
            else:
                self.spart = spartTemp  # 若不重采样，则所有粒子保持原有权重不变
            weight = np.sum(q, 0) / self.pillar.shape[0]  # 重采样后再次计算一次权重
            self.spartVector[0:2, :] = self.spart[0:2, :]
            self.spartVector[2, :] = np.cos(self.spart[2, :])
            self.spartVector[3, :] = np.sin(self.spart[2, :])
            estimatePoseVector = np.matmul(self.spartVector, weight.reshape(-1, 1))
            self.estimatePose[0:2, :] = estimatePoseVector[0:2, :]
            self.estimatePose[2, :] = np.arctan2(estimatePoseVector[3, :], estimatePoseVector[2, :])
            return self.estimatePose, self.spart
        else:
            return self.estimatePose, self.spart

    def control(self, Target, controlMode):  # controlMode == 1 means only rotation control
        kpa = 30  # 角度控制增益
        kda = 30
        kpd = 80  # 距离控制增益
        angle_target = np.arctan2(Target[1] - self.estimatePose[1], Target[0] - self.estimatePose[0])
        angle_error = (angle_target - self.estimatePose[2])
        angle_error = self.piRound(angle_error)
        delta_angle_error = angle_error - self.last_angle_error
        distance_error = np.sqrt((Target[1] - self.estimatePose[1]) ** 2 + (Target[0] - self.estimatePose[0]) ** 2)
        distance_control = kpd * distance_error * np.cos(angle_error)
        rotation_control = kpa * angle_error + kda * delta_angle_error
        if distance_error < 0.04 and controlMode == 0:
            rotation_control = 0;
            distance_control = - distance_error * kpd;
        if rotation_control > 25:
            rotation_control = 25
        if rotation_control < -25:
            rotation_control = -25
        if distance_control > 50:
            distance_control = 50
        if distance_control < -50:
            distance_control = -50
        if controlMode == 1:
            distance_control = 0
        # distance_control = 0
        wl_output = -1 * int(distance_control - rotation_control)
        wr_output = -1 * int(distance_control + rotation_control)
        self.last_angle_error = angle_error
        '''
        if wl_output <5 and wl_output >-5:
            wl_output = 0
        if wr_output <5 and wr_output >-5:
            wr_output = 0
        '''
        # print ('distance_error'+ str(distance_error))
        # print ('angle_error'+ str(angle_error))
        # print ('distance_control'+ str(distance_control))
        # print ('rotation_control'+ str(rotation_control))
        # wl_output = 0
        # wr_output = 0

        return wl_output, wr_output

    def two2one(self, x, y):
        if x < -0.28:
            zx = 0
        if x >= -0.28 and x < 0.28:
            zx = 1
        if x >= 0.28:
            zx = 2
        if y < -0.28:
            zy = 0
        if y >= -0.28 and y < 0.28:
            zy = 1
        if y >= 0.28:
            zy = 2
        z = zx + zy * 3
        return z

    def one2two(self, z):
        x = z % 3 * 0.55 - 0.55
        y = z // 3 * 0.53 - 0.53
        point = [x, y]
        return point

    def planning(self, nowTime, Target):
        Target = np.array(Target)
        print(Target)
        print(self.lastTarget)

        if (Target != self.lastTarget).any():
            self.planningPos = self.estimatePose[0:2].reshape(-1)
            start = self.two2one(self.estimatePose[0], self.estimatePose[1])
            end = self.two2one(Target[0], Target[1])
            if start != end:
                self.planstep[0] = 1
                self.planstep[1] = 0

                self.avoidanceTraj = self.avoidancePlan.AstarPlan(start, end)
                self.avoidTarget = self.one2two(self.avoidanceTraj[1])
                self.planningTarget = (self.avoidTarget - self.planningPos) * 0.1 + self.planningPos
                distance = np.sqrt((self.avoidTarget[1] - self.estimatePose[1]) ** 2 + (
                            self.avoidTarget[0] - self.estimatePose[0]) ** 2)
                self.TrajectoryTime = distance / 0.21
                self.avoidNum = 1

        if self.planstep[0] == 1:
            angle_target = np.arctan2(self.planningTarget[1] - self.estimatePose[1],
                                      self.planningTarget[0] - self.estimatePose[0])
            angle_error = (angle_target - self.estimatePose[2])
            angle_error = self.piRound(angle_error)
            controlMode = 1
            if np.abs(angle_error) > 0.8:
                self.planningTarget = (self.avoidTarget - self.planningPos) * 0.1 + self.planningPos
            if np.abs(angle_error) <= 0.8:
                self.planstep[0] = 0
                self.planstep[1] = 1
                self.planningTime = nowTime
                self.planningTarget = (self.avoidTarget - self.planningPos) * 0.1 + self.planningPos

        print('self.TrajectoryTime:', self.TrajectoryTime)
        if self.planstep[1] == 1:
            controlMode = 0
            if (nowTime - self.planningTime) < self.TrajectoryTime:
                print('avoidTarget:', self.avoidTarget)
                print('planningPos:', self.planningPos)
                print('self.planningTime:', self.planningTime)
                print('self.TrajectoryTime:', self.TrajectoryTime)
                print('nowT:', nowTime)
                self.planningTarget = (self.avoidTarget - self.planningPos) * (
                            nowTime - self.planningTime) / self.TrajectoryTime + self.planningPos

            elif self.avoidNum < len(self.avoidanceTraj) - 1:
                self.avoidNum += 1
                self.planningPos = np.array(self.avoidTarget)
                self.planningTarget = self.avoidTarget
                self.avoidTarget = self.one2two(self.avoidanceTraj[self.avoidNum])
                self.planningTime = nowTime
                distance = np.sqrt((self.avoidTarget[1] - self.estimatePose[1]) ** 2 + (
                            self.avoidTarget[0] - self.estimatePose[0]) ** 2)
                self.TrajectoryTime = distance / 0.21

            if self.avoidNum > len(self.avoidanceTraj):
                self.planningTarget = Target

        self.lastTarget = Target
        self.planningTarget = list(self.planningTarget)
        return self.planningTarget, controlMode
