import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import scipy
import cartopy.crs as ccrs
import geopandas as gpd
import rioxarray
import cartopy.feature as cf
from rasterio.enums import Resampling

# load SEASONAL observed flow data
seasonal_flow_df = pd.read_csv('/nesi/project/niwa00015/queenle/data/flows/seasonal/50yrs/new_full_records.csv')
seasonal_flow_df.date = pd.to_datetime(seasonal_flow_df.date)
seasonal_flow_df.set_index('date', inplace=True)
seasonal_flow_df = seasonal_flow_df['1969':'2019'] 

# load metadata
metadata_df = pd.read_csv('/nesi/project/niwa00015/queenle/data/metadata/40_50yr_sites.csv')
metadata_df.set_index('Number',inplace=True)
subset_meta = metadata_df.loc[[int(s) for s in seasonal_flow_df.columns]]
subset_meta.sort_values('gauge_lat', ascending = False, inplace=True)
subset_meta['number_label'] = np.arange(1,len(subset_meta)+1)
subset_meta['number_copy'] = subset_meta.index.values.tolist()
meta_df = gpd.GeoDataFrame(subset_meta,geometry=gpd.points_from_xy(x=subset_meta.gauge_lon, y=subset_meta.gauge_lat),crs='EPSG:4326')

# load catchment shape data
fp = '/nesi/project/niwa00015/queenle/data/arcgis/'
file = 'NESTCAT_v2_NZTM.shp'
catchment_data = gpd.read_file(fp+file)
catchment_data = catchment_data.to_crs("EPSG:4326")
catchment_data = catchment_data.loc[catchment_data['SITE'].isin(seasonal_flow_df.columns)]
catchment_data.index = catchment_data['SITE']


'''
loop through each ensemble member, interpolate to high-resolution grid, clip by each catchment, save catchment-averaged time series
in csv in /catchment_resolution directory 
'''

var = 'ROF'
direc = '/nesi/project/niwa00015/queenle/data/hydro_fingerprinting/model/d4PDF/gaussian/'

for scen in ['HPB','HPB_NAT']:

    print(scen)

    for s in ['winter','spring','summer','autumn']:
        print(s)

        for ens_mem in range(1,101):

            print(ens_mem)

            if ens_mem == 100:
                number = '100'
            else:
                number = '00' + str(ens_mem) if ens_mem < 10 else '0' + str(ens_mem)

            ens_mem_season = xr.open_dataarray(direc+var+"/full/"+var+'_Amon_d4PDF_'+scen+'_m'+number+"_gaussian_"+s+'_1951-2021.nc')
            
            ens_mem_season = ens_mem_season.rio.write_crs("EPSG:4326")
            ens_mem_season = ens_mem_season.transpose('time','lat','lon')
            ens_mem_season = ens_mem_season.rio.set_spatial_dims('lon','lat')

            mem_interp = ens_mem_season.rio.reproject(ens_mem_season.rio.crs,shape=(150,150),resampling=Resampling.bilinear)

            df_dict = {'time':ens_mem_season.time.values}

            for site in seasonal_flow_df.columns:
                try:
                    catchment_geo = catchment_data.loc[[float(site)]]
                    model_catchment = ex_interp.rio.clip(catchment_geo.geometry,catchment_data.crs,all_touched=True)

                    df_dict[site] = model_catchment.mean(['x','y']).values

                except KeyError as e:
                    print(e)

            df = pd.DataFrame(df_dict)
            df.to_csv(direc+var+"/full/catchment_resolution/"+var+'_d4PDF_'+scen+'_m'+number+"_gaussian_"+s+'_1951-2021.nc')

