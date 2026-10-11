FROM ubuntu:26.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 python3-cairo python3-gi python3-venv \
    python3-gst-1.0 pkg-config build-essential curl git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip wheel setuptools
RUN pip install tox

# mount sources on /app before running the default entrypoint
CMD ["tox", "-e", "py314", "--", "--cov-report=xml"]
