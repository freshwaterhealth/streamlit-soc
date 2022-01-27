# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 10:04:15 2022

@author: kshaad
"""

import streamlit as st
from PIL import Image
import urllib.request

@st.cache
def dispImage(url):
    urllib.request.urlretrieve(url,"lbl.png")
    image=Image.open("lbl.png")
    return image

st.title("FHI: Species of Concern Index")
url='https://webtools.freshwaterhealthindex.org/img/bio.jpg'
img=dispImage(url)
col1, col2=st.columns([2, 5])
with col1:
    st.image(img)
with col2:
    st.markdown("""
                Applied on selected freshwater species whose status and population trends are linked to the health of the freshwater ecosystem.
                
                Access details on indicator calculation [here](https://www.freshwaterhealthindex.org/tool/Ecosystem_Viltality/Biodiversity_(BIO)/Species_of_Concern_(SoC).html)
                """)
with st.expander("Input requirements", expanded=False):
    st.markdown("""
                **Process data using IUCN Redlist webtool.** [Access here](https:///www.iucnredlist.org/serach/map)
                    
                    1. Select 'Map' and draw a polygon around area of interest.
                    2. Using 'Search filters', select appropraite habitats (such as 'Wetlands').
                    3. Wait for the list to be extracted (this may be slow) 
                    4. Go to 'Stats' page and enter the numbers below.
    
        """)

wcr=3.0
wen=2.0
wvu=1.0
wnott=0.5
wjen=3.0
wjtr=2.0

ncr=0.0
nen=0.0
nvu=0.0
nnott=0.0
njen=0.0
njtr=0.0

ite_i=1.0
dsc_i=1.0
sc0=1.0
sc_i=1.0
isc_i=100
isc0=100
iYear=2000

blnFirstAssessment=st.checkbox("Species of Concern was calcuated for a previous time period ", value=False) 
if blnFirstAssessment:
    st.info("**Provide details:**")
    col1, col2 = st.columns(2)
    with col1:
        isc0=st.number_input('Indicator value for previous assessment',value=100.0, min_value=0.0, max_value=100.0)
    with col2:
        iYear=st.number_input('Year of previous assessment', value=2000, max_value=2020, min_value=1900,step =1) 
    
st.subheader("Enter data on the number of species:")
blnLocalSpeciesData=st.checkbox("Data from local assessement (Not just IUCN Redlits) available ", value=False)
col1, col2 = st.columns(2)
with col1:
    ncr = st.number_input('IUCN Red list critically endangered species [CR]',value=0.0, min_value=0.0)
with col2:
    nen = st.number_input('IUCN Red list endangered species [EN]',value=0.0, min_value=0.0)

col1, col2 = st.columns(2)
with col1:
    nvu = st.number_input('IUCN Red list vulnerable species [VU]',value=0.0, min_value=0.0)    
with col2:
    if blnLocalSpeciesData:
        njen = st.number_input('Locally endangered',value=0.0, min_value=0.0)
        njtr = st.number_input('Locally threatened',value=0.0, min_value=0.0)
    else:
        st.write("No local assessment data")
nnott = st.number_input('Number of remaining assessed species (excluding data deficient)',value=0.0, min_value=0.0)

if (ncr+nen+nvu+nnott+njen+njtr)>0:
    nu=(wcr*ncr)+(wen*nen)+(wvu*nvu)+(wjen*njen)+(wjtr*njtr)
    dm=nu+(wnott*nnott)
    ite_i=1-(nu/dm)

blnChangeInNumber=st.checkbox("Species data from the year "+str(iYear)+" is available ", value=False)  
if blnChangeInNumber:
    st.info("**Enter Change in species of concern data:**")
    col1, col2 = st.columns(2)
    with col1:
        sc0 = st.number_input('Number of species of concern at previous assessment',value=0.0, min_value=0.0)
    with col2:
        sc_i = st.number_input('Number of species of concern now',value=0.0, min_value=0.0)
    if sc_i>0:
        dsc_i=sc0/sc_i

st.success("**Indicator Score:**")
isc_temp=isc0*ite_i*dsc_i
isc_i=min(isc_temp,100.0)
if blnFirstAssessment:
    pDrp=100*((isc_i-isc0)/isc0)
    st.metric("SOCi", round(isc_i,2), round(pDrp,2))
else:     
    st.metric("SOCi", round(isc_i,2),"")
        
