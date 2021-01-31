import unittest
from unittest import mock

from mopidy.models import Track, SearchResult, Image
from mopidy_bandcamp import Extension
from mopidy_bandcamp import backend as backend_lib


class ExtensionTest(unittest.TestCase):
    @staticmethod
    def get_config():
        config = {}
        config["enabled"] = True
        config["art_url_as_comment"] = False
        config["discover_pages"] = 1
        config["discover_genres"] = [
            "All",
            "Electronic",
            "Rock",
            "Metal",
            "Alternative",
            "Hip-Hop/Rap",
            "Experimental",
            "Punk",
            "Folk",
            "Pop",
            "Ambient",
            "Soundtrack",
            "World",
            "Jazz",
            "Acoustic",
            "Funk",
            "R&B/Soul",
            "Devotional",
            "Classical",
            "Reggae",
            "Podcasts",
            "Country",
            "Spoken Word",
            "Comedy",
            "Blues",
            "Kids",
            "Audiobooks",
            "Latin",
        ]
        config["discover_tags"] = [
            "Outrun",
            "Future Funk",
            "Alternative Hip-Hop",
            "Tokyo, Japan",
        ]
        config["image_sizes"] = ["10", "5", "2"]
        return {"bandcamp": config, "proxy": {}}

    def test_get_config_schema(self):
        ext = Extension()
        schema = ext.get_config_schema()

        assert "enabled" in schema
        assert "art_url_as_comment" in schema
        assert "discover_pages" in schema
        assert "discover_genres" in schema
        assert "discover_tags" in schema
        assert "image_sizes" in schema

    def test_get_backend_classes(self):
        registry = mock.Mock()
        ext = Extension()
        ext.setup(registry)
        assert (
            mock.call("backend", backend_lib.BandcampBackend) in registry.add.mock_calls
        )

    def test_init_backend(self):
        backend = backend_lib.BandcampBackend(ExtensionTest.get_config(), None)
        assert backend is not None
        backend.on_start()
        backend.on_stop()

    def test_browse(self):
        backend = backend_lib.BandcampBackend(ExtensionTest.get_config(), None)
        root = backend.library.browse("bandcamp:browse")
        assert len(root) == 2
        g1 = backend.library.browse("bandcamp:genres")
        assert len(g1) == len(backend.library.genres)
        assert g1[1].name == "Electronic"
        g2 = backend.library.browse(g1[1].uri)
        # Length SHOULD be 49, but Bandcamp is friggin crazy, and doesn't
        # always send the same number of items.
        assert len(g2) > 1
        t1 = backend.library.browse("bandcamp:tags")
        assert len(t1) == len(backend.library.tags)
        assert t1[1].name == "Future Funk"
        t2 = backend.library.browse(t1[1].uri)
        # Length SHOULD be 49, but Bandcamp is friggin crazy, and doesn't
        # always send the same number of items.
        assert len(t2) > 1
        a = backend.library.browse(t2[0].uri)
        # Album browse
        assert len(a) > 1

    def test_search_lookup_translate(self):
        backend = backend_lib.BandcampBackend(ExtensionTest.get_config(), None)
        res = backend.library.search('waveshaper')
        assert isinstance(res, SearchResult)
        artist = backend.library.lookup(res.artists[0].uri)
        assert isinstance(artist[0], Track)
        album = backend.library.lookup(res.albums[0].uri)
        assert isinstance(album[0], Track)
        track = backend.library.lookup(album[0].uri)
        assert isinstance(track[0], Track)
        img = backend.library.get_images([album[0].uri, res.albums[0].uri])
        assert isinstance(img[album[0].uri][0], Image)
        uri = backend.playback.translate_uri(album[0].uri)
        assert uri.startswith('http')
        uri = backend.playback.translate_uri("chewbacca")
        assert uri is None
