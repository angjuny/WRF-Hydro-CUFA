import os, glob, datetime
import numpy as np
import pandas as pd
import xarray as xr
import pyproj

def convert_xy2lonlat(XY, ds):
    WRF_proj = pyproj.Proj(proj = 'lcc', lat_1 = ds['crs'].standard_parallel[0], lat_2 = ds['crs'].standard_parallel[1], lat_0 = ds['crs'].latitude_of_projection_origin, lon_0 = ds['crs'].longitude_of_central_meridian, a = 6370000, b = 6370000)
    return pyproj.Transformer.from_proj(WRF_proj, 'EPSG:4326').transform(XY[0], XY[1])[::-1]

def convert_lonlat2xy(lonlat, ds):
    WRF_proj = pyproj.Proj(proj = 'lcc', lat_1 = ds['crs'].standard_parallel[0], lat_2 = ds['crs'].standard_parallel[1], lat_0 = ds['crs'].latitude_of_projection_origin, lon_0 = ds['crs'].longitude_of_central_meridian, a = 6370000, b = 6370000)
    return pyproj.Transformer.from_proj('EPSG:4326', WRF_proj).transform(lonlat[1], lonlat[0])

def extract_fulldom(loc, path_fulldom, var = 'TOPOGRAPHY', loc_type = 'lonlat'):
    ds_ref = xr.open_dataset(path_fulldom, decode_coords = 'all')
    if loc_type == 'lonlat': xy = convert_lonlat2xy(lonlat = loc, ds = ds_ref)
    else: xy = loc

    ds = ds_ref[var].sel(y = xy[1], x = xy[0], method = 'nearest')
    
    return ds.values

def load_nc(path, begin_date = datetime.datetime(1900, 1, 1), end_date = datetime.datetime(2100, 1, 1), var = None, layer = {}, offset = 0, factor = 1, save_nc = None):
    files = glob.glob(path); files.sort()
    files_ds = [file for file in files if begin_date <= datetime.datetime.strptime(os.path.basename(file).split('.')[0],'%Y%m%d%H%M') and datetime.datetime.strptime(os.path.basename(file).split('.')[0],'%Y%m%d%H%M') <= end_date]
    ds = xr.open_mfdataset(files_ds, concat_dim = 'time', combine = 'nested', parallel = True, decode_coords = 'all')
    if var is not None:
        ds_var = (ds[var] + offset) * factor

        layer_copy = {}
        for key, value in layer.items():
            if key in ds_var.dims and value is not None:
                if value in ds_var[key]: layer_copy[key] = value
        ds_var = ds_var.loc[layer_copy]
        
        ds_var = ds_var.to_dataset()
        ds_var.attrs = ds.attrs
    else: ds_var = ds
    
    if save_nc is not None: ds_var.to_netcdf(save_nc)
        
    return ds_var

def load_output(loc, path, begin_date = datetime.datetime(1900, 1, 1), end_date = datetime.datetime(2100, 1, 1), var = None, layer = {}, offset = 0, factor = 1, loc_type = 'lonlat', save_csv = None):
    ds_var = load_nc(path = path, begin_date = begin_date, end_date = end_date, var = var, offset = offset, factor = factor, save_nc = None)
    layer_copy = {}
    for key, value in layer.items():
        if key in ds_var.dims and value is not None:
            if value in ds_var[key]: layer_copy[key] = value
    ds_var = ds_var.loc[layer_copy]

    if 'reference_time' in ds_var.dims: ds_var = ds_var.drop_dims('reference_time')
    
    if loc_type == 'lonlat': xy = convert_lonlat2xy(lonlat = loc, ds = ds_var)
    else: xy = loc

    if var is not None: ds = ds_var[var].sel(y = xy[1], x = xy[0], method = 'nearest')
    else: ds = ds_var.sel(y = xy[1], x = xy[0], method = 'nearest')

    df = ds.to_dataframe()
    if save_csv is not None: df.to_csv(save_csv)

    return ds, df