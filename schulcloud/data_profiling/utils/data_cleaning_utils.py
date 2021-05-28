import base64
import io
from urllib.parse import urlparse

import pandas as pd
from PIL import Image
from url_normalize import url_normalize


def prepare_records(df: pd.DataFrame):
    r_dummy = get_prepared_record({})
    for k, v in r_dummy.items():
        df[k] = ""

    for i, r in df.iterrows():
        r_prepared = get_prepared_record(r.to_dict(into=dict))
        for k, v in r_prepared.items():
            df.at[i, k] = v

    df = df.drop(columns=["thumbnail.small", "thumbnail.large"])

    return df

def get_prepared_record(r: dict) -> dict:
    thumbnail_metadata = get_thumbnail_metadata(r)
    r = {**r, **thumbnail_metadata}  # add thumbnail_metadata (dict) to r (dict) -- i.e., merge.

    try:
        normalized_location = get_normalized_location(r)
        # r = {**r, **normalized_location}  # add thumbnail_metadata (dict) to r (dict) -- i.e., merge.
        r["lom"]["technical"]["location"] = normalized_location
    except:
        pass

    r["lom"]["technical"]["location_hostname"] = get_location_hostname(r)

    return r

def get_thumbnail_metadata(r):
    thumbnail_metadata = {}

    if "thumbnail" in r:
        thumbnail_metadata["thumbnail.large"] = r["thumbnail"]["large"] if "large" in r["thumbnail"] else r["thumbnail"]["small"]
        thumbnail_metadata["thumbnail.small"] = r["thumbnail"]["small"]
        thumbnail_metadata["thumbnail.mimetype"] = r["thumbnail"]["mimetype"]

    # Default value empty string
    for attribute in ["thumbnail.large", "thumbnail.small", "thumbnail.mimetype"]:
        if attribute not in thumbnail_metadata:
            thumbnail_metadata[attribute] = ""

    for property in ["width", "height", "size"]:
        for attribute in  ["thumbnail.large", "thumbnail.small"]:
            thumbnail_metadata[attribute + "." + property] = infer_thumbnail_dimensions(thumbnail_metadata[attribute])[property]

    if "thumbnail.large.width" in thumbnail_metadata and "thumbnail.large.height" in thumbnail_metadata:
        thumbnail_metadata["thumbnail.large.width_height"] = thumbnail_metadata["thumbnail.large.width"] + "x" + thumbnail_metadata["thumbnail.large.height"]

    r["thumbnail.mimetype"] = r["thumbnail"]["mimetype"]

    del thumbnail_metadata["thumbnail.large"]
    del thumbnail_metadata["thumbnail.small"]

    return thumbnail_metadata


def infer_thumbnail_dimensions(image_as_str):
    default = {
        "width": "-1",
        "height": "-1",
        "size": "-1"
    }
    if image_as_str == "":
        return default
    img = None
    try:
        img = Image.open(io.BytesIO(base64.b64decode(image_as_str)))
    except:
        print("Issue while parsing thumbnail")
        return default

    return {
        "width": str(img.width),
        "height": str(img.height),
        "size": str(img.width * img.height)
    }

def get_normalized_location(r):
    normalized_location = url_normalize(r["lom"]["technical"]["location"])
    # return {"lom": {"technical": {"location": normalized_location }}}
    return normalized_location

def get_location_hostname(r):
    location = r["lom"]["technical"]["location"]
    parsed_uri = urlparse(location)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return result