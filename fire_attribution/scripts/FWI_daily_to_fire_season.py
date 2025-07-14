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
        
        day_FWI = xr.open_dataarray('/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/daily/FWI_'+scen+'_m'+num_string+'.nc')
        
        months_selected = day_FWI.sel(time=fire_season(day_FWI['time.month']))
        fire_season_da = months_selected.resample(time ='A').mean('time')
        
        fire_season_da.to_netcdf('/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/6m_fire_season/FWI_'+scen+'_m'+num_string+'.nc')

        
