# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 12:06:11 2022

@author: kshaad
"""

import numpy as np
import math
import pandas as pd
import geopandas
import shapely
from shapely import wkt
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import urllib.request
import gc
#from plotly.subplots import make_subplots
@st.cache
def dispImage(url):
    urllib.request.urlretrieve(url,"lbl.png")
    image=Image.open("lbl.png")
    return image

def readRiv(uploadedFile):
    try:
        df = pd.read_excel(uploadedFile)
        df_riv = df.filter(['ID','WKT','LEN'], axis=1)
        return df_riv
    except:
        st.error("Error reading file")
        st.stop()

def readDam(uploadedFile):
    try:
        df = pd.read_excel(uploadedFile)
        df_dam = df.filter(['DamID','x','y','Name','p'], axis=1)
        return df_dam
    except:
        st.error("Error reading file")
        st.stop()

class Reach:
    def __init__(self, idr, length, x_u,y_u,x_d,y_d,l):
        self.idr = idr
        self.lenr = length
        self.x_u=x_u
        self.x_d=x_d
        self.y_u=y_u
        self.y_d=y_d
        self.nodes=l
        self.down=-1
        self.up=[]
        self.xList=[]
        self.yList=[]
        self.ndam=[]
        self.damDist2dwn=[]
        self.did_dwn=0
    
    def swap(self):
        xt=self.x_u
        yt=self.y_u
        self.x_u=self.x_d
        self.y_u=self.y_d
        self.x_d=xt
        self.y_d=yt
        self.nodes.reverse()
    
    #If working correctly, node list will go from upstream to downstream
    def genNodeList(self):
        for p in self.nodes:
           a=p.split()
           x1=float(a[0])
           y1=float(a[1])
           self.xList.append(x1)
           self.yList.append(y1)
    
    def setDam(self,dloc,nodeLoc):
        self.ndam.append(dloc)
        d=0.
        if nodeLoc==len(self.nodes):
            self.damDist2dwn.append(d)
        else:
            for i in range(nodeLoc,len(self.nodes)-1):
                d=d+distPoints(self.xList[i],self.yList[i],self.xList[i+1],self.yList[i+1])
            self.damDist2dwn.append(d)
        #st.write("**Dam:**",self.ndam)
        #st.write("**Reach:**",self.idr)
        #st.write("**Dist:**",self.damDist2dwn)
        
    def sortDams(self):
        if len(self.ndam)>1:
            #Sort dams
            for i in range(len(self.damDist2dwn)):
                minpos=self.damDist2dwn.index(min(self.damDist2dwn[0:len(self.damDist2dwn)-i]))
                self.damDist2dwn.append(self.damDist2dwn.pop(minpos))
                self.ndam.append(self.ndam.pop(minpos))

class Dam:
    noDamFound=0
    def __init__(self,did,x,y,n,p):
        self.did=did
        self.x=x
        self.y=y
        self.name=n
        self.passability=p
        #For sections
        self.len_up=0.
        self.nextDwn=-1
        self.ldam=[]
        
    def setDamList(self,l):
        self.ldam=l

def matchPoints(x1,y1,x2,y2):
    err=0.1
    xR=abs(x1-x2)
    yR=abs(y1-y2)
    if (xR<err) and (yR<err):
        #st.write(str(x1)+","+str(x2)+","+str(y1)+","+str(y2))
        return True
    else:
        return False

def distPoints(x1,y1,x2,y2):
    xR=abs(x1-x2)
    yR=abs(y1-y2)
    dist=math.sqrt(xR*xR+yR*yR)
    return dist
st.title("FHI: Dentritic Connectivity Index")   
gc.enable() 
url='https://webtools.freshwaterhealthindex.org/img/dci.jpg'  
img=dispImage(url)
col1, col2=st.columns([2,5])
with col1:
    st.image(img)
with col2:
    st.markdown("""
                Flow connectivity is important for the movement of aquatic life such as fish and the flow of organic matter, nutrients and sediment. 
                
                Access details on indicator calculation [here](https://www.freshwaterhealthindex.org/tool/Ecosystem_Viltality/Drainage_Basin_Condition_(DBC)/Flow_Connectivity_(FC).html)
                """)
with st.expander("Input requirements", expanded=False):
    st.markdown("""
                **Provide input data in following format.** 
                    
                    1. All data must in same projected coordinate system (such as UTM zones).
                    2. Enter the x and y oordinate of outlet in webtool.
                    3. River network is accepted in WKT format.
                    4. Dam locations must be provided as a table (XLSX file)
                    5. This table must be in format: DamID|x|y|Name|p; where p is "passability" (between 0 to 1)
                    6. Use checkbox below to control details of output and interaction.
                [See River network template here](https://github.com/freshwaterhealth/fhiScripts/blob/main/02VBAtools/EV%20-%20Dendritic%20Connectivity%20Index/Data/3S_River_HydroBasin.xlsx)
        """)
reach_list=[]
dam_list=[]
outlet_reach=-1
rivLen=0.
nRR=0
nDam=0
boolRivLoaded=False
boolDamLoaded=False
controls = st.container()
blnDiagnostic=controls.checkbox("Print diagnostic information on screen", value=False)

st.sidebar.title("Inputs")
st.sidebar.subheader("Step 1: Enter river outlet coordinates")
xx_out = st.sidebar.number_input('Set Outlet X coordinate (in meters)',value=603021.863849466)
yy_out = st.sidebar.number_input('Set Outlet Y coordinate (in meters)', value=1497007.87162709)
#Hard set for now. Change to user input on final version
#xx_out=603021.863849466
#yy_out=1497007.87162709

st.sidebar.subheader("Step 2: Input river network")
uploaded_file = st.sidebar.file_uploader("Upload River Network File",type=['xlsx'])
if uploaded_file is not None:    
    df_riv = readRiv(uploaded_file)  
    #Prepare network part
    try:     
        nRR=df_riv.shape[0] 
        #Read dataset into list of class Reach and locate outlet
        for k in range(nRR):
            l=df_riv.iat[k,1].lstrip("LINESTRING (").rstrip(")").split(",")
            a=l[0].split()
            b=l[-1].split()
            idr=df_riv.iat[k,0]
            lenr=df_riv.iat[k,2]
            reach_list.append(Reach(idr,lenr,float(a[0]),float(a[1]),float(b[0]),float(b[1]),l))
            if (outlet_reach==-1):
                if matchPoints(xx_out,yy_out,float(b[0]),float(b[1])):
                    reach_list[k].down=-999 #Outlet has downstream reach set as -999
                    outlet_reach=k
                if matchPoints(xx_out,yy_out,float(a[0]),float(a[1])):
                    reach_list[k].swap()
                    reach_list[k].down=-999
                    outlet_reach=k
    except:
        st.error("River network not in expected format")
        st.stop()
        
    if (outlet_reach==-1):
        st.write("No match for outlet found!!")
        st.stop()
    else:
        boolRivLoaded=True
    #Recurcive function to find recah upstream
    def findup(i):
        for k in range(nRR):
            if reach_list[k].down==-1:
                if matchPoints(reach_list[i].x_u,reach_list[i].y_u,reach_list[k].x_d,reach_list[k].y_d):
                    reach_list[k].down=i
                    reach_list[i].up.append(k)
                    findup(k)
                if matchPoints(reach_list[i].x_u,reach_list[i].y_u,reach_list[k].x_u,reach_list[k].y_u):
                    reach_list[k].swap()
                    reach_list[k].down=i
                    reach_list[i].up.append(k)
                    findup(k)                
    findup(outlet_reach)
    for obj in reach_list:
        obj.genNodeList()
    
     
    #Dignostics
    if blnDiagnostic:
        st.write("Input River Newtork:")
        st.write(df_riv)
        
        st.write("Total number of river reaches:",nRR)
        st.write("Number of reach(s) unconnected:")
        nCnt=0
        for k in range(nRR):
             if reach_list[k].down==-1:
                 st.write("Reach id:", reach_list[k].idr)
                 nCnt+=1
        st.write(nCnt)
        st.write("Reach identified as outlet:",reach_list[outlet_reach].idr)

st.sidebar.subheader("Step 3: Input obstruction location")
uploaded_file = st.sidebar.file_uploader("Upload obstruction location file",type=['xlsx'])
if uploaded_file is not None:
    if boolRivLoaded:
        df_dam = readDam(uploaded_file)
        
        if blnDiagnostic:
            st.write(df_dam)
        
        nDam=df_dam.shape[0]
        
        #add placeholder Dam at outlet
        dam_list.append(Dam(0,xx_out,yy_out,'Outlet',1.0))    
        boolNoDamAtOutlet=True
        
        def updateNoDam():
            Dam.noDamFound=Dam.noDamFound+1
            
        #Function to locate dam on river network and then push to class Reach
        def locateDam(i):
            d_err=10000
            r_id=-1
            n_id=-1
            k=0
            for k in range(nRR):
                for j in range(len(reach_list[k].nodes)):
                    d= distPoints(dam_list[i].x,dam_list[i].y,reach_list[k].xList[j],reach_list[k].yList[j])
                    if (d<d_err):
                        d_err=d
                        r_id=k
                        n_id=j
    
            if(r_id==-1):
                updateNoDam()
                if blnDiagnostic:
                    st.write("Obstruction not found:",dam_list[i].name)
            else:
                reach_list[r_id].setDam(i,n_id)
                
        for i in range(nDam):
            if matchPoints(xx_out,yy_out,df_dam.iat[i,1],df_dam.iat[i,2]):
                dam_list[0].did=df_dam.iat[i,0]
                dam_list[0].name=df_dam.iat[i,3]
                dam_list[0].passability=float(df_dam.iat[i,4])
                boolNoDamAtOutlet=False
            else:
                dam_list.append(Dam(df_dam.iat[i,0],df_dam.iat[i,1],df_dam.iat[i,2],df_dam.iat[i,3],float(df_dam.iat[i,4])))
                locateDam(i+1)
        locateDam(0)
        
        if boolNoDamAtOutlet:
            nDam=nDam+1
            
        if blnDiagnostic:
            st.write("Total number of obstructions found on network:",nDam - Dam.noDamFound -1)
        
        if(Dam.noDamFound<nDam):
            boolDamLoaded=True
        
        for obj in reach_list:
            obj.sortDams()
            rivLen=rivLen+obj.lenr
         
    else:
        st.error("Please load River network before adding dams")
        st.stop()

##Interaction
blnPass=controls.checkbox("Show interface to change obstruction passability values", value=False)
if blnPass:
    controls.subheader("Edit obstruction passability values")
    opt=controls.radio("Edit collectively or individually?" , ('Apply to all','Slider for all obstructions'))
    if opt == 'Apply to all':
        p=controls.number_input("Value",min_value=0., max_value=1., value=1.0)
        for obj in dam_list:
            if obj.name!='Outlet':
                obj.passability=p 
    else:
        for obj in dam_list:
            obj.passability=controls.slider(obj.name,min_value=0., max_value=1., value=float(obj.passability))

if st.button('Calculate DCI'):
    if boolRivLoaded and boolDamLoaded:
        def damSections(i, did_dwn):
            reach_list[i].did_dwn=did_dwn
            didT=did_dwn
            #Case reach has no dam        
            if (len(reach_list[i].ndam)==0):
               dam_list[did_dwn].len_up=dam_list[did_dwn].len_up+reach_list[i].lenr 
            #Case reach has 1 dam
            if (len(reach_list[i].ndam)==1):
                dam_list[did_dwn].len_up=dam_list[did_dwn].len_up+reach_list[i].damDist2dwn[0]
                didT2=didT
                didT=reach_list[i].ndam[0]
                dam_list[didT].len_up=dam_list[didT].len_up+reach_list[i].lenr-reach_list[i].damDist2dwn[0]
                dam_list[didT].nextDwn=didT2
            #Case reach has more than 1 dam
            if (len(reach_list[i].ndam)>1):
                for j in range(len(reach_list[i].ndam)-1):
                    didT2=didT
                    didT=reach_list[i].ndam[j]
                    dam_list[didT].len_up=reach_list[i].damDist2dwn[j+1]-reach_list[i].damDist2dwn[j]
                    dam_list[didT].nextDwn=didT2
                didT2=didT
                didT=reach_list[i].ndam[-1]
                dam_list[didT].len_up=dam_list[didT].len_up+reach_list[i].lenr-reach_list[i].damDist2dwn[-1]
                dam_list[didT].nextDwn=didT2
            for k in range(len(reach_list[i].up)):
                    damSections(reach_list[i].up[k],didT)
        #Start at outlet as it will always have a section
        didT=0
        if (len(reach_list[outlet_reach].ndam)>1):
            for j in range(len(reach_list[outlet_reach].ndam)-1):
                didT2=didT
                didT=reach_list[outlet_reach].ndam[j]
                dam_list[didT].len_up=reach_list[outlet_reach].damDist2dwn[j+1]-reach_list[outlet_reach].damDist2dwn[j]
                dam_list[didT].nextDwn=didT2
            didT2=didT
            didT=reach_list[outlet_reach].ndam[-1]
            dam_list[didT].len_up=reach_list[outlet_reach].lenr-reach_list[outlet_reach].damDist2dwn[-1]
            dam_list[didT].nextDwn=didT2
        else:
            dam_list[didT].len_up=reach_list[outlet_reach].lenr
        for k in range(len(reach_list[outlet_reach].up)):
                damSections(reach_list[outlet_reach].up[k],didT)
        
        chkLen=rivLen
        for obj in dam_list:        
            chkLen=chkLen-obj.len_up
            l=[]
            l.append(obj.did)
            nxtDam=obj.nextDwn
            while nxtDam>-1:
                l.append(dam_list[nxtDam].did)
                nxtDam=dam_list[nxtDam].nextDwn
            obj.setDamList(l)
            #st.write("**Dam:**",obj.name)
            #st.write("**Above**",obj.nextDwn)
            #st.write("**Len:**",obj.len_up)
        if blnDiagnostic:
            st.write("Total River length:",rivLen)
            st.write("% length unaccounted for:",round(100*chkLen/rivLen,2))
               
        #DCId
        dci_d=0.
        for obj in dam_list:
            p=1.0
            for i in obj.ldam:
                p=p*dam_list[i].passability
            dci_d=dci_d+ (p*(obj.len_up/rivLen))
        dci_d=dci_d*100
        
        #DCIp
        dci_p=0.
        for obj1 in dam_list:
            for obj2 in dam_list:
                p=1.0
                l1=obj1.len_up/rivLen
                l2=obj2.len_up/rivLen
                a=set(obj1.ldam)
                b=set(obj2.ldam)
                bna=list(b-a)
                anb=list(a-b)
                path=bna+anb
                for i in path:
                    p=p*dam_list[i].passability
                dci_p=dci_p+(p*l1*l2)
        dci_p=dci_p*100
        
        st.success("**Indicator Score:**")
        col1, col2 = st.columns(2)
        col1.metric("DCIp", round(dci_p,2), "")
        col2.metric("DCId", round(dci_d,2), "")
    
        st.write("**Data Plot:**")
        seg=[]
        for obj in reach_list:
            seg.append(obj.did_dwn)
    
        df_riv['SEG']=seg    
        df_riv['WKT'] = df_riv.WKT.apply(wkt.loads)
        gdf1 = geopandas.GeoDataFrame(df_riv,geometry='WKT')        
        gdf2 = geopandas.GeoDataFrame(df_dam, geometry=geopandas.points_from_xy(df_dam.x, df_dam.y))
        
        #Matplotlib
        #fig, ax = plt.subplots()
        #gdf2.plot(ax=ax, color='black')
        #gdf1.plot('LEN',ax=ax)    
        #st.pyplot(fig) 
        
        #Plotly
        lats = []
        lons = []
        names = []
        
        fig=go.Figure()
    
        for feature, name in zip(gdf1.geometry, gdf1.ID):
            if isinstance(feature, shapely.geometry.linestring.LineString):
                linestrings = [feature]
            elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
                linestrings = feature.geoms
            else:
                continue
            for linestring in linestrings:
                #st.write(linestring)
                lats = []
                lons = []
                x, y = linestring.xy
                lats = np.append(lats, y)
                lons = np.append(lons, x)
                fig.add_trace(go.Scatter(x=lons,y=lats,mode='lines', name=name))
    
        fig.add_trace(go.Scatter(x=df_dam.x,y=df_dam.y,mode='markers', name="Dams", marker_color='black'))
        fig.update_layout(showlegend=False)
        fig.update_yaxes(
                scaleanchor = "x",
                scaleratio = 1,
                )
    
        st.plotly_chart(fig, use_container_width=False)
        gc.collect()
    else:
        st.error("Please ensure River network and dams are correctly added before this step")     