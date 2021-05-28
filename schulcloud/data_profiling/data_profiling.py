import argparse
import os
import sys
from datetime import datetime

import pandas as pd

from schulcloud.data_profiling.utils.convert import convert_json_to_csv, convert_csv_to_sqlite
from schulcloud.data_profiling.utils.data_exploration_utils import keep_non_multicolor_thumbnails, \
    group_same_thumbnails, \
    detect_near_duplicates
from schulcloud.data_profiling.utils.data_profiling_utils import gather_statistics, gather_exploratory_queries


def profile_dataset(workspace, dataset, dataset_csv, dataset_json, dataset_sqlite) -> dict:
    pd.set_option('display.max_columns', None)
    """
    Data Exploration

    Before we decide on things we want to examine regularly with Data Profiling, we need to explore the data and find 
    out potential issues.
    """
    # Step 1: Convert data (skipping thumbnails due to large size).
    if not os.path.exists(dataset_csv):
        convert_json_to_csv(dataset_json, dataset_csv)
    if not os.path.exists(dataset_sqlite):
        convert_csv_to_sqlite(dataset_csv, dataset_sqlite)
    df = pd.read_csv(dataset_csv)
    df = df.fillna('')

    # Step 2: Explore data
    # a. Execute SQL queries (reuse existing SQL files) manually using SQL queries under 'utils/sql_queries'.

    # b. Thumbnails:
    group_same_thumbnails(workspace, dataset, dataset_json)
    keep_non_multicolor_thumbnails(workspace, dataset, dataset_json)

    # Manually examine thumbnails for duplications under data_profiling/data/thumbnails_*
    detect_near_duplicates(workspace, dataset_json)

    """
    Data Profiling

    Gather things we considered in data exploration to be meaningful and export them in an easy to read format. 
    """
    exploratory_queries = gather_exploratory_queries(df)

    df_aggregated_statistics = gather_statistics(df)
    exploratory_queries["Aggregated statistics"] = df_aggregated_statistics

    return exploratory_queries


if __name__ == '__main__':
    profile_dataset()
