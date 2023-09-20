import os

import streamlit as st
import pandas as pd

from usms_seed.data import extract, clean, transforms, pipelines


@st.cache_data
def load_data() -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    data_dir = os.environ['SWIM_SEED_APP_DATA_DIR']
    df_results = extract.combine_csv_files(extract.find_meet_results(data_dir))
    df_meet_list = extract.combine_csv_files(extract.find_meet_list(data_dir))

    df_results = pipelines.standard_cleaning_df_results(df_results)
    df_mean = transforms.compute_mean_final_time(df_results)

    df_results = df_results.merge(df_meet_list, left_on='meet_list_uuid', right_on='meet_uuid', how='left')

    return df_results, df_mean, df_meet_list
