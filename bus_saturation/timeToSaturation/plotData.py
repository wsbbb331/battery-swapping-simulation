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


busChargerIncomeDataFrame = pd.read_pickle("busChargerIncomeDataFrame.pkl")
busSwappingIncomeDataFrame = pd.read_pickle("busSwappingIncomeDataFrame.pkl")
busDCChargerIncomeDataFrame = pd.read_pickle("busDCChargerIncomeDataFrame.pkl")
busSwapperIncomeDataFrame = pd.read_pickle("busSwapperIncomeDataFrame.pkl")

busUpperLimitCharge = pd.read_csv("BusUpperLimitCharge.csv",names=["number","income"])
busLowerLimitCharge = pd.read_csv("BusLowerLimitCharge.csv",names=["number","income"])

plt.figure(figsize=(9, 8), dpi=1600)
ax = plt.subplot(2,1,1)
ax2 = plt.subplot(2,1,2)
busChargerIncomeDataFrame.plot(x="number",y="income",label="Charging", ax=ax,style="r-",lw=3)
# busSwappingIncomeDataFrame.plot(x="number",y="income",label="Swapping", ax=ax,style="b-.",lw=3)

computedIncome = busSwapperIncomeDataFrame["income"]
fixedCost = (9-1) * 5000 + 2.5*(10**6)
monthlyIncome = (computedIncome + fixedCost )*(1-0.023)/1 - 36245*0.023
busSwapperIncomeDataFrame["income"] = monthlyIncome - fixedCost
fixedChargerCost = 210*15000
monthlyIncome_charger = (busDCChargerIncomeDataFrame["income"] + fixedChargerCost)*(0.6-0.023)/0.6 - 0.13*210*24*30*0.023
busDCChargerIncomeDataFrame["income"] = monthlyIncome_charger - fixedChargerCost

busDCChargerIncomeDataFrame.plot(x="number",y="income",label="Charging", ax=ax2,style="r-",lw=3)
# busSwapperIncomeDataFrame.plot(x="number",y="income",label="Swapping", ax=ax2,style="b-.",lw=3)
ax.set(ylabel= "Income ($)", xlabel='Number of Vehicles')
ax2.set(ylabel= "Income ($)", xlabel='Number of Vehicles')

plt.tight_layout()
plt.savefig('optimalNumberStudy_bus.pdf')

plt.figure(figsize=(9, 4), dpi=1600)
ax = plt.subplot(1,1,1)
busChargerIncomeDataFrame[busChargerIncomeDataFrame["number"]<511].plot(x="number",y="income",label="Charging", ax=ax,style="r-o",lw=3)
busUpperLimitCharge[busUpperLimitCharge["number"]<511].plot(x="number",y="income",label="Upper Limit",ax=ax,style="b--",lw=3)
busLowerLimitCharge[busLowerLimitCharge["number"]<511].plot(x="number",y="income",label="Lower Limit",ax=ax,style="g-.",lw=3)

ax.set(ylabel= "Income ($)", xlabel='Number of Vehicles')
ax.legend(numpoints=1)


plt.tight_layout()
plt.savefig('Theory-Simulation-Comparison-Bus.pdf')

print(busChargerIncomeDataFrame[-1:])
print(busUpperLimitCharge[-1:])
print(busLowerLimitCharge[-1:])
print(busSwappingIncomeDataFrame[-1:])
print(busUpperLimitSwap[-1:])
print(busLowerLimitSwap[-1:])
