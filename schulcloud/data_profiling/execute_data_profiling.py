import os
import sys
import argparse

import pandas as pd

from schulcloud.data_profiling.utils.convert import convert_json_to_csv, convert_csv_to_sqlite
from schulcloud.data_profiling.utils.data_exploration import keep_non_multicolor_thumbnails, group_same_thumbnails, \
    detect_near_duplicates
from schulcloud.data_profiling.utils.data_profiling import gather_statistics, gather_exploratory_queries

def get_parser():
    workspace = "/data/Projects/schulcloud/code/oeh-search-etl/schulcloud/data_profiling/data/"
    # dataset = "oeh";json_file_path = workspace + "output_oeh_spider.json"
    # dataset = "merlin";json_file_path = workspace + "output_merlin_spider.json"
    dataset = "mediothek";json_file_path = workspace + "output_mediothek_pixiothek_spider.json"

    parser = argparse.ArgumentParser(description='Profile your dataset')

    parser.add_argument('--dataset', metavar='D', type=str, nargs='+',
                        help='the dataset\'s name to be profiled',
                        default=dataset)
    parser.add_argument('--json_file_path', metavar='J', type=str, nargs='+',
                        help='the path of the file to be profiled',
                        default=json_file_path)
    return parser

def profile_dataset():
    parser = get_parser()
    args = parser.parse_args()

    if not os.path.exists(args.json_file_path):
        print('The path specified does not exist')
        sys.exit()

    workspace = os.path.dirname(os.path.abspath(args.json_file_path)) + os.path.sep
    dataset = args.dataset
    dataset_json = args.json_file_path

    dataset_csv = dataset_json + ".csv"
    dataset_sqlite = dataset_json + ".db"
    dataset_aggregated_statistics_csv = dataset_json + "_aggregated_statistics.csv"
    dataset_exploratory_queries_csv = dataset_json + "_exploratory_queries.xlsx"

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
    # df_aggregated_statistics.to_csv(dataset_aggregated_statistics_csv)
    export_dict_to_excel(exploratory_queries, dataset_exploratory_queries_csv)


def export_dict_to_excel(info: dict, filepath: str):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    for k in sorted(info.keys()):
        v = info[k]
        v.reset_index().to_excel(writer, sheet_name=k, index=False)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


if __name__ == '__main__':
    profile_dataset()
