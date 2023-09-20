import streamlit as st
import numpy as np
import appdata

df_results, df_mean, df_meet_list = appdata.load_data()

st.subheader('Distribution of age of swimmers')
swimmer_ages = df_mean.groupby('name').last().age

hist_values = np.histogram(swimmer_ages, bins=100, range=(0,99))[0]
st.bar_chart(hist_values)