import copy
import pandas as pd
import matplotlib.pyplot as plt
import math
from mpl_toolkits.basemap import Basemap
from pylab import *
import numpy as np
from scipy import interpolate
import pylab as pl
import calendar
import time

def dmto101(a):
    if np.isnan(a):
        return None
    degrees = math.floor(a/100)
    minutes = (a/100 - math.floor(a/100)) * 100
    b = degrees + minutes/60
    b = float('%.6f' % b) #保留小数点后六位
    return b

def dmto10(a):

    return a

#返回DataFrame:used_ship_info
def read_iship(iship_path):
    iship = pd.read_csv(iship_path, low_memory=False)
    info = iship[["SAMPLE_TIMESTAMP", 'RMC_LATITUDE', 'RMC_LONGITUDE', 'RMC_GROUND_SPEED']]
    new_time_name = []
    shiplats = []
    shiplons = []
    ground_speed = []
    for i in info["SAMPLE_TIMESTAMP"]:
        new_time_name.append(i.replace('/', '_').replace(':', '_'))

    for i in info["RMC_LATITUDE"]:
        shiplats.append(dmto10(i))

    for i in info["RMC_LONGITUDE"]:
        shiplons.append(dmto10(i))

    for i in info["RMC_GROUND_SPEED"]:
        ground_speed.append(i)

    used_ship_info = pd.DataFrame(
        {'SAMPLE_TIMESTAMP': new_time_name, 'RMC_LATITUDE': shiplats, 'RMC_LONGITUDE': shiplons,
         'RMC_GROUND_SPEED': ground_speed})
    return used_ship_info

def get_day_of_year(year, month, day):
    month_of_days31 = [1, 3, 5, 7, 8, 10, 12]
    month_of_days30 = [4, 6, 9, 11]
    if month == 1:
        return day

    if month == 2:
        return day + 31

    days_of_31_num = 0
    days_of_30_num = 0
    # 31天月份数
    for days_of_31 in month_of_days31:
        if days_of_31 < month:
            days_of_31_num += 1
        else:
            break

    # 30天月份数
    for days_of_30 in month_of_days30:
        if days_of_30 < month:
            days_of_30_num += 1
        else:
            break

    return days_of_31_num * 31 + days_of_30_num * 30 + (29 if calendar.isleap(year) else 28) + day

def ship_time_value(timestamp):
    timestamp = timestamp.replace("_",' ').replace(":",' ').replace("/",' ')
    time_list = timestamp.split()
    day = int(time_list[0])
    month = int(time_list[1])
    year = int(time_list[2])
    hour = int(time_list[3])
    minute = int(time_list[4])
    second = int(time_list[5])
    t = float(3600*24 * (get_day_of_year(year,month,day) -1) + 3600 * 24 * 365 * year + hour *3600 + minute * 60 + second)
    return t

def meteo_time_value(timestamp):
    """timestamp = timestamp.replace("_",' ').replace(":",' ').replace("/",' ')
    time_list = timestamp.split()
    day = int(time_list[2])
    month = int(time_list[1])
    year = int(time_list[0])
    hour = int(time_list[3])
    minute = int(time_list[4])
    second = 0
    t = float(3600*24 * (get_day_of_year(year,month,day) -1) + 3600 * 24 * 365 * year + hour *3600 + minute * 60 + second)
    return t"""
    return ship_time_value(timestamp)

#返回DataFrame:routes
def get_routes(iship_path):
    used_ship_info = read_iship(iship_path)
    used_ship_info = used_ship_info[
        ["SAMPLE_TIMESTAMP", 'RMC_LATITUDE', 'RMC_LONGITUDE', 'RMC_GROUND_SPEED']]
    used_ship_info = used_ship_info[used_ship_info['RMC_LATITUDE'].notna()]
    used_ship_info = used_ship_info[used_ship_info['RMC_GROUND_SPEED'].notna()]
    # 可知选取的所有航行数据中，维度位于36.590880到37.4323之间，且经度位于121.228到126.35981之间
    ship_info_description = used_ship_info.describe(include='all')
    lon_min = ship_info_description.at['min', 'RMC_LONGITUDE']
    lon_max = ship_info_description.at['max', 'RMC_LONGITUDE']


    # 接下来将得到一系列到达两个港口的时间戳

    # 第一个条件是,RMC_GROUND_SPEED < 0.1，表示船是停着的
    park_port = used_ship_info[(used_ship_info['RMC_GROUND_SPEED'] < 0.1)]

    # 第二个条件是,根据经度判断船是停在左港口还是右港口
    left_port = park_port[
        (abs(park_port['RMC_LONGITUDE'] - lon_min) <= (lon_max - lon_min) * 10e-2)].reset_index(level=None,
                                                                                                drop=False,
                                                                                                inplace=False,
                                                                                                col_level=0,
                                                                                                col_fill='')
    right_port = park_port[
        (abs(park_port['RMC_LONGITUDE'] - lon_max) <= (lon_max - lon_min) * 10e-2)].reset_index(level=None,
                                                                                                drop=False,
                                                                                                inplace=False,
                                                                                                col_level=0,
                                                                                                col_fill='')

    # 第三个条件是，对于某侧港口，既是终点又是起点的相邻的两个时间必须超过半天
    # 我们只需要记录列表中，比后面的时间数值小超过一天的，就可以记录这两个端点

    left_port_time_1 = list(left_port["SAMPLE_TIMESTAMP"])
    left_port_time_2 = [left_port_time_1[0]]

    for i in range(len(left_port_time_1) - 1):
        if (ship_time_value(left_port_time_1[i + 1]) - ship_time_value(left_port_time_1[i]) >= 60 * 60 * 24):
            left_port_time_2.append(left_port_time_1[i])
            left_port_time_2.append(left_port_time_1[i + 1])

    right_port_time_1 = list(right_port["SAMPLE_TIMESTAMP"])
    right_port_time_2 = [right_port_time_1[0]]

    for i in range(len(right_port_time_1) - 1):
        if (ship_time_value(right_port_time_1[i + 1]) - ship_time_value(right_port_time_1[i]) >= 60 * 60 * 24):
            right_port_time_2.append(right_port_time_1[i])
            right_port_time_2.append(right_port_time_1[i + 1])

    # pd.DataFrame({'SAMPLE_TIMESTAMP': left_port_time_2}).to_csv('left_port_time.csv')
    # pd.DataFrame({'SAMPLE_TIMESTAMP': right_port_time_2}).to_csv('right_port_time.csv')

    # 下一步是输出一个[departure,arrival]的时间戳，表示一段去或者返的航线
    temp = []
    for i in range(len(left_port_time_2)):
        temp.append('left')
    for i in range(len(right_port_time_2)):
        temp.append('right')
    temp_timevalue = []
    for i in left_port_time_2 + right_port_time_2:
        temp_timevalue.append(ship_time_value(i))

    temp2 = pd.DataFrame(
        {'SAMPLE_TIMESTAMP': left_port_time_2 + right_port_time_2, 'Port': temp, 'time_value': temp_timevalue})
    temp3 = temp2.sort_values('time_value', ascending=True, inplace=False).reset_index(level=None, drop=False,
                                                                                       inplace=False, col_level=0,
                                                                                       col_fill='')


    ship_routes = []
    for i in range(1, len(temp3)):
        a = temp3.loc[i, 'Port']
        b = temp3.loc[i - 1, 'Port']
        # 从b到a
        if (a != b):
            if (a != 'left'):
                ship_routes.append([temp3.loc[i - 1, 'SAMPLE_TIMESTAMP'], temp3.loc[i, 'SAMPLE_TIMESTAMP'], 'going'])
            else:
                ship_routes.append([temp3.loc[i - 1, 'SAMPLE_TIMESTAMP'], temp3.loc[i, 'SAMPLE_TIMESTAMP'], 'return'])
    departure = []
    arrival = []
    voyage = []
    trip_type = []
    for i in ship_routes:
        departure.append(i[0])
        arrival.append(i[1])
        voyage.append((ship_time_value(i[1]) - ship_time_value(i[0])) / 3600)
        trip_type.append(i[2])
    routes = pd.DataFrame({'departure': departure, 'arrival': arrival, 'voyage_time': voyage, 'trip_type': trip_type})
    # routes = routes[(routes['voyage_time'] <= 24 )]
    routes.to_csv("ship_routes.csv")
    return routes

#返回平均值，注意start_time是iship替换成_后的字符串
def get_data_mean(rectangle,target_name,start_time,end_time,meteo):
    #([start_time,end_time])
    time_value_min = ship_time_value(start_time) - (ship_time_value(end_time) - ship_time_value(start_time)) * 0.1
    time_value_max = ship_time_value(end_time) + (ship_time_value(end_time) - ship_time_value(start_time)) * 0.1

    rectangle_data = meteo[(meteo["latitude"] >= rectangle[2]) & (meteo["latitude"] <= rectangle[3])
                           & (meteo["longitude"] >= rectangle[0]) & (meteo["longitude"] <= rectangle[1])
                           ]
    #print(rectangle_data)
    rectangle_data2 = rectangle_data[(meteo['time_value'] >= time_value_min) & (meteo['time_value'] <= time_value_max)]
    #print([time_value_min,time_value_max])
    notna_rec_data = rectangle_data2[rectangle_data[target_name] != '--']
    t=[]
    for i in notna_rec_data[target_name]:
        t.append(float(i))
    if (len(t) < 1):
        return NAN
    data_mean = pd.DataFrame(t).mean()[0]
    return data_mean

def ship_timestamp(timestamp):
    timestamp = timestamp.replace("_", ' ').replace(":", ' ').replace("/", ' ')
    time_list = timestamp.split()
    day = int(time_list[0])
    month = int(time_list[1])
    year = int(time_list[2])
    minute = int(time_list[4])
    second = int(time_list[5])
    return str(day)+'/'+str(month)+'/'+str(year)+' '+time_list[3]+':'+str(minute)+':'+str(second)

#没有返回值的函数，需要所在目录有叫'route_fig'和'route_meteo_mean'的两个文件夹(默认是空的)
def div_one_route(departure_time,arrival_time,time_loc,meteo,schedule,index = 0,point_num=100,DPI=400):
    time_loc_description = time_loc.describe()
    latmin = time_loc_description.at['min', 'RMC_LATITUDE']
    latmax = time_loc_description.at['max', 'RMC_LATITUDE']
    lonmin = time_loc_description.at['min', 'RMC_LONGITUDE']
    lonmax = time_loc_description.at['max', 'RMC_LONGITUDE']

    lon_dpt = float(time_loc[time_loc["SAMPLE_TIMESTAMP"] == departure_time]["RMC_LONGITUDE"])
    lat_dpt  = float(time_loc[time_loc["SAMPLE_TIMESTAMP"] == departure_time]["RMC_LATITUDE"])
    dpt_index = time_loc[time_loc["SAMPLE_TIMESTAMP"] == departure_time]["RMC_LONGITUDE"].index[
        0]  # 注意，这里记录index，是为了避免后面循环的判断降低运行速度
    lon_arvl = float(time_loc[time_loc["SAMPLE_TIMESTAMP"] == arrival_time]["RMC_LONGITUDE"])
    lat_arvl  = float(time_loc[time_loc["SAMPLE_TIMESTAMP"] == arrival_time]["RMC_LATITUDE"])
    arvl_index = time_loc[time_loc["SAMPLE_TIMESTAMP"] == arrival_time]["RMC_LONGITUDE"].index[0]


    div_lon1 = lon_dpt + (lon_arvl - lon_dpt) / 3  # 距离起点最近
    div_lon2 = lon_arvl - (lon_arvl - lon_dpt) / 3  # 距离终点最近

    # 读取起点到终点之间的经纬度

    df = time_loc.loc[dpt_index: arvl_index + 1, ["SAMPLE_TIMESTAMP", 'RMC_LATITUDE', 'RMC_LONGITUDE']]

    ## 插值不可以有重复的值，因此删除重复的lons
    #df.drop_duplicates(subset="RMC_LONGITUDE", keep='first', inplace=True)
    #df.reset_index(level=None, drop=False, inplace=True, col_level=0, col_fill='')

    lats = np.array(list(df["RMC_LATITUDE"]))
    lons = np.array(list(df["RMC_LONGITUDE"]))

    x_index_3 = len(lons)-1 #这里的index是相对列表来说的，而不是df
    x_index_0 = 0
    x_index_1 = -1
    x_index_2 = -1

    dlt_1 = []
    dlt_2 = []
    for i in lons:
        dlt_1.append(abs(i-div_lon1) )
        dlt_2.append(abs(i-div_lon2))
    t = 0
    dlt1_min = min(dlt_1)
    dlt2_min = min(dlt_2)
    for i in lons:
        if (abs(i-div_lon1) == dlt1_min):
            x_index_1 = t
        if (abs(i - div_lon2) == dlt2_min):
            x_index_2 = t
        t = t + 1
    div_lon1 = lons[x_index_1]
    div_lon2 = lons[x_index_2]
    div_lat1 = lats[x_index_1]
    div_lat2 = lats[x_index_2]



    # 输出三个区域的矩形[x_1,x_2,y_1,y_2]
    x11 = min(lons[x_index_0:x_index_1+1])
    x12 = max(lons[x_index_0:x_index_1+1])
    x21 = min(lons[x_index_1+1:x_index_2+1])
    x22 = max(lons[x_index_1+1:x_index_2+1])
    x31 = min(lons[x_index_2+1:x_index_3+1])
    x32 = max(lons[x_index_2+1:x_index_3+1])

    y11 = min(lats[x_index_0:x_index_1 + 1])
    y12 = max(lats[x_index_0:x_index_1 + 1])
    y21 = min(lats[x_index_1 + 1:x_index_2 + 1])
    y22 = max(lats[x_index_1 + 1:x_index_2 + 1])
    y31 = min(lats[x_index_2 + 1:x_index_3 + 1])
    y32 = max(lats[x_index_2 + 1:x_index_3 + 1])
    three_rectangles = [[x11, x12, y11, y12], [x21, x22, y21, y22], [x31, x32, y31, y32]]

    t = 0
    for i in lats:
        if (i==y11):
            y11_index = t
        if (i==y12):
            y12_index = t
        if (i==y21):
            y21_index = t
        if (i==y22):
            y22_index = t
        if (i==y31):
            y31_index = t
        if (i==y32):
            y32_index = t
        t = t + 1
    red_x=[lons[y11_index],lons[y12_index],lons[y21_index],lons[y22_index],lons[y31_index],lons[y32_index]]
    red_y=[lats[y11_index],lats[y12_index],lats[y21_index],lats[y22_index],lats[y31_index],lats[y32_index]]
    '''
    ## 为了做出航迹，这里用均匀的点进行插值;
    ## 获得均匀的点，以便作图
    #uniform_x = []
    #for i in range(point_num):
        #uniform_x.append(lon_dpt + (lon_arvl - lon_dpt) / (point_num - 1) * i)
    #f = interpolate.interp1d(lons, lats, kind="slinear")  # 分段线性插值slinear
    #new_y = f(uniform_x)
    '''
    now = time.time()
    # 作图
    map = Basemap(llcrnrlon=lonmin - 0.5, llcrnrlat=latmin - 0.5, urcrnrlon=lonmax + 0.5, urcrnrlat=latmax + 0.5,
                  resolution='l', projection='tmerc', lat_0=(latmax + latmin) / 2,
                  lon_0=(lonmax + lonmin) / 2)
    print(time.time()-now)
    now = time.time()
    #map.arcgisimage(server='http://server.arcgisonline.com/arcgis/rest/services',service='ESRI_Imagery_World_2D', xpixels = 1500, verbose= True)
    map.drawmapboundary(fill_color='aqua')
    map.fillcontinents(color='#cc9955', lake_color='aqua', zorder=0)
    map.drawcoastlines(color='0.15')
    map.drawparallels(np.arange(latmin, latmax, (latmax - latmin) / 5), labels=[False, True, True, False])
    map.drawmeridians(np.arange(lonmin, lonmax, (lonmax - lonmin) / 6), labels=[False, True, True, False])

    print(time.time() - now)
    now = time.time()

    div_x, div_y = map([lon_dpt, div_lon1, div_lon2, lon_arvl],
                       [lat_dpt, div_lat1, div_lat2,lat_arvl ])

    map.scatter(lons, lats,latlon= True, c='y',s=1)
    map.scatter([lon_dpt, div_lon1, div_lon2, lon_arvl], [lat_dpt, div_lat1, div_lat2,lat_arvl ],latlon=True, c='m')
    map.scatter(red_x,red_y, latlon=True, c='r',s = 75)
    plt.text(div_x[0], div_y[0], 'Depature')
    plt.text(div_x[1], div_y[1], 'Point1')
    plt.text(div_x[2], div_y[2], 'Point2')
    plt.text(div_x[3], div_y[3], 'Arrivl')
    plt.title("Route "+'%d' % index +'\n'+ ship_timestamp(departure_time) +' to '+ ship_timestamp(arrival_time)
              +'\n'+ schedule.at[int(index-1),'trip_type'], x=0.5, y=1.2)
    plt.text((div_x[0] + div_x[1]) / 2, (div_y[0] + div_y[1]) / 2, 'Zone1', color='m')
    plt.text((div_x[1] + div_x[2]) / 2, (div_y[1] + div_y[2]) / 2, 'Zone2', color='m')
    plt.text((div_x[2] + div_x[3]) / 2, (div_y[2] + div_y[3]) / 2, 'Zone3', color='m')

    print(time.time() - now)
    now = time.time()

    meteo = meteo.loc[:, [ 'time','latitude','longitude','mwp', 'swh', 'mwd','time_value']]
    meteo = meteo.reset_index(level=None, drop=False, inplace=False, col_level=0, col_fill='')


    #pd.DataFrame(meteo['time_value']).to_csv('meteo1.csv')


    data_names = [ 'mwp', 'swh', 'mwd']
    data_mean = []
    for i in data_names:
        mean_temp = []
        for j in three_rectangles:
            #print([departure_time,arrival_time])
            mean_temp.append(get_data_mean(j, i,departure_time,arrival_time, meteo))
        data_mean.append(mean_temp)
        #print(mean_temp)
    #pd.DataFrame(data_mean).to_csv('meteo1.csv')
    data_mean_df = pd.DataFrame({
                                 'mwp': data_mean[0], 'swh': data_mean[1],
                                 'mwd': data_mean[2]}, index=['Zone1', 'Zone2', 'Zone3'])
    data_mean_df.to_csv('./route_meteo_mean/route'+ '%d' % index +'.csv')
    print(data_mean_df)
    print("完成：route" + '%d' % index + '.csv')

    print(time.time() - now)
    now = time.time()


    map.plot([x11, x11], [y12, y11], 'go-', latlon=True, linewidth=2)
    map.plot([x11, x12], [y11, y11], 'go-', latlon=True)
    map.plot([x12, x12], [y11, y12], 'go-', latlon=True)
    map.plot([x12, x11], [y12, y12], 'go-', latlon=True)
    map.plot([x21, x21], [y22, y21], 'go-', latlon=True)
    map.plot([x21, x22], [y21, y21], 'go-', latlon=True)
    map.plot([x22, x22], [y21, y22], 'go-', latlon=True)
    map.plot([x22, x21], [y22, y22], 'go-', latlon=True)
    map.plot([x31, x31], [y32, y31], 'go-', latlon=True)
    map.plot([x31, x32], [y31, y31], 'go-', latlon=True)
    map.plot([x32, x32], [y31, y32], 'go-', latlon=True)
    map.plot([x32, x31], [y32, y32], 'go-', latlon=True)
    plt.savefig('./route_fig/route' + '%d' % index + '.jpg', dpi= DPI)
    plt.show()
    print("完成：route"+ '%d' % index + '.jpg')
    plt.clf()
    plt.cla()
    plt.close()


def divide_all_routes(iship_path,meteo_path):
    used_ship_info = read_iship(iship_path)
    used_ship_info = used_ship_info[used_ship_info['RMC_GROUND_SPEED'].notna()]
    used_ship_info.reset_index(level=None, drop=False, inplace=True, col_level=0, col_fill='')

    time_loc = used_ship_info[
        ["SAMPLE_TIMESTAMP", 'RMC_LATITUDE', 'RMC_LONGITUDE']]
    s_time_value = []
    for i in time_loc["SAMPLE_TIMESTAMP"]:
        i = i.replace('/', '_').replace(':', '_')
        i = i.replace('-', '_')
        s_time_value.append(ship_time_value(i))
    time_loc['time_value'] = s_time_value
    time_loc.sort_values('time_value', axis=0, ascending=True, inplace=True, kind='quicksort')
    time_loc.reset_index(level=None, drop=False, inplace=True, col_level=0, col_fill='')

    schedule = get_routes(iship_path)
    schedule.reset_index(level=None, drop=False, inplace=True, col_level=0,
                                                          col_fill='')
    m_time_value = []
    meteo = pd.read_csv(meteo_path,error_bad_lines=False,low_memory=False)
    time = []
    for i in meteo["time"]:
        i = i.replace('/', '_').replace(':', '_')
        i = i.replace('-', '_')
        time.append(i)
        m_time_value.append(meteo_time_value(i))
    meteo['time_value'] = m_time_value

    meteo['time'] = time
    meteo.sort_values('time_value', axis=0, ascending=True, inplace=True, kind='quicksort')
    meteo.reset_index(level=None, drop=False, inplace=True, col_level=0, col_fill='')

    for i in range(len(schedule)):
        departure_time = schedule.loc[i, 'departure']
        arrival_time = schedule.loc[i, 'arrival']
        div_one_route(departure_time, arrival_time, time_loc, meteo, schedule, index=i + 1, DPI=400)


if __name__ == '__main__':
    iship_path = 'ship.csv'
    meteo_path = 'meteo.csv'
    divide_all_routes(iship_path,meteo_path)















