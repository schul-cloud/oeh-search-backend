import glob
import os
import shutil
import time
from datetime import datetime

import smtplib
from email.message import EmailMessage
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.utils import COMMASPACE

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from converter.spiders.mediothek_pixiothek_spider import MediothekPixiothekSpider
from converter.spiders.merlin_spider import MerlinSpider

from converter import env
from converter.spiders.oeh_spider import OEHSpider
from schulcloud.data_profiling.execute_data_profiling import execute_profiling

"""
The script should be executed from within the data_profiling directory
"""

def download_profile_email():
    # Step 1: Download dataset locally. This requires some changes to the .env file:
    set_env_vars()

    start_crawling = time.time()
    # process = CrawlerProcess(get_project_settings())
    # process.crawl(MerlinSpider)
    # process.crawl(MediothekPixiothekSpider)
    # process.crawl(OEHSpider)
    # process.start()
    crawling_duration = time.time() - start_crawling

    # Step 2: Profile datasets
    data_dir, dataset_files = move_datasets_to_data_dir()

    start_profiling = time.time()
    for dataset, json_file_path in dataset_files.items():
        try:
            execute_profiling(["--dataset", dataset, "--json_file_path", json_file_path])
        except:
            pass
    profiling_duration = time.time() - start_profiling

    aggregated_statistics = glob.glob(data_dir + "*_exploratory_queries_" + datetime.today().strftime('%Y_%m_%d') + ".xlsx")
    # Step 3: send e-mail to specified people.
    send_mail_with_excel(
        "ioannis.koumarelas@hpi.de",
        "Aggregated statistics for Edu-Sharing content - " + datetime.today().strftime('%Y_%m_%d'),
        "Please find attached the latest aggregated statistics for the Edu-Sharing content.\n\n" + \
            "Crawling duration: " + str(crawling_duration) + " seconds.\n" + \
            "Profiling duration: " + str(profiling_duration) + " seconds",
        aggregated_statistics
    )

    pass

def set_env_vars():
    os.environ["MODE"] = "json"
    os.environ["CSV_ROWS"] = "lom.general.title,lom.general.description,lom.general.keyword,lom.technical.location," + \
                             "valuespaces.discipline,valuespaces.learningResourceType,groups,ccm:replicationsourceorigin," + \
                             "ccm:replicationsourceorigin_DISPLAYNAME,cclom:general_keyword"
    # We just want to avoid having any interaction with an actual edu-sharing instance.
    # os.environ["EDU_SHARING_BASE_URL"] = "https://localhost:443/not-an-edu-sharing-service"
    os.environ["EDU_SHARING_BASE_URL"] = "https://content.schul-cloud.dev:443/edu-sharing/"
    os.environ["LOG_LEVEL"] = "INFO"
    os.environ["DRY_RUN"] = "True"
    os.environ["DISABLE_SPLASH"] = "False"
    # os.environ["CLOSESPIDER_PAGECOUNT"] = "1"


    rows = env.get("CSV_ROWS", allow_null=False).split(",")

# Move downloaded files to data directory:
def move_datasets_to_data_dir():
    cwd = os.getcwd()

    files = glob.glob(cwd + os.path.sep + "output_*.json")

    data_dir = cwd + os.path.sep + "data" + os.path.sep
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    dataset_files = {}
    for file in files:
        new_path = shutil.copy(file, data_dir)

        if "mediothek" in new_path:
            dataset_files["mediothek"] = new_path
        elif "merlin" in new_path:
            dataset_files["merlin"] = new_path
        elif "oeh" in new_path:
            dataset_files["oeh"] = new_path
        else:
            pass

    return data_dir, dataset_files

def send_mail_with_excel(recipient_email, subject, content, excel_files):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "ContentMetrics"
    msg['To'] = recipient_email
    msg.set_content(content)

    for excel_file in excel_files:
        with open(excel_file, 'rb') as f:
            file_data = f.read()

        msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=os.path.basename(excel_file))

    with smtplib.SMTP("localhost", 25) as smtp:
        smtp.send_message(msg)

if __name__ == '__main__':
    download_profile_email()

