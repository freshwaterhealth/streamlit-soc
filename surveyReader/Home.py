import streamlit as st
import xml.etree.ElementTree as ET
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import urllib.request as url
import requests

st.set_page_config(
    layout="wide", 
    page_title="FHI Survey",
    menu_items={
        'Get Help':'https://www.freshwaterhealthindex.org/',
        'About':'https://www.freshwaterhealthindex.org/',
        'Report a bug':'https://www.freshwaterhealthindex.org/'
})

#Map of XML entry to session state fhi_conc, 1->Ecosystem Services, etc
conMapRev=[1,7,8,9,2,10,11,12,13]
url_blank=st.secrets['data']['url_blank']

#geomteric mean
def gm_df(x,y):
    a=[]
    b=[]
    for i in range(y):
        a.append(float(st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'score']))
        b.append(float(st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'weight']))
    c=list(map(pow,a,b))   
    return round(np.prod(c),2)

# Initialization
def xml2df(s): 
    tree = ET.parse(s)
    root = tree.getroot()
    indNames=[]
    indID=[]
    indScores=[]
    indWeights=[]
    indDescp=[]
    indCon=[]
    for ind in root:
        indID.append(ind.attrib["id"])    
        for inm in ind.findall('name'):
            indNames.append(inm.text)
        for isc in ind.findall('score'):
            indScores.append(isc.text)
        for iwt in ind.findall('weight'):
            indWeights.append(iwt.text)
        for ide in ind.findall('description'):
            indDescp.append(ide.text)
    for x in conMapRev:
        indCon.append(root[x].attrib["con"])   

    # initialize data of lists.
    data = {'name': indNames,
            'id': indID,
            'score':indScores,
            'weight':indWeights,
            'description':indDescp
            }
    # Create DataFrame
    df = pd.DataFrame(data)
    return root,df,indCon

def fetch_html_from_url(url: str) -> str:
    response = requests.get(url)
    return response.text

source = url.urlopen(url_blank)
root,df,indCon=xml2df(source)
#Session State Variables
if 'fhi_df' not in st.session_state:
    st.session_state.fhi_df = df
if 'fhi_conc' not in st.session_state:
    st.session_state.fhi_conc = indCon
if 'fhi_wt' not in st.session_state:
    st.session_state.fhi_wt = False
if 'fhi_gs' not in st.session_state:
    st.session_state.fhi_gs = False
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = False
if 'code' not in st.session_state:
    st.session_state.code = 123456

#Main display
st.title("Freshwater Health Index Webtool")
col1, col2 = st.columns(2)
col2.markdown("![Alt Text](https://uploads-ssl.webflow.com/5d10fe385d27da1387c00f51/5f976713da23327149c6e327_ezgif.com-gif-maker%20(1).gif)")
col1.subheader("Governance & Stakeholder Analysis")
col1.markdown("Governance & Stakeholders is defined as \"the structures and processes by which people in societies make decisions and share power, creating the conditions for ordered rule and collective action, or institutions of social coordination\" (Schultz et al. 2015).")
#col1.markdown("This definition encompasses multiple tiers of government, their formal rules and informal norms (e.g., community-established guidelines) and market mechanisms. It also encompasses a range of stakeholders comprising decision makers and the human beneficiary population (from individual citizens and community groups to municipalities, corporations and international organizations), as well as other stakeholders such as donor agencies, who may not directly benefit from the ecosystem services in a particular location, but nonetheless have an interest in, and influence over, decisions that affect a particular basin.")
col1.markdown("For the Governance and Stakeholders component of the FHI, we have developed a survey instrument to measure this aspect by using four major indicators: Enabling Environment, Stakeholder Engagement, Vision and Adaptive Governance, and Effectiveness. Each of these indicators is composed by two up to five sub-indicators ([definitions](https://manual.freshwaterhealthindex.org/Governance_and_Stakeholders/Definitions.html)). This webtools helps a user analyse the outputs from the survey and add descriptions to each indicator score.")
st.markdown("---")
st.subheader("Instructions")
st.markdown("1. To proceed with a new analysis, obtain the results of the weights and governance survey results for your basin by fectching the results from the server and then entering your session code")
st.markdown("2. Alternatively, to visualize results from pre-existing analysis, upload the FHI Results XML file instead.")
st.markdown("---")

if st.sidebar.button('Reset to blank'):
    source = url.urlopen(url_blank)
    root,df,indCon=xml2df(source)
    st.session_state.fhi_df = df
    st.session_state.fhi_conc = indCon
    st.session_state.fhi_wt = False
    st.session_state.fhi_gs = False
    st.session_state.raw_data = False

st.sidebar.title("Option 1: Pull from XML")
uploaded_file = st.sidebar.file_uploader("Upload XML File",type=['xml'])
if uploaded_file is not None:
    try:
        root,df,indCon=xml2df(uploaded_file)
        df['weight']=df['weight'].astype(float)
        df['score']=df['score'].astype(float)
        st.session_state.fhi_df = df
        st.session_state.fhi_conc = list(np.float_(indCon))
        #Setting both true for now. later will need a better check
        st.session_state.fhi_wt = True
        st.session_state.fhi_gs = True
        st.session_state.raw_data = False
    except:
        st.error("Faliure loading results")
        st.stop()

st.sidebar.title("Option 2: Pull from server")
if st.sidebar.button('Refresh/Fetch from server'):
    url_data=st.secrets['data']['url']
    raw_html = fetch_html_from_url(url_data)
    dataframes = pd.read_html(raw_html)
    if not len(dataframes):
        st.warning("No Tables / Dataframes found 😿")
        st.stop()
    else:
        st.session_state.raw_data = True
        st.session_state.df_wt = dataframes[0]
        st.session_state.df_gs = dataframes[1]
if st.session_state.raw_data == True:
    codeList=st.session_state.df_wt.Code.unique()
    st.session_state.code=st.sidebar.text_input("Set session code",st.session_state.code)

if st.session_state.fhi_gs and st.session_state.fhi_wt:
    df=st.session_state.fhi_df
    df.at[df.index[10],'score']= gm_df(30,5)  
    df.at[df.index[11],'score']= gm_df(35,2)
    df.at[df.index[12],'score']= gm_df(37,2)
    df.at[df.index[13],'score']= gm_df(39,3)

    df.at[df.index[2],'score']= gm_df(10,4)

    #Plots df    
    df31=df.iloc[2:3,:]
    df32=df.iloc[10:14,:]
    df33=df.iloc[30:,:]
    df3=pd.concat([df31,df32,df33])
    df3=df3.reset_index(drop=True)
    
    pt=["",df3.at[df3.index[0],'name'],df3.at[df3.index[0],'name'],df3.at[df3.index[0],'name'],df3.at[df3.index[0],'name'],
    df3.at[df3.index[1],'name'],df3.at[df3.index[1],'name'],df3.at[df3.index[1],'name'],df3.at[df3.index[1],'name'],df3.at[df3.index[1],'name'],
    df3.at[df3.index[2],'name'],df3.at[df3.index[2],'name'],
    df3.at[df3.index[3],'name'],df3.at[df3.index[3],'name'],
    df3.at[df3.index[4],'name'],df3.at[df3.index[4],'name'],df3.at[df3.index[4],'name']
    ]
    ptw=[1,1,1,1,1,
    df3.at[df3.index[1],'weight'],df3.at[df3.index[1],'weight'],df3.at[df3.index[1],'weight'],df3.at[df3.index[1],'weight'],df3.at[df3.index[1],'weight'],
    df3.at[df3.index[2],'weight'],df3.at[df3.index[2],'weight'],
    df3.at[df3.index[3],'weight'],df3.at[df3.index[3],'weight'],
    df3.at[df3.index[4],'weight'],df3.at[df3.index[4],'weight'],df3.at[df3.index[4],'weight']
    ]
    s1 = pd.Series(pt, name="parent")
    s2 = pd.Series(ptw, name="parentWeight")
    df3 = pd.concat([df3, s1, s2], axis=1)
    df3.at[df3.index[0],'weight']=1.0
    df3['weight']=df3['weight'].astype(float)
    df3['parentWeight']=df3['parentWeight'].astype(float)
    df3['nweight']=df3.weight*df3['parentWeight']*100
    df3['nweight']=df3['nweight'].round(2) 
    
    tsum=np.sum(df3['nweight'][1:5])
    if tsum!=100:
        #df3['nweight'][1]=df3['nweight'][1]+(100.0-tsum)
        df3.loc[1,"nweight"]=df3['nweight'][1]+(100.0-tsum)
    tsum=np.sum(df3['nweight'][5:17])    
    if tsum!=100:
        #df3['nweight'][5]=df3['nweight'][5]+(100.0-tsum)
        df3.loc[5,"nweight"]=df3['nweight'][5]+(100.0-tsum)
    df3['nweight']=df3['nweight'].astype(str)      

    col1, col2 = st.columns(2)
    cs = col2.selectbox(
     'Select color palette for scores:',
     ('blackbody', 'jet', 'rainbow','picnic','portland','spectral', 'curl','edge','hsv'))
    rcs= col2.checkbox('Reverse color palette')
    
    fig = go.Figure()

    fig.add_trace(go.Sunburst(
            labels = df3.name,
            ids = df3.name,
            values = df3.nweight,            
            parents = df3.parent,
            marker=dict(
                colors=df3.score,
                colorscale=cs,
                reversescale=rcs,
                cmin=0, cmax=100,
                colorbar=dict(thickness=20)), 
            hovertemplate='<b>%{label} </b> <br> Score: %{color} </b> <br> Proportional Weight: %{value} </b>',
            insidetextorientation='radial',
            branchvalues="total",
    ))
    
    fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))
    # Plot! 
    
    col1.subheader("Overall Governance & Stakeholder score")
    col1.metric(label="Score",
                value= st.session_state.fhi_df.at[st.session_state.fhi_df.index[2],'score'])
    txt=st.session_state.fhi_df.at[st.session_state.fhi_df.index[2],'description']
    st.session_state.fhi_df.at[st.session_state.fhi_df.index[2],'description']=col1.text_area(
        label="Add or update description", 
        value=txt, 
        key=st.session_state.fhi_df.at[st.session_state.fhi_df.index[2],'id'])
    col2.plotly_chart(fig, use_container_width=False)

    
    #Add description    
    x=10
    for i in range(4):
        st.subheader(st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'name'])
        col1, col2 = st.columns([1,3])
        col1.metric(label="Score",
                    value= st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'score'])
        txt=st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'description']
        st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'description']=col2.text_area(
            label="Add or update description", 
            value=txt, 
            key=st.session_state.fhi_df.at[st.session_state.fhi_df.index[x+i],'id'])
    
    df3=df3.drop(df3.index[0])
    df3['score']=df3['score'].astype(float)
    st.subheader("Results Summary")
    cs = st.selectbox(
     'Select color palette for weight:',
     ('blackbody', 'jet', 'rainbow','picnic','portland','spectral', 'curl','edge','hsv'))
    fig2 = px.bar(df3, x='name', y='score', color='weight', height=450, color_continuous_scale=cs)
    st.plotly_chart(fig2, use_container_width=True)
  

#update root from df
if st.session_state.fhi_gs or st.session_state.fhi_wt:
    ii=0
    df=st.session_state.fhi_df
    #st.write(df)
    for ind in root:
        if(df.at[df.index[ii],'score'])!=None:
            ind[1].text = str(df.at[df.index[ii],'score'])
        if(df.at[df.index[ii],'weight'])!=None:
            ind[2].text = str(df.at[df.index[ii],'weight'])
        if(df.at[df.index[ii],'description'])!=None:
            ind[3].text = df.at[df.index[ii],'description']
        ii=ii+1
    for x in range(9):
        root[conMapRev[x]].attrib["con"]=str(st.session_state.fhi_conc[x])
    upXML=ET.tostring(root)
    st.download_button(
                label="Download FHI Results XML file",
                data=upXML,
                file_name='fhi.xml',
                mime='text/xml',
                )