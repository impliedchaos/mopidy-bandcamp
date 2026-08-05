import logging
import re

import pykka

from mopidy.audio import AudioProxy
from mopidy.backend import Backend, PlaybackProvider
from mopidy.config import Config
from mopidy.types import UriScheme

from mopidy_bandcamp.bandcamp import BandcampClient
from mopidy_bandcamp.library import BandcampLibraryProvider


logger = logging.getLogger(__name__)


class BandcampBackend(pykka.ThreadingActor, Backend):
    uri_schemes = [UriScheme("bandcamp")]

    bandcamp: BandcampClient

    def __init__(self, config: Config, audio: AudioProxy):
        super(BandcampBackend, self).__init__()
        self.config = config
        self.bandcamp = BandcampClient(config)
        self.library = BandcampLibraryProvider(
            backend=self, config=config, bandcamp=self.bandcamp
        )
        self.playback = BandcampPlaybackProvider(
            audio=audio, backend=self, library=self.library
        )


class BandcampPlaybackProvider(PlaybackProvider):

    bandcamp: BandcampClient
    library: BandcampLibraryProvider

    def __init__(
        self,
        audio: AudioProxy,
        backend: BandcampBackend,
        library: BandcampLibraryProvider
    ):
        super().__init__(audio, backend)
        self.bandcamp = backend.bandcamp
        self.library = library

    def translate_uri(self, uri):
        logger.debug('"Bandcamp translate_uri "%s"', uri)
        if re.match(r"^bandcamp:(my)?track:", uri) is None:
            return None

        try:
            _, func, p = uri.split(":")
            artist, album, track = p.split("-")
            if func == "mytrack":
                if uri in self.library.scrape_urls:
                    logger.debug("Bandcamp found url in track scrape url cache")
                    url = self.library.scrape_urls[uri]
                else:
                    track = self.library.tracks.get(p)
                    if (
                            track is not None
                            and track.comment is not None
                            and track.comment.startswith("URL: ")
                    ):
                        logger.debug("Bandcamp found url in track comment")
                        url = track.comment.split(": ")[1]
                    else:
                        logger.debug("Bandcamp fetching url from web")
                        resp = self.bandcamp.get_track(artist, p)
                        url = resp["bandcamp_url"]
                resp = self.bandcamp.scrape(url)
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
                logger.error("Track not found. %s", uri)  # pragma: no cover
            else:
                resp = self.bandcamp.get_track(artist, track)
                if "tracks" in resp:
                    tr = resp["tracks"][0]
                    if "streaming_url" in tr and "mp3-128" in tr["streaming_url"]:
                        logger.debug(
                            "Bandcamp found url '%s'",
                            tr["streaming_url"]["mp3-128"],
                        )
                        return tr["streaming_url"]["mp3-128"]
                logger.error("Track not found. %s", uri)  # pragma: no cover
        except Exception as e:
            logger.error('translate_uri error "%s"', str(e))
        return None
