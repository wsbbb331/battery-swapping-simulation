import numpy as np
import pandas as pd
from scipy import stats, integrate
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import DateFormatter, HourLocator, MinuteLocator, AutoDateLocator
import seaborn as sns
import csv
import sys
from datetime import datetime,date,timedelta
import random
from math import ceil
import math

sns.set_context("paper")
sns.set(font_scale=2)
sns.set_style("whitegrid", {
        "font.family": "serif",
        "font.serif": ["Times", "Palatino", "serif"],
        'grid.color': '.9',
        'grid.linestyle': '--',
})

busChargerIncomeDataFrame = pd.read_pickle("busChargerIncomeDataFrame0.pkl")
busSwappingIncomeDataFrame = pd.read_pickle("busSwappingIncomeDataFrame0.pkl")
busDCChargerIncomeDataFrame = pd.read_pickle("busDCChargerIncomeDataFrame0.pkl")
busSwapperIncomeDataFrame = pd.read_pickle("busSwapperIncomeDataFrame0.pkl")

for iteration in range(1,30):
        busChargerIncomeDataFrame = pd.concat((busChargerIncomeDataFrame,pd.read_pickle("busChargerIncomeDataFrame"+str(iteration) + ".pkl")))
        busSwappingIncomeDataFrame = pd.concat((busSwappingIncomeDataFrame, pd.read_pickle("busSwappingIncomeDataFrame"+str(iteration) + ".pkl")))
        busDCChargerIncomeDataFrame = pd.concat((busDCChargerIncomeDataFrame, pd.read_pickle("busDCChargerIncomeDataFrame"+str(iteration) + ".pkl")))
        busSwapperIncomeDataFrame = pd.concat((busSwapperIncomeDataFrame, pd.read_pickle("busSwapperIncomeDataFrame"+str(iteration) + ".pkl")))
# for iteration in range(30):
#         busChargerIncomeDataFrame = pd.concat((busChargerIncomeDataFrame,pd.read_pickle("9-11/busChargerIncomeDataFrame"+str(iteration) + ".pkl")))
#         busSwappingIncomeDataFrame = pd.concat((busSwappingIncomeDataFrame, pd.read_pickle("9-11/busSwappingIncomeDataFrame"+str(iteration) + ".pkl")))
#         busDCChargerIncomeDataFrame = pd.concat((busDCChargerIncomeDataFrame, pd.read_pickle("9-11/busDCChargerIncomeDataFrame"+str(iteration) + ".pkl")))
#         busSwapperIncomeDataFrame = pd.concat((busSwapperIncomeDataFrame, pd.read_pickle("9-11/busSwapperIncomeDataFrame"+str(iteration) + ".pkl")))



busChargerIncomeDataFrame = busChargerIncomeDataFrame.groupby(busChargerIncomeDataFrame.index).mean()
busSwappingIncomeDataFrame = busSwappingIncomeDataFrame.groupby(busSwappingIncomeDataFrame.index).mean()
busDCChargerIncomeDataFrame = busDCChargerIncomeDataFrame.groupby(busDCChargerIncomeDataFrame.index).mean()
busSwapperIncomeDataFrame = busSwapperIncomeDataFrame.groupby(busSwapperIncomeDataFrame.index).mean()

plt.figure()
ax = plt.subplot(1,1,1)
busChargerIncomeDataFrame.plot(x="number",y="income",label="Charging", ax=ax,style="r-o",lw=3)
# busSwappingIncomeDataFrame.plot(x="number",y="income",label="Swapping", ax=ax,style="b-.o",lw=3)

ax.set(ylabel= "Saturation Number", xlabel='Battery Capacity (kWh)')
ax.legend(numpoints=1)

plt.tight_layout()
plt.savefig('battery_capacity_bus.pdf')

print(busDCChargerIncomeDataFrame)
print(busSwapperIncomeDataFrame)