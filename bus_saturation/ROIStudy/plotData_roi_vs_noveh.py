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
sns.set(font_scale=2)
sns.set_style("whitegrid", {
        "font.family": "serif",
        "font.serif": ["Times", "Palatino", "serif"],
        'grid.color': '.9',
        'grid.linestyle': '--',
})
plt.figure(figsize=(9, 6.5), dpi=1600)
ax = plt.subplot(1,1,1)
numberOfBattery = busSwapperBatteryDataFrame["number of battery"]
# print(numberOfBattery)
fixedCost = numberOfBattery*324*227 + (9-1) * 5000 + 2.5*(10**6)
computedIncome = busSwapperIncomeDataFrame["income"]
#consider cost for electricity
monthlyIncome = (computedIncome + fixedCost )/6*(1-0.023)/1 - 36245*0.023
addtionalCostSwapPerBattery = 15000*numberOfBattery


fixedChargerCost = 210*15000
#considering cost of electricity of running cost of charging station
monthlyIncome_charger = (busDCChargerIncomeDataFrame["income"] + fixedChargerCost)/6*(0.6-0.023)/0.6 - 0.13*210*24*30*0.023
print(monthlyIncome-busSwapperBatterySwapNoDataFrame["number of swap"]*324*227/550-monthlyIncome_charger)
print(fixedCost-fixedChargerCost)
breakevenPoint = (fixedCost-fixedChargerCost)/(monthlyIncome-busSwapperBatterySwapNoDataFrame["number of swap"]*324*227/550-monthlyIncome_charger)

breakevenPoint = breakevenPoint[(breakevenPoint > 10)]
print(breakevenPoint)
breakevenPoint.index = busDCChargerIncomeDataFrame.iloc[breakevenPoint.index]["number"]
breakevenPoint.plot(label="Provider",ax=ax,style="r-o",lw=3,legend=True)

breakevenPoint2 = (fixedCost+busSwappingIncomeDataFrame.iloc[:,0]*550000-fixedChargerCost-busChargerIncomeDataFrame.iloc[:,0]*500000)/\
                 (monthlyIncome+busSwappingIncomeDataFrame["income"]/6-busSwapperBatterySwapNoDataFrame["number of swap"]*324*227/550-\
                  (monthlyIncome_charger+busChargerIncomeDataFrame.iloc[-1]["income"]/6-busDCChargeNumberDataFrame["number of charge"]*324*227/250))

breakevenPoint2 = breakevenPoint2[(breakevenPoint2 > 10)]
breakevenPoint2.index = busDCChargerIncomeDataFrame.iloc[breakevenPoint2.index]["number"]
breakevenPoint2.plot(label="Society",ax=ax,style="b-.o",lw=3,legend=True)

ax.set(xlabel= "Number of Vehicles", ylabel='Time (month)')
plt.xlim(0,600)
plt.tight_layout()
plt.savefig('ROIStudy_bus.pdf')