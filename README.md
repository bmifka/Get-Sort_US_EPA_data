# Get-Sort_US_EPA_data
Code to download multiple US-EPA Meteo or Air Quality data and make custom files
consists of program files:

Analyze_EPA_Files.py
  read the aqs_monitors.csv meta-file form link
    link: https://aqs.epa.gov/aqsweb/airdata/download_files.html#Meta
  for a user-defined range of years and a list of variables, make
  output (".csv") file that contains the list of all stations and instruments

get_EPA_files.sh 
  To download the EPA (for now only) hourly files for Wind and 
  scalar (Meteo and/or Air Quality) variables from 
  EPA files from https://aqs.epa.gov/aqsweb/airdata/ 

Sort_EPA_Files.py
  reads the Meta_File.csv and downloaded files, sorts them and
  writes to the custom output file in *.mat format

Sort_EPA_Functions.py 
  contains 2 functions for Wind and Scalar Variable extraction and sort:
    Extract_EPA_Wind
    Extract_EPA_Variable


Input Files:

aqs_monitors.csv  (for Analyze_EPA_Files.py)
  link: https://aqs.epa.gov/aqsweb/airdata/download_files.html#Meta
  contains meta-data about monitors and variables

Meta_File.csv     (for Sort_EPA_Files.py)
  contains user-defined station and instrument codes, and other meta-data 

files made by get_EPA_files.sh program containing variables at all stations


Output Files:

Muttual_EPA_Vars_File.csv made by Analyze_EPA_Files.py
  file that contains the list of all stations and instruments

user-defined_name.mat FINAL file with all user-defined 
variables, stations, instruments and meta-data
  

