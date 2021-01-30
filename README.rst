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

`Mopidy <http://www.mopidy.com/>`_ extension for playing music from
`Bandcamp <http://bandcamp.com/>`_.

This backend this allows searching bandcamp and playing the free 128kbps MP3 streams.

Unfortunately, it does **not** support authentication and listening to high quality
streams in your collection.  I'd love to support that if someone wants to
reverse-engineer the :code:`X-Bandcamp-DM` and :code:`X-Bandcamp-PoW` headers.


Installation
============

Install by running::

    sudo pip install Mopidy-Bandcamp



Configuration
=============

Before starting Mopidy, you must enable Mopidy-Bandcamp in 
the Mopidy configuration file::

    [bandcamp]
    enabled = true


Other Configuration Options
---------------------------

- :code:`discover_tags` - List of tags to discover. **You'll really want to change this to any tags that interest you.**
- :code:`discover_genres` - List of bandcamp's genres to discover.  You'll only want to edit this to remove unwanted genres.
- :code:`discover_pages` - Number of pages to load in the browse discover sections.  Default: 1
- :code:`art_url_as_comment` - a hack to set the album art url as the track comment.  Default: false
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
