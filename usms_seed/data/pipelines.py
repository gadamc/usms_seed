import pandas as pd
from usms_seed.data import extract, clean, transforms


def standard_cleaning_df_results(df_results: pd.DataFrame) -> pd.DataFrame:
    df_results['final_time_s'] = df_results['final_time'].apply(transforms.convert_to_seconds)
    df_results = clean.filter_na_or_none(df_results)
    df_results = transforms.convert_strings_to_ints(df_results, ['age'])
    df_results = clean.filter_bad_ages(df_results)
    df_results = clean.filter_bad_stroke_names(df_results)
    return df_results
