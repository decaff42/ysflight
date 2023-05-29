#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 29 14:38:33 2023

"""

# Import standard Python Modules
import os

# Import 3rd Party Modules

# Import ysflight modules
from ysflight.fileparse.AircraftDat import *


cwd = os.getcwd()
filepath = os.path.join(cwd, 'a4.dat')

dat = AircraftDat(filepath)

