import copy
import pandas as pd
import math
import numpy as np
from time import *

def meteo_time_value(timestamp:str):
    t = timestamp.replace('-','/').replace('_','/')
    time_struct = strptime(t, "%Y/%m/%d %H:%M:%S")
    time_value = mktime(time_struct)
    return int(time_value)


def meteo_append_timevalue(meteo):
    t = []
    for i in meteo['time']:
        time_value = meteo_time_value(i)
        t.append(time_value)
    meteo['time_value'] = t
    print('time_value finished')
    return meteo

#############################
def time_termipoints_values(start_time:str,zone_time:list):
    t_v_0 = meteo_time_value(start_time)
    t_v_1 = t_v_0 + zone_time[0] * 3600
    t_v_2 = t_v_1 + zone_time[1] * 3600
    t_v_3 = t_v_2 + zone_time[2] * 3600
    return [t_v_0,t_v_1,t_v_2,t_v_3]

def get_three_rectangles(trip_type:str):
    if (trip_type == 'going'):
        return [[121.495739,122.3414072,37.6213845,37.6717885],
                [122.3414072,126.0171692,37.6717885,36.98266417],
                [126.0171692,126.4747438,36.98266417,37.335683]
                ]
    if (trip_type == 'return'):
        return [[125.9921567,126.4666543,36.99155214,37.34494357],
                [122.7623974,125.9921567,37.71311943,36.99155214],
                [121.5533707,122.7623974,37.63835814,37.71311943]
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

#起始时间戳，三个小时的列表
def select_meteo_by_time(start_timevalue,end_timevalue,meteo):
    df = meteo[(meteo['time_value'] >= start_timevalue) & (meteo['time_value']<= end_timevalue)]
    return df

def div_three_zones_by_time(z123,start_time:str,zone_time:list):
    t = []
    termipoints = time_termipoints_values(start_time,zone_time)
    print(termipoints)
    for i in range(len(z123)):
        t.append(select_meteo_by_time(termipoints[i],termipoints[i+1] , z123[i]))
    return t

def get_means(zone_data,target:str):
    zone_data = zone_data[(zone_data[target] != '--')]
    pd_series = zone_data[target]
    if (len(pd_series)==0):
        return '--'
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

def main_gat_meteo_mean(meteo_path,trip_type,target_list,start_time:str,zone_time:list):
    meteo = pd.read_csv(meteo_path,sep='\t')
    print('read meteo finished.')
    #print(meteo)
    meteo = meteo_append_timevalue(meteo)
    three_rectangles = get_three_rectangles(trip_type)
    z123 = div_meteo_by_rectangles(three_rectangles, meteo)

    z123 = div_three_zones_by_time(z123,start_time,zone_time)

    mean_list_list = []
    for i in target_list:
        mean_list_list.append(get_means_of_three_zones(z123, i))
    mean_df = pd.DataFrame()
    for i in range(len(target_list)):
        mean_df[target_list[i]] = mean_list_list[i]
    mean_df.to_csv('meteo_mean.csv')


if __name__ == '__main__':
    meteo_path = 'me.txt'
    trip_type = 'going'
    target_list = ['u10','v10','mwd','mwp','swh']
    start_time='2021/5/1 0:00:00'
    zone_time=[2,3.5,7]
    main_gat_meteo_mean(meteo_path, trip_type, target_list, start_time,zone_time)


















