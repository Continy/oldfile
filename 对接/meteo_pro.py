import pandas as pd
import numpy as np

def meteo_process(df):#df为气象数据的dataframe
    tmp1 = df.drop_duplicates(['time'])
    dur = len(tmp1)#得到时间的长度
    df = df.set_index('time')#将时间设置为索引
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
    for i in range(0, len(df), dur):#把同一地点dur之内的气象数据丢进循环,根据时间连续性进行插值(+1是因为经历dur小时，需要dur+1个时间点。例如：从今天0点到明天0点，是25个点)
        df1 = df.iloc[i:i+dur, :].dropna()#删除所有有空缺值的行
        if len(df1) >= 2:#如果删除空缺值后还剩2行以上即可做插值
            df.iloc[i:i+dur, :] = df.iloc[i:i+dur, :].interpolate(limit_direction='both')#线性插值
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














