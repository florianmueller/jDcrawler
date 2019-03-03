from pathlib import Path
import yaml
import pysftp
from ftplib import FTP, error_reply
import os
from guessit import guessit
from bs4 import BeautifulSoup
import requests


def read_config(path_to_file: str):
    with open(path_to_file, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            return None


CURRENT_FOLDER = os.path.dirname(os.path.realpath(__file__))
WATCH_FOLDER = CURRENT_FOLDER + "/folderwatch"
CONFIG_FILE = CURRENT_FOLDER + "/config.yml"
FTP_CONFIG = CURRENT_FOLDER + "/ftp.yml"
DB_FILENAME = CURRENT_FOLDER + '/downloads.db'
connection = read_config(FTP_CONFIG).get('ftp_connection')
username = connection.get('username')
passwd = connection.get('password')
port = connection.get('port')
folder = connection.get('folderwatch')
host = connection.get('host')
port = connection.get('port')

def generate_absolute_path_mediaserver(folder):
    rootfolder = "/share/Web/temp/"
    return "{}{}".format(rootfolder, folder)


def get_ftp_connection(host, port, username, password):
    ftp = FTP()
    try:
        ftp.connect(host=host, port=port)
        ftp.login(user=username, passwd=password)
        ftp.cwd(folder)
    except error_reply:
        print(error_reply)
    # finally:
    #     ftp.quit()
    return ftp


def generate_download_folder(folder):
    rootfolder = "/temp/"
    return "{}{}".format(rootfolder, folder)


def create_crawljob_and_upload(jobname: str, link: str, download_folder):
    with open("{}/{}.crawljob".format(WATCH_FOLDER, jobname), "w") as f:
        f.write("text = {}\n".format(link))
        f.write("downloadFolder = {}\n".format(download_folder))
        f.write("enabled = TRUE\n")
        f.write("autoStart = TRUE\n")
        f.write("forcedStart = TRUE\n")
        f.write("autoConfirm = TRUE\n")
        f.close()
    push_file_to_ftp(f)


def push_file_to_ftp(file):
    connection = read_config(FTP_CONFIG).get('ftp_connection')
    f = open(file.name, 'rb')
    filename = os.path.basename(file.name)
    ftp = get_ftp_connection(host=host, port=port, username=username, password=passwd)
    try:
        ftp.storbinary('STOR ' + filename, f)
        f.close()
    except error_reply:
        print(error_reply)
    finally:
        f.close()
        ftp.quit()

def log_download(name: str):
    with open("history.txt", "a") as f:
        f.write(name + "\n")


def get_show_information(title):
    return guessit(title)


# Creates a beautifulsoup object for an url
def beautiful_soup(raw_url):
    page = requests.get(raw_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


if __name__ == "__main__":
    print(CONFIG_FILE)
