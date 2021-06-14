import copy
from functools import reduce

import pandas as pd

from schulcloud.data_profiling.utils.data_exploration_utils import generate_aggregate_statistics


def gather_statistics(df: pd.DataFrame):
    pd.set_option('display.max_columns', None)

    # Print descriptive statistics.
    descriptive_statistics = df.describe(include="all")
    stats_df = descriptive_statistics.transpose()

    # Aggregate statistics
    aggregate_stats = generate_aggregate_statistics(df)
    aggregate_stats_df = pd.DataFrame.from_dict(aggregate_stats)

    df.drop(columns=["sourceId"], inplace=True)
    df_mode = df.mode(axis='index', dropna=True).iloc[0].to_frame(name="mode")

    dfs = [stats_df, aggregate_stats_df, df_mode]
    df_final = reduce(lambda left, right: pd.merge(left, right, how="left", left_index=True, right_index=True), dfs)

    return df_final

def gather_exploratory_queries(df: pd.DataFrame):
    # TODO: thumbnail size
    attributes = ["lom.general.title", "lom.general.description", "space.cclom:location", "thumbnail.large.width_height"]

    exploratory_queries = {}

    for attribute_group in attributes:
        attribute_group_name = attribute_group.replace(":", "_")

        top100_count = df[[attribute_group]].groupby(by=[attribute_group])[[attribute_group]].count().nlargest(n=100, columns=[attribute_group])
        # top100_count.reset_index(level=0, inplace=True)
        top100_count = top100_count.rename(columns={attribute_group: "count"})
        top100_count = top100_count.reset_index().rename({'index': attribute_group}, axis='columns')

        # top100_count[attribute_group] = top100_count.index
        # top100_count = top100_count.reindex(columns=[attribute_group, "count"])
        exploratory_queries[truncate_worksheet_name(attribute_group_name + "_" + "OBcount" + "_" + "top100")] = top100_count

        df[attribute_group_name + "_length"] = df[attribute_group].str.len().fillna(value=0).astype(int)
        # df[attribute_group_name + "_length"] = df[attribute_group].apply(lambda x: len(x))
        top100_attributes = [attribute_group] + [attribute_group_name + "_length"]

        # sorted_by_length = df[top100_attributes].groupby(by=[attribute_group])[top100_attributes].count()
        # sorted_by_length = sorted_by_length.rename(columns={attribute_group: "count"})
        # sorted_by_length = sorted_by_length.sort_values(by=[attribute_group_name + "_length"], ascending=False)

        sorted_by_length = df[top100_attributes].sort_values(by=[attribute_group_name + "_length"], ascending=False)

        top100_length = sorted_by_length.head(n=100).rename(columns={attribute_group_name + "_length": "length"})
        bottom100_length = sorted_by_length.tail(n=100).rename(columns={attribute_group_name + "_length": "length"})

        exploratory_queries[truncate_worksheet_name(attribute_group_name + "_" + "OBlen" + "_" + "top100")] = top100_length
        exploratory_queries[truncate_worksheet_name(attribute_group_name + "_" + "OBlen" + "_" + "bottom100")] = bottom100_length


    # Group records by location and include title, description, and id.
    duplicates_attributes_info = ["space.cclom:location", "lom.general.title", "lom.general.description", "sourceId"]
    for attr in copy.deepcopy(duplicates_attributes_info):
        if attr not in df.columns:
            duplicates_attributes_info.remove(attr)

    duplicates_count = df[duplicates_attributes_info].groupby(by=["space.cclom:location"])[duplicates_attributes_info].count()
    duplicates_count = duplicates_count.rename(columns={"space.cclom:location": "count"})
    duplicates_count = duplicates_count[duplicates_count["count"] > 1]
    duplicates_count.sort_values(by=["count"], ascending=False, inplace=True)

    exploratory_queries[truncate_worksheet_name("duplicates_by_location")] = duplicates_count

    return exploratory_queries

def truncate_worksheet_name(name: str):
    attribute_mappings = {
        "lom.general.title": "title",
        "lom.general.description": "description",
        "space.cclom_location": "location",
        # "thumbnail.large": "thumbnail"
        "thumbnail.large.width_height": "thumbnail.sz"
    }
    for k, v in attribute_mappings.items():
        name = name.replace(k, v)
    for c in ['[', ']', ':', '*', '?', '/', '\\']:
        name = name.replace(c, "")
    if len(name) > 31:
        return name[:31]
    else:
        return name