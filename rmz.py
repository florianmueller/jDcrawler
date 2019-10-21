# -*- coding: utf-8 -*-

import feedparser
import pprint
import time
from utilities import create_crawljob_and_upload, read_config, get_show_information
from db import persist_download, download_exists
from pathlib import Path
from guessit import guessit
from utilities import CURRENT_FOLDER, WATCH_FOLDER, CONFIG_FILE, FTP_CONFIG, DB_FILENAME, DB_FILENAME
from bs4 import BeautifulSoup
import requests
import urllib3
import re
#import cfscrape
#import subprocess

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

def filter_link(link, hosterName):
    
    #headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
   'Accept-Encoding': 'none',
   'Accept-Language': 'en-US,en;q=0.8',
   'Connection': 'keep-alive'}
    #page = requests.get(link, headers = headers).content
    
    #scraper test
    #scraper = cfscrape.CloudflareScraper()
    #scraper.get(link)
    #tokens = cfscrape.get_tokens('http://rmz.cr')
    #browser = mechanicalsoup.StatefulBrowser(session=scraper, user_agent=tokens[1])
    #output = browser.get(link)
    #str_browser = str('BROWSER:'+output)
    #print (str_browser)
    
    #scraper = cfscrape.create_scraper(delay=15) 
    #output = scraper.get(link)
    #str_scraper = str(output)
    #print (str_scraper)
    


        
    page = requests.get(link, headers = headers)
    str_page = str(page)
    print(page)
    now = time.time()
    last_time = now + 20
    while time.time() <= last_time:
        if not '[503]' in str_page:
             print('success')
             page = requests.get(link, headers = headers)
             return True
        else:
            # Wait for check interval seconds, then check again.
            print('waiting for 10sec')
            time.sleep( 10 )
            page = requests.get(link, headers = headers)
            str_page = str(page)
            print(str_page)
            
    #return False
    
    
    
    soup = BeautifulSoup(page.content, 'html.parser')
    link_container = soup.findAll("div", {"class": "blog-details clear"})
    #print(link_container)
    links = list(map(lambda row: row.find_all("pre", class_="links"), link_container))
    flat_list = [item for sublist in links for item in sublist]
    print(flat_list)
    filteredLinks = list(filter(lambda entry: hosterName in entry.string, flat_list))  
    if(len(filteredLinks) > 0):
    	return filteredLinks[0]
    return None


if __name__ == '__main__':
    d = feedparser.parse('http://rmz.cr/feed')
    download_folder = config.get('downloadfolder')
    quality = config.get('quality')
    shows = config.get('shows')
    hosterShort = config.get('hosterShort')
    hosterName = config.get('hosterName')
    # Iterate through the entries and fetch the title and link, which is the relevant data
    print('###################start################### ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    prefiltered_values = list(filter(lambda x: hosterShort in x.title and quality in x.title, d['entries']))

    for entry in prefiltered_values:
        raw_title = entry['title']
        link = entry['link']


        # Fetch show infos from the guessit library
        show_info = get_show_information(raw_title)
        title = show_info['title']
        #print(show_info)
        for show in shows:
            season = ''
            episode = ''
            # Check, if show_info contains the keys 'title', 'episode' and 'screen_size' to avoid KeyErrors
            if 'title' in show_info and 'screen_size' in show_info:
                if 'season' in show_info and 'episode' in show_info:
                    season = show_info['season']
                    episode = show_info['episode']
                screen_size = show_info['screen_size']
               
                if show.lower() == title.lower() and quality == screen_size and hosterShort in raw_title and not download_exists(title=title,
                                                                                                            season=season,
                                                                                                        episode=episode):
                   
                    #deep link filter hoster shorten URL reste (dirty)
                    filteredLinkSlice = filter_link(link, hosterName)
                    filteredLink = str(filteredLinkSlice)[33:-6]
                    #print(filteredLinkSlice)
                    if not(filteredLink == ''):
                        print(filteredLink)
                    else:
                        filteredLink = link
                        print(filteredLink) 
                                        
                    # create crawljob and upload to server
                    crawljob_name = title+" S"+str(season)+"E"+str(episode)
                    #create_crawljob_and_upload(jobname=crawljob_name, link=filteredLink, download_folder=download_folder)
                    create_crawljob_and_upload(jobname=crawljob_name, link=filteredLink, download_folder=download_folder)
                    

                    # save download to avoid multiple downloads of the same file
                    persist_download(title=title, season=season, episode=episode)
                    print(show_info)
    print('###################ende################### ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))