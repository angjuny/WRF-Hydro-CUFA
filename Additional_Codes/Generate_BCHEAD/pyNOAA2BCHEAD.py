import os, datetime, requests
import numpy as np
import pandas as pd
import xarray as xr
import netCDF4 as nc4
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('TKAgg')

def main():
    ############### INPUT BEGIN ###############
    ElevOffset = -1.5 # an datum offset to apply for TOPOGRAPHY in Fulldom_hires.nc
    output_dir = 'BCHEAD' # output directory
    f_fulldom = 'Fulldom_hires.nc' # 'Fulldom_hires.nc'
    ds_fulldom = xr.open_dataset(f_fulldom)

    ### BCMASK: MODIFY THIS PART FOR YOUR DOMAIN
    f_mask = '4-GDAL_Translate(netCDF).nc' # netcdf filename for BCMASK
    ds_mask = xr.open_dataset(f_mask)
    da_mask = ds_mask['Band1'].reindex_like(ds_fulldom, method = 'nearest') # specifiy which variable you will use for BCMASK
    
    ### SET PARAMETERS TO FETCH NOAA TIDE GAUGE DATA FROM CO-OPS
    id = 8670870 # NOAA ID
    begin_date = datetime.datetime(2017, 9, 12) # date/time of forcing start
    end_date = datetime.datetime(2017, 9, 13) # date/time of forcing end
    product = 'water_level'# 'water_level': 6-min interval observations, 'hourly_height': 1-hour interval observations, 'predictions'
    datum = 'NAVD' # e.g., NAVD, MHHW, MHW, MSL, MLW, MLLW
    plot = True # whether to plot for data check
    ############### INPUT END ###############
    
    ### FETCH NOAA TIDE GAUGE DATA FROM CO-OPS
    COOPS = Station(stationId = id)
    print('NAME:', COOPS.name)
    print('LONGITUDE:', COOPS.lng)
    print('LATITUDE:', COOPS.lat)
    df = COOPS.get_Data(begin_date = begin_date, end_date = end_date, product = product, units = 'metric', time_zone = 'gmt', datum = datum, csv = True)
    df_h = df[product].resample('1H').interpolate('time') # resample hourly intervals

    if plot: # if plot = True for data
        plt.figure(figsize = (16, 8))
        plt.title('Water Levels at NOAA Tide Gauge: {} [{} deg, {} deg] for {} - {}'.format(COOPS.name, COOPS.lng, COOPS.lat, begin_date.strftime('%Y/%m/%d %H:%M'), end_date.strftime('%Y/%m/%d %H:%M')))
        plt.plot(df.index, df[product], 'r-o', label = 'NOAA Tide Gauge')
        plt.plot(df_h.index, df_h, 'b-^', label = 'NOAA Tide Gauge - Hourly Resampled')
        plt.xlabel('Time'); plt.ylabel('Water Level [$\it{m}$, ' + datum + ']'); plt.legend(), plt.grid()
        plt.tight_layout()
        plt.savefig('COOPS-' + str(id) + '_' + product + '_' + begin_date.strftime('%Y%m%dT%H%M') + '_' + end_date.strftime('%Y%m%dT%H%M') +'.png')
        plt.show()
        plt.close('all')

    ### GENERATE BCHEAD FILES
    os.makedirs(output_dir, exist_ok = True)
    if df_h.empty: return ''
    else:
        ds_copy = ds_fulldom.copy()
        ds_copy['HEAD'] = (('time', 'y', 'x'), np.repeat(df_h.values, len(ds_copy['y']) * len(ds_copy['x'])).reshape(-1, len(ds_copy['y']), len(ds_copy['x'])))
        ds_copy['HEAD'] = ds_copy['HEAD'].where(da_mask == 1)
        ds_copy = ds_copy.assign_coords({'time': df_h.index})
        da = ds_copy['HEAD']

        generate_BCHEAD(da, da_mask, f_fulldom, path = output_dir, offset = ElevOffset)

    return

def generate_BCHEAD(da, da_mask, f_fulldom, path, offset = 0):
    nc_fulldom = nc4.Dataset(f_fulldom, 'r')
    for t in da['time']:
        datetime_t = t.values.astype('datetime64[s]').tolist()
        fout = os.path.join(path, datetime_t.strftime('%Y%m%d%H') + '.BCHEAD_DOMAIN1')
        nc_bchead = nc4.Dataset(fout, 'w')
        dim_t = nc_bchead.createDimension('time', None)
        var_t = nc_bchead.createVariable('time', 'i4', ('time'))
        var_t.units = "minutes since 1970-01-01 00:00:00 UTC"
        var_t.standard_name = "time"
        var_t.long_name= "valid output time"
        var_t[0] = (datetime_t - datetime.datetime(1970, 1, 1))/datetime.timedelta(minutes = 1)
        var_tref = nc_bchead.createVariable('reference_time', 'i4')
        var_tref.units = "minutes since 1970-01-01 00:00:00 UTC"
        var_tref.standard_name = "forecast_reference_time"
        var_tref.long_name= "model initialization time"
        var_tref[0] = (da['time'][0].values.astype('datetime64[s]').tolist() - datetime.datetime(1970, 1, 1))/datetime.timedelta(minutes = 1)
        
        nc_bchead.setncatts(nc_fulldom.__dict__)
        for dimname, dim in nc_fulldom.dimensions.items():
            if dimname == 'y': nc_bchead.createDimension('y', len(dim))
            if dimname == 'x': nc_bchead.createDimension('x', len(dim))

        FillValue = 1.0E20
        var = nc_bchead.createVariable('y', nc_fulldom['y'].dtype, 'y')
        var.setncatts(nc_fulldom['y'].__dict__)
        var[:] = nc_fulldom['y'][:]
        var = nc_bchead.createVariable('x', nc_fulldom['x'].dtype, 'x')
        var.setncatts(nc_fulldom['x'].__dict__)
        var[:] = nc_fulldom['x'][:]
        var = nc_bchead.createVariable('crs', nc_fulldom['crs'].dtype)
        var.setncatts(nc_fulldom['crs'].__dict__)
        var[0] = nc_fulldom['crs'][0]
        #var = nc_bchead.createVariable('TOPOGRAPHY', nc_fulldom['TOPOGRAPHY'].dtype, nc_fulldom['TOPOGRAPHY'].dimensions)
        #var.setncatts(nc_fulldom['TOPOGRAPHY'].__dict__)
        #var[:] = nc_fulldom['TOPOGRAPHY'][:]
        #var = nc_bchead.createVariable('LONGITUDE', nc_fulldom['LONGITUDE'].dtype, nc_fulldom['LONGITUDE'].dimensions)
        #var.setncatts(nc_fulldom['LONGITUDE'].__dict__)
        #var[:] = nc_fulldom['LONGITUDE'][:]
        #var = nc_bchead.createVariable('LATITUDE', nc_fulldom['LATITUDE'].dtype, nc_fulldom['LATITUDE'].dimensions)
        #var.setncatts(nc_fulldom['LATITUDE'].__dict__)
        #var[:] = nc_fulldom['LATITUDE'][:]

        var = nc_bchead.createVariable('HEADMASK', nc_fulldom['basn_msk'].dtype, ('time', nc_fulldom['basn_msk'].dimensions[0], nc_fulldom['basn_msk'].dimensions[1]))
        var.setncatts(nc_fulldom['basn_msk'].__dict__)
        var[0] = da_mask.transpose('y', 'x')
        var = nc_bchead.createVariable('HEAD', nc_fulldom['TOPOGRAPHY'].dtype, ('time', nc_fulldom['TOPOGRAPHY'].dimensions[0], nc_fulldom['TOPOGRAPHY'].dimensions[1]))
        var.setncatts(nc_fulldom['TOPOGRAPHY'].__dict__)
        var.units = "mm"
        var[0] = nc_bchead['HEADMASK'][:] * np.nan_to_num(np.maximum(da.sel(time = t).transpose('y', 'x') * nc_bchead['HEADMASK'][0] - (offset + nc_fulldom['TOPOGRAPHY'][:]), 0)) * 1000 # if Water Level > Offset + TOPOGRAPHY: BCHEAD = Water Level - (Offset + TOPOGRAPHY) or BCHEAD = 0.0 [mm] otherwise
        
        nc_bchead.sync()
        nc_bchead.close()
    nc_fulldom.close()

    return

class Station:
    def __init__(self, stationId):
        self.stationId = stationId
        self.metaData = self.get_MetaData()
        self.data = pd.DataFrame()
        return

    # CO-OPS Metadata API v1.0:  https://tidesandcurrents.noaa.gov/mdapi/latest/
    def get_MetaData(self):
        stationId = self.stationId

        url_base = 'https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/'
        url_extension = '.json'
        url_expand = '?expand=details,sensors,floodlevels,datums,harcon,tidepredoffsets,products,disclaimers,notices,benchmarks'
        url = url_base + str(stationId) + url_extension + url_expand

        n = 0
        while n < 10:
            try:
                req = requests.get(url).json()
                break
            except:
                n += 1
        if n == 10: print('Failed to Query Data!')

        metadata = req['stations'][0]

        keys = ['tidal', 'greatlakes', 'shefcode', 'details', 'sensors', 'floodlevels', 'datums', 'supersededdatums', 'harmonicConstituents', 'benchmarks', 'tidePredOffsets', 'state', 'timezone', 'timezonecorr', 'observedst', 'stormsurge', 'nearby', 'forecast', 'nonNavigational', 'id', 'name', 'lat', 'lng', 'affiliations', 'portscode', 'products', 'disclaimers', 'notices', 'self', 'expand', 'tideType']
        for key in keys:
            if key in metadata.keys() and not hasattr(self, key): setattr(self, key, metadata[key])

        self.metaData = metadata
        return self.metaData
    
    # CO-OPS API For Data Retrieval: https://api.tidesandcurrents.noaa.gov/api/prod/
    def _get_DataQuery(self, parameters):
        url_base = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?'
        url = requests.Request('GET', url_base, params=parameters).prepare().url
        
        n = 0
        while n < 10:
            try:
                req = requests.get(url).json()
                break
            except:
                n += 1
        if n == 10: print('Failed to Query Data!')

        df = pd.DataFrame()
        if 'error' not in req.keys():
            if parameters['product'] == 'predictions': key = 'predictions'
            else: key = 'data'
            df = pd.json_normalize(req[key])
        else:
            print('Erros in Querying Data!')
            print(req['error']['message'])

        return df

    # CO-OPS API For Data Retrieval: https://api.tidesandcurrents.noaa.gov/api/prod/
    def get_Data(self, begin_date, end_date, product = 'water_level', units = 'metric', time_zone = 'gmt', datum = 'NAVD', interval = None, csv = False):
        stationId = self.stationId
        
        begin_datetime, end_datetime = begin_date, end_date
        if type(begin_datetime) != datetime.datetime or type(end_datetime) != datetime.datetime:
            self.data = pd.DataFrame()
            print('All dates should be formatted with the datetime.datetime object')
            return self.data
        
        parameters = {'station': str(stationId), 'product': product, 'units': units, 'time_zone': time_zone, 'datum': datum, 'format': 'json'}
        if interval is not None: parameters['interval'] = interval
        
        dfs = pd.DataFrame()
        if product == 'hourly_height' or product == 'high_low':
            year_iter = begin_datetime.year
            while year_iter <= end_datetime.year:
                year_begin, year_end = datetime.datetime(year_iter, 1, 1), datetime.datetime(year_iter + 1, 1, 1) - datetime.timedelta(seconds = 1)
                if year_iter == begin_datetime.year: year_begin = max(year_begin, begin_datetime)
                if year_iter == end_datetime.year: year_end = min(year_end, end_datetime)
                parameters['begin_date'] = year_begin.strftime('%Y%m%d %H:%M')
                parameters['end_date'] = year_end.strftime('%Y%m%d %H:%M')
                df = self._get_DataQuery(parameters)
                dfs = dfs.append(df)
                year_iter += 1
        else:
            year_iter = begin_datetime.year
            month_iter = begin_datetime.month
            while datetime.datetime(year_iter, month_iter, 1) <= end_datetime:
                month_begin, month_end = datetime.datetime(year_iter, month_iter, 1), datetime.datetime(year_iter + int(month_iter/12), 1 + month_iter%12, 1) - datetime.timedelta(seconds = 1)
                if year_iter == begin_datetime.year and month_iter == begin_datetime.month: month_begin = max(month_begin, begin_datetime)
                if year_iter == end_datetime.year and month_iter == end_datetime.month: month_end = min(month_end, end_datetime)
                parameters['begin_date'] = month_begin.strftime('%Y%m%d %H:%M')
                parameters['end_date'] = month_end.strftime('%Y%m%d %H:%M')
                df = self._get_DataQuery(parameters)
                dfs = dfs.append(df)
                year_iter += int(month_iter/12)
                month_iter = 1 + month_iter%12
        if dfs.empty: return dfs
        
        dfs.drop_duplicates(inplace = True)
        dfs_columns = dfs.columns.to_list()
        for i, column in enumerate(dfs_columns):
            if column == 't': dfs_columns[i] = 'time'; dfs[column] = pd.to_datetime(dfs[column])
            elif column == 'v': dfs_columns[i] = product; dfs[column] = pd.to_numeric(dfs[column], errors = 'coerce')
            elif column == 's': dfs_columns[i] = 'sigma'; dfs[column] = pd.to_numeric(dfs[column], errors = 'coerce')
            elif column == 'f': dfs_columns[i] = 'flags'; dfs[column] = dfs[column].astype(str)
            elif column == 'q': dfs_columns[i] = 'quality'; dfs[column] = dfs[column].astype(str)
            elif column == 'ty': dfs_columns[i] = 'type'; dfs[column] = dfs[column].astype(str)
        dfs.columns = dfs_columns
        dfs.index = dfs['time']
        dfs.drop(columns = ['time'], inplace = True)
        
        if csv:
            if isinstance(csv, str): dfs.to_csv(csv)
            else: dfs.to_csv('COOPS-' + str(stationId) + '_' + product + '_' + begin_date.strftime('%Y%m%dT%H%M') + '_' + end_date.strftime('%Y%m%dT%H%M') + '.csv')

        self.data = dfs
        return self.data

if __name__ == '__main__':
    main()