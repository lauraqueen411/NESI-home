import os
import xarray as xr
import numpy as np

'''
Merge 1951-2011 and 2011-2021 netcdfs
'''

var = input('input var (TA, WIND, PRECIPI, RHA):')

for scen in ['HPB','HPB_NAT']:
        
    for num in range(1,101):
        num_string = '0' + str(num) if num > 9 else '00' + str(num)
        if num == 100:
            num_string = '100'
            
        if scen == 'HPB':
            samfile = '/nesi/project/niwa02986/deansm/data/d4pdf/WNAmerica/'+scen+'/day/' + var + '/' + var + '_Aday_d4PDF_'+scen+'_m'+num_string+'_1951-2011.nc'
        elif scen == 'HPB_NAT':
            samfile = '/nesi/project/niwa02986/deansm/data/d4pdf/WNAmerica/'+scen+'/day/' + var + '/' + var + '_Aday_d4PDF_'+scen+'_m'+num_string+'_1951-2010.nc'

        laurafile = '/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/'+scen+'/'+var+'/decade/'+var+'_Aday_d4PDF_'+scen+'_m'+num_string+'_2011-2021.nc'
        outfile = '/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/'+scen+'/'+var+'/'+var+'_Aday_d4PDF_'+scen+'_m'+num_string+'_1951-2021.nc'
            
        os.system('cdo mergetime ' + samfile + ' ' + laurafile + ' ' + outfile)
