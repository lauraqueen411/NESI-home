import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib
import scipy.stats
import pymannkendall as mk

def get_linregress_slope(arr):
    if (np.isnan(arr)).any():
        result = np.nan
    else:
        result = np.polyfit([i for i in range(len(arr))],arr,deg=1)[0]
        
    return(result)

def get_variance(arr):
    return(scipy.stats.variation(arr))

def get_mannkendall_slope(arr):
    if (np.isnan(arr)).any():
        result = np.nan
    else:
        result = mk.original_test(arr).slope
        
    return(result)
   
def get_mannkendall_p(arr):
    if (np.isnan(arr)).any():
        result = np.nan
    else:
        result = mk.original_test(arr).p
        
    return(result)

'''
plot maps for inputs
'''

def fire_season(month):
    return (month >= 5) & (month <= 10)

in_path = '/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/daily/inputs/'
out_path = '/nesi/project/niwa00015/queenle/plots/fire/inputs/ensemble_members/maps/'
cmap = matplotlib.cm.get_cmap('viridis_r', 4)

range_dict = {'ta':[-0.03,0.03],
              'precipi':[-0.02,0.02],
              'wind':[-0.02,0.02],
              'rha':[-0.1,0.1]}

for ens_mem in range(1,102):
    print(ens_mem)
    if ens_mem == 100:
        number = 'm100'
    else:
        number = 'm00' + str(ens_mem) if ens_mem < 10 else 'm0' + str(ens_mem)
    if ens_mem == 101:
        number = 'ensMean'
        
    ALL_ds = xr.open_dataset(in_path+'HPB/FWI_inputs_HPB_'+number+'_1951-2021.nc')
    ALL_months_selected = ALL_ds.sel(time=fire_season(ALL_ds['time.month']))
    ALL_fire_season = ALL_months_selected.resample(time ='A').mean('time')
    
    NAT_ds = xr.open_dataset(in_path+'HPB_NAT/FWI_inputs_HPB_NAT_'+number+'_1951-2021.nc')
    NAT_months_selected = NAT_ds.sel(time=fire_season(NAT_ds['time.month']))
    NAT_fire_season = NAT_months_selected.resample(time ='A').mean('time')

    for var in ['ta','precipi','wind','rha']:

        fig,axs = plt.subplots(2,2, figsize=(12,10),sharex=True)
        axs = axs.flatten()
    
        all_da = ALL_fire_season[var]
        nat_da = NAT_fire_season[var]
        ant_da = all_da - nat_da

        xr.apply_ufunc(get_linregress_slope, all_da, input_core_dims=[["time"]], vectorize = True).plot(ax=axs[0],vmin=range_dict[var][0],vmax=range_dict[var][1],cmap='RdBu_r')
        xr.apply_ufunc(get_linregress_slope, nat_da, input_core_dims=[["time"]], vectorize = True).plot(ax=axs[1],vmin=range_dict[var][0],vmax=range_dict[var][1],cmap='RdBu_r')
        xr.apply_ufunc(get_linregress_slope, ant_da, input_core_dims=[["time"]], vectorize = True).plot(ax=axs[2],vmin=range_dict[var][0],vmax=range_dict[var][1],cmap='RdBu_r')
        im = xr.apply_ufunc(get_mannkendall_p, ant_da, input_core_dims=[["time"]], vectorize = True).plot(ax=axs[3],vmin=0,vmax=0.4,cmap=cmap)#,norm=norm)

        axs[0].text(0.1,0.8,'ALL Trend',transform=axs[0].transAxes)
        axs[1].text(0.1,0.8,'NAT Trend',transform=axs[1].transAxes)
        axs[2].text(0.1,0.8,'ANT Trend',transform=axs[2].transAxes)
        axs[3].text(0.1,0.8,'ANT Trend p-values',transform=axs[3].transAxes)

        plt.savefig(out_path + var + '/' + var + '_' + number + '_maps.png')
        plt.close()
        
