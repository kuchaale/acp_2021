# libraries
from netrc import netrc
import pandas as pd
from pydap.cas.urs import setup_session
import xarray as xr
from tqdm import tqdm
import os
import numpy as np
import sys

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
dataset_url = sys.argv[1]
infile = dataset_url.split('/')[-1]
#print(infile)
try:
    session = setup_session(username, password, check_url=dataset_url)    
    store = xr.backends.PydapDataStore.open(dataset_url, session=session)

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