import numpy as np
import matplotlib.pyplot as plt
import pygame
import time
from rotor import ROTOR
from simulator import SIMULATOR
import multiprocessing as mp

'''CONSTANTS'''

NUM_PARTICLES = 1000      #number of air particles
TIME_STEPS = 10000          #time steps
AIR_MASS = 0.000003       #air mass (arbitrary)
SIZE = 200                #pygame window size (width and height)
AIR_R = 2                 #particle radius
AIR_V = 3.0               #default air speed
DT = 0.01                 #time step
TAU = 1.5                 #constant for decay of turbine speed

BREAK = NUM_PARTICLES/5   #number of partices evaluated on each core (multiprocessing)

'''OUTSIDE FUNCTIONS'''

############################################
###Checks if two line segments intersect
###Credit to http://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/

def ccw(a1, a2, b1, b2, c1, c2):
	
	return (c2-a2)*(b1-a1) > (b2-a2)*(c1-a1)

def intersect(a1, a2, b1, b2, c1, c2, d1, d2):
	
	return ccw(a1,a2,c1,c2,d1,d2) != ccw(b1,b2,c1,c2,d1,d2) and ccw(a1,a2,b1,b2,c1,c2) != ccw(a1,a2,b1,b2,d1,d2)

############################################



class TURBINE:

	def __init__(self, ID, pygame=True):
		'''Initializes turbine obect'''
		
		#evaluate with graphics or not
		self.pg = pygame
		
		#id to track lineage
		self.ID = ID
		
		#age (for AFPO)
		self.age = 0
		
		#fitness value
		self.fitness = 0.0
		
		#initialize random variables for rotor
		self.x2 = np.random.randint(10,100)
		self.y2 = np.random.randint(10,100)
		self.rx = np.random.random() + 1
		self.ry = np.random.random()
		self.n = np.random.randint(2,4)
		
		#assume non dominated (for AFPO)
		self.non_dominated = True
		
		#stores line positions
		self.lines = []
		#stores vectors for calculations
		self.line_vec = []
		
		#current rotational speed
		self.ang = 0
		
		#global counter for speed
		self.t = 0
		
		#keeps track of rotational speed over time
		self.speed = np.zeros(TIME_STEPS)
		
		#create rotor instance
		self.rotor = ROTOR(self.x2, self.y2, self.rx, self.ry, self.n)
		

	def mutate(self):
		'''Mutates the turbine'''
		
		#choose value to change
		r = np.random.randint(0,9)

		# p = 1/9 to change n
		# p = 2/9 to change other values
		
		#change chosen value slightly
		if r == 0:
			self.n += np.random.choice( [-1, 1] )
		elif r == 1 or r == 2:
			self.x2 += np.random.choice( [-2, -1, 1, 2] )
		elif r == 3 or r == 4:
			self.y2 += np.random.choice( [-2, -1, 1, 2] )
		elif r == 5 or r == 6:
			self.rx = np.random.normal(self.rx, self.rx/2.)
		elif r == 7 or r == 8:
			self.ry = np.random.normal(self.ry, self.ry/2.)

		# force values to fit within boundaries

		if self.n < 2:
			self.n = 2
		elif self.n > 3:
			self.n = 3

		if self.x2 < 10:
			self.x2 = 10
		elif self.x2 > 100:
			self.x2 = 100

		if self.y2 < 10:
			self.y2 = 10
		elif self.y2 > 100:
			self.y2 = 100

		if self.rx < 1.0:
			self.rx = 1.0
		elif self.rx > 2.0:
			self.rx = 2.0

		if self.ry < 0.0:
			self.ry = 0.0
		elif self.ry > 1.0:
			self.ry = 1.0
			
		self.rotor = ROTOR(self.x2, self.y2, self.rx, self.ry, self.n)
			
	
	def evaluate(self):
		'''Simulates turbine to get fitness'''
		
		#reset params (in case it is not the first evaluation)
		self.non_dominated = True
		
		#stores line positions
		self.lines = []
		
		self.ang = 0
		
		self.t = 0
		
		self.speed = np.zeros(TIME_STEPS)
		
		self.initialize()
		
		if self.pg:
			self.sim.wipe()
		                
		#main loop
		for _ in range(TIME_STEPS):
			
			if self.pg:
				self.check_exit()
			
			if self.pg:
				self.sim.wipe()

				self.sim.draw_circle(200,200,5, 'black')
				
			
			self.rotate_blades()
			
			self.draw_blades()
			
			#collisions
			output = mp.Queue()
			
			#list of end particle number for each task
			part = [BREAK*r for r in range(1,6)]
			
			processes = [mp.Process(target=self.update_wind, args=(x,output)) for x in part]
			
			for p in processes:
				p.start()

			# Exit the completed processes
			for p in processes:
				p.join()
				
			results = [output.get() for p in processes]
			
			#update from results
			#need to do this because multiprocessing spawns separate processes for each task
			for r in results:
				self.ang += r['a']
				s = r['s'][0]
				self.air_px[s-BREAK:s] = r['s'][1]
				self.air_py[s-BREAK:s] = r['s'][2]
				self.air_vx[s-BREAK:s] = r['v'][0]
				self.air_vy[s-BREAK:s] = r['v'][1]
				if self.pg:
					for x,y in zip(self.air_px[s-BREAK:s], self.air_py[s-BREAK:s]):
						self.sim.draw_circle(int(x), int(y), AIR_R)
			
			#periodic boundaries for wind
			self.boundaries()
			
			if self.pg:
				self.sim.refresh()
		
		#fitness = sum of rotated angles normalized for actual rotations
		self.fitness = np.sum(np.abs(self.speed))/(2*np.pi)
		
		if self.pg:
			self.sim.quit()
		
		
	def initialize(self):
		
		if self.pg:
			self.sim = SIMULATOR()
		
		self.rotor = ROTOR(self.x2, self.y2, self.rx, self.ry, self.n)
		
		self.center = SIZE
		
		lim = len(self.rotor.TSPACE)

		self.segments = np.linspace(0,lim,10)
		
		#holds current blade positions
		self.currBladesx = []
		self.currBladesy = []
		
		self.line_vec = []
		
		for b in range(self.rotor.n):
	
			blade = []
			#vec_i = []
			tempx = []
			tempy = []
			
			x1 = self.center
			y1 = self.center
			
			for i in range(len(self.segments)-1):
				
				j = int(self.segments[i])

				x2 = self.rotor.bladesx[b][j+1] + self.center
				y2 = self.rotor.bladesy[b][j+1] + self.center

				#vec = (x2-x1, y2-y1)

				#vec_i.append(vec)

				#print '(%f,%f) (%f,%f)'%(x1, y1, x2, y2)
				if self.pg:
					self.sim.draw_line(x1,y1,x2,y2)
				
				tempx.append(x1-self.center)
				tempx.append(x2-self.center)
				tempy.append(y1-self.center)
				tempy.append(y2-self.center)
				
				x1 = x2
				y1 = y2
			
			self.currBladesx.append(tempx)
			self.currBladesy.append(tempy)
			#self.line_vec.append(vec_i)
				
		self.air_px = np.zeros(NUM_PARTICLES)
		self.air_py = np.zeros(NUM_PARTICLES)
		self.air_vx = np.zeros(NUM_PARTICLES)
		self.air_vy = np.zeros(NUM_PARTICLES)
		
		for i in range(NUM_PARTICLES):
			
			x = np.random.randint(0,self.center*2)
			y = np.random.randint(0,self.center*2)
			
			self.air_px[i] = x
			self.air_py[i] = y
			self.air_vx[i] = AIR_V
			self.air_vy[i] = 0
			
			
			
			
	
	def boundaries(self):
		
		for k in range(NUM_PARTICLES):
				
				if np.abs(self.air_px[k]) > self.center*2 or np.abs(self.air_py[k]) > self.center*2:
					
					y = np.random.randint(0,self.center*2)
			
					self.air_px[k] = 0
					self.air_py[k] = y
					self.air_vx[k] = AIR_V
					self.air_vy[k] = 0
	
	def check_exit(self):
		for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.sim.quit()
					
	
	def update_wind(self, s, ret):
		
		rd = {}
		partx = np.zeros(BREAK)
		party = np.zeros(BREAK)
		partvx = np.zeros(BREAK)
		partvy = np.zeros(BREAK)
		turn = 0
		
		for q in range(s-BREAK,s):
			
			collide = False
			
			x1 = self.air_px[q]
			y1 = self.air_py[q]
			
			vx = self.air_vx[q]
			vy = self.air_vy[q]
			
			x2 = x1 + vx
			y2 = y1 + vy

			for line in self.lines:
				for seg in line:

					x3 = seg[0]
					y3 = seg[1]
					x4 = seg[2]
					y4 = seg[3]
					
					#draw lines for particle movement
					#self.sim.draw_line(x1,y1,x2,y2, (0,100,255),1)
					
					if intersect(x1, y1, x2, y2, x3, y3, x4, y4):
						
						collide = True
						
						#collision
						dist = np.sqrt( (x1-self.center)**2 + (y1-self.center)**2)     #distance from center of turbine
						F = AIR_MASS * np.sqrt( vx**2 + vy**2)                     #more like momentum
						
						vec_l = np.array([x4-x3, y4-y3])         #vector for blade segment
						vec_a = np.array([x2-x1, y2-y1])         #vector for particle movement
						
						norm = np.array([-vec_l[1], vec_l[0]])
						norm = norm/np.linalg.norm(norm)
						
						refl = vec_a - (2 * norm * np.dot(vec_a,norm))
						
						v1_u = vec_a/np.linalg.norm(vec_a)
						v2_u = vec_l/np.linalg.norm(vec_l)
						theta = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
						
						#get reflect as new velocity
						partvx[q%BREAK] = refl[0]
						partvy[q%BREAK] = refl[1]
						
						#print q%BREAK, refl[0], refl[1]
						
						#keep initial position
						partx[q%BREAK] = x1
						party[q%BREAK] = y1
						
						torq = dist*F*np.sin(theta)
						if y1 < self.center:
							torq *= -1
							
						#increment turning angle
						turn += torq
						
						#draw bright line over segment if collision
						#for debugging
						#self.sim.draw_line(x3,y3,x4,y4, (255,100,255))
						
						break
						
					else:
						#no collision
						
						#keep new position
						partx[q%BREAK] = x2
						party[q%BREAK] = y2
						#keep same velocity
						partvx[q%BREAK] = vx
						partvy[q%BREAK] = vy
				if collide:
					break
						
						
		
		rd['s'] = (s, partx, party)
		rd['v'] = (partvx, partvy)
		rd['a'] = turn
		ret.put(rd)
			
	
	def draw_blades(self):
		
		self.lines = []
		
		for b in range(self.rotor.n):
			x1 = self.center
			y1 = self.center
			blade = []
			vec_i = []
			for i in range(0,18,2):
				
				x2 = self.pBlade[b][0][i+1] + self.center
				y2 = self.pBlade[b][1][i+1] + self.center
				
				if self.pg:
					L = self.sim.draw_line(x1,y1,x2,y2)
				
				blade.append((x1,y1,x2,y2))
				x1 = x2
				y1 = y2
			
			self.lines.append(blade)
			
			
	
	def rotate_blades(self):
		import pprint 
		
		#self.ang = 0
		
		R = np.array([[np.cos(self.ang), -np.sin(self.ang)], [np.sin(self.ang), np.cos(self.ang)]])
		self.pBlade = np.zeros((self.n,2,18))
		
		for i in range(len(self.currBladesx)):

			temp = np.array([self.currBladesx[i], self.currBladesy[i]])
			temp = np.dot(temp.T,R).T
			

			self.currBladesx[i] = temp[0]
			self.currBladesy[i] = temp[1]

			
			self.pBlade[i][0] = self.currBladesx[i]
			self.pBlade[i][1] = self.currBladesy[i]
			
		self.ang *= (1-DT/TAU)
		self.speed[self.t] = self.ang
		self.t += 1




