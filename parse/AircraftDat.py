#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

A python module file to handle the processing of an aircraft dat file

"""

# Define Constants
YSFLIGHT_DAT_DISTANCE_VARS = ["ISPNLPOS", "LEFTGEAR", "RIGHGEAR", "WHELGEAR", "ARRESTER", "MACHNGUN", 
                              "GUNDIREC", "SMOKEGEN", "VAPORPO0", "VAPORPO1", "HTRADIUS", "POSITION", 
                              "HRDPOINT", "REFACRUS", "REFLNRWY", "COCKPITP", "POSITION", "MACHNGN2", 
                              "MACHNGN3", "MACHNGN4", "MACHNGN5", "MACHNGN6", "MACHNGN7", "MACHNGN8", 
                              "TRSTDIR0", "TRSTDIR1", "LOOKOFST", "FLAREPOS", "BOMBSLOT", "AAMSLOT_", 
                              "AGMSLOT_", "RKTSLOT_"]
YSFLIGHT_DAT_SPEED_VARS = ["PROPVMIN", "CRITSPED", "MAXSPEED", "MANESPD1", "MANESPD2", "INITSPED", 
                           "REFVCRUS", "REFVLAND", "PSTMSPD1", "PSTMSPD2", "VGWSPED1", "VGWSPED2"]
YSFLIGHT_DAT_FORCE_VARS = ["THRAFTBN", "THRMILIT"]
YSFLIGHT_DAT_WEIGHT_VARS = ["WEIGHCLN", "WEIGFUEL", "WEIGLOAD", "FUELABRN", "FUELMILI", "SMOKEOIL", 
                            "INITLOAD"]
YSFLIGHT_DAT_AREA_VARS = ["WINGAREA"]
YSFLIGHT_DAT_ANGLE_VARS = ["CRITAOAP", "CRITAOAM", "MXIPTAOA", "MXIPTSSA", "MXIPTROL", "MAXCDAOA", 
                           "FLATCLR1", "FLATCLR2", "CLDECAY1", "CLDECAY2", "PSTMPTCH", "PSTMYAW_", 
                           "PSTMROLL", "REFAOALD", "ATTITUDE", "COCKPITA", "ISPNLATT"]
YSFLIGHT_DAT_TURRET_VARS = ["TURRETPO", "TURRETPT", "TURRETHD", "TURRETAM", "TURRETIV", "TURRETNM", 
                            "TURRETAR", "TURRETCT", "TURRETRG", "TURRETGD"]
YSFLIGHT_DAT_BOOL_VARS = ["AFTBURNR", "HASSPOIL", "RETRGEAR", "VARGEOMW", "CTLLDGEA", "STALHORN", "GEARHORN", 
                          "CTLBRAKE", "CTLABRNR", "TRSTVCTR", "CTLATVGW", "VRGMNOSE", "GUNSIGHT", "CKPITIST", 
                          "CKPITHUD", "ISPNLHUD", "BOMINBAY", "LMTBYHDP", "AAMVISIB", "AGMVISIB", "BOMVISIB", 
                          "RKTVISIB"]
YSFLIGHT_DAT_NONDIM_VARS = ["STRENGTH", "RADARCRS", "FLAPPOSI", "CLBYFLAP", "CDBYFLAP", "CDBYGEAR", "CDSPOILR", 
                            "TIREFRIC", "PSTMPWR1", "PSTMPWR2", "CPITMANE", "CPITSTAB", "CYAWMANE", "CYAWSTAB", 
                            "CROLLMAN", "CTLSPOIL", "CTLTHROT", "CTLIFLAP", "PROPEFCY", "THRSTREV", "NREALPRP", 
                            "GUNPOWER", "ISPNLSCL", "SMOKECOL", "NMTURRET", "CLVARGEO", "CDVARGEO", "CTLINVGW", 
                            "SCRNCNTR", "INITZOOM", "INITIGUN", "BMBAYRCS", "INITAAAM", "INITHDBM", "MAXNMFLR", 
                            "INITAAMM", "MAXNAAMM", "INITB250", "MAXNB250", "INITRCKT", "INITIAGM", "MAXNBOMB", 
                            "MAXNMAGM", "MAXNMAAM", "MAXNMRKT", "INITIAAM", "MAXNMGUN", "NMACHNGN"]

YSFLIGHT_WEAPON_NAMES = ["B500", "B500HD", "B250", "RKT", "FUEL", "AGM65", "AIM9X", "AIM9", "AIM120"]

# Import standard modules
import os

# Import YSFlight Modules
from ..file import import_file
from ..unts import convert_unit, determine_units, determine_value_units


def AircraftDat(filepath):
    """Parse an aircraft dat from a filepath.
    
    inputs:
    filepath (str): an os.path-like string to a dat file.
    
    output:
    airplane (AirplaneDat): an AirplaneDat class instance
    """
    
    # Only want to import a .dat file. Flag other filetypes as invalid because 
    # they may not contain the expected data the user wants.
    if filepath.lower().endswith("dat") is False:
        print("Error: [AircraftDat] expected a DAT file but was provided a {} file.".format(os.path.splitext(filepath)[-1]))
        raise TypeError
    
    # Import the file
    raw_dat = import_file(filepath)
    
    # Extract information from the DAT.
    dat = dict()
    smokecols = dict()
    turrets = dict()
    weaponshapes = list()
    hardpoints = list()
    realprops = dict()
    loadweapons = dict()
    for key in YSFLIGHT_WEAPON_NAMES:
        loadweapons[key] = 0
    
    for line in raw_dat:
        if len(line) > 8 and line.startswith("REM") is False:
            if " " not in line[:8]:
                datvar = line[:8]
                
                # Split the line by the inline comment '#' and then take the parts (ignoring the dat 
                # variable) and process the units.
                parts = line.split('#')[0].split()[1:]
                
                # Evaluate if we need to prep the turret, and realprop dicts to contain all the parts of the DAT
                if datvar == "NMTURRET":
                    for i in range(int(parts[0])):
                        turrets[i] = dict()               
                elif datvar == "NREALPRP":
                    for i in range(int(parts[0])):
                        realprops[i] = dict()
                elif datvar == "WPNSHAPE":
                    weaponshapes.append(WeaponShape(line))
                    continue  # No need for further analysis
                elif datvar == "HRDPOINT":
                    hardpoints.append(HardPoints(line))
                    continue  # No need for further analysis
                        
                # Assign dict/list values for different multiply defined DATVARs
                if datvar in YSFLIGHT_DAT_TURRET_VARS:
                    turret_id = int(parts[0])
                    parts = parts[1:]   # Ignore the turret ID
                    
                    # Handle the boolean (present/not present) turret targetting
                    if datvar in ["TURRETAR", "TURRETGD"]:
                        turrets[turret_id][datvar] = True
                    else:
                        for idx, part in enumerate(parts): 
                            value, units = determine_value_units(part)
                            if units not in ["STRING", "NUMBER", "BOOL"]:    
                                parts[idx] = convert_unit(value, units)
                        turrets[turret_id][datvar] = parts
                elif datvar == "REALPROP":
                    engine_id = int(parts[0])
                    parts = parts[1:]
                    
                    for idx, part in enumerate(parts):
                        value, units = determine_value_units(part)
                        if units not in ["STRING", "NUMBER", "BOOL"]:
                            parts[idx] = convert_unit(value, units)
                            
                    realprops[engine_id][datvar] = parts
                elif datvar == "LOADWEPN":
                    loadweapons[parts[0]] = int(parts[1])
                elif datvar == "SMOKECOL":
                    smokecols[int(parts[0])] = [int(i) for i in parts[1:]]
                else:
                    for idx, part in enumerate(parts):
                        value, units = determine_value_units(part)
                        if units not in ["STRING", "NUMBER", "BOOL"]:
                            parts[idx] = convert_unit(value, units)
                            
                    dat[datvar] = parts
                
    

    
    
    
    
class AirplaneDat:
    def __init__(self, raw_dat):
        self.raw_dat = raw_dat    
        self.multi_datvar = ["HRDPOINT", "WPNSHAPE", "LOADWEPN", "EXCAMERA", "SMOKEGEN", "TURRETPO",
                             "TURRETPT", "TURRETHD", "TURRETAM", "TURRETIV", "TURRETNM", "TURRETAR", 
                             "TURRETCT", "TURRETRG"]
        
        self.parse_dat()
        
        
    def parse_dat(self):
        """Parse in the dat file properties and then perform auto-calculate 
        calculations for lift and drag.
        
        NOTE: REALPROP, SMOKE, TURRETS, EXCAMERAS, HARDPOINTs, and WEAPONSHAPES 
        can all have duplicate calls in the DAT File and will need to be specially 
        handled.
        """
        
        
        # Extract the DAT Variables through automatic parsing for stand-alone dat variables
        dat = dict()
        for line in self.raw_dat:
            if len(line) > 8 and line.startswith("REM") is False:
                if " " not in line[:8]:
                    dat[line[:8]] = line[9:].split('#')[0].strip()
        
        # Extract Turrent information
        turrets = dict()
        if "NMTURRET" in dat.keys():
            # Need to import turrets.
            for i in range(int(dat["NMTURRET"])):
                turrets[i] = Turret(i)
            
            lines = [x for x in self.raw_data if x.startswith("TURRET")]
            for line in lines:
                data = line.split('#')[0].strip().split()[1:]
                turrets[int(data[0])].assign(data[2:], data[1])
                
                
        # Extract hardpoint information
        hardpoints = list()
        if "HRDPOINT" in dat.keys():
            lines = [x for x in self.raw_data if x.startswith("HRDPOINT")]
            for line in lines:
                if len(line) > 8 and line.startswith("REM") is False:
                    if line[:8] == "HRDPOINT":
                        hardpoints.append(HardPoints(line.split('#')[0]))
                        
        # Extract Weaponshape information
        weaponshapes = list()
        if "WPNSHAPE" in dat.keys():
            lines = [x for x in self.raw_data if x.startswith("WPNSHAPE")]
        
        # Extract Real Propeller information
        real_props = dict()
        if "NREALPRP" in dat.keys():
            for i in range(int(dat["NREALPRP"])):
                real_props[i] = RealProp(i)
            
            lines = [x for x in self.raw_data if x.startswith("REALPROP")]
            for line in lines:
                parts = line.split('#')[0].split()[1:]
                real_props[int(parts[0])].assign(parts[2:], parts[1])
                
        # Store extracted data
        self.dat = dat
        self.turrets = turrets
        self.hardpoints = hardpoints
        self.weaponshapes = weaponshapes
        self.realprops = real_props
            
            
    def autocalc(self):
        """Automatically calculate the properties from the dat file."""
                               
                    
                    
class HardPoints:
    def __init__(self, line):
        self.line = line
        self.internal = False
        self.position = [0, 0, 0]  # Default position
        self.weapon_count = dict()
        for i in YSFLIGHT_WEAPON_NAMES:
            self.weapon_count[i] = 0
            
        self.parse()        
        
    def parse(self):
        parts = self.line.split()
        self.position = [convert_unit(determine_value_units(pos)) for pos in parts[1:4]]
        
        if "$INTERNAL" in parts:
            self.internal = True
        
        for element in parts[4:]:
            if element.startswith(YSFLIGHT_WEAPON_NAMES):
                element.replace("&", "*")
                values = element.split("*")
                if len(values) == 1:
                    self.weapon_count[values[0]] = 1
                else:
                    self.weapon_count[values[0]] = float(values[1])
                
class WeaponShape:
    def __init__(self, line):
        self.line = line
        
        parts = line.split()
        self.weapon = parts[1]
        self.phase = parts[2]
        self.parts[3]
        
        
class RealProp:
    def __init__(self, engine_id, properties):
        self.engine_id = engine_id                    
        for k, v in properties.items():
            setattr(self, k, v)
                    

class Turret:
    def __init__(self, id_number, properties):
        self.turret_id = id_number
        for k, v in properties.items():
            setattr(self, k, v)
