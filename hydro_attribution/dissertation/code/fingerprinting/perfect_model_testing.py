#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from idlpy import *


# In[2]:


'''
Define dictionaries of meta-data for each model
'''

var_dict = {'ECHAM5':['tasmax','pr','mrro'],
            'HadGEM3':['tasmax','pr'],
            'd4PDF':['TA','PRECIPI','ROF']}

ensemble_members_dict = {'ECHAM5':['ens01', 'ens02', 'ens03', 'ens04', 'ens05', 'ens06', 'ens07', 'ens08', 'ens09', 'ens10', 'ens11', 'ens12', 'ens13', 'ens14', 'ens15', 'ens16', 'ens17', 'ens18', 'ens19', 'ens20', 'ens21', 'ens22', 'ens23', 'ens24', 'ens25',                                    'ens26', 'ens27', 'ens28', 'ens29', 'ens30', 'ens31', 'ens32', 'ens33', 'ens34', 'ens35', 'ens36', 'ens37', 'ens38', 'ens39', 'ens40', 'ens41', 'ens42', 'ens43', 'ens44', 'ens45', 'ens46', 'ens47', 'ens48', 'ens49', 'ens50'],
                         'HadGEM3':['r1i1p1','r1i1p11','r1i1p13','r1i1p15','r1i1p3','r1i1p5','r1i1p7','r1i1p9',
                                    'r1i1p10','r1i1p12','r1i1p14','r1i1p2','r1i1p4','r1i1p6','r1i1p8'],
                         'd4PDF':['m001', 'm002', 'm003', 'm004', 'm005', 'm006', 'm007', 'm008', 'm009', 'm010', 'm011', 'm012', 'm013', 'm014', 'm015', 'm016', 'm017', 'm018', 'm019', 'm020', 'm021', 'm022', 'm023', 'm024', 'm025', \
                                  'm026', 'm027', 'm028', 'm029', 'm030', 'm031', 'm032', 'm033', 'm034', 'm035', 'm036', 'm037', 'm038', 'm039', 'm040', 'm041', 'm042', 'm043', 'm044', 'm045', 'm046', 'm047', 'm048', 'm049', 'm050', \
                                  'm051', 'm052', 'm053', 'm054', 'm055', 'm056', 'm057', 'm058', 'm059', 'm060', 'm061', 'm062', 'm063', 'm064', 'm065', 'm066', 'm067', 'm068', 'm069', 'm070', 'm071', 'm072', 'm073', 'm074', 'm075', \
                                  'm076', 'm077', 'm078', 'm079', 'm080', 'm081', 'm082', 'm083', 'm084', 'm085', 'm086', 'm087', 'm088', 'm089', 'm090', 'm091', 'm092', 'm093', 'm094', 'm095', 'm096', 'm097', 'm098', 'm099', 'm100']}

trunc_dict = {'ECHAM5':np.array([i for i in range(3,48)]),
              'HadGEM3':np.array([i for i in range(3,13)]),
              'd4PDF':np.array([i for i in range(3,98)])}

time_window_dict = {'ECHAM5':('1979','2018'),
                    'HadGEM3':('1979','2015'),
                    'd4PDF':('1951','2020')}


'''
model,variable,season,trunc,ensemble_member,time_step,ant_upper,ant_lower,ant_best,nat_upper,nat_lower,nat_best,notes
'''

def write_results(file,model,var,ens_mem,season,time_step,scan_beta_est):
        
    trunc_list = trunc_dict[model]
    
    for i,result in enumerate(scan_beta_est):

        beta_est = result
        
        trunc = trunc_list[i]
        ant_best=beta_est[0][0]
        ant_lower=beta_est[1][0]
        ant_upper=beta_est[2][0]
        nat_best=beta_est[0][1]
        nat_lower=beta_est[1][1]
        nat_upper=beta_est[2][1]
        notes = ''
        
        line = model
        for value in [var,season,trunc,ens_mem,time_step,ant_upper,ant_lower,ant_best,nat_upper,nat_lower,nat_best,notes]:
            line += ','+str(value)
        
        file.write(line+'\n')


# In[5]:


def optimal_fingerprint(model,var,ens_mem,season,time_step):
    
    IDL.retall
    
    data_obs, data_scen, data_noise_1, data_noise_2 = get_data_arrays(model,var,ens_mem,season,time_step)
    trunc = trunc_dict[model]

    IDL.data_obs = data_obs
    IDL.data_scen = data_scen
    IDL.data_noise_1 = data_noise_1
    IDL.data_noise_2 = data_noise_2
    IDL.trunc = trunc
    IDL.scan_beta_est = []
    IDL.scan_p_resid = []
    IDL.scan_resid_sumsq = []
    IDL.p_resid = []
    IDL.resid_sumsq = []
    IDL.noise_singval = []
    IDL.z_best = []
    
    '''
    print(IDL.data_obs.shape)
    print(np.isnan(IDL.data_obs).any())
    print(IDL.data_scen.shape)
    print(np.isnan(IDL.data_scen).any())
    print(IDL.data_noise_1.shape)
    print(np.isnan(IDL.data_noise_1).any())
    print(IDL.data_noise_2.shape)
    print(np.isnan(IDL.data_noise_2).any())
    print(IDL.trunc)
    '''

    IDL.run("gendetec, data_obs, data_scen, data_noise_1, beta_est, scan_resid_sumsq=scan_resid_sumsq,             data_noise_2=data_noise_2,transform=['1*0','1*0+1*1'], trunc=trunc, scan_beta_est=scan_beta_est,            scan_p_resid=scan_p_resid,noise_singval=noise_singval,z_best=z_best")

    beta_est = IDL.beta_est
    scan_beta_est = IDL.scan_beta_est
    scan_p_resid = IDL.scan_p_resid
    scan_resid_sumsq = IDL.scan_resid_sumsq
    noise_singval = IDL.noise_singval
    z_best = IDL.z_best
        
    return(scan_beta_est)

def get_data_arrays(model,var,ens_mem,season,time_step):
    
    all_ens_mean,noise_all = get_mean_and_noise(model,var,ens_mem,season,time_step,'all')
    nat_ens_mean,noise_nat = get_mean_and_noise(model,var,ens_mem,season,time_step,'nat')
    
    data_obs = get_obs_data(model,var,ens_mem,season,time_step)
    data_scen = np.array([all_ens_mean,nat_ens_mean])

    break_point = int((len(ensemble_members_dict[model])-1)/2)
    
    data_noise_1 = np.concatenate((noise_all[:break_point],noise_nat[break_point:]))
    data_noise_2 = np.concatenate((noise_all[break_point:],noise_nat[:break_point]))

    return(data_obs,data_scen,data_noise_1,data_noise_2)


# In[6]:


def get_obs_data(model,var,ens_mem,season,time_step):
    
    da = xr.open_dataarray(input_dir+model+'/gaussian/'+var+'/seasonal/'+model+'_all_'+season+'_'+var+'_gaussian_'+ens_mem+'.nc')

    if time_step != 'annual':
        da = da.resample(time=time_step).mean()
        
    da = da.sel(time=slice(time_window_dict[model][0],time_window_dict[model][1]))
                
    da = da.stack(pixel=("lat", "lon"))
    da = da.dropna("pixel", how="all")        
    
    return(da.values.flatten())



def get_mean_and_noise(model,var,ens_mem,season,time_step,scenario):
    
    mean_sub_member = xr.open_dataarray(input_dir+model+'/gaussian/'+var+'/seasonal/means/'+model+'_'+scenario+'_'+season+'_'+var+'_gaussian_mean_sub_'+ens_mem+'_.nc')
    
    if time_step != 'annual':
        mean_sub_member = mean_sub_member.resample(time=time_step).mean()
        
    mean_sub_member = mean_sub_member.sel(time=slice(time_window_dict[model][0],time_window_dict[model][1]))
    
    mean_sub_member = mean_sub_member.stack(pixel=("lat", "lon")) 
    mean_sub_member = mean_sub_member.dropna("pixel", how="all") 
    mean_sub_member_array = mean_sub_member.values.flatten()
                                          
    noise = get_noise(model,var,season,time_step,scenario)
        
    return((mean_sub_member_array, noise))



def get_noise(model,var,season,time_step,scenario):
    
    ens_mean = xr.open_dataarray(input_dir+model+'/gaussian/'+var+'/seasonal/means/'+model+'_'+scenario+'_'+season+'_'+var+'_gaussian_ensMean.nc')
    
    if time_step != 'annual':
        ens_mean = ens_mean.resample(time=time_step).mean()
        
    ens_mean = ens_mean.sel(time=slice(time_window_dict[model][0],time_window_dict[model][1]))
    
    noise = []
    for mem_name in ensemble_members_dict[model]:

        if mem_name == ens_mem:
            continue

        mem_da = xr.open_dataarray(input_dir+model+'/gaussian/'+var+'/seasonal/'+model+'_'+scenario+'_'+season+'_'+var+'_gaussian_'+mem_name+'.nc')

        if time_step != 'annual':
            mem_da = mem_da.resample(time=time_step).mean()
            
        mem_da = mem_da.sel(time=slice(time_window_dict[model][0],time_window_dict[model][1]))
                            
        diff = mem_da - ens_mean
        
        diff = diff.stack(pixel=("lat", "lon"))
        diff = diff.dropna("pixel", how="all")
                
        noise.append(diff.values.flatten())
        
    return(np.array(noise))


# In[ ]:


'''
Main script for running optimal fingerprinting across perfect model ensemble
'''

model = input('Model (HadGEM3,ECHAM5,d4PDF): ')
start = int(input('start index: '))
end = int(input('end index: '))
variable = input('variable: ')
time_step = input('time step (annual, 5Y, 10Y): ')

input_dir = '/nesi/project/niwa00015/queenle/data/hydro_fingerprinting/model/'
result_file = '/nesi/project/niwa00015/queenle/results/'+model+'_'+variable+'_perfect_model_results.csv'

with open(result_file, "a") as file:
    #file.write('model,variable,season,trunc,ensemble_member,time_step,ant_upper,ant_lower,ant_best,nat_upper,nat_lower,nat_best,notes\n')
    
    print(model)
    for var in var_dict[model]:
        if var != variable:
            continue
        print(var)
        for ens_mem in ensemble_members_dict[model][start:end]:

            print(ens_mem)
            for season in ['winter','spring','summer','autumn']:

                print(season)
                scan_beta_est = optimal_fingerprint(model,var,ens_mem,season,time_step)
                
                write_results(file,model,var,ens_mem,season,time_step,scan_beta_est)
                
                file.flush()


# In[ ]:




