import unittest
from unittest import mock

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
