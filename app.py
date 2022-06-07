import streamlit as st
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.colors import XKCD_COLORS as xc
import matplotlib as mpl
import utils as u

# Matplotlib configuration
plt.style.use('ggplot')
COL_CRIMSON = xc['xkcd:crimson']

CURRENT_YEAR = 2022

# Get all the xml file names
xml_data_files = [
    "./data/"+file for file in os.listdir("./data/") if file.endswith('.xml')]
xml_data_files.sort()
# Extract the data into a single dataframe
data_kwargs = {'id': True, 'year_published': True}
df = pd.concat([pd.DataFrame(u.extract_xml(file, **data_kwargs))
               for file in xml_data_files], axis=0)

# Raw stats
st.write("## Raw Statistics")
# Duplications
st.write("### Duplications")
dupes = st.columns(2)
dupes[0].metric("Items", df.shape[0])
dupes[1].metric("Duplicates", df.duplicated().sum())
# Missing data
st.write("### Missing Data")
missing = st.columns(1)
missing[0].metric("Year Published", (df['year_published'] == 0).sum())

# Clean the df
clean_df = df.drop_duplicates().query("year_published != 0")
st.write("## Cleaned Statistics")
st.write(clean_df.describe())


# Examine year published statistics
st.write("## Games by Year Published")


def generate_year_histograms(df: pd.DataFrame) -> mpl.figure.Figure:
    """Generates"""
    FIG_SIZE = (6, 3)
    YEAR_KEY = 'year_published'

    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE)

    # Histogram with all data
    axes[0].hist(data=df,
                 x=YEAR_KEY,
                 bins=20,
                 log=True,
                 color=COL_CRIMSON
                 )
    # Histogram from 1980 onwards
    axes[1].hist(data=df,
                 x=YEAR_KEY,
                 bins=np.arange(1979.5,
                                df[YEAR_KEY].max() + 1,
                                1),
                 color=COL_CRIMSON)

    # Set labels
    for ax in axes:
        ax.set_xlabel("Year")
        ax.set_ylabel("Count")

    fig.tight_layout()
    return fig


st.pyplot(generate_year_histograms(clean_df))
