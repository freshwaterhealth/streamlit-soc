# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 14:39:33 2022

@author: kshaad
"""

import geopandas as gpd
import pandas as pd
import streamlit as st
import zipfile
import os
import rioxarray as rxr
import numpy as np
import tempfile
from shapely.geometry import mapping
import random
import matplotlib.pyplot as plt

rr=random.randrange(10,20000,1)
lc_list=[]
tot_cnt=0. 
blnShapeLoaded=False
blnRasterLoaded=False
blnRasterLookup=False

@st.cache(ttl=900)
def readShp(uploaded_file):
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(uploaded_file) as z:
            z.extractall(tmpdirname)   
        pth=os.path.join(os.getcwd(),tmpdirname) 
        for item in os.listdir(path=pth):
            if (item.__contains__('.shp')):                  
                return gpd.read_file(pth+"/"+item)
        #Reach here, means no shapefile
        st.error("No valid file found in zipped folder")
        st.stop()
        
@st.cache(suppress_st_warning=True, ttl=900)
def readRaster(uploaded_file):
    tmdir='rastemp'+str(rr)
    with zipfile.ZipFile(uploaded_file) as z:
        z.extractall(tmdir) 
    pth=os.path.join(os.getcwd(),tmdir)  
    for item in os.listdir(path=pth):
        if (item.__contains__('.tif')):            
            lcdata = rxr.open_rasterio(pth+"/"+item,masked=False)
            lcdata_clipped=lcdata.rio.clip(basindata.geometry.apply(mapping),basindata.crs)
            no_data=lcdata_clipped.rio.nodata          
            arr=np.array(lcdata_clipped[0,:,:])                       
            lcdata.close()
    for item in os.listdir(path=pth):
        os.remove(pth+"/"+item)
    os.rmdir(tmdir)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(arr)
    st.write(fig) 

    if arr.size == 0:
        st.error("No valid file found in zipped folder")
        st.stop()
    unique, counts = np.unique(arr, return_counts=True)
    t_cnt=0.
    for i in range(len(unique)):
        if (unique[i]!=no_data):
            lc_list.append(lc(unique[i],float(counts[i])))
            t_cnt=t_cnt+counts[i]  
    return t_cnt

class lc:
    def __init__(self, idl, nlc):
        self.idl=idl
        self.nlc=nlc
        self.desc=""
        self.wt=0.

      
st.title("FHI: Bank Modification")
with st.expander("Input requirements", expanded=False):
    st.markdown("""
                **Provide input data in following format.** 
                    
                    1. For river shapefile: Atleast .shp,.shx,.dbf and.prj as a zipped file.
                    2. For land cover: Atleast .tif and .tfw as a zipped file
                    3. For raster lookup, CSV table in following format: |value|description|weight| 
                    4. 'value' in raster lookup is the raster value corresponding to a land cover type (such as Water is 210)
                [Sample Raster lookup file](https://github.com/freshwaterhealth/fhiScripts/blob/main/01SampleDatasets/02_Ecosystem%20Vitality/LCN%20Mock%20Data/ESACCI-LC-Legend.csv)
        """)
st.sidebar.title("Inputs")
st.sidebar.subheader("Step 1: Enter buffer length around river")
buffrLen=st.sidebar.number_input("Buffer length (must be in same units are river shapefile)", value=100., min_value=0., step=0.01)
st.sidebar.subheader("Step 2: Upload River Outline")
uploaded_file = st.sidebar.file_uploader("Upload Zipped Shapefile",type=['zip'])
if uploaded_file is not None:
    try:
        basindata1=readShp(uploaded_file)
        blnShapeLoaded=True
        basindata=basindata1.buffer(buffrLen)
        
    except:
        st.error("Faliure loading river outline shapefile")
        
st.sidebar.subheader("Step 3: Basin Land cover")
uploaded_file = st.sidebar.file_uploader("Upload Zipped Geotiff",type=['zip'])
if uploaded_file is not None:
    try:
        if blnShapeLoaded == False:
            st.error("Load shapefile first")
            st.stop()
        tot_cnt=readRaster(uploaded_file)
        
        blnRasterLoaded=True
    except:
        st.error("Faliure loading landcover")

st.sidebar.subheader("Step 4: Upload Raster Lookup File")    
uploaded_file = st.sidebar.file_uploader("Upload CSV File",type=['csv'])
if uploaded_file is not None:
    try:
        if blnShapeLoaded == False or blnRasterLoaded==False:
                st.error("Input of basin outline and landcover needed before this step")
                st.stop()
        df=pd.read_csv(uploaded_file)
        st.write("**Raster Lookup table**")
        
        df['count']=np.nan
        blnRasterLookup=True
        for k in range(df.shape[0]):
            for obj in lc_list:
                if (obj.idl==int(df.iat[k,0])):
                    obj.desc=df.iat[k,1]
                    obj.wt=float(df.iat[k,2])
                    df.iat[k,3]=obj.nlc
        st.write(df)
    except:
        st.error("Faliure loading landcover lookup")

if st.button('Calculate Bank Modification Index'):
    lcn=0.
    if(len(lc_list)==0) or blnRasterLookup==False:
        st.error("Inputs missing. Cannot proceed")
        st.stop()
    for obj in lc_list:
        lcn=lcn+(obj.wt*obj.nlc)
    lcn=(lcn/tot_cnt)
    st.success("**Indicator Score:**")
    st.metric("LCN", round(lcn,2), "")
