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
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>Mopidy-Bandcamp</title>

  <script type="text/javascript">
    var file = "http://" + window.location.host + "/mopidy/mopidy.css";  /* use mopidy's css */
    var link = document.createElement("link");
    link.href = file;
    link.type = "text/css";
    link.rel = "stylesheet";
    link.media = "screen,print";
    document.getElementsByTagName("head")[0].appendChild(link);
  </script>
</head>
<body><div class="box focus">
    <h1>Mopidy-Bandcamp</h1>
    <p>
      The purpose of this webclient is to be able to easily add bandcamp 
      albums to Mopidy from your web browser.
    </p>
  </div>

  <div class="box">
    <p>
    <div>
      <h2>Add a bandcamp URL to Mopidy tracklist</h2>
      <form>
        <table style="width: 100%;"><tr>
          <td style="width: 10%;">URL: </td>
          <td style="width: 80%;"><input style="width: 98%;" name="url" type="text" /></td>
          <td style="width: 10%;"><input style="width: 100%;" type="submit" /></td>
        </tr></table>
      </form>
      <p>
    </div>
    <div>
      <h2>Add a bandcamp URL to Mopidy tracklist while browsing</h2>
      <textarea id="bookmark" rows="4" style="width: 100%;"></textarea>
        <script>document.getElementById('bookmark').value="javascript:s='" + window.location +
            "';f=document.createElement('form');f.action=s;i=document.createElement('input');i.type='hidden';" +
            "i.name='url';i.value=window.location.href;f.appendChild(i);document.body.appendChild(f);f.submit();"
        </script>
      <p>
        <h3>Why is this here?</h3>
        <p>Copy the above snippet, and create a bookmark in your web browser with the snippet as the URL. 
           When you're browsing bandcamp, you can simply click that bookmark to add the current page to Mopidy.</p>
           <a href="https://github.com/impliedchaos/mopidy-bandcamp#web-client">more info</a>
      </p>
    </div>
  </div>
</div></body></html>
"""
            )
