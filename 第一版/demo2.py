import pymysql
import csv
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine

from wind_speed10 import improved

from plot_wind import *
from meteo_pro import *
import numpy as np

ship = pd.read_csv('ship_working.csv',index_col=0)
new_time_name = []
for i in ship["SAMPLE_TIMESTAMP"]:
    t = datetime.datetime.strptime(i.replace('-', '_').replace(':', '_'), '%Y_%m_%d %H_%M_%S')
    d = str(t.month) + '/' +str(t.day) +' '+str(t.hour)
    new_time_name.append(d)

ship.drop('RMC_UTC_DATE_YMD',axis = 1,inplace = True)
ship.drop('RMC_UTC_DATE',axis = 1,inplace = True)
ship[['RMC_LATITUDE','RMC_LONGITUDE']]=ship[['RMC_LONGITUDE','RMC_LATITUDE']]
ship["date"]=new_time_name
pd.DataFrame(ship).to_csv('ship_new.csv')