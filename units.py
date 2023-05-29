#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 13 18:18:18 2023

"""

# Import standard modules
import math

# Import 3rd Party Modules


# Import YSFlight module
from ..simulation.simulation import YSFLIGHT_G

# Define valid units for YSFLIGHT and organize for different types of units.
YSFLIGHT_SPEED_UNITS = ["MACH", "M/S", "KT", "KM/H"]
YSFLIGHT_ANGLE_UNITS = ["RAD", "DEG"]
YSFLIGHT_AREA_UNITS = ["IN^2", "M^2"]
YSFLIGHT_DISTANCE_UNITS = ["NM", "KM", "CM", "M", "FT", "IN"]
YSFLIGHT_FORCE_UNITS = ["T", "LB", "KG", "N"]
YSFLIGHT_POWER_UNITS = ["J/S", "HP"]
YSFLIGHT_TIME_UNITS = ["SEC"]
YSFLIGHT_WEIGHT_UNITS = ["T", "KG", "LB"]

# Merge and sort valid units into single list.
VALID_YSFLIGHT_UNITS = list(set(YSFLIGHT_SPEED_UNITS + YSFLIGHT_ANGLE_UNITS + YSFLIGHT_AREA_UNITS + YSFLIGHT_DISTANCE_UNITS + YSFLIGHT_FORCE_UNITS + YSFLIGHT_POWER_UNITS + YSFLIGHT_TIME_UNITS + YSFLIGHT_WEIGHT_UNITS))
VALID_YSFLIGHT_UNITS.sort(key=len, reverse=True)

# Define conversion factors
YSFLIGHT_UNIT_CONVERSION = dict()
YSFLIGHT_UNIT_CONVERSION["MACH"] = 340
YSFLIGHT_UNIT_CONVERSION["M/S"] = 1
YSFLIGHT_UNIT_CONVERSION["KT"] = 1852/3600
YSFLIGHT_UNIT_CONVERSION["KM/H"] = 1000 / 3600
YSFLIGHT_UNIT_CONVERSION["RAD"] = 1
YSFLIGHT_UNIT_CONVERSION["DEG"] = math.pi / 180
YSFLIGHT_UNIT_CONVERSION["IN^2"] = 0.00064516
YSFLIGHT_UNIT_CONVERSION["M^2"] = 1
YSFLIGHT_UNIT_CONVERSION["NM"] = 1852
YSFLIGHT_UNIT_CONVERSION["KM"] = 1000
YSFLIGHT_UNIT_CONVERSION["CM"] = 100
YSFLIGHT_UNIT_CONVERSION["M"] = 1
YSFLIGHT_UNIT_CONVERSION["FT"] = 0.3048
YSFLIGHT_UNIT_CONVERSION["IN"] = 0.0254
YSFLIGHT_UNIT_CONVERSION["T"] = 2000 * YSFLIGHT_G
YSFLIGHT_UNIT_CONVERSION["LB"] = YSFLIGHT_G * 0.45397
YSFLIGHT_UNIT_CONVERSION["KG"] = YSFLIGHT_G
YSFLIGHT_UNIT_CONVERSION["N"] = 1
YSFLIGHT_UNIT_CONVERSION["J/S"] = 1
YSFLIGHT_UNIT_CONVERSION["HP"] = 740
YSFLIGHT_UNIT_CONVERSION["SEC"] = 1


def determine_value_units(raw_value):
    """Extract the value and unit from a raw value provided from a YSFlight File. Integrated 
    determine_value and determine_units into a single function to save processing time.
    
    inputs:
    raw_value (str): a raw value from a dat file
    
    outputs:
    value (float, bool, str): the extracted raw value
    unit (str): A string indicating the unit type or the type of variable.
    """
    
    if isinstance(raw_value, str) is False:
        print("Error: [determine_value_units] was expecting a string input. Got a {}".format(type(raw_value)))
        raise TypeError
        
    # If this is just a straight number, end early
    try:
        value = float(raw_value)
        return value, "NUMBER"
    except ValueError:
        # We need to determine the units
        pass
    
    # Handle Boolean
    if raw_value == "TRUE":
        return True, "BOOL"
    elif raw_value == "FALSE":
        return False, "BOOL"
    
    # Split the end unit from the value
    value = raw_value.upper()
    for unit in VALID_YSFLIGHT_UNITS:
        if value.endswith(unit):
            return float(value.split(unit)[0]), unit
    
    # If the input value is something else and a string, then it is a string input
    return raw_value, "STRING"


def determine_value(raw_value):
    """Get the value from a raw input of a YSFlight file.
    
    inputs:
    raw_value (str): a raw value from a dat file
    
    outputs:
    value (float, bool, str): the extracted raw value
    """
    
    if isinstance(raw_value, str) is False:
        print("Error: [determine_value] was expecting a string input. Got a {}".format(type(raw_value)))
        raise TypeError
    
    # If this is just a straight number, end early
    try:
        value = float(raw_value)
        return value
    except ValueError:
        pass
    
    # Handle Boolean
    if raw_value == "TRUE":
        return True
    elif raw_value == "FALSE":
        return False
    
    # Split the end unit from the value
    value = raw_value.upper()
    for unit in VALID_YSFLIGHT_UNITS:
        if value.endswith(unit):
            return float(value.split(unit)[0])
    
    # If we get here, then the code has found an unknown unit type has been found
    print("Caution: [determine_value] has found an unknown unit from: {}".format(value))
    raise ValueError

def determine_units(raw_value):
    """Often times YSFlight units are defined in a dat file without a space next to the value and so
    we need a way to automatically detect what units are being used.
    
    inputs: 
    raw_value (str): the raw input from a dat file
    
    output:
    unit (str, None): the unit associated with the value
    """
    
    if isinstance(raw_value, str) is False:
        print("Error: [determine_units] was expecting a string input. Got a {}".format(type(raw_value)))
        raise TypeError
            
    # Handle case where we don't have any units and dealing with a float
    try:
        raw_value = float(raw_value)
        return "NUMBER"
    except ValueError:
        # We need to determine the units
        pass
    
    # Because the VALID_YSFLIGHT_UNITS is sorted in reverse order by length of unit, we can avoid meters 
    # and tons being confused with another unit by iterating over the list in its current order.
    value = raw_value.upper()  # Get rid of case-sensitivity and match VALID_YSFLIGHT_UNITS
    for unit in VALID_YSFLIGHT_UNITS:
        if value.endswith(unit):
            return unit
    
    # If we get here, then the code has found an unknown unit type has been found
    print("Caution: [determine_units] has found an unknown unit from: {}".format(value))
    raise ValueError
    

def convert_unit(value: (int, float, str), unit: str) -> (int, float):
    """Convert the provided value into default YSFlight units.
    
    inputs:
    value (float, int, str): The value provided of the originally defined units
    unit (str): The units used to originally define a value
    unit_type (str): The unit type we need to convert
    
    outputs:
    result (float, int): the converted value into default ysflight units
    """
    
    # Validate inputs
    if isinstance(unit, str) is False:
        print("Error: [convert_unit] Expected a string for the units, but recieved {}.".format(type(unit)))
        raise TypeError
    
    if isinstance(value, (int, float, str)) is False:
        print("Error: [convert_unit] Expected a string, int or float for the units, but recieved {}.".format(type(value)))
        raise TypeError
    elif isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            print("Error: [convert_unit] could not convert the provided value ({}) to a numeric value.".format(value))
    
    
    # Perform calculation
    if isinstance(value, str):
        value = float(value)
    factor = YSFLIGHT_UNIT_CONVERSION[unit]
    return value * factor
    
    
    
