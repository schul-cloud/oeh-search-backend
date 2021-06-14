import argparse
import os
import sys
from datetime import datetime

import pandas as pd

from schulcloud.data_profiling.data_profiling import profile_dataset


def parse_arguments_profiling(argv):
    workspace = "/data/Projects/schulcloud/code/oeh-search-etl/schulcloud/data_profiling/data/"
    dataset = "mediothek"
    json_file_path = workspace + "output_mediothek_pixiothek_spider.json"

    parser = argparse.ArgumentParser(description='Profile your dataset')

    parser.add_argument('--dataset', metavar='D', type=str, nargs='+',
                        help='the dataset\'s name to be profiled',
                        default=dataset)
    parser.add_argument('--json_file_path', metavar='J', type=str, nargs='+',
                        help='the path of the file to be profiled',
                        default=json_file_path)

    args = parser.parse_args(argv)

    dataset = args.dataset if type(args.dataset) is not list else args.dataset[0]
    json_file_path = args.json_file_path if type(args.json_file_path) is not list else args.json_file_path[0]

    if not os.path.exists(json_file_path):
        print('The path specified does not exist')
        sys.exit()

    arguments = {
        "workspace": os.path.dirname(os.path.abspath(json_file_path)) + os.path.sep,
        "dataset": dataset,
        "dataset_json": json_file_path,
        "dataset_csv": json_file_path + ".csv",
        "dataset_sqlite": json_file_path + ".db",
        "dataset_exploratory_queries_excel_path": json_file_path + "_exploratory_queries_" + datetime.today().strftime(
            '%Y_%m_%d') + ".xlsx"
    }

    return arguments


def execute_profiling(argv=None):
    arguments = parse_arguments_profiling(argv)

    profiling_exploratory_queries = profile_dataset(arguments["workspace"], arguments["dataset"],
                                                    arguments["dataset_csv"], arguments["dataset_json"],
                                                    arguments["dataset_sqlite"])

    export_dict_to_excel(profiling_exploratory_queries, arguments["dataset_exploratory_queries_excel_path"])


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
    execute_profiling()