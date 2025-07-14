import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

'''
PLOTTING NATURALIZED TA AND RH
'''

ALL_ds = xr.open_dataset('/nesi/project/niwa00015/queenle/data/fire/d4pdf/FWI/6month_fire_season/inputs/BC_wind/FWI_inputs_HPB_ensMean.nc')
NAT_ds = xr.open_dataset('/nesi/project/niwa00015/queenle/data/fire/d4pdf/FWI/6month_fire_season/inputs/BC_wind/FWI_inputs_HPB_NAT_ensMean.nc')
ex_mem_da = xr.open_dataset("/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/daily/inputs/FWI_inputs_HPB_m001_1951-2021.nc")['ta']
beta_est_df = pd.read_csv('/home/queenle/fire_attribution/result_files/d4pdf_beta_est_trunc_60_1951_2021.csv')
beta_est_df.set_index('type',inplace=True)

titles = {'ta':'temp','rha':'rel. humidity'}

tasmax_ANT_da = ALL_ds['ta'] - NAT_ds['ta']
tasmax_daily_ANT = tasmax_ANT_da.reindex_like(ex_mem_da, method="bfill")
rh_ANT_da = ALL_ds['rha'] - NAT_ds['rha']
rh_daily_ANT = rh_ANT_da.reindex_like(ex_mem_da, method="bfill")
ANT_dict = {'ta':tasmax_daily_ANT,'rha':rh_daily_ANT}

scen='HPB'
for ens_mem in range(1,101):

    print(ens_mem)

    if ens_mem == 100:
        number = '100'
    else:
        number = '00' + str(ens_mem) if ens_mem < 10 else '0' + str(ens_mem)
        
    mem_ds = xr.open_dataset("/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/daily/inputs/FWI_inputs_"+scen+"_m"+number+"_1951-2021.nc")
    #mem_ds = mem_ds.rename({'lon':'longitude','lat':'latitude'})
    fig,axs = plt.subplots(2,2,figsize=(14,8))
    for i,var in enumerate(['ta','rha']):
        scaling_factor = beta_est_df.loc['best_ant'][titles[var]]
        daily_ANT = ANT_dict[var]
        mem_da = mem_ds[var]
        nat_mem = xr.open_dataarray('/nesi/nobackup/niwa00015/queenle/d4PDF/daily/naturalized/'+var+'_'+scen+'_m'+number+'_1951-2021.nc')

        mem_da.mean(['lat','lon']).resample(time='A').mean().plot(ax=axs[i][0],label='ALL mem')
        nat_mem.mean(['latitude','longitude']).resample(time='A').mean().plot(ax=axs[i][0],label='naturalized mem')
        (scaling_factor * daily_ANT).mean(['latitude','longitude']).plot(ax=axs[i][0],label='scaled ANT signal')
        
        mem_da.mean(['lat','lon']).plot(ax=axs[i][1],label='ALL mem')
        nat_mem.mean(['latitude','longitude']).plot(ax=axs[i][1],label='naturalized mem')
        (scaling_factor * daily_ANT).mean(['latitude','longitude']).plot(ax=axs[i][1],label='scaled ANT signal')

    axs[0][0].legend()
    axs[0][0].set_title('Annual')
    axs[0][1].set_title('Daily')
    plt.savefig('/home/queenle/fire_attribution/figures/plots/naturalized_ta_rh/d4pdf/m'+number+'.png')
    plt.close()
    
    
    
