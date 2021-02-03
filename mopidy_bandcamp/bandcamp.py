import json
import mopidy_bandcamp
import re
import requests

from html import unescape
from mopidy import httpclient
from time import time


class BandcampClient:
    BASE_URL = "https://bandcamp.com/api"
    PAGE_ITEMS = 48
    IMAGE_SIZE = {
        "10": [1200, 1200],
        "20": [1024, 1024],
        "5": [700, 700],
        "13": [380, 380],
        "14": [368, 368],
        "2": [350, 350],
        "4": [300, 300],
        "9": [210, 210],
        "44": [200, 200],
        "11": [172, 172],
        "7": [150, 150],
        "50": [140, 140],
        "12": [138, 138],
        "15": [135, 135],
        "8": [124, 124],
        "21": [120, 120],
        "3": [100, 100],
        "42": [50, 50],
        "22": [25, 25],
        "26": [800, 600],
        "36": [400, 300],
        "32": [380, 285],
        "33": [368, 276],
        "37": [168, 126],
        "38": [144, 108],
        "29": [100, 75],
        "28": [768, 432],
        "27": [715, 402],
    }

    def __init__(self, config):
        self.proxy = httpclient.format_proxy(config["proxy"])
        self.ua_str = httpclient.format_user_agent(
            f"{mopidy_bandcamp.Extension.dist_name}/{mopidy_bandcamp.__version__}"
        )
        self.identity = config["bandcamp"]["identity"]
        self.collection_items = config["bandcamp"]["collection_items"]
        self.fan_id = None

    def _get(self, *args, **kwargs):
        headers = {"User-Agent": self.ua_str}
        resp = requests.get(*args, **kwargs, headers=headers, proxies=self.proxy)
        resp.raise_for_status()
        js = resp.json()
        if "error" in js:
            raise RuntimeError(js["error_message"])
        return js

    def _post(self, *args, **kwargs):
        headers = {"User-Agent": self.ua_str}
        resp = requests.post(*args, **kwargs, headers=headers, proxies=self.proxy)
        resp.raise_for_status()
        js = resp.json()
        if "error" in js:
            raise RuntimeError(js["error_message"])
        return js

    def scrape(self, uri):
        headers = {"User-Agent": self.ua_str}
        if self.identity:
            headers["Cookie"] = f"identity={self.identity}"
        resp = requests.get(uri, headers=headers, proxies=self.proxy)
        resp.raise_for_status()
        # Build the tralbum data by joining multiple json chunks.
        data = re.search(r'\s+data-tralbum="(.*?)"', resp.text)
        if data is None:
            raise RuntimeError("Couldn't scrape data-tralbum from " + uri)
        tralbum = json.loads(unescape(data.group(1)))
        if "trackinfo" not in tralbum:
            # Artist page.
            data = re.search(r'\s+data-band="(.*?)"', resp.text)
            if data is None:
                raise RuntimeError("Couldn't scrape data-band from " + uri)
            tralbum.update(json.loads(unescape(data.group(1))))
        else:
            # Album/track page.
            data = re.search(r'\s+data-band-follow-info="(.*?)"', resp.text)
            if data is None:
                raise RuntimeError("Couldn't scrape data-band-follow-info from " + uri)
            tralbum.update(json.loads(unescape(data.group(1))))
            data = re.search(r'\s+data-embed="(.*?)"', resp.text)
            if data is None:
                raise RuntimeError("Couldn't scrape data-embed from " + uri)
            tralbum.update(json.loads(unescape(data.group(1))))
            data = re.search(r'application/ld\+json">\s*(.*?)\s*</script', resp.text)
            if data is not None:
                tralbum["keywords"] = json.loads(data.group(1))["keywords"]
            tralbum["tracks"] = tralbum["trackinfo"]
            tralbum["tralbum_artist"] = tralbum["artist"]
            tralbum["num_downloadable_tracks"] = None
        return tralbum

    def get_collection(self, token=None):
        if not self.identity:
            return []
        headers = {"User-Agent": self.ua_str, "Cookie": f"identity={self.identity}"}
        if self.fan_id is None:
            resp = requests.get(
                self.BASE_URL + "/fan/2/collection_summary",
                headers=headers,
                proxies=self.proxy,
            )
            resp.raise_for_status()
            self.fan_id = resp.json()["fan_id"]
        if token is None:
            token = str(time()) + ":0:a::"
        resp = requests.post(
            self.BASE_URL + "/fancollection/1/collection_items",
            headers=headers,
            proxies=self.proxy,
            json={
                "fan_id": self.fan_id,
                "older_than_token": token,
                "count": self.collection_items,
            },
        )
        resp.raise_for_status()
        js = resp.json()
        if "error" in js:
            raise RuntimeError(js["error_message"])
        return js

    def get_album(self, artistid, itemid, track=False):
        js = self._get(
            self.BASE_URL
            + "/mobile/24/tralbum_details?band_id="
            + str(artistid)
            + "&tralbum_type="
            + ("t" if track else "a")
            + "&tralbum_id="
            + str(itemid)
        )
        return js

    def get_track(self, artistid, trackid):
        return self.get_album(artistid, trackid, track=True)

    def get_artist(self, artistid):
        js = self._post(
            self.BASE_URL + "/mobile/24/band_details",
            json={"band_id": artistid},
        )
        return js

    def search(self, query):
        js = self._get(f"{self.BASE_URL}/fuzzysearch/1/app_autocomplete?q={query}")
        return js

    def discover(self, sort="top", genre="all", tag=None, page=0):
        query = f"{self.BASE_URL}/discover/2/get?s={sort}&l=0&emulate_loc=true&f=all&g={genre}"
        if tag is not None:
            query += f"&t={tag}"
        if page > 0:
            query += f"&p={page}"
        js = self._get(query)
        return js
