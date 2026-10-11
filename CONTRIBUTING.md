Contributing
============

Feel free to submit any pull requests.  I don't care much about style guidelines (I just run python black on the tree, even though I think it's ugly).

- Dave

Use [Containerfile](./Containerfile) to run tests an environment
matching the CI one. Eg with `podman`:

``` bash
podman build -t mopidy-bandcamp -f Containerfile
podman run -ti -v ${PWD}:/app localhost/mopidy-bandcamp:latest 
```
