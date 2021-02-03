import logging
import os

from mopidy import config, ext

__version__ = "1.1.2"

logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = "Mopidy-Bandcamp"
    ext_name = "bandcamp"
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), "ext.conf")
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema["discover_pages"] = config.Integer(optional=True)
        schema["collection_items"] = config.Integer(optional=True)
        schema["discover_genres"] = config.List(optional=True)
        schema["discover_tags"] = config.List(optional=True)
        schema["image_sizes"] = config.List(optional=True)
        schema["identity"] = config.String(optional=True)
        return schema

    def setup(self, registry):
        from .backend import BandcampBackend

        registry.add("backend", BandcampBackend)
        registry.add("http:app", {"name": self.ext_name, "factory": self.factory})

    def factory(self, config, core):
        from .web import WebHandler

        return [(r"/", WebHandler, {"config": config, "core": core})]
