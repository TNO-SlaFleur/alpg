
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

import abc
import os
import profilegentools
from configLoader import Config


class AbstractWriter(abc.ABC):
    @abc.abstractmethod
    def createEmptyFiles(self):
        pass

    @abc.abstractmethod
    def writeNeighbourhood(self, num):
        pass

    @abc.abstractmethod
    def writeHousehold(self, config, house, num):
        pass

    @abc.abstractmethod
    def writeDeviceBufferTimeshiftable(self, machine, hnum):
        pass

    @abc.abstractmethod
    def writeDeviceTimeshiftable(self, machine, hnum):
        pass

    @abc.abstractmethod
    def writeDeviceThermostat(self, machine, hnum):
        pass


class DefaultWriter(AbstractWriter):
    output_folder: str

    def __init__(self, config: Config):
        self.output_folder = config.output_dir

    def writeCsvLine(self, fname, hnum, line):
        if not os.path.exists(self.output_folder+'/'+fname):
            #overwrite
            f = open(self.output_folder+'/'+fname, 'w')
        else:
            #append
            f = open(self.output_folder+'/'+fname, 'a')
        f.write(line + '\n')
        f.close()

    def writeCsvRow(self, fname, hnum, data):
        if hnum == 0:
            with open(self.output_folder+'/'+fname, 'w') as f:
                for l in range(0, len(data)):
                    f.write(str(round(data[l])) + '\n')
        else:
            with open(self.output_folder+'/'+fname, 'r+') as f:
                lines = f.readlines()
                f.seek(0)
                f.truncate()
                j = 0
                for line in lines:
                    line = line.rstrip()
                    line = line + ';' + str(round(data[j])) + '\n'
                    f.write(line)
                    j = j + 1

    def createFile(self, fname):
        if os.path.exists(fname):
            os.utime(self.output_folder+'/'+fname, None)
        else:
            open(self.output_folder+'/'+fname, 'a').close()

    def createEmptyFiles(self):
        # Function to create empty files to ensure that certain software doesn't crash for lack of files
        self.createFile('Electricity_Profile.csv')
        self.createFile('Electricity_Profile_GroupOther.csv')
        self.createFile('Electricity_Profile_GroupInductive.csv')
        self.createFile('Electricity_Profile_GroupFridges.csv')
        self.createFile('Electricity_Profile_GroupElectronics.csv')
        self.createFile('Electricity_Profile_GroupLighting.csv')
        self.createFile('Electricity_Profile_GroupStandby.csv')

        self.createFile('Reactive_Electricity_Profile.csv')
        self.createFile('Reactive_Electricity_Profile_GroupOther.csv')
        self.createFile('Reactive_Electricity_Profile_GroupInductive.csv')
        self.createFile('Reactive_Electricity_Profile_GroupFridges.csv')
        self.createFile('Reactive_Electricity_Profile_GroupElectronics.csv')
        self.createFile('Reactive_Electricity_Profile_GroupLighting.csv')
        self.createFile('Reactive_Electricity_Profile_GroupStandby.csv')

        self.createFile('Electricity_Profile_PVProduction.csv')
        self.createFile('PhotovoltaicSettings.txt')
        self.createFile('Electricity_Profile_PVProduction.csv')
        self.createFile('BatterySettings.txt')
        self.createFile('HeatingSettings.txt')

        self.createFile('ElectricVehicle_Starttimes.txt')
        self.createFile('ElectricVehicle_Endtimes.txt')
        self.createFile('ElectricVehicle_RequiredCharge.txt')
        self.createFile('ElectricVehicle_Specs.txt')

        self.createFile('WashingMachine_Starttimes.txt')
        self.createFile('WashingMachine_Endtimes.txt')
        self.createFile('WashingMachine_Profile.txt')

        self.createFile('Dishwasher_Starttimes.txt')
        self.createFile('Dishwasher_Endtimes.txt')
        self.createFile('Dishwasher_Profile.txt')

        self.createFile('Thermostat_Starttimes.txt')
        self.createFile('Thermostat_Setpoints.txt')

        # Save HeatGain profiles
        self.createFile('Heatgain_Profile.csv')
        self.createFile('Heatgain_Profile_Persons.csv')
        self.createFile('Heatgain_Profile_Devices.csv')

        # Safe TapWater profiles
        self.createFile('Heatdemand_Profile.csv')
        self.createFile('Heatdemand_Profile_DHWTap.csv')

        self.createFile('Airflow_Profile_Ventilation.csv')

    def writeNeighbourhood(self, num):
        pass

    def writeHousehold(self, config, house, num):
        #Save the profile:
        self.writeCsvRow('Electricity_Profile.csv', num, house.Consumption['Total'])
        self.writeCsvRow('Electricity_Profile_GroupOther.csv', num, house.Consumption['Other'])
        self.writeCsvRow('Electricity_Profile_GroupInductive.csv', num, house.Consumption['Inductive'])
        self.writeCsvRow('Electricity_Profile_GroupFridges.csv', num, house.Consumption['Fridges'])
        self.writeCsvRow('Electricity_Profile_GroupElectronics.csv', num, house.Consumption['Electronics'])
        self.writeCsvRow('Electricity_Profile_GroupLighting.csv', num, house.Consumption['Lighting'])
        self.writeCsvRow('Electricity_Profile_GroupStandby.csv', num, house.Consumption['Standby'])

        self.writeCsvRow('Reactive_Electricity_Profile.csv', num, house.ReactiveConsumption['Total'])
        self.writeCsvRow('Reactive_Electricity_Profile_GroupOther.csv', num, house.ReactiveConsumption['Other'])
        self.writeCsvRow('Reactive_Electricity_Profile_GroupInductive.csv', num, house.ReactiveConsumption['Inductive'])
        self.writeCsvRow('Reactive_Electricity_Profile_GroupFridges.csv', num, house.ReactiveConsumption['Fridges'])
        self.writeCsvRow('Reactive_Electricity_Profile_GroupElectronics.csv', num, house.ReactiveConsumption['Electronics'])
        self.writeCsvRow('Reactive_Electricity_Profile_GroupLighting.csv', num, house.ReactiveConsumption['Lighting'])
        self.writeCsvRow('Reactive_Electricity_Profile_GroupStandby.csv', num, house.ReactiveConsumption['Standby'])

        # Save HeatGain profiles
        self.writeCsvRow('Heatgain_Profile.csv', num, house.HeatGain['Total'])
        self.writeCsvRow('Heatgain_Profile_Persons.csv', num, house.HeatGain['PersonGain'])
        self.writeCsvRow('Heatgain_Profile_Devices.csv', num, house.HeatGain['DeviceGain'])

        # Safe TapWater profiles
        self.writeCsvRow('Heatdemand_Profile.csv', num, house.HeatDemand['Total'])
        self.writeCsvRow('Heatdemand_Profile_DHWTap.csv', num, house.HeatDemand['DHWDemand'])

        # Airflow, kind of hacky
        self.writeCsvRow('Airflow_Profile_Ventilation.csv', num, house.HeatGain['VentFlow'])

        # writeCsvRow('Heatgain_Profile_Solar.csv', num, house.HeatGain['SolarGain'])

        # FIXME Add DHW Profile

        #Write all devices:
        for k, v, in house.Devices.items():
            house.Devices[k].writeDevice(config, num)

        #Write all heatdevices:
        for k, v, in house.HeatingDevices.items():
            house.HeatingDevices[k].writeDevice(num)

        #House specific devices
        if house.House.hasPV:
            text = str(num)+':'
            text += str(house.House.pvElevation)+','+str(house.House.pvAzimuth)+','+str(house.House.pvEfficiency)+','+str(house.House.pvArea)
            self.writeCsvLine('PhotovoltaicSettings.txt', num, text)

        self.writeCsvRow('Electricity_Profile_PVProduction.csv', num, house.PVProfile)

        if house.House.hasBattery:
            text = str(num)+':'
            text += str(house.House.batteryPower)+','+str(house.House.batteryCapacity)+','+str(round(house.House.batteryCapacity/2))
            self.writeCsvLine('BatterySettings.txt', num, text)

        # Write what type of heating device is used
        if house.hasHP:
            text = str(num)+':HP'			# Heat pump
            self.writeCsvLine('HeatingSettings.txt', num, text)
        elif house.hasCHP:
            text = str(num)+':CHP'			# Combined Heat Power
            self.writeCsvLine('HeatingSettings.txt', num, text)
        else:
            text = str(num)+':CONVENTIONAL'	# Conventional heating device, e.g. natural gas boiler
            self.writeCsvLine('HeatingSettings.txt', num, text)

    def writeDeviceBufferTimeshiftable(self, machine, hnum):
        if machine.BufferCapacity > 0 and len(machine.StartTimes) > 0:
            text = str(hnum)+':'
            text += profilegentools.createStringList(machine.StartTimes, None, 60)
            self.writeCsvLine('ElectricVehicle_Starttimes.txt', hnum, text)

            text = str(hnum)+':'
            text += profilegentools.createStringList(machine.EndTimes, None, 60)
            self.writeCsvLine('ElectricVehicle_Endtimes.txt', hnum, text)

            text = str(hnum)+':'
            text += profilegentools.createStringList(machine.EnergyLoss, None, 1, False)
            self.writeCsvLine('ElectricVehicle_RequiredCharge.txt', hnum, text)

            text = str(hnum)+':'
            text += str(machine.BufferCapacity)+','+str(machine.Consumption)
            self.writeCsvLine('ElectricVehicle_Specs.txt', hnum, text)

    def writeDeviceTimeshiftable(self, machine, hnum):
        if machine.name == "WashingMachine" and len(machine.StartTimes) > 0:
            text = str(hnum)+':'
            text += profilegentools.createStringList(machine.StartTimes, None, 60)
            self.writeCsvLine('WashingMachine_Starttimes.txt', hnum, text)

            text = str(hnum)+':'
            text += profilegentools.createStringList(machine.EndTimes, None, 60)
            self.writeCsvLine('WashingMachine_Endtimes.txt', hnum, text)

            text = str(hnum)+':'
            text += machine.LongProfile
            self.writeCsvLine('WashingMachine_Profile.txt', hnum, text)

        elif len(machine.StartTimes) > 0:
            #In our case it is a dishwasher
            text = str(hnum)+':'
            text += profilegentools.createStringList(machine.StartTimes, None, 60)
            self.writeCsvLine('Dishwasher_Starttimes.txt', hnum, text)

            text = str(hnum)+':'
            text += profilegentools.createStringList(machine.EndTimes, None, 60)
            self.writeCsvLine('Dishwasher_Endtimes.txt', hnum, text)

            text = str(hnum)+':'
            text += machine.LongProfile
            self.writeCsvLine('Dishwasher_Profile.txt', hnum, text)

    def writeDeviceThermostat(self, machine, hnum):
        text = str(hnum)+':'
        text += profilegentools.createStringList(machine.StartTimes, None, 60)
        self.writeCsvLine('Thermostat_Starttimes.txt', hnum, text)

        text = str(hnum)+':'
        text += profilegentools.createStringList(machine.Setpoints)
        self.writeCsvLine('Thermostat_Setpoints.txt', hnum, text)
