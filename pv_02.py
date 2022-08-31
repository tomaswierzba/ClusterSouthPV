# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 14:34:45 2022

@author: Tomás Wierzba
"""
#This is a calculation-based algorithm that provides power production for PV panels located anywhere on earth.
#Assumption: Pv system has a fixed tilt and orientation

import pandas as pd
import numpy as np
import numpy_financial as npf
import math
from matplotlib import pyplot as plt

#Parameters
inverter_eff = 0.9
panels_nom_cap = 1 #kW array power rating (DC) the total DC power output of all installed PV modules at the power rating reference condition, assumed to be standard test conditions (STC reference values irradiance 1 000 W/m2, at normal incidence, PV cell temperature 25 °C)


#Inputs: select one of the locations listed or add a new one!
#Location
City_Long = {'Copenhagen': 12.55, 'Tel Aviv': 34.77, 'Buenos Aires': -58.43,'Puna Catamarca': -67.34, 'Usagre':-6.17, 'Libreville':0.40,'Laayoune':-13.20} #city longitude (coordinate) in degrees
City_Lat = {'Copenhagen': 55.70, 'Tel Aviv': 32.08, 'Buenos Aires':-34.60,'Puna Catamarca': -25.72, 'Usagre':38.35 ,'Libreville':9.46,'Laayoune': 27.24} #city latitude (coordinate) in degrees
sunshine_hr_monthly = {'Copenhagen': [45,65,115,190,260,245,260,240,255,205,60,40]}  #city longitude (coordinate) in degrees
GMT_zone = {'Copenhagen': 1, 'Tel Aviv': 2, 'Buenos Aires':-3,'Puna Catamarca': -3,'Usagre':1,'Libreville':0,'Laayoune': 0} #remember that some countries have winter and summer time, anyways this not affect the results. We just need to look at the power production vs time carefully and intepret depending on the season if we should sum or sustract one hour. 
altitude = {'Copenhagen': 0, 'Tel Aviv': 0, 'Buenos Aires':0,'Puna Catamarca': 3.35, 'Usagre':0,'Libreville':0,'Laayoune':0 } # altitude above sea level in kilometers
#Select location:
city = 'Copenhagen'
#PV module
if City_Lat[city]<0:    #modules on the northern hemisphere face south and the azimuth angle of the panels is 180 degrees. If the modlues are located in the southern hemisphere the modules face north and the azimuth is 0 degrees.
    azimuth_panel_d = 0 #PV panel faces north
else:
    azimuth_panel_d = 180 #PV panel faces south
latitude_angle_d = City_Lat[city] #degrees
Longitude_d = City_Long[city] #degrees

DT_gmt = GMT_zone[city] #difference between localtime from greenwich meridian mean time in hours

if latitude_angle_d < 0:
    tilt_angle_d = -latitude_angle_d
else:
    tilt_angle_d = latitude_angle_d #degrees, the tilt degree which yields approx maximum production over a year is when the tilt angle equals the latitude angle (this is not accurate, rule of thumb!)
tilt_angle_r = tilt_angle_d*math.pi/180 #tilt angle in radians

#Time
LT_h = np.linspace(0, 23,24) #Local Time hour component
LT_m = np.linspace(0, 59,60) #Local Time minute component
LT_d = np.zeros((len(LT_h),len(LT_m))) 
for i in range (0, len(LT_h)):
    for j in range (0, len(LT_m)):
        LT_d[i,j] = LT_h[i] + LT_m[j]/60 #Local Time in degrees for a given hour and minute
day = np.zeros(365) #day number of the year
for n in range(0,len(day)):
    day[n]=n+1 #day number of the year
 
#Model
azimuth_panel_r = azimuth_panel_d*math.pi/180 #azimuth panel angle in radians
latitude_angle_r = latitude_angle_d*math.pi/180 #latitude angle in radians
declination_angle_r = np.zeros(len(day))
for n in range(0,len(day)):
    declination_angle_r[n] = -23.45*math.pi/180*math.cos(360/365*(day[n]+10)*math.pi/180) #declination angle in radians on a given day of the year. The declination angle reflects the different seasons on earth.
declination_angle_d = declination_angle_r/math.pi*180
LSTM_d = 15*DT_gmt
EoT_m = np.zeros(len(day))
B_r = 360/365*(day-81)*math.pi/180
for n in range(0,len(day)):
    EoT_m[n] = 9.87*math.sin(2*B_r[n])-7.53*math.cos(B_r[n])-1.5*math.sin(B_r[n])
TC_m = 4*(Longitude_d-LSTM_d) + EoT_m
LST_d = np.zeros((len(day),len(LT_h),len(LT_m)))
for i in range (0, len(LT_h)):
    for j in range (0, len(LT_m)):
        for n in range(0,len(day)):
            LST_d[n,i,j] = LT_d[i,j] + TC_m[n]/60
HRA_d = 15*(LST_d -12)
HRA_r = HRA_d*math.pi/180
elevation_angle_r = np.zeros((len(day),len(LT_h),len(LT_m)))
azimuth_sun_r = np.zeros((len(day),len(LT_h),len(LT_m)))
for i in range (0, len(LT_h)):
    for j in range (0, len(LT_m)):
        for n in range(0,len(day)):
            elevation_angle_r[n,i,j] = math.asin(math.sin(declination_angle_r[n]) * math.sin(latitude_angle_r) + math.cos(declination_angle_r[n]) * math.cos(latitude_angle_r) * math.cos(HRA_r[n,i,j]))
            azimuth_sun_r[n,i,j] = math.acos((math.sin(declination_angle_r[n])*math.cos(latitude_angle_r)-math.cos(declination_angle_r[n])*math.sin(latitude_angle_r)*math.cos(HRA_r[n,i,j]))/math.cos(elevation_angle_r[n,i,j]))
            if HRA_r[n,i,j]>0:
                azimuth_sun_r[n,i,j] = 2*math.pi - azimuth_sun_r[n,i,j]
elevation_angle_d = elevation_angle_r/math.pi*180
azimuth_sun_d = azimuth_sun_r/math.pi*180
zenith_angle_d = 90 - elevation_angle_d #degrees
zenith_angle_r = zenith_angle_d*math.pi/180

AM = np.zeros((len(day),len(LT_h),len(LT_m)))
direct_irradiance = np.zeros((len(day),len(LT_h),len(LT_m)))
for i in range (0, len(LT_h)):
    for j in range (0, len(LT_m)):
        for n in range(0,len(day)):
            AM[n,i,j] = 1/math.cos(zenith_angle_r[n,i,j])
            if AM[n,i,j]>0:
                direct_irradiance[n,i,j] = 1.353 * ((1 - 0.14 * altitude[city]) * math.pow(0.7,math.pow(AM[n,i,j],0.678)) + 0.14 * altitude[city]) #kW/m2
            else:
                direct_irradiance[n,i,j] = 0
global_irradiance = 1.1 * direct_irradiance #kW/m2
module_irradiance = np.zeros((len(day),len(LT_h),len(LT_m))) #kW/m2
Power_output = np.zeros((len(day),len(LT_h),len(LT_m))) #kW
for i in range (0, len(LT_h)):
    for j in range (0, len(LT_m)):
        for n in range(0,len(day)):
            module_irradiance[n,i,j] = global_irradiance[n,i,j] * ( math.cos(elevation_angle_r[n,i,j])*math.sin(tilt_angle_r)*math.cos(azimuth_panel_r-azimuth_sun_r[n,i,j]) + math.sin(elevation_angle_r[n,i,j])*math.cos(tilt_angle_r))
            if module_irradiance[n,i,j]<0:
                module_irradiance[n,i,j] = 0
daylight_min_daily=np.zeros(len(day))
daylight_hr_daily=np.zeros(len(day))
for i in range (0, len(LT_h)):
    for j in range (0, len(LT_m)):
        for n in range(0,len(day)):
            if elevation_angle_r[n,i,j]>0:
                daylight_min_daily[n] = daylight_min_daily[n]+1
                daylight_hr_daily[n] = daylight_min_daily[n]/60
cloud_coverage=np.zeros(len(day))     
correction_factor=np.zeros(len(day)) 
k=0.4   
for n in range(0, len(day)):
    cloud_coverage[n] = 1-sunshine_hr_monthly[city][int(n/30.34)]/30.34/daylight_hr_daily[n]
    correction_factor[n] = 1-(1-k)*cloud_coverage[n]
for i in range (0, len(LT_h)):
    for j in range (0, len(LT_m)):
        for n in range(0,len(day)):
            Power_output[n,i,j] = panels_nom_cap * inverter_eff * module_irradiance[n,i,j] * correction_factor[n]
print('Total Energy production in a year is: ',np.sum(Power_output)/60/1000 ,' MWh')
print('PV farm capacity factor is ',np.sum(Power_output)/60/8760/panels_nom_cap*100, ' %')

Power_output_mean_daily = np.zeros(len(day))
for n in range (0, len(day)):
    Power_output_mean_daily[n]= np.sum(Power_output[n,:,:])/60     #kWh/day  
Power_output_mean_hourly_Copenhagen = np.zeros(8760)
for n in range (0, len(day)):
    for i in range (0, len(LT_h)):
        Power_output_mean_hourly_Copenhagen[n*24 + i]= np.sum(Power_output[n,i,:])/60     #kWh/hr 
#plot
plt.plot(day, Power_output_mean_daily, color='orange', label=city)
plt.legend(loc="lower center")
plt.xlabel('Day')
plt.ylabel('Average solar power generation[kwh/day]')
plt.show()

