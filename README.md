# battery-swapping-simulation

This is the simulation source files to implement the simulation published in [A Monte Carlo Simulation Approach to Evaluate Service Capacities of EV Charging and Battery Swapping Stations](https://ieeexplore.ieee.org/document/8265183/). 

The repository contains the following files

1, **simulationClasses**: The classes for taxis and buses to keep track of the status of each bus and taxi. The mathematical model of each vehicle and EVSE is discussed in the paper.

2, **dailyRunningSimulation**: The file to simulate day to day operation and see the daily status statistics

3, **bus_saturation**: The simulation can be scaled up to 6 months length to investigate the impact of different parameters on the outcome of the simulated income. This folder contains example code to investigate the parameters in buses. For each parameters, 30 parallel Monte-Carlo simulations are implemented to avoid the random effects of each single random process. "timeToSaturation.py" should be run to generate .pkl files to provide data to plot.

By Tianyang Zhang and Xi Chen, [Global Energy Interconnection Research Institute North America (GEIRINA)](geirina.net),  2017-2018