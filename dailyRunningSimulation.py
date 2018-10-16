from simulationClasses import DCChargingStations, Taxi, Bus, BatterySwappingStation
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

taxiChargingStation = DCChargingStations(5)
taxiFleet =[]
for i in range(100):
    newTaxi = Taxi()
    newTaxi.useSwapping = 0
    taxiFleet.append(newTaxi)

busChargingStation = DCChargingStations(5)
busFleet = []
for i in range(20):
    newBus = Bus()
    newBus.useSwapping = 0
    busFleet.append(newBus)

time = 0
taxiIncome = []
busIncome = []
taxiChargerIncome = []
busChargerIncome = []
while time < 24*60*7:
    tempTaxiFleet = []
    todayTaxiIncome = 0
    todayBusIncome = 0
    for runningTaxi in taxiFleet:
        runningTaxi.decideChargeMode(time)
        if runningTaxi.chargingMode == 1:
            taxiChargingStation.addCharge(runningTaxi)
        else:
            runningTaxi.getTravelSpeed(time)
            tempTaxiFleet.append(runningTaxi)
    taxiFleet = tempTaxiFleet

    tempChargingVehicles = []
    for chargingTaxi in taxiChargingStation.chargingVehicles:
        chargingTaxi.decideChargeMode(time)
        if chargingTaxi.chargingMode == 0:
            chargingTaxi.getTravelSpeed(time)
            taxiFleet.append(chargingTaxi)
        else:
            chargingTaxi.charge(time,0,taxiChargingStation.chargeSpeed)
            tempChargingVehicles.append(chargingTaxi)
    taxiChargingStation.chargingVehicles = tempChargingVehicles

    while taxiChargingStation.numberOfStations - len(taxiChargingStation.chargingVehicles) > 0:
        if len(taxiChargingStation.pendingVehicles) > 0:
            newChargeTaxi = taxiChargingStation.pendingVehicles.pop(0)
            newChargeTaxi.charge(time,0,taxiChargingStation.chargeSpeed)
            taxiChargingStation.chargingVehicles.append(newChargeTaxi)
        else:
            break
    taxiChargingStation.charge()


    tempBusFleet = []
    for runningBus in busFleet:
        runningBus.decideChargeMode(time)
        if runningBus.chargingMode == 1:
            busChargingStation.addCharge(runningBus)
        else:
            runningBus.getTravelSpeed(time)
            tempBusFleet.append(runningBus)
    busFleet = tempBusFleet

    tempChargingVehicles = []
    for chargingBus in busChargingStation.chargingVehicles:
        chargingBus.decideChargeMode(time)
        if chargingBus.chargingMode == 0:
            chargingBus.getTravelSpeed(time)
            busFleet.append(chargingBus)
        else:
            chargingBus.charge(time, 0, busChargingStation.chargeSpeed)
            tempChargingVehicles.append(chargingBus)
    busChargingStation.chargingVehicles = tempChargingVehicles

    while busChargingStation.numberOfStations - len(busChargingStation.chargingVehicles) > 0:
        if len(busChargingStation.pendingVehicles) > 0:
            newChargeBus = busChargingStation.pendingVehicles.pop(0)
            newChargeBus.charge(time, 0, busChargingStation.chargeSpeed)
            busChargingStation.chargingVehicles.append(newChargeBus)
        else:
            break
    busChargingStation.charge()


    for taxi in taxiFleet + taxiChargingStation.chargingVehicles + taxiChargingStation.pendingVehicles:
        todayTaxiIncome += taxi.income
    for bus in busFleet + busChargingStation.chargingVehicles + busChargingStation.pendingVehicles:
        todayBusIncome += bus.income

    taxiIncome.append([time,todayTaxiIncome,len(taxiFleet),len(taxiChargingStation.chargingVehicles),len(taxiChargingStation.pendingVehicles)])
    busIncome.append([time,todayBusIncome,len(busFleet),len(busChargingStation.chargingVehicles),len(busChargingStation.pendingVehicles)])
    taxiChargerIncome.append([time,taxiChargingStation.income])
    busChargerIncome.append([time, busChargingStation.income])
    time += 1

taxiIncomeDataFrame = pd.DataFrame(taxiIncome,columns=["time","income","running","charging","waiting"])
busIncomeDataFrame = pd.DataFrame(busIncome,columns=["time","income","running","charging","waiting"])
taxiChargerIncomeDataFrame = pd.DataFrame(taxiChargerIncome,columns=["time","income"])
busChargerIncomeDataFrame = pd.DataFrame(busChargerIncome,columns=["time","income"])

plt.figure(figsize=(9, 16), dpi=1600)
ax = plt.subplot(4,1,1)
for day in range(7):
    plt.axvspan(2*60 + day*60*24, 5*60 + day*60*24, facecolor='g', alpha=0.1)
    plt.axvspan(18*60 + day*60*24, 21*60 + day*60*24, facecolor='r', alpha=0.1)
ax2 = plt.subplot(4,1,2)
ax3 = plt.subplot(4,1,3)
for day in range(7):
    plt.axvspan(2*60 + day*60*24, 5*60 + day*60*24, facecolor='g', alpha=0.1)
    plt.axvspan(18*60 + day*60*24, 21*60 + day*60*24, facecolor='r', alpha=0.1)
ax4 = plt.subplot(4,1,4)
taxiIncomeDataFrame.plot(x="time",y="income",ax=ax,label="")
taxiIncomeDataFrame.plot(x="time",y="running",ax=ax2,label="Running",style="-")
taxiIncomeDataFrame.plot(x="time",y="charging",ax=ax2,label="Charging", style=":")
taxiIncomeDataFrame.plot(x="time",y="waiting",ax=ax2,label="Waiting",style="-.")
busIncomeDataFrame.plot(x="time",y="income",ax=ax3,label="")
busIncomeDataFrame.plot(x="time",y="running",ax=ax4,label="Running",style="-")
busIncomeDataFrame.plot(x="time",y="charging",ax=ax4,label="Charging",style=":")
busIncomeDataFrame.plot(x="time",y="waiting",ax=ax4,label="Waiting",style="-.")

ax.set(ylabel= "Income ($)", xlabel='Time (min)')
ax.legend_.remove()
ax2.set(ylabel= "Number", xlabel='Time (min)')
ax3.set(ylabel= "Income ($)", xlabel='Time (min)')
ax3.legend_.remove()
ax4.set(ylabel= "Number", xlabel='Time (min)')
plt.tight_layout()
box = ax2.get_position()
ax2.set_position([box.x0, box.y0, box.width * 0.8, box.height])
box = ax4.get_position()
ax4.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax2.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
ax4.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

plt.savefig('busTaxiSimulationResult.pdf', bbox_inches='tight')
# print(taxiIncomeDataFrame)
print(busIncomeDataFrame)
#
# print(taxiIncomeDataFrame.sum())
# print(taxiIncomeDataFrame.sum()/24/7/60/100)
# print("tc1:")
# print(taxiIncomeDataFrame[(taxiIncomeDataFrame["time"]%(24*60) > 18*60) & (taxiIncomeDataFrame["time"]%(24*60) < 21*60)].sum()/60/3/7/100)
# print("tc2:")
# print(taxiIncomeDataFrame[(taxiIncomeDataFrame["time"]%(24*60) > 2*60) & (taxiIncomeDataFrame["time"]%(24*60) < 5*60)].sum()/60/3/7/100)
# print("tc3:")
# print(taxiIncomeDataFrame[(taxiIncomeDataFrame["time"]%(24*60) > 5*60) & (taxiIncomeDataFrame["time"]%(24*60) < 18*60)].sum()/60/13/7/100)
# print("tc4:")
# print(taxiIncomeDataFrame[(taxiIncomeDataFrame["time"]%(24*60) > 21*60) | (taxiIncomeDataFrame["time"]%(24*60) < 2*60)].sum()/60/5/7/100)

print(busIncomeDataFrame.sum())
print(busIncomeDataFrame.sum()/24/7/60/100)
print("tc1:")
print(busIncomeDataFrame[(busIncomeDataFrame["time"]%(24*60) > 18*60) & (busIncomeDataFrame["time"]%(24*60) < 21*60)].sum()/60/7/20)
print("tc2:")
print(busIncomeDataFrame[(busIncomeDataFrame["time"]%(24*60) > 2*60) & (busIncomeDataFrame["time"]%(24*60) < 5*60)].sum()/60/7/20)
print("tc3:")
print(busIncomeDataFrame[(busIncomeDataFrame["time"]%(24*60) > 5*60) & (busIncomeDataFrame["time"]%(24*60) < 18*60)].sum()/60/7/20)
print("tc4:")
print(busIncomeDataFrame[(busIncomeDataFrame["time"]%(24*60) > 21*60) | (busIncomeDataFrame["time"]%(24*60) < 2*60)].sum()/60/7/20)




taxiSwappingStation = BatterySwappingStation(5, 30)
taxiFleet =[]
for i in range(100):
    newTaxi = Taxi()
    newTaxi.useSwapping = 1
    taxiFleet.append(newTaxi)

busSwappingStation = BatterySwappingStation(5, 324)
busFleet = []
for i in range(20):
    newBus = Bus()
    newBus.useSwapping = 1
    busFleet.append(newBus)

time = 0
taxiIncome = []
busIncome = []
taxiSwapperIncome = []
busSwapperIncome = []
swapRecord = []
while time < 24*60*7:
    tempTaxiFleet = []
    todayTaxiIncome = 0
    todayBusIncome = 0
    taxiMileage = 0
    for runningTaxi in taxiFleet:
        runningTaxi.decideChargeMode(time)
        if runningTaxi.chargingMode == 1:
            result = taxiSwappingStation.addVehicle(runningTaxi)
            swapRecord.append([time, runningTaxi.remainingBatterykWh])
            if result > 0:
                runningTaxi.charge(time,result,0)
                # print("get into queue:" + str(time))
                taxiSwappingStation.swappingVehicles.append(runningTaxi)
        else:
            runningTaxi.getTravelSpeed(time)
            tempTaxiFleet.append(runningTaxi)
    taxiFleet = tempTaxiFleet

    tempSwappingVehicles = []
    for swappingTaxi in taxiSwappingStation.swappingVehicles:
        swappingTaxi.charge(time,0,0)
        if swappingTaxi.chargingMode == 0:
            swappingTaxi.getTravelSpeed(time)
            taxiFleet.append(swappingTaxi)
        else:
            tempSwappingVehicles.append(swappingTaxi)
    taxiSwappingStation.swappingVehicles = tempSwappingVehicles

    while len(taxiSwappingStation.pendingVehicles):
        if len(taxiSwappingStation.swappingVehicles) < taxiSwappingStation.numberOfSlot:
            newTaxi = taxiSwappingStation.pendingVehicles.pop(0)
            result = taxiSwappingStation.swap(newTaxi.remainingBatterykWh)
            newTaxi.charge(time,result,0)
            # print("bump from pending to swap:" + str(time))
            taxiSwappingStation.swappingVehicles.append(newTaxi)
        else:
            break

    tempBusFleet = []
    for runningBus in busFleet:
        runningBus.decideChargeMode(time)
        if runningBus.chargingMode == 1:
            result = busSwappingStation.addVehicle(runningBus)
            if result > 0:
                runningBus.charge(time, result, 0)
                busSwappingStation.swappingVehicles.append(runningBus)
        else:
            runningBus.getTravelSpeed(time)
            tempBusFleet.append(runningBus)
    busFleet = tempBusFleet

    tempSwappingVehicles = []
    for swappingBus in busSwappingStation.swappingVehicles:
        swappingBus.charge(time, 0, 0)
        if swappingBus.chargingMode == 0:
            swappingBus.getTravelSpeed(time)
            busFleet.append(swappingBus)
        else:
            tempSwappingVehicles.append(swappingBus)
    busSwappingStation.swappingVehicles = tempSwappingVehicles

    while len(busSwappingStation.pendingVehicles) > 0:
        if len(busSwappingStation.swappingVehicles) < busSwappingStation.numberOfSlot:
            newBus = busSwappingStation.pendingVehicles.pop(0)
            result = busSwappingStation.swap(newBus.remainingBatterykWh)
            newBus.charge(time, result, 0)
            busSwappingStation.swappingVehicles.append(newBus)
        else:
            break


    for taxi in taxiFleet + taxiSwappingStation.swappingVehicles + taxiSwappingStation.pendingVehicles:
        todayTaxiIncome += taxi.income
    for bus in busFleet + busSwappingStation.swappingVehicles + busSwappingStation.pendingVehicles:
        todayBusIncome += bus.income
    taxiIncome.append([time,todayTaxiIncome,len(taxiFleet),len(taxiSwappingStation.swappingVehicles),len(taxiSwappingStation.pendingVehicles),\
                       len(taxiFleet)+len(taxiSwappingStation.swappingVehicles)+len(taxiSwappingStation.pendingVehicles)])
    busIncome.append([time,todayBusIncome,len(busFleet),len(busSwappingStation.swappingVehicles),len(busSwappingStation.pendingVehicles), \
                      len(busFleet) + len(busSwappingStation.swappingVehicles) + len(busSwappingStation.pendingVehicles)])
    taxiSwapperIncome.append([time, taxiSwappingStation.income])
    busSwapperIncome.append([time, busSwappingStation.income])
    time += 1

taxiIncomeDataFrame = pd.DataFrame(taxiIncome,columns=["time","income","running","swapping","waiting","total"])
busIncomeDataFrame = pd.DataFrame(busIncome,columns=["time","income","running","swapping","waiting","total"])
taxiSwapperIncomeDataFrame = pd.DataFrame(taxiSwapperIncome,columns=["time","income"])
busSwapperIncomeDataFrame = pd.DataFrame(busSwapperIncome,columns=["time","income"])
swapRecordDataFrame = pd.DataFrame(swapRecord,columns=["time","kWh"])

plt.figure(figsize=(9, 16), dpi=1600)
ax = plt.subplot(4,1,1)
for day in range(7):
    plt.axvspan(2*60 + day*60*24, 5*60 + day*60*24, facecolor='g', alpha=0.1)
    plt.axvspan(18*60 + day*60*24, 21*60 + day*60*24, facecolor='r', alpha=0.1)

ax2 = plt.subplot(4,1,2)
ax3 = plt.subplot(4,1,3)
for day in range(7):
    plt.axvspan(2*60 + day*60*24, 5*60 + day*60*24, facecolor='g', alpha=0.1)
    plt.axvspan(18*60 + day*60*24, 21*60 + day*60*24, facecolor='r', alpha=0.1)
ax4 = plt.subplot(4,1,4)
taxiIncomeDataFrame.plot(x="time",y="income",ax=ax,label="")
# taxiIncomeDataFrame.plot(x="time",y="total",ax=ax2,label="Total Taxi")
taxiIncomeDataFrame.plot(x="time",y="running",ax=ax2,label="Running",style="-")
taxiIncomeDataFrame.plot(x="time",y="swapping",ax=ax2,label="Swapping",style=":")
taxiIncomeDataFrame.plot(x="time",y="waiting",ax=ax2,label="Waiting",style="-.")
busIncomeDataFrame.plot(x="time",y="income",ax=ax3,label="")
# busIncomeDataFrame.plot(x="time",y="total",ax=ax4,label="Total Bus")
busIncomeDataFrame.plot(x="time",y="running",ax=ax4,label="Running",style="-")
busIncomeDataFrame.plot(x="time",y="swapping",ax=ax4,label="Swapping",style=":")
busIncomeDataFrame.plot(x="time",y="waiting",ax=ax4,label="Waiting",style="-.")
ax.set(ylabel= "Income ($)", xlabel='Time (min)')
ax.legend_.remove()
ax2.set(ylabel= "Number", xlabel='Time (min)')

ax2.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
ax3.set(ylabel= "Income ($)", xlabel='Time (min)')
ax3.legend_.remove()
ax4.set(ylabel= "Number", xlabel='Time (min)')
plt.tight_layout()
box = ax2.get_position()
ax2.set_position([box.x0, box.y0, box.width * 0.8, box.height])
box = ax4.get_position()
ax4.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax2.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
ax4.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

plt.savefig('busTaxiSimulationResult_swap.pdf',bbox_inches='tight')

# print(taxiIncomeDataFrame)
# print(busIncomeDataFrame)
#
# print(taxiIncomeDataFrame.sum())
# print(taxiIncomeDataFrame.sum()/24/7/60/100)
# print("tc1:")
# print(taxiIncomeDataFrame[(taxiIncomeDataFrame["time"]%(24*60) > 18*60) & (taxiIncomeDataFrame["time"]%(24*60) < 21*60)].sum()/60/3/7/100)
# print("tc2:")
# print(taxiIncomeDataFrame[(taxiIncomeDataFrame["time"]%(24*60) > 2*60) & (taxiIncomeDataFrame["time"]%(24*60) < 5*60)].sum()/60/3/7/100)
# print("tc3:")
# print(taxiIncomeDataFrame[(taxiIncomeDataFrame["time"]%(24*60) > 5*60) & (taxiIncomeDataFrame["time"]%(24*60) < 18*60)].sum()/60/13/7/100)
# print(swapRecordDataFrame[(swapRecordDataFrame["time"]%(24*60) > 5*60) & (swapRecordDataFrame["time"]%(24*60) < 18*60)].mean())
# print(swapRecordDataFrame[(swapRecordDataFrame["time"]%(24*60) > 5*60) & (swapRecordDataFrame["time"]%(24*60) < 18*60)].count()/7/100)
#
# print("tc4:")
# print(taxiIncomeDataFrame[(taxiIncomeDataFrame["time"]%(24*60) > 21*60) | (taxiIncomeDataFrame["time"]%(24*60) < 2*60)].sum()/60/5/7/100)


# plt.figure(figsize=(9, 8), dpi=1600)
# ax = plt.subplot(2,1,1)
# ax2 = plt.subplot(2,1,2)
# taxiChargerIncomeDataFrame.plot(x="time",y="income",label="Taxi Charger Income",ax=ax)
# busChargerIncomeDataFrame.plot(x="time",y="income",label="Bus Charger Income",ax=ax2)
#
# taxiSwapperIncomeDataFrame.plot(x="time",y="income",label="Taxi Swapper Income",ax=ax)
# busSwapperIncomeDataFrame.plot(x="time",y="income",label="Bus Swapper Income",ax=ax2)
# plt.savefig('busTaxiChargerResult.pdf')