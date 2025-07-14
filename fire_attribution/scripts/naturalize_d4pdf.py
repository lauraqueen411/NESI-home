import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt


def write_natural_member(var, scen, number, ANT_signal):

    mem_ds = xr.open_dataset("/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/daily/inputs/FWI_inputs_"+scen+"_m"+number+"_1951-2021.nc")
    mem_da = mem_ds[var]
    mem_da = mem_da.rename({'lon':'longitude','lat':'latitude'})
    
    nat_mem = mem_da - ANT_signal
    
    nat_mem.to_netcdf('/nesi/nobackup/niwa00015/queenle/d4PDF/daily/naturalized/'+var+'_'+scen+'_m'+number+'_1951-2021.nc')

'''
NATURALIZE D4PDF-G TEMP AND RH
'''

ALL_ds = xr.open_dataset('/nesi/project/niwa00015/queenle/data/fire/d4pdf/FWI/6month_fire_season/inputs/BC_wind/FWI_inputs_HPB_ensMean.nc')
NAT_ds = xr.open_dataset('/nesi/project/niwa00015/queenle/data/fire/d4pdf/FWI/6month_fire_season/inputs/BC_wind/FWI_inputs_HPB_NAT_ensMean.nc')
ex_mem_da = xr.open_dataset("/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/daily/inputs/FWI_inputs_HPB_m001_1951-2021.nc")['ta']

titles = {'ta':'temp','rha':'rel. humidity'}

var = input('ta or rha: ')
print('naturalizing d4pdf ' + var)

ALL_da = ALL_ds[var]
NAT_da = NAT_ds[var]

ANT_da = ALL_da - NAT_da
daily_ANT = ANT_da.reindex_like(ex_mem_da, method="bfill")

for scen in ['HPB']:
    for ens_mem in range(1,101):
        
        print(ens_mem)

        if ens_mem == 100:
            number = '100'
        else:
            number = '00' + str(ens_mem) if ens_mem < 10 else '0' + str(ens_mem)

        write_natural_member(var, scen, number, daily_ANT)

