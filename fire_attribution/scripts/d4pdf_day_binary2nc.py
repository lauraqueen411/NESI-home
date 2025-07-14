import os



print('Enter variable (TA_max, RHA_min, PRECIPI, WIND):')
var = input()

for scen in ['HPB','HPB_NAT']:
    for num in range(1,101):
        num_string = '0' + str(num) if num > 9 else '00' + str(num)
        if num == 100:
            num_string = '100'

        if scen == 'HPB':
            in_file = '/nesi/nobackup/niwa02986/queenle/d4PDF/HPB/ctl_files/'+var+'_day_HPB_m'+num_string+'.ctl'
            out_file = '/nesi/project/niwa02986/queenle/data/d4pdf/global/HPB/day/' + var +'/'+var+'_Aday_d4PDF_HPB_m'+num_string+'_2011-2021.nc'

            os.system("cdo -f nc import_binary " + in_file + " " + out_file)

        if scen == 'HPB_NAT':
            in_file = '/nesi/nobackup/niwa02986/queenle/d4PDF/NAT/ctl_files/'+var+'_day_HPB_NAT_m'+num_string+'.ctl'
            out_file = '/nesi/project/niwa02986/queenle/data/d4pdf/global/HPB_NAT/day/' + var +'/'+var+'_Aday_d4PDF_HPB_NAT_m'+num_string+'_2011-2021.nc'

            os.system("cdo -f nc import_binary " + in_file + " " + out_file)

