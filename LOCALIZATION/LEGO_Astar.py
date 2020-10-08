# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 19:50:13 2019

@author: ydc
"""
import numpy as np
class LEGO_Astar():

    row_num = 3#行
    column_num = 3#列
    
    def __init__(self):
        pass
    
    def pointX(self,point):
        pointX = point%self.column_num
        return pointX
    
    def pointY(self,point):
        pointY = point//self.row_num
        return pointY
        
    def point2to1(self,x,y):
        point = x+y*self.row_num 
        return point
    
    def distance_to_end(self,x,y):
        distance = np.abs(self.pointX(x)-self.pointX(y))+np.abs(self.pointY(x)-self.pointY(y))
        return distance
    
    def AstarPlan(self,AllStart,end):
        
    
        direction = [[-1,0],[0,1],[0,-1],[1,0]]
        space = np.array([0,0,0,
                          10,0,10,
                          0,0,0])
        point_list = 999*np.ones([self.row_num*self.column_num,5])
        point_list[:,0] = np.arange(0,9)
        start = AllStart
        open_list = np.array([[start,0]])
        close_list = np.array([])
        end_num = 0
        
        point_list[start,:] = [start,start,0,self.distance_to_end(start,end),0]
        #self_num,parent,G,H,F
        point_list[start,4] = point_list[start,2]+point_list[start,3]
        while end_num == 0:
            for i in direction:
                if self.pointX(start)+i[0]>=0 and self.pointX(start)+i[0]<=2 and self.pointY(start)+i[1]>=0 and self.pointY(start)+i[1]<=2:
                    son = int(self.point2to1(self.pointX(start)+i[0],self.pointY(start)+i[1]))
                    if (son not in close_list) or (point_list[start,2]+1 < point_list[son,2]):
                        point_list[son,1] = start
                        point_list[son,2] = point_list[start,2]+1
                        point_list[son,3] = self.distance_to_end(son,end)+space[son]
                        point_list[son,4] = point_list[son,2]+point_list[son,3]
                        open_list = np.append(open_list,[[son,point_list[son,4]]],axis=0)
                    if son == end:
                        end_num = 1
                    
            open_list = np.delete(open_list, 0, axis=0)
            close_list = np.append(close_list,[start],axis=0)
            open_list = open_list[open_list[:,1].argsort()] 
            start = int(open_list[0,0])
        trajectory = [end]
        now_point = end
        while trajectory[-1] != AllStart:
            trajectory.append(point_list[int(trajectory[-1]),1])
        trajectory.reverse()
        print('Trajectory:',trajectory)
        return trajectory
    

