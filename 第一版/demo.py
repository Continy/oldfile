import pymysql
import csv
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine

from wind_speed10 import improved

from plot_wind import *
from meteo_pro import *
import numpy as np



con = pymysql.connect(host='localhost', user='root', password='YANZIhome$&Pp',
                      database='mysql', charset='utf8', use_unicode=True)
cursor = con.cursor()

meteo_sql_1 = "SELECT time,longitude,latitude,mwp,swh,mwd,u10,v10 FROM b WHERE unix_timestamp(time) >= unix_timestamp("

meteo_sql_2 = "'2021-05-18 8:00:00'"
meteo_sql_3 = ") AND unix_timestamp(time) <= unix_timestamp(date_add("
meteo_sql_4 = ",interval 3 day))"

meteo_sql=meteo_sql_1+meteo_sql_2+meteo_sql_3+meteo_sql_2+meteo_sql_4

print(meteo_sql)
meteo = pd.read_sql(meteo_sql, con)

meteo = improved(meteo)
print(0)
open('C:/Users/zihaozhang/Desktop/bigdata1.csv', "w", encoding='utf8', newline='')
pd.DataFrame(meteo).to_csv('bigdata1.csv')
meteo = meteo_process(meteo, 72)
open('C:/Users/zihaozhang/Desktop/bigdata2.csv', "w", encoding='utf8', newline='')
pd.DataFrame(meteo).to_csv('meteo.csv')
print(1)


