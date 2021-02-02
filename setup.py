import re

from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall('__([a-z]+)__ = "([^"]+)"', content))
    return metadata["version"]


setup(
    name="Mopidy-Bandcamp",
    version=get_version("mopidy_bandcamp/__init__.py"),
    url="https://github.com/impliedchaos/mopidy-bandcamp",
    license="MIT License",
    author="Dave Maez",
    author_email="impliedchaos@gmail.com",
    description="Backend for listening to bandcamp",
    long_description=open("README.rst").read(),
    packages=find_packages(exclude=["tests", "tests.*"]),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "setuptools",
        "Mopidy >= 3.0.0",
        "Pykka >= 1.1",
    ],
    entry_points={
        "mopidy.ext": [
            "bandcamp = mopidy_bandcamp:Extension",
        ],
    },
    classifiers=[
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Multimedia :: Sound/Audio :: Players",
    ],
)
