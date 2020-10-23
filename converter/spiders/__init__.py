# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent
