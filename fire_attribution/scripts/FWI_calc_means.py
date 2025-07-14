import os

def file_list_sub_member(num, scen, direct):
    direc = '/nesi/project/'
    string = ''
    for mem in range(1,101):
        if mem == num:
            continue
            
        if mem == 100:
            number = 'm100'
        else:
            number = 'm00' + str(mem) if mem < 10 else 'm0' + str(mem)
            
        string += direct + 'FWI_' + scen + '_' + number + '.nc '
        
    return string

for scen in ['HPB','HPB_NAT']:

    direct = '/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/6m_fire_season/'
    for ens_mem in range(1,101):
            
        print(ens_mem)
        if ens_mem == 100:
            number = 'm100'
        else:
            number = 'm00' + str(ens_mem) if ens_mem < 10 else 'm0' + str(ens_mem)
            
        file_list = file_list_sub_member(ens_mem, scen, direct)
        
        os.system('cdo ensmean ' + file_list + direct + 'means/FWI_' + scen + '_ensMeanSub_' + number + '.nc')
                        
        

    
            
