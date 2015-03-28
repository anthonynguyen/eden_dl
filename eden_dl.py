#!/usr/bin/env python3

import requests

LIST_URL = "https://www.mangaeden.com/api/list/0/"
MANGA_URL = "https://www.mangaeden.com/api/manga/{}/"
CHAPTER_URL = "https://www.mangaeden.com/api/chapter/{}/"
IMAGE_URL = "https://cdn.mangaeden.com/mangasimg/{}"

allManga = []

def get_list():
	global allManga
	r = requests.get(LIST_URL)
	allManga = r.json()["manga"]

def slugify(s):
	allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 "
	s = "".join(l for l in s if l in allowed)
	return s.replace(" ", "-").lower()

def find_in_list(s):
	search = slugify(s)
	print("Searching for {}".format(search))
	for m in allManga:
		if m["a"] == search:
			print(m)

get_list()
