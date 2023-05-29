#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Perform calculations that rely on YSFlight source code calculations

"""

# Import standard modules
import math

# Import 3rd Party Modules
import numpy as np

# Import ysflight modules


# Define constants
YSFLIGHT_G = 9.807


def calculate_thrust(altitude: (float, int), airspeed: (float, int), throttle: (float, int), afterburner: bool, airplane_dat, realprop):
    """Calculate the thrust of an aircraft at a specific altitude and air speed.
    
    inputs:
    altitude (float, int): the altitude in meters 
    airspeed (float, int): the airspeed in m/s
    afterburner (bool): if the afterburner is used or not
    airplane_dat (N/A): The DAT Properties of an airplane.
    realprop (dict): dict of realprop classes.
    
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
        
    if throttle < 0 or throttle > 1:
        print("Error: [calculate_thrust] Invalid throttle input. Must be between 0 and 1 but got: {}".format(throttle))
        raise ValueError
        
    # Determine which type of analysis to perform based on the type of engine
    if len(realprop.keys()) > 0:
        # Real Propeller calculation
        return calculate_real_prop_thrust(altitude, airspeed, throttle, airplane_dat, realprop)
    elif "PROPELLR" in airplane_dat.keys():
        # Simple Propeller calculation
        return calculate_simple_prop_thrust(altitude, airspeed, throttle, airplane_dat)
    else:
        # Jet Engine
        return calculate_jet_thrust(altitude, throttle, afterburner, airplane_dat)
    

def calculate_real_prop_thrust(altitude, airspeed, throttle, airplane_dat, realprop):
    """Calculate the real propeller engine thrust at the specified altitude, airspeed, and throttle setting.
    altitude (float, int): the altitude in meters 
    airspeed (float, int): the airspeed in m/s
    afterburner (bool): if the afterburner is used or not
    airplane_dat (N/A): The DAT Properties of an airplane.
    realprop (dict): dict of realprop classes.
    
    output:
    thrust (float, int): thrust in newtons of the aircraft
    """
    
    # Until we sort things out use the simple engine model
    return calculate_simple_prop_thrust(altitude, airspeed, throttle, airplane_dat)
    
    
    # Need to find equations in YSFlight Source Code
    
    # num_blades = realprop['NBLADE']
    # blade_area = realprop['AREAPERBLADE']
    
    # air_density_bias = get_air_density(altitude) / get_air_density(0)
    
    
    # moment_of_intertia = realprop["GRAVITYCENTER"] * realprop["GRAVITYCENTER"] * realprop["WEIGHTPERBLADE"]
    
    
    
    # T = T / 60
    # w = 2 * math.pi * T / 60
    # vprop = 2 * math.pi * T * R / 60
    # PropAngle = math.atan(airspeed / vprop)
    
    return 0
    

def calculate_ias(altitude, airspeed):
    """convert a true air speed into the indicated air speed at a given altitude.
    
    inputs:
    altitude (float, int): the altitude in meters
    airspeed (float, int): the airspeed (any units)
    
    outputs:
    ias (float, int): the indicated air speed
    """
    return airspeed * math.sqrt(get_air_density(altitude) / get_air_density(0))

    
def calculate_simple_prop_thrust(altitude, airspeed, throttle, airplane_dat):
    """Calculate the thrust that a simple propeller engine produces at specified altitude, airspeed,
    and throttle setting.
    
    inputs:
    altitude (float, int): the altitude in meters 
    airspeed (float, int): the airspeed in m/s
    throttle (float, 0-1): the throttle setting as a decimal percentage.
    airplane_dat (N/A): The DAT Properties of an airplane.
    
    outputs:
    thrust (float): thrust force in newtons of the aircraft.
    """
    
    propvmin = airplane_dat['PROPVMIN']
    propefcy = airplane_dat['PROPEFCY']
    propellr = airplane_dat['PROPELLR']
    
    if airspeed < propvmin:
        Power = propellr * throttle * propefcy / propvmin
        thrust = (get_air_density(0) / get_air_density(altitude)) * Power / airspeed
    else:
        propk = -1 * (propellr * propefcy) / propvmin**2
        
        thrust_static = propellr * propefcy / propvmin
        thrust_max = thrust_static - propk * propvmin * airspeed
        thrust = thrust_max * throttle * get_air_density(altitude) / get_air_density(0)
        
    return thrust
        
    
def calculate_jet_thrust(altitude, throttle, afterburner, airplane_dat):
    """Calculate the thrust that a jet engine produces at specified altitude and throttle setting.
    
    inputs:
    altitude (float, int): the altitude in meters 
    throttle (float, 0-1): the throttle setting as a decimal percentage.
    afterburner (bool): if the afterburner is used or not
    airplane_dat (N/A): The DAT Properties of an airplane.
    
    outputs:
    thrust (float): thrust force in newtons of the aircraft.
    """
    
    n = calculate_jet_efficiency(altitude)
    if afterburner is True and airplane_dat['AFTBURNR'] == True:
        thrust = n * airplane_dat['THRMILIT'] * (airplane_dat['THRAFTBN'] - airplane_dat['THRMILIT']) * throttle
    else:
        thrust = n * airplane_dat['THRMILIT'] * throttle
        
    return thrust

    
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
    ref_n = [1, 1, 0.6, 0.3, 0.0, 0.084991, 0.084991, 0]

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














