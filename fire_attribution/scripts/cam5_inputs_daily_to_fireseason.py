import os
import xarray as xr
import numpy as np

def fire_season(month):
    return (month >= 5) & (month <= 10)

for scen in ['HPB','HPB_NAT']:
    print(scen)
    for num in range(1,101):
        num_string = '0' + str(num) if num > 9 else '00' + str(num)
        if num == 100:
            num_string = '100'
            
        print(num_string)
        
        day = xr.open_dataset('/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/daily/inputs/FWI_inputs_'+scen+'_m'+num_string+'_1951-2021.nc')
        
        months_selected = day.sel(time=fire_season(day['time.month']))
        fire_season_da = months_selected.resample(time ='A').mean('time')
        
        fire_season_da.to_netcdf('/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/6m_fire_season/inputs/FWI_inputs_'+scen+'_m'+num_string+'.nc')

        
