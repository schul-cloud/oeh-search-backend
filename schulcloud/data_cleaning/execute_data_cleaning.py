import os

from schulcloud.data_cleaning.utils.convert import convert_json_to_csv, convert_csv_to_sqlite
from schulcloud.data_cleaning.utils.data_exploration import keep_non_multicolor_thumbnails, group_same_thumbnails, \
    detect_near_duplicates
from schulcloud.data_cleaning.utils.data_profiling import gather_statistics, gather_exploratory_queries

import pandas as pd

def clean_dataset():
    workspace = "/data/Projects/schulcloud/code/oeh-search-etl/schulcloud/data_cleaning/data/"
    # dataset = "oeh"; dataset_json = workspace + "output_oeh_spider.json"
    # dataset = "merlin";dataset_json = workspace + "output_merlin_spider.json"
    dataset = "mediothek"; dataset_json = workspace + "output_mediothek_pixiothek_spider.json"

    dataset_csv = dataset_json + ".csv"
    dataset_sqlite = dataset_json + ".db"
    dataset_enriched_csv = dataset_json + "_enriched.csv"
    dataset_aggregated_statistics_csv = dataset_json + "_aggregated_statistics.csv"
    dataset_exploratory_queries_csv = dataset_json + "_exploratory_queries.xlsx"

    pd.set_option('display.max_columns', None)
    """
    Data Exploration
    """
    # Step 1: Convert data (skipping thumbnails due to large size).
    if not os.path.exists(dataset_csv):
        convert_json_to_csv(dataset_json, dataset_csv)
    if not os.path.exists(dataset_sqlite):
        convert_csv_to_sqlite(dataset_csv, dataset_sqlite)
    df = pd.read_csv(dataset_csv)
    df = df.fillna('')

    # Step 2: Explore data
    # a. Execute SQL queries (reuse existing SQL files)
    # TODO

    # b. Thumbnails:
    # group_same_thumbnails(workspace, dataset, dataset_json)
    # keep_non_multicolor_thumbnails(workspace, dataset, dataset_json)

    # detect_near_duplicates(workspace, dataset_json)

    """
    Data Profiling
    
    Gather things we considered in data exploration to be meaningful and export them in an easy to read format. 
    """
    # df_aggregated_statistics = gather_statistics(df)
    # df_aggregated_statistics.to_csv(dataset_aggregated_statistics_csv)

    exploratory_queries = gather_exploratory_queries(df)
    export_dict_to_excel(exploratory_queries, dataset_exploratory_queries_csv)


    # TODO: Generate statistics??
    # df = pd.read_csv(dataset_csv)
    #
    # # Step 3: Enrich data. (prepare + enrichment)
    # df_clean = pd.read_csv(dataset_csv)

    pass

def export_dict_to_excel(info: dict, filepath: str):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    for k, v in info.items():
        v.reset_index().to_excel(writer, sheet_name=k, index=False)
        # df1.to_excel(writer, sheet_name='Sheet1')
        # df2.to_excel(writer, sheet_name='Sheet2')
        # df3.to_excel(writer, sheet_name='Sheet3')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


if __name__ == '__main__':
    clean_dataset()
