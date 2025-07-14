import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

def write_natural_member(var, scen, number, daily_ANT):

    mem_ds = xr.open_dataset("/nesi/project/niwa00015/queenle/data/fire/CAM5-1-1/daily/inputs/FWI_inputs_"+scen+"_run"+number+"_1959-2018.nc")
    mem_da = mem_ds[var]
    
    nat_mem = mem_da - daily_ANT

    nat_mem.to_netcdf('/nesi/nobackup/niwa00015/queenle/CAM5/daily/naturalized/'+var+'_'+scen+'_run'+number+'_1959-2018.nc')

'''
NATURALIZE CAM5 TEMP AND RH
'''

ALL_ds = xr.open_dataset('/nesi/project/niwa00015/queenle/data/fire/CAM5-1-1/6month_fire_season/inputs/FWI_inputs_All_ensMean.nc')
NAT_ds = xr.open_dataset('/nesi/project/niwa00015/queenle/data/fire/CAM5-1-1/6month_fire_season/inputs/FWI_inputs_Nat_ensMean.nc')
ex_mem_da = xr.open_dataset("/nesi/project/niwa00015/queenle/data/fire/CAM5-1-1/daily/inputs/FWI_inputs_All_run001_1959-2018.nc")['tasmax']
beta_est_df = pd.read_csv('/home/queenle/fire_attribution/result_files/cam5_beta_est_trunc_30_1959_2014.csv')
beta_est_df.set_index('type',inplace=True)

titles = {'tasmax':'temp','rh':'rel. humidity'}

var = input('tasmax or rh: ')
print('naturalizing cam5 ' + var)

ALL_da = ALL_ds[var]
NAT_da = NAT_ds[var]

ANT_da = ALL_da - NAT_da
daily_ANT = ANT_da.reindex_like(ex_mem_da, method="bfill")

runs = [i for i in range(1,11)] + [i for i in range(36,44)] + [i for i in range(61,71)] + [i for i in range(86,101)]
for scen in ['All']:
    for ens_mem in runs:
        
        print(ens_mem)

        if ens_mem == 100:
            number = '100'
        else:
            number = '00' + str(ens_mem) if ens_mem < 10 else '0' + str(ens_mem)

        write_natural_member(var, scen, number, daily_ANT)


