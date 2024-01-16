#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
This program analyzes the US-EPA air quality and meteo meta data file:
    
    aqs_monitors.csv 
    link: https://aqs.epa.gov/aqsweb/airdata/download_files.html#Meta
    
User defines the: 1) date range 
                  2) desired variables using 'Parameter Code'
    
Program finds and makes list of all stations and instruments 
(identified with POC number) and stores the list in otuput .csv file
    
Usage:
Download file and edit SET OPTIONS:
    
#**************************************************************************
#                               SET OPTIONS: 
#**************************************************************************
#--set range of years to analyze
Year_s        = 2021
Year_e        = 2022

#--set the path of meta-data file
file_dir  = ''
fname     = 'aqs_monitors.csv'
file_path  = os.path.join(file_dir,fname )

#--in meta-date file, find the numeric 'Parameter Code' and make array 
#  including all desired parameters
#--add the Parameters Code to array 'params' bellow:
params         = np.array([61103,61104,62101,81102])

#--add user defined names for instrument identifier (POC) in forme
#  Variable_Name for each parameter 
POCprefix      = np.array(['POC WS','POC WD','POC TEMP','POC PM10'])

# Specify the file path
outFile_path = 'Muttual_EPA_file.csv'   
******************************************************************************* 
NOTICE: the number of instruments for certain parameter at the certain station 
        may be more than one. In this case, the additional rows in the 
        output.csv file are added. They contain the additional POC number, but 
        only in the column(s) of certain parameter(s). In other columns 
        (for other instruments) there is simply 'nan'. The number of additional
        rows is equal to the max number of instruments of certain parameter -1. 
    
-------------------------------------------------------------------------------
Created on Fri Jan  5 10:13:00 2024
@author: boris mifka (boris.mifka@phy.uniri.hr)
"""

import os
import pandas as pd
import numpy as np
from   datetime import datetime
import sys


#--this clears the console if IDE is used...MORA I IZBRISATI SVE VARIJABLE!!
def clear_console():
    # Check if the operating system is Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # Check if the operating system is Unix/Linux/Mac
    elif os.name == 'posix':
        _ = os.system('clear')
clear_console()

#******************************************************************************
#                               SET OPTIONS: 
#******************************************************************************
#--set range of years to analyze
Year_s        = 2021
Year_e        = 2022

#--set the path of meta-data file
file_dir  = ''
fname     = 'aqs_monitors.csv'
file_path  = os.path.join(file_dir,fname )

#--in meta-date file, find the numeric 'Parameter Code' and make array 
#  including all desired parameters
#--add the Parameters Code to array 'params' bellow:
params         = np.array([61103,61104,62101,81102])

#--add user defined names for instrument identifier (POC) in forme
#  Variable_Name for each parameter 
POCprefix      = np.array(['POC WS','POC WD','POC TEMP','POC PM10'])

# Specify the file path
outFile_path = 'Muttual_EPA_Vars_File.csv'

#******************************************************************************
#                               PROGRAM
#******************************************************************************
#--read the aqs_monitors.csv file and get important parameters
METAin     = pd.read_csv(file_path,low_memory=False)
MdateSp    = METAin["First Year of Data"]
MdateEp    = METAin["Last Sample Date"]
ParCode    = METAin["Parameter Code"]
MID_1      = METAin["State Code"].to_numpy()
MID_2      = METAin["County Code"].to_numpy()
MID_3      = METAin["Site Number"].to_numpy()
MPOC       = METAin["POC"].to_numpy()

MParName   = METAin["Parameter Name"]
Mlat       = METAin["Latitude"].to_numpy()
Mlon       = METAin["Longitude"].to_numpy()
MStateName = METAin["State Name"].to_numpy()
MCounName  = METAin["County Name"].to_numpy()
MCityName  = METAin["City Name"].to_numpy()

#--convert 'MdateSp' to datetime
MdateSdt = pd.to_datetime(MdateSp, format='%Y', errors='coerce')
MdateEdt = pd.to_datetime(MdateEp , errors='coerce')

#--convert 'MdateSp' to numeric timestamp 
MdateSn = MdateSdt.astype(int) / 10**9 - 3600
MdateEn = MdateEdt.astype(int) / 10**9  -3600

#--convert custom start and end year to check the matching data
dateS  = datetime(Year_s, 1, 1, 0, 0, 0)
dateE  = datetime(Year_e, 1, 1, 0, 0, 0)
#dateE  = datetime(Year_e, 12, 31, 23, 0, 0)

#--convert start_date to numeric timestamp
dateSn = dateS.timestamp()
dateEn = dateE.timestamp()

#--find all rows (stations) that contain desired individual parameters in range Year_s-Year_e
#  first initialize the IDs, sitename and position (lat and lon) lists 
IDs    = []
MSname = []
MCoName = []
MCiName = []
MPos   = []

for i in range(len(params)):
    IndParams   = np.where((ParCode==params[i])  & (MdateSn<=dateSn) & (MdateEn>=dateEn))[0] 
    MIDs_123tmp = np.hstack((MID_1[IndParams,None], MID_2[IndParams,None], MID_3[IndParams,None], 
                              MPOC[IndParams,None]))
    MSnameTmp   = MStateName[IndParams]
    MCoNameTmp  = MCounName[IndParams]
    MCiNameTmp  = MCityName[IndParams]
    MPosTmp     = np.hstack((Mlat[IndParams,None],Mlon[IndParams,None]))
    
    IDs.append(MIDs_123tmp)
    MSname.append(MSnameTmp)
    MCoName.append(MCoNameTmp)
    MCiName.append(MCiNameTmp)
    MPos.append(MPosTmp)
    

#--find the stations that mutually contain the desired parameters in Year_s-Year_e
#  first initialize the output rows, muttual (boolean), rowsOut for numeric 
muttual   = [False] * (len(IDs) - 1)
rowsOut   = []
SnameOut  = []
CoNameOut = []
CiNameOut = []

cnt=0
for i in range(len(IDs[0])):
    MutIndL = 0
    MutIndtmp=[np.array([]) for _ in range(len(IDs)-1)]
    for j in range(len(IDs)-1):
        muttual[j]    = np.any(np.all(IDs[j+1][:,0:3] == IDs[0][i,0:3], axis=1))
        MutIndtmp[j]  = np.where(np.all(IDs[j+1][:,0:3] == IDs[0][i,0:3], axis=1))[0]
  
    all_true = all(muttual)
    if all_true:
        
          rowL = [len(row) for row in MutIndtmp]
         
          rowsOutTmp = np.full((max(rowL), 5+len(params)), np.nan)
          SnameTmp   = np.full((max(rowL),1),'',dtype='<U50')
          CoNameTmp  = np.full((max(rowL),1),'',dtype='<U50')
          CiNameTmp  = np.full((max(rowL),1),'',dtype='<U50')
        
          for k in range(1,len(params)):
              for k2 in range(rowL[k-1]):
                  indtmp              = MutIndtmp[k-1][k2]
                  rowsOutTmp[k2,k+3]  = IDs[k][indtmp,-1]
                  rowsOutTmp[k2,0:3]  = IDs[0][i,0:3]
                  SnameTmp   [k2,:]   = MSname [k][indtmp]
                  CoNameTmp  [k2,:]   = MCoName[k][indtmp]
                  CiNameTmp  [k2,:]   = MCiName[k][indtmp]
                 
                  if k2==0:
                      rowsOutTmp[k2,  3] = IDs[0][i,  3]
                 
            
          #--add the Postion and Station name info to the rows
          rowsOutTmp[:,-2:]   = MPos[0][i,:]
        
          if len(rowsOut)==0:
              rowsOut   = rowsOutTmp    
              SnameOut  = SnameTmp
              CoNameOut = CoNameTmp
              CiNameOut = CiNameTmp
          else:
              rowsOut   = np.vstack((rowsOut,rowsOutTmp))
              SnameOut  = np.vstack((SnameOut,SnameTmp))
              CoNameOut = np.vstack((CoNameOut,CoNameTmp))
              CiNameOut = np.vstack((CiNameOut,CiNameTmp))
        
          cnt = cnt+1
if cnt>0:       
    print('Number of stations containing the mutual data is:',cnt,'\n')       
else:
    print('There is no stations in this period contaning mutual data...\
           Define different period! \n')
    sys.exit()
    
#--write data to csv
strings1   = np.array(['State Code', 'County Code', 'Site Number'])
strings2   = np.array(['Latitude','Longitude','State Name','County Name','City Name'])
stringsRow = np.concatenate((strings1, POCprefix, strings2))

matrix           = np.column_stack((rowsOut,SnameOut,CoNameOut,CiNameOut))
combined_matrix  = np.row_stack((stringsRow,matrix))

#--convert the combined matrix to a Pandas DataFrame
df = pd.DataFrame(combined_matrix)

#--writing data to the CSV file
df.to_csv(outFile_path, index=False, na_rep='')

print(f'Data has been written to {outFile_path}')




    
    