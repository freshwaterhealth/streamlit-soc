# -*- coding: utf-8 -*-
"""
Created on Nov 11 10:04:15 2022

@author: kshaad
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

wtDict= {
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
                "Weight":[]
                },
        "GS1":{
                "n":5,
                "title":"Enabling Environment",
                "Indicator":["Water Resource Management","Rights to Resource Use","Incentives and Regulations","Financial Capacity","Technical Capacity"],
                "con":0.0,
                "Weight":[]
                },
        "GS2":{
                "n":2,
                "title":"Stakeholder Engagement",
                "Indicator":["Information Access","Engagement in Decision-Making"],
                "con":0.0,
                "Weight":[]
                },
        "GS3":{
                "n":2,
                "title":"Vision and Adaptive Governance",
                "Indicator":["Strategic Planning","Monitoring Mechanisms"],
                "con":0.0,
                "Weight":[]
                },
        "GS4":{
                "n":3,
                "title":"Effectiveness",
                "Indicator":["Enforcement & Compliance","Distribution of Benefits","Water-Related Conflict"],
                "con":0.0,
                "Weight":[]
                },
        }
weightFinal={
        "indicators":[],
        "weights":[]
        }
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

st.set_page_config(layout="wide", page_title="FHI: Weight Survey Results")
st.title("FHI: Weight Survey Results")
st.sidebar.title("Inputs")
uploaded_file = st.sidebar.file_uploader("Upload CSV File",type=['csv'])
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
    for x in wtDict:
        betaD=round(float(dfBetaDiv.iloc[i]),3)
        DalphaMin=round(fnDalphaMin(float(wtDict[x]["n"]),10.0),3)
        DgammaMax=round(fnDgammaMax(float(wtDict[x]["n"]),10.0, float(k)),3)
        c=round(con(betaD,DalphaMin,DgammaMax),3)
        wtDict[x]["con"]=c*100
        
        for j in range(wtDict[x]["n"]):
            wt=dfweight.iloc[i+j]
            wtDict[x]["Weight"].append(round(wt,4))
        i=i+wtDict[x]["n"]
        #st.write(wtDict[x]["Weight"])
        #st.write(wtDict[x]["con"])
        
        if cnt==1:
            with col1:
                dt=pd.DataFrame.from_dict(wtDict[x]) 
                t= str(wtDict[x]["title"]) +" [Consensus: "+str(round(wtDict[x]["con"],2))+"%]"
                fig = px.pie(dt, values='Weight', names='Indicator', title=t,hole=.3)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        if cnt==2:
            with col2:
                dt=pd.DataFrame.from_dict(wtDict[x]) 
                t= str(wtDict[x]["title"]) +" [Consensus: "+str(round(wtDict[x]["con"],2))+"%]"
                fig = px.pie(dt, values='Weight', names='Indicator', title=t,hole=.3)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        if cnt==3:
            with col3:
                dt=pd.DataFrame.from_dict(wtDict[x]) 
                t= str(wtDict[x]["title"]) +" [Consensus: "+str(round(wtDict[x]["con"],2))+"%]"
                fig = px.pie(dt, values='Weight', names='Indicator', title=t,hole=.3)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        cnt=cnt+1
        if cnt==4:
            cnt=1

    
    @st.cache
    def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')
    
    for x in wtDict:
        weightFinal["indicators"]=weightFinal["indicators"]+wtDict[x]["Indicators"]
        weightFinal["weights"]=weightFinal["weights"]+wtDict[x]["Weight"]
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
