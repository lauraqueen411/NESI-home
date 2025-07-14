import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from idlpy import *

def get_obs_data(var,season, mem, resample_interval):
    
    file_name_setup = [var+'_Aday_d4PDF_HPB_m','_1951-2011.nc']
        
    da = xr.open_dataarray("/nesi/project/niwa00015/queenle/data/hydro_fingerprinting/model/d4PDF/gaussian/"+var+"/" + file_name_setup[0] + mem + "_gaussian_" + season + file_name_setup[1])

    if resample_interval != 'annual':
        da = da.resample(time=resample_interval).mean()

    da = da.sel(time=slice("1951","2010"))
    da = da.stack(pixel=("lat", "lon"))
    da = da.dropna("pixel", how="all")        
    
    array = da.values.flatten()
    
    del da
    
    return(array)

def get_mean_and_noise(var,season,scen, mem, resample_interval):
    
    if scen == 'HPB':
        file_name_setup = [var+'_Aday_d4PDF_HPB_m','_1951-2011.nc']
    if scen == 'HPB_NAT':
        file_name_setup = [var+'_Aday_d4PDF_HPB_NAT_m','_1951-2010.nc']

    ens_mean_sub_member = xr.open_dataarray('/nesi/project/niwa00015/queenle/data/hydro_fingerprinting/model/d4PDF/gaussian/'+var+'/means/' + file_name_setup[0][:-1] + 'EnsMeanSub_m' + mem + "_gaussian_" + season + file_name_setup[1])
    
    if resample_interval != 'annual':
        ens_mean_sub_member = ens_mean_sub_member.resample(time=resample_interval).mean()
        
    ens_mean_sub_member = ens_mean_sub_member.sel(time=slice("1951","2010"))
    
    noise = []
    for ens_mem in range(1,101):
        if ens_mem == 100:
            number = '100'
        else:
            number = '00' + str(ens_mem) if ens_mem < 10 else '0' + str(ens_mem)

        if number == mem:
            continue

        mem_da = xr.open_dataarray("/nesi/project/niwa00015/queenle/data/hydro_fingerprinting/model/d4PDF/gaussian/"+var+"/" + file_name_setup[0] + number + "_gaussian_" + season + file_name_setup[1])

        if resample_interval != 'annual':
            mem_da = mem_da.resample(time=resample_interval).mean()
            
        mem_da = mem_da.sel(time=slice("1951","2010"))
        
        diff = mem_da - ens_mean_sub_member

        diff = diff.stack(pixel=("lat", "lon"))# Create a MultiIndex
        diff = diff.dropna("pixel", how="all")# Drop the pixels that only have NA values.
                
        diff_array = diff.values.flatten()
        noise.append(diff_array)
        
        del mem_da
        del diff_array

    ens_mean_sub_member = ens_mean_sub_member.stack(pixel=("lat", "lon"))# Create a MultiIndex
    ens_mean_sub_member = ens_mean_sub_member.dropna("pixel", how="all")# Drop the pixels that only have NA values.
    ens_mean_array = ens_mean_sub_member.values.flatten()

    del ens_mean_sub_member
    
    return((ens_mean_array, np.array(noise)))


def scan_optimal_fingerprinting(var,season,number,resample_interval):
    
    IDL.retall

    all_ens_mean,noise_all = get_mean_and_noise(var,season,'HPB', number, resample_interval)
    nat_ens_mean,noise_nat = get_mean_and_noise(var,season,'HPB_NAT', number, resample_interval)

    data_obs = get_obs_data(var,season, number, resample_interval)
    data_scen = np.array([all_ens_mean,nat_ens_mean])

    data_noise_1 = np.concatenate((noise_all[:49],noise_nat[:49]))
    data_noise_2 = np.concatenate((noise_all[50:],noise_nat[50:]))

    trunc = np.array([i for i in range(3,98)])

    IDL.data_obs = data_obs
    IDL.data_scen = data_scen
    IDL.data_noise_1 = data_noise_1
    IDL.data_noise_2 = data_noise_2
    IDL.trunc = trunc
    IDL.scan_beta_est = []

    IDL.run("gendetec, data_obs, data_scen, data_noise_1, beta_est, scan_resid_sumsq=scan_resid_sumsq, \
            data_noise_2=data_noise_2,transform=['1*0','1*0+1*1'], trunc=trunc, scan_beta_est=scan_beta_est")

    #beta_est = IDL.beta_est
    scan_beta_est = IDL.scan_beta_est
    
    return scan_beta_est


def perfect_model_test(var, number, resample_interval, trunc):
    
    seasons = ['summer','autumn','winter','spring']

    fig,axs = plt.subplots(2,2, figsize=(12,10))
    axs = axs.flatten()

    seasonal_results = []
    for i,s in enumerate(seasons):    
        print(s)

        scan_beta_est = scan_optimal_fingerprinting(var,s,number,resample_interval)

        for j in range(len(scan_beta_est)):

            beta_est = scan_beta_est[j]
            best_1,low_1,up_1 = beta_est[0][0],beta_est[1][0],beta_est[2][0]
            best_2,low_2,up_2 = beta_est[0][1],beta_est[1][1],beta_est[2][1]

            axs[i].scatter([j+3]*3,[low_2,best_2,up_2],c='blue',alpha=0.7,label='nat' if j == 0 else '')
            axs[i].scatter([j+3]*3,[low_1,best_1,up_1],c='red',label='ant' if j == 0 else '')

            axs[i].vlines(j+3,low_2,up_2,colors=['blue'])
            axs[i].vlines(j+3,low_1,up_1,colors=['red'])

            axs[i].axhline(0,-0.5,1.5)
            axs[i].axhline(1,-0.5,1.5)


        axs[i].set_title(s)
        axs[i].legend()

        #['ensemble_member','season','ant_upper','ant_lower','ant_best','nat_upper','nat_lower','nat_best']
        seasonal_results.append(number+','+s+','+
                                 str(scan_beta_est[t-3][2][0])+','+str(scan_beta_est[t-3][1][0])+','+str(scan_beta_est[t-3][0][0])+','+
                                 str(scan_beta_est[t-3][2][1])+','+str(scan_beta_est[t-3][1][1])+','+str(scan_beta_est[t-3][0][1]))

        
    plt.savefig('/nesi/project/niwa00015/queenle/plots/d4PDF/perfect_model/'+var+'/'+resample_interval+'/' + 'PM_ens_' + number + '.png')
    plt.close(fig)
    
    return seasonal_results


def plot_summary(var,t,resample_interval):
    
    summary_df = pd.read_csv("/nesi/project/niwa00015/queenle/data/hydro_fingerprinting/model/d4PDF/summary_csv/"+var+"_" +resample_interval + "_trunc_" + str(t) + ".csv")
        
    for sort_type in ['nat_best','ant_best']:

        fig,axs = plt.subplots(2,2, figsize=(12,10))
        axs = axs.flatten()

        for i,s in enumerate(['summer','autumn','winter','spring']):

            sorted_df = summary_df[summary_df.season==s].sort_values(by=sort_type)

            axs[i].scatter([i for i in range(len(sorted_df.nat_upper))],sorted_df.nat_upper,c='blue',label='nat')
            axs[i].scatter([i for i in range(len(sorted_df.nat_lower))],sorted_df.nat_lower,c='blue',label='')
            axs[i].scatter([i for i in range(len(sorted_df.nat_best))],sorted_df.nat_best,c='blue',label='')

            axs[i].scatter([i for i in range(len(sorted_df.ant_upper))],sorted_df.ant_upper,c='red',label='ant')
            axs[i].scatter([i for i in range(len(sorted_df.ant_lower))],sorted_df.ant_lower,c='red',label='')
            axs[i].scatter([i for i in range(len(sorted_df.ant_best))],sorted_df.ant_best,c='red',label='')

            axs[i].vlines([i for i in range(len(sorted_df.nat_lower))],sorted_df.nat_lower,sorted_df.nat_upper,colors=['blue'],label='')
            axs[i].vlines([i for i in range(len(sorted_df.ant_lower))],sorted_df.ant_lower,sorted_df.ant_upper,colors=['red'],label='')

            axs[i].axhline(0,-0.5,1.5)
            axs[i].axhline(1,-0.5,1.5)

            axs[i].set_title(s + ', trunc = ' + str(t))

            axs[i].legend()

        plt.savefig('/nesi/project/niwa00015/queenle/plots/d4PDF/perfect_model/'+var+'/' + resample_interval + '/' + 'PM_ensemble_summary_'+sort_type+'_sort.png')

        plt.close(fig)


'''
MAIN function for performing perfect_model testing for one variable in d4PDF
'''

var = input("variable [TA, PRECIPI, ROFS]:")
t = int(input("truncation [3,98]:"))
resample_interval = input("resample_interval [annual,5Y,10Y]:")

with open("/nesi/project/niwa00015/queenle/data/hydro_fingerprinting/model/d4PDF/summary_csv/"+var+"_" +resample_interval + "_trunc_" + str(t) + ".csv", 'w') as file:
    file.write('ensemble_member,season,ant_upper,ant_lower,ant_best,nat_upper,nat_lower,nat_best')

    for member in range(1,101):
            
        print(member)

        if member == 100:
            number = '100'
        else:
            number = '00' + str(member) if member < 10 else '0' + str(member)

        seasonal_results = perfect_model_test(var,number,resample_interval,t)

        for result in seasonal_results:
            file.write('\n' +result)

        del seasonal_results          
            
plot_summary(var,t,resample_interval)
