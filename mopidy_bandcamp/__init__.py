import logging
from pathlib import Path
from typing import Any

from mopidy import config, ext
from mopidy.config import Config, ConfigSchema
from mopidy.core import CoreProxy
from mopidy.ext import Registry


__version__ = "1.1.5"

logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = "Mopidy-Bandcamp"
    ext_name = "bandcamp"
    version = __version__

    def get_default_config(self) -> str:
        conf_file = Path(__file__).parent / "ext.conf"
        return config.read(conf_file)

    def get_config_schema(self) -> ConfigSchema:
        schema = super(Extension, self).get_config_schema()
        schema["discover_pages"] = config.Integer(optional=True)
        schema["collection_items"] = config.Integer(optional=True)
        schema["discover_genres"] = config.List(optional=True)
        schema["discover_tags"] = config.List(optional=True)
        schema["image_sizes"] = config.List(optional=True)
        schema["identity"] = config.String(optional=True)
        return schema

    def setup(self, registry: Registry) -> None:
        from .backend import BandcampBackend

        registry.add("backend", BandcampBackend)
        registry.add("http:app", {"name": self.ext_name, "factory": self.factory})

    def factory(self, config: Config, core: CoreProxy) -> Any:
        from .web import WebHandler

        return [(r"/", WebHandler, {"config": config, "core": core})]
