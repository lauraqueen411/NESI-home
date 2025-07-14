import os
import xarray as xr
import matplotlib.pyplot as plt

'''
Set up ERA5 wind for model bias correction
'''

era5_da = xr.open_dataset('/nesi/project/niwa00015/queenle/data/fire/ERA5/model-style/inputs_1951-2021.nc').wind
model_da = xr.open_dataset('/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/daily/inputs/FWI_inputs_HPB_ensMean_1951-2021.nc').wind

era5_da['longitude'] = [lon + 360 for lon in era5_da.longitude.data]
print('coarsening')
era5_da = era5_da.coarsen(latitude=3,longitude=3,boundary='pad').mean()
print('interpolating')
era5_da = era5_da.interp(longitude=model_da.lon, latitude=model_da.lat, method="linear")
print('masking')
era5_da = era5_da.where(~model_da.isnull())

def bias_correct(scen, number):
    model_da = xr.open_dataset('/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/daily/inputs/FWI_inputs_'+scen+'_'+number+'_1951-2021.nc').wind

    BC_da = (model_da / model_da.mean('time'))*era5_da.mean('time')
    BC_da = BC_da.rename('wind')
    BC_da.to_netcdf('/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/daily/inputs/BC_wind/BC_WIND_'+scen+'_'+number+'_1951-2021.nc')

for scen in ['HPB','HPB_NAT']:
    print(scen)
    for ens_mem in range(1,101):
        print(ens_mem)
        if ens_mem == 100:
            number = 'm100'
        else:
            number = 'm00' + str(ens_mem) if ens_mem < 10 else 'm0' + str(ens_mem)

        bias_correct(scen, number)
