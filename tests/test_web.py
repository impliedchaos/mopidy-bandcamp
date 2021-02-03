from unittest import mock

import tornado.testing
import tornado.web
import tornado.websocket

import mopidy.config as config
from mopidy_bandcamp import Extension


class BaseTest(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        extension = Extension()
        self.config = config.Proxy({})
        return tornado.web.Application(extension.factory(self.config, mock.Mock()))


class WebHandlerTest(BaseTest):
    def test_index(self):
        response = self.fetch("/", method="GET")
        assert response.code == 200
        response = self.fetch("/?url=https%3A%2F%2Fgoogle.com%2F", method="GET")
        assert response.code == 200
        body = tornado.escape.to_unicode(response.body)
        assert "<title>Error</title>" in body
        response = self.fetch(
            "/?url=https%3A%2F%2Flouiezong.bandcamp.com%2Ftrack%2Fbrain-age",
            method="GET",
        )
        assert response.code == 200
        body = tornado.escape.to_unicode(response.body)
        assert "<title>URL Added</title>" in body
