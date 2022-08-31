# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 13:55:54 2022

@author: Tomás Wierzba
"""

import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

headers_test = {'content-type': 'application/json'}
query_test = """ 
{
  electricityprodex5minrealtime(where: {Minutes5DK: {_gte: "2012-01-01T00:00:00", _lte: "2021-12-31T23:55:00"},PriceArea: {_eq: "DK2"}}, order_by: {Minutes5DK: desc}) {
    SolarPower
    Minutes5DK
    PriceArea
  }
}

"""
response_test = requests.post('https://data-api.energidataservice.dk/v1/graphql', json={'query': query_test}, headers=headers_test)
test_json = response_test.json()
data_test = pd.DataFrame(test_json['data']['electricityprodex5minrealtime'])

headers_test = {'content-type': 'application/json'}
query_test = """ 
{
  electricityprodex5minrealtime(where: {Minutes5DK: {_gte: "2021-01-01T00:00:00", _lte: "2021-01-18T17:35:00"},PriceArea: {_eq: "DK2"}}, order_by: {Minutes5DK: desc}) {
    SolarPower
    Minutes5DK
    PriceArea
  }
}

"""
response_test = requests.post('https://data-api.energidataservice.dk/v1/graphql', json={'query': query_test}, headers=headers_test)
test_json = response_test.json()
data_test2 = pd.DataFrame(test_json['data']['electricityprodex5minrealtime'])

solar_data_2021 = [[0]*72,[0]*72,[0]*72]
for n in range(0,8333):
    for i in range(0,3):
        solar_data_2021[i][n] = data_test.iat[5+n*12,i]
for n in range(8333,8759):
    for i in range(0,3):
        solar_data_2021[i][n] = data_test2.iat[1+(n-8333)*12,i]
hours = np.linspace(1,8759,8759)  
hours2 = np.linspace(1,8760,8760)   
Power_output_mean_hourly_Copenhagen = np.load('CPH_hr.npy')
def zero_to_nan(values):
    """Replace every 0 with 'nan' and return a copy."""
    return [float('nan') if x==0 else x for x in values]
plt.plot(hours, solar_data_2021[0][:], color='green', label='Real solar power generation in DK')
plt.plot(hours2, zero_to_nan(600*Power_output_mean_hourly_Copenhagen), color='purple', label='Model for Copenhagen',linestyle = 'dotted')
plt.legend(loc="upper center")
plt.xlabel('Hours')
plt.ylabel('Solar power generation[kwh/h]')
plt.show()

#difference in behaviour can be modelled with sunshine hours per month instead of per year