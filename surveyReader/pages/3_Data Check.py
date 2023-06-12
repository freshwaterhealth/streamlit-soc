import streamlit as st
import pandas as pd

if st.session_state.raw_data == True:
    c1=int(st.session_state.code)
    st.write(c1)
    #cList=st.session_state.df_wt.Code.unique()
    #st.write(cList)
    df_wt=st.session_state.df_wt.loc[st.session_state.df_wt.Code == c1]
    df_gs=st.session_state.df_gs.loc[st.session_state.df_gs.Code == c1]
    st.write(df_wt)
    st.write(df_gs)
else:
    st.write("No raw survey data to show, reading from XML")