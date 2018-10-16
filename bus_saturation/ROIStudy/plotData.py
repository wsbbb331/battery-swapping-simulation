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

busChargerIncomeDataFrame = pd.read_pickle("busChargerIncomeDataFrame.pkl")
busSwappingIncomeDataFrame = pd.read_pickle("busSwappingIncomeDataFrame.pkl")
busDCChargerIncomeDataFrame = pd.read_pickle("busDCChargerIncomeDataFrame.pkl")
busSwapperIncomeDataFrame = pd.read_pickle("busSwapperIncomeDataFrame.pkl")
busSwapperBatteryDataFrame = pd.read_pickle("busSwapperBatteryDataFrame.pkl")
busSwapperBatterySwapNoDataFrame = pd.read_pickle("busSwapperBatterySwapNoDataFrame.pkl")
busDCChargeNumberDataFrame = pd.read_pickle("busDCChargeNumberDataFrame.pkl")

sns.set_context("paper")
sns.set(font_scale=1.5)
sns.set_style("whitegrid", {
        "font.family": "serif",
        "font.serif": ["Times", "Palatino", "serif"],
        'grid.color': '.9',
        'grid.linestyle': '--',
})

plt.figure(figsize=(9, 20), dpi=1600)
ax = plt.subplot(4,1,1)
ax2 = plt.subplot(4,1,2)
ax3 = plt.subplot(4,1,3)
ax4 = plt.subplot(4,1,4)
ax5 = ax4.twinx()
busChargerIncomeDataFrame.iloc[:]["income"] -= busDCChargeNumberDataFrame.iloc[:]["number of charge"]*6*324*227/250
busChargerIncomeDataFrame.plot(x="number",y="income",label="Bus w/ Charging", ax=ax)
busSwappingIncomeDataFrame.plot(x="number",y="income",label="Bus w/ Swapping", ax=ax)

busDCChargerIncomeDataFrame.plot(x="number",y="income",label="Bus Charger", ax=ax2)
busSwapperIncomeDataFrame.iloc[:]["income"] -= busSwapperBatterySwapNoDataFrame.iloc[:]["number of swap"]*6*324*227/550
busSwapperIncomeDataFrame.plot(x="number",y="income",label="Bus Swapper", ax=ax2)

busSwapperBatteryDataFrame.plot(x="number",y="number of battery", ax=ax3)
print(busSwapperBatteryDataFrame)
busDCChargeNumberDataFrame.plot(x="number",y="number of charge", ax=ax4)
busSwapperBatterySwapNoDataFrame.plot(x="number",y="number of swap", ax=ax4)
busDCChargeNumberDataFrame.plot(x="number",y="remainingkWh", label="remaining kWh when charge", ax=ax5, style="r")

ax.set(ylabel= "Income of Bus Company", xlabel='Number of Buses')
ax2.set(ylabel= "Income of Charging Company", xlabel='Number of Buses')
ax3.set(ylabel= "Number of Battery", xlabel='Number of Buses')
ax4.set(ylabel= "Number of Cycle", xlabel='Number of Buses')
ax5.set(ylabel= "Remaining kWh", xlabel='Number of Buses')
ax5.grid(None)

plt.tight_layout()
plt.savefig('optimalNumberStudy_bus.pdf')

print(busChargerIncomeDataFrame)
