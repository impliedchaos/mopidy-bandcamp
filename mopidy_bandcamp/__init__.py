import logging
import os

from mopidy import config, ext

__version__ = "0.2.0"

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
        schema["art_url_as_comment"] = config.Boolean(optional=True)
        schema["discover_pages"] = config.Integer(optional=True)
        schema["discover_genres"] = config.List(optional=True)
        schema["discover_tags"] = config.List(optional=True)
        return schema

    def get_command(self):
        #       from .commands import BandcampCommand
        #       return BandcampCommand()
        pass

    def validate_environment(self):
        # Any manual checks of the environment to fail early.
        # Dependencies described by setup.py are checked by Mopidy, so you
        # should not check their presence here.
        pass

    def setup(self, registry):
        # You will typically only do one of the following things in a
        # single extension.

        # Register a backend
        from .backend import BandcampBackend

        registry.add("backend", BandcampBackend)
