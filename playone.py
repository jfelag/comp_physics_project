from turbine2 import TURBINE
import matplotlib.pyplot as plt

'''

PLAYS A RANDOM TURBINE

'''


t = TURBINE(1, pygame=True)
t.evaluate()

plt.figure()
plt.plot(t.speed)
plt.show()

print t.fitness