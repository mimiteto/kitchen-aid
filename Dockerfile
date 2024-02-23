FROM python:3.12.2-slim as base

FROM base as builder
WORKDIR /install

COPY requirements.txt /requirements.txt
RUN apt-get update &&\
    apt-get install -y git &&\
    pip install \
    --no-cache-dir \
    --disable-pip-version-check \
    --prefix=/install \
    -r /requirements.txt


FROM base

ENV APP_NAME=kitchen-aid
WORKDIR /${APP_NAME}
ENV PYTHONPATH=/install:/${APP_NAME}
ENTRYPOINT ["/usr/local/bin/python", "-m", "kitchen_aid"]
CMD ["--conf", "/conf/conf.yaml"]

COPY --from=builder /install /usr/local
COPY . /${APP_NAME}

WORKDIR /${APP_NAME}
