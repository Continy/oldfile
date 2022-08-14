import copy
import pandas as pd
import matplotlib.pyplot as plt
import math
from mpl_toolkits.basemap import Basemap
from pylab import *
import numpy as np
from scipy import interpolate
import pylab as pl
def improved(meteo):
    u10 = np.array(list(meteo["u10"]))
    v10 = np.array(list(meteo["v10"]))
    u10 = u10.astype(float)
    meteo["u10"] = u10

    v10 = v10.astype(float)
    meteo["v10"] = v10
    wind_speed10 = np.sqrt(u10 * u10 + v10 * v10)
    meteo['wind_speed10'] = wind_speed10
    return meteo