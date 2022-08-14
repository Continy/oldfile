import copy
import pandas as pd
import matplotlib.pyplot as plt
import math
from mpl_toolkits.basemap import Basemap
from pylab import *
import numpy as np
from scipy import interpolate
import pylab as pl

def time_value(timestamp):
    return int(timestamp.replace("_",'').replace(' ',''))


if __name__ == '__main__':

    #这段代码用来给meteo增加wind_speed_10这一列，这样在后面的循环中不用每一次都读一次文件
    #计划编写函数 get_data_mean(rectangle,target_name,meteo)
    meteo = pd.read_csv("meteo_working.csv")
    for i in meteo['time']:
        i = i.replace('/', '_').replace(':', '_')

    u10 = np.array(list(meteo["u10"]))
    v10 = np.array(list(meteo["v10"]))
    wind_speed10 = np.sqrt(u10 * u10 + v10 * v10)
    meteo['wind_speed10'] = wind_speed10
    meteo.to_csv('improved_meteo.csv')

    meteo = pd.read_csv('improved_meteo.csv')
    three_rectangles = [[124.67814, 126.35981, 36.45783097231687, 37.2521],
                        [122.99647, 124.67814, 36.53828311072724, 37.357454299863576],
                        [121.3148, 122.99647, 37.37111941694849, 37.432956297401645]]
    rectangle = [124.67814, 126.35981, 36.45783097231687, 37.2521]
    target_name = 'wsp'
    rectangle_data = meteo[(meteo["latitude"]>=rectangle[2]) & (meteo["latitude"]<=rectangle[3])
                           &(meteo["longitude"]>=rectangle[0])&(meteo["longitude"]>=rectangle[1])]
    notna_rec_data = rectangle_data[ rectangle_data[target_name] != '--' ]
    data_mean = notna_rec_data[target_name].mean()#注意有的元素被当作字符串，应当转化成float
    print (data_mean)





















