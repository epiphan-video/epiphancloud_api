# Epiphan Cloud API

This repo contains:

- `/epiphancloud`: Python wrapper for Epiphan Cloud API
- `/docs`: API reference
- `/examples/full_lifecycle.py`: Usage example

## Installation

```
$ git clone https://github.com/epiphan-video/epiphancloud_api.git
$ cd epiphancloud_api
$ pip install -r requirements.txt
```

## Documentation

API documentation is available via Github Pages: [https://epiphan-video.github.io/epiphancloud_api](https://epiphan-video.github.io/epiphancloud_api/)


### How to update docs

Documentation source is stored in `docs-source-slate` folder.

1) Build a slate builder container (once):

```shell
$ cd slate
$ docker build -t slate-builder .
```

2) (optional) Start doc server:
```bash
docker run -it --rm \
  -v $(pwd)/docs-source-slate/:/slate/source \
  -v $(pwd)/docs:/slate/build \
  -p 4567:4567 \
  slate-builder bundle exec middleman server
```

...and open http://localhost:4567/ in your browser.

3) When editing is done, use the container to build static docs:

```bash
docker run -it --rm -v $(pwd)/docs-source-slate/:/slate/source -v $(pwd)/docs:/slate/build slate-builder
```

This command will update files in `docs` folder, if necessary.

3) git commit and push

### Exporting notebook tutorial:

```
jupyter nbconvert --to html --execute device_api.ipynb --ExecutePreprocessor.timeout=-1
```