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


def simulateDCChargingStationIncome(numberOfDCCharger, numberOfTaxis, numberOfBuses):
    chargerCost = 5000*numberOfDCCharger
    # chargerCost = 0
    taxiChargingStation = DCChargingStations(numberOfDCCharger)
    taxiFleet = []
    for i in range(numberOfTaxis):
        newTaxi = Taxi()
        newTaxi.useSwapping = 0
        taxiFleet.append(newTaxi)

    busChargingStation = DCChargingStations(numberOfDCCharger)
    busFleet = []
    for i in range(numberOfBuses):
        newBus = Bus()
        newBus.useSwapping = 0
        busFleet.append(newBus)

    time = 0
    taxiIncome = []
    busIncome = []
    taxiChargerIncome = []
    busChargerIncome = []
    while time < 24 * 60 * 30:
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
                chargingTaxi.charge(time, 0, taxiChargingStation.chargeSpeed)
                tempChargingVehicles.append(chargingTaxi)
        taxiChargingStation.chargingVehicles = tempChargingVehicles

        while taxiChargingStation.numberOfStations - len(taxiChargingStation.chargingVehicles) > 0:
            if len(taxiChargingStation.pendingVehicles) > 0:
                newChargeTaxi = taxiChargingStation.pendingVehicles.pop(0)
                newChargeTaxi.charge(time, 0, taxiChargingStation.chargeSpeed)
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

        taxiIncome.append([time, todayTaxiIncome, len(taxiFleet), len(taxiChargingStation.chargingVehicles),
                           len(taxiChargingStation.pendingVehicles)])
        busIncome.append([time, todayBusIncome, len(busFleet), len(busChargingStation.chargingVehicles),
                          len(busChargingStation.pendingVehicles)])
        taxiChargerIncome.append([time, taxiChargingStation.income])
        busChargerIncome.append([time, busChargingStation.income])
        time += 1
    return taxiIncome[-1][1], busIncome[-1][1],taxiChargerIncome[-1][1]-chargerCost,busChargerIncome[-1][1]-chargerCost

def simulateSwapperIncome(numberOfSlot, numberOfTaxis, numberOfBuses):
    swapperInitCost = 2.5*(10**6)
    swapperSlotCost = 1000 * (numberOfSlot-1)
    totalSwapperCost = swapperInitCost+swapperSlotCost
    # totalSwapperCost = 0
    taxiSwappingStation = BatterySwappingStation(numberOfSlot, 30)
    taxiFleet = []
    for i in range(numberOfTaxis):
        newTaxi = Taxi()
        newTaxi.useSwapping = 1
        taxiFleet.append(newTaxi)

    busSwappingStation = BatterySwappingStation(numberOfSlot, 324)
    busFleet = []
    for i in range(numberOfBuses):
        newBus = Bus()
        newBus.useSwapping = 1
        busFleet.append(newBus)

    time = 0
    taxiIncome = []
    busIncome = []
    taxiSwapperIncome = []
    busSwapperIncome = []
    while time < 24 * 60 * 7:
        tempTaxiFleet = []
        todayTaxiIncome = 0
        todayBusIncome = 0
        for runningTaxi in taxiFleet:
            runningTaxi.decideChargeMode(time)
            if runningTaxi.chargingMode == 1:
                result = taxiSwappingStation.addVehicle(runningTaxi)
                if result > 0:
                    runningTaxi.charge(time, result, 0)
                    # print("get into queue:" + str(time))
                    taxiSwappingStation.swappingVehicles.append(runningTaxi)
            else:
                runningTaxi.getTravelSpeed(time)
                tempTaxiFleet.append(runningTaxi)
        taxiFleet = tempTaxiFleet

        tempSwappingVehicles = []
        for swappingTaxi in taxiSwappingStation.swappingVehicles:
            swappingTaxi.charge(time, 0, 0)
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
                newTaxi.charge(time, result, 0)
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
        taxiIncome.append([time, todayTaxiIncome, len(taxiFleet), len(taxiSwappingStation.swappingVehicles),
                           len(taxiSwappingStation.pendingVehicles), \
                           len(taxiFleet) + len(taxiSwappingStation.swappingVehicles) + len(
                               taxiSwappingStation.pendingVehicles)])
        busIncome.append([time, todayBusIncome, len(busFleet), len(busSwappingStation.swappingVehicles),
                          len(busSwappingStation.pendingVehicles), \
                          len(busFleet) + len(busSwappingStation.swappingVehicles) + len(
                              busSwappingStation.pendingVehicles)])
        taxiSwapperIncome.append([time, taxiSwappingStation.income])
        busSwapperIncome.append([time, busSwappingStation.income])

        time += 1
    return taxiIncome[-1][1], busIncome[-1][1],taxiSwapperIncome[-1][1]-totalSwapperCost,busSwapperIncome[-1][1]-totalSwapperCost

def simulateTaxiDCChargingStationIncome(numberOfDCCharger, numberOfTaxis):
    chargerCost = 15000*numberOfDCCharger
    # chargerCost = 0
    taxiChargingStation = DCChargingStations(numberOfDCCharger)
    taxiFleet = []
    for i in range(numberOfTaxis):
        newTaxi = Taxi()
        newTaxi.useSwapping = 0
        taxiFleet.append(newTaxi)

    time = 0
    taxiIncome = []
    taxiChargerIncome = []
    while time < 24 * 60 * 30:
        tempTaxiFleet = []
        todayTaxiIncome = 0
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
                chargingTaxi.charge(time, 0, taxiChargingStation.chargeSpeed)
                tempChargingVehicles.append(chargingTaxi)
        taxiChargingStation.chargingVehicles = tempChargingVehicles

        while taxiChargingStation.numberOfStations - len(taxiChargingStation.chargingVehicles) > 0:
            if len(taxiChargingStation.pendingVehicles) > 0:
                newChargeTaxi = taxiChargingStation.pendingVehicles.pop(0)
                newChargeTaxi.charge(time, 0, taxiChargingStation.chargeSpeed)
                taxiChargingStation.chargingVehicles.append(newChargeTaxi)
            else:
                break
        taxiChargingStation.charge()


        taxiIncome.append([time, todayTaxiIncome, len(taxiFleet), len(taxiChargingStation.chargingVehicles),
                           len(taxiChargingStation.pendingVehicles)])
        taxiChargerIncome.append([time, taxiChargingStation.income])
        time += 1
    return taxiIncome[-1][1]*6, taxiChargerIncome[-1][1]*6-chargerCost

def simulateBusDCChargingStationIncome(numberOfDCCharger, numberOfBuses):
    chargerCost = 15000*numberOfDCCharger
    # chargerCost = 0

    busChargingStation = DCChargingStations(numberOfDCCharger)
    busFleet = []
    for i in range(numberOfBuses):
        newBus = Bus()
        newBus.useSwapping = 0
        busFleet.append(newBus)

    time = 0
    busIncome = []
    busChargerIncome = []
    while time < 24 * 60 * 30*6:
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
    return busIncome[-1][1],busChargerIncome[-1][1]-chargerCost

def simulateTaxiSwapperIncome(numberOfSlot, numberOfTaxis):
    swapperInitCost = 2.5*(10**6)
    swapperSlotCost = 5000 * (numberOfSlot-1)
    totalSwapperCost = swapperInitCost+swapperSlotCost
    # totalSwapperCost = 0
    taxiSwappingStation = BatterySwappingStation(numberOfSlot, 30)
    taxiFleet = []
    for i in range(numberOfTaxis):
        newTaxi = Taxi()
        newTaxi.useSwapping = 1
        taxiFleet.append(newTaxi)

    time = 0
    taxiIncome = []
    taxiSwapperIncome = []
    while time < 24 * 60 * 30*6:
        tempTaxiFleet = []
        todayTaxiIncome = 0
        for runningTaxi in taxiFleet:
            runningTaxi.decideChargeMode(time)
            if runningTaxi.chargingMode == 1:
                result = taxiSwappingStation.addVehicle(runningTaxi)
                if result > 0:
                    runningTaxi.charge(time, result, 0)
                    # print("get into queue:" + str(time))
                    taxiSwappingStation.swappingVehicles.append(runningTaxi)
            else:
                runningTaxi.getTravelSpeed(time)
                tempTaxiFleet.append(runningTaxi)
        taxiFleet = tempTaxiFleet

        tempSwappingVehicles = []
        for swappingTaxi in taxiSwappingStation.swappingVehicles:
            swappingTaxi.charge(time, 0, 0)
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
                newTaxi.charge(time, result, 0)
                # print("bump from pending to swap:" + str(time))
                taxiSwappingStation.swappingVehicles.append(newTaxi)
            else:
                break


        for taxi in taxiFleet + taxiSwappingStation.swappingVehicles + taxiSwappingStation.pendingVehicles:
            todayTaxiIncome += taxi.income
        taxiIncome.append([time, todayTaxiIncome, len(taxiFleet), len(taxiSwappingStation.swappingVehicles),
                           len(taxiSwappingStation.pendingVehicles), \
                           len(taxiFleet) + len(taxiSwappingStation.swappingVehicles) + len(
                               taxiSwappingStation.pendingVehicles)])

        taxiSwapperIncome.append([time, taxiSwappingStation.income])

        time += 1
    return taxiIncome[-1][1],taxiSwapperIncome[-1][1]-totalSwapperCost


def simulateBusSwapperIncome(numberOfSlot, numberOfBuses):
    swapperInitCost = 2.5*(10**6)
    swapperSlotCost = 5000 * (numberOfSlot-1)
    totalSwapperCost = swapperInitCost+swapperSlotCost
    # totalSwapperCost = 0

    busSwappingStation = BatterySwappingStation(numberOfSlot, 324)
    busFleet = []
    for i in range(numberOfBuses):
        newBus = Bus()
        newBus.useSwapping = 1
        busFleet.append(newBus)

    time = 0
    busIncome = []
    busSwapperIncome = []
    while time < 24 * 60 * 30*6:
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
    return busIncome[-1][1],busSwapperIncome[-1][1]-totalSwapperCost


taxiChargerIncome = []
busChargerIncome = []
taxiSwappingIncome = []
busSwappingIncome = []
taxiDCChargerIncome = []
taxiSwapperIncome = []
busDCChargerIncome = []
busSwapperIncome = []
for i in range(2):
    print(i+1)
    # approximately income is 20851 per charger
    thisTaxiCharger, thisTaxiDCCharger = simulateTaxiDCChargingStationIncome(1, i+1)#27.2

    #approximately 206000 per swapper
    thisTaxiSwap, thisTaxiSwapper = simulateTaxiSwapperIncome(1, i+1)
    taxiChargerIncome.append([i+1,thisTaxiCharger])
    taxiSwappingIncome.append([i+1,thisTaxiSwap])
    taxiDCChargerIncome.append([i+1,thisTaxiDCCharger])
    taxiSwapperIncome.append([i+1,thisTaxiSwapper])

for i in range(0,600,10):
    print(i+1)
    # thisBusCharger, thisBusDCCharger = simulateBusDCChargingStationIncome(210, i+1)
    thisBusSwap, thisBusSwapper = simulateBusSwapperIncome(9, i+1)
    # busChargerIncome.append([i+1,thisBusCharger])
    busSwappingIncome.append([i+1,thisBusSwap])
    # busDCChargerIncome.append([i+1,thisBusDCCharger])
    busSwapperIncome.append([i+1,thisBusSwapper])

taxiChargerIncomeDataFrame = pd.DataFrame(taxiChargerIncome,columns=["number","income"])
# busChargerIncomeDataFrame = pd.DataFrame(busChargerIncome,columns=["number","income"])
taxiSwappingIncomeDataFrame = pd.DataFrame(taxiSwappingIncome,columns=["number","income"])
busSwappingIncomeDataFrame = pd.DataFrame(busSwappingIncome,columns=["number","income"])
taxiDCChargerIncomeDataFrame = pd.DataFrame(taxiDCChargerIncome,columns=["number","income"])
taxiSwapperIncomeDataFrame = pd.DataFrame(taxiSwapperIncome,columns=["number","income"])
# busDCChargerIncomeDataFrame = pd.DataFrame(busDCChargerIncome,columns=["number","income"])
busSwapperIncomeDataFrame = pd.DataFrame(busSwapperIncome,columns=["number","income"])

taxiChargerIncomeDataFrame.to_pickle("taxiChargerIncomeDataFrame.pkl")
# busChargerIncomeDataFrame.to_pickle("busChargerIncomeDataFrame.pkl")
taxiSwappingIncomeDataFrame.to_pickle("taxiSwappingIncomeDataFrame.pkl")
busSwappingIncomeDataFrame.to_pickle("busSwappingIncomeDataFrame.pkl")
taxiDCChargerIncomeDataFrame.to_pickle("taxiDCChargerIncomeDataFrame.pkl")
taxiSwapperIncomeDataFrame.to_pickle("taxiSwapperIncomeDataFrame.pkl")
# busDCChargerIncomeDataFrame.to_pickle("busDCChargerIncomeDataFrame.pkl")
busSwapperIncomeDataFrame.to_pickle("busSwapperIncomeDataFrame.pkl")

