# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 12:06:11 2022

@author: kshaad
"""

import math
import geopandas as gpd
import pandas as pd
import zipfile
import tempfile
import os
import streamlit as st
from PIL import Image
import urllib.request
import gc
import leafmap.foliumap as leafmap

def convert_wgs_to_utm(lon: float, lat: float):
    """Based on lat and lng, return best utm epsg-code"""
    utm_band = str((math.floor((lon + 180) / 6 ) % 60) + 1)
    if len(utm_band) == 1:
        utm_band = '0'+utm_band
    if lat >= 0:
        epsg_code = '326' + utm_band
        return epsg_code
    epsg_code = '327' + utm_band
    return epsg_code

#from plotly.subplots import make_subplots
@st.experimental_singleton
def dispImage(url):
    urllib.request.urlretrieve(url,"lbl.png")
    image=Image.open("lbl.png")
    return image

@st.cache(ttl=900)
def readShp(uploaded_file):
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(uploaded_file) as z:
            z.extractall(tmpdirname)   
        pth=os.path.join(os.getcwd(),tmpdirname) 
        for item in os.listdir(path=pth):
            if (item.__contains__('.shp')): 
                return gpd.read_file(pth+"\\"+item)
        #Reach here, means no shapefile
        st.error("No valid file found in zipped folder")
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
    err=0.5
    xR=abs(x1-x2)
    yR=abs(y1-y2)
    if (xR<err) and (yR<err):
        #st.write(str(x1)+","+str(x2)+","+str(y1)+","+str(y2))
        return True
    else:
        return False

def matchPointsHE(x1,y1,x2,y2):
    err=5.0
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
                    
                    1. Ideally, all data must in same projected coordinate system (such as UTM zones).
                    2. River network and dam shapefiles must be provided as zipped folders
                    3. Obstruction passavility can be modified after adding the locations using the control in step 2.                
        """)
reach_list=[]
dam_list=[]
outlet_reach=-1
rivLen=0.
nRR=0
nDam=0
blnRivLoaded=False
blnDamLoaded=False
epWGS84="epsg:4326"

inputs = st.container()
inputs.header("Step 1: Inputs")
inputs.subheader("Upload River Network")
controls = st.container()
controls.header("Step 2: Calculation")
blnDiagnostic=st.sidebar.checkbox("Print diagnostic information on screen", value=False)
st.sidebar.title("Error notifcation")
if blnDiagnostic:
    diagnotics = st.container()
    diagnotics.header("Diagnostic information")
row1_col1, row1_col2 = inputs.columns([2, 1])
uploaded_file = row1_col2.file_uploader("Upload zipped river shapefile",type=['zip'])
if uploaded_file is not None:
    try:
        basindata1=readShp(uploaded_file)
        blnRivLoaded=True
        df_riv=gpd.GeoDataFrame(geometry=basindata1['geometry'])
        df_riv = df_riv.reset_index()
        if (df_riv.crs=="epsg:4326"):
            st.sidebar.warning("River data is in WGS84 format, autoprojecting to nearest UTM")
            ep=convert_wgs_to_utm(df_riv.centroid[0].x,df_riv.centroid[0].y)
            df_riv=df_riv.to_crs(epsg=ep)

        df_riv["len"]=df_riv['geometry'].length
        if blnDiagnostic: 
            diagnotics.caption("River data preview")
            diagnotics.write(df_riv.crs)
            diagnotics.write(df_riv.head())
        
        val=row1_col2.text_input("Coordinates (in format: xx,yy):","")
        if (val!=""):
             v=val.split(",")  
             d={'x':[v[0]],'y':[v[1]]}
             df = pd.DataFrame(data=d)             
             p0=gpd.points_from_xy(df.x,df.y,crs="EPSG:4326")
             p01=p0.to_crs(df_riv.crs)
             xx_out=float(p01.x)
             yy_out=float(p01.y)
             row1_col2.write("Outlet (in "+str(df_riv.crs)+ ") is [X:"+ str(round(xx_out,2)) +", Y:"+ str(round(yy_out,2))+"]")

    except:
        blnRivLoaded=False
        st.sidebar.error("Faliure loading river outline shapefile")
        
inputs.subheader("Upload Obstruction Locations")
uploaded_file = inputs.file_uploader("Upload zipped obstruction shapefile",type=['zip'])
if uploaded_file is not None:
    try:
        df_dam=readShp(uploaded_file)
        if(df_riv.crs!=df_dam.crs):
            st.sidebar.warning("Dam data projection does not match river data, reprojecting to match")
            df_dam=df_dam.to_crs(df_riv.crs)

        colNames1=["Auto generate"]
        colNames2=["Same as index"]
        colNames3=["Default to 0"]

        for col in df_dam.columns.drop('geometry'):
            colNames1.append(col)
            colNames2.append(col)
            colNames3.append(col)
        blnDamLoaded=True
        
        df_dam=df_dam.reset_index()
        df_dam['x'] = df_dam['geometry'].x
        df_dam['y'] = df_dam['geometry'].y
        
        inputs.subheader("Set obstruction identifiers and default passability")
        c1,c2=inputs.columns([1,1])
        optName=c1.selectbox( 'Set obstruction names as?', colNames2)
        optP=c2.selectbox( 'Set obstruction passapbility as?', colNames3)
            
        if optName == "Same as index":
            df_dam['damName']=df_dam['index']
        else:
            df_dam['damName']=df_dam[optName]
        
        if optP == "Default to 0":
            df_dam['p']=0.0
        else:
            df_dam['p']=df_dam[optP]
        
        df_dam=gpd.GeoDataFrame(df_dam,columns=['index','x','y','damName','p','geometry'])
        if blnDiagnostic:
            diagnotics.caption("Dam data preview")
            diagnotics.write(df_dam.crs)
            diagnotics.write(df_dam.head())
    except:
        blnDamLoaded=False
        st.sidebar.error("Faliure loading obstruction shapefile")

with row1_col1:
    if blnRivLoaded and blnDamLoaded:
        dfdisplay=df_riv.to_crs(epWGS84)
        dfdamdisplay=df_dam.to_crs(epWGS84)
        lon, lat = leafmap.gdf_centroid(dfdisplay)
        m = leafmap.Map(center=(lat, lon))
        m.set_center(lon, lat, zoom=None) 
        m.add_gdf(dfdisplay, layer_name="River")
        m.add_gdf(dfdamdisplay, layer_name="Obstrcutions")
        m.zoom_to_gdf(dfdisplay)
        m.to_streamlit(width=450, height=450)
    elif blnRivLoaded:
        dfdisplay=df_riv.to_crs(epWGS84)
        lon, lat = leafmap.gdf_centroid(dfdisplay)
        m = leafmap.Map(center=(lat, lon))
        m.set_center(lon, lat, zoom=None) 
        m.add_gdf(dfdisplay, layer_name="River")
        m.zoom_to_gdf(dfdisplay)
        m.to_streamlit(width=450, height=450)
    else:
        m=leafmap.Map()
        m.to_streamlit(width=450, height=450)

  
if blnDamLoaded and blnRivLoaded:
    #Prepare network part
    try:     
        nRR=df_riv.shape[0] 
        #Read dataset into list of class Reach and locate outlet
        for k in range(nRR):
            l=str(df_riv.iat[k,1])
            l=l.lstrip("LINESTRING (").rstrip(")").split(",")
            a=l[0].split()
            b=l[-1].split()
            idr=df_riv.iat[k,0]
            lenr=df_riv.iat[k,2]
            
            reach_list.append(Reach(idr,lenr,float(a[0]),float(a[1]),float(b[0]),float(b[1]),l))
            if (outlet_reach==-1):
                if matchPointsHE(xx_out,yy_out,float(b[0]),float(b[1])):
                    reach_list[k].down=-999 #Outlet has downstream reach set as -999
                    outlet_reach=k
                if matchPointsHE(xx_out,yy_out,float(a[0]),float(a[1])):
                    reach_list[k].swap()
                    reach_list[k].down=-999
                    outlet_reach=k
    except:
        st.sidebar.error("River network not in expected format")
        st.stop()
        
    if (outlet_reach==-1):
        st.sidebar.error("No match for outlet found!!")
        st.stop()

    #Recurcive function to find reach upstream
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
        diagnotics.write("Input River Newtork:")               
        diagnotics.write("Total number of river reaches: "+ str(nRR))
        
        nCnt=0
        for k in range(nRR):
             if reach_list[k].down==-1:
                 diagnotics.write("Reach id:", reach_list[k].idr)
                 nCnt+=1
        diagnotics.write("Number of reach(s) unconnected: "+str(nCnt))
        diagnotics.write("Reach identified as outlet: "+ str(reach_list[outlet_reach].idr))


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
                diagnotics.write("Obstruction not found: "+ str(dam_list[i].name))
        else:
            reach_list[r_id].setDam(i,n_id)
            
    for i in range(nDam):
        if matchPointsHE(xx_out,yy_out,df_dam.iat[i,1],df_dam.iat[i,2]):
            dam_list[0].did=df_dam.iat[i,0]
            dam_list[0].name=df_dam.iat[i,3]
            dam_list[0].passability=float(df_dam.iat[i,4])
            boolNoDamAtOutlet=False
        else:
            dam_list.append(Dam(df_dam.iat[i,0],df_dam.iat[i,1],df_dam.iat[i,2],df_dam.iat[i,3],float(df_dam.iat[i,4])))
            locateDam(i+1)
    locateDam(0)
               
    if blnDiagnostic:
        diagnotics.write("Total number of obstructions found on network: "+ str(nDam - Dam.noDamFound))

    if(Dam.noDamFound== (nDam-1)):
        st.sidebar.error("No dams found on river network")
        st.stop()    
    
    if boolNoDamAtOutlet:
        nDam=nDam+1
    
    for obj in reach_list:
        obj.sortDams()
        rivLen=rivLen+obj.lenr

##Interaction
blnPass=controls.checkbox("Show interface to change obstruction passability values", value=False)
if blnPass:
    controls.subheader("Edit obstruction passability values")
    opt=controls.radio("Edit collectively or individually?" , ('Apply to all','Slider for all obstructions'))
    if opt == 'Apply to all':
        p1=controls.number_input("Value",min_value=0., max_value=1., value=1.0)
        for obj in dam_list:
            if obj.name!='Outlet':
                obj.passability=float(p1)
    else:
        for obj in dam_list:
            obj.passability=controls.slider(obj.name,min_value=0., max_value=1., value=float(obj.passability))

    
if controls.button('Step 2: Calculate DCI'):
    if len(dam_list)>0:
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

        if blnDiagnostic:
            diagnotics.write("Total River length (in meters): "+str(round(rivLen)))
            diagnotics.write("% length unaccounted for: "+ str(round(100*chkLen/rivLen,2)))
               
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
        
        controls.success("**Indicator Score:**")
        col1, col2 = controls.columns(2)
        col1.metric("DCIp", round(dci_p,2), "")
        col2.metric("DCId", round(dci_d,2), "")
    
        gc.collect()
    else:
        st.sidebar.error("Please ensure river network and obstruction locations are ingested before this step")   
