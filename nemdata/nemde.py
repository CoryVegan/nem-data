import os

import pandas as pd

from nemdata.config import HOME
from nemdata.interfaces import scrape_url, unzip_file
from nemdata.utils import download_zipfile_from_url, URL, unzip


def form_nemde_url(year, month, day):
    month = str(month).zfill(2)
    day = str(day).zfill(2)
    return "http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/NEMDE/{0}/NEMDE_{0}_{1}/NEMDE_Market_Data/NEMDE_Files/NemPriceSetter_{0}{1}{2}_xml.zip".format(
        year, month, day
    )


def make_nemde_url(year, month, day):
    month = str(month).zfill(2)
    day = str(day).zfill(2)

    home = HOME / "nemde" / f"{year}-{month}-{day}"
    home.mkdir(exist_ok=True, parents=True)

    return URL(
        url=f"http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/NEMDE/{year}/NEMDE_{year}_{month}/NEMDE_Market_Data/NEMDE_Files/NemPriceSetter_{year}{month}{day}_xml.zip",
        year=year,
        month=month,
        report="nemde",
        csv=None,
        xml=f"NemPriceSetter_{year}{month}{day}.xml",
        home=home,
    )


def make_many_nemde_urls(start, end):
    urls = []
    months = pd.date_range(start=start, end=end, freq="D")
    for year, month, day in zip(months.year, months.month, months.day):
        urls.append(make_nemde_url(year, month, day))
    return urls


from pathlib import Path


def find_xmls(path):
    fis = [p for p in Path(path).iterdir() if p.suffix == ".xml"]
    return [pd.read_xml(f) for f in fis]


def download_nemde(start, end, report_id):
    assert report_id == "nemde"
    urls = make_many_nemde_urls(start, end)
    output = []
    for url in urls:
        zf = download_zipfile_from_url(url)
        unzip(zf)
        xmls = find_xmls(url.home)

        clean = pd.concat(xmls, axis=0)

        #  get problems with a value of '5' without the cast to float
        clean["BandNo"] = clean["BandNo"].astype(float)
        print(f" saving csv and parquet to {url.home}/clean")
        clean.to_csv(Path(url.home) / "clean.csv")
        clean.to_parquet(Path(url.home) / "clean.parquet")


# def main(start, end, db):
#     months = pd.date_range(start=start, end=end, freq='D')
#     for year, month, day in zip(months.year, months.month, months.day):
#         month = str(month).zfill(2)
#         day = str(day).zfill(2)

#         url = form_nemde_url(year, month, day)
#         fldr = db.root
#         z_file = os.path.join(db.root, '{}-{}-{}.zip'.format(year, month, day))

#         if scrape_url(url, z_file):
#             unzip_file(z_file, fldr)
