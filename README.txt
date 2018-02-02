Final project for PHYS 256: Computational Physics.

This will evolve a vertical-axis wind turbine to be efficient in a particle-based simulation.

Full write up in phys256-report.pdf


MODULES USED:

Matplotlib
Numpy
Pygame

FILES:

afpo.py        -- runs evolution, requires sys argument for seed: "python afpo.py <seed>"
playbest.py    -- plays the best evolved turbine
playone.py     -- plays a randomly generated turbine
plot.py        -- plots improvement over evolutionary time
population.py  -- holds functions for AFPO
rotor.py       -- generates blades for turbine
simulator.py   -- holds functions for drawing the simulation in pygame
turbine2.py    -- holds turbine and evaluation functions

best.p         -- holds best turbine, load using pickle (std lib)
bestGen.txt    -- holds data: best per generation, per run



