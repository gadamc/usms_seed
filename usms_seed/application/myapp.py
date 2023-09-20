import streamlit as st
import appdata
import numpy as np
import pandas as pd
from usms_seed.data import transforms


def run_app():
    st.title("""Swim Seed App""")

    st.write("Fill in the following to see a histogram of event times.")

    df_results, df_mean, df_meet_list = appdata.load_data()

    gender = st.selectbox(
        'Gender (note: USMS results are binary gendered)',
        df_results.gender.unique())

    stroke = st.selectbox(
        'Stroke',
        df_results.stroke_type.unique())

    distance = st.selectbox(
        'Distance',
        np.sort(df_results.distance.unique().astype(int)))

    unit = st.selectbox(
        'Course',
        df_results.unit.unique())

    age = st.number_input('Age', min_value=18, max_value=100, value=25, step=1)
    age_range = st.number_input('Age Range', min_value=0, max_value=10, value=0, step=1)

    #if st.button("Generate Histogram"):
    st.write('Results')

    if age_range != 0:
        age_predicate = (df_mean.age >= age - age_range) & (df_mean.age < age + age_range)
    else:
        age_predicate = df_mean.age == age

    x = df_mean[(df_mean.gender == gender) &
                age_predicate &
                (df_mean.stroke_type == stroke) &
                (df_mean.distance == distance) &
                (df_mean.unit == unit)].mean_final_time_s

    x_min = int(x.min())
    x_max = int(x.max()) + 1

    n_bins = 2*(x_max - x_min)
    _hist_values, _bin_edges = np.histogram(x, bins=n_bins, range=(x_min, x_max))

    if np.mean(_hist_values[np.where(_hist_values > 0)]) < 6:
        n_bins = (x_max - x_min)
        _hist_values, _bin_edges = np.histogram(x, bins=n_bins, range=(x_min, x_max))

    bin_values = map(lambda x: transforms.convert_time_to_min_sec_hundredths(x, _bin_edges[-2] > 60), _bin_edges[:-1])
    hist_pd = pd.DataFrame({'count': _hist_values, 'time (s)': bin_values})
    st.bar_chart(hist_pd, x="time (s)", y="count")


if __name__ == '__main__':
    run_app()
