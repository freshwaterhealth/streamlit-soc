# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 09:11:20 2022

@author: kshaad
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import urllib.request

def DvNF(AAPFD):                
    if 0.0 <= AAPFD and AAPFD < 0.3:
        return 100 - 100 * AAPFD
    elif   0.3 <= AAPFD and AAPFD < 0.5:
        return 85 - 50 * AAPFD
    elif   0.5 <= AAPFD and AAPFD < 2.0: 
        return 80 - 20 * AAPFD
    elif   2.0 <= AAPFD and AAPFD < 5.0: 
        return 50 - 10 * AAPFD
    else:
        return 0

@st.cache
def dispImage(url):
    urllib.request.urlretrieve(url,"lbl.png")
    image=Image.open("lbl.png")
    return image

st.title("FHI: Deviation from Natural Flow")
url='https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Aspect_ratio_-_16x9.svg/1200px-Aspect_ratio_-_16x9.svg.png'  
img=dispImage(url)
col1, col2=st.columns([2, 5])
with col1:
    st.image(img)
with col2:
    st.markdown("""
                Deviation from natural flow regime measures the degree to which current flow conditions have shifted from historic natural flows.
                
                Access details on indicator calculation [here](https://www.freshwaterhealthindex.org/tool/Ecosystem_Viltality/Water_Quantity_(WQT)/Deviation_from_Natural_Flow_Regime(DvNF).html)
                """)

with st.expander("Input requirements", expanded=False):
    st.markdown("""
                **Provide input data in following format.** [See template here](https://github.com/freshwaterhealth/fhiScripts/blob/main/01SampleDatasets/02_Ecosystem%20Vitality/DvNF%20Mock%20Data.xlsx)
                    
                    1. Input is accepted in excel spreadsheet (XLSX) format.
                    2. Each tab in the spreadsheet is named after the discharge gauge or location.
                    3. Each tab has a table with header of form: |Date|Regulated|Unregulated| 
                    4. The first column in each tab should be date of discharge (or level). 
                    5. If mutliple readings are availble per month, mean value will be used.
        """)
st.sidebar.title("Inputs")
st.sidebar.subheader("Step 1: Input discharge or level time series")
uploaded_file = st.sidebar.file_uploader("Upload file",type=['xlsx'])

st.sidebar.subheader("Step 2: Set aggregation method")
opt = st.sidebar.radio(
     "Aggregate scores from multiple gauges using:",
     ('Simple mean', 'Mean weighted by annual average*'), index=1)
st.sidebar.write("*recommended when input is dicharge data")
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, sheet_name = None, index_col=0)
    except:
        st.error("Read error. Data not in format expected")
        st.stop()

if st.button('Calculate DvNF'):
    try:
        n_gauge=list(df)
        st.write("**Total number of gauges:**",len(n_gauge))
        dvnfList=np.empty(len(n_gauge), dtype=float)
        dischargeList=np.empty(len(n_gauge), dtype=float)
        fig = make_subplots(rows=len(n_gauge), cols=1, shared_xaxes=True,
                            vertical_spacing=0.03)
        gauge_number=0
        
        for i in n_gauge:
        
          df[i].index = pd.to_datetime(df[i].index)
          df_m=pd.DataFrame(df[i].resample('M').mean())
    
          df_m['month']=df_m.index.month
          monthly_mean=df_m.groupby('month').mean()
             
          
          m=df_m.iloc[:,0:1].values
          n=df_m.iloc[:,1:2].values
    
          dischargeList[gauge_number]=n.mean()
        
          sp=df_m.shape
          sp1=sp[0]/12
          n_1=monthly_mean.iloc[:,1:2].values
          n_m=n_1
        
          j=1
          while j<sp1:
            n_m=np.concatenate((n_m,n_1))
            j=j+1
        
          a=(m-n)/n_m
          a=a*a
        
          ap=pd.DataFrame(a)
          ap.index=df_m.index
          ap['year']=ap.index.year
          ap1=ap.groupby('year').sum()
          ap2=ap1.iloc[:,0:1].values
          ap2=np.sqrt(ap2)
          ap3=ap2.mean()
        
          d=DvNF(ap3)
          dvnfList[gauge_number]=d
          gauge_number=gauge_number+1
          t= "DvNF, Gauge "+ str(i)+": "+str(round(d,2))
          st.write(t)
          t1="Gauge "+ str(i) +" Regulated"
          t2="Gauge "+ str(i) +" Unregulated"
          df_m=df_m.drop('month', axis=1)
          fig.add_trace(
                  go.Scatter(x=df_m.index, y=df_m["Regulated"], name=t1),
                  row=gauge_number,col=1
                  )
          fig.add_trace(
                  go.Scatter(x=df_m.index, y=df_m["Unregulated"], name=t2),
                  row=gauge_number,col=1
                  )
    except:
        st.error("Inputs not in format expected. Please check data against sample dataset")
        st.stop()
    
    if opt=='Simple mean':
        sDVNF=dvnfList.mean()
        st.success("**Net DvNF (mean across gauges):**")
        st.metric("DvNF", round(sDVNF,2), "")
    else:
        wDVNF=dvnfList*dischargeList
        wDVNF=wDVNF.mean()/dischargeList.mean()
        st.success("**Net DvNF (weighted by mean discharge):**")
        st.metric("DvNF", round(wDVNF,2), "")
    fig.update_layout(
            height=600,
            title_text="Time-series plots for all gauges",)
    st.plotly_chart(fig, use_container_width=True)
