import datetime
import pandas as pd
b = '2021-5-1 10:00:00'
e = '2021-5-2 0:00:00'
start = datetime.datetime.strptime(b, '%Y-%m-%d %H:%M:%S')
end = datetime.datetime.strptime(e, '%Y-%m-%d %H:%M:%S')
print(start.__lt__(end))
meteo_path = 'meteo_working.txt'
data = pd.read_csv(meteo_path,sep='\t')
meteo = data
date = []
for i in range(len(meteo)):
    t = datetime.datetime.strptime(meteo.loc[i, 'time'], '%Y-%m-%d %H:%M:%S')
    date.append(t)

meteo['date'] = date

df = meteo[
(meteo['date'].__gt__(start)) & (meteo['date'].__lt__(end) ) ]
print(df)