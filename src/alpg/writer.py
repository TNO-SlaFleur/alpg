
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
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Optional

import pandas

from alpg import profilegentools
from alpg.configLoader import Config
from alpg.devices import DeviceElectricalVehicle, DeviceWashingMachine, DeviceDishwasher
from alpg.heatdemand import Thermostat
from alpg.households import THERMOSTAT_DEVICE, ELECTRIC_VEHICLE_DEVICE, DISHWASHER_DEVICE, WASHING_MACHINE_DEVICE


class AbstractWriter(abc.ABC):
    config: Config

    @abc.abstractmethod
    def createEmptyFiles(self):
        pass

    @abc.abstractmethod
    def writeNeighbourhood(self, num):
        pass

    @abc.abstractmethod
    def writeHousehold(self, config, house, num):
        pass


@dataclass
class WashingMachineExecutions:
    profile: pandas.Series
    start_and_stop_moments: list[tuple[timedelta, timedelta]]  # In time since start of year!


@dataclass
class DishwasherExecutions:
    profile: pandas.Series
    start_and_stop_moments: list[tuple[timedelta, timedelta]]  # In time since start of year!


class HouseHoldHeatingMethod(Enum):
    HEAT_PUMP = 'Heat Pump'
    COMBINED_HEAT_POWER = 'Combined Heat Power'
    CONVENTIONAL = 'CONVENTIONAL'


@dataclass
class BatterySettings:
    maximum_power_watt: float
    capacity_watt_hour: float
    initial_soc_watt_hour: float


@dataclass
class PVSettings:
    elevation_angle_degrees: float
    azimuth_degrees: float # north = 0, east = 90
    efficiency_perc: float
    area_m2: float


@dataclass
class EVChargeSession:
    start_time_since_begin: timedelta
    end_time_since_begin: timedelta
    required_charge_watt_hour: float


@dataclass
class EVChargeSessions:
    capacity_watt_hour: float
    maximum_charging_power_watt: float
    sessions: list[EVChargeSession]


@dataclass
class ThermostatSetpoint:
    start_time_since_begin: timedelta
    setpoint: float


@dataclass
class PandasHouseHold:
    house_number: int

    electricity_profile: pandas.Series
    electricity_profile_group_other: pandas.Series
    electricity_profile_group_inductive: pandas.Series
    electricity_profile_group_fridges: pandas.Series
    electricity_profile_group_electronics: pandas.Series
    electricity_profile_group_lighting: pandas.Series
    electricity_profile_group_standby: pandas.Series
    electricity_profile_pv_production: pandas.Series

    reactive_electricity_profile: pandas.Series
    reactive_electricity_profile_group_other: pandas.Series
    reactive_electricity_profile_group_inductive: pandas.Series
    reactive_electricity_profile_group_fridges: pandas.Series
    reactive_electricity_profile_group_electronics: pandas.Series
    reactive_electricity_profile_group_lighting: pandas.Series
    reactive_electricity_profile_group_standby: pandas.Series

    heating_method: HouseHoldHeatingMethod
    heatgain_profile: pandas.Series
    heatgain_profile_persons: pandas.Series
    heatgan_profile_devices: pandas.Series

    heatdemand_profile: pandas.Series
    heatdemand_profile_dhw_tap: pandas.Series

    airflow_profile_ventilation: pandas.Series

    battery_settings: Optional[BatterySettings]
    pv_settings: Optional[PVSettings]

    ev_charge_sessions: EVChargeSessions
    washing_machine_executions: WashingMachineExecutions
    dishwasher_executions: DishwasherExecutions
    thermostat_setpoints: list[ThermostatSetpoint]


class PandasWriter(AbstractWriter):
    config: Config
    households: list[PandasHouseHold]

    def __init__(self, config: Config):
        self.config = config
        self.households = []

    def createEmptyFiles(self):
        pass

    def writeNeighbourhood(self, num):
        pass

    def writeHousehold(self, config, house, num):
        if house.hasHP:
            heating_method = HouseHoldHeatingMethod.HEAT_PUMP
        elif house.hasCHP:
            heating_method = HouseHoldHeatingMethod.COMBINED_HEAT_POWER
        else:
            heating_method = HouseHoldHeatingMethod.CONVENTIONAL

        battery_settings = None
        if house.House.hasBattery:
            battery_settings = BatterySettings(maximum_power_watt=house.House.batteryPower,
                                               capacity_watt_hour=house.House.batteryCapacity,
                                               initial_soc_watt_hour=round(house.House.batteryCapacity/2))

        pv_settings = None
        if house.House.hasPV:
            pv_settings = PVSettings(elevation_angle_degrees=house.House.pvElevation,
                                     azimuth_degrees=house.House.pvAzimuth,
                                     efficiency_perc=house.House.pvEfficiency,
                                     area_m2=house.House.pvArea)

        household = PandasHouseHold(num,
                                    heating_method=heating_method,
                                    battery_settings=battery_settings,
                                    pv_settings=pv_settings,
                                    ev_charge_sessions=self.writeElectricVehicle(house.Devices[ELECTRIC_VEHICLE_DEVICE]),
                                    washing_machine_executions=self.writeDeviceWashingMachine(house.Devices[WASHING_MACHINE_DEVICE]),
                                    dishwasher_executions=self.writeDeviceDishwasher(house.Devices[DISHWASHER_DEVICE]),
                                    thermostat_setpoints=self.writeDeviceThermostat(house.HeatingDevices[THERMOSTAT_DEVICE]),
                                    electricity_profile=pandas.Series(house.Consumption['Total']),
                                    electricity_profile_group_other=pandas.Series(house.Consumption['Other']),
                                    electricity_profile_group_inductive=pandas.Series(house.Consumption['Inductive']),
                                    electricity_profile_group_fridges=pandas.Series(house.Consumption['Fridges']),
                                    electricity_profile_group_electronics=pandas.Series(house.Consumption['Electronics']),
                                    electricity_profile_group_lighting=pandas.Series(house.Consumption['Lighting']),
                                    electricity_profile_group_standby=pandas.Series(house.Consumption['Standby']),
                                    electricity_profile_pv_production=pandas.Series(house.PVProfile),
                                    reactive_electricity_profile=pandas.Series(house.ReactiveConsumption['Total']),
                                    reactive_electricity_profile_group_other=pandas.Series(house.ReactiveConsumption['Other']),
                                    reactive_electricity_profile_group_inductive=pandas.Series(house.ReactiveConsumption['Inductive']),
                                    reactive_electricity_profile_group_fridges=pandas.Series(house.ReactiveConsumption['Fridges']),
                                    reactive_electricity_profile_group_electronics=pandas.Series(house.ReactiveConsumption['Electronics']),
                                    reactive_electricity_profile_group_lighting=pandas.Series(house.ReactiveConsumption['Lighting']),
                                    reactive_electricity_profile_group_standby=pandas.Series(house.ReactiveConsumption['Standby']),
                                    heatgain_profile=pandas.Series(house.HeatGain['Total']),
                                    heatgain_profile_persons=pandas.Series(house.HeatGain['PersonGain']),
                                    heatgan_profile_devices=pandas.Series(house.HeatGain['DeviceGain']),
                                    heatdemand_profile=pandas.Series(house.HeatDemand['Total']),
                                    heatdemand_profile_dhw_tap=pandas.Series(house.HeatDemand['DHWDemand']),
                                    airflow_profile_ventilation=pandas.Series(house.HeatGain['VentFlow']))
        self.households.append(household)

    @staticmethod
    def writeElectricVehicle(machine: DeviceElectricalVehicle) -> EVChargeSessions:
        sessions = [EVChargeSession(timedelta(minutes=start_time_minutes),
                                    timedelta(minutes=end_time_minutes),
                                    required_charge_watt_hour)
                    for start_time_minutes, end_time_minutes, required_charge_watt_hour
                    in zip(machine.StartTimes, machine.EndTimes, machine.EnergyLoss)]

        return EVChargeSessions(capacity_watt_hour=machine.BufferCapacity,
                                maximum_charging_power_watt=machine.Consumption,
                                sessions=sessions)

    def writeDeviceWashingMachine(self, machine: DeviceWashingMachine) -> WashingMachineExecutions:
        return WashingMachineExecutions(pandas.Series(machine.LongProfile),
                                        [(timedelta(minutes=start_time_minutes), timedelta(minutes=end_time_minutes))
                                         for start_time_minutes, end_time_minutes
                                         in zip(machine.StartTimes, machine.EndTimes)])

    def writeDeviceDishwasher(self, machine: DeviceDishwasher) -> DishwasherExecutions:
        return DishwasherExecutions(machine.LongProfile,
                                    [(timedelta(minutes=start_time_minutes), timedelta(minutes=end_time_minutes))
                                     for start_time_minutes, end_time_minutes
                                     in zip(machine.StartTimes, machine.EndTimes)])

    def writeDeviceThermostat(self, machine: Thermostat) -> list[ThermostatSetpoint]:
        return [ThermostatSetpoint(timedelta(minutes=start_time_minutes),
                                   setpoint)
                for start_time_minutes, setpoint in zip(machine.StartTimes, machine.Setpoints)]


class DEMKitWriter(AbstractWriter):
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
                for datum in data:
                    f.write(str(round(datum)) + '\n')
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

        #Write all flexible devices:
        self.writeElectricVehicle(house.Devices[ELECTRIC_VEHICLE_DEVICE], num)
        self.writeDeviceDishwasher(house.Devices[DISHWASHER_DEVICE], num)
        self.writeDeviceWashingMachine(house.Devices[WASHING_MACHINE_DEVICE], num)
        self.writeDeviceThermostat(house.HeatingDevices[THERMOSTAT_DEVICE], num)

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

    def writeElectricVehicle(self, machine: DeviceElectricalVehicle, hnum: int):
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

    def writeDeviceWashingMachine(self, machine: DeviceWashingMachine, hnum: int):
        if len(machine.StartTimes) > 0:
            text = str(hnum)+':'
            text += profilegentools.createStringList(machine.StartTimes, None, 60)
            self.writeCsvLine('WashingMachine_Starttimes.txt', hnum, text)

            text = str(hnum)+':'
            text += profilegentools.createStringList(machine.EndTimes, None, 60)
            self.writeCsvLine('WashingMachine_Endtimes.txt', hnum, text)

            text = str(hnum)+':'
            text += machine.LongProfile
            self.writeCsvLine('WashingMachine_Profile.txt', hnum, text)

    def writeDeviceDishwasher(self, machine: DeviceDishwasher, hnum: int):
        if len(machine.StartTimes) > 0:
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

    def writeDeviceThermostat(self, machine: Thermostat, hnum: int):
        text = str(hnum)+':'
        text += profilegentools.createStringList(machine.StartTimes, None, 60)
        self.writeCsvLine('Thermostat_Starttimes.txt', hnum, text)

        text = str(hnum)+':'
        text += profilegentools.createStringList(machine.Setpoints)
        self.writeCsvLine('Thermostat_Setpoints.txt', hnum, text)
