# -*- coding: utf-8 -*-
"""
Created on Nov 11 10:04:15 2022

@author: kshaad
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from operator import pow

indDict= {
        "ES":{
                "n":3,
                "title": "Ecosystem Services",
                "Indicator":["Provisioning","Regulation","Cultural"],
                "con":0.0,
                "Weight":[]
                },
        "ES1":{
                "n":2,
                "title":"Provisioning",
                "Indicator":["Water Supply Reliability","Biomass"],
                "con":0.0,
                "Weight":[]
                },
        "ES2":{
                "n":4,
                "title":"Regulation",
                "Indicator":["Sediment Regulation","Water Quality Regulation","Flood Regulation","Disease Regulation"],
                "con":0.0,
                "Weight":[]
                },
        "ES3":{
                "n":2,
                "title":"Cultural",
                "Indicator":["Conservation Areas","Recreation"],
                "con":0.0,
                "Weight":[]
                },
        "GS":{
                "n":4,
                "title":"Governance & Stakeholders",
                "Indicator":["Enabling Environment","Stakeholder Engagement","Vision and Adaptive Governance","Effectiveness"],
                "con":0.0,
                "Weight":[],"Value":[]

                },
        "GS1":{
                "n":5,
                "title":"Enabling Environment",
                "Indicator":["Water Resource Management","Rights to Resource Use","Incentives and Regulations","Financial Capacity","Technical Capacity"],
                "con":0.0,
                "Weight":[],"Value":[]
                },
        "GS2":{
                "n":2,
                "title":"Stakeholder Engagement",
                "Indicator":["Information Access","Engagement in Decision-Making"],
                "con":0.0,
                "Weight":[],"Value":[]
                },
        "GS3":{
                "n":2,
                "title":"Vision and Adaptive Governance",
                "Indicator":["Strategic Planning","Monitoring Mechanisms"],
                "con":0.0,
                "Weight":[],"Value":[]
                },
        "GS4":{
                "n":3,
                "title":"Effectiveness",
                "Indicator":["Enforcement & Compliance","Distribution of Benefits","Water-Related Conflict"],
                "con":0.0,
                "Weight":[],"Value":[]
                },
        }
weightFinal={
        "indicators":[],
        "weights":[]
        }

weightSet=False
valSet=False

def dataFrameWeightClustering(df1):
    df1.ES1=df1.ES1+df1.ES2+df1.ES3
    df1.ES2=df1.ES1
    df1.ES3=df1.ES1
    df1.ES11=df1.ES11+df1.ES12
    df1.ES12=df1.ES11
    df1.ES21=df1.ES21+df1.ES22+df1.ES23+df1.ES24
    df1.ES22=df1.ES21
    df1.ES23=df1.ES21
    df1.ES24=df1.ES21
    df1.ES31=df1.ES31+df1.ES32
    df1.ES32=df1.ES31
    df1.GS1=df1.GS1+df1.GS2+df1.GS3+df1.GS4
    df1.GS2=df1.GS1
    df1.GS3=df1.GS1
    df1.GS4=df1.GS1
    df1.GS11=df1.GS11+df1.GS12+df1.GS13+df1.GS14+df1.GS15
    df1.GS12=df1.GS11
    df1.GS13=df1.GS11
    df1.GS14=df1.GS11
    df1.GS15=df1.GS11
    df1.GS21=df1.GS21+df1.GS22
    df1.GS22=df1.GS21
    df1.GS31=df1.GS31+df1.GS32
    df1.GS32=df1.GS31
    df1.GS41=df1.GS41+df1.GS42+df1.GS43
    df1.GS42=df1.GS41
    df1.GS43=df1.GS41

def adjust(x):
    if x>6.0:
        return x/10.0
    elif x>0.0:
        return x
    else:
        return np.nan
def gm(a,b):
    c=list(map(pow,a,b))   
    return np.prod(c)

st.set_page_config(layout="wide", page_title="FHI: Survey Results")
st.title("FHI: Survey Results")
st.sidebar.title("Inputs")
uploaded_file = st.sidebar.file_uploader("Upload WT CSV File",type=['csv'])
if uploaded_file is not None:
    try:
        df=pd.read_csv(uploaded_file)
        
    except:
        st.error("Faliure loading results")
    
    sectorList=df.Sector.unique()
    countryList=df.Country.unique()  
    
    if st.sidebar.checkbox('Subset by country'):
        op1=st.sidebar.selectbox("Select country", countryList, index=0)
        df=df.loc[df.Country == op1]


    if st.sidebar.checkbox('Subset by sector'):
        op2=st.sidebar.selectbox("Select sector", sectorList, index=0)
        df=df.loc[df.Sector == op2]
    
    df.drop(['PID', 'Code', 'Country','Sector'], axis=1, inplace=True)
    df=df.astype(float)
    k=len(df.index)
    #st.write(df)
    st.metric("Number of responses",k)
    dfsum=df.copy()
    dataFrameWeightClustering(dfsum)    
    dfweight1=df.div(dfsum)
    
#    dfW2=dfweight1.T
#    st.write(dfW2)
#    fig = px.box(dfweight1)
#    st.plotly_chart(fig, use_container_width=True)
    
    #Weights!
    dfweight=dfweight1.mean()
    #st.write(dfweight)
    
    def fln(x):
        return -1*np.log(x)*x
    
    def fln2(x):
        return np.exp(x)
    
    dfalpha=dfweight1.copy()
    dfgamma=dfweight.copy()
    
    dfalpha=dfalpha.apply(fln)
    dataFrameWeightClustering(dfalpha)

    dfalphaD=dfalpha.mean()
    dfgamma=dfgamma.apply(fln)
    dataFrameWeightClustering(dfgamma)
    dfBetaDiv=dfgamma-dfalphaD
    dfBetaDiv=dfBetaDiv.apply(fln2)
    #st.write(dfBetaDiv)
    
    def fnDalphaMin(n,m):
        x1=1/(n+m-1.0)
        x2=m/(n+m-1.0)
        x3=-1*x2*np.log(x2)        
        x5=(n-1)*x1*np.log(x1)
        x6=x3-x5
        x=np.exp(x6)
        return x
    
    def fnDgammaMax(n,m,k):
        x1=1/(n+m-1.0)
        x2=(n-k)*(-1*x1*np.log(x1))
        x3=k+m-1.0
        x4=x3*x1*np.log(x3*x1/k)
        x6=x2-x4
        x=np.exp(x6)
        return x
    
    def con(a,b,c):
        x=b/c 
        x1= 1.0-(b/c)
        x2=1/a
        
        if x1<1e-16:
             return 1
        return ((x2-x)/(x1))

    
    i=0
    cnt=1
    container = st.container()
    col1, col2, col3 = st.columns(3)
    for x in indDict:
        betaD=round(float(dfBetaDiv.iloc[i]),3)
        DalphaMin=round(fnDalphaMin(float(indDict[x]["n"]),10.0),3)
        DgammaMax=round(fnDgammaMax(float(indDict[x]["n"]),10.0, float(k)),3)
        c=round(con(betaD,DalphaMin,DgammaMax),3)
        indDict[x]["con"]=c*100
        
        for j in range(indDict[x]["n"]):
            wt=dfweight.iloc[i+j]
            indDict[x]["Weight"].append(round(wt,4))
        i=i+indDict[x]["n"]
        #st.write(indDict[x]["Weight"])
        #st.write(indDict[x]["con"])

    weightSet=True     
    @st.cache
    def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')
    
    for x in indDict:
        weightFinal["indicators"]=weightFinal["indicators"]+indDict[x]["Indicator"]
        weightFinal["weights"]=weightFinal["weights"]+indDict[x]["Weight"]
    dfW=pd.DataFrame.from_dict(weightFinal)
    csv = convert_df(dfW)

    fig2 = px.bar(dfW, x='indicators', y='weights', color='weights', height=450, title="Weights Summary")
    container.plotly_chart(fig2, use_container_width=True)
    st.download_button(
            label="Download weights as CSV",
            data=csv,
            file_name='weights.csv',
            mime='text/csv',
            )

uploaded_file2 = st.sidebar.file_uploader("Upload GS CSV File",type=['csv'])
if uploaded_file2 is not None:
    try:
        df=pd.read_csv(uploaded_file2)
        
    except:
        st.error("Faliure loading results")
    
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

    #st.write(df)
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            v=df.iloc[i,j]
            df.iloc[i,j]=adjust(v)
    #st.write(df)

    dfval=df.mean()
    #st.write(dfval)
    
    i1=25.0*(((dfval.q11 + dfval.q12 + dfval.q13 + dfval.q14 + dfval.q15)/5)-1)
    indDict["GS1"]["Value"].append(round(i1,2))
    i2=25.0*(((dfval.q21 + dfval.q22 + dfval.q23 + dfval.q24 + dfval.q25  + dfval.q26)/6)-1)
    indDict["GS1"]["Value"].append(round(i2,2))
    i3=25.0*(((dfval.q31 + dfval.q32 + dfval.q33 + dfval.q34 + dfval.q35)/5)-1)
    indDict["GS1"]["Value"].append(round(i3,2))
    i4=25.0*(((dfval.q41 + dfval.q42 + dfval.q43)/3)-1)
    
    i5=25.0*(((dfval.q51 + dfval.q52 + dfval.q53 + dfval.q54 + dfval.q55)/5)-1)
    indDict["GS1"]["Value"].append(round(i5,2))
    indDict["GS1"]["Value"].append(round(i4,2))
    i6=25.0*(((dfval.q61 + dfval.q62 + dfval.q63 + dfval.q64)/4)-1)
    indDict["GS2"]["Value"].append(round(i6,2))
    i7=25.0*(((dfval.q71 + dfval.q72 + dfval.q73 + dfval.q74)/4)-1)
    indDict["GS2"]["Value"].append(round(i7,2))
    i8=25.0*(((dfval.q81 + dfval.q82 + dfval.q83 + dfval.q84 + dfval.q85)/5)-1)
    indDict["GS4"]["Value"].append(round(i8,2))
    i9=25.0*(((dfval.q91 + dfval.q92 + dfval.q93 + dfval.q94 + dfval.q95)/5)-1)
    indDict["GS4"]["Value"].append(round(i9,2))
    i10=25.0*(((dfval.q101 + dfval.q102 + dfval.q103 + dfval.q104 + dfval.q105)/5)-1)
    indDict["GS4"]["Value"].append(round(i10,2))
    i11=25.0*(((dfval.q111 + dfval.q112 + dfval.q113 + dfval.q114)/4)-1)    
    i12=25.0*(((dfval.q121 + dfval.q122 + dfval.q123)/3)-1)
    indDict["GS3"]["Value"].append(round(i12,2))
    indDict["GS3"]["Value"].append(round(i11,2))

    valSet=True

if valSet and weightSet:
    ig1= gm(indDict["GS1"]["Value"],indDict["GS1"]["Weight"])    
    indDict["GS"]["Value"].append(round(ig1,2))
    ig2= gm(indDict["GS2"]["Value"],indDict["GS2"]["Weight"])
    indDict["GS"]["Value"].append(round(ig2,2))
    ig3= gm(indDict["GS3"]["Value"],indDict["GS3"]["Weight"])
    indDict["GS"]["Value"].append(round(ig3,2))
    ig4= gm(indDict["GS4"]["Value"],indDict["GS4"]["Weight"])
    indDict["GS"]["Value"].append(round(ig4,2))

    ig= gm(indDict["GS"]["Value"],indDict["GS"]["Weight"])
    st.metric("G&S score",ig)

st.write(indDict)
