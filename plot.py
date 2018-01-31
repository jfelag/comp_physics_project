import numpy as np
import matplotlib.pyplot as plt

'''

PLOT DATA FROM SAVED RUNS

'''

gens = []

with open('bestGen.txt','r') as f:
	for line in f:
		li = line.split(' ')[0:-1]
		li = [float(x) for x in li]
		li2 = np.array(li)
		gens.append( li2 )
		
total = np.zeros_like(gens[0])

sterr = np.zeros_like(gens[0])
temp = []

for i in gens:
	total = total + i
	
for j in range(len(gens[0])):
	temp = [gens[k][j] for k in range(len(gens))]
	sterr[j] = np.std(temp)
	
avg = total/len(gens)

plt.figure()
#plt.plot(avg-sterr, 'b-')
plt.plot(avg, 'b-', label='Average of Generations')
plt.title('Best Fitness over Generations for %d Runs'%len(gens))
plt.xlabel('Generation #')
plt.ylabel('Fitness')
#plt.plot(avg+sterr, 'b-')
plt.fill_between(range(len(sterr)), avg-sterr, avg+sterr, color='b', alpha=0.3, label='StdErr')
plt.legend(loc=2)
plt.show()


