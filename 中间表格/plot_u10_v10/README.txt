这些代码主要是吧meteo数据中的u10、v10plot出来，并且把风速中位数前后5%的点用紫色标注出来。
地图是用basemap包。

get_by_time的输入是meteo.csv的文件路径，set（）可以得到所有不重复的时间戳，再在不重复的时间戳里循环，每种时间戳形成一个DataFrame并且生成一个csv文件。
同时，生成'new_time_name.csv'便于进一步处理的for循环。注意，由于命名规则，时间戳的‘’/‘’'’:‘’字符被替换成‘’_‘’。

plot_all里的plot_u10_v10只需要读取'new_time_name.csv'中的文件名字，就可以做出图案，并且导出jpg。
注意导出的文件路径，不存在的文件夹需要提前在工作文件夹建立好。

---by 陈俊璇