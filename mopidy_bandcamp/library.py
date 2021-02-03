import datetime
import re

from mopidy import backend
from mopidy.models import Album, Artist, Image, Ref, SearchResult, Track
from urllib.parse import quote

from mopidy_bandcamp import logger


class BandcampLibraryProvider(backend.LibraryProvider):
    root_directory = Ref.directory(uri="bandcamp:browse", name="bandcamp")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracks = {}
        self.images = {}
        self.scrape_urls = {}
        self.tags = self.backend.config["bandcamp"]["discover_tags"]
        self.genres = self.backend.config["bandcamp"]["discover_genres"]
        self.pages = self.backend.config["bandcamp"]["discover_pages"]

    def browse(self, uri):
        if not uri:
            return []
        logger.debug('Bandcamp browse : "%s"', uri)
        if uri == "bandcamp:browse":
            dirs = []
            if self.pages:
                dirs += [
                    Ref.directory(uri="bandcamp:genres", name="Discover by Genre"),
                    Ref.directory(uri="bandcamp:tags", name="Discover by Tag"),
                ]
            if self.backend.config["bandcamp"]["identity"]:
                dirs.append(Ref.directory(uri="bandcamp:collection", name="Collection"))
            return dirs
        if uri.startswith("bandcamp:collection"):
            token = None
            if uri != "bandcamp:collection":
                token = uri[20:]
            out = []
            try:
                data = self.backend.bandcamp.get_collection(token=token)
                for i in data["items"]:
                    if "item_art" in i and "art_id" in i["item_art"]:
                        art = (
                            f"a{i['item_art']['art_id']:010d}"
                            if i["item_art"]["art_id"]
                            else None
                        )
                    if i["tralbum_type"] == "a":
                        aId = f"{i['band_id']}-{i['album_id']}"
                        name = f"{i['band_name']} - {i['album_title']} (Album)"
                        if art:
                            self.images[aId] = art
                        out.append(Ref.album(uri=f"bandcamp:myalbum:{aId}", name=name))
                        self.scrape_urls[f"bandcamp:myalbum:{aId}"] = i["item_url"]
                    elif i["tralbum_type"] == "t":
                        aId = 0
                        if i["album_id"] is not None:
                            aId = i["album_id"]
                        tId = f"{i['band_id']}-{aId}-{i['item_id']}"
                        name = f"{i['item_title']} (Track)"
                        if art:
                            self.images[tId] = art
                        out.append(Ref.album(uri=f"bandcamp:mytrack:{tId}", name=name))
                        self.scrape_urls[f"bandcamp:mytrack:{tId}"] = i["item_url"]
                if data["more_available"]:
                    out.append(
                        Ref.directory(
                            uri="bandcamp:collection:" + data["last_token"],
                            name="More...",
                        )
                    )
            except Exception:
                logger.exception("Failed to get collection")
            return out
        if uri == "bandcamp:genres" or uri == "bandcamp:tags":
            stype = uri.split(":")[1]
            return [
                Ref.directory(
                    uri="bandcamp:"
                    + ("tag:" if stype == "tags" else "genre:")
                    + re.sub(r",", "%2C", re.sub(r"[^a-z0-9,]", "-", d.lower())),
                    name=d,
                )
                for d in (self.tags if stype == "tags" else self.genres)
            ]
        if re.match(r"^bandcamp:(genre|tag):", uri):
            component = uri.split(":")
            stype, sid = component[1:3]
            total = 0
            pagenum = int(component[3]) if (len(component) > 3) else 0
            out = []
            for page in range(self.pages):
                try:
                    if stype == "genre":
                        resp = self.backend.bandcamp.discover(
                            genre=sid, page=page + pagenum
                        )
                    else:
                        resp = self.backend.bandcamp.discover(
                            tag=sid, page=page + pagenum
                        )
                except Exception:
                    logger.exception('Bandcamp failed to discover genre "%s"', uri)
                total = resp["total_count"] if ("total_count" in resp) else 0
                for i in resp["items"] if ("items" in resp) else []:
                    art = f"a{i['art_id']:010d}" if ("art_id" in i) else None
                    if i["type"] == "a":
                        aId = f"{i['band_id']}-{i['id']}"
                        name = f"{i['secondary_text']} - {i['primary_text']} (Album)"
                        if art:
                            self.images[aId] = art
                        out.append(Ref.album(uri="bandcamp:album:" + aId, name=name))
                    else:
                        # Only seen discover return album types.
                        logger.info("Found unknown type: '%s'", i["type"])
                        logger.info(i)
            if (pagenum + self.pages) * self.backend.bandcamp.PAGE_ITEMS < total:
                pagenum += self.pages
                out.append(
                    Ref.directory(
                        uri=f"bandcamp:{stype}:{sid}:{pagenum}", name="More..."
                    )
                )
            return out
        elif re.match(r"^bandcamp:(my)?(track|album):", uri):
            tracks = self.lookup(uri)
            return [Ref.track(uri=t.uri, name=t.name) for t in tracks]

    def get_images(self, uris):
        ret = {}
        for uri in uris:
            ret[uri] = []
            bcId = uri.split(":")[2]
            if bcId in self.images:
                i = self.images[bcId]
                img = f"https://f4.bcbits.com/img/{i}"
                for s in self.backend.image_sizes:
                    if s in self.backend.bandcamp.IMAGE_SIZE:
                        d = self.backend.bandcamp.IMAGE_SIZE[s]
                        ret[uri].append(
                            Image(uri=img + f"_{s}.jpg", width=d[0], height=d[1])
                        )
                    else:
                        ret[uri].append(Image(uri=img + f"_{s}.jpg"))
        return ret

    def lookup(self, uri):
        logger.debug('Bandcamp lookup "%s"', uri)
        _, func, bcId = uri.split(":")
        ret = []
        if func == "album" or func == "track" or func.startswith("my"):
            if func == "track" or func == "mytrack":
                artist, album, song = bcId.split("-")
                if bcId in self.tracks:
                    return [self.tracks[bcId]]
            else:
                artist, album = bcId.split("-")
            try:
                if func.startswith("my") and (uri in self.scrape_urls):
                    resp = self.backend.bandcamp.scrape(self.scrape_urls[uri])
                    comment = "URL: " + self.scrape_urls[uri]
                elif func == "track" or func == "mytrack":
                    resp = self.backend.bandcamp.get_track(artist, song)
                else:
                    resp = self.backend.bandcamp.get_album(artist, album)
            except Exception:
                logger.exception('Bandcamp failed to load info for "%s"', uri)
                return []
            my = ""
            if func.startswith("my"):
                my = "my"
                # If we haven't already scraped it, we'll need to:
                if "bandcamp_url" in resp:
                    url = resp["bandcamp_url"]
                    resp = self.backend.bandcamp.scrape(url)
                    comment = "URL: " + url
            dt = datetime.date
            year = "0000"
            if "release_date" in resp and resp["release_date"] is not None:
                year = dt.fromtimestamp(resp["release_date"]).strftime("%Y")
            elif (
                "album_release_date" in resp and resp["album_release_date"] is not None
            ):
                year = resp["album_release_date"].split(" ")[2]
            if "bandcamp_url" in resp:
                comment = "URL: " + resp["bandcamp_url"]
            if "art_id" in resp:
                self.images[bcId] = f"a{resp['art_id']:010d}"
            genre = ""
            if "tags" in resp:
                genre = "; ".join([t["name"] for t in resp["tags"]])
            elif "keywords" in resp:
                genre = "; ".join(resp["keywords"].split(", "))
            artref = Artist(
                uri=f"bandcamp:artist:{artist}",
                name=resp["tralbum_artist"],
                sortname=resp["tralbum_artist"],
                musicbrainz_id="",
            )
            albref = None
            if "album_title" in resp:
                albref = Album(
                    uri=f"bandcamp:{my}album:{artist}-{album}",
                    name=resp["album_title"],
                    artists=[artref],
                    num_tracks=resp["num_downloadable_tracks"],
                    num_discs=None,
                    date=year,
                    musicbrainz_id="",
                )
            for track in resp["tracks"]:
                if "is_streamable" not in track or track["is_streamable"]:
                    trref = Track(
                        uri=f"bandcamp:{my}track:{artist}-{album}-{track['track_id']}",
                        name=track["title"],
                        artists=[artref],
                        album=albref,
                        composers=[],
                        performers=[],
                        genre=genre,
                        track_no=track["track_num"],
                        disc_no=None,
                        date=year,
                        length=int(track["duration"] * 1000)
                        if track["duration"]
                        else None,
                        bitrate=320 if my == "my" else 128,
                        comment=comment,
                        musicbrainz_id="",
                        last_modified=None,
                    )
                    ret.append(trref)
                    self.tracks[f"{bcId}-{track['track_id']}"] = trref
                    if "art_id" in resp:
                        self.images[
                            f"{artist}-{album}-{track['track_id']}"
                        ] = f"a{resp['art_id']:010d}"
            logger.debug("Bandcamp returned %d tracks in lookup", len(ret))
        elif func == "artist":
            try:
                resp = self.backend.bandcamp.get_artist(bcId)
            except Exception:
                logger.exception('Bandcamp failed to load artist info for "%s"', uri)
                return []
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
        elif re.match(r"^https?", func, re.I):
            url = uri[9:]
            try:
                resp = self.backend.bandcamp.scrape(url)
                if "tracks" not in resp:
                    return self.lookup(f"bandcamp:artist:{resp['id']}")
                else:
                    my = ""
                    if "is_purchased" in resp and resp["is_purchased"]:
                        my = "my"
                    artist = resp["band_id"]
                    album = 0
                    if resp["item_type"] == "album":
                        album = resp["id"]
                    elif "current" in resp and "album_id" in resp["current"]:
                        album = resp["current"]["album_id"]
                    year = "0000"
                    if (
                        "album_release_date" in resp
                        and resp["album_release_date"] is not None
                    ):
                        year = resp["album_release_date"].split(" ")[2]
                    elif (
                        "current" in resp
                        and "release_date" in resp["current"]
                        and resp["current"]["release_date"] is not None
                    ):
                        year = resp["current"]["release_date"].split(" ")[2]
                    comment = "URL: " + url
                    if "art_id" in resp:
                        self.images[f"{artist}-{album}"] = f"a{resp['art_id']:010d}"
                    genre = ""
                    if "keywords" in resp:
                        genre = "; ".join(resp["keywords"].split(", "))
                    artref = Artist(
                        uri=f"bandcamp:artist:{artist}",
                        name=resp["tralbum_artist"],
                        sortname=resp["tralbum_artist"],
                        musicbrainz_id="",
                    )
                    albref = None
                    if "album_title" in resp:
                        albref = Album(
                            uri=f"bandcamp:{my}album:{artist}-{album}",
                            name=resp["album_title"],
                            artists=[artref],
                            num_tracks=resp["num_downloadable_tracks"],
                            num_discs=None,
                            date=year,
                            musicbrainz_id="",
                        )
                    for track in resp["tracks"]:
                        if "file" in track:
                            trref = Track(
                                uri=f"bandcamp:{my}track:{artist}-{album}-{track['track_id']}",
                                name=track["title"],
                                artists=[artref],
                                album=albref,
                                composers=[],
                                performers=[],
                                genre=genre,
                                track_no=track["track_num"],
                                disc_no=None,
                                date=year,
                                length=int(track["duration"] * 1000)
                                if track["duration"]
                                else None,
                                bitrate=320 if "mp3-v0" in track["file"] else 128,
                                comment=comment,
                                musicbrainz_id="",
                                last_modified=None,
                            )
                            ret.append(trref)
                            self.tracks[f"{bcId}-{track['track_id']}"] = trref
                            if "art_id" in resp:
                                self.images[
                                    f"{artist}-{album}-{track['track_id']}"
                                ] = f"a{resp['art_id']:010d}"
                    logger.debug("Bandcamp returned %d tracks in lookup", len(ret))
            except Exception:
                logger.error('Bandcamp failed to scrape "%s"', url)
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
            q = "+".join(map(quote, r))
        elif type(query) is list:
            q = "+".join(map(quote, query))
        try:
            resp = self.backend.bandcamp.search(q)
        except Exception:
            logger.exception("Bandcamp failed to search.")
        if "results" in resp:
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
                    comment = ""
                    if "url" in r:
                        comment = "URL: " + r["url"]
                    if "art_id" in r:
                        self.images[
                            f"bandcamp:track:{r['band_id']}-{r['album_id']}-{r['id']}"
                        ] = f"a{r['art_id']:010d}"
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
                        comment=comment,
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
        logger.debug(
            "Bandcamp search returned %d results",
            len(tracks) + len(albums) + len(artists),
        )
        return SearchResult(
            uri="bandcamp:search",
            tracks=list(tracks),
            albums=list(albums),
            artists=list(artists),
        )
