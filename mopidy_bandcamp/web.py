import re
import tornado.web


class WebHandler(tornado.web.RequestHandler):
    def initialize(self, config, core):
        self.core = core
        self.config = config

    def get(self):
        url = self.get_argument("url", None)
        if url is not None:
            if re.match(r"^https?://[^/]+.bandcamp\.com/", url):
                self.core.tracklist.add(uris=[f"bandcamp:{url}"])
                self.write(
                    "<!DOCTYPE html><html><head><title>URL Added</title><script>alert('URL has been added.');window.history.back()</script></head></html>"
                )
            else:
                self.write(
                    "<!DOCTYPE html><html><head><title>Error</title></head><body><h1>Error</h1><p>Invalid URL: &quot;%s&quot;</p></body></html>"
                    % url
                )
        else:
            self.write(
                """<!DOCTYPE html>
<html><head><title>Add a bandcamp URL</title></head>
<body><div><h1>Add a bandcamp URL to Mopidy tracklist</h1>
<form><p>URL: <input name="url" type="text" /></p><p><input type="submit" /></p></form><p></div>
<div><h1>Why is this here?</h1>
<p>The purpose of this is to be able to easily add bandcamp albums to Mopidy from your web browser.</p>
<textarea id="bookmark" rows="4" cols="80"></textarea>
<script>document.getElementById('bookmark').value="javascript:s='" + window.location +
"';f=document.createElement('form');f.action=s;i=document.createElement('input');i.type='hidden';" +
"i.name='url';i.value=window.location.href;f.appendChild(i);document.body.appendChild(f);f.submit();"
</script>
<p>Copy the above snippet, and create a bookmark in your web browser with the snippet as the URL.<br/>
When you're browsing bandcamp, you can simply click that bookmark to add the current page to Mopidy.</p>
<a href="https://github.com/impliedchaos/mopidy-bandcamp#web-client">more info</a></div></body></html>
"""
            )
