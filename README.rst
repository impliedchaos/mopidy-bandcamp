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

This backend does not support authentication and listening to high quality
streams in your collection.  I'd love to support that if someone wants to
reverse-engineer the X-Bandcamp-DM and X-Bandcamp-PoW headers.  In the
meantime, this allows searching bandcamp and playing the 128kbps
preview streams.

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



Project resources
=================

- `Source code <https://github.com/impliedchaos/mopidy-bandcamp>`_
- `Issue tracker <https://github.com/impliedchaos/mopidy-bandcamp/issues>`_
