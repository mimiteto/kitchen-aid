FROM python:3.12.2-slim as base

ARG APP_NAME=kitchen-aid
ENV APP_NAME=${APP_NAME}

FROM base as builder
WORKDIR /install

COPY requirements.txt /requirements.txt
RUN pip install \
    --no-cache-dir \
    --disable-pip-version-check \
    --prefix=/install \
    -r /requirements.txt


FROM base

WORKDIR /${APP_NAME}
ENV PYTHONPATH=/install:${APP}
ENTRYPOINT ["python3", "-m", "${APP_NAME}"]
CMD ["/conf/conf.yaml"]

COPY --from=builder /install /usr/local
COPY ${APP_NAME} /${APP_NAME}
COPY VERSION /${APP_NAME}/VERSION

WORKDIR /app/${APP_NAME}
