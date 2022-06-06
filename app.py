import streamlit as st
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.colors import XKCD_COLORS as xc
import utils as u

# Matplotlib configuration
plt.style.use('ggplot')

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


def plot_year_hist(df: pd.DataFrame,
                   year_published_key: str = 'year_published',
                   n_bins: int = 24,
                   bin_range: tuple[float, float] = None,
                   **kwargs):
    fig, ax = plt.subplots(figsize=(6, 6))
    n, bins, patches = ax.hist(x=year_published_key,
                               data=df,
                               range=bin_range,
                               bins=n_bins,
                               **kwargs)

    return fig


test = plot_year_hist(clean_df,
                      bin_range=(700, 2024),
                      color=xc['xkcd:crimson']
                      )

# dpi arg gets passed to matplotlib.savefig
st.pyplot(test, dpi=600)
