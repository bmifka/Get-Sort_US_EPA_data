#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
This program reads the US-EPA hourly Wind and scalar Variables (e.g. 
concentrations of pollutants and/or meteo variables) data from yearly files. 
It extracts the Wind Speed and Wind Direction from Wind files and Variables of 
choice from the Variable files for specific stations and instruments (POC). 


User edits the input Meta_File.csv: each row is for a new station (or instrument 
at the same station).

INPUT columns in Meta_File.csv are:
    'State Code''County Code' 'Site Number'	
    'POC WS'	'POC WD' 'POC TEMP'	'POC PM10', .....etc (user defined)	
    'Latitude'	'Longitude'	'Local Site Name'

    The POCs need to be added by the user in the Meta_File.csv depending on the
    choice of variables. 
    
    In this program, the user also edits the section SET OPTIONS: 
       #--input
       year_s            = 2021                 # years of first and last file
       year_e            = 2022                 
       metaFile_dir      = ''                   # set path of Meta_File.csv
       metaFname         = 'Meta_File.csv'
       files_dir         = 'EPA_FILES/'         # set path of EPA files folder
       fname_prefixW     = 'WIND'               # set prefixes for WIND and Vars files
       fname_prefixVars  = np.array(['PM10'])   # it is also used for names of output 
                                                # variables in the output .mat file
       POCs              = ["POC PM10"]         # use names same as you define in
                                                # Meta_File.csv
       
       Additional meta-data can be found in  aqs_monitors.csv file at
       https://aqs.epa.gov/aqsweb/airdata/download_files.html#Meta
       
       #--additional arrays for Meta Data to store in the output .mat file
       MsiteName   = METAin["Local Site Name"]
       Mlat        = METAin["Latitude"].to_numpy()
       Mlon        = METAin["Longitude"].to_numpy()
       #..............................................................................
       #......!!!USER CAN ADD MORE PARAMETERS HERE AND ADD THE CUSTOM VARIBLES IN 
       #DATA_out dictionary...........................................................
       CUSTOM_MVAR = METAin["Var Name as in Meta_File.csv"]
        
        
The OUTPUT DATA for a specified period is stored in a dictionarny and written in 
a .mat file. The data is Wind Speed, Wind Direction, Variables, and dates in
numeric format with reference 0000/01/01 00:00:00. In addition, other meta data
as station name, latitude, and longitude can be added in DATA_out dictionary.
The variable array for each station is in a new row. 
The first row is for the first station etc...

Further development plans:
    - make an option for the data at all time resolutions (now works for hourly data only)
    - at this moment, there is a minimum of 2 years (files) of data needed...
-------------------------------------------------------------------------------
Created on Wed Jan  3 09:51:35 2024
@author: boris mifka (boris.mifka@phy.uniri.hr)
"""

import os
import pandas as pd
import numpy as np
from Sort_EPA_Functions import Extract_EPA_Wind
from Sort_EPA_Functions import Extract_EPA_Variable
import scipy


#--this clears the console if IDE is used
def clear_console():
    # Check if the operating system is Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # Check if the operating system is Unix/Linux/Mac
    elif os.name == 'posix':
        _ = os.system('clear')
clear_console()

#******************************************************************************
#                          SET OPTIONS: 
#******************************************************************************
#--input
year_s            = 2021                 
year_e            = 2022                 
metaFile_dir      = ''                  
metaFname         = 'Meta_File.csv'
files_dir         = 'EPA_FILES/'         
fname_prefixW     = 'WIND'               
fname_prefixVars  = np.array(['TEMP','PM10'])
POCs              = ["POC TEMP","POC PM10"]

#--output
outputFile_path   = 'EPA.mat' # set path including the name of output file


#--read the Meta_File.csv file and get important parameters
metaFile_path  = os.path.join(metaFile_dir,metaFname)
METAin    = pd.read_csv(metaFile_path)

#--arrays important for data search (leave in numpy): 
MID_1     = METAin["State Code"].to_numpy()
MID_2     = METAin["County Code"].to_numpy()
MID_3     = METAin["Site Number"].to_numpy()
MPOC_WS   = METAin["POC WS"].to_numpy()
MPOC_WD   = METAin["POC WD"].to_numpy()

#--additional arrays for Meta Data to store in otuput .mat file
MsiteName = METAin["CBSA Name"]
Mlat      = METAin["Latitude"].to_numpy()
Mlon      = METAin["Longitude"].to_numpy()
MUnitWS   = METAin["Unit WS"][0]           #only 1st row is needed
MUnitWD   = METAin["Unit WD"][0]
MUnitT    = METAin["Unit TEMP"][0]
MUnitPM10 = METAin["Unit PM10"][0]
#..............................................................................
#......!!!USER CAN ADD MORE PARAMETERS HERE AND ADD THE CUSTOM VARIBLES IN 
#DATA_out dictionary...........................................................
#CUSTOM_MVAR = METAin["Var Name as in Meta_File.csv"] #example

#--stack the station IDs
ID_stat =  np.hstack((MID_1[:,None], MID_2[:,None], MID_3[:,None])) 

#******************************************************************************
#                               PROGRAM
#******************************************************************************
#--set years range
years   = np.arange(year_s, year_e + 1)

try:
    #--call the function to extract the wind data
    WIND_out = Extract_EPA_Wind(years,ID_stat,files_dir,fname_prefixW,MPOC_WS,MPOC_WD)
    print("Wind Data Extraction and Sort Done!")
    
except Exception as e:
    print("An error occurred while sorting Wind Data:", e)

try:
    #--combine dictionaries and variables into a single dictionary
    DATA_out = {'WIND': WIND_out,'lat': Mlat,'lon': Mlon,'SiteName': MsiteName,
                'UnitWindSpeed': MUnitWS, 'UnitWindDirection': MUnitWD,
                'UnitTemperature': MUnitT,'UnitPM10': MUnitPM10}

    #--call the function to extract the variable(s)
    for i in range(len(fname_prefixVars)):
        MPOC_VAR  = METAin[POCs[i]]
        VAR_out = Extract_EPA_Variable(years,ID_stat,files_dir,fname_prefixVars[i],MPOC_VAR)
        
        #--remove the redundant date arrays from VAR_out dictionary
        #VAR_out.pop('dates', None)   #--comment for test
        
        # Add VAR_out to DATA_out
        DATA_out['VAR_{}'.format(i)] = VAR_out
        
    print("Scalar Variable Data Extraction and Sort Done!")    
        
    #--save the data to the .mat file
    scipy.io.savemat(outputFile_path, {'EPA_DATA': DATA_out})
    print("Extraction and Sort Done!")

except Exception as e:
    print("An error occurred while sorting scalar Variable data:", e)
