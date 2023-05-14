#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Perform calculations that rely on YSFlight source code calculations

"""

# Import standard modules

# Import 3rd Party Modules
import numpy as np

# Import ysflight modules


# Define constants

YSFLIGHT_G = 9.807


def calculate_thrust(altitude: (float, int), airspeed: (float, int), throttle: (float, int), afterburner: bool, airplane_dat):
    """Calculate the thrust of an aircraft at a specific altitude and air speed.
    
    inputs:
    altitude (float, int): the altitude in meters 
    airspeed (float, int): the airspeed in m/s
    afterburner (bool): if the afterburner is used or not
    airplane_dat (N/A): The DAT Properties of an airplane.
    
    output:
    thrust (float, int): thrust in newtons of the aircraft
    """
    
    # Validate Inputs
    func_input = [altitude, airspeed, throttle, afterburner]
    func_pos = ["altitude", "airspeed", "throttle", "afterburner"]
    good_types = [(float, int), (float, int), (float, int), bool]
    for (i, p, t) in zip(func_input, func_pos, good_types):
        if isinstance(i, t) is False:
            print("Error: [calculate_thrust] Invalid input for {}. Expected {} and got {}".format(p, t, type(i)))
            raise TypeError
        
    if altitude < 0:
        print("Error: [calculate_thrust] Invalid altitude input. Expecting greater than zero but got: {}".format(altitude))
        raise ValueError
        
    # TODO: Only care about an invalid airspeed input if we are using a propeller.
    # Consider not checking this if we have a jet engine?
    if airspeed < 0:
        print("Error: [calculate_thrust] Invalid airspeed input. Expecting greater than zero but got: {}".format(altitude))
        raise ValueError
        
    # Determine which type of analysis to perform based on the type of engine

    

def calculate_drag(altitude, airspeed, aoa, airplane_dat):
    """Calculate the drag on the aircraft.
    
    inputs:
    altitude (float, int): the altitude in meters 
    airspeed (float, int): the airspeed in m/s
    aoa (float, int): The angle of attack
    airplane_dat (N/A): The DAT Properties of an airplane.
    
    output:
    drag (float): Drag Force in Newtons at the condition provided.
    """
    
    
    # Validate Inputs
    if altitude < 0:
        print("Error: [calculate_drag] Invalid altitude input. Expecting greater than zero but got: {}".format(altitude))
        raise ValueError
        
    if altitude < 0:
        print("Error: [calculate_drag] Invalid airspeed input. Expecting greater than zero but got: {}".format(altitude))
        raise ValueError
        

def get_air_density(altitude):
    """Converts an ailtitude into the equivalent air density.
    
    inputs:
    altitude (int, float): aircraft altitude in meters
    
    outputs:
    density (float): air density at input altitude.
    """
    
    # Ensure that we have good inputs
    if isinstance(altitude, (float, int)) is False:
        print("Error: [get_air_density] was expecting altitude input to be float or int. Got {}".format(type(altitude)))
        raise TypeError
    
    ref_altitude = [0, 4000, 8000, 12000, 16000, 20000]
    ref_density = [1.224991, 0.819122, 0.529999, 0.299988, 0.153000, 0.084991]
    
    if altitude < 0:
        return 0
    elif altitude > 32000:
        return 0
    elif altitude > 20000:
        return ref_density[-1]
    else:
        return np.interp(altitude, ref_altitude, ref_density)
    
    
def calculate_jet_efficiency(altitude):
    """Determine thrust cutback factor
    
    inputs:
    altitude (int, float): aircraft altitude in meters
    
    outputs:
    efficiency (float): jet engine thrust efficiency at specified altitude."""
    
    # Ensure that we have good inputs
    if isinstance(altitude, (float, int)) is False:
        print("Error: [calculate_jet_efficiency] was expecting altitude input to be float or int. Got {}".format(type(altitude)))
        raise TypeError
    
    ref_alt = [0, 4000, 12000, 16000, 20000, 20000.00001, 36000, 36.000001]
    ref_n = [1, 1, 0.6, 0.3, 0.0, 0.08, 0.08, 0]

    return np.interp(altitude, ref_alt, ref_n)


def calculate_mach(altitude, velocity):
    """Calculate the mach number
    
    inputs:
    altitude (int, float): aircraft altitude in meters
    velocity (int, float): aircraft velocity in m/s
    
    outputs:
    efficiency (float): jet engine thrust efficiency at specified altitude.
    """
    
    # Ensure that we have good inputs
    if isinstance(altitude, (float, int)) is False:
        print("Error: [calculate_mach] was expecting altitude input to be float or int. Got {}".format(type(altitude)))
        raise TypeError
    if isinstance(velocity, (float, int)) is False:
        print("Error: [calculate_mach] was expecting velocity input to be float or int. Got {}".format(type(altitude)))
        raise TypeError
    
    ref_alt = [0, 4000, 8000, 12000, 16000, 20000, 36000]
    ref_mach = [340.294, 324.579, 308.063, 295.069, 295.069, 295.069, 295.069]

    if altitude < 0:
        a = ref_mach[0]
    elif altitude > 36000:
        return 0
    else:
        a = np.interp(altitude, ref_alt, ref_mach)

    return velocity / a














