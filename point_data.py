# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 12:52:52 2014

@author: Spiridonov Denis
"""

from xml.dom import minidom
import os
import re
import urllib
import xlsxwriter

from pydap.client import open_url
import numpy
from numpy import logical_or
import numpy.ma as ma
from scipy import spatial
import datetime

years = [2011, 2014]
points_list = [(-13, -10), (-12.5, -10), (-12, -9.5), (-12, -9), (-11.3, -8.6), 
               (-11, -8), (-10, -7), (-7, -6.5), (-76, -36), (-80, -5), (-85, 40)]
hide_null_values = True
variables = ['wind_speed', 'sst', 'atmosphere_water_vapor_content', 'icecon']

# find the nearest element indexes
def do_kdtree(combined_x_y_arrays,points):
    mytree = spatial.cKDTree(combined_x_y_arrays)
    dist, indexes = mytree.query(points)
    return dist, indexes

def set_coords_value(worksheet, num_row, coords, value=''):
    lat, lon = coords
    worksheet.write('C%d' % num_row, lat)
    worksheet.write('D%d' % num_row, lon)

    worksheet.write('E%d' % num_row, value)

def add_title(worksheet, num_row=1):
    worksheet.write('A%d' % num_row, 'Date')
    worksheet.write('B%d' % num_row, 'Granule name')
    worksheet.write('C%d' % num_row, 'latitude')
    worksheet.write('D%d' % num_row, 'longitude')
    worksheet.write('E%d' % num_row, 'value')

opendap_catalog = 'http://opendap.solab.rshu.ru:8080/opendap/hyrax/allData/'

# wind_speed
def wind_speed_read_parameter_value(dataset, pp_name):
    attrs = dataset[pp_name].attributes.keys()
    fill_value = dataset[pp_name]._FillValue

    if 'scale_factor' in attrs:
        scale_factor = dataset[pp_name].scale_factor
    else:
        scale_factor = 1
    if 'add_offset' in attrs:
        add_offset = dataset[pp_name].add_offset
    else:
        add_offset = 0

    valid_min = dataset[pp_name].valid_min
    valid_max = dataset[pp_name].valid_max

    #read parameter data and remove singleton dimensions:
    data_array = dataset[pp_name][:].squeeze()

    data_array = ma.masked_where(data_array < valid_min, data_array)
    data_array = ma.masked_where(data_array > valid_max, data_array)
    data_array = ma.masked_where(logical_or(data_array == fill_value,
                 data_array is None),data_array) * scale_factor + add_offset
    return data_array

def wind_speed_handler(granule, granule_date, worksheet, num_row):
    try:
        dataset = open_url(granule)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        return num_row
    
    lat = dataset['lat'][:]
    lon = dataset['lon'][:]

    lat_fv = dataset['lat']._FillValue
    lon_fv = dataset['lon']._FillValue

    lat = ma.masked_where(lat == lat_fv, lat)
    lon = ma.masked_where(lon == lon_fv, lon)
    
    lat = lat * dataset['lat'].scale_factor
    lon = lon * dataset['lon'].scale_factor
    #fix longitude:
    lon = ma.where(lon <= 180, lon, lon - 360)
    
    wind_speed = wind_speed_read_parameter_value(dataset, 'wind_speed')
    combined_x_y_arrays = numpy.dstack([lat.ravel(),lon.ravel()])[0]
    #points_list = list(points.transpose())
    dist, indexes = do_kdtree(combined_x_y_arrays,points_list)
    
    flag_added_granule = False
    
    for i in range(len(points_list)):
        if dist[i] > 0.2:
            if hide_null_values:
                continue
            if not flag_added_granule:
                flag_added_granule = True
                worksheet.write('B%d' % num_row, os.path.basename(granule))
            worksheet.write('A%d' % num_row, granule_date)
            set_coords_value(worksheet, num_row, points_list[i])
            num_row += 1
            # set NULL values
            continue
        index = indexes[i]
        f_lat, f_lon = combined_x_y_arrays[index].tolist()
    
        print f_lat, f_lon
        # indexes in lat and lon
        ind_mas = numpy.where(numpy.logical_and (lon==f_lon , lat==f_lat))
        
        x_ind = ind_mas[0][0]
        y_ind = ind_mas[1][0]
        
        print x_ind, y_ind
        print 'dist: ', dist[i]
        print "wind_speed: ", wind_speed[x_ind, y_ind]
        print 'granule_date: ', granule_date
        value = wind_speed[x_ind, y_ind]
        if type(value) == ma.core.MaskedConstant:
            if hide_null_values:
                continue
            if not flag_added_granule:
                flag_added_granule = True
                worksheet.write('B%d' % num_row, os.path.basename(granule))
            worksheet.write('A%d' % num_row, granule_date)
            set_coords_value(worksheet, num_row, points_list[i])
            num_row += 1
            # set NULL values
            continue        
        
        if not flag_added_granule:
            flag_added_granule = True
            worksheet.write('B%d' % num_row, os.path.basename(granule))
        worksheet.write('A%d' % num_row, granule_date)
        set_coords_value(worksheet, num_row, points_list[i], wind_speed[x_ind, y_ind])
        num_row += 1
        
    del lat
    del lon
    del wind_speed
    del dataset
    return num_row

def wind_speed_workflow(worksheet, num_row):
    worksheet.write('A%d' % num_row, 'wind_speed')
    num_row+=1
    
    catalog = opendap_catalog + 'ASCAT-L2-12km'
    catalogxml = os.path.join(catalog, 'catalog.xml')
    
    xmldoc = minidom.parse(urllib.urlopen(catalogxml))
    itemlist = xmldoc.getElementsByTagName('thredds:catalogRef')
    
    for y in itemlist:
        year_name = y.attributes['name'].value
    
        if not year_name.isdigit():
            continue
        if not int(year_name) in years:
            continue
        
        print '\n\nStart year: %s' %year_name
        year_cat = os.path.join(catalog, year_name)
        year_xml = os.path.join(year_cat, 'catalog.xml')
        
        yeardoc = minidom.parse(urllib.urlopen(year_xml))
        days_item_list = yeardoc.getElementsByTagName('thredds:catalogRef')
        for day in days_item_list:
            day_name = day.attributes['name'].value
            if not day_name.isdigit():
                continue
            print '\nStart day: %s' %day_name
            
            # write day (date) to file
            granule_date = datetime.datetime.strptime('%s %s' %(year_name, day_name),
                                                      '%Y %j').strftime('%d.%m.%Y')

            day_cat = os.path.join(year_cat, day_name)
            day_xml = os.path.join(day_cat, 'catalog.xml')
            daydoc = minidom.parse(urllib.urlopen(day_xml))
            datasets_item_list = daydoc.getElementsByTagName('thredds:dataset')
    
            for _dataset in datasets_item_list:
    
                dataset_name = _dataset.attributes['name'].value
                if dataset_name.startswith('ascat') and \
                                           dataset_name.endswith('.nc.gz'):
                    granule_path = os.path.join(day_cat, dataset_name)
                    print 'Start granule: %s' %granule_path
                    
                    num_row = wind_speed_handler(granule_path, granule_date,
                                                 worksheet, num_row)


# SST
def sst_read_parameter_value(dataset, pp_name):
    fill_value = dataset[pp_name]._FillValue

    scale_factor = dataset[pp_name].scale_factor
    add_offset = dataset[pp_name].add_offset

    valid_min = dataset[pp_name].valid_min
    valid_max = dataset[pp_name].valid_max

    #read parameter data and remove singleton dimensions:
    data_array = dataset[pp_name][pp_name][:].squeeze()

    data_array = ma.masked_where(data_array < valid_min, data_array)
    data_array = ma.masked_where(data_array > valid_max, data_array)
    data_array = ma.masked_where(logical_or(data_array == fill_value,
                 data_array is None),data_array) * scale_factor + add_offset
    return data_array

def sst_handler(granule, granule_date, worksheet, num_row):
    try:
        dataset = open_url(granule)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        return num_row
    
    lat = dataset['lat'][:]
    lon = dataset['lon'][:]
    
    sst = sst_read_parameter_value(dataset, 'sst')
    
    flag_added_granule = False
    
    for i in range(len(points_list)):
        lat_coord, lon_coord = points_list[i]
        if lon_coord < 0:
            lon_coord += 360
        ind_lat = (numpy.abs(lat-lat_coord)).argmin()
        ind_lon = (numpy.abs(lon-lon_coord)).argmin()

        value = sst[ind_lat, ind_lon]

        if type(value) == ma.core.MaskedConstant:
            if hide_null_values:
                continue
            if not flag_added_granule:
                flag_added_granule = True
                worksheet.write('B%d' % num_row, os.path.basename(granule))
            worksheet.write('A%d' % num_row, granule_date)
            set_coords_value(worksheet, num_row, points_list[i])
            num_row += 1
            # set NULL values
            continue

        print "sst: ", sst[ind_lat, ind_lon]
        print 'granule_date: ', granule_date
        if not flag_added_granule:
            flag_added_granule = True
            worksheet.write('B%d' % num_row, os.path.basename(granule))
        worksheet.write('A%d' % num_row, granule_date)
        set_coords_value(worksheet, num_row, points_list[i], sst[ind_lat, ind_lon])
        num_row += 1
        
    del lat
    del lon
    del sst
    del dataset
    return num_row

def sst_workflow(worksheet, num_row):
    worksheet.write('A%d' % num_row, 'sst')
    num_row+=1
    
    catalog = opendap_catalog + 'OISST-AVHRR-V2'
    sub_dir = 'AVHRR'
    catalogxml = os.path.join(catalog, 'catalog.xml')
    
    xmldoc = minidom.parse(urllib.urlopen(catalogxml))
    itemlist = xmldoc.getElementsByTagName('thredds:catalogRef')
    
    prog = re.compile(r'(\d{8})')
    
    for y in itemlist:
        year_name = y.attributes['name'].value
    
        if not year_name.isdigit():
            continue
        if not int(year_name) in years:
            continue
        
        print '\n\nStart year: %s' %year_name
        year_cat = os.path.join(catalog, year_name, sub_dir)
        year_xml = os.path.join(year_cat, 'catalog.xml')
        
        yeardoc = minidom.parse(urllib.urlopen(year_xml))
        datasets_item_list = yeardoc.getElementsByTagName('thredds:dataset')

        for t_dataset in datasets_item_list:
            for dataset in t_dataset.getElementsByTagName('thredds:dataset'):
                dataset_name = dataset.attributes['name'].value
    
                if dataset_name.startswith('avhrr') and (not 'preliminary' in dataset_name) and \
                                (dataset_name.endswith('.nc.gz') or dataset_name.endswith('.nc')):
                    # print dataset_name
                    try:
                        dataset_date = prog.findall(dataset_name)[0]
                    except:
                        continue
                    _year = dataset_date[:4]
                    _month = dataset_date[4:6]
                    _day = dataset_date[-2:]
    
                    granule_date = '%s-%s-%s' %(_year, _month, _day)
                    granule_path = os.path.join(year_cat, dataset_name)
                    print 'Start granule: %s' %granule_path
        
                    num_row = sst_handler(granule_path, granule_date,
                                                 worksheet, num_row)


# atmosphere_water_vapor_content
def water_vapor_read_parameter_value(dataset, pp_name):
    data_array = dataset[pp_name][pp_name][:]

    fill_value = 251
    valid_min, valid_max = 0, 250

    data_array = ma.masked_where(data_array > valid_max, data_array)
    data_array = ma.masked_where(data_array < valid_min, data_array)

    scale_factor = dataset[pp_name].attributes['scale_factor']
    add_offset = dataset[pp_name].attributes['add_offset']

    data_array = numpy.float64(ma.masked_values(ma.masked_equal(data_array, None, copy=False),
                               fill_value, copy=False)) * scale_factor + add_offset

    return data_array

def water_vapor_handler(granule, granule_date, worksheet, num_row):
    try:
        dataset = open_url(granule)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        return num_row

    lat = dataset['latitude'][:]
    lon = dataset['longitude'][:]
    
    water_vapor_all = water_vapor_read_parameter_value(dataset,
                                            'atmosphere_water_vapor_content')
    flag_added_granule = False
    
    # for ascending and descending
    time_v = [0,1]
    for t in time_v:
        water_vapor = water_vapor_all[t,:,:]
        
    
        for i in range(len(points_list)):
            lat_coord, lon_coord = points_list[i]
            if lon_coord < 0:
                lon_coord += 360
            ind_lat = (numpy.abs(lat-lat_coord)).argmin()
            ind_lon = (numpy.abs(lon-lon_coord)).argmin()
    
            value = water_vapor[ind_lat, ind_lon]
    
            if type(value) == ma.core.MaskedConstant:
                if hide_null_values:
                    continue
                if not flag_added_granule:
                    flag_added_granule = True
                    worksheet.write('B%d' % num_row, os.path.basename(granule))
                worksheet.write('A%d' % num_row, granule_date)
                set_coords_value(worksheet, num_row, points_list[i])
                num_row += 1
                # set NULL values
                continue
    
            print "water_vapor: ", water_vapor[ind_lat, ind_lon]
            print 'granule_date: ', granule_date
            if not flag_added_granule:
                flag_added_granule = True
                worksheet.write('B%d' % num_row, os.path.basename(granule))
            worksheet.write('A%d' % num_row, granule_date)
            set_coords_value(worksheet, num_row, points_list[i], water_vapor[ind_lat, ind_lon])
            num_row += 1
        del water_vapor
        
    del lat
    del lon
    del water_vapor_all
    del dataset
    return num_row

def water_vapor_workflow(worksheet, num_row):
    worksheet.write('A%d' % num_row, 'water_vapor')
    num_row+=1
    
    catalog = opendap_catalog + 'SSMI_NC/f16/daily/data'
    catalogxml = os.path.join(catalog, 'catalog.xml')
    
    xmldoc = minidom.parse(urllib.urlopen(catalogxml))
    years_list = xmldoc.getElementsByTagName('thredds:catalogRef')
    
    dataset_starts_with = 'f16_ssmi'
    
    for year in years_list:
        year_name = year.attributes['name'].value

        if not year_name.isdigit():
            continue
        if not int(year_name) in years:
            continue
  
        print '\n\nStart year: %s' %year_name
        year_cat = os.path.join(catalog, year_name)
        year_xml = os.path.join(year_cat, 'catalog.xml')
        
        yeardoc = minidom.parse(urllib.urlopen(year_xml))
        datasets_item_list = yeardoc.getElementsByTagName('thredds:dataset')

        for _dataset in datasets_item_list:

            dataset_name = _dataset.attributes['name'].value
            if dataset_name.startswith(dataset_starts_with) and \
                                (dataset_name.endswith('.nc') or dataset_name.endswith('.nc')):

                strip_count = 9
                if dataset_name.startswith(dataset_starts_with + 's'):
                    strip_count = 10
                dataset_date = dataset_name[strip_count:][:8]
                _year = dataset_date[:4]
                _month = dataset_date[4:6]
                _day = dataset_date[-2:]

                granule_date = '%s-%s-%s' %(_year, _month, _day)
                granule_path = os.path.join(year_cat, dataset_name)
                print 'Start granule: %s' %granule_path
    
                num_row = water_vapor_handler(granule_path, granule_date,
                                             worksheet, num_row)
# ICE
def ice_read_parameter_value(dataset, pp_name):
    fill_value = dataset[pp_name]._FillValue

    scale_factor = dataset[pp_name].scale_factor

    #read parameter data and remove singleton dimensions:
    data_array = dataset[pp_name][:].squeeze()

    data_array = ma.masked_where(logical_or(data_array == fill_value,
                 data_array is None),data_array) * scale_factor
    return data_array

def ice_handler(granule, granule_date, worksheet, num_row):
    try:
        dataset = open_url(granule)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        return num_row

    lat = dataset['latitude'][:]
    lon = dataset['longitude'][:]

    lat = lat * dataset['latitude'].scale_factor
    lon = lon * dataset['longitude'].scale_factor
    #fix longitude:
    lon = ma.where(lon <= 180, lon, lon - 360)
    
    ice = ice_read_parameter_value(dataset, 'icecon')
    combined_x_y_arrays = numpy.dstack([lat.ravel(),lon.ravel()])[0]
    #points_list = list(points.transpose())
    dist, indexes = do_kdtree(combined_x_y_arrays,points_list)
    
    flag_added_granule = False
    
    for i in range(len(points_list)):
        if dist[i] > 0.2:
            if hide_null_values:
                continue
            if not flag_added_granule:
                flag_added_granule = True
                worksheet.write('B%d' % num_row, os.path.basename(granule))
            worksheet.write('A%d' % num_row, granule_date)
            set_coords_value(worksheet, num_row, points_list[i])
            num_row += 1
            # set NULL values
            continue
        index = indexes[i]
        f_lat, f_lon = combined_x_y_arrays[index].tolist()
    
        print f_lat, f_lon
        # indexes in lat and lon
        ind_mas = numpy.where(numpy.logical_and (lon==f_lon , lat==f_lat))
        
        x_ind = ind_mas[0][0]
        y_ind = ind_mas[1][0]
        
        print x_ind, y_ind
        print 'dist: ', dist[i]
        print "ice: ", ice[x_ind, y_ind]
        print 'granule_date: ', granule_date
        value = ice[x_ind, y_ind]
        if type(value) == ma.core.MaskedConstant:
            if hide_null_values:
                continue
            if not flag_added_granule:
                flag_added_granule = True
                worksheet.write('B%d' % num_row, os.path.basename(granule))
            worksheet.write('A%d' % num_row, granule_date)
            set_coords_value(worksheet, num_row, points_list[i])
            num_row += 1
            # set NULL values
            continue
            
        if not flag_added_granule:
            flag_added_granule = True
            worksheet.write('B%d' % num_row, os.path.basename(granule))
        worksheet.write('A%d' % num_row, granule_date)
        set_coords_value(worksheet, num_row, points_list[i], ice[x_ind, y_ind])
        num_row += 1
        
    del lat
    del lon
    del ice
    del dataset
    return num_row

def ice_workflow(worksheet, num_row):
    worksheet.write('A%d' % num_row, 'icecon')
    num_row+=1
    prog = re.compile(r'(\d{8})')

    catalog = opendap_catalog + 'ASI-AMSRE'
    catalogxml = os.path.join(catalog, 'catalog.xml')

    xmldoc = minidom.parse(urllib.urlopen(catalogxml))
    itemlist = xmldoc.getElementsByTagName('thredds:catalogRef')
    for y in itemlist:
        year_name = y.attributes['name'].value
        print year_name
    
        if not year_name.isdigit():
            continue
        if not int(year_name) in years:
            continue

        print '\n\nStart year: %s' %year_name
        year_cat = os.path.join(catalog, year_name)
        year_xml = os.path.join(year_cat, 'catalog.xml')
        
        yeardoc = minidom.parse(urllib.urlopen(year_xml))
        datasets_item_list = yeardoc.getElementsByTagName('thredds:dataset')
        for dataset in datasets_item_list:
#            for dataset in t_dataset.getElementsByTagName('thredds:dataset'):
            dataset_name = dataset.attributes['name'].value

            if dataset_name.startswith('asi-s') and (dataset_name.endswith('.nc.gz') or dataset_name.endswith('.nc')):
                try:
                    dataset_date = prog.findall(dataset_name)[0]
                except:
                    continue
                _year = dataset_date[:4]
                _month = dataset_date[4:6]
                _day = dataset_date[-2:]

                granule_date = '%s-%s-%s' % (_year, _month, _day)
                granule_path = os.path.join(year_cat, dataset_name)
        
                print 'Start granule: %s' %granule_path
                num_row = ice_handler(granule_path, granule_date,
                                                         worksheet, num_row)

if __name__ == '__main__':
    try:
        # create xlsx file
        workbook = xlsxwriter.Workbook('DataArray.xlsx')
        
        if 'wind_speed' in variables:
            # add list for variable
            worksheet1 = workbook.add_worksheet()
            num_row = 1
            add_title(worksheet1)
            num_row += 1
        
            wind_speed_workflow(worksheet1, num_row)
            del worksheet1
    
        if 'sst' in variables:
            worksheet2 = workbook.add_worksheet()
            num_row = 1
            add_title(worksheet2)
            num_row += 1
            sst_workflow(worksheet2, num_row)
            del worksheet2
    
        if 'atmosphere_water_vapor_content' in variables:
            worksheet3 = workbook.add_worksheet()
            num_row = 1
            add_title(worksheet3)
            num_row += 1
            water_vapor_workflow(worksheet3, num_row)
            del worksheet3
        
        if 'icecon' in variables:
            worksheet4 = workbook.add_worksheet()
            num_row = 1
            add_title(worksheet4)
            num_row += 1
            ice_workflow(worksheet4, num_row)
            del worksheet4
    
    except KeyboardInterrupt:
        pass
    finally:
        workbook.close()