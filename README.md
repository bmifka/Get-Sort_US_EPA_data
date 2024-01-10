# Get-Sort_US_EPA_data
Code to download multiple US-EPA Meteo or Air Quality data and make custom files
consists of program files:

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

Input files:

Meta_File.csv 
  contains user-defined station and instrument codes, and other meta-data 



