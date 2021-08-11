# libraries
from netrc import netrc
import pandas as pd
from pydap.cas.urs import setup_session
import xarray as xr
from tqdm import tqdm
import os
import numpy as np


# authentification
urs = 'urs.earthdata.nasa.gov'
netrcDir = os.path.expanduser("~/.netrc")
netrc_auth = netrc(netrcDir).authenticators(urs)
username = netrc_auth[0]
password = netrc_auth[2]
basepath = 'https://goldsmr5.gesdisc.eosdis.nasa.gov/opendap/hyrax/MERRA2/M2I3NVASM.5.12.4'
basepath = 'https://goldsmr5.gesdisc.eosdis.nasa.gov/opendap/MERRA2/M2I3NVASM.5.12.4'
outpath = '/projekt4/hochatm/MERRA2-3h_stations/'

# constants
pr = pd.period_range(start='1980-01-01',end='2020-12-31', freq='D')
station_dict = {'Rothera': {'ref_lat': -68, 'ref_lon': -68}, 
                'RioGrande': {'ref_lat': -53.785, 'ref_lon': -67.751}, 
                'Davis': {'ref_lat': -68.576, 'ref_lon': 77.969}}  
rmr = 300.0   # meteor radar measurement radius
var_ls = ['T','U','V','H','PL']


store_ls = []
url_ls = []
for dt in pr:#tqdm(pr, total = pr.shape[0]):    # get recent year and month
    year = int(dt.strftime('%Y'))
    month = dt.strftime('%m')
    day = dt.strftime('%d')
    
    if year >= 1980 and year < 1992:
        file_number = '100'
    elif year >= 1992 and year < 2001:
        file_number = '200'
    elif year >= 2001 and year < 2011:
        file_number = '300'
    elif year >= 2011:
        file_number = '400'
    elif year == 2000 and  month == '09':
        file_number = '401'
    else:
        raise Exception('The specified year is out of range.')

    
    infile = f'MERRA2_{file_number}.inst3_3d_asm_Nv.{year}{month}{day}.nc4'
    dataset_url = os.path.join(basepath, 
                           str(year),
                           month,
                           infile)
    url_ls.append(dataset_url)
    
    try:
        session = setup_session(username, password, check_url=dataset_url)    
        store = xr.backends.PydapDataStore.open(dataset_url, session=session)
        store_ls.append(store)


        ds = xr.open_dataset(store)[var_ls]

        lons = ds.lon
        lats = ds.lat

        for station in tqdm(station_dict, total = 3):
            ref_lat = station_dict[station]['ref_lat']
            ref_lon = station_dict[station]['ref_lon']

            dlon=rmr/(111.0*np.cos(ref_lat*np.pi/180.0))
            dlat=rmr/111.0

            idlon=(lons>=ref_lon-dlon) & (lons<=ref_lon+dlon)
            idlat=(lats>=ref_lat-dlat) & (lats<=ref_lat+dlat)
            ds_sel = ds.sel(lon = lons[idlon], lat = lats[idlat])

            outfile =  os.path.join(outpath, 
                                    station,
                                    infile)
            ds_sel.to_netcdf(outfile)
    except:
        print(dataset_url)
        #sys.exit()
    
#ds = xr.open_mfdataset(store_ls)[var_ls]
#ds