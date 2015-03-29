#!/usr/bin/env python3

import datetime
import json
import os
import readline
import string

import requests

LIST_URL = "https://www.mangaeden.com/api/list/0/"
MANGA_URL = "https://www.mangaeden.com/api/manga/{}/"
CHAPTER_URL = "https://www.mangaeden.com/api/chapter/{}/"
IMAGE_URL = "https://cdn.mangaeden.com/mangasimg/{}"

allManga = []
searchResults = []

args = []

def get_list():
    global allManga
    r = requests.get(LIST_URL)
    allManga = r.json()["manga"]

    print("Downloading list...")

    try:
        f = open("list_cache.json", "w")
        f.write(json.dumps(allManga))
        f.close()
    except:
        pass

def read_list():
    global allManga
    try:
        f = open("list_cache.json")
        print("Reading list from cache...")
        allManga = json.loads(f.read())
        f.close()
    except:
        get_list()

_STATUSES = ["0", "Ongoing", "Completed"]

def get_info():
    if not len(args):
        print("Usage: info <id>")
        return

    mID = None

    try:
        # search result number
        sID = int(args[0]) - 1
        if sID < len(searchResults):
            mID = allManga[searchResults[sID]]["i"]
    except:
        # manga eden id
        sID = args[0]
        for m in allManga:
            if m["i"] == sID:
                mID = sID
                break

    if not mID:
        print("Invalid ID")
        return

    r = requests.get(MANGA_URL.format(mID))
    m = r.json()

    t = "[{}] {}".format(mID, m["title"])
    print("{}\n{}".format(t, "-" * len(t)))
    print(m["description"])
    print("")
    print("Status: {}".format(_STATUSES[m["status"]]))
    print("Chapters: {}".format(m["chapters_len"]))
    print("Last updated: {}".format(datetime.datetime.fromtimestamp(int(m["last_chapter_date"])).strftime("%Y-%m-%d")))


def print_search_results():
    if not len(searchResults):
        print("No results")
        return

    digits = len(str(len(searchResults)))

    for i, r in enumerate(searchResults):
        print("[{}] {}".format(str(i + 1).zfill(digits), allManga[r]["t"]))

def fuzzy_match(string1, string2):
    string1 = string1.lower()
    string2 = string2.lower()

    string1 = "".join(c for c in string1 if c.isalnum())
    string2 = "".join(c for c in string2 if c.isalnum())

    if string1 in string2:
        return True

    return False

def find():
    global searchResults
    s = " ".join(args)
    print("Searching for {}...".format(s))
    searchResults = []
    for i, m in enumerate(allManga):
        if fuzzy_match(s, m["t"]):
            searchResults.append(i)

    print_search_results()

if __name__ == "__main__":
    read_list()

    commands = {
        "refresh": get_list,
        "find": find,
        "quit": exit,
        "exit": exit,
        "results": print_search_results,
        "info": get_info,
    }

    while True:
        try:
            raw = input("> ")
        except:
            break
        parts = raw.split(" ")
        if parts:
            cmd = parts[0]
            args = parts[1:]
            if cmd in commands:
                commands[cmd]()
            else:
                print("Unknown command: " + cmd)