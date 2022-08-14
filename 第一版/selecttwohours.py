import pymysql
import csv
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from get_simplify import simplify
from pre_routes import pre
from get_routes import routes
from wind_speed10 import improved
from div_routes import *
import numpy as np



con = pymysql.connect(host='localhost', user='root', password='YANZIhome$&Pp',
                      database='mysql', charset='utf8', use_unicode=True)
cursor = con.cursor()
#ship_sql="SELECT SAMPLE_TIMESTAMP , WPL_LATITUDE,WPL_LONGITUDE FROM iship_iss_jw "

#sql="SELECT * FROM user"




#open('C:/Users/zihaozhang/Desktop/ship_working2.csv', "w", encoding='utf8', newline='')

#ship_df = pd.read_sql(ship_sql, con)
#ship_df.to_csv('C:/Users/zihaozhang/Desktop/ship_working.csv',index=True)

#time_loc_permin_notna = simplify(ship_df)
#pre_routes = pre(time_loc_permin_notna)
#routes = routes(pre_routes)
#SQL="SELECT TIME_TO_SEC 2021-05-11 16:00:00 "

meteo_sql_1 = "SELECT * FROM a WHERE time >= "

#meteo_sql_2 = "time"

meteo_sql_2 = "'2021-05-11 16:00:00'"
meteo_sql_3 = "AND time<= date_add("
meteo_sql_4 = ",interval 2 day)"

meteo_sql=meteo_sql_1+meteo_sql_2+meteo_sql_3+meteo_sql_2+meteo_sql_4


meteo_df = pd.read_sql(meteo_sql, con)

meteo_df = improved(meteo_df)
print(meteo_df)
meteo_df.to_csv('C:/Users/zihaozhang/Desktop/ship_working2.csv',index=True)

#for i in range(len(routes)):
    #departure_time = routes.loc[i, 'departure']
    #arrival_time = routes.loc[i, 'arrival']
    #div_one_route(departure_time, arrival_time, time_loc_permin_notna, meteo_df, index=i + 1, DPI=400)

