import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from operator import pow

def adjust(x):
    if x>6.0:
        return x/10.0
    elif x>0.0:
        return x
    else:
        return np.nan


st.set_page_config(
    layout="wide", 
    page_title="FHI GS",
    menu_items={
        'Get Help':'https://www.freshwaterhealthindex.org/',
        'About':'https://www.freshwaterhealthindex.org/',
        'Report a bug':'https://www.freshwaterhealthindex.org/'
})

st.title("FHI: G&S Survey Results")

if st.session_state.raw_data == True:
    st.sidebar.title("Inputs")
    try:
        c1=int(st.session_state.code)
        df=st.session_state.df_gs.loc[st.session_state.df_gs.Code == c1]      
    except:
        st.error("Faliure loading results")
        st.stop()
    
    sectorList=df.Sector.unique()
    countryList=df.Country.unique()  
    
    if st.sidebar.checkbox('Subset by country', key="GSC"):
        op1=st.sidebar.selectbox("Select country", countryList, index=0, key="GS_country")
        df=df.loc[df.Country == op1]


    if st.sidebar.checkbox('Subset by sector', key="GCS"):
        op2=st.sidebar.selectbox("Select sector", sectorList, index=0, key="GS_sector")
        df=df.loc[df.Sector == op2]
    
    df.drop(['PID', 'Code', 'Country','Sector','com1','com2','com3','com4','com5','com6','com7','com8','com9','com10','com11','com12'], axis=1, inplace=True)
    df=df.astype(float)
    k=len(df.index)
    st.metric("Number of responses",k)

    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            v=df.iloc[i,j]
            df.iloc[i,j]=adjust(v)

    dfval=df.mean()
    
    dfTemp=st.session_state.fhi_df
    i1=25.0*(((dfval.q11 + dfval.q12 + dfval.q13 + dfval.q14 + dfval.q15)/5)-1)    
    dfTemp.at[dfTemp.index[30],'score']=round(i1,2)
    i2=25.0*(((dfval.q21 + dfval.q22 + dfval.q23 + dfval.q24 + dfval.q25  + dfval.q26)/6)-1)    
    dfTemp.at[dfTemp.index[31],'score']=round(i2,2)
    i3=25.0*(((dfval.q31 + dfval.q32 + dfval.q33 + dfval.q34 + dfval.q35)/5)-1)    
    dfTemp.at[dfTemp.index[32],'score']=round(i3,2)
    i4=25.0*(((dfval.q41 + dfval.q42 + dfval.q43)/3)-1)    
    i5=25.0*(((dfval.q51 + dfval.q52 + dfval.q53 + dfval.q54 + dfval.q55)/5)-1)    
    dfTemp.at[dfTemp.index[33],'score']=round(i5,2)    
    dfTemp.at[dfTemp.index[34],'score']=round(i4,2)

    i6=25.0*(((dfval.q61 + dfval.q62 + dfval.q63 + dfval.q64)/4)-1)    
    dfTemp.at[dfTemp.index[35],'score']=round(i6,2)
    i7=25.0*(((dfval.q71 + dfval.q72 + dfval.q73 + dfval.q74)/4)-1)    
    dfTemp.at[dfTemp.index[36],'score']=round(i7,2)

    i8=25.0*(((dfval.q81 + dfval.q82 + dfval.q83 + dfval.q84 + dfval.q85)/5)-1)    
    dfTemp.at[dfTemp.index[37],'score']=round(i8,2)
    i9=25.0*(((dfval.q91 + dfval.q92 + dfval.q93 + dfval.q94 + dfval.q95)/5)-1)    
    dfTemp.at[dfTemp.index[38],'score']=round(i9,2)

    i10=25.0*(((dfval.q101 + dfval.q102 + dfval.q103 + dfval.q104 + dfval.q105)/5)-1)    
    dfTemp.at[dfTemp.index[39],'score']=round(i10,2)
    i11=25.0*(((dfval.q111 + dfval.q112 + dfval.q113 + dfval.q114)/4)-1)    
    i12=25.0*(((dfval.q121 + dfval.q122 + dfval.q123)/3)-1)    
    dfTemp.at[dfTemp.index[40],'score']=round(i12,2)    
    dfTemp.at[dfTemp.index[41],'score']=round(i11,2)

    st.session_state.fhi_df=dfTemp
    st.session_state.fhi_gs=True

if st.session_state.fhi_gs:
    #Display scores and ask for description
    x=30
    st.subheader(st.session_state.fhi_df.at[st.session_state.fhi_df.index[10],'name'])
    for i in range(12):
        if(i==5):
            st.subheader(st.session_state.fhi_df.at[st.session_state.fhi_df.index[11],'name'])
        if(i==7):
            st.subheader(st.session_state.fhi_df.at[st.session_state.fhi_df.index[12],'name'])
        if(i==9):
            st.subheader(st.session_state.fhi_df.at[st.session_state.fhi_df.index[13],'name'])
        col1, col2 = st.columns([1,3])
        col1.metric(label=st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'name'],
                    value= st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'score'])
        txt=st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'description']
        st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'description']=col2.text_area(
            label="Add or update description", 
            value=txt, 
            key=st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'id'])





    