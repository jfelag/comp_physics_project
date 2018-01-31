import numpy as np
import matplotlib.pyplot as plt
import pygame
import time

class SIMULATOR:
    
    def __init__(self):
        
        pygame.init()
        
        self.size = 400, 400
        
        self.screen = pygame.display.set_mode(self.size)
        
        self.lines = []
        
        self.circs = []
        
    def refresh(self):
        
        pygame.display.flip()
        
    def wipe(self):
        
        self.screen.fill((255,255,255))
        
    def draw_line(self, x1, y1, x2, y2, color=(0,0,0), w=3):

        line = pygame.draw.line(self.screen, color, (x1,y1), (x2,y2), w)
        
        return line
        
    def draw_circle(self, x, y, r, color='blue',):
        
        if color == 'black':
            c = (0,0,0)
        else:
            c = (0,100,150)
        circ = pygame.draw.circle(self.screen, c , (x,y), r)
        
        return circ
        
    def quit(self):

        #quits out of pygame and window
        pygame.quit()

        
        
        
        
        
        
        