import pickle
import matplotlib.pyplot as plt
import numpy as np

'''

PLAY BEST SAVED TURBINE

'''

f = open('best.p','r')
best = pickle.load(f)
f.close()

best.pg = True
best.evaluate()

'''
#show blade representation
best.rotor.plot_blades()

plt.figure()
plt.title('Speed over Time for Best Turbine')
plt.xlabel('Time')
plt.ylabel(r'Rotational Speed $\theta / \Delta t$')
plt.plot((-1)*best.speed*180/np.pi)
plt.show()
'''