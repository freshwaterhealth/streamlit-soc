import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    layout="wide", 
    page_title="FHI Weights",
    menu_items={
        'Get Help':'https://www.freshwaterhealthindex.org/',
        'About':'https://www.freshwaterhealthindex.org/',
        'Report a bug':'https://www.freshwaterhealthindex.org/'
})

st.title("FHI: Weight Survey Results")
#Map of rows in session_state DF to dict ind row below, 7 -> Provisoning, etc
rowMap=[7,8,9,22,23,24,25,26,27,28,29,10,11,12,13,30,31,32,33,34,35,36,37,38,39,40,41]
#Map of order of con values to dict below
conMap=[0,2,3,4,1,5,6,7,8]

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
                "Indicator":["Enforcement and Compliance","Distribution of Benefits","Water-Related Conflict"],
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

#Update dict from session_state df & list
tempCon=st.session_state.fhi_conc
dfTemp=st.session_state.fhi_df

i=0
ii=0
if(tempCon[0])!="":
    for x in wtDict:    
        wtDict[x]["con"]=float(tempCon[conMap[ii]])
        nn=wtDict[x]["n"]        
        for j in range(nn):
            wtDict[x]["Weight"].append(dfTemp.at[dfTemp.index[rowMap[i+j]],'weight'])
        i=i+nn
        ii=ii+1


if st.session_state.raw_data == True:
    st.sidebar.title("Inputs")
    try:
        c1=int(st.session_state.code)
        df=st.session_state.df_wt.loc[st.session_state.df_wt.Code == c1]
        for x in wtDict:
            wtDict[x]["Weight"].clear()
            wtDict[x]["con"]=0.0
    except:
        st.error("Faliure loading results")
        st.stop()
    
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
    
    st.metric("Number of responses",k)
    dfsum=df.copy()
    dataFrameWeightClustering(dfsum)    
    dfweight1=df.div(dfsum)
        
    #Weights!
    dfweight=dfweight1.mean()
    
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
    i=0
    ii=0
    for x in wtDict:
        #st.write(wtDict[x]["con"])
        tempCon[conMap[ii]]=float(round(wtDict[x]["con"],2))
        nn=wtDict[x]["n"]        
        for j in range(nn):
            dfTemp.at[dfTemp.index[rowMap[i+j]],'weight']= wtDict[x]["Weight"][j]
        i=i+nn
        ii=ii+1

    st.session_state.fhi_conc=tempCon
    st.session_state.fhi_df=dfTemp
    st.session_state.fhi_wt=True  

if(tempCon[0])!="":   
    cnt=1
    container = st.container()
    col1, col2, col3 = st.columns(3)
    for x in wtDict:  
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

    for x in wtDict:
        weightFinal["indicators"]=weightFinal["indicators"]+wtDict[x]["Indicator"]
        weightFinal["weights"]=weightFinal["weights"]+wtDict[x]["Weight"]
    #st.write(weightFinal["indicators"])
    #st.write(weightFinal["weights"])
    dfW=pd.DataFrame.from_dict(weightFinal)
    fig2 = px.bar(dfW, x='indicators', y='weights', color='weights', height=450, title="Weights Summary")
    container.plotly_chart(fig2, use_container_width=True)


    
