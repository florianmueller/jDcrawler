# -*- coding: utf-8 -*-

from utilities import *
from db import download_exists2, persist_download2


FEED_URL = "http://cre.fm/feed/m4a/"
TEST_URL = "https://tracking.feedpress.it/link/13440/7306641/cre216-chilikultur.m4a"


def parse_podcast_title_from_url(url):
    return url.split("/")[-1].split(".")[0]


def get_raw_links(feed_url):
    soup = beautiful_soup(feed_url)
    enclosures = soup.find_all("enclosure")
    return list(map(lambda x: x['url'], enclosures))


def run():
    config = read_config(path_to_file="config.yml").get('CRE')
    download_folder = config.get('downloadfolder')

    raw_links = get_raw_links(feed_url=config.get('feed'))

    for raw_link in raw_links:
        podcast_title = parse_podcast_title_from_url(raw_link)
        if not download_exists2(identifier=podcast_title):
            create_crawljob_and_upload(jobname=podcast_title, link=raw_link, download_folder=download_folder)
            persist_download2(identifier=podcast_title)
            # print("Downloading" + podcast_title)


if __name__ == "__main__":
    run()







