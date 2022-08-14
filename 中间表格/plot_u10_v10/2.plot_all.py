import pandas as pd
import matplotlib.pyplot as plt
import math
from mpl_toolkits.basemap import Basemap
from pylab import *
import numpy as np

def in90(list):
    a=[]
    for i in list:
        if (i>90):
            i = i -180
        a.append(i)
    return a

def plot_u10_v10(filename):
    df = pd.read_csv("./bigdata/"+filename+'.csv')
    lats = np.array(list(df["latitude"]))
    lons = np.array(list(df["longitude"]))
    u10 = np.array(list(df["u10"]))
    v10 = np.array(list(df["v10"]))
    speed = np.sqrt(u10 * u10 + v10 * v10)

    df_lons = pd.DataFrame(lons)
    df_lats = pd.DataFrame(lats)
    # 找出划分航段的速度
    df_speed = pd.DataFrame(speed)
    speed_mean = df_speed[0].mean()
    speed_description = df_speed.describe()
    mid_speed = speed_description.at['50%', 0]
    # 记录下中速上下 总速度差别的 5%的所有点
    speed_iter = speed_description.at['max', 0] - speed_description.at['min', 0]
    delt_speed = 0.05 * speed_iter
    special_lons = []
    special_lats = []
    special_speed = []

    for i in range(len(speed)):
        if speed[i] <= mid_speed + delt_speed and speed[i] >= mid_speed - delt_speed:
            special_lats.append(lats[i])
            special_speed.append(speed[i])
            special_lons.append(lons[i])

    lonmax = df_lons.describe().at['max', 0]
    lonmin = df_lons.describe().at['min', 0]
    latmax = df_lats.describe().at['max', 0]
    latmin = df_lats.describe().at['min', 0]
    map = Basemap(llcrnrlon=lonmin - 0.5, llcrnrlat=latmin - 0.5, urcrnrlon=lonmax + 0.5, urcrnrlat=latmax + 0.5,
                  resolution='l', projection='tmerc', lat_0=df_lats.describe().at['50%', 0],
                  lon_0=df_lons.describe().at['50%', 0])
    map.drawmapboundary(fill_color='aqua')
    map.fillcontinents(color='#cc9955', lake_color='aqua', zorder=0)
    map.drawcoastlines(color='0.15')
    map.drawparallels(np.arange(latmin, latmax, (latmax - latmin) / 5), labels=[False, True, True, False])
    map.drawmeridians(np.arange(lonmin, lonmax, (lonmax - lonmin) / 6), labels=[False, True, True, False])

    special_x, special_y = map(special_lons, special_lats)
    plt.scatter(special_x, special_y, c='m')

    x, y = map(lons, lats)
    map.quiver(x, y,
               u10, v10, speed,
               cmap=plt.cm.autumn)

    cb = map.colorbar(location='bottom', format='%d', label='wind speed')
    cb.set_ticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    cb.set_ticklabels([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    plt.title("Average wind speed is " + '%f' % speed_mean +'\n'+"date: "+filename, x=0.5, y=1.1)
    plt.savefig("./fig/"+filename+'.jpg', dpi=100)
    print("完成:"+filename)
    plt.clf()
    plt.cla()
    plt.close()

if __name__ == '__main__':

    name_list =list( pd.read_csv("new_time_name.csv")["time"])
    for i in name_list:
        plot_u10_v10(i)



