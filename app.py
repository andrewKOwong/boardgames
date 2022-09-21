import streamlit as st
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.colors import XKCD_COLORS as xc
import matplotlib as mpl

CURRENT_YEAR = 2022
PATH_GENERAL_DATA = "./data/csv/2022-09-19_general_data.csv"
PATH_LINK_DATA = "./data/csv/2022-09-19_link_data.csv"
PATH_POLL_DATA = "./data/csv/2022-09-19_poll_data.csv"

# Matplotlib configuration
plt.style.use('ggplot')
COL_CRIMSON = xc['xkcd:crimson']

@st.cache
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


info_box = st.empty()
with info_box.container():
    st.info("Loading general data...")
    gen_df = load_data(PATH_GENERAL_DATA)
    st.info("Loading link data...")
    link_df = load_data(PATH_LINK_DATA)
    st.info("Loading poll data...")
    poll_df = load_data(PATH_POLL_DATA)

info_box.empty()

st.write("## EDA: General Data")
st.metric("Rows", gen_df.shape[0])
st.metric("Columns", gen_df.shape[1])
st.dataframe(data=gen_df.head(3))

#st.metric("NAs", gen_df.is_na().sum())

st.dataframe(data=gen_df.describe())
st.dataframe(data=gen_df.dtypes)