import pykka
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
        self.art_comment = config["bandcamp"]["art_url_as_comment"]
        self.bandcamp = BandcampClient()
        self.library = BandcampLibraryProvider(backend=self)
        self.playback = BandcampPlaybackProvider(audio=audio, backend=self)


class BandcampPlaybackProvider(backend.PlaybackProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def translate_uri(self, uri):
        logger.debug('"Bandcamp translate_uri "%s"', uri)
        if "bandcamp:track:" not in uri:
            return None

        try:
            _, func, p = uri.split(":")
            artist, album, track = p.split("-")
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
