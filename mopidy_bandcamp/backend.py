import datetime
import json
import pykka
import requests

from mopidy import backend
from mopidy.models import Track, Album, Artist, SearchResult, Image
from mopidy_bandcamp import logger


class BandcampBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super(BandcampBackend, self).__init__()
        self.config = config
        self.audio = audio
        self.uri_schemes = ["bandcamp"]
        self.library = BandcampLibraryProvider(backend=self)
        self.playback = BandcampPlaybackProvider(audio=audio, backend=self)


class BandcampLibraryProvider(backend.LibraryProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TRACKS = {}
        self.IMAGES = {}

    def get_images(self, uris):
        ret = {}
        for uri in uris:
            bcId = uri.split(":")[2]
            if bcId in self.IMAGES:
                i = self.IMAGES[bcId]
                if type(i) is int:
                    ret[uri] = [Image(uri=f"https://f4.bcbits.com/img/{i:010d}_10.jpg")]
                else:
                    ret[uri] = [Image(uri=f"https://f4.bcbits.com/img/{i}_10.jpg")]
            else:
                ret[uri] = []
        return ret

    def lookup(self, uri):
        logger.info('Bandcamp lookup "%s"', uri)
        _, func, bcId = uri.split(":")
        ret = []
        if func == "album" or func == "track":
            if func == "track":
                artist, album, song = bcId.split("-")
                if bcId in self.TRACKS:
                    return [self.TRACKS[bcId]]
            else:
                artist, album = bcId.split("-")
            respdata = requests.get(
                "https://bandcamp.com/api/mobile/24/tralbum_details?band_id="
                + artist
                + "&tralbum_type="
                + ("a" if func == "album" else "t")
                + "&tralbum_id="
                + (album if func == "album" else song)
            )
            resp = json.loads(respdata.text)
            dt = datetime.date
            year = "0000"
            if "release_date" in resp and resp["release_date"] is not None:
                year = dt.fromtimestamp(resp["release_date"]).strftime("%Y")
            if "art_id" in resp:
                self.IMAGES[bcId] = f"a{resp['art_id']:010d}"
            genre = ""
            if 'tags' in resp:
                genre = "; ".join([t['name'] for t in resp['tags']])
            comment = ""
            if 'bandcamp_url' in resp:
                comment = "On bandcamp: " + resp['bandcamp_url']
            artref = Artist(
                uri=f"bandcamp:artist:{artist}",
                name=resp["tralbum_artist"],
                sortname=resp["tralbum_artist"],
                musicbrainz_id="",
            )
            albref = Album(
                uri=uri,
                name=resp["album_title"],
                artists=[artref],
                num_tracks=resp["num_downloadable_tracks"],
                num_discs=None,
                date=year,
                musicbrainz_id="",
            )
            if func == "album":
                for track in resp["tracks"]:
                    if "streaming_url" in track:
                        trref = Track(
                            uri=f"bandcamp:track:{artist}-{album}-{track['track_id']}",
                            name=track["title"],
                            artists=[artref],
                            album=albref,
                            composers=[],
                            performers=[],
                            genre=genre,
                            track_no=track["track_num"],
                            disc_no=None,
                            date=year,
                            length=int(track["duration"] * 1000),
                            bitrate=128,
                            comment=comment,
                            musicbrainz_id="",
                            last_modified=None,
                        )
                        ret.append(trref)
                        self.TRACKS[f"{bcId}-{track['track_id']}"] = trref
                        if "art_id" in resp:
                            self.IMAGES[
                                f"{artist}-{album}-{track['track_id']}"
                            ] = f"a{resp['art_id']:010d}"
            elif func == "track":
                track = resp["tracks"][0]
                trref = Track(
                    uri=f"bandcamp:track:{artist}-{album}-{track['track_id']}",
                    name=track["title"],
                    artists=[artref],
                    album=albref,
                    composers=[],
                    performers=[],
                    genre=genre,
                    track_no=track["track_num"],
                    disc_no=None,
                    date=year,
                    length=int(track["duration"] * 1000),
                    bitrate=128,
                    comment=comment,
                    musicbrainz_id="",
                    last_modified=None,
                )
                ret.append(trref)
                self.TRACKS[bcId] = trref
                if "art_id" in resp:
                    self.IMAGES[
                        f"{artist}-{album}-{track['track_id']}"
                    ] = f"a{resp['art_id']:010d}"
            logger.info("Bandcamp returned %d tracks in lookup", len(ret))
        elif func == "artist":
            respdata = requests.post(
                "https://bandcamp.com/api/mobile/24/band_details",
                json={"band_id": bcId},
            )
            resp = json.loads(respdata.text)
            if "discography" in resp:
                for disc in resp["discography"]:
                    if disc["item_type"] == "album":
                        ret.extend(
                            self.lookup(
                                f"bandcamp:album:{disc['band_id']}-{disc['item_id']}"
                            )
                        )
                    elif disc["item_type"] == "track":
                        ret.extend(
                            self.lookup(
                                f"bandcamp:track:{disc['band_id']}-0-{disc['item_id']}"
                            )
                        )
        return ret

    def search(self, query=None, uris=None, exact=False):
        tracks = set()
        albums = set()
        artists = set()
        q = query
        if type(query) is dict:
            r = []
            for v in query.values():
                if type(v) is list:
                    r.extend(v)
                else:
                    r.append(v)
            q = "+".join(r)
        elif type(query) is list:
            q = "+".join(query)
        try:
            respdata = requests.get(
                f"https://bandcamp.com/api/fuzzysearch/1/app_autocomplete?q={q}"
            )
            resp = json.loads(respdata.text)
        except Exception:
            logger.exception("Bandcamp failed to search.")
        if "results" in resp:
            logger.info("Bandcamp returned %d entries", len(resp["results"]))
            for r in resp["results"]:
                if r["type"] == "t":
                    artref = Artist(
                        uri=f"bandcamp:artist:{r['band_id']}",
                        name=r["band_name"],
                        sortname=r["band_name"],
                        musicbrainz_id="",
                    )
                    albref = Album(
                        uri=f"bandcamp:album:{r['band_id']}-{r['album_id']}",
                        name=r["album_name"],
                        artists=[artref],
                        num_tracks=None,
                        num_discs=None,
                        date="0000",
                        musicbrainz_id="",
                    )
                    trref = Track(
                        uri=f"bandcamp:track:{r['band_id']}-{r['album_id']}-{r['id']}",
                        name=r["name"],
                        artists=[artref],
                        album=albref,
                        composers=[],
                        performers=[],
                        genre="",
                        track_no=None,
                        disc_no=None,
                        date="0000",
                        length=None,
                        bitrate=128,
                        comment="",
                        musicbrainz_id="",
                        last_modified=None,
                    )
                    tracks.add(trref)
                elif r["type"] == "a":
                    artref = Artist(
                        uri=f"bandcamp:artist:{r['band_id']}",
                        name=r["band_name"],
                        sortname=r["band_name"],
                        musicbrainz_id="",
                    )
                    albref = Album(
                        uri=f"bandcamp:album:{r['band_id']}-{r['id']}",
                        name=r["name"],
                        artists=[artref],
                        num_tracks=None,
                        num_discs=None,
                        date="0000",
                        musicbrainz_id="",
                    )
                    albums.add(albref)
                elif r["type"] == "b":
                    artref = Artist(
                        uri=f"bandcamp:artist:{r['id']}",
                        name=r["name"],
                        sortname=r["name"],
                        musicbrainz_id="",
                    )
                    artists.add(artref)
        logger.info(
            "Bandcamp search returned %d results",
            len(tracks) + len(albums) + len(artists),
        )
        return SearchResult(
            uri="bandcamp:search",
            tracks=list(tracks),
            albums=list(albums),
            artists=list(artists),
        )


class BandcampPlaybackProvider(backend.PlaybackProvider):
    def translate_uri(self, uri):
        logger.info('"Bandcamp translate_uri "%s"', uri)
        if "bandcamp:track:" not in uri:
            return None

        try:
            _, func, p = uri.split(":")
            artist, album, track = p.split("-")
            respdata = requests.get(
                "https://bandcamp.com/api/mobile/24/tralbum_details?band_id="
                + artist
                + "&tralbum_type=t&tralbum_id="
                + track
            )
            resp = json.loads(respdata.text)
            if "tracks" in resp:
                tr = resp["tracks"][0]
                if "streaming_url" in tr and "mp3-128" in tr["streaming_url"]:
                    logger.info(
                        "Bandcamp found url '%s'",
                        tr["streaming_url"]["mp3-128"],
                    )
                    return tr["streaming_url"]["mp3-128"]
            logger.error("Track not found. %s", uri)
        except Exception as e:
            logger.error('translate_uri error "%s"', str(e))
        return None
