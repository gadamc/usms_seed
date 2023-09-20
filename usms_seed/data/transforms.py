import pandas as pd
from typing import List


def convert_to_seconds(time_str):
    """
    Convert a time string in the format "minutes:seconds.hundredths" or "seconds.hundredths"
    to total seconds.
    For instance, '1:34.12' becomes 94.12 and '45.12' becomes 45.12.

    Usage:
        df['seconds'] = df['time'].apply(convert_to_seconds)

    Args:
    - time_str (str): Time string in "minutes:seconds.hundredths" or "seconds.hundredths".

    Returns:
    - float: Total time in seconds.
    """
    try:
        if ':' in time_str:  # Time has minutes and seconds
            time_split = time_str.split(':')
            hours = 0
            if len(time_split) == 3:
                hours, minutes, sec_hund = time_split
                minutes = int(minutes) + 60*int(hours)
            elif len(time_split) == 2:
                minutes, sec_hund = time_split
            else:
                raise ValueError(f'{time_str} is not a valid time string.')

            seconds, hundredths = sec_hund.split('.')
            return int(minutes) * 60 + int(seconds) + int(hundredths) / 100
        else:  # Time has only seconds
            seconds, hundredths = time_str.split('.')
            return int(seconds) + int(hundredths) / 100
    except Exception as e:
        print(time_str)
        print(e)
        raise Exception(time_str)


def convert_strings_to_ints(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """
    Convert strings to ints in a dataframe.

    Usage:
        df = convert_strings_to_ints(df, ['col1', 'col2'])
    """
    df_copy = df.copy()
    for col in cols:
        df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')

    return df_copy


def compute_mean_final_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function groups the given DataFrame by 'name', 'age', 'gender', 'distance',
    'unit', and 'stroke_type' columns, computes the mean of 'final_time_s', and counts
    the number of occurrences for each group, storing it in the 'number_of_swims' column.

    :param df: Input DataFrame with swimming competition data
    :type df: pd.DataFrame
    :return: DataFrame with grouped by columns, mean final time in seconds, and number of swims
    :rtype: pd.DataFrame
    """

    # Grouping by the required columns
    grouped_df = df.groupby(['name', 'age', 'gender', 'distance', 'unit', 'stroke_type'])

    # Computing the mean of 'final_time_s' and the count for each group
    result_df = grouped_df.agg(
        mean_final_time_s=('final_time_s', 'mean'),
        std_final_time_s=('final_time_s', 'std'),
        number_of_swims=('final_time_s', 'size')
    ).reset_index()

    return result_df


def convert_time_to_min_sec_hundredths(time_in_seconds: float, return_minutes=True) -> str:
    """
    Convert time in seconds to a formatted string in "minute:seconds.hundredths" format.

    Parameters:
    - time_in_seconds (float): Time in seconds to be converted.

    Returns:
    - str: Formatted string in "minute:seconds.hundredths" format.
    """
    minutes = int(time_in_seconds // 60)
    remaining_seconds = time_in_seconds % 60
    seconds = int(remaining_seconds)
    hundredths = round((remaining_seconds - seconds) * 100)

    if return_minutes:
        return f"{minutes}:{seconds:02d}.{hundredths:02d}"
    else:
        return f"{seconds}.{hundredths:02d}"