#!/usr/bin/env python3

import datetime
import json
import os
import readline
import string
import zipfile

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
    print("Downloading list...")
    r = requests.get(LIST_URL)
    allManga = r.json()["manga"]

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

def resolve_id():
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

    return mID


_STATUSES = ["0", "Ongoing", "Completed"]

def get_info():
    if not len(args):
        print("Usage: info <id>")
        return

    mID = resolve_id()

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

def get_chapters():
    if len(args) < 1:
        print("Usage: get <id> <chapters>")
        return

    mID = resolve_id()

    if not mID:
        print("Invalid ID")
        return

    r = requests.get(MANGA_URL.format(mID))
    m = r.json()
    slug = m["alias"]
    chapters = m["chapters"]

    if len(args) < 2 or args[1] == "all":
        start = 1
        end = len(chapters)
    elif len(args) == 2:
        try:
            start = int(args[1])
            end = start
        except:
            print("Invalid chapter")
            return
    else:
        try:
            start = int(args[1])
            end = int(args[2])
        except:
            print("Invalid chapter")
            return

        if end < start:
            print("Invalid chapter range")
            return

    start = start - 1
    if start > len(chapters):
        print("{} only has {} chapters".format(m["title"], len(chapters)))
        return

    if end > len(chapters):
        end = len(chapters)

    print("Getting chapters {} to {} of {}".format(start + 1, end, m["title"]))

    chaptersASC = chapters[::-1]
    toGet = chaptersASC[start:end]

    if not os.path.exists("download/" + slug):
        os.makedirs("download/" + slug)

    digits = len(str(m["chapters_len"]))

    for c in toGet:
        cNum = c[0] # chapter num cause we narrowed the list down before
        czip = zipfile.ZipFile("download/{}/{}_{}.zip".format(slug, slug, str(cNum).zfill(digits)), "w")

        cR = requests.get(CHAPTER_URL.format(c[3]))
        chapterImages = cR.json()["images"]

        imgDigits = len(str(len(chapterImages)))
        downloaded = 1

        for n, i in enumerate(chapterImages):
            imgID = i[0]

            print("Downloading {} chapter {}... {}/{}".format(m["title"], cNum, downloaded, len(chapterImages)), end = "\r")

            iReq = requests.get(IMAGE_URL.format(i[1]))
            czip.writestr("{}.jpg".format(str(imgID).zfill(imgDigits)), iReq.content)

            downloaded += 1

        print("")


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
        "get": get_chapters,
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