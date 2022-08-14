import pandas as pd
import numpy as np
import csv



if __name__ == '__main__':
    meteo = pd.read_csv("meteo_working.csv")

    notna_meteo = meteo[meteo["time"].notna()]
    time_meteo = notna_meteo["time"]
    time_data = set(time_meteo)

    bigdata=[]
    for i in time_data:
        bigdata.append(notna_meteo[(notna_meteo["time"]== i)] )

    new_time_name=[]
    for i in bigdata:
        i.to_csv('./bigdata/'+i["time"].iat[0].replace('/','_').replace(':','_')+'.csv')
        new_time_name.append(i["time"].iat[0].replace('/', '_').replace(':', '_'))

    pd.DataFrame(new_time_name).to_csv('new_time_name.csv')




