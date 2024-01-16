close all; clear all; clc
%---------------------------------------------------------------
% Testiranje PYthon coda za čupanje EPA podataka
%
%---------------------------------------------------------------

%---------------------------------------------------------------
%        SET OPTIONS:
%---------------------------------------------------------------
stat = 1;
year_s = 2021;
year_e = 2022;

fWSName   = strcat('WS_stat',num2str(stat),'_test.csv');
fWDName   = strcat('WD_stat',num2str(stat),'_test.csv');
fTEMPName = strcat('TEMP_stat',num2str(stat),'_test.csv');
fPM10Name = strcat('PM10_stat',num2str(stat),'_test.csv');

%---------CONTINE...........
%---read the .csv observations
WS    = readtable(fWSName);
WD    = readtable(fWDName);
TEMP  = readtable(fTEMPName);
PM_10 = readtable(fPM10Name);

%--read python output
load EPA.mat

%--date and time from WS and WD measurements
dateWS        = datevec(WS.DateGMT);
timeWS        = datevec(WS.TimeGMT);
dateWS(:,4)   = [timeWS(:,4)];
dateWSn       = datenum(dateWS); 
ind23         = find(dateWS(:,1)>year_e);
WSt           = WS.SampleMeasurement;
dateWSn(ind23)= [];
WSt(ind23) = [];

%--date and time from WS and WD measurements
dateWD        = datevec(WD.DateGMT);
timeWD        = datevec(WD.TimeGMT);
dateWD(:,4)   = [timeWD(:,4)];
dateWDn       = datenum(dateWD); 
ind23         = find(dateWD(:,1)>year_e);
WDt           = WD.SampleMeasurement;
dateWDn(ind23)= [];
WDt(ind23) = [];

%--date and time from TEMP measurements
dateT           = datevec(TEMP.DateGMT);
timeT           = datevec(TEMP.TimeGMT);
dateT(:,4)      = [timeT(:,4)];
dateTn          = datenum(dateT); 
ind23           = find(dateT(:,1)>year_e);
Tt              = TEMP.SampleMeasurement;
Tt(ind23) = [];
dateTn(ind23)   = [];

%--date and time from PM10 measurements
datePM10        = datevec(PM_10.DateGMT);
timePM10        = datevec(PM_10.TimeGMT);
datePM10(:,4)   = [timePM10(:,4)];
datePM10n       = datenum(datePM10); 
ind23           = find(datePM10(:,1)>year_e);
PM10t           = PM_10.SampleMeasurement;
PM10t(ind23) = [];
datePM10n(ind23)= [];

%--get dates from Python
dateWSPy   = EPA_DATA.WIND.dates';
dateWDPy   = EPA_DATA.WIND.dates';
dateTPy    = EPA_DATA.VAR_0.dates';
datePMPy   = EPA_DATA.VAR_1.dates';

%--get data from Python
WSPy      = EPA_DATA.WIND.WS(stat,:)';
WDPy      = EPA_DATA.WIND.WD(stat,:)';
TPy       = EPA_DATA.VAR_0.TEMP(stat,:)';
PM10Py    = EPA_DATA.VAR_1.PM10(stat,:)';

%--poredba
%---check if the dates are the same for all variables in .mat file
PyDateCheck1 = unique(dateWSPy==dateTPy);
PyDateCheck2 = unique(dateWSPy==datePMPy);

%--check if the dates in test files and .mat files are the same
%  (after removing the -999.9)
indWS=find(WSPy ==-999.9);
dateWSPy(indWS)=[];
WSPy(indWS)=[];

indWD=find(WDPy ==-999.9);
dateWDPy(indWD)=[];
WDPy(indWD)=[];

indT=find(TPy ==-999.9);
dateTPy(indT)=[];
TPy(indT)=[];

indPM=find(PM10Py ==-999.9);
datePMPy(indPM)=[];
PM10Py(indPM)=[];

%--check it...
 diff_WSdate   = unique(dateWSPy-dateWSn)
 diff_WDdate   = unique(dateWDPy-dateWDn)
 diff_Tdate    = unique(dateTPy-dateTn)
 diff_PMdate   = unique(datePMPy-datePM10n)

%--finaly, check variables:
 diff_WS   = unique(WSPy-WSt)
 diff_WD   = unique(WDPy-WDt)
 diff_T    = unique(TPy-Tt)
 diff_PM10 = unique(PM10Py-PM10t)
 
%  
% 
% figure(1)
% subplot(2,1,1)
% plot(dateWDPy); hold on
% subplot(2,1,2)
% plot(dateWDn)