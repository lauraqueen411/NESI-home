import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import warnings
import datetime
warnings.filterwarnings("ignore")

for scen in ['HPB','HPB_NAT']:
    print(scen)
    for num in range(1,101):
        num_string = '0' + str(num) if num > 9 else '00' + str(num)
        if num == 100:
            num_string = '100'

        print(num_string)

        day_FWI = xr.open_dataarray('/nesi/project/niwa00015/queenle/data/fire/d4pdf/FWI/daily/BC_wind_FWI/BC_wind_FWI_'+scen+'_m'+num_string+'.nc')

        d4pdf_percentile = day_FWI.groupby('time.year').quantile(0.95,dim='time')
        d4pdf_percentile['year'] = [datetime.datetime(year, 1, 1) for year in d4pdf_percentile.year]
        d4pdf_percentile = d4pdf_percentile.rename({'year':'time'})
        
        
        d4pdf_percentile.to_netcdf('/nesi/project/niwa00015/queenle/data/fire/d4pdf/FWI/95percentile/BC_wind_FWI/BC_wind_95_p_FWI_'+scen+'_m'+num_string+'.nc')

