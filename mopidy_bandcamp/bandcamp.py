import requests


class BandcampClient:
    BASE_URL = "https://bandcamp.com/api"

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
        return resp.json()

    def get_track(self, artistid, trackid):
        return self.get_album(artistid, trackid, track=True)

    def get_artist(self, artistid):
        resp = requests.post(
            self.BASE_URL + "/mobile/24/band_details",
            json={"band_id": artistid},
        )
        return resp.json()

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
