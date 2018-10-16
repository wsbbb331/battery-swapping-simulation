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
import multiprocessing


def simulateBusDCChargingStationIncome(numberOfDCCharger, numberOfBuses, movingSpeed):
    chargerCost = 15000*numberOfDCCharger
    chargerCost = 0

    busChargingStation = DCChargingStations(numberOfDCCharger)
    busFleet = []
    for i in range(numberOfBuses):
        newBus = Bus()
        newBus.useSwapping = 0
        newBus.normalSpeed = movingSpeed
        busFleet.append(newBus)

    time = 0
    busIncome = []
    busChargerIncome = []
    while time < 24 * 60 * 30:
        todayBusIncome = 0
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

        for bus in busFleet + busChargingStation.chargingVehicles + busChargingStation.pendingVehicles:
            todayBusIncome += bus.income

        busIncome.append([time, todayBusIncome, len(busFleet), len(busChargingStation.chargingVehicles),
                          len(busChargingStation.pendingVehicles)])
        busChargerIncome.append([time, busChargingStation.income])
        time += 1
    return busIncome[-1][1]*6,busChargerIncome[-1][1]*6-chargerCost



def simulateBusSwapperIncome(numberOfSlot, numberOfBuses, busSpeed):
    swapperInitCost = 2.5*(10**6)
    swapperSlotCost = 5000 * (numberOfSlot-1)
    totalSwapperCost = swapperInitCost+swapperSlotCost
    totalSwapperCost = 0

    busSwappingStation = BatterySwappingStation(numberOfSlot, 324)
    busFleet = []
    for i in range(numberOfBuses):
        newBus = Bus()
        newBus.useSwapping = 1
        newBus.normalSpeed = busSpeed
        busFleet.append(newBus)

    time = 0
    busIncome = []
    busSwapperIncome = []
    while time < 24 * 60 * 30:
        todayBusIncome = 0
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

        for bus in busFleet + busSwappingStation.swappingVehicles + busSwappingStation.pendingVehicles:
            todayBusIncome += bus.income

        busIncome.append([time, todayBusIncome, len(busFleet), len(busSwappingStation.swappingVehicles),
                          len(busSwappingStation.pendingVehicles), \
                          len(busFleet) + len(busSwappingStation.swappingVehicles) + len(
                              busSwappingStation.pendingVehicles)])
        busSwapperIncome.append([time, busSwappingStation.income])

        time += 1
    return busIncome[-1][1]*6,busSwapperIncome[-1][1]*6-totalSwapperCost

def iterate(iteration):
    taxiChargerIncome = []
    busChargerIncome = []
    taxiSwappingIncome = []
    busSwappingIncome = []
    taxiDCChargerIncome = []
    taxiSwapperIncome = []
    busDCChargerIncome = []
    busSwapperIncome = []

    j_previous_charge = 50
    j_previous_swap = 200
    for i in range(10,45,1):
        # previousBusCharger = 0.001
        # for j in range(j_previous_charge - 25, j_previous_charge+67, 1):
        #     thisBusCharger, thisBusDCCharger = simulateBusDCChargingStationIncome(24, j, i)
        #     if abs(thisBusCharger - previousBusCharger)/previousBusCharger < 0.005:
        #         break
        #     else:
        #         previousBusCharger = thisBusCharger
        # j_previous_charge = j
        # busChargerIncome.append([i, j])
        # busDCChargerIncome.append([i, j])

        previousBusSwapper = 0.001
        for j in range(j_previous_swap - 20, j_previous_swap + 67, 1):
            thisBusSwap, thisBusSwapper = simulateBusSwapperIncome(2, j, i)
            print(thisBusSwap)
            if abs(thisBusSwapper - previousBusSwapper)/previousBusSwapper < 0.005:
                break
            else:
                previousBusSwapper = thisBusSwapper
        j_previous_swap = j
        busSwappingIncome.append([i, j])
        busSwapperIncome.append([i, j])

    # busChargerIncomeDataFrame = pd.DataFrame(busChargerIncome,columns=["number","income"])
    busSwappingIncomeDataFrame = pd.DataFrame(busSwappingIncome,columns=["number","income"])
    # busDCChargerIncomeDataFrame = pd.DataFrame(busDCChargerIncome,columns=["number","income"])
    busSwapperIncomeDataFrame = pd.DataFrame(busSwapperIncome,columns=["number","income"])

    # busChargerIncomeDataFrame.to_pickle("busChargerIncomeDataFrame"+str(iteration)+".pkl")
    busSwappingIncomeDataFrame.to_pickle("busSwappingIncomeDataFrame"+str(iteration)+".pkl")
    # busDCChargerIncomeDataFrame.to_pickle("busDCChargerIncomeDataFrame"+str(iteration)+".pkl")
    busSwapperIncomeDataFrame.to_pickle("busSwapperIncomeDataFrame"+str(iteration)+".pkl")

for i in range(30):
    p = multiprocessing.Process(target=iterate, args=(i,))
    p.start()