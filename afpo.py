import numpy as np
import matplotlib.pyplot as plt
import pygame
import time
from turbine2 import TURBINE
from population import POPULATION
import random
import copy
import pickle
import sys

random.seed(sys.argv[1])

g = 100

# a = TURBINE(1, pygame=True)
# a.evaluate()

#INITIALIZE PARENT POPULATION
parents = POPULATION()
parents.Initialize()
#EVALUATE
parents.Evaluate()
parents.Print()

top = ''

for i in range(1,g+1):
	#CREATE CHILD POPULATION
	children = POPULATION()
	#COPY OVER NON-DOMINATED PARENTS
	parents.Delete_Dominated(children)
	#INCREASE AGE BY 1
	children.Inc_Age()
	#FILL REST OF POPULATION WITH MUTANTS OF CHILDREN
	children.Fill_Mutants()
	#ADD A RANOM TURBINE INTO THE POPULATION
	children.Inject_Random()
	#EVAULATE NEW CHILDREN
	children.Evaluate()
	print i
	children.Print()
	
	#GET BEST CHILD
	best = children.p[0]
	for i in range(1,len(children.p)-1):
		if children.p[i].fitness > best.fitness:
			best = children.p[i]
			
	top += str(best.fitness) + ' '
	
	#COPY CHILDREN OVER TO BE NEW PARENTS
	del parents
	parents = POPULATION()
	children.Copy_Population(parents)
	del children

best = parents.p[0]

#GET BEST OF RUN
for i in range(1,len(parents.p)-1):
	if parents.p[i].fitness > best.fitness:
		best = parents.p[i]

#compare best fitness
f = open('best.p','r')
oldBest = pickle.load(f)
f.close()

#SAVE BEST
if best.fitness > oldBest.fitness:
	g = open('best.p','w')
	pickle.dump(best, g)
	g.close()

#SAVE BEST IN GENERATION DATA
with open('bestGen.txt','a') as f:
	f.write(top + '\n')

print 'saved successfully'

