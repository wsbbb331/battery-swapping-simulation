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

print(busDCChargeNumberDataFrame)
sns.set_context("paper")
sns.set(font_scale=2)
sns.set_style("whitegrid", {
        "font.family": "serif",
        "font.serif": ["Times", "Palatino", "serif"],
        'grid.color': '.9',
        'grid.linestyle': '--',
})

fixedChargerCost = 210*15000
monthlyIncome_charger = (busDCChargerIncomeDataFrame.iloc[-1]["income"] + fixedChargerCost)/6*(0.6-0.023)/0.6 - 0.13*210*24*30*0.023

plt.figure()
ax = plt.subplot(1,1,1)
roiSeries_charger = []
for i in range(11):
    roiSeries_charger.append([i,(monthlyIncome_charger)*i\
                              -fixedChargerCost])
roiSeriesChargerDataFrame = pd.DataFrame(roiSeries_charger,columns=["time","profit"])

roiSeriesChargerDataFrame.plot(x="time",y="profit",label="Charging", ax=ax,style="r-",lw=3)
ax.set(xlabel= "Time (month)", ylabel='Profit ($)')

plt.tight_layout()
plt.savefig('ROIStudy_bus.pdf')

plt.figure()
ax = plt.subplot(1,1,1)
roiSeries_charger = []
for i in range(61):
    roiSeries_charger.append([i,(busChargerIncomeDataFrame.iloc[-1]["income"]/6 + monthlyIncome_charger)*i-busChargerIncomeDataFrame.iloc[-1,0]*550000\
                              -fixedChargerCost-busDCChargeNumberDataFrame.iloc[-1]["number of charge"]*324*227/250*i])
roiSeriesChargerDataFrame = pd.DataFrame(roiSeries_charger,columns=["time","profit"])

roiSeriesChargerDataFrame.plot(x="time",y="profit",label="Charging", ax=ax,style="r-",lw=3)
ax.set(xlabel= "Time (month)", ylabel='Profit ($)')

plt.tight_layout()
plt.savefig('ROIStudy_bus_total.pdf')