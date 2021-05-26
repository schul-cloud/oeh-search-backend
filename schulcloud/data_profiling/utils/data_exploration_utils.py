import base64
import io
import json
import os

import ijson
import numpy as np
import pandas as pd
import pprint

from PIL import Image
from tqdm import tqdm

import pickle

from schulcloud.data_profiling.utils.data_cleaning import get_prepared_record


def generate_aggregate_statistics(df: pd.DataFrame):
    # Treat all columns as strings.
    df = df.astype(str)
    # Replace empty values with NaN.
    df = df.replace(r'^\s+$', np.nan, regex=True)
    df = df.replace('^nan$', np.nan, regex=True)

    stats = {}
    stats["completeness"] = {}
    stats["uniqueness"] = {}
    for col in df.columns:
        df[col].replace('', np.nan)
        df[col].replace(r'^\s*$', np.nan, regex=True)
        stats["completeness"][col] = df[col].count() / len(df[col])
        stats["uniqueness"][col] = len(df[col].unique()) / df[col].count()

    # print(stats)
    # print(json.dumps(stats, indent=2, default=str))

    return stats


def save_thumbnail(image_str: str, filepath: str):
  img = Image.open(io.BytesIO(base64.b64decode(image_str)))
  img.save(filepath, format="png")
  pass


def block_by_thumbnail(workspace: str, dataset_json: str):
    thumbnails_pickled_path = dataset_json + "_thumbnails.p"
    if not os.path.exists(thumbnails_pickled_path):
        # key: thumbnail_str, value: first sourceId
        thumbnails_dict = {}
        with open(dataset_json, 'rb') as json_file:
            counter = 0
            for item in tqdm(ijson.items(json_file, "item")):
                counter += 1
                # print(item)
                item = get_prepared_record(item)

                thumbnail_str = item["thumbnail"]["large"] if "large" in item["thumbnail"] else item["thumbnail"][
                    "small"]
                sourceId = item["sourceId"]

                title = "notitle_" + str(counter)
                if "space" in item and "cclom:title" in item["space"]:
                    title = item["space"]["cclom:title"][0]
                # print(title)
                if thumbnail_str not in thumbnails_dict:
                    thumbnails_dict[thumbnail_str] = {"canonicalId": sourceId, "count": 1, "title": title}
                else:
                    thumbnails_dict[thumbnail_str]["count"] += 1
        pickle.dump(thumbnails_dict, open(thumbnails_pickled_path, "wb"))
    else:
        thumbnails_dict = pickle.load(open(thumbnails_pickled_path, "rb"))

    thumbnails_list = [(k, v["canonicalId"], v["count"]) for k, v in thumbnails_dict.items()]
    thumbnails_list = sorted(thumbnails_list, key=lambda x: int(x[2]), reverse=True)

    return thumbnails_dict, thumbnails_list


def group_same_thumbnails(workspace, dataset, dataset_json):
    thumbnail_dir = workspace + "thumbnails_duplicates_" + dataset + "/"
    if not os.path.exists(thumbnail_dir):
        os.makedirs(thumbnail_dir)

    thumbnails_dict, thumbnails_list = block_by_thumbnail(workspace, dataset_json)

    thumbnails = list(thumbnails_dict.keys())

    for i, thumbnail_str in tqdm(enumerate(thumbnails)):
        try:
            if thumbnails_dict[thumbnail_str]["count"] == 1:
                continue
            filepath = thumbnail_dir + str(thumbnails_dict[thumbnail_str]["count"]) + "_" + \
                       thumbnails_dict[thumbnail_str]["title"]

            save_thumbnail(thumbnail_str, filepath)
        except:
            pass


def keep_non_multicolor_thumbnails(workspace, dataset, dataset_json):
    number_of_colors = 10

    thumbnail_dir = workspace + "thumbnails_colors_" + dataset + "_lt_" + str(number_of_colors) + "/"
    if not os.path.exists(thumbnail_dir):
        os.makedirs(thumbnail_dir)

    thumbnails_dict, thumbnails_list = block_by_thumbnail(workspace, dataset_json)

    thumbnails = list(thumbnails_dict.keys())

    for i, thumbnail_str in tqdm(enumerate(thumbnails)):
        try:
            img = Image.open(io.BytesIO(base64.b64decode(thumbnail_str)))
            clrs = img.getcolors()
            if clrs is not None and len(clrs) < 30:
                colors_int_str = "_".join(sorted(list(set([str(c[0]) for c in clrs]))))
            else:
                continue
            filepath = thumbnail_dir + str(thumbnails_dict[thumbnail_str]["count"]) + "_" + colors_int_str

            save_thumbnail(thumbnail_str, filepath)
        except:
            pass


def detect_near_duplicates(workspace, dataset_json):

    pass