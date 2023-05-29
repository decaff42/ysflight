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

# Import 3rd Party Modules
import numpy as np

# Import YSFlight Modules
from ..file import import_file
from ..unts import convert_unit, determine_value_units
from ..simulation import YSFLIGHT_G, get_air_density, calculate_thrust


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
    excameras = list()
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

                # Handle dat variables that can be fully defined in a single line, but multiple 
                # definitions would be overwritten using the normal process because they use the 
                # same DAT variable.
                if datvar == "WPNSHAPE":
                    weaponshapes.append(WeaponShape(line))
                    continue  # No need for further analysis of this line
                elif datvar == "HRDPOINT":
                    hardpoints.append(HardPoints(line, len(hardpoints)))
                    continue  # No need for further analysis of this line
                elif datvar == "LOADWEPN":
                    loadweapons[parts[0]] = int(parts[1])
                    continue  # No need for further analysis of this line
                elif datvar == "SMOKECOL":
                    smokecols[int(parts[0])] = [int(i) for i in parts[1:]]
                    continue  # No need for further analysis of this line
                elif datvar == "EXCAMERA":
                    excameras.append(ExCamera(line))
                    continue  # No need for further analysis of this line
                        
                # Assign values for properties that take mulitple lines to fully define.
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

                else:
                    for idx, part in enumerate(parts):
                        value, units = determine_value_units(part)
                        if units not in ["STRING", "NUMBER", "BOOL"]:
                            parts[idx] = convert_unit(value, units)
                    dat[datvar] = parts
                
    
    # Package up into class
    DAT = AirplaneDat(dat, smokecols, turrets, weaponshapes, hardpoints, realprops, loadweapons, excameras)

    return DAT
    
    
    
    
class AirplaneDat:
    def __init__(self, dat, smokecols, turrets, weaponshapes, hardpoints, realprops, loadweapons, excameras):
        self.dat = dat
        self.smokecols = smokecols
        self.turrets = turrets
        self.weaponshapes = weaponshapes
        self.hardpoints = hardpoints
        self.realprops = realprops
        self.loadweapons = loadweapons
        self.excameras = excameras
        
        # Define class properties
        self.cl_zero = np.nan
        self.cl_land = np.nan
        self.cl_slope = np.nan
        
        self.cd_zero = np.nan
        self.cd_land = np.nan
        self.cd_const = np.nan
        self.cd_max = np.nan
        
        self.t_cruise = np.nan
        self.t_vmax = np.nan
        self.t_landing = np.nan
        
        self.cl_angles = list()
        self.cl_points = list()
        
        # Perform initial analysis
        self.apply_defaults()
        self.autocalc()
        
    def apply_defaults(self):
        """Ensure dat file has default values incorporated incase something requires them."""
        
        if "PROPELLR" in self.dat.keys() and "PROPEFCY" not in self.dat.keys():
            self.dat["PROPEFCY"] = 0.7
        if "PROPELLR" in self.dat.keys() and "PROPVMIN" not in self.dat.keys():
            self.dat["PROPVMIN"] = 30
        if "AIRCLASS" not in self.dat.keys():
            self.dat["AIRCLASS"] = "AIRPLANE"
        if "VGWSPED1" not in self.dat.keys():
            self.dat["VGWSPED1"] = convert_unit(determine_value_units("0.3MACH"))
        if "VGWSPED2" not in self.dat.keys():
            self.dat["VGWSPED2"] = convert_unit(determine_value_units("0.8MACH"))
        if "MAXCDAOA" not in self.dat.keys():
            self.dat["MAXCDAOA"] = convert_unit(determine_value_units("45deg"))
        if "FLATCLR1" not in self.dat.keys():
            self.dat["FLATCLR1"] = convert_unit(determine_value_units("0deg"))
        if "FLATCLR2" not in self.dat.keys():
            self.dat["FLATCLR2"] = convert_unit(determine_value_units("0deg"))
        if "CLDECAY1" not in self.dat.keys():
            self.dat["CLDECAY1"] = convert_unit(determine_value_units("0deg"))
        if "CLDECAY2" not in self.dat.keys():            self.dat["CLDECAY2"] = convert_unit(determine_value_units("0deg"))
        
        
    def autocalc(self):
        """Automatically calculate the properties from the dat file."""
        
        # Caluclate CL properties
        self.cl_zero = YSFLIGHT_G * (self.dat['WEIGHCLN'] + self.dat["WEIGHTFUEL"]) / (0.5 * get_air_density(self.dat['REFACRUS']) * self.dat['REFVCRUS']**2 * self.dat['WINGAREA'])
        self.cl_land = YSFLIGHT_G * (self.dat['WEIGHCLN'] + self.dat['WEIGFUEL']) / (0.5 * get_air_density(0) * self.dat['REFVCRUS']**2 * self.dat['WINGAREA']) * (1 / (1 + self.dat['CLBYFLAP'])) * (1 / (1 + self.dat['CLVARGEO']))
        self.cl_slope = (self.cl_land - self.cl_zero) / (self.dat['REFAOALD'])
        
        # Calculate Thrust values
        self.t_cruise = calculate_thrust(self.dat['REFACRUS'], self.dat['REFVCRUS'], self.dat['REFTCRUS'], False, self.dat, self.realprops)
        self.t_vmax = calculate_thrust(self.dat['REFACRUS'], self.dat['MAXSPEED'], 1.0, True, self.dat, self.realprops)
        self.t_landing = calculate_thrust(0, self.dat['REFVLAND'], self.dat['REFTLAND'], False, self.dat, self.realprops)
        
        # Calculate drag properties
        self.cd_zero = self.t_cruise / (0.5 * get_air_density(self.dat["REFACRUS"]) * self.dat["REFVCRUS"]**2 * self.dat["WINGAREA"])
        self.cd_land = (self.t_landing / (0.5 * get_air_density(0) * self.dat["REFVLAND"]**2 * self.dat["WINGAREA"])) * (1 / (1 + self.dat["CLBYFLAP"])) * (1 / (1 + self.dat["CLVARGEO"])) * (1 / (1 + self.dat["CDBYGEAR"]))
        self.cd_const = (self.cd_land - self.cd_zero) / self.dat["REFAOALD"]**2
        self.cd_max = self.t_vmax / (0.5 * get_air_density(self.dat["REFACRUS"]) * self.dat["MAXSPEED"]**2 * self.dat["WINGAREA"])
        
        # Define the lift coefficient curve points
        self.cl_angles.append(self.dat['CRITAOAM'] - self.dat['FLATCLR2'] - self.dat['CLDECAY2'])
        self.cl_angles.append(self.dat['CRITAOAM'] - self.dat['FLATCLR2'])
        self.cl_angles.append(self.dat['CRITAOAM'])
        self.cl_angles.append(self.dat['CRITAOAP'])
        self.cl_angles.append(self.dat['CRITAOAP'] + self.dat['FLATCLR1'])
        self.cl_angles.append(self.dat['CRITAOAP'] + self.dat['FLATCLR1'] + self.dat['CLDECAY1'])
        
        self.cl_points.append(0)
        self.cl_points.append(self.cl_zero + self.dat["CRITAOAM"] * self.cl_slope)
        self.cl_points.append(self.cl_zero + self.dat["CRITAOAM"] * self.cl_slope)
        self.cl_points.append(self.cl_zero + self.dat["CRITAOAM"] * self.cl_slope)
        self.cl_points.append(self.cl_zero + self.dat["CRITAOAM"] * self.cl_slope)
        self.cl_points.append(0)
        
    def calc_cl(self, aoa, flap_pct=0, vgw_pct=1):
        """calculate a the lift coefficient at a provided angle of attack.
        
        inputs:
        aoa (float, int): the angle of attack of the aircraft as a radian value.
        flap_pct (float, int): the decimal percent that the flaps are deployed (0=clean/1=down)
        vgw_pct (float, int): the decimal percent that the VGW are swept (0=forward/1=swept)
        
        outputs:
        cl (float): the lift coefficient at the specified angle of attack.
        """
        
        if isinstance(aoa, (float, int)) is False:
            print("Error: [AirplaneDat.calc_cl] was expecting angle of attack input to be float or int. Got {}".format(type(aoa)))
            raise TypeError
            
        # Modify the lift coefficient magnitude as required for flap and vgw
        cl_points = [x + flap_pct * self.dat['CLBYFLAP'] for x in self.cl_points]
        cl_points = [x - vgw_pct * self.dat['CLVARGEO'] for x in cl_points]
                
        # The lift coefficient points and angles can be used with linear interpolation to find the 
        # lift coefficient at an angle of attack. Because the min and max y values for the lift coefficient 
        # is zero, then any aoa values beyond the valid range of aoa values will also be zero which
        # is desired.
        return np.interp(aoa, self.cl_angles, cl_points)
            
    def calc_cd(self, aoa, flap_pct=0, vgw_pct=0, spoiler_pct=0, gear_pct=0, airspeed=0):
        """Calculate the drag coefficicent of the aircraft at the provided angle of attack.
        
        inputs:
        aoa (float, int): the angle of attack of the aircraft as a radian value.
        flap_pct (float, int): the decimal percent that the flaps are deployed (0=clean/1=down)
        vgw_pct (float, int): the decimal percent that the VGW are swept (0=forward/1=swept)
        spoiler_pct (float, int): the decimal percent that the spoiler is extended (0=retracted/1=extended)
        gear_pct (float, int): the decimal percent that the landing gear is extended (0=retracted/1=extended)
        airspeed (float, int): the airspeed the aircraft is traveling.
        
        outputs:
        cd (float): the drag coefficient at the specified angle of attack.
        """
        
        if isinstance(aoa, (float, int)) is False:
            print("Error: [AirplaneDat.calc_cd] was expecting angle of attack input to be float or int. Got {}".format(type(aoa)))
            raise TypeError
        
        cd = self.cd_zero + self.cd_const * aoa**2
        
        # Acount for transonic drag
        if airspeed > self.dat['CRITSPEED'] or (self.cd_max < self.cd_zero and self.dat['CRITSPED'] < self.dat['MAXSPEED']):
            cd = cd + (self.cd_max - self.cd_zero) * (airspeed - self.dat['CRITSPED']) / (self.dat['MAXSPEED'] - self.dat['CRITSPED'])
        
        # Acount for effectors
        cd = cd * (1 + self.dat['CDSPOILR'] * spoiler_pct) * (1 + self.dat['CDVARGEO'] * vgw_pct) * (1 + self.dat['CDBYFLAP'] * gear_pct) * (1 + self.dat['CDBYGEAR'] * gear_pct)
        
        return cd
    
    def calc_lift_force(self, aoa, flap_pct, vgw_pct, velocity, altitude):
        """Calculate the lift force at the specified angle of attack.
        
        inputs
        aoa (int, float): the angle of attack in radians
        flap_pct (float, int): the decimal percent that the flaps are deployed (0=clean/1=down)
        vgw_pct (float, int): the decimal percent that the VGW are swept (0=forward/1=swept)
        velocity (float, int): the aircraft's speed in meters per second
        altitude (float, int): the aircraft's altitude in meters
        
        outputs
        lift (float): the lift force in Newtons
        """
        
        density = get_air_density(altitude)
        cl = self.calc_cl(aoa, flap_pct, vgw_pct)
        
        return 0.5 * density * velocity**2 * self.dat['WINGAREA'] * cl
    
    
    def calc_drag_force(self, aoa, velocity, altitude, flap_pct=0, vgw_pct=0, spoiler_pct=0, gear_pct=0):
        """Calculate the drag force on the aircraft at the specified conditions
        
        inputs:
        aoa (float, int): the angle of attack of the aircraft as a radian value.
        flap_pct (float, int): the decimal percent that the flaps are deployed (0=clean/1=down)
        vgw_pct (float, int): the decimal percent that the VGW are swept (0=forward/1=swept)
        spoiler_pct (float, int): the decimal percent that the spoiler is extended (0=retracted/1=extended)
        gear_pct (float, int): the decimal percent that the landing gear is extended (0=retracted/1=extended)
        velocity (float, int): the airspeed the aircraft is traveling.
        altitude (float, int): the aircraft's altitude in meters
        
        outputs:
        drag (float): the drag force in Newtons
        """
        
        density = get_air_density(altitude)
        cd = self.calc_cd(aoa, flap_pct, vgw_pct, spoiler_pct, gear_pct, velocity)
        
        return 0.5 * density * velocity**2 * self.dat['WINGAREA'] * cd
    
    
    def calc_required_throttle(self, altitude, velocity, flap_pct, vgw_pct, spoiler_pct, gear_pct, g = 1):
        """Calculate the required throttle for straight and level flight (g=1) unless overridden with a g loading.
        
        inputs:
        flap_pct (float, int): the decimal percent that the flaps are deployed (0=clean/1=down)
        vgw_pct (float, int): the decimal percent that the VGW are swept (0=forward/1=swept)
        spoiler_pct (float, int): the decimal percent that the spoiler is extended (0=retracted/1=extended)
        gear_pct (float, int): the decimal percent that the landing gear is extended (0=retracted/1=extended)
        velocity (float, int): the airspeed the aircraft is traveling.
        altitude (float, int): the aircraft's altitude in meters
        g (float, int): the g loading of the aircraft.
        
        outputs:
        throttle_setting (float): throttle position
        afterburner (Boolean): indication if afterburner is required.
        """
        
        # TODO: Finish this section
        
    def assign_weapon_config_event(self, wonconfig):
        """Assign weapons to hardpoints based on the YSF file weapon config event block.
        
        inputs:
        wpnconfig (dict): keys = weapon types, value = count of weapons
        """
        
        # TODO: Finish this section.

        
    
        
          
                    
class ExCamera:
    def __init__(self, line):
        self.line = line
        self.location = line.split()[-1]  # INSIDE, OUTSIDE, CABIN
        self.name = line.split('"')[1]
        self.position = [convert_unit(determine_value_units(pos)) for pos in line.split()[2:5]]
        self.orientation = [convert_unit(determine_value_units(angle)) for angle in line.split()[5:8]]
        
                    
class HardPoints:
    def __init__(self, line, count):
        self.line = line
        self.internal = False
        self.position = [0, 0, 0]  # Default position
        self.weapon_count = dict()
        for i in YSFLIGHT_WEAPON_NAMES:
            self.weapon_count[i] = 0
            
        self.current_load = (None, None)  # indication of type and quantity of weapon on hardpoint.
            
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
