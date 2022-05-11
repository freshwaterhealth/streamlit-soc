# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 14:07:56 2022

@author: kshaad
"""

import geopandas as gpd
import streamlit as st
import zipfile
import os
import rioxarray as rxr
import numpy as np
import tempfile
from shapely.geometry import mapping
import gc
import random

rr=random.randrange(10,20000,1)

@st.cache(suppress_st_warning=True, ttl=900)
def readShp(uploaded_file):
    with tempfile.TemporaryDirectory() as tmpdirname:
        try:
            with zipfile.ZipFile(uploaded_file) as z:
                z.extractall(tmpdirname) 
        except:
            st.error("Faliure extracting basin shapefile")
        pth=os.path.join(os.getcwd(),tmpdirname) 
        for item in os.listdir(path=pth):
            if (item.__contains__('.shp')):                  
                return gpd.read_file(pth+"/"+item)
        #Reach here, means no shapefile
        st.error("No valid file found in zipped folder")
        st.stop()
        
def readRaster(uploaded_file):
    tmdir='rastemp'+str(rr)
    with zipfile.ZipFile(uploaded_file) as z:
        z.extractall(tmdir) 
    pth=os.path.join(os.getcwd(),tmdir)  
    for item in os.listdir(path=pth):
        if (item.__contains__('.tif')):            
            lcdata = rxr.open_rasterio(pth+"/"+item,masked=False)
            lcdata_clipped=lcdata.rio.clip(basindata.geometry.apply(mapping),basindata.crs)         
            arr=np.array(lcdata_clipped[0,:,:])    
            lcdata.close()
    arr[arr==-999.0]=np.nan
    return np.nanmean(arr)

def norm(x):
    if x>0:
        return 1
    else:
        y=(x+1.)
        return y

st.title("FHI: Groundwater Storage")
gc.enable()
with st.expander("Input requirements", expanded=False):
    st.markdown("""
                **Provide input data in following format.** 
                    
                    1. Basin shapefile: Atleast .shp,.shx,.dbf and.prj as a zipped file. 
                    2. Gloabal groundwater raster trends, [download here](https://drive.google.com/file/d/13pJrzC9KQSnDVljdIcFNQX7Dta4_CzZ4/view?usp=sharing)

                The code uses global results from [Regional Analysis of GRACE Groundwater Data](https://doi.org/10.1111/1752-1688.12968) and should be only used in absence of local data of groundwater.
                A raster is created by applying a Seasonal Mann-Kendall (SKM) test on the results to obtain overall direction of groundwater storage.
                Tau value (from the SKM) is used to calcuate the index.
        """)
st.sidebar.title("Inputs")
st.sidebar.subheader("Step 1: Upload Basin Polygon Shapefile")
uploaded_file = st.sidebar.file_uploader("Upload Zipped Shapefile",type=['zip'])
if uploaded_file is not None:
    try:
        basindata=readShp(uploaded_file)
    except:
        st.error("Faliure loading basin shapefile")

st.sidebar.subheader("Step 2: Upload Tau Raster File")
uploaded_file = st.sidebar.file_uploader("Upload Zipped Geotiff",type=['zip'])
if uploaded_file is not None:
    try:
        sc=100*norm(readRaster(uploaded_file))
        st.success("**Indicator Score:**")
        st.metric("GWsd", round(sc,2), "")
        gc.collect()
    except:
        st.error("Faliure intersecting with Raster")
