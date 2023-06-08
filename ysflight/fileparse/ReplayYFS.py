#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 29 17:09:44 2023

@author: Decaff42
"""

# Import standard modules
import os

# Import 3rd Party Modules
import numpy as np

# Import YSFlight Modules
from ..file import import_file
from ..units import convert_unit, determine_value_units
from ..simulation import YSFLIGHT_G, get_air_density, calculate_thrust


def ReplayYFS(filepath):
    """Import and parse a replay file.
    
    inputs
    filepath (str): os.path-like to where the replay file is.
    
    """
    # Only want to import a .yfs file. Flag other filetypes as invalid because 
    # they may not contain the expected data the user wants.
    if filepath.lower().endswith("yfs") is False:
        print("Error: [AircraftDat] expected a YFS file but was provided a {} file.".format(os.path.splitext(filepath)[-1]))
        raise TypeError
        
    # Import the file
    raw_yfs = import_file(filepath)
    
    # Initialize properties
    fieldname = ""
    events = list()
    airplanes = list()
    groundob = list()
    bulletrecords = list()
    killcredits = list()
    
    
    
class airplane:
    def __init__(self, lines):
        self.lines = lines
        
        
class event:
    def __init__(self, lines):
        self.lines = lines
        self.time = float(lines[0].split()[1])
        self.event_type = lines[0].split()[0]
        self.event_flag = lines[0].split()[-1]
        
        # Initialize properties for each type of event
        self.wind = None  # only WNDCHG
        self.message = None  # only TXTEVT
        self.visibility = None  # only VISCHG
        self.cloud_layers = None  # only VISCHG
        self.object_id = None  # PLRAIR, AIRCMD, WPNCFG
        self.weapons = None  # AIRCMD
        self.misc = None  # AIRCMD
        
    def parse(self):
        """Extract information from the raw data"""
        if self.event_type == "TXTEVT":
            self.message = self.lines[1][4:]
            
        elif self.event_type == "WNDCHG":
            parts = self.lines[1].split()[1:]
            self.wind = list()
            for i in parts:
                self.wind.append(float(i[:-3]))
                
        elif self.event_type == "VISCHG":
            # May have visibility or cloud later inputs
            self.cloud_layers = list()
            for line in self.lines[1:-1]:
                if "CLDLYR" in line:
                    self.cloud_layers.append(line.split()[1:])
                else:
                    self.visibility = float(line.split()[1][:-1])
            
            # Reset cloud layers if not used.
            if len(self.cloud_layers) == 0:
                self.cloud_layers = None
                
        elif self.event_type == "PLRAIR":
            self.object_id = int(self.lines[1].split()[1])
            
        elif self.event_type == "AIRCMD":
            self.object_id = int(self.lines[1].split()[1])
            
            self.commands = list()
            for line in self.lines[2:-1]:
                self.commands.append(line.split()[1:])
                
        elif self.event_type == "WPNCFG":
            self.object_id = int(self.lines[1].split()[1])
            self.weapons = list()
            self.misc = list()
            for line in self.lines:
                parts = line.split()
                if parts[0] == "CFG":
                    self.weapons.append(parts[1], float(parts[2]))
                elif parts[0] == "TXT":
                    self.misc.append(parts[1], float(parts[2]))
            
            # Reset unused properties
            if len(self.weapons) == 0:
                self.weapons = None
            if len(self.misc) == 0:
                self.misc = None
                    
                    
        
class text_event:
    def __init__(self, lines):
        self.lines = lines
        self.time = float(lines[0].split()[1])
        self.message = lines[1][4:]
        self.event_type = lines[0].split()[0]
        self.event_flag = lines[0].split()[-1]
        
class player_ob_change_event:
    def __init__(self, lines):
        self.lines = lines
        
        
        