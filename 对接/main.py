import pandas as pd
from pylab import *
import numpy as np

def time_termipoints_values(b_time, zone_time):
    dt1 = datetime.timedelta(hours=zone_time[0])
    dt2 = datetime.timedelta(hours=zone_time[1])
    dt3 = datetime.timedelta(hours=zone_time[2])
    return [b_time, b_time + dt1, b_time + dt1 + dt2, b_time + dt1 + dt2 + dt3]

def split_meteo_time(meteo):
    date = []
    for i in range(len(meteo)):
        t = datetime.datetime.strptime(meteo.loc[i, 'time'], '%Y-%m-%d %H:%M:%S')
        date.append(t)
    meteo['date'] = date
    print('split meteo time finished')
    return meteo

def get_three_rectangles(trip_type:str):
    if (trip_type == 'going'):
        return [[121.495739,126.4747438,37.5215865,37.7715865],
                [122.3414072,126.0171692,36.98266417,37.6717885],
                [126.0171692,126.4747438,37.335683,36.98266417]
                ]
    if (trip_type == 'return'):
        return [[125.9921567,126.4666543,36.99155214,37.34494357],
                [122.7623974,125.9921567,36.99155214,37.71311943],
                [121.5533707,122.7623974,37.55073879,37.80073879]
                ]

def select_meteo_by_one_rectangle(rectangle,meteo):
    x1 = rectangle[0]
    x2 = rectangle[1]
    y1 = rectangle[2]
    y2 = rectangle[3]
    df = meteo[(meteo['longitude']>=x1) & (meteo['longitude']<=x2) &
               (meteo['latitude']>=y1) & (meteo['latitude']<=y2)]
    return df

def div_meteo_by_rectangles(three_rectangles, meteo):
    t = []
    for i in three_rectangles:
        t.append(select_meteo_by_one_rectangle(i,meteo))
    return t

def select_meteo_by_time(b_time,e_time,meteo):
    df = meteo[(meteo['date'].__ge__(b_time)) & (meteo['date'].__le__(e_time))]
    return df

def div_three_zones_by_time(z123,b_time,zone_time):
    t = []
    termipoints = time_termipoints_values(b_time, zone_time)
    for i in range(len(z123)):
        t.append(select_meteo_by_time(termipoints[i], termipoints[i + 1], z123[i]))
    return t

def get_means(zone_data,target:str):
    zone_data = zone_data[(zone_data[target] != '--')]
    pd_series = zone_data[target]
    if (len(pd_series)==0):
        return NAN
    data_list = list(pd_series)
    t = []
    for i in data_list:
        t.append(float(i))
    np_array = np.array(t)
    return np.mean(np_array)

def get_means_of_three_zones(z123,target):
    t = []
    for i in z123:
        t.append(get_means(i,target))
    return t

def main_gat_meteo_mean(meteo,trip_type,target_list, b_time, zone_time):
    meteo = split_meteo_time(meteo)
    three_rectangles = get_three_rectangles(trip_type)
    z123 = div_meteo_by_rectangles(three_rectangles, meteo)
    z123 = div_three_zones_by_time(z123, b_time, zone_time)
    mean_list_list = []
    for i in target_list:
        mean_list_list.append(get_means_of_three_zones(z123, i))
    mean_df = pd.DataFrame()
    for i in range(len(target_list)):
        mean_df[target_list[i]] = mean_list_list[i]
    mean_df.to_csv('meteo_mean.csv')



















