import uuid
import re

import requests
import click
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://www.usms.org/comp/meets"


def create_directory(directory_path):
    # Convert the input path to a Path object
    path = Path(directory_path)

    # Check if the directory already exists
    if path.exists():
        logger.debug(f"Directory '{path}' already exists.")
    else:
        # Create the directory
        path.mkdir(parents=True)
        logger.debug(f"Directory '{path}' created successfully.")


def meetlist_url_generator(page=0):
    return f"{BASE_URL}/meetlist.php?page={page}&CourseID=0&LMSCID="


def extract_meet_list_to_df(html):
    soup = BeautifulSoup(html, 'html.parser')

    rows = soup.select('table.meetlist tr')
    data = []

    for row in rows[1:]:
        logger.debug('row: ' + row.text)
        if row.text.startswith('DatesCourseLMSC'):
            continue  # skip this row
        date = row.select('td')[0].text.strip()
        course = row.select('td')[1].text.strip()
        lmsc = row.select('td')[2].text.strip()
        meet_name = row.select('td a')[0].text.strip()
        meet_url = f"{BASE_URL}/{row.select('td a')[0]['href']}"
        meet_id = re.search(r'MeetID=([\w\d]+)', meet_url).group(1) if re.search(r'MeetID=(\d+)', meet_url) else None
        random_uuid = str(uuid.uuid4())

        data.append([date, course, lmsc, meet_name, meet_id, meet_url, random_uuid])

    columns = ["date", "course", "lmsc", "name", "meet_id", "meet_url", "meet_uuid"]
    df = pd.DataFrame(data, columns=columns)

    return df


def extract_participants_urls(html_content, meet_id):
    soup = BeautifulSoup(html_content, 'html.parser')
    form = soup.find('form', action='meetsearch.php')
    select = form.find('select', attrs={'name': 'c'})
    options = select.find_all('option')

    urls = [f"{BASE_URL}/meetsearch.php?c={option['value']}&MeetID={meet_id}" for option in options]

    return urls


def extract_individual_results(html, verbose=False):
    soup = BeautifulSoup(html, 'html.parser')
    columns = ["name", "age", "event name", "club", "seed time", "final time",
               "gender", "stroke type", "distance", "unit"]

    results_pre = soup.find('pre', {'style': 'white-space: pre; font-size:13px; font-family: monospace'})
    if not results_pre:
        logger.info("No results found for individual")
        return pd.DataFrame([], columns=columns)

    results_text = results_pre.text

    lines = results_text.split('\n')
    rows = []
    gender = None
    event_name = None
    stroke_type = None
    distance = None
    unit = None

    for line in lines:
        if 'Relay' in line:
            break  # stop if we've reached the relay results for this individual

        if verbose:
            logger.debug("line")
            logger.debug(line)
        if "Men's Results" in line:
            gender = 'Men'
        elif "Women's Results" in line:
            gender = 'Women'

        if 'Meter' in line or 'Yard' in line:
            event_name = line
            stroke_match = re.search(r'(?P<distance>\d+)\s+(Meter|Yard)\s+(?P<stroke_type>[\w\s]+)\s+', line)

            if stroke_match:
                if verbose:
                    logger.debug("stroke_match")
                    logger.debug(stroke_match)
                distance = stroke_match.group('distance')
                unit = 'Meters' if 'Meter' in line else 'Yards'
                stroke_type = stroke_match.group('stroke_type')

        result_match = re.match(r'\s*\d+\s+(?P<name>[\w\s,]+)\s+(?P<age>\d+)\s+(?P<club>\w+)\s+(?P<seed_time>[\d\.:]+)\s+(?P<final_time>[\d\.:]+)', line)
        if result_match:
            if verbose:
                logger.debug("result_match")
                logger.debug(result_match)
            name = result_match.group('name').strip()
            age = result_match.group('age')
            club = result_match.group('club')
            seed_time = result_match.group('seed_time')
            final_time = result_match.group('final_time')
            rows.append([name, age, event_name, club, seed_time, final_time, gender, stroke_type, distance, unit])

    df = pd.DataFrame(rows, columns=columns)
    return df


@click.command()
@click.option(
    "--number-of-pages", "-n",
    type=int,
    default=5,
    required=False,
    help="number of meet pages to scrape. There are 100 meet results per page.",
)
@click.option(
    "--start-page", "-sp",
    type=int,
    default=0,
    required=False,
)
@click.option(
    "--save-dir", "-s",
    type=str,
    default='data',
    required=True,
    help="location to save the scraped data",
)
@click.option(
    "--verbose", "-v",
    type=str,
    is_flag=True,
    default=False,
    required=False,
    help="print more stuff to logger output",
)
def main(**kwargs):

    create_directory(kwargs["save_dir"])
    if kwargs["verbose"]:
        logger.setLevel(logging.DEBUG)

    # first, page through USMS meet list and extract meet urls
    meetlist_urls = [meetlist_url_generator(100*page) for page in range(kwargs['start_page'], kwargs["number_of_pages"])]

    meet_list_dfs = []
    for meet_list_url in meetlist_urls:
        logger.debug('meet list url: ' + meet_list_url)
        meet_list_response = requests.get(meet_list_url)
        if meet_list_response.status_code == 200:
            logger.debug('meet list response: ' + str(len(meet_list_response.text)))
            df = extract_meet_list_to_df(meet_list_response.text)
            meet_list_dfs.append(df)

    meet_list_df = pd.concat(meet_list_dfs)
    meet_list_df.to_csv("data/meet_list.csv", index=False)
    logger.debug('meet list shape: ' + str(meet_list_df.shape))
    logger.debug(meet_list_df.head())

    # for each meet, we need to extract the meet results
    meet_results_dfs = []
    for a_meet_url, a_meet_uuid, a_meet_id in meet_list_df[['meet_url', 'meet_uuid', 'meet_id']].values:
        logger.info('meet url: ' + a_meet_url)
        logger.info('meet id: ' + str(a_meet_id))

        meet_response = requests.get(a_meet_url)
        logger.debug('meet url status: ' + str(meet_response.status_code))
        if meet_response.status_code == 200:
            # for each meet, we need to get the list of URLs for each participant
            participant_urls = extract_participants_urls(meet_response.text, a_meet_id)
            logger.info(f'found {len(participant_urls)} participants')
            # extract the results from each participant
            for participant_url in participant_urls:
                logger.debug('participant results url: ' + participant_url)
                participant_response = requests.get(participant_url)
                if participant_response.status_code == 200:
                    df = extract_individual_results(participant_response.text)
                    df['meet_list_uuid'] = a_meet_uuid
                    logger.debug('extract individual results df')
                    logger.debug(df.shape)
                    if df.shape[0] > 0:
                        meet_results_dfs.append(df)

    meet_results_df = pd.concat(meet_results_dfs)
    meet_results_df.to_csv("data/meet_results.csv", index=False)
    logger.debug(meet_results_df.shape)
    logger.debug(meet_results_df.head())


if __name__ == '__main__':
    main()
