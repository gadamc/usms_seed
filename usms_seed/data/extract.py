import pandas as pd
from typing import List
import glob
import os


def find_meet_list(directory: str) -> list:
    """
    Finds all the files in the specified directory that start with 'meet' and end with '_list.csv'.

    Args:
        directory (str): The path to the directory to search.

    Returns:
        list: A list containing the full paths of the matching files.
    """
    pattern = os.path.join(directory, 'meet*_list.csv')
    return glob.glob(pattern)


def find_meet_results(directory: str) -> list:
    """
    Finds all the files in the specified directory that start with 'meet' and end with '_results.csv'.

    Args:
        directory (str): The path to the directory to search.

    Returns:
        list: A list containing the full paths of the matching files.
    """
    pattern = os.path.join(directory, 'meet*_results.csv')
    return glob.glob(pattern)


def combine_csv_files(file_paths: List[str]) -> pd.DataFrame:
    """
    Combine multiple CSV files with the same format into a single DataFrame.

    :param file_paths: Arbitrary number of paths to CSV files to be combined
    :type file_paths: str
    :return: Combined DataFrame
    :rtype: pd.DataFrame
    """
    # List to store individual DataFrames
    data_frames_list: List[pd.DataFrame] = []

    # Iterate over each file path, read the CSV file, and append the DataFrame to the list
    for file_path in file_paths:
        csv_data = pd.read_csv(file_path)
        data_frames_list.append(csv_data)

    # Concatenate the list of DataFrames into a single DataFrame
    combined_dataframe = pd.concat(data_frames_list, ignore_index=True)

    return combined_dataframe
