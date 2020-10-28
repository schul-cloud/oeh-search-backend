# This package will contain utilities for the spiders of your Scrapy project
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent.parent
