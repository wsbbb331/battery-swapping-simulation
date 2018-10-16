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



class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)

class Taxi:
    __metaclass__ = IterRegistry
    _registry = []

    def __init__(self):
        self.batteryCapacity = 30.0
        self.remainingBatterykWh = self.batteryCapacity
        self.income = 0
        self.travelConsumption = 0.34 #kwh per mile
        self.chargingMode = 0
        self.busyTime = 18*60 #unit is minute
        self.endBusyTime = 21*60
        self.stopShiftTime = 2*60
        self.startShiftTime = 5*60
        self.electricityPrice = 0.6 #dollar/kwh
        self.hirePrice = 2 #dollar/mile
        self.useSwapping = 0
        self.swapCost = 1 #dollar/mile
        self.swapStartTime = 0 #startTimeForEach ongoing Swap
        self.swapTime = 5
        self.hiredSpeed = 30

    def getTravelSpeed(self, currentTime):
        if self.chargingMode == 0:
            if self.getHiredOrNot(currentTime):
                trafficAdjustment = self.getTrafficAdjustment(currentTime)
                self.speed = max(random.normalvariate(self.hiredSpeed/60+trafficAdjustment/60,10/60),0)
                self.income += self.speed * self.hirePrice
            elif currentTime%(24*60) < self.stopShiftTime or currentTime%(24*60) > self.startShiftTime:
                self.speed = max(random.normalvariate(10/60,10/60),0)
            else:
                self.speed = max(random.normalvariate(1/ 60, 1/ 60), 0)
            self.remainingBatterykWh -= self.speed * self.travelConsumption

    def probByBusyTime(self,currentTime):
        return self.calculateProbabilityFromTime(currentTime,self.busyTime)

    def probByStopShiftTime(self,currentTime):
        if currentTime%(24*60) < self.startShiftTime and currentTime%(24*60) > self.stopShiftTime:
            return 1
        else:
            return self.calculateProbabilityFromTime(currentTime,self.stopShiftTime)

    def calculateProbabilityFromTime(self,currentTime,targetTime):
        if currentTime%(24*60) > targetTime:
            return math.exp(2*(targetTime-currentTime % (24 * 60)))
        else:
            return math.exp(currentTime % (24 * 60) - targetTime)

    def decideChargeMode(self, currentTime):
        if (self.chargingMode == 1):
            if random.random() < math.exp(self.remainingBatterykWh-self.batteryCapacity) \
                    or random.random() < self.probByBusyTime(currentTime):
                #busy time must leave or leave when almost full
                self.chargingMode = 0
        else:
            if random.random() < math.exp(-self.remainingBatterykWh) or \
                    (random.random() < self.probByStopShiftTime(currentTime) and self.remainingBatterykWh < self.batteryCapacity * 0.9):
                #go to charge when battery is low or stop shift time is coming
                self.chargingMode = 1

    def getHiredOrNot(self, currentTime):
        if currentTime%(24*60) < self.endBusyTime and currentTime%(24*60) > self.busyTime:
            return random.random() < 0.95
        elif currentTime%(24*60) < self.stopShiftTime or currentTime%(24*60) > self.startShiftTime:
            return random.random() < 0.6
        else:
            return random.random() < 0.1

    def getTrafficAdjustment(self, currentTime):
        if currentTime%(24*60) < self.endBusyTime and currentTime%(24*60) > self.busyTime:
            return -3
        elif currentTime%(24*60) < self.stopShiftTime or currentTime%(24*60) > self.startShiftTime:
            return 0
        else:
            return 3

    def charge(self, currentTime, swapCapacity, chargeSpeed):
        if self.chargingMode == 1:
            if self.useSwapping:
                if (currentTime > self.swapStartTime + self.swapTime):#first time start
                    self.swapStartTime = currentTime
                    self.income -= (swapCapacity - self.remainingBatterykWh)*self.swapCost
                    self.remainingBatterykWh = swapCapacity
                elif (currentTime == self.swapStartTime + self.swapTime):
                    self.chargingMode = 0
            else:
                self.income -= self.electricityPrice * chargeSpeed
                self.remainingBatterykWh += chargeSpeed

class Bus:
    __metaclass__ = IterRegistry
    _registry = []

    def __init__(self):
        self.batteryCapacity = 324
        self.remainingBatterykWh = self.batteryCapacity
        self.income = 0
        self.chargingMode = 0
        self.travelConsumption = 2
        self.tripTotal = 0
        self.maxTrip = 145
        self.useSwapping = 0
        self.swapCost = 1
        self.swapStartTime = 0
        self.swapTime = 10
        self.electricityPrice = 0.6
        self.busyTime = 18 * 60  # unit is minute
        self.endBusyTime = 21 * 60
        self.stopShiftTime = 2 * 60
        self.startShiftTime = 5 * 60
        self.runOnNightShift = 0
        self.normalSpeed = 25

    def getTravelSpeed(self, currentTime):
        if self.chargingMode == 0:
            if currentTime%(24*60) == self.stopShiftTime:
                if random.random() < 0.3:
                    self.runOnNightShift = 1
                else:
                    self.runOnNightShift = 0

            if currentTime%(24*60) < self.endBusyTime and currentTime%(24*60) > self.busyTime:
                self.speed = max(random.normalvariate((self.normalSpeed - 3) / 60, 3 / 60), 0)
                self.tripPrice = max(random.normalvariate(9, 1.5), 0)
            elif currentTime%(24*60) < self.startShiftTime and currentTime%(24*60) > self.stopShiftTime:
                if self.runOnNightShift == 1:
                    self.speed = max(random.normalvariate((self.normalSpeed +3) / 60, 3 / 60), 0)
                    self.tripPrice = max(random.normalvariate(2, 1.5), 0)
                else:
                    self.speed = 0
                    self.tripPrice = 0
            else:
                self.speed = max(random.normalvariate(self.normalSpeed / 60, 3 / 60), 0)
                self.tripPrice = max(random.normalvariate(5.5,1.5),0)
            self.remainingBatterykWh -= self.speed * self.travelConsumption
            self.tripTotal += self.speed
            self.income += self.speed * self.tripPrice

    def charge(self, currentTime, swapCapacity, chargeSpeed):
        if self.useSwapping:
            if (currentTime > self.swapStartTime + self.swapTime):  # first time start
                self.swapStartTime = currentTime
                self.income -= (swapCapacity - self.remainingBatterykWh) * self.swapCost
                self.remainingBatterykWh = swapCapacity
            elif (currentTime == self.swapStartTime + self.swapTime):
                self.chargingMode = 0
        else:
            self.income -= self.electricityPrice * chargeSpeed
            self.remainingBatterykWh += chargeSpeed

    def decideChargeMode(self, currentTime):
        if self.chargingMode == 0:
            if self.tripTotal >= self.maxTrip:
                self.chargingMode = 1
                self.tripTotal = 0
        else:
            if self.remainingBatterykWh >= self.batteryCapacity:
                self.chargingMode = 0
                self.maxTrip = min(random.normalvariate(130,20),160)


class BatterySwappingStation:
    def __init__(self, numberOfSlot, batteryCapacity):
        self.numberOfSlot = numberOfSlot
        self.batteryCapacity = batteryCapacity
        self.pendingVehicles = []
        self.swappingVehicles = []
        self.income = 0
        self.kwhPrice = 1
    def swap(self, intakeBattery):
        self.income += self.kwhPrice * (self.batteryCapacity - intakeBattery)
        return self.batteryCapacity
    def addVehicle(self, vehicle):
        if len(self.pendingVehicles) > 0 or len(self.swappingVehicles) >= self.numberOfSlot:
            self.pendingVehicles.append(vehicle)
            return False
        else:
            swapResult = self.swap(vehicle.remainingBatterykWh)
            return swapResult


class DCChargingStations:
    def __init__(self,numberOfStations):
        self.numberOfStations = numberOfStations
        self.chargeSpeed = 40/60
        self.chargingVehicles = []
        self.pendingVehicles = []
        self.income = 0
        self.kwhPrice = 0.6
    def addCharge(self,vehicle):
        if len(self.chargingVehicles) < self.numberOfStations:
            self.chargingVehicles.append(vehicle)
        else:
            self.pendingVehicles.append(vehicle)
    def charge(self):
        self.income += len(self.chargingVehicles)*self.kwhPrice*self.chargeSpeed
