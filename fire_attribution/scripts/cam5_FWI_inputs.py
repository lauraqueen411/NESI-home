import xarray as xr
import time
import os
from os import listdir
from os.path import isfile, join
import numpy as np
from metpy.calc import relative_humidity_from_specific_humidity
from metpy.units import units
import pandas as pd
import packaging as pk
import pint
import warnings
warnings.filterwarnings("ignore")

def join_years(var,scen,num_string):
    
    if var == 'ps':
        path = '/home/stoneda/data/C20C/LBNL/CAM5-1-1degree/All-Hist/est1/v2-0/mon/atmos/ps/run' + num_string + '/'
        
    else:
        path = file_setup[scen] + var + '/run' + num_string + '/'
        
    files = [f for f in listdir(path) if isfile(join(path, f))]

    da_list = []
    for file in files:

        da = xr.open_dataset(path+file)[var].sel(lat=slice(20,71), lon=slice(223,255)).where(lsm.sftlf > 0)
        da['time'] = da.indexes['time'].to_datetimeindex()

        da_list.append(da)

    full_da = xr.concat(da_list,'time')
    full_da = full_da.sortby('time')
    full_da = full_da.drop_duplicates('time')
    
    return(full_da)
        
def create_input_ds(scen,num_string):
    
    pr_da = join_years('pr',scen,num_string).drop('height')
    uas_da = join_years('uas',scen,num_string).drop('height')
    vas_da = join_years('vas',scen,num_string).drop('height')
    tasmax_da = join_years('tasmax',scen,num_string).drop('height')
    huss_da = join_years('huss',scen,num_string).drop('height')
    ps_da = join_years('ps',scen,num_string).drop('height')
    ps_da = ps_da.mean('time')

    # tasmax K to C
    tasmax_da = tasmax_da - 273.15

    # precip kg/m2/s to mm/hr
    pr_da = pr_da*(60*60*24)
        
    # wind m/s to km/h
    wind_da = np.sqrt(uas_da**2 + vas_da**2)
    wind_da = (wind_da * 60 * 60)/1000
    wind_da = wind_da.rename('wind')

    # rel. humidity from pressure, tasmax, specific humidity
    tasmax_da = tasmax_da.assign_attrs(units='degC')
    huss_da = huss_da.assign_attrs(units='kg/kg')
    ps_da = ps_da.assign_attrs(units='Pa')

    rh = relative_humidity_from_specific_humidity(ps_da, tasmax_da, huss_da).to('percent')

    # create dataset
    FWI_inputs = xr.merge([tasmax_da, pr_da, wind_da])
    FWI_inputs['rh'] = (['time','height','lat','lon'],rh)

    FWI_inputs.to_netcdf('/nesi/project/niwa00015/queenle/data/fire/CAM5-1-1/inputs/FWI_inputs_'+scen+'_run'+num_string+'_1959-2018.nc')
    
    
file_setup = {'All':'/home/stoneda/data/C20C/LBNL/CAM5-1-1degree/All-Hist/est1/v2-0/day/atmos/',
              'Nat':'/home/stoneda/data/C20C/LBNL/CAM5-1-1degree/Nat-Hist/CMIP5-est1/v2-0/day/atmos/'}

lsm = xr.open_dataset('/home/stoneda/data/C20C/LBNL/CAM5-1-1degree/All-Hist/est1/v2-0/fx/atmos/sftlf/run000/sftlf_fx_CAM5-1-1degree_All-Hist_est1_v2-0_run000_000000-000000.nc')

ens_list_dict = {'All':[i for i in range(1,11)] + [i for i in range(36,44)] + [i for i in range(61,71)] + [i for i in range(86,101)],
                 'Nat':[i for i in range(1,11)] + [i for i in range(36,51)] + [i for i in range(61,71)] + [i for i in range(86,96)] + [i for i in range(97,101)]}

scen = input('scenario (All, Nat): ')
runs = ens_list_dict[scen]

print(scen)
print(runs)
for num in runs: 
    print(num)

    t0 = time.time()
    num_string = '0' + str(num) if num > 9 else '00' + str(num)                                                             
    if num == 100: 
        num_string = '100'  
    
    if os.path.exists('/nesi/project/niwa00015/queenle/data/fire/CAM5-1-1/inputs/FWI_inputs_'+scen+'_run'+num_string+'_1959-2018.nc'):
        continue

    create_input_ds(scen, num_string)

    t1 = time.time()
    total = t1-t0
    print(total)

