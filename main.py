# main file for website

# Import convention
import streamlit as st
import pandas as pd

master_stats = pd.read_csv("master_stats.csv")

st.table(master_stats)