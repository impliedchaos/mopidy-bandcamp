import os
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
        config["identity"] = ""
        config["collection_items"] = 50
        return {"bandcamp": config, "proxy": {}}

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        assert "[bandcamp]" in config
        assert "enabled=true" in config

    def test_get_config_schema(self):
        ext = Extension()
        schema = ext.get_config_schema()

        assert "enabled" in schema
        assert "discover_pages" in schema
        assert "discover_genres" in schema
        assert "discover_tags" in schema
        assert "image_sizes" in schema
        assert "identity" in schema
        assert "collection_items" in schema

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
        root = backend.library.browse(None)
        assert root == []
        root = backend.library.browse("chewbacca")
        assert root is None
        root = backend.library.browse("bandcamp:browse")
        assert len(root) == 2
        g1 = backend.library.browse("bandcamp:genres")
        assert len(g1) == len(backend.library.genres)
        assert g1[1].name == "Electronic"
        g2 = backend.library.browse(g1[1].uri + ":2")
        # Length SHOULD be 49, but Bandcamp is friggin crazy, and doesn't
        # always send the same number of items.
        assert len(g2) > 40
        t1 = backend.library.browse("bandcamp:tags")
        assert len(t1) == len(backend.library.tags)
        assert t1[1].name == "Future Funk"
        t2 = backend.library.browse(t1[1].uri)
        # Length SHOULD be 49, but Bandcamp is friggin crazy, and doesn't
        # always send the same number of items.
        assert len(t2) > 40
        a = backend.library.browse(t2[0].uri)
        # Album browse
        assert len(a) > 1

    def test_search_lookup_translate(self):
        backend = backend_lib.BandcampBackend(ExtensionTest.get_config(), None)
        track = backend.library.lookup("bandcamp:track:nope-0-nuhuh")
        assert track == []
        artist = backend.library.lookup("bandcamp:artist:nope")
        assert artist == []
        album = backend.library.lookup("bandcamp:album:nope-nuhuh")
        assert album == []
        sleep(1)
        res = backend.library.search(
            {"any": "Waveshaper", "album": ["Station", "Nova"]}
        )
        assert isinstance(res, SearchResult)
        res = backend.library.search(["Station", "Nova"])
        assert isinstance(res, SearchResult)
        res = backend.library.search("Waveshaper")
        assert isinstance(res, SearchResult)
        artist = backend.library.lookup("bandcamp:nothing")
        assert artist == []
        sleep(1)
        artist = backend.library.lookup("bandcamp:artist:4274249518")
        assert isinstance(artist[0], Track)
        album = backend.library.lookup("bandcamp:album:4274249518-4240848302")
        assert isinstance(album[0], Track)
        sleep(0.5)
        track = backend.library.lookup("bandcamp:track:2937093478-3573329354-2851348889")
        assert isinstance(track[0], Track)
        img = backend.library.get_images(
            ["bandcamp:track:1715582766-4294604529-839491036"]
        )
        assert isinstance(
            img["bandcamp:track:1715582766-4294604529-839491036"][0], Image
        )
        img = backend.library.get_images(["bandcamp:browse", "bandcamp:tag:outrun"])
        assert isinstance(img["bandcamp:browse"][0], Image)
        assert isinstance(img["bandcamp:tag:outrun"][0], Image)
        uri = backend.playback.translate_uri(album[0].uri)
        assert uri.startswith("http")
        uri = backend.playback.translate_uri("chewbacca")
        assert uri is None
        uri = backend.playback.translate_uri(
            "bandcamp:mytrack:1113572798-2944001033-1139398039"
        )
        assert uri is None
        uri = backend.playback.translate_uri("bandcamp:track:0-0-0")
        assert uri is None

    def test_other(self):
        cfg = ExtensionTest.get_config()
        cfg["bandcamp"]["art_url_as_comment"] = True
        cfg["bandcamp"]["discover_pages"] = 0
        cfg["bandcamp"]["image_sizes"] = ["1"]
        backend = backend_lib.BandcampBackend(cfg, None)
        res = backend.library.search("Waveshaper")
        assert isinstance(res, SearchResult)
        track = backend.library.lookup("bandcamp:track:4274249518-4240848302-55800693")
        assert isinstance(track[0], Track)
        img = backend.library.get_images(
            ["bandcamp:track:4274249518-4240848302-55800693"]
        )
        assert isinstance(
            img["bandcamp:track:4274249518-4240848302-55800693"][0], Image
        )
        root = backend.library.browse("bandcamp:browse")
        assert root == []
        root = backend.library.browse("bandcamp:collection:0:0:a::")
        assert root == []
        root = backend.library.browse("bandcamp:wishlist:0:0:a::")
        assert root == []

    def test_auth(self):
        cfg = ExtensionTest.get_config()
        cfg["bandcamp"]["collection_items"] = 2
        cfg["bandcamp"]["identity"] = os.environ.get("TEST_BANDCAMP_ID")
        if cfg["bandcamp"]["identity"] is not None:
            backend = backend_lib.BandcampBackend(cfg, None)
            root = backend.library.browse("bandcamp:browse")
            assert len(root) == 4
            col = backend.library.browse("bandcamp:collection")
            assert len(col) >= 1
            wish = backend.library.browse("bandcamp:wishlist")
            assert len(wish) >= 1
            alb = backend.library.browse(col[0].uri)
            assert len(alb) >= 1
            # Track we own
            track = backend.library.lookup("bandcamp:mytrack:2937093478-0-4173304455")
            assert isinstance(track[0], Track)
            uri = backend.playback.translate_uri(
                "bandcamp:mytrack:2937093478-0-4173304455"
            )
            assert uri.startswith("http")
            # Free track we don't own
            track = backend.library.lookup("bandcamp:mytrack:2937093478-0-1532026871")
            assert isinstance(track[0], Track)
            uri = backend.playback.translate_uri(
                "bandcamp:mytrack:2937093478-0-1532026871"
            )
            assert uri.startswith("http")
            uri = backend.playback.translate_uri("bandcamp:mytrack:nope-0-notgonnawork")
            assert uri is None

    def test_scrape(self):
        cfg = ExtensionTest.get_config()
        backend = backend_lib.BandcampBackend(cfg, None)
        nothing = backend.library.lookup("bandcamp:https://bandcamp.com/")
        assert nothing == []
        artist = backend.library.lookup("bandcamp:https://kitschclub.bandcamp.com/")
        assert len(artist) > 1
        album = backend.library.lookup(
            "bandcamp:https://louiezong.bandcamp.com/album/jazz"
        )
        assert len(album) > 1
        track = backend.library.lookup(
            "bandcamp:https://louiezong.bandcamp.com/track/minty-fresh"
        )
        assert isinstance(track[0], Track)

    def test_scrape_auth(self):
        cfg = ExtensionTest.get_config()
        cfg["bandcamp"]["identity"] = os.environ.get("TEST_BANDCAMP_ID")
        backend = backend_lib.BandcampBackend(cfg, None)
        nothing = backend.library.lookup("bandcamp:https://bandcamp.com/")
        assert nothing == []
        artist = backend.library.lookup("bandcamp:https://kitschclub.bandcamp.com/")
        assert len(artist) > 1
        album = backend.library.lookup(
            "bandcamp:https://louiezong.bandcamp.com/album/jazz"
        )
        assert len(album) > 1
        track = backend.library.lookup(
            "bandcamp:https://louiezong.bandcamp.com/track/minty-fresh"
        )
        assert isinstance(track[0], Track)
