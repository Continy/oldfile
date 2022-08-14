from main import *
from meteo_pro import *
import datetime

meteo_path = 'meteo_working.txt'
data = pd.read_csv(meteo_path,sep='\t')
print('read meteo finished')

try:
    data = meteo_process(data)
    print('data preprocessing done!')
except Exception as e:
    print("except:", e)
    print('meteo_process() wrong! please check input file!')

data = data.reset_index()
trip_type = 'going'  #去返程
target_list = ['u10','v10','mwd', 'mwp', 'swh']  #所需数据
b = '2021-5-1 10:00:00'
zone_time=[2,3.5,7]
start_time = datetime.datetime.strptime(b, '%Y-%m-%d %H:%M:%S')

try:
    main_gat_meteo_mean(data, trip_type, target_list, start_time, zone_time)
    print('complete! please check meteo_mean.csv !')
except Exception as e:
    print("except:", e)
    print('main_gat_meteo_mean() wrong! please check input parameters!')