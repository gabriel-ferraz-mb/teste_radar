# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 16:44:43 2022

@author: gabriel.ferraz
"""


# =============================================================================
# /* FUNCIONALIDADES
# Código para montar um dataset com as variáveis espectrais das imagens do Sentinel-2.
# */ 
# =============================================================================

# // Limite da área de interesse - disponível no Assets

import ee
import pandas as pd
#import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm, gamma, f, chi2
import IPython.display as disp


ee.Initialize()
aoi = ee.FeatureCollection(r'C:\Temp\gee\aoi.shp');
poi = ee.Geometry.Point(-45.2068123,-21.7643639)

sentinel1 = ee.ImageCollection('COPERNICUS/S1_GRD').filterDate('2020-10-01', '2021-04-01').filterBounds(poi);
s1_poi = sentinel1.getInfo()

vvVhIw = sentinel1.filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')).filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')).filter(ee.Filter.eq('instrumentMode', 'IW'));
#// Filter to get images with VV and VH dual polarization.
vvVhIwDesc = vvVhIw.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING')).map(lambda img: img.set('date', ee.Date(img.date()).format('YYYYMMdd'))).sort('date')
# Filter to get images collected in interferometric wide swath mode.
vv_list = vvVhIwDesc.toList(vvVhIwDesc.size())


timestamplist = (vvVhIwDesc.aggregate_array('date').map(lambda d: ee.String('T').cat(ee.String(d))).getInfo())
timestamplist

def omnibus(im_list, m = 4.4):
    """Calculates the omnibus test statistic, monovariate case."""
    def log(current):
        return ee.Image(current).log()

    im_list = ee.List(im_list)
    k = im_list.length()
    klogk = k.multiply(k.log())
    klogk = ee.Image.constant(klogk)
    sumlogs = ee.ImageCollection(im_list.map(log)).reduce(ee.Reducer.sum())
    logsum = ee.ImageCollection(im_list).reduce(ee.Reducer.sum()).log()
    return klogk.add(sumlogs).subtract(logsum.multiply(k)).multiply(-2*m)


#k = 10
hist = (omnibus(vv_list)).reduceRegion(ee.Reducer.fixedHistogram(0, 40, 200), geometry=poi, scale=10).get('constant').getInfo()
        
        