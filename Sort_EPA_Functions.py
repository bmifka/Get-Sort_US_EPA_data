#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Functions to sort input EPA files:
    EXTRACT_EPA_Wind & EXTRACT_EPA_Variable
    
They are simmilar, except the function for wind extracts and sorts the Wind
Speed and Wind direction data which are in the same file in same columns.
Functions:
    - search for the rows with ID and POC of desired station and instrument within 
    the yearly file
    - extracts these rows for each station and stores the data in the one list
    per station
    - since the original data does not contain all dates and missing data code
    (e.g.) it creats all dates (hourly) within the the year_start - year_end 
    range and sets the -999.99 for the missing data  
-------------------------------------------------------------------------------
Created on Fri Jan  5 12:12:11 2024
@author: boris mifka (boris.mifka@phy.uniri.hr)
"""

import os
import pandas as pd
import numpy as np
from   datetime import datetime, timedelta


def Extract_EPA_Wind(years,ID_stat,files_dir,fname_prefix,POC_WS,POC_WD):
    
    #----initialize the outer loop numeric dates, WS and WD lists 
    WSdate_outer = []
    WDdate_outer = []
    WS_outer     = []
    WD_outer     = []
    
    #--get the number of years and stations
    NoYears = len(years)
    NoStats = ID_stat.shape[0]
    
    
    #--begin loop over years
    for k in range(NoYears):
        #--combine path and prefix to create the complete file path
        file_path = os.path.join(files_dir, f'{fname_prefix}_{years[k]}.csv')
        #--read important columns
        VARin     = pd.read_csv(file_path)
        VAR       = VARin["Sample Measurement"]
        VAR_POC   = VARin["POC"]
        VAR_datep = VARin["Date GMT"]
        VAR_timep = VARin["Time GMT"]
        VAR_date  = VAR_datep.to_numpy()
        VAR_time  = VAR_timep.to_numpy()
        ID_1      = VARin["State Code"]
        ID_2      = VARin["County Code"]
        ID_3      = VARin["Site Num"]
        ID_W      = VARin["Parameter Name"]
        
        #--initialize the inner loop numeric date and VAR list
        innerDatelistWS = []
        innerDatelistWD = []
        innerWSlist     = []
        innerWDlist     = []
        
        #--index the data for each station and instrument (POC)
        for j in range(NoStats):
            IndStatWS = np.where((ID_1 == ID_stat[j, 0]) & (ID_2 == ID_stat[j, 1]) & \
                                 (ID_3 == ID_stat[j, 2]) & (VAR_POC == POC_WS[j]) & \
                                 (ID_W == 'Wind Speed - Resultant'))[0]
                
            IndStatWD = np.where((ID_1 == ID_stat[j, 0]) & (ID_2 == ID_stat[j, 1]) & \
                                 (ID_3 == ID_stat[j, 2]) & (VAR_POC == POC_WD[j]) & \
                                 (ID_W == 'Wind Direction - Resultant'))[0]
         
            #--get WS and WD data at station, date and time, merge date and time
            WS_statp    = VAR[IndStatWS]
            WS_stat_tmp = WS_statp.to_numpy()
            WD_statp    = VAR[IndStatWD] 
            WD_stat_tmp = WD_statp.to_numpy()  
            
            #--get WS and WD data at station, date and time, merge date and time
            date_strWSp = VAR_date[IndStatWS]+'T' + VAR_time[IndStatWS]+':00'
            date_strWS  = np.array(date_strWSp, dtype='datetime64')
            date_WStmpn = (date_strWS - np.datetime64('0000-01-01T00:00:00')).astype('timedelta64[h]').astype(float)/24+1
            date_strWDp = VAR_date[IndStatWD]+'T' + VAR_time[IndStatWD]+':00'
            date_strWD  = np.array(date_strWDp, dtype='datetime64')
            date_WDtmpn = (date_strWD - np.datetime64('0000-01-01T00:00:00')).astype('timedelta64[h]').astype(float)/24+1
            
     
            innerDatelistWS.append(date_WStmpn)
            innerDatelistWD.append(date_WDtmpn)
            innerWSlist.append(WS_stat_tmp)
            innerWDlist.append(WD_stat_tmp)
            
        #--append the dates and VAR lists to outer lists
        WSdate_outer.append(innerDatelistWS)
        WDdate_outer.append(innerDatelistWD)
        WS_outer.append(innerWSlist)
        WD_outer.append(innerWDlist)
            
    #--create the numeric date range with no gaps in hourly increments 
    #  and convert to numeric format
    start_date = datetime(years[0], 1, 1, 0, 0, 0)
    end_date   = datetime(years[-1], 12, 31, 23, 0, 0)
    date_range = np.arange(start_date, end_date + timedelta(hours=1),timedelta(hours=1))
    daten      = (date_range - np.datetime64('0000-01-01T00:00:00')).astype('timedelta64[h]').astype(float)/24+1
    L          = len(daten)
    

    #--make the lists for Variables at stations
    listsDateWSIn = [[] for _ in range(NoStats)]
    listsDateWDIn = [[] for _ in range(NoStats)]
    listsWSIn     = [[] for _ in range(NoStats)]
    listsWDIn     = [[] for _ in range(NoStats)]
    
    for k in range(NoStats):
        for j in range(NoYears):    
            listsDateWSIn[k].extend(WSdate_outer[j][k])
            listsDateWDIn[k].extend(WDdate_outer[j][k])
            listsWSIn[k].extend(WS_outer[j][k])
            listsWDIn[k].extend(WD_outer[j][k]) 
    
    
    #--initialize the output list with full data_range at each station   
    listsWSOut  = [[-999.9] * L for _ in range(NoYears)]
    listsWDOut  = [[-999.9] * L for _ in range(NoYears)]
    
    #--and append the variable data, otherwise leave -999.9
    for j in range(NoStats):
          for i in range(L):
             IndDateExistWS = np.where(listsDateWSIn[j]==daten[i])[0]
             IndDateExistWD = np.where(listsDateWDIn[j]==daten[i])[0]
             
             
             #--if the data exist for the current hour write, else replace with -999.9
             if len(IndDateExistWS) != 0:
                 listsWSOut[j][i] = listsWSIn[j][IndDateExistWS[0]]
             else:
                 listsWSOut[j][i] = -999.9
                 
             #--if the data exist for the current hour write, else replace with -999.9
             if len(IndDateExistWD) != 0:
                 listsWDOut[j][i] = listsWDIn[j][IndDateExistWD[0]]
             else:
                 listsWDOut[j][i] = -999.9
             
    # Create a dictionary to store the variables
    data_dict = {
        'dates': daten,  
        'WS'   : listsWSOut,
        'WD'   : listsWDOut
    }
    return data_dict
    
    
def Extract_EPA_Variable(years,ID_stat,fname_dir,fname_prefix,POC):
    
    #--initialize the outer loop numeric date and VAR list 
    date_outer = []
    VAR_outer  = []

    #--get the number of years and stations
    NoYears = len(years)
    NoStats = ID_stat.shape[0]

    #--begin loop over years
    for k in range(NoYears):
        #--combine path and prefix to create the complete file path
        file_path = os.path.join(fname_dir, f'{fname_prefix}_{years[k]}.csv')
        #--read important columns
        VARin     = pd.read_csv(file_path)
        VAR       = VARin["Sample Measurement"]
        VAR_POC   = VARin["POC"]
        VAR_datep = VARin["Date GMT"]
        VAR_timep = VARin["Time GMT"]
        VAR_date  = VAR_datep.to_numpy()
        VAR_time  = VAR_timep.to_numpy()
        ID_1      = VARin["State Code"]
        ID_2      = VARin["County Code"]
        ID_3      = VARin["Site Num"]
        
        #--initialize the inner loop numeric date and VAR list
        innerDatelist = []
        innerVarlist  = []
        #--index the data for each station and instrument (POC)
        for j in range(NoStats):
            IndStatVAR = np.where((ID_1 == ID_stat[j, 0]) & (ID_2 == ID_stat[j, 1]) & \
                                  (ID_3 == ID_stat[j, 2]) & (VAR_POC == POC[j]))[0]
            
            #--get Variable data at station, date and time, merge date and time
            VAR_statp    = VAR[IndStatVAR] 
            VAR_stat_tmp = VAR_statp.to_numpy()   
            date_strVARp = VAR_date[IndStatVAR]+'T' + VAR_time[IndStatVAR]+':00'
            date_strVAR  = np.array(date_strVARp, dtype='datetime64')
            date_tmpn    = (date_strVAR - np.datetime64('0000-01-01T00:00:00')).astype('timedelta64[h]').astype(float)/24+1
            
            innerDatelist.append(date_tmpn)
            innerVarlist.append(VAR_stat_tmp)
        
            
        #--append the dates and VAR lists to outer lists
        date_outer.append(innerDatelist)
        VAR_outer.append(innerVarlist)
    
    #--create the numeric date range with no gaps in hourly increments 
    #  and convert to numeric format
    start_date = datetime(years[0], 1, 1, 0, 0, 0)
    end_date   = datetime(years[-1], 12, 31, 23, 0, 0)
    date_range = np.arange(start_date, end_date + timedelta(hours=1),timedelta(hours=1))
    daten      = (date_range - np.datetime64('0000-01-01T00:00:00')).astype('timedelta64[h]').astype(float)/24+1
    L          = len(daten)
    
    
    #--make the lists for Variables at stations
    listsDateIn = [[] for _ in range(NoStats)]
    listsVarIn  = [[] for _ in range(NoStats)]
    
    for k in range(NoStats):
        for j in range(NoYears):    
            listsDateIn[k].extend(date_outer[j][k])
            listsVarIn[k].extend(VAR_outer[j][k]) 
    
    
    #--initialize the output list with full data_range at each station   
    listsVarOut  = [[-999.9] * L for _ in range(NoYears)]
    
    #--and append the variable data, otherwise leave -999.9
    for j in range(NoStats):
          for i in range(L):
             IndDateExist = np.where(listsDateIn[j]==daten[i])[0]
             
             #--if the data exist for the current hour write, else replace with -999.9
             if len(IndDateExist) != 0:
                 listsVarOut[j][i] = listsVarIn[j][IndDateExist[0]]
             else:
                 listsVarOut[j][i] = -999.9
 

    # Create a dictionary to store the variables
    data_dict = {
        'dates'      : daten,  
        fname_prefix : listsVarOut
    }
    
    return data_dict
    

