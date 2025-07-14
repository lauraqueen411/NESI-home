import xarray as xr
import time

def create_input_ds(scen,num_string):
    tasmax_ds = xr.open_dataset("/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/raw_inputs/"+scen+"/TA/TA_Aday_d4PDF_"+scen+"_m"+num_string+"_1951-2021.nc")
    rhmin_ds = xr.open_dataset("/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/raw_inputs/"+scen+"/RHA/RHA_Aday_d4PDF_"+scen+"_m"+num_string+"_1951-2021.nc")
    wind_ds = xr.open_dataset("/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/raw_inputs/"+scen+"/WIND/WIND_Aday_d4PDF_"+scen+"_m"+num_string+"_1951-2021.nc")
    pr_ds = xr.open_dataset("/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/raw_inputs/"+scen+"/PRECIPI/PRECIPI_Aday_d4PDF_"+scen+"_m"+num_string+"_1951-2021.nc")

    # merge variables into one dataset
    FWI_inputs = xr.merge([pr_ds.precipi, tasmax_ds.ta, rhmin_ds.rha, wind_ds.wind]).drop('lev')
    FWI_inputs = FWI_inputs.where(lsm.sftlf > 0)

    # temp K to C
    FWI_inputs["ta"] = FWI_inputs["ta"] - 273.15 # convert temp K to C
    # wind m/s to km/h
    FWI_inputs["wind"] = (FWI_inputs["wind"] * 60 * 60)/1000
    # precip kg/m2/s to mm/hr
    FWI_inputs["precipi"] = FWI_inputs["precipi"]*(60*60*24)

    FWI_inputs.to_netcdf("/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/FWI/inputs/"+scen+"/FWI_inputs_"+scen+"_m"+num_string+"_1951-2021.nc")

'''
Create FWI input netcdf for each ensemble member
'''

ex_da = xr.open_dataset("/nesi/project/niwa02986/queenle/data/d4pdf/WNAmerica/raw_inputs/HPB/TA/TA_Aday_d4PDF_HPB_m001_1951-2021.nc")
lons = ex_da.lon.data
lats = ex_da.lat.data
ex_da.close()

lsm = xr.open_dataset('/nesi/project/niwa02986/queenle/data/d4pdf/sftlf_fx_d4PDF_HPB_m000_000000-000000.nc')
lsm = lsm.isel(time=0).drop('time')
lsm = lsm.interp(lat=lats,lon=lons)

for scen in ['HPB','HPB_NAT']:
    for num in range(1,101):  
        t0 = time.time()
        num_string = '0' + str(num) if num > 9 else '00' + str(num)                                                             
        if num == 100: 
            num_string = '100'  
            
        create_input_ds(scen, num_string)
        
        t1 = time.time()
        total = t1-t0
        print(total)
