import pykka
import re

from mopidy import backend
from mopidy_bandcamp import logger
from mopidy_bandcamp.bandcamp import BandcampClient
from mopidy_bandcamp.library import BandcampLibraryProvider


class BandcampBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super(BandcampBackend, self).__init__()
        self.config = config
        self.audio = audio
        self.uri_schemes = ["bandcamp"]
        self.image_sizes = []
        for s in config["bandcamp"]["image_sizes"]:
            self.image_sizes.append(str(s))
        self.bandcamp = BandcampClient(config)
        self.library = BandcampLibraryProvider(backend=self)
        self.playback = BandcampPlaybackProvider(audio=audio, backend=self)


class BandcampPlaybackProvider(backend.PlaybackProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def translate_uri(self, uri):
        logger.debug('"Bandcamp translate_uri "%s"', uri)
        if re.match(r"^bandcamp:(my)?track:", uri) is None:
            return None
        try:
            _, func, p = uri.split(":")
            artist, album, track = p.split("-")
            if func == "mytrack":
                if uri in self.backend.library.scrape_urls:
                    logger.debug("Bandcamp found url in track scrape url cache")
                    url = self.backend.library.scrape_urls[uri]
                elif p in self.backend.library.tracks and self.backend.library.tracks[
                    p
                ].comment.startswith("URL: "):
                    logger.debug("Bandcamp found url in track comment")
                    url = self.backend.library.tracks[p].comment.split(": ")[1]
                else:
                    logger.debug("Bandcamp fetching url from web")
                    resp = self.backend.bandcamp.get_track(artist, track)
                    url = resp["bandcamp_url"]
                resp = self.backend.bandcamp.scrape(url)
                for tr in resp["tracks"]:
                    if str(tr["id"]) == track:
                        if "mp3-v0" in tr["file"]:
                            logger.debug(
                                "Bandcamp found mp3-v0 url '%s'",
                                tr["file"]["mp3-v0"],
                            )
                            return tr["file"]["mp3-v0"]
                        else:
                            if "mp3-128" in tr["file"]:
                                logger.debug(
                                    "Bandcamp found mp3-128 url '%s'",
                                    tr["file"]["mp3-128"],
                                )
                                return tr["file"]["mp3-128"]
                logger.error("Track not found. %s", uri)
            else:
                resp = self.backend.bandcamp.get_track(artist, track)
                if "tracks" in resp:
                    tr = resp["tracks"][0]
                    if "streaming_url" in tr and "mp3-128" in tr["streaming_url"]:
                        logger.debug(
                            "Bandcamp found url '%s'",
                            tr["streaming_url"]["mp3-128"],
                        )
                        return tr["streaming_url"]["mp3-128"]
                logger.error("Track not found. %s", uri)
        except Exception as e:
            logger.error('translate_uri error "%s"', str(e))
        return None
