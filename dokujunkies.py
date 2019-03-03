# -*- coding: utf-8 -*-

import feedparser
from db import download_exists, persist_download
from utilities import read_config, get_show_information
from bs4 import BeautifulSoup
import urllib
import requests
from utilities import create_crawljob_and_upload, CONFIG_FILE

config = read_config(path_to_file=CONFIG_FILE).get('Dokujunkies_Geschichtepolitik')
link_list = []


# DEPRECATED
def get_raw_urls_old():
    """ Returns a list of tuples. A tuple contains the link and the title of a documentary that should be downloaded."""
    linklist = []
    feed_url = config.get('feed')
    d = feedparser.parse(feed_url)
    for entry in d['entries']:
        if not is_blacklisted(entry):
            link = entry['link']
            # raw_title = entry['title']
            title = entry['title'].split(" – ")[0] if len(entry['title'].split(" – ")[0]) > 0 else 'title'
            linklist.append((link, title))
    return linklist


def get_raw_urls():
    """ Returns a list of tuples. A tuple contains the link and the title of a documentary that should be downloaded."""
    feed_url = config.get('feed')
    d = feedparser.parse(feed_url)
    return list(map(lambda entry: (
        entry['link'], entry['title'].split(" – ")[0] if len(entry['title'].split(" – ")[0]) > 0 else 'title'),
                    d['entries']))


def is_blacklisted(entry):
    blacklist = config.get('blacklist')
    for tag in entry['tags']:
        if tag['term'] in blacklist:
            return True
    return False


def sanitize(raw_title):
    return raw_title.replace("–", "")


def remove_white_spaces(text):
    return text.replace(" ", "")


def get_download_link(soup):
    quality = config.get('quality')
    hoster = config.get('hoster')
    paragraphs = soup.findAll('p')
    for p in paragraphs:
        if quality in p.text and hoster in p.text:
            downloadable_links = p.findAll('a')
            for dl in downloadable_links:
                if hoster in dl.next_sibling:
                    return dl['href']


# Adds the links + show information to the link_list
def filter_downloads(soup, link_list, quality, hoster):
    paragraphs = soup.findAll("p")
    pre_filtered_paragraphs = list(filter(lambda p: quality in p.text and hoster in p.text, paragraphs))
    for item in pre_filtered_paragraphs:
        links = item.findAll('a')
        for link in links:
            if hoster in link.next_sibling:
                link_list.append((link['href'], get_show_information(item.text)))


# Creates a beautifulsoup object for an url
def beautiful_soup(raw_url):
    page = requests.get(raw_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def run():
    raw_urls = get_raw_urls()
    quality = config.get('quality')
    hoster = config.get('hoster')
    download_folder = config.get('downloadfolder')

    list(map(lambda x: filter_downloads(link_list=link_list, soup=beautiful_soup(x[0]), quality=quality, hoster=hoster),
             raw_urls))

    for entry in link_list:
        download_link = entry[0]
        # Remove whitespaces from title
        title = entry[1]['title']
        title = remove_white_spaces(title)

        # Fetch season if available, else set it as empty string, remove whitespaces
        season = remove_white_spaces(str(entry[1]['season'])) if 'season' in entry[1] else ""

        # Fetch episode if available, else set it as empty string, remove whitespaces
        episode = remove_white_spaces(str(entry[1]['episode'])) if 'episode' in entry[1] else ""

        identifier = "{}S{}E{}".format(title, season, episode)

        # if there's no db entry yet, create the crawljob and upload it to the FTP server

        if not download_exists(title=title, season=season, episode=episode):
            create_crawljob_and_upload(jobname=identifier, link=download_link, download_folder=download_folder)
            persist_download(title=title, season=season, episode=episode)

    link_list.clear()


if __name__ == '__main__':
    run()
