#!/usr/bin/python3

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


import os
import random
from types import ModuleType

import configLoader
import neighbourhood
from writer import AbstractWriter, PandasWriter, DEMKitWriter

Writer = ModuleType


def prepare_output_directory(cmd_options: configLoader.CommandLineOptions) -> None:
    # Check if the output dir exists, otherwise make it
    os.makedirs(os.path.dirname(cmd_options.cfgOutputDir), exist_ok=True)

    if os.listdir(cmd_options.cfgOutputDir):
        # Empty the directory
        if cmd_options.forceDeletion:
            for tf in os.listdir(cmd_options.cfgOutputDir):
                fp = os.path.join(cmd_options.cfgOutputDir, tf)
                try:
                    if os.path.isfile(fp):
                        os.unlink(fp)
                except Exception as e:
                    print(e, flush=True)
        else:
            print("Output directory is not empty! Provide the --force flag to delete the contents", flush=True)
            exit()


def write_output(config: configLoader.Config) -> AbstractWriter:
    # Create empty files
    config.writer.createEmptyFiles()

    hnum = 0
    numOfHouseholds = len(config.householdList)

    config.writer.writeNeighbourhood(hnum)
    for household in config.householdList:
        print("Writing Household "+str(hnum+1)+" of "+str(numOfHouseholds), flush=True)
        config.writer.writeHousehold(config, household, hnum)
        hnum = hnum + 1

    return config.writer


def simulate(config: configLoader.Config):
    # Randomize using the seed
    random.seed(config.seed)

    neighbourhood.neighbourhood(config)

    hnum = 0
    numOfHouseholds = len(config.householdList)

    for household in config.householdList:
        print("Simulating household " + str(hnum + 1) + " of " + str(numOfHouseholds), flush=True)
        household.simulate()

        # Warning: On my PC the random number is still the same at this point, but after calling scaleProfile() it isn't!!!
        household.scaleProfile()
        household.reactivePowerProfile()
        household.thermalGainProfile()
        hnum = hnum + 1


def main():
    print("Profilegenerator 1.3.2\n", flush=True)
    print("Copyright (C) 2023 University of Twente", flush=True)
    print("This program comes with ABSOLUTELY NO WARRANTY.", flush=True)
    print("This is free software, and you are welcome to redistribute it under certain conditions.", flush=True)
    print("See the acompanying license for more information.\n", flush=True)

    cmd_options = configLoader.parse_cmdline_options()
    prepare_output_directory(cmd_options)
    config = configLoader.load_config(cmd_options)

    print('Loading config: '+cmd_options.cfgFile, flush=True)
    print("The current config will create and simulate "+str(len(config.householdList))+" households", flush=True)
    print("Results will be written into: "+cmd_options.cfgOutputDir+"\n", flush=True)
    print("NOTE: Simulation may take a (long) while...\n", flush=True)

    # Check the config:
    if config.penetrationEV + config.penetrationPHEV > 100:
        print("Error, the combined penetration of EV and PHEV exceed 100!", flush=True)
        exit()
    if config.penetrationPV < config.penetrationBattery:
        print("Error, the penetration of PV must be equal or higher than PV!", flush=True)
        exit()
    if config.penetrationHeatPump + config.penetrationCHP > 100:
        print("Error, the combined penetration of heatpumps and CHPs exceed 100!", flush=True)
        exit()

    simulate(config)
    write_output(config)


if __name__ == '__main__':
    main()
