# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://komikcast.lol/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.)?komikcast\.(?:lol|site|me|com)"


class KomikcastBase():
    """Base class for komikcast extractors"""
    category = "komikcast"
    root = "https://komikcast.lol"

    @staticmethod
    def parse_chapter_string(chapter_string, data=None):
        """Parse 'chapter_string' value and add its info to 'data'"""
        if not data:
            data = {}

        match = re.match(
            r"(?:(.*) Chapter )?0*(\d+)([^ ]*)(?: (?:- )?(.+))?",
            text.unescape(chapter_string),
        )
        manga, chapter, data["chapter_minor"], title = match.groups()

        if manga:
            data["manga"] = manga.partition(" Chapter ")[0]
        if title and not title.lower().startswith("bahasa indonesia"):
            data["title"] = title.strip()
        else:
            data["title"] = ""
        data["chapter"] = text.parse_int(chapter)
        data["lang"] = "id"
        data["language"] = "Indonesian"

        return data


class KomikcastChapterExtractor(KomikcastBase, ChapterExtractor):
    """Extractor for manga-chapters from komikcast.lol"""
    pattern = BASE_PATTERN + r"(/chapter/[^/?#]+/)"
    example = "https://komikcast.lol/chapter/TITLE/"

    def metadata(self, page):
        info = text.extr(page, "<title>", " - Komikcast<")
        return self.parse_chapter_string(info)

    @staticmethod
    def images(page):
        readerarea = text.extr(
            page, '<div class="main-reading-area', '</div')
        return [
            (text.unescape(url), None)
            for url in re.findall(r"<img[^>]* src=[\"']([^\"']+)", readerarea)
        ]


class KomikcastMangaExtractor(KomikcastBase, MangaExtractor):
    """Extractor for manga from komikcast.lol"""
    chapterclass = KomikcastChapterExtractor
    pattern = BASE_PATTERN + r"(/(?:komik/)?[^/?#]+)/?$"
    example = "https://komikcast.lol/komik/TITLE"

    def chapters(self, page):
        results = []
        data = self.metadata(page)

        for item in text.extract_iter(
                page, '<a class="chapter-link-item" href="', '</a'):
            url, _, chapter_string = item.rpartition('">Chapter ')
            self.parse_chapter_string(chapter_string, data)
            results.append((url, data.copy()))
        return results

    @staticmethod
    def metadata(page):
        """Return a dict with general metadata"""
        manga , pos = text.extract(page, "<title>" , " - Komikcast<")
        genres, pos = text.extract(
            page, 'class="komik_info-content-genre">', "</span>", pos)
        author, pos = text.extract(page, ">Author:", "</span>", pos)
        mtype , pos = text.extract(page, ">Type:"  , "</span>", pos)

        return {
            "manga": text.unescape(manga),
            "genres": text.split_html(genres),
            "author": text.remove_html(author),
            "type": text.remove_html(mtype),
        }
