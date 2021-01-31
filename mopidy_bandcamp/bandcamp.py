import requests


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

    def get_album(self, artistid, itemid, track=False):
        resp = requests.get(
            self.BASE_URL
            + "/mobile/24/tralbum_details?band_id="
            + str(artistid)
            + "&tralbum_type="
            + ("t" if track else "a")
            + "&tralbum_id="
            + str(itemid)
        )
        json = resp.json()
        if "error" in json:
            raise RuntimeError(json["error_message"])
        return json

    def get_track(self, artistid, trackid):
        return self.get_album(artistid, trackid, track=True)

    def get_artist(self, artistid):
        resp = requests.post(
            self.BASE_URL + "/mobile/24/band_details",
            json={"band_id": artistid},
        )
        json = resp.json()
        if "error" in json:
            raise RuntimeError(json["error_message"])
        return json

    def search(self, query):
        resp = requests.get(f"{self.BASE_URL}/fuzzysearch/1/app_autocomplete?q={query}")
        return resp.json()

    def discover(self, sort="top", genre="all", tag=None, page=0):
        query = f"{self.BASE_URL}/discover/2/get?s={sort}&l=0&emulate_loc=true&f=all&g={genre}"
        if tag is not None:
            query += f"&t={tag}"
        if page > 0:
            query += f"&p={page}"
        resp = requests.get(query)
        return resp.json()
