import os
import sqlite3
from utilities import DB_FILENAME




# def connect() -> sqlite3.Connection:
#     conn = sqlite3.connect(DB_FILENAME)
#     return conn


def persist_download(title, season, episode):
    conn = sqlite3.connect(DB_FILENAME)
    identifier = "{}S{}E{}".format(title.replace(" ", ""), str(season).replace(" ", ""), str(episode).replace(" ", ""))
    sql = "INSERT INTO download(identifier, title, season, episode) VALUES ('{}', '{}', '{}', '{}')".format(identifier,
                                                                                                            title,
                                                                                                            season,
                                                                                                            episode)
    conn.execute(sql)
    conn.commit()
    conn.close()


def persist_download2(identifier: str):
    conn = sqlite3.connect(DB_FILENAME)
    if not download_exists(identifier=identifier):
        sql = "INSERT INTO download(identifier, title, season, episode) VALUES ('{}', '{}', '{}', '{}')".format(
            identifier,
            None,
            None,
            None)
        conn.execute(sql)
        conn.commit()
        conn.close()


def download_exists(title: str, season: int, episode: int):

    # Identifier is concatenation of title, season and episode - everything without white space
    identifier = "{}S{}E{}".format(title.replace(" ", ""), str(season).replace(" ", ""), str(episode).replace(" ", ""))
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    sql = "select * from download where identifier = '{}'".format(identifier)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    if len(result) > 0:
        return True
    return False


def download_exists2(identifier: str):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    sql = "select * from download where identifier = '{}'".format(identifier)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    if len(result) > 0:
        return True
    return False
