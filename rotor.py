import numpy as np
import matplotlib.pyplot as plt
import pygame
import time

dt = 0.05

# calculates a bezier curve that represents the blade
class ROTOR:
    
    def __init__(self, x2, y2, rx, ry, n):
        
        #define points
        self.x1 = 0
        self.y1 = 0
        self.x2 = x2
        self.y2 = y2
        self.x3 = x2 * rx
        self.y3 = y2 * ry         
        
        #define number of blades
        self.n = n
        
        #time parameters
        self.TSPACE = np.arange(0,1+dt,dt)
        
        #curve values
        self.Bx = np.ones_like(self.TSPACE)
        self.By = np.ones_like(self.TSPACE)
        
        #angle of blades
        theta = np.radians(360./n)
        
        #rotation matrix
        self.R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        
        self.make_blade()
        self.make_fan()
        
    def make_blade(self):
        
        x1 = self.x1
        y1 = self.y1
        x2 = self.x2
        y2 = self.y2
        x3 = self.x3
        y3 = self.y3
        
        for i in range(len(self.TSPACE)):
            t = self.TSPACE[i]
            self.Bx[i] = ((1 - t)**2 * x1) + (2*t*x2*(1 - t)) + (t**2 * x3)
            self.By[i] = ((1 - t)**2 * y1) + (2*t*y2*(1 - t)) + (t**2 * y3)
    
    def make_fan(self):
        
        self.bladesx = [0] * self.n
        self.bladesy = [0] * self.n
    
        self.bladesx[0] = self.Bx
        self.bladesy[0] = self.By
        
        for i in range(1, self.n):
            pBlade = np.array([self.bladesx[i-1],self.bladesy[i-1]])
            #transpose before dot to match dimensions
            #transpose after to match x,y
            nBlade = np.dot(pBlade.T,self.R).T
            self.bladesx[i] = nBlade[0]
            self.bladesy[i] = nBlade[1]
            
        
            
        
    def plot_blades(self):

        plt.figure()
        ax = plt.axes(aspect='equal')
        
        lim = max([self.x2,self.x3, self.y2,self.y3])
        
        ax.set_xlim((-lim-10, lim+10))
        ax.set_ylim((-lim-10, lim+10))
        
        for i in range(self.n):
            
            ax.plot(self.bladesx[i],self.bladesy[i], 'k')
            
        ax.plot(self.x1,self.y1, 'g*', markersize= 15, label = 'ref 1')
        ax.plot(self.x2,self.y2, 'r*', markersize= 15, label = 'ref 2')
        ax.plot(self.x3,self.y3, 'b*', markersize= 15, label = 'ref 3')
        ax.legend()
        
        plt.show()
        
        