import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

ALL_ds = xr.open_dataset('/nesi/project/niwa00015/queenle/data/fire/CAM5-1-1/6month_fire_season/inputs/FWI_inputs_All_ensMean.nc')
NAT_ds = xr.open_dataset('/nesi/project/niwa00015/queenle/data/fire/CAM5-1-1/6month_fire_season/inputs/FWI_inputs_Nat_ensMean.nc')
ex_mem_da = xr.open_dataset("/nesi/project/niwa00015/queenle/data/fire/CAM5-1-1/daily/inputs/FWI_inputs_All_run001_1959-2018.nc")['tasmax']
beta_est_df = pd.read_csv('/home/queenle/fire_attribution/result_files/cam5_beta_est_trunc_30_1959_2014.csv')
beta_est_df.set_index('type',inplace=True)
titles = {'tasmax':'temp','rh':'rel. humidity'}

tasmax_ANT_da = ALL_ds['tasmax'] - NAT_ds['tasmax']
tasmax_daily_ANT = tasmax_ANT_da.reindex_like(ex_mem_da, method="bfill")

rh_ANT_da = ALL_ds['rh'] - NAT_ds['rh']
rh_daily_ANT = rh_ANT_da.reindex_like(ex_mem_da, method="bfill")

ANT_dict = {'tasmax':tasmax_daily_ANT,'rh':rh_daily_ANT}

runs = [i for i in range(1,11)] + [i for i in range(36,44)] + [i for i in range(61,71)] + [i for i in range(86,101)]
scen='All'
for ens_mem in runs:

    print(ens_mem)

    if ens_mem == 100:
        number = '100'
    else:
        number = '00' + str(ens_mem) if ens_mem < 10 else '0' + str(ens_mem)
        
    mem_ds = xr.open_dataset("/nesi/project/niwa00015/queenle/data/fire/CAM5-1-1/daily/inputs/FWI_inputs_"+scen+"_run"+number+"_1959-2018.nc")
    fig,axs = plt.subplots(2,2,figsize=(14,8))
    for i,var in enumerate(['tasmax','rh']):
        scaling_factor = beta_est_df.loc['best_ant'][titles[var]]
        daily_ANT = ANT_dict[var]
        mem_da = mem_ds[var]
        nat_mem = xr.open_dataarray('/nesi/nobackup/niwa00015/queenle/CAM5/daily/naturalized/'+var+'_'+scen+'_run'+number+'_1959-2018.nc')

        mem_da.mean(['lat','lon']).resample(time='A').mean().plot(ax=axs[i][0],label='ALL mem')
        nat_mem.mean(['lat','lon']).resample(time='A').mean().plot(ax=axs[i][0],label='naturalized mem')
        (scaling_factor * daily_ANT).mean(['lat','lon']).plot(ax=axs[i][0],label='scaled ANT signal')
        
        mem_da.mean(['lat','lon']).plot(ax=axs[i][1],label='ALL mem')
        nat_mem.mean(['lat','lon']).plot(ax=axs[i][1],label='naturalized mem')
        (scaling_factor * daily_ANT).mean(['lat','lon']).plot(ax=axs[i][1],label='scaled ANT signal')

    axs[0][0].legend()
    axs[0][0].set_title('Annual')
    axs[0][1].set_title('Daily')
    plt.savefig('/home/queenle/fire_attribution/figures/plots/naturalized_ta_rh/cam5/run'+number+'.png')
    plt.close()
    
