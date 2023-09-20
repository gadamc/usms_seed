import pandas as pd


def filter_na_or_none(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame removing any row has NA or None in any column.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: A DataFrame containing only the rows without NA or None values.
    """
    return df[df.isnull().any(axis=1) == False]


def filter_bad_ages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame view removing any row that has age 0 or greater than 100,
    as well as rows where the swimmer name starts with a number.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: A DataFrame (view) containing only the rows without age 0.
    """
    df = df[df.age != 0]
    df = df[df.age < 100]
    df = df[df.name.str.match(r'^\d') == False]

    return df


def filter_bad_stroke_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame view removing any row that has stroke_type not 
    in [Freestyle, Breaststroke, Backstroke, Individual Medley, Butterfly].

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: A DataFrame (view)
    """
    df = df[df.stroke_type.isin(['Freestyle', 'Breaststroke', 'Backstroke', 'Individual Medley', 'Butterfly'])]

    return df


def extract_date_from_meet_id(meet_id: str) -> str:
    """
    Extracts the date in 'Month Day Year' format from the meet_id string.

    Parameters:
        meet_id (str): The meet_id in the format YYYYMMDDXXXXX

    Returns:
        str: The extracted date in 'Month Day Year' format
    """
    year = meet_id[0:4]
    month = meet_id[4:6]
    day = meet_id[6:8]

    # Convert to pandas Timestamp to facilitate easy formatting
    date = pd.Timestamp(f"{year}-{month}-{day}")

    return date
