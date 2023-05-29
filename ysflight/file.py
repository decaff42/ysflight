#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

A module for importing and exporting ysflight files

"""

# Define constants
YSFLIGHT_FILE_TYPES = [".dat", ".yfs", ".fld", ".dnm", ".srf", ".lst", ".stp", ".ist", ".acp"]

import os

def import_file(filepath):
    """Import a text file and format as needed based on type of file. Only import
    YSFlight files as defined by file extension.
    
    input:
    filepath (str): os.path like string to where a file is
    
    output:
    lines (list): a list of strings which are the lines of the ysflight file.
    """    
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError
    elif os.path.splitext(filepath)[-1] not in YSFLIGHT_FILE_TYPES:
        print("Error: File is not a valid YSFlight File Type: {}".format(YSFLIGHT_FILE_TYPES))
        raise TypeError
        
    # If valid YSFlight file found, proceed with import and ensure that the 
    # newline (\n) character is removed from each row
    with open(filepath, mode='r') as ysflight_file:
        lines = ysflight_file.read().splitlines()
    
    # Make sure we imported something
    if len(lines) == 0:
        # This may be flagged for null.srf files so we shouldn't break just for a lack of lines.
        print("YSFlight File Import Issue: No lines in file")
        return lines
    
    # FUTURE: Make sure that any automatic handling we want done for specific 
    # filetypes are handled here. NOT processing of data in file.    
    
    return lines


def export_file(filepath, data):
    """Export a ysflight file to a specified location. Overwrite an existing file
    if one exists.
    
    input:
    filepath (str): os.path like string to where the file should be saved
    data (list): a list of lines that should be written to the file.
    
    output:
    None
    """
    
    if os.path.splitext(filepath)[-1] not in YSFLIGHT_FILE_TYPES:
        print("Error: file is not a valid YSFlight file type: {}".format(YSFLIGHT_FILE_TYPES))
        raise TypeError
    elif os.access(os.path.dirname(filepath), os.W_OK) is False:
        print("Error: Cannot save a file to this location due to insufficient privaleges")
        raise PermissionError
    
    # Write data to file
    with open(filepath, mode='w') as ysflight_file:
        ysflight_file.writelines(data)
        
    
    
    