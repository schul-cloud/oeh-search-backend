import json

import numpy as np
import pandas as pd
import pprint

def generate_statistics(df: pd.DataFrame):
    stats = {}
    stats["completeness"] = {}
    stats["uniqueness"] = {}
    for col in df.columns:
        df[col].replace('', np.nan)
        df[col].replace(r'^\s*$', np.nan, regex=True)
        stats["completeness"][col] = df[col].count() / len(df[col])
        stats["uniqueness"][col] = len(df[col].unique()) / df[col].count()

    # print(stats)
    print(json.dumps(stats, indent=2, default=str))

    return stats