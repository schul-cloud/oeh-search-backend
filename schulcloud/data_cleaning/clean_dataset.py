from schulcloud.data_cleaning.utils.convert import convert_file
from schulcloud.data_cleaning.utils.understand_data import generate_statistics
import pandas as pd

def clean_dataset():
    dataset_json = "/data/Projects/schulcloud/code/oeh-search-etl/schulcloud/data_cleaning/output_oeh_spider.json"
    dataset_csv = "/data/Projects/schulcloud/code/oeh-search-etl/schulcloud/data_cleaning/output_oeh_spider.json.csv"

    # Step 1: Convert data.
    # convert_file(dataset_json, dataset_csv)

    # Step 2: Generate statistics.
    df = pd.read_csv(dataset_csv)
    stats = generate_statistics(df)
    pass

if __name__ == '__main__':
    clean_dataset()