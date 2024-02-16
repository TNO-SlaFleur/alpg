
#Copyright (C) 2023 University of Twente

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random

from alpg import configLoader
from alpg import profilegentools

class House:
    #In the end we need to define houses as well with their orientation
    def __init__(self, config: configLoader.Config):
        self.config = config
        self.hasPV = False
        self.hasBattery = False

    def addPV(self, area):
        self.hasPV = True
        self.pvArea = area
        self.pvEfficiency = random.randint(self.config.PVEfficiencyMin, self.config.PVEfficiencyMax)
        self.pvAzimuth = profilegentools.gaussMinMax(self.config.PVAzimuthMean, self.config.PVAzimuthSigma)
        if(self.pvAzimuth < 0):
            self.pvAzimuth = self.pvAzimuth + 360
        self.pvElevation = profilegentools.gaussMinMax(self.config.PVAngleMean, self.config.PVAngleSigma)

    def addBattery(self, capacity, power):
        if capacity > 0:
            self.hasBattery = True
            self.batteryCapacity = capacity
            self.batteryPower = power
