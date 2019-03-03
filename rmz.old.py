# -*- coding: utf-8 -*-

import feedparser
import pprint
import time
from utilities import create_crawljob_and_upload, read_config, get_show_information
from db import persist_download, download_exists
from pathlib import Path
from guessit import guessit
from utilities import CURRENT_FOLDER, WATCH_FOLDER, CONFIG_FILE, FTP_CONFIG, DB_FILENAME, DB_FILENAME

config = read_config(path_to_file=CONFIG_FILE).get('RMZ_Shows')


# Checks, if
def filter_relevant_show_info(show_info):
    if 'title' in show_info and 'season' in show_info and 'episode' in show_info and 'screen_size' in show_info:
        title = show_info['title']
        season = show_info['season']
        episode = show_info['episode']
        screen_size = show_info['screen_size']
    return title, season, episode, screen_size


def filter_for_shows(entries, shows):
    prefiltered_shows = list(filter(lambda x: x in entries, shows))
    return prefiltered_shows


if __name__ == '__main__':
    d = feedparser.parse('http://rmz.cr/feed')
    download_folder = config.get('downloadfolder')
    quality = config.get('quality')
    shows = config.get('shows')
    hoster = config.get('hoster')
    # Iterate through the entries and fetch the title and link, which is the relevant data
    print('###################start################### ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    prefiltered_values = list(filter(lambda x: hoster in x.title and quality in x.title, d['entries']))

    for entry in prefiltered_values:
        raw_title = entry['title']
        link = entry['link']

        # Fetch show infos from the guessit library
        show_info = get_show_information(raw_title)
        title = show_info['title']
        for show in shows:
            season = ''
            episode = ''
            # Check, if show_info contains the keys 'title', 'episode' and 'screen_size' to avoid KeyErrors
            if 'title' in show_info and 'screen_size' in show_info:
                if 'season' in show_info and 'episode' in show_info:
                    season = show_info['season']
                    episode = show_info['episode']
                screen_size = show_info['screen_size']
                if show == title and quality == screen_size and hoster in raw_title and not download_exists(title=title,
                                                                                                            season=season,
                                                                                                            episode=episode):
                    # create crawljob and upload to server
                    create_crawljob_and_upload(jobname=show, link=link, download_folder=download_folder)

                    # save download to avoid multiple downloads of the same file
                    persist_download(title=title, season=season, episode=episode)
                    print(show_info)
    print('###################ende################### ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
