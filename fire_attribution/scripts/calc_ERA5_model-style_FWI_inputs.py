import xarray as xr
#from datetime import datetime
#import math
import numpy as np
#import geopandas as gpd
#import rioxarray as rio
#import matplotlib.pyplot as plt

'''
take hourly data and make daily in appropriate way
    - daily max temp (tasmax): daily max from hourly maximum t2m (mx2t)
    - daily u/v wind component: daily mean from hourly u/v
    - daily min dew point temp (min_dt): daily min from hourly d2m
    - daily precip (tp): daily sum from hourly tp
'''

def calc_hourly_windspeed(ds):
    
    u_da = ds['u10']
    v_da = ds['v10']
    
    wind_da = 3.6 * np.sqrt(u_da**2 + v_da**2)
    
    return(wind_da.rename('wind'))
    
def calc_hourly_rh(ds):
    t2m_da = ds['t2m'] - 273.15
    d2m_da = ds['d2m'] - 273.15
    
    rh_da = 100*np.exp((243.04*17.625*(d2m_da-t2m_da))/((243.04+t2m_da)*(243.04+d2m_da)))
    
    return(rh_da.rename('min_rh'))

def process_variables(date):
    ds = xr.open_dataset('/nesi/project/niwa00015/queenle/data/ERA5/hourly/post_1951/ERA5-hourly-' + date + '.nc')

    wind_hr = calc_hourly_windspeed(ds)
    wind_da = wind_hr.resample(time='D').mean()
    
    rh_hr = calc_hourly_rh(ds)
    rh_da = rh_hr.resample(time='D').min()

    tasmax_da = ds['mx2t'].resample(time='D').max() - 273.15
    tp_da = ds['tp'].resample(time='D').sum() * 1000

    out_ds = xr.merge([wind_da, rh_da, tasmax_da, tp_da])
    
    out_ds.to_netcdf('/nesi/project/niwa00015/queenle/data/ERA5/daily/d4pdf_style_FWI_inputs_' + date + '.nc') 
    
for year in range(1951,2022):
    print(year)
    for month in range(1,13):
        date = str(year) + '-' + '0' + str(month) if month < 10 else str(year) + '-' + str(month)
        
        process_variables(date)
        
