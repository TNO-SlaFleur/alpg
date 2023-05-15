
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


import sys
import argparse
import importlib
from dataclasses import dataclass
from types import ModuleType
from typing import Optional

Config = ModuleType

sys.path.insert(0, 'configs')

@dataclass
class CommandLineOptions:
    cfgFile: Optional[str] = None
    cfgOutputDir: str = 'output/output/'
    forceDeletion: bool = False


def parse_cmdline_options() -> CommandLineOptions:
    parser = argparse.ArgumentParser(prog='Artifical Load Profile Generator (ALPG)')
    parser.add_argument('-c', '--config', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-f', '--force', action='store_true')
    args = parser.parse_args()

    return CommandLineOptions(cfgFile=args.config,
                              cfgOutputDir='output/' + args.output + '/',
                              forceDeletion=args.force)


def load_config(cmd_options: CommandLineOptions) -> Config:
    config_module = importlib.import_module(cmd_options.cfgFile)
    config = config_module.Config()
    config.config_file = cmd_options.cfgFile
    config.output_dir = cmd_options.cfgOutputDir
    config.writer = config.writer_class(config)
    config.householdList = [householdCnf.to_model(config) for householdCnf in config.householdConfigs]

    return config
