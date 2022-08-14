import pandas as pd
import numpy as np
import time
from geopy.distance import geodesic
def ang(a):
    a = a / 100
    b = int(a)
    c = a - b
    e = c / 3 * 5
    f = b + e

    return f





def meteo_process(df, dur):#df为气象数据的dataframe,dur为所需要的未来的小时(整数)
   # df = df.set_index('time')#将时间设置为索引
    df = df.replace('--', np.nan)#(这一步可以删除，数据库给出的一般是nan，因为测试的数据含有‘--’，需要转换，才在这里给出这一步）
    #把数据类型从object换为float(这一步可以删除，数据库给出的类型一般是float，因为测试的数据需要转换，才在这里给出这一步）
    df['mwp'] = pd.to_numeric(df['mwp'], errors='coerce')
    df['mwd'] = pd.to_numeric(df['mwd'], errors='coerce')
    df['swh'] = pd.to_numeric(df['swh'], errors='coerce')

    #异常值处理
    df.loc[(df['u10'] > 40) | (df['u10'] < -50), 'u10'] = np.nan#把u10>40和<-50的数设为空值
    df.loc[(df['v10'] > 40) | (df['v10'] < -64), 'v10'] = np.nan
    df.loc[(df['mwp'] > 19) | (df['mwp'] < 0), 'mwp'] = np.nan
    df.loc[(df['swh'] > 20) | (df['swh'] < 0), 'swh'] = np.nan
    df.loc[(df['mwd'] > 360) | (df['mwd'] < 0), 'mwd'] = np.nan


    #缺失值插入
    df = df.sort_values(by=['latitude', 'longitude'])#整理df,使其按地点排序
    for i in range(0, len(df), dur+1):#把同一地点dur之内的气象数据丢进循环,根据时间连续性进行插值(+1是因为经历dur小时，需要dur+1个时间点。例如：从今天0点到明天0点，是25个点)
        df1 = df.iloc[i:i+dur+1, :].dropna()#删除所有有空缺值的行
        if len(df1) >= 2:#如果删除空缺值后还剩2行以上即可做插值
            df.iloc[i:i+dur+1, :] = df.iloc[i:i+dur+1, :].interpolate(limit_direction='both')#线性插值
        else:#删除空缺值后只剩一行或没有则不可插值，跳出，进入下一个循环
            continue


    df = df.sort_values(by=['time', 'latitude'])#再将df按照时间和纬度排序
    df2 = df.drop_duplicates(['longitude'])#得到经度的个数
    for i in range(0, len(df), len(df2)):#把同一时间同一纬度的气象数据丢进循环,根据经度连续性进行插值
        df3 = df.iloc[i:i + len(df2), :].dropna()  # 删除所有有空缺值的行
        if len(df3) >= 2:#如果删除空缺值后还剩2行以上即可做插值
            df.iloc[i:i+len(df2), :] = df.iloc[i:i+len(df2), :].interpolate(limit_direction='both')#线性插值
        else:#删除空缺值后只剩一行或没有则不可插值，跳出，进入下一个循环
            continue


    df = df.sort_values(by=['time', 'longitude'])  # 再将df按照时间和经度排序
    df4 = df.drop_duplicates(['latitude'])  # 得到纬度的个数
    for i in range(0, len(df), len(df4)):#把同一时间同一纬度的气象数据丢进循环,根据经度连续性进行插值
        df5 = df.iloc[i:i + len(df4), :].dropna()  # 删除所有有空缺值的行
        if len(df5) >= 2:#如果删除空缺值后还剩2行以上即可做插值
            df.iloc[i:i+len(df4), :] = df.iloc[i:i+len(df4), :].interpolate(limit_direction='both')#线性插值
        else:#删除空缺值后只剩一行或没有则不可插值，跳出，进入下一个循环
            continue

    df = df.sort_values(by=['latitude', 'longitude'])#整理df,使其按地点排序
    return df



def iss_process(iss):
    iss = iss.dropna()  # 删除所有有空缺值的行
    iss = iss.reset_index(drop=True)#整理索引
    timestamp = []
    for k in range(len(iss)):
        iss.loc[k, 'RMC_LATITUDE'] = ang(iss.loc[k, 'RMC_LATITUDE'])
        iss.loc[k, 'RMC_LONGITUDE'] = ang(iss.loc[k, 'RMC_LONGITUDE'])
        iss.loc[k, 'RMC_LATITUDE'] = round(iss.loc[k, 'RMC_LATITUDE'], 6)  # 保留到小数点后6位
        iss.loc[k, 'RMC_LONGITUDE'] = round(iss.loc[k, 'RMC_LONGITUDE'], 6)
        tmp = iss.loc[k, 'RMC_UTC_DATE_YMD'][4:6:1] + iss.loc[k, 'RMC_UTC_DATE_YMD'][2:4:1] + iss.loc[k, 'RMC_UTC_DATE_YMD'][0:2:1] + iss.loc[k, 'RMC_UTC_DATE'][0:6:1]  # 把时间整理成年月日时分秒
        time1 = time.strptime(tmp, "%y%m%d%H%M%S")  # 转换成时间数组
        timestamp.append(time.mktime(time1))  # 转化成时间戳放入timestamp列表

    i = 1
    while i < len(iss):
        if iss.loc[i - 1, 'RMC_GROUND_SPEED'] >= 0.1 and iss.loc[i, 'RMC_GROUND_SPEED'] >= 0.1:  # 只对速度大于0.1的点进行判断。小于0.1时，无法判断
            span = timestamp[i] - timestamp[i - 1]
            coords_1 = (iss.loc[i - 1, 'RMC_LATITUDE'], iss.loc[i - 1, 'RMC_LONGITUDE'])
            coords_2 = (iss.loc[i, 'RMC_LATITUDE'], iss.loc[i, 'RMC_LONGITUDE'])
            distance = geodesic(coords_1, coords_2).m  # 两个地点之间的距离
            journey = iss.loc[i - 1, 'RMC_GROUND_SPEED'] * span  # 得到time内的船行路程
            if distance > journey * 3:  # 如果距离大于路程的三倍
                iss.loc[i, 'RMC_LATITUDE'] = np.nan  # 判断该地点异常并设为空值
                iss.loc[i, 'RMC_LONGITUDE'] = np.nan
                iss = iss.dropna()  # 删除空值行
                iss = iss.reset_index(drop=True)  # 重新整理索引
                timestamp.pop(i)  # 删除timestamp中对应的时间戳
                i = i  # 判断下一个点（因为下一个点前移，索引即为i）
            else:  # 如果符合
                i = i + 1  # 判断下一个点
        else:
            i = i + 1
    return iss












