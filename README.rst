Mopidy-Bandcamp
****************

.. image:: https://img.shields.io/pypi/v/Mopidy-Bandcamp
    :target: https://pypi.org/project/Mopidy-Bandcamp
    :alt: Latest PyPI version

.. image:: https://img.shields.io/github/v/release/impliedchaos/mopidy-bandcamp
    :target: https://github.com/impliedchaos/mopidy-bandcamp/releases
    :alt: Latest GitHub release

.. image:: https://img.shields.io/github/commits-since/impliedchaos/mopidy-bandcamp/latest
    :target: https://github.com/impliedchaos/mopidy-bandcamp/commits/master
    :alt: Latest GitHub Commits

.. image:: https://img.shields.io/github/workflow/status/impliedchaos/mopidy-bandcamp/CI
    :target: https://github.com/impliedchaos/mopidy-bandcamp/actions
    :alt: CI build status

.. image:: https://img.shields.io/codecov/c/github/impliedchaos/mopidy-bandcamp
    :target: https://app.codecov.io/gh/impliedchaos/mopidy-bandcamp/
    :alt: Code Coverage

.. image:: https://img.shields.io/badge/PRs-welcome-brightgreen
    :target: https://https://makeapullrequest.com/
    :alt: Pull Requests Welcome

`Mopidy <http://www.mopidy.com/>`_ extension for playing music from
`Bandcamp <http://bandcamp.com/>`_.

This backend allows searching bandcamp and playing the free 128kbps MP3 streams.

Initial support has been added (as of v1.1.0) for browsing and playing your bandcamp collection.
Authentication is a hassle, and described below.  Expect things to be wonky, and
please create an issue when you encounter things that don't work.  Also this is slow
because it requires scraping the bandcamp website instead of using an API.


Installation
============

Install by running::

    sudo python3 -m pip install Mopidy-Bandcamp


Authentication
==============

Authentication is done by grabbing your :code:`identity` token from the cookies of the
bandcamp website. Point your browser at https://bandcamp.com, log in if you aren't already,
and then open up your browser's developer tools (usually by pressing Ctrl-Shift-I or F12).
Reload the page and you should be able to go to the "Network" tab of developer tools and
click on the top entry.  You should be able to click on a "Headers" subtab and see the
Request and Response headers.  Find the "Cookie" request header and look for "identity".

You should see something similar to:

.. code::

    identity=7%09xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx%3D%09%7B%22ex%22%3Ax%2C%22id%22%3Axxxxxxxxxx%7D;

This is what we need.  Copy the data (leave out the semi-colon) and add it to your Mopidy config file like:

.. code::

    [bandcamp]
    identity = 7%09xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx%3D%09%7B%22ex%22%3Ax%2C%22id%22%3Axxxxxxxxxx%7D


Usage
=====

Albums and tracks can be searched for or browsed.  Additionaly, you can force Mopidy-Bandcamp to scrape
a bandcamp URL for you by just prepending the url with "bandcamp:" and adding it to Mopidy.  For example,
using mpc on the command line:

.. code:: shell

    $ mpc add "bandcamp:https://louiezong.bandcamp.com/album/jazz"

Would add the bandcamp album to the queue.

Note: Adding an artist by clicking on the artist in a search result or by manually scraping an artist's
bandcamp page can take a long time depending on the artist.  This is because Mopidy-Bandcamp tries to load
the entirety of the artist's discography.


Web Client
----------

As of v1.1.2 a simple webclient has been added to allow for more easily scraping a page. Not by going to
http://hostname:6680/bandcamp/ and entering in a url (which you can do), but by using the following
as a URL for a bookmark in your web browser:

.. code::

    javascript:s='http://hostname:6680/bandcamp/';f=document.createElement('form');f.action=s;i=document.createElement('input');i.type='hidden';i.name='url';i.value=window.location.href;f.appendChild(i);document.body.appendChild(f);f.submit();

Note: Replace *hostname* and *6680* with your mopidy server's hostname and configured HTTP port.

Now when you're browsing bandcamp you can simply click that bookmark to add the current page to Mopidy.
(This works in Chrome and Firefox.  I haven't bothered checking anything else.)

Configuration
=============

example:

.. code::

    [bandcamp]
    discover-tags = French House, Brit Pop, Tokyo, New Wave, Industrial


- :code:`identity` - Identity token from your bandcamp cookies to authenticate with Bandcamp.
- :code:`collection_items` - Number of items (per page) to fetch from your collection (if authenticated).  Default: 50
- :code:`discover_tags` - List of tags to discover. **You'll really want to change this to any tags that interest you.**
- :code:`discover_genres` - List of bandcamp's genres to discover.  You'll only want to edit this to remove unwanted genres.
- :code:`discover_pages` - Number of pages to load in the browse discover sections.  Default: 1
- :code:`image_sizes` - a list of ids for image sizes to return to mopidy for album art.  Default: 10, 5, 2 (1200x1200, 700x700, 350x350)


Bandcamp image size ids:

+----+-------+--------+--------+
| ID | Width | Height | Aspect |
+====+=======+========+========+
| 1  | Original (usually big)  |
+----+-------+--------+--------+
| 10 | 1200  | 1200   | Square |
+----+-------+--------+--------+
| 20 | 1024  | 1024   | Square |
+----+-------+--------+--------+
| 5  | 700   | 700    | Square |
+----+-------+--------+--------+
| 13 | 380   | 380    | Square |
+----+-------+--------+--------+
| 14 | 368   | 368    | Square |
+----+-------+--------+--------+
| 2  | 350   | 350    | Square |
+----+-------+--------+--------+
| 4  | 300   | 300    | Square |
+----+-------+--------+--------+
| 9  | 210   | 210    | Square |
+----+-------+--------+--------+
| 44 | 200   | 200    | Square |
+----+-------+--------+--------+
| 11 | 172   | 172    | Square |
+----+-------+--------+--------+
| 7  | 150   | 150    | Square |
+----+-------+--------+--------+
| 50 | 140   | 140    | Square |
+----+-------+--------+--------+
| 12 | 138   | 138    | Square |
+----+-------+--------+--------+
| 15 | 135   | 135    | Square |
+----+-------+--------+--------+
| 8  | 124   | 124    | Square |
+----+-------+--------+--------+
| 21 | 120   | 120    | Square |
+----+-------+--------+--------+
| 3  | 100   | 100    | Square |
+----+-------+--------+--------+
| 42 | 50    | 50     | Square |
+----+-------+--------+--------+
| 22 | 25    | 25     | Square |
+----+-------+--------+--------+
| 26 | 800   | 600    | 4:3    |
+----+-------+--------+--------+
| 36 | 400   | 300    | 4:3    |
+----+-------+--------+--------+
| 32 | 380   | 285    | 4:3    |
+----+-------+--------+--------+
| 33 | 368   | 276    | 4:3    |
+----+-------+--------+--------+
| 37 | 168   | 126    | 4:3    |
+----+-------+--------+--------+
| 38 | 144   | 108    | 4:3    |
+----+-------+--------+--------+
| 29 | 100   | 75     | 4:3    |
+----+-------+--------+--------+
| 28 | 768   | 432    | 16:9   |
+----+-------+--------+--------+
| 27 | 715   | 402    | 16:9   |
+----+-------+--------+--------+


Project resources
=================

- `Source code <https://github.com/impliedchaos/mopidy-bandcamp>`_
- `Issue tracker <https://github.com/impliedchaos/mopidy-bandcamp/issues>`_
