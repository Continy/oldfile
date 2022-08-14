import pandas as pd
import numpy as np
import datetime

df = pd.read_csv(r'C:\Users\zihaozhang\Desktop\iship_iss_jw.csv')
#输入气象数据的基本信息

print("输入的时间格式为YYYY-MM-DD HH:MM:SS")
time1 = input("请输入气象数据开始时间：")
time2 = input("请输入气象数据结束时间：")
dur = input("请输入时间间隔(单位为H/M/S): ")
time = input("请输入时间的维度： ")
time = int(time)


#传出来的气象数据变量名为df
#异常值处理
'''
df.loc[(df['u10'] > 40) | (df['u10'] < -50), 'u10'] = np.nan
df.loc[(df['v10'] > 40) | (df['v10'] < -64), 'v10'] = np.nan
df.loc[(df['cdww'] > 0.0072) | (df['cdww'] < 0.0004), 'cdww'] = np.nan
df.loc[(df['mwp'] > 19) | (df['mwp'] < 0), 'mwp'] = np.nan
df.loc[(df['pp1d'] > 25) | (df['pp1d'] < 1), 'pp1d'] = np.nan
df.loc[(df['shww'] > 20) | (df['shww'] < 0), 'shww'] = np.nan
df.loc[(df['dwww'] > 1.5) | (df['dwww'] < 0), 'dwww'] = np.nan
df.loc[(df['wsk'] > 1) | (df['wsk'] < -0.4), 'wsk'] = np.nan
df.loc[(df['wsp'] > 42) | (df['wsp'] < 0), 'wsp'] = np.nan
df.loc[(df['wss'] > 0.12) | (df['wss'] < 0), 'wss'] = np.nan
'''

#缺失值插入
for i in range(0, len(df), time):
    df1 = df.iloc[i:i+time, :].dropna()
    if len(df1) >= 2:
        time1 = datetime.datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
        time2 = datetime.datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
        idx = pd.date_range(time1, time2, freq=dur)
        df.iloc[i:i+time, :] = df.iloc[i:i+time, :].reindex(idx)
        df.iloc[i:i+time, :] = df.iloc[i:i+time, :].interpolate(limit_direction='both')
    else:
        continue




