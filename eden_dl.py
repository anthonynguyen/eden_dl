#!/usr/bin/env python3

import json
import os
import requests
import string

LIST_URL = "https://www.mangaeden.com/api/list/0/"
MANGA_URL = "https://www.mangaeden.com/api/manga/{}/"
CHAPTER_URL = "https://www.mangaeden.com/api/chapter/{}/"
IMAGE_URL = "https://cdn.mangaeden.com/mangasimg/{}"

allManga = []
searchResults = []

def get_list():
    global allManga
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
        allManga = json.loads(f.read())
        f.close()
    except:
        get_list()

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

def find(s):
    global searchResults
    print("Searching for {}...".format(s))
    searchResults = []
    for i, m in enumerate(allManga):
        if fuzzy_match(s, m["t"]):
            searchResults.append(i)

    print_search_results()

if __name__ == "__main__":
    read_list()