import os
import xarray as xr
import numpy as np

'''
Mask global 2011-2021 d4PDF data to study region:
NZ
W North America: lat (19.9376, 71.045), lon (222.75, 255.375)
'''

print('input variable (TA_max, WIND, PRECIPI, RHA_min)')
var = input()

for scen in ['HPB','HPB_NAT']:    
    for num in range(1,101):
        num_string = '0' + str(num) if num > 9 else '00' + str(num)
        if num == 100:
            num_string = '100'
                
        infile = '/nesi/project/niwa02986/queenle/data/d4pdf/global/'+scen+'/day/' + var + '/' + var + '_Aday_d4PDF_'+scen+'_m'+num_string+'_2011-2021.nc'
        outfile = '/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/'+scen+'/'+var.split('_')[0]+'/decade/'+var.split('_')[0]+'_Aday_d4PDF_'+scen+'_m'+num_string+'_2011-2021.nc'
            
        os.system('cdo sellonlatbox,222.75,255.375,19.93757,71.04504 '+infile+' '+outfile)
