from turbine2 import TURBINE
import copy
import random
import pickle


vis = False
POP = 10

class POPULATION:

	def __init__( self ):
		
		self.pop = POP
		self.p = {}
		self.globalID = 0

	def Print( self ):
		
		for i in self.p:
			print '%0.4f'%self.p[i].fitness,
		print ''

	def Evaluate( self ):

		for i in self.p:
			if self.p[i].fitness == 0:
				self.p[i].evaluate()

	def ReplaceWith(self, other):

		for i in self.p:
			if (self.p[i].fitness <= other.p[i].fitness):
				self.p[i] = other.p[i]

	def Initialize(self):

		for i in xrange(0, self.pop):
			self.p[i] = TURBINE(1, pygame=vis)
			self.globalID = self.globalID + 1

	def Delete_Dominated(self, o):
		self.c = 0
		for i in xrange(0,self.pop):
			self.p[i].non_dominated = True

		for i in self.p:	
			for j in self.p:
				if i != j:
					if self.p[j].age <= self.p[i].age and self.p[j].fitness > self.p[i].fitness:
						self.p[i].non_dominated = False
					elif self.p[j].age == self.p[i].age and self.p[j].fitness == self.p[i].fitness and self.p[j].ID > self.p[i].ID:
						self.p[i].non_dominated = False
					elif self.p[j].age < self.p[i].age and self.p[j].fitness == self.p[i].fitness:
						self.p[i].non_dominated = False

			if self.p[i].non_dominated: #keep the individual and copy over
				o.p[self.c] = copy.deepcopy(self.p[i])
				self.c += 1
		o.c = self.c


	def Inc_Age(self):
		for i in self.p:
			self.p[i].age += 1

	def Fill_Mutants(self):
		c = len(self.p)
		num_mutants = self.pop-c
		counter = 0
		if num_mutants > 0:
			to_mutate = [random.choice(xrange(c)) for i in xrange(num_mutants)]
			for i in to_mutate:
				self.p[counter+c] = copy.deepcopy(self.p[i])
				self.p[counter+c].mutate()
				self.p[counter+c].ID = self.globalID
				self.globalID += 1
				counter += 1
		else:
			self.p[c] = copy.deepcopy(self.p[random.randint(0,c-1)])
			self.p[c].mutate()
			self.p[c].ID = self.globalID
			self.globalID += 1


	def Inject_Random(self):
		self.p[-1] = TURBINE( self.globalID, False)


	def Copy_Population(self, o):
		for i in self.p:
			o.p[i] = copy.deepcopy(self.p[i])
